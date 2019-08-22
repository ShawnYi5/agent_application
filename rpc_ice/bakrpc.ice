#pragma once

#include "utils.ice"

module bakrpc{

  sequence<byte> BinaryStream;

  interface BackupRPC{

    int callFunction(string callJson, string inJson, BinaryStream inRaw, out string outJson, out BinaryStream outRaw)
      throws Utils::SystemError;
  };

};

module kvm4remote{ 

  sequence<byte> BinaryStream;

  interface KVM{

    void SetRemoteCallable(string ident, Utils::Callable* callable)
      throws Utils::SystemError;

    void CleanRemoteCallable(string ident);

    Utils::Callable* getKVMCallable()
      throws Utils::SystemError;
  };

};