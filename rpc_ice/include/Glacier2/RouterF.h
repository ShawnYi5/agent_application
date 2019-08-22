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
// Generated from file `RouterF.ice'
//
// Warning: do not edit this file.
//
// </auto-generated>
//

#ifndef __Glacier2_RouterF_h__
#define __Glacier2_RouterF_h__

#include <IceUtil/PushDisableWarnings.h>
#include <Ice/ProxyF.h>
#include <Ice/ObjectF.h>
#include <Ice/Exception.h>
#include <Ice/LocalObject.h>
#include <Ice/StreamHelpers.h>
#include <Ice/Proxy.h>
#include <IceUtil/ScopedArray.h>
#include <IceUtil/Optional.h>
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

#ifndef GLACIER2_API
#   ifdef GLACIER2_API_EXPORTS
#       define GLACIER2_API ICE_DECLSPEC_EXPORT
#   elif defined(ICE_STATIC_LIBS)
#       define GLACIER2_API /**/
#   else
#       define GLACIER2_API ICE_DECLSPEC_IMPORT
#   endif
#endif

namespace IceProxy
{

namespace Glacier2
{

class Router;
GLACIER2_API void __read(::IceInternal::BasicStream*, ::IceInternal::ProxyHandle< ::IceProxy::Glacier2::Router>&);
GLACIER2_API ::IceProxy::Ice::Object* upCast(::IceProxy::Glacier2::Router*);

}

}

namespace Glacier2
{

class Router;
bool operator==(const Router&, const Router&);
bool operator<(const Router&, const Router&);
GLACIER2_API ::Ice::Object* upCast(::Glacier2::Router*);
typedef ::IceInternal::Handle< ::Glacier2::Router> RouterPtr;
typedef ::IceInternal::ProxyHandle< ::IceProxy::Glacier2::Router> RouterPrx;
GLACIER2_API void __patch(RouterPtr&, const ::Ice::ObjectPtr&);

}

#include <IceUtil/PopDisableWarnings.h>
#endif