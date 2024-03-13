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
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

#%% Functions used for analysis
def get_sitename(site):
    """Get the name for the site from the codes
    
    Parameters
    ----------
    site : string
         Site code
    """
    
    if site=='PAL_FMI':
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
    
    df = pd.DataFrame({'timeStart': date_var, 'GEM': Hg_var})
    df['SiteID'] = site

    # Add offset to calculate start and end time to be consistent with other networks
    df['timeEnd'] = df['timeStart'] +  pd.DateOffset(hours=1)
    
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
    df = df.sort_values(by='timeStart')

    # reorder columns
    df = df[['SiteID','timeStart','timeEnd','GEM']] 
    return df

#%% Read FIN data
stations_all = ['PAL_FMI', 'HYY', 'VIR']
dn = '../../obs_datasets/TGM/misc/' # directory for FIN files, change to your path
do = 'all_data/' # directory for outputted files

# run loop over sites to load and process data
for station in stations_all:
    print("Loading site: " + station)
    # get daily data from site
    df = get_data_FIN(station, dn)
    # output csv of all datav
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
    
