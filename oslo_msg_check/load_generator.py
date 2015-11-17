import eventlet
eventlet.monkey_patch()

import sys

from oslo_log import log
from oslo_config import cfg
import oslo_messaging as messaging
from oslo_messaging.notify import notifier


opts = [
    cfg.IntOpt('messages-to-send',
               help='A number of messages to send',
               default=1),
]
CONF = cfg.CONF
CONF.register_cli_opts(opts)

log.register_options(CONF)
LOG = None


def main():
    global LOG

    CONF(sys.argv[1:], project='load_generator')

    log.setup(CONF, 'load_generator')
    LOG = log.getLogger(__name__)

    transport = messaging.get_transport(cfg.CONF)
    notif = notifier.Notifier(transport,
                             'load_generator',
                             driver='messagingv2',
                             topic='sometopic')

    for i in xrange(CONF.messages_to_send):
        notif.info({}, '', 'Notification #%i' %i)
