import threading
import pprint

from simulation_bamboo.api import main as bamboo_main
from simulation_nore.api import main as nore_main
from simulation_oobleck.api import main as oobleck_main
from simulation_varu.api import main as varu_main

def execute_main(main_func, args):
    main_func(args)

def execute_all_prob(performance_log_interval_map={'350M': {'g4dn': 1, 'p3': 1}, '1.3B': {'g4dn': 1, 'p3': 1}, '2.7B': {'g4dn': 1, 'p3': 1}}):
    systems = ['bamboo', 'nore', 'oobleck', 'varu']
    system_funcs = {
        'bamboo': bamboo_main,
        'nore': nore_main,
        'oobleck': oobleck_main,
        'varu': varu_main
    }
    model_sizes = ['350M', '1.3B', '2.7B', '6.7B', '13B']
    traces = ['g4dn', 'p3']
    total_args = []
    args = ['--generate-graphs', '--spot-instance-trace', 'traces/', '--performace-log-interval', '5', '--model-size']
    for model_size in model_sizes:
        for trace in traces:
            args[4] = str(performance_log_interval_map[model_size][trace])
            args[2] += (trace + '-trace.csv')
            total_args.append(args + [model_size])
            args[2] = 'traces/'

    for system in systems:
        for args in total_args:
            execute_main(system_funcs[system], args)
    

def execute_all(performance_log_interval_map={'350M': {'g4dn': 1, 'p3': 1}, '1.3B': {'g4dn': 1, 'p3': 1}, '2.7B': {'g4dn': 1, 'p3': 1}}):
    systems = ['bamboo', 'nore', 'oobleck', 'varu']
    system_funcs = {
        'bamboo': bamboo_main,
        'nore': nore_main,
        'oobleck': oobleck_main,
        'varu': varu_main
    }
    model_sizes = ['350M', '1.3B', '2.7B', '6.7B', '13B']
    traces = ['g4dn', 'p3']
    total_args = []
    args = ['--generate-graphs', '--spot-instance-trace', 'traces/', '--performace-log-interval', '5', '--model-size']
    for model_size in model_sizes:
        for trace in traces:
            args[4] = str(performance_log_interval_map[model_size][trace])
            args[2] += (trace + '-trace.csv')
            total_args.append(args + [model_size])
            args[2] = 'traces/'

    for system in systems:
        for args in total_args:
            execute_main(system_funcs[system], args)

def main(which='trace'):
    if which == 'trace':
        execute_all()
    else:
        execute_all_prob()
    print('All done!')