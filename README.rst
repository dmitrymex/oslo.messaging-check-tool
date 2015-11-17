HOW TO USE
==========

First you should provide a config file for messaging driver. Sample config
for kombu driver could be found in oslo_msg_check.conf.sample in git repo.

Check applications
------------------

The check pair of applications allows you to run two processes and
then periodically check "RPC connectivity" between them.

To run them execute:

::
    oslo_msg_check_client --config-file oslo_msg_check.conf
    oslo_msg_check_server --config-file oslo_msg_check.conf

Now whenever you send GET request to port 5000, oslo_msg_check_client
will return 200 OK only it was able to send RPC request to
oslo_msg_check_server and received reply from it.

Load applications
-----------------

The load pair of applications allows to load messages into rabbitmq
and consume them. It uses oslo.messaging notification mechanism.

To put messages into RabbitMQ run

::
    oslo_msg_load_generator --config-file oslo_msg_check.conf --messages-to-send 1000

To read them, run

::
    oslo_msg_load_consumer --config-file oslo_msg_check.conf


HOW TO INSTALL
==============

Like a regular deb package

::
    sudo apt-get update
    sudo dpkg -i oslo.messaging-check-tool_1.0-1~u14.04+mos1_all.deb

If the command above fails, run

::
    sudo apt-get -f install


HOW TO BUILD
============

Get an Ubuntu 14.04 machine

::
    sudo apt-get update
    sudo apt-get install git dpkg-dev debhelper dh-systemd openstack-pkg-tools po-debconf python-all python-pbr python-setuptools python-sphinx python-babel python-eventlet python-flask python-oslo.config python-oslo.log python-oslo.messaging python-oslosphinx

Clone the project to it:

::
    git clone https://github.com/dmitrymex/oslo.messaging-check-tool.git
    cd oslo.messaging-check-tool

Add Fuel mirrors, for 8.0 do

::
    sudo tar -xzf aptsources.tgz -C /etc/apt/
    sudo apt-get update

Build the package

::
    DEB_BUILD_OPTIONS=nocheck dpkg-buildpackage -rfakeroot -us -uc

The built package could be found in the parent directory, like

::
    ../oslo.messaging-check-tool_1.0-1~u14.04+mos1_all.deb

