"""
Optimizes a set of classifiers.
"""

from argparse import ArgumentParser

from hyperopt.hp import choice
from hyperopt.hp import uniform
from hyperopt.hp import uniformint
from numpy import float32
from pandas import read_csv
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.utils import compute_class_weight
from skorch import NeuralNetClassifier
from torch import Tensor
from torch.optim import Adam

from data import features
from ml import NeuralModule
from ml import optimize

# Parses the input arguments.
parser = ArgumentParser(description="Optimizes a set of classifiers.")
parser.add_argument("output", help="the name of the output feature")
parser.add_argument("--training_set", default="datasets/training.csv.gz", help="the name of the training set")
parser.add_argument("--dev_set", default="datasets/dev.csv.gz", help="the name of the dev set")
parser.add_argument("--folder", default="models", help="the folder for saving the models")
parser.add_argument("--timeout", type=int, default=60 * 60 * 24, help="the optimization timeout in seconds")
parser.add_argument("--window", type=int, default=30, help="the stability window size")
parser.add_argument("--jobs", type=int, default=-1, help="the number of cores to use")
args = parser.parse_args()

# Reads the data sets.
training_set = read_csv(args.training_set)
dev_set = read_csv(args.dev_set)
train_x = training_set.loc[:, features].astype(float32)
train_y = training_set.loc[:, args.output].astype("category")
class_weights = compute_class_weight("balanced", classes=train_y.cat.categories, y=train_y)
dev_x = dev_set.loc[:, features].astype(float32)
dev_y = dev_set.loc[:, args.output].astype("category")

# Creates the scaler.
scaler = StandardScaler()
scaler.fit(train_x)

# Optimizes the classifiers.
optimize("extra-trees", "%s/%s-extra_trees.joblib" % (args.folder, args.output),
         ExtraTreesClassifier, {
                 "class_weight": "balanced",
                 "n_jobs":       args.jobs
         }, {
                 "n_estimators":      uniformint("n_estimators", 1, 500),
                 "criterion":         choice("criterion", ["gini", "entropy"]),
                 "max_depth":         uniformint("max_depth", 5, 20),
                 "min_samples_split": uniformint("min_samples_split", 2, 50),
                 "min_samples_leaf":  uniformint("min_samples_leaf", 2, 50)
         }, train_x, train_y, dev_x, dev_y, False, scaler, args.timeout, args.window)

optimize("random forest", "%s/%s-random_forest.joblib" % (args.folder, args.output),
         RandomForestClassifier, {
                 "class_weight": "balanced",
                 "n_jobs":       args.jobs
         }, {
                 "n_estimators":      uniformint("n_estimators", 1, 500),
                 "criterion":         choice("criterion", ["gini", "entropy"]),
                 "max_depth":         uniformint("max_depth", 5, 20),
                 "min_samples_split": uniformint("min_samples_split", 2, 50),
                 "min_samples_leaf":  uniformint("min_samples_leaf", 2, 50)
         }, train_x, train_y, dev_x, dev_y, False, scaler, args.timeout, args.window)

optimize("neural network", "%s/%s-nn.joblib" % (args.folder, args.output),
         NeuralNetClassifier, {
                 "module":                  NeuralModule,
                 "optimizer":               Adam,
                 "train_split":             None,
                 "iterator_train__shuffle": True,
                 "verbose":                 0,
                 "max_epochs":              50,
                 "batch_size":              1024,
                 "module__inputs":          len(features),
                 "module__outputs":         len(train_y.cat.categories),
                 "criterion__weight":       Tensor(class_weights),
                 "device":                  "cuda"
         }, {
                 "lr":                        uniform("lr", 0.001, 0.01),
                 "module__layers":            uniformint("module__layers", 1, 10),
                 "module__neurons_per_layer": uniformint("module__neurons_per_layer", 16, 512),
                 "module__p":                 uniform("module__p", 0.1, 0.5),
         }, train_x, train_y, dev_x, dev_y, True, scaler, args.timeout, args.window)
