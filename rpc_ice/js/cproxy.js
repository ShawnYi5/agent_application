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
// Generated from file `cproxy.ice'
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

    var CProxy = __M.module("CProxy");

    CProxy.EndPoint = Slice.defineStruct(
        function(Index, IpAddress, Port)
        {
            this.Index = Index !== undefined ? Index : 0;
            this.IpAddress = IpAddress !== undefined ? IpAddress : "";
            this.Port = Port !== undefined ? Port : 0;
        },
        true,
        function(__os)
        {
            __os.writeInt(this.Index);
            __os.writeString(this.IpAddress);
            __os.writeInt(this.Port);
        },
        function(__is)
        {
            this.Index = __is.readInt();
            this.IpAddress = __is.readString();
            this.Port = __is.readInt();
        },
        9, 
        false);
    Slice.defineSequence(CProxy, "EndPointsHelper", "CProxy.EndPoint", false);

    CProxy.TunnelManager = Slice.defineObject(
        undefined,
        Ice.Object, undefined, 0,
        [
            "::CProxy::TunnelManager",
            "::Ice::Object"
        ],
        -1, undefined, undefined, false);

    CProxy.TunnelManagerPrx = Slice.defineProxy(Ice.ObjectPrx, CProxy.TunnelManager.ice_staticId, undefined);

    Slice.defineOperations(CProxy.TunnelManager, CProxy.TunnelManagerPrx,
    {
        "Update": [, , , , , , [["CProxy.EndPointsHelper"]], , 
        [
            Utils.SystemError
        ], , ],
        "QueryIndexByInternalLinkSourcePort": [, , , , , [3], [[3]], , 
        [
            Utils.SystemError
        ], , ]
    });
    exports.CProxy = CProxy;
}
(typeof(global) !== "undefined" && typeof(global.process) !== "undefined" ? module : undefined,
 typeof(global) !== "undefined" && typeof(global.process) !== "undefined" ? require : window.Ice.__require,
 typeof(global) !== "undefined" && typeof(global.process) !== "undefined" ? exports : window));