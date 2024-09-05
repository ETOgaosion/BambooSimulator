import csv
import pprint

cards_varient_total = {}
cards_varient_total_csv_list = []
cards_varient_total_group_by_card = {}
cards_nums = []
cards_nums_cu = []
cards_actions = []
cards_times = []

def cards_parser(file):
    start_nodes_num = 0
    if file.endswith(".csv"):
        with open(file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            last_time = '0'
            last_cards = 0
            last_action = 'add'
            for row in reader:
                if row[0] == last_time and row[1] == last_action:
                    last_cards += 1
                elif row[0] == last_time and row[1] != last_action:
                    raise Exception('Error: not gonna happen')
                    last_cards -= 1
                    if last_cards < 0:
                        last_cards = -last_cards
                        last_action = row[1]
                elif row[0] != last_time:
                    cards_nums.append(last_cards)
                    cards_actions.append(last_action)
                    cards_times.append(last_time)
                    if last_cards == 0:
                        print(last_time)
                    if len(cards_nums_cu) == 0:
                        cards_nums_cu.append(last_cards)
                    else:
                        if last_action == 'add':
                            cards_nums_cu.append(cards_nums_cu[-1] + last_cards)
                        else:
                            cards_nums_cu.append(cards_nums_cu[-1] - last_cards)
                    last_time = row[0]
                    last_cards = 1
                    last_action = row[1]
            cards_nums.append(cards_nums_cu[-1])
            cards_nums_cu.append(0)
            cards_actions.append('remove')
            cards_times.append(last_time)
            print(cards_nums)
            print(cards_nums_cu)
            print(cards_actions)
            print(cards_times)

def cards_varient():
    for i in range(len(cards_nums_cu) - 1):
        if cards_varient_total.get(cards_nums_cu[i]) is None:
            cards_varient_total[cards_nums_cu[i]] = {cards_actions[i+1]: {cards_nums_cu[i + 1]: (cards_nums[i+1], cards_times[i+1])}}
        else:
            if cards_varient_total[cards_nums_cu[i]].get(cards_actions[i+1]) is None:
                cards_varient_total[cards_nums_cu[i]][cards_actions[i+1]] = {cards_nums_cu[i + 1]: (cards_nums[i+1], cards_times[i+1])}
            else:
                if cards_varient_total[cards_nums_cu[i]][cards_actions[i+1]].get(cards_nums_cu[i + 1]) is None:
                    cards_varient_total[cards_nums_cu[i]][cards_actions[i+1]][cards_nums_cu[i + 1]] = (cards_nums[i+1], cards_times[i+1])
    pprint.pp(cards_varient_total)

def get_csv_list(sort_by_time, add_header=False):
    global cards_varient_total_csv_list
    for key in cards_varient_total:
        for key2 in cards_varient_total[key]:
            for key3 in cards_varient_total[key][key2]:
                if key == 0 or key3 == 0:
                    continue
                cards_varient_total_csv_list.append([key, key2, cards_varient_total[key][key2][key3][0], key3, int(cards_varient_total[key][key2][key3][1])])
    if sort_by_time:
        cards_varient_total_csv_list = sorted(cards_varient_total_csv_list, key=lambda x: x[4])
    else:
        cards_varient_total_csv_list = sorted(cards_varient_total_csv_list, key=lambda x: x[0])
    if add_header:
        cards_varient_total_csv_list.insert(0, ['start_nodes_num', 'action', 'varience', 'end_nodes', 'time'])
    pprint.pp(cards_varient_total_csv_list)

def to_csv(file):
    with open(file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in cards_varient_total_csv_list:
            writer.writerow(row)

def get_group_by_cards(reverse=False):
    global cards_varient_total_group_by_card
    for key in cards_varient_total:
        for key2 in cards_varient_total[key]:
            for key3 in cards_varient_total[key][key2]:
                if key == 0 or key3 == 0:
                    continue
                k, v = key, key3
                if not reverse:
                    if k > v:
                        k, v = v, k
                else:
                    if k < v:
                        k, v = v, k
                if k not in cards_varient_total_group_by_card:
                    cards_varient_total_group_by_card[k] = {v: 0}
                else:
                    cards_varient_total_group_by_card[k][v] = 0
    for in_dict in cards_varient_total_group_by_card:
        cards_varient_total_group_by_card[in_dict] = dict(sorted(cards_varient_total_group_by_card[in_dict].items()))
    cards_varient_total_group_by_card = dict(sorted(cards_varient_total_group_by_card.items()))

cards_parser('traces/p3-trace-16.csv')
cards_varient()
# get_csv_list(True)
# to_csv('res/trace/p3-card-varient-sort-by-time.csv')
get_csv_list(False)
# to_csv('res/trace/p3-card-varient.csv')

cards_parser('traces/g4dn-trace-16.csv')
cards_varient()
# get_csv_list(True)
# to_csv('res/trace/all-card-varient-sort-by-time.csv')
get_csv_list(False, True)
to_csv('res/trace/all-card-varient-16.csv')

get_group_by_cards(True)
pprint.pp(cards_varient_total_group_by_card)