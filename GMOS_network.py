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
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

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
    df_GEM_d = df_GEM.set_index('tstamp')

    # Need to check sites that are both GEM and TGM
    if site in tgm_list:
        df_TGM = df_station[df_station['target']=='tgm'].copy()
        
        # convert to datetime format
        df_TGM['tstamp'] = pd.to_datetime(df_TGM['tstamp']) 
        
        # remove missing values
        df_TGM['value'] = df_TGM['value'].mask(df_TGM['value']<0) #missing values
        
        # resample daily averages for TGM
        df_TGM_d = df_TGM.set_index('tstamp')
        
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
    if site=='PAL_GMOS': # change name to be consistent
      site = 'PAL'

    # get the filename for the site
    fn = dn + site + '.csv'
        
    # load data for all years into dataframe, take daily average
    df = get_GEM_avg(site, fn)

    # sort data by correct time
    df = df.sort_index().dropna()
     
    # clean up column names
    df['tstamp'] = df.index
    df = df[['FID','tstamp','value']]
    df = df.rename(columns={"FID": 'SiteID',"tstamp": 'timeMid', "value":'GEM'})
    df['SiteID'] = site # rename to site
    if site=='PAL': # change name to be consistent
      df['SiteID'] = 'PAL_GMOS'
                
    return df

#%% Read GMOS data


stations_all = ['NIK','BAR','CAL', 'CMA', 'CST', 'EVK', 'KOD', 'KREGND',
                'LIS', 'LSM', 'PAL_GMOS', 'SHL','SIS', 
                'CPO','LON','MAL','MBA','MIN','MWA','SLU','GVB', 'MCH']

dn = '../../obs_datasets/TGM/GMOS/' # directory for GMOS files, change to your path
do = 'all_data/' # directory for outputted files

# run loop over sites to load and process data
for station in stations_all:
    print("Loading site: " + station)
    # get daily data from site
    df = get_data_GMOS(station, dn)
    # output csv
    fo = do + station + '_all.csv'
    df.to_csv(fo)
    df.to_csv(fo, index=False)
    # add plot
    f,  axes = plt.subplots(1,1, figsize=[18,10],
                        gridspec_kw=dict(hspace=0.35, wspace=0.35))
    axes.plot(pd.to_datetime(df.timeMid), df['GEM'], '.', ms=1)
    axes.set_title(station)
    axes.set_ylabel('GEM (ng m$^{-3}$)')
    # set limits, for better visualization
    pct_995 = np.percentile( df['GEM'],99.5)
    pct_005 = np.percentile( df['GEM'],00.5)
    axes.set_ylim(top = pct_995, bottom = pct_005)
    f.savefig('Figures/'+station+'_all.pdf',bbox_inches = 'tight')

