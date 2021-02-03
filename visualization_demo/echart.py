from pyecharts.charts import *
from pyecharts.components import Table
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
import random
import datetime

import sys

from pyecharts.globals import CurrentConfig

CurrentConfig.ONLINE_HOST = "https://cdn.kesci.com/lib/pyecharts_assets/"

'''
class Map
env：订单分配环境，必选
id：呈现的司机id，必选
strategy：策略，如income-base、distance-base，必选
'''

class Map():
    def __init__(self, env, id, strategy, color, position):
        is_show = 0
        self.color = color
        for tmp_dict in env.drivers.total_driver:
            if tmp_dict['driver_id'] == id:
                is_show = 1
                self.location = tmp_dict['trace']
        if is_show == 0:
            print("Cannot find the driver!")
            sys.exit(1)
        self.id = id
        self.strategy = strategy
        self.position = position

    def get_chart_name(self):
        name = "司机" + str(self.id) + "接单过程的行车轨迹.html"
        return name

    def set_chart(self, is_show=False):
        length = len(self.location)
        charts = Geo()
        charts.add_schema(maptype="成都", zoom=15,  # 缩放比例为15
                          center=[104.07, 30.67],  # 设置地图中心
                          itemstyle_opts=opts.ItemStyleOpts(color="#DCDCDC", border_color="#000000",border_width=1))  # 设置地图背景
        trace = []

        if length == 1:
            return charts

        for i in range(length):
            id = "0"
            if i == 0:
                id = "起点"
            elif i == 1:
                id = "地点0"
                trace.append(["起点", "地点0"])
            elif i > 1:
                id = "地点" + str(i)
                trace_start = "地点" + str(i - 1)
                trace_cell = [trace_start, id]
                trace.append(trace_cell)
            charts.add_coordinate(name=id, longitude=self.location[i][0], latitude=self.location[i][1])  # 把点与点的id加入到地图的坐标点中

        charts.add(self.strategy, trace, type_='lines',
                   effect_opts=opts.EffectOpts(symbol='circle', symbol_size=6, color=self.color, trail_length=0.02, period=8),  # 设置涟漪效果
                   linestyle_opts=opts.LineStyleOpts(width=0.5, opacity=0.8, curve=0.2,color=self.color))  # 设置线

        name = self.get_chart_name()
        title = "司机" + str(self.id) + "\n接单过程的运行轨迹"
        charts.set_global_opts(title_opts=opts.TitleOpts(title=title,
                                                         title_textstyle_opts=opts.TextStyleOpts(font_size=16, color='#808080')),
                               legend_opts=opts.LegendOpts(is_show=True,pos_top = '2%',pos_left = self.position))
        if is_show == True:
            charts.render(name)
        return charts

'''
class grid
参数：
    chart_list:两个Map.set_chart组合的list，必选
    id：司机id，可选，只会影响html文件的生成
函数：
    
'''

class grid_chart(): # 注该类最多只能将两个图组合在一起！
    def __init__(self, chart_list, id = None):
        self.chart = chart_list
        self.id = id

    def get_grid_name(self):
        name = "司机" + str(self.id) + "接单过程的行车轨迹对比.html"
        return name

    def set_grid(self, is_show=False):
        grid = (Grid(init_opts=opts.InitOpts(theme='white'))
                .add(self.chart[0], grid_opts=opts.GridOpts())
                .add(self.chart[1], grid_opts=opts.GridOpts())
                )
        if is_show == True:
            if self.id is None:
                grid.render()
            else:
                name = self.get_grid_name()
                grid.render(name)
        return grid



class Timeline_chart():
    def __init__(self, grid_list, time_point_list = None, id = None):
        self.id = id
        self.grid = grid_list
        self.time_point = time_point_list

    def get_timeline_name(self):
        name = "司机" + str(self.id) + "多数据接单过程的行车轨迹对比.html"
        return name

    def set_timeline(self):
        count = len(self.grid)
        timeline_chart = Timeline()
        timeline_chart.add_schema()
        for i in range(count):
            if self.time_point is not None:
                timeline_chart.add(self.grid[i], self.time_point[i])
            else:
                time_point = "数据" + str(i+1)
                timeline_chart.add(self.grid[i], time_point)

        if self.id is not None:
            name = self.get_timeline_name()
            timeline_chart.render(name)
        else:
            timeline_chart.render("多数据接单过程的行车轨迹对比.html")