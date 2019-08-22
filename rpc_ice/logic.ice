#pragma once

#include "utils.ice"
#include "perpcice.ice"

module BoxLogic {

  sequence<string> MACs;

  struct AgentIdentification {
    string  Name;
    MACs    Hardware;
  };

  enum DiskType {
    RAW = 0,
    MBR = 1,
    GPT = 2,
  };

  enum DiskStatus {
    ErrorOccurred         = 0,  //驱动发生错误，不能备份
    Unsupported           = 1,  //不支持的磁盘，不备份该磁盘
    NotExistLastSnapshot  = 2,  //未备份过的磁盘
    Backuping             = 3,  //正在备份中
    CDPing                = 4,  //正在CDP模式下
    LastSnapshotIsNormal  = 5,  //上一次快照点是普通快照
    LastSnapshotIsCDP     = 6,  //上一次快照点是CDP模式
  };

  struct CDPSnapshot {
    bool    setByRestore  = false;
    string  token         = "invalid";  //当setByRestore为true时，该值为还原任务的Token；当setByRestore为false时，该值为上次CDP使用的Token
    long    seconds       = -1;         //POSIX time，当setByRestore为true时有效
    int     microseconds  = -1;         //当setByRestore为true时有效
  };

  struct DiskDetail {
    string      name;                     //随机生成的字符串，不含'\0'最大32byte，大小写敏感
    DiskStatus  status;
    DiskType    type;
    long        numberOfSectors;          //磁盘扇区数大小
    bool        bootDevice;               //是否为启动设备
    string      lastSnapshot = "invalid"; //当status为LAST_SNAPSHOT_IS_NORMAL时候有效
    CDPSnapshot cdpSnapshot;              //当status为LAST_SNAPSHOT_IS_CDP时候有效
  };

  struct Disk {
    int         id;
    DiskDetail  detail;
  };

  sequence<Disk> Disks;

  struct AgentModuleError {
    string  moduleName;
    string  description;
    string  debug;
    long    rawCode;
  };

  enum BackupProgressCode {
    UnknownBackupProgressCode = 0,
    ScanningDuplicateFile     = 1,
    AnalyzingDuplicateFile    = 2,
    CreatingDataBitmap        = 3,
    CreatingDiskSnapshot      = 4,
    TransitingData            = 5,
  };

  struct BackupProgress {
    BackupProgressCode  code;
    long                progressIndex;
    long                progressTotal;
  };

  enum BackupFinishCode {
    Successful    = 0,
    UserCancel    = 1,
    Failed        = 2,
    Error         = 3, 
  };

  struct CDPConfig {
    byte    mode  = 0; 
    string  ip    = "invalid";
    short   port  = -1;
    int     socketNumber  = -1;
    int     cacheMaxBytes = -1;
    int     netTimeouts   = -1;  //second
    string  token = "invalid";
  };

  struct RestoreProgress {
    long  remainingBytes;
    long  totalBytes;
  };

  enum RestoreStageCode {
    FinishFailed      = 0,
    FinishOk          = 1,
    UmountAllVolumes  = 2,
    Started           = 3,
  };

  struct LastCdpDetail {
    string  token;
    long    seconds;
    int     microseconds;
  };

  //Agent的当前状态：
  //  "off_line": 离线
  //  "error"   : 驱动启动失败，请检查AgentModuleError
  //  "idle"    : 空闲
  //  "backup"  : 备份中
  //  "restore" ：还原中
  //  "cdp_syn" : 同步CDP保护中
  //  "cdp_asy" : 异步CDP保护中
  //  "v_restore" ：卷还原中
  sequence<string> AgentStatus;

  interface Logic {

    void ping();

    string queryHostName(AgentIdentification ident, string info)
      throws Utils::SystemError;

    bool login(string hostName, string remoteIp, string localIp, int tunnelIndex)
      throws Utils::SystemError;

    void logout(string hostName);

    string queryHostSoftIdent(string hostName)
      throws Utils::SystemError;

    void reportAgentModuleError(string hostName, AgentModuleError error);

    void reportBackupProgress(string hostName, BackupProgress progress);

    void reportBackupFinish(string hostName, BackupFinishCode code)
      throws Utils::SystemError;

    void reportVolumeRestoreStatus(string peHost, RestoreStageCode code, string msg, string debug)
      throws Utils::SystemError;

    void clearAllHostSession(); //agent与pe-agent都需要清理

    string peLogin(PerpcIce::PeGuestInfo info, string remoteIp, string localIp, int tunnelIndex, optional(1) string moreInfo)
      throws Utils::SystemError;

    void peLogout(string peName);

    //  更新CDP的Token
    //  背景：当CDP文件报告写满的时候，需要创建一个新的CDP文件存放数据
    //  传入参数：
    //    token：Agent使用的Token 参考KTService::Token.token
    //    lastFilePath：参考KTService::Token.snapshot
    //  实现细节：
    //    该调用会触发业务逻辑同步调用KTService::KTS::update接口
    void updateCDPToken(string token, string lastFilePath)
      throws Utils::SystemError;

    void updateTrafficControl(string token, long ioSession)
      throws Utils::SystemError;

    void updateRestoreToken(string updateConfig)
      throws Utils::SystemError;

    //  关闭CDP的Token
    //  背景：当CDP对应的Token暂时不使用时，需要关闭当前CDP，释放资源
    //  传入参数：
    //    token：Agent使用的Token 参考KTService::Token.token
    //  实现细节：
    //    该调用会触发业务逻辑同步调用KTService::KTS::update接口
    void closeCDPToken(string token)
      throws Utils::SystemError;

    //  更新还原时（CDP备份时）的Token信息
    //  背景：1.当还原时（CDP备份时），客户端驱动会发送携带Token的读（写）请求；如果这个Token不在内存的TokenPool中，则需要从业务逻辑层获取Token对应的快照点信息
    //        2.当还原时，业务逻辑需要裁定一个未还原完成的任务不再有效，则需要功能模块定期（参考KTService::Token.keepAliveIntervalSeconds）报告该Token正在使用
    //  传入参数：
    //    token：Agent使用的Token 参考KTService::Token.token
    //  实现细节：
    //    该调用会触发业务逻辑同步调用KTService::KTS::update接口
    void refreshSnapshotToken(string token)
      throws Utils::SystemError;

    void reportRestoreStatus(string token, RestoreProgress progress, bool finished, optional(1) string hostIdent)
      throws Utils::SystemError;

    string QueryJsonData(string hostName, string inputJson)
      throws Utils::SystemError;

    void startKvm(string peHostIdent)
      throws Utils::SystemError;

    void fetchProxyEndPoints()
      throws Utils::SystemError;

    LastCdpDetail queryLastCdpDetailByRestoreToken(string token)
      throws Utils::SystemError;

    bool queryLastCdpDetailByCdpToken(string token, string hostName, out LastCdpDetail detail)
      throws Utils::SystemError;

    string queryNetworkTransmissionType(string info)
      throws Utils::SystemError;

    int dataQueuingReport(string jsonContent)
      throws Utils::SystemError;

    string getHashFilePathByRestoreToken(string token)
      throws Utils::SystemError;

    void VmwareAgentReport(string jsonContent)
      throws Utils::SystemError;

  };

  sequence<string> Paths;
  sequence<string> StringList;

  struct Hardware {
    string      Type;   //"net", "disk"
    string      Vid;    //厂商ID
    StringList  HWIds;
    StringList  CompatIds;
  };
  sequence<Hardware> Hardwares;

  struct IPConfig {
    string      ipAddress;
    string      subnetMask;
    string      gateway;
    string      nameServer;
    string      multiInfos;
    string      hardwareConfig;
  };
  sequence<IPConfig> IPConfigs;
  sequence<byte> BinaryStream;

  interface LogicInternal {

    string pathJoin(Paths paths);

    bool isFileExist(string path);

    bool AllFilesExist(Paths paths);

    bool isFolderExist(string path);

    void makeDirs(string path, bool existOk, short mode);

    void remove(string path);

    void copy(string params)
      throws Utils::SystemError;

    void findFiles(string params, out Paths paths);

    string queryCdpTimestampRange(string path, bool discardDirtyData)
      throws Utils::SystemError;

    string queryCdpTimestamp(string path, string timestamp)
      throws Utils::SystemError;

    string formatCdpTimestamp(string timestamp)
      throws Utils::SystemError;

    void mergeCdpFile(string params)
      throws Utils::SystemError;

    bool isHardwareDriverExist(Hardware hardware, string osType, string osBit)
      throws Utils::SystemError;

    string GetDriversVersions(Hardware hardware, string osType, string osBit)
      throws Utils::SystemError;

    bool ChkIsSubId(Hardware hardware)
      throws Utils::SystemError;

    string GetDriversSubList(string userSelect)
      throws Utils::SystemError;

    void generatePeStageIso(string isoWorkerFolderPath, string isoFilePath, Hardwares hardwares, IPConfigs ipconfigs, StringList pciBusDeviceIds, string osType, string osBit, string driverIds, string jsonConfigure)
      throws Utils::SystemError;

    string runRestoreKvm(string params)
      throws Utils::SystemError;

    string getCurrentNetworkInfos()
      throws Utils::SystemError;

    void setNetwork(string setting)
      throws Utils::SystemError;

    string enumStorageNodes()
      throws Utils::SystemError;

    string getLocalIqn()
      throws Utils::SystemError;

    void setLocalIqn(string iqn)
      throws Utils::SystemError;

    void setGlobalDoubleChap(string userName, string password)
      throws Utils::SystemError;

    bool getGlobalDoubleChap(out string userName, out string password)
      throws Utils::SystemError;

    string loginExternalDevice(string remoteIp, int remotePort, bool useChap, string userName, string password)
      throws Utils::SystemError;

    void logoutExternalDevice(string iqn)
      throws Utils::SystemError;

    void refreshExternalDevice(string iqn)
      throws Utils::SystemError;

    void formatAndInitializeStorageNode(string node)
      throws Utils::SystemError;

    void mountStorageNode(string node)
      throws Utils::SystemError;

    void unmountStorageNode(string node)
      throws Utils::SystemError;

    int runCmd(string cmd, bool shell, out StringList lines)
      throws Utils::SystemError;

    string CmdCtrl(string cmdinfo)
      throws Utils::SystemError;

    void setPasswd(string passwd)
      throws Utils::SystemError;

    string getPasswd()
      throws Utils::SystemError;

    void calcClusterTime0Hash(string config)
      throws Utils::SystemError;

    void generateClusterDiffImages(string config)
      throws Utils::SystemError;

    void mergeCdpFiles(string config)
      throws Utils::SystemError;

    void cutCdpFile(string config)
      throws Utils::SystemError;

    int getRawDiskFiles(string binpath,string destpath)
      throws Utils::SystemError;

    string NbdFindUnusedReverse()
      throws Utils::SystemError;

    void NbdSetUnused(string deviceName)
      throws Utils::SystemError;

    void NbdSetUsed(string deviceName)
      throws Utils::SystemError;

    string queryTakeOverHostInfo(string queryString)
      throws Utils::SystemError;

    void mergeQcowFile(string jsonInput)
      throws Utils::SystemError;

    string startBackupOptimize(string jsonInput)
      throws Utils::SystemError;

    void stopBackupOptimize(string jsonInput)
      throws Utils::SystemError;

    void mergeHashFile(string jsonInput)
      throws Utils::SystemError;

    void generateBitMapFromQcowFile(string jsonArgs)
      throws Utils::SystemError;

    long fromMapGetQcowMaxSize(string mapPath)
      throws Utils::SystemError;

    void reorganizeHashFile(BinaryStream bitmap, string jsonInput)
      throws Utils::SystemError;

    void reorganizeHashFilev2(string bitmapPath, string jsonInput)
      throws Utils::SystemError;

    long hash2Interval(string jsonInput)
      throws Utils::SystemError;

    string exportSnapshot(string jsonInput)
      throws Utils::SystemError;

    string getAllTapeJson()
      throws Utils::SystemError;

    string getAllMediumxJson()
       throws Utils::SystemError;

    string archiveMediaOperation(string jsonInput)
      throws Utils::SystemError;

    string getArchiveFileMetaData(string jsonInput)
      throws Utils::SystemError;

    string genArchiveQcowFile(string jsonInput)
      throws Utils::SystemError;

    string fileBackup(string jsonInput)
      throws Utils::SystemError;

    string kvmRpc(string jsonInput)
      throws Utils::SystemError;
  };

  interface Setup {

    void startSetup(string session, string flagJson)
      throws Utils::SystemError;

    void cancelSetup(string session)
      throws Utils::SystemError;

  };

};