# coding:utf-8
import subprocess
import os
import re
import sys

from common_utils import xlogging, loadIce

import platform

_logger = xlogging.getLogger('register')

cfs_args = {'agent_service':
                {'systemd_cfg': "LinuxAgentService.service", "initd_cfg": "LinuxAgentService.initd_cfg",
                 "AgentServiceName": 'ClwDRClient', "Service_Service": "ClwDRClient.service"
                 },
            'set_ip_service':
                {'systemd_cfg': "ip2sys.service", "initd_cfg": "ip2sys",
                 "AgentServiceName": 'ClwDRIpSvr', "Service_Service": "ClwDRIpSvr.service"
                 },
            'agent_application':
                {'systemd_cfg': "agent_application.service", "initd_cfg": "agent_application.initd_cfg",
                 "AgentServiceName": 'agent_application', "Service_Service": "agent_application.service"
                 }
            }


def get_rc_dir():
    rc3_dir = r'/etc/rc3.d/'
    if os.path.exists(rc3_dir):
        return rc3_dir

    rc3_dir = r'/etc/init.d/rc3.d/'
    if os.path.exists(rc3_dir):
        return rc3_dir

    xlogging.raise_system_error("get_rc_dir error", "can not find rc3.d dir")


def get_ip_service_rank(script_dir, default='06'):
    rank = default
    find = False
    try:
        rank_re = re.compile('^S(\d+)network$')
        for file_name in os.listdir(script_dir):
            match = rank_re.match(file_name)
            if match:
                _rank = match.groups()[0]
                if str.isdigit(_rank) and int(_rank) < int(rank):
                    rank = _rank
                    find = True
        if find:
            assert int(rank) > 0
            rank = '0{}'.format(int(rank) - 1)
    except AssertionError:
        xlogging.raise_system_error("get_ip_service_rank error", "rank <= 0", 0)
    except Exception as e:
        _logger.error("get_ip_service_rank error: {}".format(e), exc_info=True)
    _logger.info('get_ip_service_rank return {}'.format(rank))
    return rank


def get_rcx_full_path(rc_x, file_name):
    rc_x_path = "/etc/{}/".format(rc_x)

    if os.path.exists(rc_x_path):
        return os.path.join(rc_x_path, file_name)

    rc_x_path = "/etc/init.d/{}/".format(rc_x)
    if os.path.exists(rc_x_path):
        return os.path.join(rc_x_path, file_name)

    xlogging.raise_system_error("get_rc_x_path error", "can not find {}".format(rc_x), 0)
    return ""


def _get_service_method():
    # cmd = "systemctl --version"
    cmd = "ps -p 1 -o comm="
    info = executeCommand(cmd)
    if info[0] == 0 and "systemd" in info[1]:
        return "systemd"
    else:
        return "initd"


def executeCommand(cmd, wait=True):
    _logger.info("executeCommand cmd: {}".format(cmd))
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         universal_newlines=True)

    if wait:
        stdout, stderr = p.communicate()
        ret_val = p.returncode

    else:
        ret_val = 0
        stdout = []
        stderr = []

    return ret_val, stdout, stderr


def str_2_int(ker_ver):
    _logger.info("[str_2_int] ker_ver={}".format(ker_ver))

    s_array = ker_ver.split(".")
    i_array = list()
    for s in s_array:
        i = int(s)
        i_array.append(i)

    _logger.info("[str_2_int] i_array={}".format(i_array))

    return i_array


def lower_than_compare(current, compare):
    i_current = str_2_int(current)
    i_compare = str_2_int(compare)

    current_cnt = len(i_current)
    compare_cnt = len(i_compare)
    count = min(current_cnt, compare_cnt)

    i = 0
    while i < count:
        if i_current[i] < i_compare[i]:
            return True
        elif i_current[i] > i_compare[i]:
            return False
        i += 1

    return False


def is_lower_kernel(compare):
    release = platform.release()
    n = release.find('-')
    if n == -1:
        current = release
    else:
        current = release[0:n]

    retval = lower_than_compare(current, compare)

    return retval


# check suse kernel
def check_suse_kernel():
    cmp_version_max = "2.6.28"
    cmp_version_min = "2.6.19"
    cmd = 'cat /proc/version'
    retval_max = is_lower_kernel(cmp_version_max)
    retval_min = is_lower_kernel(cmp_version_min)
    # 当版本大于2.6.28时
    if not retval_max:
        return False
    # 当版本小于2.6.19时
    if retval_min:
        return False
    code, out, err = executeCommand(cmd, True)
    _logger.info(
        "[check_suse_kernel] is_lower_kernel return cmp_version_max={0},cmp_version_min={1}".format(cmp_version_max,
                                                                                                    cmp_version_min))
    if code == 0 and ('SUSE' in out.upper()):
        return True
    else:
        return False


def check_cmd(cmd):
    _logger.info("[do_servcie_config] cmd:{}".format(cmd))
    retval, out, err = executeCommand(cmd)
    _logger.info("[do_servcie_config] retval={} out={} err={}".format(retval, out, err))
    if retval != 0:
        _logger.error("[do_servcie_config] failed")
        return False

    _logger.info("[do_servcie_config] success")

    return True


def do_servcie_config(ver_name):
    cmp_version = "2.6.18"
    retval = is_lower_kernel(cmp_version)
    _logger.info("[do_servcie_config] is_lower_kernel return={}".format(retval))
    check_suse = check_suse_kernel()
    cmd = "chkconfig -a {}".format(ver_name)
    _logger.info("do_service_config_cmd_info:{0}".format(cmd))
    if check_suse:
        cmd_result = check_cmd(cmd)
        return cmd_result
    if not retval:
        return True
    cmd_result = check_cmd(cmd)
    return cmd_result


def get_systemd_path():
    # default
    path = "/usr/lib/systemd/system/"
    if os.path.exists(path):
        return path

    # ubuntu 16.04
    path = "/etc/systemd/system"
    if os.path.exists(path):
        return path

    xlogging.raise_system_error("register error", "[get_systemd_path] not found systemd path", 0)
    return None


class Register(object):
    def __init__(self, working_dir, exe_path, cfg_path):
        self.WorkingDirectory = self._check_path(working_dir)
        self.ExecStart = exe_path
        self.ConfigPath = self._check_path(cfg_path)
        self.method = _get_service_method()
        self.args = self._local_args()

    def _local_args(self):
        return cfs_args['agent_application']

    @staticmethod
    def _check_path(path):
        if os.path.exists(path):
            return path
        else:
            xlogging.raise_system_error("Register _check_path error",
                                        "Register service path not exists {}".format(path), 0)

    def init(self):
        if self.method == "systemd":
            self._modify_cfg(self.args['systemd_cfg'])
            self._agentService_systemd_init()
        else:
            self._modify_cfg(self.args['initd_cfg'])
            self._agentService_initd_init()

    def start(self):
        if self.method == "systemd":
            self._agentService_systemd_start()
        else:
            self._agentService_initd_start()

    def _agentService_initd_init(self):
        _logger.info("_start_agentService_init start")
        cmd_stop = "/etc/init.d/" + self.args['AgentServiceName'] + " stop"
        if self.args['AgentServiceName'] == 'ClwDRClient':
            rc_file_name = 'S20' + self.args['AgentServiceName']
        else:
            rank = get_ip_service_rank(get_rc_dir())
            rc_file_name = 'S{}'.format(rank) + self.args['AgentServiceName']

        executeCommand(cmd_stop)

        rc2_full = get_rcx_full_path("rc2.d", rc_file_name)
        rc3_full = get_rcx_full_path("rc3.d", rc_file_name)
        rc5_full = get_rcx_full_path("rc5.d", rc_file_name)

        cmd_del_rc3 = "rm -f " + rc3_full
        cmd_del_rc5 = "rm -f " + rc5_full
        cmd_del_rc2 = "rm -f " + rc2_full

        cmd4 = "chmod +x /etc/init.d/" + self.args['AgentServiceName']
        cmd5 = "ln -s /etc/init.d/" + self.args['AgentServiceName'] + " " + rc3_full
        cmd6 = "ln -s /etc/init.d/" + self.args['AgentServiceName'] + " " + rc5_full
        ubuntu_a_cmd = "ln -s /etc/init.d/" + self.args['AgentServiceName'] + " " + rc2_full

        # cmd7 = "/etc/init.d/" + self.args['AgentServiceName'] + " start"

        if os.path.exists(rc3_full):
            _logger.info("[_start_agentService_init] remove file={}".format(rc3_full))
            executeCommand(cmd_del_rc3)

        if os.path.exists(rc5_full):
            _logger.info("[_start_agentService_init] remove file={}".format(rc5_full))
            executeCommand(cmd_del_rc5)

        if os.path.exists(rc2_full):
            _logger.info("[_start_agentService_init] remove file={}".format(rc2_full))
            executeCommand(cmd_del_rc2)

        wait = True
        for cmd in [cmd4, cmd5, cmd6, ubuntu_a_cmd]:
            # if cmd == cmd7:
            #     wait = False
            info = executeCommand(cmd, wait)
            if info[0] != 0:
                xlogging.raise_system_error("_agentService_initd_init error",
                                            "init_agentService, error:{}".format(info[2]), 0)

        retval = do_servcie_config(self.args['AgentServiceName'])
        if not retval:
            xlogging.raise_system_error("_agentService_initd_init error", "do_servcie_config failed", 0)

    def _agentService_initd_start(self):
        cmd7 = "/etc/init.d/" + self.args['AgentServiceName'] + " start"
        info = executeCommand(cmd7, False)
        if info[0] != 0:
            xlogging.raise_system_error("_agentService_initd_start error",
                                        "start_agentService, error:{}".format(info[2]), 0)

    def _agentService_systemd_init(self):
        _logger.info("_start_agentService_systemd start")
        # cmd1 = "chmod +x /usr/lib/systemd/system/" + self.args['Service_Service']
        systemd_path = get_systemd_path()
        systemd_cfg = os.path.join(systemd_path, self.args['Service_Service'])
        cmd1 = "chmod +x {}".format(systemd_cfg)
        cmd2 = "systemctl daemon-reload"
        cmd3 = "systemctl enable " + self.args['Service_Service']
        # cmd3 = "systemctl start " + self.args['Service_Service']
        for cmd in [cmd1, cmd2, cmd3]:
            info = executeCommand(cmd)
            if info[0] != 0:
                xlogging.raise_system_error("_agentService_systemd_init error",
                                            "init_agentService, error:{}".format(info[2]), 0)

    def _agentService_systemd_start(self):
        cmd3 = "systemctl start " + self.args['Service_Service']
        info = executeCommand(cmd3)
        if info[0] != 0:
            xlogging.raise_system_error("_agentService_systemd_start error",
                                        "start_agentService, error:{}".format(info[2]), 0)

    def _modify_cfg(self, filename):
        if filename == self.args['systemd_cfg']:
            # dst = "/usr/lib/systemd/system/" + self.args['Service_Service']
            systemd_path = get_systemd_path()
            dst = os.path.join(systemd_path, self.args['Service_Service'])

        else:
            dst = "/etc/init.d/" + self.args['AgentServiceName']

        with open(os.path.join(self.ConfigPath, filename), 'r') as f:
            content = f.read()
            content = content.replace("[WorkingDirectory]", self.WorkingDirectory)
            exe_path = self._get_exe_path(self.ExecStart)
            content = content.replace("[ExecStart]", exe_path)
            with open(dst, 'w') as f1:
                f1.write(content)

    @staticmethod
    def _get_exe_path(path):
        if path.endswith('LinuxAgentService'):
            dir_name = os.path.dirname(path)
            wdg_name = 'clerwd'
            wdg_path = os.path.join(dir_name, wdg_name)
            if not os.path.exists(wdg_path):
                xlogging.raise_system_error("Register _check_path error",
                                            "Register service path not exists {}".format(wdg_path), 0)
            interval_times = 10
            exe_cmd = "{exe_wdg} {itv_tms} {exe_agt_srv}".format(exe_wdg=wdg_path, itv_tms=interval_times,
                                                                 exe_agt_srv=path)
            return exe_cmd
        else:
            return path


class UnInstall(object):
    def __init__(self):
        self.method = _get_service_method()
        self.service_name = ''

    def _uninstall(self, service_name):
        try:
            self.service_name = service_name
            _logger.debug('start unInstall service, service name {}'.format(self.service_name))
            if self.method == "systemd":
                if not service_name.endswith('.service'):
                    self.service_name = '{}.service'.format(self.service_name)
                self._stop_service_systemd()
                self._remove_cfg_systemd()
            else:
                self._stop_service_initd()
                self._remove_cfg_initd()
        except Exception as e:
            _logger.error('_uninstall service {} fail, error:{}'.format(self.service_name, e))

    def uninstall(self, service_name=None):
        if service_name is not None:
            self._uninstall(service_name)
        else:
            self._uninstall('ClwDRClient')
            self._uninstall('ClwDRIpSvr')

    def _stop_service_systemd(self):
        cmd = "systemctl stop {}".format(self.service_name)
        info = executeCommand(cmd)
        if info[0] != 0:
            _logger.error('stop service fail, service name {}, error{}'.format(self.service_name, info[2]))

    def _remove_cfg_systemd(self):
        cmd = "systemctl disable {}".format(self.service_name)
        executeCommand(cmd)
        cmd1 = "rm -f {}".format(os.path.join(get_systemd_path(), self.service_name))
        executeCommand(cmd1)

    def _stop_service_initd(self):
        cmd = "/etc/init.d/{} stop".format(self.service_name)
        info = executeCommand(cmd)
        if info[0] != 0:
            _logger.error('stop service fail, service name {}, error{}'.format(self.service_name, info[2]))

    def _remove_cfg_initd(self):
        found = False
        rc_dirs = ["rc2.d", "rc3.d", "rc5.d"]

        _logger.info("[_remove_cfg_initd] service_name={}".format(self.service_name))

        if len(self.service_name) <= 0:
            _logger.info("[_remove_cfg_initd] } invalid service name")
            return

        for rc_x in rc_dirs:
            rc_x_dir = get_rcx_full_path(rc_x, "")
            dir_files = os.listdir(rc_x_dir)
            rc_find = ''
            for one_file in dir_files:
                if one_file.endswith(self.service_name):
                    rc_find = one_file
                    found = True
                    break

            if rc_find:
                rc_full = get_rcx_full_path(rc_x, rc_find)
                _logger.info("[_remove_cfg_initd] remove file={}".format(rc_full))

                cmd = "rm -f {}".format(rc_full)
                executeCommand(cmd)

        if found:
            cmd = "rm -f /etc/init.d/{}".format(self.service_name)
            _logger.info("[_remove_cfg_initd] excute command={}".format(cmd))
            executeCommand(cmd)

    def stop_service(self, srvname_list=None):
        if srvname_list is None or len(srvname_list) == 0:
            srvname_list = ['ClwDRClient', 'ClwDRIpSvr']
        for name in srvname_list:
            self.service_name = name
            if self.method == "systemd":
                self._stop_service_systemd()
            else:
                self._stop_service_initd()
        self.service_name = ''


if __name__ == "__main__":
    service_dir = os.path.realpath(os.path.join(loadIce.current_dir, '..'))
    if getattr(sys, 'frozen', False):  # The application is frozen
        exe_path = os.path.join(service_dir, 'application_main')
    else:
        exe_path = os.path.join('/usr/bin/python3')
        exe_path += ' {}'.format(os.path.join(service_dir, 'application_main.py'))
    print('working dir {}'.format(service_dir))
    print('exe_path {}'.format(exe_path))
    r = Register(service_dir, exe_path, service_dir)
    r.init()
    r.start()
    print('finish')
