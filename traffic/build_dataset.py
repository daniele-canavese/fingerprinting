from argparse import ArgumentParser
from glob import glob
from os import listdir
from os import system
from os import unlink
from os.path import isdir

from numpy import linspace
# Parses the input arguments.
from numpy import split
from pandas import DataFrame
from pandas import read_csv

parser = ArgumentParser(description="Generates the final data sets")
parser.add_argument("--tstat", default="tstat-3.1.1/tstat/tstat", help="the tstat command")
parser.add_argument("--dev_ratio", default=10, help="the dev set ratio")
parser.add_argument("--test_ratio", default=10, help="the test set ratio")
parser.add_argument("pcap", help="the name of the pcap folder")
parser.add_argument("dataset", help="the name of the data set folder")
args = parser.parse_args()

thresholds = linspace(0.000000, 0.001000, 11).tolist()
thresholds += linspace(0.001000, 0.010000, 10).tolist()
thresholds += linspace(0.010000, 0.100000, 10).tolist()
thresholds += linspace(0.100000, 1.000000, 10).tolist()
thresholds += linspace(1.000000, 10.000000, 10).tolist()
thresholds += linspace(10.000000, 100.000000, 10).tolist()
thresholds += linspace(100.000000, 1000.000000, 10).tolist()
thresholds = set(thresholds)


def split_capture(folder: str, threshold: float) -> None:
    """
    Splits some pcap files into multiple smaller capture files.

    :param folder: the name of the folder containing the pcap files to split
    :param threshold: the time threshold
    """

    system("mkdir -p %s-%f" % (folder, threshold))

    for f in listdir(folder):
        if f.endswith(".pcap"):
            system("tshark -r %s/%s -w %s-%f/%s -Y \"tcp.time_relative <= %f\"" %
                   (folder, f, folder, threshold, f, threshold))


def create_data_set(source: str, output: str) -> None:
    """
    Creates a CSV file by launching tstat.

    :param source: the source file
    :param output: the output folder
    """

    prefix = "dataset"
    parts = source.split("-")

    m = {
            "dos":                  "dos",
            "browser":              "browser",
            "crawler":              "crawler",
            "goldeneye":            "dos",
            "hulk":                 "dos",
            "firefox":              "browser",
            "wget":                 "crawler",
            "edge":                 "browser",
            "httrack":              "crawler",
            "chrome":               "browser",
            "rudy":                 "dos",
            "slowloris":            "dos",
            "curl":                 "crawler",
            "wpull":                "crawler",
            "goldeneye-2.1":        "dos",
            "firefox-62.0":         "browser",
            "hulk-1.0":             "dos",
            "wget-1.11.4":          "crawler",
            "edge-42.17134.1.0":    "browser",
            "httrack-3.49.2":       "crawler",
            "chrome-48.0.2564.109": "browser",
            "rudy-1.0.0":           "dos",
            "chrome-68.0.3440.84":  "browser",
            "firefox-42.0":         "browser",
            "slowloris-0.1.5":      "dos",
            "curl-7.55.1":          "crawler",
            "curl-7.61.0":          "crawler",
            "slowloris-0.1.4":      "dos",
            "wpull-2.0.1":          "crawler",
            "wget-1.19.5":          "crawler"
    }

    if len(parts) == 1:
        name = "%s/%s-all.csv" % (output, prefix)
    else:
        name = "%s/%s-%s.csv" % (output, prefix, parts[1])

    with open(name, "w") as o:
        print(
                "c_ip c_port c_pkts_all c_rst_cnt c_ack_cnt c_ack_cnt_p c_bytes_uniq c_pkts_data c_bytes_all "
                "c_pkts_retx c_bytes_retx c_pkts_ooo c_syn_cnt c_fin_cnt s_ip s_port s_pkts_all s_rst_cnt s_ack_cnt "
                "s_ack_cnt_p s_bytes_uniq s_pkts_data s_bytes_all s_pkts_retx s_bytes_retx s_pkts_ooo s_syn_cnt "
                "s_fin_cnt first last durat c_first s_first c_last s_last c_first_ack s_first_ack c_isint s_isint "
                "c_iscrypto s_iscrypto con_t p2p_t http_t complete application_short application_long os_short "
                "os_long all category",
                file=o)
        for f in listdir(source):
            if f.endswith(".pcap"):
                parts = f[:-5].split("_")
                app_parts = parts[0].split("-")
                os_parts = parts[1].split("-")
                category = m[parts[0]]

                system("%s %s/%s -s %s > /dev/null" % (args.tstat, source, f, f))

                if not isdir(f):
                    continue

                tcp = []
                tcp.append("%s/%s/log_tcp_complete" % (f, listdir("%s" % f)[0]))
                tcp.append("%s/%s/log_tcp_nocomplete" % (f, listdir("%s" % f)[0]))
                for t in tcp:
                    with open(t) as csv:
                        count = 1
                        for row in csv.readlines():
                            if count > 1:
                                row = row.rstrip("\n")
                                fields = row.split()
                                l = " ".join(fields[0: 44])
                                print(l, end="", file=o)
                                if t.endswith("_complete"):
                                    print(" true", end="", file=o)
                                else:
                                    print(" false", end="", file=o)
                                print(" %s" % app_parts[0], end="", file=o)
                                print(" %s" % parts[0], end="", file=o)
                                print(" %s" % os_parts[0], end="", file=o)
                                print(" %s" % parts[1], end="", file=o)
                                print(" %s_%s" % (parts[0], parts[1]), end="", file=o)
                                print(" %s" % category, end="", file=o)
                                print(file=o)
                            count += 1

                system("rm -fr %s" % f)


print("Analyzing the pcap files...")
system("rm -fr %s/*.csv" % args.dataset)
create_data_set(args.pcap, args.dataset)

for i in thresholds:
    split_capture(args.pcap, i)
    create_data_set("%s-%f" % (args.pcap, i), args.dataset)
    system("rm -fr %s-%f" % (args.pcap, i))

print("Processing the statistics...")
data_set = DataFrame()
for i in glob("%s/*.csv" % args.dataset):
    data_set = data_set.append(read_csv(i, sep=" "))
    unlink(i)
del data_set["c_ip"]
del data_set["s_ip"]
del data_set["c_port"]
del data_set["s_port"]
data_set.to_csv("%s/dataset.csv.gz" % args.dataset)
unknown = ["grabsite-2.1.16", "opera-62.0.3331.66", "slowhttptest-1.6", "firefox-68.0"]
unknown_set = data_set[data_set["application_long"].isin(unknown)]
data_set = data_set[~data_set["application_long"].isin(unknown)]
training_set, dev_set, known_set = split(data_set.sample(frac=1),
                                         [int((1 - args.dev_ratio / 100 - args.test_ratio / 100) * len(data_set)),
                                          int((1 - args.dev_ratio / 100) * len(data_set))])
training_set.to_csv("%s/training.csv.gz" % args.dataset)
dev_set.to_csv("%s/dev.csv.gz" % args.dataset)
known_set.to_csv("%s/known.csv.gz" % args.dataset)
unknown_set.to_csv("%s/unknown.csv.gz" % args.dataset)
