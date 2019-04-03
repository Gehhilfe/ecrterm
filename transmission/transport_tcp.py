# -*- coding: utf-8 -*-

"""

    TCP Layer


    @author Tim Burkert <tim.burkert@zoi.de>
"""

from ecrterm import crc, conv, common
from ecrterm.packets.apdu import APDUPacket, Packets
import os, serial, select, time#@UnresolvedImport
from ecrterm.transmission.signals import *
import asyncio
import logging


DEFAULT_PORT = 1234

def noop(*args, **kwargs):
    pass

class TCPTransport(common.Transport):
    slog = noop

    def __init__(self, connectionString, log=None):
        self.connectionString = connectionString
        self.connection = None

    def connect(self):
        regex = '(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
        matcher = re.search(regex, self.connectionString)
        hostname = m.group('host')
        port = m.group('port')
        if not port:
            port = DEFAULT_PORT
        else:
            port = int(port)
        self.connection = await asyncio.open_connection(host, port)

    def close(self):
        if self.connection:
            self.connection.close()

    def reset(self):
        pass

    def receive(self):
        apdu = []
        pktClass = await self.connection.readexactly(2))
        apdu  += pktClass
        length = 0
        bLength = await self.connection.readexactly(1)
        apdu += [bLength]
        
        if bLength == 0xFF:
            bLength = await self.connection.readexactly(2)
            apdu.extend([bLength])
            length = int.from_bytes(bLength, 'big')
        else
            length = bLength

        data = await self.connection.readexactly(length)
        apdu.extend([data])
        logging.info("Received APDU pktClass = %s, length = %i" % pktClass, length)

        return True, APDUPacket.parse(apdu)


    def send(self, apdu, tries=0, no_wait=False):
        if apdu:
            self.connection.write(apdu.to_list())
            await self.connection.drain()

            if not no_wait:
                return self.receive()
            return True
            

    
