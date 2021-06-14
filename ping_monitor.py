#!/usr/bin/env python3

from boofuzz import BaseMonitor
import subprocess
import re


class PingMonitor(BaseMonitor):

    def __init__(self):

        self.output = []
        self.output_first = []

    def ping(self, host, count=50, delay=0):

        # hping3 -q --count 10 -i u0 --icmp www.mondragon.edu

        command = ['hping3',
                   '-q',
                   '--count', str(count),
                   '-i', 'u'+str(delay),
                   '--icmp',
                   host]
        try:
            output = subprocess.check_output(
                command, stderr=subprocess.STDOUT, universal_newlines=True)
        except subprocess.CalledProcessError:
            pass

        try:
            outputbyline = output.split('\n')
            for line in outputbyline:
                # does not work over entire output
                aux = re.search('^\d*\spackets.*', line)
                if aux is not None:
                    pt_pr = line
                # does not work over entire output
                aux = re.search('^round.*', line)
                if aux is not None:
                    rtt = line
            # aux = [pt, pr, rtt_min, rtt_avg, rtt_max]
            aux = []
            # packets transmitted
            aux.append(pt_pr.split(' ')[0])
            # packets received
            aux.append(pt_pr.split(' ')[3])
            # rtt min
            aux.append(rtt.split(' ')[3].split('/')[0])
            # rtt avg
            aux.append(rtt.split(' ')[3].split('/')[1])
            # rtt max
            aux.append(rtt.split(' ')[3].split('/')[2])
            return aux
        except NameError:
            pass

    def pre_send(self, target, fuzz_data_logger, session):

        print("PingMonitor: pre_send")
        host = target._target_connection.info.split(':')[0]
        if (session.mutant_index == 1):
            self.output_first = self.ping(host, count=100)
            self.output = self.output_first
            self.pl = int(self.output[0]) * \
                (int(self.output[0]) - int(self.output[1])) / 100
            self.pl_max = (100 - self.pl) / 2 + self.pl
        else:
            self.output = self.ping(host)
            # Packet loss - compare with double of first packet loss
            pl = int(self.output[0]) * \
                (int(self.output[0]) - int(self.output[1])) / 100
            if (pl > self.pl_max):
                print(str(pl) + "% packet loss")
            fuzz_data_logger.log_fail(
                "Ping monitor: packet loss=" + str(pl) + "%")
            # rtt max
            if (float(self.output[4]) > (float(self.output_first[4]) * 3)):
                print("rtt max")
                fuzz_data_logger.log_fail(
                    "Ping monitor: rtt max=" + self.output[4])

    def post_send(self, target, fuzz_data_logger, session):

        print("PingMonitor: post_send")
        host = target._target_connection.info.split(':')[0]
        self.output = self.ping(host, 100)
        # Packet loss - compare with double of first packet loss
        pl = int(self.output[0]) * \
            (int(self.output[0]) - int(self.output[1])) / 100
        if (pl > self.pl_max):
            print(str(pl) + "% packet loss")
            fuzz_data_logger.log_fail(
                "Ping monitor: packet loss=" + str(pl) + "%")
        # rtt max
        if (float(self.output[4]) > (float(self.output_first[4]) * 3)):
            print("rtt max")
            fuzz_data_logger.log_fail(
                "Ping monitor: rtt max=" + self.output[4])
        return True
