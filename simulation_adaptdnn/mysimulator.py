
from simulation_adaptdnn.simulator import Simulator
import math
import csv
import statistics

class MySimulator(Simulator):
    def __init__(self, seed=None, start_hour=None,
                 model='GPT-3', model_size='350M', spot_instance_desired_capacity=24, spot_instance_trace='traces/p3-trace-16.csv', performance_log_interval=5, runnable_instances=None, generate_addition_probabilities=False, removal_probability=None, generate_graphs=False):
        super().__init__(seed, start_hour, model, model_size, spot_instance_desired_capacity, spot_instance_trace, performance_log_interval, runnable_instances, generate_addition_probabilities, removal_probability, generate_graphs)
    
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
        self.on_demand_performance = (self.global_batch_size * self.on_demand_num_instances) / self.simulate_iteration_delta_calc(self.on_demand_num_instances)
        self.on_demand_value = self.on_demand_performance / self.on_demand_cost

    def reconfigure_delta(self, last_instances_num, new_instances_num) -> int:
        # reconfigure time (ms)
        reconfigure_map = {
            "350M": {
                9: 15440,
                10: 18070,
                11: 18370,
                12: 19360,
                13: 190720,
                14: 21140,
                15: 21370,
                16: 23670},
            "1.3B": {
                9: 18420,
                10: 18850,
                11: 22130,
                12: 17510,
                13: 18520,
                14: 18120,
                15: 18420,
                16: 21330},
            "2.7B": {
                9: 16082,
                10: 16941,
                11: 16940,
                12: 20060,
                13: 18580,
                14: 21620,
                15: 20270,
                16: 22220},
        }

        assert last_instances_num != new_instances_num, f'last_instances_num: {last_instances_num}, new_instances_num: {new_instances_num} should be different'
        if last_instances_num < new_instances_num:
            last_instances_num, new_instances_num = new_instances_num, last_instances_num
        assert last_instances_num > 8 and last_instances_num <= 16, f'last_instances_num: {last_instances_num} is not supported'
        reconfigure_time = reconfigure_map[self.model_size][last_instances_num]
        return reconfigure_time

    def simulate_iteration_delta(self):
        # iteration time
        self.iteration_delta = self.simulate_iteration_delta_calc(self.data_parallel_size * self.pipeline_parallel_size)


    def simulate_iteration_delta_calc(self, nodes_num) -> int:
        
        '''
        Returns:
            the iteration time (ms)
        '''
        iteration_map = {
            "350M": {
                8: 24670,
                9: 21480,
                10: 18580,
                11: 17300,
                12: 15810,
                13: 15600,
                14: 13990,
                15: 13620,
                16: 12460,
            },
            "1.3B": {
                8: 58600,
                9: 56760,
                10: 48750,
                11: 48130,
                12: 42780,
                13: 42510,
                14: 37620,
                15: 36600,
                16: 29750,
            },
            "2.7B": {
                8: 124540,
                9: 121030,
                10: 108030,
                11: 93620,
                12: 74430,
                13: 73550,
                14: 63080,
                15: 61400,
                16: 61600,
            },

        }
        return iteration_map[self.model_size][nodes_num]
        