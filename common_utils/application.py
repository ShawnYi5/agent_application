import abc
import os
import signal
import threading
import traceback

import Glacier2
import Ice


class _ApplicationLoggerI(Ice.Logger):

    def __init__(self, py_logger):
        super(_ApplicationLoggerI, self).__init__()
        self._py_logger = py_logger

    def _print(self, message):
        self._py_logger.info(message)

    def trace(self, category, message):
        self._py_logger.info('{} : {}'.format(category, message) if category else message)

    def warning(self, message):
        self._py_logger.warning(message)

    def error(self, message):
        self._py_logger.error(message)


class Application(abc.ABC):

    def __init__(self, signal_policy=0):
        """The constructor accepts an optional argument indicating whether to handle signals.

        :param signal_policy:
            Application.HandleSignals (the default) or
            Application.NoSignalHandling.
        """
        Application._signalPolicy = signal_policy

    def main(self, args: list, config_file: str, init_data_list: list, logger):
        """The main entry point for the Application class.

        :param args:
            The arguments are an argument list (such as sys.argv)， 最高优先级
        :param config_file:
            The file path of an Ice configuration file，次优先级
        :param init_data_list:
            InitializationData properties 参数，最低优先级
            [('Ice.Default.Host', '127.0.0.1'), ('Ice.Warn.Connections', '1'), ... ]
        :param logger:
            python 的标准库 logger 对象
        :return:
            This method does not return until after the completion of the run method.
            The return value is an integer representing the exit status.
        """
        if Application._communicator:
            Ice.getProcessLogger().error(args[0] + ": only one instance of the Application class can be used")
            return 1

        Ice.setProcessLogger(_ApplicationLoggerI(logger))

        #
        # We parse the properties here to extract Ice.ProgramName.
        #
        init_data = self.generate_init_data(config_file, init_data_list, args)

        #
        # Install our handler for the signals we are interested in. We assume main() is called from the main thread.
        #
        if Application._signalPolicy == Application.HandleSignals:
            Application._ctrlCHandler = Ice.CtrlCHandler()

        try:
            Application._interrupted = False
            Application._app_name = \
                init_data.properties.getPropertyWithDefault("Ice.ProgramName", args[0])
            Application._application = self

            #
            # Used by _destroy_on_interrupt_callback and _shutdown_on_interrupt_callback.
            #
            Application._nohup = init_data.properties.getPropertyAsInt("Ice.Nohup") > 0

            #
            # The default is to destroy when a signal is received.
            #
            if Application._signalPolicy == Application.HandleSignals:
                Application.destroy_on_interrupt()

            status = self.do_main(args, init_data)
        except Exception as e:
            Ice.getProcessLogger().error('main loop exception {}\n{}'.format(e, traceback.format_exc()))
            status = 1

        #
        # Set _ctrlCHandler to 0 only once communicator.destroy() has completed.
        #
        if Application._signalPolicy == Application.HandleSignals:
            Application._ctrlCHandler.destroy()
            Application._ctrlCHandler = None

        return status

    @staticmethod
    def generate_init_data(config_file, init_data_list, args):
        init_data = Ice.InitializationData()
        init_data.properties = Ice.createProperties(None, None)
        for _property in init_data_list:
            assert isinstance(_property[0], str) and isinstance(_property[1], str)
            init_data.properties.setProperty(_property[0], _property[1])
        if config_file and os.path.isfile(config_file):
            init_data.properties = Ice.createProperties(None, init_data.properties)
            init_data.properties.load(config_file)
        if args:
            init_data.properties = Ice.createProperties(args, init_data.properties)
        return init_data

    def do_main(self, args, init_data):
        try:
            Application._communicator = Ice.initialize(args, init_data)
            Application._destroyed = False
            status = self.run(args)
        except Exception as e:
            Ice.getProcessLogger().error('{}\n{}'.format(e, traceback.format_exc()))
            status = 1

        #
        # Don't want any new interrupt and at this point (post-run),
        # it would not make sense to release a held signal to run
        # shutdown or destroy.
        #
        if Application._signalPolicy == Application.HandleSignals:
            Application.ignore_interrupt()

        Application._condVar.acquire()
        while Application._callbackInProgress:
            Application._condVar.wait()
        if Application._destroyed:
            Application._communicator = None
        else:
            Application._destroyed = True
            #
            # And _communicator != 0, meaning will be destroyed
            # next, _destroyed = true also ensures that any
            # remaining callback won't do anything
            #
        Application._application = None
        Application._condVar.release()

        if Application._communicator:
            try:
                Application._communicator.destroy()
            except Exception as e:
                Ice.getProcessLogger().error(
                    'destroy _communicator exception {}\n{}'.format(e, traceback.format_exc()))
                status = 1
            Application._communicator = None
        return status

    @abc.abstractmethod
    def run(self, args):
        """This method must be overridden in a subclass.
            The base class supplies an argument list from which all Ice arguments have already been removed.
            The method returns an integer exit status (0 is success, non-zero is failure).
        """
        raise RuntimeError('run() not implemented')

    def interrupt_callback(self, sig):
        """Subclass hook to intercept an interrupt."""
        pass

    def app_name(cls):
        """Returns the application name (the first element of the argument list)."""
        return cls._app_name

    app_name = classmethod(app_name)

    def communicator(cls):
        """Returns the communicator that was initialized for the application."""
        return cls._communicator

    communicator = classmethod(communicator)

    def destroy_on_interrupt(cls):
        """Configures the application to destroy its communicator when interrupted by a signal."""
        if Application._signalPolicy == Application.HandleSignals:
            cls._condVar.acquire()
            if cls._ctrlCHandler.getCallback() == cls._hold_interrupt_callback:
                cls._released = True
                cls._condVar.notify()
            cls._ctrlCHandler.setCallback(cls._destroy_on_interrupt_callback)
            cls._condVar.release()
        else:
            Ice.getProcessLogger().error("interrupt method called on Application configured to not handle interrupts.")

    destroy_on_interrupt = classmethod(destroy_on_interrupt)

    def shutdown_on_interrupt(cls):
        """Configures the application to shutdown its communicator when interrupted by a signal."""
        if Application._signalPolicy == Application.HandleSignals:
            cls._condVar.acquire()
            if cls._ctrlCHandler.getCallback() == cls._hold_interrupt_callback:
                cls._released = True
                cls._condVar.notify()
            cls._ctrlCHandler.setCallback(cls._shutdown_on_interrupt_callback)
            cls._condVar.release()
        else:
            Ice.getProcessLogger().error("interrupt method called on Application configured to not handle interrupts.")

    shutdown_on_interrupt = classmethod(shutdown_on_interrupt)

    def ignore_interrupt(cls):
        """Configures the application to ignore signals."""
        if Application._signalPolicy == Application.HandleSignals:
            cls._condVar.acquire()
            if cls._ctrlCHandler.getCallback() == cls._hold_interrupt_callback:
                cls._released = True
                cls._condVar.notify()
            cls._ctrlCHandler.setCallback(None)
            cls._condVar.release()
        else:
            Ice.getProcessLogger().error("interrupt method called on Application configured to not handle interrupts.")

    ignore_interrupt = classmethod(ignore_interrupt)

    def callback_on_interrupt(cls):
        """Configures the application to invoke interrupt_callback when interrupted by a signal."""
        if Application._signalPolicy == Application.HandleSignals:
            cls._condVar.acquire()
            if cls._ctrlCHandler.getCallback() == cls._hold_interrupt_callback:
                cls._released = True
                cls._condVar.notify()
            cls._ctrlCHandler.setCallback(cls._callback_on_interrupt_callback)
            cls._condVar.release()
        else:
            Ice.getProcessLogger().error("interrupt method called on Application configured to not handle interrupts.")

    callback_on_interrupt = classmethod(callback_on_interrupt)

    def hold_interrupt(cls):
        """Configures the application to queue an interrupt for later processing."""
        if Application._signalPolicy == Application.HandleSignals:
            cls._condVar.acquire()
            if cls._ctrlCHandler.getCallback() != cls._hold_interrupt_callback:
                cls._previousCallback = cls._ctrlCHandler.getCallback()
                cls._released = False
                cls._ctrlCHandler.setCallback(cls._hold_interrupt_callback)
            # else, we were already holding signals
            cls._condVar.release()
        else:
            Ice.getProcessLogger().error("interrupt method called on Application configured to not handle interrupts.")

    hold_interrupt = classmethod(hold_interrupt)

    def release_interrupt(cls):
        """Instructs the application to process any queued interrupt."""
        if Application._signalPolicy == Application.HandleSignals:
            cls._condVar.acquire()
            if cls._ctrlCHandler.getCallback() == cls._hold_interrupt_callback:
                #
                # Note that it's very possible no signal is held;
                # in this case the callback is just replaced and
                # setting _released to true and signalling _condVar
                # do no harm.
                #
                cls._released = True
                cls._ctrlCHandler.setCallback(cls._previousCallback)
                cls._condVar.notify()
            # Else nothing to release.
            cls._condVar.release()
        else:
            Ice.getProcessLogger().error("interrupt method called on Application configured to not handle interrupts.")

    release_interrupt = classmethod(release_interrupt)

    def interrupted(cls):
        """Returns True if the application was interrupted by a signal, or False otherwise."""
        cls._condVar.acquire()
        result = cls._interrupted
        cls._condVar.release()
        return result

    interrupted = classmethod(interrupted)

    def _hold_interrupt_callback(cls, sig):
        cls._condVar.acquire()
        while not cls._released:
            cls._condVar.wait()
        if cls._destroyed:
            #
            # Being destroyed by main thread
            #
            cls._condVar.release()
            return
        callback = cls._ctrlCHandler.getCallback()
        cls._condVar.release()
        if callback:
            callback(sig)

    _hold_interrupt_callback = classmethod(_hold_interrupt_callback)

    def _destroy_on_interrupt_callback(cls, sig):
        cls._condVar.acquire()
        if cls._destroyed or cls._nohup and sig == signal.SIGHUP:
            #
            # Being destroyed by main thread, or nohup.
            #
            cls._condVar.release()
            return

        cls._callbackInProcess = True
        cls._interrupted = True
        cls._destroyed = True
        cls._condVar.release()

        try:
            cls._communicator.destroy()
        except Exception as e:
            Ice.getProcessLogger().error(
                "{} (while destroying in response to signal {}): e: {}\n{}".format(
                    cls._app_name, str(sig), e, traceback.format_exc()))

        cls._condVar.acquire()
        cls._callbackInProcess = False
        cls._condVar.notify()
        cls._condVar.release()

    _destroy_on_interrupt_callback = classmethod(_destroy_on_interrupt_callback)

    def _shutdown_on_interrupt_callback(cls, sig):
        cls._condVar.acquire()
        if cls._destroyed or cls._nohup and sig == signal.SIGHUP:
            #
            # Being destroyed by main thread, or nohup.
            #
            cls._condVar.release()
            return

        cls._callbackInProcess = True
        cls._interrupted = True
        cls._condVar.release()

        try:
            cls._communicator.shutdown()
        except Exception as e:
            Ice.getProcessLogger().error(
                "{} (while shutting down in response to signal {}): e: {}\n{}".format(
                    cls._app_name, str(sig), e, traceback.format_exc()))

        cls._condVar.acquire()
        cls._callbackInProcess = False
        cls._condVar.notify()
        cls._condVar.release()

    _shutdown_on_interrupt_callback = classmethod(_shutdown_on_interrupt_callback)

    def _callback_on_interrupt_callback(cls, sig):
        cls._condVar.acquire()
        if cls._destroyed:
            #
            # Being destroyed by main thread.
            #
            cls._condVar.release()
            return
        # For SIGHUP the user callback is always called. It can decide what to do.

        cls._callbackInProcess = True
        cls._interrupted = True
        cls._condVar.release()

        try:
            cls._application.interrupt_callback(sig)
        except Exception as e:
            Ice.getProcessLogger().error(
                "{} (while interrupting in response to signal {}): e: {}\n{}".format(
                    cls._app_name, str(sig), e, traceback.format_exc()))

        cls._condVar.acquire()
        cls._callbackInProcess = False
        cls._condVar.notify()
        cls._condVar.release()

    _callback_on_interrupt_callback = classmethod(_callback_on_interrupt_callback)

    HandleSignals = 0
    NoSignalHandling = 1

    _nohup = False

    _app_name = None
    _application = None
    _ctrlCHandler = None
    _previousCallback = None
    _interrupted = False
    _released = False
    _destroyed = False
    _callbackInProgress = False
    _condVar = threading.Condition()
    _signalPolicy = HandleSignals

    _communicator = None


class SessionNotExistException(Exception):
    def __init__(self):
        pass


class RestartSessionException(Exception):
    def __init__(self):
        pass


class SessionCancelException(Exception):
    def __init__(self):
        pass


class ConnectionCallbackI(Ice.ConnectionCallback):
    def __init__(self, app):
        self._app = app

    def heartbeat(self, conn):
        pass

    def closed(self, conn):
        Ice.getProcessLogger().warning('{} connect closed {}'.format(self._app.name, conn))
        self._app.connection_closed()


class GlacierSession(threading.Thread, abc.ABC):
    """数据透传链路"""

    def __init__(self, name: str, config_file: str, init_data_list: list, logger):
        """
        :param name:
            实例and线程的名称
        :param config_file:
            The file path of an Ice configuration file，高优先级
        :param init_data_list:
            InitializationData properties 参数，低优先级
            [('Ice.Default.Host', '127.0.0.1'), ('Ice.Warn.Connections', '1'), ... ]
        :param logger:
            python 的标准库 logger 对象
        :var self.exception:
            当线程退出后，可获取线程内部产生的异常
            在网络连接断开后，内部进行自动重试，因此不会记录到网络通信组件的异常
        """
        super(GlacierSession, self).__init__(name=name)
        self.config_file = config_file
        self.init_data_list = init_data_list
        self.logger = logger

        self.init_data_list.append(("Ice.RetryIntervals", "-1"))  # 关闭ACM的重试功能

        self._communicator = None
        self._adapter = None
        self._router = None
        self._session = None
        self._is_session_created = False
        self._category = None

        self.exception = None

        self._quit = False
        self._quit_cond = threading.Condition()

    def __del__(self):
        if self.session_exist:
            Ice.getProcessLogger().error('{} not uninit !!!!'.format(self.name))
            self._do_uninit_internal()
        Ice.getProcessLogger().trace(None, '{} __del__'.format(self.name))

    def start(self):
        """连接到透传网关

        :remark:
            当首次连接失败时，抛出异常
            当运行过程中链路断开后，会进行自动重连
        """
        init_data = Application.generate_init_data(self.config_file, self.init_data_list, None)
        self._do_init_internal(init_data)
        Ice.getProcessLogger().trace(None, '{} init ok'.format(self.name))

        try:
            super(GlacierSession, self).start()
        except Exception as e:
            Ice.getProcessLogger().error('{} start failed {}\n{}'.format(self.name, e, traceback.format_exc()))
            self._do_uninit_internal()
            raise

    def stop(self):
        """停止连接

        :remark:
            异步，不等待连接停止
        """
        Ice.getProcessLogger().trace(None, '{} set quit flag'.format(self.name))
        self._quit_cond.acquire()
        self._quit = True
        self._quit_cond.notify_all()
        self._quit_cond.release()

    def stop_and_join(self):
        """停止连接并等待连接停止

        :remark:
            同步
        """
        self.stop()
        if self.is_alive():
            self.join()

    @abc.abstractmethod
    def get_session_username_and_password(self) -> (str, str):
        """获得连接到Glacier服务的username与password"""
        raise NotImplementedError()

    @abc.abstractmethod
    def run_with_session(self):
        """主业务逻辑

        :remark:
            已经连接到Glacier服务，可以调用所有成员函数
            不可阻塞在该函数中
            如果发生链路断开，该方法会被重复调用
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def post_run_with_session(self):
        """主业务逻辑清理接口

        :remark:
            当 run_with_session 中发生异常时，将会被调用
            当 run_with_session 返回后发生异常，将会被调用
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def connection_closed(self):
        """保留：通知链路断开"""
        raise NotImplementedError()

    @abc.abstractmethod
    def heartbeat_check(self):
        """高层逻辑心跳"""
        raise NotImplementedError()

    @property
    def communicator(self):
        return self._communicator

    @property
    def session_exist(self) -> bool:
        """判断session是否正常

        :remark:
            仅仅检查标记，不进行数据报文探测
        """
        return self._is_session_created and self._category is not None

    @property
    def router(self):
        assert self._router is not None
        return self._router

    @property
    def session(self):
        if not self.session_exist:
            raise SessionNotExistException()
        return self._session

    @property
    def category_for_client(self):
        if not self.session_exist:
            raise SessionNotExistException()
        return self._category

    def create_callback_identity(self, name):
        return Ice.Identity(name, self.category_for_client)

    def add_with_uuid(self, servant):
        return self.object_adapter.add(servant, self.create_callback_identity(Ice.generateUUID()))

    @property
    def object_adapter(self):
        if not self.session_exist:
            raise SessionNotExistException()
        if self._adapter is None:
            self._adapter = self._communicator.createObjectAdapterWithRouter("", self._router)
            self._adapter.activate()
        return self._adapter

    @property
    def _run_continue(self) -> bool:
        """线程是否继续循环工作"""
        if self._quit:
            raise SessionCancelException()
        return self.exception is None

    def run(self):
        try:
            while self._run_continue:
                if self.session_exist:
                    self._run_with_session()
                else:
                    self._create_new_session()
        except SessionCancelException:
            pass  # do nothing
        finally:
            Ice.getProcessLogger().warning('{} exit'.format(self.name))

    def _set_exception(self, e):
        if isinstance(e, SessionCancelException):
            # 主动取消的优先级最高
            self.exception = e
        elif self.exception is None:
            self.exception = e
        else:
            # 仅记录最初始的异常
            Ice.getProcessLogger().trace(None, '{} ignore record {}'.format(self.name, e))

    def _create_new_session(self):
        init_data = Application.generate_init_data(self.config_file, self.init_data_list, None)
        try:
            self._do_init_internal(init_data)
        except RestartSessionException:
            self._do_uninit_internal()
            pass  # do nothing
        except (Ice.ConnectionRefusedException, Ice.ConnectionLostException, Ice.UnknownLocalException,
                Ice.RequestFailedException, Ice.TimeoutException) as e:
            Ice.getProcessLogger().error('{} init net {}\n{}'.format(self.name, e, traceback.format_exc()))
            self._do_uninit_internal()
            pass  # do nothing
        except Exception as e:
            Ice.getProcessLogger().error('{} failed {}\n{}'.format(self.name, e, traceback.format_exc()))
            self._set_exception(e)

    def _need_running(self) -> bool:
        self._quit_cond.acquire()
        self._quit_cond.wait(60)  # wait 60s
        self._quit_cond.release()
        return not self._quit

    def _run_with_session(self):
        try:
            self.run_with_session()
            while self._need_running():
                self.heartbeat_check()
            raise SessionCancelException()

        # We want to restart on those exceptions which indicate a
        # break down in communications, but not those exceptions that
        # indicate a programming logic error (ie: marshal, protocol
        # failure, etc).
        except SessionCancelException as sce:
            Ice.getProcessLogger().warning('{} SessionCancelException'.format(self.name))
            self._set_exception(sce)
        except RestartSessionException:
            pass  # do nothing
        except (Ice.ConnectionRefusedException, Ice.ConnectionLostException, Ice.UnknownLocalException,
                Ice.RequestFailedException, Ice.TimeoutException) as e:
            Ice.getProcessLogger().error('{} run net {}\n{}'.format(self.name, e, traceback.format_exc()))
            pass  # do nothing
        except Exception as e:
            Ice.getProcessLogger().error('{} failed {}\n{}'.format(self.name, e, traceback.format_exc()))
            self._set_exception(e)
        finally:
            self._post_run_with_session()
            self._do_uninit_internal()

    def _post_run_with_session(self):
        try:
            self.post_run_with_session()
        except Exception as e:
            Ice.getProcessLogger().warning(
                '{} _post_run_with_session {}\n{}'.format(self.name, e, traceback.format_exc()))

    def _do_init_internal(self, init_data):
        try:
            self._communicator = Ice.initialize(data=init_data)

            self._router = Glacier2.RouterPrx.uncheckedCast(
                self._communicator.getDefaultRouter())
            if self._router is None:
                raise Exception('no glacier2 router configured')

            try:
                username, password = self.get_session_username_and_password()
                self._session = self._router.createSession(username, password)
                self._is_session_created = True
            except Ice.LocalException as e:
                Ice.getProcessLogger().error('call create_session failed {}\n{}'.format(e, traceback.format_exc()))
                raise

            if self._is_session_created:
                self._set_acm_setting()
                self._category = self._router.getCategoryForClient()
        except Exception as e:
            Ice.getProcessLogger().error('_do_init_internal failed : {}'.format(e))
            self._do_uninit_internal()
            raise

    def _set_acm_setting(self):
        acm_timeout = 0
        try:
            acm_timeout = self._router.getACMTimeout()
        except Ice.OperationNotExistException:
            pass
        if acm_timeout <= 0:
            acm_timeout = self._router.getSessionTimeout()
        if acm_timeout > 0:
            connection = self._router.ice_getCachedConnection()
            assert connection, '_do_init_internal ice_getCachedConnection failed'
            connection.setACM(acm_timeout, Ice.Unset, Ice.ACMHeartbeat.HeartbeatAlways)
            connection.setCallback(ConnectionCallbackI(self))

    def _do_uninit_internal(self):
        if self._router:
            if self._is_session_created:
                self._is_session_created = False
                try:
                    self._router.destroySession()
                except (Ice.ConnectionLostException, SessionNotExistException):
                    pass
                except Exception as e:
                    Ice.getProcessLogger().error(
                        'unexpected exception when destroying the session {}\n{}'.format(e, traceback.format_exc()))

            self._router = None

        if self._communicator:
            try:
                self._communicator.destroy()
            except Exception as e:
                Ice.getProcessLogger().error(
                    'unexpected exception when destroying the communicator {}\n{}'.format(e, traceback.format_exc()))

            self._communicator = None

        self._adapter = None
        self._router = None
        self._session = None
        self._createdSession = False
        self._category = None
