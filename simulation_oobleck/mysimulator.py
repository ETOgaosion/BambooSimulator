
from simulation_oobleck.simulator import Simulator
import math
import csv
import statistics

class MySimulator(Simulator):
    def __init__(self, seed=None, start_hour=None,
                 model='GPT-3', model_size='350M', spot_instance_desired_capacity=24, spot_instance_trace='traces/p3-trace-16.csv', performance_log_interval=5, runnable_instances=None, generate_addition_probabilities=False, removal_probability=None, generate_graphs=False):
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
            "350M": 
                {9: {8: 10000},
                10: {8: 10000, 9: 10000},
                11: {10: 10000},
                12: {10: 10000, 11: 10000},
                13: {11: 10000, 12: 10000},
                14: {12: 10000, 13: 10000},
                15: {14: 10000},
                16: {14: 10000, 15: 10000},
                17: {14: 10000, 15: 10000, 16: 10000},
                18: {12: 10000, 14: 10000, 15: 10000, 16: 10000, 17: 10000},
                19: {16: 10000, 17: 10000, 18: 10000},
                20: {16: 10000, 17: 10000, 18: 10000, 19: 10000},
                21: {15: 10000, 18: 10000, 19: 10000, 20: 10000},
                22: {18: 10000, 19: 10000, 20: 10000, 21: 10000},
                23: {19: 10000, 20: 10000, 21: 10000, 22: 10000},
                24: {18: 10000, 19: 10000, 20: 10000, 21: 10000, 22: 10000, 23: 10000},
                25: {21: 10000, 23: 10000, 24: 10000},
                26: {23: 10000, 25: 10000},
                27: {23: 10000, 25: 10000, 26: 10000},
                28: {22: 10000, 25: 10000, 26: 10000, 27: 10000},
                29: {21: 10000, 26: 10000, 27: 10000, 28: 10000},
                30: {23: 10000, 29: 10000},
                31: {25: 10000, 26: 10000, 27: 10000, 28: 10000, 29: 10000, 30: 10000},
                32: {26: 10000, 28: 10000, 29: 10000, 30: 10000, 31: 10000}},
            "1.3B": 
                {9: {8: 10000},
                10: {8: 10000, 9: 10000},
                11: {10: 10000},
                12: {10: 10000, 11: 10000},
                13: {11: 10000, 12: 10000},
                14: {12: 10000, 13: 10000},
                15: {14: 10000},
                16: {14: 10000, 15: 10000},
                17: {14: 10000, 15: 10000, 16: 10000},
                18: {12: 10000, 14: 10000, 15: 10000, 16: 10000, 17: 10000},
                19: {16: 10000, 17: 10000, 18: 10000},
                20: {16: 10000, 17: 10000, 18: 10000, 19: 10000},
                21: {15: 10000, 18: 10000, 19: 10000, 20: 10000},
                22: {18: 10000, 19: 10000, 20: 10000, 21: 10000},
                23: {19: 10000, 20: 10000, 21: 10000, 22: 10000},
                24: {18: 10000, 19: 10000, 20: 10000, 21: 10000, 22: 10000, 23: 10000},
                25: {21: 10000, 23: 10000, 24: 10000},
                26: {23: 10000, 25: 10000},
                27: {23: 10000, 25: 10000, 26: 10000},
                28: {22: 10000, 25: 10000, 26: 10000, 27: 10000},
                29: {21: 10000, 26: 10000, 27: 10000, 28: 10000},
                30: {23: 10000, 29: 10000},
                31: {25: 10000, 26: 10000, 27: 10000, 28: 10000, 29: 10000, 30: 10000},
                32: {26: 10000, 28: 10000, 29: 10000, 30: 10000, 31: 10000}},
            "2.7B": 
                {9: {8: 10000},
                10: {8: 10000, 9: 10000},
                11: {10: 10000},
                12: {10: 10000, 11: 10000},
                13: {11: 10000, 12: 10000},
                14: {12: 10000, 13: 10000},
                15: {14: 10000},
                16: {14: 10000, 15: 10000},
                17: {14: 10000, 15: 10000, 16: 10000},
                18: {12: 10000, 14: 10000, 15: 10000, 16: 10000, 17: 10000},
                19: {16: 10000, 17: 10000, 18: 10000},
                20: {16: 10000, 17: 10000, 18: 10000, 19: 10000},
                21: {15: 10000, 18: 10000, 19: 10000, 20: 10000},
                22: {18: 10000, 19: 10000, 20: 10000, 21: 10000},
                23: {19: 10000, 20: 10000, 21: 10000, 22: 10000},
                24: {18: 10000, 19: 10000, 20: 10000, 21: 10000, 22: 10000, 23: 10000},
                25: {21: 10000, 23: 10000, 24: 10000},
                26: {23: 10000, 25: 10000},
                27: {23: 10000, 25: 10000, 26: 10000},
                28: {22: 10000, 25: 10000, 26: 10000, 27: 10000},
                29: {21: 10000, 26: 10000, 27: 10000, 28: 10000},
                30: {23: 10000, 29: 10000},
                31: {25: 10000, 26: 10000, 27: 10000, 28: 10000, 29: 10000, 30: 10000},
                32: {26: 10000, 28: 10000, 29: 10000, 30: 10000, 31: 10000}},
        }

        assert last_instances_num != new_instances_num, f'last_instances_num: {last_instances_num}, new_instances_num: {new_instances_num} should be different'
        if last_instances_num > new_instances_num:
            last_instances_num, new_instances_num = new_instances_num, last_instances_num
        assert reconfigure_map[self.model_size].get(last_instances_num) is not None, f'last_instances_num: {last_instances_num} is not supported'
        if not self.generate_addition_probabilities:
            assert reconfigure_map[self.model_size][last_instances_num].get(new_instances_num) is not None, f'last_instances_num: {last_instances_num}, new_instances_num: {new_instances_num} is not supported'
            reconfigure_time = reconfigure_map[self.model_size][last_instances_num][new_instances_num]
        else:
            for _, v in reconfigure_map[self.model_size][last_instances_num]:
                reconfigure_time = v
                break
        return reconfigure_time + self.iteration_delta / 2

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
                8: 47120,
                9: 47120,
                10: 45706,
                11: 45706,
                12: 44522,
                13: 44522,
                14: 43690,
                15: 43690,
                16: 34315,
                17: 34315,
                18: 32913,
                19: 32913,
                20: 34195,
                21: 34195,
                22: 36739,
                23: 36739,
                24: 33550,
                25: 33550,
                26: 32385,
                27: 32385,
                28: 31445,
                29: 31445,
                30: 30785,
                31: 30785,
                32: 30200,
            },
            "1.3B": {
                8: 47120,
                9: 47120,
                10: 45706,
                11: 45706,
                12: 44522,
                13: 44522,
                14: 43690,
                15: 43690,
                16: 34315,
                17: 34315,
                18: 32913,
                19: 32913,
                20: 34195,
                21: 34195,
                22: 36739,
                23: 36739,
                24: 33550,
                25: 33550,
                26: 32385,
                27: 32385,
                28: 31445,
                29: 31445,
                30: 30785,
                31: 30785,
                32: 30200,
            },
            "2.7B": {
                8: 47120,
                9: 47120,
                10: 45706,
                11: 45706,
                12: 44522,
                13: 44522,
                14: 43690,
                15: 43690,
                16: 34315,
                17: 34315,
                18: 32913,
                19: 32913,
                20: 34195,
                21: 34195,
                22: 36739,
                23: 36739,
                24: 33550,
                25: 33550,
                26: 32385,
                27: 32385,
                28: 31445,
                29: 31445,
                30: 30785,
                31: 30785,
                32: 30200,
            },
            "6.7B": {
                8: 47120,
                9: 47120,
                10: 45706,
                11: 45706,
                12: 44522,
                13: 44522,
                14: 43690,
                15: 43690,
                16: 34315,
                17: 34315,
                18: 32913,
                19: 32913,
                20: 34195,
                21: 34195,
                22: 36739,
                23: 36739,
                24: 33550,
                25: 33550,
                26: 32385,
                27: 32385,
                28: 31445,
                29: 31445,
                30: 30785,
                31: 30785,
                32: 30200,
            },
            "13B": {
                8: 47120,
                9: 47120,
                10: 45706,
                11: 45706,
                12: 44522,
                13: 44522,
                14: 43690,
                15: 43690,
                16: 34315,
                17: 34315,
                18: 32913,
                19: 32913,
                20: 34195,
                21: 34195,
                22: 36739,
                23: 36739,
                24: 33550,
                25: 33550,
                26: 32385,
                27: 32385,
                28: 31445,
                29: 31445,
                30: 30785,
                31: 30785,
                32: 30200,
            },

        }
        return iteration_map[self.model_size][nodes_num]
        