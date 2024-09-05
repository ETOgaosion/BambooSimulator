import threading
import pprint

from simulation_adaptdnn.api import main as adaptdnn_main
from simulation_oobleck_16.api import main as oobleck_main
from simulation_checkpoint.api import main as ckpt_main

def execute_main(main_func, args):
    main_func(args)

systems = ['checkpoint', 'oobleck', 'adaptdnn']
system_funcs = {
    'checkpoint': ckpt_main,
    'adaptdnn': adaptdnn_main,
    'oobleck': oobleck_main,
}
model_sizes = ['350M', '1.3B', '2.7B']
traces = ['g4dn', 'p3']
total_args = []
args = ['--generate-graphs', '--spot-instance-trace', 'traces/', '--model-size']

for model_size in model_sizes:
    for trace in traces:
        args[2] += (trace + '-trace-16.csv')
        total_args.append(args + [model_size])
        args[2] = 'traces/'

for system in systems:
    for args in total_args:
        execute_main(system_funcs[system], args)

print('All done!')