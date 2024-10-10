
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
                10: {8: 360, 9: 320},
                11: {10: 300},
                12: {10: 300, 11: 270},
                13: {10: 270, 11: 270, 12: 270},
                14: {12: 270, 13: 270},
                15: {13: 270, 14: 240},
                16: {13: 270, 14: 240, 15: 240},
                17: {13: 240, 14: 240, 15: 240, 16: 210},
                18: {12: 280, 14: 240, 15: 240, 16: 210, 17: 220},
                19: {16: 220, 17: 210, 18: 180},
                20: {15: 240, 16: 210, 17: 210, 18: 180, 19: 230},
                
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
                10: {8: 690, 9: 810},
                11: {10: 590},
                12: {10: 600, 11: 580},
                13: {11: 580, 12: 590},
                14: {12: 580, 13: 480},
                15: {13: 540, 14: 590},
                16: {13: 480, 14: 470, 15: 720},
                17: {14: 470, 15: 710, 16: 810},
                18: {12: 930, 14: 470, 15: 700, 16: 810, 17: 700},
                19: {16: 940, 17: 700, 18: 700},
                20: {13: 240, 15: 240, 16: 210, 17: 210, 18: 180, 19: 230},
                
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
                10: {8: 1430, 9: 980},
                11: {10: 720},
                12: {10: 720, 11: 540},
                13: {11: 560, 12: 540},
                14: {12: 1500, 13: 1410},
                15: {13: 540, 14: 540},
                16: {13: 550, 14: 540, 15: 900},
                17: {14: 550, 15: 900, 16: 900},
                18: {12: 2650, 14: 550, 15: 900, 16: 2650, 17: 940},
                19: {16: 910, 17: 730, 18: 740},
                20: {13: 2510, 15: 2510, 16: 2730, 17: 1150, 18: 1310, 19: 1180},
                
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
                8: 18860,
                9: 17430,
                10: 15310,
                11: 14850,
                12: 12330,
                13: 13000,
                14: 11190,
                15: 11140,
                16: 10440,
                17: 10870,
                18: 8900,
                19: 9030,
                20: 7710,
                
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
                8: 54140,
                9: 49230,
                10: 42930,
                11: 43300,
                12: 39760,
                13: 35110,
                14: 32560,
                15: 28890,
                16: 26750,
                17: 25530,
                18: 24670,
                19: 24730,
                20: 21570,
                
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
                8: 112050,
                9: 92100,
                10: 85160,
                11: 72360,
                12: 70800,
                13: 71220,
                14: 65160,
                15: 55380,
                16: 55230,
                17: 45730,
                18: 45230,
                19: 45030,
                20: 41300,
                
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
        