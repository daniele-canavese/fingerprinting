"""
Report generator.
"""

from argparse import ArgumentParser
from glob import glob
from warnings import simplefilter

from joblib import load
from numpy import float32
from pandas import read_csv
from pandas import set_option
from skorch.exceptions import DeviceWarning

from data import features
from ml import classify
from ml import print_confusion
from ml import print_data_set
from ml import print_hyperparameters
from ml import print_optimization
from ml import print_packets
from ml import print_unknown
from ml.ui import print_statistics

# Parses the input arguments.
parser = ArgumentParser(description="Generates the LaTeX report")
parser.add_argument("--output", default="docs", help="the folder that will contain the produced LaTeX files")
parser.add_argument("--data_set", default="datasets/dataset.csv.gz", help="the name of the full data set")
parser.add_argument("--training_set", default="datasets/training.csv.gz", help="the name of the training set")
parser.add_argument("--dev_set", default="datasets/dev.csv.gz", help="the name of the dev set")
parser.add_argument("--known_set", default="datasets/known.csv.gz", help="the name of the known tools test set")
parser.add_argument("--unknown_set", default="datasets/unknown.csv.gz", help="the name of the unknown tools test set")
parser.add_argument("--folder", default="models", help="the folder containing the models")
args = parser.parse_args()

set_option("precision", 3)
simplefilter(action="ignore", category=DeviceWarning)
simplefilter(action="ignore", category=UserWarning)

# Reads the data sets.
data_set = read_csv(args.data_set)
training_set = read_csv(args.training_set)
known_set = read_csv(args.known_set)
unknown_set = read_csv(args.unknown_set)
dev_set = read_csv(args.dev_set)
train_x = training_set.loc[:, features].astype(float32)
dev_x = dev_set.loc[:, features].astype(float32)
known_x = known_set.loc[:, features].astype(float32)
unknown_x = unknown_set.loc[:, features].astype(float32)

# Generates the data set report.
groups = {"category": "category", "application_short": "tool", "application_long": "tool instance"}
for k, v in groups.items():
    tex = "%s/data_set_%s.tex" % (args.output, k)
    print("generating %s..." % tex)
    with open(tex, "w") as f:
        print_data_set(f, k, v, data_set, k)

# Generates the classifier reports.
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

outputs = {"category": "category", "application_short": "tool", "application_long": "tool instance"}
first = True
for output, what in outputs.items():
    for i in sorted(glob("%s/%s-*.joblib" % (args.folder, output))):
        model = load(i)
        name = model["name"]
        description = "%s classifier based on %s" % (what, name)
        tag = ("%s_%s" % (output, name)).replace("-", "_").replace(" ", "_")
        tex = "%s/data_%s.tex" % (args.output, tag)
        print("generating %s..." % tex)

        with open(tex, "w") as f:
            print_optimization(f, tag, description, model)
            print_hyperparameters(f, tag, description, model)

            classes = dict(enumerate(training_set.loc[:, output].astype("category").cat.categories))
            train_y = training_set.loc[:, output].astype("category")
            train_yy, train_p = classify(model, train_x, classes)
            dev_y = dev_set.loc[:, output].astype("category")
            dev_yy, dev_p = classify(model, dev_x, classes)
            known_y = known_set.loc[:, output].astype("category")
            known_yy, known_p = classify(model, known_x, classes)
            unknown_y = unknown_set.loc[:, output].astype("category")
            unknown_yy, unknown_p = classify(model, unknown_x, classes)
            print_statistics(f, tag, description, train_y, train_yy, dev_y, dev_yy, known_y, known_yy, unknown_y,
                             unknown_yy)
            print_confusion(f, tag, description, known_y, known_yy, classes)
            print_packets(f, tag, description, known_y, known_yy, known_set)
            print_unknown(f, tag, description, unknown_yy, unknown_set)
