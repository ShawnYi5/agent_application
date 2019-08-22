# coding: utf-8
import sys
import json
import os
import win32api
import shutil
import re

from io import StringIO

try:
    from common_utils import xlogging, funcs, remote_helper
    import Utils
except:
    sys.path.append('..')  # 工程目录加入
    from common_utils import xlogging, funcs, remote_helper
    import Utils

_logger = xlogging.getLogger(__name__)


def get_free_drive_letter(args_dict, raw_input):
    """
    获取本机可用的盘符名称
    :return:
    """
    _drive_fixed = list()
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split(':\\\000')[:-1]
    for i in range(24):
        new_create_drive = chr(i + ord('C'))
        _drive_fixed.append(new_create_drive)
        for drive in drives:
            if drive in _drive_fixed:
                _drive_fixed.remove(drive)
    return json.dumps(_drive_fixed), b''


def cp_file(args_dict, raw_input):
    sync_source = args_dict['sync_source']
    sync_destination = args_dict['sync_destination']
    _logger.info('start cp_file sync_source {} sync_destination {}'.format(sync_source, sync_destination))
    xlogging.makedirs(sync_destination, exist_ok=True)
    result = {'success': list(),
              'failed': list(),
              'not_exists': list()}
    for source in sync_source:
        if not os.path.exists(source):
            result['not_exists'].append(source)
        else:
            try:
                dir_items = [i.strip(':') for i in re.split(r'\\*', source) if i]
                dst_dir = os.path.join(sync_destination, *dir_items[:-1])
                xlogging.makedirs(dst_dir, exist_ok=True)
                target = os.path.join(dst_dir, dir_items[-1])
                _logger.debug('start copy {} to {}'.format(source, target))
                if os.path.isfile(source):
                    shutil.copy2(source, target)
                else:
                    shutil.copytree(source, target)
            except Exception as e:
                _logger.warning('cp_file error: {} {}'.format(e, source), exc_info=True)
                result['failed'].append(source)
            else:
                result['success'].append(source)
    return json.dumps(result), b''


def get_all_mounted_vdisk(args_dict, raw_input):
    _vdisk_list = list()
    get_all_mounted_vdisk_script_name = 'get_all_mounted_vdisk.txt'
    get_all_mounted_vdisk_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                     get_all_mounted_vdisk_script_name)
    with open(get_all_mounted_vdisk_script_path, 'w') as f:
        f.write('list vdisk \r\n')
        f.write('exit \r\n')
    get_all_mounted_vdisk_cmd = 'DiskPart /s "{}"'.format(get_all_mounted_vdisk_script_path)

    retval, outs, errs = funcs.execute_cmd(get_all_mounted_vdisk_cmd)
    strio = StringIO(outs)
    while True:
        _line = strio.readline()
        if not _line:
            break
        print(_line)
        if '------' in _line:
            break
    while True:
        _line = strio.readline()
        if not _line:
            break
        _line_data_list = _line.split()
        if len(_line_data_list) < 4:
            break
        _vdisk_list.append(_line_data_list[len(_line_data_list) - 1])

    return json.dumps(_vdisk_list), b''


def connect_smb(args_dict, raw_input):
    root_url = args_dict['root_url']
    username = args_dict['username']
    password = args_dict['password']
    aio_data_disk_login_cmd = 'net use "{}" /user:{} {}'.format(root_url, username, password)
    retval, outs, errs = funcs.execute_cmd(aio_data_disk_login_cmd)
    return json.dumps({'retval': retval, 'outs': outs, 'errs': errs}), b''


def mount_smb(args_dict, raw_input):
    """
    通过验证账号密码登录到aio的备份点的位置，将备份点的镜像挂载到一个新的空的盘符上
    :param args_dict:{'root_url':r'\\172.16.1.3\share\aio','username':'test','password':'f',
    'drive_letter_and_sub_url_list':[['X', r'\\172.16.1.3\share\aio\X'],['Y ', r'\\172.16.1.3\share\aio\Y'],...],}
    :param raw_input:
    :return:
    """
    # root_url = args_dict['root_url']
    # username = args_dict['username']
    # password = args_dict['password']
    drive_letter_and_sub_url_list = args_dict['drive_letter_and_sub_url_list']
    #
    # aio_data_disk_login_cmd = 'net use "{}" /user:{} {}'.format(root_url, username, password)
    # funcs.execute_cmd(aio_data_disk_login_cmd)

    reval_list = list()
    outs_list = list()
    errs_list = list()
    for drive_letter_and_sub_url in drive_letter_and_sub_url_list:
        mount_drive_cmd = 'subst {}: "{}"'.format(drive_letter_and_sub_url[0], drive_letter_and_sub_url[1])
        retval, outs, errs = funcs.execute_cmd(mount_drive_cmd)
        reval_list.append(retval)
        outs_list.append(outs)
        errs_list.append(errs)

    return json.dumps({'retval': reval_list, 'outs': outs_list, 'errs': errs_list}), b''


def mount_disk(args_dict, raw_input):
    """
    将vhd格式的镜像数据通过diskpart重新以文件格式挂载到新盘符上
    :param args_dict:{'file_vhd':r'Y:\vhd2\w10vhd.vhd','part_num_and_drive_letter_list':[[1,'K'],[2,'J'],...],}
    :param raw_input:
    :return:
    """
    file_vhd = args_dict['file_vhd']
    part_num_and_drive_letter_list = args_dict['part_num_and_drive_letter_list']

    mount_disk_script_name = 'mount_disk_script.txt'
    mount_disk_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), mount_disk_script_name)
    with open(mount_disk_script_path, 'w') as f:
        f.write('select vdisk file="{}" \r\n'.format(file_vhd))
        f.write('attach vdisk \r\n')
        f.write('rescan \r\n')
        for part_num_and_drive_letter in part_num_and_drive_letter_list:
            # 如果select不到volume号则会直接退出本脚本也不再执行，因此暂取消本卸载功能
            # f.write('select volume {} \r\n'.format(part_num_and_drive_letter[1]))
            # f.write('remove letter={} \r\n'.format(part_num_and_drive_letter[1]))
            f.write('select part {} \r\n'.format(part_num_and_drive_letter[0]))
            f.write('assign letter={} \r\n'.format(part_num_and_drive_letter[1]))
        f.write('exit \r\n')
    mount_disk_cmd = 'DiskPart /s "{}"'.format(mount_disk_script_path)
    retval, outs, errs = funcs.execute_cmd(mount_disk_cmd)  # retval=-1 操作也是成功的

    return json.dumps({'retval': retval, 'outs': outs, 'errs': errs}), b''


def umount_disk(args_dict, raw_input):
    """
    清除挂载的vhd文件格式的分区
    :param args_dict:{'file_vhd':r'Y:\vhd2\w10vhd.vhd','part_num_and_drive_letter_list':[[1,'K'],[2,'J'],...],}
    :param raw_input:
    :return:
    """
    umount_disk_script_name = 'umount_disk_script.txt'
    umount_disk_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), umount_disk_script_name)
    file_vhd = args_dict['file_vhd']
    part_num_and_drive_letter_list = args_dict['part_num_and_drive_letter_list']
    with open(umount_disk_script_path, 'w') as f:
        for part_num_and_drive_letter in part_num_and_drive_letter_list:
            f.write('select volume={} \r\n'.format(part_num_and_drive_letter[1]))
            f.write('remove \r\n')
        f.write('select vdisk file="{}" \r\n'.format(file_vhd))
        f.write('detach vdisk \r\n')
        f.write('rescan \r\n')
        f.write('exit \r\n')
    umount_disk_cmd = 'DiskPart /s "{}"'.format(umount_disk_script_path)
    retval, outs, errs = funcs.execute_cmd(umount_disk_cmd)  # reval = -1，实际操作也是正常的。

    return json.dumps({'retval': retval, 'outs': outs, 'errs': errs}), b''


def umount_smb(args_dict, raw_input):
    """
    卸载在smb中的挂载aio备份镜像数据的盘符，将连接aio数据备份点的账号登出
    :param args_dict: {'root_url':r'\\172.16.1.3\share\aio','username':'test','password':'f',
    'drive_letter_and_sub_url_list':[['X', r'\\172.16.1.3\share\aio\X'],['Y ', r'\\172.16.1.3\share\aio\Y'],...],}
    :param raw_input:
    :return:
    """
    root_url = args_dict['root_url']
    drive_letter_and_sub_url_list = args_dict['drive_letter_and_sub_url_list']

    reval_list = list()
    outs_list = list()
    errs_list = list()
    for drive_letter_and_sub_url in drive_letter_and_sub_url_list:
        drive_letter = drive_letter_and_sub_url[0]
        umount_disk_cmd = 'subst {}: /d'.format(drive_letter)
        retval, outs, errs = funcs.execute_cmd(umount_disk_cmd)
        reval_list.append(retval)
        outs_list.append(outs)
        errs_list.append(errs)

    aio_data_disk_login_out_cmd = 'net use "{}"  /delete'.format(root_url)
    funcs.execute_cmd(aio_data_disk_login_out_cmd)
    return json.dumps({'retval': reval_list, 'outs': outs_list, 'errs': errs_list}), b''


if __name__ == '__main__':
    print(get_free_drive_letter())

    # print(get_all_mounted_vdisk())

    # mount_smb_args_dict = {'root_url': r'\\172.16.1.3\share\aio', 'username': 'test', 'password': 'f',
    #                        'drive_letter_and_sub_url_list': [['Y', r'\\172.16.1.3\share\aio\y']], }
    # print(mount_smb(mount_smb_args_dict, raw_input=None))

    # mount_disk_args_dict = {'file_vhd':r'Y:\vhd2\w10vhd.vhd', 'part_num_and_drive_letter_list': [[1, 'K']]}
    # print(mount_disk(mount_disk_args_dict,raw_input=None))

    # umount_disk_args_dict = {'file_vhd': r'Y:\vhd2\w10vhd.vhd', 'part_num_and_drive_letter_list': [[1, 'K']]}
    # print(umout_disk(umount_disk_args_dict, raw_input=None))
    #
    # umount_smb_args_dict = {'root_url': r'\\172.16.1.3\share\aio', 'username': 'test', 'password': 'f',
    #                         'drive_letter_and_sub_url_list': [['Y', r'\\172.16.1.3\share\aio\y']], }
    # print(umount_smb(umount_smb_args_dict, raw_input=None))

# if __name__ == '__main__':
#     print('main start...')
#     with open('/tmp/data.json', 'r') as f:
#         dict_info = json.load(f)
#     ins = MainLogic(dict_info, b'')
#     ins.start_backup(dict_info, b'')
#     while True:
#         print(ins.poll('', b''))
#         time.sleep(5)
