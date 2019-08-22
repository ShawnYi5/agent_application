#pragma once

#include <Ice/Identity.ice>
#include "utils.ice"
#include "img.ice"

module DataQueuingIce {

  sequence<byte> BinaryStream;
  
  struct DiskBitmap {
    string            token;
    BinaryStream      bitmap;
  };

  struct DiskBitmapv2 {
    string            token;
    string            bitmapPath;
  };

  sequence<DiskBitmap> DiskBitmaps;
  
  struct ExcludeRun {
    long  byteOffset;
    long  bytes;
  };

  sequence<ExcludeRun> ExcludeRuns;
  
  enum WorkType {
    noneWork = 0,
    cdpWork,
    qemuWork
  };

  interface DataCreator {

	int StartCDPWork(string task, string token, string cdpFileName, string startTime, bool watch, ExcludeRuns excludeRuns)
		throws Utils::SystemError;

	int StartQemuWorkForBitmap(string task, string token, IMG::ImageSnapshotIdents  snapshot, BinaryStream bitmap, ExcludeRuns excludeRuns) 
		throws Utils::SystemError;

	int StartQemuWorkForBitmapv2(string task, string token, IMG::ImageSnapshotIdents  snapshot, string bitmapPath, ExcludeRuns excludeRuns)
		throws Utils::SystemError;

	int StartQemuWork(string task, string token, IMG::ImageSnapshotIdents  snapshot, ExcludeRuns excludeRuns)
		throws Utils::SystemError;

	idempotent int QueryQemuProgress(string task, string token, out long totalBytes, out long completedBytes, out int queueLen)
		throws Utils::SystemError;

	idempotent int QueryCDPProgress(string task, string token, out string lastTime, out int queueLen)
		throws Utils::SystemError;

	idempotent int QueryWorkStatus(string task, string token, out WorkType workType)
		throws Utils::SystemError;

	int StopQemuWork(string task, string token, out BinaryStream bitmap)
		throws Utils::SystemError;

	int StopQemuWorkv2(string task, string token)
		throws Utils::SystemError;

	int StopCDPWork(string task, string token, out string lastTime)
		throws Utils::SystemError;

	idempotent int SetRestoreBitmap(string task, DiskBitmap diskBitmap)
		throws Utils::SystemError;

	idempotent int SetRestoreBitmapv2(string task, DiskBitmapv2 diskBitmap)
        throws Utils::SystemError;

	idempotent int EndTask(string task)
		throws Utils::SystemError;

	idempotent int CloseTask(string task)
		throws Utils::SystemError;

  };

  interface DataGuest {

	idempotent int InitGuest(string task, int QueueIdent)
		throws Utils::SystemError;

	int GetData(string task, int QueueIdent, out long DataIdent, 
						out string token, out long Lba, out int secs, out BinaryStream data, out bool isEnd)
		throws Utils::SystemError;

		
	idempotent int GetDataEx(string task, int QueueIdent, long CompletedDataIdent, out long DataIdent, 
						out string token, out long Lba, out int secs, out BinaryStream data, out bool isEnd, out long sn, out long TimeSeconds, out int TimeMicroseconds, out int crc, out int dataType, out int fragmentTotals, out int fragmentIndex)
		throws Utils::SystemError;
		
	int DataCompleted(string task, int QueueIdent, long DataIdent)
		throws Utils::SystemError;

	idempotent int GetBitmapInfo(string task, out int bitmapCount)
		throws Utils::SystemError;

	idempotent int GetBitmapData(string task, int bitmapId, int bitmapOffset, int maxbytes, out string token, out BinaryStream data, out bool isEnd)
		throws Utils::SystemError;

  };

};