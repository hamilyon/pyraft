# -*- coding: utf-8 -*-
import zmq
import yaml
import time
import sys

import client_thread
import zeromq_context
import threading

from core import RaftPeer
from messages import ClientUpdate


def run_peer():
    context = zeromq_context.context
    server_name = sys.argv[1]

    with open("servers.yaml", 'r') as stream:
        config = yaml.load(stream)

    peer(server_name, config, context)


def run_client_emulation_thread(config):
    server_name = sys.argv[1]
    print(server_name)
    threading.Thread(None, client_emulation, None, [config]).start()


def client_emulation(config):
    # hack to wait for to server is up
    time.sleep(0.8)

    context = zeromq_context.context
    socket = context.socket(zmq.REQ)
    print(config)
    socket.connect("tcp://" + config['servers']['first'])
    for i in range(10):
        socket.send_pyobj(ClientUpdate([str(i)]))
        answer = socket.recv_pyobj()
        print(answer)
        print(server.state.log)


server = None


def peer(server_name, config, context):
    print(config, type(config))
    server_netloc = config['servers'][server_name]
    raft_server = RaftPeer(server_name, config, context)
    # hardcode test stuff
    global server
    server = raft_server
    if sys.argv[1] == 'first':
        run_client_emulation_thread(config)

    raft_server.run()



if __name__ == '__main__':
    run_peer()
