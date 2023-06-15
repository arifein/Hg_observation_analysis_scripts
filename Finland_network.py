#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  14 16:04:41 2023
Load Hg0 observation data from Finland dataset (courtesy of ￼Katriina Kyllönen)
@author: arifeinberg
"""
#%% Import packages
import glob
import numpy as np
import pandas as pd
#%% Functions used for analysis
def get_sitename(site):
    """Get the name for the site from the codes
    
    Parameters
    ----------
    site : string
         Site code
    """
    
    if site=='PAL1':
        sitename = 'Pallas'
    elif site=='HYY':
        sitename = 'Hyytiälä'
    elif site=='VIR':
        sitename = 'Virolahti '

    return sitename

def load_data_FIN(site, fn):
    """Load the data over all years for the site
    
    Parameters
    ----------
    site : string
         Site code
    fn : string
         File name for finnish data
         
    """
        
    # load dataset for all Finnish Hg data
    df_d_f = pd.read_csv(fn)            
    
    # select time and save as datetime variable
    date_var = pd.to_datetime(df_d_f.iloc[:,0], format='%d/%m/%Y %H.%M')
    
    # select correct site
    sitename = get_sitename(site)
    Hg_var = df_d_f[sitename]
    
    df = pd.DataFrame({'time': date_var, 'TGM': Hg_var})
    
    # drop rows with NaN values
    df_na = df.dropna()

    return df_na

def get_data_FIN(site, dn):
    """Get the daily data for the FIN site
    
    Parameters
    ----------
    site : string
         Site code
    dn : string
         Path for FIN mercury files   
    """
    
    # filename of Finnish sites
    fn = dn + 'Finnish_TGM_final.csv'
    
    # load data for all years into dataframe
    df = load_data_FIN(site, fn)
    
    # Check as well that concentrations are non-negative
    # bool_neg = df.iloc[:,1] <= 0
    # print(sum(bool_neg))
        
    # sort data by correct time
    df = df.sort_values(by='time')
    
    # resample daily averages
    df_d = df.set_index('time').resample('D').mean().dropna()
                    
    return df_d

#%% Read FIN data
stations_all = ['PAL1']#, 'HYY', 'VIR']
dn = '../../obs_datasets/TGM/misc/' # directory for FIN files, change to your path
do = '../misc_Data/' # directory for outputted daily mean files

# run loop over sites to load and process data
for station in stations_all:
    print("Loading site: " + station)
    # get daily data from site
    df = get_data_FIN(station, dn)
    # output csv of daily averages
    fo = do + station + '_d.csv'
    df.to_csv(fo)
    