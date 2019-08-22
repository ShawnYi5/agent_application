// **********************************************************************
//
// Copyright (c) 2003-2015 ZeroC, Inc. All rights reserved.
//
// This copy of Ice is licensed to you under the terms described in the
// ICE_LICENSE file included in this distribution.
//
// **********************************************************************
//
// Ice version 3.6.1
//
// <auto-generated>
//
// Generated from file `box_api.ice'
//
// Warning: do not edit this file.
//
// </auto-generated>
//

(function(module, require, exports)
{
    var Ice = require("ice").Ice;
    var __M = Ice.__M;
    var BoxLogic = require("logic").BoxLogic;
    var IMG = require("img").IMG;
    var PerpcIce = require("perpcice").PerpcIce;
    var Utils = require("utils").Utils;
    var Slice = Ice.Slice;

    var Box = __M.module("Box");
    Slice.defineSequence(Box, "BinaryStreamHelper", "Ice.ByteHelper", true);

    Box.BackupFile = Slice.defineStruct(
        function(diskIndex, diskIdent, snapshot, lastSnapshot, diskByteSize, enableCDP, cdpConfig, jsonConfig)
        {
            this.diskIndex = diskIndex !== undefined ? diskIndex : 0;
            this.diskIdent = diskIdent !== undefined ? diskIdent : "";
            this.snapshot = snapshot !== undefined ? snapshot : new IMG.ImageSnapshotIdent();
            this.lastSnapshot = lastSnapshot !== undefined ? lastSnapshot : null;
            this.diskByteSize = diskByteSize !== undefined ? diskByteSize : 0;
            this.enableCDP = enableCDP !== undefined ? enableCDP : false;
            this.cdpConfig = cdpConfig !== undefined ? cdpConfig : new BoxLogic.CDPConfig();
            this.jsonConfig = jsonConfig !== undefined ? jsonConfig : "";
        },
        true,
        function(__os)
        {
            __os.writeInt(this.diskIndex);
            __os.writeString(this.diskIdent);
            IMG.ImageSnapshotIdent.write(__os, this.snapshot);
            IMG.ImageSnapshotIdentsHelper.write(__os, this.lastSnapshot);
            __os.writeLong(this.diskByteSize);
            __os.writeBool(this.enableCDP);
            BoxLogic.CDPConfig.write(__os, this.cdpConfig);
            __os.writeString(this.jsonConfig);
        },
        function(__is)
        {
            this.diskIndex = __is.readInt();
            this.diskIdent = __is.readString();
            this.snapshot = IMG.ImageSnapshotIdent.read(__is, this.snapshot);
            this.lastSnapshot = IMG.ImageSnapshotIdentsHelper.read(__is);
            this.diskByteSize = __is.readLong();
            this.enableCDP = __is.readBool();
            this.cdpConfig = BoxLogic.CDPConfig.read(__is, this.cdpConfig);
            this.jsonConfig = __is.readString();
        },
        35, 
        false);
    Slice.defineSequence(Box, "BackupFilesHelper", "Box.BackupFile", false);

    Box.RestoreFile = Slice.defineStruct(
        function(diskIndex, diskBytes, snapshot)
        {
            this.diskIndex = diskIndex !== undefined ? diskIndex : 0;
            this.diskBytes = diskBytes !== undefined ? diskBytes : 0;
            this.snapshot = snapshot !== undefined ? snapshot : null;
        },
        true,
        function(__os)
        {
            __os.writeInt(this.diskIndex);
            __os.writeLong(this.diskBytes);
            IMG.ImageSnapshotIdentsHelper.write(__os, this.snapshot);
        },
        function(__is)
        {
            this.diskIndex = __is.readInt();
            this.diskBytes = __is.readLong();
            this.snapshot = IMG.ImageSnapshotIdentsHelper.read(__is);
        },
        13, 
        false);
    Slice.defineSequence(Box, "RestoreFilesHelper", "Box.RestoreFile", false);

    Box.ServiceInfoStatus = Slice.defineStruct(
        function(lpDisplayName, lpServiceName, dwServiceType, dwCurrentState, dwWin32ExitCode, dwServiceSpecificExitCode, dwProcessId, dwServiceFlags)
        {
            this.lpDisplayName = lpDisplayName !== undefined ? lpDisplayName : "";
            this.lpServiceName = lpServiceName !== undefined ? lpServiceName : "";
            this.dwServiceType = dwServiceType !== undefined ? dwServiceType : 0;
            this.dwCurrentState = dwCurrentState !== undefined ? dwCurrentState : 0;
            this.dwWin32ExitCode = dwWin32ExitCode !== undefined ? dwWin32ExitCode : 0;
            this.dwServiceSpecificExitCode = dwServiceSpecificExitCode !== undefined ? dwServiceSpecificExitCode : 0;
            this.dwProcessId = dwProcessId !== undefined ? dwProcessId : 0;
            this.dwServiceFlags = dwServiceFlags !== undefined ? dwServiceFlags : 0;
        },
        true,
        function(__os)
        {
            __os.writeString(this.lpDisplayName);
            __os.writeString(this.lpServiceName);
            __os.writeInt(this.dwServiceType);
            __os.writeInt(this.dwCurrentState);
            __os.writeInt(this.dwWin32ExitCode);
            __os.writeInt(this.dwServiceSpecificExitCode);
            __os.writeInt(this.dwProcessId);
            __os.writeInt(this.dwServiceFlags);
        },
        function(__is)
        {
            this.lpDisplayName = __is.readString();
            this.lpServiceName = __is.readString();
            this.dwServiceType = __is.readInt();
            this.dwCurrentState = __is.readInt();
            this.dwWin32ExitCode = __is.readInt();
            this.dwServiceSpecificExitCode = __is.readInt();
            this.dwProcessId = __is.readInt();
            this.dwServiceFlags = __is.readInt();
        },
        26, 
        false);
    Slice.defineSequence(Box, "ServiceInfoStatusSHelper", "Box.ServiceInfoStatus", false);
    Slice.defineSequence(Box, "vectorINTHelper", "Ice.IntHelper", true);

    Box.Apis = Slice.defineObject(
        undefined,
        Ice.Object, undefined, 0,
        [
            "::Box::Apis",
            "::Ice::Object"
        ],
        -1, undefined, undefined, false);

    Box.ApisPrx = Slice.defineProxy(Ice.ObjectPrx, Box.Apis.ice_staticId, undefined);

    Slice.defineOperations(Box.Apis, Box.ApisPrx,
    {
        "ping": [, , , , , , , , , , ],
        "reloginAllHostSession": [, , , , , , [[3]], , , , ],
        "isAgentLinked": [, , , , , [1], [[7]], , , , ],
        "GetStatus": [, , , , , ["BoxLogic.AgentStatusHelper"], [[7]], , , , ],
        "queryDisksStatus": [, , , , , , [[7]], [["BoxLogic.DisksHelper"], [7, , 1]], 
        [
            Utils.SystemError
        ], , ],
        "JsonFunc": [, , , , , [7], [[7], [7]], , 
        [
            Utils.SystemError
        ], , ],
        "querySystemInfo": [, , , , , [7], [[7]], , 
        [
            Utils.SystemError
        ], , ],
        "backup": [, , , , , , [[7], ["Box.BackupFilesHelper"], [3], [7, , 1]], , 
        [
            Utils.CreateSnapshotImageError,
            Utils.SystemError
        ], , ],
        "forceCloseBackupFiles": [, , , , , , [["Ice.StringSeqHelper"]], , , , ],
        "getBackupInfo": [, , , , , [7], [[7], [7]], , 
        [
            Utils.SystemError
        ], , ],
        "setBackupInfo": [, , , , , , [[7], [7]], , 
        [
            Utils.SystemError
        ], , ],
        "queryLastBackupError": [, , , , , [7], [[7]], , , , ],
        "queryLastCdpError": [, , , , , [7], [[7]], , , , ],
        "stopCdpStatus": [, , , , , , [[7]], , 
        [
            Utils.SystemError
        ], , ],
        "volumeRestore": [, , , , , , [[7], [7], ["Box.RestoreFilesHelper"], [7]], , 
        [
            Utils.SystemError
        ], , ],
        "restore": [, , , , , , [[7], [PerpcIce.PeRestoreInfo], ["Box.RestoreFilesHelper"], [7]], , 
        [
            Utils.SystemError
        ], , ],
        "setBootDataList": [, , , , , , [[7], [7]], , 
        [
            Utils.SystemError
        ], , ],
        "notifyHighPriority": [, , , , , , [[4], [4]], , 
        [
            Utils.SystemError
        ], , ],
        "ReadDiskWithPeHost": [, , , , , [3], [[7], [7], [4], [3]], [["Box.BinaryStreamHelper"]], 
        [
            Utils.SystemError
        ], , ],
        "WriteDiskWithPeHost": [, , , , , [3], [[7], [7], [4], [3], ["Box.BinaryStreamHelper"]], , 
        [
            Utils.SystemError
        ], , ],
        "QueryRWDiskWithPeHost": [, , , , , [1], [[7]], [[4], [4]], 
        [
            Utils.SystemError
        ], , ],
        "KvmStopped": [, , , , , , [[7]], , 
        [
            Utils.SystemError
        ], , ],
        "GetPeHostClassHWInfo": [, , , , , [3], [[7], [7], [3]], [["PerpcIce.HWInfosHelper"]], 
        [
            Utils.SystemError
        ], , ],
        "GetPeHostNetAdapterInfo": [, , , , , [3], [[7]], [["PerpcIce.NetAdapterInfosHelper"]], 
        [
            Utils.SystemError
        ], , ],
        "isPeHostLinked": [, , , , , [1], [[7]], , , , ],
        "StartAgentPe": [, , , , , [7], [[7]], , 
        [
            Utils.SystemError
        ], , ],
        "fetchAgentDebugFile": [, , , , , , [[7], [7]], , 
        [
            Utils.SystemError
        ], , ],
        "queryRunnerAbsPathOnAgentSetup": [, , , , , [7], [[7]], , 
        [
            Utils.SystemError
        ], , ],
        "prepareInfoOnAgentSetup": [, , , , , [7], [[7], [7]], , 
        [
            Utils.SystemError
        ], , ],
        "getFileInfoOnAgentSetup": [, , , , , [7], [[7], [7], [7]], , 
        [
            Utils.SystemError
        ], , ],
        "searchBootFileAbsPathOnAgentSetup": [, , , , , [7], [[7]], , 
        [
            Utils.SystemError
        ], , ],
        "generateKeyInfosOnAgentSetup": [, , , , , , [[7], [7], [7]], , 
        [
            Utils.SystemError
        ], , ],
        "openOnAgentSetup": [, , , , , [7], [[7], [7], [7]], , 
        [
            Utils.SystemError
        ], , ],
        "preadOnAgentSetup": [, , , , , ["Ice.ByteSeqHelper"], [[7], [7], [4], [3]], , 
        [
            Utils.SystemError
        ], , ],
        "pwriteOnAgentSetup": [, , , , , , [[7], [7], [4], [3], ["Ice.ByteSeqHelper"]], , 
        [
            Utils.SystemError
        ], , ],
        "closeOnAgentSetup": [, , , , , , [[7], [7]], , 
        [
            Utils.SystemError
        ], , ],
        "extractFileOnAgentSetup": [, , , , , , [[7], [7], [7], [7]], , 
        [
            Utils.SystemError
        ], , ],
        "executeCommandOnAgentSetup": [, , , , , [3], [[7], [7], [7]], [["Ice.StringSeqHelper"], ["Ice.StringSeqHelper"]], 
        [
            Utils.SystemError
        ], , ],
        "reportStatusOnAgentSetup": [, , , , , , [[7], [7]], , 
        [
            Utils.SystemError
        ], , ],
        "exitOnAgentSetup": [, , , , , , [[7], [3]], , 
        [
            Utils.SystemError
        ], , ],
        "forceOfflineAgent": [, , , , , , [[7]], , 
        [
            Utils.SystemError
        ], , ],
        "forceOfflinePeHost": [, , , , , , [[7]], , 
        [
            Utils.SystemError
        ], , ],
        "refreshNetwork": [, , , , , , , , , , ],
        "GetServiceList": [, , , , , [3], [[7]], [["Box.ServiceInfoStatusSHelper"]], 
        [
            Utils.SystemError
        ], , ],
        "GetTcpListenList": [, , , , , [3], [[7], ["Box.vectorINTHelper"]], [["Box.vectorINTHelper"]], 
        [
            Utils.SystemError
        ], , ],
        "StartServiceSync": [, , , , , [3], [[7], [7]], , 
        [
            Utils.SystemError
        ], , ],
        "StopServiceSync": [, , , , , [3], [[7], [7]], , 
        [
            Utils.SystemError
        ], , ],
        "StartHttpDServiceAsync": [, , , , , [3], [[7], [3], ["Box.BinaryStreamHelper"]], , 
        [
            Utils.SystemError
        ], , ],
        "GetHttpDServiceListSync": [, , , , , [3], [[7]], [["Box.vectorINTHelper"]], 
        [
            Utils.SystemError
        ], , ],
        "StopAllHttpDServiceSync": [, , , , , [3], [[7]], , 
        [
            Utils.SystemError
        ], , ],
        "testDisk": [, , , , , [3], [[7], [3], [4], [2]], , 
        [
            Utils.SystemError
        ], , ],
        "readDisk": [, , , , , [3], [[7], [3], [4], [2]], [["Box.BinaryStreamHelper"]], 
        [
            Utils.SystemError
        ], , ],
        "writeDisk": [, , , , , [3], [[7], [3], [4], [2], ["Box.BinaryStreamHelper"]], , 
        [
            Utils.SystemError
        ], , ],
        "JsonFuncV2": [, , , , , [7], [[7], [7], ["Box.BinaryStreamHelper"]], [["Box.BinaryStreamHelper"]], 
        [
            Utils.SystemError
        ], , ],
        "PEJsonFunc": [, , , , , [7], [[7], [7], ["Box.BinaryStreamHelper"]], [["Box.BinaryStreamHelper"]], 
        [
            Utils.OperationNotExistError,
            Utils.SystemError
        ], , ]
    });
    exports.Box = Box;
}
(typeof(global) !== "undefined" && typeof(global.process) !== "undefined" ? module : undefined,
 typeof(global) !== "undefined" && typeof(global.process) !== "undefined" ? require : window.Ice.__require,
 typeof(global) !== "undefined" && typeof(global.process) !== "undefined" ? exports : window));
