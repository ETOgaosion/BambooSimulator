
from simulation_varu.simulator import Simulator
import math
import csv
import statistics

class MySimulator(Simulator):
    def __init__(self, seed=None, start_hour=None,
                 model='GPT-3', model_size='350M', spot_instance_trace='traces/p3-trace-16.csv', generate_addition_probabilities=False, removal_probability=None, generate_graphs=False):
        super().__init__(seed, start_hour, model, model_size, spot_instance_trace, generate_addition_probabilities, removal_probability, generate_graphs)
    
        # Amazon EC2 Tesla T4
        if model == 'GPT-3':
            # the number of nodes that can be added at a time, bamboo do lazy reconfigure, not reconfig every time
            self.global_batch_size = 1024
        
        # prepare for first time launch
        self.preparation_delta = 10000
        self.check_pt_steps = 10000

        # on demand instance config, no need to change
        def calculate_avg_nodes(file):
            seconds, operations, nodes, nodes_samples = [], [], [], []
            if file.endswith(".csv"):
                with open(file, newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    for row in reader:
                        seconds.append(int(row[0]))
                        operations.append(row[1])
                        nodes.append(row[2])
            current_nodes = 0
            seconds_norepeat = []
            for i in range(0, len(seconds)):
                if len(seconds_norepeat) > 0 and seconds_norepeat[-1] != seconds[i]:
                    nodes_samples.append(current_nodes)
                    seconds_norepeat.append(seconds[i])
                if operations[i] == 'add':
                    current_nodes += 1
                elif operations[i] == 'remove':
                    current_nodes -= 1
                if len(seconds_norepeat) == 0:
                    seconds_norepeat.append(seconds[i])
            nodes_samples.append(current_nodes)
            return statistics.mean(nodes_samples)
    
        self.on_demand_num_instances = int(math.pow(2, math.ceil(math.log2(calculate_avg_nodes(spot_instance_trace)))))
        
        self.on_demand_cost = self.on_demand_num_instances * self.on_demand_cost_per_hour
        self.on_demand_performance = (self.global_batch_size * self.on_demand_num_instances) / self.simulate_iteration_delta_calc(self.on_demand_num_instances)
        self.on_demand_value = self.on_demand_performance / self.on_demand_cost

    def reconfigure_delta(self):
        # reconfigure time (ms)
        # layer time model: (layers / 12) * 150s
        return 32904.7

    def simulate_iteration_delta(self):
        # iteration time
        self.iteration_delta = self.simulate_iteration_delta_calc(self.active_spot_instances())
    
    def simulate_iteration_delta_calc(self, nodes_num):
        data = {
            8: 19.1,
            10: 27.3,
            12: 17.6,
            14: 22.3,
            16: 14.7
        }
        if data.get(nodes_num) is not None:
            return data[nodes_num]
        else:
            return data[int(math.pow(2, math.ceil(math.log2(nodes_num))))]