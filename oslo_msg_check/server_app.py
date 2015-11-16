import eventlet
eventlet.monkey_patch()

import sys

from oslo_log import log
from oslo_config import cfg
import oslo_messaging as messaging


opts = [
    cfg.StrOpt('server_id',
               help='A string uniquely identifying current instance. Used'
                    'by server to distinguish instances.',
               default='server123'),
]
CONF = cfg.CONF
CONF.register_cli_opts(opts)

log.register_options(CONF)


LOG = None


class RpcEndpoint(object):
    def test_method(self, ctxt, a):
        LOG.info('Somebody is calling test_method')
        import time
        time.sleep(a)


def main():
    global LOG

    CONF(sys.argv[1:], project='test_rpc_server')

    log.setup(CONF, 'test_rpc_server')
    LOG = log.getLogger(__name__)

    LOG.info('Running test_rpc_server from main()')

    transport = messaging.get_transport(cfg.CONF)
    target = messaging.Target(topic='test_rpc', version='1.0',
                              server=CONF.server_id)
    server = messaging.get_rpc_server(transport, target,
                                      endpoints=[RpcEndpoint()],
                                      executor='eventlet')

    server.start()
    server.wait()