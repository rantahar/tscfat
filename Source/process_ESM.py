
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 15:08:26 2020

@author: arsi
"""
# standard library imports
import os
from pathlib import Path
import json

# change correct working directory
WORK_DIR = Path('/u/26/ikaheia1/unix/Documents/SpecialAssignment/CS-special-assignment/')
os.chdir(WORK_DIR)

# third party imports
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from matplotlib.dates import DateFormatter
import nolds
from arma import arma, autocorr
from datetime import datetime

from statsmodels.tsa.stattools import acf, pacf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# Local application import


from vector_encoding import ordinal_encoding, one_hot_encoding, decode_string, decode_string_3, custom_resampler, normalize_values
from calculate_RQA import Calculate_RQA
from calculate_JRQA import Calculate_JRQA
from plot_recurrence import Show_recurrence_plot
from save_results import dump_to_json
from plot_timeseries import show_timeseries_scatter, show_features
from save2mat import save2mat
from calculate_similarity import calculate_similarity
from calculate_novelty import compute_novelty_SSM
from json_load import load_one_subject
from Plot_similarity import Plot_similarity
from interpolate_missing import interpolate_missing
from assign_labels import assign_groups
from scipy.stats import pearsonr, spearmanr
from decompose_timeseries import STL_decomposition

def process_ESM(df):
    
    GROUP_LABEL_CSV_PATH = Path('/u/26/ikaheia1/unix/Documents/SpecialAssignment/esm_groups.csv/')
    df = assign_groups(df,GROUP_LABEL_CSV_PATH)
    
    #%% Recursion plot settings
    ED = 1 # embedding dimensions
    TD = 1 # time delay
    RA = 0.15 # neigborhood radius
    
    #%% Check NaN's
    #df_nans = df.groupby[]
    df.isna().sum().plot(kind='bar')  
    plt.show()
    print(df.isna().any())
    # df.dropna() / df.fillna(0)
    
    #%%
    
    mask1 = df["type"] == 1
    mask2 = df["type"] == 2
    mask3 = df["type"] == 3
    mask6 = df["type"] == 6
    df['scaled_answer'] = 0
    
    # fill nan's
    df.loc[mask6,'scaled_answer'] = df.loc[mask6,'answer'].fillna(np.round((df.loc[mask6,'answer'].astype(float).mean())))
    
    df.loc[mask1,"scaled_answer"] = df.loc[mask1,"answer"].map(decode_string)
    df.loc[mask2,"scaled_answer"] = df.loc[mask2,"answer"].map(decode_string)
    df.loc[mask3,"scaled_answer"] = df.loc[mask3,"answer"].map(decode_string_3)
    
    sequence = zip(df['scaled_answer'].values,df['negate_value'].values)
    x = lambda i : 0 if i == 1 else 1
    df['scaled_answer'] = [x(i) if neg == True else i for i,neg in sequence]
    
    #df.loc[mask1,"Scaled_answer"] = df.loc[mask1,"answer"] 
    #df.loc[mask2,"Scaled_answer"] = df.loc[mask2,"answer"] 
    #df.loc[mask3,"Scaled_answer"] = normalize_values(df.loc[mask3,"answer"].values.astype(float))
    #df.loc[mask6,"Scaled_answer"] = normalize_values(df.loc[mask6,"answer"].values.astype(float))
    
    #%%
    #df_filt = df.filter(["time","Scaled_answer",])
    df_filt = df.filter(["time","group","negate_value","scaled_answer",])
    #df_filt = df_filt["Scaled_answer"].astype(int)
    df_filt['scaled_answer'] = df_filt["scaled_answer"].astype(int)
    #resampled = df_filt.resample("D").apply(custom_resampler)
    
    #%% Positive and negative affects
    
    # Positive
    df_temp = df[df['title'] == 'Right now I feel Active']
    df_temp = df_temp['scaled_answer'].astype('int64')
    active = df_temp.resample('D').mean()
    
    df_temp = df[df['title'] == 'Right now I feel Determined']
    df_temp = df_temp['scaled_answer'].astype('int64')
    determined = df_temp.resample('D').mean()
    
    df_temp = df[df['title'] == 'Right now I feel Attentive']
    df_temp = df_temp['scaled_answer'].astype('int64')
    attentive = df_temp.resample('D').mean()
    
    df_temp = df[df['title'] == 'Right now I feel Inspired']
    df_temp = df_temp['scaled_answer'].astype('int64')
    inspired = df_temp.resample('D').mean()
    
    df_temp = df[df['title'] == 'Right now I feel Alert']
    df_temp = df_temp['scaled_answer'].astype('int64')
    alert = df_temp.resample('D').mean()
    
    # Negative
    df_temp2 = df[df['title'] == 'Right now I feel Afraid']
    df_temp2 = df_temp2['scaled_answer'].astype('int64')
    afraid = df_temp2.resample('D').mean()
    
    df_temp2 = df[df['title'] == 'Right now I feel Nervous']
    df_temp2 = df_temp2['scaled_answer'].astype('int64')
    nervous = df_temp2.resample('D').mean()
    
    df_temp2 = df[df['title'] == 'Right now I feel Upset']
    df_temp2 = df_temp2['scaled_answer'].astype('int64')
    upset = df_temp2.resample('D').mean()
    
    df_temp2 = df[df['title'] == 'Right now I feel Hostile']
    df_temp2 = df_temp2['scaled_answer'].astype('int64')
    hostile = df_temp2.resample('D').mean()
    
    df_temp2 = df[df['title'] == 'Right now I feel Ashamed']
    df_temp2 = df_temp2['scaled_answer'].astype('int64')
    ashamed = df_temp2.resample('D').mean()
    
    df_temp2 = df[df['title'] == 'Right now I feel Stressed']
    df_temp2 = df_temp2['scaled_answer'].astype('int64')
    stressed = df_temp2.resample('D').mean()
    stressed_max = df_temp2.resample('D').max()
    
    df_temp2 = df[df['title'] == 'Right now I feel Distracted']
    df_temp2 = df_temp2['scaled_answer'].astype('int64')
    distracted = df_temp2.resample('D').mean()
    #%%
    affections = pd.concat([active,determined,attentive,inspired,alert,afraid,nervous,upset,hostile,ashamed,stressed,distracted],axis=1)
    affections.columns=['active','determined','attentive','inspired','alert','afraid','nervous','upset','hostile',
                                  'ashamed','stressed','distracted']
    
    #%% correlation
    corr_s = affections.corr(method="spearman")
    fig, ax = plt.subplots(figsize=(9,8))
    xticks = corr_s.columns
    sns.heatmap(corr_s, annot = True, fmt='.1g',ax=ax,xticklabels=xticks)
    ax.set_title('Postivie and Negative Affections \nSpearman Correlation',fontsize=22)
    plt.xticks(rotation=45,fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout(pad=0)

    #%% plot affections
    date_form = DateFormatter("%m-%d")
       
    fig,ax = plt.subplots(3,2,figsize=(12,15))
    fig.suptitle("Positive affections / daily averages",fontsize=20,y=1.02)
    
    ax[0,0].plot(affections.iloc[:,0])
    ax[0,0].set_title('Active',fontsize=16)
    ax[0,0].set_xlabel('Time (d)')
    ax[0,0].set_ylabel('Value')
    ax[0,0].set_ylim(1,6)
    ax[0,0].xaxis.set_major_formatter(date_form)
       
    ax[0,1].plot(affections.iloc[:,1])
    ax[0,1].set_title('Determined',fontsize=16)
    ax[0,1].set_xlabel('Time (d)')
    ax[0,1].set_ylabel('Value')
    ax[0,1].set_ylim(1,6)
    ax[0,1].xaxis.set_major_formatter(date_form)
    
    ax[1,0].plot(affections.iloc[:,2])
    ax[1,0].set_title('Attentive',fontsize=16)
    ax[1,0].set_xlabel('Time (d)')
    ax[1,0].set_ylabel('Value')
    ax[1,0].set_ylim(1,6)
    ax[1,0].xaxis.set_major_formatter(date_form)
    
    ax[1,1].plot(affections.iloc[:,3])
    ax[1,1].set_title('Inspired',fontsize=16)
    ax[1,1].set_xlabel('Time (d)')
    ax[1,1].set_ylabel('Value')
    ax[1,1].set_ylim(1,6)
    ax[1,1].xaxis.set_major_formatter(date_form)
    
    ax[2,0].plot(affections.iloc[:,4])
    ax[2,0].set_title('Alert',fontsize=16)
    ax[2,0].set_xlabel('Time (d)')
    ax[2,0].set_ylabel('Value')
    ax[2,0].set_ylim(1,6)
    ax[2,0].xaxis.set_major_formatter(date_form)
    
    fig.tight_layout(pad=1.0)
    plt.show()
    
    #%% plot affections
        
    affect_rolls = affections.rolling(window=7).var()
    affect_autocorr = affections.rolling(window=7).apply(autocorr)
    affect_mean = affections.rolling(window=7).mean()    
         
    fig,ax = plt.subplots(3,2,figsize=(12,15))
    fig.suptitle("Positive affections rolling window(7) variance",fontsize=20,y=1.02)
    
    ax[0,0].plot(affect_rolls.iloc[:,0])
    ax[0,0].set_title('Active',fontsize=16)
    ax[0,0].set_xlabel('Time (d)')
    ax[0,0].set_ylabel('Value')
    ax[0,0].set_ylim(0,0.7)
    ax[0,0].xaxis.set_major_formatter(date_form)
       
    ax[0,1].plot(affect_rolls.iloc[:,1])
    ax[0,1].set_title('Determined',fontsize=16)
    ax[0,1].set_xlabel('Time (d)')
    ax[0,1].set_ylabel('Value')
    ax[0,1].set_ylim(0,0.7)
    ax[0,1].xaxis.set_major_formatter(date_form)
    
    ax[1,0].plot(affect_rolls.iloc[:,2])
    ax[1,0].set_title('Attentive',fontsize=16)
    ax[1,0].set_xlabel('Time (d)')
    ax[1,0].set_ylabel('Value')
    ax[1,0].set_ylim(0,0.7)
    ax[1,0].xaxis.set_major_formatter(date_form)
    
    ax[1,1].plot(affect_rolls.iloc[:,3])
    ax[1,1].set_title('Inspired',fontsize=16)
    ax[1,1].set_xlabel('Time (d)')
    ax[1,1].set_ylabel('Value')
    ax[1,1].set_ylim(0,0.7)
    ax[1,1].xaxis.set_major_formatter(date_form)
    
    ax[2,0].plot(affect_rolls.iloc[:,4])
    ax[2,0].set_title('Alert',fontsize=16)
    ax[2,0].set_xlabel('Time (d)')
    ax[2,0].set_ylabel('Value')
    ax[2,0].set_ylim(0,0.7)
    ax[2,0].xaxis.set_major_formatter(date_form)
    
    fig.tight_layout(pad=1.0)
    plt.show()
    
    #%%
    fig,ax = plt.subplots(3,2,figsize=(12,15))
    fig.suptitle("Positive affections rolling window(7) autocorrelation(1)",fontsize=20,y=1.02)
    
    ax[0,0].plot(affect_autocorr.iloc[:,0])
    ax[0,0].set_title('Active',fontsize=16)
    ax[0,0].set_xlabel('Time (d)')
    ax[0,0].set_ylabel('Value')
    ax[0,0].set_ylim(-1,1)
    ax[0,0].xaxis.set_major_formatter(date_form)
       
    ax[0,1].plot(affect_autocorr.iloc[:,1])
    ax[0,1].set_title('Determined',fontsize=16)
    ax[0,1].set_xlabel('Time (d)')
    ax[0,1].set_ylabel('Value')
    ax[0,1].set_ylim(-1,1)
    ax[0,1].xaxis.set_major_formatter(date_form)
    
    ax[1,0].plot(affect_autocorr.iloc[:,2])
    ax[1,0].set_title('Attentive',fontsize=16)
    ax[1,0].set_xlabel('Time (d)')
    ax[1,0].set_ylabel('Value')
    ax[1,0].set_ylim(-1,1)
    ax[1,0].xaxis.set_major_formatter(date_form)
    
    ax[1,1].plot(affect_autocorr.iloc[:,3])
    ax[1,1].set_title('Inspired',fontsize=16)
    ax[1,1].set_xlabel('Time (d)')
    ax[1,1].set_ylabel('Value')
    ax[1,1].set_ylim(-1,1)
    ax[1,1].xaxis.set_major_formatter(date_form)
    
    ax[2,0].plot(affect_autocorr.iloc[:,4])
    ax[2,0].set_title('Alert',fontsize=16)
    ax[2,0].set_xlabel('Time (d)')
    ax[2,0].set_ylabel('Value')
    ax[2,0].set_ylim(-1,1)
    ax[2,0].xaxis.set_major_formatter(date_form)
    
    fig.tight_layout(pad=1.0)
    plt.show()
    
    #%%
    #%%
    fig,ax = plt.subplots(3,2,figsize=(12,15))
    fig.suptitle("Positive affections rolling window(7) mean",fontsize=20,y=1.02)
    
    ax[0,0].plot(affect_mean.iloc[:,0])
    ax[0,0].set_title('Active',fontsize=16)
    ax[0,0].set_xlabel('Time (d)')
    ax[0,0].set_ylabel('Value')
    ax[0,0].set_ylim(1,4)
    ax[0,0].xaxis.set_major_formatter(date_form)
       
    ax[0,1].plot(affect_mean.iloc[:,1])
    ax[0,1].set_title('Determined',fontsize=16)
    ax[0,1].set_xlabel('Time (d)')
    ax[0,1].set_ylabel('Value')
    ax[0,1].set_ylim(1,4)
    ax[0,1].xaxis.set_major_formatter(date_form)
    
    ax[1,0].plot(affect_mean.iloc[:,2])
    ax[1,0].set_title('Attentive',fontsize=16)
    ax[1,0].set_xlabel('Time (d)')
    ax[1,0].set_ylabel('Value')
    ax[1,0].set_ylim(1,4)
    ax[1,0].xaxis.set_major_formatter(date_form)
    
    ax[1,1].plot(affect_mean.iloc[:,3])
    ax[1,1].set_title('Inspired',fontsize=16)
    ax[1,1].set_xlabel('Time (d)')
    ax[1,1].set_ylabel('Value')
    ax[1,1].set_ylim(1,4)
    ax[1,1].xaxis.set_major_formatter(date_form)
    
    ax[2,0].plot(affect_mean.iloc[:,4])
    ax[2,0].set_title('Alert',fontsize=16)
    ax[2,0].set_xlabel('Time (d)')
    ax[2,0].set_ylabel('Value')
    ax[2,0].set_ylim(1,4)
    ax[2,0].xaxis.set_major_formatter(date_form)
    
    fig.tight_layout(pad=1.0)
    plt.show()
    
    #%% negative affections
    fig,ax = plt.subplots(4,2,figsize=(12,15))
    fig.suptitle("Negative affections rolling daily averages",fontsize=20,y=1.02)
    
    ax[0,0].plot(affections.iloc[:,5])
    ax[0,0].set_title('Afraid',fontsize=16)
    ax[0,0].set_xlabel('Time (d)')
    ax[0,0].set_ylabel('Value')
    ax[0,0].set_ylim(0.8,3.2)
    ax[0,0].xaxis.set_major_formatter(date_form)
       
    ax[0,1].plot(affections.iloc[:,6])
    ax[0,1].set_title('Nervous',fontsize=16)
    ax[0,1].set_xlabel('Time (d)')
    ax[0,1].set_ylabel('Value')
    ax[0,1].set_ylim(0.8,3.2)
    ax[0,1].xaxis.set_major_formatter(date_form)
    
    ax[1,0].plot(affections.iloc[:,7])
    ax[1,0].set_title('Upset',fontsize=16)
    ax[1,0].set_xlabel('Time (d)')
    ax[1,0].set_ylabel('Value')
    ax[1,0].set_ylim(0.8,3.2)
    ax[1,0].xaxis.set_major_formatter(date_form)
    
    ax[1,1].plot(affections.iloc[:,8])
    ax[1,1].set_title('Hostile',fontsize=16)
    ax[1,1].set_xlabel('Time (d)')
    ax[1,1].set_ylabel('Value')
    ax[1,1].set_ylim(0.8,3.2)
    ax[1,1].xaxis.set_major_formatter(date_form)
    
    ax[2,0].plot(affections.iloc[:,9])
    ax[2,0].set_title('Ashamed',fontsize=16)
    ax[2,0].set_xlabel('Time (d)')
    ax[2,0].set_ylabel('Value')
    ax[2,0].set_ylim(0.8,3.2)
    ax[2,0].xaxis.set_major_formatter(date_form)
    
    ax[2,1].plot(affections.iloc[:,10])
    ax[2,1].set_title('Stressed',fontsize=16)
    ax[2,1].set_xlabel('Time (d)')
    ax[2,1].set_ylabel('Value')
    ax[2,1].set_ylim(0.8,3.2)
    ax[2,1].xaxis.set_major_formatter(date_form)
    
    ax[3,0].plot(affections.iloc[:,11])
    ax[3,0].set_title('Distracted',fontsize=16)
    ax[3,0].set_xlabel('Time (d)')
    ax[3,0].set_ylabel('Value')
    ax[3,0].set_ylim(0.8,3.2)
    ax[3,0].xaxis.set_major_formatter(date_form)
    
    fig.tight_layout(pad=1.0)
    plt.show()
    
    #%% negative affections
    fig,ax = plt.subplots(4,2,figsize=(12,15))
    fig.suptitle("Negative affections rolling window(7) variance",fontsize=20,y=1.02)
    
    ax[0,0].plot(affect_rolls.iloc[:,5])
    ax[0,0].set_title('Afraid',fontsize=16)
    ax[0,0].set_xlabel('Time (d)')
    ax[0,0].set_ylabel('Value')
    ax[0,0].set_ylim(0,1)
    ax[0,0].xaxis.set_major_formatter(date_form)
       
    ax[0,1].plot(affect_rolls.iloc[:,6])
    ax[0,1].set_title('Nervous',fontsize=16)
    ax[0,1].set_xlabel('Time (d)')
    ax[0,1].set_ylabel('Value')
    ax[0,1].set_ylim(0,1)
    ax[0,1].xaxis.set_major_formatter(date_form)
    
    ax[1,0].plot(affect_rolls.iloc[:,7])
    ax[1,0].set_title('Upset',fontsize=16)
    ax[1,0].set_xlabel('Time (d)')
    ax[1,0].set_ylabel('Value')
    ax[1,0].set_ylim(0,1)
    ax[1,0].xaxis.set_major_formatter(date_form)
    
    ax[1,1].plot(affect_rolls.iloc[:,8])
    ax[1,1].set_title('Hostile',fontsize=16)
    ax[1,1].set_xlabel('Time (d)')
    ax[1,1].set_ylabel('Value')
    ax[1,1].set_ylim(0,1)
    ax[1,1].xaxis.set_major_formatter(date_form)
    
    ax[2,0].plot(affect_rolls.iloc[:,9])
    ax[2,0].set_title('Ashamed',fontsize=16)
    ax[2,0].set_xlabel('Time (d)')
    ax[2,0].set_ylabel('Value')
    ax[2,0].set_ylim(0,1)
    ax[2,0].xaxis.set_major_formatter(date_form)
    
    ax[2,1].plot(affect_rolls.iloc[:,10])
    ax[2,1].set_title('Stressed',fontsize=16)
    ax[2,1].set_xlabel('Time (d)')
    ax[2,1].set_ylabel('Value')
    ax[2,1].set_ylim(0,1)
    ax[2,1].xaxis.set_major_formatter(date_form)
    
    ax[3,0].plot(affect_rolls.iloc[:,11])
    ax[3,0].set_title('Distracted',fontsize=16)
    ax[3,0].set_xlabel('Time (d)')
    ax[3,0].set_ylabel('Value')
    ax[3,0].set_ylim(0,1)
    ax[3,0].xaxis.set_major_formatter(date_form)
    
    fig.tight_layout(pad=1.0)
    plt.show()
    
    #%% negative affections
    fig,ax = plt.subplots(4,2,figsize=(12,15))
    fig.suptitle("Negative affections rolling window(7) mean",fontsize=20,y=1.02)
    
    ax[0,0].plot(affect_mean.iloc[:,5])
    ax[0,0].set_title('Afraid',fontsize=16)
    ax[0,0].set_xlabel('Time (d)')
    ax[0,0].set_ylabel('Value')
    ax[0,0].set_ylim(0.8,2.4)
    ax[0,0].xaxis.set_major_formatter(date_form)
       
    ax[0,1].plot(affect_mean.iloc[:,6])
    ax[0,1].set_title('Nervous',fontsize=16)
    ax[0,1].axvspan(datetime(2020,7,1),datetime(2020,7,15),facecolor="red",alpha=0.15,label="Days of interest")
    ax[0,1].set_xlabel('Time (d)')
    ax[0,1].set_ylabel('Value')
    ax[0,1].set_ylim(0.8,2.4)
    ax[0,1].xaxis.set_major_formatter(date_form)
    
    ax[1,0].plot(affect_mean.iloc[:,7])
    ax[1,0].set_title('Upset',fontsize=16)
    ax[1,0].set_xlabel('Time (d)')
    ax[1,0].set_ylabel('Value')
    ax[1,0].set_ylim(0.8,2.4)
    ax[1,0].xaxis.set_major_formatter(date_form)
    
    ax[1,1].plot(affect_mean.iloc[:,8])
    ax[1,1].set_title('Hostile',fontsize=16)
    ax[1,1].set_xlabel('Time (d)')
    ax[1,1].set_ylabel('Value')
    ax[1,1].set_ylim(0.8,2.4)
    ax[1,1].xaxis.set_major_formatter(date_form)
    
    ax[2,0].plot(affect_mean.iloc[:,9])
    ax[2,0].set_title('Ashamed',fontsize=16)
    ax[2,0].set_xlabel('Time (d)')
    ax[2,0].set_ylabel('Value')
    ax[2,0].set_ylim(0.8,2.4)
    ax[2,0].xaxis.set_major_formatter(date_form)
    
    ax[2,1].plot(affect_mean.iloc[:,10])
    ax[2,1].set_title('Stressed',fontsize=16)
    ax[2,1].axvspan(datetime(2020,7,1),datetime(2020,7,15),facecolor="red",alpha=0.15,label="Days of interest")
    ax[2,1].set_xlabel('Time (d)')
    ax[2,1].set_ylabel('Value')
    ax[2,1].set_ylim(0.8,2.4)
    ax[2,1].xaxis.set_major_formatter(date_form)
    
    ax[3,0].plot(affect_mean.iloc[:,11])
    ax[3,0].set_title('Distracted',fontsize=16)
    ax[3,0].set_xlabel('Time (d)')
    ax[3,0].set_ylabel('Value')
    ax[3,0].set_ylim(0.8,2.4)
    ax[3,0].xaxis.set_major_formatter(date_form)
    
    fig.tight_layout(pad=1.0)
    plt.show()
    
    #%% for the report
    fig, (ax1,ax2) = plt.subplots(1,2,figsize=(12,3.5),dpi=300)
    fig.suptitle("Negative affections rolling window(7) average",fontsize=20,y=1.05)
    
    ax1.plot(affect_mean.iloc[:,10])
    ax1.set_title('Stressed',fontsize=16)
    ax1.axvspan(datetime(2020,7,1),datetime(2020,7,15),facecolor="red",alpha=0.15,label="Days of interest")
    ax1.set_xlabel('Time (date)',fontsize=14)
    ax1.set_ylabel('Value',fontsize=14)
    ax1.set_ylim(0.9,2.1)
    ax1.tick_params(axis='x',labelrotation=45)
    ax1.xaxis.set_major_formatter(date_form)
       
    ax2.plot(affect_mean.iloc[:,6])
    ax2.set_title('Nervous',fontsize=16)
    ax2.axvspan(datetime(2020,7,1),datetime(2020,7,15),facecolor="red",alpha=0.15,label="Days of interest")
    ax2.set_xlabel('Time (date)',fontsize=14)
    ax2.set_ylabel('Value',fontsize=14)
    ax2.set_ylim(0.9,2.1)
    ax2.tick_params(axis='x',labelrotation=45)
    ax2.xaxis.set_major_formatter(date_form)
    
    #%% negative affections
    fig,ax = plt.subplots(4,2,figsize=(12,15))
    fig.suptitle("Negative affections rolling window(7) autocorrelation(1)",fontsize=20,y=1.02)
    
    ax[0,0].plot(affect_autocorr.iloc[:,5])
    ax[0,0].set_title('Afraid',fontsize=16)
    ax[0,0].set_xlabel('Time (d)')
    ax[0,0].set_ylabel('Value')
    ax[0,0].set_ylim(-1,1)
    ax[0,0].xaxis.set_major_formatter(date_form)
       
    ax[0,1].plot(affect_autocorr.iloc[:,6])
    ax[0,1].set_title('Nervous',fontsize=16)
    ax[0,1].set_xlabel('Time (d)')
    ax[0,1].set_ylabel('Value')
    ax[0,1].set_ylim(-1,1)
    ax[0,1].xaxis.set_major_formatter(date_form)
    
    ax[1,0].plot(affect_autocorr.iloc[:,7])
    ax[1,0].set_title('Upset',fontsize=16)
    ax[1,0].set_xlabel('Time (d)')
    ax[1,0].set_ylabel('Value')
    ax[1,0].set_ylim(-1,1)
    ax[1,0].xaxis.set_major_formatter(date_form)
    
    ax[1,1].plot(affect_autocorr.iloc[:,8])
    ax[1,1].set_title('Hostile',fontsize=16)
    ax[1,1].set_xlabel('Time (d)')
    ax[1,1].set_ylabel('Value')
    ax[1,1].set_ylim(-1,1)
    ax[1,1].xaxis.set_major_formatter(date_form)
    
    ax[2,0].plot(affect_autocorr.iloc[:,9])
    ax[2,0].set_title('Ashamed',fontsize=16)
    ax[2,0].set_xlabel('Time (d)')
    ax[2,0].set_ylabel('Value')
    ax[2,0].set_ylim(-1,1)
    ax[2,0].xaxis.set_major_formatter(date_form)
    
    ax[2,1].plot(affect_autocorr.iloc[:,10])
    ax[2,1].set_title('Stressed',fontsize=16)
    ax[2,1].set_xlabel('Time (d)')
    ax[2,1].set_ylabel('Value')
    ax[2,1].set_ylim(-1,1)
    ax[2,1].xaxis.set_major_formatter(date_form)
    
    ax[3,0].plot(affect_autocorr.iloc[:,11])
    ax[3,0].set_title('Distracted',fontsize=16)
    ax[3,0].set_xlabel('Time (d)')
    ax[3,0].set_ylabel('Value')
    ax[3,0].set_ylim(-1,1)
    ax[3,0].xaxis.set_major_formatter(date_form)
    
    fig.tight_layout(pad=1.0)
    plt.show()
    #%% DFA
    dfa_rolls = affections.rolling(window=14).apply(nolds.dfa)
    
    #%% negative affections
    fig,ax = plt.subplots(6,2,figsize=(16,20))
    fig.suptitle("Affections DFA window(14)",fontsize=20,y=1.02)
    
    ax[0,0].plot(dfa_rolls.iloc[:,0])
    ax[0,0].set_title('Active',fontsize=16)
    ax[0,0].set_xlabel('Time (d)')
    ax[0,0].set_ylabel('Value')
    ax[0,0].set_ylim(-1,3)
    ax[0,0].xaxis.set_major_formatter(date_form)
       
    ax[0,1].plot(dfa_rolls.iloc[:,1])
    ax[0,1].set_title('Determined',fontsize=16)
    ax[0,1].set_xlabel('Time (d)')
    ax[0,1].set_ylabel('Value')
    ax[0,1].set_ylim(-1,3)
    ax[0,1].xaxis.set_major_formatter(date_form)
    
    ax[1,0].plot(dfa_rolls.iloc[:,2])
    ax[1,0].set_title('Attentive',fontsize=16)
    ax[1,0].set_xlabel('Time (d)')
    ax[1,0].set_ylabel('Value')
    ax[1,0].set_ylim(-1,3)
    ax[1,0].xaxis.set_major_formatter(date_form)
    
    ax[1,1].plot(dfa_rolls.iloc[:,3])
    ax[1,1].set_title('Inspired',fontsize=16)
    ax[1,1].set_xlabel('Time (d)')
    ax[1,1].set_ylabel('Value')
    ax[1,1].set_ylim(-1,3)
    ax[1,1].xaxis.set_major_formatter(date_form)
    
    ax[2,0].plot(dfa_rolls.iloc[:,4])
    ax[2,0].set_title('Alert',fontsize=16)
    ax[2,0].set_xlabel('Time (d)')
    ax[2,0].set_ylabel('Value')
    ax[2,0].set_ylim(-1,3)
    ax[2,0].xaxis.set_major_formatter(date_form)
    
    ax[2,1].plot(dfa_rolls.iloc[:,5])
    ax[2,1].set_title('Afraid',fontsize=16)
    ax[2,1].set_xlabel('Time (d)')
    ax[2,1].set_ylabel('Value')
    ax[2,1].set_ylim(-1,3)
    ax[2,1].xaxis.set_major_formatter(date_form)
          
    ax[3,0].plot(dfa_rolls.iloc[:,7])
    ax[3,0].set_title('Upset',fontsize=16)
    ax[3,0].set_xlabel('Time (d)')
    ax[3,0].set_ylabel('Value')
    ax[3,0].set_ylim(-1,3)
    ax[3,0].xaxis.set_major_formatter(date_form)
    
    ax[3,1].plot(dfa_rolls.iloc[:,8])
    ax[3,1].set_title('Hostile',fontsize=16)
    ax[3,1].set_xlabel('Time (d)')
    ax[3,1].set_ylabel('Value')
    ax[3,1].set_ylim(-1,3)
    ax[3,1].xaxis.set_major_formatter(date_form)
    
    ax[4,0].plot(dfa_rolls.iloc[:,9])
    ax[4,0].set_title('Ashamed',fontsize=16)
    ax[4,0].set_xlabel('Time (d)')
    ax[4,0].set_ylabel('Value')
    ax[4,0].set_ylim(-1,3)
    ax[4,0].xaxis.set_major_formatter(date_form)
    
    ax[4,1].plot(dfa_rolls.iloc[:,10])
    ax[4,1].set_title('Stressed',fontsize=16)
    ax[4,1].set_xlabel('Time (d)')
    ax[4,1].set_ylabel('Value')
    ax[4,1].set_ylim(-1,3)
    ax[4,1].xaxis.set_major_formatter(date_form)
    
    ax[5,0].plot(dfa_rolls.iloc[:,11])
    ax[5,0].set_title('Distracted',fontsize=16)
    ax[5,0].set_xlabel('Time (d)')
    ax[5,0].set_ylabel('Value')
    ax[5,0].set_ylim(-1,3)
    ax[5,0].xaxis.set_major_formatter(date_form)
    
    ax[5,1].plot(dfa_rolls.iloc[:,6])
    ax[5,1].set_title('Nervous',fontsize=16)
    ax[5,1].set_xlabel('Time (d)')
    ax[5,1].set_ylabel('Value')
    ax[5,1].set_ylim(-1,3)
    ax[5,1].xaxis.set_major_formatter(date_form)
    
    fig.tight_layout(pad=1.0)
    plt.show()
    #%%
    grouped = df_filt.groupby('group').resample('D').sum()
    #grouped = df_filt.groupby('group').resample('D').mean()
    
    grouped_agg = df_filt.groupby('group').resample('D').agg(lambda x: x.tolist())
    
    # fill missing values by hand :(
    grouped_agg.iloc[46,0] = [1,1,1]
    grouped_agg.iloc[49,0] = [1,1,1]
    grouped_agg.iloc[46,1] = [False,True,False]
    grouped_agg.iloc[49,1] = [False,True,False]
    grouped_agg.iloc[46,2] = [1,1,0]
    grouped_agg.iloc[49,2] = [1,1,0]
    
    grouped_agg.iloc[184,0] = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
    grouped_agg.iloc[187,0] = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
    grouped_agg.iloc[184,1] = [False]*39
    grouped_agg.iloc[187,1] = [False]*39
    grouped_agg.iloc[184,2] = [1,1,1,1,1,1,1] + grouped_agg.iloc[184,2]
    grouped_agg.iloc[187,2] = [1,1,1,1,1,1,1] + grouped_agg.iloc[187,2]
    
    grouped_agg.iloc[115,0] = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    grouped_agg.iloc[118,0] = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    grouped_agg.iloc[115,1] = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
    grouped_agg.iloc[118,1] = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
    grouped_agg.iloc[115,2] = [2,2,2,2,2] + grouped_agg.iloc[115,2]
    grouped_agg.iloc[118,2] = [2,2,2,2,2] + grouped_agg.iloc[118,2]
    
    
    
    #grouped_agg = grouped.groupby(grouped['id']).agg(lambda x: x.tolist())
    positives = np.stack(grouped_agg.scaled_answer[grouped_agg.index.isin(['2'], level=0)].to_numpy())
    negatives = np.stack(grouped_agg.scaled_answer[grouped_agg.index.isin(['3'], level=0)].to_numpy())
    rho, pval = spearmanr(positives,negatives,axis=0)
    
    ts1 = grouped.scaled_answer[grouped.index.isin(['1'], level=0)]
    ts2 = grouped.scaled_answer[grouped.index.isin(['2'], level=0)]
    ts3 = grouped.scaled_answer[grouped.index.isin(['3'], level=0)]
    ts4 = grouped.scaled_answer[grouped.index.isin(['4'], level=0)]
    ts5 = grouped.scaled_answer[grouped.index.isin(['5'], level=0)]
    ts6 = grouped.scaled_answer[grouped.index.isin(['6'], level=0)]
    ts7 = grouped.scaled_answer[grouped.index.isin(['7'], level=0)]
    ts8 = grouped.scaled_answer[grouped.index.isin(['8'], level=0)]
    
    ts1.index = ts1.index.droplevel(level=0)
    ts2.index = ts2.index.droplevel(level=0)
    ts3.index = ts3.index.droplevel(level=0)
    ts4.index = ts4.index.droplevel(level=0)
    ts5.index = ts5.index.droplevel(level=0)
    ts6.index = ts6.index.droplevel(level=0)
    ts7.index = ts7.index.droplevel(level=0)
    ts8.index = ts8.index.droplevel(level=0)
    
    
    series = [ts1,ts2,ts3,ts4,ts5,ts6,ts7,ts8]
    
    combined_df = pd.concat(series, axis=1)
    combined_df.columns = ['Sleep','Positive_mood','Negative_mood','Social_interaction','Difficulty_comp','Explanatory','Substances','Exercise']
    
    #%% Correlation
    corr_p = combined_df.corr(method ='pearson') 
    corr_s = combined_df.corr(method ='spearman')
    corr_k = combined_df.corr(method ='kendall')
    
    #%%
    def corrfunc(x,y, ax=None, **kws):
        """Plot the correlation coefficient in the top left hand corner of a plot."""
        r, _ = spearmanr(x, y)
        ax = ax or plt.gca()
        # Unicode for lowercase rho (ρ)
        rho = '\u03C1'
        ax.annotate(f'{rho} = {r:.2f}', xy=(.1, .9), xycoords=ax.transAxes)
        
    g = sns.pairplot(combined_df,kind="reg")
    g.map_lower(corrfunc)
    g.fig.suptitle("ESM data pairplots and Spearman correlation", y=1.02,fontsize=20)
    
    plt.show()
    #%% scale the data
    scaler = MinMaxScaler()
    scaled_df = pd.DataFrame(scaler.fit_transform(combined_df), columns=combined_df.columns, index = combined_df.index)
    #%%
    #sns.pairplot(df_scaled,kind="reg")
    #sns.plt.show()
    #%%
    plt.figure(figsize=(20,20))
    
    plt.suptitle('ESM results',fontsize=20)
    
    plt.subplot(4,2,1)
    ts1.plot()
    plt.axvspan(datetime(2020,7,1),datetime(2020,7,15),facecolor="red",alpha=0.15,label="Days of interest")
    plt.title('Sleep quality')
    plt.xticks([])
    #plt.show()
    
    plt.subplot(4,2,2)
    ts2.plot()
    plt.title('Positive mood')
    plt.xticks([])
    #plt.xticks(rotation=45)
    #plt.show()
    
    plt.subplot(4,2,3)
    ts3.plot()
    plt.title('Negative mood')
    plt.xticks([])
    #plt.xticks(rotation=45)
    #plt.show()
    
    plt.subplot(4,2,4)
    ts4.plot()
    plt.title('Social interaction')
    plt.xticks([])
    #plt.xticks(rotation=45)
    #plt.show()
    
    plt.subplot(4,2,5)
    ts5.plot()
    plt.title('Difficulty in task completion')
    plt.xticks([])
    #plt.xticks(rotation=45)
    #plt.show()
    
    plt.subplot(4,2,6)
    ts6.plot()
    plt.title('Explanatory fact')
    plt.xticks([])
    #plt.xticks(rotation=45)
    #plt.show()
    
    plt.subplot(4,2,7)
    ts7.plot()
    plt.title('Sunbstance usage')
    plt.xticks(rotation=45)
    #plt.show()
    
    plt.subplot(4,2,8)
    ts8.plot()
    plt.title('Exercise')
    plt.xticks(rotation=45)
    
    plt.show()
    
    
    #%%
    #grouper = df.groupby([pd.Grouper(freq='D'), df.index])
    #result = grouper['group'].count().unstack('scaled_answer')
    #%%
    #timeseries = resampled.values
    #timeseries = np.stack(timeseries[:-1])
    #print(timeseries.shape)
    
    timeseries = combined_df.to_numpy()
    timeseries_2 = scaled_df.to_numpy()
    #%% calculate receursion plot and metrics
    # similarity
    AXIS = scaled_df.index.strftime('%m-%d') 
    sim = calculate_similarity(timeseries_2,'cosine')
    nov, kernel = compute_novelty_SSM(sim,L=7)
    #sim[sim >= 0.11] = 1
    Plot_similarity(sim,nov,"ESM",False,False,(0,0.06),0.95,AXIS,kernel)
    
    #%% neg sim
    sim = calculate_similarity(positives,'cosine')
    nov, kernel = compute_novelty_SSM(sim,L=7)
    #sim[sim >= 0.11] = 1
    Plot_similarity(sim,nov,"Pos ESM",False,False,(0,0.02),0.97,AXIS,kernel)
    #%% pos sim
    sim = calculate_similarity(negatives,'cosine')
    nov, kernel= compute_novelty_SSM(sim,L=7)
    #sim[sim >= 0.11] = 1
    Plot_similarity(sim,nov,"Neg ESM",False,False,(0,0.02),0.92,AXIS,kernel)
    
    
    #%% Calculate recursion plot and metrix
    res, mat = Calculate_RQA(timeseries,ED,TD,RA)
    
    #%%
    #%% Recursion plot settings

    #%% show recursion plot and save figure
    
    # set correct names and plot title
    FIGPATH = Path(r'/u/26/ikaheia1/unix/Documents/SpecialAssignment/Results/Plots/')
    FIGNAME = "recplot_2"
    TITLE = "ESM Recurrence Plot \n dim = {}, td = {}, r = {}".format(ED,TD,RA)  
    Show_recurrence_plot(mat,TITLE,FIGPATH,FIGNAME)
    
    #%% Decomposition
    
    dates = combined_df.index[6::7]
    #dates = np.arange(6,len(combined_df.index),7)
    decomposition_1 = STL_decomposition(combined_df['Sleep'],"Sleep")
    decomposition_2 = STL_decomposition(combined_df['Positive_mood'],"Aggregated Positive Mood Score \n STL Decomposition",False,False,"Score","Time (date)",dates)
    decomposition_3 = STL_decomposition(combined_df['Negative_mood'],"Aggregated Negative Mood Score \n STL Decomposition",False,False,"Score","Time (date)",dates)
    decomposition_4 = STL_decomposition(combined_df['Social_interaction'],"Social interaction")
    decomposition_5 = STL_decomposition(combined_df['Difficulty_comp'],"Difficulty to complete")
    decomposition_6 = STL_decomposition(combined_df['Explanatory'],"Explanatory")
    decomposition_7 = STL_decomposition(combined_df['Substances'],"Substances")
    decomposition_8 = STL_decomposition(combined_df['Exercise'],"Exercise")
    
    #%% ACF and PACF
    # Calculate ACF and PACF upto 50 lags / POSITIVE MOOD
    #acf_50 = acf(decomposition_2.seasonal.values, nlags=50)
    #pacf_50 = pacf(decomposition_2.seasonal.values, nlags=50)

    # Draw Plot
    fig, ax = plt.subplots(1,2,figsize=(10,5), dpi= 100)
    plt.suptitle('Mood Score Decomposition Autocorrelation Functions',fontsize=20,y=1.04)
    plot_acf(decomposition_2.seasonal.values, lags=50, ax = ax[0], title="Positive Mood / Seasonal")
    ax[0].set_xlabel("Lag",fontsize=14)
    ax[0].set_ylabel("Autocorrelation",fontsize=14)
    plot_acf(decomposition_3.seasonal.values, lags=50, ax = ax[1], title="Negative Mood / Seasonal")
    ax[1].set_xlabel("Lag",fontsize=14)
    ax[1].set_ylabel("Autocorrelation",fontsize=14)
    fig.tight_layout(pad=1)
    
    '''
    plot_acf(decomposition_2.trend.values, lags=50, ax = ax[2], title="Positive Mood / Trend")
    ax[2].set_xlabel("Lag")
    ax[2].set_ylabel("Autocorrelation")
    plot_acf(decomposition_3.trend.values, lags=50, ax = ax[3], title="Negative Mood / Trend")
    ax[3].set_xlabel("Lag")
    ax[3].set_ylabel("Autocorrelation")
    
    plot_acf(decomposition_2.seasonal.values, lags=50, ax = ax[4], title="Positive Mood / Seasonal")
    ax[4].set_xlabel("Lag")
    ax[4].set_ylabel("Autocorrelation")
    plot_acf(decomposition_3.seasonal.values, lags=50, ax = ax[5], title="Negative Mood / Seasonal")
    ax[5].set_xlabel("Lag")
    ax[5].set_ylabel("Autocorrelation")
    
    plot_acf(decomposition_2.resid.values, lags=50, ax = ax[6], title="Positive Mood / Residual")
    ax[6].set_xlabel("Lag")
    ax[6].set_ylabel("Autocorrelation")
    plot_acf(decomposition_3.resid.values, lags=50, ax = ax[7], title="Negative Mood / Residual")
    ax[7].set_xlabel("Lag")
    ax[7].set_ylabel("Autocorrelation")
    '''
    
    # Calculate ACF and PACF upto 50 lags / NEGATIVE MOOD
    #acf_50 = acf(decomposition_3.seasonal.values, nlags=50)
    #pacf_50 = pacf(decomposition_3.seasonal.values, nlags=50)

    # Draw Plot
    #fig, axes = plt.subplots(1,2,figsize=(16,3), dpi= 100)
    #plot_acf(decomposition_3.seasonal.values, lags=60, ax=axes[0])
    #plot_pacf(decomposition_3.seasonal.values, lags=60, ax=axes[1])
    
    #%% plot pos and negative valences
    scaled_df['Negative_negative'] = scaled_df['Negative_mood']*(-1)
    scaled_df['Valence_diff'] = scaled_df['Positive_mood'] - scaled_df['Negative_mood']
    cors = scaled_df.filter(['Positive_mood','Negative_mood']).rolling(7).corr().unstack()
    scaled_df['origin'] = 0
    
    plt.figure(figsize=(20,10))
    plt.suptitle('ESM: Negative and positive valence',y=0.98,fontsize=20)
    scaled_df['Positive_mood'].plot(style=[':'])
    scaled_df['Negative_negative'].plot(style=[':'],label="Negative_mood")
    #scaled_df['Negative_mood'].plot(style=[':'],label="Negative_mood")
    cors.iloc[:,0].plot(style=['black'],label="Correlation")
    
    '''
    scaled_df['Valence_diff'].plot(color='gray',style=[':'])
    
    plt.fill_between(scaled_df.index,scaled_df['Valence_diff'].values, 0, 
                     where=(scaled_df['Valence_diff'] < 0), alpha=0.15, color='Firebrick', interpolate=True)
    
    plt.fill_between(scaled_df.index,scaled_df['Valence_diff'].values, 0, 
                     where=(scaled_df['Valence_diff'] > 0), alpha=0.15, color='Steelblue', interpolate=True)
    '''
    scaled_df['origin'].plot(style=['--'],label='')
    plt.xlabel('Time / Days')
    plt.ylabel('Value')
    plt.legend()
    plt.show()
    
    #%%
    # set correct names and save metrics as json 
    RESPATH = Path(r'/u/26/ikaheia1/unix/Documents/SpecialAssignment/Results/Metrics/')
    RESNAME = "metrics_2.json"
    dump_to_json(res,RESPATH,RESNAME)  
    
    # save the timeseries
    TSPATH = Path(r'/u/26/ikaheia1/unix/Documents/SpecialAssignment/Results/Timeseries/')
    TSNAME = "timeseries_2.mat"
    save2mat(timeseries,TSPATH,TSNAME)        
    
    #%% Plot timeseries and save figure -> How to plot these!!!
    #FIGPATH = Path(r'/home/arsi/Documents/SpecialAssignment/Results/Plots/')
    #FIGNAME = "timeseries_2"
    #show_timeseries(resampled.index,resampled.battery_level,"ESM","time","Level",FIGPATH,FIGNAME)
    #&& how about features???
    #%% Extract features from timeseries, plot, and save
    #%% Extract features from timeseries, plot, and save
    FIGPATH = Path(r'/u/26/ikaheia1/unix/Documents/SpecialAssignment/Results/Features/')
    FIGNAME = "ESM_features"

    
    show_features(scaled_df['Positive_mood'],"Positive mood ","Time (d)","Value",7,1,"right",False,FIGPATH,FIGNAME)
    show_features(scaled_df['Negative_mood'],"Negative mood ","Time (d)","Value",7,1,"right",False,FIGPATH,FIGNAME)
    

    #%% plot some
    
    ts2_roll = ts2.rolling(7).mean()
    ts3_roll = ts3.rolling(7).mean()
    
    ts2_var = ts2.rolling(7).var()
    ts3_var = ts3.rolling(7).var()
    
    ts2_auto = ts2.rolling(7).apply(autocorr)
    ts3_auto = ts3.rolling(7).apply(autocorr)
    
    #%%
    fig = plt.figure(figsize=(13,13))
    
    plt.suptitle('ESM scores and rolling window features',fontsize=26,y=1.03)
    
    plt.subplot(4,2,1)
    ts2.plot()
    plt.axvspan(datetime(2020,7,1),datetime(2020,7,15),facecolor="red",alpha=0.15,label="Days of interest")
    plt.title('Positive mood',fontsize=20)
    plt.xlabel('')
    plt.ylabel('Score',fontsize=18)
    #plt.show()
    
    plt.subplot(4,2,2)
    ts3.plot()
    plt.axvspan(datetime(2020,7,1),datetime(2020,7,15),facecolor="red",alpha=0.15,label="Days of interest")

    plt.title('Negative mood',fontsize=20)
    plt.xlabel('')
    plt.ylabel('Score',fontsize=18)
    #plt.xticks(rotation=45)
    #plt.show()
    
    plt.subplot(4,2,3)
    ts2_roll.plot()
    plt.axvspan(datetime(2020,7,1),datetime(2020,7,15),facecolor="red",alpha=0.15,label="Days of interest")
    plt.title('Positive mood rolling(7) mean',fontsize=20)
    plt.xlabel('')
    plt.ylabel('Score',fontsize=18)
    #plt.xticks(rotation=45)
    #plt.show()
    
    plt.subplot(4,2,4)
    ts3_roll.plot()
    plt.axvspan(datetime(2020,7,1),datetime(2020,7,15),facecolor="red",alpha=0.15,label="Days of interest")
    plt.title('Negative mood rolling(7) mean',fontsize=20)
    plt.xlabel('')
    plt.ylabel('Score',fontsize=18)
    #plt.xticks(rotation=45)
    #plt.show()
    
    plt.subplot(4,2,5)
    ts2_var.plot()
    plt.axvspan(datetime(2020,7,1),datetime(2020,7,15),facecolor="red",alpha=0.15,label="Days of interest")
    plt.title('Positive mood rolling(7) variance',fontsize=20)
    plt.xlabel('')
    plt.ylabel('Variance',fontsize=18)
    #plt.xticks(rotation=45)
    #plt.show()
    
    plt.subplot(4,2,6)
    ts3_var.plot()
    plt.axvspan(datetime(2020,7,1),datetime(2020,7,15),facecolor="red",alpha=0.15,label="Days of interest")
    plt.title('Negative mood rolling(7) variance',fontsize=20)
    plt.xlabel('')
    plt.ylabel('Variance',fontsize=18)
    #plt.xticks(rotation=45)
    #plt.show()
    
    plt.subplot(4,2,7)
    ts2_auto.plot()
    plt.axvspan(datetime(2020,7,1),datetime(2020,7,15),facecolor="red",alpha=0.15,label="Days of interest")
    plt.title('Positive mood autocorrelation(1)',fontsize=20)
    plt.xlabel('Time (date)',fontsize=18)
    plt.ylabel('Autocorrelation',fontsize=18)
    #plt.xticks(rotation=45)
    #plt.show()
    
    plt.subplot(4,2,8)
    ts3_auto.plot()
    plt.axvspan(datetime(2020,7,1),datetime(2020,7,15),facecolor="red",alpha=0.15,label="Days of interest")
    plt.title('Negative mood autocorrelation(1)',fontsize=20)
    plt.xlabel('Time (date)',fontsize=18)
    plt.ylabel('Autocorrelation',fontsize=18)
    #plt.xticks(rotation=45)
    #plt.show()
    
    fig.tight_layout(pad=1.0)
    
    
    
    #%%
    return combined_df, timeseries, affections
    
if __name__ == "__main__":
    pass