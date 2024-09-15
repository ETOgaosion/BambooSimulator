import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import pickle
import os
from pathlib import Path
import dataclasses
import pprint

from execute.execute_all import execute_all, execute_all_prob

results = {}
isinstances_xs = {}
isinstances_ys = {}
performances_xs = {}
performances_ys = {}
total_throughputs = {}

systems = ['bamboo', 'varu', 'oobleck', 'nore']
traces = ['g4dn', 'p3']
probabilities = [0.2]
model_sizes = ['350M', '1.3B', '2.7B']
colormap = {'bamboo': 'cyan', 'varu': 'green', 'oobleck': 'blue', 'nore': 'red'}
namemap = {'bamboo': 'Bamboo', 'varu': 'Varu', 'oobleck': 'Oobleck', 'nore': 'Nore'}
linewidth = {'bamboo': 1, 'varu': 1, 'oobleck-16': 1, 'nore': 1.5}
label_size = 12
font_bold = FontProperties(size=14, weight= 'bold')
font = FontProperties(size=label_size)

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

def get_data(use_trace=True):
    global isinstances_xs, isinstances_ys, performances_xs, performances_ys
    for system in systems:
        for model_size in model_sizes:
            if use_trace:
                for trace in traces:
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
            else:
                for prob in probabilities:
                    if not os.path.exists(f'data/{system}/result_prob_{prob}_{model_size}.pkl'):
                        print(f'data/{system}/result_prob_{prob}_{model_size}.pkl')
                        continue
                    key = system + '-' + str(prob) + '-' + model_size
                    results[key] = pickle.load(open(f'data/{system}/result_prob_{prob}_{model_size}.pkl', 'rb'))
                    performances_xs[key] = pickle.load(open(f'data/{system}/performance_xs_prob_{prob}_{model_size}.pkl', 'rb'))
                    performances_ys[key] = pickle.load(open(f'data/{system}/performance_ys_prob_{prob}_{model_size}.pkl', 'rb'))

def plot_instances(axes, trace, trace_i):
    axes.plot(isinstances_xs[trace], isinstances_ys[trace], linewidth=0.5, color='black')
    axes.set_ylim(0, 24)
    axes.set_title(f'Spot Instances Number Over Time (trace-{trace_i + 1})', fontproperties=font_bold)
    axes.set_yticks(range(0, max(isinstances_ys[trace]) + 1, (max(isinstances_ys[trace]) + 1) // 4))
    axes.set_ylabel('Instances Number', fontproperties=font)
    axes.set_xlabel('Time (h)', fontproperties=font)
    axes.tick_params(labelsize=label_size)

def plot_performance_together(axes, trace, trace_i, model_size, with_label, with_x_label, with_title):
    max_y = 0
    for system in systems:
        key = system + '-' + trace + '-' + model_size
        if max_y < max(performances_ys[key]):
            max_y = int(max(performances_ys[key]))
        if key not in performances_xs:
            continue
        if with_label:
            axes.plot(performances_xs[key], performances_ys[key], color=colormap[system], linewidth=linewidth[system], label=namemap[system])
        else:
            axes.plot(performances_xs[key], performances_ys[key], color=colormap[system], linewidth=linewidth[system])
        if with_x_label:
            axes.set_xlabel('Time (hours)', fontproperties=font)
        axes.set_ylabel(f'Thrpt (Samples/s)', fontproperties=font)
        if with_title:
            axes.set_title(f'GPT-3 {model_size} Throuphput Changes (trace-{trace_i + 1})', fontproperties=font_bold)
    axes.set_yticks(range(0, max_y + 1, (max_y + 1) // 4))
    axes.set_ylim(0, axes.get_ylim()[1])
    axes.tick_params(labelsize=label_size)

def plot_performance(files):
    fig, axs = plt.subplots(len(model_sizes) + 1, len(traces), figsize=((len(model_sizes) + 1) * 3, len(traces) * 3.5), dpi=1000)
    
    plot_instances(axs[0, 0], traces[0], 0)
    plot_instances(axs[0, 1], traces[1], 1)
    
    for model_size_i, model_size in enumerate(model_sizes):
        for trace_i, trace in enumerate(traces):
            plot_performance_together(axs[model_size_i + 1, trace_i], trace, trace_i, model_size, with_label=(model_size_i == 0 and trace_i == 0), with_x_label=True, with_title=True)
    
    fig.tight_layout(rect = [0, 0.04, 1, 1])
    fig.legend(loc='lower center', ncol=3, handlelength=1.1, handletextpad=0.001, columnspacing=0.2, handleheight=0, borderaxespad=0.001, prop={'size': label_size}, labelspacing=0.2,frameon=False)

    for file in files:
        plt.savefig(file, bbox_inches='tight')

    plt.close()
    
def calculate_total_throughputs():
    global total_throughputs
    for trace in traces:
        for model_size in model_sizes:
            tt_key = trace + '-' + model_size
            for system in systems:
                if total_throughputs.get(tt_key) is None:
                    total_throughputs[tt_key] = []
                key = system + '-' + trace + '-' + model_size
                assert key in results
                total_throughputs[tt_key].append(results[key].average_performance)
    pprint.pp(total_throughputs)

def plot_total_throughputs(files):
    global total_throughputs
    fig, axs = plt.subplots(len(model_sizes), 1, figsize=(2 * len(model_sizes), 5 * len(traces)), dpi=1000)
    for model_size_i, model_size in enumerate(model_sizes):
        for trace_i, trace in enumerate(traces):
            tt_key = trace + '-' + model_size
            for system_i, system in enumerate(systems):
                if trace_i == 0 and model_size_i == 0:
                    axs[model_size_i].bar(namemap[system] + '\n' + trace, total_throughputs[tt_key][system_i], width=0.3, color=colormap[system], label=namemap[system])
                else:
                    axs[model_size_i].bar(namemap[system] + '\n' + trace, total_throughputs[tt_key][system_i], width=0.3, color=colormap[system])
                axs[model_size_i].bar_label(axs[model_size_i].containers[trace_i * len(systems) + system_i], label_type='edge', fontsize=8)
        axs[model_size_i].set_ylim(0, max(total_throughputs[tt_key]) * 1.2)
        axs[model_size_i].vlines((len(traces) * len(systems) - 1) / 2, axs[model_size_i].get_ylim()[0], axs[model_size_i].get_ylim()[1], linestyles='dashed')
        axs[model_size_i].set_ylabel('Throughput (samples/s)')
        axs[model_size_i].set_xlabel('GPT-3 ' + model_size)
    axs[0].set_title(f'Average Throughput in GPT-3 (left trace: g4dn, right: p3))')
    fig.subplots_adjust(bottom=0.1, hspace=0.4)
    fig.legend(loc="lower center", bbox_to_anchor=(0., 0.005, 1., .102), ncol=4, fancybox=True, shadow=True)
    for file in files:
        plt.savefig(file, bbox_inches='tight')
    plt.close()

performance_log_interval_map_prob = {
    '350M': {0.1: 1, 0.2: 1, 0.4: 1},
    '1.3B': {0.1: 1, 0.2: 1},
    '2.7B': {0.1: 1, 0.2: 1}
}

performace_log_interval_map = {
    '350M': {
        'g4dn': 18,
        'p3': 21,
    },
    '1.3B': {
        'g4dn': 5,
        'p3': 8,
    },
    '2.7B': {
        'g4dn': 2,
        'p3': 5,
    },
}
execute_all_prob(probabilities, 24, performance_log_interval_map_prob)
# execute_all(performace_log_interval_map)
get_data()
plot_performance([f'res/performances_prob.png', f'res/performances_prob.pdf'])
    
calculate_total_throughputs()
plot_total_throughputs([f'res/total_throughputs_prob.png'])

# handle_performances()
# plot_performance('res/performances_modified.png')