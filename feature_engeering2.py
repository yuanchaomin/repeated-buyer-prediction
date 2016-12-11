#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 27 15:17:57 2016

@author: yuanchaomin
"""

#%% loading package
import pandas as pd
#from pandas import DataFrame,Series
import re
import collections
import time
import numpy as np
import regex as reg
#%% the start of counting 
start_time = time.time()

#%% loading data
df1 = pd.read_csv('D:\project\one\Project\data\data_example.csv').dropna()

#%%
"""The format of month and action_code should be int."""
def pattern(month,action_code):
    if month < 10:
        return (r'0' + str(month) + r'\d{2}\:' + str(action_code) + r'\b')
    else:
        return (str(month) + r'\d{2}\:' + str(action_code) + r'\b')

#%%  The list of name
month_list = ['Jun','Jul','Aug','Sep','Oct','Nov']
action_list = ["%i"%i for i in range(4)]

#%%
def generate():
    month_action_pattern_name = []
    for month in month_list:
        for i in range(4):
            month_action_pattern_name.append("{0}_{1}_pattern".format(month,i))
    #zip_action_month_list = [(x,y) for x in action_list for y in month_list]
    month_action_pattern = list(month_action_pattern_name)
    
    for i in range(len(month_action_pattern)):
        month_action_pattern[i] = pattern(i//4 + 6, i%4)
    
    return month_action_pattern_name,month_action_pattern
    
month_action_pattern_name, month_action_pattern = generate()

#%%
def split_(data,new_column_name,pattern,target_column):
    regex = re.compile(pattern)
    f = lambda x: regex.findall(x)
    data[new_column_name] = data[target_column].apply(f)
    
def split_no_duplicate(data,new_column_name,pattern,target_column):
    regex = re.compile(pattern)
    f = lambda x: list(set(regex.findall(x)))
    data[new_column_name] = data[target_column].apply(f)
    
def split_itemid_from_log(data,new_column_name, pattern, target_column):
    regex = reg.compile(pattern)
    f = lambda x: regex.findall(x)
    data[new_column_name] = data[target_column].apply(f)
    
def split_categoryid_from_log(data,new_column_name, pattern, target_column):
    regex = reg.compile(pattern)
    f = lambda x: regex.findall(x)
    data[new_column_name] = data[target_column].apply(f)
    
def split_brandid_from_log(data,new_column_name, pattern, target_column):
    regex = reg.compile(pattern)
    f = lambda x: regex.findall(x)
    data[new_column_name] = data[target_column].apply(f)
    
#%% split log into timestamp and action_type

def timestamp_action_pair():
    timestamp_action_pair_list = []
    timestamp_action_pair_no_duplicate_list = []
    for month in month_list:
        for i in range(4):
            timestamp_action_pair_list.append("{0}_{1}".format(month,i))
            timestamp_action_pair_no_duplicate_list.append("{0}_{1}_no_duplicate".format(month,i))

    for i in range(len(timestamp_action_pair_list)):
        split_(df1, timestamp_action_pair_list[i], month_action_pattern[i],'activity_log')
    
    for i in range(len(timestamp_action_pair_no_duplicate_list)):
        split_no_duplicate(df1, timestamp_action_pair_no_duplicate_list[i], month_action_pattern[i],'activity_log')
    
    return timestamp_action_pair_list, timestamp_action_pair_no_duplicate_list

timestamp_action_pair_list, timestamp_action_pair_no_duplicate_list = timestamp_action_pair()

#%% extract item information from log
def extract_item_from_log():
    extract_item_pattern = r'\d{1,10}(?=(?:\:\d{1,10}){4})'
    split_itemid_from_log(df1,'item_info',extract_item_pattern,'activity_log')
extract_item_from_log()

def extract_category_from_log():
    extract_categoryid_pattern = r'(?<=\d{1,10}\:)\d{1,10}(?=(?:\:\d{1,10}){3}\#)'
    split_categoryid_from_log(df1,'category_info',extract_categoryid_pattern,'activity_log')
extract_category_from_log()

def extract_brand_from_log():
    extract_brandid_pattern = r'(?<=(?:\d{1,10}\:){2})\d{1,10}(?=(?:\:\d{1,10}){2}\#)'
    split_brandid_from_log(df1,'brand_info',extract_brandid_pattern,'activity_log')
extract_brand_from_log()
#%%
def create_count_name():

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
    
    
    zip_columnname_list = list(zip(new_column_name_list,timestamp_action_pair_list))
    zip_columnname_no_duplicate_list = list(zip(new_column_name_no_duplicates_list,timestamp_action_pair_no_duplicate_list))

    return zip_columnname_list, zip_columnname_no_duplicate_list

zip_columnname_list, zip_columnname_no_duplicate_list = create_count_name()

#%% Counting the number of each action in each month
def count_monthly_action():
    count_f = lambda x: sum(collections.Counter(x).values())
    for k in range(len(zip_columnname_list)):
        df1[zip_columnname_list[k][0]] = df1[zip_columnname_list[k][1]].apply(count_f)
    for k in range(len(zip_columnname_no_duplicate_list)):
        df1[zip_columnname_no_duplicate_list[k][0]] = df1[zip_columnname_no_duplicate_list[k][1]].apply(count_f)
    
    df1['item_count'] = df1['item_info'].apply(count_f)
    df1['category_count'] = df1['category_info'].apply(count_f)
    df1['brand_count'] = df1['brand_info'].apply(count_f)

count_monthly_action()
#%%
def action_month_count_name():
    zip_action_month_list = [(x,y) for x in action_list for y in month_list]
    action_month_list = [("{1}_{0}_Count".format(x,y)) for x in action_list for y in month_list]
    index_action_month = pd.MultiIndex.from_tuples(zip_action_month_list, names=['action_type', 'month'])
    action_month_count_series = pd.Series(action_month_list, index = index_action_month)
    
    return action_month_count_series
action_month_count_series = action_month_count_name()

#%% sum of monthly  count by different action type
def monthly_sum():
    total_action_count_list = []
    for action_type in action_list:
            total_action_count_list.append("total_{0}_Count".format(action_type))

    for i in range(len(total_action_count_list)):
        df1[total_action_count_list[i]] = df1[action_month_count_series[action_list[i]]].sum(axis = 1)

    df1['sum_action_count'] = df1[[total_action_count_list[i] for i in range(4)]].sum(axis = 1)
    
    return total_action_count_list

total_action_count_list = monthly_sum()

#%%
def action_ratio():
    action_ratio_name_list = []
    for action_type in action_list:
        action_ratio_name_list.append("{0}_ratio_of_all".format(action_type))
        
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
            df1[action_function_series[i][function_name_list[j]]] = df1[action_month_count_series[i]].apply(function_list[j],axis = 1)
caculate_action_aggregate_feature()


#%%
df1.to_csv('D:\project\one\Project\data\data_example5.csv')

#%%
print('---%s seconds ---' %(time.time() - start_time))
