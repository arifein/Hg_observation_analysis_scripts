#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 2023
Load Hg0 observation data courtesy from Experimental Lakes Area courtesy of Vincent St. Louis
@author: arifeinberg
"""
#%% Import packages
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
    df = pd.read_excel(fn)            
        
    # Create datetime variables for start and end of measurements
    time_start = df['Sample date/Time start']
    time_end = df['Sample date/Time end']

    # find midpoint time
    time_mid = ((time_end - time_start)/2 + time_start).values
    df['time_mid'] = time_mid
    
    return df

def get_data_misc(site, dn):
    """Get the daily data for the misc site
    
    Parameters
    ----------
    site : string
         Site code
    dn : string
         Path for misc mercury files   
    """
    
    # filename of site
    if site == 'ELA':
        fn = dn + 'ELA_TEKRAN_DATA_2005-2013_GEM-PHg-RGM_3-hr_averages.xlsx'
    else:
        print('error, site not found!')
    
    # load data for all years into dataframe
    df = load_data_misc(site, fn)
    
    # Rename columns that have spaces
    df = df.rename(columns={"GEM (ng/m^3)": "GEM", 
                            "RGM (pg/m^3)": "RGM_pg_m3",
                            "PHg (pg/m^3)": "PHg_pg_m3"})
            
    # resample daily averages
    df_d = df.set_index('time_mid').resample('D').mean().dropna()
                    
    return df_d

#%% Read misc data
stations_all = ['ELA']
dn = '../../obs_datasets/GEM/' # directory for misc files, change to your path
do = '../misc_Data/' # directory for outputted daily mean files

# run loop over sites to load and process data
for station in stations_all:
    print("Loading site: " + station)
    # get daily data from site
    df = get_data_misc(station, dn)
    # output csv of daily averages
    fo = do + station + '_d.csv'
    df.to_csv(fo)