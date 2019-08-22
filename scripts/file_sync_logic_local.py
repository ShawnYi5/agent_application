import threading
import time
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
        self._error_msg = None
        self._status = ('', '')

        self._sync_thread = None
        self._cp_result = None

        _logger.info('MainLogic init args_dict {}'.format(args_dict))
        with open('/tmp/data.json', 'w') as f:
            json.dump(args_dict, f)
        self._successful = False
        if args_dict.get('in_debug_mod'):
            _logger.info('start in debug mod')
            funcs.checkout2debug()

    def start_sync(self, args_dict, raw_input):
        self._sync_thread = threading.Thread(target=self._start_sync, args=(args_dict, raw_input))
        self._sync_thread.setDaemon(True)
        self._sync_thread.start()
        return '', b''

    def _start_sync(self, args_dict, raw_input):
        _logger.error('_start_backup begin')
        try:
            """
                args_dict = {
                    'samba_params':{
                        'username':'test',
                        'password':'f',
                        'root_url':r'\\172.16.1.3\share\aio',
                        'drive_letter_and_sub_url_list':[['Y', r'\\172.16.1.3\share\aio\目录y']],
                    },
                    'vdisks':[{
                        'file_vhd':'Y:\\d1\d2.vhdx',
                        'part_num_and_drive_letter_list':[[3, 'K']]
                    }],
                    'sync_source':['K:\\d1\file1.txt', 'K:\\d1\dir1']
                    'sync_destination': 'd:\\clw20190708\'
                }
            """
            """
                # print(get_free_drive_letter())
                # print(get_all_mounted_vdisk())
                # mount_smb_args_dict = {'root_url': r'\\172.16.1.3\share\aio', 'username': 'test', 'password': 'f',
                #                        'drive_letter_and_sub_url_list': [['Y', r'\\172.16.1.3\share\aio\y']], }
                # print(mount_smb(mount_smb_args_dict, raw_input=None))
                # mount_disk_args_dict = {'file_vhd':r'Y:\vhd2\w10vhd.vhd', 'part_num_and_drive_letter_list': [[1, 'K']]}
                # print(mount_disk(mount_disk_args_dict,raw_input=None))
                umount_disk_args_dict = {'file_vhd': r'Y:\vhd2\w10vhd.vhd', 'part_num_and_drive_letter_list': [[1, 'K']]}
                print(umout_disk(umount_disk_args_dict, raw_input=None))
                umount_smb_args_dict = {'root_url': r'\\172.16.1.3\share\aio', 'username': 'test', 'password': 'f',
                                        'drive_letter_and_sub_url_list': [['Y', r'\\172.16.1.3\share\aio\y']], }
                print(umount_smb(umount_smb_args_dict, raw_input=None))
            
            """
            _logger.info('**************************************************************\n')
            _logger.info('**************************** start_sync ******************************\n')
            _logger.info('**************************************************************\n')
            self._status = ('启动远端同步组件', 'start remote sync')
            self._get_remote_proxy()
            self._status = ('发送同步指令', 'send_remote_backup_cmd')
            self._check_and_umount_vdisk()  # 如果发现vdisk 则卸载
            self._connect_smb_retry(self._args_dict['samba_params'])
            self._mount_smb(self._args_dict['samba_params'])
            self._mount_disk(self._args_dict['vdisks'])
            self._status = ('等待传输完毕', 'waite_end')
            self._start_cp_file()
            self._connect_smb_retry(self._args_dict['samba_params'])
            self._umount_disk(self._args_dict['vdisks'])
            self._connect_smb_retry(self._args_dict['samba_params'])
            self._umount_smb(self._args_dict['samba_params'])
            # self._reboot_remote()  # 暂时关闭重启
            if len(self._cp_result['success']) == 0:
                self.set_error('同步文件失败', 'cp failed {}'.format(self._cp_result))
                self._successful = False
            else:
                self._successful = True
        except Utils.SystemError as se:
            self.set_error(se.description, se.debug, se.rawCode)
            _logger.error('_start_backup error:{}'.format(se), exc_info=True)
        except Exception as e:
            self.set_error('内部异常1151', '_start_backup {} {}'.format(e, traceback.format_exc()))
            _logger.error('_start_backup error:{}'.format(e), exc_info=True)
        finally:
            self._notify_remote_end()
            self._is_end.set()
        _logger.info('**************************************************************\n')
        _logger.info('**************************** end_sync ******************************\n')
        _logger.info('**************************************************************\n')
        _logger.error('_start_backup end')

    @xlogging.convert_exception_to_value(None)
    def _notify_remote_end(self):
        self.remote_func_proxy.execute('common_funcs', 'set_end_event_api')

    @xlogging.convert_exception_to_value(None)
    def _reboot_remote(self):
        self.remote_func_proxy.execute('common_funcs', 'reboot')

    def _check_and_umount_vdisk(self):
        mounted_vdisk_list, _ = self.remote_func_proxy.execute('file_sync_logic_remote', 'get_all_mounted_vdisk')
        if not mounted_vdisk_list:
            mounted_vdisk_list = json.loads(mounted_vdisk_list[0])
            for mounted_vdisk in mounted_vdisk_list:
                vdisk_args_dict = {'file_vhd': mounted_vdisk}
                self.remote_func_proxy.execute('file_sync_logic_remote', 'umount_disk', vdisk_args_dict)
        return None

    def _connect_smb_retry(self, args_dict):
        while not self._stop_flag:
            result, _ = self.remote_func_proxy.execute('file_sync_logic_remote', 'connect_smb', args_dict)
            result = json.loads(result)
            if result['retval'] == 0 or result['retval'] == '0':
                break
            else:
                time.sleep(5)

    def _mount_smb(self, args_dict):
        self.remote_func_proxy.execute('file_sync_logic_remote', 'mount_smb', args_dict)
        return None

    def _mount_disk(self, vdisks):
        for vdisk in vdisks:
            self.remote_func_proxy.execute('file_sync_logic_remote', 'mount_disk', vdisk)
        return None

    def _umount_disk(self, vdisks):
        for vdisk in vdisks:
            self.remote_func_proxy.execute('file_sync_logic_remote', 'umount_disk', vdisk)
        return None

    def _umount_smb(self, args_dict):
        self.remote_func_proxy.execute('file_sync_logic_remote', 'umount_smb', args_dict)
        return None

    def _start_cp_file(self):
        self._cp_result, _ = self.remote_func_proxy.execute('file_sync_logic_remote', 'cp_file',
                                                            {'sync_source': self._args_dict['sync_source'],
                                                             'sync_destination': self._args_dict['sync_destination']})
        self._cp_result = json.loads(self._cp_result)

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

    def _get_remote_proxy(self):
        from service_in_kvm import app
        count = 12 * 5
        remote_proxy = None
        while count > 0 and (not self._stop_flag):
            count -= 1
            try:
                remote_proxy = app.get_remote_proxy(self._args_dict['ident'])
            except Exception as e:
                _logger.warning('_get_remote_proxy error: {} will retry {}'.format(e, count))
                time.sleep(5)
            else:
                break
        if not remote_proxy:
            xlogging.raise_system_error('等待R端连入超时', 'waite remote timeout', 172)
        self.remote_proxy = remote_proxy
        self.remote_func_proxy = remote_helper.FunctionMapper(self.remote_proxy, _logger)

    # 询问备份状况
    def poll(self, args_dict, raw_input):
        status = {
            'finished': self._is_end.is_set(),
            'progressIndex': -1,
            'progressTotal': -1,
            'successful': self._successful,
            'error_msg': self._error_msg,
            'status': self._status,
            'cp_result': self._cp_result
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
