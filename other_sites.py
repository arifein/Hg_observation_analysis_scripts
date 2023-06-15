#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  14 16:04:41 2023
Load misc Hg0 observation data courtesy of D. Custodio
@author: arifeinberg
"""
#%% Import packages
import glob
import numpy as np
import pandas as pd
#%% Functions used for analysis
def load_data_misc(site, fn):
    """Load the data over all years for the site
    
    Parameters
    ----------
    site : string
         Site code
    fn : string
         File name for misc data
         
    """
        
    # load dataset for all misc Hg data
    df_d_f = pd.read_csv(fn)            
    
    # select time and save as datetime variable
    df_d_f['time'] = pd.to_datetime(df_d_f.iloc[:,0], format='%Y-%m-%d %H:%M')
        
    # drop rows with NaN values
    df_na = df_d_f.dropna()

    return df_na

def get_data_misc(site, dn):
    """Get the daily data for the misc site
    
    Parameters
    ----------
    site : string
         Site code
    dn : string
         Path for misc mercury files   
    """
    
    # filename of misc sites
    fn = dn + site + '.csv'
    
    # load data for all years into dataframe
    df = load_data_misc(site, fn)
    
    # Check as well that concentrations are non-negative
    # bool_neg = df['MH'] <= 0
    # print(sum(bool_neg))
            
    # resample daily averages
    df_d = df.set_index('time').resample('D').mean().dropna()
                    
    return df_d

#%% Read misc data
stations_all = ['MHD']
dn = '../../obs_datasets/TGM/misc/' # directory for misc files, change to your path
do = '../misc_Data/' # directory for outputted daily mean files

# run loop over sites to load and process data
for station in stations_all:
    print("Loading site: " + station)
    # get daily data from site
    df = get_data_misc(station, dn)
    # output csv of daily averages
    fo = do + station + '_d.csv'
    df.to_csv(fo)
    