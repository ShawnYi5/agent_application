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
// Generated from file `Connection.ice'
//
// Warning: do not edit this file.
//
// </auto-generated>
//

#ifndef __Ice_Connection_h__
#define __Ice_Connection_h__

#include <IceUtil/PushDisableWarnings.h>
#include <Ice/ProxyF.h>
#include <Ice/ObjectF.h>
#include <Ice/Exception.h>
#include <Ice/LocalObject.h>
#include <Ice/StreamHelpers.h>
#include <Ice/Proxy.h>
#include <Ice/AsyncResult.h>
#include <IceUtil/ScopedArray.h>
#include <IceUtil/Optional.h>
#include <Ice/ObjectAdapterF.h>
#include <Ice/Identity.h>
#include <Ice/Endpoint.h>
#include <IceUtil/UndefSysMacros.h>

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

#ifndef ICE_API
#   ifdef ICE_API_EXPORTS
#       define ICE_API ICE_DECLSPEC_EXPORT
#   elif defined(ICE_STATIC_LIBS)
#       define ICE_API /**/
#   else
#       define ICE_API ICE_DECLSPEC_IMPORT
#   endif
#endif

namespace Ice
{

class ConnectionInfo;
bool operator==(const ConnectionInfo&, const ConnectionInfo&);
bool operator<(const ConnectionInfo&, const ConnectionInfo&);
ICE_API ::Ice::LocalObject* upCast(::Ice::ConnectionInfo*);
typedef ::IceInternal::Handle< ::Ice::ConnectionInfo> ConnectionInfoPtr;

class Connection;
bool operator==(const Connection&, const Connection&);
bool operator<(const Connection&, const Connection&);
ICE_API ::Ice::LocalObject* upCast(::Ice::Connection*);
typedef ::IceInternal::Handle< ::Ice::Connection> ConnectionPtr;

class ConnectionCallback;
bool operator==(const ConnectionCallback&, const ConnectionCallback&);
bool operator<(const ConnectionCallback&, const ConnectionCallback&);
ICE_API ::Ice::LocalObject* upCast(::Ice::ConnectionCallback*);
typedef ::IceInternal::Handle< ::Ice::ConnectionCallback> ConnectionCallbackPtr;

class IPConnectionInfo;
bool operator==(const IPConnectionInfo&, const IPConnectionInfo&);
bool operator<(const IPConnectionInfo&, const IPConnectionInfo&);
ICE_API ::Ice::LocalObject* upCast(::Ice::IPConnectionInfo*);
typedef ::IceInternal::Handle< ::Ice::IPConnectionInfo> IPConnectionInfoPtr;

class TCPConnectionInfo;
bool operator==(const TCPConnectionInfo&, const TCPConnectionInfo&);
bool operator<(const TCPConnectionInfo&, const TCPConnectionInfo&);
ICE_API ::Ice::LocalObject* upCast(::Ice::TCPConnectionInfo*);
typedef ::IceInternal::Handle< ::Ice::TCPConnectionInfo> TCPConnectionInfoPtr;

class UDPConnectionInfo;
bool operator==(const UDPConnectionInfo&, const UDPConnectionInfo&);
bool operator<(const UDPConnectionInfo&, const UDPConnectionInfo&);
ICE_API ::Ice::LocalObject* upCast(::Ice::UDPConnectionInfo*);
typedef ::IceInternal::Handle< ::Ice::UDPConnectionInfo> UDPConnectionInfoPtr;

class WSConnectionInfo;
bool operator==(const WSConnectionInfo&, const WSConnectionInfo&);
bool operator<(const WSConnectionInfo&, const WSConnectionInfo&);
ICE_API ::Ice::LocalObject* upCast(::Ice::WSConnectionInfo*);
typedef ::IceInternal::Handle< ::Ice::WSConnectionInfo> WSConnectionInfoPtr;

}

namespace Ice
{

enum ACMClose
{
    CloseOff,
    CloseOnIdle,
    CloseOnInvocation,
    CloseOnInvocationAndIdle,
    CloseOnIdleForceful
};

enum ACMHeartbeat
{
    HeartbeatOff,
    HeartbeatOnInvocation,
    HeartbeatOnIdle,
    HeartbeatAlways
};

struct ACM
{
    ::Ice::Int timeout;
    ::Ice::ACMClose close;
    ::Ice::ACMHeartbeat heartbeat;

    bool operator==(const ACM& __rhs) const
    {
        if(this == &__rhs)
        {
            return true;
        }
        if(timeout != __rhs.timeout)
        {
            return false;
        }
        if(close != __rhs.close)
        {
            return false;
        }
        if(heartbeat != __rhs.heartbeat)
        {
            return false;
        }
        return true;
    }

    bool operator<(const ACM& __rhs) const
    {
        if(this == &__rhs)
        {
            return false;
        }
        if(timeout < __rhs.timeout)
        {
            return true;
        }
        else if(__rhs.timeout < timeout)
        {
            return false;
        }
        if(close < __rhs.close)
        {
            return true;
        }
        else if(__rhs.close < close)
        {
            return false;
        }
        if(heartbeat < __rhs.heartbeat)
        {
            return true;
        }
        else if(__rhs.heartbeat < heartbeat)
        {
            return false;
        }
        return false;
    }

    bool operator!=(const ACM& __rhs) const
    {
        return !operator==(__rhs);
    }
    bool operator<=(const ACM& __rhs) const
    {
        return operator<(__rhs) || operator==(__rhs);
    }
    bool operator>(const ACM& __rhs) const
    {
        return !operator<(__rhs) && !operator==(__rhs);
    }
    bool operator>=(const ACM& __rhs) const
    {
        return !operator<(__rhs);
    }
};

typedef ::std::map< ::std::string, ::std::string> HeaderDict;

}

namespace Ice
{
}

namespace Ice
{

class Callback_Connection_flushBatchRequests_Base : virtual public ::IceInternal::CallbackBase { };
typedef ::IceUtil::Handle< Callback_Connection_flushBatchRequests_Base> Callback_Connection_flushBatchRequestsPtr;

}

namespace Ice
{

class ICE_API ConnectionInfo : virtual public ::Ice::LocalObject
{
public:

    typedef ConnectionInfoPtr PointerType;

    ConnectionInfo()
    {
    }

    ConnectionInfo(bool __ice_incoming, const ::std::string& __ice_adapterName, const ::std::string& __ice_connectionId, ::Ice::Int __ice_rcvSize, ::Ice::Int __ice_sndSize) :
        incoming(__ice_incoming),
        adapterName(__ice_adapterName),
        connectionId(__ice_connectionId),
        rcvSize(__ice_rcvSize),
        sndSize(__ice_sndSize)
    {
    }


public:

    bool incoming;

    ::std::string adapterName;

    ::std::string connectionId;

    ::Ice::Int rcvSize;

    ::Ice::Int sndSize;
protected:

    virtual ~ConnectionInfo() {}

friend class ConnectionInfo__staticInit;
};

inline bool operator==(const ConnectionInfo& l, const ConnectionInfo& r)
{
    return static_cast<const ::Ice::LocalObject&>(l) == static_cast<const ::Ice::LocalObject&>(r);
}

inline bool operator<(const ConnectionInfo& l, const ConnectionInfo& r)
{
    return static_cast<const ::Ice::LocalObject&>(l) < static_cast<const ::Ice::LocalObject&>(r);
}

class ICE_API ConnectionCallback : virtual public ::Ice::LocalObject
{
public:

    typedef ConnectionCallbackPtr PointerType;

    virtual void heartbeat(const ::Ice::ConnectionPtr&) = 0;

    virtual void closed(const ::Ice::ConnectionPtr&) = 0;
};

inline bool operator==(const ConnectionCallback& l, const ConnectionCallback& r)
{
    return static_cast<const ::Ice::LocalObject&>(l) == static_cast<const ::Ice::LocalObject&>(r);
}

inline bool operator<(const ConnectionCallback& l, const ConnectionCallback& r)
{
    return static_cast<const ::Ice::LocalObject&>(l) < static_cast<const ::Ice::LocalObject&>(r);
}

class ICE_API Connection : virtual public ::Ice::LocalObject
{
public:

    typedef ConnectionPtr PointerType;

    virtual void close(bool) = 0;

    virtual ::Ice::ObjectPrx createProxy(const ::Ice::Identity&) const = 0;

    virtual void setAdapter(const ::Ice::ObjectAdapterPtr&) = 0;

    virtual ::Ice::ObjectAdapterPtr getAdapter() const = 0;

    virtual ::Ice::EndpointPtr getEndpoint() const = 0;

    virtual void flushBatchRequests() = 0;
    // Only supported with C++ 11 support enabled
    virtual ::Ice::AsyncResultPtr begin_flushBatchRequests(const ::IceInternal::Function<void (const ::Ice::Exception&)>& exception, const ::IceInternal::Function<void (bool)>& sent = ::IceInternal::Function<void (bool)>()) = 0;

    virtual ::Ice::AsyncResultPtr begin_flushBatchRequests() = 0;

    virtual ::Ice::AsyncResultPtr begin_flushBatchRequests(const ::Ice::CallbackPtr& __del, const ::Ice::LocalObjectPtr& __cookie = 0) = 0;

    virtual ::Ice::AsyncResultPtr begin_flushBatchRequests(const ::Ice::Callback_Connection_flushBatchRequestsPtr& __del, const ::Ice::LocalObjectPtr& __cookie = 0) = 0;

    virtual void end_flushBatchRequests(const ::Ice::AsyncResultPtr&) = 0;

    virtual void setCallback(const ::Ice::ConnectionCallbackPtr&) = 0;

    virtual void setACM(const IceUtil::Optional< ::Ice::Int>&, const IceUtil::Optional< ::Ice::ACMClose>&, const IceUtil::Optional< ::Ice::ACMHeartbeat>&) = 0;

    virtual ::Ice::ACM getACM() = 0;

    virtual ::std::string type() const = 0;

    virtual ::Ice::Int timeout() const = 0;

    virtual ::std::string toString() const = 0;

    virtual ::Ice::ConnectionInfoPtr getInfo() const = 0;

    virtual void setBufferSize(::Ice::Int, ::Ice::Int) = 0;
};

inline bool operator==(const Connection& l, const Connection& r)
{
    return static_cast<const ::Ice::LocalObject&>(l) == static_cast<const ::Ice::LocalObject&>(r);
}

inline bool operator<(const Connection& l, const Connection& r)
{
    return static_cast<const ::Ice::LocalObject&>(l) < static_cast<const ::Ice::LocalObject&>(r);
}

class ICE_API IPConnectionInfo : public ::Ice::ConnectionInfo
{
public:

    typedef IPConnectionInfoPtr PointerType;

    IPConnectionInfo() :
        localAddress(""),
        localPort(-1),
        remoteAddress(""),
        remotePort(-1)
    {
    }

    IPConnectionInfo(bool __ice_incoming, const ::std::string& __ice_adapterName, const ::std::string& __ice_connectionId, ::Ice::Int __ice_rcvSize, ::Ice::Int __ice_sndSize, const ::std::string& __ice_localAddress, ::Ice::Int __ice_localPort, const ::std::string& __ice_remoteAddress, ::Ice::Int __ice_remotePort) :
        ::Ice::ConnectionInfo(__ice_incoming, __ice_adapterName, __ice_connectionId, __ice_rcvSize, __ice_sndSize),
        localAddress(__ice_localAddress),
        localPort(__ice_localPort),
        remoteAddress(__ice_remoteAddress),
        remotePort(__ice_remotePort)
    {
    }


public:

    ::std::string localAddress;

    ::Ice::Int localPort;

    ::std::string remoteAddress;

    ::Ice::Int remotePort;
protected:

    virtual ~IPConnectionInfo() {}

friend class IPConnectionInfo__staticInit;
};

inline bool operator==(const IPConnectionInfo& l, const IPConnectionInfo& r)
{
    return static_cast<const ::Ice::LocalObject&>(l) == static_cast<const ::Ice::LocalObject&>(r);
}

inline bool operator<(const IPConnectionInfo& l, const IPConnectionInfo& r)
{
    return static_cast<const ::Ice::LocalObject&>(l) < static_cast<const ::Ice::LocalObject&>(r);
}

class ICE_API TCPConnectionInfo : public ::Ice::IPConnectionInfo
{
public:

    typedef TCPConnectionInfoPtr PointerType;

    TCPConnectionInfo()
    {
    }

    TCPConnectionInfo(bool __ice_incoming, const ::std::string& __ice_adapterName, const ::std::string& __ice_connectionId, ::Ice::Int __ice_rcvSize, ::Ice::Int __ice_sndSize, const ::std::string& __ice_localAddress, ::Ice::Int __ice_localPort, const ::std::string& __ice_remoteAddress, ::Ice::Int __ice_remotePort) :
        ::Ice::IPConnectionInfo(__ice_incoming, __ice_adapterName, __ice_connectionId, __ice_rcvSize, __ice_sndSize, __ice_localAddress, __ice_localPort, __ice_remoteAddress, __ice_remotePort)
    {
    }


    virtual ~TCPConnectionInfo() {}

friend class TCPConnectionInfo__staticInit;
};

inline bool operator==(const TCPConnectionInfo& l, const TCPConnectionInfo& r)
{
    return static_cast<const ::Ice::LocalObject&>(l) == static_cast<const ::Ice::LocalObject&>(r);
}

inline bool operator<(const TCPConnectionInfo& l, const TCPConnectionInfo& r)
{
    return static_cast<const ::Ice::LocalObject&>(l) < static_cast<const ::Ice::LocalObject&>(r);
}

class ICE_API UDPConnectionInfo : public ::Ice::IPConnectionInfo
{
public:

    typedef UDPConnectionInfoPtr PointerType;

    UDPConnectionInfo() :
        mcastPort(-1)
    {
    }

    UDPConnectionInfo(bool __ice_incoming, const ::std::string& __ice_adapterName, const ::std::string& __ice_connectionId, ::Ice::Int __ice_rcvSize, ::Ice::Int __ice_sndSize, const ::std::string& __ice_localAddress, ::Ice::Int __ice_localPort, const ::std::string& __ice_remoteAddress, ::Ice::Int __ice_remotePort, const ::std::string& __ice_mcastAddress, ::Ice::Int __ice_mcastPort) :
        ::Ice::IPConnectionInfo(__ice_incoming, __ice_adapterName, __ice_connectionId, __ice_rcvSize, __ice_sndSize, __ice_localAddress, __ice_localPort, __ice_remoteAddress, __ice_remotePort),
        mcastAddress(__ice_mcastAddress),
        mcastPort(__ice_mcastPort)
    {
    }


public:

    ::std::string mcastAddress;

    ::Ice::Int mcastPort;
protected:

    virtual ~UDPConnectionInfo() {}

friend class UDPConnectionInfo__staticInit;
};

inline bool operator==(const UDPConnectionInfo& l, const UDPConnectionInfo& r)
{
    return static_cast<const ::Ice::LocalObject&>(l) == static_cast<const ::Ice::LocalObject&>(r);
}

inline bool operator<(const UDPConnectionInfo& l, const UDPConnectionInfo& r)
{
    return static_cast<const ::Ice::LocalObject&>(l) < static_cast<const ::Ice::LocalObject&>(r);
}

class ICE_API WSConnectionInfo : public ::Ice::TCPConnectionInfo
{
public:

    typedef WSConnectionInfoPtr PointerType;

    WSConnectionInfo()
    {
    }

    WSConnectionInfo(bool __ice_incoming, const ::std::string& __ice_adapterName, const ::std::string& __ice_connectionId, ::Ice::Int __ice_rcvSize, ::Ice::Int __ice_sndSize, const ::std::string& __ice_localAddress, ::Ice::Int __ice_localPort, const ::std::string& __ice_remoteAddress, ::Ice::Int __ice_remotePort, const ::Ice::HeaderDict& __ice_headers) :
        ::Ice::TCPConnectionInfo(__ice_incoming, __ice_adapterName, __ice_connectionId, __ice_rcvSize, __ice_sndSize, __ice_localAddress, __ice_localPort, __ice_remoteAddress, __ice_remotePort),
        headers(__ice_headers)
    {
    }


public:

    ::Ice::HeaderDict headers;
protected:

    virtual ~WSConnectionInfo() {}

friend class WSConnectionInfo__staticInit;
};

inline bool operator==(const WSConnectionInfo& l, const WSConnectionInfo& r)
{
    return static_cast<const ::Ice::LocalObject&>(l) == static_cast<const ::Ice::LocalObject&>(r);
}

inline bool operator<(const WSConnectionInfo& l, const WSConnectionInfo& r)
{
    return static_cast<const ::Ice::LocalObject&>(l) < static_cast<const ::Ice::LocalObject&>(r);
}

}

#include <IceUtil/PopDisableWarnings.h>
#endif
