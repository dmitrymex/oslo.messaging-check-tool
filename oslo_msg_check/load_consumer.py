import eventlet
eventlet.monkey_patch()

import sys
import threading
import time

from oslo_log import log
from oslo_config import cfg
import oslo_messaging


CONF = cfg.CONF

log.register_options(CONF)
LOG = None


counter = 0


class NotificationEndpoint(object):
    filter_rule = oslo_messaging.NotificationFilter(
        publisher_id='load_generator')

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        global counter
        #LOG.info('Got message: %s' % str(payload))
        counter += 1


def main():
    global counter
    global LOG

    CONF(sys.argv[1:], project='load_consumer')

    log.setup(CONF, 'load_consumer')
    LOG = log.getLogger(__name__)

    transport = oslo_messaging.get_transport(cfg.CONF)

    targets = [
        oslo_messaging.Target(topic='sometopic'),
    ]

    endpoints = [
        NotificationEndpoint(),
    ]

    server = oslo_messaging.get_notification_listener(
        transport, targets, endpoints)

    threading.Thread(target=server.start).start()
    LOG.info('after threading')

    last_counter = -1
    while last_counter < counter:
        last_counter = counter
        time.sleep(1)

    print('Consumed %i messages' % counter)

    server.stop()
