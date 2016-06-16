import eventlet
eventlet.monkey_patch()

import signal
import sys
import time

from oslo_log import log
from oslo_config import cfg
import oslo_messaging as messaging
from oslo_messaging.notify import notifier


opts = [
    cfg.StrOpt('notif_topic_name',
               help='Topic name for notifications',
               default='sometopic'),
    cfg.IntOpt('messages_to_send',
               help='A number of messages to send',
               default=1),
    cfg.BoolOpt('infinite_loop',
                help='Send messages in infinite loop',
                default=False),
    cfg.IntOpt('messages_per_second',
               help='A number of messages per second to send if'
                    'infinite run is enabled.',
               default=10),
]
CONF = cfg.CONF
CONF.register_cli_opts(opts)

log.register_options(CONF)
LOG = None

counter = 0

def ctrlchandler(sig, frame):
    LOG.info('Caught keyboard interrupt, finishing')
    LOG.info('Sent %s messages' % counter)
    sys.exit(0)

signal.signal(signal.SIGINT, ctrlchandler)


def main():
    global counter
    global LOG

    CONF(sys.argv[1:], project='load_generator')

    log.setup(CONF, 'load_generator')
    LOG = log.getLogger(__name__)

    transport = messaging.get_transport(cfg.CONF)
    notif = notifier.Notifier(transport,
                             'load_generator',
                             driver='messagingv2',
                             topic=CONF.notif_topic_name)

    if not CONF.infinite_loop:
        for counter in xrange(1, CONF.messages_to_send + 1):
            notif.info({}, '', 'Notification #%i' % counter)

        LOG.info('Sent %s messages' % counter)
    else:
        while True:
            start_time = int(time.time())

            for counter in xrange(counter + 1, counter + CONF.messages_per_second + 1):
                notif.info({}, '', 'Notification #%i' % counter)
            #counter += CONF.messages_per_second

            if start_time == int(time.time()):
                LOG.info('Sleeping for %s' % str(start_time + 1 - time.time()))
                time.sleep(start_time + 1 - time.time())
