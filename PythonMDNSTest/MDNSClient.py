# http://avahi.org/wiki/PythonBrowseExample
import dbus, gobject
import avahi
from dbus import DBusException
from dbus.mainloop.glib import DBusGMainLoop

# Looks for iTunes shares

"From https://stackoverflow.com/questions/3430245/how-to-develop-an-avahi-client-server"

TYPE = "_http._udp"


def service_resolved(*args):
    print('service resolved')
    print('name:', args[2])
    print('address:', args[7])
    print('port:', args[8])
    print('protocol:', args[3])
    print('host name:', args[5])

    print('?0:', args[0])
    print('?1:', args[1])
    print('?4:', args[4])
    print('?6:', args[6])


def print_error(*args):
    print('error_handler')
    print(args[0])


def myhandler(interface, protocol, name, stype, domain, flags):
    print("Found service '%s' type '%s' domain '%s' " % (name, stype, domain))

    if flags & avahi.LOOKUP_RESULT_LOCAL:
            # local service, skip
            pass

    server.ResolveService(interface, protocol, name, stype,
        domain, avahi.PROTO_UNSPEC, dbus.UInt32(0),
        reply_handler=service_resolved, error_handler=print_error)


loop = DBusGMainLoop()

bus = dbus.SystemBus(mainloop=loop)

server = dbus.Interface( bus.get_object(avahi.DBUS_NAME, '/'),
        'org.freedesktop.Avahi.Server')

sbrowser = dbus.Interface(bus.get_object(avahi.DBUS_NAME,
        server.ServiceBrowserNew(avahi.IF_UNSPEC,
            avahi.PROTO_UNSPEC, TYPE, 'local', dbus.UInt32(0))),
        avahi.DBUS_INTERFACE_SERVICE_BROWSER)

sbrowser.connect_to_signal("ItemNew", myhandler)

gobject.MainLoop().run()