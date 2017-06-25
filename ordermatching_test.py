import unittest
from way import Way
from order import Order
from orderbook import OrderBook
from instrument import Instrument


class TestOrderMatching(unittest.TestCase):
    book = None
    instrument = None

    def setUp(self):
        self.instrument = Instrument(identifier=0, name='Carrefour', isin='FR0000120172', currency_identifier=0)
        self.book = OrderBook(self.instrument)

    def validate_one_matching(self, attackingOrder, attackedOrder):
        self.book.on_new_order(attackedOrder)
        matching = self.book.get_matching_orders(attackingOrder)
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0], attackedOrder)

    def test_buy_price_greater_than_sell(self):
        attackingOrder = Order(Way.BUY, self.instrument, 10, 40.0, 'Trader1')
        attackedOrder = Order(Way.SELL, self.instrument, 10, 38.0, 'Trader2')
        self.validate_one_matching(attackingOrder, attackedOrder)

    def test_buy_price_equal_to_sell(self):
        attackingOrder = Order(Way.BUY, self.instrument, 10, 40.0, 'Trader1')
        attackedOrder = Order(Way.SELL, self.instrument, 10, 40.0, 'Trader2')
        self.validate_one_matching(attackingOrder, attackedOrder)

    def test_sell_price_greater_than_buy(self):
        attackingOrder = Order(Way.SELL, self.instrument, 10, 40.0, 'Trader1')
        attackedOrder = Order(Way.BUY, self.instrument, 10, 42.0, 'Trader2')
        self.validate_one_matching(attackingOrder, attackedOrder)

    def test_sell_price_equal_to_buy(self):
        attackingOrder = Order(Way.SELL, self.instrument, 10, 40.0, 'Trader1')
        attackedOrder = Order(Way.BUY, self.instrument, 10, 40.0, 'Trader2')
        self.validate_one_matching(attackingOrder, attackedOrder)

    def test_one_full_execution(self):
        quantity = 10
        price = 42.0
        attackingOrder = Order(Way.SELL, self.instrument, quantity, price, 'Trader1')
        attackedOrder = Order(Way.BUY, self.instrument, quantity, price, 'Trader2')
        self.book.on_new_order(attackedOrder)
        self.book.on_new_order(attackingOrder)
        self.assertEqual(self.book.count_bids(), 0)
        self.assertEqual(self.book.count_asks(), 0)
        self.assertEqual(attackingOrder.executed_quantity, quantity)
        self.assertEqual(attackedOrder.executed_quantity, quantity)
        self.assertEqual(attackingOrder.get_remaining_quantity(), 0)
        self.assertEqual(attackedOrder.get_remaining_quantity(), 0)

    def test_one_partial_execution(self):
        attackingQuantity = 20
        attackedQuantity = 10
        price = 42.0
        attackingOrder = Order(Way.BUY, self.instrument, attackingQuantity, price, 'Trader1')
        attackedOrder = Order(Way.SELL, self.instrument, attackedQuantity, price, 'Trader2')
        self.book.on_new_order(attackedOrder)
        self.book.on_new_order(attackingOrder)
        self.assertEqual(self.book.count_bids(), 1)
        self.assertEqual(self.book.count_asks(), 0)
        self.assertEqual(attackingOrder.executed_quantity, attackingQuantity - attackedQuantity)
        self.assertEqual(attackedOrder.executed_quantity, attackedQuantity)
        self.assertEqual(attackingOrder.get_remaining_quantity(), attackingQuantity - attackedQuantity)
        self.assertEqual(attackedOrder.get_remaining_quantity(), 0)

    def test_multiple_partial_executions(self):
        attackingQuantity = 50
        attackedQuantity = 10
        price = 42.0
        attackingOrder = Order(Way.BUY, self.instrument, attackingQuantity, price, 'Trader1')
        attackedOrders = []
        for _ in list(range(5)):
            attackedOrder = Order(Way.SELL, self.instrument, attackedQuantity, price, 'Trader2')
            attackedOrders.append(attackedOrder)
            self.book.on_new_order(attackedOrder)
        self.book.on_new_order(attackingOrder)
        self.assertEqual(self.book.count_bids(), 0)
        self.assertEqual(self.book.count_asks(), 0)
        self.assertEqual(attackingOrder.executed_quantity, attackingQuantity)
        self.assertEqual(attackingOrder.get_remaining_quantity(), 0)
        for attackedOrder in attackedOrders:
            self.assertEqual(attackedOrder.executedquantity, attackedQuantity)
            self.assertEqual(attackedOrder.get_remaining_quantity(), 0)

if __name__ == '__main__':
    unittest.main()
