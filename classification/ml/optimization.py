"""
Bayesian optimization stuff.
"""
from os.path import exists
from typing import Any
from typing import Dict
from typing import Sequence
from typing import Type

from colorama import Fore
from colorama import Style
from hyperopt import Trials
from hyperopt import fmin
from hyperopt import space_eval
from hyperopt import tpe
from hyperopt.early_stop import no_progress_loss
from joblib import dump
from numpy import int64
from pandas import DataFrame
from sklearn.base import ClassifierMixin
from sklearn.metrics import matthews_corrcoef
from sklearn.preprocessing import StandardScaler


def __train(clazz: Type[ClassifierMixin], extra: Dict[Any, Any], hyperparameters: Dict[str, Sequence[Any]],
            x_train: DataFrame, y_train: DataFrame) -> ClassifierMixin:
    """
    Trains a classifier.

    :param clazz: the base class to use
    :param extra: extra class parameters
    :param hyperparameters: the hyperparameters to use
    :param x_train: the input training samples
    :param y_train: the output training samples
    :return: the classifier
    """

    # noinspection PyArgumentList
    classifier = clazz(**extra, **hyperparameters)
    # noinspection PyUnresolvedReferences
    classifier.fit(x_train, y_train)

    return classifier


def __evaluate(clazz: Type[ClassifierMixin], extra: Dict[Any, Any], hyperparameters: Dict[str, Sequence[Any]],
               x_train: DataFrame, y_train: DataFrame, x_dev: DataFrame, y_dev: DataFrame) -> float:
    """
    Trains a classifier and computes its MCC.

    :param clazz: the base class to use
    :param extra: extra class parameters
    :param hyperparameters: the hyperparameters to use
    :param x_train: the input training samples
    :param y_train: the output training samples
    :param x_dev: the input development samples
    :param y_dev: the output development samples
    :return: the inverse of the MCC
    """

    # noinspection PyArgumentList
    classifier = __train(clazz, extra, hyperparameters, x_train, y_train)
    # noinspection PyUnresolvedReferences
    y_predicted = classifier.predict(x_dev)

    return -matthews_corrcoef(y_dev, y_predicted)


def optimize(name: str, path: str, clazz: Type[ClassifierMixin], extra: Dict[Any, Any], space: Dict[str, Any],
             x_train: DataFrame, y_train: DataFrame, x_dev: DataFrame, y_dev: DataFrame, numbers: bool,
             scaler: StandardScaler, timeout: int, window_size: int) -> None:
    """
    Trains a single generic classifier by performing a Bayesian optimization search and saves it to file.

    :param name: a good name for the classifier
    :param path: the file name for the saved classifier
    :param clazz: the base class to use
    :param extra: extra class parameters
    :param space: the hyper-parameter space
    :param x_train: the input training samples
    :param y_train: the output training samples
    :param x_dev: the input development samples
    :param y_dev: the output development samples
    :param scaler: the scaler to use on the inputs
    :param numbers: indicates if this classifier can only handle number
    :param timeout: the timeout in seconds
    :param window_size: the window size for the stability check
    """

    if not exists(path):
        print(Fore.RED + ("%s" % name).upper() + Style.RESET_ALL)

        print("scaling...")
        # noinspection PyUnresolvedReferences
        x_train = scaler.transform(x_train)
        # noinspection PyUnresolvedReferences
        x_dev = scaler.transform(x_dev)

        if numbers:
            print("encoding...")
            y_train = y_train.cat.codes.astype(int64)
            y_dev = y_dev.cat.codes.astype(int64)

        print("optimizing...")
        trials = Trials()
        best = fmin(fn=lambda x: __evaluate(clazz, extra, x, x_train, y_train, x_dev, y_dev), space=space,
                    algo=tpe.suggest, timeout=timeout, max_evals=1024, trials=trials,
                    early_stop_fn=no_progress_loss(iteration_stop_count=window_size))

        print("training the final classifier...")
        classifier = __train(clazz, extra, space_eval(space, best), x_train, y_train)

        print("saving to %s..." % path)
        data = {
                "name":       name,
                "classifier": classifier,
                "numbers":    numbers,
                "scaler":     scaler,
                "trials":     trials
        }
        dump(data, path, compress=9)
