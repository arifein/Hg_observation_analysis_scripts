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
import matplotlib.pyplot as plt

#%% functions
def get_filenames(dn, site):
    """Get the data filename(s) for the site
    
    Parameters
    ----------
    dn : string
         Path for EMEP mercury files
    site : string
         Site code
    """
    
    if site=='SCH':
        fn = [dn + 'daily_data/DE0008R.*.Hg_mon.mercury_TGM.air.1y.1d.DE03L_UBA_Sm_Mon_0101.DE03L_CVAFS.lev2.nas']
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
    
        #Search file for strings, trim lines and save as variables
        for ll, line in enumerate(searchfile):
                    
            if ("starttime" in line): # where have column labels
                header_num = ll
                #print(header_num)
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

def convert_time_res(df, t_res):
    """Convert DataFrame to be the correct time resolution

    df : DataFrame
         Site data at original time resolution
    t_res : string
         Required time resolution of output DataFrame
    """
    
    # use if statements to get data at correct time resolution
    if t_res =='H': # hourly data
        df_t = df.resample('H').mean().dropna()
    elif t_res =='D': # daily data
        df_t = df.resample('D').mean().dropna()
    elif t_res =='W': # weekly data
        df_t = df.resample('7D').mean().dropna()
        # shift index by 3.5 so centered
        df_t.index = df_t.index + pd.to_timedelta( 3.5, unit = 'D')
    elif t_res =='2W': # biweekly data
        df_t = df.resample('14D').mean().dropna()
        # shift index by 7 so centered
        df_t.index = df_t.index + pd.to_timedelta(7, unit = 'D')
    elif t_res =='M': # monthly data
        df_t = df.resample('MS').mean().dropna()
        # shift index by 15 so centered
        df_t.index = df_t.index + pd.to_timedelta(15, unit = 'D')
      
    return df_t

def load_data(site, dn, fn_a, t_res):
    """Load the data over all years for the site
    
    Parameters
    ----------
    site : string
         Site code
    dn : string
         Path for EMEP mercury files                      
    fn_a : list
         List of file names
    t_res : string
         Required time resolution of output dataframe
    """

    # create empty data frame to store all sites and years
    frame = []
    colnames_a = []
    
    # Loop over all data files, concatenate
    for fn in fn_a: # loop over filenames
        for f in glob.glob(fn): # loop over the different file years
            print(f)
            header_row = find_header_line(f) # find the row number to start data
            # find the column names from the csv file
            colnames = pd.read_csv(f, skiprows=header_row, nrows=1, header=None, sep=' ',
                     encoding='ISO-8859-1').values.flatten().tolist()
            
            # load dataset from file
            df = pd.read_csv(f, 
                    skiprows=header_row, header=0, sep='\s+',
                    names = colnames,  encoding='ISO-8859-1')    
            
            # find the start date of the file
            start_date = find_startdate(f)
            # Calculate actual measurement start in date format (convert from days since)
            date_start = pd.to_timedelta(df.starttime, unit = "D") + start_date
            # Calculate actual measurement end in date format (convert from days since)
            date_end = pd.to_timedelta(df.endtime, unit = "D") + start_date
            # find midpoint time and include this in dataframe
            time_mid = ((date_end - date_start)/2 + date_start).values
            df['time_mid'] = time_mid
            
            # select valid values
            bool_valid = df['flag_TGM']==0. # Valid value 
            
            # Filter data for validity
            df = df[bool_valid]
            
            # save out column names, in case have to debug this
            colnames_a.append(df.columns)
            
            # calculate the time resolution of the file
            d_diff = round(np.mean(df.endtime - df.starttime))
            
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
            # check if time resolution can be suitably converted
            if t_res in suitable_res:
                if t_res == f_t_res: 
                    df_t = df
                else: # need to convert time resolution
                    df_t = convert_time_res(df, t_res)
                    
            else: # don't have suitable time resolution
                raise Exception("Error with short averaging time resolution chosen for file with resolution: " + f_t_res )
            
            # append to frame, so that can later concatenate
            df_d_temp = frame.append(df_t)
               
    # print all column names
    colnames_list = [item for sublist in colnames_a for item in sublist if item==item] # make sure not nan
    colnames_u = list(set(colnames_list))
    print(colnames_u)
        
    # concatenate all data frames        
    df_t = pd.concat(frame)
    return df_t

def get_data_d(site, dn, t_res):
    """Get the daily data for the site
    
    Parameters
    ----------
    site : string
         Site code
    dn : string
         Path for EMEP mercury files   
    t_res: string      
         Time resolution of the data   
    """
    
    # get the list of filename formats for the site
    fn_a = get_filenames(dn, site)
        
    # load data for all years into dataframe
    df = load_data(site, dn, fn_a, t_res)

    # sort data by correct time
    df = df.sort_index()
        
    # Check whether have duplicated dates within dataset, remove these
    #df = df.drop_duplicates(subset=['time_mid'])
            
    return df


#%% Calling functions
dn = '../../obs_datasets/EMEP/' # directory for EMEP files, change to your path
df_d = get_data_d('SCH', dn, 'D')
plt.plot(df_d.index.values, df_d.TGM.values,'o', ms=1)

#%% testing
dn = '../../obs_datasets/EMEP/' # directory for EMEP files, change to your path
fn = 'hourly_data/GB0048R.20120101001000.20190830121302.Hg_mon.mercury_TGM.air.1y.3h.GB03L_Hg01.GB03L_Hg_online_1.lev2.nas'

f = dn + fn
header_row = find_header_line(f)
# find the column names from the csv file
colnames = pd.read_csv(f, skiprows=header_row, nrows=1, header=None, sep=' ',
         encoding='ISO-8859-1').values.flatten().tolist()
# load dataset for year
df = pd.read_csv(f, 
        skiprows=header_row, header=0, sep='\s+',
        names = colnames,  encoding='ISO-8859-1')
# find the start date of the file
start_date = find_startdate(f)
# Calculate actual measurement start in date format (convert from days since)
date_start = pd.to_timedelta(df.starttime, unit = "D") + start_date
# Calculate actual measurement end in date format (convert from days since)
date_end = pd.to_timedelta(df.endtime, unit = "D") + start_date
# find midpoint time and include this in dataframe
time_mid = ((date_end - date_start)/2 + date_start).values
df['time_mid'] = time_mid
# select valid values
bool_valid = df['flag_TGM']==0. # Valid value 
# # Check as well that concentrations are non-negative
# bool_pos = df['Hg_Gaseous_ngm3'] >= 0
# # Combine these two requirements
# bool_overall = bool_valid & bool_pos # these are valid data

# Filter data for validity
df = df[bool_valid]

#%% functions


def load_data(site, dn,  fn_a):
    """Load the data over all years for the site
    
    Parameters
    ----------
    site : string
         Site code
    dn : string
         Path for Canadian mercury files                      
    fn_a : list
         List of file names
         
    """

    # create empty data frame to store all sites and years
    frame = []
    colnames_a = []
    
    # problematic filenames, need to treat special cases
    fn_issue = [dn + 'AtmosphericGases-TGM-CAPMoN-NS_Kejimkujik-2009.csv',
                dn + 'AtmosphericGases-TGM-CAPMoN-NS_Kejimkujik-2010.csv',
                dn + 'AtmosphericGases-TGM-CAPMoN-NS_Kejimkujik-2011.csv',
                dn + 'AtmosphericGases-TGM-CAPMoN-NS_Kejimkujik-2012.csv',
                dn + 'AtmosphericGases-TGM-CAPMoN-NS_Kejimkujik-2013.csv',]
    
    # Loop over all data files, concatenate
    for fn in fn_a: # loop over filenames
        for f in glob.glob(fn): # loop over the different file years
            print(f)
            header_row = find_header_line(f) # find the row number to start data
            column_row = find_column_line(f) # find the row number of column names
            # find the column names from the csv file
            colnames = pd.read_csv(f, skiprows=column_row, nrows=1, header=None, 
                     encoding='ISO-8859-1').values.flatten().tolist()
            # fix csv issues manually with problematic files
            if (f in fn_issue):
                colnames = colnames[:-1] # take off last column, not in data
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
            # Note: DtypeWarnings can be ignored, do not affect performance
            
            # drop rows with less than 2 non NaN values, and all NaN columns
            df_d_f_na = df_d_f.dropna(thresh=2).dropna(axis=1, how='all')
            # save out column names, in case have to debug this
            colnames_a.append(df_d_f_na.columns)
            # append to frame, so that can later concatenate
            df_d_temp = frame.append(df_d_f_na)
    
    # print all column names
    colnames_list = [item for sublist in colnames_a for item in sublist if item==item] # make sure not nan
    colnames_u = list(set(colnames_list))
    # print(colnames_u)
        
    # concatenate all data frames        
    df = pd.concat(frame)
    return df

def get_data_d(site, dn):
    """Get the daily data for the site
    
    Parameters
    ----------
    site : string
         Site code
    dn : string
         Path for Canadian mercury files             
    """
    
    # get the list of filename formats for the site
    fn_a = get_filenames(dn, site)
    
    # load data for all years into dataframe
    df = load_data(site, dn, fn_a)
    
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
    df = df[bool_overall]
    
    # Check whether have multiple sites within dataset
    #print(df['SiteID'].unique())
    
    # Find list of site codes associated with the site
    sitecodes = get_sitecodes(site)
    
    # Select only rows associated with desired site
    df = df[df['SiteID'].isin(sitecodes)]
    
    # Check whether have multiple instruments with site
    #print(df['Instrument co-location ID'].unique())
    
    # Create datetime variables for start and end of measurements
    time_start = pd.to_datetime(df['DateStartLocalTime'] + ' ' + df['TimeStartLocalTime'])
    time_end = pd.to_datetime(df['DateEndLocalTime'] + ' ' + df['TimeEndLocalTime'])
    
    # find midpoint time
    time_mid = ((time_end - time_start)/2 + time_start).values
    df['time_mid'] = time_mid
    
    # sort data by correct time
    df = df.sort_values(by='time_mid')
    
    # Check whether have duplicated dates within dataset, remove these
    df = df.drop_duplicates(subset=['time_mid','SiteID'])
    
    # resample daily averages
    df_d = df.set_index('time_mid').resample('D').mean().dropna()
        
    return df, df_d

#%% Calling functions
# Names of sites in the Canadian network 
site_names = ['Alert', "Bratt's Lake",'Burnt Island','Delta','Egbert','Esther',
              'Flin Flon','Hunstsman Center','Kejimkujik','Little Fox Lake',
              'Mingan', 'Fort McMurray','Point Petre','Saturna','Southampton',
              'St. Anicet','Kuujjuarapik']
# Codes for the sites (these aren't always consistent throughout data years)
site_codes = ['ALT', 'BRL','BNT','DEL','EGB','EST','FLN','STA','KEJ','LFL',
            'WBT', 'FTM','PPT','SAT','PEI','WBZ','YGW']

dn = '../../obs_datasets/CAPMON/' # directory for Candian files, change to your path
do = '../misc_Data/' # directory for outputted daily mean files
for i in range(len(site_codes)):
    print("Loading site: " + site_names[i])
    # get hourly and daily data from sites
    df, df_d = get_data_d(site_codes[i], dn)
    # output csv of daily averages
    fo = do + site_codes[i] + '_d.csv'
    df_d.to_csv(fo)