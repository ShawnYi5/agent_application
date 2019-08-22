#pragma once

#include "ImgServicePrxPool.hpp"
#include "linux_rw.h"
#include "bitmap2seg.h"
#include <json/json.h>
#include <iomanip>
#include <sstream>
#include <string.h>
#include "fileutil.h"
#include "magic_number.h"
#include "md4.h"
#include "quickHash.h"
#include "fileCompblk.h"

inline std::stringstream &bin2hex(const::VpsAgent::BinaryStream &bin, std::stringstream & ss)
{
  ss.str("");
  ss.fill('0');
  for (size_t i = 0; i < bin.size(); ++i)
  {
    ss << std::nouppercase << std::setw(2) << std::hex << (int)bin[i];
  }
  return ss;
}

inline char char_2_bin(char ch)
{
  if ('0' <= ch && ch <= '9')
  {
    return ch - '0';
  }
  if ('a' <= ch && ch <= 'f')
  {
    return ch - 'a' + 0xa;
  }
  if ('A' <= ch && ch <= 'F')
  {
    return ch - 'A' + 0xa;
  }
  return 0x0;
}

static int hexlen(char *src)
{
  int		i;
  for (i = 0; src[i]; i++)
  {
    if (('0' <= src[i] && src[i] <= '9') ||
      ('a' <= src[i] && src[i] <= 'f') ||
      ('A' <= src[i] && src[i] <= 'F'))
    {
      continue;
    }
    break;
  }
  return i;
}

static void hex2bin(char *src, ::VpsAgent::BinaryStream &oBinary)
{
  int n = hexlen(src);

  n = (n + 1) >> 1;

  oBinary.resize(n);

  for (int i = 0; i < n; i++)
  {
    oBinary[i] = (char_2_bin(src[i * 2]) << 4) | char_2_bin(src[i * 2 + 1]);
  }
  return;
}

static unsigned char read_char(unsigned char volatile *p)
{
  return *p;
}

class dedupleHashFile
{
public:
  dedupleHashFile()
  {
    _read_hashfile_mem_addr = NULL;
    _read_hashfile_max_size = _read_hashfile_file_offset = 0;
  }
  ~dedupleHashFile()
  {

  }
  void load_hash_file_to_cache()
  {
    size_t		count;
#define MAX_READ_HASH_CACHE_SIZE		(32*1024*1024)	//客户端是8M，这存32M.

    count = min((size_t)MAX_READ_HASH_CACHE_SIZE, _read_hashfile_max_size - _read_hashfile_file_offset);

    madvise(_read_hashfile_mem_addr + _read_hashfile_file_offset, _read_hashfile_file_offset, count);
    if (0 == _read_hashfile_file_offset)
    {//第一次强制读出来。
      for (size_t i = 0; i < count; i += 0x1000)
      {
        read_char(_read_hashfile_mem_addr + i);
      }
    }
    return;
  }
  unsigned int get_line_size(unsigned char *pbuf, unsigned char *end_addr)
  {
    unsigned int i;
	for (i = 0; pbuf < end_addr && pbuf[i]; i++)
    {
      if (pbuf[i] == 0xa || pbuf[i] == 0xd)
      {
        break;
      }
    }
	for (; pbuf < end_addr && pbuf[i] ; i++)
    {
      if (pbuf[i] == 0xa || pbuf[i] == 0xd)
      {
        continue;
      }
      else
      {
        break;
      }
    }
    return i;
  }
  //::VpsAgent::PostExtDataVector& dataExt
  bool get_hash_entry(int   &extType, ULONG64  &sectorOffset, ::VpsAgent::BinaryStream& extData)
  {
    ULONG64		ullCurt;
    int			hashType;
    int			line_size;
    unsigned char *pbufaddr;
    char	one_line[MAX_PATH];
    char	buftemp[MAX_PATH];
    //snprintf(buf, MAX_PATH, "0x%lx,%d,%s\n", dataExt[i].sectorOffset, EXT_DATA_MINOR_MASK(dataExt[i].extType), h.c_str());
    if (_read_hashfile_file_offset >= _read_hashfile_max_size)
    {
      return false;
    }
    pbufaddr = _read_hashfile_file_offset + _read_hashfile_mem_addr;
	line_size = get_line_size(pbufaddr, _read_hashfile_mem_addr + _read_hashfile_max_size);
    _read_hashfile_file_offset += line_size;
    one_line[MAX_PATH - 1] = 0;
    memcpy(one_line, pbufaddr, min(MAX_PATH - 2, line_size));
    ullCurt = 0;
    sscanf((const char *)one_line, "0x%lx,%d,%s,", (long unsigned int*)&ullCurt, &hashType, buftemp);//这里加","是为了更好的兼容性。
                                                                                                     //sscanf((const char *)pbufaddr, "0x%lx,%d", (long unsigned int*)&ullCurt, &hashType);//这里加","是为了更好的兼容性。
                                                                                                     //bug #2442, sscanf性能非常低下。
    sectorOffset = ullCurt;
    extType = hashType;
    hex2bin(buftemp, extData);
    return true;
  }

  void open_read_hash_file(const std::string filepath)
  {
    struct stat st;
    int		fd_read_hash = 0;
    if (stat(filepath.c_str(), &st))
    {
      return;
    }
    if (st.st_size == 0)
    {
      return;
    }
    _read_hashfile_max_size = st.st_size;
    fd_read_hash = _x_open64(filepath.c_str(), O_RDONLY);
    if (fd_read_hash <= 0)
    {
      LOG(INFO) << "open read hash file:" << filepath << " fd: " << hex << fd_read_hash;
      return;
    }
    _read_hashfile_mem_addr = (unsigned char *)mmap(NULL, _read_hashfile_max_size, PROT_READ, MAP_PRIVATE, fd_read_hash, 0);

    LOG(INFO) << "open read hash file:" << filepath << " fd: " << hex << fd_read_hash << " size: " << hex << _read_hashfile_max_size << " map ptr: " << hex << (ULONG64)_read_hashfile_mem_addr;

    ::close(fd_read_hash);
    fd_read_hash = 0;
    if (_read_hashfile_mem_addr == MAP_FAILED)
    {
      return;
    }

    _read_hashfile_file_offset = 0;

    load_hash_file_to_cache();

    return;
  }
  bool valid_data()
  {
    if (_read_hashfile_mem_addr && _read_hashfile_file_offset < _read_hashfile_max_size)
    {
      return true;
    }
    return false;
  }
  void closefile()
  {
    if (_read_hashfile_mem_addr)
    {
      munmap(_read_hashfile_mem_addr, _read_hashfile_max_size);
      _read_hashfile_mem_addr = NULL;
    }
  }

private:
  unsigned char 	*_read_hashfile_mem_addr;
  size_t			_read_hashfile_file_offset;
  size_t			_read_hashfile_max_size;
};

class ImgWrapper
{
public:
  ImgWrapper(const ImgServicePrxPoolPtr& prxes, const IMG::ImageSnapshotIdents& snapshot, const string& flag, const string& jsonConfig, int retry_times = 0)
    : _snapshot(snapshot), _prxes(prxes), _handle(0), _successful(false), _flag(flag), _write_hashfileHandle(0), _retry_times(retry_times)
  {
    _fd_pre_data = 0;
    _ullStartBit = 0;
    _ullCdpBlockIndex = 0;
    _de_duplication = 0;
    _hash_disk_data = false;
    _bakblkSegSetPtr = make_shared<SetBlkNodeSeg>();
    parseJson(jsonConfig, _read_hash_filepath, _hash_disk_data, _de_duplication, _pre_data_device);
  }

  ~ImgWrapper()
  {
    close();
  }

  void parseJson(const string& json, string& pre_deduple_hash_filepath, bool& hash_disk_data, int &de_duplication, string& pre_data_device)
  {
    Json::Reader  reader;
    Json::Value   jsonRoot;

    if (json.empty())
      return;

    if (!reader.parse(json, jsonRoot))
    {
      LOG(ERROR) << "ImgWrapper::parseJson failed, !reader.parse()";
      return;
    }
    if (jsonRoot["de_duplication"].isNull() || !jsonRoot["de_duplication"].isInt())
    {
      LOG(ERROR) << "AgentReceiverI::parseJson failed, jsonRoot[\"de_duplication\"] type error";
    }
    else
    {
      de_duplication = jsonRoot["de_duplication"].asInt();
      LOG(INFO) << "AgentReceiverI::parseJson de_duplication:" << de_duplication;
    }
    if (jsonRoot["deduple_hash_filepath"].isNull() || !jsonRoot["deduple_hash_filepath"].asCString())
    {
      LOG(ERROR) << "AgentReceiverI::parseJson failed, jsonRoot[\"deduple_hash_filepath\"] type error";
    }
    else
    {
      pre_deduple_hash_filepath = jsonRoot["deduple_hash_filepath"].asCString();
      LOG(INFO) << "AgentReceiverI::parseJson deduple_hash_filepath:" << pre_deduple_hash_filepath;
    }

    if (jsonRoot["hash_disk_data"].isNull() || !jsonRoot["hash_disk_data"].isBool())
    {
      LOG(ERROR) << "AgentReceiverI::parseJson failed, jsonRoot[\"hash_disk_data\"] type error";
    }
    else
    {
      hash_disk_data = jsonRoot["hash_disk_data"].asBool();
      LOG(INFO) << "AgentReceiverI::parseJson hash_disk_data:" << hash_disk_data;
    }

    if (jsonRoot["pre_data_device"].isNull() || !jsonRoot["pre_data_device"].asCString())
    {
      LOG(ERROR) << "AgentReceiverI::parseJson failed, jsonRoot[\"pre_data_device\"] type error";
    }
    else
    {
      pre_data_device = jsonRoot["pre_data_device"].asCString();
      LOG(INFO) << "AgentReceiverI::parseJson pre_data_device:" << pre_data_device;
    }
    if (0)
    {//debug
      de_duplication = DEDUPLE_TYPE_client_work | DEDUPLE_TYPE_COPY_ALL_DATA_WRITE_2_NEW | DEDUPLE_TYPE_HASH_verify_Before_WRITE;
      //pre_deduple_hash_filepath = "/mnt/nodes/5822ee8450474cc5a2fd09abff859d00/images/f8c88a31839a434e87d237a50e61b446/1f39e851aa464f74b95c17f0118ce2e4.qcow_89883571585e4a959db58c8eb9b19fdf.hash";
      pre_deduple_hash_filepath = "/mnt/nodes/412a65b00d9b4eeabde7dfba7b8ae595/images/f8c88a31839a434e87d237a50e61b446/726023e6fb5a4f28a811552ed4077cbf.qcow_dc28473908d74c08931e767e79f91f86.hash";
      //pre_data_device = "/dev/nbd0";
      pre_data_device = "/dev/sda";
    }
  }

  void setClose(bool successful)
  {
    _successful = successful;
  }

  bool close()
  {
    Ice::Long handle = 0;
    bool result = false;

    _dedupleFile.closefile();

    close_hashdata();

    if (_fd_pre_data)
    {
      ::close(_fd_pre_data);
      _fd_pre_data = 0;
    }

    if (_handle != 0)
    {
      LOG(INFO) << "ImgWrapper::close with (" << _successful << ")" << imgInfo();
      handle = _handle;
      _handle = 0;
    }

    if (handle != 0)
    {
      try
      {
        _prxes->allocate()->proxy()->close(handle, _successful);
        LOG(INFO) << "ImgWrapper::close returned with (" << _successful << ") 0x" << hex << handle;
        result = true;
      }
      catch (const Utils::SystemError& e)
      {
        LOG(ERROR) << "ImgWrapper::close SystemError : " << FormatError::SystemError2String(e) << imgInfo();
      }
      catch (const IceUtil::Exception& e)
      {
        LOG(ERROR) << "ImgWrapper::close Exception : " << e.ice_name() << imgInfo();
      }
      catch (const std::exception& e)
      {
        LOG(ERROR) << "ImgWrapper::close exception : " << e.what() << imgInfo();
      }
      catch (...)
      {
        LOG(ERROR) << "ImgWrapper::close unknown exception" << imgInfo();
      }
    }

    return result;
  }

  void writeWithIndex(Ice::Long byteOffset, const IMG::BinaryStream& bs, ULONG64 index, ULONG64 rev1, ULONG64 rev2)
  {
    if (_handle == 0)
    {
      throw Utils::SystemError("写入快照文件失败，无效的文件句柄", "ImgWrapper::write NULL handle", 0);
    }
    stringstream s;
    ::Ice::Int writeBytes = 0;

    try
    {
      writeBytes = _prxes->allocate()->proxy()->writeCdpByIndex(_handle, byteOffset, bs, index, rev1, rev2);
    }
    catch (const Utils::SystemError& e)
    {
      s << "ImgWrapper::write byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << bs.size() \
        << " SystemError : " << FormatError::SystemError2String(e) << imgInfo();
      if (((::Ice::Long)0xffffffffffffffe4) == e.rawCode)
      {
        throw Utils::SystemError("快照文件写入失败，存储空间不足", s.str(), e.rawCode);
      }
      else
      {
        throw Utils::SystemError("快照文件写入失败", s.str(), e.rawCode);
      }
    }
    catch (const IceUtil::Exception& e)
    {
      s << "ImgWrapper::write byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << bs.size()\
        << " Exception : " << e.ice_name() << imgInfo();
    }
    catch (const std::exception& e)
    {
      s << "ImgWrapper::write byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << bs.size()\
        << " exception : " << e.what() << imgInfo();
    }
    catch (...)
    {
      s << "ImgWrapper::write byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << bs.size()\
        << " unknown exception" << imgInfo();
    }

    if (writeBytes != static_cast<Ice::Int>(bs.size()))
    {
      if (s.str().empty())
      {
        s << "ImgWrapper::write byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << bs.size()\
          << " writeBytes != bs.size() writeBytes 0x" << hex << writeBytes << imgInfo();
      }
      throw Utils::SystemError("快照文件写入失败", s.str(), 0);
    }
  }

  void writeWithTimeAndIndex(Ice::Long byteOffset, const IMG::BinaryStream& bs, bool enableTime, ULONG64 timeSeconds, 
                int timeMicroseconds, bool IgnoreQuota, ULONG64 index, ULONG64 rev1, ULONG64 rev2)
  {
      if (_handle == 0)
      {
          throw Utils::SystemError("写入快照文件失败，无效的文件句柄", "ImgWrapper::write NULL handle", 0);
      }
      stringstream s;
      ::Ice::Int writeBytes = 0;

      try
      {
          writeBytes = _prxes->allocate()->proxy()->writeCdpByTmeAndIndex(_handle, byteOffset, bs, enableTime, timeSeconds, timeMicroseconds, 
                                                                    IgnoreQuota, index, rev1, rev2);
      }
      catch (const Utils::SystemError& e)
      {
          s << "ImgWrapper::write byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << bs.size() \
              << " SystemError : " << FormatError::SystemError2String(e) << imgInfo();
          if (((::Ice::Long)0xffffffffffffffe4) == e.rawCode)
          {
              throw Utils::SystemError("快照文件写入失败，存储空间不足", s.str(), e.rawCode);
          }
          else
          {
              throw Utils::SystemError("快照文件写入失败", s.str(), e.rawCode);
          }
      }
      catch (const IceUtil::Exception& e)
      {
          s << "ImgWrapper::write byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << bs.size()\
              << " Exception : " << e.ice_name() << imgInfo();
      }
      catch (const std::exception& e)
      {
          s << "ImgWrapper::write byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << bs.size()\
              << " exception : " << e.what() << imgInfo();
      }
      catch (...)
      {
          s << "ImgWrapper::write byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << bs.size()\
              << " unknown exception" << imgInfo();
      }

      if (writeBytes != static_cast<Ice::Int>(bs.size()))
      {
          if (s.str().empty())
          {
              s << "ImgWrapper::write byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << bs.size()\
                  << " writeBytes != bs.size() writeBytes 0x" << hex << writeBytes << imgInfo();
          }
          throw Utils::SystemError("快照文件写入失败", s.str(), 0);
      }
  }

  void write(Ice::Long byteOffset, const IMG::BinaryStream& bs)
  {
    if (_handle == 0)
    {
      throw Utils::SystemError("写入快照文件失败，无效的文件句柄", "ImgWrapper::write NULL handle", 0);
    }
    stringstream s;
    ::Ice::Int writeBytes = 0;

    try
    {
      writeBytes = _prxes->allocate()->proxy()->write(_handle, byteOffset, bs);
    }
    catch (const Utils::SystemError& e)
    {
      s << "ImgWrapper::write byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << bs.size() \
        << " SystemError : " << FormatError::SystemError2String(e) << imgInfo();
      if (((::Ice::Long)0xffffffffffffffe4) == e.rawCode) // -28
      {
        throw Utils::SystemError("快照文件写入失败，存储空间不足", s.str(), e.rawCode);
      }
      else if(((::Ice::Long)0xfffffffffffffff4) == e.rawCode) // -12
      {
        throw Utils::SystemError("快照文件写入失败，写入偏移大于磁盘大小", s.str(), e.rawCode);
      }
      else
      {
        throw Utils::SystemError("快照文件写入失败", s.str(), e.rawCode);
      }
    }
    catch (const IceUtil::Exception& e)
    {
      s << "ImgWrapper::write byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << bs.size()\
        << " Exception : " << e.ice_name() << imgInfo();
    }
    catch (const std::exception& e)
    {
      s << "ImgWrapper::write byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << bs.size()\
        << " exception : " << e.what() << imgInfo();
    }
    catch (...)
    {
      s << "ImgWrapper::write byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << bs.size()\
        << " unknown exception" << imgInfo();
    }

    if (writeBytes != static_cast<Ice::Int>(bs.size()))
    {
      if (s.str().empty())
      {
        s << "ImgWrapper::write byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << bs.size()\
          << " writeBytes != bs.size() writeBytes 0x" << hex << writeBytes << imgInfo();
      }
      throw Utils::SystemError("快照文件写入失败", s.str(), 0);
    }
  }
  void hash_verifyData(int extType, Ice::Long byteOffset, Ice::Int org_dataBytes, IMG::BinaryStream &bs,
    const::std::pair<const::Ice::Byte *, const::Ice::Byte *>& client_hashData,
    ::VpsAgent::PostExtData &Good_hashData)
  {
    stringstream s;

    size_t client_hashSize = 0;
    client_hashSize = client_hashData.second - client_hashData.first;
#define  EXT_DATA_TYPE_hash_bytes_length	( sizeof(u32) * (MD4_HASH_WORDS + 1 ) )

    if (client_hashSize != EXT_DATA_TYPE_hash_bytes_length)
    {
      s << "hash_verifyData error client_hashSize 0x" << hex << client_hashSize << imgInfo();
      LOG(ERROR) << s.str();
      throw Utils::SystemError("hash size 出错", s.str(), hash_error_and_resend_data);
      return;
    }

    Good_hashData.extData.resize(EXT_DATA_TYPE_hash_bytes_length);
    Good_hashData.sectorOffset = byteOffset / SECTOR_SIZE;

    int hash_type = EXT_TYPE_DATA_MINOR_MASK(extType);

    if (DATA_TYPE_MINOR_hash_md4_and_crc32 == hash_type)
    {
        Good_hashData.extType = DATA_TYPE_MAJOR_HASH | DATA_TYPE_MINOR_hash_md4_and_crc32;
        md4_buf(bs.data(), org_dataBytes, Good_hashData.extData.data());
        ((u32 *)Good_hashData.extData.data())[MD4_HASH_WORDS] = cmpress_CalculateCrc32(bs.data(), org_dataBytes);
    }
    else if (DATA_TYPE_MINOR_hash_quick == hash_type)
    {
        Good_hashData.extType = DATA_TYPE_MAJOR_HASH | DATA_TYPE_MINOR_hash_quick;
        Ice::Byte* extDataBuf = bs.data();
        *((U32 *)extDataBuf) = Clerware_MurmurHash3_x86_32(bs.data(), org_dataBytes, Clerware_MurmurHash3_x86_32_seed);
        U64* hash1Buf = (U64 *)(extDataBuf + sizeof(U32));
        U64* hash2Buf = (U64 *)(extDataBuf + sizeof(U32) + sizeof(U64));
        *hash1Buf = spooky_hash_seed_one;
        *hash2Buf = spooky_hash_seed_two;
        spooky_hash128(bs.data(), org_dataBytes, hash1Buf, hash2Buf);
    }
    else
    {
      s << "hash_verifyData error extType: 0x" << hex << extType << imgInfo();
      LOG(ERROR) << s.str();
      throw Utils::SystemError("hash算法出错", s.str(), hash_error_and_resend_data);
      return;
    }

    if (!(_de_duplication&DEDUPLE_TYPE_HASH_verify_Before_WRITE))
    {
      return;
    }

    if (0 != memcmp(Good_hashData.extData.data(), client_hashData.first, client_hashSize))
    {
      s << "hash_verifyData LBA: 0x" << hex << byteOffset / 0x200 << " new hashData != old hashData" << imgInfo();
      LOG(ERROR) << s.str();
      std::stringstream	ssout;
      const::VpsAgent::BinaryStream binUpdate(client_hashData.first, client_hashData.second);
      bin2hex(Good_hashData.extData, ssout);
      LOG(ERROR) << "old hash:" << ssout.str();
      bin2hex(binUpdate, ssout);
      LOG(ERROR) << "new hash:" << ssout.str();
      throw Utils::SystemError("hash比较出错", s.str(), hash_error_and_resend_data);
      return;
    }

    return;
  }

  void cleanUsedBlockBitmap(Ice::Long byteOffset, Int realBytes)
  {
    int  ret = 0;
    stringstream s;
    if (byteOffset % BYTE_COUNT_PER_BLOCK)
    {
      s << "ImgWrapper::cleanUsedBlockBitmap invalid byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << realBytes << " " << imgInfo();
      throw Utils::SystemError("清理备份位图中的去重区域失败", s.str(), 0);
    }

    if (realBytes % BYTE_COUNT_PER_BLOCK)
    {
      LOG(WARNING) << "ImgWrapper::cleanUsedBlockBitmap last range bytes:0x" << byteOffset << " bytes:0x" << hex << realBytes << "" << imgInfo();
    }

    if (_handle == 0)
    {
      throw Utils::SystemError("清理备份位图中的去重区域失败，无效的文件句柄", "ImgWrapper::cleanUsedBlockBitmap NULL handle", 0);
    }

    ::IMG::BlockIndexes Indexes;
    int			i, nCount = (realBytes - 1 + BYTE_COUNT_PER_BLOCK) / BYTE_COUNT_PER_BLOCK;		//其实这里只会传一块进来，顺手把代码实现了，未来有小概率使用。
    Ice::Long	blkID = byteOffset / BYTE_COUNT_PER_BLOCK;
    Indexes.resize(nCount);

    for (i = 0; i < nCount; i++, blkID++)
    {
      Indexes[i] = blkID;
    }

    try
    {
      ret = _prxes->allocate()->proxy()->cleanUsedBlockBitmap(_handle, Indexes);
    }
    catch (const Utils::SystemError& e)
    {
      s << "ImgWrapper::cleanUsedBlockBitmap byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << realBytes\
        << " SystemError : " << FormatError::SystemError2String(e) << imgInfo();
      throw Utils::SystemError("清理备份位图中的去重区域失败", s.str(), e.rawCode);
    }
    catch (const IceUtil::Exception& e)
    {
      s << "ImgWrapper::cleanUsedBlockBitmap byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << realBytes\
        << " Exception : " << e.ice_name() << imgInfo();
    }
    catch (const std::exception& e)
    {
      s << "ImgWrapper::cleanUsedBlockBitmap byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << realBytes\
        << " exception : " << e.what() << imgInfo();
    }
    catch (...)
    {
      s << "ImgWrapper::cleanUsedBlockBitmap byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << realBytes\
        << " unknown exception" << imgInfo();
    }

    if (ret)
    {
      if (s.str().empty())
      {
        s << "ImgWrapper::cleanUsedBlockBitmap byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << realBytes\
          << " ret 0x" << hex << ret << imgInfo();
      }
      throw Utils::SystemError("清理备份位图中的去重区域失败", s.str(), 0);
    }
  }

  void writeCopy(int extType, const::std::pair<const::Ice::Byte *, const::Ice::Byte *>& client_hashData, Ice::Long byteOffset, Int org_dataBytes)
  {
    stringstream s;
    int		ret;

    if (!(_de_duplication&DEDUPLE_TYPE_COPY_ALL_DATA_WRITE_2_NEW))
    {
      //client已经发现是相同数据，不再传送，但是要通知qemu-img，让他从之前的数据中读取。
      cleanUsedBlockBitmap(byteOffset, org_dataBytes);
      return;
    }
    //后面的流程都会写入数据，不能cleanUsedBlockBitmap

    if (0 == _fd_pre_data)
    {//居然没有设备，则需要全部重传。
      s << "extType: error  " << hex << extType << imgInfo();
      throw Utils::SystemError("hash dev err", s.str(), hash_error_and_resend_data);
      return;
    }

    IMG::BinaryStream bs;
    ::VpsAgent::PostExtData		Good_hashData;
    bs.resize(org_dataBytes);

    size_t	doneByte;
    ret = _block_rw(_fd_pre_data, bs.data(), byteOffset, org_dataBytes, doneByte, false);
    if (ret || (size_t)org_dataBytes != doneByte)
    {
      s << "ImgWrapper::write byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << bs.size()\
        << " _block_rw return 0x" << hex << ret << " org_dataBytes:" << hex << org_dataBytes << " doneByte:" << hex << doneByte << imgInfo();
      throw Utils::SystemError("原备份点数据读取失败", s.str(), hash_error_and_resend_data);
      return;
    }

    hash_verifyData(extType, byteOffset, org_dataBytes, bs, client_hashData, Good_hashData);

    write(byteOffset, bs);
    writeHash(Good_hashData);

    //fixme:这里可以有2种预读功能，1是用client的位图精准预读。2是无条件预读下一块。先无条件预读下一块，以后再精准预读。				
    readahead(_fd_pre_data, byteOffset + 0x100000, 0x100000);
  }

  Ice::Int getTotalUsedBitmap(Ice::Int index, IMG::BinaryStream& bs)
  {
    if (_handle == 0)
    {
      throw Utils::SystemError("读取快照文件有效区域失败，无效的文件句柄", "ImgWrapper::getTotalUsedBitmap NULL handle", 0);
    }

    Ice::Int result = 0;
    bool finish = false;

    stringstream s;
    s << "ImgWrapper::getTotalUsedBitmap index:0x" << hex << index;
    string msg = s.str();
    s.str(std::string());

    try
    {
      result = _prxes->allocate()->proxy()->getTotalUesdBlockBitmap(_handle, index, bs, finish);
    }
    catch (const Utils::SystemError& e)
    {
      s << msg << " SystemError : " << FormatError::SystemError2String(e) << imgInfo();
      throw Utils::SystemError("读取快照文件有效区域失败", s.str(), e.rawCode);
    }
    catch (const IceUtil::Exception& e)
    {
      s << msg << " Exception : " << e.ice_name() << imgInfo();
    }
    catch (const std::exception& e)
    {
      s << msg << " exception : " << e.what() << imgInfo();
    }
    catch (...)
    {
      s << msg << " unknown exception" << imgInfo();
    }

    if (finish)
    {
      LOG(INFO) << "ImgWrapper::getTotalUsedBitmap get last buffer.";
      result = 0;
    }
    else if (0 == result)
    {
      if (s.str().empty())
      {
        s << msg << " 0 == result" << imgInfo();
      }
      throw Utils::SystemError("读取快照文件有效区域失败", s.str(), 0);
    }

    return result;
  }

  void read(Ice::Long byteOffset, Ice::Int bytes, IMG::BinaryStream& bs)
  {
    if (_handle == 0 && !retry(true))
    {
      throw Utils::SystemError("读取快照文件失败，无效的文件句柄", "ImgWrapper::read NULL handle", 0);
    }

    ::Ice::Int readBytes = 0;
    stringstream s;
    s << "ImgWrapper::read byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << bytes;
    string msg = s.str();
    s.str(std::string());

    try
    {
      readBytes = _prxes->allocate()->proxy()->read(_handle, byteOffset, bytes, bs);
    }
    catch (const Utils::SystemError& e)
    {
      s << msg << " SystemError : " << FormatError::SystemError2String(e) << imgInfo();
      retry();
      throw Utils::SystemError("快照文件读取失败", s.str(), e.rawCode);
    }
    catch (const IceUtil::Exception& e)
    {
      s << msg << " Exception : " << e.ice_name() << imgInfo();
    }
    catch (const std::exception& e)
    {
      s << msg << " exception : " << e.what() << imgInfo();
    }
    catch (...)
    {
      s << msg << " unknown exception" << imgInfo();
    }

    if (readBytes != static_cast<Ice::Int>(bs.size()) || readBytes != bytes)
    {
      if (s.str().empty())
      {
        s << msg << " readBytes != bs.size() || readBytes != bytes readBytes:0x" << hex << readBytes << " bs.size():0x" << bs.size() << imgInfo();
      }
      retry();
      throw Utils::SystemError("快照文件读取失败", s.str(), 0);
    }
  }

  void readEx(Ice::Long byteOffset, Ice::Int bytes, IMG::BinaryStream& bs)
  {
    if (_handle == 0 && !retry(true))
    {
      throw Utils::SystemError("readEx 读取文件失败，无效的文件句柄", "ImgWrapper::read NULL handle", 0);
    }

    ::Ice::Int readBytes = 0;
    stringstream s;
    s << "ImgWrapper::readEx byteOffset:0x" << hex << byteOffset << " bytes:0x" << hex << bytes;
    string msg = s.str();
    s.str(std::string());

    try
    {
      readBytes = _prxes->allocate()->proxy()->readEx(_handle, byteOffset, bytes, bs);
    }
    catch (const Utils::SystemError& e)
    {
      s << msg << " SystemError : " << FormatError::SystemError2String(e) << imgInfo();
      retry();
      throw Utils::SystemError("readEx 读取失败", s.str(), e.rawCode);
    }
    catch (const IceUtil::Exception& e)
    {
      s << msg << " Exception : " << e.ice_name() << imgInfo();
    }
    catch (const std::exception& e)
    {
      s << msg << " exception : " << e.what() << imgInfo();
    }
    catch (...)
    {
      s << msg << " unknown exception" << imgInfo();
    }

    if (readBytes != static_cast<Ice::Int>(bs.size()) || readBytes != bytes)
    {
      if (s.str().empty())
      {
        s << msg << " readBytes != bs.size() || readBytes != bytes readBytes:0x" << hex << readBytes << " bs.size():0x" << bs.size() << imgInfo();
      }
      retry();
      throw Utils::SystemError("readEx 文件读取失败", s.str(), 0);
    }
  }

  virtual void ReadOnNoCache(Ice::Long byteOffset, Ice::Int bytes, IMG::BinaryStream& bs)
  {
    throw Utils::SystemError("ReadOnNoCache 文件读取失败", "not support", 0);
  }

  virtual void ReadWithCache(Ice::Long byteOffset, Ice::Int bytes, IMG::BinaryStream& bs)
  {
    throw Utils::SystemError("ReadWithCache 文件读取失败", "not support", 0);
  }

  virtual bool SetCacheImageBitmap(const IMG::BinaryStream& bitmap, Ice::Long index)
  {
    return false;
  }

  void setUsedBlkSegSet(const::IMG::BinaryStream& bs)
  {
    if (!(_de_duplication&DEDUPLE_TYPE_client_work))
      return;

    ULONG64	 bitCount = bs.size() * 8;
    ULONG64	completeBits = bitmap_2_seg(bs.data(), 0, bitCount, _ullStartBit, _bakblkSegSetPtr, SEC_COUNT_PER_BLOCK, 0x7ffffff);  //0x7ffffff，几乎是无穷大了。
    if (bitCount != completeBits)
    {
      LOG(ERROR) << "ImgWrapper::setUsedBlkSegSet bitmap_2_seg too large! _ullStartBit: " << hex << _ullStartBit << " bitCount : " << hex << bitCount << "completeBits: " << hex << completeBits << " bs.size(): " << hex << bs.size();
    }
    _ullStartBit += bitCount;
    return;
  }

  bool get_first_valid_blknodeSeg(ULONG64 ullBitpost_inFile, BlkNodeSeg	&newblk)
  {
    while (1)
    {
      auto itr = _bakblkSegSetPtr->begin();
      if (itr == _bakblkSegSetPtr->end())
      {
        return false;
      }
      newblk = *itr;
      _bakblkSegSetPtr->erase(itr);
      if (ullBitpost_inFile < newblk.end)
      {
        return true;
      }
    }
    return false;
  }

  void GetBakDataExt(::VpsAgent::GetExtData getExtData, ::VpsAgent::PostExtDataVector& dataExt)
  {
    BlkNodeSeg		newblk;
    ULONG64			ulStartBit = getExtData.sectorOffset;
    ULONG64			downloadbits = getExtData.bitCount;
    ULONG64			returnCount, u64sectorOffset;
    ULONG64			bits_inFile;

	IceUtil::Mutex::Lock lock(_ExtData_mutex);

    if (!(_de_duplication&DEDUPLE_TYPE_client_work) ||
      !_dedupleFile.valid_data() ||
      _bakblkSegSetPtr->size() == 0
      )
    {
      return;
    }
    if (!downloadbits)
      return;

    LOG(INFO) << "GetBakDataExt get " << hex << downloadbits;
    returnCount = dataExt.size();
    dataExt.resize(returnCount + downloadbits);
    newblk.start = newblk.end = 0;
    while (downloadbits)
    {
      if (!_dedupleFile.get_hash_entry(dataExt[returnCount].extType, u64sectorOffset, dataExt[returnCount].extData))
      {//error
        newblk.start = newblk.end = 0;
        break;
      }
      dataExt[returnCount].extType |= DATA_TYPE_MAJOR_HASH;
      dataExt[returnCount].sectorOffset = u64sectorOffset;
      dataExt[returnCount].diskIndex = getExtData.diskIndex;
      dataExt[returnCount].numberOfSectors = SEC_COUNT_PER_BLOCK;

      bits_inFile = dataExt[returnCount].sectorOffset;
      if (bits_inFile < ulStartBit)
      {
        continue;
      }
      if (newblk.start >= newblk.end || bits_inFile >= newblk.end)
      {
        if (!get_first_valid_blknodeSeg(bits_inFile, newblk))
        {
          break;
        }
      }
      if (bits_inFile >= newblk.end)
      {//BUGBUG
        LOG(INFO) << "error: bits_inFile :" << hex << bits_inFile << " > newblk.end: " << hex << newblk.end;
        continue;
      }
      if (bits_inFile < newblk.start)
      {//文件中太小。
        continue;
      }
      if (bits_inFile > newblk.start)
      {
        newblk.start = bits_inFile;
      }
      if (bits_inFile == newblk.start)
      {//刚好相同，
        returnCount++;
        newblk.start += SEC_COUNT_PER_BLOCK;
        downloadbits--;
        continue;
      }
      //不应该发生的。
      LOG(INFO) << "error: dataExt[returnCount].sectorOffset :" << hex << dataExt[returnCount].sectorOffset << " > newblk.start: " << hex << newblk.start;
    }
    if (newblk.start < newblk.end)
    {
      _bakblkSegSetPtr->insert(newblk);
    }
    dataExt.resize(returnCount);
    LOG(INFO) << "GetBakDataExt ret0x" << hex << returnCount;
    _dedupleFile.load_hash_file_to_cache();
    return;
  }

  void setUsedBlockBitmap(::Ice::Int diskIndex, const ::IMG::BinaryStream& bs, bool completed)
  {
    if (_handle == 0)
    {
      throw Utils::SystemError("写入数据位图失败，无效的文件句柄", "ImgWrapper::setUsedBlockBitmap NULL handle", 0);
    }

    if (_de_duplication&DEDUPLE_TYPE_client_work)
    {//记录下来以便去重时查询。
      setUsedBlkSegSet(bs);
      if (completed)
      {//将以前的hash文件准备好。以便需要时使用。
        _ullStartBit = 0;
        _dedupleFile.open_read_hash_file(_read_hash_filepath);
      }
    }

    int returned = 0xAAAAAAAA;
    stringstream s;
    s << "ImgWrapper::setUsedBlockBitmap diskIndex:" << diskIndex << " completed:" << completed;
    string msg = s.str();
    s.str(std::string());

    try
    {
      returned = _prxes->allocate()->proxy()->setUsedBlockBitmap(_handle, bs, completed);
    }
    catch (const Utils::SystemError& e)
    {
      s << msg << " SystemError : " << FormatError::SystemError2String(e) << imgInfo();
      throw Utils::SystemError("写入数据位图失败", s.str(), e.rawCode);
    }
    catch (const IceUtil::Exception& e)
    {
      s << msg << " Exception : " << e.ice_name() << imgInfo();
    }
    catch (const std::exception& e)
    {
      s << msg << " exception : " << e.what() << imgInfo();
    }
    catch (...)
    {
      s << msg << " unknown exception" << imgInfo();
    }

    if (returned != 0)
    {
      if (s.str().empty())
      {
        s << msg << " returned != 0 returned:0x" << hex << returned << imgInfo();
      }
      throw Utils::SystemError("写入数据位图失败", s.str(), 0);
    }
  }

  void setDuplicateFileSectors(::Ice::Int diskIndex, const ::IMG::DuplicateFileSectors& sectors, bool completed)
  {
    if (_handle == 0)
    {
      throw Utils::SystemError("写入去重映射关系失败，无效的文件句柄", "ImgWrapper::setDuplicateFileSectors NULL handle", 0);
    }

    int returned = 0xAAAAAAAA;
    stringstream s;
    s << "ImgWrapper::setDuplicateFileSectors diskIndex:" << diskIndex << " completed:" << completed;
    string msg = s.str();
    s.str(std::string());

    try
    {
      returned = _prxes->allocate()->proxy()->setDuplicateFileSectors(_handle, sectors, completed);
    }
    catch (const Utils::SystemError& e)
    {
      s << msg << " SystemError : " << FormatError::SystemError2String(e) << imgInfo();
      throw Utils::SystemError("写入去重映射关系失败", s.str(), e.rawCode);
    }
    catch (const IceUtil::Exception& e)
    {
      s << msg << " Exception : " << e.ice_name() << imgInfo();
    }
    catch (const std::exception& e)
    {
      s << msg << " exception : " << e.what() << imgInfo();
    }
    catch (...)
    {
      s << msg << " unknown exception" << imgInfo();
    }

    if (returned != 0)
    {
      if (s.str().empty())
      {
        s << msg << " returned != 0 returned:0x" << hex << returned << imgInfo();
      }
      LOG(ERROR) << s.str();
      throw Utils::SystemError("写入去重映射关系失败", s.str(), 0);
    }
  }

  string imgInfo()
  {
    stringstream s;
    s << " handle:0x" << hex << _handle << " flag:" << _flag;

    for_each(_snapshot.begin(), _snapshot.end(), [&](const IMG::ImageSnapshotIdent& ident) {
      s << "\n path:" << ident.path << " snapshot:" << ident.snapshot;
    });

    return s.str();
  }

  Ice::Long handle() { return _handle; }

  std::string getPath() { return _createPath; }

  std::string getIdent() { return _creatIdent; }

  const IMG::ImageSnapshotIdents _snapshot;

protected:
  ImgServicePrxPoolPtr  _prxes;

  Ice::Long volatile    _handle;

  bool                  _successful;
  std::string           _createPath;
  std::string           _creatIdent;

  const string          _flag;

  void create(const IMG::ImageSnapshotIdent& ident, Ice::Long diskBytes)
  {
    if (_handle == 0)
    {
      _createPath = ident.path;
      _creatIdent = ident.snapshot;
      stringstream s;
      s << "ImgWrapper::create ident:" << ident.path << " snapshot:" << ident.snapshot << " diskBytes:0x" << hex << diskBytes << " flag:" << _flag;
      string msg = s.str();
      s.str(std::string());

      try
      {
        LOG(INFO) << msg << " start...";
        _handle = _prxes->allocate()->proxy()->create(ident, _snapshot, diskBytes, _flag);
        LOG(INFO) << "ImgWrapper::create ok " << imgInfo();
      }
      catch (const Utils::SystemError& e)
      {
        s << msg << " SystemError : " << FormatError::SystemError2String(e) << imgInfo();
        throw Utils::SystemError("创建快照文件失败", s.str(), 0);
      }
      catch (const IceUtil::Exception& e)
      {
        s << msg << " Exception : " << e.ice_name() << imgInfo();
      }
      catch (const std::exception& e)
      {
        s << msg << " exception : " << e.what() << imgInfo();
      }
      catch (...)
      {
        s << msg << " unknown exception" << imgInfo();
      }

      if (0 == _handle)
      {
        if (s.str().empty())
        {
          s << msg << " NULL handle" << imgInfo();
        }
        throw Utils::CreateSnapshotImageError("创建快照文件失败", s.str(), 0);
      }
      else
      {
        LOG(INFO) << msg << " ok." << imgInfo();
      }
      _bakblkSegSetPtr.reset();
      _bakblkSegSetPtr = make_shared<SetBlkNodeSeg>();
      _ullStartBit = 0;

      if (!_pre_data_device.empty())
        _fd_pre_data = _x_open64(_pre_data_device.c_str(), O_RDONLY);

      //create hash file.
      if (_hash_disk_data || (_de_duplication&DEDUPLE_TYPE_client_work))
        if (_write_hashfileHandle <= 0)
        {
          stringstream s;
          _write_hash_filepath = getPath() + "_" + getIdent() + ".hash";
          _write_hashfileHandle = _x_open64(_write_hash_filepath.c_str(), O_CREAT | O_WRONLY | O_APPEND);
          LOG(INFO) << "create hash file:" << _write_hash_filepath << " fd: " << hex << _write_hashfileHandle;
          if (_write_hashfileHandle <= 0)
          {
            int		err = errno;
            s << "file:" << _write_hash_filepath << " error code:0x" << hex << err;
            throw Utils::SystemError("创建hash文件失败！", s.str(), 0);
          }
        }
    }
  }

  void open()
  {
    if (_handle == 0)
    {
      stringstream s;
      try
      {
        _handle = _prxes->allocate()->proxy()->open(_snapshot, _flag);
      }
      catch (const Utils::SystemError& e)
      {
        s << "ImgWrapper::open SystemError : " << FormatError::SystemError2String(e) << imgInfo();
        throw Utils::SystemError("打开快照文件失败", s.str(), 0);
      }
      catch (const IceUtil::Exception& e)
      {
        s << "ImgWrapper::open Exception : " << e.ice_name() << imgInfo();
      }
      catch (const std::exception& e)
      {
        s << "ImgWrapper::open exception : " << e.what() << imgInfo();
      }
      catch (...)
      {
        s << "ImgWrapper::open unknown exception" << imgInfo();
      }

      if (0 == _handle)
      {
        if (s.str().empty())
        {
          s << "ImgWrapper::open NULL handle" << imgInfo();
        }
        throw Utils::SystemError("打开快照文件失败", s.str(), 0);
      }
      else
      {
        LOG(INFO) << "ImgWrapper::open ok " << imgInfo();
      }
    }
  }

  bool retry(bool tryOpen = false)
  {
    bool result = false;

    if (_retry_times == -1)
    {
      IceUtil::Mutex::Lock lock(_retry_mutex);
      if (_handle)
      {
        if (!tryOpen)
        {
          close();
        }
      }
      else
      {
        if (tryOpen)
        {
          open();
          result = true;
        }
      }
    }

    return result;
  }

public:
  void write_hashdata(char *buf, size_t count)
  {
    size_t		done;
    int		ret;
    if (_write_hashfileHandle <= 0)
    {
      throw Utils::SystemError("没有hash文件句柄！", "no hash file handle", 0);
    }
    ret = _stream_rw(_write_hashfileHandle, buf, count, done, true);
    if (0 != ret)
    {
      stringstream s;
      s << "write errcode:" << ret;
      throw Utils::SystemError("hash文件写入失败！", s.str(), 0);
    }
    return;
  }

  void writeHash(const::VpsAgent::PostExtData& hashData)
  {
    std::stringstream ss;
    std::string h = bin2hex(hashData.extData, ss).str();

    char buf[MAX_PATH];
    snprintf(buf, MAX_PATH, "0x%lx,%d,%s\n", hashData.sectorOffset, EXT_TYPE_DATA_MINOR_MASK(hashData.extType), h.c_str());
    write_hashdata(buf, strlen(buf));
    return;
  }
  void close_hashdata()
  {
    if (_write_hashfileHandle > 0)
    {
      ::fsync(_write_hashfileHandle);
      ::close(_write_hashfileHandle);
      _write_hashfileHandle = 0;
    }
    if (!_successful && _write_hash_filepath.size())
    {
      unlink(_write_hash_filepath.c_str());
    }

    return;
  }

  ULONG64		_ullCdpBlockIndex;

private:
  std::string     _write_hash_filepath;
  int    _write_hashfileHandle;

  std::string     _read_hash_filepath;
  dedupleHashFile	_dedupleFile;
  bool			_hash_disk_data;
  int				_de_duplication;

  string			_pre_data_device;
  int				_fd_pre_data;

  IceUtil::Mutex   _ExtData_mutex;
  ULONG64			_ullStartBit;
  SetBlkNodeSegPtr _bakblkSegSetPtr;

  int volatile    _retry_times;
  IceUtil::Mutex  _retry_mutex;
};

class ReadableImgWrapper : public ImgWrapper
{
public:
  ReadableImgWrapper(const ImgServicePrxPoolPtr& prxes, const IMG::ImageSnapshotIdents& snapshot, const string& flag, int retry_times = 0)
    : ImgWrapper(prxes, snapshot, flag, "", retry_times)
  {
    open();
    setClose(true);
  }
};

class WritableImgWrapper : public ImgWrapper
{
public:
  WritableImgWrapper(const ImgServicePrxPoolPtr& prxes, const IMG::ImageSnapshotIdent& ident
    , const IMG::ImageSnapshotIdents& lastSnapshot, Ice::Long diskBytes, const string& flag, const string& jsonConfig)
    : ImgWrapper(prxes, lastSnapshot, flag, jsonConfig)
  {
    create(ident, diskBytes);
  }
};

typedef shared_ptr<ImgWrapper> ImgWrapperPtr;
typedef shared_ptr<WritableImgWrapper> WritableImgWrapperPtr;
typedef shared_ptr<ReadableImgWrapper> ReadableImgWrapperPtr;
