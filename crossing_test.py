import time
from decimal import Decimal

from depth_builder import sort_orderbook, CrossingBidAskException
from utils import mem_get_orderbook

if __name__ == "__main__":
    while True:
        orderbook = mem_get_orderbook()
        orderbook_sorted = sort_orderbook(orderbook)
        best_bid = Decimal(str(orderbook_sorted['bids'][0][0]))
        best_ask = Decimal(str(orderbook_sorted['asks'][0][0]))
        print(best_ask - best_bid, 'bid', best_bid, 'ask', best_ask)

        if best_ask - best_bid <= 0:
            print(f'Crossing bid and ask: best bid {best_bid} best ask {best_ask}')
            raise CrossingBidAskException(f'Crossing bid and ask: best bid {best_bid} best ask {best_ask}')

        time.sleep(0.2)
