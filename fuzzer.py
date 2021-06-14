#!/usr/bin/env python3

from boofuzz import TCPSocketConnection, Target, Session
from datamodel import request
from ping_monitor import PingMonitor
from tcp_monitor import TCPMonitor
from callbacks import pre_send1, post_test1
from loggers import open_logger, close_logger


def main():

    # host = "172.16.1.1"
    host = "www.mondragon.edu"
    host = "www.google.com"
    port = 80

    connection = TCPSocketConnection(host=host, port=port)

    pingmonitor = PingMonitor()
    tcpmonitor = TCPMonitor()

    target = Target(connection=connection,
                    monitors=[pingmonitor, tcpmonitor],
                    max_recv_bytes=100000)

    pre_send_callbacks = [pre_send1]

    post_test_case_callbacks = [post_test1]

    [log_file, text_logger] = open_logger()

    fuzz_loggers = [text_logger]

    session = Session(target=target,
                      pre_send_callbacks=pre_send_callbacks,
                      post_test_case_callbacks=post_test_case_callbacks,
                      fuzz_loggers=fuzz_loggers)

    session.connect(request)

    session.fuzz()
    # session.fuzz_single_case(1)

    close_logger(log_file)


if __name__ == "__main__":
    main()
