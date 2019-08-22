#pragma once

#include <Ice/Identity.ice>
#include "utils.ice"
#include "img.ice"
#include "logic.ice"
#include "box_api.ice"

module VpsAgent {

  interface Services {
    idempotent void ping();
  };

  sequence<byte> BinaryStream;

  /*
    * 可标识range不超过2^32-1个扇区（512B per sector 约 1.99T）
    */
  struct SectorRange {
    long  startSectorOffset;
    int   numberOfSectors;
  };

  struct LargeSectorRange {
    long startSectorOffset;
    long numberOfSectors;
  };

  struct DataLocation {
    int diskIndex;
    int diskBlockOffset; //64KB per block，可标识到 64TB
  };

  struct DataBlock {
    DataLocation location;
    BinaryStream data;
  };

  struct PostSector {
    int   type;
    int   diskIndex; 
    int   byteOffsetInBuffer;
    int   numberOfByteInBuffer;
    long  sectorOffset;
    short numberOfSectors;
    };

  sequence<PostSector> PostSectors;

  struct PostExtData {
    int   diskIndex;
    long  sectorOffset;
    short numberOfSectors;
    int   extType;
    BinaryStream extData;
  };
  sequence<PostExtData> PostExtDataVector;

  struct GetExtData {
    int   diskIndex;
    int   extType;
    long  sectorOffset;
    int   bitCount;
  };
  sequence<GetExtData> GetExtDataVector;

  interface Backup {

    //传备份的数据
    idempotent void PostSectorData(int diskIndex, SectorRange range, ["cpp:array"] BinaryStream data)
      throws Utils::SystemError;

    //传备份的数据
    idempotent void PostSectorDataEx(int type, int diskIndex, SectorRange range, ["cpp:array"] BinaryStream data)
      throws Utils::SystemError;

    //传备份的数据
    idempotent void PostSectorDataExV2(PostSectors sectors, ["cpp:array"] BinaryStream data)
      throws Utils::SystemError;

    //传备份的hash等扩展数据
    idempotent void PostBakDataExt(PostExtDataVector extDataVector)
      throws Utils::SystemError;

    //返回备份的hash等扩展数据
    idempotent bool GetBakDataExt(GetExtDataVector extTypeVector, out PostExtDataVector extDataVector)
      throws Utils::SystemError;

    //上传本次备份的块位图
    void PostUsedBlockBitmap(int diskIndex, BinaryStream bitmap, bool completed)
      throws Utils::SystemError;

    //上传去重文件扇区映射关系 
    void PostDuplicateFileSectors(int diskIndex, IMG::DuplicateFileSectors sectors, bool completed)
      throws Utils::SystemError;

    //上传记录“本地文件列表”的文件
    //参考DuplicateFilePool中queryFilesFromClient接口inPath参数
    void PostCurrentFileList(BinaryStream bitmap, bool completed)
      throws Utils::SystemError;

    //获取记录“可能去重文件列表”的文件
    //参考DuplicateFilePool中queryFilesFromClient接口outPath参数
    //返回值表示是否是最后一块数据
    bool GetFileListFromDuplicateFilePool(out BinaryStream bitmap)
      throws Utils::SystemError, Utils::NeedRetryLaterError;

    //备份的状态。
    idempotent void ReportStatus(BoxLogic::BackupProgress progress)
      throws Utils::SystemError;

    //备份完成
    idempotent void Exit(BoxLogic::BackupFinishCode code)
      throws Utils::SystemError;

  };

  interface Restore {

    //获取磁盘已使用位图
    idempotent int getUesdBlockBitmap(string token, int index, out BinaryStream bitmap)
      throws Utils::SystemError;

    //报告还原阶段状态
    idempotent void reportStatus(BoxLogic::RestoreStageCode code, string msg, string debug)
      throws Utils::SystemError;

  };

  /**
    * 关键模块发生错误
    */
  exception AgentModuleError extends Utils::SystemError {
    string moduleName;
  };

  struct SnapshotName {
    int                 diskIndex;
    string              diskIdent;        //如果传入的磁盘标识名与本地的不符合，表示重新制作基础备份
    string              snapshot;
    bool                startCDP = false; //是否开启CDP模式
    BoxLogic::CDPConfig cdpConfig;        //当startCDP为true时有效
  };

  sequence<SnapshotName> SnapshotNames;

  struct SnapshotConfig {
    int                 diskIndex;
    string              jsonConfig;
  };

  sequence<SnapshotConfig> SnapshotConfigs;

  enum BackupErrorType {
    SystemError = 1,  // 1||message||debug||raw_code
    SbdError = 2,     // 2||error_code||message
    NetError = 3,     // 3||error_name||message
    DriverError = 4   // 4||Region||User||System
  };

  interface AgentReceiver
  {
      idempotent void check() //调用其它接口前需要先调用该接口，检查链路与驱动模块
        throws AgentModuleError;

      idempotent string JsonFunc(string InputParam)
        throws Utils::SystemError;

      idempotent string QuerySystemInfo()
        throws Utils::SystemError;

      idempotent void QueryDisksStatus(out BoxLogic::Disks disks, out optional(1) string more)
        throws Utils::SystemError;

      void DoBackup(SnapshotNames snapshots, Backup* prx)
        throws Utils::SystemError;

      void DoBackupEx(SnapshotNames snapshots, SnapshotConfigs configs, Backup* prx, optional(1) string jsonConfig)
        throws Utils::SystemError;

      idempotent string GetLastBackupError();

      idempotent string GetLastCdpError();

      int StartAgentPe(out string peHostIdent)
        throws Utils::SystemError;

      idempotent void CancelBackup()
        throws Utils::SystemError;

      idempotent void NotifyHighPriority(string diskIdent, long byteOffset)
        throws Utils::SystemError;

      idempotent BoxLogic::AgentStatus GetStatus();

      idempotent void StopCdpStatus();

      bool PackDebugFiles();

      idempotent int FetchDebugPacket(int index, out BinaryStream data);

      // {
      //     "volumes": [
      //         {
      //             "device_name": "(string_volume_device_name)",
      //             "display_name": "(string_display_name)",
      //             "disks": [
      //                 {
      //                     "disk_number": "(int_disk_number)",
      //                     "ranges": [
      //                         {
      //                             "sector_offset": "(string_long_xxx)",
      //                             "sectors": "(string_long_yyy)"
      //                         }
      //                     ]
      //                 }
      //             ],
      //             "mount_point_after_restore": "(string_volume_mount_point_path)",
      //             "mount_fs_type_after_restore": "string_fs_type",
      //             "mount_fs_opts_after_restore": "string_fs_opts"
      //         }
      //     ],
      //     "disks": [
      //         {
      //             "disk_number": "(int_disk_number)",
      //             "disk_token": "(string_token)",
      //             "disk_bytes": "(string_long_xxx)",
      //             "timestamp": "(string_long_xxx)"
      //         }
      //     ],
      //     "config": {
      //         "aio_ip": "(ip)",
      //         "aio_port": "(int_port)",
      //         "sockets": "(int_count)"
      //     }
      // }
      void DoRestore(string json, Restore* prx)
        throws Utils::SystemError;

      idempotent void CancelRestore()
        throws Utils::SystemError;

      idempotent int GetServiceList(out Box::ServiceInfoStatusS ServiceList)
        throws Utils::SystemError;

      idempotent int GetTcpListenList(Box::vectorINT portList,out Box::vectorINT pidList)
        throws Utils::SystemError;

      idempotent int StartServiceSync(string ServiceName)
        throws Utils::SystemError;

      idempotent int StopServiceSync(string ServiceName)
        throws Utils::SystemError;

      idempotent int StartHttpDServiceAsync(int port, BinaryStream bs)
        throws Utils::SystemError;

      idempotent int GetHttpDServiceListSync(out Box::vectorINT pidList)
        throws Utils::SystemError;

      idempotent int StopAllHttpDServiceSync()
        throws Utils::SystemError;

      idempotent int testdisk(int diskIndex, long sectorOffset, short numberOfSectors)
        throws Utils::SystemError;

      idempotent int readdisk(int diskIndex, long sectorOffset, short numberOfSectors, out BinaryStream bs)
        throws Utils::SystemError;

      idempotent int writedisk(int diskIndex, long sectorOffset, short numberOfSector, BinaryStream bs)
        throws Utils::SystemError;

      //  返回值也为json格式字符串
      //  功能1：文件读写
      //    返回值为空json
      //    发生错误时抛出异常
      //    inputJson 格式：
      //      {
      //        "type": "read_exist",           可选类型 "read_exist","write_exist","write_new","get_size"
      //        "pathPrefix": "current",        可选类型 "current"(Agent运行目录),"temp"(临时目录)
      //        "path": "aaa\1.txt",            路径，文件夹表示用windows的"\"
      //        "byteOffset": "123456"          字节偏移，十进制字符串
      //        "bytes": "123"                  类型为 "read_exist" 时有效，需要读取的大小
      //      }
      //    outputJson 格式：
      //      {
      //        "Bytes": "0xFDA"                "get_size" 的返回值，十六进制字符串
      //      }
      idempotent string JsonFuncV2(string inputJson, BinaryStream inputBs, out BinaryStream outputBs)
        throws Utils::SystemError;

  };

  interface Session 
  {
    idempotent string QueryName();

    idempotent string QueryIdentity();

    idempotent string QuerySoftIdent();

    idempotent string QueryJsonData(string inputJson)
      throws Utils::SystemError;

    void destroy();

    void initiateReceiver(Ice::Identity ident) //AgentReceiver
      throws Utils::SystemError;

    idempotent void refresh();

    idempotent void reportRestoreStatus(string token, BoxLogic::RestoreProgress progress, bool finished)
      throws Utils::SystemError;

    idempotent BoxLogic::LastCdpDetail queryLastCdpDetailByRestoreToken(string token)
      throws Utils::SystemError;

    idempotent bool queryLastCdpDetailByCdpToken(string token, out BoxLogic::LastCdpDetail detail)
      throws Utils::SystemError;

    idempotent void setPreReadBitmap(string token, long index, BinaryStream bitmap)
      throws Utils::SystemError;
  };

  struct AgentIdentification {
    BoxLogic::AgentIdentification ident;
    string                        Identity;
  };

  interface SessionFactory 
  {
    // info 为json格式的系统信息
    Session* create(AgentIdentification id, string info)
      throws Utils::SystemError;
  };
};
