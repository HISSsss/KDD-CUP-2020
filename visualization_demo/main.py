import numpy as np
# from A2C1_0 import *
import torch
import torch.nn.functional as F
import copy
# import visualization as vis
import order_cancel
import echart

def initiate_time(time_stamp):
    time_stamp += 28800
    time_stamp %= 86400
    time_stamp //= 600
    return time_stamp

# 得到时间步


class Order(object):
    def __init__(self):
        self.total_order = []
        self.length = len(self.total_order)

    def read_order_data(self, path):
        with open(path, 'r') as file_to_read:
            while True:
                lines = file_to_read.readline()  # 整行读取数据
                if not lines:
                    break
                tmp_dict = dict()
                item = [i for i in lines.split(',')]
                data0 = item[0]  # 每行第一个值
                data1 = item[1]  # 每行第二个值
                data2 = item[2]
                data3 = item[3]
                data4 = item[4]
                data5 = item[5]
                data6 = item[6]
                data7 = item[7].rstrip()
                tmp_dict['id'] = data0
                tmp_dict['order_ride_start_time'] = initiate_time(int(data1))
                tmp_dict['order_ride_end_time'] = initiate_time(int(data2))
                tmp_dict['order_pickup_longitude'] = float(data3)
                tmp_dict['order_pickup_latitude'] = float(data4)
                tmp_dict['order_dropoff_longitude'] = float(data5)
                tmp_dict['order_dropoff_latitude'] = float(data6)
                tmp_dict['order_reward_units'] = data7
                tmp_dict['status'] = 0
                self.total_order.append(tmp_dict)
                # 0为未分配， 1为候选等待， 2为已分配且成功, 3为分配但被取消


class Driver(object):
    def __init__(self):
        self.total_driver = []

    def read_driver_data(self, path):
        with open(path, 'r') as file_to_read:
            while True:
                tmp_dict = dict()
                lines = file_to_read.readline()  # 整行读取数据
                if not lines:
                    break
                item = [i for i in lines.split(',')]
                data0 = item[0]  # 每行第一个值
                data1 = item[1]  # 每行第二个值
                data2 = item[2]
                data3 = item[3].rstrip()
                tmp_dict['driver_id'] = data0
                tmp_dict['driver_time_stamp'] = initiate_time(int(data1))
                tmp_dict['driver_longitude'] = float(data2)
                tmp_dict['driver_latitude'] = float(data3)
                tmp_dict['next_free_time'] = initiate_time(int(data1))
                tmp_dict['status'] = 0
                # print(tmp_dict['driver_time_stamp'])
                tmp_dict['total_rewards'] = 0
                tmp_dict['last_reward'] = 0
                tmp_dict['trace'] = [[float(data2), float(data3)]]
                self.total_driver.append(tmp_dict)


class order_alloc_env():
    def __init__(self, orders, drivers):
        self.orders = orders
        self.drivers = drivers
        self.eff_drivers = []
        self.eff_orders = []
        self.env_time = 0
        self.env_end_time = 144

    def get_candidate_list(self):
        i = 0
        for tmp_dict in self.drivers.total_driver:
            if tmp_dict['status'] == 0 and tmp_dict['next_free_time'] <= self.env_time:  # 空车且上线
                self.eff_drivers.append(i)
                tmp_dict['status'] = 1
            i += 1

        i = 0
        for tmp_dict in self.orders.total_order:
            if tmp_dict['status'] == 0 and tmp_dict['order_ride_start_time'] <= self.env_time:
                self.eff_orders.append(i)
                tmp_dict['status'] = 1
            i += 1

    def reset(self, d_path, o_path):
        # reset env
        self.eff_drivers = []
        self.eff_orders = []
        self.env_time = 0
        # reset order
        self.orders.total_order = []
        self.orders.read_order_data(o_path)
        # reset driver
        self.drivers.total_driver = []
        self.drivers.read_driver_data(d_path)
        self.get_candidate_list()
        eff_drivers = copy.deepcopy(self.eff_drivers)
        eff_orders = copy.deepcopy(self.eff_orders)
        return eff_drivers, eff_orders

    def render(self): # 请在env.step()后调用env.render()
        pass

    def get_env_time(self):
        return self.env_time

    def update_time(self):
        self.env_time += 1

    def trace_env(self):
        # 追踪drivers情况
        for tmp_dict in self.drivers.total_driver:
            if tmp_dict['driver_time_stamp'] < self.env_time:
                tmp_dict['driver_time_stamp'] = self.env_time
            if tmp_dict['status'] == 0 or tmp_dict['status'] == 1:
                tmp_dict['next_free_time'] = tmp_dict['driver_time_stamp']  # 特别地，对于时间步表示可用
            elif tmp_dict['status'] == 2 and tmp_dict['next_free_time'] <= self.env_time:
                tmp_dict['status'] = 0
                tmp_dict['next_free_time'] = tmp_dict['driver_time_stamp']

    def step(self, match_list):
        order_match_list = match_list[0]
        driver_match_list = match_list[1]
        # print('eff_drivers:', self.eff_drivers, 'eff_orders:', self.eff_orders)

        for i in range(len(order_match_list)):
            if order_match_list[i] != -1 and driver_match_list[i] != -1 and self.orders.total_order[order_match_list[i]]['status'] != 3: #不被取消
                # 更新候选列表
                order_index = order_match_list[i]
                driver_index = driver_match_list[i]
                # print('driver_index', driver_index, 'order_index', order_index)
                self.eff_orders.remove(order_index)
                # print('driver id', driver_index)
                self.eff_drivers.remove(driver_index)
                # 更新order信息
                self.orders.total_order[order_index]['status'] = 2
                # 更新driver信息
                self.drivers.total_driver[driver_index]['status'] = 2
                self.drivers.total_driver[driver_index]['driver_longitude'] = self.orders.total_order[order_index][
                    'order_dropoff_longitude']
                self.drivers.total_driver[driver_index]['driver_latitude'] = self.orders.total_order[order_index][
                    'order_dropoff_latitude']
                self.drivers.total_driver[driver_index]['next_free_time'] = self.orders.total_order[order_index][
                    'order_ride_end_time']
                self.drivers.total_driver[driver_index]['total_rewards'] += float(
                    self.orders.total_order[order_index]['order_reward_units'])
                self.drivers.total_driver[driver_index]['last_reward'] += float(
                    self.orders.total_order[order_index]['order_reward_units'])

                #记录轨迹信息，作图用
                trace_pickup_longitude = self.orders.total_order[order_index]['order_pickup_longitude']
                trace_pickup_latitude = self.orders.total_order[order_index]['order_pickup_latitude']
                trace_dropoff_longitude = self.orders.total_order[order_index]['order_dropoff_longitude']
                trace_dropoff_latitude = self.orders.total_order[order_index]['order_dropoff_latitude']
                self.drivers.total_driver[driver_index]['trace'].append([trace_pickup_longitude, trace_pickup_latitude])
                self.drivers.total_driver[driver_index]['trace'].append([trace_dropoff_longitude, trace_dropoff_latitude])

            elif order_match_list[i] != -1 and driver_match_list[i] != -1 and self.orders.total_order[order_match_list[i]]['status'] == 3:
                self.eff_orders.remove(order_match_list[i])
            elif order_match_list[i] != -1 and driver_match_list == -1:
                continue
            elif order_match_list[i] == -1:
                continue


        # check if one day has finished
        self.update_time()
        self.trace_env()
        finished = False
        if self.env_time == self.env_end_time:
            finished = True
        # print(self.eff_orders, self.eff_drivers)
        self.get_candidate_list()
        eff_drivers = copy.deepcopy(self.eff_drivers)
        eff_orders = copy.deepcopy(self.eff_orders)
        return eff_drivers, eff_orders, finished


import order_match_income
import order_match_distance

def cat_list(list, key):
    res_list = []
    for tmp_dict in list:
        res_list.append(tmp_dict[key])
    return res_list


_order = Order()
# 可以用循环的形式读入多个文件数据,driver测试代码同
path1 = './order_500.txt'
_order.read_order_data(path1)
_driver = Driver()
path2 = './driver_100.txt'
_driver.read_driver_data(path2)
path3 = './order_20161101_cancel_prob'
cancel_prob = order_cancel.read_order_cancel_data(path3)


env = order_alloc_env(_order, _driver)
# env.reset(path1)
env.get_candidate_list()
grid_list = []
for i in range(5):
    step = 0
    cancel_count = 0
    while step <= 144 :
        match_list = order_match_income.order_match(env)
        cancel_count += order_cancel.cancel_selection(env, cancel_prob, match_list)
        env.step(match_list)
        step += 1
    '''
    color参数可以用十六进制表示，也可以用rgb表示。这里直接套用'#006400'或者'rgb(72,61,139)'即可
    position参数表示图例的位置，图例分隔开可以显示的更清楚，这里直接用'40%'和'60%'即可
    '''
    map_income = echart.Map(env=env, id="7ee831b9edb7327bca8a1ac6bd82f00b", strategy="income-base", color='#006400', position='40%')
    print(np.array(cat_list(env.drivers.total_driver, 'total_rewards')))
    print(round(np.sum(np.array(cat_list(env.drivers.total_driver, 'total_rewards'))), 2))
    print("The number of order being cancelled is", cancel_count)

    env.reset(path2, path1)
    step = 0
    cancel_count = 0
    while step <= 144 :
        match_list = order_match_distance.order_match(env)
        cancel_count += order_cancel.cancel_selection(env, cancel_prob, match_list)
        env.step(match_list)
        step += 1

    print(np.array(cat_list(env.drivers.total_driver, 'total_rewards')))
    print(round(np.sum(np.array(cat_list(env.drivers.total_driver, 'total_rewards'))), 2))
    print("The number of order being cancelled is", cancel_count)

    map_distance = echart.Map(env=env, id="7ee831b9edb7327bca8a1ac6bd82f00b", strategy="distance-base", color='rgb(72,61,139)', position='60%')
    chart_list = [map_income.set_chart(), map_distance.set_chart()]
    grid = echart.grid_chart(chart_list=chart_list, id="7ee831b9edb7327bca8a1ac6bd82f00b")
    grid_list.append(grid.set_grid())
    env.reset(path2, path1)

timeline = echart.Timeline_chart(grid_list=grid_list, id="7ee831b9edb7327bca8a1ac6bd82f00b")
timeline.set_timeline()