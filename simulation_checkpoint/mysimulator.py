
from simulation_checkpoint.simulator import Simulator
import math
import csv
import statistics

class MySimulator(Simulator):
    def __init__(self, seed=None, start_hour=None,
                 model='GPT-3', model_size='350M', spot_instance_desired_capacity=24, spot_instance_trace='traces/p3-trace-16.csv', performance_log_interval=5, runnable_instances=None, generate_addition_probabilities=False, removal_probability=None, generate_graphs=False):
        super().__init__(seed, start_hour, model, model_size, spot_instance_desired_capacity, spot_instance_trace, performance_log_interval, runnable_instances, generate_addition_probabilities, removal_probability, generate_graphs)
    
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
                9: 32265,
                10: 30670,
                11: 29220,
                12: 28580,
                13: 27835,
                14: 27730,
                15: 26925,
                16: 26740},
            "1.3B": {
                9: 47600,
                10: 46680,
                11: 42675,
                12: 42365,
                13: 39690,
                14: 39555,
                15: 37110,
                16: 36600},
            "2.7B": {
                9: 100260,
                10: 98505,
                11: 92005,
                12: 84800,
                13: 75205,
                14: 74765,
                15: 69530,
                16: 68690},
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
                8: 30250,
                9: 27060,
                10: 24160,
                11: 22880,
                12: 21390,
                13: 21180,
                14: 19570,
                15: 19200,
                16: 18040,
            },
            "1.3B": {
                8: 79310,
                9: 77470,
                10: 69460,
                11: 68840,
                12: 63490,
                13: 63220,
                14: 58330,
                15: 57310,
                16: 50460,
            },
            "2.7B": {
                8: 167550,
                9: 164040,
                10: 151040,
                11: 136630,
                12: 117440,
                13: 116560,
                14: 106090,
                15: 104410,
                16: 104610,
            },

        }
        return iteration_map[self.model_size][nodes_num]
        