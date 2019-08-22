// **********************************************************************
//
// Copyright (c) 2003-2013 ZeroC, Inc. All rights reserved.
//
// This copy of Ice is licensed to you under the terms described in the
// ICE_LICENSE file included in this distribution.
//
// **********************************************************************
//
// Ice version 3.5.1
//
// <auto-generated>
//
// Generated from file `install.ice'
//
// Warning: do not edit this file.
//
// </auto-generated>
//

#include <install.h>
#include <Ice/LocalException.h>
#include <Ice/ObjectFactory.h>
#include <Ice/BasicStream.h>
#include <Ice/Object.h>
#include <IceUtil/Iterator.h>

#ifndef ICE_IGNORE_VERSION
#   if ICE_INT_VERSION / 100 != 305
#       error Ice version mismatch!
#   endif
#   if ICE_INT_VERSION % 100 > 50
#       error Beta header file detected
#   endif
#   if ICE_INT_VERSION % 100 < 1
#       error Ice patch level mismatch!
#   endif
#endif

namespace
{

const ::std::string __InstallModule__InstallInterface__install_name = "install";

}
::IceProxy::Ice::Object* ::IceProxy::InstallModule::upCast(::IceProxy::InstallModule::InstallInterface* p) { return p; }

void
::IceProxy::InstallModule::__read(::IceInternal::BasicStream* __is, ::IceInternal::ProxyHandle< ::IceProxy::InstallModule::InstallInterface>& v)
{
    ::Ice::ObjectPrx proxy;
    __is->read(proxy);
    if(!proxy)
    {
        v = 0;
    }
    else
    {
        v = new ::IceProxy::InstallModule::InstallInterface;
        v->__copyFrom(proxy);
    }
}

bool
IceProxy::InstallModule::InstallInterface::install(const ::std::string& path, const ::Ice::Context* __ctx)
{
    ::IceInternal::InvocationObserver __observer(this, __InstallModule__InstallInterface__install_name, __ctx);
    int __cnt = 0;
    while(true)
    {
        ::IceInternal::Handle< ::IceDelegate::Ice::Object> __delBase;
        try
        {
            __checkTwowayOnly(__InstallModule__InstallInterface__install_name);
            __delBase = __getDelegate(false);
            ::IceDelegate::InstallModule::InstallInterface* __del = dynamic_cast< ::IceDelegate::InstallModule::InstallInterface*>(__delBase.get());
            return __del->install(path, __ctx, __observer);
        }
        catch(const ::IceInternal::LocalExceptionWrapper& __ex)
        {
            __handleExceptionWrapper(__delBase, __ex, __observer);
        }
        catch(const ::Ice::LocalException& __ex)
        {
            __handleException(__delBase, __ex, true, __cnt, __observer);
        }
    }
}

::Ice::AsyncResultPtr
IceProxy::InstallModule::InstallInterface::begin_install(const ::std::string& path, const ::Ice::Context* __ctx, const ::IceInternal::CallbackBasePtr& __del, const ::Ice::LocalObjectPtr& __cookie)
{
    __checkAsyncTwowayOnly(__InstallModule__InstallInterface__install_name);
    ::IceInternal::OutgoingAsyncPtr __result = new ::IceInternal::OutgoingAsync(this, __InstallModule__InstallInterface__install_name, __del, __cookie);
    try
    {
        __result->__prepare(__InstallModule__InstallInterface__install_name, ::Ice::Normal, __ctx);
        ::IceInternal::BasicStream* __os = __result->__startWriteParams(::Ice::DefaultFormat);
        __os->write(path);
        __result->__endWriteParams();
        __result->__send(true);
    }
    catch(const ::Ice::LocalException& __ex)
    {
        __result->__exceptionAsync(__ex);
    }
    return __result;
}

bool
IceProxy::InstallModule::InstallInterface::end_install(const ::Ice::AsyncResultPtr& __result)
{
    ::Ice::AsyncResult::__check(__result, this, __InstallModule__InstallInterface__install_name);
    bool __ret;
    bool __ok = __result->__wait();
    try
    {
        if(!__ok)
        {
            try
            {
                __result->__throwUserException();
            }
            catch(const ::Ice::UserException& __ex)
            {
                throw ::Ice::UnknownUserException(__FILE__, __LINE__, __ex.ice_name());
            }
        }
        ::IceInternal::BasicStream* __is = __result->__startReadParams();
        __is->read(__ret);
        __result->__endReadParams();
        return __ret;
    }
    catch(const ::Ice::LocalException& ex)
    {
        __result->__getObserver().failed(ex.ice_name());
        throw;
    }
}

const ::std::string&
IceProxy::InstallModule::InstallInterface::ice_staticId()
{
    return ::InstallModule::InstallInterface::ice_staticId();
}

::IceInternal::Handle< ::IceDelegateM::Ice::Object>
IceProxy::InstallModule::InstallInterface::__createDelegateM()
{
    return ::IceInternal::Handle< ::IceDelegateM::Ice::Object>(new ::IceDelegateM::InstallModule::InstallInterface);
}

::IceInternal::Handle< ::IceDelegateD::Ice::Object>
IceProxy::InstallModule::InstallInterface::__createDelegateD()
{
    return ::IceInternal::Handle< ::IceDelegateD::Ice::Object>(new ::IceDelegateD::InstallModule::InstallInterface);
}

::IceProxy::Ice::Object*
IceProxy::InstallModule::InstallInterface::__newInstance() const
{
    return new InstallInterface;
}

bool
IceDelegateM::InstallModule::InstallInterface::install(const ::std::string& path, const ::Ice::Context* __context, ::IceInternal::InvocationObserver& __observer)
{
    ::IceInternal::Outgoing __og(__handler.get(), __InstallModule__InstallInterface__install_name, ::Ice::Normal, __context, __observer);
    try
    {
        ::IceInternal::BasicStream* __os = __og.startWriteParams(::Ice::DefaultFormat);
        __os->write(path);
        __og.endWriteParams();
    }
    catch(const ::Ice::LocalException& __ex)
    {
        __og.abort(__ex);
    }
    bool __ok = __og.invoke();
    bool __ret;
    try
    {
        if(!__ok)
        {
            try
            {
                __og.throwUserException();
            }
            catch(const ::Ice::UserException& __ex)
            {
                ::Ice::UnknownUserException __uue(__FILE__, __LINE__, __ex.ice_name());
                throw __uue;
            }
        }
        ::IceInternal::BasicStream* __is = __og.startReadParams();
        __is->read(__ret);
        __og.endReadParams();
        return __ret;
    }
    catch(const ::Ice::LocalException& __ex)
    {
        throw ::IceInternal::LocalExceptionWrapper(__ex, false);
    }
}

bool
IceDelegateD::InstallModule::InstallInterface::install(const ::std::string& path, const ::Ice::Context* __context, ::IceInternal::InvocationObserver&)
{
    class _DirectI : public ::IceInternal::Direct
    {
    public:

        _DirectI(bool& __result, const ::std::string& __p_path, const ::Ice::Current& __current) : 
            ::IceInternal::Direct(__current),
            _result(__result),
            _m_path(__p_path)
        {
        }
        
        virtual ::Ice::DispatchStatus
        run(::Ice::Object* object)
        {
            ::InstallModule::InstallInterface* servant = dynamic_cast< ::InstallModule::InstallInterface*>(object);
            if(!servant)
            {
                throw ::Ice::OperationNotExistException(__FILE__, __LINE__, _current.id, _current.facet, _current.operation);
            }
            _result = servant->install(_m_path, _current);
            return ::Ice::DispatchOK;
        }
        
    private:
        
        bool& _result;
        const ::std::string& _m_path;
    };
    
    ::Ice::Current __current;
    __initCurrent(__current, __InstallModule__InstallInterface__install_name, ::Ice::Normal, __context);
    bool __result;
    try
    {
        _DirectI __direct(__result, path, __current);
        try
        {
            __direct.getServant()->__collocDispatch(__direct);
        }
        catch(...)
        {
            __direct.destroy();
            throw;
        }
        __direct.destroy();
    }
    catch(const ::Ice::SystemException&)
    {
        throw;
    }
    catch(const ::IceInternal::LocalExceptionWrapper&)
    {
        throw;
    }
    catch(const ::std::exception& __ex)
    {
        ::IceInternal::LocalExceptionWrapper::throwWrapper(__ex);
    }
    catch(...)
    {
        throw ::IceInternal::LocalExceptionWrapper(::Ice::UnknownException(__FILE__, __LINE__, "unknown c++ exception"), false);
    }
    return __result;
}

::Ice::Object* InstallModule::upCast(::InstallModule::InstallInterface* p) { return p; }

namespace
{
const ::std::string __InstallModule__InstallInterface_ids[2] =
{
    "::Ice::Object",
    "::InstallModule::InstallInterface"
};

}

bool
InstallModule::InstallInterface::ice_isA(const ::std::string& _s, const ::Ice::Current&) const
{
    return ::std::binary_search(__InstallModule__InstallInterface_ids, __InstallModule__InstallInterface_ids + 2, _s);
}

::std::vector< ::std::string>
InstallModule::InstallInterface::ice_ids(const ::Ice::Current&) const
{
    return ::std::vector< ::std::string>(&__InstallModule__InstallInterface_ids[0], &__InstallModule__InstallInterface_ids[2]);
}

const ::std::string&
InstallModule::InstallInterface::ice_id(const ::Ice::Current&) const
{
    return __InstallModule__InstallInterface_ids[1];
}

const ::std::string&
InstallModule::InstallInterface::ice_staticId()
{
    return __InstallModule__InstallInterface_ids[1];
}

::Ice::DispatchStatus
InstallModule::InstallInterface::___install(::IceInternal::Incoming& __inS, const ::Ice::Current& __current)
{
    __checkMode(::Ice::Normal, __current.mode);
    ::IceInternal::BasicStream* __is = __inS.startReadParams();
    ::std::string path;
    __is->read(path);
    __inS.endReadParams();
    bool __ret = install(path, __current);
    ::IceInternal::BasicStream* __os = __inS.__startWriteParams(::Ice::DefaultFormat);
    __os->write(__ret);
    __inS.__endWriteParams(true);
    return ::Ice::DispatchOK;
}

namespace
{
const ::std::string __InstallModule__InstallInterface_all[] =
{
    "ice_id",
    "ice_ids",
    "ice_isA",
    "ice_ping",
    "install"
};

}

::Ice::DispatchStatus
InstallModule::InstallInterface::__dispatch(::IceInternal::Incoming& in, const ::Ice::Current& current)
{
    ::std::pair< const ::std::string*, const ::std::string*> r = ::std::equal_range(__InstallModule__InstallInterface_all, __InstallModule__InstallInterface_all + 5, current.operation);
    if(r.first == r.second)
    {
        throw ::Ice::OperationNotExistException(__FILE__, __LINE__, current.id, current.facet, current.operation);
    }

    switch(r.first - __InstallModule__InstallInterface_all)
    {
        case 0:
        {
            return ___ice_id(in, current);
        }
        case 1:
        {
            return ___ice_ids(in, current);
        }
        case 2:
        {
            return ___ice_isA(in, current);
        }
        case 3:
        {
            return ___ice_ping(in, current);
        }
        case 4:
        {
            return ___install(in, current);
        }
    }

    assert(false);
    throw ::Ice::OperationNotExistException(__FILE__, __LINE__, current.id, current.facet, current.operation);
}

void
InstallModule::InstallInterface::__writeImpl(::IceInternal::BasicStream* __os) const
{
    __os->startWriteSlice(ice_staticId(), -1, true);
    __os->endWriteSlice();
}

void
InstallModule::InstallInterface::__readImpl(::IceInternal::BasicStream* __is)
{
    __is->startReadSlice();
    __is->endReadSlice();
}

void 
InstallModule::__patch(InstallInterfacePtr& handle, const ::Ice::ObjectPtr& v)
{
    handle = ::InstallModule::InstallInterfacePtr::dynamicCast(v);
    if(v && !handle)
    {
        IceInternal::Ex::throwUOE(::InstallModule::InstallInterface::ice_staticId(), v);
    }
}
