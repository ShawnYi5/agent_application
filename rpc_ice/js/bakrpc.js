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
// Generated from file `bakrpc.ice'
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

    var bakrpc = __M.module("bakrpc");
    Slice.defineSequence(bakrpc, "BinaryStreamHelper", "Ice.ByteHelper", true);

    bakrpc.BackupRPC = Slice.defineObject(
        undefined,
        Ice.Object, undefined, 1,
        [
            "::Ice::Object",
            "::bakrpc::BackupRPC"
        ],
        -1, undefined, undefined, false);

    bakrpc.BackupRPCPrx = Slice.defineProxy(Ice.ObjectPrx, bakrpc.BackupRPC.ice_staticId, undefined);

    Slice.defineOperations(bakrpc.BackupRPC, bakrpc.BackupRPCPrx,
    {
        "callFunction": [, , , , , [3], [[7], [7], ["bakrpc.BinaryStreamHelper"]], [[7], ["bakrpc.BinaryStreamHelper"]], 
        [
            Utils.SystemError
        ], , ]
    });

    var kvm4remote = __M.module("kvm4remote");
    Slice.defineSequence(kvm4remote, "BinaryStreamHelper", "Ice.ByteHelper", true);

    kvm4remote.KVM = Slice.defineObject(
        undefined,
        Ice.Object, undefined, 1,
        [
            "::Ice::Object",
            "::kvm4remote::KVM"
        ],
        -1, undefined, undefined, false);

    kvm4remote.KVMPrx = Slice.defineProxy(Ice.ObjectPrx, kvm4remote.KVM.ice_staticId, undefined);

    Slice.defineOperations(kvm4remote.KVM, kvm4remote.KVMPrx,
    {
        "SetRemoteCallable": [, , , , , , [[7], ["Utils.CallablePrx"]], , 
        [
            Utils.SystemError
        ], , ],
        "CleanRemoteCallable": [, , , , , , [[7]], , , , ],
        "getKVMCallable": [, , , , , ["Utils.CallablePrx"], , , 
        [
            Utils.SystemError
        ], , ]
    });
    exports.bakrpc = bakrpc;
    exports.kvm4remote = kvm4remote;
}
(typeof(global) !== "undefined" && typeof(global.process) !== "undefined" ? module : undefined,
 typeof(global) !== "undefined" && typeof(global.process) !== "undefined" ? require : window.Ice.__require,
 typeof(global) !== "undefined" && typeof(global.process) !== "undefined" ? exports : window));
