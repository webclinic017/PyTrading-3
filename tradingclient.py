import logging
import socket
import pickle
from instrument import Instrument
from referential import Referential

class TradingClient:
    logger = logging.getLogger(__name__)
    referential = None
    orderBooks = None

    def __init__(self):
        pass

    """ public """
    def start(self):
        serverSocket = None

        try:
            serverSocket = socket.socket()
            host = socket.gethostname()
            port = 12345

            print('Connecting')
            serverSocket.connect((host, port))
            self.receive_referential(serverSocket)
            self.receive_order_books_full_snapshot(serverSocket)

        except KeyboardInterrupt:
            print('Stopped by user')
        except Exception, exception:
        # TODO: catch other exceptions
            print(exception)

        if serverSocket:
            serverSocket.close()

        print('Ok')

    """ private """
    def receive_referential(self, serverSocket):
        self.logger.debug('Receiving referential from [{}]'.format(serverSocket))
        buffer = serverSocket.recv(4096)
        self.referential = pickle.loads(buffer)

    """ private """
    def receive_order_books_full_snapshot(self, serverSocket):
        self.logger.debug('Receiving order books full snapshot from [{}]'.format(serverSocket))
        buffer = serverSocket.recv(4096)
        self.orderBooks = pickle.loads(buffer)
        print('Order books', self.orderBooks)

if __name__ == '__main__':
    logging.basicConfig(filename='TradingServer.log',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p')
    client = TradingClient()
    client.start()
