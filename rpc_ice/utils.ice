#pragma once

module Utils {
  exception ErrorBase {
    string description;
    string debug;
  };

  /**
    * 系统调用失败错误
   */
  exception SystemError extends ErrorBase {
    long rawCode;
  };

  exception NeedRetryLaterError extends ErrorBase { };

  exception CreateSnapshotImageError extends SystemError { };

  exception OperationNotExistError extends ErrorBase { };

  sequence<byte> BinaryStream;

  interface Callable {

    void execute(string callJson, string inputJson, BinaryStream inputBs, out string outputJson, out BinaryStream outputBs)
      throws SystemError;

  };

};
