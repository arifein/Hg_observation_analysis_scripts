#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""
Created on Wed Nov  9 16:04:41 2022
Load Hg0 observation data from CAPMoN dataset
@author: arifeinberg
"""

#%% Import packages
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
import datetime
import glob
#%% functions
def get_filenames(site):
    """Get the data filename(s) for the site
    
    Parameters
    ----------
    site : string
         Site code
    """
    dn = '../../obs_datasets/CAPMON/' # directory name - CHANGE TO YOUR RELATIVE PATH
    if site=='ALT':
        fn = [dn + 'AtmosphericGases-TGM-CAMNET-NU_Alert-*.csv', # before 2009
              dn + 'AtmosphericGases-TGM-ECCC_AQRD-NU_Alert-*.csv'] # after 2010
    else:
        fn = ['']
    return fn

def find_header_line(fn):
    """Find line number of header in a data file
    
    Parameters
    ----------
    fn : string
         Filename
    """
    header_num = -99 # placeholder
    with open(fn, 'r', encoding='ISO-8859-1') as searchfile:
    
        # Clear variable names
        right_table = False # change when have found right table
         
    
        #Search file for strings, trim lines and save as variables
        for ll, line in enumerate(searchfile):
    
            if "Surface--fixed" in line:
                right_table = True # found correct table
                
            if (right_table == True) and (("*TABLE BEGINS" in line) or ("*TABLE DATA BEGINS" in line)):
                header_num = ll
                print(header_num)
                break
    
    if header_num==-99: #didn't find a header number
        print("Error with filename: " + fn)
    return header_num


def load_data(site, fn_a):
    """Load the data over all years for the site
    
    Parameters
    ----------
    site : string
         Site code
    fn_a : list
         List of file names
         
    """
    # Column names in the CAPMON files
    colnames = ['SiteID', 'Instrument_ID',	'Date_start_LT', 'Time_start_LT',
        'Date_end_LT', 'Time_end_LT', 'Time_zone','Date_start_UTC', 
        'Time_start_UTC','Date_end_UTC', 'Time_end_UTC', 'TGM','Flag']

    # create empty data frame to store all sites and years
    frame = []
    # Loop over all data files, concatenate
    for fn in fn_a: # loop over filenames
        for f in glob.glob(fn): # loop over the different file years
            print(f)
            header_row = find_header_line(f) # find the row number to start
            df_d_temp = frame.append(pd.read_csv(f, 
                    skiprows=header_row, header=0,
                    names = colnames,  encoding='ISO-8859-1')) 
                    #usecols=range(0,13)))
    df = pd.concat(frame)

    return df

def get_data_d(site):
    """Get the daily data for the site
    
    Parameters
    ----------
    site : string
         Site code
    """
    
    # get the list of filenames for the site
    fn_a = get_filenames(site)
    df = load_data(site, fn_a)
    return df

#%% Calling functions
# Names of sites in the Canadian network 
site_names = ['Alert', "Bratt's Lake",'Burnt Island','Delta','Egbert','Esther',
              'Flin Flon','Huntsman Center','Kejimkujik','Little Fox Lake',
              'Mingan', 'Fort McMurray','Point Petre','Saturna','Southampton',
              'St. Anicet','Kuujjuarapik']
# Codes for the sites (these aren't always consistent throughout data years)
site_codes = ['ALT', 'BRL','BNT','DEL','EGB','EST','FLN','STA','KEJ','LFL',
            'WBT', 'FTM','PPT','SAT','PEI','WBZ','YGW']


df_ALT = get_data_d('ALT')
#%% debug getting these data files - inconsistent columns for different years :S
fn = '../../obs_datasets/CAPMON/AtmosphericGases-TGM-ECCC_AQRD-NU_Alert-2010.csv' # 119
fn = '../../obs_datasets/CAPMON/AtmosphericGases-TGM-CAMNET-NU_Alert-2009.csv' # 89
fn = '../../obs_datasets/CAPMON/AtmosphericGases-TGM-ECCC_AQRD-NU_Alert-2018.csv' # 84
fn = '../../obs_datasets/CAPMON/AtmosphericGases-TGM-ECCC_AQRD-NU_Alert-2021.csv' # 83

colnames = ['SiteID', 'Instrument_ID',	'Date_start_LT', 'Time_start_LT',
    'Date_end_LT', 'Time_end_LT', 'Time_zone','Date_start_UTC', 
    'Time_start_UTC','Date_end_UTC', 'Time_end_UTC', 'TGM','Flag']


df_temp2 = pd.read_csv(fn, 
                    skiprows=89, header=0, delimiter = ',',
                    names = colnames,  index_col=False, encoding='ISO-8859-1', 
                    usecols=range(1,14))
    #%%
temp = pd.read_csv('../../obs_datasets/CAPMON/AtmosphericGases-TGM-ECCC_AQRD-NU_Alert-2018.csv', 
                    skiprows=87, header=0, names=colnames, encoding='ISO-8859-1')