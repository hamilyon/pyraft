import yaml
import zmq
context = zmq.Context()

with open("servers.yaml", 'r') as stream:
    config = yaml.load(stream)


def client(server_name):
    for name in config['servers']:
        server = config['servers'][name]
        if name != server_name:
            print("Connecting to "+ name +" server …")
            socket = context.socket(zmq.REQ)
            socket.connect("tcp://" + server)

            #  Do 10 requests, waiting each time for a response
            for request in range(10):
                print("Sending request %s …" + "i am " + server_name)
                socket.send(b"i am " + server_name.encode())

                #  Get the reply.
                message = socket.recv()
                print("Received reply %s [ %s ]" % (request, message))
