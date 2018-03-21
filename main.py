# -*- coding: utf-8 -*-
import zmq
# print(zmq.pyzmq_version())
import yaml
import time
import sys

import client_thread
import threading

context = zmq.Context()
socket = context.socket(zmq.REP)
server_name = sys.argv[1]
print(server_name)
threading.Thread(None, client_thread.client, None, [server_name]).start()

with open(server_name + ".yaml", 'r') as stream:
    config = yaml.load(stream)

socket.bind("tcp://*:" + str(config['listen']))

while True:
    #  Wait for next request from client
    message = socket.recv()
    print("Received request: %s" % message)

    #  Do some 'work'
    time.sleep(1)

    #  Send reply back to client
    socket.send(b"i am " + server_name.encode())
