import redis as redis
import simplejson

PROJECT_PATH = '/home/artem/PycharmProjects/depthcache/'
PROJECT_FOLDER = PROJECT_PATH.split('/')[-2]
SUPERVISOR_PATH = '/etc/supervisor/conf.d/'


def get_preferences():
    ff = open(PROJECT_PATH + 'preferences.json', "r")
    preferences = simplejson.loads(ff.read())
    ff.close()
    return preferences


# MEM CACHE SERVER
MEMORY_CACHE = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
# MEM CACHE CONST
MEMORY_CACHE_LOG = 'memory_cache'
MEM_DEPTH_UPDATE = 'depth_update'
MEM_LAST_UPDATE_ID = 'last_update_id'
MEM_ORDERBOOK = 'orderbook'
MEM_FIRST_UPDATE_FLAG = 'first_update_flag'
MEM_TEST_LOG_PREFIX = 'test_log_prefix'

# Logging
LOG_PATH = PROJECT_PATH + 'log'
GENERAL_LOG = 'general'
TEST_LOG_LENGTH = 4000
