from argparse import ArgumentParser
from os import system
from time import sleep

delay = 5

# Parses the input arguments.
parser = ArgumentParser(description="Generates the wpull pcap file")
parser.add_argument("--app", default="wpull-2.0.1", help="the name of the application")
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
    system(
        "python3 -m wpull %s --warc-file tmp --no-check-certificate --no-robots --user-agent \"InconspiuousWebBrowser/1.0\" --wait 0.5 --random-wait --waitretry 600 --page-requisites --recursive --level inf --span-hosts-allow linked-pages,page-requisites --escaped-fragment --strip-session-id --sitemaps --reject-regex \"/login\.php\" --tries 3 --retry-connrefused --retry-dns-error --timeout 60 --session-timeout 21600 --delete-after --database tmp.db --quiet --output-file tmp.log  > /dev/null && killall node" % i)
    count += 1
sleep(delay)
system("killall tshark")
