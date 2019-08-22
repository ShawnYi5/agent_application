#pragma once

#include "utils.ice"

module FileBackup {

  interface Logic {

    // {
    //    "nas_type": "nfs" / "cifs",
    //    "mount_cmd": str,
    //    "mount_path": "/mnt/nas",
    //    "timeouts_seconds": int
    // }
    void MountNas(string jsonParams)
      throws Utils::SystemError;

    // {
    //    "mount_path": "/mnt/nas"
    //    "timeouts_seconds: int (seconds)
    // }
    bool UmountNas(string jsonParams)
      throws Utils::SystemError;

    // {
    //    "mount_path": "/mnt/backup"
    // }
    void MountBackup(string jsonParams)
      throws Utils::SystemError;

    // {
    //    "mount_path": "/mnt/backup"
    // }
    void UmountBackup(string jsonParams)
      throws Utils::SystemError;

    // {
    //    "excludes": [str, ]
    //    "skip_scan": bool
    // }
    void Backup(string jsonParams)
      throws Utils::SystemError;

    // {empty json}
    void CancleBackup(string jsonParams)
      throws Utils::SystemError;

    // {
    //    "step": [str, str]
    //    "skip_scan": bool
    //    "current_sync_bytes": int
    //    "current_percent": str        88%
    //    "current_speed": str          3.9MB/s
    //    "current_sync_files: int      当前已传文件数 (xfr#63797)
    //    "to_chk_current: int          待检查的文件数
    //    "to_chk_total": int           列表中文件总数 (to-chk=0/4)
    //    "finished_successful": bool
    //    "finished_description"：str   错误描述
    //    "finished_debug": str         调试信息
    // }
    string QueryBackupStatus()
      throws Utils::SystemError;

    void Shutdown();

  };

};