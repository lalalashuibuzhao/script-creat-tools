# coding: utf-8
# @Author: Fule
# @Date:   2020-05-20 18:03:50
# @Last Modified by:   Fule
# @Last Modified time: 2020-05-24 04:41:00

import os
from pathlib import Path
from secrets import token_hex
import datetime

import pandas as pd
import PySimpleGUI as psg
import xlrd
from pandas import DataFrame as df

#from pandas.plotting._matplotlib import tabl

pro_dir = os.path.join(os.getcwd(), 'profile')
script_dir = os.path.join(os.getcwd(), 'script')
dirlist = []
event = ''
data_return=''
counter = 0
script_prew = ''
error = 'chushizhi'

if Path(script_dir).is_dir():
    pass
    #print('目录存在')
else:
    os.makedirs(script_dir)
    #print('创建目录')

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
    with open(template, encoding = 'utf-8') as f:
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


def replace_data_mult(table, template ,cheack):
    with open(template,encoding='utf-8') as f:
        template = f.read()
        pd_table = pd.read_excel(table)
        if cheack == True:
            if '@filename' not in list(pd_table.columns):
                popup=psg.popup_cancel('\n表格里面没有@filename列\n检查下！！！',title='提示',keep_on_top=True)
                popup = 'Cancel'
                return popup #跳出点1
            else:
                pass
            filenanme_columns = pd_table['@filename']
            filename_nodup = filenanme_columns.drop_duplicates('first',False)
            if len(filename_nodup) == 1:
                warning = '警告！！！\n数据表中文件名只有一个或为空，\n （1）点击OK，将强行使用多文件模式！！后果不可预料！！   \n （2）点击Cancel检查下表格\n （3）X掉弹窗将自动采用单文件模式生成脚本'
                popup = psg.popup_ok_cancel(warning,title='警告',  )
                return popup
            elif len(filename_nodup) > 100:
                warning = '警告！！！\n将生成%s个脚本文件\n（1）确定继续作死，点OK\n（2）点Cancel选择不作死\n （3）X掉弹窗你    也可以试试^_^  '%(len(pd_table['@filename']))
                popup = psg.popup_ok_cancel(warning,title='警告' )
                return popup
            else:
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
        else:
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

# 文件名函数

def script_name(excelname):
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    filename_nopath = os.path.split(excelname)[1] #分离路径和文件名
    filename_noextention  = os.path.splitext(filename_nopath)[0] #分离文件名和扩展名
    script_dir = os.path.join(os.getcwd(), 'script')
    #filename = os.path.join(script_dir, '%s.txt'%now)
    #if Path(filename).exists():
        #filename_noextention = os.path.splitext(filename_nopath)[0] +'_'+str(token_hex(nbytes=2))
    filename = os.path.join(script_dir, '%s.txt'%(filename_noextention+now))
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
    [psg.Output(size=(85, 15),key='messge',)]
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
    [psg.Radio('单文件模式', 'mode', key='sing',default=True,change_submits=True,enable_events=True)],
    [psg.Text(text='如果需生成的脚本为多文件，则勾选此项')],
    [psg.Radio('多文件模式', 'mode', key='mult',change_submits=True,enable_events=True)],
]
script_creat = [
    [psg.Submit(button_text='生成脚本'), psg.Checkbox(
        '预览脚本，单文件下可以见', key='preview',visible=True)],
    [psg.Text('脚本生成进度'), psg.Text('  ', size=(5, 1), key='percentage')],
    [psg.ProgressBar(max_value=1, size=(61.5, 20), key='进度条')]
]
print_tab = [psg.Multiline(size=(50,20),key='view',tooltip='小提示:\n预览界面可以直接看到脚本的输出信息，\n建议单文件模式使用。')]
tab1_layout = [
    [psg.Frame('第一步', temp_input),psg.Frame('第二步', table_input)],
    [psg.Frame('第三步', script_creat)],
    [psg.Frame('打印信息', print_out)],
]
tab2_layout = [print_tab]
layout=[
    [psg.TabGroup(
        [
            [psg.Tab('主页面',tab1_layout,)],[psg.Tab('脚本预览界面',tab2_layout,)]
        ]
    )],
        [psg.Cancel('退出')]
]
gui = psg.Window('脚本生成器(好用给我点个赞！^_^)_v0.2').Layout(layout)
a = 'python脚本启动成功，加载界面成功！！\n请在刷新模板后，选择模板\n'
b = '请在刷新模板后，选择模板\n'

# %%
while True:
    event, var_read = gui.Read()
    counter+=1
    [print(a) if counter<2 else b]
    #print(event,var_read)
    dirlist = file_name(pro_dir, '.pro')
    dict_template = dict(dirlist[1])
    if event == None:
        break
    elif event == '退出':
        break
    elif event == 'flush':
        gui.Element('模板列表').update(values=dirlist[0])
        gui.Element('view').expand(expand_x= True, expand_y= True)
    elif event == 'mult':
        gui.Element('preview').Update(disabled=True)  
    elif event == 'sing':
        gui.Element('preview').Update(disabled=False)
    else:
        pass
    while  event == '生成脚本':
        print('读入数据成功，\n开始读入生成模式！！\n')
        templist = gui.Element('模板列表').get()
        if templist == []:
            print('刷新模板列表后，再提交数据')
            break
        elif var_read.get('excelname') == '':
            print('请选择数据表格')
            break
        else:
            template = dict_template.get(templist[0])
            template = os.path.join(pro_dir, template)
            excelname = var_read.get('excelname')
            if  var_read['sing']==True:
                print('单文件模式！！\n')
                scriptname = script_name(excelname)
                data = replace_data_sing(excelname, template)
                # print('生成脚本%s成功'%(scriptname))
                try:
                    for [i, temp_cache] in data:
                        writer(temp_cache,scriptname)
                        gui.Element('percentage').update('{:.1%}'.format(i))
                        gui.Element('进度条').UpdateBar(i)
                        if var_read.get('preview') == True:
                            script_prew = script_prew +'%s'%temp_cache
                            #print(temp_cache)
                        if i == 1:
                            print('脚本名为\n%s,\n请在Script目录查看！！'%(scriptname))
                            gui.Element('view').update(script_prew)
                            psg.popup_ok('生成完毕！')
                            script_prew = ''
                            i = 0
                            gui.Element('进度条').UpdateBar(i)
                            gui.Element('percentage').update('{:.1%}'.format(i))
                except :
                    psg.popup('出错了，我也不知道为啥！！')
                break


            if  var_read['mult']==True:
                print('多文件循环写入模式\n')
                #print(error)
                if error == 'chushizhi':  
                    data = replace_data_mult(excelname, template,True)
                    try:
                    #触发异常，使用try.....except....else
                        next(data)
                    except StopIteration as stop:
                    #捕获预期异常，同时对异常进行处理
                        error = str(stop)
                        #print(err)
                        if error == 'Cancel':
                            print('中断脚本生成！！\n')
                            error = 'chushizhi'
                            break

                        elif error == '':
                            var_read['sing']=True
                            var_read['mult']=False
                            gui.Element('sing').Update(value=True)
                            event = 'sing'
                            gui.Element('preview').Update(disabled=False)
                            print('强行进入单文件模式\n')
                            error = 'chushizhi'
                            event = '生成脚本'
                            #print(var_read)

                        else:
                            print('多文件模式启动\n')
                            event = '生成脚本'
                    else:
                        print('@filename检查正常')
                        error = '文件名正常'
                else:
                    data = replace_data_mult(excelname, template,False)
                    create_dir_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                    script_dir = os.path.join(script_dir,create_dir_time)
                    os.mkdir(script_dir)
                    for data_return in data:
                        [i,temp_cache,filename] = data_return
                        #if filename == 'nan':
                            #filename = filename+ str(token_hex(nbytes=2))
                            #scriptname = os.path.join(script_dir,str(filename))
                        #else: 
                        filename = str(filename) +'.txt'     
                        scriptname = os.path.join(script_dir,filename)
                        writer(temp_cache,scriptname)
                        gui.Element('percentage').update('{:.1%}'.format(i))
                        gui.Element('进度条').UpdateBar(i)
                        print(scriptname)
                        if i == 1:
                            print('请在Script\%s目录查看脚本！！\n'%create_dir_time)
                            psg.popup_ok('生成完毕！')
                            i = 0
                            gui.Element('进度条').UpdateBar(i)
                            gui.Element('percentage').update('{:.1%}'.format(i))
                            error = 'chushizhi'
                    break    
                    #打断while event == '生成脚本‘循环
            #print(7)
        #break
    #break
                                                #print('未知异常')
                                                #psg.popup('程序中止！！')

gui.close() # 一定要加上这行，不然退出按钮无法使用

        # print('数据表格为')

# 2020-05-18 1:49完成脚本文件的读取，下一步计划进行表格遍历，然后根据表格读取值生成脚本
# 脚本生成两种方式：
# 1、 一个表格生成一个脚本文件；单文件方式
# 2、一个表格生成多个脚本文件；多文件方式
# %%

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
# 2020-5-22 遗留问题，面板结构调整，缩进线需要新插件，界面太大
#layout = [
#    [sg.TabGroup(
#                [[sg.Tab('Tab 1', tab1_layout, tooltip='tip'), sg.Tab('Tab 2',#tab2_layout)]], tooltip='TIP2')],
#    [sg.Button('Read')]
#          ]  
# 2020-5-24 优化了脚本结构采取事件捕获的方式进行脚本转跳，单独列出了预览界面，关闭了多# 文件的预览