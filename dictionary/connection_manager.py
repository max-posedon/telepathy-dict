from telepathy.server import ConnectionManager

from dictionary import PROGRAM, PROTOCOL
from dictionary.protocol import DictionaryProtocol

__all__ = (
	'FooConnectionManager',
)


class DictionaryConnectionManager(ConnectionManager):
    def __init__(self, shutdown_func=None):
        ConnectionManager.__init__(self, PROGRAM)
        self._implement_protocol(PROTOCOL, DictionaryProtocol)
