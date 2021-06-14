#!/usr/bin/env python3

from boofuzz import BaseMonitor
import subprocess
import re


class TCPMonitor(BaseMonitor):

    def __init__(self):

        self.output = []
        self.output_first = []

    def tcpsyn(self, host, port=80, count=10, delay=0):

        # hping3 -q --count 10 -i u0 --syn -p 80 --tcp-recv-pkts \
        #     --tcp-recv-flags www.mondragon.edu

        command = ['hping3',
                   '-q',
                   '--count', str(count),
                   '-i', 'u'+str(delay),
                   '--syn',
                   '-p', str(port),
                   '--tcp-recv-pkts',
                   '--tcp-recv-flags', 'S,A',
                   host]
        try:
            output = subprocess.check_output(
                command, stderr=subprocess.STDOUT, universal_newlines=True)
        except subprocess.CalledProcessError:
            pass

        try:
            pt_pr = re.search("\d*\spackets.*\n", output)
            rtt = re.search("round-trip.*\n", output)
            outputbyline = output.split('\n')
            for line in outputbyline:
                # does not work over entire output
                aux = re.search('^[\*\.]{1}[^,].*', line)
                if aux is not None:
                    recv_pkts = line
                # does not work over entire output
                aux = re.search('^[\d\.]{1}[,].*', line)
                if aux is not None:
                    recv_order = line
            # aux = [pt, pr, rtt_min, rtt_avg, rtt_max, recv_pkts, recv_order]
            aux = []
            # packets transmitted
            aux.append(output[pt_pr.start():pt_pr.end()].split(' ')[0])
            # packets received
            aux.append(output[pt_pr.start():pt_pr.end()].split(' ')[3])
            # rtt min
            aux.append(output[rtt.start():rtt.end()].split(
                ' ')[3].split('/')[0])
            # rtt avg
            aux.append(output[rtt.start():rtt.end()].split(
                ' ')[3].split('/')[1])
            # rtt max
            aux.append(output[rtt.start():rtt.end()].split(
                ' ')[3].split('/')[2])
            # recv_pkts
            aux.append(recv_pkts)
            # recv_order
            aux.append(recv_order)
            return aux
        except NameError:
            pass

    def pre_send(self, target, fuzz_data_logger, session):

        print("TcpMonitor: pre_send")
        host = target._target_connection.info.split(':')[0]

        # first check 'longer' in order to get proper rtt numbers
        if (session.mutant_index == 1):
            sent_pkts = 100
            self.output_first = self.tcpsyn(host, count=sent_pkts)
            self.output = self.output_first
            # evaluate packet lost percentage
            self.pl = int(self.output[0]) * \
                (int(self.output[0]) - int(self.output[1])) / 100
            # evaluate maximum allowed packet lost
            self.pl_max = (sent_pkts - self.pl) / 2 + self.pl
            # evaluate maximum allowed rtt
            self.rtt_max = float(self.output_first[4]) * 3
            # all packets lost
            if (self.output_first[1] == 0):
                print("TCPMonitor: all packets lost")
                fuzz_data_logger.log_fail("TCP monitor: all packets lost")
            # packets lost in first %5
            pkts_lost = False
            for p in range(sent_pkts * 5 / 100):
                if self.output_first[5][p] == '.':
                    pkts_lost = True
            if pkts_lost:
                print("TCPMonitor: packets lost first 5%")
                fuzz_data_logger.log_fail(
                    "TCP monitor: packets lost on first 5% sent packets")
        else:
            sent_pkts = 10
            self.output = self.tcpsyn(host)
            # rtt max
            if (float(self.output[4]) > (float(self.rtt_max))):
                print("rtt max")
                fuzz_data_logger.log_fail(
                    "TCP monitor: rtt max=" + self.output[4])
            # packets lost - max allowed
            pl = int(self.output[0]) * \
                (int(self.output[0]) - int(self.output[1])) / 100
            if (pl > self.pl_max):
                print(str(pl) + "% packet loss")
                fuzz_data_logger.log_fail(
                    "TCP monitor: max number of packets lost=" + str(pl) + "%")
            # packets lost in first %5
            pkts_lost = False
            for p in range(int(sent_pkts * 5 / 100)):
                if self.output[5][p] == '.':
                    pkts_lost = True
            if pkts_lost:
                print("TCPMonitor: packets lost first 5%")
                fuzz_data_logger.log_fail(
                    "TCP monitor: packets lost on first 5% sent packets")

    def post_send(self, target, fuzz_data_logger, session):

        print("TcpMonitor: post_send")
        host = target._target_connection.info.split(':')[0]
        sent_pkts = 10
        self.output = self.tcpsyn(host)
        # rtt max
        if (float(self.output[4]) > (float(self.rtt_max))):
            print("rtt max")
            fuzz_data_logger.log_fail(
                "TCP monitor: rtt max=" + self.output[4])
        # packets lost - max allowed
        pl = int(self.output[0]) * \
            (int(self.output[0]) - int(self.output[1])) / 100
        if (pl > self.pl_max):
            print(str(pl) + "% packet loss")
            fuzz_data_logger.log_fail(
                "TCP monitor: max number of packets lost=" + str(pl) + "%")
        # packets lost in first %5
        pkts_lost = False
        for p in range(int(sent_pkts * 5 / 100)):
            if self.output[5][p] == '.':
                pkts_lost = True
        if pkts_lost:
            print("TCPMonitor: packets lost first 5%")
            fuzz_data_logger.log_fail(
                "TCP monitor: packets lost on first 5% sent packets")
        return True
