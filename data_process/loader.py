import os
import csv
import pandas as pd

systems = ['bamboo', 'varuna', 'oobleck', 'livepipe']

def load_data(system):
    data_df = pd.read_csv(os.path.join('data', 'metadata', system, 'res.csv'))
    return data_df

def load_data_all():
    data_dfs = {}
    for system in systems:
        data_dfs[system] = load_data(system)
    return data_dfs

def get_data(data_dfs, system):
    return data_dfs[system]