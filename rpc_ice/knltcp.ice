#pragma once

#include "utils.ice"
#include "img.ice"

module KTService {

  sequence<byte> BinaryStream;

  struct Token {
    string                    token;
    IMG::ImageSnapshotIdents  snapshot;                         //only one and the path is ".cdp", mean cdp token
    int                       keepAliveIntervalSeconds  = 3600;
    int                       expiryMinutes             = 1440; //when value is 0，mean immediately delete token
    long                      diskBytes                 = 0;    //valid when cdp token
  };

  interface KTS {

    void ping();

    void update(Token token)
      throws Utils::SystemError;

    void updateTrafficControl(long ioSession, string ident, int kiloBytesPerSecond)
      throws Utils::SystemError;

    void refreshNetwork();

    idempotent void setPreReadBitmap(Token token, long index, BinaryStream bitmap)
      throws Utils::SystemError;	  
  };
};