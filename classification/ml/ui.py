"""
UI functions.
"""

from typing import Any
from typing import Dict
from typing import TextIO

from pandas import DataFrame
from pandas import Series
from pandas import unique
from sklearn.metrics import accuracy_score
from sklearn.metrics import balanced_accuracy_score
from sklearn.metrics import cohen_kappa_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from sklearn.metrics import hamming_loss
from sklearn.metrics import jaccard_score
from sklearn.metrics import matthews_corrcoef
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import zero_one_loss


def print_data_set(tex: TextIO, tag: str, description: str, data_set: DataFrame, group: str) -> None:
    """
    Prints some statistics about a dataset.

    :param tex: the output LaTeX file
    :param tag: a tag for generating the labels
    :param description: a description for the caption
    :param data_set: the data set to analyze
    :param group: the feature name for grouping the data
    """
    features = ["c_pkts_all", "c_bytes_all", "s_pkts_all", "s_bytes_all", "durat"]
    means = data_set[[group, *features]].groupby(group).mean()
    print("\\begin{table}[H]", file=tex)
    print("\t\\centering", file=tex)
    print("\t\\begin{tabular}{lrrrrr}", file=tex)
    print("\t\t\\toprule", file=tex)
    print(
            "\t\t & \multicolumn{2}{c}{\\textsc{sent by client}} & \multicolumn{2}{c}{\\textsc{sent by server}}\\\\",
            file=tex)
    print("\t\t\\cmidrule(lr){2-3}", file=tex)
    print("\t\t\\cmidrule(lr){4-5}", file=tex)
    print(
            "\t\t\\textsc{%s} & \\textsc{packets} & \\textsc{bytes} & \\textsc{packets} & \\textsc{bytes} & \\textsc{duration} [$ms$]\\\\" % description,
            file=tex)
    print("\t\t\\midrule", file=tex)
    for index, row in means.iterrows():
        print("\t\t%s & %s\\\\" % (index, " & ".join(["{:.3f}".format(i) for i in row])), file=tex)
    print("\t\t\\bottomrule", file=tex)
    print("\t\\end{tabular}", file=tex)
    print("\t\\caption{Means of some features for the %s in our data set.}" % description, file=tex)
    print("\t\\label{tab:means_%s}" % tag, file=tex)
    print("\\end{table}", file=tex)


def print_optimization(tex: TextIO, tag: str, description: str, model: Dict[str, Any]) -> None:
    """
    Prints the optimization trials' losses of a model.

    :param tex: the output LaTeX file
    :param tag: a tag for generating the labels
    :param description: a description for the caption
    :param model: the model to use
    """

    trials = model["trials"]
    x = []
    y = []
    for trial in trials:
        x.append((trial["book_time"] - trials.trials[0]["book_time"]).total_seconds() / 3600)
        y.append(-trial["result"]["loss"])
    table = DataFrame(data=[x, y]).transpose()

    print("\\begin{figure}[H]", file=tex)
    print("\t\\centering", file=tex)
    print("\t\\begin{tikzpicture}", file=tex)
    print(
            "\t\t\\begin{axis}[xlabel=\\textsc{time [hours]}, ylabel=\\textsc{$R_k$}, axis lines=left, grid=major, width=0.9\linewidth, height=12em, ymax=1, ymin=-1]",
            file=tex)
    print("\t\t\t\\addplot +[mark=none, OrangeRed, thick, smooth] table {", file=tex)
    for _, row in table.iterrows():
        print("\t\t\t\t" + " ".join(map(str, row.to_list())), file=tex)
    print("\t\t\t};", file=tex)
    print("\t\t\\end{axis}", file=tex)
    print("\t\\end{tikzpicture}", file=tex)
    print("\t\\caption{Hyper-parameters optimization plot for the %s.}" % description, file=tex)
    print("\t\\label{fig:optimization_%s}" % tag, file=tex)
    print("\\end{figure}", file=tex)


def print_hyperparameters(tex: TextIO, tag: str, description: str, model: Dict[str, Any]) -> None:
    """
    Prints the hyper-parameters of a model.

    :param tex: the output LaTeX file
    :param tag: a tag for generating the labels
    :param description: a description for the caption
    :param model: the model to use
    """

    classifier = model["classifier"]
    hyperparameters = list(model["trials"].trials[0]["misc"]["vals"].keys())

    print("\\begin{table}[H]", file=tex)
    print("\t\\centering", file=tex)
    print("\t\\begin{tabular}{ll}", file=tex)
    print("\t\t\\toprule", file=tex)
    print("\t\t\\textsc{hyper-parameter} & \\textsc{value}\\\\", file=tex)
    print("\t\t\\midrule", file=tex)
    for i in hyperparameters:
        print("\t\t\\verb|%s| & %s\\\\" % (i, classifier.get_params()[i]), file=tex)
    print("\t\t\\bottomrule", file=tex)
    print("\t\\end{tabular}", file=tex)
    print("\t\\caption{Optimal hyper-parameters for the %s.}" % description, file=tex)
    print("\t\\label{tab:hyperparameters_%s}" % tag, file=tex)
    print("\\end{table}", file=tex)


def print_statistics(tex: TextIO, tag: str, description: str, train_y: Series, train_yy: Series, dev_y: Series,
                     dev_yy: Series, known_y: Series, known_yy: Series, unknown_y: Series, unknown_yy: Series) -> None:
    """
    Prints some classification statistics.

    :param tex: the output LaTeX file
    :param tag: a tag for generating the labels
    :param description: a description for the caption
    :param train_y: the training set target classes
    :param train_yy: the training set inferred classes
    :param dev_y: the development set target classes
    :param dev_yy: the development set inferred classes
    :param known_y: the known set target classes
    :param known_yy: the known set inferred classes
    :param unknown_y: the unknown set target classes
    :param unknown_yy: the unknown set inferred classes
    """

    print("\\begin{table}[H]", file=tex)
    print("\t\\centering", file=tex)
    print("\t\\begin{tabular}{lrrrr}", file=tex)
    print("\t\t\\toprule", file=tex)
    print("\t\t\\textsc{statistic} & \\textsc{training set} & \\textsc{dev set} & \\textsc{kts} & \\textsc{uts}\\\\",
          file=tex)
    print("\t\t\\midrule", file=tex)
    print("\t\tsamples & %d & %d & %d & %d\\\\" % (len(train_y), len(dev_y), len(known_y), len(unknown_y)), file=tex)
    print("\t\taccuracy [$\\%%$] & %.3f & %.3f & %.3f & %.3f\\\\" % (
            accuracy_score(train_y, train_yy) * 100,
            accuracy_score(dev_y, dev_yy) * 100,
            accuracy_score(known_y, known_yy) * 100,
            accuracy_score(unknown_y, unknown_yy) * 100), file=tex)
    print("\t\tbalanced accuracy [$\\%%$] & %.3f & %.3f & %.3f & %.3f\\\\" % (
            balanced_accuracy_score(train_y, train_yy) * 100,
            balanced_accuracy_score(dev_y, dev_yy) * 100,
            balanced_accuracy_score(known_y, known_yy) * 100,
            balanced_accuracy_score(unknown_y, unknown_yy) * 100), file=tex)
    print("\t\tprecision [$\\%%$] & %.3f & %.3f & %.3f & %.3f\\\\" % (
            precision_score(train_y, train_yy, average="macro") * 100,
            precision_score(dev_y, dev_yy, average="macro") * 100,
            precision_score(known_y, known_yy, average="macro") * 100,
            precision_score(unknown_y, unknown_yy, average="macro") * 100), file=tex)
    print("\t\trecall [$\\%%$] & %.3f & %.3f & %.3f & %.3f\\\\" % (
            recall_score(train_y, train_yy, average="macro") * 100,
            recall_score(dev_y, dev_yy, average="macro") * 100,
            recall_score(known_y, known_yy, average="macro") * 100,
            recall_score(unknown_y, unknown_yy, average="macro") * 100), file=tex)
    print("\t\tCohen’s kappa [$\\%%$] & %.3f & %.3f & %.3f & %.3f\\\\" % (
            cohen_kappa_score(train_y, train_yy) * 100,
            cohen_kappa_score(dev_y, dev_yy) * 100,
            cohen_kappa_score(known_y, known_yy) * 100,
            cohen_kappa_score(unknown_y, unknown_yy) * 100), file=tex)
    print("\t\tF-score [$\\%%$] & %.3f & %.3f & %.3f & %.3f\\\\" % (
            f1_score(train_y, train_yy, average="macro") * 100,
            f1_score(dev_y, dev_yy, average="macro") * 100,
            f1_score(known_y, known_yy, average="macro") * 100,
            f1_score(unknown_y, unknown_yy, average="macro") * 100), file=tex)
    print("\t\tJaccard score [$\\%%$] & %.3f & %.3f & %.3f & %.3f\\\\" % (
            jaccard_score(train_y, train_yy, average="macro") * 100,
            jaccard_score(dev_y, dev_yy, average="macro") * 100,
            jaccard_score(known_y, known_yy, average="macro") * 100,
            jaccard_score(unknown_y, unknown_yy, average="macro") * 100), file=tex)
    print("\t\tHamming loss & %.3f & %.3f & %.3f & %.3f\\\\" % (
            hamming_loss(train_y, train_yy),
            hamming_loss(dev_y, dev_yy),
            hamming_loss(known_y, known_yy),
            hamming_loss(unknown_y, unknown_yy)), file=tex)
    print("\t\tzero-one loss & %.3f & %.3f & %.3f & %.3f\\\\" % (
            zero_one_loss(train_y, train_yy),
            zero_one_loss(dev_y, dev_yy),
            zero_one_loss(known_y, known_yy),
            zero_one_loss(unknown_y, unknown_yy)), file=tex)
    print("\t\t$R_k$ & %.3f & %.3f & %.3f & %.3f\\\\" % (
            matthews_corrcoef(train_y, train_yy),
            matthews_corrcoef(dev_y, dev_yy),
            matthews_corrcoef(known_y, known_yy),
            matthews_corrcoef(unknown_y, unknown_yy)), file=tex)
    print("\t\t\\bottomrule", file=tex)
    print("\t\\end{tabular}", file=tex)
    print("\t\\caption{Classification statistics for the %s.}" % description, file=tex)
    print("\t\\label{tab:classification_%s}" % tag, file=tex)
    print("\\end{table}", file=tex)


def print_confusion(tex: TextIO, tag: str, description: str, known_y: Series, known_yy: Series,
                    classes: Dict[int, str]) -> None:
    """
    Prints a confusion matrix.

    :param tex: the output LaTeX file
    :param tag: a tag for generating the labels
    :param description: a description for the caption
    :param known_y: the known set target classes
    :param known_yy: the known set inferred classes
    :param classes: the dict for decoding the outputs
    """

    confusion = confusion_matrix(known_y, known_yy)

    m = {
            "dos":                  "dos",
            "browser":              "browser",
            "crawler":              "crawler",
            "goldeneye":            "goldeneye",
            "hulk":                 "hulk",
            "firefox":              "firefox",
            "wget":                 "wget",
            "edge":                 "edge",
            "httrack":              "httrack",
            "chrome":               "chrome",
            "rudy":                 "rudy",
            "slowloris":            "slowloris",
            "curl":                 "curl",
            "wpull":                "wpull",
            "goldeneye-2.1":        "go-2.1",
            "firefox-62.0":         "fi-62.0",
            "hulk-1.0":             "hu-1.0",
            "wget-1.11.4":          "wg-1.11.4",
            "edge-42.17134.1.0":    "ed-42",
            "httrack-3.49.2":       "ht-3.49.2",
            "chrome-48.0.2564.109": "ch-48.0",
            "rudy-1.0.0":           "ru-1.0.0",
            "chrome-68.0.3440.84":  "ch-68.0",
            "firefox-42.0":         "fi-42.0",
            "slowloris-0.1.5":      "sl-0.1.5",
            "curl-7.55.1":          "cu-7.55.1",
            "curl-7.61.0":          "cu-7.61.0",
            "slowloris-0.1.4":      "sl-0.1.4",
            "wpull-2.0.1":          "wp-2.0.1",
            "wget-1.19.5":          "wg-1.19.5"
    }

    c = {}
    for k, v in classes.items():
        c[k] = m[v]
    classes = c

    print("\\begin{table}[H]", file=tex)
    print("\t\\centering", file=tex)
    if len(classes) > 6:
        print("\\resizebox{\\linewidth}{!}{%", file=tex)
    print("\t\\begin{tabular}{ll|%s}" % ("l" * confusion.shape[0]), file=tex)
    print("\t\\setlength{\\tabcolsep}{2pt}", file=tex)
    print("\t\t & & \\multicolumn{%d}{c}{\\textsc{inferred}}\\\\" % len(classes), file=tex)
    if len(classes) > 11:
        print("\t\t & & \\rotatebox{90}{\\textsc{" + "}} & \\rotatebox{90}{\\textsc{".join(
            map(str, classes.values())) + "}}\\\\", file=tex)
    else:
        print("\t\t & & \\textsc{" + "} & \\textsc{".join(map(str, classes.values())) + "}\\\\", file=tex)
    print("\t\t\\midrule", file=tex)
    for index, row in enumerate(confusion):
        if index == 0:
            p = "\\multirow{%d}{*}{\\rotatebox{90}{\\textsc{target}}}" % len(classes)
        else:
            p = ""
        print("\t\t%s & \\textsc{%s} & " % (p, classes[index]) + " & ".join(map(str, row)) + "\\\\", file=tex)
    print("\t\\end{tabular}", file=tex)
    if len(classes) > 6:
        print("\t}", file=tex)
    if len(classes) > 11:
        extra = (r" (where \textsc{go} = \textsc{goldeneye}," +
                 r" \textsc{fi} = \textsc{firefox}, " +
                 r"\textsc{hu} = \textsc{hulk}, " +
                 r"\textsc{wg} = \textsc{wget}, " +
                 r"\textsc{ed} = \textsc{edge}, " +
                 r"\textsc{ht} = \textsc{httrack}, " +
                 r"\textsc{ch} = \textsc{chrome}, " +
                 r"\textsc{ru} = \textsc{rudy}, " +
                 r"\textsc{sl} = \textsc{slowloris}, " +
                 r"\textsc{cu} = \textsc{curl} and " +
                 r"\textsc{wp} = \textsc{wpull}")
    else:
        extra = ""
    print("\t\\caption{Confusion matrix for the %s on the KTS%s.}" % (description, extra), file=tex)
    print("\t\\label{tab:confusion_%s}" % tag, file=tex)
    print("\\end{table}", file=tex)


def print_packets(tex: TextIO, tag: str, description: str, known_y: Series, known_yy: Series,
                  known_set: DataFrame) -> None:
    """
    Prints a confusion matrix.

    :param tex: the output LaTeX file
    :param tag: a tag for generating the labels
    :param description: a description for the caption
    :param known_y: the known set target classes
    :param known_yy: the known set inferred classes
    :param known_set: the known test set
    """

    packets = known_set["c_pkts_all"] + known_set["s_pkts_all"]
    data = DataFrame()
    data["packets"] = packets
    data["target"] = known_y
    data["inferred"] = known_yy
    data.sort_values(by="packets", inplace=True)
    values = []
    for j in unique(data["packets"]):
        if j > 50:
            break
        d = data[data["packets"] == j]
        m = balanced_accuracy_score(d["target"], d["inferred"]) * 100
        values.append({"packets": j, "metric": m})
    table = DataFrame(data=values)

    print("\\begin{figure}[H]", file=tex)
    print("\t\\centering", file=tex)
    print("\t\\begin{tikzpicture}", file=tex)
    print(
            "\t\t\\begin{axis}[xlabel=\\textsc{exchanged packets}, ylabel=\\textsc{balanced accuracy [$\\%$]}, axis lines=left, grid=major, width=0.9\linewidth, height=12em, ymax=100, ymin=0]",
            file=tex)
    print("\t\t\t\\addplot +[mark=none, Purple, thick, smooth] table {", file=tex)
    for _, row in table.iterrows():
        print("\t\t\t\t" + " ".join(map(str, row.to_list())), file=tex)
    print("\t\t\t};", file=tex)
    print("\t\t\\end{axis}", file=tex)
    print("\t\\end{tikzpicture}", file=tex)
    print("\t\\caption{Balanced accuracy vs. exchange packets plot for the %s on the KTS.}" % description, file=tex)
    print("\t\\label{fig:packets_%s}" % tag, file=tex)
    print("\\end{figure}", file=tex)


def print_unknown(tex: TextIO, tag: str, description: str, unknown_yy: Series, unknown_set: DataFrame) -> None:
    """
    Prints the classification for the unknown tools.

    :param tex: the output LaTeX file
    :param tag: a tag for generating the labels
    :param description: a description for the caption
    :param unknown_yy: the unknown set inferred classes
    :param unknown_set: the unknown test set
    """

    table = DataFrame()
    table["y"] = unknown_set["application_long"]
    table["yy"] = unknown_yy
    table = DataFrame(table.groupby(["y", "yy"]).size())

    print("\\begin{table}[H]", file=tex)
    print("\t\\centering", file=tex)
    tools = unique([i[0] for i in table.index])
    for tool in tools:
        print("\t\\begin{subtable}{.45\\linewidth}", file=tex)
        print("\t\t\\centering", file=tex)
        print("\t\\begin{tabular}{ll}", file=tex)
        print("\t\t\\toprule", file=tex)
        print("\t\t\\textsc{inferred class} & \\textsc{samples}\\\\", file=tex)
        print("\t\t\\midrule", file=tex)
        for count, (index, row) in enumerate(table.iterrows()):
            if index[0] == tool:
                print("\t\t%s & %d\\\\" % (index[1], row), file=tex)
        print("\t\t\\bottomrule", file=tex)
        print("\t\\end{tabular}", file=tex)
        print("\t\\caption{Classification of \\textsc{%s}.}" % tool, file=tex)
        print("\t\\end{subtable}", file=tex)

    print("\t\\caption{Classification of unknown tools for the %s.}" % description, file=tex)
    print("\t\\label{tab:unknown_%s}" % tag, file=tex)
    print("\\end{table}", file=tex)


def print_ensemble_statistics(tex: TextIO, tag: str, description: str, y: Series, yy: Series) -> None:
    """
    Prints some classification statistics about an ensemble.

    :param tex: the output LaTeX file
    :param tag: a tag for generating the labels
    :param description: a description for the caption
    :param y: the target classes
    :param yy: the inferred classes
    """

    print("\\begin{table}[H]", file=tex)
    print("\t\\centering", file=tex)
    print("\t\\begin{tabular}{ll}", file=tex)
    print("\t\t\\toprule", file=tex)
    print("\t\t\\textsc{statistic} & \\textsc{value}\\\\", file=tex)
    print("\t\t\\midrule", file=tex)
    print("\t\tsamples & %d\\\\" % len(y), file=tex)
    print("\t\taccuracy [$\\%%$] & %.3f\\\\" % (accuracy_score(y, yy) * 100), file=tex)
    print("\t\tbalanced accuracy [$\\%%$] & %.3f\\\\" % (balanced_accuracy_score(y, yy) * 100), file=tex)
    print("\t\tprecision [$\\%%$] & %.3f\\\\" % (precision_score(y, yy, average="macro") * 100), file=tex)
    print("\t\trecall [$\\%%$] & %.3f\\\\" % (recall_score(y, yy, average="macro") * 100), file=tex)
    print("\t\tCohen’s kappa [$\\%%$] & %.3f\\\\" % (cohen_kappa_score(y, yy) * 100), file=tex)
    print("\t\tF-score [$\\%%$] & %.3f\\\\" % (f1_score(y, yy, average="macro") * 100), file=tex)
    print("\t\tJaccard score [$\\%%$] & %.3f\\\\" % (jaccard_score(y, yy, average="macro") * 100), file=tex)
    print("\t\tHamming loss & %.3f\\\\" % hamming_loss(y, yy), file=tex)
    print("\t\tzero-one loss & %.3f\\\\" % zero_one_loss(y, yy), file=tex)
    print("\t\t$R_k$ & %.3f\\\\" % matthews_corrcoef(y, yy), file=tex)
    print("\t\t\\bottomrule", file=tex)
    print("\t\\end{tabular}", file=tex)
    print("\t\\caption{Classification statistics for the %s on the KTS.}" % description, file=tex)
    print("\t\\label{tab:ensemble_%s}" % tag, file=tex)
    print("\\end{table}", file=tex)
