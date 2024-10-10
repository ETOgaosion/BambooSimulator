
from simulation_varu.simulator import Simulator
import math
import csv
import statistics

class MySimulator(Simulator):
    def __init__(self, seed=None, start_hour=None,
                 model='GPT-3', model_size='350M', spot_instance_desired_capacity=24, pipeline_parallel_size=2, ckpt_steps=100, spot_instance_trace='traces/p3-trace-16.csv', performance_log_interval=1, runnable_instances=None, generate_addition_probabilities=False, removal_probability=None, generate_graphs=False):
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

    def checkpoint_load_delta(self):
        # checkpoint load time
        data = {
            '350M': {
                8: 42475.43168,
                10: 33975.31867,
                12: 77950.89817,
                14: 35362.89454,
                16: 115614.7542,
                18: 80279.53172,
                20: 152853.5693,
                
                22: 28579.37741,
                24: 30014.53805,
                26: 1,
                28: 1,
                30: 1,
                32: 1,
            },
            '1.3B': {
                8: 139524.0681,
                10: 132032.9852,
                12: 282174.2513,
                14: 156121.9044,
                16: 418040.9725,
                18: 311971.0498,
                20: 553184.2401,
                
                22: 115967.1862,
                24: 30006.22892,
                26: 1,
                28: 1,
                30: 1,
                32: 1,
            },
            '2.7B': {
                8: 120466.6085,
                10: 302239.511,
                12: 325951.894,
                14: 323475.5192,
                16: 405715.4648,
                18: 587177.3295,
                20: 799947.7508,
                
                22: 200233.2916,
                24: 114042.3822,
                26: 1,
                28: 1,
                30: 1,
                32: 1,
            },
        }
        return data[self.model_size][self.data_parallel_size * self.pipeline_parallel_size] / 10

    def checkpoint_save_delta(self):
        # checkpoint load time
        data = {
            '350M': {
                8: 4603.884697,
                10: 9091.940403,
                12: 3110.169411,
                14: 12759.67813,
                16: 30012.20202,
                18: 17680.86052,
                20: 3026.195765,
                
                22: 28579.37741,
                24: 30014.53805,
                26: 1,
                28: 1,
                30: 1,
                32: 1,
            },
            '1.3B': {
                8: 30004.38666,
                10: 32123.32082,
                12: 10173.39659,
                14: 58078.09949,
                16: 30006.00767,
                18: 61008.61573,
                20: 30024.8394,
                
                22: 115967.1862,
                24: 30006.22892,
                26: 1,
                28: 1,
                30: 1,
                32: 1,
            },
            '2.7B': {
                8: 174420.1455,
                10: 77729.68721,
                12: 113812.7,
                14: 131950.9952,
                16: 174069.0582,
                18: 112645.9255,
                20: 77429.51131,
                
                22: 200233.2916,
                24: 114042.3822,
                26: 1,
                28: 1,
                30: 1,
                32: 1,
            },
        }
        return data[self.model_size][self.data_parallel_size * self.pipeline_parallel_size] / 10

    def fallback_delta(self):
        return (self.num_iterations_complete % self.ckpt_steps + 1 / 2) * self.simulate_iteration_delta_calc(self.data_parallel_size * self.pipeline_parallel_size)

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