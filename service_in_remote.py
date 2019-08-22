import json
import os
import signal
import sys
import threading
import time
import datetime

import Ice

from common_utils import xlogging, application, funcs, remote_helper
from application_helper import CallFunction, NewInstance, DelInstance, NoneCall
from scripts import system_info
import Utils
import kvm4remote
import VpsAgent

app = None
_logger = xlogging.getLogger(__name__)


class CallableI(Utils.Callable):

    def __init__(self):
        xlogging.TraceDecorator().decorate()

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


_kvm_channel = None


class KVMChannel(application.GlacierSession):
    """维持与KVM服务器的通信通道"""

    def __init__(self, remote_ident, kvm_ip, aio_ip, aio_port):
        super(KVMChannel, self).__init__('KVMChannel',
                                         '',
                                         [('KVM.Proxy', 'kvm:tcp -h {} -p 10001'.format(kvm_ip)),
                                          ('Ice.ThreadPool.Server.Size', '8'),
                                          ('Ice.ThreadPool.Server.Size', '8'),
                                          ('Ice.ThreadPool.Server.SizeMax', '64'),
                                          ('Ice.ThreadPool.Server.StackSize', '8388608'),
                                          ('Ice.Default.Router', 'ClwGlacier/router:tcp -p 20100 -h {}'.format(aio_ip)),
                                          ],
                                         _logger)
        self._callback = CallableI()
        self._kvm_prx = None
        self._remote_ident = remote_ident

    def get_session_username_and_password(self):
        print("This demo accepts any user-id / password combination.")
        return 'username', 'password'

    def run_with_session(self):
        self._kvm_prx = kvm4remote.KVMPrx.checkedCast(self.communicator.propertyToProxy('KVM.Proxy'))
        assert self._kvm_prx is not None

        remote_ident = self.create_callback_identity(self._remote_ident)
        self.object_adapter.add(self._callback, remote_ident)

        remote_prx = Utils.CallablePrx.uncheckedCast(self.object_adapter.createProxy(remote_ident))
        self._kvm_prx.SetRemoteCallable(self._remote_ident, remote_prx)

        # 调用远端接口
        kvm_callable_prx = self._kvm_prx.getKVMCallable()
        func = remote_helper.FunctionMapper(kvm_callable_prx, _logger)
        func.execute('demo', 'foo', '{"hello":"just test"}')

    def post_run_with_session(self):
        kvm_prx, self._kvm_prx = self._kvm_prx, None
        if kvm_prx is not None:
            kvm_prx.CleanRemoteCallable(self._remote_ident)

    def heartbeat_check(self):
        self._kvm_prx.ice_ping()

    def connection_closed(self):
        pass
        print("connection_closed")


class AgentReceiverI(VpsAgent.AgentReceiver):

    def __init__(self, _app):
        super(AgentReceiverI, self).__init__()
        self._app = _app

    def JsonFuncV2(self, json_str, raw_bytes, current=None):
        _logger.info('JsonFuncV2 json_str {}'.format(json_str))
        _ = raw_bytes
        data = json.loads(json_str)
        try:
            action = data.pop('type')
            method = 'p_{}'.format(action)
            if hasattr(self, method):
                return getattr(self, method)(data, raw_bytes)
            else:
                return json.dumps({'msg': 'invalid invoke {}'.format(json_str)}), bytes()
        except Exception as e:
            _logger.error('JsonFuncV2 failed:{}'.format(e))
            raise

    def p_start_kvm_channel(self, data, raw_bytes):
        global _kvm_channel
        if _kvm_channel:
            _kvm_channel.stop_and_join()
            _kvm_channel = None
        _kvm_channel = KVMChannel(data['remote_ident'], data['kvm_ip'],
                                  self._app.communicator().getProperties().getProperty(r'Ice.Default.Host'),
                                  '20100')
        _kvm_channel.start()
        return '{}', bytes()

    def p_stop_kvm_channel(self, data, raw_bytes):
        global _kvm_channel
        if _kvm_channel:
            _kvm_channel.stop_and_join()
            _kvm_channel = None
        return '{}', bytes()


class RPCChannel(threading.Thread):
    """维持与AIO服务器的通信通道"""

    SLEEP_SECONDS_MIN = 30
    SLEEP_SECONDS_MAX = 120

    def __init__(self, _app):
        super(RPCChannel, self).__init__(name='RPCChannel', daemon=True)
        self._app = _app
        self._session_prx = None
        self._sleep_seconds = self.SLEEP_SECONDS_MIN
        self._last_session_ice_identity = ''
        self._last_session_name = ''

    def run(self):
        try:
            while True:
                try:
                    _logger.debug('RPCChannel start check _session_exist')
                    if not self._session_exist():
                        _logger.debug('RPCChannel set set_session_prx None')
                        self._app.set_session_prx(None)
                        _logger.debug('RPCChannel _destroy_session None')
                        self._destroy_session()
                        self._create_session()
                        _logger.debug('RPCChannel _create_session TRUE self._session_prx{}'.format(self._session_prx))
                        self._app.set_session_prx(self._session_prx)
                    _logger.debug('RPCChannel check _session_exist TRUE')
                    self._sleep_seconds = 20
                except Exception as e:
                    _logger.error(r'RPCChannel failed : {}'.format(e), exc_info=True)
                    self._sleep_seconds = min(self._sleep_seconds + 10, self.SLEEP_SECONDS_MAX)
                finally:
                    time.sleep(self._sleep_seconds)
        except Exception as e:
            _logger.error('run Exception {}'.format(e), exc_info=True)

    def _session_exist(self):
        if not self._session_prx:
            _logger.debug('RPCChannel _session_exist not self._session_prx')
            return False

        for _ in range(3):
            try:
                self._session_prx.refresh()
                return True
            except (Ice.ObjectNotExistException, Ice.ObjectNotFoundException):
                _logger.debug('RPCChannel _session_exist refresh ObjectNotExistException ObjectNotFoundException')
                return False
            except Exception as e:
                _logger.debug(r'call session refresh failed {}'.format(e))

        return False

    def _create_session(self):
        factory = None

        try:
            factory = VpsAgent.SessionFactoryPrx.checkedCast(
                self._app.communicator().propertyToProxy("SessionFactory.Proxy"))
        except Exception as e:
            _logger.debug(r'ssl factory {}'.format(e))

        if factory is None:
            factory = VpsAgent.SessionFactoryPrx.checkedCast(
                self._app.communicator().propertyToProxy("SessionFactoryTcp.Proxy"))

        system_info_dict = system_info.SystemInfo().get()
        macs = [nic['Mac'] for nic in system_info_dict['Nic']]
        macs.append('CLW9385b913b')
        agent_ident = self._generate_agent_ident(['CLW9385b913b'])
        system_info_str = json.dumps(system_info_dict)
        self._session_prx = factory.create(agent_ident, system_info_str)

        if factory.ice_getConnection().toString() != self._session_prx.ice_getConnection().toString():
            factory.ice_getConnection().close(True)

        # TODO deal soft ident ?
        self._last_session_ice_identity = self._session_prx.QueryIdentity()
        self._last_session_name = self._session_prx.QueryName()

        self._session_prx.ice_getConnection().setAdapter(self._app.agent_receiver_adapter)
        self._session_prx.initiateReceiver(self._app.agent_receiver_ice_ident)

    def _destroy_session(self):
        try:
            prx, self._session_prx = self._session_prx, None
            if prx:
                prx.destroy()
                prx.ice_getConnection().close(True)
        except Exception as e:
            _logger.debug(r'_destroy_session failed {}'.format(e))

    def _generate_agent_ident(self, macs):
        agent_ident = VpsAgent.AgentIdentification()
        agent_ident.Identity = self._last_session_ice_identity
        agent_ident.ident.Name = self._last_session_name
        agent_ident.ident.Hardware = macs
        return agent_ident


class SessionNotExistException(Exception):
    pass


class Client(application.Application):
    """客户端主线程"""

    def __init__(self):
        super(Client, self).__init__()
        self._session_prx = None
        self.agent_receiver_ice_ident = Ice.Identity()
        self.agent_receiver_ice_ident.category = "RPCChannel"
        self.agent_receiver_ice_ident.name = Ice.generateUUID()
        self.agent_receiver_adapter = None
        self.agent_receiver = AgentReceiverI(self)

    def run(self, args):
        _ = args

        self._create_adapter()

        rpc = RPCChannel(self)
        rpc.start()

        self.communicator().waitForShutdown()

        return 0

    def _create_adapter(self):
        self.agent_receiver_adapter = self.communicator().createObjectAdapter("")
        self.agent_receiver_adapter.add(self.agent_receiver, self.agent_receiver_ice_ident)
        self.agent_receiver_adapter.activate()

    @property
    def session_prx(self):
        s = self._session_prx
        if s:
            return s
        else:
            raise SessionNotExistException()

    def set_session_prx(self, session_prx):
        if session_prx:
            _logger.info(r'update session_prx')
        elif self._session_prx is not None:
            _logger.info(r'clean session_prx')
        self._session_prx = session_prx


def create_flag_file(file_path, contents):
    with open(file_path, 'w') as f:
        f.write(contents)


def set_event(event_name):
    import win32event as w32e
    hEvent = w32e.CreateEvent(None, 0, 0, event_name)
    w32e.SetEvent(hEvent)


def run_without_agent(args):
    _logger.info(
        '********************************* start service pid {}****************************************'.format(
            os.getpid()))
    _logger.info('run_without_agent args {}'.format(args))
    print('run_without_agent args {}'.format(args))
    kvm_channel = KVMChannel(args['ident'], args['ip_in_kvm'], args['aio_ip'], args['aio_port'])
    try:
        if os.path.exists(args['flag_path']):
            os.remove(args['flag_path'])
        kvm_channel.setDaemon(True)
        kvm_channel.start()
        create_flag_file(args['flag_path'],
                         '{} start ok\n'
                         'ident {} \n'
                         'aio ip {}\n'
                         'kvm ip {}'.format(datetime.datetime.now(), args['ident'],
                                            args['aio_ip'], args['ip_in_kvm']))
    except Exception as e:
        _logger.error('run_without_agent error :{}'.format(e), exc_info=True)
        _logger.info(
            '********************************* end service pid {}****************************************'.format(
                os.getpid()))
    finally:
        set_event(args['event_name'])
    funcs.waite_end_event()
    _logger.info(
        '********************************* end service pid {}****************************************'.format(
            os.getpid()))


def run():
    global app

    if app is None:
        try:
            app = Client()
            sys.exit(
                app.main(
                    sys.argv,
                    os.path.join(funcs.get_install_path(), "remote_agent.config"),
                    [("Ice.ACM.Close", "0"),
                     ("Ice.ACM.Heartbeat", "3"),
                     ("Ice.ACM.Timeout", "120"),
                     ("Ice.Warn.Connections", "1"),
                     ("Ice.ThreadPool.Server.SizeMax", "16"),
                     # ("Ice.ThreadPool.Client.SizeMax", "16"), 只需要响应服务器请求，不需要配置客户端线程
                     ("Ice.RetryIntervals", "1000 5000 10000"),
                     ("Ice.MessageSizeMax", "4096"),
                     ("Ice.TCP.RcvSize", "4194304"),
                     ("Ice.TCP.SndSize", "4194304"),
                     ("Ice.ThreadPool.Client.StackSize", "1048576"),
                     ("Ice.ThreadPool.Server.StackSize", "1048576"),
                     ("SessionFactory.Proxy", "agent:ssl -p 20001 -t 20000"),
                     ("SessionFactoryTcp.Proxy", "agent:tcp -p 20000 -t 20000"),
                     ],
                    _logger
                )
            )
        except Exception as e:
            _logger.error(r'run failed. {}'.format(e), exc_info=True)
            raise
