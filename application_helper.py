import uuid
import threading
from importlib import import_module

from common_utils import xlogging

_logger = xlogging.getLogger(__name__)


class InstanceManager(object):
    _ins = None

    def __init__(self):
        self._ins_dict = dict()
        self._lock = threading.RLock()

    @classmethod
    def init(cls):
        if cls._ins is None:
            ins = cls()
            cls._ins = ins
        else:
            ins = cls._ins
        return ins

    def get(self, key):
        with self._lock:
            return self._ins_dict.get(key)

    def add(self, value):
        with self._lock:
            key = uuid.uuid4().hex
            self._ins_dict[key] = value
            _logger.info('InstanceManager bond {}={}'.format(key, value))
            return key

    def remove(self, key):
        with self._lock:
            value = self._ins_dict.pop(key, None)
            _logger.info('InstanceManager remove {} {}'.format(key, value))


class Action(object):

    def __init__(self, call_dict, input_dict, raw_input):
        self._call_dict = call_dict
        self._input_dict = input_dict
        self._raw_input = raw_input

        self._ins_mgr = InstanceManager.init()

    def work(self):
        return self._work()

    def _work(self):
        raise RuntimeError('you must imp this method')

    def _load_obj(self):
        module_or_instance = self._call_dict.pop('module_or_instance')
        func_name = self._call_dict.pop('func_name')
        module = self._ins_mgr.get(module_or_instance)
        if not module:
            module = import_module('scripts.{}'.format(module_or_instance))
        func = getattr(module, func_name)
        return func


class CallFunction(Action):
    def _work(self):
        return self._load_obj()(self._input_dict, self._raw_input)


class NewInstance(Action):

    def _work(self):
        ins = self._load_obj()(self._input_dict, self._raw_input)
        key = self._ins_mgr.add(ins)
        return key, b''


class DelInstance(Action):

    def _work(self):
        func_name = self._call_dict.pop('module_or_instance')
        return self._ins_mgr.remove(func_name)


class NoneCall(Action):

    def _work(self):
        xlogging.raise_system_error('无效的调用类型', 'invalid action', 1047)
