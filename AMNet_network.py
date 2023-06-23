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
    
    # Find where data is invalid
    temp = ((df_station['GEMVal']=='B') | (df_station['GEMVal']=='A')) & (df_station['GEM'] >= 0) # these are valid flags
    
    # filter data
    df_valid = df_station[temp].copy()

    # load times
    time_start = pd.to_datetime(df_valid['collStart'])
    time_end = pd.to_datetime(df_valid['collEnd'])

    # find midpoint time
    time_mid = ((time_end - time_start)/2 + time_start).values 
    df_valid['time_GEM'] = time_mid
    
    # get only years from time_mid, so that can use cutoff
    # resample daily averages
    df_valid_d = df_valid.set_index('time_GEM').resample('D').mean().dropna()
    
    # sort data by correct time
    df_valid_d = df_valid_d.sort_index()
        
    return df_valid_d

#%% Read all AMNet data
# file name
fn_all= '../../obs_datasets/GEM/AMNET-ALL-h.csv' # change relative path to AMNet data
do = '../misc_Data/' # directory for outputted daily mean files

# Names of long-term sites in the AMNet network 
site_names = ['Birmingham', 'Pensacola','Yorkville','Mauna Loa','Piney Reservoir',
              'Beltsville','Grand Bay NERR','New Brunswick','Bronx','Huntington Wildlife',
              'Rochester','Athens','South Bass Island','Stillwell','Salt Lake City',
              'Underhill','Horicon Marsh']

# Codes for the sites
site_codes = ['AL19','FL96','GA40', 'HI00','MD08','MD98','MS99','NJ30',
              'NY06','NY20','NY43','OH02','OH52','OK99','UT97','VT99','WI07',]
# read file with all hourly data
df_all = pd.read_csv(fn_all)
for i in range(len(site_names)):
    print("Loading site: " + site_names[i])
    # get data from sites at daily time resolution
    df = get_data_AMNet(df_all, site_codes[i])
    # output csv of daily averages
    fo = do + site_codes[i] + '_d.csv'
    df.to_csv(fo)
    
