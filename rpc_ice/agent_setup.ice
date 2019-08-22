#pragma once

#include "utils.ice"
#include <Ice/BuiltinSequences.ice>
#include <Ice/Identity.ice>

module AgentSetup {

  interface AgentSetupReceiver
  {
    idempotent string queryRunnerAbsPath()
      throws Utils::SystemError;

    idempotent string searchBootFileAbsPath()
      throws Utils::SystemError;

    idempotent string prepareAgentInfo(string flagJson)
      throws Utils::SystemError;

    idempotent string getFileInfo(string fileName, string flagJson)
      throws Utils::SystemError;  

    idempotent void generateKeyInfos(string absFilePath, string flagJson)
      throws Utils::SystemError;

    string open(string absFilePath, string flagJson)
      throws Utils::SystemError;

    idempotent Ice::ByteSeq pread(string handle, long byteOffset, int bytes)
      throws Utils::SystemError;

    idempotent void pwrite(string handle, long byteOffset, int bytes, Ice::ByteSeq data)
      throws Utils::SystemError;

    void close(string handle)
      throws Utils::SystemError;

    void extractFile(string absSourceFilePath, string absDestinationPath, string flagJson)
      throws Utils::SystemError;

    int executeCommand(string cmd, string flagJson, out Ice::StringSeq stdout, out Ice::StringSeq stderr)
      throws Utils::SystemError;

    idempotent void reportStatus(string contentJson)
      throws Utils::SystemError;

    void exit(int returnCode);
  };

  interface AgentSetupSession 
  {
    idempotent string queryName();

    idempotent void destroy();

    idempotent void initiateReceiver(Ice::Identity ident) //AgentSetupReceiver
      throws Utils::SystemError;

    idempotent void refresh();

    idempotent void startSetup(string flagJson)
      throws Utils::SystemError;
  };

  interface AgentSetupSessionFactory 
  {
    // info 为json格式的系统信息
    AgentSetupSession* create(string info)
      throws Utils::SystemError;
  };

};