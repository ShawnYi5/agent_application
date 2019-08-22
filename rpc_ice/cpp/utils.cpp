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
// Generated from file `utils.ice'
//
// Warning: do not edit this file.
//
// </auto-generated>
//

#include <utils.h>
#include <IceUtil/PushDisableWarnings.h>
#include <Ice/LocalException.h>
#include <Ice/ObjectFactory.h>
#include <Ice/Outgoing.h>
#include <Ice/OutgoingAsync.h>
#include <Ice/BasicStream.h>
#include <IceUtil/Iterator.h>
#include <IceUtil/PopDisableWarnings.h>

#ifndef ICE_IGNORE_VERSION
#   if ICE_INT_VERSION / 100 != 306
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

const ::std::string __Utils__Callable__execute_name = "execute";

}

namespace
{

const ::IceInternal::DefaultUserExceptionFactoryInit< ::Utils::ErrorBase> __Utils__ErrorBase_init("::Utils::ErrorBase");

}

Utils::ErrorBase::ErrorBase(const ::std::string& __ice_description, const ::std::string& __ice_debug) :
    ::Ice::UserException(),
    description(__ice_description),
    debug(__ice_debug)
{
}

Utils::ErrorBase::~ErrorBase() throw()
{
}

::std::string
Utils::ErrorBase::ice_name() const
{
    return "Utils::ErrorBase";
}

Utils::ErrorBase*
Utils::ErrorBase::ice_clone() const
{
    return new ErrorBase(*this);
}

void
Utils::ErrorBase::ice_throw() const
{
    throw *this;
}

void
Utils::ErrorBase::__writeImpl(::IceInternal::BasicStream* __os) const
{
    __os->startWriteSlice("::Utils::ErrorBase", -1, true);
    __os->write(description);
    __os->write(debug);
    __os->endWriteSlice();
}

void
Utils::ErrorBase::__readImpl(::IceInternal::BasicStream* __is)
{
    __is->startReadSlice();
    __is->read(description);
    __is->read(debug);
    __is->endReadSlice();
}

namespace
{

const ::IceInternal::DefaultUserExceptionFactoryInit< ::Utils::SystemError> __Utils__SystemError_init("::Utils::SystemError");

}

Utils::SystemError::SystemError(const ::std::string& __ice_description, const ::std::string& __ice_debug, ::Ice::Long __ice_rawCode) :
    ::Utils::ErrorBase(__ice_description, __ice_debug),
    rawCode(__ice_rawCode)
{
}

Utils::SystemError::~SystemError() throw()
{
}

::std::string
Utils::SystemError::ice_name() const
{
    return "Utils::SystemError";
}

Utils::SystemError*
Utils::SystemError::ice_clone() const
{
    return new SystemError(*this);
}

void
Utils::SystemError::ice_throw() const
{
    throw *this;
}

void
Utils::SystemError::__writeImpl(::IceInternal::BasicStream* __os) const
{
    __os->startWriteSlice("::Utils::SystemError", -1, false);
    __os->write(rawCode);
    __os->endWriteSlice();
    ::Utils::ErrorBase::__writeImpl(__os);
}

void
Utils::SystemError::__readImpl(::IceInternal::BasicStream* __is)
{
    __is->startReadSlice();
    __is->read(rawCode);
    __is->endReadSlice();
    ::Utils::ErrorBase::__readImpl(__is);
}

namespace
{

const ::IceInternal::DefaultUserExceptionFactoryInit< ::Utils::NeedRetryLaterError> __Utils__NeedRetryLaterError_init("::Utils::NeedRetryLaterError");

}

Utils::NeedRetryLaterError::NeedRetryLaterError(const ::std::string& __ice_description, const ::std::string& __ice_debug) :
    ::Utils::ErrorBase(__ice_description, __ice_debug)
{
}

Utils::NeedRetryLaterError::~NeedRetryLaterError() throw()
{
}

::std::string
Utils::NeedRetryLaterError::ice_name() const
{
    return "Utils::NeedRetryLaterError";
}

Utils::NeedRetryLaterError*
Utils::NeedRetryLaterError::ice_clone() const
{
    return new NeedRetryLaterError(*this);
}

void
Utils::NeedRetryLaterError::ice_throw() const
{
    throw *this;
}

void
Utils::NeedRetryLaterError::__writeImpl(::IceInternal::BasicStream* __os) const
{
    __os->startWriteSlice("::Utils::NeedRetryLaterError", -1, false);
    __os->endWriteSlice();
    ::Utils::ErrorBase::__writeImpl(__os);
}

void
Utils::NeedRetryLaterError::__readImpl(::IceInternal::BasicStream* __is)
{
    __is->startReadSlice();
    __is->endReadSlice();
    ::Utils::ErrorBase::__readImpl(__is);
}

namespace
{

const ::IceInternal::DefaultUserExceptionFactoryInit< ::Utils::CreateSnapshotImageError> __Utils__CreateSnapshotImageError_init("::Utils::CreateSnapshotImageError");

}

Utils::CreateSnapshotImageError::CreateSnapshotImageError(const ::std::string& __ice_description, const ::std::string& __ice_debug, ::Ice::Long __ice_rawCode) :
    ::Utils::SystemError(__ice_description, __ice_debug, __ice_rawCode)
{
}

Utils::CreateSnapshotImageError::~CreateSnapshotImageError() throw()
{
}

::std::string
Utils::CreateSnapshotImageError::ice_name() const
{
    return "Utils::CreateSnapshotImageError";
}

Utils::CreateSnapshotImageError*
Utils::CreateSnapshotImageError::ice_clone() const
{
    return new CreateSnapshotImageError(*this);
}

void
Utils::CreateSnapshotImageError::ice_throw() const
{
    throw *this;
}

void
Utils::CreateSnapshotImageError::__writeImpl(::IceInternal::BasicStream* __os) const
{
    __os->startWriteSlice("::Utils::CreateSnapshotImageError", -1, false);
    __os->endWriteSlice();
    ::Utils::SystemError::__writeImpl(__os);
}

void
Utils::CreateSnapshotImageError::__readImpl(::IceInternal::BasicStream* __is)
{
    __is->startReadSlice();
    __is->endReadSlice();
    ::Utils::SystemError::__readImpl(__is);
}

namespace
{

const ::IceInternal::DefaultUserExceptionFactoryInit< ::Utils::OperationNotExistError> __Utils__OperationNotExistError_init("::Utils::OperationNotExistError");

}

Utils::OperationNotExistError::OperationNotExistError(const ::std::string& __ice_description, const ::std::string& __ice_debug) :
    ::Utils::ErrorBase(__ice_description, __ice_debug)
{
}

Utils::OperationNotExistError::~OperationNotExistError() throw()
{
}

::std::string
Utils::OperationNotExistError::ice_name() const
{
    return "Utils::OperationNotExistError";
}

Utils::OperationNotExistError*
Utils::OperationNotExistError::ice_clone() const
{
    return new OperationNotExistError(*this);
}

void
Utils::OperationNotExistError::ice_throw() const
{
    throw *this;
}

void
Utils::OperationNotExistError::__writeImpl(::IceInternal::BasicStream* __os) const
{
    __os->startWriteSlice("::Utils::OperationNotExistError", -1, false);
    __os->endWriteSlice();
    ::Utils::ErrorBase::__writeImpl(__os);
}

void
Utils::OperationNotExistError::__readImpl(::IceInternal::BasicStream* __is)
{
    __is->startReadSlice();
    __is->endReadSlice();
    ::Utils::ErrorBase::__readImpl(__is);
}

namespace Ice
{
}
::IceProxy::Ice::Object* ::IceProxy::Utils::upCast(::IceProxy::Utils::Callable* p) { return p; }

void
::IceProxy::Utils::__read(::IceInternal::BasicStream* __is, ::IceInternal::ProxyHandle< ::IceProxy::Utils::Callable>& v)
{
    ::Ice::ObjectPrx proxy;
    __is->read(proxy);
    if(!proxy)
    {
        v = 0;
    }
    else
    {
        v = new ::IceProxy::Utils::Callable;
        v->__copyFrom(proxy);
    }
}

void
IceProxy::Utils::Callable::execute(const ::std::string& __p_callJson, const ::std::string& __p_inputJson, const ::Utils::BinaryStream& __p_inputBs, ::std::string& __p_outputJson, ::Utils::BinaryStream& __p_outputBs, const ::Ice::Context* __ctx)
{
    __checkTwowayOnly(__Utils__Callable__execute_name);
    ::IceInternal::Outgoing __og(this, __Utils__Callable__execute_name, ::Ice::Normal, __ctx);
    try
    {
        ::IceInternal::BasicStream* __os = __og.startWriteParams(::Ice::DefaultFormat);
        __os->write(__p_callJson);
        __os->write(__p_inputJson);
        __os->write(__p_inputBs);
        __og.endWriteParams();
    }
    catch(const ::Ice::LocalException& __ex)
    {
        __og.abort(__ex);
    }
    if(!__og.invoke())
    {
        try
        {
            __og.throwUserException();
        }
        catch(const ::Utils::SystemError&)
        {
            throw;
        }
        catch(const ::Ice::UserException& __ex)
        {
            ::Ice::UnknownUserException __uue(__FILE__, __LINE__, __ex.ice_name());
            throw __uue;
        }
    }
    ::IceInternal::BasicStream* __is = __og.startReadParams();
    __is->read(__p_outputJson);
    __is->read(__p_outputBs);
    __og.endReadParams();
}

::Ice::AsyncResultPtr
IceProxy::Utils::Callable::begin_execute(const ::std::string& __p_callJson, const ::std::string& __p_inputJson, const ::Utils::BinaryStream& __p_inputBs, const ::Ice::Context* __ctx, const ::IceInternal::CallbackBasePtr& __del, const ::Ice::LocalObjectPtr& __cookie)
{
    __checkAsyncTwowayOnly(__Utils__Callable__execute_name);
    ::IceInternal::OutgoingAsyncPtr __result = new ::IceInternal::OutgoingAsync(this, __Utils__Callable__execute_name, __del, __cookie);
    try
    {
        __result->prepare(__Utils__Callable__execute_name, ::Ice::Normal, __ctx);
        ::IceInternal::BasicStream* __os = __result->startWriteParams(::Ice::DefaultFormat);
        __os->write(__p_callJson);
        __os->write(__p_inputJson);
        __os->write(__p_inputBs);
        __result->endWriteParams();
        __result->invoke();
    }
    catch(const ::Ice::Exception& __ex)
    {
        __result->abort(__ex);
    }
    return __result;
}

#ifdef ICE_CPP11

::Ice::AsyncResultPtr
IceProxy::Utils::Callable::__begin_execute(const ::std::string& __p_callJson, const ::std::string& __p_inputJson, const ::Utils::BinaryStream& __p_inputBs, const ::Ice::Context* __ctx, const ::IceInternal::Function<void (const ::std::string&, const ::Utils::BinaryStream&)>& __response, const ::IceInternal::Function<void (const ::Ice::Exception&)>& __exception, const ::IceInternal::Function<void (bool)>& __sent)
{
    class Cpp11CB : public ::IceInternal::Cpp11FnCallbackNC
    {
    public:

        Cpp11CB(const ::std::function<void (const ::std::string&, const ::Utils::BinaryStream&)>& responseFunc, const ::std::function<void (const ::Ice::Exception&)>& exceptionFunc, const ::std::function<void (bool)>& sentFunc) :
            ::IceInternal::Cpp11FnCallbackNC(exceptionFunc, sentFunc),
            _response(responseFunc)
        {
            CallbackBase::checkCallback(true, responseFunc || exceptionFunc != nullptr);
        }

        virtual void completed(const ::Ice::AsyncResultPtr& __result) const
        {
            ::Utils::CallablePrx __proxy = ::Utils::CallablePrx::uncheckedCast(__result->getProxy());
            ::std::string __p_outputJson;
            ::Utils::BinaryStream __p_outputBs;
            try
            {
                __proxy->end_execute(__p_outputJson, __p_outputBs, __result);
            }
            catch(const ::Ice::Exception& ex)
            {
                Cpp11FnCallbackNC::exception(__result, ex);
                return;
            }
            if(_response != nullptr)
            {
                _response(__p_outputJson, __p_outputBs);
            }
        }
    
    private:
        
        ::std::function<void (const ::std::string&, const ::Utils::BinaryStream&)> _response;
    };
    return begin_execute(__p_callJson, __p_inputJson, __p_inputBs, __ctx, new Cpp11CB(__response, __exception, __sent));
}
#endif

void
IceProxy::Utils::Callable::end_execute(::std::string& __p_outputJson, ::Utils::BinaryStream& __p_outputBs, const ::Ice::AsyncResultPtr& __result)
{
    ::Ice::AsyncResult::__check(__result, this, __Utils__Callable__execute_name);
    if(!__result->__wait())
    {
        try
        {
            __result->__throwUserException();
        }
        catch(const ::Utils::SystemError&)
        {
            throw;
        }
        catch(const ::Ice::UserException& __ex)
        {
            throw ::Ice::UnknownUserException(__FILE__, __LINE__, __ex.ice_name());
        }
    }
    ::IceInternal::BasicStream* __is = __result->__startReadParams();
    __is->read(__p_outputJson);
    __is->read(__p_outputBs);
    __result->__endReadParams();
}

const ::std::string&
IceProxy::Utils::Callable::ice_staticId()
{
    return ::Utils::Callable::ice_staticId();
}

::IceProxy::Ice::Object*
IceProxy::Utils::Callable::__newInstance() const
{
    return new Callable;
}

::Ice::Object* Utils::upCast(::Utils::Callable* p) { return p; }

namespace
{
const ::std::string __Utils__Callable_ids[2] =
{
    "::Ice::Object",
    "::Utils::Callable"
};

}

bool
Utils::Callable::ice_isA(const ::std::string& _s, const ::Ice::Current&) const
{
    return ::std::binary_search(__Utils__Callable_ids, __Utils__Callable_ids + 2, _s);
}

::std::vector< ::std::string>
Utils::Callable::ice_ids(const ::Ice::Current&) const
{
    return ::std::vector< ::std::string>(&__Utils__Callable_ids[0], &__Utils__Callable_ids[2]);
}

const ::std::string&
Utils::Callable::ice_id(const ::Ice::Current&) const
{
    return __Utils__Callable_ids[1];
}

const ::std::string&
Utils::Callable::ice_staticId()
{
#ifdef ICE_HAS_THREAD_SAFE_LOCAL_STATIC
    static const ::std::string typeId = "::Utils::Callable";
    return typeId;
#else
    return __Utils__Callable_ids[1];
#endif
}

::Ice::DispatchStatus
Utils::Callable::___execute(::IceInternal::Incoming& __inS, const ::Ice::Current& __current)
{
    __checkMode(::Ice::Normal, __current.mode);
    ::IceInternal::BasicStream* __is = __inS.startReadParams();
    ::std::string __p_callJson;
    ::std::string __p_inputJson;
    ::Utils::BinaryStream __p_inputBs;
    __is->read(__p_callJson);
    __is->read(__p_inputJson);
    __is->read(__p_inputBs);
    __inS.endReadParams();
    ::std::string __p_outputJson;
    ::Utils::BinaryStream __p_outputBs;
    try
    {
        execute(__p_callJson, __p_inputJson, __p_inputBs, __p_outputJson, __p_outputBs, __current);
        ::IceInternal::BasicStream* __os = __inS.__startWriteParams(::Ice::DefaultFormat);
        __os->write(__p_outputJson);
        __os->write(__p_outputBs);
        __inS.__endWriteParams(true);
        return ::Ice::DispatchOK;
    }
    catch(const ::Utils::SystemError& __ex)
    {
        __inS.__writeUserException(__ex, ::Ice::DefaultFormat);
    }
    return ::Ice::DispatchUserException;
}

namespace
{
const ::std::string __Utils__Callable_all[] =
{
    "execute",
    "ice_id",
    "ice_ids",
    "ice_isA",
    "ice_ping"
};

}

::Ice::DispatchStatus
Utils::Callable::__dispatch(::IceInternal::Incoming& in, const ::Ice::Current& current)
{
    ::std::pair< const ::std::string*, const ::std::string*> r = ::std::equal_range(__Utils__Callable_all, __Utils__Callable_all + 5, current.operation);
    if(r.first == r.second)
    {
        throw ::Ice::OperationNotExistException(__FILE__, __LINE__, current.id, current.facet, current.operation);
    }

    switch(r.first - __Utils__Callable_all)
    {
        case 0:
        {
            return ___execute(in, current);
        }
        case 1:
        {
            return ___ice_id(in, current);
        }
        case 2:
        {
            return ___ice_ids(in, current);
        }
        case 3:
        {
            return ___ice_isA(in, current);
        }
        case 4:
        {
            return ___ice_ping(in, current);
        }
    }

    assert(false);
    throw ::Ice::OperationNotExistException(__FILE__, __LINE__, current.id, current.facet, current.operation);
}

void
Utils::Callable::__writeImpl(::IceInternal::BasicStream* __os) const
{
    __os->startWriteSlice(ice_staticId(), -1, true);
    __os->endWriteSlice();
}

void
Utils::Callable::__readImpl(::IceInternal::BasicStream* __is)
{
    __is->startReadSlice();
    __is->endReadSlice();
}

void 
Utils::__patch(CallablePtr& handle, const ::Ice::ObjectPtr& v)
{
    handle = ::Utils::CallablePtr::dynamicCast(v);
    if(v && !handle)
    {
        IceInternal::Ex::throwUOE(::Utils::Callable::ice_staticId(), v);
    }
}