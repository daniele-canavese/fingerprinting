#!/usr/bin/python3
from argparse import ArgumentParser
from os import system
from subprocess import Popen
from time import sleep

delay = 5
modes = ["H", "B", "R", "X"]

# Parses the input arguments.
parser = ArgumentParser(description="Generates the SlowHTTPTest pcap file")
parser.add_argument("--app", default="slowhttptest-1.6", help="the name of the application")
parser.add_argument("--os", default="linux-4.17.0", help="the name of the OS")
parser.add_argument("--folder", default=".", help="the folder that will contain the produced pcap file")
parser.add_argument("urls", help="the comma separated list of target URLs")
args = parser.parse_args()

# Builds the URL list.
urls = args.urls.split(",")

# Captures the traffic.
# pcap = "%s/%s_%s_none.pcap" % (args.folder, args.app, args.os)
# system("tshark -Q -F libpcap -w %s \"tcp and (port 443 or port 80)\" &> /dev/null &" % pcap)
for mode in modes:
    # Builds the URL list.
    print("Mode %s" % mode)
    print("%d URLs" % len(urls))
    pcap = "%s/%s-%s_%s_none.pcap" % (args.folder, args.app, mode, args.os)
    system("tshark -Q -F libpcap -w %s \"tcp and (port 443 or port 80)\" &> /dev/null &" % pcap)
    sleep(delay)
    count = 1
    for i in urls:
        print("%d) %s" % (count, i))
        pid = Popen(["slowhttptest", "-%s" % mode, "-u", i]).pid
        sleep(60)
        system("killall slowhttptest")
        count += 1
    sleep(delay)
    system("killall tshark")
    sleep(delay)
