import os
import csv

def get_start_nodes_num(file):
    start_nodes_num = 0
    if file.endswith(".csv"):
        with open(file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0] != '0':
                    break
                if row[1] == 'add':
                    start_nodes_num += 1
    return start_nodes_num