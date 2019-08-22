import json
import os
import signal
import sys

import Ice

from common_utils import xlogging
from application_helper import CallFunction, NewInstance, DelInstance, NoneCall
import Utils
import kvm4remote

app = None
_logger = xlogging.getLogger(__name__)


class CallableI(Utils.Callable):

    def __init__(self):
        xlogging.TraceDecorator().decorate()
        xlogging.ExceptionHandlerDecorator().decorate()

    @staticmethod
    def execute(callJson, argsJson, rawInput, current=None):
        call_dict = json.loads(callJson)
        args_dict = json.loads(argsJson)
        action = call_dict.pop('action', None)  # call_function new_instance del_instance
        if action == 'call_function':
            worker = CallFunction(call_dict, args_dict, rawInput)
        elif action == 'new_instance':
            worker = NewInstance(call_dict, args_dict, rawInput)
        elif action == 'del_instance':
            worker = DelInstance(call_dict, args_dict, rawInput)
        else:
            worker = NoneCall(call_dict, args_dict, rawInput)

        return worker.work()


class KVMI(kvm4remote.KVM):

    def __init__(self, call_prx):
        self._callable_prx = call_prx
        self.remote_proxy_dict = dict()
        xlogging.TraceDecorator().decorate()

    def SetRemoteCallable(self, ident, remote_proxy, current=None):
        self.remote_proxy_dict[ident] = remote_proxy

    def CleanRemoteCallable(self, ident, current=None):
        self.remote_proxy_dict.pop(ident, None)

    def getKVMCallable(self, current=None):
        return self._callable_prx

    def _current_agent_info(self, current):
        return (current.adapter.getCommunicator().proxyToString(self._remote_proxy)
                if (current and self._remote_proxy) else 'null')


class Server(object):
    def __init__(self):
        _logger.info(r'starting ...')

        init_data = Ice.InitializationData()
        init_data.properties = Ice.createProperties()
        init_data.properties.setProperty(r'Ice.LogFile', r'/var/log/clw_agent_application_ice.log')
        init_data.properties.setProperty(r'Ice.ThreadPool.Server.Size', r'1')
        init_data.properties.setProperty(r'Ice.ThreadPool.Server.SizeMax', r'8')
        init_data.properties.setProperty(r'Ice.ThreadPool.Server.StackSize', r'8388608')
        init_data.properties.setProperty(r'Ice.ThreadPool.Client.Size', r'1')
        init_data.properties.setProperty(r'Ice.ThreadPool.Client.SizeMax', r'8')
        init_data.properties.setProperty(r'Ice.ThreadPool.Client.StackSize', r'8388608')
        init_data.properties.setProperty(r'Ice.Default.Host', r'localhost')
        init_data.properties.setProperty(r'Ice.Warn.Connections', r'1')
        init_data.properties.setProperty(r'Ice.ACM.Heartbeat', r'3')
        init_data.properties.setProperty(r'Ice.ThreadPool.Client.ThreadIdleTime', r'0')
        init_data.properties.setProperty(r'Ice.ThreadPool.Server.ThreadIdleTime', r'0')
        init_data.properties.setProperty(r'KVM.Server.Endpoints', r'tcp -h 0.0.0.0 -p 10001')
        init_data.properties.setProperty(r'Ice.MessageSizeMax', r'131072')  # 单位KB, 128MB

        config_path = r'/etc/clw_logic_service.cfg'
        if os.path.exists(config_path):
            init_data.properties.load(config_path)

        self.communicator = Ice.initialize(sys.argv, init_data)

        adapter = self.communicator.createObjectAdapter("KVM.Server")
        adapter.add(CallableI(), self.communicator.stringToIdentity("callable"))
        call_prx = Utils.CallablePrx.uncheckedCast(
            adapter.createProxy(self.communicator.stringToIdentity("callable")))
        self._kvmi = KVMI(call_prx)
        adapter.add(self._kvmi, self.communicator.stringToIdentity("kvm"))
        adapter.activate()

    def run(self):
        self.communicator.waitForShutdown()
        _logger.info(r'stopped.')

    def stop(self):
        _logger.info(r'stopping...')
        self.communicator.destroy()

    def get_remote_proxy(self, ident):
        return self._kvmi.remote_proxy_dict[ident]


def handler(signum, frame):
    global app
    app.stop()


def run():
    global app

    if app is None:
        try:

            app = Server()
            signal.signal(signal.SIGINT, handler)
            app.run()
        except Exception as e:
            _logger.error(r'run failed. {}'.format(e), exc_info=True)
            raise
