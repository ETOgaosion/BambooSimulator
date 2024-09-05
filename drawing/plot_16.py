import matplotlib.pyplot as plt
import pickle
import os
import dataclasses
import pprint

results = {}
isinstances_xs = {}
isinstances_ys = {}
performances_xs = {}
performances_ys = {}

systems = ['checkpoint', 'oobleck-16', 'adaptdnn']
traces = ['g4dn', 'p3']
model_sizes = ['350M', '1.3B', '2.7B']
color = {'checkpoint': 'turquoise', 'oobleck-16': 'darkviolet', 'adaptdnn': 'coral'}
namemap = {'checkpoint': 'Checkpoint', 'oobleck-16': 'Oobleck', 'adaptdnn': 'Adaptdnn'}
linewidth = {'checkpoint': 1, 'oobleck-16': 1, 'adaptdnn': 1}

@dataclasses.dataclass
class Result:
    removal_probability: float
    preemption_mean: float
    preemption_median: float
    preemption_stdev: float
    lifetime_mean: float
    lifetime_median: float
    lifetime_stdev: float
    num_preemptions: int
    num_fatal_failures: int
    num_iterations_complete: int
    average_instances: float
    average_performance: float
    average_cost: float
    average_value: float

def get_data():
    global isinstances_xs, isinstances_ys, performances_xs, performances_ys
    for system in systems:
        for trace in traces:
            for model_size in model_sizes:
                if not os.path.exists(f'data/{system}/result_{trace}_{model_size}.pkl'):
                    print(f'data/{system}/result_{trace}_{model_size}.pkl does not exist')
                    continue
                key = system + '-' + trace + '-' + model_size
                results[key] = pickle.load(open(f'data/{system}/result_{trace}_{model_size}.pkl', 'rb'))
                if isinstances_xs.get(trace) is None:
                    isinstances_xs[trace] = pickle.load(open(f'data/{system}/instances_xs_{trace}_{model_size}.pkl', 'rb'))
                    isinstances_ys[trace] = pickle.load(open(f'data/{system}/instances_ys_{trace}_{model_size}.pkl', 'rb'))
                performances_xs[key] = pickle.load(open(f'data/{system}/performance_xs_{trace}_{model_size}.pkl', 'rb'))
                performances_ys[key] = pickle.load(open(f'data/{system}/performance_ys_{trace}_{model_size}.pkl', 'rb'))

def plot_instances(axes, trace):
    axes.plot(isinstances_xs[trace], isinstances_ys[trace], linewidth=0.5, color='blue')
    axes.set_ylim(0, 17)
    axes.set_title('Spot Instances Number Over Time')
    axes.set_ylabel('Instances Number')

def plot_performance_together(axes, trace, model_size, with_label, with_x_label):
    for system in systems:
        key = system + '-' + trace + '-' + model_size
        if key not in performances_xs:
            continue
        if with_label:
            axes.plot(performances_xs[key], performances_ys[key], color=color[system], linewidth=linewidth[system], label=namemap[system])
        else:
            axes.plot(performances_xs[key], performances_ys[key], color=color[system], linewidth=linewidth[system])
        if with_x_label:
            axes.set_xlabel('Time (hours)')
        axes.set_ylabel(f'Thrpt (Samples/s)')

def plot_performance():
    get_data()

    fig, axs = plt.subplots(len(model_sizes) + 1, len(traces), figsize=(15, 10))
    
    plot_instances(axs[0, 0], traces[0])
    plot_instances(axs[0, 1], traces[1])
    
    for model_size_i, model_size in enumerate(model_sizes):
        for trace_i, trace in enumerate(traces):
            plot_performance_together(axs[model_size_i + 1, trace_i], trace, model_size, with_label=(model_size_i == 0 and trace_i == 0), with_x_label=(model_size_i == len(model_sizes) - 1))
    
    fig.subplots_adjust(bottom=0.1, hspace=0.4, wspace=0.2)
    fig.legend(loc="lower center", bbox_to_anchor=(0., 0.005, 1., .102), ncol=4, fancybox=True, shadow=True)

    plt.savefig('res/performances_16.png', bbox_inches='tight')

    plt.close()

def plot_total_throughputs():
    total_throughputs = {}
    for system in systems:
        for trace in traces:
            if total_throughputs.get(trace) is None:
                total_throughputs[trace] = []
            key = system + '-' + trace + '-' + '350M'
            assert key in results
            total_throughputs[trace].append(results[key].average_performance)
    pprint.pp(total_throughputs)
    fig, axs = plt.subplots(1, 2, figsize=(10, 5), dpi=1000)
    for trace_i, trace in enumerate(traces):
        for system_i, system in enumerate(systems):
            if trace_i == 0:
                axs[trace_i].bar(system, total_throughputs[trace][system_i], width=0.5, color=color[system], label=namemap[system])
            else:
                axs[trace_i].bar(system, total_throughputs[trace][system_i], width=0.5, color=color[system])
            axs[trace_i].bar_label(axs[trace_i].containers[0], label_type='edge')
        axs[trace_i].set_title(f'Average Throughput in GPT-3 (trace: {trace})')
        axs[trace_i].set_ylabel('Throughput (samples/s)')
    fig.subplots_adjust(bottom=0.15)
    fig.legend(loc="lower center", bbox_to_anchor=(0., 0.005, 1., .102), ncol=4, fancybox=True, shadow=True)
    plt.savefig('res/total_throughputs_16.png', bbox_inches='tight')
    plt.close()

get_data()
plot_performance()
plot_total_throughputs()