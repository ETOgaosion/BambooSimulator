
from simulation_oobleck_16.simulator import Simulator
import math
import csv
import statistics

class MySimulator(Simulator):
    def __init__(self, seed=None, start_hour=None,
                 model='GPT-3', model_size='350M', spot_instance_desired_capacity=24, spot_instance_trace='traces/p3-trace-16.csv', performance_log_interval=10,
                 runnable_instances={'2.7B': 10}, generate_addition_probabilities=False, removal_probability=None, generate_graphs=False):
        super().__init__(seed, start_hour, model, model_size, spot_instance_desired_capacity, spot_instance_trace, performance_log_interval, runnable_instances, generate_addition_probabilities, removal_probability, generate_graphs)
    
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
    
        if spot_instance_trace is None:
            self.on_demand_num_instances = spot_instance_desired_capacity
        else:
            self.on_demand_num_instances = (int(calculate_avg_nodes(spot_instance_trace)) // self.pipeline_parallel_size) * self.pipeline_parallel_size
        
        self.on_demand_cost = self.on_demand_num_instances * self.on_demand_cost_per_hour
        self.on_demand_performance = (self.global_batch_size * self.on_demand_num_instances) / self.simulate_iteration_delta_calc(self.on_demand_num_instances)
        self.on_demand_value = self.on_demand_performance / self.on_demand_cost

    def reconfigure_delta(self, last_instances_num, new_instances_num) -> int:
        # reconfigure time (ms)
        reconfigure_map = {
            "350M": {
                9: 27400,
                10: 27390,
                11: 25890,
                12: 24380,
                13: 24375,
                14: 23595,
                15: 22825,
                16: 24755},
            "1.3B": {
                9: 52649,
                10: 49937,
                11: 46937,
                12: 42363,
                13: 39748,
                14: 43652,
                15: 46159,
                16: 35779},
            "2.7B": {
                9: 69366,
                10: 67008,
                11: 67870,
                12: 62405,
                13: 59060,
                14: 55605,
                15: 52485,
                16: 52925},
        }

        assert last_instances_num != new_instances_num, f'last_instances_num: {last_instances_num}, new_instances_num: {new_instances_num} should be different'
        if last_instances_num < new_instances_num:
            last_instances_num, new_instances_num = new_instances_num, last_instances_num
        assert last_instances_num > 8 and last_instances_num <= 16, f'last_instances_num: {last_instances_num} is not supported'
        reconfigure_time = reconfigure_map[self.model_size][last_instances_num]
        return reconfigure_time

    def simulate_iteration_delta(self):
        # iteration time
        self.iteration_delta = self.simulate_iteration_delta_calc(self.last_spot_instance_num)


    def simulate_iteration_delta_calc(self, nodes_num) -> int:
        
        '''
        Returns:
            the iteration time (ms)
        '''
        iteration_map = {
            "350M": {
                8: 24799,
                9: 24779,
                10: 21779,
                11: 18759,
                12: 18749,
                13: 17189,
                14: 15649,
                15: 19509,
                16: 12549,
            },
            "1.3B": {
                8: 72617,
                9: 67193,
                10: 61073,
                11: 51885,
                12: 46375,
                13: 54464,
                14: 60178,
                15: 38478,
                16: 36192,
            },
            "2.7B": {
                8: 127460,
                9: 120090,
                10: 100060,
                11: 92070,
                12: 85940,
                13: 79030,
                14: 72790,
                15: 73490,
                16: 71140,
            },

        }
        return iteration_map[self.model_size][nodes_num]
        