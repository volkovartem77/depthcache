import os
import time
import traceback
from datetime import datetime
from decimal import Decimal

import simplejson

from config import MEMORY_CACHE_LOG, MEMORY_CACHE, LOG_PATH, MEM_DEPTH_UPDATE, MEM_LAST_UPDATE_ID, MEM_ORDERBOOK, \
    MEM_FIRST_UPDATE_FLAG, MEM_TEST_LOG_PREFIX, TEST_LOG_LENGTH


class UtilsException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'Utils: %s' % self.message


def set_mem_cache(key, prefix, data):
    try:
        MEMORY_CACHE.set(f'{key}:{prefix}', simplejson.dumps(data))
    except TypeError:
        err_log(traceback.format_exc(), MEMORY_CACHE_LOG)


def get_mem_cache(key, prefix):
    try:
        data = MEMORY_CACHE.get(f'{key}:{prefix}')
        return simplejson.loads(data) if data is not None else None
    except TypeError:
        err_log(traceback.format_exc(), MEMORY_CACHE_LOG)


def delete_mem_cache(key, prefix):
    try:
        MEMORY_CACHE.delete(f'{key}:{prefix}')
    except TypeError:
        err_log(traceback.format_exc(), MEMORY_CACHE_LOG)


def get_mem_sub_keys(key):
    return list(MEMORY_CACHE.scan_iter(f"{key}:*"))


def delete_mem_sub_keys(key):
    for sub_key in MEMORY_CACHE.scan_iter(f"{key}:*"):
        MEMORY_CACHE.delete(sub_key)


def mem_set_depth_update(timestamp, depth_update: dict):
    set_mem_cache(MEM_DEPTH_UPDATE, str(timestamp), depth_update)


def mem_get_depth_update(timestamp):
    return get_mem_cache(MEM_DEPTH_UPDATE, str(timestamp))


def mem_remove_depth_update(timestamp):
    return delete_mem_cache(MEM_DEPTH_UPDATE, str(timestamp))


def mem_set_last_update_id(last_update_id):
    set_mem_cache(MEM_LAST_UPDATE_ID, '', last_update_id)


def mem_get_last_update_id():
    return get_mem_cache(MEM_LAST_UPDATE_ID, '')


def mem_set_orderbook(orderbook: dict):
    set_mem_cache(MEM_ORDERBOOK, '', orderbook)


def mem_get_orderbook():
    return get_mem_cache(MEM_ORDERBOOK, '')


def mem_set_first_update_flag(first_update_flag: bool):
    set_mem_cache(MEM_FIRST_UPDATE_FLAG, '', first_update_flag)


def mem_get_first_update_flag():
    return get_mem_cache(MEM_FIRST_UPDATE_FLAG, '')


def mem_set_test_log_prefix(test_log_prefix):
    set_mem_cache(MEM_TEST_LOG_PREFIX, '', test_log_prefix)


def mem_get_test_log_prefix():
    return get_mem_cache(MEM_TEST_LOG_PREFIX, '')


def datetime_str():
    return datetime.now().replace(microsecond=0).isoformat().replace('T', ' ')


def log(text, module, mark=''):
    os.makedirs(LOG_PATH, exist_ok=True)
    # print(text, module, mark, LOG_PATH)
    file = open('{}/{}.log'.format(LOG_PATH, module), "a")
    dt = datetime_str()
    file.write(dt + ' ' + mark + ' ' + text + '\n')
    file.close()
    print(dt + ' ' + mark + ' ' + text)


def err_log(text, module, mark=''):
    os.makedirs(LOG_PATH, exist_ok=True)
    file = open('{}/{}.err.log'.format(LOG_PATH, module), "a")
    dt = datetime_str()
    file.write(dt + ' ' + mark + text + '\n')
    file.close()
    print(dt + ' ' + mark + text)


def test_log(text, module):
    os.makedirs(LOG_PATH, exist_ok=True)
    prefix = mem_get_test_log_prefix()
    if prefix is None:
        mem_set_test_log_prefix(1)
        prefix = mem_get_test_log_prefix()

    file_path = '{}/{}.test{}.log'.format(LOG_PATH, module, prefix)

    if os.path.exists(file_path):
        file = open(file_path, "r")
        lines = file.readlines()
        if len(lines) > TEST_LOG_LENGTH:
            mem_set_test_log_prefix(prefix + 1)
            print('new file', prefix + 1)
        file.close()

    file = open('{}/{}.test{}.log'.format(LOG_PATH, module, prefix), "a")
    dt = datetime_str()
    file.write(dt + ' ' + text + '\n')
    file.close()
    # print(dt + ' ' + text)


def time_now_ms():
    return int(time.time() * 1000)


def time_now_ms_decimal():
    return Decimal(str(time.time() * 1000))
