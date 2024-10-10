
from simulation_varu.simulator import Simulator
import math
import csv
import statistics

class MySimulator(Simulator):
    def __init__(self, seed=None, start_hour=None,
                 model='GPT-3', model_size='350M', spot_instance_desired_capacity=24, pipeline_parallel_size=2, ckpt_steps=100, spot_instance_trace='traces/p3-trace-16.csv', performance_log_interval=5, runnable_instances=None, generate_addition_probabilities=False, removal_probability=None, generate_graphs=False):
        super().__init__(seed, start_hour, model, model_size, spot_instance_desired_capacity, pipeline_parallel_size, ckpt_steps, spot_instance_trace, performance_log_interval, runnable_instances, generate_addition_probabilities, removal_probability, generate_graphs)
    
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
        
    def checkpoint_delta(self):
        data = {
            '350M': {
                8: 4296.147108,
                10: 9277.608871,
                12: 3121.950388,
                14: 14656.55994,
                16: 30005.0838,
                18: 17675.45199,
                20: 2982.938766,
                22: 28579.37741,
                24: 30014.53805,
                26: 1,
                28: 1,
                30: 1,
                32: 1,
            },
            '1.3B': {
                8: 30004.92954,
                10: 32925.54379,
                12: 30006.79803,
                14: 56444.9091,
                16: 30004.97913,
                18: 57500.74387,
                20: 30005.11837,
                22: 115967.1862,
                24: 30006.22892,
                26: 1,
                28: 1,
                30: 1,
                32: 1,
            },
            '2.7B': {
                8: 149084.1184,
                10: 105098.3019,
                12: 114498.944,
                14: 150447,
                16: 109499.6846,
                18: 142304.4288,
                20: 77322.00456,
                22: 200233.2916,
                24: 114042.3822,
                26: 1,
                28: 1,
                30: 1,
                32: 1,
            },
        }
        return data[self.model_size][self.data_parallel_size * self.pipeline_parallel_size]

    def checkpoint_load_delta(self):
        # checkpoint load time
        fallback_delta = (self.num_iterations_complete % self.check_pt_steps + 1 / 2) * self.simulate_iteration_delta_calc(self.data_parallel_size * self.pipeline_parallel_size)
        self.delta_fallback += fallback_delta
        return self.checkpoint_delta() + fallback_delta

    def checkpoint_save_delta(self):
        # checkpoint load time
        return self.checkpoint_delta()

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
        if data[self.model_size].get(nodes_num) is not None:
            return data[self.model_size][nodes_num]
        else:
            return data[self.model_size][int(math.pow(2, math.ceil(math.log2(nodes_num))))]