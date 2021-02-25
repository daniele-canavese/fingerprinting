# Encryption agnostic classifiers of traffic originators andtheir application to anomaly detection

This is the repository for the paper _Encryption agnostic classifiers of traffic originators and their application to
anomaly detection_ submitted to the _Computers & Electrical Engineering_ journal. It contains the source code that can
be used to both create a suitable data set and train a set of traffic classificators. In addition, we are also sharing
the preprocessed data set that we used to write the paper and all our trained models. We did not include the pcap files
for privacy reasons.

## Content

This project contains the following folders:

+ `classification` contains all the Python scripts used to traing and test the machine learning models;
+ `datasets` contains the data sets that we used to perform our experiments;
+ `models` contains all the nine trained models described in our paper
+ `traffic` contains all the Python scripts used to capture the traffic and generate our data set.

Note: due to some temporary server problems, the `datasets` and `models` folder are hosted on Google Drive at the URL:
https://drive.google.com/drive/folders/1x86yIAY-I3LcF40gvRXI80RNT_wmc4O-?usp=sharing.

## Getting started

This section briefly describes how the source code contained in this repository can be used to train a new machine
learning model.

### Generating the traffic captures

Before starting you should install all the Python dependencies via

```shell
pipenv install
```

The folder `traffic` contains several scripts that can be used to automatize the generation of the traffic. You will
need `tshark` to sniff the traffic and you can install it on a Debian/Ubuntu distribution via the command:

```shell
# apt install tshark
```

You might need to use `sudo` or run as superuser the next scripts if your current user does not have the right privilege
to sniff raw data from the network interfaces.

You will also need to install the following tools:

+ network stress tools (a.k.a. DoS tools):
  + GoldenEye, which can be downloaded from https://wroot.org/projects/goldeneye;
  + HULK, which can be downloaded from https://github.com/grafov/hulk;
  + RudyJS, which can be downloaded from https://www.imperva.com/learn/ddos/rudy-r-u-dead-yet;
  + SlowHTTPTest, which can be downloaded from https://tools.kali.org/stress-testing/slowhttptest;
  + SlowLoris, which can be downloaded from https://github.com/gkbrk/slowloris;
+ web crawlers:
  + cURL, which can be installed via ` # apt install curl`;
  + grab-site, which can be downloaded from https://github.com/ArchiveTeam/grab-site;
  + httrack, which can be installed via ` # apt install httrack`;
  + wget, which can be installed via ` # apt install wget`;
  + wpull, which can be installed via `pip3 install wpull`.

Then, you can launch the following scripts to produce a series of pcap files:

+ network stress tools (a.k.a. DoS tools):
  + `traffic/create_goldeneye.py` to create a pcap file by using GoldenEye;
  + `traffic/create_hulk.py` to create a pcap file by using HULK;
  + `traffic/create_rudy.py` to create a pcap file by using RUDY;
  + `traffic/create_slowhttptest.py` to create a pcap file by using SlowHTTPTest;
  + `traffic/create_slowloris.py` to create a pcap file by using SlowLoris;
+ web crawlers:
  + `traffic/create_curl.py` to create a pcap file by using cURL;
  + `traffic/create_grabsite.py` to create a pcap file by using grab-site;
  + `traffic/create_httrack.py` to create a pcap file by using httrack;
  + `traffic/create_wget.py` to create a pcap file by using wget;
  + `traffic/create_wpull.py` to create a pcap file by using wpull.

In addition, you will need to capture some manual browser traffic. For our experiments we used Chrome 48 and 68, Firefox
42, 62 and 68, Edge 42 and Opera 62.

### Generating the processed data set

Before going further, you need to install and compile `tstat` from http://tstat.polito.it/. You may need to use GCC
version 9 or previous since `tstat` is not (yet) compatible with GCC 10.

Then, once all the pcap files are ready, the script `traffic/build_dataset.py` can be used to launch tstat and create
the final CSV data sets (training, dev, known and unknown tools sets).

### Training the models

In order to train the models you need to launch the `classification/optimize.py`. This is a long running script and it
can last for several ours until completion.

Once the training has been completed, you can use the `classification/report.py` to test the classifiers and to
generate a set of LaTeX files with a commprehensive report. This is the same script that we used to generate the data
in brief accompanying our paper.
