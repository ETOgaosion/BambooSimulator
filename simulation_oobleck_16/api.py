import argparse
import logging

from simulation_oobleck_16.mysimulator import MySimulator

logger = logging.getLogger('simulation')

fig_directory = 'res/simulator'

def parse(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int)
    parser.add_argument('--start-hour', type=int, choices=range(24))
    parser.add_argument('--generate-addition-probabilities', action='store_true')
    parser.add_argument('--removal-probability', type=float, default=None)
    parser.add_argument('--generate-graphs', action='store_true')
    parser.add_argument('--generate-table', action='store_true')
    parser.add_argument('--spot-instance-trace', type=str, default=None)
    parser.add_argument('--model', type=str, default='GPT-3')
    parser.add_argument('--model-size', type=str, default='350M')
    parser.add_argument('--spot-instance-desired-capacity', type=int, default=24)
    parser.add_argument('--fig-directory', type=str, default='res/simulator')
    parser.add_argument('--performace-log-interval', type=int, default=1)
    return parser.parse_args(args)

def simulate(args):
    model, duration, spot_instance_trace, fig_directory = args
    print(args)
    simulator = MySimulator(
        seed=0,
        start_hour=0,
        generate_addition_probabilities=True,
        removal_probability=0,
        spot_instance_trace=spot_instance_trace,
        model=model
    )
    result = simulator.simulate(duration=duration, fig_directory=fig_directory)
    return result

def generate_table(model='GPT-3', spot_instance_trace='trace/p3-trace.csv', duration=4_320_000, fig_directory='res/simulator'):
    logging.getLogger('project_pactum.simulation.simulator').setLevel(logging.INFO)


    result = simulate([model, duration, spot_instance_trace, fig_directory])

    print('Probability', 'Preemptions', 'Interruptions', 'Lifetimes', 'Fatal Failures', 'Instances', 'Performance', '     Cost', '    Value',
          sep=' & ', end=' \\\\\n')
    print(f'{result.removal_probability:11.2f}',
        '{:11.2f}'.format(result.preemption_mean),
        '{:13.2f}'.format(result.num_preemptions),
        '{:9.2f}'.format(result.lifetime_mean),
        '{:14.2f}'.format(result.num_fatal_failures),
        '{:9.2f}'.format(result.average_instances),
        '{:11.2f}'.format(result.average_performance),
        '{:9.2f}'.format(result.average_cost),
        '{:9.2f}'.format(result.average_value),
        sep=' & ', end=' \\\\\n'
        )

def main(args):
    options = parse(args)
    print(options)

    assert not (options.generate_graphs and options.generate_table)

    if not options.generate_table:
        simulator = MySimulator(
            seed=options.seed,
            performance_log_interval=options.performace_log_interval,
            start_hour=options.start_hour,
            generate_addition_probabilities=options.generate_addition_probabilities,
            removal_probability=options.removal_probability,
            generate_graphs=options.generate_graphs,
            spot_instance_trace=options.spot_instance_trace,
            spot_instance_desired_capacity=options.spot_instance_desired_capacity,
            model=options.model,
            model_size=options.model_size
        )
        # simulator.simulate()
        if options.spot_instance_trace is None:
            options.fig_directory = 'res/simutest-oobleck-16-prob-' + options.model_size + '-' + str(options.removal_probability)
        else:
            options.fig_directory = 'res/simutest-oobleck-16-' + options.spot_instance_trace.split('/')[-1].split('-')[0] + '-' + options.model_size
        simulator.simulate(duration=4_320_0000, fig_directory=options.fig_directory)
        # simulator.simulate(duration=1_200_000)
    else:
        generate_table(options.model, spot_instance_trace=options.spot_instance_trace, duration=4_320_0000, fig_directory=options.fig_directory)
