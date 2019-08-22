import os
import uuid
import argparse

from common_utils import xlogging, xdebug, funcs
from scripts import db_backup_logic
import service_in_kvm
import service_in_remote

_logger = xlogging.getLogger(__name__)
_x_debug_helper = None
app = None


def _mount_clw_lvm():
    try:
        funcs.execute_cmd('mount {device} {path}'.format(path=db_backup_logic.MOUNT_PATH,
                                                         device='/dev/mapper/{}-{}'.format(
                                                             db_backup_logic.VG_NAME,
                                                             db_backup_logic.LV_NAME)))
    except Exception as e:
        _logger.warning('_mount_clw_lvm error:{}'.format(e))


def _start_x_debug_helper():
    global _x_debug_helper
    _x_debug_helper = xdebug.XDebugHelper()
    _x_debug_helper.setDaemon(True)
    _x_debug_helper.start()


def _generate_ident():
    path = os.path.join('/boot/', 'ClerWareDbIdent')
    if not os.path.exists(path):
        ident = uuid.uuid4().hex
        with open(path, 'w') as wf:
            wf.write(ident)
    else:
        pass


def _is_in_kvm():
    for net in funcs.get_net_dev_info():
        mac = net.get('Mac', '')
        if not mac:
            continue
        if mac.upper().startswith('CC'):
            break
    else:
        return False
    return True


def get_args():
    arg_parse = argparse.ArgumentParser('clw agent application')
    arg_parse.add_argument('--without_agent', action='store_true')
    arg_parse.add_argument('--ip_in_kvm')
    arg_parse.add_argument('--aio_ip')
    arg_parse.add_argument('--aio_port', default='20100')
    arg_parse.add_argument('--flag_path', default='')
    arg_parse.add_argument('--event_name', default='')
    arg_parse.add_argument('--ident', default='')
    return arg_parse.parse_args()


if __name__ == '__main__':
    _start_x_debug_helper()
    if _is_in_kvm():
        service_in_kvm.run()
    else:
        args = get_args()
        if args.without_agent:
            service_in_remote.run_without_agent({
                'ip_in_kvm': args.ip_in_kvm,
                'aio_ip': args.aio_ip,
                'aio_port': args.aio_port,
                'flag_path': args.flag_path,
                'event_name': args.event_name,
                'ident': args.ident
            })
        else:
            _generate_ident()
            service_in_remote.run()
