
from simulation_livepipe.simulator import Simulator
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
                {9: {8: 0},
                10: {8: 0, 9: 0},
                11: {10: 0},
                12: {10: 0, 11: 0},
                13: {11: 0, 12: 0},
                14: {12: 0, 13: 0},
                15: {13: 0, 14: 0},
                16: {13: 0, 14: 0, 15: 0},
                17: {14: 0, 15: 0, 16: 0},
                18: {12: 0, 14: 0, 15: 0, 16: 0, 17: 0},
                19: {16: 0, 17: 0, 18: 0},
                20: {15: 0, 16: 0, 17: 0, 18: 0, 19: 0},
                21: {15: 0, 18: 0, 19: 0, 20: 0},
                22: {18: 0, 19: 0, 20: 0, 21: 0},
                23: {19: 0, 20: 0, 21: 0, 22: 0},
                24: {18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0},
                25: {21: 0, 23: 0, 24: 0},
                26: {23: 0, 25: 0},
                27: {23: 0, 25: 0, 26: 0},
                28: {22: 0, 25: 0, 26: 0, 27: 0},
                29: {21: 0, 26: 0, 27: 0, 28: 0},
                30: {23: 0, 29: 0},
                31: {25: 0, 26: 0, 27: 0, 28: 0, 29: 0, 30: 0},
                32: {26: 0, 28: 0, 29: 0, 30: 0, 31: 0}},
            "1.3B": 
                {9: {8: 0},
                10: {8: 0, 9: 0},
                11: {10: 0},
                12: {10: 0, 11: 0},
                13: {11: 0, 12: 0},
                14: {12: 0, 13: 0},
                15: {13: 0, 14: 0},
                16: {13: 0, 14: 0, 15: 0},
                17: {14: 0, 15: 0, 16: 0},
                18: {12: 0, 14: 0, 15: 0, 16: 0, 17: 0},
                19: {16: 0, 17: 0, 18: 0},
                20: {15: 0, 16: 0, 17: 0, 18: 0, 19: 0},
                21: {15: 0, 18: 0, 19: 0, 20: 0},
                22: {18: 0, 19: 0, 20: 0, 21: 0},
                23: {19: 0, 20: 0, 21: 0, 22: 0},
                24: {18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0},
                25: {21: 0, 23: 0, 24: 0},
                26: {23: 0, 25: 0},
                27: {23: 0, 25: 0, 26: 0},
                28: {22: 0, 25: 0, 26: 0, 27: 0},
                29: {21: 0, 26: 0, 27: 0, 28: 0},
                30: {23: 0, 29: 0},
                31: {25: 0, 26: 0, 27: 0, 28: 0, 29: 0, 30: 0},
                32: {26: 0, 28: 0, 29: 0, 30: 0, 31: 0}},
            "2.7B": 
                {9: {8: 0},
                10: {8: 0, 9: 0},
                11: {10: 0},
                12: {10: 0, 11: 0},
                13: {11: 0, 12: 0},
                14: {12: 0, 13: 0},
                15: {13: 0, 14: 0},
                16: {13: 0, 14: 0, 15: 0},
                17: {14: 0, 15: 0, 16: 0},
                18: {12: 0, 14: 0, 15: 0, 16: 0, 17: 0},
                19: {16: 0, 17: 0, 18: 0},
                20: {15: 0, 16: 0, 17: 0, 18: 0, 19: 0},
                21: {15: 0, 18: 0, 19: 0, 20: 0},
                22: {18: 0, 19: 0, 20: 0, 21: 0},
                23: {19: 0, 20: 0, 21: 0, 22: 0},
                24: {18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0},
                25: {21: 0, 23: 0, 24: 0},
                26: {23: 0, 25: 0},
                27: {23: 0, 25: 0, 26: 0},
                28: {22: 0, 25: 0, 26: 0, 27: 0},
                29: {21: 0, 26: 0, 27: 0, 28: 0},
                30: {23: 0, 29: 0},
                31: {25: 0, 26: 0, 27: 0, 28: 0, 29: 0, 30: 0},
                32: {26: 0, 28: 0, 29: 0, 30: 0, 31: 0}},
        }

        assert last_instances_num != new_instances_num, f'last_instances_num: {last_instances_num}, new_instances_num: {new_instances_num} should be different'
        if last_instances_num < new_instances_num:
            last_instances_num, new_instances_num = new_instances_num, last_instances_num
        assert reconfigure_map[self.model_size].get(last_instances_num) is not None, f'last_instances_num: {last_instances_num} is not supported'
        if not self.generate_addition_probabilities:
            assert reconfigure_map[self.model_size][last_instances_num].get(new_instances_num) is not None, f'last_instances_num: {last_instances_num}, new_instances_num: {new_instances_num} is not supported'
            reconfigure_time = reconfigure_map[self.model_size][last_instances_num][new_instances_num]
        else:
            for _, v in enumerate(reconfigure_map[self.model_size][last_instances_num]):
                reconfigure_time = v
                break
        
        fallback_delta = self.simulate_iteration_delta_calc(new_instances_num) / 16
        self.delta_fallback += fallback_delta
        return reconfigure_time + fallback_delta

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
                8: 27120,
                9: 27120,
                10: 25706,
                11: 25706,
                12: 24522,
                13: 24522,
                14: 23690,
                15: 23690,
                16: 14315,
                17: 14315,
                18: 12913,
                19: 12913,
                20: 14195,
                21: 14195,
                22: 16739,
                23: 16739,
                24: 13550,
                25: 13550,
                26: 12385,
                27: 12385,
                28: 11445,
                29: 11445,
                30: 10785,
                31: 10785,
                32: 10200,
            },
            "1.3B": {
                8: 27120,
                9: 27120,
                10: 25706,
                11: 25706,
                12: 24522,
                13: 24522,
                14: 23690,
                15: 23690,
                16: 14315,
                17: 14315,
                18: 12913,
                19: 12913,
                20: 14195,
                21: 14195,
                22: 16739,
                23: 16739,
                24: 13550,
                25: 13550,
                26: 12385,
                27: 12385,
                28: 11445,
                29: 11445,
                30: 10785,
                31: 10785,
                32: 10200,
            },
            "2.7B": {
                8: 27120,
                9: 27120,
                10: 25706,
                11: 25706,
                12: 24522,
                13: 24522,
                14: 23690,
                15: 23690,
                16: 14315,
                17: 14315,
                18: 12913,
                19: 12913,
                20: 14195,
                21: 14195,
                22: 16739,
                23: 16739,
                24: 13550,
                25: 13550,
                26: 12385,
                27: 12385,
                28: 11445,
                29: 11445,
                30: 10785,
                31: 10785,
                32: 10200,
            },
            "6.7B": {
                8: 27120,
                9: 27120,
                10: 25706,
                11: 25706,
                12: 24522,
                13: 24522,
                14: 23690,
                15: 23690,
                16: 14315,
                17: 14315,
                18: 12913,
                19: 12913,
                20: 14195,
                21: 14195,
                22: 16739,
                23: 16739,
                24: 13550,
                25: 13550,
                26: 12385,
                27: 12385,
                28: 11445,
                29: 11445,
                30: 10785,
                31: 10785,
                32: 10200,
            },
            "13B": {
                8: 27120,
                9: 27120,
                10: 25706,
                11: 25706,
                12: 24522,
                13: 24522,
                14: 23690,
                15: 23690,
                16: 14315,
                17: 14315,
                18: 12913,
                19: 12913,
                20: 14195,
                21: 14195,
                22: 16739,
                23: 16739,
                24: 13550,
                25: 13550,
                26: 12385,
                27: 12385,
                28: 11445,
                29: 11445,
                30: 10785,
                31: 10785,
                32: 10200,
            },

        }
        return iteration_map[self.model_size][nodes_num]
        