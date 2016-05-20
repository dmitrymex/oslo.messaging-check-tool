import eventlet
eventlet.monkey_patch()

import sys
import threading

import flask
from flask import request
from oslo_log import log
from oslo_config import cfg
import oslo_messaging as messaging


opts = [
    cfg.StrOpt('listen_port',
               help='Client app will listen for HTTP requests on that port',
               default=5000),
    cfg.StrOpt('topic',
               help='Topic name.',
               default='test_rpc'),
    cfg.StrOpt('server_id',
               help='A string uniquely identifying target instance.',
               default='server123'),
]

CONF = cfg.CONF
CONF.register_cli_opts(opts)

log.register_options(CONF)
LOG = None


req_counter = 0
req_counter_lock = threading.Lock()

rpc_client = None


app = flask.Flask(__name__)

@app.route('/')
def hello_world():
    global req_counter

    with req_counter_lock:
        request_id = req_counter
        req_counter += 1

    timeout = int(request.args.get('timeout', 60))
    delay = int(request.args.get('delay', 0))
    rpc_client.test_method(request_id, timeout, delay)
    return ''


class RpcClient(object):
    def __init__(self, transport):
        target = messaging.Target(topic=CONF.topic, version='1.0',
                                  server=CONF.server_id)
        self._client = messaging.RPCClient(transport, target)

    def test_method(self, request_id, timeout, delay):
        LOG.info('[request id: %i] Calling test_method' % request_id)
        self._client.prepare(timeout=timeout).call(
            {}, 'test_method', delay=delay)
        LOG.info('[request id: %i] Server responded on our call' % request_id)


def main():
    global rpc_client
    global LOG

    CONF(sys.argv[1:], project='test_rpc_server')

    log.setup(CONF, 'test_rpc_server')
    LOG = log.getLogger(__name__)

    transport = messaging.get_transport(cfg.CONF)
    rpc_client = RpcClient(transport)

    app.run(host='0.0.0.0', port=CONF.listen_port, threaded=True)
