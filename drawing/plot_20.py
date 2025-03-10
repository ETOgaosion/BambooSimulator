import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import pickle
import os
from pathlib import Path
import dataclasses
import pprint

from execute.execute_all_20 import execute_all, execute_all_freq, execute_all_prob

systems = ['bamboo', 'varu', 'oobleck', 'livepipe', 'oobleck_opt']
dirs = {'bamboo': 'bamboo-20',  'varu': 'varu-20', 'oobleck': 'oobleck-20', 'oobleck_opt': 'oobleck-opt-20', 'livepipe-red1': 'livepipe-red1-20', 'livepipe-red2': 'livepipe-red2-20', 'livepipe': 'livepipe-red1-20'}
traces = ['g4dn', 'p3']
probabilities = [0.2]
frequencies = ['1h', '2m']
# frequencies = ['1h', '10m', '5m', '2m']
model_sizes = ['350M', '1.3B', '2.7B']
# model_sizes = ['350M', '2.7B']
# colormap = {'bamboo': '#e79397', 'varu': '#e1c855', 'oobleck': '#e07b54', 'livepipe': '#51b1b7'}
# colormap = {'bamboo': '#55b7e6', 'varu': '#193e8f', 'oobleck': '#f09739', 'livepipe': '#e53528'}
colors = ['#ffd093', '#ceaad7', '#ff897e', "#cee64b", '#85ccfd']
# colormap = {'bamboo': '#fcb20a', 'varu': '#c4a5d2', 'oobleck': '#ff897e', 'oobleck_opt': '#7bd331', 'livepipe-red1': '#85ccfd', 'livepipe-red2': '#7391d5', 'livepipe': '#7dc1f3'}
# colormap = {'bamboo': '#f7c97e', 'varu': '#cfafd4', 'oobleck': '#d3e2b7', 'oobleck_opt': '#74aed4', 'livepipe-red1': '#eca8a9', 'livepipe-red2': '#7391d5', 'livepipe': '#eca8a9'}
# colormap = {'bamboo': '#00b19f', 'varu': '#ffbe7a', 'oobleck': '#fa7f6f', 'oobleck_opt': '#b28bd6', 'livepipe-red1': '#17b5e9', 'livepipe-red2': '#7391d5', 'livepipe': '#17b5e9'}
colormap = {'bamboo': '#00b19f', 'varu': '#ffbe7a', 'oobleck': '#fa7f6f', 'oobleck_opt': '#bf55eb', 'livepipe-red1': '#17b5e9', 'livepipe-red2': '#7391d5', 'livepipe': '#17b5e9'}
breakdown_names = ['delta_effective_time', 'delta_checkpointing', 'delta_redundant_computation', 'delta_reconfig', 'delta_fallback']
breakdown_colormap = {'delta_effective_time': '#b99dc6', 'delta_checkpointing': '#7acdaf', 'delta_redundant_computation': '#e78a72', 'delta_reconfig': '#f3ca4d', 'delta_fallback': '#a6d0eb'}
# breakdown_colormap = {'delta_effective_time': '#99cccc', 'delta_checkpointing': '#80b1d3', 'delta_redundant_computation': '#f0988c', 'delta_reconfig': '#456990', 'delta_fallback': '#f7d998'}
# breakdown_colormap = {'delta_effective_time': '#d0e7ed', 'delta_checkpointing': '#e58579', 'delta_redundant_computation': '#d5e48a', 'delta_reconfig': '#9dd0c7', 'delta_fallback': '#9180ac'}
breakdown_namemap = {'delta_effective_time': 'Effective Time', 'delta_checkpointing': 'Save Checkpoint', 'delta_redundant_computation': 'Redundant Computation', 'delta_reconfig': 'Reconfigure', 'delta_fallback': 'Fall Back'}
namemap = {'bamboo': 'Bamboo', 'varu': 'Varuna', 'oobleck': 'Oobleck', 'oobleck_opt': 'Oobleck-opt', 'livepipe-red1': 'LivePipe Red1', 'livepipe-red2': 'LivePipe Red2', 'livepipe': 'LivePipe'}
shortnamemap = {'bamboo': 'Bam', 'varu': 'Varu', 'oobleck': 'Oob', 'oobleck_opt': 'Oob-o', 'livepipe-red1': 'LivePipe Red1', 'livepipe-red2': 'LivePipe Red2', 'livepipe': 'Live'}
linewidth = {'bamboo': 1.5, 'varu': 1.5, 'oobleck': 1.5, 'oobleck_opt': 1.5, 'livepipe-red1': 2, 'livepipe-red2': 2, 'livepipe': 2}
label_size = 14
mid_label_size = 18
small_label_size = 15
large_label_size = 22
avg_linewidth = 0.8
font_bold = FontProperties(size=20, weight= 'bold')
font_large = FontProperties(size=large_label_size)
font_mid = FontProperties(size=mid_label_size)
font = FontProperties(size=label_size)

file_suffix = ['png', 'pdf']

USE_TRACE = 0
USE_FREQUENCY = 1
USE_PROB = 2

results = {}
isinstances_xs = {}
isinstances_ys = {}
performances_xs = {}
performances_ys = {}
total_throughputs = {}
throughputs_ratios = {}
breakdown_results = {}

@dataclasses.dataclass
class Result:
    system_name: str
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
    total_delta: int
    delta_effective_time: int
    delta_checkpointing: int
    delta_redundant_computation: int
    delta_reconfig: int
    delta_fallback: int
    delta_idle_waste: int

def get_data(use_which=USE_TRACE):
    global isinstances_xs, isinstances_ys, performances_xs, performances_ys
    print(f'trace,system_name,model_size,delta_effective_time,delta_checkpointing,delta_redundant_computation,delta_reconfig,delta_fallback')
    for system in systems:
        sys_dir = dirs[system]
        for model_size in model_sizes:
            if use_which == USE_TRACE:
                for trace in traces:
                    if not os.path.exists(f'data/{sys_dir}/result_{trace}_{model_size}.pkl'):
                        # print(f'data/{sys_dir}/result_{trace}_{model_size}.pkl does not exist')
                        continue
                    key = system + '-' + trace + '-' + model_size
                    results[key] = pickle.load(open(f'data/{sys_dir}/result_{trace}_{model_size}.pkl', 'rb'))
                    if isinstances_xs.get(trace) is None:
                        isinstances_xs[trace] = pickle.load(open(f'data/{sys_dir}/instances_xs_{trace}_{model_size}.pkl', 'rb'))
                        isinstances_ys[trace] = pickle.load(open(f'data/{sys_dir}/instances_ys_{trace}_{model_size}.pkl', 'rb'))
                    performances_xs[key] = pickle.load(open(f'data/{sys_dir}/performance_xs_{trace}_{model_size}.pkl', 'rb'))
                    performances_ys[key] = pickle.load(open(f'data/{sys_dir}/performance_ys_{trace}_{model_size}.pkl', 'rb'))
            elif use_which == USE_FREQUENCY:
                for freq in frequencies:
                    if not os.path.exists(f'data/{sys_dir}/result_{freq}_{model_size}.pkl'):
                        # print(f'data/{sys_dir}/result_{freq}_{model_size}.pkl does not exist')
                        continue
                    key = system + '-' + freq + '-' + model_size
                    results[key] = pickle.load(open(f'data/{sys_dir}/result_{freq}_{model_size}.pkl', 'rb'))
                    if isinstances_xs.get(freq) is None:
                        isinstances_xs[freq] = pickle.load(open(f'data/{sys_dir}/instances_xs_{freq}_{model_size}.pkl', 'rb'))
                        isinstances_ys[freq] = pickle.load(open(f'data/{sys_dir}/instances_ys_{freq}_{model_size}.pkl', 'rb'))
                    performances_xs[key] = pickle.load(open(f'data/{sys_dir}/performance_xs_{freq}_{model_size}.pkl', 'rb'))
                    performances_ys[key] = pickle.load(open(f'data/{sys_dir}/performance_ys_{freq}_{model_size}.pkl', 'rb'))
            else:
                for prob in probabilities:
                    if not os.path.exists(f'data/{sys_dir}/result_prob_{prob}_{model_size}.pkl'):
                        # print(f'data/{sys_dir}/result_prob_{prob}_{model_size}.pkl')
                        continue
                    key = system + '-' + str(prob) + '-' + model_size
                    results[key] = pickle.load(open(f'data/{sys_dir}/result_prob_{prob}_{model_size}.pkl', 'rb'))
                    performances_xs[key] = pickle.load(open(f'data/{sys_dir}/performance_xs_prob_{prob}_{model_size}.pkl', 'rb'))
                    performances_ys[key] = pickle.load(open(f'data/{sys_dir}/performance_ys_prob_{prob}_{model_size}.pkl', 'rb'))
    for key, result in results.items():
        total_time = result.delta_effective_time + result.delta_checkpointing + result.delta_redundant_computation + result.delta_reconfig + result.delta_fallback
        breakdown_results[key] = {}
        breakdown_results[key]['delta_effective_time'] = result.delta_effective_time / total_time
        breakdown_results[key]['delta_checkpointing'] = result.delta_checkpointing / total_time + breakdown_results[key]['delta_effective_time']
        breakdown_results[key]['delta_redundant_computation'] = result.delta_redundant_computation / total_time + breakdown_results[key]['delta_checkpointing']
        breakdown_results[key]['delta_reconfig'] = result.delta_reconfig / total_time + breakdown_results[key]['delta_redundant_computation']
        breakdown_results[key]['delta_fallback'] = result.delta_fallback / total_time + breakdown_results[key]['delta_reconfig']
        print(f'{key.split("-")[-2]},{result.system_name},{key.split("-")[-1]},{result.delta_effective_time},{result.delta_checkpointing},{result.delta_redundant_computation},{result.delta_reconfig},{result.delta_fallback}')
        pprint.pp(breakdown_results)

def get_performance_freq(files):
    for freq_i, freq in enumerate(frequencies):
        for model_size_i, model_size in enumerate(model_sizes):
            for system_i, system in enumerate(systems):
                key = system + '-' + freq + '-' + model_size
                print(key, results[key])
    
def calculate_total_throughputs(use_which=USE_TRACE):
    global total_throughputs
    if use_which == USE_TRACE:
        for trace in traces:
            for model_size in model_sizes:
                tt_key = trace + '-' + model_size
                for system in systems:
                    if total_throughputs.get(tt_key) is None:
                        total_throughputs[tt_key] = {}
                    key = system + '-' + trace + '-' + model_size
                    if key not in results:
                        continue
                    total_throughputs[tt_key][system] = results[key].average_performance
    elif use_which == USE_FREQUENCY:
        for freq in frequencies:
            for model_size in model_sizes:
                tt_key = freq + '-' + model_size
                for system in systems:
                    if total_throughputs.get(tt_key) is None:
                        total_throughputs[tt_key] = {}
                    key = system + '-' + freq + '-' + model_size
                    if key not in results:
                        continue
                    total_throughputs[tt_key][system] = results[key].average_performance
    for trace_model, values in total_throughputs.items():
        throughputs_ratios[trace_model] = {}
        for system, value in values.items():
            throughputs_ratios[trace_model][system] = max(values.values()) / value
    # pprint.pp(total_throughputs)
    # pprint.pp(throughputs_ratios)

def plot_instances(file_preffix, index, key, with_title=True):
    fig, axes = plt.subplots(1, 1, figsize=(5, 3), dpi=1000)
    axes.plot(isinstances_xs[key], isinstances_ys[key], linewidth=1, color='black')
    axes.set_ylim(0, 24)
    if with_title:
        axes.set_title(f'Trace {index + 1} Instances Change', fontproperties=font_bold)
    axes.set_xlim(-0.5, 12.5)
    axes.set_xticks(range(0, 13, 4))
    axes.set_yticks(range(0, max(isinstances_ys[key]) + 1, (max(isinstances_ys[key]) + 1) // 4))
    axes.set_ylabel('Instances #', fontproperties=font_large)
    axes.set_xlabel('Time (hours)', fontproperties=font_large)
    axes.tick_params(labelsize=large_label_size)
    fig.tight_layout()
    plt.savefig(f'{file_preffix}-trace-{index}.pdf', bbox_inches='tight')
    plt.savefig(f'{file_preffix}-trace-{index}.png', bbox_inches='tight')
    plt.close()
    

def plot_performance_together(file_preffix, trace, trace_i, model_size, model_size_i, with_label, with_x_label, with_title, with_avg=False):
    fig, axes = plt.subplots(1, 1, figsize=(5, 3), dpi=1000)
    max_y = 0
    for system in systems:
        key = system + '-' + trace + '-' + model_size
        if key not in performances_xs:
            continue
        if max_y < max(performances_ys[key]):
            max_y = int(max(performances_ys[key]))
        # reorder lables
        if with_label:
            if system != 'livepipe':
                axes.plot(performances_xs[key], performances_ys[key], color=colormap[system], linewidth=linewidth[system], label=namemap[system])
            else:
                axes.plot(performances_xs[key], performances_ys[key], color=colormap[system], linewidth=linewidth[system])
        else:
            if system == 'livepipe' and trace_i == 1 and model_size == model_sizes[0]:
                axes.plot(performances_xs[key], performances_ys[key], color=colormap[system], linewidth=linewidth[system], label=namemap[system])
            else:
                axes.plot(performances_xs[key], performances_ys[key], color=colormap[system], linewidth=linewidth[system])
        if with_avg:
            axes.hlines(results[key].average_performance, -0.5, 12.5, linestyles='dotted', color=colormap[system], linewidth=avg_linewidth)
        if with_x_label:
            axes.set_xlabel('Time (hours)', fontproperties=font_large)
        axes.set_ylabel(f'Throughput\n(Samples/s)', fontproperties=font_large)
        if with_title:
            axes.set_title(f'GPT-3 {model_size}', fontproperties=font_bold)
    axes.set_yticks(range(0, max_y + 1, (max_y + 1) // 4))
    axes.set_xticks(range(0, 13, 4))
    axes.set_xlim(-0.5, 12.5)
    axes.set_ylim(0, axes.get_ylim()[1])
    axes.tick_params(labelsize=large_label_size)
    fig.tight_layout()
    plt.savefig(f'{file_preffix}-thrpt-{trace_i}-{model_size_i}.pdf', bbox_inches='tight')
    plt.savefig(f'{file_preffix}-thrpt-{trace_i}-{model_size_i}.png', bbox_inches='tight')
    plt.close()

def plot_performance_trace(files):
    fig, axs = plt.subplots(len(model_sizes) + 1, len(traces), figsize=(len(traces) * 7, (len(model_sizes) + 1) * 3), dpi=1000)
    
    plot_instances(axs[0, 0], traces[0], 1, with_title=True)
    plot_instances(axs[0, 1], traces[1], 2, with_title=False)
    
    for model_size_i, model_size in enumerate(model_sizes):
        for trace_i, trace in enumerate(traces):
            plot_performance_together(axs[model_size_i + 1, trace_i], trace, trace_i, model_size, with_label=(model_size_i == 0 and trace_i == 0), with_x_label=True, with_title=True, with_avg=True)
    
    fig.tight_layout(rect = [0, 0.04, 1, 1])
    lgd = fig.legend(loc='lower center', ncol=len(systems), handlelength=1.1, handletextpad=0.2, columnspacing=0.5, handleheight=0, borderaxespad=0.001, prop={'size': label_size}, labelspacing=0.5,frameon=False)
    for line in lgd.get_lines():
        line.set_linewidth(2.5)
    lgd.get_lines()[-1].set_linewidth(3.5)

    for file in files:
        plt.savefig(file, bbox_inches='tight')

    plt.close()

def plot_performance_trace_horizental(file_preffix):
    plot_instances(file_preffix, 0, traces[0], with_title=False)
    plot_instances(file_preffix, 1, traces[1], with_title=False)
    
    for model_size_i, model_size in enumerate(model_sizes):
        for trace_i, trace in enumerate(traces):
            plot_performance_together(file_preffix, trace, trace_i, model_size, model_size_i, with_label=(model_size_i == 0 and trace_i == 0), with_x_label=True, with_title=False, with_avg=True)

def plot_total_throughputs(files):
    global total_throughputs
    fig, axs = plt.subplots(len(model_sizes), 1, figsize=(3 * len(model_sizes), 6 * len(traces)), dpi=1000)
    for model_size_i, model_size in enumerate(model_sizes):
        for trace_i, trace in enumerate(traces):
            tt_key = trace + '-' + model_size
            for system_i, system in enumerate(systems):
                if tt_key not in total_throughputs or system not in total_throughputs[tt_key]:
                    continue
                if trace_i == 0 and model_size_i == 0:
                    axs[model_size_i].bar(namemap[system] + '\n' + trace, total_throughputs[tt_key][system], width=0.3, color=colormap[system], label=namemap[system])
                else:
                    axs[model_size_i].bar(namemap[system] + '\n' + trace, total_throughputs[tt_key][system], width=0.3, color=colormap[system])
                # axs[model_size_i].bar_label(axs[model_size_i].containers[trace_i * len(systems) + system_i], label_type='edge', fontsize=8)
        axs[model_size_i].set_ylim(0, max(total_throughputs[tt_key].values()) * 1.2)
        if model_size_i == 0:
            axs[model_size_i].vlines((len(traces) * len(systems) - 1) / 2, axs[model_size_i].get_ylim()[0], axs[model_size_i].get_ylim()[1], linestyles='dashed')
        else:
            axs[model_size_i].vlines((len(traces) * len(systems) - 1) / 2 - 1, axs[model_size_i].get_ylim()[0], axs[model_size_i].get_ylim()[1], linestyles='dashed')
        axs[model_size_i].set_ylabel('Throughput (samples/s)')
        axs[model_size_i].set_xlabel('GPT-3 ' + model_size)
    axs[0].set_title(f'Average Throughput in GPT-3 (left trace: g4dn, right: p3))')
    fig.subplots_adjust(bottom=0.1, hspace=0.4)
    fig.legend(loc="lower center", bbox_to_anchor=(0., 0.005, 1., .102), ncol=4, fancybox=True, shadow=True, prop={'size': large_label_size})
    for file in files:
        plt.savefig(file, bbox_inches='tight')
    plt.close()

def plot_breakdown(file_preffix):
    extra_legends = [' ']
    labels = []
    fig_label = 'a'
    for model_size_i, model_size in enumerate(model_sizes):
        xticklables = []
        if model_size_i == 0:
            fig, axs = plt.subplots(1, 1, figsize=(11.5, 2.5), dpi=1000)
        else:
            fig, axs = plt.subplots(1, 1, figsize=(11.5, 2.5), dpi=1000)
        for freq_i, freq in enumerate(frequencies):
            for system_i, system in enumerate(systems):
                if freq_i == 0 and model_size_i == 0:
                    extra_legends.append(f'{shortnamemap[system]}: {namemap[system]}')
                key = system + '-' + freq + '-' + model_size
                if key not in results:
                    continue
                xticklables.append(shortnamemap[system] + '\n' + freq)
                for breakdown_name in list(reversed(breakdown_names)):
                    if system_i == 0 and freq_i == 0 and freq_i == 0:
                        p = axs.bar(shortnamemap[system] + '\n' + freq, breakdown_results[key][breakdown_name] * 100, color=breakdown_colormap[breakdown_name], label=breakdown_namemap[breakdown_name], width=0.6)
                        labels.append(p)
                    else:
                        p = axs.bar(shortnamemap[system] + '\n' + freq, breakdown_results[key][breakdown_name] * 100, color=breakdown_colormap[breakdown_name], width=0.6)
                    if breakdown_name == 'delta_effective_time':
                        # axs.bar_label(p, label_type='edge', fmt='%.2f', fontsize=14, padding=-20)
                        print(f'{model_size} {system} {freq} {breakdown_name} {breakdown_results[key][breakdown_name]}')
            if freq_i < len(frequencies) - 1:
                axs.vlines(len(xticklables) - 0.5, 0, 1, linestyles='dashed')
        # axs.set_title(f'({chr(ord(fig_label) + model_size_i)})GPT-3 {model_size}', fontproperties=font_bold, fontfamily='Times New Roman', fontstyle='normal', fontweight='bold')
        axs.set_ylabel('Time\noccupation (%)', fontproperties=font_large)
        if model_size_i == 0:
            axs.set_ylim(40, 105)
            axs.set_yticks([x * 10 for x in range(4, 12, 2)])
        else:
            axs.set_yticks([x * 10 for x in range(0, 12, 2)])
        axs.set_xticks(range(len(xticklables)))
        axs.set_xticklabels(xticklables)
        axs.yaxis.set_tick_params('major', labelsize=large_label_size)
        axs.xaxis.set_tick_params('major', labelsize=large_label_size)
    # for i in range(len(extra_legends)):
    #     axs[0].bar(0, 0, color='white', label=extra_legends[i])
    # h, l = axs[0].get_legend_handles_labels()
    # reorder = lambda l, nc: sum((l[i::nc] for i in range(nc)), [])
    # fig.legend(reorder(h, len(breakdown_names) // 2 + 1,), reorder(l, len(breakdown_names) // 2 + 1,), loc="lower center", bbox_to_anchor=(0., 0.005, 1., .102), ncol=len(breakdown_names) // 2 + 1, fancybox=True, shadow=True, prop={'size': large_label_size})
        if model_size_i == 0:
            # text = "Bam Bamboo            Varu     Varuna                               Live   LivePipe\nOob  Oobleck            Oob-o   Oobleck-opt"
            leg = fig.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02, 1., 0.2), ncol=len(breakdown_names) // 2 + 1, prop={'size': large_label_size}, title_fontsize=large_label_size, handlelength=1.4, handletextpad=0.3, columnspacing=1.3, frameon=False)
            leg._legend_box.align = "center"
        fig.subplots_adjust(top=1)
        for suffix in file_suffix:
            plt.savefig(f'{file_preffix}-{model_size_i}.{suffix}', bbox_inches='tight')
        fig.clear()

performance_log_interval_map_prob = {
    '350M': {0.1: 1, 0.2: 1, 0.4: 1},
    '1.3B': {0.1: 1, 0.2: 1},
    '2.7B': {0.1: 1, 0.2: 1}
}

performace_log_interval_map = {
    '350M': {
        'g4dn': 10,
        'p3': 10,
    },
    '1.3B': {
        'g4dn': 6,
        'p3': 6,
    },
    '2.7B': {
        'g4dn': 5,
        'p3': 5,
    },
}

# execute_all_prob(probabilities, 24, performance_log_interval_map_prob)
# execute_all_freq(spot_instance_desired_capacity=20)
# execute_all(spot_instance_desired_capacity=20, performance_log_interval_map=performace_log_interval_map)

get_data()
calculate_total_throughputs()
plot_performance_trace_horizental(f'res/exp-trace') 

# plot_performance_trace([f'res/performances_trace_20.png', f'res/performances_trace_20.pdf'])    
# plot_total_throughputs([f'res/total_throughputs_trace_20.png'])
   
# plot_total_throughputs([f'res/total_throughputs_trace_20.png'])


# handle_performances()
# plot_performance('res/performances_modified.png')

# get_data(use_which=USE_FREQUENCY)
# calculate_total_throughputs(use_which=USE_FREQUENCY)
# plot_breakdown(f'res/exp-breakdown')