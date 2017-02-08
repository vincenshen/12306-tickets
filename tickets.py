# coding: utf-8

"""命令行火车票查看器

Usage:
    tickets [-gdtkz] <from> <to> <date>

Options:
    -h --help   显示帮助菜单
    -g          高铁
    -d          动车
    -t          特快
    -k          快速
    -z          直达
    -v --version    查看版本

Example:
    tickets 北京 上海 2016-10-10
    tickets -dg 成都 南京 2016-10-10
"""
from docopt import docopt
from stations import stations
import requests
from prettytable import PrettyTable
from colorama import init, Fore
init(autoreset=True)

class TrainsCollection(object):
    header = '车次 始末车站 始末时间 历时 商务座 一等 二等 软卧 硬卧 硬座 无座'.split()

    def __init__(self, available_trains, options):
        '''
        :param available_trains: 一个列表，包含可获得的火车班次，每个班次是一个字典
        :param options: 查询的选项，如高铁、动车
        '''
        self.available_trains = available_trains
        self.options = options

    def _get_duration(self, raw_train):
        duration = raw_train.get('lishi').replace(':', '小时')+'分'
        if duration.startswith('00'):
            return duration[4:]
        if duration.startswith('0'):
            return duration[1:]
        return duration

    @property
    def trains(self):
        for raw_train in self.available_trains:
            train_no = raw_train['station_train_code']
            initial = train_no[0].lower()
            if not self.options or initial in self.options:
                train = [
                    train_no,
                    '\n'.join([Fore.GREEN+raw_train['from_station_name']+Fore.RESET,
                               Fore.RED+raw_train['to_station_name']+Fore.RESET]),
                    '\n'.join([Fore.GREEN+raw_train['start_time']+Fore.RESET,
                               Fore.RED+raw_train['arrive_time']+Fore.RESET]),
                    self._get_duration(raw_train),
                    raw_train['swz_num'],
                    raw_train['zy_num'],
                    raw_train['ze_num'],
                    raw_train['rw_num'],
                    raw_train['yw_num'],
                    raw_train['yz_num'],
                    raw_train['wz_num']
                ]
                yield train

    def pretty_print(self):
        pt = PrettyTable()
        pt._set_field_names(self.header)
        for train in self.trains:
            pt.add_row(train)
        print(pt)

def cli():
    """command-line interface"""
    arguments = docopt(__doc__,version="1.0")
    from_station = stations.get(arguments['<from>'])
    to_staion = stations.get(arguments['<to>'])
    date = arguments['<date>']
    # 构建12306 API URL
    url = 'https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}' \
          '&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(date,from_station,to_staion)
    # 获取参数Options
    options = ''.join([key for key,value in arguments.items() if value is True])

    r = requests.get(url, verify=False)
    rows = r.json()['data']
    available_trains = []
    for row in rows:
        if row.get('queryLeftNewDTO') != None:
            available_trains.append(row['queryLeftNewDTO'])
    TrainsCollection(available_trains,options).pretty_print()


if __name__ == '__main__':
    cli()
