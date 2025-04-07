
from simulation_livepipe.simulator import Simulator
import math
import csv
import statistics
from data_process.loader import load_raw_data
from data.metadata.livepipe.raw_data import get_remap_layer_time

class MySimulator(Simulator):
    def __init__(self, seed=None, start_hour=None,
                 model='GPT-3', model_size='gpt3_1_3B', spot_instance_desired_capacity=24, spot_instance_trace='traces/p3-trace-16.csv', performance_log_interval=5, generate_addition_probabilities=False, removal_probability=None, generate_graphs=False):
        super().__init__(seed, start_hour, model, model_size, spot_instance_desired_capacity, spot_instance_trace, performance_log_interval, generate_addition_probabilities, removal_probability, generate_graphs)
    
        self.global_batch_size = 1024
        
        # prepare for first time launch
        self.preparation_delta = 0
        
        self.meta_data = load_raw_data('livepipe')

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
        self.on_demand_performance = (self.global_batch_size * self.on_demand_num_instances) / self.simulate_iteration_delta_calc(self.on_demand_num_instances)
        self.on_demand_value = self.on_demand_performance / self.on_demand_cost

    def reconfigure_delta(self, last_instances_num, new_instances_num) -> int:
        # reconfigure time (ms)
        layer_remap_time = get_remap_layer_time(self.model_size, last_instances_num, new_instances_num)
        
        fallback_delta = self.simulate_iteration_delta_calc(new_instances_num) / 16
        self.delta_fallback += fallback_delta
        return layer_remap_time + fallback_delta

    def simulate_iteration_delta(self):
        # iteration time
        self.iteration_delta = self.simulate_iteration_delta_calc(self.data_parallel_size * self.pipeline_parallel_size)


    def simulate_iteration_delta_calc(self, nodes_num) -> int:
        
        '''
        Returns:
            the iteration time (ms)
        '''
        
        
        