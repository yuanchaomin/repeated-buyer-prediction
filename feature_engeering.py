#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 27 15:17:57 2016

@author: yuanchaomin
"""

#%% loading package
import pandas as pd
from pandas import DataFrame,Series
import re
import collections
import time
import numpy as np

#%%
start_time = time.time()
#%% loading data
df1 = pd.read_csv('C:/Users/Chaomin/one/Project/data/data_example.csv').dropna()
#%%
"""The format of month and action_code should be int."""
def pattern(month,action_code):
    if month < 10:
        return (r'0' + str(month) + r'\d{2}\:' + str(action_code) + r'\b')
    else:
        return (str(month) + r'\d{2}\:' + str(action_code) + r'\b')
#%%
month_list = ['Jun','Jul','Aug','Sep','Oct','Nov']

def generate():
    variable_list_1 = []
    variable_list_2 = []
    for month in month_list:
        for i in range(4):
            variable_list_1.append("pattern_{0}_{1}".format(month,i))
    variable_list_2 = list(variable_list_1)
   
    for i in range(len(variable_list_2)):
        variable_list_2[i] = pattern(i//4 + 6, i%4)
    
    return (variable_list_1, variable_list_2)

variable_list_1,variable_list_2 = generate()

#%%
def split_(data,new_column_name,pattern,target_column):
    regex = re.compile(pattern)
    f = lambda x: regex.findall(x)
    data[new_column_name] = data[target_column].apply(f)

#%%
def split_no_duplicate(data,new_column_name,pattern,target_column):
    regex = re.compile(pattern)
    f = lambda x: list(set(regex.findall(x)))
    data[new_column_name] = data[target_column].apply(f)
#%% split log into timestamp and action_type
intermediate_columnname_list = []
for month in month_list:
    for i in range(4):
        intermediate_columnname_list.append("{0}_{1}".format(month,i))

for i in range(len(intermediate_columnname_list)):
    split_(df1,intermediate_columnname_list[i],variable_list_2[i],'activity_log')
#%% split log into timestamp and action_type without duplicates
intermediate_columnname_no_dplicate_list = []
for month in month_list:
    for i in range(4):
        intermediate_columnname_no_dplicate_list.append("{0}_{1}_no_duplicates".format(month,i))

for i in range(len(intermediate_columnname_no_dplicate_list)):
    split_no_duplicate(df1,intermediate_columnname_no_dplicate_list[i],variable_list_2[i],'activity_log')   
#%%
#del df1['activity_log']
#%%
new_column_name_list = []
for month in month_list:
    for i in range(4):
        new_column_name_list.append("{0}_{1}_Count".format(month,i))

new_column_name_no_duplicates_list = []
for month in month_list:
    for i in range(4):
        new_column_name_no_duplicates_list.append("{0}_{1}_no_duplicate_Count".format(month,i))

        
actiontype_month_count_list = []
for i in range(4):
    for month in month_list:
        actiontype_month_count_list.append("{0}_{1}_Count".format(month,i)) 
        
zip_columnname_list = list(zip(new_column_name_list,intermediate_columnname_list))
zip_columnname_no_duplicate_list = list(zip(new_column_name_no_duplicates_list,intermediate_columnname_no_dplicate_list))

#%%
count_f = lambda x: sum(collections.Counter(x).values())
for k in range(len(zip_columnname_list)):
    df1[zip_columnname_list[k][0]] = df1[zip_columnname_list[k][1]].apply(count_f)
    #del df1[zip_columnname_list[k][1]]
for k in range(len(zip_columnname_no_duplicate_list)):
    df1[zip_columnname_no_duplicate_list[k][0]] = df1[zip_columnname_no_duplicate_list[k][1]].apply(count_f)
    #del df1[zip_columnname_list[k][1]]

#%%
action_list = ["%i"%i for i in range(4)]
zip_month_action_list = [(x,y) for x in month_list for y in action_list]
zip_action_month_list = [(x,y) for x in action_list for y in month_list]
                         
index_month_action = pd.MultiIndex.from_tuples(zip_month_action_list, names=['month', 'action_type'])
index_action_month = pd.MultiIndex.from_tuples(zip_action_month_list, names=['action_type', 'month'])

new_column_name_series = pd.Series(new_column_name_list, index = index_month_action)
actiontype_month_count_series = pd.Series(actiontype_month_count_list, index = index_action_month)




#%% sum of monthly  count by different action type
total_action_count_list = []
for action_type in action_list:
        total_action_count_list.append("total_{0}_Count".format(action_type))

for i in range(len(total_action_count_list)):
    df1[total_action_count_list[i]] = df1[actiontype_month_count_series[action_list[i]]].sum(axis = 1)

df1['sum_action_count'] = df1[[total_action_count_list[i] for i in range(4)]].sum(axis = 1)
#%%
def action_ratio_name():
    action_ratio_name_list = []
    for action_type in action_list:
        action_ratio_name_list.append("{0}_ratio_of_all".format(action_type))
    return action_ratio_name_list

action_ratio_name_list = action_ratio_name()

for i in range(len(action_ratio_name_list)):
        df1[action_ratio_name_list[i]]= df1[total_action_count_list[i]]/df1['sum_action_count']
#%%
def monthly_aggregate_feature_name():
    function_name = ['avg','std','max','med']
    action_function_name_list = []
    for action_type in action_list:
        for i in range(len(function_name)):
            action_function_name_list.append("{0}_monthly_{1}".format(action_type,function_name[i]))
    zip_action_function_list = [(x,y) for x in action_list for y in function_name]
    index_month_action = pd.MultiIndex.from_tuples(zip_action_function_list, names=['action', 'function'])                         
    action_function_series = pd.Series(action_function_name_list, index = index_month_action)
    return action_function_series                   

action_function_series = monthly_aggregate_feature_name()
#%% caculating values
def caculate_action_aggregate_feature():
    f_avg = np.average
    f_std = np.std
    f_max = np.amax
    f_med = np.median
    function_name_list = ['avg','std','max','med']
    function_list = [f_avg, f_std, f_max, f_med]
    for i in action_list:
        for j in range(len(function_list)):
            df1[action_function_series[i][function_name_list[j]]] = df1[actiontype_month_count_series[i]].apply(function_list[j],axis = 1)
            

            
caculate_action_aggregate_feature()
#%%
df1.to_csv('C:/Users/Chaomin/one/Project/data/data_example5.csv')
#%%
print('---%s seconds ---' %(time.time() - start_time))
