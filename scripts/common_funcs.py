import json

from common_utils.funcs import execute_cmd, set_end_event


def shutdown(args_dict, raw_input):
    if args_dict['logic'] == 'windows':
        cmd = 'start wpeutil shutdown'
    else:
        # shutdown之前的命令是用来清除缓存的
        cmd = 'sync && echo 3 > /proc/sys/vm/drop_caches;shutdown -h now'
    code, stdout, stderr = execute_cmd(cmd)
    return json.dumps({'code': code, 'stdout': stdout, 'stderr': stderr}), b''


def set_end_event_api(args_dict, raw_input):
    set_end_event()
    return '', b''


def reboot(args_dict, raw_input):
    cmd = 'shutdown /f /r /t 0'
    code, stdout, stderr = execute_cmd(cmd)
    return json.dumps({'code': code, 'stdout': stdout, 'stderr': stderr}), b''
