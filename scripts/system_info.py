# coding=utf-8
import sys
import psutil
import platform
import configparser
import os

if __name__ == '__main__':
    # 调试模式，将工程目录加入
    sys.path.append('..')

from common_utils import funcs, xlogging

_logger = xlogging.getLogger(__name__)


def get_linux_info():
    return {
        'initrdfs_path': '',
        'kconfig_file': '',
        'grub_file': '',
        'kernel_ver': '',
        'system_map': '',
        'vermagic': '',
        'bit_opt': '',
        'release': '',
        'vmlinuz_path': '',
        'grub_ver': '',
        'install_path': '',
        'boot_symvers': '',
        'platform': '',
        'syms_file': ''
    }


def get_storage_info():
    return {}


def get_disk_info():
    rv = list()
    return rv


def get_system_caption():
    sc = platform.system() + ' ' + ' '.join(platform.linux_distribution())
    if sc.upper().find('linux'.upper()) == -1:
        sc = 'Linux-' + sc
    return sc


def system_type():
    processor = platform.processor()
    if processor == '':
        return platform.machine()
    else:
        return processor


def get_agent_version():
    cf = configparser.ConfigParser()
    path = os.path.join(funcs.get_install_path(), "remote_agent.ini")
    try:
        cf.read(path)
        return cf.get("client", "ver")
    except Exception as e:
        _logger.error('get_agent_version failed {} . {}'.format(path, e))
        return ''


def get_user_ident():
    cf = configparser.ConfigParser()
    path = os.path.join(funcs.get_install_path(), "remote_agent.ini")
    try:
        cf.read(path)
        return cf.get("client", "username")
    except Exception as e:
        _logger.error('get_user_ident failed {} . {}'.format(path, e))
        return ''


def get_client_timestamp():
    cf = configparser.ConfigParser()
    path = os.path.join(funcs.get_install_path(), "remote_agent.ini")
    try:
        cf.read(path)
        return cf.get("client", "timestamp")
    except Exception as e:
        _logger.error('get_client_timestamp failed {} . {}'.format(path, e))
        return ''


def get_system():
    system_info = {
        # cpu
        "ProcessorInfo": '',
        "ComputerName": platform.node(),
        # mem info
        "PhysicalMemory": psutil.virtual_memory().total,
        # work group
        "WorkGroup": '',
        # system caption
        "SystemCaption": get_system_caption(),
        "ServicePack": "",
        "BuildNumber": platform.platform(),
        "ProcessorArch": system_type(),
        "SystemCatName": ' '.join(platform.architecture()),
        "version": get_agent_version(),
    }
    return system_info


class SystemInfo(object):

    def __init__(self):
        self._sys_info = None

    def get(self, use_cache=True):
        if use_cache and self._sys_info:
            return self._sys_info
        else:
            return self._get_system_info()

    def _get_system_info(self):
        self._sys_info = {
            "System": get_system(),
            # netdev info
            "Nic": funcs.get_net_dev_info(),
            # disk info
            "Disk": get_disk_info(),
            # linux storage
            "Storage": get_storage_info(),
            # linux info
            "Linux": get_linux_info(),
            'host_ident': open(os.path.join('/boot', 'ClerWareDbIdent')).read(),
            # user
            "UserIdent": get_user_ident(),
            # client timestamp
            "ClientTimestamp": get_client_timestamp(),
        }
        return self._sys_info


if __name__ == '__main__':
    import pprint

    pprint.pprint(SystemInfo().get())
