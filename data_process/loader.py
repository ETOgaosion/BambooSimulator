import os
import csv
import pandas as pd

systems = ['bamboo', 'varuna', 'oobleck', 'livepipe']

def load_raw_data(system):
    data_df = pd.read_csv(os.path.join('data', 'metadata', system, 'res.csv'))
    return data_df

def load_raw_data_all():
    data_dfs = {}
    for system in systems:
        data_dfs[system] = load_raw_data(system)
    return data_dfs