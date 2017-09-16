import errno
import select
import socket
import logging
import traceback
from abc import ABCMeta, abstractmethod


class ClosedConnection(BaseException):
    """ Client socket connection has been closed """


class TcpServer:
    __metaclass__ = ABCMeta

    def __init__(self, port):
        self.logger = logging.getLogger(__name__)
        self.port = port
        self.select_timeout = 0.5
        self.listener = None
        self.inputs = []
        self.outputs = []
        self.message_stacks = {}
        self.r = None
        self.w = None

    @staticmethod
    def close_sockets(socket_container):
        for sock in socket_container:
            if sock:
                sock.close()

    def cleanup(self):
        self.listener.close()
        TcpServer.close_sockets(self.inputs)
        TcpServer.close_sockets(self.outputs)

    def remove_client_socket(self, sock):
        print('Removing client [{}]'.format(sock.getpeername()))
        if sock in self.outputs:
            self.outputs.remove(sock)
        if sock in self.inputs:
            self.inputs.remove(sock)
        sock.close()
        if sock in self.message_stacks:
            del self.message_stacks[sock]
        if sock in self.r:
            self.r.remove(sock)
        if sock in self.w:
            self.w.remove(sock)

    def accept_connection(self):
        sock, _ = self.listener.accept()
        sock.setblocking(0)
        self.inputs.append(sock)
        self.outputs.append(sock)
        self.on_accept_connection(sock)

    @abstractmethod
    def on_accept_connection(self, sock):
        pass

    @abstractmethod
    def handle_readable_client(self, sock):
        pass

    def process_sockets(self):
        self.r, self.w, _ = select.select(self.inputs, self.outputs, self.inputs, self.select_timeout)

        for sock in self.r:
            if sock is self.listener:
                self.accept_connection()
            else:
                self.handle_generic(self.handle_readable_client, sock)

        for sock in self.w:
            self.handle_generic(self.handle_writable, sock)

    def handle_generic(self, handler, sock):
        try:
            handler(sock)
            return
        except KeyboardInterrupt:
            raise
        except KeyError:
            pass
        except socket.error as exception:
            if exception.errno not in (errno.ECONNRESET, errno.ENOTCONN):
                print('Client connection lost, unhandled errno [{}]'.format(exception.errno))
                print(traceback.print_exc())
        except Exception as exception:
            print('handle_generic: {}'.format(exception))
            print(traceback.print_exc())

        self.remove_client_socket(sock)

    def handle_writable(self, sock):
        # sent_messages = 0
        while len(self.message_stacks[sock]) > 0:
            next_message = self.message_stacks[sock].pop(0)
            sock.send(next_message)
            # sent_messages += 1
            # print('DEBUG {}'.format(next_message))
        # print('[{}] messages were sent to [{}]'.format(sent_messages, sock.getpeername()))

    def listen(self):
        self.listener = socket.socket()
        self.listener.setblocking(0)
        host = socket.gethostname()
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind((host, self.port))
        self.listener.listen(5)
        self.inputs.append(self.listener)

