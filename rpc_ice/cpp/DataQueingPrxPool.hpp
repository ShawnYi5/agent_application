#pragma once

#include "data_queuing.h"
#include "ServicePrxPool.hpp"

typedef ServicePrxPool<DataQueuingIce::DataGuestPrx>  DataGuestPrxPool;
typedef DataGuestPrxPool::ServicePrxPoolPtr         DataGuestPrxPoolPtr;
typedef DataGuestPrxPool::ServicePrxPoolItemType    DataGuestPrxPoolItem;
typedef DataGuestPrxPool::ServicePrxPoolItemPtr     DataGuestPrxPoolItemPtr;