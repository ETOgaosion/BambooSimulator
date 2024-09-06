
from simulation_oobleck.simulator import Simulator
import math
import csv
import statistics

class MySimulator(Simulator):
    def __init__(self, seed=None, start_hour=None,
                 model='GPT-3', model_size='350M', spot_instance_trace='traces/p3-trace-16.csv', performance_log_interval=5, generate_addition_probabilities=False, removal_probability=None, generate_graphs=False):
        super().__init__(seed, start_hour, model, model_size, spot_instance_trace, performance_log_interval, generate_addition_probabilities, removal_probability, generate_graphs)
    
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
    
        self.on_demand_num_instances = math.ceil(calculate_avg_nodes(spot_instance_trace))
        
        self.on_demand_cost = self.on_demand_num_instances * self.on_demand_cost_per_hour
        self.on_demand_performance = (self.global_batch_size * self.on_demand_num_instances) / self.simulate_iteration_delta_calc(self.on_demand_num_instances)
        self.on_demand_value = self.on_demand_performance / self.on_demand_cost

    def reconfigure_delta(self, last_instances_num, new_instances_num) -> int:
        # reconfigure time (ms)
        reconfigure_map = {
            "350M": {
                8:  {  9: 32853, 10: 32853,},
                9:  { 10: 32853,},
                10: { 11: 32261, 12: 32853,},
                11: { 12: 32261, 13: 31845,},
                12: { 13: 31845, 14: 31845,},
                13: { 14: 31845,},
                14: { 15: 7157, 16: 7157, 17: 6456, 18: 6456,},
                15: { 16: 7157, 17: 6456, 18: 6456, 21: 8369,},
                16: { 17: 6456, 18: 6456, 19: 7097, 20: 7097,},
                17: { 18: 6456, 20: 7097,},
                18: { 19: 7097, 20: 7097, 21: 8369, 22: 8369,},
                19: { 20: 7097, 21: 8369, 22: 8369, 23: 6775,},
                20: { 21: 8369, 22: 8369, 24: 6775,},
                21: { 22: 8369, 23: 8369, 24: 6775, 25: 6775, 29: 6775,},
                22: { 23: 6775, 24: 6775, 28: 6775,},
                23: { 24: 6775, 25: 6775, 26: 6775, 27: 6775, 30: 6775,},
                24: { 25: 6775,},
                25: { 26: 6775, 27: 6775, 28: 6775, 31: 6775,},
                26: { 27: 6775, 28: 6775, 29: 6775, 31: 6775, 32: 6775,},
                27: { 28: 6775, 29: 6775, 31: 6775,},
                28: { 29: 6775, 31: 6775, 32: 6775,},
                29: { 30: 6775, 31: 6775, 32: 6775,},
                30: { 31: 6775, 32: 6775,},
                31: { 32: 6775,},
            },
            "1.3B": {
                8:  {  9: 32853, 10: 32853,},
                9:  { 10: 32853,},
                10: { 11: 32261, 12: 32853,},
                11: { 12: 32261, 13: 31845,},
                12: { 13: 31845, 14: 31845,},
                13: { 14: 31845,},
                14: { 15: 7157, 16: 7157, 17: 6456, 18: 6456,},
                15: { 16: 7157, 17: 6456, 18: 6456, 21: 8369,},
                16: { 17: 6456, 18: 6456, 19: 7097, 20: 7097,},
                17: { 18: 6456, 20: 7097,},
                18: { 19: 7097, 20: 7097, 21: 8369, 22: 8369,},
                19: { 20: 7097, 21: 8369, 22: 8369, 23: 6775,},
                20: { 21: 8369, 22: 8369, 24: 6775,},
                21: { 22: 8369, 23: 8369, 24: 6775, 25: 6775, 29: 6775,},
                22: { 23: 6775, 24: 6775, 28: 6775,},
                23: { 24: 6775, 25: 6775, 26: 6775, 27: 6775, 30: 6775,},
                24: { 25: 6775,},
                25: { 26: 6775, 27: 6775, 28: 6775, 31: 6775,},
                26: { 27: 6775, 28: 6775, 29: 6775, 31: 6775, 32: 6775,},
                27: { 28: 6775, 29: 6775, 31: 6775,},
                28: { 29: 6775, 31: 6775, 32: 6775,},
                29: { 30: 6775, 31: 6775, 32: 6775,},
                30: { 31: 6775, 32: 6775,},
                31: { 32: 6775,},
            },
            "2.7B": {
                8:  {  9: 32853, 10: 32853,},
                9:  { 10: 32853,},
                10: { 11: 32261, 12: 32853,},
                11: { 12: 32261, 13: 31845,},
                12: { 13: 31845, 14: 31845,},
                13: { 14: 31845,},
                14: { 15: 7157, 16: 7157, 17: 6456, 18: 6456,},
                15: { 16: 7157, 17: 6456, 18: 6456, 21: 8369,},
                16: { 17: 6456, 18: 6456, 19: 7097, 20: 7097,},
                17: { 18: 6456, 20: 7097,},
                18: { 19: 7097, 20: 7097, 21: 8369, 22: 8369,},
                19: { 20: 7097, 21: 8369, 22: 8369, 23: 6775,},
                20: { 21: 8369, 22: 8369, 24: 6775,},
                21: { 22: 8369, 23: 8369, 24: 6775, 25: 6775, 29: 6775,},
                22: { 23: 6775, 24: 6775, 28: 6775,},
                23: { 24: 6775, 25: 6775, 26: 6775, 27: 6775, 30: 6775,},
                24: { 25: 6775,},
                25: { 26: 6775, 27: 6775, 28: 6775, 31: 6775,},
                26: { 27: 6775, 28: 6775, 29: 6775, 31: 6775, 32: 6775,},
                27: { 28: 6775, 29: 6775, 31: 6775,},
                28: { 29: 6775, 31: 6775, 32: 6775,},
                29: { 30: 6775, 31: 6775, 32: 6775,},
                30: { 31: 6775, 32: 6775,},
                31: { 32: 6775,},
            },
            "6.7B": {
                8:  {  9: 32853, 10: 32853,},
                9:  { 10: 32853,},
                10: { 11: 32261, 12: 32853,},
                11: { 12: 32261, 13: 31845,},
                12: { 13: 31845, 14: 31845,},
                13: { 14: 31845,},
                14: { 15: 7157, 16: 7157, 17: 6456, 18: 6456,},
                15: { 16: 7157, 17: 6456, 18: 6456, 21: 8369,},
                16: { 17: 6456, 18: 6456, 19: 7097, 20: 7097,},
                17: { 18: 6456, 20: 7097,},
                18: { 19: 7097, 20: 7097, 21: 8369, 22: 8369,},
                19: { 20: 7097, 21: 8369, 22: 8369, 23: 6775,},
                20: { 21: 8369, 22: 8369, 24: 6775,},
                21: { 22: 8369, 23: 8369, 24: 6775, 25: 6775, 29: 6775,},
                22: { 23: 6775, 24: 6775, 28: 6775,},
                23: { 24: 6775, 25: 6775, 26: 6775, 27: 6775, 30: 6775,},
                24: { 25: 6775,},
                25: { 26: 6775, 27: 6775, 28: 6775, 31: 6775,},
                26: { 27: 6775, 28: 6775, 29: 6775, 31: 6775, 32: 6775,},
                27: { 28: 6775, 29: 6775, 31: 6775,},
                28: { 29: 6775, 31: 6775, 32: 6775,},
                29: { 30: 6775, 31: 6775, 32: 6775,},
                30: { 31: 6775, 32: 6775,},
                31: { 32: 6775,},
            },
            "13B": {
                8:  {  9: 32853, 10: 32853,},
                9:  { 10: 32853,},
                10: { 11: 32261, 12: 32853,},
                11: { 12: 32261, 13: 31845,},
                12: { 13: 31845, 14: 31845,},
                13: { 14: 31845,},
                14: { 15: 7157, 16: 7157, 17: 6456, 18: 6456,},
                15: { 16: 7157, 17: 6456, 18: 6456, 21: 8369,},
                16: { 17: 6456, 18: 6456, 19: 7097, 20: 7097,},
                17: { 18: 6456, 20: 7097,},
                18: { 19: 7097, 20: 7097, 21: 8369, 22: 8369,},
                19: { 20: 7097, 21: 8369, 22: 8369, 23: 6775,},
                20: { 21: 8369, 22: 8369, 24: 6775,},
                21: { 22: 8369, 23: 8369, 24: 6775, 25: 6775, 29: 6775,},
                22: { 23: 6775, 24: 6775, 28: 6775,},
                23: { 24: 6775, 25: 6775, 26: 6775, 27: 6775, 30: 6775,},
                24: { 25: 6775,},
                25: { 26: 6775, 27: 6775, 28: 6775, 31: 6775,},
                26: { 27: 6775, 28: 6775, 29: 6775, 31: 6775, 32: 6775,},
                27: { 28: 6775, 29: 6775, 31: 6775,},
                28: { 29: 6775, 31: 6775, 32: 6775,},
                29: { 30: 6775, 31: 6775, 32: 6775,},
                30: { 31: 6775, 32: 6775,},
                31: { 32: 6775,},
            },
        }

        assert last_instances_num != new_instances_num, f'last_instances_num: {last_instances_num}, new_instances_num: {new_instances_num} should be different'
        if last_instances_num > new_instances_num:
            last_instances_num, new_instances_num = new_instances_num, last_instances_num
        assert reconfigure_map[self.model_size].get(last_instances_num) is not None, f'last_instances_num: {last_instances_num} is not supported'
        assert reconfigure_map[self.model_size][last_instances_num].get(new_instances_num) is not None, f'last_instances_num: {last_instances_num}, new_instances_num: {new_instances_num} is not supported'
        reconfigure_time = reconfigure_map[self.model_size][last_instances_num][new_instances_num]
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
        