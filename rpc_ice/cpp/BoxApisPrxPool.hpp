#pragma once

#include "box_api.h"
#include "ServicePrxPool.hpp"

typedef ServicePrxPool<Box::ApisPrx> 		ApisPrxPool;
typedef ApisPrxPool::ServicePrxPoolPtr 		ApisPrxPoolPtr;
typedef ApisPrxPool::ServicePrxPoolItemType ApisPrxPoolItem;
typedef ApisPrxPool::ServicePrxPoolItemPtr 	ApisPrxPoolItemPtr;