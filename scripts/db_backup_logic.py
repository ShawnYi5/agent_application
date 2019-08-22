import threading
import time
import random
import json
import os
import traceback
import sys

try:
    from common_utils import xlogging, funcs, remote_helper
    import Utils
except:
    sys.path.append('..')  # 工程目录加入
    from common_utils import xlogging, funcs, remote_helper
    import Utils

_logger = xlogging.getLogger(__name__)

VG_NAME = 'clw_b7f1e0_vg'
LV_NAME = 'data'
VMAGENT_PATH = '/opt/ClwDbMgr/ClwVmAgent'
MOUNT_PATH = os.path.join(VMAGENT_PATH, 'data')


class MainLogic(object):

    def __init__(self, args_dict, raw_input):
        self._args_dict = args_dict
        self._raw_input = raw_input

        self._stop_flag = False
        self._is_end = threading.Event()
        self._backup_thread = None
        self._already_created_lvm = False

        self._write_counts = 0
        self._write_total = random.randrange(100, 1000)
        self._error_msg = None
        self._status = ('', '')

        self._all_blocks_size = self._get_all_block_size()  # {‘/dev/sda’:size_bytes}
        _logger.info('MainLogic init args_dict {}'.format(args_dict))
        with open('/tmp/data.json', 'w') as f:
            json.dump(args_dict, f)
        self._successful = False

    @xlogging.convert_exception_to_value(None)
    def _pause_in_debug_mod(self, msg):
        if not self._args_dict['in_debug_mod']:
            return
        file_name = '/tmp/pause_db_backup_{}'.format(time.time())
        with open(file_name, 'w'):
            pass
        while os.path.exists(file_name):
            _logger.warning('{} pause until {} removed!'.format(msg, file_name))
            time.sleep(5)

    def start_backup(self, args_dict, raw_input):
        self._backup_thread = threading.Thread(target=self._start_backup, args=(args_dict, raw_input))
        self._backup_thread.setDaemon(True)
        self._backup_thread.start()
        return '', b''

    def _init_data_area(self):
        if 'lvm_config' not in self._args_dict:
            return
        lvm_path = '/dev/mapper/{}-{}'.format(VG_NAME, LV_NAME)
        if not os.path.exists(lvm_path):
            self._status = ('初始化数据缓存区域', 'init_data_area')
            _logger.warning('not found lvm {}, start create'.format(lvm_path))
            self._pause_in_debug_mod('开始创建lvm')
            self._create_lvm()
        xlogging.makedirs(MOUNT_PATH, exist_ok=True)
        code, stdout, stderr = funcs.execute_cmd('mount {} {}'.format(lvm_path, MOUNT_PATH))
        if code != 0:
            xlogging.raise_system_error('初始化数据缓存区域失败', 'execute_cmd mount:{}{}{}'.format(code, stdout, stderr), 1162)

    @staticmethod
    def _get_all_block_size():
        rs = dict()
        for file_name in os.listdir('/sys/block'):
            if not file_name.isalpha():
                continue
            abs_path = os.path.abspath(os.path.join('/sys/block', file_name))
            try:
                with open(os.path.join(abs_path, 'size')) as f:
                    size = int(f.read()) * 512
            except Exception as e:
                _logger.error('_get_all_block_size error:{}'.format(e), exc_info=True)
            else:
                dev_path = '/dev/{}'.format(file_name)
                rs[dev_path] = size
        _logger.debug('_get_all_block_size {}'.format(rs))
        return rs

    def _create_lvm(self):
        disks = self._args_dict['lvm_config']['disks']
        code, stdout, stderr = funcs.execute_cmd('pvscan')
        if code != 0:
            xlogging.raise_system_error('初始化数据缓存区域失败', 'execute_cmd pvscan:{}{}{}'.format(code, stdout, stderr), 1161)
        pvs = list()
        for disk in disks:
            for dev_path, size in self._all_blocks_size.items():
                if int(disk['disk_bytes']) == int(size):
                    disk['dev_path'] = dev_path
                    break
            else:
                xlogging.raise_system_error('初始化数据缓存区域失败',
                                            'not found disk {} dev_path {}'.format(disk, self._all_blocks_size),
                                            1162
                                            )
            funcs.execute_cmd('pvcreate {}'.format(disk['dev_path']))
            pvs.append(disk['dev_path'])
        cmd = 'vgcreate {} '.format(VG_NAME)
        cmd += ' '.join(pvs)
        funcs.execute_cmd(cmd)
        funcs.execute_cmd('lvcreate -l 100%VG -n {} {}'.format(LV_NAME, VG_NAME))
        funcs.execute_cmd('mkfs.ext4 /dev/mapper/{}-{}'.format(VG_NAME, LV_NAME), 60 * 30)

    def startup_data_agent(self):
        vmagent = VMAGENT_PATH
        cmd = "nohup ./clwobkapp > clwobkapp.log 2>&1 &"
        retval, stdout, stderr = funcs.execute_cmd(cmd, cwd=vmagent)
        if retval != 0:
            _logger.error(
                '[startup_data_agent] execute_cmd failed, cmd={} out={} err={}'.format(cmd, stdout, stderr))
            return False

        return True

    def _start_backup(self, args_dict, raw_input):
        _logger.error('_start_backup begin')
        try:
            self._status = ('初始化网络', 'init_network')
            self._init_network()
            self._init_data_area()
            self._already_created_lvm = True
            self._status = ('初始化本地代理', 'init_local_proxy')
            retval = self.startup_data_agent()
            if not retval:
                self.set_error('内部异常1151', 'startup_data_agent failed')
                _logger.error('startup_data_agent failed', exc_info=True)
            self._status = ('等待R端连入', 'waite R connect in')
            self._get_remote_proxy()
            self._status = ('发送远端备份指令', 'send_remote_backup_cmd')
            self._send_backup_cmd()
            self._status = ('等待传输完毕', 'waite_end')
            self._waite_end()
            self._get_bkpinfo_file()
        except Utils.SystemError as se:
            self.set_error(se.description, se.debug, se.rawCode)
            _logger.error('_start_backup error:{}'.format(se), exc_info=True)
        except Exception as e:
            self.set_error('内部异常1151', '_start_backup {} {}'.format(e, traceback.format_exc()))
            _logger.error('_start_backup error:{}'.format(e), exc_info=True)
        finally:
            self._is_end.set()
        _logger.error('_start_backup end')

    def _get_remote_proxy(self):
        from service_in_kvm import app
        count = 12 * 5
        remote_proxy = None
        while count > 0:
            count -= 1
            try:
                remote_proxy = app.get_remote_proxy(self._args_dict['db_backup_params']['master_ident'])
            except Exception as e:
                _logger.warning('_get_remote_proxy error: {} will retry {}'.format(e, count))
                time.sleep(5)
            else:
                break
        if not remote_proxy:
            xlogging.raise_system_error('等待R端连入超时', 'waite remote timeout', 172)
        self.remote_proxy = remote_proxy

    def _get_bkpinfo_file(self):
        if self._successful:
            rev_json_str, _ = self.remote_ins.execute('get_bkpinfo_file')
            rev_dict = json.loads(rev_json_str)
            with open(os.path.join(MOUNT_PATH, rev_dict['name']), 'w') as wf:
                wf.write(rev_dict['data'])

    def _init_network(self):
        for net_info in funcs.get_net_dev_info():
            if net_info.get('Mac', '-2').upper() == self._args_dict['kvm_ip_info'].get('mac', '-1').upper():
                break
        else:
            _logger.warning('not found net info {} {}'.format(self._args_dict['kvm_ip_info'], funcs.get_net_dev_info()))
            return
        funcs.execute_cmd('ip addr add {}/{} dev {}'.format(self._args_dict['kvm_ip_info']['ip'],
                                                            self._args_dict['kvm_ip_info']['mask'], net_info['Name']))
        funcs.execute_cmd('ip link set {} up'.format(net_info['Name']))

    def _send_backup_cmd(self):
        self.remote_ins = remote_helper.ModuleMapper('oraworker', 'oraworker', self.remote_proxy, _logger)
        while True:
            try:
                rev, _ = self.remote_ins.execute('backup_db', self._args_dict['db_backup_params'])
            except Exception as e:
                _logger.error('_send_backup_cmd {}'.format(e), exc_info=True)
            else:
                break
        assert rev == 'ok'

    def _waite_end(self):
        while not self._stop_flag:
            rev_str, _ = self.remote_ins.execute('check_finish')
            rev_dict = json.loads(rev_str)
            if rev_dict['finish']:
                self._successful = rev_dict['success']
                break
            time.sleep(10)

    # 询问备份状况
    def poll(self, args_dict, raw_input):
        status = {
            'finished': self._is_end.is_set(),
            'progressIndex': self._write_counts,
            'progressTotal': self._write_total,
            'successful': self._successful,
            'error_msg': self._error_msg,
            'status': self._status,
            'already_created_lvm':self._already_created_lvm,
        }
        return json.dumps(status, ensure_ascii=False), b''

    def stop_backup(self, args_dict, raw_input):
        _logger.info('get stop flag', args_dict, raw_input)
        self.set_error('用户取消', 'user cancel')
        self._stop_flag = True
        self._is_end.wait()
        return '', b''

    def set_error(self, msg, debug, code=-1):
        if self._error_msg:
            return
        else:
            self._error_msg = (msg, debug, code)


if __name__ == '__main__':
    print('main start...')
    with open('/tmp/data.json', 'r') as f:
        dict_info = json.load(f)
    ins = MainLogic(dict_info, b'')
    ins.start_backup(dict_info, b'')
    while True:
        print(ins.poll('', b''))
        time.sleep(5)
