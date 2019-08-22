#pragma once

#include <Ice/Identity.ice>
#include "utils.ice"

module DuplicateFilePool 
{
  sequence<byte> BinaryStream;

  struct FileFromClient {
    int     clientFileIdent;
    string  fileFullName;
    long    fileBytes;
  };

  struct FileInPool {
    string  identInPool;      //文件在去重文件池中的唯一编码
    int     clientFileIdent;  //来自 FileFromClient
    string  fileHash;
    int     hashType;         //生成hash的方式：0为全部文件，1为文件前4KByte
  };
  
  interface UpdateProgressReceiver
  {
    void ReportProgess(bool finished, long totalFileNumber, long importedFileNumber);
  };

  interface FilePool 
  {
    //将指定目录下的升级文件导入到文件池中
    void update(string path, Ice::Identity ident)
      throws Utils::SystemError;

    //读取输入路径下的文本文件(字符格式为UTF-8，每行内容见FileFromClient，各个元素用|分隔，数字为16进制，换行用‘\n’)
    //在输出路径下新建文本文件，将文件池中存在的文件的属性写入其中（字符格式为UTF-8，每行内容见FileInPool，各个元素用|分隔，数字为16进制，hash为byte数组的16进制字符串且需要补零, 换行用‘\n’）
    void queryFilesFromClient(string inPath, string outPath)
      throws Utils::SystemError;

    //读取文件内容
    BinaryStream readFile(string identInPool, long byteOffset, int bytes)
      throws Utils::SystemError;
  };
};