#pragma once

#include "utils.ice"
#include "perpcice.ice"
#include "logic.ice"
#include "img.ice"
#include <Ice/BuiltinSequences.ice>

module Box {

  sequence<byte> BinaryStream;

  struct BackupFile {
    int                       diskIndex;
    string                    diskIdent;
    IMG::ImageSnapshotIdent   snapshot;
    IMG::ImageSnapshotIdents  lastSnapshot;
    long                      diskByteSize;
    bool                      enableCDP = false;
    BoxLogic::CDPConfig       cdpConfig; //当enableCDP为true时有效
    string                    jsonConfig;
  };

  sequence<BackupFile> BackupFiles;

  struct RestoreFile {
    int                      diskIndex;
    long                     diskBytes;
    IMG::ImageSnapshotIdents snapshot;
  };

  sequence<RestoreFile> RestoreFiles;

  struct ServiceInfoStatus {
    string              lpDisplayName;
    string              lpServiceName;
    int                 dwServiceType;
    int                 dwCurrentState;
    int                 dwWin32ExitCode;
    int                 dwServiceSpecificExitCode;
    int                 dwProcessId;
    int                 dwServiceFlags;
  };
  
  sequence<ServiceInfoStatus>   ServiceInfoStatusS;
  sequence<int>                 vectorINT;

  interface Apis {

    void ping();

    void reloginAllHostSession(int delaySeconds);

    bool isAgentLinked(string hostName);

    BoxLogic::AgentStatus GetStatus(string hostName);

    void queryDisksStatus(string hostName, out BoxLogic::Disks disks, out optional(1) string more)
      throws Utils::SystemError;

    string JsonFunc(string hostName, string inputParam)
      throws Utils::SystemError;

    string querySystemInfo(string hostName)
      throws Utils::SystemError;

    void backup(string hostName, BackupFiles images, int kiloBytesPerSecond, optional(1) string jsonConfig)
      throws Utils::SystemError, Utils::CreateSnapshotImageError;

    void forceCloseBackupFiles(Ice::StringSeq files);

    string getBackupInfo(string hostName, string inputJson)
      throws Utils::SystemError;

    void setBackupInfo(string hostName, string inputJson)
      throws Utils::SystemError;

    string queryLastBackupError(string hostName);

    string queryLastCdpError(string hostName);

    void stopCdpStatus(string hostName)
      throws Utils::SystemError;

    void volumeRestore(string hostName, string jsonConfig, RestoreFiles images, string dummyHost)
      throws Utils::SystemError;

    void restore(string hostName, PerpcIce::PeRestoreInfo info, RestoreFiles images, string jsonConfig)
      throws Utils::SystemError;

    void setBootDataList(string hostName, string filePath)
      throws Utils::SystemError;

    void notifyHighPriority(long imageFileHandle, long byteOffset)
      throws Utils::SystemError;

    int ReadDiskWithPeHost(string peHostIdent, string token, long sectorOffset, int sectors, out BinaryStream data)
      throws Utils::SystemError;

    int WriteDiskWithPeHost(string peHostIdent, string token, long sectorOffset, int sectors, BinaryStream data)
      throws Utils::SystemError;

    bool QueryRWDiskWithPeHost(string peHostIdent, out long totalSectors, out long sentSectors)
      throws Utils::SystemError;

    void KvmStopped(string peHostIdent)
      throws Utils::SystemError;

    int GetPeHostClassHWInfo(string peHostIdent, string classname, int parentLevel, out PerpcIce::HWInfos hwinfo)
      throws Utils::SystemError;

    int GetPeHostNetAdapterInfo(string peHostIdent, out PerpcIce::NetAdapterInfos adapterInfos)
      throws Utils::SystemError;

    bool isPeHostLinked(string peHostName);

    string StartAgentPe(string hostName)
      throws Utils::SystemError;

    void fetchAgentDebugFile(string hostName, string path)
      throws Utils::SystemError;

    string queryRunnerAbsPathOnAgentSetup(string session)
      throws Utils::SystemError;

    string prepareInfoOnAgentSetup(string session, string flagJson)
      throws Utils::SystemError;

    string getFileInfoOnAgentSetup(string session, string fileName, string flagJson)
      throws Utils::SystemError;

    string searchBootFileAbsPathOnAgentSetup(string session)
      throws Utils::SystemError;

    void generateKeyInfosOnAgentSetup(string session, string absFilePath, string flagJson)
      throws Utils::SystemError;

    string openOnAgentSetup(string session, string absFilePath, string flagJson)
      throws Utils::SystemError;

    Ice::ByteSeq preadOnAgentSetup(string session, string handle, long byteOffset, int bytes)
      throws Utils::SystemError;

    void pwriteOnAgentSetup(string session, string handle, long byteOffset, int bytes, Ice::ByteSeq data)
      throws Utils::SystemError;

    void closeOnAgentSetup(string session, string handle)
      throws Utils::SystemError;

    void extractFileOnAgentSetup(string session, string absSourceFilePath, string absDestinationPath, string flagJson)
      throws Utils::SystemError;

    int executeCommandOnAgentSetup(string session, string cmd, string flagJson, out Ice::StringSeq stdout, out Ice::StringSeq stderr)
      throws Utils::SystemError;

    void reportStatusOnAgentSetup(string session, string contentJson)
      throws Utils::SystemError;

    void exitOnAgentSetup(string session, int returnCode)
      throws Utils::SystemError;

    void forceOfflineAgent(string hostName)
      throws Utils::SystemError;

    void forceOfflinePeHost(string peHostIdent)
      throws Utils::SystemError;

    void refreshNetwork();

    int GetServiceList(string hostName, out ServiceInfoStatusS ServiceList)
        throws Utils::SystemError;

    int GetTcpListenList(string hostName, vectorINT portList,out vectorINT pidList)
      throws Utils::SystemError;

    int StartServiceSync(string hostName, string ServiceName)
      throws Utils::SystemError;

    int StopServiceSync(string hostName, string ServiceName)
      throws Utils::SystemError;

    int StartHttpDServiceAsync(string hostName, int port, BinaryStream bs)
      throws Utils::SystemError;

    int GetHttpDServiceListSync(string hostName, out vectorINT pidList)
        throws Utils::SystemError;

    int StopAllHttpDServiceSync(string hostName)
      throws Utils::SystemError;

    int testDisk(string hostName, int diskIndex, long sectorOffset, short numberOfSectors)
      throws Utils::SystemError;

    int readDisk(string hostName, int diskIndex, long sectorOffset, short numberOfSectors, out BinaryStream bs)
      throws Utils::SystemError;

    int writeDisk(string hostName, int diskIndex, long sectorOffset, short numberOfSector, BinaryStream bs)
      throws Utils::SystemError;

    string JsonFuncV2(string hostName, string inputJson, BinaryStream inputBs, out BinaryStream outputBs)
      throws Utils::SystemError;

    string PEJsonFunc(string peHostIdent, string inputJson, BinaryStream inputBs, out BinaryStream outputBs)
      throws Utils::SystemError, Utils::OperationNotExistError;
  };

};