
from simulation_gemini.simulator import Simulator
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
                10: {8: 360, 9: 320},
                11: {10: 300},
                12: {10: 300, 11: 270},
                13: {10: 270, 11: 270, 12: 270},
                14: {12: 270, 13: 270},
                15: {8: 270, 13: 270, 14: 240},
                16: {12: 270, 13: 270, 14: 240, 15: 240},
                17: {12: 240 ,13: 240, 14: 240, 15: 240, 16: 210},
                18: {12: 280, 13: 250, 14: 240, 15: 240, 16: 210, 17: 220},
                19: {12: 220, 13: 240, 14: 220, 15: 240, 16: 220, 17: 210, 18: 180},
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
                13: {10: 580, 11: 580, 12: 590},
                14: {12: 580, 13: 480},
                15: {8: 540, 13: 540, 14: 590},
                16: {12: 480, 13: 480, 14: 470, 15: 720},
                17: {12: 380, 13: 400, 14: 470, 15: 710, 16: 810},
                18: {12: 930, 13: 700, 14: 470, 15: 700, 16: 810, 17: 700},
                19: {12: 1000, 13: 1000, 14: 1000, 15: 940, 16: 940, 17: 700, 18: 700},
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
                13: {10: 560, 11: 560, 12: 540},
                14: {12: 1500, 13: 1410},
                15: {8: 540, 13: 540, 14: 540},
                16: {12: 550, 13: 550, 14: 540, 15: 900},
                17: {12: 450, 13: 450, 14: 550, 15: 900, 16: 900},
                18: {12: 2650, 13: 2650, 14: 550, 15: 900, 16: 2650, 17: 940},
                19: {12: 1000, 13: 1000, 14: 1000, 15: 910, 16: 910, 17: 730, 18: 740},
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


    def simulate_iteration_delta_calc(self, nodes_num):
        data = {
            '350M': {
                8: 26687.8,
                10: 22878.3,
                12: 22220.3,
                14: 19429.2,
                16: 15269.1,
                18: 15421.1,
                20: 12574.5,
                
                22: 17573.8,
                24: 10325.2,
                26: 44444,
                28: 40000,
                30: 33333,
                32: 30000,
            },
            '1.3B': {
                8: 79764.2,
                10: 58399.3,
                12: 54330.2,
                14: 50659.9,
                16: 40158.2,
                18: 40333.5,
                20: 32901.5,
                
                22: 37698.7,
                24: 27164.4,
                26: 44444,
                28: 40000,
                30: 33333,
                32: 30000,
            },
            '2.7B': {
                8: 206968.6,
                10: 119983.1,
                12: 87746.7,
                14: 73101.7,
                16: 70696.4,
                18: 60015.1,
                20: 61319.8,
                
                22: 52594.6,
                24: 50000,
                26: 44444,
                28: 40000,
                30: 33333,
                32: 30000,
            },
            '6.7B': {
                8: 99700,
                10: 88888,
                12: 84444,
                14: 77777,
                16: 70000,
                18: 66666,
                20: 60000,
                22: 55555,
                24: 50000,
                26: 44444,
                28: 40000,
                30: 33333,
                32: 30000,
            },
            '13B': {
                8: 99700,
                10: 88888,
                12: 84444,
                14: 77777,
                16: 70000,
                18: 66666,
                20: 60000,
                22: 55555,
                24: 50000,
                26: 44444,
                28: 40000,
                30: 33333,
                32: 30000,
            },
        }
        gloo_decrease_time = {
            '350M': 3000,
            '1.3B': 11500,
            '2.7B': 23884,
            '6.7B': 59270,
            '13B': 115000,
        }
        if data[self.model_size].get(nodes_num) is not None:
            return data[self.model_size][nodes_num] - gloo_decrease_time[self.model_size] / (nodes_num // 8)
        else:
            return data[self.model_size][nodes_num - nodes_num % 2] - gloo_decrease_time[self.model_size] / (nodes_num // 8)