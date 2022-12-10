import pandas as pd

try:
    from cfuzzyset import cFuzzySet as FuzzySet
except ImportError:
    from fuzzyset import FuzzySet


def get_fl(s: str):
    sl = s.split()
    return f"{sl[0]} {sl[-1]}"


def fuzzy_merge(
    d1: pd.DataFrame, d2: pd.DataFrame, fuzz_on="", alpha=0.75, beta=0.75, how="inner"
):
    d1_keys = d1[fuzz_on]
    d2_keys = d2[fuzz_on]
    fuzz_left = len(d2_keys.unique()) > len(d1_keys.unique())

    if fuzz_left:
        fuzz = FuzzySet(d2_keys.unique())
        fuzz_fl = FuzzySet(d2_keys.apply(get_fl).unique())
    else:
        fuzz = FuzzySet(d1_keys.unique())
        fuzz_fl = FuzzySet(d1_keys.apply(get_fl).unique())

    def fuzzy_match(row):
        key = row[fuzz_on]
        matches = fuzz.get(key)
        match_conf, match_name = matches[0]

        # print(f"{key} -> {matches}")

        if match_conf <= beta:
            matches = fuzz_fl.get(key)
            match_conf, match_name = matches[0]
            # print(f"{key} -> {matches}")

        return match_name if match_conf >= alpha else None

    if fuzz_left:
        d1["_fuzz"] = d1.apply(fuzzy_match, axis=1)
        return pd.merge(d1, d2, left_on="_fuzz", right_on=fuzz_on, how=how).rename(
            columns={"_fuzz": fuzz_on}
        )
    else:
        d2["_fuzz"] = d2.apply(fuzzy_match, axis=1)
        return pd.merge(d1, d2, left_on=fuzz_on, right_on="_fuzz", how=how).rename(
            columns={"_fuzz": fuzz_on}
        )

