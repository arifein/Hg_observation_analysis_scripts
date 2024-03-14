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
    df = pd.read_excel(fn)            
        
    # Create datetime variables for start and end of measurements
    time_start = df['Sample date/Time start']
    time_end = df['Sample date/Time end']

    df = df.rename(columns={"Sample date/Time start": "timeStart", 
                            "Sample date/Time end": "timeEnd"})
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
            
    df['SiteID'] = 'ELA'
    # remove NAN 
    df_d = df.dropna()
    df_d = df_d[['SiteID','timeStart','timeEnd','GEM']]
                    
    return df_d

#%% Read misc data
stations_all = ['ELA']
dn = '../../obs_datasets/GEM/' # directory for misc files, change to your path
do = 'all_data/' # directory for outputted files

# run loop over sites to load and process data
for station in stations_all:
    print("Loading site: " + station)
    # get daily data from site
    df = get_data_misc(station, dn)
    # output csv of daily averages
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
