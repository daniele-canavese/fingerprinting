"""
Classification functions.
"""
from typing import Any
from typing import Dict
from typing import Tuple

from pandas import DataFrame
from pandas import Series


def classify(model: Dict[str, Any], x: DataFrame, classes: Dict[int, str]) -> Tuple[Series, DataFrame]:
    """
    Classifies some data.

    :param model: the model to use
    :param x: the input data
    :param classes: the dict for decoding the outputs
    :return: a tuple where the first element is the class and the second the probabilities.
    """

    scaler = model["scaler"]
    numbers = model["numbers"]
    classifier = model["classifier"]

    x = scaler.transform(x)

    yy = Series(classifier.predict(x))
    p = DataFrame(data=classifier.predict_proba(x), columns=classes.values())
    if numbers:
        yy = yy.map(classes).astype("category")

    return yy, p
