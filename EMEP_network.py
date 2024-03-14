#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""
Created on Mon Jun  9 16:04:41 2023
Load Hg0 observation data from EMEP dataset
@author: arifeinberg
"""

#%% Import packages
import numpy as np
import pandas as pd
import glob
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

#%% functions
def get_filenames_EMEP(dn, site):
    """Get the data filename(s) for the site
    
    Parameters
    ----------
    dn : string
         Path for EMEP mercury files
    site : string
         Site code
    """
    if site=='AUC':
        fn = [dn + 'biweekly_data/GB0048R.200*.nas',
              dn + 'biweekly_data/GB0048R.2011*.nas',
              dn + 'hourly_data/GB0048R.*.nas'] # hourly data after 2011
    elif site=='LST':
        fn = [dn + 'monthly_data/NO0099R.*.nas', #1992-1994, 1999
              dn + 'daily_data/NO0099R.*.nas']
    elif site=='BIR':
        fn = [dn + 'daily_data/NO0001R.*.nas', # 2004, 2007-2009
              dn + 'weekly_data/NO0001R.*.nas', # 2005
              dn + 'hourly_data/NO0001R.*.nas', # 2006, 2010
              dn + 'hourly_data/NO0002R.*.nas'] # 2011-2022
    elif site=='ZEP':
        fn = [dn + 'daily_data/NO0042G.*.nas', # until 1999
              dn + 'hourly_data/NO0042G.*.nas'] # after 2000
    elif site=='DIA':
        fn = [dn + 'daily_data/PL0005R.*.nas']
    elif site=='WAL':
        fn = [dn + 'daily_data/DE0002R*.nas']
    elif site=='SCA':
        fn = [dn + 'daily_data/DE0003R*.nas']
    elif site=='SCK':
        fn = [dn + 'daily_data/DE0008R.*.nas']
    elif site=='ZIN':
        fn = [dn + 'daily_data/DE0009R.*.nas']
    elif site=='NBO':
        fn = [dn + 'daily_data/ES0008R.*.nas', #2005-2006
              dn + 'hourly_data/ES0008R.*.nas'] #2010-2021
    elif site=='ISK':
        fn = [dn + 'daily_data/SI0008R.*.nas']
    elif site=='STN':
        fn = [dn + 'hourly_data/DK0010G.*.nas']
    elif site=='LAH':
        fn = [dn + 'hourly_data/EE0009R.*.nas']  
    elif site=='CHI':
        fn = [dn + 'hourly_data/GB1055R.*.nas']
    elif site=='TRO1':
        fn = [dn + 'hourly_data/NO0058G.*.nas']
    elif site=='TRO2':
        fn = [dn + 'hourly_data/NO0059G.*.nas']
    elif site=='AND':
        fn = [dn + 'hourly_data/NO0090R.*.nas']
    elif site=='PAL_IVL':
        fn = [dn + 'daily_data/FI0036R.*gold_trap*.nas', # 1996-1997
              dn + 'daily_data/FI0036R.*amalg_tube*.nas'] # 1998-2020
    elif site=='BRE':
        fn = [dn + 'daily_data/SE0005R.*.nas']
    elif site=='RAO':
        fn = [dn + 'daily_data/SE0014R.*.nas']
    elif site=='VAV':
        fn = [dn + 'daily_data/SE0011R.*.nas']  # Vavihill 2009-2015
    elif site=='HAL':
        fn = [dn + 'daily_data/SE0020R.*.nas']  # Hallahus 2016-2021
    else:
        fn = ['']
    return fn


def find_header_line_EMEP(fn):
    """Find line number of header in a data file
    
    Parameters
    ----------
    fn : string
         Filename
    """
    header_num = -99 # placeholder
    with open(fn, 'r', encoding='ISO-8859-1') as searchfile:         
    
        #Search file for strings, trim lines and save as variables
        for ll, line in enumerate(searchfile):
                    
            if ("starttime" in line): # where have column labels
                header_num = ll
                # print(header_num)
                break
    
    if header_num==-99: #didn't find a header number
        print("Error with filename: " + fn)
    return header_num

def find_startdate(fn):
    """return startdate of EMEP EBAS files
    
    Parameters
    ----------
    fn : string
         Filename
    """
    line_num = -99 # placeholder
    with open(fn, 'r', encoding='ISO-8859-1') as searchfile:         
    
        #Search file for strings, trim lines and save as variables
        for ll, line in enumerate(searchfile):
                    
            if ("Startdate" in line): # where have column labels
                line_num = ll
                break
    
    if line_num==-99: #didn't find a header number
        print("Error with filename: " + fn)
    
    # Extract date from string
    date_str = line[-15:-1]
    # format is YYYYMMDDhhmmss
    start_date = pd.to_datetime(date_str, format='%Y%m%d%H%M%S', utc = True) # assume UTC
    return start_date

def fix_column_names_EMEP(colnames):
    """Fix column names so that consistent between different years/sites of the dataset
    
    Parameters
    ----------
    colnames : list
         list of column names
    """
    
    # list of names to adjust
    old_names = ['GEM',
                 'Hg',
                 'flag_GEM',
                 'flag',
                 'flag_Hg']
    
   # list of new names to set
    new_names = ['TGM', 
                 'TGM',
                 'flag_TGM',
                 'flag_TGM',
                 'flag_TGM']
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

def load_data_EMEP(site, dn, fn_a ):
    """Load the data over all years for the site
    
    Parameters
    ----------
    site : string
         Site code
    dn : string
         Path for EMEP mercury files                      
    fn_a : list
         List of file names
    """

    # create empty data frame to store all sites and years
    frame = []
    colnames_a = []
    
    # Loop over all data files, concatenate
    for fn in fn_a: # loop over filenames
        for f in glob.glob(fn): # loop over the different file years
            print(f)
            header_row = find_header_line_EMEP(f) # find the row number to start data
            # find the column names from the csv file
            colnames = pd.read_csv(f, skiprows=header_row, nrows=1, header=None, sep=' ',
                     encoding='ISO-8859-1').values.flatten().tolist()
            # can't have multiple columns with same name
            if colnames.count('GEM') > 1: # have duplicate GEM entries
                inds_dup = [i for i, c in enumerate(colnames) if c == 'GEM'] # indices of duplicates
                colnames[inds_dup[1]] = 'GEM_std' # list as stdev
            
            # standardize column names between different datasets
            colnames_f = fix_column_names_EMEP(colnames)

            # load dataset from file
            df = pd.read_csv(f, 
                    skiprows=header_row, header=0, sep='\s+',
                    names = colnames_f,  encoding='ISO-8859-1')    
            
            # find the start date of the file
            start_date = find_startdate(f)
            # Calculate actual measurement start in date format (convert from days since)
            date_start = pd.to_timedelta(df.starttime, unit = "D") + start_date
            # Calculate actual measurement end in date format (convert from days since)
            date_end = pd.to_timedelta(df.endtime, unit = "D") + start_date
            # find midpoint time and include this in dataframe
            time_mid = ((date_end - date_start)/2 + date_start).values
            df['time_mid'] = time_mid
            # for Helene, add start and end date
            df['timeStart'] = date_start.dt.tz_localize(None)
            df['timeEnd'] = date_end.dt.tz_localize(None)

            # select valid values
            bool_valid = df['flag_TGM']==0.  # Valid value 
            
            # Check as well that concentrations are not invalid
            bool_pos = (df['TGM'] < 99.) & (df['TGM'] > 0.)
            
            # Combine these two requirements
            bool_overall = bool_valid & bool_pos # these are valid data
            # Filter data for validity
            df = df[bool_overall]

            # if all measurements invalid, skip to next iteration
            if df.empty:
                print('No valid measurements in this file')
                continue
            # save out column names, in case have to debug this
            colnames_a.append(df.columns)
            
            # calculate the time resolution of the file
            d_diff = round(np.median(df.endtime - df.starttime))
            print(d_diff)
            # set index to the time_mid, needed for resampling consistently
            df = df.set_index('time_mid')
            
            # figure out time resolution of file
            if d_diff == 1: # daily data
                f_t_res = 'D'
                # output resolutions that work with daily data
                suitable_res = ['D', 'W', '2W','M']
            elif d_diff == 0: # hourly or multi-hourly data
                f_t_res = 'H'
                # output resolutions that work with daily data
                suitable_res = ['H','D', 'W', '2W','M']
            elif (d_diff > 4) and (d_diff < 10) : # weekly data
                f_t_res = 'W'
                # output resolutions that work with daily data
                suitable_res = ['W', '2W','M']
            elif (d_diff > 10) and (d_diff < 18) : # biweekly data
                f_t_res = '2W'
                # output resolutions that work with daily data
                suitable_res = ['2W','M']
            elif (d_diff > 20) and (d_diff < 40) : # monthly data
                f_t_res = 'M'
                # output resolutions that work with daily data
                suitable_res = ['M']
            else:
                raise Exception('Correct time resolution not found')
            
            # append to frame, so that can later concatenate
            df_temp = frame.append(df)
               
    # print all column names
    colnames_list = [item for sublist in colnames_a for item in sublist if item==item] # make sure not nan
    colnames_u = list(set(colnames_list))
    print(colnames_u)
        
    # concatenate all data frames        
    df_t = pd.concat(frame)
    
    # adjust names of columns
    return df_t

def get_data_EMEP(site, dn):
    """Get the daily data for the site
    
    Parameters
    ----------
    site : string
         Site code
    dn : string
         Path for EMEP mercury files   
    """
    
    # get the list of filename formats for the site
    fn_a = get_filenames_EMEP(dn, site)

    # load data for all years into dataframe
    df = load_data_EMEP(site, dn, fn_a)

    # sort data by correct time
    df = df.sort_index().reset_index()
        
    df = df.rename(columns={"TGM": 'GEM'})
    df['SiteID'] = site
    df = df[['SiteID','timeStart','timeEnd','GEM']]

    # Check whether have duplicated dates within dataset, remove these
    #df = df.drop_duplicates(subset=['time_mid'])
            
    return df


#%% Calling functions

# Codes for the sites (these aren't the same as EMEP codes)
site_codes = ['AUC', 'LST','BIR','ZEP', 'DIA', 'WAL', 'SCA', 'SCK', 'ZIN', 'NBO',
              'ISK','STN','LAH', 'CHI','TRO1', 'TRO2','AND','PAL_IVL','BRE', 'RAO','HAL','VAV']

dn = '../../obs_datasets/EMEP/' # directory for EMEP files, change to your path
do = 'all_data/' # directory for outputted daily mean files

# run loop over sites to load and process data
for i in range(len(site_codes)):
    print("Loading site: " + site_codes[i])
    # get data from sites at desired time resolution
    df = get_data_EMEP(site_codes[i], dn)
    # output csv of daily averages
    fo = do + site_codes[i] + '_all.csv'
    df.to_csv(fo, index=False)
    # add plot
    f,  axes = plt.subplots(1,1, figsize=[18,10],
                        gridspec_kw=dict(hspace=0.35, wspace=0.35))
    axes.plot(pd.to_datetime(df.timeStart), df['GEM'], '.', ms=1)
    axes.set_title(site_codes[i])
    axes.set_ylabel('GEM (ng m$^{-3}$)')
    # set limits, for better visualization
    pct_995 = np.percentile( df['GEM'],99.5)
    pct_005 = np.percentile( df['GEM'],00.5)
    axes.set_ylim(top = pct_995, bottom = pct_005)
    f.savefig('Figures/'+site_codes[i]+'_all.pdf',bbox_inches = 'tight')

