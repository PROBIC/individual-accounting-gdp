import json
import os

import numpy as np
from mimic_utils.data_loaders import load_cached_data
import pandas as pd


def select_by_key(labels: list, selectors: list, n: int, path: str = None):
    train_X, train_y, _, _ = load_cached_data(
        "phenotyping"
    )

    config_dict = dict()

    train_Xs = list()
    train_ys = list()
    sample_id_ks = list()

    if path is not None and not os.path.exists(path):
        os.makedirs(path)

    available_indicies = set(range(len(train_y)))

    groups = list()

    for i in range(len(labels)):
        print(labels[i])
        indicies_k, group = _pick_indicies(available_indicies, n, train_y, selectors[i])
        groups.append(group)
        available_indicies.difference_update(indicies_k)

        if path is not None:
            X_path = os.path.join(path, "X_data_{}.npy".format(i))
            y_path = os.path.join(path, "y_data_{}.npy".format(i))
            sample_id_path = os.path.join(path, "sample_id_path_{}.npy".format(i))
            config_path = os.path.join(path, "config.json")
        else:
            X_path, y_path, config_path, sample_id_path = None, None, None, None

        train_X_k = train_X[indicies_k]
        train_y_k = train_y[indicies_k]
        sample_id_k = np.arange(n)

        train_Xs.append(train_X_k)
        train_ys.append(train_y_k)
        sample_id_ks.append(sample_id_k)

        config_dict[i] = {
            "subgroup_id": i,
            "name": labels[i],
            "N": n,
            "path_X": X_path,
            "path_y": y_path,
            "sample_id_path": sample_id_path,
        }
        if path is not None:
            np.save(X_path, train_X_k, allow_pickle=False, fix_imports=False)
            np.save(y_path, train_y_k, allow_pickle=False, fix_imports=False)
            np.save(sample_id_path, sample_id_k, allow_pickle=False, fix_imports=False)

    print(bool(set(groups[0]) & set(groups[1])))
    print(bool(set(groups[0]) & set(groups[3])))
    print(len(set(groups[1]) & set(groups[3])))

    if path is not None:
        with open(config_path, "w") as fp:
            json.dump(
                config_dict,
                fp,
                sort_keys=True,
                indent=4,
                separators=(",", ": "),
                ensure_ascii=False,
            )
    

    return train_Xs, train_ys, sample_id_ks, config_dict


def _pick_indicies(available_indicies: set, n: int, y: list, selector: list):
    y_df = pd.DataFrame(y, columns=["y_{}".format(i) for i in range(25)])
    y_df["labels"] = np.arange(len(y))
    y_df = y_df[y_df["labels"].isin(available_indicies)]
    for k, v in selector.items():
        y_df = y_df[y_df["y_{}".format(k)] == v]

    possible_indicies = y_df["labels"].unique()
    print(len(possible_indicies))
    if len(possible_indicies) < n:
        raise ValueError("Not enough indicies available.")
    else:
        return np.random.choice(a=possible_indicies, size=n, replace=False)

if __name__ == "__main__":
    non_diagnosis = dict()
    for i in range(25):
        non_diagnosis[i] = 0
    select_by_key(
        labels=[
            "no diagnosis",
            "Pneumonia",
            "No Pneumonia",
            "Acute myocardial infarction",
            "No acute myocardial infarction",
        ],
        selectors=[non_diagnosis, {"21": 1}, {"21": 0}, {"3": 1}, {"3": 0}],
        n=1000,
        path="data/subgroups/picked_subgroups",
    )
