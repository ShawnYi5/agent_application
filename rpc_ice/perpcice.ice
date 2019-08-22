#pragma once

#include <Ice/Identity.ice>
#include "utils.ice"

module PerpcIce {

  sequence<byte> BinaryStream;

  struct ExcludeBrokenBlock {
    string  diskToken;
    long  blockOffset;
    BinaryStream bitmap;
  };

  sequence<ExcludeBrokenBlock> ExcludeBrokenBlocks;
  
  struct ExcludeBlockRun {
    string  diskToken;
    long  blockOffset;
    long  blockCount;
  };
  
  sequence<ExcludeBlockRun> ExcludeBlockRuns;
  
  
  struct PeDiskInfo {
    int   diskID;
    long  diskSecCount;
  };

  sequence<PeDiskInfo> PeDiskInfos;

  struct PeGuestInfo {
    PeDiskInfos   diskInfos;
    int           bootDiskId;
    int           loginType;  // 0: pe, 1: agent
  };

  struct PeDiskToken {
    int     diskID;
    string  token;
    string  diskGUID;
  };

  sequence<PeDiskToken> PeDiskTokens;

  struct PeRestoreInfo {
    string        szServerIPAddr;
    int           dwServerPortNumber;
    int           dwSocketConnectCount;
    int           dwOsDiskID;
    PeDiskTokens  tokens;
  };

  sequence<string> HardwareIds;
  sequence<string> HardwareCompatIds;

  struct HWInfo {
    string            szDeviceInstanceID;
    string            szDescription;
    string            szLocationInfo;
    string            szContainerID;
    string            szMacAddress;
    string            szService;
    int               parentDevLevel;
    int               Address;        // -1: 无效
    int               UINumber;       // -1: 无效
    HardwareIds       HWIds;
    HardwareCompatIds CompatIds;
  };

  sequence<HWInfo> HWInfos;

  struct NetAdapterInfo {
    string            szDeviceInstanceID;
    string            szDescription;
    string            szGuid;
    string            szNetType;
    string            szMacAddress;
    bool              isConnected;
  };

  sequence<NetAdapterInfo> NetAdapterInfos;

  interface PeGuestReceiver {
      idempotent int ReadDisk(string token, long LBA, int dwSectorCount, out BinaryStream pBuf)
        throws Utils::SystemError;

      idempotent int WriteDisk(string token, long LBA, int dwSectorCount, BinaryStream pBuf)
        throws Utils::SystemError;

      idempotent void SetRestoreExcludeInfo(ExcludeBrokenBlocks brokenBlocks, ExcludeBlockRuns blockRuns)
        throws Utils::SystemError;

      idempotent void KvmEnd()
        throws Utils::SystemError;

      idempotent int GetClassHWInfo(string classname, int requestParentLevel, out HWInfos hwinfo)
        throws Utils::SystemError;

      idempotent int GetNetAdapterInfo(out NetAdapterInfos adapterInfos)
        throws Utils::SystemError;

      idempotent void SetRestoreInfo(PeRestoreInfo restoreInfo)
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
      //  功能2：获取主机标识
      //    inputJson :  {"type": "get_soft_ident"}
      //    outJson : {"soft_ident": "Gxxxxxxxxxx"}
      //  功能3： 获取启动介质的用户标识
      //    inputJson : {"type": "get_user_fingerprint"}
      //    outJson: {"user_fingerprint": "*xxxxxxxxxx"}
      idempotent string JsonFunc(string inputJson, BinaryStream inputBs, out BinaryStream outputBs)
        throws Utils::SystemError;
  };

  interface PeSession {

    void InitiatePeReceiver(Ice::Identity ident) //PeGuestReceiver
      throws Utils::SystemError;

    idempotent void GetPeHostIdent(out string peHostIdent);

    idempotent void UnInit(int dwStatus);

    //TODO: will remove
    idempotent int GetBootList(int index, out string bootlist)
      throws Utils::SystemError, Utils::NeedRetryLaterError;

    idempotent int GetKvmBitmapFile(int index, out BinaryStream data)
      throws Utils::SystemError, Utils::NeedRetryLaterError;


    idempotent int ReadDiskData(string token, long LBA, int dwSectorCount, out BinaryStream pBuf)
      throws Utils::SystemError;

    idempotent int ReadKvmBootData(int threadIndex, int blockIndex , out bool isEnd, out bool isSkip, out string diskToken, out long LBA, out int dwSectorCount, out BinaryStream data)
      throws Utils::SystemError;

    idempotent int getUesdBlockBitmap(string token, int index, out BinaryStream bitmap)
      throws Utils::SystemError;

    idempotent void Refresh();

    void StartKvm();

    void destroy();
  };

  interface PeSessionFactory {

    PeSession* CreateSession(PeGuestInfo guestInfo, int kvmSocketCount, optional(1) string moreInfo)
      throws Utils::SystemError;

  };

};