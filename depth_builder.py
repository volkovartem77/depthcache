import time
from decimal import Decimal
from operator import itemgetter

import requests
import simplejson

from config import MEM_DEPTH_UPDATE, GENERAL_LOG
from utils import get_mem_sub_keys, mem_get_depth_update, mem_remove_depth_update, log, mem_get_last_update_id, \
    mem_set_last_update_id, mem_set_orderbook, time_now_ms_decimal, mem_get_orderbook, mem_set_first_update_flag, \
    mem_get_first_update_flag, test_log, mem_set_test_log_prefix


class WrongUpdateException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'DepthBuilder: %s' % self.message


class WrongFirstUpdateException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'DepthBuilder: %s' % self.message


class CrossingBidAskException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'DepthBuilder: %s' % self.message


def get_depth_snapshot():
    res = requests.get(f"https://api.binance.com/api/v3/depth?symbol={SYMBOL}&limit={LIMIT}")
    if res and res.status_code == 200:
        return simplejson.loads(res.text)


def fetch_the_oldest_update():
    all_keys = get_mem_sub_keys(MEM_DEPTH_UPDATE)
    if all_keys:
        the_oldest_key = str(sorted(all_keys, key=lambda key: Decimal(key.split(':')[1]))[0])
        timestamp = the_oldest_key.split(':')[1]
        return the_oldest_key, timestamp, mem_get_depth_update(timestamp)


def save_orderbook(bids: dict, asks: dict):
    timestamp = time_now_ms_decimal()
    mem_set_orderbook({
        "bids": bids,
        "asks": asks,
        "timestamp": timestamp
    })


def apply_update(update):
    orderbook = mem_get_orderbook()

    for bid in update['b']:
        orderbook['bids'][bid[0]] = bid[1]
        if bid[1] == "0.00000000":
            del orderbook['bids'][bid[0]]

    for ask in update['a']:
        orderbook['asks'][ask[0]] = ask[1]
        if ask[1] == "0.00000000":
            del orderbook['asks'][ask[0]]

    save_orderbook(orderbook['bids'], orderbook['asks'])


def update_depth(update):
    last_update_id = mem_get_last_update_id()
    first_update_flag = mem_get_first_update_flag()

    if update['u'] <= last_update_id:
        return

    if first_update_flag:
        if update['U'] <= last_update_id + 1 <= update['u']:
            apply_update(update)
            mem_set_last_update_id(update['u'])
            mem_set_first_update_flag(False)
        else:
            raise WrongFirstUpdateException(f"The first update is wrong {update}")
    else:
        if update['U'] == last_update_id + 1:
            apply_update(update)
            mem_set_last_update_id(update['u'])
        else:
            raise WrongUpdateException(f"Got wrong update {update}")


def load_initial_snapshot():
    depth_snapshot = get_depth_snapshot()
    test_log(f'initial_snapshot {depth_snapshot}', GENERAL_LOG)
    mem_set_last_update_id(depth_snapshot['lastUpdateId'])
    save_orderbook(dict((price, amount) for price, amount in depth_snapshot['bids']),
                   dict((price, amount) for price, amount in depth_snapshot['asks']))
    mem_set_first_update_flag(True)
    log(f'Initial snapshot {mem_get_last_update_id()}', GENERAL_LOG, 'INFO')


def sort_orderbook(orderbook: dict):
    """Sort bids and asks by price"""
    bids = [[float(price), float(quantity)] for price, quantity in orderbook['bids'].items()]
    bids = sorted(bids, key=itemgetter(0), reverse=True)
    asks = [[float(price), float(quantity)] for price, quantity in orderbook['asks'].items()]
    asks = sorted(asks, key=itemgetter(0), reverse=False)
    return {"bids": bids, "asks": asks}


def run_builder():
    load_initial_snapshot()

    while True:
        the_oldest_update = fetch_the_oldest_update()
        if the_oldest_update:
            test_log(f'the_oldest_update {the_oldest_update}', GENERAL_LOG)
            key, timestamp, update = the_oldest_update
            mem_remove_depth_update(timestamp)

            try:
                update_depth(update)
            except WrongFirstUpdateException:
                log(f'WrongFirstUpdateException', GENERAL_LOG, 'ERROR')
                load_initial_snapshot()
            except WrongUpdateException:
                log(f'WrongUpdateException', GENERAL_LOG, 'ERROR')
                load_initial_snapshot()

            orderbook = mem_get_orderbook()
            orderbook_sorted = sort_orderbook(orderbook)
            best_bid = Decimal(str(orderbook_sorted['bids'][0][0]))
            best_ask = Decimal(str(orderbook_sorted['asks'][0][0]))
            print(best_ask - best_bid, 'bid', best_bid, 'ask', best_ask)

            if best_ask - best_bid <= 0:
                log(f'Crossing bid and ask: best bid {best_bid} best ask {best_ask}', GENERAL_LOG, 'ERROR')
                raise CrossingBidAskException(f'Crossing bid and ask: best bid {best_bid} best ask {best_ask}')

        time.sleep(.1)


if __name__ == "__main__":
    try:
        SYMBOL = "BTCUSDT"
        LIMIT = 5000
        mem_set_test_log_prefix(1)
        run_builder()
    except KeyboardInterrupt:
        exit()
