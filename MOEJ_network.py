#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  14 16:04:41 2023
Load Hg0 observation data from MOEJ dataset (Japan)
@author: arifeinberg
"""
#%% Import packages
import glob
import numpy as np
import pandas as pd
#%% Functions used for analysis
def get_filenames_MOEJ(dn, site):
    """Get the data filename(s) for the site
    
    Parameters
    ----------
    dn : string
         Path for MOEJ mercury files
    site : string
         Site code
    """
    
    if site=='CHE':
        fn = [dn + 'CapeHEDO_GEM_2007-2022/CapeHEDO_GEM_*.csv'] 
    elif site=='OGA':
        fn = [dn + 'OGA_GEM_2014-2022/OGA_GEM_*.csv'] 
    else:
        fn = ['']
    return fn

def load_data_MOEJ(site, dn,  fn_a):
    """Load the data over all years for the site
    
    Parameters
    ----------
    site : string
         Site code
    dn : string
         Path for MOEJ mercury files                      
    fn_a : list
         List of file names
         
    """

    # create empty data frame to store all sites and years
    frame = []
        
    # Loop over all data files, concatenate
    for fn in fn_a: # loop over filenames
        for f in glob.glob(fn): # loop over the different file years
            print(f)
            # load dataset for year
            df_d_f = pd.read_csv(f)            
            # append to frame, so that can later concatenate
            df_d_temp = frame.append(df_d_f)
            
    # concatenate all data frames        
    df = pd.concat(frame)
    return df

def get_data_MOEJ(site, dn):
    """Get the daily data for the MOEJ site
    
    Parameters
    ----------
    site : string
         Site code
    dn : string
         Path for MOEJ mercury files   
    """
    
    # get the list of filename formats for the site
    fn_a = get_filenames_MOEJ(dn, site)
    
    # load data for all years into dataframe
    df = load_data_MOEJ(site, dn, fn_a)
    
    # Check as well that concentrations are non-negative
    # bool_neg = df.iloc[:,1] <= 0
    # print(sum(bool_neg))
    
    # Create datetime variables for time of measurement
    df['time'] = pd.to_datetime(df.iloc[:,0])
    
    # sort data by correct time
    df = df.sort_values(by='time')
    
    # resample daily averages
    df_d = df.set_index('time').resample('D').mean().dropna()
                    
    return df_d

#%% Read MOEJ data
stations_all = ['CHE', 'OGA']
dn = '../../obs_datasets/GEM/CapeHEDO_GEM_2007-2022/' # directory for MOEJ files, change to your path
do = '../misc_Data/' # directory for outputted daily mean files
import matplotlib.pyplot as plt

# run loop over sites to load and process data
for station in stations_all:
    print("Loading site: " + station)
    # get daily data from site
    df = get_data_MOEJ(station, dn)
    # output csv of daily averages
    fo = do + station + '_d.csv'
    df.to_csv(fo)
