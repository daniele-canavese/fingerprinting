#!/usr/bin/python3

import subprocess
from os import system
from random import choice
from string import ascii_lowercase
from time import sleep

iterations = 4
size = 4
delay = 5
app = "grab-site-2.1.16"
os = "linux-4.18.0-18"
hypervisor = "none"
interfaceNo = "1"

# Builds the URL list.
urls = []
while len(urls) < iterations:
    string = "".join(choice(ascii_lowercase) for _ in range(size))
    results = subprocess.check_output(["googler", "--nocolor", "--noprompt", string]).decode()
    for line in results.splitlines():
        line = line.lstrip()
        if line.startswith("https://") or line.startswith("http://"):
            urls.append(line)
urls = set(urls)
print("%d URLs" % len(urls))

# Captures the traffic.
subprocess.Popen(["sudo", "tshark", "-i", interfaceNo, "-Q", "-F", "libpcap", "-w",
                  "traffic/%s_%s_%s.pcap" % (app, os, hypervisor), "tcp"])
sleep(delay)
count = 1
for i in urls:
    print("%d) %s" % (count, i))
    pid = subprocess.Popen(["grab-site", "--dir", "grabSiteTemp", i]).pid
    sleep(delay)
    system("sudo killall grab-site")
    sleep(delay)
    system("rm -rf grabSiteTemp")
    count += 1
sleep(delay)
system("sudo killall tshark")
