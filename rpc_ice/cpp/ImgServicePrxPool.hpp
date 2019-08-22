#pragma once

#include "img.h"
#include "ServicePrxPool.hpp"

typedef ServicePrxPool<IMG::ImgServicePrx> ImgServicePrxPool;
typedef ImgServicePrxPool::ServicePrxPoolPtr ImgServicePrxPoolPtr;
typedef ImgServicePrxPool::ServicePrxPoolItemType ImgServicePrxPoolItem;
typedef ImgServicePrxPool::ServicePrxPoolItemPtr ImgServicePrxPoolItemPtr;