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
    #dn = '../../obs_datasets/CAPMON/' # directory name - CHANGE TO YOUR RELATIVE PATH
    dn = '/Users/arifeinberg/Documents/Postdoc_MIT/datasets/CAPMON_Conc/' # directory name - CHANGE TO YOUR RELATIVE PATH
    
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

def find_column_line(fn):
    """Find line number of column names in a data file
    
    Parameters
    ----------
    fn : string
         Filename
    """
    column_num = -99 # placeholder
    with open(fn, 'r', encoding='ISO-8859-1') as searchfile:
    
        # Clear variable names
        right_table = False # change when have found right table
    
        #Search file for strings, trim lines and save as variables
        for ll, line in enumerate(searchfile):
    
            if "Surface--fixed" in line:
                right_table = True # found correct table
                
            # for better readability, list potential column line names:
            bool_col1 = "*TABLE COLUMN NAME--SHORT FORM" in line
            bool_col2 = '*TABLE COLUMN NAME,"Site ID' in line
            bool_col3 = '*TABLE COLUMN NAME,Site ID' in line
            bool_col = bool_col1 or bool_col2 or bool_col3
            
            # see if find overall corect line:
            if right_table and bool_col:
                column_num = ll
                print(column_num)
                break
    
    if column_num==-99: #didn't find a header number
        print("Error with filename: " + fn)
    return column_num

def fix_column_names(colnames):
    """Fix column names so that consistent between different years/sites of the dataset
    
    Parameters
    ----------
    colnames : list
         list of column names
    """
    
    # list of names to adjust
    old_names = ['Time end: local time',
                 'Instrument co-location ID ',
                 'Date start: local time',
                 'Date end: local time',
                 'Mercury',
                 'Site ID: NAtChem',
                 'Site ID: standard',
                 'Time start: local time',
                 'Time zone: local',
                 'Hg_Gaseous_ngm3_Flag',
                 'Time end: UTC',
                 'Time start: UTC',
                 'Date end: UTC',
                 'Date start: UTC']
    
   # list of new names to set
    new_names = ['TimeEndLocalTime',
                 'Instrument co-location ID',
                 'DateStartLocalTime',
                 'DateEndLocalTime',
                 'Hg_Gaseous_ngm3',
                 'SiteID',
                 'SiteID',
                 'TimeStartLocalTime',
                 'TimeZone',
                 'MercuryFlag1',
                 'TimeEndUTC',
                 'TimeStartUTC',
                 'DateEndUTC',
                 'DateStartUTC']
    colnames_new = colnames
    # loop through, make changes
    for i in range(len(old_names)):
        # find index of name to change
        try: #only if within the list
            ind = colnames.index(old_names[i])
            # replace name with new name
            colnames_new[ind] = new_names[i]
        except:
            ind = -1
            
    return colnames_new

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
    # colnames = ['SiteID', 'Instrument_ID',	'Date_start_LT', 'Time_start_LT',
    #     'Date_end_LT', 'Time_end_LT', 'Time_zone','Date_start_UTC', 
    #     'Time_start_UTC','Date_end_UTC', 'Time_end_UTC', 'TGM','Flag']

    # create empty data frame to store all sites and years
    frame = []
    colnames_a = []

    # Loop over all data files, concatenate
    for fn in fn_a: # loop over filenames
        for f in glob.glob(fn): # loop over the different file years
            print(f)
            header_row = find_header_line(f) # find the row number to start data
            column_row = find_column_line(f) # find the row number of column names
            # find the column names from the csv file
            colnames = pd.read_csv(f, skiprows=column_row, nrows=1, header=None, 
                     encoding='ISO-8859-1').values.flatten().tolist()
            # can't have multiple columns with same name
            if colnames.count('Mercury') > 1: # have duplicate Mercury entries
                inds_dup = [i for i, c in enumerate(colnames) if c == 'Mercury'] # indices of duplicates
                for i in range(len(inds_dup)-1): # for number of duplicates
                    i1 = i +1
                    colnames[inds_dup[i1]] = 'MercuryFlag' + str(i1) # list as flag
            # standardize column names between different datasets
            colnames_f = fix_column_names(colnames)
            # load dataset for year
            df_d_f = pd.read_csv(f, 
                    skiprows=header_row, header=0,
                    names = colnames_f,  encoding='ISO-8859-1')
            # drop rows with less than 2 non NaN values, and all NaN columns
            df_d_f_na = df_d_f.dropna(thresh=2).dropna(axis=1, how='all')
            # save out column names, in case have to debug this
            colnames_a.append(df_d_f_na.columns)
            # append to frame, so that can later concatenate
            df_d_temp = frame.append(df_d_f_na)
            
    # concatenate all data frames        
    df = pd.concat(frame)
    return df

def get_data_d(site):
    """Get the daily data for the site
    
    Parameters
    ----------
    site : string
         Site code
    """
    
    # get the list of filename formats for the site
    fn_a = get_filenames(site)
    # load data for all years into dataframe
    df = load_data(site, fn_a)
    # Find where data is valid
    bool_valid1 = df['MercuryFlag1']=='V0' # Valid value 
    bool_valid2 = df['MercuryFlag1']=='V1' # Valid value but below detection limit. 
    bool_valid3 = df['MercuryFlag1']=='V4' # Flag not in use 
    # Boolean variable for data validity
    bool_valid = bool_valid1 | bool_valid2 | bool_valid3 
    # Check as well that concentrations are non-negative
    bool_pos = df['Hg_Gaseous_ngm3'] >= 0
    # Combine these two requirements
    bool_overall = bool_valid & bool_pos # these are valid data
    # Filter data for validity
    df_v = df[bool_overall]
    # continue with getting the location, date etc...
    # # sort data by year
    # df = df.sort_values(by='DateStartLocalTime')
    return df_v

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
# # debug column names
# colnames_list = [item for sublist in df_ALT for item in sublist if item==item] # make sure not nan
# colnames_u = list(set(colnames_list))
# print(colnames_u)
#%% debug getting these data files - inconsistent columns for different years :S
dn = '/Users/arifeinberg/Documents/Postdoc_MIT/datasets/CAPMON_Conc/' # directory name - CHANGE TO YOUR RELATIVE PATH

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
#%% testing reading
colnames_f = pd.read_csv(dn + 'AtmosphericGases-TGM-ECCC_AQRD-NU_Alert-2016.csv', 
                    skiprows=68, header=None, nrows=1, encoding='ISO-8859-1').values.flatten().tolist()
print(colnames_f)
#%%
temp = pd.read_csv(dn + 'AtmosphericGases-TGM-ECCC_AQRD-NU_Alert-2018.csv', 
                    skiprows=89, header=0, names = colnames_f, encoding='ISO-8859-1')
# drop rows with less than 2 non NaN values, and all NaN columns
temp_nona = temp.dropna(thresh=2).dropna(axis=1, how='all')