#pragma once

#include "utils.ice"

module WatchPowerServ {

  interface PowerOffProc {

    string CreatePowerOffProc(string servName, string procScript)
      throws Utils::SystemError;

    void DeletePowerOffProc(string ident)
      throws Utils::SystemError;

    string GetTime()
      throws Utils::SystemError;

  };

};