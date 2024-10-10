import csv

# frequency: how many seconds to remove a node
def generate_trace(max_node_num, frequency):
    trace = []
    for i in range(max_node_num):
        trace.append([0, 'add', 'node' + str(i + 1)])
    for i in range(max_node_num // 2):
        trace.append([frequency * 1000 * (i + 1), 'remove', 'node' + str(i + 1)])
    return trace

def write_trace(trace, file):
    with open(file, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile)
        for line in trace:
            spamwriter.writerow(line)

# trace = generate_trace(20, 6 * 3600)
# write_trace(trace, 'traces/6h-trace-20.csv')

# trace = generate_trace(20, 1 * 3600)
# write_trace(trace, 'traces/1h-trace-20.csv')

# trace = generate_trace(20, 10 * 60)
# write_trace(trace, 'traces/10m-trace-20.csv')

# trace = generate_trace(20, 5 * 60)
# write_trace(trace, 'traces/5m-trace-20.csv')

trace = generate_trace(20, 2 * 60)
write_trace(trace, 'traces/2m-trace-20.csv')

# trace = generate_trace(20, 1 * 60)
# write_trace(trace, 'traces/1m-trace-20.csv')