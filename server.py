"""
This script demonstrates simple server structures based on simple loop, select, selector and twisted
####requires python 3.6 or newer######
"""
import sys, time
from select import select
from socket import socket
import selectors
import subprocess
import sched
import multiprocessing
import client
sockobj = socket()
sel = selectors.DefaultSelector()
"""###############################
base echo server based on event loop
################################"""


class baseserver:
    def __init__(self, myhost='localhost', myport=1234, listen=5):
        self.myhost = myhost
        self.myport = myport
        self.listen = listen
        self.sockobj = socket()
        self.sockobj.bind((self.myhost, self.myport))
        self.sockobj.listen(self.listen)

    def run(self):
        while True:  # listen until process killed
            conn, address = self.sockobj.accept()  # wait for next client connect
            print('Server connected by', address)  # connection is a new socket
            datalist = []
            while True:
                data = conn.recv(4096)  # read next line on client socket
                datalist.append(data)
                if not data:
                    break  # send a reply line to the client
                print(f'got from {conn}: ' + (b''.join(datalist).decode()))  # transfer bytelist to unicode
                conn.send(b'Echo=>' + b''.join(datalist))  # until eof when socket closed
            conn.close()


"""####################
echo server based on select
#######################"""


class selectserver():
    def __init__(self, myhost='localhost', myport=1234, numportsocks=1, listen=5):
        self.myhost = myhost
        self.myport = myport
        self.listen = listen
        self.numportsocks = numportsocks
        self.mainsocks, self.readsocks, self.writesocks = [], [], []
        if len(sys.argv) == 3:  # in case the script is run in cmd or powershell
            self.myhost, self.myport = sys.argv[1:]

    def now(self):
        return time.ctime(time.time())

    def makeportsock(self):  # making socket object
        for i in range(self.numportsocks):
            portsock = socket()
            portsock.bind((self.myhost, self.myport))
            portsock.listen(5)
            self.mainsocks.append(portsock)  # support numerous port
            self.readsocks.append(portsock)
            self.myport += 1

    def run(self):  # start server with selectserver().start()
        self.makeportsock()
        print('selectserver start looping')
        while True:
            readables, writeables, exceptions = select(self.readsocks, self.writesocks, [])
            for sockobj in readables:
                if sockobj in self.mainsocks:  # for ready input sockets
                    conn, address = sockobj.accept()  # port socket: accept new client
                    print('Connect:', address, id(conn))
                    self.readsocks.append(conn)
                else:
                    data = sockobj.recv(4096)
                    if data:
                        print(f'got from {conn} ' + data.decode())
                        sockobj.send(b'Echo=>' + data)
                    else:
                        sockobj.close()
                        self.readsocks.remove(sockobj)


"""#######################
selector based echo server
#########################"""


class selectorserver:
    def __init__(self, myhost='localhost', myport=1234, listen=5):
        self.myhost = myhost
        self.myport = myport
        self.listen = listen
        if len(sys.argv) == 3:  # in case the script is run in cmd or powershell
            self.myhost, self.myport = sys.argv[1:]

    def accept(self, sock):
        conn, addr = sock.accept()
        conn.setblocking(False)
        sel.register(conn, selectors.EVENT_READ, self.read)

    def read(self, conn):
        data = conn.recv(4096)
        if data:
            print(f'got from {conn} ' + data.decode())
            conn.send(data)
        else:
            sel.unregister(conn)
            conn.close()

    def makeselector(self):
        sockobj.bind((self.myhost, self.myport))
        sockobj.listen(self.listen)
        sockobj.setblocking(False)
        sel.register(sockobj, selectors.EVENT_READ, self.accept)

    def run(self):  # start server with selectorserver().start()
        self.makeselector()
        print('selectorserver start looping')
        while True:
            events = sel.select()
            for key, event in events:
                callback = key.data  # sockobj jump  to ->->-> self.accept
                callback(key.fileobj)  # conn jump  to ->->-> self.read



"""#######################
twisted based echo server
#########################"""

from twisted.internet import protocol, reactor, endpoints

class Echo(protocol.Protocol):
    def dataReceived(self, data):
        self.transport.write(data)

class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()

endpoints.serverFromString(reactor, "tcp:1234").listen(EchoFactory())
reactor.run()


# test code
if __name__ == '__main__':
    # s = baseserver()
    # s = selectserver()
	# s = reactor
    s = selectorserver()
    startserver = multiprocessing.Process(target=s.run)
    #time.sleep(5)
    startclient = multiprocessing.Process(target=client().run)
    startserver.start()
    startclient.start()

#scheduleobj = sched.scheduler()
#scheduleobj.enter(2,1,subprocess.run,(r'python C:\Users\wxhoh\Desktop\practise\tools\client.py',))
#scheduleobj.enter(0,1,s.start)
#scheduleobj.run(blocking=False)
