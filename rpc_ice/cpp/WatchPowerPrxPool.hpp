#pragma once

#include "WatchPowerServ.h"
#include "ServicePrxPool.hpp"

typedef ServicePrxPool<WatchPowerServ::PowerOffProcPrx> 	WatchPowerPrxPool;
typedef WatchPowerPrxPool::ServicePrxPoolPtr 		WatchPowerPrxPoolPtr;
typedef WatchPowerPrxPool::ServicePrxPoolItemType WatchPowerPrxPoolItem;
typedef WatchPowerPrxPool::ServicePrxPoolItemPtr 	WatchPowerPrxPoolItemPtr;

