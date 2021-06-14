#!/usr/bin/env python3

def pre_send1(target, fuzz_data_logger, session, sock):

    print("Session: pre_send1")
    print("Test case: " + str(session.mutant_index))


def pre_send2(target, fuzz_data_logger, session, sock):

    print("Session: pre_send2")


def post_test1(target, fuzz_data_logger, session, sock):

    print("Session: post_test1")
    response = target.recv(10000)
    if ("HTTP/1.1 400 Bad Request\r\n" in response.decode("utf-8")):
        fuzz_data_logger.log_pass('Everything ok')
    else:
        fuzz_data_logger.log_fail(str(response))
