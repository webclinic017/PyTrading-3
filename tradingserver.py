import logging
import socket
import select
import struct
from staticdata import StaticData
from referential import Referential
from instrument import Instrument
from currency import Currency
from orderbook import OrderBook
from serialization import Serialization

class TradingServer:
    logger = logging.getLogger(__name__)
    referential = None
    orderBooks = None
    inputs = None
    outputs = None
    listener = None
    messageStacks = None

    def __init__(self):
        self.initialize_referential()
        self.initialize_order_books()
        self.inputs = []
        self.outputs = []
        self.messageStacks = {}

    """ public """
    def start(self):
        try:
            self.listener = socket.socket()
            self.listener.setblocking(0)
            host = socket.gethostname()
            port = 12345
            self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listener.bind((host, port))

            print('Listening')
            self.listener.listen(5)
            self.inputs.append(self.listener)

            while self.inputs:
                readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs, 1)
                self.handle_readable(readable)
                self.handle_writable(writable)
                self.handle_exceptional(exceptional)

        except KeyboardInterrupt, exception:
            print('Stopped by user')
        except Exception, exception:
            print(exception)

        if self.listener:
            self.listener.close()

        print('Ok')

    """ private """
    def initialize_referential(self):
        self.logger.debug('Loading referential')
        self.referential = StaticData.get_default_referential()
        self.logger.debug('Referential is loaded')

    """ private """
    def initialize_order_books(self):
        self.logger.debug('Initializing order books')
        self.orderBooks = {}
        # TODO: use generator
        for instrument in self.referential.instruments:
            self.orderBooks[instrument.id] = OrderBook(instrument)
        self.logger.debug('[{}] order books are initialized'.format(len(self.referential)))

    """ private """
    def handle_readable(self, readable):
        for s in readable:
            if s is self.listener:
                connection, client_address = self.listener.accept()
                print('Got connection from', client_address)
                connection.setblocking(0)
                self.inputs.append(connection)

                messageStack = []
                referentialMessage = Serialization.encode_referential(self.referential)
                referentialBytes = referentialMessage.to_bytes()
                message = struct.pack('>Q', len(referentialBytes)) + referentialBytes
                messageStack.append(message)

                orderBookFullSnapshotMessage = Serialization.encode_orderbookfullsnapshot(self.orderBooks[0])
                orderBookFullSnapshotBytes = orderBookFullSnapshotMessage.to_bytes()
                message = struct.pack('>Q', len(orderBookFullSnapshotBytes)) + orderBookFullSnapshotBytes
                messageStack.append(message)

                self.messageStacks[connection] = messageStack

                # Adding client socket to write list
                self.outputs.append(connection)

            else:
                removeSocket = True
                try:
                    data = s.recv(4096)
                    if data:
                        removeSocket = False
                except KeyboardInterrupt:
                    raise
                except:
                    pass

                if removeSocket:
                    print('Client closed its socket')
                    if s in self.outputs:
                        self.outputs.remove(s)
                    self.inputs.remove(s)
                    s.close()
                    del self.messageStacks[s]

    """ private """
    def handle_writable(self, writable):
        for s in writable:
            try:
                next_msg = self.messageStacks[s].pop(0)
                print('Message stack length:', len(self.messageStacks[s]))
            except Exception, exception:
                if s in self.outputs:
                    self.outputs.remove(s)
            else:
                s.send(next_msg)

    """ private """
    def handle_exceptional(self, exceptional):
        for s in exceptional:
            self.inputs.remove(s)
            if s in self.outputs:
                self.outputs.remove(s)
            s.close()
            del self.messageStacks[s]

if __name__ == '__main__':
    logging.basicConfig(filename='TradingServer.log',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p')
    server = TradingServer()
    server.start()
