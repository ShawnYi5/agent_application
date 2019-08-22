#pragma once

#include "utils.ice"

module IMG {

  sequence<byte> BinaryStream;

  struct DuplicateFileSector
  {
    long    diskByteOffset;
    long    diskBytes;
    long    fileByteOffset;
    string  fileIdent;
  }; 

  sequence<DuplicateFileSector> DuplicateFileSectors;

  struct FileSector
  {
    long diskByteOffset;
    long diskBytes;
  }; 

  sequence<FileSector> FileSectors;

  struct ImageSnapshotIdent
  {
    string path;
    string snapshot;
  };

  //最早的快照点在最前面
  sequence<ImageSnapshotIdent> ImageSnapshotIdents;

  sequence<long> BlockIndexes;

  interface ImgService {

    // flag 为不超过255字符的字符串，表明调用者的身份，格式为 "模块名|创建原因"
    long create(ImageSnapshotIdent ident, ImageSnapshotIdents lastSnapshot, long diskByteSize, string flag)
      throws Utils::SystemError;

    int setUsedBlockBitmap(long handle, BinaryStream bitmap, bool completed)
      throws Utils::SystemError;

    idempotent int cleanUsedBlockBitmap(long handle, BlockIndexes indexes)
      throws Utils::SystemError;

    int setDuplicateFileSectors(long handle, DuplicateFileSectors sectors, bool completed)
      throws Utils::SystemError;

    // flag 为不超过255字符的字符串，表明调用者的身份，格式为 "PiD十六进制pid 模块名|创建原因"
    long open(ImageSnapshotIdents ident, string flag)
      throws Utils::SystemError;

    // 第一次调用时，index必然填写0，函数返回下次调用时需要使用的index。
    // 如果数据发送到最后一块，则 finish 设置为true，否则为false。
    // 当函数内部发生错误时，函数返回0。
    // 每块为64KByte
    int getTotalUesdBlockBitmap(long handle, int index, out BinaryStream bitmap, out bool finish)
      throws Utils::SystemError;

    long getAllFileSectors(long handle, long index, out FileSectors sectors, out bool finish)
      throws Utils::SystemError;

    idempotent int read(long handle, long byteOffset, int byteSize, out BinaryStream data)
      throws Utils::SystemError;

    idempotent int readEx(long handle, long byteOffset, int byteSize, out BinaryStream data)
      throws Utils::SystemError;

    idempotent int write(long handle, long byteOffset, BinaryStream data)
      throws Utils::SystemError; 

    idempotent int writeCdp(long handle, long byteOffset, BinaryStream data, bool enableTime, long timeSeconds, int timeMicroseconds, bool IgnoreQuota)
      throws Utils::SystemError;
	  
    idempotent int writeCdpByIndex(long handle, long byteOffset, BinaryStream data, long index, long rev1, long rev2)
      throws Utils::SystemError;

	 idempotent int writeCdpByTmeAndIndex(long handle, long byteOffset, BinaryStream data, bool enableTime, long timeSeconds, int timeMicroseconds, bool IgnoreQuota, long index, long rev1, long rev2)
      throws Utils::SystemError;
	  
    idempotent void close(long handle, bool success)
      throws Utils::SystemError;

    idempotent long GetSnSize(long handle)
      throws Utils::SystemError;

    int DelSnaport(ImageSnapshotIdent ident)
      throws Utils::SystemError;

    int RenameSnapshot(ImageSnapshotIdent ident, string newSnapshot)
      throws Utils::SystemError;

    //GetOnSnMapFile 获取一个 map 表，可能是 qcow,可能是 cdp
    string GetOnSnMapFile(ImageSnapshotIdent ident)
      throws Utils::SystemError;
  };
};
