#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  23 16:04:41 2023
Load MLO dataset from 2002–2010 courtesy of Matt Landis (EPA)
@author: arifeinberg
"""
#%% Import packages
import glob
import numpy as np
import pandas as pd
#%% Functions used for analysis
def load_data_MLO(site, fn):
    """Load the data over all years for the MLO site
    
    Parameters
    ----------
    site : string
         Site code
    fn : string
         File name for misc data
         
    """
        
    # load dataset for all misc Hg data
    df = pd.read_csv(fn)            
    
    # select time and save as datetime variable
    str_time = df['Year'].apply(str) + ' ' + df['Month'].apply(str) + \
        ' ' + df['Day'].apply(str) + ' ' +  df['Hour'].apply(str) + ' ' + \
            df['Minute'].apply(str)
    df['time'] = pd.to_datetime(str_time, format='%Y %m %d %H %M')
        
    # drop rows with NaN values
    df_na = df.dropna(subset=['Hg0 (ngm-3)'])
    
    df_na = df_na[['time','Hg0 (ngm-3)','Hg(p) (pgm-3)','Hg(p)_2 (pgm-3)',
                   'RGM (pgm-3)']]
    df_na = df_na.rename(columns={"Hg0 (ngm-3)": 'GEM'})
    
    return df_na

def get_data_MLO(site, dn):
    """Get the daily data for MLO
    
    Parameters
    ----------
    site : string
         Site code
    dn : string
         Path for misc mercury files   
    """
    
    # filename of misc sites
    fn = dn + 'mauna_loa_All_processed.csv'
    
    # load data for all years into dataframe
    df = load_data_MLO(site, fn)
    
    # filter rows with extremely high Hg values
    bool_high = df['GEM'] < 10 # remove values over 10 ng m-3
        
    # Filter data for validity
    df = df[bool_high]

    # resample daily averages
    df_d = df.set_index('time').resample('D').mean().dropna()
                    
    return df_d
#%% Read MLO data
stations_all = ['MLO1'] # add one to differentiate from AMNet data
dn = '../../obs_datasets/GEM/MLO_data_Landis/' # directory for misc files, change to your path
do = '../misc_Data/' # directory for outputted daily mean files

# run loop over sites to load and process data
for station in stations_all:
    print("Loading site: " + station)
    # get daily data from site
    df = get_data_MLO(station, dn)
    # output csv of daily averages
    fo = do + station + '_d.csv'
    df.to_csv(fo)
