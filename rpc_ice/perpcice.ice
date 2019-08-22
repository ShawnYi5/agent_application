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
    int               Address;        // -1: ��Ч
    int               UINumber;       // -1: ��Ч
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

      //  ����ֵҲΪjson��ʽ�ַ���
      //  ����1���ļ���д
      //    ����ֵΪ��json
      //    ��������ʱ�׳��쳣
      //    inputJson ��ʽ��
      //      {
      //        "type": "read_exist",           ��ѡ���� "read_exist","write_exist","write_new","get_size"
      //        "pathPrefix": "current",        ��ѡ���� "current"(Agent����Ŀ¼),"temp"(��ʱĿ¼)
      //        "path": "aaa\1.txt",            ·�����ļ��б�ʾ��windows��"\"
      //        "byteOffset": "123456"          �ֽ�ƫ�ƣ�ʮ�����ַ���
      //        "bytes": "123"                  ����Ϊ "read_exist" ʱ��Ч����Ҫ��ȡ�Ĵ�С
      //      }
      //    outputJson ��ʽ��
      //      {
      //        "Bytes": "0xFDA"                "get_size" �ķ���ֵ��ʮ�������ַ���
      //      }
      //  ����2����ȡ������ʶ
      //    inputJson :  {"type": "get_soft_ident"}
      //    outJson : {"soft_ident": "Gxxxxxxxxxx"}
      //  ����3�� ��ȡ�������ʵ��û���ʶ
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