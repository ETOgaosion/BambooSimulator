import threading
import pprint
import os

from simulation_bamboo_20.api import main as bamboo_main
from simulation_livepipe_red1_20.api import main as livepipe_red1_main
from simulation_livepipe_red2_20.api import main as livepipe_red2_main
from simulation_oobleck_20.api import main as oobleck_main
from simulation_oobleck_opt_20.api import main as oobleck_opt_main
from simulation_varu_20.api import main as varu_main

from traces.handler.trace_freq_constructor import generate_trace, write_trace

def execute_main(main_func, args):
    main_func(args)

def execute_all_prob(probabilities=[0.2], spot_instance_desired_capacity=20, performance_log_interval_map={'350M': {0.1: 1, 0.2: 1}, '1.3B': {0.1: 1, 0.2: 1}, '2.7B': {0.1: 1, 0.2: 1}}):
    systems = ['bamboo', 'livepipe_red1', 'livepipe_red2', 'oobleck', 'oobleck_opt', 'varu']
    system_funcs = {
        'bamboo': bamboo_main,
        'livepipe_red1': livepipe_red1_main,
        'livepipe_red2': livepipe_red2_main,
        'oobleck': oobleck_main,
        'oobleck_opt': oobleck_opt_main,
        'varu': varu_main
    }
    model_sizes = ['350M', '1.3B', '2.7B']
    total_args = []
    args = ['--generate-graphs', '--removal-probability', '0.2', '--performace-log-interval', '5', '--spot-instance-desired-capacity', str(spot_instance_desired_capacity), '--model-size']
    for model_size in model_sizes:
        for prob in probabilities:
            args[2] = str(prob)
            args[5] = str(performance_log_interval_map[model_size][prob])
            total_args.append(args + [model_size])

    for system in systems:
        for args in total_args:
            if system == 'bamboo' and args[-1] != '350M':
                continue
            if system == 'varu' and args[-1] == '6.7B':
                continue
            execute_main(system_funcs[system], args)

def execute_all_freq(spot_instance_desired_capacity=20, performance_log_interval_map={'350M': {'6h': 1, '1h': 1, '10m': 1, '5m': 1, '2m': 1, '1m': 1}, '1.3B': {'6h': 1, '1h': 1, '10m': 1, '5m': 1, '2m': 1, '1m': 1}, '2.7B': {'6h': 1, '1h': 1, '10m': 1, '2m': 1, '5m': 1, '1m': 1}}):
    # systems = ['oobleck', 'varu']
    systems = ['bamboo', 'livepipe_red1', 'livepipe_red2', 'oobleck', 'oobleck_opt', 'varu']
    system_funcs = {
        'bamboo': bamboo_main,
        'livepipe_red1': livepipe_red1_main,
        'livepipe_red2': livepipe_red2_main,
        'oobleck': oobleck_main,
        'oobleck_opt': oobleck_opt_main,
        'varu': varu_main
    }
    model_sizes = ['350M', '1.3B', '2.7B']
    # model_sizes = ['2.7B']
    # traces = ['2m']
    traces = ['1h', '10m', '5m', '2m', '1m']
    durations = {'6h': 6*60*60, '1h': 60*60, '10m': 10*60, '5m': 5*60, '2m': 2*60, '1m': 1*60}
    for trace in traces:
        if os.path.exists(f'traces/{trace}-trace-{spot_instance_desired_capacity}.csv'):
            continue
        trace = generate_trace(spot_instance_desired_capacity, durations[trace])
        write_trace(trace, f'traces/{trace}-trace-{spot_instance_desired_capacity}.csv')
    total_args = []
    args = ['--generate-graphs', '--spot-instance-trace', 'traces/', '--performace-log-interval', '5', '--spot-instance-desired-capacity', str(spot_instance_desired_capacity), '--duration', '', '--model-size']
    for model_size in model_sizes:
        for trace in traces:
            args[4] = str(performance_log_interval_map[model_size][trace])
            args[2] += f'{trace}-trace-{spot_instance_desired_capacity}.csv'
            args[8] = str(durations[trace] * (spot_instance_desired_capacity // 2))
            total_args.append(args + [model_size])
            args[2] = 'traces/'

    for system in systems:
        for args in total_args:
            print(f'start execute {system} with args: {args}')
            if system == 'bamboo' and args[-1] != '350M':
                continue
            if system == 'varu' and args[-1] == '6.7B':
                continue
            if ('oobleck' in system) and '1m' in args[2] and args[-1] == '2.7B':
                continue
            execute_main(system_funcs[system], args)
    

def execute_all(spot_instance_desired_capacity=20, performance_log_interval_map={'350M': {'g4dn': 1, 'p3': 1}, '1.3B': {'g4dn': 1, 'p3': 1}, '2.7B': {'g4dn': 1, 'p3': 1}}):
    # systems = ['livepipe_red1']
    systems = ['bamboo', 'livepipe_red1', 'livepipe_red2', 'oobleck', 'oobleck_opt', 'varu']
    system_funcs = {
        'bamboo': bamboo_main,
        'livepipe_red1': livepipe_red1_main,
        'livepipe_red2': livepipe_red2_main,
        'oobleck': oobleck_main,
        'oobleck_opt': oobleck_opt_main,
        'varu': varu_main
    }
    model_sizes = ['350M', '1.3B', '2.7B']
    traces = ['g4dn', 'p3']
    total_args = []
    args = ['--generate-graphs', '--spot-instance-trace', 'traces/', '--performace-log-interval', '5', '--spot-instance-desired-capacity', str(spot_instance_desired_capacity), '--model-size']
    for model_size in model_sizes:
        for trace in traces:
            args[4] = str(performance_log_interval_map[model_size][trace])
            args[2] += (trace + '-trace-8-20.csv')
            total_args.append(args + [model_size])
            args[2] = 'traces/'

    for system in systems:
        for args in total_args:
            if system == 'bamboo' and args[-1] != '350M':
                continue
            if system == 'varu' and args[-1] == '6.7B':
                continue
            execute_main(system_funcs[system], args)

def main(which='trace'):
    if which == 'trace':
        execute_all()
    else:
        execute_all_freq()
    print('All done!')