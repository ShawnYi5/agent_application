#pragma once

#include "duplicate_file.h"
#include "ServicePrxPool.hpp"

typedef ServicePrxPool<DuplicateFilePool::FilePoolPrx> 		FilePoolPrxPool;
typedef FilePoolPrxPool::ServicePrxPoolPtr 		FilePoolPrxPoolPtr;
typedef FilePoolPrxPool::ServicePrxPoolItemType FilePoolPrxPoolItem;
typedef FilePoolPrxPool::ServicePrxPoolItemPtr 	FilePoolPrxPoolItemPtr;