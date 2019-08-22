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
// Generated from file `CustomizedOS.ice'
//
// Warning: do not edit this file.
//
// </auto-generated>
//

(function(module, require, exports)
{
    var Ice = require("ice").Ice;
    var __M = Ice.__M;
    var Utils = require("utils").Utils;
    var Slice = Ice.Slice;

    var CustomizedOS = __M.module("CustomizedOS");
    Slice.defineSequence(CustomizedOS, "BinaryStreamHelper", "Ice.ByteHelper", true);

    CustomizedOS.MiniLoader = Slice.defineObject(
        undefined,
        Ice.Object, undefined, 0,
        [
            "::CustomizedOS::MiniLoader",
            "::Ice::Object"
        ],
        -1, undefined, undefined, false);

    CustomizedOS.MiniLoaderPrx = Slice.defineProxy(Ice.ObjectPrx, CustomizedOS.MiniLoader.ice_staticId, undefined);

    Slice.defineOperations(CustomizedOS.MiniLoader, CustomizedOS.MiniLoaderPrx,
    {
        "popen": [, , , , , [7], [[7]], , 
        [
            Utils.SystemError
        ], , ],
        "rwFile": [, 2, 2, , , [7], [[7], ["CustomizedOS.BinaryStreamHelper"]], [["CustomizedOS.BinaryStreamHelper"]], 
        [
            Utils.SystemError
        ], , ],
        "getRunPath": [, , , , , [7], , , 
        [
            Utils.SystemError
        ], , ]
    });

    CustomizedOS.CallbackSender = Slice.defineObject(
        undefined,
        Ice.Object, undefined, 0,
        [
            "::CustomizedOS::CallbackSender",
            "::Ice::Object"
        ],
        -1, undefined, undefined, false);

    CustomizedOS.CallbackSenderPrx = Slice.defineProxy(Ice.ObjectPrx, CustomizedOS.CallbackSender.ice_staticId, undefined);

    Slice.defineOperations(CustomizedOS.CallbackSender, CustomizedOS.CallbackSenderPrx,
    {
        "addClient": [, , , , , , [[Ice.Identity]], , 
        [
            Utils.SystemError
        ], , ]
    });
    exports.CustomizedOS = CustomizedOS;
}
(typeof(global) !== "undefined" && typeof(global.process) !== "undefined" ? module : undefined,
 typeof(global) !== "undefined" && typeof(global.process) !== "undefined" ? require : window.Ice.__require,
 typeof(global) !== "undefined" && typeof(global.process) !== "undefined" ? exports : window));
