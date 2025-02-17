import csv
import pprint
import collections

time_data = {}

def handle_csv(file):
    seconds, operations = [], []
    if file.endswith(".csv"):
        with open(file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                seconds.append(int(row[0]))
                operations.append(row[1])
    return seconds, operations


def squeeze_data(seconds, operations):
    seconds_norepeat = []
    min_seconds = 0
    seconds_gap = []
    operations_norepeat = []
    nodes_action = []
    for i in range(len(seconds)):
        if (len(seconds_norepeat) > 0 and seconds_norepeat[-1] != seconds[i] / 1000) or len(seconds_norepeat) == 0:
            nodes_action.append(1)
            seconds_norepeat.append(seconds[i] / 1000)
            operations_norepeat.append(operations[i])
            if min_seconds == 0 and len(seconds_norepeat) > 1:
                min_seconds = seconds_norepeat[-1] - seconds_norepeat[-2]
            if len(seconds_norepeat) > 1 and min_seconds > seconds_norepeat[-1] - seconds_norepeat[-2]:
                min_seconds = seconds_norepeat[-1] - seconds_norepeat[-2]
            if len(seconds_norepeat) > 1:
                seconds_gap.append(seconds_norepeat[-1] - seconds_norepeat[-2])
            continue
        if seconds_norepeat[-1] == seconds[i] / 1000:
            if operations[i] == operations_norepeat[-1]:
                nodes_action[-1] += 1
            else:
                nodes_action[-1] -= 1
                raise ValueError("Not gonna happen")
                if nodes_action[-1] == 0:
                    nodes_action.pop()
                    seconds_norepeat.pop()
                    operations_norepeat.pop()
    print(f"min_seconds: {min_seconds}")
    # pprint.pp(seconds_gap)
    print(f'avg_seconds: {sum(seconds_gap) / len(seconds_norepeat)}')
    return seconds_norepeat, operations_norepeat, nodes_action


def calculate_nodes_varient(seconds, operations, nodes):
    current_nodes = 0
    last_seconds = 0
    global time_data
    for i in range(len(seconds)):
        if current_nodes > 0:
            if current_nodes not in time_data:
                time_data[current_nodes] = seconds[i] - last_seconds
            else:
                time_data[current_nodes] += seconds[i] - last_seconds
        if operations[i] == 'add':
            current_nodes += nodes[i]
        else:
            current_nodes -= nodes[i]
        last_seconds = seconds[i]
    time_data = collections.OrderedDict(sorted(time_data.items()))

calculate_nodes_varient(*squeeze_data(*handle_csv("traces/p3-trace.csv")))

pprint.pp(time_data)
pprint.pp(sum(time_data.values()))

time_data = {}

calculate_nodes_varient(*squeeze_data(*handle_csv("traces/g4dn-trace.csv")))

pprint.pp(time_data)
pprint.pp(sum(time_data.values()))