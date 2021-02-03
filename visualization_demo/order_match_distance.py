import numpy as np


def get_distance(env, order_index, driver_index):
    distance = ((float(env.orders.total_order[order_index]['order_pickup_longitude']) - float(
        env.drivers.total_driver[driver_index]['driver_longitude'])) ** 2
                + (float(env.orders.total_order[order_index]['order_pickup_latitude']) - float(
                env.drivers.total_driver[driver_index]['driver_latitude'])) ** 2) ** 0.5
    return distance

def cat_list(list, key):
    res_list = []
    for tmp_dict in list:
        res_list.append(tmp_dict[key])
    return res_list

def order_match(env):
    maxnum = 999999999999
    order_status_np = np.ones((len(env.eff_orders)), dtype=np.int)
    driver_status_np = np.ones((len(env.eff_drivers)), dtype=np.int)
    match_orders_list = []
    match_drivers_list = []
    for i in range(len(env.eff_orders)):
        dis_list = []
        for j in range(len(env.eff_drivers)):
            if not (driver_status_np[j] == 2):
                dis_list.append(get_distance(env, env.eff_orders[i], env.eff_drivers[j]))
            else:
                dis_list.append(maxnum)

        if len(dis_list) > 0:
            driver_index = np.argmin(np.array(dis_list))
            if (dis_list[driver_index] == maxnum):
                continue
            # print(dis_list, driver_index)
            order_status_np[i] = 2
            driver_status_np[driver_index] = 2
            match_dic = {'order': env.eff_orders[i], 'driver': env.eff_drivers[driver_index]}
            match_orders_list.append(match_dic['order'])
            match_drivers_list.append(match_dic['driver'])
    for i in range(len(env.eff_orders)):
        if (order_status_np[i] == 1):
            match_dic = {'order': env.eff_orders[i], 'driver': -1}
            match_orders_list.append(match_dic['order'])
            match_drivers_list.append(match_dic['driver'])
    for i in range(len(env.eff_drivers)):
        if (driver_status_np[i] == 1):
            match_dic = {'order': -1, 'driver': env.eff_drivers[i]}
            match_orders_list.append(match_dic['order'])
            match_drivers_list.append(match_dic['driver'])
    match_list = [match_orders_list, match_drivers_list]
    # print('status:', order_status_np, driver_status_np)
    return match_list


def cancel_probability_processing():
    pass
