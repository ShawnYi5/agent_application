# coding: utf-8
import string
import os
import psutil
import tempfile
import pprint
import argparse
import json
import time
import traceback

from common_utils import xlogging, funcs, mount_linux, mount_windows

_logger = xlogging.getLogger(__name__)

key_files = [
    {'path': 'etc/', 'type': 'dir_all'},
    {'path': 'lib/systemd/', 'type': 'dir_all'},
    {'path': 'lib64/systemd/', 'type': 'dir_all'},
    {'path': 'lib/', 'type': 'dir_cur'},
    {'path': 'lib64/', 'type': 'dir_cur'},
    {'path': 'bin/sh', 'type': 'file'},
    {'path': 'bin/bash', 'type': 'file'},
    {'path': 'sbin/init', 'type': 'file'},
    {'path': 'sbin/login', 'type': 'file'},
    {'path': 'lib/firmware', 'type': 'dir_all'},
]


def get_path_from_key_files(root_path, file_type):
    items = list(filter(lambda key_file: key_file['type'] == file_type, key_files))
    path_existed = list()
    for item in items:
        item_path = os.path.join(root_path, item['path'])
        if os.path.exists(item_path):
            path_existed.append(item_path)
    return path_existed


def _read_key_files_in_system(root_path):
    # 预读单个文件
    single_files = get_path_from_key_files(root_path, file_type='file')
    for file in single_files:
        cmd = r'cat {0} > /dev/null'.format(file)
        funcs.execute_cmd(cmd, 60 * 5)
    # 预读目录当层文件
    folders = get_path_from_key_files(root_path, file_type='dir_cur')
    for folder in folders:
        cmd = r'find {0} -maxdepth 1 -type f | tar -cf - -T - | cat > /dev/null'.format(folder)
        funcs.execute_cmd(cmd, 60 * 5)
    # 预读文件夹内所有(子)文件(<5MB)
    folders = get_path_from_key_files(root_path, file_type='dir_all')
    for folder in folders:
        cmd = r'find {0} -type f -size -5M | tar -cf - -T - | cat > /dev/null'.format(folder)
        funcs.execute_cmd(cmd, 60 * 5)


def get_info_from_file(in_file):
    if os.path.isfile(in_file):
        try:
            with open(in_file) as fd:
                mstr = fd.read()
                fd.close()
                _logger.info("read file {} success,info {}".format(in_file, mstr))
                return 0, mstr
        except Exception as e:
            _logger.error("read file {} failed {},{}".format(in_file, e, traceback.format_exc()))
    else:
        _logger.error("read file {} failed,file not exist".format(in_file))
    return -1, None


def set_info_to_file(in_file, in_str, in_format):
    # if os.path.isfile(in_file):
    try:
        with tempfile.NamedTemporaryFile(in_format, dir=os.path.dirname(in_file), delete=False) as tf:
            tf.write(in_str)
            tempname = tf.name
            tf.flush()
            os.fdatasync(tf)
            os.rename(tempname, in_file)
            dirfd = os.open(os.path.dirname(in_file), os.O_DIRECTORY)
            try:
                os.fsync(dirfd)
            finally:
                os.close(dirfd)
            _logger.debug("write file {} success,info {}".format(in_file, in_str))
            return 0
    except Exception as e:
        _logger.error("write file {} failed {},{}".format(in_file, e, traceback.format_exc()))
    # else:
    #     _logger.error("read file {} failed,file not exist".format(in_file))
    return -1


def smb_get_cfgfile_name(user_name):
    return '/etc/samba/{}.smb.conf'.format(user_name)


def smb_get_userpath(user_name):
    return os.path.join('/home/', user_name, user_name)


def smb_get_hostpath(user_name, host_name):
    return os.path.join(smb_get_userpath(user_name), host_name)


def smb_umount_path(hostpath):
    if not os.path.isdir(hostpath):
        _logger.error('umount host path not exist {}'.format(hostpath))
        return 0, 'success'
    mountlist = psutil.disk_partitions()
    umountlist = list()
    for diskpart in mountlist:
        mountpoint = diskpart.mountpoint
        if mountpoint.startswith(hostpath):
            umountlist.append(mountpoint)
    if len(umountlist) > 0:
        sortlist = sorted(umountlist, key=(lambda x: len(x)), reverse=True)
        _logger.debug('umount sort list {}'.format(sortlist))
        for mountpoint in sortlist:
            _logger.debug('umount path {}'.format(mountpoint))
            cmdline = 'fuser -k "{mountpoint}";fuser -k "{mountpoint}";fuser -k "{mountpoint}";umount "{mountpoint}"'.format(
                mountpoint=mountpoint)
            funcs.execute_cmd(cmdline)


def smb_del_cfg(user_name):
    # cfgfile = smb_get_cfgfile_name(in_name)
    cfgfile = '/etc/samba/user.smb.conf'
    if not os.path.isfile(cfgfile):
        return 0
    phase_name = '[' + user_name + ']'
    new_cfg_str = ''
    retval = get_info_from_file(cfgfile)
    if retval[0] != 0:
        _logger.error("del user {} get cfg info from {} failed".format(user_name, cfgfile))
        return -1
    strlist = retval[1].split('\n\n')
    update_flag = 0
    for i in range(len(strlist)):
        mstr = strlist[i].strip('\n').strip(' ')
        if len(mstr) <= 2:
            continue
        if mstr.startswith(phase_name):
            _logger.debug('del user {} cfg info {} at str success'.format(user_name, mstr))
            update_flag = 1
            continue
        else:
            new_cfg_str += mstr + '\n\n'
    if update_flag == 1:
        retval = set_info_to_file(cfgfile, new_cfg_str, 'w')
        if retval != 0:
            _logger.error("del user {} update cfg to file {} failed".format(user_name, cfgfile))
            return -1
        else:
            _logger.debug("del user {} update cfg to file {} success".format(user_name, cfgfile))
    return 0


def smb_add_cfg(user_name, read_only):
    cfgfile = '/etc/samba/user.smb.conf'
    smbconf = '/etc/samba/smb.conf'
    phase_name = '[' + user_name + ']'
    add_cfg_str = '[{user_name}]\n' \
                  'path = {path}\n' \
                  'comment = My shared folder\n' \
                  'force group = root\n' \
                  'force user = root\n' \
                  'valid users = {user_name}\n'.format(user_name=user_name, path=smb_get_userpath(user_name))
    if read_only:
        add_cfg_str += 'read only = yes\n'
    else:
        add_cfg_str += 'readonly = no\n'
        add_cfg_str += 'writable = yes\n'

    add_smbconf_str = '[global]\n' \
                      'workgroup = MYGROUP\n' \
                      'server string = Samba Server Version\n' \
                      'netbios name =SambaServer\n' \
                      'log file = /var/log/samba/%m.log\n' \
                      'max log size = 10\n' \
                      'security = user\n' \
                      'encrypt passwords = yes\n' \
                      'socket options = TCP_NODELAY SO_RCVBUF=8192 SO_SNDBUF=8192\n' \
                      'config file = /etc/samba/user.smb.conf\n\n'

    new_cfg_str = ''
    if os.path.isfile(cfgfile):
        retval = get_info_from_file(cfgfile)
        if retval[0] != 0:
            _logger.error("add user {} get cfg info from {} failed".format(user_name, cfgfile))
            return -1
        if retval[1].find(phase_name) < 0:
            new_cfg_str = retval[1] + add_cfg_str
    else:
        new_cfg_str = add_cfg_str

    if new_cfg_str != '':
        retval = set_info_to_file(cfgfile, new_cfg_str, 'w')
        retval_smb = set_info_to_file(smbconf, add_smbconf_str, 'w')
        if retval_smb != 0:
            _logger.error("retval_smb update file {} failed".format(add_smbconf_str))
            return -1
        else:
            _logger.debug("retval_smb update file {} success".format(add_smbconf_str))
        if retval != 0:
            _logger.error("add user {} add cfg to file {} failed".format(user_name, cfgfile))
            return -1
        else:
            _logger.debug("add user {} add cfg to file {} success".format(user_name, cfgfile))
    return 0


def smb_get_user_list():
    userlist = list()
    cmd_line = 'pdbedit -L'
    retval = funcs.execute_cmd(cmd_line)
    if retval[0] != 0:
        _logger.error("get info from cmd {} failed".format(cmd_line))
    else:
        mlist = retval[1].strip().split('\n')
        for i in range(len(mlist)):
            mstr = mlist[i]
            mindex = mstr.find(':')
            if mindex > 0:
                muser_name = mstr[:mindex]
                userlist.append(muser_name)
    return userlist


# 如果检测到当前用户没有主机共享则删除用户
def smb_del_userpath(user_name):
    # del sys usr
    userpath = smb_get_userpath(user_name)
    have_host = 0
    if os.path.isdir(userpath):
        for hostname in os.listdir(userpath):
            hostpath = os.path.join(userpath, hostname)
            if os.path.isdir(hostpath):
                have_host += 1
                break
    if have_host == 0:
        # del sys user
        cmd_line = 'userdel -r -f "{}"'.format(user_name)
        _logger.debug("start del sys user {},cmd {}".format(user_name, cmd_line))
        funcs.execute_cmd(cmd_line)
        # del smb user
        smb_del_cfg(user_name)
        cmd_line = 'pdbedit -x {}'.format(user_name)
        _logger.debug("start del smb user {},cmd {}".format(user_name, cmd_line))
        funcs.execute_cmd(cmd_line)
        cmdline = 'fuser -k "{userpath}";fuser -k "{userpath}";fuser -k "{userpath}";rm -rf "{userpath}"'.format(
            userpath=userpath)
        _logger.debug("start user path,cmd {}".format(cmd_line))
        funcs.execute_cmd(cmdline)
    else:
        _logger.error('already have {} host,can not del userpath {}'.format(have_host, userpath))
        return -1, "failed"

    return 0, 'success'


# 添加用户同时生成用户目录,如果已有用户目录则直接返回成功
def smb_add_userpath(username, userpwd, read_only):
    userpath = smb_get_userpath(username)
    if not os.path.isdir(userpath):
        cmd_line = 'useradd {};mkdir -p "{}"'.format(username, userpath)
        retval = funcs.execute_cmd(cmd_line)
        if retval[0] != 0:
            smb_del_userpath(username)
            return -1, 'create sys user {} failed'.format(username)
        # samba config
        cmd_line = '(echo "{}";echo "{}")|smbpasswd -a "{}"'.format(userpwd, userpwd, username)
        retval = funcs.execute_cmd(cmd_line)
        if retval[0] != 0:
            _logger.error("add smb user {} failed,ret str\n{}".format(username, retval[1]))
            smb_del_userpath(username)
            return -1, 'create smb user {} failed'.format(username)
        else:
            _logger.error("add smb user {} success,ret str\n{}".format(username, retval[1]))
            retval = smb_add_cfg(username, read_only)
            if retval != 0:
                _logger.error("smb user {} create cfg file failed".format(username))
                smb_del_userpath(username)
                return -1, 'create smb cfg file failed,user {}'.format(username)
    else:
        _logger.debug('smb susr path already have {}'.format(userpath))
    _logger.debug('smb_create_smbuser user {} pwd {} success'.format(username, userpwd))
    return 0, 'success'


def is_one_mount(mount_point):
    r = funcs.execute_cmd(r'mount')
    if r[0] != 0:
        _logger.warning('list mount failed. {}'.format(r))
        return False
    return mount_point in r[1]


# 删除主机共享目录,同步清除所有mount信息,外部的主机监控信息和mount信息需为额外清除
# 同时会尝试删除用户信息
def smb_del_hostpath(username, hostname):
    hostpath = smb_get_hostpath(username, hostname)
    _logger.debug('del host path: user {} host {} host path {}'.format(username, hostname, hostpath))
    if os.path.isdir(hostpath):
        smb_umount_path(hostpath)
        cmdline = 'fuser -k "{hostpath}";fuser -k "{hostpath}";fuser -k "{hostpath}";rm -rf "{hostpath}"'.format(
            hostpath=hostpath)
        funcs.execute_cmd(cmdline)
    time.sleep(0.1)
    while is_one_mount(hostpath):
        r = funcs.execute_cmd(r'umount "{}"'.format(hostpath))
        if r[0] != 0:
            funcs.execute_cmd(r'fuser -k "{}"'.format(hostpath))
            time.sleep(0.1)
    smb_del_userpath(username)
    return 0, 'success'


# 添加主机共享目录，如已有主机目录则返回失败
def smb_add_hostpath(user_name, hostname):
    hostpath = smb_get_hostpath(user_name, hostname)
    if os.path.exists(hostpath):
        _logger.error('smb_add_hostpath host {} already exist'.format(hostpath))
        return -1, ''
    cmdline = 'mkdir -p "{}"'.format(hostpath)
    ret = funcs.execute_cmd(cmdline)
    if ret[0] != 0:
        _logger.debug('add hostpath failed {}'.format(ret))
        return -1, 'failed'
    return 0, 'success'


# 删除用户信息,用户主机共享信息,外部的主机监控信息和mount信息需额外清除
def smb_del_user(user_name):
    # del sys usr
    _logger.debug('del user {}'.format(user_name))
    userpath = smb_get_userpath(user_name)
    if os.path.isdir(userpath):  # sambauser name
        for hostname in os.listdir(userpath):
            hostpath = os.path.join(userpath, hostname)
            if os.path.isdir(hostpath):  # host snapshot path
                smb_del_hostpath(user_name, hostname)
    smb_del_userpath(user_name)
    return 0, 'success'


# 添加用户,同smb_add_userpath
def smb_add_user(user_name, userpwd, read_only):
    return smb_add_userpath(user_name, userpwd, read_only)


# 同smb_del_hostpath
def smb_del_host(username, hostname):
    smb_del_hostpath(username, hostname)
    return 0


# 删除主机共享,同步清除监控信息和mount信息
def smb_del_host_share(hostinfo):
    _logger.debug('del host {}'.format(hostinfo))
    username = hostinfo[0]
    hostname = hostinfo[1]
    smb_del_host(username, hostname)
    return 0, username, hostname


# 从include_ranges 筛选出制定磁盘的 partitions info
def get_partitions_info(disk_index, include_ranges):
    rs = list()
    for ranges in include_ranges:
        if int(disk_index) == ranges['diskIndex']:
            rs = ranges['ranges']
            break
    return rs


def get_agent_config(bin_path, name):
    config_path = os.path.join(bin_path, "AgentService.config")

    _logger.info("get_agent_config config_path={}".format(config_path))

    if not os.path.exists(config_path):
        _logger.info("get_agent_config config_path={} not exist".format(config_path))
        return None
    with open(config_path) as rf:
        for line in rf:
            if line.strip().startswith(name):
                break
        else:
            return None

    index = line.find('=')

    if index < 0:
        return None
    else:
        value = line[index:].strip()
        _logger.info("get_agent_config name={} value={}".format(name, value))
        return value


def get_agent_path(bin_path, root_path, name):
    _logger.info("get_agent_path bin_path={} root_path={}".format(bin_path, root_path))
    path = get_agent_config(bin_path, name)
    if not path:
        return None

    _logger.info("get_agent_path path={}".format(path))

    index = path.find("/")
    if index < 0:
        _logger.info("get_agent_path invalid path={}".format(path))
        return None

    full = os.path.join(root_path, path[index + 1:])

    _logger.info("get_agent_path full={}".format(full))

    return full


def get_clwmeta_path(bin_path, root_path):
    path = get_agent_path(bin_path, root_path, "Agent.ClwMetaPath")
    if not path:
        return None

    clwmeta = os.path.join(path, "ClerWareMeta")

    return clwmeta


def get_reg_file_path_imp(root_path, install_path):
    """
    获取clerware_meta_path
    1. AgentService.config 中配置了Agent.ClwMetaPath 目录，那么使用这个
    2. 也有可能 ClwMeta 存在与 install_path 目录下
    2. 以上都不存在，那么就在 /boot 目录下
    :return: clerware_meta_path
    """
    bin_path = root_path + install_path
    if not os.path.exists(bin_path):
        xlogging.raise_system_error('无效的安装路径', 'invalid install path', 445)
        return None

    # from AgentService.config
    meta_path = get_clwmeta_path(bin_path, root_path)
    if meta_path:
        return meta_path

    _logger.info(r'get_reg_file_path_imp config path is not exist')

    # from bin_path
    meta_path = os.path.join(bin_path, 'ClerWareMeta')
    if os.path.exists(meta_path):
        return meta_path

    _logger.info(r'get_reg_file_path_imp bin path is not exist')

    # from boot dir
    meta_path = os.path.join(root_path, 'boot', 'ClerWareMeta')
    if os.path.exists(meta_path):
        return meta_path

    xlogging.raise_system_error(r'无法访问备份快照中的关键数据区域',
                                r'get_reg_file_path_imp failed : {}'.format(meta_path), 1)
    return None


def chattr_clerwaremeta_del_i(clerware_meta_path):
    """
    从一下目录找到clerware_meta, 并取消掉 -i 属性
    /bin/目录下
    /opt/
    :param clerware_meta_path:
    :return:
    """
    cmd = 'chattr -i {}'.format(clerware_meta_path)
    code, stdout, stderr = funcs.execute_cmd(cmd)
    if code != 0:
        # xlogging.raise_system_error('更改属性失败', 'change meta failed', 532)
        _logger.info('ClerWareMeta del i Failed.ignore.')
    else:
        _logger.info('ClerWareMeta del i successful!')


class SambaShareUser(object):

    def __init__(self, args_dict, raw_input):
        """
        :param args_dict: {
            'username':'', samba user
            'password':'', samba pwd
            'hostname':'', share path name,
            'read_only': ''
        }
        """
        self.user = args_dict['username']
        self.password = args_dict['userpwd']
        self.host_name = args_dict['hostname']
        self.read_only = args_dict['read_only']
        self.host_path = smb_get_hostpath(self.user, self.host_name)

    def share(self, args_dict, raw_input):
        ret = smb_add_user(self.user, self.password, self.read_only)
        if ret[0] != 0:
            raise Exception('SambaShareUser add user fail')

        ret = smb_add_hostpath(self.user, self.host_path)
        if ret[0] != 0:
            raise Exception('SambaShareUser add host path fail')
        return self.host_path, b''

    def del_share(self):
        smb_del_hostpath(self.user, self.host_path)
        smb_del_userpath(self.user)

    @staticmethod
    def restart_samba(args_dict, raw_input):
        ret = funcs.execute_cmd('systemctl restart smb;systemctl restart nmb')
        if ret[0] != 0:
            _logger.info('reset_samba,fail')
        else:
            _logger.info('reset_samba,successful')
        return '', b''


class MountFileSystem(object):

    def __init__(self, args_dict, raw_input):
        """{
            'mount_root':'xxxx',
            'ostype'：'xxx',
            'read_only':''
            'disklist':[{
                'nbd_uuid':''.
                'diskid':''
            }],
            'include_ranges':[],
            'windows_volumes':[],
            'linux_storage':[]
        }
        """
        self._mount_root = args_dict['mount_root']
        self._os_type = args_dict['ostype']
        self._read_only = args_dict['read_only']
        self._disk_list = args_dict['disklist']
        self._include_ranges = args_dict['include_ranges']
        self._windows_volumes = args_dict['windows_volumes']
        self._linux_storage = args_dict['linux_storage']

    def mount(self, args_dict, raw_input):
        self._add_disk_info()  # 添加映射关系
        if self._os_type == 'windows':
            self._mount_windows()
        else:
            self._mount_linux()
        return 'ok', b''

    def _mount_windows(self):
        # 非动态卷部分
        mount_handle = mount_windows.Mount(self._mount_root, self._read_only)
        for disk_info in self._disk_list:
            partition_info = get_partitions_info(disk_info['diskid'], self._include_ranges)
            mount_handle.mount(disk_info['disk_path'], partition_info)
        mount_handle.mount_dynamic(self._windows_volumes)
        _logger.info('_mount_windows successful_mount_info info:\n{}\n'.format(
            pprint.pformat(mount_handle.successful_mount_info)))
        _logger.warning(
            '_mount_windows fail_mount_info info:\n{}\n'.format(pprint.pformat(mount_handle.fail_mount_info)))

    def _mount_linux(self):
        nbd_list = list()
        for disk_info in self._disk_list:
            mdict = {'snapshot_disk_index': disk_info['diskid'], 'device_path': disk_info['disk_path']}
            nbd_list.append(mdict)
        linux_mount_ins = mount_linux.Mount(nbd_list, self._linux_storage,
                                            self._mount_root, self._read_only, self._include_ranges)
        try:
            linux_mount_ins.mount()
        except Exception as e:
            linux_mount_ins.umount_all()
            raise e

    def _add_disk_info(self):
        for disk_info in self._disk_list:
            disk_info['disk_path'] = self._find_disk_by_nbd_uuid(disk_info['nbd_uuid'])
            _logger.info(
                'map nbd:{} to disk:{}'.format(disk_info['nbd_uuid'], disk_info['disk_path']))

    @staticmethod
    def _find_disk_by_nbd_uuid(nbd_uuid):
        for file in os.listdir('/dev/disk/by-id'):
            """
            lrwxrwxrwx 1 root root  9 Jan  7 16:49 scsi-0QEMU_QEMU_HARDDISK_26a27dbc20154fd58596 -> ../../sdb
            lrwxrwxrwx 1 root root 10 Jan  7 16:49 scsi-0QEMU_QEMU_HARDDISK_26a27dbc20154fd58596-part1 -> ../../sdb1
            """
            fstr = 'QEMU_QEMU_HARDDISK_'
            s_index = file.find(fstr)
            if s_index > 0 and file.find('part') == -1:
                uuid = file[s_index + len(fstr):]
            else:
                continue

            if uuid == nbd_uuid[:len(uuid)]:
                break
        else:
            raise Exception('map nbd:{} to disk fail'.format(nbd_uuid))
        return os.path.realpath(os.path.join('/dev/disk/by-id', file))
