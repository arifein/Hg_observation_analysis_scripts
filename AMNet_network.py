#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  15 16:04:41 2023
Load Hg0 observation data from AMNet dataset
@author: arifeinberg
"""
#%% Import packagres
import numpy as np
import pandas as pd
#%% Functions used for analysis
def get_data_AMNet(df, station):
    """return daily-averaged value for station
    
    Parameters
    ----------
    df : DataFrame
         All AMNET data
    station : str
         Station code
    """
    # find data of station
    df_station = df[df['SiteID']==station].copy()

    # check for cases where have two instruments at station, use both datasets in that case
    if (station == 'MD98'):
        df_station2 = df[df['SiteID']=='MD99'].copy()
        df_station =  pd.concat([df_station, df_station2]) 
    elif (station == 'MS99'):
        df_station2 = df[df['SiteID']=='MS12'].copy()
        df_station =  pd.concat([df_station, df_station2]) 
    elif (station == 'OH52'):
        df_station2 = df[df['SiteID']=='oh52'].copy()
        df_station2['SiteID'] = 'OH52' # correct lowercase error
        df_station =  pd.concat([df_station, df_station2]) 
    elif (station == 'NY20'):
        df_station2 = df[df['SiteID']=='ny20'].copy()
        df_station2['SiteID'] = 'NY20' # correct lowercase error
        df_station =  pd.concat([df_station, df_station2]) 
    
    # Find where data is invalid
    temp = ((df_station['GEMVal']=='B') | (df_station['GEMVal']=='A')) & (df_station['GEM'] >= 0) # these are valid flags
    
    # filter data
    df_valid = df_station[temp].copy()
    
    # sort data by correct time
    df_valid = df_valid.sort_index()
    
    df_valid = df_valid[['SiteID','collStart','collEnd','GEM']]
    df_valid = df_valid.rename(columns={"collStart": 'timeStart',"collEnd": 'timeEnd'})

    return df_valid

#%% Read all AMNet data
# file name
fn_all= '../../obs_datasets/GEM/AMNET-ALL-h.csv' # change relative path to AMNet data
do = 'all_data/' # directory for outputted daily mean files

# Codes for the sites
site_codes = ['AK03','AL03','AL19','CA48','FL96','GA40','HI00','IL11',
              'IN21','IN34','MD08','MD99','ME97','MI09','MS99',
              'NH06','NJ05','NJ30','NJ54','NY06','NY20','NY43','NY95','OH02',
              'OH52','OK99','PA13','UT96','UT97','VT99','WI07','WV99',
              'AK95','IL69','NY98', 'MA22']
      
# read file with all hourly data
df_all = pd.read_csv(fn_all)
for i in range(len(site_codes)):
    print("Loading site: " + site_codes[i])
    # get data from sites at daily time resolution
    df = get_data_AMNet(df_all, site_codes[i])
    # output csv of daily averages
    fo = do + site_codes[i] + '_all.csv'
    df.to_csv(fo, index=False)
    
