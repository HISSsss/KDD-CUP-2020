import numpy as np
import copy


def cat_list(list, key):
    res_list = []
    for tmp_dict in list:
        res_list.append(tmp_dict[key])
    return res_list


def order_match(env):
    match_orders_list = []
    match_drivers_list = []
    efftive_drivers = copy.deepcopy(env.eff_drivers)
    efftive_orders = copy.deepcopy(env.eff_orders)
    for i in range(len(env.eff_drivers)):
        dis_list = []
        for j in range(len(efftive_orders)):
            dis_list.append(env.orders.total_order[j]['order_reward_units'])
        if len(dis_list) > 0:
            order_index = np.argmax(np.array(dis_list))
            match_orders_list.append(efftive_orders[order_index])
            match_drivers_list.append(env.eff_drivers[i])
            del efftive_orders[order_index]
        else:
            match_orders_list.append(-1)
            match_drivers_list.append(env.eff_drivers[i])

    for i in range(len(efftive_orders)):
        match_orders_list.append(efftive_orders[i])
        match_drivers_list.append(-1)
    match_list = [match_orders_list, match_drivers_list]
    return match_list


def cancel_probability_processing():
    pass