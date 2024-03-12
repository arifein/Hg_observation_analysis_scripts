#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""
Created on Wed Nov  9 16:04:41 2022
Load Hg0 observation data from CAPMoN dataset
@author: arifeinberg
"""

#%% Import packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from dateutil.parser import parse
import glob
#%% functions
def get_filenames_CAPMoN(dn, site):
    """Get the data filename(s) for the site
    
    Parameters
    ----------
    dn : string
         Path for Canadian mercury files
    site : string
         Site code
    """
    
    if site=='ALT':
        fn = [dn + 'AtmosphericGases-TGM-CAMNET-NU_Alert-*.csv', # before 2009
              dn + 'AtmosphericGases-TGM-ECCC_AQRD-NU_Alert-*.csv'] # after 2010
    elif site=='BRL':
        fn = [dn + 'AtmosphericGases-TGM-CAMNET-SK_BrattsLake-*.csv', # before 2008
              dn + 'AtmosphericGases-TGM-CAPMoN-SK_BrattsLake-*.csv', # 2009-2010
              dn + 'AtmosphericGases-TGM-CAPMoN-AllSites-*.csv'] # 2008, after 2011       
    elif site=='BNT':
        fn = [dn + 'AtmosphericGases-TGM-CAMNET-ON_BurntIsland-*.csv']
    elif site=='DEL':
        fn = [dn + 'AtmosphericGases-TGM-CAMNET-BC_Delta-*.csv']   
    elif site=='EGB':
        fn = [dn + 'AtmosphericGases-TGM-CAMNET-ON_Egbert-*.csv', 
              dn + 'AtmosphericGases-TGM-CAPMoN-AllSites-*.csv',
              dn + 'AtmosphericGases-TGM-CAPMoN-ON_Egbert-*.csv']
    elif site=='EST':
        fn = [dn + 'AtmosphericGases-TGM-CAMNET-AB_Esther-*.csv']   
    elif site=='FLN':
        fn = [dn + 'AtmosphericGases-TGM-ECCC_PNR-MB_FlinFlon-*.csv']
    elif site=='STA':
        fn = [dn + 'AtmosphericGases-TGM-CAMNET-NB_HuntsmanScienceCenter-*.csv']
    elif site=='KEJ':
        fn = [dn + 'AtmosphericGases-TGM-CAMNET-NS_Kejimkujik-*.csv', 
              dn + 'AtmosphericGases-TGM-CAPMoN-AllSites-*.csv',
              dn + 'AtmosphericGases-TGM-CAPMoN-NS_Kejimkujik-*.csv']  
    elif site=='LFL':
        fn = [dn + 'AtmosphericGases-TGM-ECCC_AQRD-YT_LittleFoxLake-*.csv']
    elif site=='WBT':
        fn = [dn + 'AtmosphericGases-TGM-CAMNET-PQ_Mingan-*.csv']
    elif site=='FTM':
        fn = [dn + 'AtmosphericGases-TGM-ECCC_PNR-AB_FtMcMurray-*.csv']
    elif site=='PPT':
        fn = [dn + 'AtmosphericGases-TGM-CAMNET-ON_PointPetre-*.csv']
    elif site=='SAT':
        fn = [dn + 'AtmosphericGases-TGM-CAPMoN-BC_Saturna-*.csv', 
              dn + 'AtmosphericGases-TGM-CAPMoN-AllSites-*.csv'] 
    elif site=='PEI':
        fn = [dn + 'AtmosphericGases-TGM-CAMNET-PE_Southampton-*.csv'] 
    elif site=='WBZ':
        fn = [dn + 'AtmosphericGases-TGM-CAMNET-PQ_StAnicet-*.csv'] 
    elif site=='YGW':
        fn = [dn + 'AtmosphericGases-TGM-CAMNET-PQ_Mingan-*.csv']
    else:
        fn = ['']
    return fn

def get_sitecodes(site):
    """Get the options for sitecode(s) for the site
    
    Parameters
    ----------
    site : string
         Site code
    """
    
    if site=='ALT':
        sitecodes = ['CAMNCANU1ALT', 'CAMNCANUALT']
    elif site=='BRL':
        sitecodes = ['CAMNCASK1BRL','CAPMCASKBRL','CAPMCASK1BRA']
    elif site=='BNT':
        sitecodes = ['CAMNCAON1BNT']
    elif site=='DEL':
        sitecodes = ['CAMNCABC1DEL']
    elif site=='EGB':
        sitecodes = ['CAMNCAON1EGB','CAPMCAON1EGB','CAPMCAONEGB','CAPMCAON2EGB']
    elif site=='EST':
        sitecodes = ['CAMNCAAB1EST']   
    elif site=='FLN':
        sitecodes = ['FLIN_FLON']
    elif site=='PPT':
        sitecodes = ['CAMNCAON1PPT']
    elif site=='STA':
        sitecodes = ['CAMNCANB1STA']
    elif site=='KEJ':
        sitecodes = ['CAMNCANS1KEJ','CAPMCANS1KEJ','CAPMCANSKEJ','CAPMCANS1KEB']
    elif site=='LFL':
        sitecodes = ['NCPCAYT1LFL']
    elif site=='WBT':
        sitecodes = ['CAMNCAPQ1WBT']
    elif site=='FTM':
        sitecodes = ['FT_MCMURRAY']        
    elif site=='SAT':
        sitecodes = ['CAPMCABC1SAT','CAPMCABCSAT']        
    elif site=='PEI':
        sitecodes = ['CAMNCAPE1PEI']        
    elif site=='WBZ':
        sitecodes = ['CAMNCAPQ1WBZ']        
    elif site=='YGW':
        sitecodes = ['CAMNCAPQ1YGW']        
    else:
        sitecodes = ['']
    return sitecodes

def find_header_line_CAPMoN(fn):
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
                #print(header_num)
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
                #print(column_num)
                break
    
    if column_num==-99: #didn't find a header number
        print("Error with filename: " + fn)
    return column_num

def fix_column_names_CAPMoN(colnames):
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
                 'HG_GASEOUS',
                 'Site ID: NAtChem',
                 'Site ID: standard',
                 'Time start: local time',
                 'Time zone: local',
                 'Timezone',
                 'Hg_Gaseous_ngm3_Flag',
                 'HG_GASEOUS_Flag',
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
                 'Hg_Gaseous_ngm3',                 
                 'SiteID',
                 'SiteID',
                 'TimeStartLocalTime',
                 'TimeZone',
                 'TimeZone',                 
                 'MercuryFlag1',
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

def load_data_CAPMoN(site, dn,  fn_a):
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
            header_row = find_header_line_CAPMoN(f) # find the row number to start data
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
            colnames_f = fix_column_names_CAPMoN(colnames)
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

def get_data_CAPMoN(site, dn):
    """Get the daily data for the site
    
    Parameters
    ----------
    site : string
         Site code
    dn : string
         Path for Canadian mercury files             
    """
    
    # get the list of filename formats for the site
    fn_a = get_filenames_CAPMoN(dn, site)
    
    # load data for all years into dataframe
    df = load_data_CAPMoN(site, dn, fn_a)
    
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
    
    df['timeStart'] = time_start
    df['timeEnd'] = time_start
    
    # sort data by correct time
    df = df.sort_values(by='timeStart')
    
    # Check whether have duplicated dates within dataset, remove these
    df = df.drop_duplicates(subset=['timeStart','SiteID'])
    
    df['SiteID'] = site # rename siteID
    df = df[['SiteID','timeStart','timeEnd','Hg_Gaseous_ngm3']]
    df = df.rename(columns={"Hg_Gaseous_ngm3": 'GEM'})
        
    return df

#%% Calling functions
# Names of sites in the Canadian network 
site_names = ['Alert', "Bratt's Lake",'Egbert',
              'Flin Flon','Kejimkujik','Little Fox Lake',
              'Fort McMurray','Saturna']
# Codes for the sites (these aren't always consistent throughout data years)
site_codes = ['ALT', 'BRL','EGB','FLN','KEJ','LFL',
             'FTM','SAT']

dn = '../../obs_datasets/CAPMON/' # directory for Candian files, change to your path
do = 'all_data/' # directory for outputted files

#%% Function for converting to fractional years
def year_fraction(date):
    start = datetime.date(date.year, 1, 1).toordinal()
    year_length = datetime.date(date.year+1, 1, 1).toordinal() - start
    return date.year + float(date.toordinal() - start) / year_length
# create ufunc from weird division1
u_year_fraction = np.vectorize(year_fraction)

for i in range(len(site_codes)):
    print("Loading site: " + site_names[i])
    # get hourly and daily data from sites
    df = get_data_CAPMoN(site_codes[i], dn)
    # output csv of all data 
    fo = do + site_codes[i] + '_all.csv'
    df.to_csv(fo, index=False)
    # add plot
    f,  axes = plt.subplots(1,1, figsize=[18,10],
                        gridspec_kw=dict(hspace=0.35, wspace=0.35))
    # change to string list
    #time_str = df.timeStart.strftime('%Y/%m/%d %H:%s').values

    # get date from timeseries with datetime function
    #ts_date = np.array([parse(x) for x in time_str])
    # convert to fractional year formate
    # time = u_year_fraction(ts_date)
    axes.plot(df.timeStart, df['GEM'], '.', ms=1)
    axes.set_title(site_codes[i])
    axes.set_ylabel('GEM (ng m$^{-3}$)')
    # set limits, for better visualization
    pct_995 = np.percentile( df['GEM'],99.5)
    pct_005 = np.percentile( df['GEM'],00.5)
    axes.set_ylim(top = pct_995, bottom = pct_005)
    f.savefig('Figures/'+site_codes[i]+'_all.pdf',bbox_inches = 'tight')

