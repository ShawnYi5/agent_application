# -*- coding: utf-8 -*-
# **********************************************************************
#
# Copyright (c) 2003-2017 ZeroC, Inc. All rights reserved.
#
# This copy of Ice is licensed to you under the terms described in the
# ICE_LICENSE file included in this distribution.
#
# **********************************************************************
#
# Ice version 3.6.4
#
# <auto-generated>
#
# Generated from file `bakrpc.ice'
#
# Warning: do not edit this file.
#
# </auto-generated>
#

from sys import version_info as _version_info_
import Ice, IcePy
import utils_ice

# Included module Utils
_M_Utils = Ice.openModule('Utils')

# Start of module bakrpc
_M_bakrpc = Ice.openModule('bakrpc')
__name__ = 'bakrpc'

if '_t_BinaryStream' not in _M_bakrpc.__dict__:
    _M_bakrpc._t_BinaryStream = IcePy.defineSequence('::bakrpc::BinaryStream', (), IcePy._t_byte)

if 'BackupRPC' not in _M_bakrpc.__dict__:
    _M_bakrpc.BackupRPC = Ice.createTempClass()
    class BackupRPC(Ice.Object):
        def __init__(self):
            if Ice.getType(self) == _M_bakrpc.BackupRPC:
                raise RuntimeError('bakrpc.BackupRPC is an abstract class')

        def ice_ids(self, current=None):
            return ('::Ice::Object', '::bakrpc::BackupRPC')

        def ice_id(self, current=None):
            return '::bakrpc::BackupRPC'

        def ice_staticId():
            return '::bakrpc::BackupRPC'
        ice_staticId = staticmethod(ice_staticId)

        def callFunction(self, callJson, inJson, inRaw, current=None):
            pass

        def __str__(self):
            return IcePy.stringify(self, _M_bakrpc._t_BackupRPC)

        __repr__ = __str__

    _M_bakrpc.BackupRPCPrx = Ice.createTempClass()
    class BackupRPCPrx(Ice.ObjectPrx):

        def callFunction(self, callJson, inJson, inRaw, _ctx=None):
            return _M_bakrpc.BackupRPC._op_callFunction.invoke(self, ((callJson, inJson, inRaw), _ctx))

        def begin_callFunction(self, callJson, inJson, inRaw, _response=None, _ex=None, _sent=None, _ctx=None):
            return _M_bakrpc.BackupRPC._op_callFunction.begin(self, ((callJson, inJson, inRaw), _response, _ex, _sent, _ctx))

        def end_callFunction(self, _r):
            return _M_bakrpc.BackupRPC._op_callFunction.end(self, _r)

        def checkedCast(proxy, facetOrCtx=None, _ctx=None):
            return _M_bakrpc.BackupRPCPrx.ice_checkedCast(proxy, '::bakrpc::BackupRPC', facetOrCtx, _ctx)
        checkedCast = staticmethod(checkedCast)

        def uncheckedCast(proxy, facet=None):
            return _M_bakrpc.BackupRPCPrx.ice_uncheckedCast(proxy, facet)
        uncheckedCast = staticmethod(uncheckedCast)

        def ice_staticId():
            return '::bakrpc::BackupRPC'
        ice_staticId = staticmethod(ice_staticId)

    _M_bakrpc._t_BackupRPCPrx = IcePy.defineProxy('::bakrpc::BackupRPC', BackupRPCPrx)

    _M_bakrpc._t_BackupRPC = IcePy.defineClass('::bakrpc::BackupRPC', BackupRPC, -1, (), True, False, None, (), ())
    BackupRPC._ice_type = _M_bakrpc._t_BackupRPC

    BackupRPC._op_callFunction = IcePy.Operation('callFunction', Ice.OperationMode.Normal, Ice.OperationMode.Normal, False, None, (), (((), IcePy._t_string, False, 0), ((), IcePy._t_string, False, 0), ((), _M_bakrpc._t_BinaryStream, False, 0)), (((), IcePy._t_string, False, 0), ((), _M_bakrpc._t_BinaryStream, False, 0)), ((), IcePy._t_int, False, 0), (_M_Utils._t_SystemError,))

    _M_bakrpc.BackupRPC = BackupRPC
    del BackupRPC

    _M_bakrpc.BackupRPCPrx = BackupRPCPrx
    del BackupRPCPrx

# End of module bakrpc

# Start of module kvm4remote
_M_kvm4remote = Ice.openModule('kvm4remote')
__name__ = 'kvm4remote'

if '_t_BinaryStream' not in _M_kvm4remote.__dict__:
    _M_kvm4remote._t_BinaryStream = IcePy.defineSequence('::kvm4remote::BinaryStream', (), IcePy._t_byte)

if 'KVM' not in _M_kvm4remote.__dict__:
    _M_kvm4remote.KVM = Ice.createTempClass()
    class KVM(Ice.Object):
        def __init__(self):
            if Ice.getType(self) == _M_kvm4remote.KVM:
                raise RuntimeError('kvm4remote.KVM is an abstract class')

        def ice_ids(self, current=None):
            return ('::Ice::Object', '::kvm4remote::KVM')

        def ice_id(self, current=None):
            return '::kvm4remote::KVM'

        def ice_staticId():
            return '::kvm4remote::KVM'
        ice_staticId = staticmethod(ice_staticId)

        def SetRemoteCallable(self, ident, callable, current=None):
            pass

        def CleanRemoteCallable(self, ident, current=None):
            pass

        def getKVMCallable(self, current=None):
            pass

        def __str__(self):
            return IcePy.stringify(self, _M_kvm4remote._t_KVM)

        __repr__ = __str__

    _M_kvm4remote.KVMPrx = Ice.createTempClass()
    class KVMPrx(Ice.ObjectPrx):

        def SetRemoteCallable(self, ident, callable, _ctx=None):
            return _M_kvm4remote.KVM._op_SetRemoteCallable.invoke(self, ((ident, callable), _ctx))

        def begin_SetRemoteCallable(self, ident, callable, _response=None, _ex=None, _sent=None, _ctx=None):
            return _M_kvm4remote.KVM._op_SetRemoteCallable.begin(self, ((ident, callable), _response, _ex, _sent, _ctx))

        def end_SetRemoteCallable(self, _r):
            return _M_kvm4remote.KVM._op_SetRemoteCallable.end(self, _r)

        def CleanRemoteCallable(self, ident, _ctx=None):
            return _M_kvm4remote.KVM._op_CleanRemoteCallable.invoke(self, ((ident, ), _ctx))

        def begin_CleanRemoteCallable(self, ident, _response=None, _ex=None, _sent=None, _ctx=None):
            return _M_kvm4remote.KVM._op_CleanRemoteCallable.begin(self, ((ident, ), _response, _ex, _sent, _ctx))

        def end_CleanRemoteCallable(self, _r):
            return _M_kvm4remote.KVM._op_CleanRemoteCallable.end(self, _r)

        def getKVMCallable(self, _ctx=None):
            return _M_kvm4remote.KVM._op_getKVMCallable.invoke(self, ((), _ctx))

        def begin_getKVMCallable(self, _response=None, _ex=None, _sent=None, _ctx=None):
            return _M_kvm4remote.KVM._op_getKVMCallable.begin(self, ((), _response, _ex, _sent, _ctx))

        def end_getKVMCallable(self, _r):
            return _M_kvm4remote.KVM._op_getKVMCallable.end(self, _r)

        def checkedCast(proxy, facetOrCtx=None, _ctx=None):
            return _M_kvm4remote.KVMPrx.ice_checkedCast(proxy, '::kvm4remote::KVM', facetOrCtx, _ctx)
        checkedCast = staticmethod(checkedCast)

        def uncheckedCast(proxy, facet=None):
            return _M_kvm4remote.KVMPrx.ice_uncheckedCast(proxy, facet)
        uncheckedCast = staticmethod(uncheckedCast)

        def ice_staticId():
            return '::kvm4remote::KVM'
        ice_staticId = staticmethod(ice_staticId)

    _M_kvm4remote._t_KVMPrx = IcePy.defineProxy('::kvm4remote::KVM', KVMPrx)

    _M_kvm4remote._t_KVM = IcePy.defineClass('::kvm4remote::KVM', KVM, -1, (), True, False, None, (), ())
    KVM._ice_type = _M_kvm4remote._t_KVM

    KVM._op_SetRemoteCallable = IcePy.Operation('SetRemoteCallable', Ice.OperationMode.Normal, Ice.OperationMode.Normal, False, None, (), (((), IcePy._t_string, False, 0), ((), _M_Utils._t_CallablePrx, False, 0)), (), None, (_M_Utils._t_SystemError,))
    KVM._op_CleanRemoteCallable = IcePy.Operation('CleanRemoteCallable', Ice.OperationMode.Normal, Ice.OperationMode.Normal, False, None, (), (((), IcePy._t_string, False, 0),), (), None, ())
    KVM._op_getKVMCallable = IcePy.Operation('getKVMCallable', Ice.OperationMode.Normal, Ice.OperationMode.Normal, False, None, (), (), (), ((), _M_Utils._t_CallablePrx, False, 0), (_M_Utils._t_SystemError,))

    _M_kvm4remote.KVM = KVM
    del KVM

    _M_kvm4remote.KVMPrx = KVMPrx
    del KVMPrx

# End of module kvm4remote
