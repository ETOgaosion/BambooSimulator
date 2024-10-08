import threading
import pprint
import os

from simulation_bamboo.api import main as bamboo_main
from simulation_livepipe_red1_20.api import main as livepipe_red1_main
from simulation_livepipe_red2_20.api import main as livepipe_red2_main
from simulation_oobleck_20.api import main as oobleck_main
from simulation_varu_20.api import main as varu_main

from traces.handler.trace_freq_constructor import generate_trace, write_trace

def execute_main(main_func, args):
    main_func(args)

def execute_all_prob(probabilities=[0.2], spot_instance_desired_capacity=24, performance_log_interval_map={'350M': {0.1: 1, 0.2: 1}, '1.3B': {0.1: 1, 0.2: 1}, '2.7B': {0.1: 1, 0.2: 1}}):
    systems = ['livepipe_red1', 'livepipe_red2', 'oobleck', 'varu']
    system_funcs = {
        'bamboo': bamboo_main,
        'livepipe_red1': livepipe_red1_main,
        'livepipe_red2': livepipe_red2_main,
        'oobleck': oobleck_main,
        'varu': varu_main
    }
    model_sizes = ['350M', '1.3B', '2.7B']
    total_args = []
    args = ['--generate-graphs', '--removal-probability', '0.2', '--performace-log-interval', '5', '--spot-instance-desired-capacity', '24', '--model-size']
    for model_size in model_sizes:
        for prob in probabilities:
            args[2] = str(prob)
            args[5] = str(performance_log_interval_map[model_size][prob])
            args[7] = str(spot_instance_desired_capacity)
            total_args.append(args + [model_size])

    for system in systems:
        for args in total_args:
            if system == 'bamboo' and args[-1] != '350M':
                continue
            if system == 'varu' and args[-1] == '6.7B':
                continue
            execute_main(system_funcs[system], args)

def execute_all_freq(spot_instance_desired_capacity=24, performance_log_interval_map={'350M': {'6h': 1, '1h': 1, '350M': 1}, '1.3B': {'6h': 1, '1h': 1, '350M': 1}, '2.7B': {'6h': 1, '1h': 1, '350M': 1}}):
    systems = ['livepipe_red1', 'livepipe_red2', 'oobleck', 'varu']
    system_funcs = {
        'bamboo': bamboo_main,
        'livepipe_red1': livepipe_red1_main,
        'livepipe_red2': livepipe_red2_main,
        'oobleck': oobleck_main,
        'varu': varu_main
    }
    model_sizes = ['350M', '1.3B', '2.7B']
    traces = ['6h', '1h', '10m', '5m']
    durations = {'6h': 6*60*60, '1h': 60*60, '10m': 10*60, '5m': 5*60}
    for k, duration in enumerate(durations):
        if os.path.exists(f'traces/{duration}-trace-{spot_instance_desired_capacity}.csv'):
            continue
        trace = generate_trace(24, duration)
        write_trace(trace, f'traces/{duration}-trace-{spot_instance_desired_capacity}.csv')
    for k, duration in enumerate(durations):
        durations[k] = duration * (spot_instance_desired_capacity // 2)
    total_args = []
    args = ['--generate-graphs', '--spot-instance-trace', 'traces/', '--performace-log-interval', '5', '--spot-instance-desired-capacity', '24', '--duration', '', '--model-size']
    for model_size in model_sizes:
        for trace in traces:
            args[4] = str(performance_log_interval_map[model_size][trace])
            args[2] += (trace + f'trace-{spot_instance_desired_capacity}-{trace}.csv')
            args[6] = str(spot_instance_desired_capacity)
            args[8] = str(durations[trace])
            total_args.append(args + [model_size])
            args[2] = 'traces/'

    for system in systems:
        for args in total_args:
            if system == 'bamboo' and args[-1] != '350M':
                continue
            if system == 'varu' and args[-1] == '6.7B':
                continue
            execute_main(system_funcs[system], args)
    

def execute_all(spot_instance_desired_capacity=24, performance_log_interval_map={'350M': {'g4dn': 1, 'p3': 1}, '1.3B': {'g4dn': 1, 'p3': 1}, '2.7B': {'g4dn': 1, 'p3': 1}}):
    systems = ['varu', 'livepipe_red1', 'livepipe_red2', 'oobleck']
    system_funcs = {
        'bamboo': bamboo_main,
        'livepipe_red1': livepipe_red1_main,
        'livepipe_red2': livepipe_red2_main,
        'oobleck': oobleck_main,
        'varu': varu_main
    }
    model_sizes = ['350M', '1.3B', '2.7B']
    traces = ['g4dn', 'p3']
    total_args = []
    args = ['--generate-graphs', '--spot-instance-trace', 'traces/', '--performace-log-interval', '5', '--spot-instance-desired-capacity', '24', '--model-size']
    for model_size in model_sizes:
        for trace in traces:
            args[4] = str(performance_log_interval_map[model_size][trace])
            args[2] += (trace + '-trace-8-20.csv')
            args[6] = str(spot_instance_desired_capacity)
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
        execute_all_prob()
    print('All done!')