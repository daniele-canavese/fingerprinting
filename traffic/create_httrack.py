from argparse import ArgumentParser
from os import system
from random import choice
from string import ascii_lowercase
from subprocess import run, PIPE, DEVNULL
from time import sleep

delay = 5

# Parses the input arguments.
parser = ArgumentParser(description="Generates the httrack pcap file")
parser.add_argument("--app", default="httrack-3.49.2", help="the name of the application")
parser.add_argument("--os", default="linux-4.17.0", help="the name of the OS")
parser.add_argument("--folder", default=".", help="the folder that will contain the produced pcap file")
parser.add_argument("urls", help="the comma separated list of target URLs")
args = parser.parse_args()

# Builds the URL list.
urls = args.urls.split(",")

# Captures the traffic.
pcap = "%s/%s_%s_none.pcap" % (args.folder, args.app, args.os)
system("tshark -Q -F libpcap -w %s \"tcp and (port 443 or port 80)\" &> /dev/null &" % pcap)
sleep(delay)
count = 1
for i in urls:
	print("%d) %s" % (count, i))
	system("httrack \"%s\" -O httrack.tmp \"\" > /dev/null" % i)
	count += 1
sleep(delay)
system("killall tshark")
system("rm -fr httrack.tmp")
