import eventlet
eventlet.monkey_patch()

import signal
import sys
import threading
import time

from oslo_log import log
from oslo_config import cfg
import oslo_messaging


CONF = cfg.CONF

opts = [
    cfg.StrOpt('notif_topic_name',
               help='Topic name for notifications',
               default='sometopic'),
    cfg.BoolOpt('infinite_loop',
                help='',
                default=False)
]
CONF.register_cli_opts(opts)


log.register_options(CONF)
LOG = None


counter = 0
infinite_loop = False


def ctrlchandler(sig, frame):
    global infinite_loop

    LOG.info('Caught keyboard interrupt, finishing')
    infinite_loop = False

signal.signal(signal.SIGINT, ctrlchandler)


class NotificationEndpoint(object):
    filter_rule = oslo_messaging.NotificationFilter(
        publisher_id='load_generator')

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        global counter
        #LOG.info('Got message: %s' % str(payload))
        counter += 1


def main():
    global counter
    global infinite_loop
    global LOG

    CONF(sys.argv[1:], project='load_consumer')

    log.setup(CONF, 'load_consumer')
    LOG = log.getLogger(__name__)

    transport = oslo_messaging.get_transport(cfg.CONF)

    targets = [
        oslo_messaging.Target(topic=CONF.notif_topic_name),
    ]

    endpoints = [
        NotificationEndpoint(),
    ]

    server = oslo_messaging.get_notification_listener(
        transport, targets, endpoints)

    threading.Thread(target=server.start).start()
    #LOG.info('after threading')

    infinite_loop = CONF.infinite_loop

    last_counter = -1
    try:
        while last_counter < counter or infinite_loop:
            last_counter = counter
            time.sleep(1)
    except OSError:
        # That is how keyboard interrupt appears here
        pass

    server.stop()
    server.wait()

    print('Consumed %i messages' % counter)