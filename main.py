import logging
from way import Way
from order import Order
from currency import Currency
from orderbook import OrderBook
from instrument import Instrument
from staticdata import StaticData

logging.basicConfig(filename='Pytrading.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)


if 1:
    carrefourInstrument = Instrument(id=0, name='Carrefour', isin='FR0000120172', currencyId=0)
    orderbook = OrderBook(carrefourInstrument)

if 1:
    orderbook.on_new_order(Order(Way.SELL, carrefourInstrument, 50, 20.0, 'Trader4'))
    orderbook.on_new_order(Order(Way.SELL, carrefourInstrument, 50, 20.0, 'Trader5'))
    orderbook.on_new_order(Order(Way.SELL, carrefourInstrument, 50, 20.0, 'Trader2'))
    logger.info(orderbook)
    orderbook.on_new_order(Order(Way.BUY, carrefourInstrument, 50, 20.0, 'Trader1'))

if 1:
    orderbook.on_new_order(Order(Way.BUY, carrefourInstrument, 50, 21.0, 'Trader1'))
    orderbook.on_new_order(Order(Way.BUY, carrefourInstrument, 50, 20.0, 'Trader2'))
    orderbook.on_new_order(Order(Way.BUY, carrefourInstrument, 50, 19.0, 'Trader3'))
    orderbook.on_new_order(Order(Way.SELL, carrefourInstrument, 50, 22.0, 'Trader4'))
    orderbook.on_new_order(Order(Way.SELL, carrefourInstrument, 50, 23.0, 'Trader5'))
    orderbook.on_new_order(Order(Way.SELL, carrefourInstrument, 50, 24.0, 'Trader6'))

if 1:
    logger.info(orderbook)
