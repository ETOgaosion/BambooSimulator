import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from matplotlib.font_manager import FontProperties
import pickle
import os
from pathlib import Path
import dataclasses
import pprint
import numpy as np

from execute.execute_all_16 import execute_all

results = {}
isinstances_xs = {}
isinstances_ys = {}
performances_xs = {}
performances_ys = {}
total_throughputs = {}

systems = ['checkpoint', 'oobleck-16', 'adaptdnn']
traces = ['g4dn', 'p3']
model_sizes = ['1.3B', '2.7B']
colormap = {'checkpoint': '#ff7f0e', 'oobleck-16': '#2ca02c', 'adaptdnn': '#1f77b4'}
darkcolormap = {'checkpoint': 'green', 'oobleck-16': 'red', 'adaptdnn': 'blue'}
colors = ['turquoise', 'darkviolet', 'coral']
namemap = {'checkpoint': 'Checkpoint', 'oobleck-16': 'Oobleck', 'adaptdnn': 'Adaptdnn'}
names = ['Checkpoint', 'Oobleck', 'Adaptdnn']
linewidth = {'checkpoint': 1, 'oobleck-16': 1, 'adaptdnn': 1.5}
label_size = 12
font_bold = FontProperties(fname=f'{str(Path.home())}/Library/Fonts/Arial-Unicode-Bold.ttf', size=14, weight= 'bold')
font = FontProperties(fname=f'{str(Path.home())}/Library/Fonts/Arial-Unicode-Regular.ttf', size=label_size)

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

def handle_performances():
    for system in systems:
        for trace in traces:
            for model_size in model_sizes:
                key = system + '-' + trace + '-' + model_size
                performances_x = performances_xs[key]
                performances_y = performances_ys[key]
                new_performace_x = []
                new_performace_y = []
                i, j = 0, 1
                while i < len(performances_x) - 1:
                    j = i + 1
                    while j < len(performances_x) and performances_y[j] == performances_y[i]:
                        j += 1
                    new_performace_x.append((performances_x[i] + performances_x[j - 1]) / 2)
                    new_performace_y.append(performances_y[i])
                    i = j
                performances_xs[key] = new_performace_x
                performances_ys[key] = new_performace_y

def plot_instances(axes, trace, trace_i):
    axes.plot(isinstances_xs[trace], isinstances_ys[trace], linewidth=1, color='blue')
    axes.set_ylim(0, 17)
    axes.set_title(f'弹性实例数量变化 (trace-{trace_i + 1})', fontproperties=font_bold)
    axes.set_yticks(range(0, max(isinstances_ys[trace]) + 1, (max(isinstances_ys[trace]) + 1) // 4))
    axes.set_ylabel('实例数量', fontproperties=font)
    axes.set_xlabel('时间 (h)', fontproperties=font)
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
            axes.set_xlabel(f'时间 (h)', fontproperties=font)
        axes.set_ylabel(f'吞吐量 (samples/s)', fontproperties=font)
        if with_title:
            axes.set_title(f'GPT-3 {model_size} 训练吞吐量变化 (trace-{trace_i + 1})', fontproperties=font_bold)
    axes.set_yticks(range(0, max_y + 1, (max_y + 1) // 4))
    axes.set_ylim(0, axes.get_ylim()[1])
    axes.tick_params(labelsize=label_size)

def plot_performance(file):
    fig, axs = plt.subplots(len(model_sizes) + 1, len(traces), figsize=((len(model_sizes) + 1) * 3, len(traces) * 3.5), dpi=1000)
    
    plot_instances(axs[0, 0], traces[0], 0)
    plot_instances(axs[0, 1], traces[1], 1)
    
    for model_size_i, model_size in enumerate(model_sizes):
        for trace_i, trace in enumerate(traces):
            plot_performance_together(axs[model_size_i + 1, trace_i], trace, trace_i, model_size, with_label=(model_size_i == 0 and trace_i == 0), with_x_label=True, with_title=True)
    
    fig.tight_layout(rect = [0, 0.04, 1, 1])
    fig.legend(loc='lower center', ncol=3, handlelength=1.1, handletextpad=0.001, columnspacing=0.2, handleheight=0, borderaxespad=0.001, prop={'size': label_size}, labelspacing=0.2,frameon=False)

    plt.savefig(file, bbox_inches='tight')

    plt.close()

def plot_performance_vertical(file):
    fig, axs = plt.subplots(len(traces), len(model_sizes) + 1, figsize=(len(traces) * 5, (len(model_sizes) + 1) * 3), dpi=1000)
    
    plot_instances(axs[0, 0], traces[0])
    plot_instances(axs[1, 0], traces[1])
    
    for model_size_i, model_size in enumerate(model_sizes):
        for trace_i, trace in enumerate(traces):
            plot_performance_together(axs[trace_i, model_size_i + 1], trace, model_size, with_label=(model_size_i == 0 and trace_i == 0), with_x_label=(model_size_i == len(model_sizes) - 1), with_title=(model_size_i == ()))
    
    fig.subplots_adjust(bottom=0.1, hspace=0.4, wspace=0.2)
    fig.legend(loc="lower center", bbox_to_anchor=(0., 0.005, 1., .102), ncol=4, fancybox=True, shadow=True)

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

def plot_total_throughputs(file):
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
    plt.savefig(file, bbox_inches='tight')
    plt.close()

def plot_total_throuphts_group_by_traces(file):
    global total_throughputs
    fig, axs = plt.subplots(1, len(model_sizes), figsize=(5 * len(model_sizes), 6), dpi=1000)
    x = np.arange(len(systems))
    width = 0.3
    for model_size_i, model_size in enumerate(model_sizes):
        tt_key = traces[0] + '-' + model_size
        for system_i, system in enumerate(systems):
            if model_size_i == 0:
                rects = axs[model_size_i].bar(x[system_i] - width/2, total_throughputs[tt_key][system_i], width=width, color=colormap[system], label=traces[0] + ' ' + namemap[system])
                axs[model_size_i].set_ylabel('Throughput (samples/s)')
            else:
                rects = axs[model_size_i].bar(x[system_i] - width/2, total_throughputs[tt_key][system_i], width=width, color=colormap[system])
            axs[model_size_i].bar_label(rects, fmt='%d', label_type='edge')
        axs[model_size_i].set_ylim(0, max(total_throughputs[tt_key]) + max(total_throughputs[tt_key]) * 0.1)
        tt_key = traces[1] + '-' + model_size
        for system_i, system in enumerate(systems):
            if model_size_i == 0:
                rects = axs[model_size_i].bar(x[system_i] + width/2, total_throughputs[tt_key][system_i], width=width, color='dark' + darkcolormap[system], label=traces[1] + ' ' + namemap[system])
            else:
                rects = axs[model_size_i].bar(x[system_i] + width/2, total_throughputs[tt_key][system_i], width=width, color='dark' + darkcolormap[system])
            axs[model_size_i].bar_label(rects, fmt='%d', label_type='edge')
        axs[model_size_i].set_ylim(0, max(total_throughputs[tt_key]) + max(total_throughputs[tt_key]) * 0.1)
        axs[model_size_i].set_xticks(x, names)
        axs[model_size_i].set_title(model_size + ' average performances')
    fig.subplots_adjust(bottom=0.2)
    fig.legend(loc="lower center", bbox_to_anchor=(0., 0.005, 1., .102), ncol=3, fancybox=True, shadow=True)
    plt.savefig(file, bbox_inches='tight')
    plt.close()

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
# execute_all(performace_log_interval_map)
get_data()
plot_performance(f'res/performances_16.png')
plot_performance(f'res/performances_16.pdf')
# plot_performance_vertical(f'res/performances_vertical_16.png')
    
# calculate_total_throughputs()
# plot_total_throughputs(f'res/total_throughputs_16.png')
# plot_total_throuphts_group_by_traces('res/total_throughputs_group_by_traces_16.png')

# handle_performances()
# plot_performance('res/performances_modified_16.png')