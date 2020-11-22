import time

import simplejson
import websocket

from config import MEM_DEPTH_UPDATE
from utils import log, time_now_ms_decimal, mem_set_depth_update, delete_mem_sub_keys, test_log


def on_message(ws, message):
    # print(message)

    message = simplejson.loads(message)
    if 'e' in message and message['e'] == 'depthUpdate':
        mem_set_depth_update(time_now_ms_decimal(), message)
        # test_log(f'Depth update {time_now_ms_decimal()} {message}', log_file_name)
        # print('Depth update', message)


def on_error(ws, error):
    log(f'websocket: {error}', log_file_name)


def on_close(ws):
    log(f'websocket: closed', log_file_name)


def on_open(ws):
    log(f'websocket: launched', log_file_name)
    log(f'websocket: subscribe to stream {stream}', log_file_name)


def run():
    while True:
        ws = websocket.WebSocketApp(
            f"wss://stream.binance.com:9443/ws/{stream}",
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close)

        ws.run_forever()

        log(f'websocket: restart', log_file_name)
        time.sleep(1)


if __name__ == "__main__":
    try:
        SYMBOL = "BTCUSDT"
        stream = f'{SYMBOL.lower()}@depth'
        log_file_name = "websocket"
        delete_mem_sub_keys(MEM_DEPTH_UPDATE)

        run()

    except KeyboardInterrupt:
        exit()
