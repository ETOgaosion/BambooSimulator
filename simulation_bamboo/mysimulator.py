
from simulation_bamboo.simulator import Simulator
import math
import csv
import statistics

class MySimulator(Simulator):
    def __init__(self, seed=None, start_hour=None,
                 model='GPT-3', model_size='350M', pipeline_parallel_size=4, skip_filter=50,
                 spot_instance_trace='traces/p3-trace.csv', generate_addition_probabilities=False, removal_probability=None, generate_graphs=False):
        super().__init__(seed, start_hour, model, model_size, pipeline_parallel_size, skip_filter, spot_instance_trace, performance_log_interval, generate_addition_probabilities, removal_probability, generate_graphs)
    
        # Amazon EC2 Tesla T4
        self.global_batch_size = 1024
        
        # prepare for first time launch
        self.preparation_delta = 10000

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
    
        self.on_demand_num_instances = (int(calculate_avg_nodes(spot_instance_trace)) // self.pipeline_parallel_size) * self.pipeline_parallel_size
        
        self.on_demand_cost = self.on_demand_num_instances * self.on_demand_cost_per_hour
        self.on_demand_performance = (self.global_batch_size * self.on_demand_num_instances) / self.simulate_iteration_delta_calc(self.on_demand_num_instances)
        self.on_demand_value = self.on_demand_performance / self.on_demand_cost

    def reconfigure_delta(self, prev_pipeline_num, new_pipeline_num):
        # reconfigure time (ms)
        # layer time model: (layers / 12) * 150s
        data = {
            '350M': {
                1: {2: 32904},
                2: {3: 32904},
                3: {4: 32904, 5: 32904},
                4: {5: 32904},
                5: {6: 32904, 7: 32904},
                6: {7: 32904, 8: 32904},
                7: {8: 32904},
            },
        }
        if prev_pipeline_num > new_pipeline_num:
            prev_pipeline_num, new_pipeline_num = new_pipeline_num, prev_pipeline_num
        assert prev_pipeline_num != new_pipeline_num, f"Pipeline number should not be the same, {prev_pipeline_num} == {new_pipeline_num}"
        assert data[self.model_size].get(prev_pipeline_num) is not None, f"Pipeline number {prev_pipeline_num} is not in the data"
        assert data[self.model_size][prev_pipeline_num].get(new_pipeline_num) is not None, f'Pipeline number {new_pipeline_num} is not in the data {prev_pipeline_num}'
        return data[self.model_size][prev_pipeline_num][new_pipeline_num] + self.iteration_delta / 2

    def simulate_iteration_delta(self):
        # iteration time
        self.iteration_delta = self.simulate_iteration_delta_calc(self.active_spot_instances())
    
    def simulate_iteration_delta_calc(self, nodes_num):
        data = {
            8: 111111,
            12: 99999,
            16: 88888,
            20: 77777,
            24: 66666,
            28: 55555,
            32: 44444
        }
        return data[(nodes_num // self.pipeline_parallel_size) * self.pipeline_parallel_size]