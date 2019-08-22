import unittest
import sys
import json

sys.path.append('..')  # 工程目录加入

from common_utils import xlogging
from application_helper import CallFunction, NewInstance, DelInstance, NoneCall

_logger = xlogging.getLogger(__name__)


def invoke(json_input, raw_input=b''):
    input_args = json.loads(json_input)
    action = input_args.pop('action', None)  # call_function new_instance del_instance
    if action == 'call_function':
        worker = CallFunction(input_args, raw_input)
    elif action == 'new_instance':
        worker = NewInstance(input_args, raw_input)
    elif action == 'del_instance':
        worker = DelInstance(input_args, raw_input)
    else:
        worker = NoneCall(input_args, raw_input)

    return worker.work()


class RemoteHelper(object):

    def __init__(self, module_path, module_name, additional_args=None, raw_input=b''):
        self._module_path = module_path
        self._module_name = module_name
        self._additional_args = additional_args
        self._raw_input = raw_input
        self._ins_id = None

    def __str__(self):
        return '<RemoteHelper {} {}>'.format(self._module_path, self._module_name)

    def __del__(self):
        if self._ins_id:
            args = {
                'action': 'del_instance',
                'module_or_instance': self._ins_id
            }
            invoke(json.dumps(args))
        self._ins_id = None

    def invoke(self, func_name, additional_args=None, raw_input=b''):
        args = {
            'action': 'call_function',
            'module_or_instance': self._get_inst_id(),
            'func_name': func_name
        }
        if additional_args:
            args.update(additional_args)
        return invoke(json.dumps(args), raw_input)

    def _get_inst_id(self):
        if not self._ins_id:
            args = {
                'action': 'new_instance',
                'module_or_instance': self._module_path,
                'func_name': self._module_name
            }
            if self._additional_args:
                args.update(self._additional_args)
            self._ins_id, _ = invoke(json.dumps(args), self._raw_input)
        return self._ins_id


class TestAction(unittest.TestCase):

    def test_invoke(self):
        remove_ins1 = RemoteHelper('demo', 'Foo')  # 实例化远端的一个类
        remove_ins1.invoke('hello', {'args1': 'xxxx'}, b'raw input')  # 调用实例方法
        remove_ins1.invoke('get_name', {'args1': 'xxxx'}, b'raw input')

        args = {
            'action': 'call_function',
            'module_or_instance': 'demo',
            'func_name': 'foo'
        }
        invoke(json.dumps(args), b'')


if __name__ == '__main__':
    unittest.main()
