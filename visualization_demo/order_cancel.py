import random
from math import radians, cos, sin, asin, sqrt

#读入数据
def read_order_cancel_data(path):
    total_cancel_prob = dict()
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
            data7 = item[7]
            data8 = item[8]
            data9 = item[9]
            data10 = item[10].rstrip()

            # data0为id
            tmp_dict['200'] = float(data1)
            tmp_dict['400'] = float(data2)
            tmp_dict['600'] = float(data3)
            tmp_dict['800'] = float(data4)
            tmp_dict['1000'] = float(data5)
            tmp_dict['1200'] = float(data6)
            tmp_dict['1400'] = float(data7)
            tmp_dict['1600'] = float(data8)
            tmp_dict['1800'] = float(data9)
            tmp_dict['2000'] = float(data10)
            total_cancel_prob[data0] = tmp_dict

    return total_cancel_prob


# 生成概率
def number_of_certain_probability(sequence, probability):
    x = random.uniform(0, 1)
    cumulative_probability = 0.0
    for item, item_probability in zip(sequence, probability):
        cumulative_probability += item_probability
        if x < cumulative_probability:
            break
    return item

def get_distance(order_location, driver_location): # 公式计算两点间距离（m）
    lng1, lat1, lng2, lat2 = map(radians, [order_location[0], order_location[1], driver_location[0], driver_location[1]])  # 经纬度转换成弧度
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    distance = 2 * asin(sqrt(a)) * 6371.393 * 1000  # 地球平均半径，6371.393km
    distance = round(distance / 1000, 3)*1000
    return distance

def cancel_selection(env, order_cancel_prob, match_list):
    value_list = [0, 1]
    order_match_list = match_list[0]
    driver_match_list = match_list[1]
    cancel_count = 0
    for i in range(len(order_match_list)):
        order_index = order_match_list[i]
        driver_index = driver_match_list[i]
        if order_index != -1 and driver_index != -1:
            order_location = [env.orders.total_order[order_index]['order_pickup_longitude'], env.orders.total_order[order_index]['order_pickup_latitude']]
            driver_location = [env.drivers.total_driver[driver_index]['driver_longitude'], env.drivers.total_driver[driver_index]['driver_latitude']]
            distance = get_distance(order_location, driver_location)
            dis = 0
            if distance < 200 :
                continue
            elif distance < 400 :
                dis = '200'
            elif distance < 600 :
                dis = '400'
            elif distance < 800 :
                dis = '600'
            elif distance < 1000 :
                dis = '800'
            elif distance < 1200 :
                dis = '1000'
            elif distance < 1400 :
                dis = '1200'
            elif distance < 1600 :
                dis = '1400'
            elif distance < 1800 :
                dis = '1600'
            elif distance < 2000 :
                dis = '1800'
            elif distance >= 2000 :
                dis = '2000'
            order_id = env.orders.total_order[order_index]['id']
            tmp_dict = order_cancel_prob[order_id]
            cancel_prob = tmp_dict[dis]
            probability = [cancel_prob, 1-cancel_prob]
            # 0则被取消，反之接受
            result = number_of_certain_probability(value_list, probability)
            if result == 0:
                env.orders.total_order[order_index]['status'] = 3
                cancel_count += 1
    return cancel_count