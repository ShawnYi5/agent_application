#pragma once

#include "logic.h"
#include "ServicePrxPool.hpp"

typedef ServicePrxPool<BoxLogic::LogicPrx>      LogicPrxPool;
typedef LogicPrxPool::ServicePrxPoolPtr         LogicPrxPoolPtr;
typedef LogicPrxPool::ServicePrxPoolItemType    LogicPrxPoolItem;
typedef LogicPrxPool::ServicePrxPoolItemPtr     LogicPrxPoolItemPtr;