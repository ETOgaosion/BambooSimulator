
from simulation.oob_simulator_base import OobSimulatorBase
import math
import csv
import statistics

class OobSimulator(OobSimulatorBase):
    def __init__(self, seed=None, start_hour=None,
                 model='GPT-3', spot_instance_trace='traces/p3-trace-16.csv', generate_addition_probabilities=False, removal_probability=None, generate_graphs=False, start_nodes_num = 8):
        super().__init__(seed, start_hour, model, spot_instance_trace, generate_addition_probabilities, removal_probability, generate_graphs, start_nodes_num)
        
        if model == 'GPT-3':
            # start execution when the number of arrived nodes is 8
            self.start_nodes_num = 8
            # the number of nodes that can be added at a time, bamboo do lazy reconfigure, not reconfig every time
            self.pipeline_parallel_size_target = 2
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
            last_time = 0
            for i in range(1, len(seconds)):
                if operations[i] == 'add':
                    current_nodes += 1
                elif operations[i] == 'remove':
                    current_nodes -= 1
                if seconds[i] != last_time:
                    nodes_samples.extend([current_nodes] * ((seconds[i] - last_time) // 10000))
            return statistics.mean(nodes_samples)
    
        self.on_demand_num_instances = int(math.pow(2, math.ceil(math.log2(calculate_avg_nodes(spot_instance_trace)))))
        
        self.on_demand_cost = self.on_demand_num_instances * self.on_demand_cost_per_hour
        self.on_demand_performance = (self.global_batch_size * self.on_demand_num_instances) / self.simulate_iteration_delta_calc(self.on_demand_num_instances)
        self.on_demand_value = self.on_demand_performance / self.on_demand_cost

    def reconfigure_delta(self) -> int:
        curr_active_instances = self.get_curr_active_instances()
        self.last_active_instances = curr_active_instances
        return 10
        # reconfigure time (ms)
        reconfigure_map = {
            "gpt3_350m": {
                16: {
                    15: 42.1,
                    14: 43.2
                }
            },
            "GPT-3": {
                16: {
                    15: 42.1,
                    14: 43.2
                },
                8: {
                    16: 10,
                },
                14: {
                    16: 10
                }
            }
        }

        curr_active_instances = self.get_curr_active_instances()
        print(f"last: {self.last_active_instances}, curr: {curr_active_instances}")
        reconfigure_time = reconfigure_map[self.model][self.last_active_instances][curr_active_instances]
        self.last_active_instances = curr_active_instances
        
        return reconfigure_time

    def fallback_slowdown(self) -> int:
        # nodes fail and slowdown ration, seems a garbage design
        return 1

    def simulate_iteration_delta(self):
        curr_active_instances = self.get_curr_active_instances()
        # iteration time
        self.iteration_delta = self.simulate_iteration_delta_calc(curr_active_instances)


    def simulate_iteration_delta_calc(self, nodes_num) -> int:
        
        '''
        Returns:
            the iteration time (ms)
        '''
        return 10
        iteration_map = {
            "gpt3_350m": {
                16: 30.2,
                15: 20.1
            },
            "GPT-3": {
                16: 10, 
                15: 10,
                14: 10,
                13: 10,
            }
        }
        return iteration_map[self.model][nodes_num]
        