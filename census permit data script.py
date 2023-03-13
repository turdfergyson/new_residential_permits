# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 13:16:01 2023

@author: TysonWeigel
"""

import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt
import glob

os.chdir('YOUR WORKING DIRECTORY HERE')

path = r'YOUR FILEPATH HERE'

all_files = glob.glob(os.path.join(path,"*.xls"))   

df = pd.DataFrame()

#loop through files in path and append into empty dataframe
#note that the 'date' column is coming from the filename
for f in all_files:
        data = pd.read_excel(f,'State Units', skiprows=8)
        data['date'] = f[116:122]
        data['source'] = 'census'
        df = df.append(data, ignore_index=True)

#drop unnecessary columns
df2 = df.drop(df.iloc[:,2:14],axis=1)

#rename headers
df2 = df2.rename(columns={'Unnamed: 0':'state','Unnamed: 1':'permits'})
df2['date'] = df2['date'].str[-3:]

#clean formatting on state column
df2['state'] = df2['state'].str.strip()

#drop blank rows
df2.dropna(axis=0,subset=['permits'],inplace=True)
df2.reset_index()

#normalize data
#below uses maximum absolute scaling
df2['permits_scaled'] = df2['permits']/df2['permits'].abs().max()

'''
#below uses proper normalization
for permits_normalized in df2.permits_normalized:
    df2['permits_normalized'] = (df2['permits']-df2['permits'].min())/(df2['permits'].max()-df2['permits'].min())
'''

###new dataframes of specific segments of permit metrics###
regional = df2[df2['state'].str.contains("Region")]
divisional = df2[df2['state'].str.contains("Division")]
national = df2[df2['state']=="United States"]

subset = regional.append([divisional])
subset = subset.append([national])

state = df2[~df2.state.isin(subset.state)]

#load dwh/safebuilt data
qbr_data = pd.read_csv('230228qbrsum.csv')

#summarize data
qbr_new_res = qbr_data[qbr_data['service_category_mapped']=='Residential New']
qbr_new_res['state'] = qbr_new_res['bunit_name'].str[:2]
qbr_nr_state = qbr_new_res.groupby(['date_month_start_date','state'])[['permitjob_issued_count']].sum()
qbr_nr_state = qbr_nr_state.reset_index()

#qbr_all = qbr_data.groupby("date_month_start_date"
qbr_nr = qbr_new_res.groupby(['date_month_start_date','bunit_name'])[['permitjob_issued_count']].sum()
qbr_nr = qbr_nr.reset_index()

#add date column
qbr_nr['date_month_start_date'] = pd.to_datetime(qbr_nr.date_month_start_date)
qbr_nr['date'] = qbr_nr['date_month_start_date'].dt.strftime('%Y%m')
qbr_nr['date'] = qbr_nr['date'].str[-3:]

#maximum absolute scaling
qbr_nr['permits_scaled'] = qbr_nr['permitjob_issued_count']/qbr_nr['permitjob_issued_count'].abs().max()

#create new dataframes with qbr data
qbr_nr_all = qbr_nr.groupby('date')['permitjob_issued_count'].sum()
qbr_nr_all = qbr_nr_all.reset_index()
qbr_nr_all['permits_scaled'] = qbr_nr_all['permitjob_issued_count']/qbr_nr_all['permitjob_issued_count'].abs().max()

'''
###create visualizations
#sns.relplot(data=national,x='filename',y='permits')
us_plot = sns.lineplot(data=national,x='date',y='permits')
plt.setp(us_plot.get_xticklabels(),rotation=90)
plt.title('US new residential permits, total')
plt.show()
#CLOSE COMMAND
plt.close()

us_plot_max_abs = sns.lineplot(data=national,x='date',y='permits_scaled')
plt.setp(us_plot_max_abs.get_xticklabels(),rotation=90)
plt.title('US new residential permits, max abs. scaling')
plt.show()
#CLOSE COMMAND
plt.close()

reg_plot = sns.lineplot(data=regional,x='date',y='permits',hue='state')
plt.setp(reg_plot.get_xticklabels(),rotation=90)
plt.title('regional')
plt.show()
plt.close()

div_plot = sns.lineplot(data=divisional,x='date',y='permits', hue='state')
plt.setp(div_plot.get_xticklabels(),rotation=90)
plt.title('divisional')
plt.show()
plt.close()

state_plot = sns.lineplot(data=state,x='date',y='permits',hue='state',legend="brief")
plt.setp(state_plot.get_xticklabels(),rotation=90)
plt.show()
plt.close()

qbr_all_plot = sns.lineplot(data=qbr_nr_all,x='date',y='permits_scaled')
plt.setp(qbr_all_plot.get_xticklabels(),rotation=90)
plt.title('Permits Issued, New Residential')
plt.show()
plt.close()

qbr_bunit_plot = sns.lineplot(data=qbr_nr,x='date',y='permits_scaled',hue='bunit_name')
plt.legend(bbox_to_anchor=(1.0,1),loc='upper left',borderaxespad=0)
plt.setp(qbr_bunit_plot.get_xticklabels(),rotation=90)
plt.title('Permits Issued, New Residential')
plt.show()
plt.close()
'''
