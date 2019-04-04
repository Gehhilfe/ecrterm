# -*- coding: utf-8 -*-

import unittest
import asyncio
import threading 
import pytest 
from ecrterm.transmission.transport_tcp import TCPTransport
from ecrterm.packets import *


class RespProtocol(asyncio.Protocol):

    def __init__(self, resp):
        self.resp = resp

    def connection_made(self, transport):
        print("send resp")
        self.transport = transport
        if isinstance(self.resp, str):
            self.transport.write(self.resp.encode('utf-8'))
        else:
            self.transport.write(bytes(self.resp))

async def create_server(host, data):
    loop = asyncio.get_running_loop()
    def factory():
        return RespProtocol(data)
    server = await loop.create_server(factory, host)
    return server

def loop_in_thread(loop, cr):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(cr)


@pytest.mark.asyncio
async def test_create_server():
    reg = Registration()
    reg.fixed_values['password'] = '000111'
    srv = await create_server('localhost', reg.to_list())
    async with srv:
        transport = TCPTransport("localhost:%s" % srv.sockets[0].getsockname()[1])
        await transport.connect()
        res, apdu = await transport.receive()
        print("done")
