#pragma once

#include "utils.ice"
#include <Ice/Identity.ice>

module CustomizedOS {

  sequence<byte> BinaryStream;

  interface MiniLoader {
    // {
    //    "async": bool
    //    "shell": bool
    //    "cmd": str
    //    "work_dir": str
    //    "timeouts_seconds": int
    // }
    // {
    //   "pid": pid
    //   "uuid": str
    //   "returned_code": int
    //   "stdout": str
    //   "stderr": str
    // }
    string popen(string jsonParams)
      throws Utils::SystemError;

    //  返回值也为json格式字符串
    //  文件读写
    //    返回值为空json
    //    发生错误时抛出异常
    //    inputJson 格式：
    //      {
    //        "type": "read_exist",           可选类型 "read_exist","write_exist","write_new","get_size"
    //        "path": "/path/filename",       路径
    //        "byteOffset": "0x1234"          字节偏移，十六进制字符串
    //        "bytes": "0x123"                类型为 "read_exist" 时有效，需要读取的大小
    //      }
    //    outputJson 格式：
    //      {
    //        "Bytes": "0xFDA"                "get_size" 的返回值，十六进制字符串
    //      }
    idempotent string rwFile(string inputJson, BinaryStream inputBs, out BinaryStream outputBs)
      throws Utils::SystemError;

    //得到CustomizedOSMiniLoaderIce.py所在的目录
    string getRunPath()
      throws Utils::SystemError;

  };

  interface CallbackSender
  {
    //MiniLoader在防火墙后面，需要主动连接一体机
    void addClient(Ice::Identity ident)
      throws Utils::SystemError;
  };
};