import gobject
from dbus.types import Array, Dictionary, String, Struct
import weakref

from telepathy.constants import (
    CONNECTION_PRESENCE_TYPE_AVAILABLE,
    CONNECTION_PRESENCE_STATUS_AVAILABLE,
    CONNECTION_STATUS_CONNECTED,
    CONNECTION_STATUS_DISCONNECTED,
    CONNECTION_STATUS_REASON_REQUESTED,
    CONNECTION_STATUS_REASON_NONE_SPECIFIED,
    CONTACT_LIST_STATE_SUCCESS,
    HANDLE_TYPE_CONTACT,
    SUBSCRIPTION_STATE_YES,
)
from telepathy.interfaces import (
    CONNECTION,
    CONNECTION_INTERFACE_CONTACT_GROUPS,
    CONNECTION_INTERFACE_CONTACT_LIST,
    CONNECTION_INTERFACE_SIMPLE_PRESENCE,
)
from telepathy.server import (
    Connection,
    ConnectionInterfaceContacts,
    ConnectionInterfaceContactGroups,
    ConnectionInterfaceContactList,
    ConnectionInterfaceRequests,
    ConnectionInterfaceSimplePresence,
)
from dictionary import PROGRAM, PROTOCOL, CONTACTS, GROUP
from dictionary.channel_manager import DictionaryChannelManager


__all__ = (
    'DictionaryConnection',
)


class DictionaryConnection(Connection,
    ConnectionInterfaceContactGroups,
    ConnectionInterfaceContactList,
    ConnectionInterfaceContacts,
    ConnectionInterfaceRequests,
    ConnectionInterfaceSimplePresence,
    ):

    def __init__(self, protocol, manager, parameters):
        protocol.check_parameters(parameters)
        self._manager = weakref.proxy(manager)

        account = unicode(parameters['account'])
        self._statuses = protocol._statuses
        self._channel_manager = DictionaryChannelManager(self, protocol)
        Connection.__init__(self, PROTOCOL, account, PROGRAM, protocol)
        ConnectionInterfaceContactGroups.__init__(self)
        ConnectionInterfaceContactList.__init__(self)
        ConnectionInterfaceContacts.__init__(self)
        ConnectionInterfaceRequests.__init__(self)
        ConnectionInterfaceSimplePresence.__init__(self)

        self_handle = self.create_handle(HANDLE_TYPE_CONTACT, account.encode('utf-8'))
        self.set_self_handle(self_handle)

        self.__disconnect_reason = CONNECTION_STATUS_REASON_NONE_SPECIFIED

    def handle(self, handle_type, handle_id):
        self.check_handle(handle_type, handle_id)
        return self._handles[handle_type, handle_id]

    def Connect(self):
        if self._status == CONNECTION_STATUS_DISCONNECTED:
            gobject.timeout_add(50, self._connected)

    def _connected(self):
        self._groups = [GROUP]

        self.StatusChanged(CONNECTION_STATUS_CONNECTED, CONNECTION_STATUS_REASON_REQUESTED)
        self.ContactListStateChanged(CONTACT_LIST_STATE_SUCCESS)

    def Disconnect(self):
        self.__disconnect_reason = CONNECTION_STATUS_REASON_REQUESTED
        gobject.timeout_add(50, self._disconnected)

    def _disconnected(self):
        self._groups = []

        self.StatusChanged(CONNECTION_STATUS_DISCONNECTED, self.__disconnect_reason)
        self._manager.disconnected(self)

    def GetContactListAttributes(self, interfaces, hold):
        ret = Dictionary(signature='ua{sv}')
        for contact in CONTACTS:
            handle = self.ensure_handle(HANDLE_TYPE_CONTACT, contact)
            ret[int(handle)] = Dictionary(signature='sv')
            ret[int(handle)][CONNECTION + '/contact-id'] = contact
            ret[int(handle)][CONNECTION_INTERFACE_CONTACT_LIST + '/subscribe'] = SUBSCRIPTION_STATE_YES
            ret[int(handle)][CONNECTION_INTERFACE_CONTACT_LIST + '/publish'] = SUBSCRIPTION_STATE_YES
            ret[int(handle)][CONNECTION_INTERFACE_CONTACT_GROUPS + '/groups'] = Array([String(GROUP)], signature='s')
            ret[int(handle)][CONNECTION_INTERFACE_SIMPLE_PRESENCE + '/presence'] = Struct(
                (CONNECTION_PRESENCE_TYPE_AVAILABLE, CONNECTION_PRESENCE_STATUS_AVAILABLE, "avail"),
                signature='uss',
            )
        return ret

    def GetPresences(self, contacts):
        presences = Dictionary(signature='u(uss)')
        for handle_id in contacts:
            handle = self.handle(HANDLE_TYPE_CONTACT, handle_id)
            presences[handle] = Struct(
                (CONNECTION_PRESENCE_TYPE_AVAILABLE, CONNECTION_PRESENCE_STATUS_AVAILABLE, "avail"),
                signature='uss',
            )
        return presences
