#pragma once

#include "magic_number.h"
#include "ImgWrapper.hpp"

#include <IceUtil/Thread.h>
#include <IceUtil/Monitor.h>

#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

using namespace std;
using namespace IceUtil;
using namespace IceUtilInternal;



typedef weak_ptr<ReadableImgWrapper> ReadableImgWrapperTmpPtr;

typedef enum _BlkStatus
{
	StatusUnknown = 0,
	StatusOutRange,
	StatusInCache,
	StatusPending,
	StatusWaiting,
	StatusNotSetOn,
}BlkStatus;

class Queue
{
public:
	Queue()
	{
		_count = 0;
	}

	~Queue()
	{
		clean();
	}

	void put(long index)
	{
		if (index < 0)
		{
			LOG(INFO) << "[" << __FUNCTION__ << "] invalid index=" << index;
			return;
		}		

		_q.push_back(index);
		_count++;
	}

	long size()
	{
		return _q.size();
	}

	long count()
	{
		return _count;
	}

	long get()
	{
		long index = 0;

		if (_q.empty())
		{
			return -1;
		}

		index = _q.front();
		_q.pop_front();
		_count--;

		return index;
	}

	void clean()
	{
		_q.clear();
		_count = 0;
	}

private:
	list<long>	_q;
	long _count;
};

class CacheMap 
{
public:
	CacheMap()
	{
		_count = 0;
	}

	~CacheMap()
	{
		clean();
	}

	void put(long blk_index, long cache_index)
	{
		_mp.insert(make_pair(blk_index, cache_index));
		_count++;
	}

	long pop()
	{
		long index = 0;
		map<long, long>::iterator it;

		it = _mp.begin();
		if (it == _mp.end())
		{
			return -1;
		}

		index = it->second;
		_count--;

		_mp.erase(it);
		return index;;
	}

	long discard(long low_img_index, Queue& q, long discard_count)
	{
		if (low_img_index <= 0 || discard_count <= 0)
		{
			return 0;
		}

		long count = 0;
		map<long, long>::iterator it = _mp.begin();

		while (it != _mp.end() && count < discard_count)
		{
			if (it->first < low_img_index)
			{
				q.put(it->second);
        it = _mp.erase(it);
				count++;
				_count--;
			}
      else
      {
        ++it;
      }
		}

		return count;
	}

	long get(long blk_index)
	{
		long index = 0;
		map<long, long>::iterator it;

		it = _mp.find(blk_index);
		if (it == _mp.end())
		{
			return -1;
		}

		index = it->second;

		_mp.erase(it);
		_count--;

		return index;
	}

	void clean()
	{
		_count = 0;
		_mp.clear();
	}

private:

	long _count;
	map<long, long> _mp;
};


class BitmapStream
{
public:
	BitmapStream()
	{
		SetBitmap(1);
	}

	~BitmapStream()
	{

	}

	bool SetBitmap(const IMG::BinaryStream& bitmap)
	{
		BYTE* src = NULL;
		BYTE* dst = NULL;
		long size = bitmap.size();

		if (size <= 0)
		{
			return false;
		}

		_bitmap.resize(size);

		src = (BYTE*)bitmap.data();
		dst = (BYTE*)_bitmap.data();
		memcpy(dst, src, size);

		_max_index = size * 8;
		_data = dst;

		return true;
	}

	bool SetBitmap(long size)
	{
		if (size <= 0)
		{
			return false;
		}

		_max_index = size * 8;
		_bitmap.resize(size);
		_data = (BYTE*)_bitmap.data();
		memset(_data, 0x0, size);

		return true;
	}


	bool SetBitValue(long index, bool set)
	{
		long i = 0;
		long n = 0;

		if (index >= _max_index || index < 0)
		{
			return false;
		}

		i = index / 8;
		n = index % 8;

		if (set)
		{
			_data[i] |= (1 << n);
		}
		else
		{			
			_data[i] &= ~(1 << n);
		}

		return true;
	}

	bool IsBitSetOnBitmap(long index)
	{
		long i = 0;
		long n = 0;

		if (index >= _max_index || index < 0)
		{
			return false;
		}

		i = index / 8;
		n = index % 8;	

		if (_data[i] & (1 << n))
		{
			return true;
		}

		return false;
	}

	void SetBitmapZero()
	{
		long size = _bitmap.size();
		BYTE* p = (BYTE*)_bitmap.data();

		memset(p, 0x0, size);
	}

	long GetSetOnCount()
	{
		long count = 0;
		long size = _bitmap.size() * 8;

		for (long i = 0; i < size; i++)
		{
			if (IsBitSetOnBitmap(i))
			{
				count++;
			}
		}

		return count;
	}

private:

	IMG::BinaryStream _bitmap;
	long _max_index;
	BYTE* _data;
};




class ImgCacheWorker
{
public:
	ImgCacheWorker(long cache_size)
	{
		LOG(INFO) << "[" << __FUNCTION__ << "]" << " enter";

		_stop = false;

		_ReadImagePtr = NULL;
		_cache_size = cache_size;
		_block_size = BYTE_COUNT_PER_BLOCK;

		_block_count = _cache_size / _block_size;
		_bitmap_size = _block_count / 8;
		
		_img_bgn_blk_idx = 0;
		_img_end_blk_idx = 0;
		_read_index = 0;
		_max_read_index = 0;
		_set_count = 0;

		_cache_buf.resize(cache_size);

		_set_bitmap.SetBitmap(_bitmap_size);
		_finish_bitmap.SetBitmap(_bitmap_size);
		_pending_bitmap.SetBitmap(_bitmap_size);

		for (long i = 0; i < _block_count; i++)
		{
			_free_queue.put(i);
		}
	}

	~ImgCacheWorker()
	{
		LOG(INFO) << "[" << __FUNCTION__ << "]" << " enter";
	}

	void SetReadImagePointer(ReadableImgWrapper* ReadImagePtr)
	{
		_ReadImagePtr = ReadImagePtr;
	}

private:

	long _cache_size;
	long _block_size;
	long _block_count;

	long _bitmap_size;
	long _set_count;
	long _read_index;
	long _max_read_index;

	bool _stop;
	long _keep_alive_cnt;

	bool _log_dbg_msg;

	Ice::Long _img_bgn_blk_idx;
	Ice::Long _img_end_blk_idx;

	IMG::BinaryStream _cache_buf;

	BitmapStream _set_bitmap;
	BitmapStream _finish_bitmap;
	BitmapStream _pending_bitmap;
	BitmapStream _task_bitmap;

	CacheMap _cache_map;
	Queue _free_queue;

	ReadableImgWrapper* _ReadImagePtr;

	Monitor<Mutex> _queue_lock;
	Monitor<Mutex> _cache_map_lock;
	Monitor<Mutex> _bitmap_lock;


public:

	long GetCurrentReadIndex()
	{
		return _read_index + _img_bgn_blk_idx;
	}

	long OffsetToBlockIndex(Ice::Long byteOffset)
	{
		Ice::Long blk_index = 0;

		blk_index = byteOffset / _block_size;

		if (blk_index < _img_bgn_blk_idx || blk_index >= _img_end_blk_idx)
		{
			return -1;
		}

		blk_index -= _img_bgn_blk_idx;

		return blk_index;
	}


	bool SetCacheImageBitmap(const IMG::BinaryStream& bitmap, Ice::Long index, bool log_msg)
	{

		long size = bitmap.size();

		Monitor<Mutex>::Lock lock1(_bitmap_lock);
		{
			Monitor<Mutex>::Lock lock2(_cache_map_lock);
			{
				Monitor<Mutex>::Lock lock3(_queue_lock);

				_read_index = 0;
				_max_read_index = size * 8;

				_set_count++;
				_img_bgn_blk_idx = index;
				_img_end_blk_idx = _max_read_index + index;

				_set_bitmap.SetBitmap(bitmap);
				_task_bitmap.SetBitmap(bitmap);
				_finish_bitmap.SetBitmap(size);
				_pending_bitmap.SetBitmap(size);

				_log_dbg_msg = log_msg;
				
				Queue q;
				long release_count = 0;
				long lowest_index = 0;
				
				lowest_index = _img_bgn_blk_idx - _block_count * 2;
				release_count = _cache_map.discard(lowest_index, q, _block_count);
				while (q.size() > 0)
				{
					long cache_index = q.get();
					_free_queue.put(cache_index);
				}

				if (_log_dbg_msg)
				{
					LOG(INFO) << "[" << __FUNCTION__ << "]" << " bitmap size=" << dec << size;
					LOG(INFO) << "[" << __FUNCTION__ << "]" << " _set_count=" << dec << _set_count;
					LOG(INFO) << "[" << __FUNCTION__ << "]" << " release_count=" << dec << release_count;
					LOG(INFO) << "[" << __FUNCTION__ << "]" << " _img_bgn_blk_idx=" << dec << _img_bgn_blk_idx;
					LOG(INFO) << "[" << __FUNCTION__ << "]" << " _img_end_blk_idx=" << dec << _img_end_blk_idx;
				}
				_queue_lock.notifyAll();
			}
			_cache_map_lock.notifyAll();
		}
		_bitmap_lock.notifyAll();

		return true;
	}


	BlkStatus GetBlockBitmapStatus(Ice::Long byteOffset, bool clear)
	{
		long blk_index = 0;

		Monitor<Mutex>::Lock lock(_bitmap_lock);

		blk_index = OffsetToBlockIndex(byteOffset);
		if (blk_index < 0)
		{
			return StatusOutRange;
		}

		if (!_set_bitmap.IsBitSetOnBitmap(blk_index))
		{
			return StatusNotSetOn;
		}

		if (_finish_bitmap.IsBitSetOnBitmap(blk_index))
		{
			return StatusInCache;
		}

		if (_pending_bitmap.IsBitSetOnBitmap(blk_index))
		{
			return StatusPending;
		}

		if (_task_bitmap.IsBitSetOnBitmap(blk_index))
		{
			if (clear)
			{
				_task_bitmap.SetBitValue(blk_index, 0);
			}

			return StatusWaiting;
		}

		return StatusUnknown;
	}

	long SearchBlockCache(long img_blk)
	{
		long cache_index = 0;

		Monitor<Mutex>::Lock lock(_cache_map_lock);

		cache_index = _cache_map.get(img_blk);

		return cache_index;
	}
	

	bool GetDataFromCache(IMG::BinaryStream& buffer, Ice::Long byteOffset, Ice::Int bytes, bool& try_again, bool copy_data)
	{
		BYTE* dst = NULL;
		BYTE* src = NULL;
		long img_index = 0;
		long cache_index = 0;
		BlkStatus status = StatusUnknown;
		
		try_again = false;

		img_index = byteOffset / _block_size;

		status = GetBlockBitmapStatus(byteOffset, true);
		if (StatusInCache != status && status != StatusPending && status != StatusOutRange)
		{
			return false;
		}

		if (StatusPending == status)
		{
			if (_log_dbg_msg)
			{
				LOG(INFO) << "[" << __FUNCTION__ << "] wait pending, img_index=" << dec << img_index;
				LOG(INFO) << "[" << __FUNCTION__ << "] wait pending, _read_index=" << dec << _read_index;
				LOG(INFO) << "[" << __FUNCTION__ << "] wait pending, current read=" << dec << _read_index + _img_bgn_blk_idx;
				LOG(INFO) << "[" << __FUNCTION__ << "] wait pending, _img_bgn_blk_idx=" << dec << _img_bgn_blk_idx;
				LOG(INFO) << "[" << __FUNCTION__ << "] wait pending, _img_end_blk_idx=" << dec << _img_end_blk_idx;
				LOG(INFO) << "[" << __FUNCTION__ << "] wait pending, _free_queue count=" << dec << _free_queue.count();
			}

			try_again = true;

			bool time_out = false;
			Time tm = Time::milliSeconds(100);

			Monitor<Mutex>::Lock lock(_cache_map_lock);

			time_out = _cache_map_lock.timedWait(tm);
			if (time_out == false)
			{
				LOG(INFO) << "[" << __FUNCTION__ << "] warmming, wait pending timeout";
			}
		}

		
		cache_index = SearchBlockCache(img_index);
		if (cache_index < 0 || cache_index >= _block_count)
		{
			if (status == StatusInCache)
			{
				if (_log_dbg_msg)
				{
					LOG(INFO) << "[" << __FUNCTION__ << "] error, not in cache, img_index=" << dec << img_index;
					LOG(INFO) << "[" << __FUNCTION__ << "] error, not in cache, _read_index=" << dec << _read_index;
					LOG(INFO) << "[" << __FUNCTION__ << "] error, not in cache, current read=" << dec << _read_index + _img_bgn_blk_idx;
					LOG(INFO) << "[" << __FUNCTION__ << "] error, not in cache, _img_bgn_blk_idx=" << dec << _img_bgn_blk_idx;
					LOG(INFO) << "[" << __FUNCTION__ << "] error, not in cache, _img_end_blk_idx=" << dec << _img_end_blk_idx;
				}
			}
			
			return false;
		}

		if (copy_data)
		{
			buffer.resize(_block_size);
			src = (BYTE*)_cache_buf.data();
			dst = (BYTE*)buffer.data();

			src += (cache_index * _block_size);
			memcpy(dst, src, _block_size);
		}
		else
		{
			LOG(INFO) << "[" << __FUNCTION__ << "] discard cache, img_index=" << dec << img_index;
		}


		ReleaseCacheBuffer(&cache_index, 1);

		return true;

	}

	bool TryGetDataFromCache(IMG::BinaryStream& buffer, Ice::Long byteOffset, Ice::Int bytes, bool copy_data)
	{
		bool success = false;
		bool try_again = false;


		while (true)
		{
			success = GetDataFromCache(buffer, byteOffset, bytes, try_again, copy_data);
			if (success)
			{
				return true;
			}

			if (!try_again)
			{
				return false;
			}
		}

		return false;
	}

	void DiscardCacheData(Ice::Long byteOffset)
	{
		IMG::BinaryStream buffer;

		TryGetDataFromCache(buffer, byteOffset, 0, false);
	}

	bool IsValidBlockIndex(Ice::Long img_blk_index)
	{
		if (img_blk_index >= _img_bgn_blk_idx &&
			img_blk_index < _img_end_blk_idx)
		{
			return true;
		}

		return false;
	}


	long GetCacheBuffer(long* index_s)
	{
		long available = 0;
		long index = 0;
		long i = 0;

		Monitor<Mutex>::Lock lock(_queue_lock);

		available = _free_queue.size();
		if (available <= 0)
		{
			_queue_lock.wait();
		}

		available = _free_queue.size();
		if (available > PREREAD_BLOCK_COUNT)
		{
			available = PREREAD_BLOCK_COUNT;
		}

		for (i = 0; i < available; i++)
		{
			index = _free_queue.get();
			if (index >= 0)
			{
				index_s[i] = index;
			}
			else
			{
				LOG(INFO) << "{" << __FUNCTION__ << "] error, invalid buffer index=" << dec << index;
				break;
			}
		}
		
		return i;
	}

	void ReleaseCacheBuffer(long* index_s, long count)
	{
		long index = 0;
		Monitor<Mutex>::Lock lock(_queue_lock);

		for (long i = 0; i < count; i++)
		{
			index = index_s[i];
			if (index < 0)
			{
				LOG(INFO) << "{" << __FUNCTION__ << "] error, invalid buffer index=" << dec << index;
			}
			else
			{
				_free_queue.put(index);
			}
		}
		_queue_lock.notifyAll();
	}

	bool ReadImageData(Ice::Long img_blk_index, long read_blk_cnt, IMG::BinaryStream &bs, long& finish)
	{
		bool success = false;
		long length = 0;
		Ice::Long Offset = img_blk_index * _block_size;

		finish = 0;

		try
		{
			_ReadImagePtr->readEx(Offset, read_blk_cnt*_block_size, bs);

			length = bs.size();

			if (((length%_block_size) == 0) && (length > 0))
			{
				finish = length / _block_size;
				success = true;
			}
			else
			{
				LOG(INFO) << "[" << __FUNCTION__ << "] " << "invalid length=" << dec << length;
			}
		}
		catch (...)
		{
			LOG(INFO) << "[" << __FUNCTION__ << "]" << " has exception";
		}
		
		return success;
	}

	long GetReadTask(long& blk_index, long get_count)
	{	
		long count = 0;	

		Monitor<Mutex>::Lock lock(_bitmap_lock);

		if (_max_read_index <= 0)
		{
			return 0;
		}

		blk_index = -1;
		if (_read_index >= _max_read_index)
		{
			_bitmap_lock.wait();
		}

		while (_read_index < _max_read_index && count < get_count)
		{
			if (_task_bitmap.IsBitSetOnBitmap(_read_index))
			{
				_pending_bitmap.SetBitValue(_read_index, 1);

				count++;

				if (blk_index < 0)
				{
					blk_index = _read_index + _img_bgn_blk_idx;
				}
			}
			else
			{
				if (blk_index >= 0)
				{
					break;
				}
			}

			_read_index++;
		}

		return count;
	}



	bool MarkReadComplete(long img_blk_index, long cache_index, const BYTE* data)
	{
		long blk_index = 0;
		{
			Monitor<Mutex>::Lock lock(_cache_map_lock);
			BYTE* dst = NULL;

			dst = (BYTE*)_cache_buf.data() + cache_index * _block_size;
			memcpy(dst, data, _block_size);
			_cache_map.put(img_blk_index, cache_index);

			_cache_map_lock.notifyAll();
		}

		{
			Monitor<Mutex>::Lock lock(_bitmap_lock);

			blk_index = img_blk_index - _img_bgn_blk_idx;

			if (!IsValidBlockIndex(img_blk_index))
			{
				return true;
			}

			if (!_task_bitmap.IsBitSetOnBitmap(blk_index))
			{
				return true;
			}

			_pending_bitmap.SetBitValue(blk_index, 0);
			_task_bitmap.SetBitValue(blk_index, 0);
			_finish_bitmap.SetBitValue(blk_index, 1);
		}	

		return true;
	}


	bool MarkReadFailed(long img_blk_index, long count)
	{
		{
			Monitor<Mutex>::Lock lock(_bitmap_lock);
			long blk_index = 0;

			for (int i = 0; i < count; i++)
			{
				if (!IsValidBlockIndex(img_blk_index+i))
				{
					LOG(INFO) << "[" << __FUNCTION__ << "] out of range, img_blk_index=" << dec << img_blk_index;
					LOG(INFO) << "[" << __FUNCTION__ << "] out of range, _img_bgn_blk_idx=" << dec << _img_bgn_blk_idx;
					LOG(INFO) << "[" << __FUNCTION__ << "] out of range, _img_end_blk_idx=" << dec << _img_end_blk_idx;
					return false;
				}

				blk_index = img_blk_index - _img_bgn_blk_idx + i;

				if (!_set_bitmap.IsBitSetOnBitmap(blk_index))
				{
					continue;
				}

				LOG(INFO) << "[" << __FUNCTION__ << "] read failed, img_blk_index=" << dec << img_blk_index+i;

				_pending_bitmap.SetBitValue(blk_index, 0);
				_task_bitmap.SetBitValue(blk_index, 0);
				_finish_bitmap.SetBitValue(blk_index, 0);
			}
		}

		{
			Monitor<Mutex>::Lock lock(_cache_map_lock);
			_cache_map_lock.notify();
		}

		return true;
	}

	void DiscardKeepAlive()
	{
		long min_index = 0;
		long count = 0;
		long buf_count = 0;
		long buf_index[PREREAD_BLOCK_COUNT] = { 0 };

		Queue q;

		buf_count = _free_queue.count();

		sleep(1);

		{
			Monitor<Mutex>::Lock lock(_cache_map_lock);

			long range = _block_count * 4;

			if (_read_index > range)
			{
				min_index = _img_bgn_blk_idx + _read_index - range;
				count = _cache_map.discard(min_index, q, PREREAD_BLOCK_COUNT);
			}
		}

		if (count <= 0)
		{
			return;
		}

		LOG(INFO) << "[" << __FUNCTION__ << "] discard count=" << dec << count << " buf_count=" << buf_count;

		{
			long index = 0;

			while (q.size() > 0)
			{
				buf_index[index] = q.get();
				index++;
			}

			ReleaseCacheBuffer(buf_index, index);
		}

	}

	void ReadImgToCache(IMG::BinaryStream& ImgBuffer)
	{
		bool success = false;
		long image_index = 0;
		long blk_count = 0;
		long buf_count = 0;
		long finish_cnt = 0;
		long index = 0;
		BYTE* data = NULL;
		BYTE* src = NULL;

		long buf_index[PREREAD_BLOCK_COUNT] = { 0 };

		buf_count = GetCacheBuffer(buf_index);
		if (buf_count <= 0)
		{
			DiscardKeepAlive();
			return;
		}

		blk_count = GetReadTask(image_index, buf_count);
		if (blk_count <= 0)
		{
			ReleaseCacheBuffer(buf_index, buf_count);
			return;
		}

		success = ReadImageData(image_index, blk_count, ImgBuffer, finish_cnt);
		if (!success)
		{
			LOG(ERROR) << "[" << __FUNCTION__ << "]" << " ReadImageData failed";
		}

		data = (BYTE*)ImgBuffer.data();
		for (index = 0; index < finish_cnt; index++)
		{
			src = data + _block_size * index;
			success = MarkReadComplete(image_index + index, buf_index[index], src);
			if (!success)
			{
				LOG(INFO) << "[" << __FUNCTION__ << "] MarkReadComplete failed, image_index=" << dec << (image_index + index);
				LOG(INFO) << "[" << __FUNCTION__ << "] MarkReadComplete failed, buf_index=" << dec << buf_index[index];
				LOG(INFO) << "[" << __FUNCTION__ << "] MarkReadComplete, _img_bgn_blk_idx=" << dec << _img_bgn_blk_idx;
				LOG(INFO) << "[" << __FUNCTION__ << "] MarkReadComplete, _img_end_blk_idx=" << dec << _img_end_blk_idx;

				ReleaseCacheBuffer(buf_index + index, 1);
			}
		}

		if (finish_cnt < blk_count)
		{
			LOG(INFO) << "[" << __FUNCTION__ << "] failed count=" << dec << (blk_count - finish_cnt);
			MarkReadFailed(image_index + finish_cnt, blk_count - finish_cnt);
		}

		if (finish_cnt < buf_count)
		{
			ReleaseCacheBuffer(buf_index + finish_cnt, buf_count - finish_cnt);
		}

	}

	void StopCacheWork()
	{
		LOG(INFO) << "[" << __FUNCTION__ << "]" << " enter...";

		_stop = true;

		long index = 0;

		Monitor<Mutex>::Lock lock1(_bitmap_lock);
		{
			Monitor<Mutex>::Lock lock2(_cache_map_lock);
			{
				Monitor<Mutex>::Lock lock3(_queue_lock);

				while (true)
				{
					index = _cache_map.pop();
					if (index >= 0)
					{
						_free_queue.put(index);
					}
					else
					{
						break;
					}
				}

				_finish_bitmap.SetBitmapZero();
				_set_bitmap.SetBitmapZero();
				_pending_bitmap.SetBitmapZero();

				_read_index = 0;
				_img_bgn_blk_idx = 0;
				_img_end_blk_idx = 0;

				_queue_lock.notifyAll();
			}
			_cache_map_lock.notifyAll();
		}
		_bitmap_lock.notifyAll();

		LOG(INFO) << "[" << __FUNCTION__ << "]" << " leave...";
	}


};

typedef shared_ptr<ImgCacheWorker> ImgCacheWorkerPtr;

class ReadImgThread :public Thread
{

public:
	ReadImgThread()
	{
		_stop = false;
		_CacheWorker = NULL;
	}

	~ReadImgThread()
	{
		LOG(INFO) << "[" << __FUNCTION__ << "]" << " enter";
	}

	void attach(ImgCacheWorker* CacheWorker)
	{
		_CacheWorker = CacheWorker;
	}

	void run()
	{
		LOG(INFO) << "[" << __FUNCTION__ << "]" << " enter...";

		_ThreadId = (long)pthread_self();

		while (!_stop)
		{
			_CacheWorker->ReadImgToCache(_Buffer);
		}

		LOG(INFO) << "[" << __FUNCTION__ << "]" << " leave...";
	}

	void notify_stop()
	{
		LOG(INFO) << "[" << __FUNCTION__ << "]" << " enter...";
		_stop = true;
	}

private:
	long _ThreadId;
	IMG::BinaryStream _Buffer;
	ImgCacheWorker* _CacheWorker;
	bool _stop;
};

typedef IceUtil::Handle<ReadImgThread> ReadImgThreadPtr;

class ImgThreadMgr
{
public:
	ImgThreadMgr(ImgCacheWorker* CacheWorkerPtr)
		: _ImgThreads(PREAD_THREAD_COUNT)
	{
		LOG(INFO) << "[" << __FUNCTION__ << "]" << " enter";

		int i = 0;

		for (i = 0; i < PREAD_THREAD_COUNT; i++)
		{
			_ImgThreads[i] = new ReadImgThread;
			_ImgThreads[i]->attach(CacheWorkerPtr);
		}

		LOG(INFO) << "[" << __FUNCTION__ << "]" << " finish";
	}

	~ImgThreadMgr()
	{
		LOG(INFO) << "[" << __FUNCTION__ << "]" << " enter";
	}

	void Start()
	{
		int i = 0;

		LOG(INFO) << "[" << __FUNCTION__ << "]" << " enter";

		for (i = 0; i < PREAD_THREAD_COUNT; i++)
		{
			_control[i] = _ImgThreads[i]->start();
		}

		LOG(INFO) << "[" << __FUNCTION__ << "]" << " finish";
	}

	void NotifyStop()
	{
		int i = 0;

		LOG(INFO) << "[" << __FUNCTION__ << "]" << " enter";

		for (i = 0; i < PREAD_THREAD_COUNT; i++)
		{
			_ImgThreads[i]->notify_stop();
		}

		LOG(INFO) << "[" << __FUNCTION__ << "]" << " finish";
	}

	void Wait()
	{
		int i = 0;

		LOG(INFO) << "[" << __FUNCTION__ << "]" << " enter";

		for (i = 0; i < PREAD_THREAD_COUNT; i++)
		{
			_control[i].join();
		}

		LOG(INFO) << "[" << __FUNCTION__ << "]" << " finish";
	}

private:

	vector<ReadImgThreadPtr> _ImgThreads;
	ThreadControl _control[PREAD_THREAD_COUNT];
};

typedef shared_ptr<ImgThreadMgr> ImgThreadMgrPtr;


class ReadCacheableImgWrapper : public ReadableImgWrapper
{
private:
	long _set_count;
	long _hit_count;
	long _read_count;
	long _read_before_cache;
	long _align_read_count;
	long _not_align_read_count;

public:
	ReadCacheableImgWrapper(const ImgServicePrxPoolPtr& prxes, const IMG::ImageSnapshotIdents& snapshot, const string& flag,
		long cache_size, bool EnablePreRead) :
		ReadableImgWrapper(prxes, snapshot, flag, -1)
	{
		_set_count = 0;
		_hit_count = 0;
		_read_count = 0;
		_read_before_cache = 0;
		_align_read_count = 0;
		_not_align_read_count = 0;

		_start_cache_worker = false;
		_cache_size = cache_size;

		_log_dbg_msg = false;

		_disable_cache = (!EnablePreRead);
		if (_disable_cache)
		{
			_disable_cache = true;
			LOG(INFO) << "[" << __FUNCTION__ << "]" << " cache is disable";			
		}
		else
		{
			LOG(INFO) << "[" << __FUNCTION__ << "]" << " cache is enable";
		}

		LOG(INFO) << "[" << __FUNCTION__ << "]" << " _disable_cache=" << dec << _disable_cache;
		LOG(INFO) << "[" << __FUNCTION__ << "]" << " thread count=" << dec << PREAD_THREAD_COUNT;
		LOG(INFO) << "[" << __FUNCTION__ << "]" << " discar step=" << dec << PREREAD_DISCARD_STEP;
		LOG(INFO) << "[" << __FUNCTION__ << "]" << " keep alive count=" << dec << PREREAD_KEEP_ALIVED;
		LOG(INFO) << "[" << __FUNCTION__ << "]" << " cache buffer=" << dec << PREREAD_BUFFER_SIZE;
		LOG(INFO) << "[" << __FUNCTION__ << "]" << " bitmap size=" << dec << PREREAD_BITMAP_BYTES;
		LOG(INFO) << "[" << __FUNCTION__ << "]" << " read count=" << dec << PREREAD_BLOCK_COUNT;
	}

	~ReadCacheableImgWrapper()
	{
		long mis_cache = 0;
		mis_cache = _align_read_count + _not_align_read_count - _read_before_cache - _hit_count;

		LOG(INFO) << "[" << __FUNCTION__ << "]" << " Enter";

		LOG(INFO) << "[" << __FUNCTION__ << "]" << " mis_cache=" << dec << mis_cache;
		LOG(INFO) << "[" << __FUNCTION__ << "]" << " _set_count=" << dec << _set_count;
		LOG(INFO) << "[" << __FUNCTION__ << "]" << " _hit_count=" << dec << _hit_count;
		LOG(INFO) << "[" << __FUNCTION__ << "]" << " _read_count=" << dec << _read_count;

		LOG(INFO) << "[" << __FUNCTION__ << "]" << " _read_before_cache=" << dec << _read_before_cache;
		LOG(INFO) << "[" << __FUNCTION__ << "]" << " _align_read_count=" << dec << _align_read_count;
		LOG(INFO) << "[" << __FUNCTION__ << "]" << " _not_align_read_count=" << dec << _not_align_read_count;

		if (_start_cache_worker)
		{
			_ImgThreadMgrPtr->NotifyStop();
			_CacheWorkerPtr->StopCacheWork();
			_ImgThreadMgrPtr->Wait();
		}

		LOG(INFO) << "[" << __FUNCTION__ << "]" << " Leave";				
	}

	void ReadOnNoCache(Ice::Long byteOffset, Ice::Int bytes, IMG::BinaryStream& bs)
	{
		__sync_fetch_and_add(&_read_count, 1);
		__sync_fetch_and_add(&_not_align_read_count, 1);		
		
		if (_CacheWorkerPtr && _start_cache_worker)
		{
			_CacheWorkerPtr->DiscardCacheData(byteOffset);
		}
		else
		{
			__sync_fetch_and_add(&_read_before_cache, 1);
		}

		read(byteOffset, bytes, bs);
	}
	
	void ReadWithCache(Ice::Long byteOffset, Ice::Int bytes, IMG::BinaryStream& bs)
	{
		bool success = false;

		__sync_fetch_and_add(&_read_count, 1);
		__sync_fetch_and_add(&_align_read_count, 1);

		if (_CacheWorkerPtr && _start_cache_worker)
		{
			try
			{
				long img_index = 0;
				long read_index = 0;

				img_index = byteOffset / BYTE_COUNT_PER_BLOCK;

				success = _CacheWorkerPtr->TryGetDataFromCache(bs, byteOffset, bytes, true);
				read_index = _CacheWorkerPtr->GetCurrentReadIndex();

				if (_log_dbg_msg)
				{
					if (success)
					{
						LOG(INFO) << "[" << __FUNCTION__ << "] read at cache, img_index=" << dec << img_index << " read_index=" << read_index;
					}
					else
					{
						if (img_index < read_index)
						{
							LOG(INFO) << "[" << __FUNCTION__ << "] not at cache, processed, img_index=" << dec << img_index << " read_index=" << read_index;
						}
						else
						{
							LOG(INFO) << "[" << __FUNCTION__ << "] not at cache, not process, img_index=" << dec << img_index << " read_index=" << read_index;
						}					
					}
				}

			}
			catch (...)
			{
				LOG(INFO) << "[" << __FUNCTION__ << "]" << " call GetDataFromCache has exception";
			}
			
		}
		else
		{
			__sync_fetch_and_add(&_read_before_cache, 1);
		}
		
		if (success)
		{
			__sync_fetch_and_add(&_hit_count, 1);
			return;
		}

		readEx(byteOffset, bytes, bs);
	}

	bool SetCacheImageBitmap(const IMG::BinaryStream& bitmap, Ice::Long index)
	{
		bool success = false;

		//LOG(INFO) << "[" << __FUNCTION__ << "]" << " enter...";

		if (_disable_cache)
		{
			LOG(INFO) << "[" << __FUNCTION__ << "]" << " cache is disable!";
			return false;
		}

		long ret_val = (long)access(PREREAD_LOG_DBG, F_OK);
		if (ret_val == 0)
		{
			_log_dbg_msg = true;
		}
		else
		{
			_log_dbg_msg = false;
		}

		Monitor<Mutex>::Lock lock(_cache_lock);

		_set_count++;

		try
		{
			if (!_start_cache_worker)
			{
				LOG(INFO) << "[" << __FUNCTION__ << "]" << " start cache thread...";

				_CacheWorkerPtr = make_shared<ImgCacheWorker>(_cache_size);
				_CacheWorkerPtr->SetReadImagePointer(this);
				_CacheWorkerPtr->SetCacheImageBitmap(bitmap, index, _log_dbg_msg);

				_ImgThreadMgrPtr = make_shared<ImgThreadMgr>(_CacheWorkerPtr.get());
				_ImgThreadMgrPtr->Start();

				_start_cache_worker = true;
			}
			else
			{
				_CacheWorkerPtr->SetCacheImageBitmap(bitmap, index, _log_dbg_msg);
			}

			success = true;
		}
		catch (...)
		{
			LOG(INFO) << "[" << __FUNCTION__ << "]" << " has exception...";
		}

		return success;
	}

private:

	long _thread_count;
	long _cache_size;
	bool _start_cache_worker;
	bool _disable_cache;
	bool _log_dbg_msg;

	Monitor<Mutex> _cache_lock;
	
	ImgThreadMgrPtr _ImgThreadMgrPtr;
	ImgCacheWorkerPtr _CacheWorkerPtr;
};


typedef shared_ptr<ReadCacheableImgWrapper> ReadCacheableImgWrapperPtr;

