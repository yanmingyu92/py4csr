"""Profile ClinicalSession.generate() on a synthetic 100k-row ADSL."""

import cProfile
import pstats
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "py4csr"))

from py4csr.clinical import ClinicalSession


def make_adsl(n=100_000, seed=42):
    rng = np.random.default_rng(seed)
    trt = rng.choice(["Placebo", "Drug A", "Drug B"], size=n)
    age = np.round(rng.normal(55, 12, n), 1)
    age[rng.random(n) < 0.05] = np.nan  # 5% missing
    return pd.DataFrame({
        "USUBJID": [f"01-{i:06d}" for i in range(n)],
        "TRT01P": trt,
        "AGE": age,
        "WEIGHT": np.round(rng.normal(70, 15, n), 1),
        "HEIGHT": np.round(rng.normal(170, 10, n), 1),
        "BMI": np.round(rng.normal(26, 4, n), 1),
        "PULSE": np.round(rng.normal(72, 8, n), 0),
        "SYSBP": np.round(rng.normal(130, 15, n), 0),
        "SEX": rng.choice(["M", "F"], size=n),
        "RACE": rng.choice(["WHITE", "BLACK OR AFRICAN AMERICAN", "ASIAN"], size=n),
        "AGEGR1": rng.choice(["<65", ">=65"], size=n),
        "ETHNIC": rng.choice(["HISPANIC", "NOT HISPANIC"], size=n),
    })


def run(adsl):
    s = ClinicalSession(uri="PROFILE")
    s.define_report(dataset=adsl, subjid="USUBJID")
    s.add_trt(name="TRT01P", decode="TRT01P")
    for v in ["AGE", "WEIGHT", "HEIGHT", "BMI", "PULSE", "SYSBP"]:
        s.add_var(name=v, label=v, stats="n mean sd median q1 q3 min max")
    for v in ["SEX", "RACE", "AGEGR1", "ETHNIC"]:
        s.add_catvar(name=v, label=v, stats="npct")
    s.generate()
    return s


if __name__ == "__main__":
    adsl = make_adsl()
    print(f"ADSL: {adsl.shape}")

    # wall-clock timing (3 reps)
    times = []
    for _ in range(3):
        t0 = time.perf_counter()
        run(adsl)
        times.append(time.perf_counter() - t0)
    print(f"generate() wall time: min={min(times):.2f}s  runs={[f'{t:.2f}' for t in times]}")

    # profile
    pr = cProfile.Profile()
    pr.enable()
    run(adsl)
    pr.disable()
    st = pstats.Stats(pr)
    st.sort_stats("cumulative").print_stats(25)
