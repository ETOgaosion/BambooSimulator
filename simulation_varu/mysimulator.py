
from simulation_varu.simulator import Simulator
import math
import csv
import statistics

class MySimulator(Simulator):
    def __init__(self, seed=None, start_hour=None,
                 model='GPT-3', model_size='350M', spot_instance_desired_capacity=24, pipeline_parallel_size=4, ckpt_steps=10000, spot_instance_trace='traces/p3-trace-16.csv', performance_log_interval=5, runnable_instances=None, generate_addition_probabilities=False, removal_probability=None, generate_graphs=False):
        super().__init__(seed, start_hour, model, model_size, spot_instance_desired_capacity, pipeline_parallel_size, ckpt_steps, spot_instance_trace, performance_log_interval, runnable_instances, generate_addition_probabilities, removal_probability, generate_graphs)
    
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
    
        self.on_demand_num_instances = int(math.pow(2, math.ceil(math.log2(calculate_avg_nodes(spot_instance_trace)))))
        
        self.on_demand_cost = self.on_demand_num_instances * self.on_demand_cost_per_hour
        self.on_demand_performance = (self.global_batch_size * self.on_demand_num_instances) / self.simulate_iteration_delta_calc(self.on_demand_num_instances)
        self.on_demand_value = self.on_demand_performance / self.on_demand_cost
        
    def checkpoint_delta(self):
        data = {
            '350M': {
                8: 0.5,
                10: 0.5,
                12: 0.5,
                14: 0.5,
                16: 0.5,
                18: 0.5,
                20: 0.5,
                22: 0.5,
                24: 0.5,
                26: 0.5,
                28: 0.5,
                30: 0.5,
                32: 0.5,
            },
            '1.3B': {
                8: 0.5,
                10: 0.5,
                12: 0.5,
                14: 0.5,
                16: 0.5,
                18: 0.5,
                20: 0.5,
                22: 0.5,
                24: 0.5,
                26: 0.5,
                28: 0.5,
                30: 0.5,
                32: 0.5,
            },
            '2.7B': {
                8: 0.5,
                10: 0.5,
                12: 0.5,
                14: 0.5,
                16: 0.5,
                18: 0.5,
                20: 0.5,
                22: 0.5,
                24: 0.5,
                26: 0.5,
                28: 0.5,
                30: 0.5,
                32: 0.5,
            },
        }
        return data[self.model_size][self.data_parallel_size * self.pipeline_parallel_size]

    def checkpoint_load_delta(self):
        # checkpoint load time
        return self.checkpoint_delta()

    def checkpoint_save_delta(self):
        # checkpoint load time
        return self.checkpoint_delta()

    def simulate_iteration_delta(self):
        # iteration time
        self.iteration_delta = self.simulate_iteration_delta_calc(self.data_parallel_size * self.pipeline_parallel_size)
    
    def simulate_iteration_delta_calc(self, nodes_num):
        data = {
            '350M': {
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
            '1.3B': {
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
            '2.7B': {
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
        if data[self.model_size].get(nodes_num) is not None:
            return data[self.model_size][nodes_num]
        else:
            return data[self.model_size][int(math.pow(2, math.ceil(math.log2(nodes_num))))]