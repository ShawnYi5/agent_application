# coding: utf-8
import os
import time
import traceback
import logging
import re
import uuid

from common_utils.funcs import execute_cmd, xlogging

_logger = logging.getLogger(__name__)
UUID = re.compile('UUID=\"([\w-]+)\"')


class Mount:
    def __init__(self, mount_dir, read_only):
        self.successful_mount_info = list()
        self.fail_mount_info = set()
        self.mount_dir = mount_dir
        self._windows_volumes = list()  # [(device, uuid)]
        self._scan_windows_volume()
        self._read_only =  read_only

    # 只能mount 非动态盘简单卷
    def mount(self, dev_path, partition_info):
        try:
            cmd_line = "partx -d {};partx -a {}".format(dev_path, dev_path)
            execute_cmd(cmd_line)
            dev_partition2offset_dict = self.get_dev_detail(dev_path)
            _logger.debug('dev:{} partition info:{}'.format(dev_path, dev_partition2offset_dict))
            for partition in partition_info:
                mount_func = self._fetch_mount_func(partition)
                if not mount_func:
                    continue
                dev_str = dev_partition2offset_dict.get(str(partition['PartitionOffset']), None)
                vol_name = self.get_name(partition)
                if not dev_str:
                    _logger.warning(
                        'get vol:[{},offset:{}] dev fail'.format(vol_name, partition['PartitionOffset']))
                    continue
                des_path = os.path.join(self.mount_dir, '{}'.format(vol_name))
                rev = mount_func(dev_str, des_path)
                if not rev:
                    execute_cmd('rm -rf "{}"'.format(des_path))
                    self.fail_mount_info.add((dev_str, des_path, partition['VolumeName']))
                else:
                    self.successful_mount_info.append((dev_str, des_path, partition['VolumeName']))
        except Exception as e:
            _logger.error('mount error:{}'.format(e), exc_info=True)

    def _fetch_mount_func(self, vol):
        fss = [
            ('NTFS', self._mount_ntfs),
            ('FAT', self._mount_vfat),
        ]
        for fs in fss:
            if vol['FileSystem'].upper().startswith(fs[0]):
                break
        else:
            return None
        return fs[1]

    def _mount_vfat(self, vol, point):
        xlogging.makedirs(point, exist_ok=True)
        if self._read_only:
            cmd_line = 'mount -o ro,iocharset=utf8,codepage=936 "{}" "{}"'.format(vol, point)
        else:
            cmd_line = 'mount -o rw,iocharset=utf8,codepage=936 "{}" "{}"'.format(vol, point)
        ret = execute_cmd(cmd_line)
        return ret[0] == 0

    def _mount_ntfs(self, vol, point):
        xlogging.makedirs(point, exist_ok=True)
        if self._read_only:
            cmd_line = 'mount -t ntfs-3g "{}" "{}" -o ro'.format(vol, point)
        else:
            cmd_line = 'mount -t ntfs-3g "{}" "{}";mount -no remount rw "{}"'.format(vol, point, point)
        ret = execute_cmd(cmd_line)
        return ret[0] == 0

    def mount_dynamic(self, windows_volumes):
        try:
            for volume in windows_volumes:
                mount_func = self._fetch_mount_func(volume)
                if not mount_func:
                    continue
                # 已经挂载不再挂载
                if volume['VolumeName'] in [mount[2] for mount in self.successful_mount_info]:
                    continue
                label = self.get_name(volume)
                mount_point = os.path.join(self.mount_dir, label)
                duuid = hex(int(volume['VolumeSerialNumber']))[2:].upper()
                _logger.info('start get {} {} device path'.format(label, duuid))
                devices = self._fetch_device(duuid)  # 会匹配多个
                for device in devices:
                    rev = mount_func(device, mount_point)
                    if not rev:
                        execute_cmd('rm -rf "{}"'.format(mount_point))
                        self.fail_mount_info.add((device, mount_point, volume['VolumeName']))
                    else:
                        self.successful_mount_info.append((device, mount_point, volume['VolumeName']))
                        break

        except Exception as e:
            _logger.error('mount_dynamic error:{}'.format(e), exc_info=True)

    def _scan_windows_volume(self):
        execute_cmd('/usr/local/bin/ldmtool create all')  # 加载动态卷
        rev = execute_cmd('blkid |egrep "ntfs|vfat"')
        if rev[0] != 0:
            return
        for line in rev[1].strip().splitlines():
            uuid, device = '', ''
            uuid_match = UUID.search(line)
            if uuid_match:
                uuid = uuid_match.groups()[0]
            else:
                pass
            device = line.split(':')[0]
            self._windows_volumes.append((device, uuid.replace('-', '')))
        _logger.info('_windows_volumes:{}'.format(self._windows_volumes))

    # 会找到多个
    def _fetch_device(self, duuid):
        devices = list()
        for device, suuid in self._windows_volumes:
            if suuid.upper().endswith(duuid):
                _logger.info('_fetch_device match duuid:{} to suuid:{} device:{}'.format(duuid, suuid, device))
                devices.append(device)
        return devices

    @staticmethod
    def is_one_mount(mount_point):
        r = execute_cmd(r'mount')
        if r[0] != 0:
            _logger.warning('list mount failed. {}'.format(r))
            return False
        return mount_point in r[1]

    def umount_one(self, mount_point):
        execute_cmd(r'fuser -k "{}"'.format(mount_point))
        execute_cmd(r'fuser -k "{}"'.format(mount_point))
        execute_cmd(r'fuser -k "{}"'.format(mount_point))
        execute_cmd(r'umount "{}"'.format(mount_point))
        time.sleep(0.1)
        while self.is_one_mount(mount_point):
            r = execute_cmd(r'umount "{}"'.format(mount_point))
            if r[0] != 0:
                execute_cmd(r'fuser -k "{}"'.format(mount_point))
                time.sleep(0.1)

    def UnMount(self):
        try:
            for one_dev in self.successful_mount_info:
                self.umount_one(one_dev[1])
            self.successful_mount_info.clear()
        except Exception as e:
            _logger.error('except {}'.format(traceback.format_exc()))

    @staticmethod
    def get_name(partition):
        v_name = partition['VolumeLabel']
        l_name = partition['Letter']
        if v_name and l_name:
            return "{}({})".format(v_name, l_name)
        elif v_name:
            return "{}".format(v_name)
        elif l_name:
            return "{}".format(l_name)
        else:
            return 'volume{}'.format(uuid.uuid4().hex)

    @staticmethod
    def get_dev_detail(dev_path):
        rs = dict()
        if not os.path.exists(dev_path):
            _logger.warning('DevDetail get_dict fail, dev:{} is not found'.format(dev_path))
            return rs

        cmd = r"partx -o NR,START {} |grep -v NR".format(dev_path)
        ret = execute_cmd(cmd)
        if ret[0] == 0:
            for line in ret[1].splitlines():
                item_list = line.strip().split()
                if len(item_list) == 2:
                    offset = str(int(item_list[1]) * 512)
                    rs[offset] = "{}{}".format(dev_path, item_list[0])
        else:
            _logger.error('get DevDetail fail:{}'.format(ret[2]))
        return rs


if __name__ == "__main__":
    nbd_class = Mount("/dev/nbd0", "/mnt", [])
