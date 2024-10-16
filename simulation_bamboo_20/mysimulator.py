
from simulation_bamboo.simulator import Simulator
import math
import csv
import statistics

class MySimulator(Simulator):
    def __init__(self, seed=None, start_hour=None,
                 model='GPT-3', model_size='350M', spot_instance_desired_capacity=24, pipeline_parallel_size=2, spot_instance_trace='traces/p3-trace.csv', 
                 performance_log_interval=5, runnable_instances={'350M': 8}, generate_addition_probabilities=False, removal_probability=None, generate_graphs=False):
        super().__init__(seed, start_hour, model, model_size, spot_instance_desired_capacity, pipeline_parallel_size, spot_instance_trace, performance_log_interval, runnable_instances, generate_addition_probabilities, removal_probability, generate_graphs)
    
        # Amazon EC2 Tesla T4
        self.global_batch_size = 1024
        
        # prepare for first time launch
        self.preparation_delta = 0

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

        if spot_instance_trace is None:
            self.on_demand_num_instances = spot_instance_desired_capacity
        else:
            self.on_demand_num_instances = (int(calculate_avg_nodes(spot_instance_trace)) // self.pipeline_parallel_size) * self.pipeline_parallel_size
        
        self.on_demand_cost = self.on_demand_num_instances * self.on_demand_cost_per_hour
        iter_time, _ = self.simulate_iteration_delta_calc(self.on_demand_num_instances)
        self.on_demand_performance = (self.global_batch_size * self.on_demand_num_instances) / iter_time
        self.on_demand_value = self.on_demand_performance / self.on_demand_cost

    def reconfigure_delta(self, prev_pipeline_num, new_pipeline_num):
        # reconfigure time (ms)
        # layer time model: (layers / 12) * 150s
        # data: model_size: pipeline size: reconfigure time
        fall_back_delta, _ = self.simulate_iteration_delta_calc(new_pipeline_num * self.pipeline_parallel_size)
        fall_back_delta = fall_back_delta / 3
        if prev_pipeline_num > new_pipeline_num:
            self.delta_fallback += fall_back_delta
            return fall_back_delta
        data = {
            '350M': {
                2: 417.42
            },
        }
        
        self.delta_fallback += fall_back_delta
        return data[self.model_size][self.pipeline_parallel_size] + fall_back_delta

    def simulate_iteration_delta(self):
        # iteration time
        self.iteration_delta, self.no_redundancy_delta = self.simulate_iteration_delta_calc(self.data_parallel_size * self.pipeline_parallel_size)
    
    def simulate_iteration_delta_calc(self, nodes_num):
        data = {
            8: 119752.163,
            10: 112578.5429,
            12: 72470.2445,
            14: 109371.1205,
            16: 61948.534,
            18: 66960.605,
            20: 50015.346,
            
            22: 42596.255,
            24: 66666,
            26: 55555,
            28: 55555,
            30: 44444,
            32: 44444
        }
        no_redundancy_data = {
            8: 94730.02791,
            10: 89055.33099,
            12: 63038.3595,
            14: 77470.0865,
            16: 47430.2605,
            18: 54713.997,
            20: 39728.7705,
            
            22: 42596.255,
            24: 66666,
            26: 55555,
            28: 55555,
            30: 44444,
            32: 44444
        }
        nodes_num -= (nodes_num % self.pipeline_parallel_size)
        return data[nodes_num], no_redundancy_data[nodes_num]