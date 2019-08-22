#pragma once

#include "utils.ice"

module CProxy {

  struct EndPoint {
    int    Index;
    string IpAddress;
    int    Port;
  };

  sequence<EndPoint> EndPoints;

  interface TunnelManager {

    void Update(EndPoints endPoints)
      throws Utils::SystemError;

    int QueryIndexByInternalLinkSourcePort(int port)
      throws Utils::SystemError;

  };

};