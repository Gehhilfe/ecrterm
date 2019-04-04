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
import re

DEFAULT_PORT = 1234

def noop(*args, **kwargs):
    pass

class TCPTransport(common.Transport):
    slog = noop

    def __init__(self, connectionString, log=None):
        self.connectionString = connectionString
        self.writer = None

    async def connect(self):
        regex = '(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
        matcher = re.search(regex, self.connectionString)
        hostname = matcher.group('host')
        port = matcher.group('port')
        if not port:
            port = DEFAULT_PORT
        else:
            port = int(port)
        self.reader, self.writer = await asyncio.open_connection(hostname, port)

    def close(self):
        if self.writer:
            self.writer.close()

    def reset(self):
        pass

    async def receive(self):
        apdu = []
        pktClass = await self.reader.readexactly(2)
        apdu  += pktClass
        length = 0
        bLength = await self.reader.readexactly(1)
        apdu += [int.from_bytes(bLength, 'big')]
        
        if bLength == 0xFF:
            bLength = await self.reader.readexactly(2)
            apdu.extend([int.from_bytes(bLength, 'big')])
        length = int.from_bytes(bLength, 'big')
        data = await self.reader.readexactly(length)
        apdu += data
        logging.info("Received APDU pktClass = %s, length = %s" % (pktClass, length))

        return True, APDUPacket.parse(apdu)


    async def send(self, apdu, tries=0, no_wait=False):
        if apdu:
            self.writer.write(apdu.to_list())
            await self.writer.drain()

            if not no_wait:
                return self.receive()
            return True
            

    
