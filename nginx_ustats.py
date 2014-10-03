import urllib
import json

import collectd

PLUGIN_NAME = 'nginx_ustats'

def logger(severity, msg):
    log = getattr(collectd, severity)
    log('{}: {}'.format(PLUGIN_NAME, msg))


def fetch_data():
    """Fetch statistics from nginx ustats module"""
    try:
        sock = urllib.urlopen(NGINX_USTATS_URL)
    except IOError, e:
        logger('info', 'Failed to open "%s".' % NGINX_USTATS_URL)
        if hasattr(e, 'code'):
            logger('info', 'Error code: %s.' % e.code)
        elif hasattr(e, 'reason'):
            logger('info', 'Reason: %s.' % e.reason)
        logger('info', repr(e))
    else:
        ustats = json.loads(sock.read())    # dict with backend:[stats]
        sock.close()
        return parse_data(ustats)


def parse_data(ustats=None):
    """Parse ustats data format"""
    stats_dict = {
        #0: 'backend',
        #1: 'disabled',
        #2: 'blacklisted',
        3: 'requests',
        4: 'request_rate',
        5: 'request_time_ms',
        6: 'http_499',
        7: 'http_5XX',
        8: 'http_500',
        9: 'http_503',
        10: 'tcp_errors',
        11: 'http_read_timeouts',
        12: 'http_write_timeouts',
        13: 'fails_timeout', # (s)
        14: 'fails_max',
        #15: 'fails_start',
        #16: 'fails_last',
        17: 'fails_total',
    }

    data = {}
    # dict keys are upstream server names
    for ustream in ustats.keys():
        data[ustream] = {}
        # list elements are backends, last element is 'implicit' flag
        for backend in ustats[ustream][:-1]:
            data[ustream][backend[0]] = {}
            for i in stats_dict:
                data[ustream][backend[0]][stats_dict[i]] = backend[i]
    return data


def read_callback():
    data = fetch_data()
    for upstream in data:
        for backend in data[upstream]:
            for stat in data[upstream][backend]:
                dispatch_value(
                    data[upstream][backend][stat],
                    PLUGIN_NAME,
                    stat,
                    plugin_instance=upstream,
                    type_instance=backend,
                    )


def configure_callback(conf):
    """Receive configuration block"""
    global NGINX_USTATS_URL
    for node in conf.children:
        if node.key == 'NginxUstatsURL':
            NGINX_USTATS_URL = node.values[0]
        else:
            logger('error', 'Unknown config key: {}.'.format(node.key))
    logger('info', 'Configured with URL {}'.format(NGINX_USTATS_URL))


def dispatch_value(value, plugin, type, plugin_instance=None, type_instance=None):
    """Read a key from info response data and dispatch a value"""
    full_type = type if not type_instance else '{}-{}'.format(type, type_instance)
    logger('debug', 'Sending value: %s=%s' % (full_type, value))
    val = collectd.Values(plugin=plugin)
    if plugin_instance:
        val.plugin_instance = plugin_instance
    val.type = type
    if type_instance:
        val.type_instance = type_instance
    val.values = [value]
    val.dispatch()


collectd.register_config(configure_callback)
collectd.register_read(read_callback)
