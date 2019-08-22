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
// Generated from file `data_queuing.ice'
//
// Warning: do not edit this file.
//
// </auto-generated>
//

(function(module, require, exports)
{
    var Ice = require("ice").Ice;
    var __M = Ice.__M;
    var IMG = require("img").IMG;
    var Utils = require("utils").Utils;
    var Slice = Ice.Slice;

    var DataQueuingIce = __M.module("DataQueuingIce");
    Slice.defineSequence(DataQueuingIce, "BinaryStreamHelper", "Ice.ByteHelper", true);

    DataQueuingIce.DiskBitmap = Slice.defineStruct(
        function(token, bitmap)
        {
            this.token = token !== undefined ? token : "";
            this.bitmap = bitmap !== undefined ? bitmap : null;
        },
        true,
        function(__os)
        {
            __os.writeString(this.token);
            DataQueuingIce.BinaryStreamHelper.write(__os, this.bitmap);
        },
        function(__is)
        {
            this.token = __is.readString();
            this.bitmap = DataQueuingIce.BinaryStreamHelper.read(__is);
        },
        2, 
        false);

    DataQueuingIce.DiskBitmapv2 = Slice.defineStruct(
        function(token, bitmapPath)
        {
            this.token = token !== undefined ? token : "";
            this.bitmapPath = bitmapPath !== undefined ? bitmapPath : "";
        },
        true,
        function(__os)
        {
            __os.writeString(this.token);
            __os.writeString(this.bitmapPath);
        },
        function(__is)
        {
            this.token = __is.readString();
            this.bitmapPath = __is.readString();
        },
        2, 
        false);
    Slice.defineSequence(DataQueuingIce, "DiskBitmapsHelper", "DataQueuingIce.DiskBitmap", false);

    DataQueuingIce.ExcludeRun = Slice.defineStruct(
        function(byteOffset, bytes)
        {
            this.byteOffset = byteOffset !== undefined ? byteOffset : 0;
            this.bytes = bytes !== undefined ? bytes : 0;
        },
        true,
        function(__os)
        {
            __os.writeLong(this.byteOffset);
            __os.writeLong(this.bytes);
        },
        function(__is)
        {
            this.byteOffset = __is.readLong();
            this.bytes = __is.readLong();
        },
        16, 
        true);
    Slice.defineSequence(DataQueuingIce, "ExcludeRunsHelper", "DataQueuingIce.ExcludeRun", true);

    DataQueuingIce.WorkType = Slice.defineEnum([
        ['noneWork', 0], ['cdpWork', 1], ['qemuWork', 2]]);

    DataQueuingIce.DataCreator = Slice.defineObject(
        undefined,
        Ice.Object, undefined, 0,
        [
            "::DataQueuingIce::DataCreator",
            "::Ice::Object"
        ],
        -1, undefined, undefined, false);

    DataQueuingIce.DataCreatorPrx = Slice.defineProxy(Ice.ObjectPrx, DataQueuingIce.DataCreator.ice_staticId, undefined);

    Slice.defineOperations(DataQueuingIce.DataCreator, DataQueuingIce.DataCreatorPrx,
    {
        "StartCDPWork": [, , , , , [3], [[7], [7], [7], [7], [1], ["DataQueuingIce.ExcludeRunsHelper"]], , 
        [
            Utils.SystemError
        ], , ],
        "StartQemuWorkForBitmap": [, , , , , [3], [[7], [7], ["IMG.ImageSnapshotIdentsHelper"], ["DataQueuingIce.BinaryStreamHelper"], ["DataQueuingIce.ExcludeRunsHelper"]], , 
        [
            Utils.SystemError
        ], , ],
        "StartQemuWorkForBitmapv2": [, , , , , [3], [[7], [7], ["IMG.ImageSnapshotIdentsHelper"], [7], ["DataQueuingIce.ExcludeRunsHelper"]], , 
        [
            Utils.SystemError
        ], , ],
        "StartQemuWork": [, , , , , [3], [[7], [7], ["IMG.ImageSnapshotIdentsHelper"], ["DataQueuingIce.ExcludeRunsHelper"]], , 
        [
            Utils.SystemError
        ], , ],
        "QueryQemuProgress": [, 2, 2, , , [3], [[7], [7]], [[4], [4], [3]], 
        [
            Utils.SystemError
        ], , ],
        "QueryCDPProgress": [, 2, 2, , , [3], [[7], [7]], [[7], [3]], 
        [
            Utils.SystemError
        ], , ],
        "QueryWorkStatus": [, 2, 2, , , [3], [[7], [7]], [[DataQueuingIce.WorkType.__helper]], 
        [
            Utils.SystemError
        ], , ],
        "StopQemuWork": [, , , , , [3], [[7], [7]], [["DataQueuingIce.BinaryStreamHelper"]], 
        [
            Utils.SystemError
        ], , ],
        "StopQemuWorkv2": [, , , , , [3], [[7], [7]], , 
        [
            Utils.SystemError
        ], , ],
        "StopCDPWork": [, , , , , [3], [[7], [7]], [[7]], 
        [
            Utils.SystemError
        ], , ],
        "SetRestoreBitmap": [, 2, 2, , , [3], [[7], [DataQueuingIce.DiskBitmap]], , 
        [
            Utils.SystemError
        ], , ],
        "SetRestoreBitmapv2": [, 2, 2, , , [3], [[7], [DataQueuingIce.DiskBitmapv2]], , 
        [
            Utils.SystemError
        ], , ],
        "EndTask": [, 2, 2, , , [3], [[7]], , 
        [
            Utils.SystemError
        ], , ],
        "CloseTask": [, 2, 2, , , [3], [[7]], , 
        [
            Utils.SystemError
        ], , ]
    });

    DataQueuingIce.DataGuest = Slice.defineObject(
        undefined,
        Ice.Object, undefined, 0,
        [
            "::DataQueuingIce::DataGuest",
            "::Ice::Object"
        ],
        -1, undefined, undefined, false);

    DataQueuingIce.DataGuestPrx = Slice.defineProxy(Ice.ObjectPrx, DataQueuingIce.DataGuest.ice_staticId, undefined);

    Slice.defineOperations(DataQueuingIce.DataGuest, DataQueuingIce.DataGuestPrx,
    {
        "InitGuest": [, 2, 2, , , [3], [[7], [3]], , 
        [
            Utils.SystemError
        ], , ],
        "GetData": [, , , , , [3], [[7], [3]], [[4], [7], [4], [3], ["DataQueuingIce.BinaryStreamHelper"], [1]], 
        [
            Utils.SystemError
        ], , ],
        "GetDataEx": [, 2, 2, , , [3], [[7], [3], [4]], [[4], [7], [4], [3], ["DataQueuingIce.BinaryStreamHelper"], [1], [4], [4], [3], [3], [3], [3], [3]], 
        [
            Utils.SystemError
        ], , ],
        "DataCompleted": [, , , , , [3], [[7], [3], [4]], , 
        [
            Utils.SystemError
        ], , ],
        "GetBitmapInfo": [, 2, 2, , , [3], [[7]], [[3]], 
        [
            Utils.SystemError
        ], , ],
        "GetBitmapData": [, 2, 2, , , [3], [[7], [3], [3], [3]], [[7], ["DataQueuingIce.BinaryStreamHelper"], [1]], 
        [
            Utils.SystemError
        ], , ]
    });
    exports.DataQueuingIce = DataQueuingIce;
}
(typeof(global) !== "undefined" && typeof(global.process) !== "undefined" ? module : undefined,
 typeof(global) !== "undefined" && typeof(global.process) !== "undefined" ? require : window.Ice.__require,
 typeof(global) !== "undefined" && typeof(global.process) !== "undefined" ? exports : window));