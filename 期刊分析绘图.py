# 获取某领域杂志发表某个关键词的各自数目，并作图
import requests
import json
import pandas as pd
from pyecharts.charts import Bar, Grid
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from gevent import monkey

monkey.patch_all()
import gevent


def get_journal_name_IF():
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'token': 'zgLgTjSvGLpr2QkeL805MDdCJ64=', }
    page = 0
    while True:
        page += 1
        data = {
            'pageSize': '20',
            'page': page,
            'type': '肿瘤学',
            'sortType': '0'}
        search_text = requests.get('https://www.geenmedical.com/api/journal', headers=headers, params=data).text
        r_json = json.loads(search_text)
        journals = r_json['journals']
        if journals == []:
            break
        tasks_list = []
        for journal in journals:
            current_factor = journal['current_factor']
            name = journal['name']
            name = name + '?' + str(current_factor)
            task = gevent.spawn(search_results, name)
            tasks_list.append(task)
        gevent.joinall(tasks_list)


def search_results(name_if):
    name = name_if.split('?')[0]
    IF = name_if.split('?')[1]
    global df_journal
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'token': 'zgLgTjSvGLpr2QkeL805MDdCJ64=', }
    data_search = {
        'keyword': f'(machine learning[All Fields]) AND {name}[Journal]',
        'cursor': '0'}
    url = 'https://www.geenmedical.com/api/search'
    search_response = requests.post(url, headers=headers, json=data_search).text
    r_json = json.loads(search_response)
    name = f'{name}({IF})'
    count = r_json['count']
    print(name, count)
    df_journal.append([name, IF, count])


def process_data(lst):
    df = pd.DataFrame(lst, columns=['Journal', 'IF', 'Count'])
    df_sort = df.sort_values(by='Count', ascending=False)
    df_draw = df_sort[df_sort['IF'].astype('float') >= 5]
    df_draw = df_draw[0:20]
    journals = df_draw['Journal'].tolist()
    counts = df_draw['Count'].tolist()

    grid = Grid()
    bar = Bar(init_opts=opts.InitOpts(theme=ThemeType.VINTAGE))
    bar.add_xaxis(journals)
    bar.add_yaxis('发文数', counts)
    bar.set_global_opts(
        title_opts=opts.TitleOpts(
            title='Bar-肿瘤学杂志',
            subtitle='Bar-机器学习'),
        xaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(rotate=30)),
        datazoom_opts=[opts.DataZoomOpts()]
    )
    grid.add(bar, grid_opts=opts.GridOpts(pos_bottom="30%",
                                          pos_left="30%"))
    grid.render(r'C:\Users\chenx\Desktop' + r'\肿瘤学期刊与机器学习.html')


if __name__ == '__main__':
    df_journal = []
    get_journal_name_IF()
    process_data(df_journal)



