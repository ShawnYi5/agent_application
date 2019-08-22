#pragma once

template<typename PrxType, typename PrxPool>
class ServicePrxPoolItem
{
public:
  ServicePrxPoolItem(const PrxType& prx, const PrxPool& pool)
    : _prx(prx), _pool(pool)
  {

  }
  ~ServicePrxPoolItem()
  {
    _pool->deallocate(_prx);
  }

  PrxType proxy() const
  {
    return _prx;
  }

private:
  PrxType _prx;
  PrxPool _pool;
};

enum ServicePrxPoolStringType
{
  ServicePrxPool_RawString = 1,
  ServicePrxPool_Property  = 2
};

template<typename PrxType>
class ServicePrxPool : public IceUtil::Monitor<IceUtil::Mutex>, public std::enable_shared_from_this<ServicePrxPool<PrxType>>
{
public:
  typedef shared_ptr<ServicePrxPool<PrxType>> ServicePrxPoolPtr;
  typedef ServicePrxPoolItem<PrxType, ServicePrxPoolPtr> ServicePrxPoolItemType;
  typedef shared_ptr<ServicePrxPoolItemType> ServicePrxPoolItemPtr;

  ServicePrxPool(const Ice::CommunicatorPtr& communicator, const string& prxString, ServicePrxPoolStringType type = ServicePrxPool_Property)
    : _communicator(communicator), _prxString(prxString), _type(type)
  {
  }

  ~ServicePrxPool()
  {
  }

  ServicePrxPoolItemPtr allocate()
  {
    Lock sync(*this);

    PrxType prx;

    if (_pool.empty())
    {

		//LOG(INFO) << __FUNCTION__ << " _type=0x" << hex << _type;
		//LOG(INFO) << __FUNCTION__ << " _prxString=" << _prxString.c_str();

		switch (_type)
		{
		case ServicePrxPool_RawString:
			prx = PrxType::checkedCast(_communicator->stringToProxy(_prxString));
			break;
		case ServicePrxPool_Property:
			prx = PrxType::checkedCast(_communicator->propertyToProxy(_prxString));
			break;
		}

		//LOG(INFO) << __FUNCTION__ << " prx=0x" << hex << prx;
    }
    else
    {
      prx = *(_pool.begin());
      _pool.pop_front();
    }

    return make_shared<ServicePrxPoolItemType>(prx, this->shared_from_this());
  }

  void deallocate(const PrxType& prx)
  {
    Lock sync(*this);

    _pool.push_back(prx);
  }

private:
  typedef IceUtil::LockT<IceUtil::Monitor<IceUtil::Mutex>> Lock;

  const Ice::CommunicatorPtr _communicator;
  const string _prxString;
  const ServicePrxPoolStringType _type;

  list<PrxType> _pool;
};