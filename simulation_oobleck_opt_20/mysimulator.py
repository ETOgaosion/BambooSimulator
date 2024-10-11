
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
            "350M": 
                {9: {8: 0},
                10: {8: 0, 9: 0},
                11: {10: 0},
                12: {10: 0, 11: 0},
                13: {10: 0, 11: 0, 12: 0},
                14: {12: 0, 13: 0},
                15: {8: 0, 13: 0, 14: 0},
                16: {12: 0, 13: 0, 14: 0, 15: 0},
                17: {12: 0, 13: 0, 14: 0, 15: 0, 16: 0},
                18: {12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0},
                19: {12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0},
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
                {9: {8: 1680},
                10: {8: 540, 9: 430},
                11: {10: 430},
                12: {10: 1010, 11: 430},
                13: {10: 1650, 11: 1360, 12: 750},
                14: {12: 2090, 13: 920},
                15: {8: 610, 13: 610, 14: 1060},
                16: {12: 770, 13: 750, 14: 818, 15: 810},
                17: {12: 2210, 13: 2290, 14: 2290, 15: 2210, 16: 910},
                18: {12: 2700, 13: 1540, 14: 2240, 15: 1530, 16: 1460, 17: 910},
                19: {12: 1940, 13: 1940, 14: 1940, 15: 1860, 16: 1840, 17: 1020, 18: 914},
                20: {15: 720, 16: 1310, 17: 1400, 18: 910, 19: 920},
                
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
                {9: {8: 1020},
                10: {8: 1180, 9: 830},
                11: {10: 1760},
                12: {10: 1450, 11: 1510},
                13: {10: 1340, 11: 1430, 12: 1540},
                14: {12: 1580, 13: 910},
                15: {8: 545, 13: 545, 14: 2520},
                16: {12: 1440, 13: 1443, 14: 1120, 15: 1010},
                17: {12: 2730, 13: 2690, 14: 2690, 15: 1020, 16: 838},
                18: {12: 1530, 13: 1750, 14: 1950, 15: 1750, 16: 1350, 17: 580},
                19: {12: 1230, 13: 1230, 14: 1230, 15: 1320, 16: 1230, 17: 1150, 18: 1000},
                20: {15: 3590, 16: 1750, 17: 1110, 18: 1066, 19: 830},
                
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

        if last_instances_num == new_instances_num:
            print('no need to reconfigure, {last_instances_num} == {new_instances_num}')
            return 0
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
        fallback_delta = self.simulate_iteration_delta_calc(new_instances_num) / 2
        self.delta_fallback += fallback_delta
        return reconfigure_time + fallback_delta

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
                8: 18840,
                9: 19290,
                10: 16890,
                11: 15690,
                12: 14440,
                13: 14540,
                14: 12250,
                15: 12320,
                16: 9800,
                17: 9830,
                18: 9950,
                19: 9880,
                20: 9840,
                
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
                8: 54200,
                9: 55310,
                10: 49820,
                11: 45040,
                12: 38620,
                13: 37240,
                14: 33250,
                15: 31990,
                16: 28150,
                17: 29860,
                18: 28470,
                19: 28470,
                20: 26300,
                
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
                8: 105060,
                9: 96040,
                10: 83490,
                11: 77410,
                12: 70690,
                13: 73660,
                14: 60696,
                15: 63150,
                16: 52810,
                17: 51790,
                18: 49100,
                19: 45420,
                20: 42540,
                
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
                8: 285800,
                9: 230960,
                10: 199900,
                11: 175630,
                12: 172000,
                13: 175430,
                14: 144340,
                15: 175410,
                16: 143870,
                17: 125780,
                18: 116580,
                19: 109480,
                20: 101540,
                
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
        