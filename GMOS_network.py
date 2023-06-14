#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  14 16:04:41 2023
Load Hg0 observation data from GMOS dataset
@author: arifeinberg
"""
#%% Import packages
import numpy as np
import pandas as pd
#%% Functions used for analysis
def get_GEM_avg(site, fn):
    """return daily-averaged value for GMOS time series
    
    Parameters
    ----------
    site : string
         name for station
    fn : string
         file name for station

    """
    df_station = pd.read_csv(fn)
    # Find where data is invalid
    df_GEM = df_station[df_station['target']=='gem'].copy()
    # these stations have both GEM and TGM
    tgm_list = ['NIK','BRE','CAL', 'CMA', 'CST', 'EVK', 'ISK','KOD', 'KREGND',
                'LIS', 'LSM', 'MHE','PAL', 'PIR','ROR','SHL','SIS','VAV', 'WAN'
                , 'CPO','LON','MAL','MBA','MIN','MWA','RAO','SLU','STN']
    # convert to datetime format
    df_GEM['tstamp'] = pd.to_datetime(df_GEM['tstamp']) 
    
    # remove missing values
    df_GEM['value'] = df_GEM['value'].mask(df_GEM['value']<0) #missing values

    # resample daily averages for GEM
    df_GEM_d = df_GEM.set_index('tstamp').resample('D').mean().dropna()

    # Need to check sites that are both GEM and TGM
    if site in tgm_list:
        df_TGM = df_station[df_station['target']=='tgm'].copy()
        
        # convert to datetime format
        df_TGM['tstamp'] = pd.to_datetime(df_TGM['tstamp']) 
        
        # remove missing values
        df_TGM['value'] = df_TGM['value'].mask(df_TGM['value']<0) #missing values
        
        # resample daily averages for TGM
        df_TGM_d = df_TGM.set_index('tstamp').resample('D').mean().dropna()
        
        # store the name of the targets within the dataframes, so can differentiate TGM and GEM
        df_TGM_d['target'] = 'TGM'
        df_GEM_d['target'] = 'GEM'
        
        df_GEM_d = pd.concat([df_GEM_d, df_TGM_d])     
    
    return df_GEM_d

def get_data_GMOS(site, dn):
    """Get the daily data for the GMOS site
    
    Parameters
    ----------
    site : string
         Site code
    dn : string
         Path for GMOS mercury files   
    """
    
    # get the filename for the site
    fn = dn + site + '.csv'
        
    # load data for all years into dataframe, take daily average
    df = get_GEM_avg(site, fn)

    # sort data by correct time
    df = df.sort_index()
                    
    return df

#%% Read GMOS data
# station = 'BAR'

# stations_all = ['AMS','BAR','BRE','CAL','CHE','CMA','CPO','CST','DDU',
#                 'DOC','EVK','GVB','ISK','KIS','KOD','KREGND','LIS','LON',
#                 'LSM','MAL','MAN','MBA','MCH','MHE','MIN','MWA','NIK',
#                 'PAL','PIR','PSA','RAO','ROR','SHL','SIS','SLU','STN','TRO',
#                 'VAV','WAN','ZEP','MAU']
stations_all = ['RAO', 'CPO', 'MBA']
dn = '../../obs_datasets/TGM/GMOS/' # directory for GMOS files, change to your path
do = '../misc_Data/' # directory for outputted daily mean files

# run loop over sites to load and process data
for station in stations_all:
    print("Loading site: " + station)
    # get daily data from site
    df = get_data_GMOS(station, dn)
    # output csv of daily averages
    fo = do + station + '_d.csv'
    df.to_csv(fo)