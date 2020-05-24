# -*- coding: utf-8 -*-
# @Author: Fule
# @Date:   2020-05-20 18:03:50
# @Last Modified by:   Fule
# @Last Modified time: 2020-05-21 11:30:25

# %%
import PySimpleGUI as psg
import os
import pandas as pd
from time import strftime
from pandas import DataFrame as df
from pandas import read_excel 
from pathlib import Path
from secrets import token_hex
#from pandas.plotting._matplotlib import table


pro_dir = os.path.join(os.getcwd(), 'profile')
script_dir = os.path.join(os.getcwd(), 'script')
dirlist = []
event = ''

if Path(script_dir).is_dir():
    print('目录存在')
else:
    os.makedirs(script_dir)
    print('创建目录')

#%%
# 文件名函数

def file_name(file_dir, exten):
    file_list = []
    filename_list = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            (name, extention) = os.path.splitext(file)
            if extention == exten:
                file_list.append(name)
                filename_list.append((name, file))
    return file_list, filename_list

# 替换函数

def replace_data_sing(table, template):
    with open(template) as f:
        template = f.read()
        pd_table = pd.read_excel(table)
        dict_table_index = pd_table.to_dict('index')
        for i in list(dict_table_index):
            maxlen = len(dict_table_index.keys())
            data_dict = dict_table_index[i]
            j = list(data_dict.keys())
            temp_cache = template
            for k in j:
                temp_cache = temp_cache.replace(k, str(data_dict[k]))
            yield [(i+1)/maxlen, temp_cache]


def replace_data_mult(table, template):
    with open(template) as f:
        template = f.read()
        pd_table = pd.read_excel(table)
        dict_table_index = pd_table.to_dict('index')
        for i in list(dict_table_index.keys()):
            maxlen = len(dict_table_index.keys())
            data_dict = dict_table_index[i]
            filename = str(data_dict['@filename'])
            del data_dict['@filename']
            j = list(data_dict.keys())
            temp_cache = template
            for k in j:
                temp_cache = temp_cache.replace(k, str(data_dict[k]))
            yield [(i+1)/maxlen, temp_cache,filename]
            
# 写入函数

def writer(data, filename):
    with open(filename, 'a+') as f:
        f.write(data)
        return filename
def exitsfile(filename):
    script_dir = os.path.join(os.getcwd(), 'script')
    filename = os.path.join(script_dir, filename)
    if Path(filename).exists():
        (name, extention) = os.path.splitext(filename)
        filename = name + '_' + str(token_hex(nbytes=2)) + extention 
        return filename
    else:
        return filename       
        
# 百分比函数


def percentage(i: int, n: int):
    print('\r{}{}%'.format(['/', '-', '\\'][i % 3] if n -
                           i else '', int(i/n*100)), end='' if n-i else '\n')


# if else简写方式
# 上面等效与
# a = '\r{}{}%'.format(['/', '-', '\\'][i % 3]
# if n-i:
#    print(a)
# else:
#    print('')
psg.theme('SystemDefault')
print_out = [
    [psg.Output(size=(85, 30))]
]
temp_input = [
             [psg.Text(text='刷新脚本模板后，单击选择')],
             [psg.Listbox(values=dirlist, size=(30, 6), key='模板列表'), ],
             [psg.Submit(button_text='刷新模板', key='flush', size=(25, 1))]
]


table_input = [
    [psg.Text(text='请选择脚本数据表格')],
    [psg.Input(key='excelname'), psg.FileBrowse(
        button_text='浏览',file_types=(('Table Files','*.xlsx'),) )],
    [psg.Text(text='如果需生成的脚本为单文件，则勾选此项')],
    [psg.Radio('单文件模式', 'mode', key='sing',default=True)],
    [psg.Text(text='如果需生成的脚本为多文件，则勾选此项')],
    [psg.Radio('多文件模式', 'mode', key='mult')],
]
script_creat = [
    [psg.Submit(button_text='生成脚本'), psg.Checkbox(
        '预览脚本，影响生成速度', key='preview')],
    [psg.Text('脚本生成进度'), psg.Text('  ', size=(5, 1), key='percentage')],
    [psg.ProgressBar(max_value=1, size=(61.5, 20), key='进度条')]
]
layout = [
    [psg.Frame('第一步', temp_input),
     psg.Frame('第二步', table_input)
     ],
    [psg.Frame('第三步', script_creat)],
    [psg.Frame('打印信息', print_out)],
    [psg.Cancel('退出')]
]
gui = psg.Window('脚本生成器(不好用也别告诉我)_v0.1').Layout(layout)

# %%
while True:
    event, var_read = gui.Read()
   # print(event,var_read)
    dirlist = file_name(pro_dir, '.pro')
    dict_template = dict(dirlist[1])
    if event == None:
        break
    elif event == '退出':
        break
    elif event == 'flush':
        gui.Element('模板列表').update(values=dirlist[0])
    elif event == '生成脚本':
        templist = gui.Element('模板列表').get()
        if templist == []:
            print('刷新模板列表后，再提交数据')
        elif var_read.get('excelname') == '':
            print('请选择数据表格')
        else:
            template = dict_template.get(templist[0])
            template = os.path.join(pro_dir, template)
            excelname = var_read.get('excelname')
            if  var_read['sing']==True:
                tablename = os.path.split(excelname)[1]
                name = os.path.splitext(tablename)[0]
                data = replace_data_sing(excelname, template)
                scriptname = name + '.txt'
                scriptname = exitsfile(scriptname)
                print(scriptname)
                try:
                    for [i, temp_cache] in data:
                        writer(temp_cache,scriptname)
                        gui.Element('percentage').update('{:.1%}'.format(i))
                        gui.Element('进度条').UpdateBar(i)
                        if var_read.get('preview') == True:
                            print(temp_cache)
                            pass
                        if i == 1:
                            print(scriptname)
                            psg.popup_ok('生成完毕！')
                            i = 0
                            gui.Element('进度条').UpdateBar(i)
                            gui.Element('percentage').update('{:.1%}'.format(i))
                except:
                    psg.popup('出错了，我也不知道为啥！！')
            elif var_read['mult']==True:                    
                data = replace_data_mult(tablename, template)
                try:
                    for [i, temp_cache,filename] in data:
                        writer(temp_cache,filename)
                        gui.Element('percentage').update('{:.1%}'.format(i))
                        gui.Element('进度条').UpdateBar(i)
                        if var_read.get('preview') == True:
                            print(filename)
                        else:
                            pass
                    if i == 1:
                        psg.popup_ok('生成完毕！')
                        i = 0
                        gui.Element('进度条').UpdateBar(i)
                        gui.Element('percentage').update('{:.1%}'.format(i))
                except:
                        psg.popup('出错了，我也不知道为啥！！')

gui.close() # 一定要加上这行，不然退出按钮无法使用

        # print('数据表格为')

# 2020-05-18 1:49完成脚本文件的读取，下一步计划进行表格遍历，然后根据表格读取值生成脚本
# 脚本生成两种方式：
# 1、 一个表格生成一个脚本文件；单文件方式
# 2、一个表格生成多个脚本文件；多文件方式
# %%
# def replace_data(table,template):
#    with open(template) as temp:                                    ##打开模板
#        template = temp.read()                                      ##读入模板
#        fl=pd.read_excel(table)                                     ##读入数据表，并dataframe
#        fl_test = fl.to_dict('index')                               ##以index为key转化为复合字典
#        for i in list(fl_test.keys()):                              ##遍历index值
#            data_dict=fl_test[i]                                    ##读取每行数据组成的字典
#            j = list(data_dict.keys())                              ##将每行数据组成的字典的key转化为list
#            temp_cache=template                                     ##对模板重新赋值
#            for k in j:                                             ##遍历字典key获取key的字符串
#                temp_cache=temp_cache.replace(k,str(data_dict[k]))  ##替换
#            yield [i,temp_cache]                                    ##使用迭代器yield，获取循环中的返回值，
# 2020-5-19 遗留问题：模板文件路径问题
