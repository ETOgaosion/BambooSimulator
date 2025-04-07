import random

remap_layer_map = {
    "1.3B": {
        "num_layers": 24,
        "single_layer_transmission_time": 430,
    },
    "2.7B": {
        "num_layers": 32,
        "single_layer_transmission_time": 910,
    },
    "6.7B": {
        "num_layers": 32,
        "single_layer_transmission_time": 2258,
    },
    "13B": {
        "num_layers": 40,
        "single_layer_transmission_time": 4381,
    },
}

def get_remap_layer_time(model_size, prev_nodes, new_nodes):
    if prev_nodes == new_nodes:
        return 0
    if prev_nodes < new_nodes:
        prev_nodes, new_nodes = new_nodes, prev_nodes
    if model_size in ["1.3B", "2.7B"]:
        try:
            return remap_layer_map[model_size][prev_nodes][new_nodes]
        except KeyError:
            pass
    prev_layers = remap_layer_map[model_size]["num_layers"] / prev_nodes
    new_layers = remap_layer_map[model_size]["num_layers"] / new_nodes
    transfer_layers = random.randint(0, 1)
    transfer_time = transfer_layers * remap_layer_map[model_size]["single_layer_transmission_time"]
    return transfer_time
    