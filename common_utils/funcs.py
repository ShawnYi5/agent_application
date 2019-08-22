# coding: utf-8
import subprocess
import os
import signal
import psutil
import socket
import time
import threading

from . import xlogging

_logger = xlogging.getLogger(__name__)


def get_install_path():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


DEBUG_FILE = os.path.join(get_install_path(), 'debug_mod.txt')


def checkout2debug():
    with open(DEBUG_FILE, 'w') as f:
        pass
    return True


def execute_cmd(cmd, timeout=120, **kwargs):
    _logger.debug('execute_cmd cmd:{}'.format(cmd))
    with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True, **kwargs) as p:
        try:
            stdout, stderr = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.kill(p.pid, signal.SIGKILL)  # 超时并不会让进程退出
            _logger.warning('execute_cmd {} process killed,timer {} begin'.format(cmd, timeout))
            stdout, stderr = p.communicate()  # 需要再一次获取，防止进程变成 Z状态
            _logger.warning('execute_cmd {} process killed,timer {} end {}'.format(cmd, timeout, p.returncode))
    _logger.debug('execute_cmd cmd:{} return:{}|{}|{}'.format(cmd, p.returncode, stdout, stderr))
    return p.returncode, stdout, stderr


def get_net_dev_info():
    dev_dict = list()
    no_mac_dev_dict = list()
    info = psutil.net_if_addrs()
    for k, v in info.items():
        dev_info = dict()
        ip_vector = list()
        for item in v:
            if socket.AF_INET == item.family:
                ip = item.address
                mask = item.netmask
                ip_vector.append({"Ip": ip, "Mask": mask})
            if psutil.AF_LINK == item.family:
                dev_info["Mac"] = item.address
        if dev_info.get("Mac", "00:00:00:00:00:00") == "00:00:00:00:00:00":
            dev_info["Name"] = k
            dev_info["IpAndMask"] = ip_vector
            no_mac_dev_dict.append(dev_info)
            continue
        dev_info["IpAndMask"] = ip_vector
        dev_info["Name"] = k
        dev_dict.append(dev_info)

    _merge_ip_info(dev_dict, no_mac_dev_dict)

    return dev_dict


def _merge_ip_info(has_mac_dev_list, no_mac_dev_dict):
    name_index = [(item['Name'], index) for index, item in enumerate(has_mac_dev_list)]
    for no_mac_info in no_mac_dev_dict:
        if ':' not in no_mac_info['Name']:
            continue
        dev_name = no_mac_info['Name'].split(':')[0]
        src_index = _get_src_index(name_index, dev_name)
        if src_index is not None:
            has_mac_dev_list[src_index]['IpAndMask'].extend(no_mac_info['IpAndMask'])


def _get_src_index(name_index, dev_name):
    for item in name_index:
        if item[0] == dev_name:
            return item[1]
    return None


def get_install_path():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def pause_in_debug_mod(msg):
    _logger.info('pause_in_debug_mod {} '.format(DEBUG_FILE))
    if not os.path.exists(DEBUG_FILE):
        return
    file_name = os.path.join(get_install_path(), 'pause_{}'.format(time.time()))
    with open(file_name, 'w'):
        pass
    while os.path.exists(file_name):
        _logger.warning('{} pause until {} removed!'.format(msg, file_name))
        time.sleep(5)


_end_event = threading.Event()


def set_end_event():
    _end_event.set()


def waite_end_event():
    _end_event.wait()
