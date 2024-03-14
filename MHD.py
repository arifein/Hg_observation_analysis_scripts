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
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

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
    df_d_f['timeStart'] = pd.to_datetime(df_d_f.iloc[:,0], format='%Y-%m-%d %H:%M')
    
    df_d_f['timeEnd'] = df_d_f['timeStart'] + pd.DateOffset(hours=1)
    df_d_f['SiteID'] = 'MHD'

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
            
    df = df.rename(columns={"MH":'GEM'})

    df_d = df.dropna()
    df_d = df_d[['SiteID','timeStart','timeEnd','GEM']]                
    return df_d

#%% Read misc data
stations_all = ['MHD']
dn = '../../obs_datasets/TGM/misc/' # directory for misc files, change to your path
do = 'all_data/' # directory for outputted files

# run loop over sites to load and process data
for station in stations_all:
    print("Loading site: " + station)
    # get data from site
    df = get_data_misc(station, dn)
    # output csv of data
    fo = do + station + '_all.csv'
    df.to_csv(fo, index=False)
    # add plot
    f,  axes = plt.subplots(1,1, figsize=[18,10],
                        gridspec_kw=dict(hspace=0.35, wspace=0.35))
    axes.plot(pd.to_datetime(df.timeStart), df['GEM'], '.', ms=1)
    axes.set_title(station)
    axes.set_ylabel('GEM (ng m$^{-3}$)')
    # set limits, for better visualization
    pct_995 = np.percentile( df['GEM'],99.5)
    pct_005 = np.percentile( df['GEM'],00.5)
    axes.set_ylim(top = pct_995, bottom = pct_005)
    f.savefig('Figures/'+station+'_all.pdf',bbox_inches = 'tight')

