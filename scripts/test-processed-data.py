#!/usr/bin/env python
import pandas as pd
import os

HERE = os.path.abspath(os.path.dirname(__file__))

oflc = pd.read_csv(
    os.path.join(HERE, "../data/processed/H-2-certification-decisions.csv"),
    low_memory=False
)

duplicates = oflc[
    ~oflc.index.isin(oflc.drop_duplicates().index)
]

dupes_by_fy = duplicates["fy"].value_counts()
print(dupes_by_fy.sort_index())
assert((dupes_by_fy > 5).sum() == 0)
