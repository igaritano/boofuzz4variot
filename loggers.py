#!/usr/bin/env python3

from boofuzz import *
from datetime import datetime, timezone


def open_logger():

    filename = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    log_file = open('boofuzz-results/logfile-'+filename+'.txt', 'w')
    text_logger = FuzzLoggerText(file_handle=log_file)

    return [log_file, text_logger]


def close_logger(log_file):

    log_file.close()
