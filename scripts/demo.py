from common_utils import xlogging

_logger = xlogging.getLogger(__name__)


class Foo(object):

    def __init__(self, args_dict, raw_input):
        _logger.info('Foo __init__ {} {}'.format(args_dict, raw_input))

    def hello(self, args_dict, raw_input):
        _logger.info('xxxx', args_dict, raw_input)
        return 'hi, ', b''

    def get_name(self, args_dict, raw_input):
        _logger.info('get_name', args_dict, raw_input)
        return '1cc', b''


def foo(args_dict, raw_input):
    _logger.info('foo {} {}'.format(args_dict, raw_input))
    return 'foo', b''
