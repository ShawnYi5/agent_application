import json

from . import xlogging


class ModuleMapper(object):

    def __init__(self, module_path, module_name, proxy, logger, args_dict=None, raw_input=b''):
        self._module_path = module_path
        self._module_name = module_name
        self._args_dict = args_dict
        self._raw_input = raw_input
        self._ins_id = None
        self._proxy = proxy
        self.logger = logger
        xlogging.TraceDecorator().decorate()

    def __str__(self):
        return '<RemoteHelper {} {}>'.format(self._module_path, self._module_name)

    def __del__(self):
        if self._ins_id:
            args = {
                'action': 'del_instance',
                'module_or_instance': self._ins_id
            }
            self._proxy.execute(json.dumps(args), '{}', b'')
        self._ins_id = None

    def execute(self, func_name, args_dict=None, raw_input=b''):
        args = {
            'action': 'call_function',
            'module_or_instance': self._get_inst_id(),
            'func_name': func_name
        }
        args_dict = args_dict if args_dict else dict()
        return self._proxy.execute(json.dumps(args), json.dumps(args_dict), raw_input)

    def _get_inst_id(self):
        if not self._ins_id:
            args = {
                'action': 'new_instance',
                'module_or_instance': self._module_path,
                'func_name': self._module_name
            }
            args_dict = self._args_dict if self._args_dict else dict()
            self._ins_id, _ = self._proxy.execute(json.dumps(args), json.dumps(args_dict), self._raw_input)
        return self._ins_id


class FunctionMapper(object):

    def __init__(self, proxy, logger):
        self._proxy = proxy
        self.logger = logger

        xlogging.TraceDecorator().decorate()

    def execute(self, module_path, func_name, args_dict=None, raw_input=b''):
        args = {
            'action': 'call_function',
            'module_or_instance': module_path,
            'func_name': func_name
        }
        args_dict = args_dict if args_dict else dict()
        return self._proxy.execute(json.dumps(args), json.dumps(args_dict), raw_input)
