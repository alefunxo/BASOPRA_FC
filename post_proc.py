#!/usr/bin/python3
# -*- coding: utf-8 -*-
## @namespace Core_LP
# Created on Tue Oct 31 11:11:33 2017
# Author
# Alejandro Pena-Bello
# alejandro.penabello@unige.ch
# Description
# -----------
# INPUTS
# ------
# OUTPUTS
# -------
# TODO
# ----
# Generalize for the different configurations including HP
# Requirements
# ------------
# Pandas, numpy, itertools, os

import os
import pandas as pd
import numpy as np
import itertools

def get_table_inputs():
    clusters=pd.read_csv('/data/home/alejandropena/P4/Sept_2021/Input/clusters.csv',index_col=[0])
    aux=pd.DataFrame()
    print('inside table 2')
    for i in range(9):
            aux=aux.append(clusters.loc[(clusters.country=='CH')&(clusters.cluster==i)][:(min(30,clusters.loc[(clusters.country=='CH')&(clusters.cluster==i),'name'].size))])


    PV=[{'PV':3.2,'quartile':25,'country':'US'},
        {'PV':5,'quartile':50,'country':'US'},
        {'PV':6.4,'quartile':75,'country':'US'},
        {'PV':3.2,'quartile':25,'country':'CH'},
        {'PV':4.8,'quartile':50,'country':'CH'},
        {'PV':6.9,'quartile':75,'country':'CH'}]
    PV=pd.DataFrame(PV)
    

    App_comb_scenarios=np.array([i for i in itertools.product([False, True],repeat=4)])
    App_comb_scenarios=np.insert(App_comb_scenarios,slice(2,3),True,axis=1)
    App_comb=pd.DataFrame(App_comb_scenarios)
    App_comb=App_comb[0].map(str)+' '+App_comb[1].map(str)+' '+App_comb[2].map(
                    str)+' '+App_comb[3].map(str)+' '+App_comb[4].map(str)
    App_comb=App_comb.reset_index()

    App_comb=App_comb.rename(columns={'index':'App_index',0:'App_comb'})
    conf_scenarios=np.array([i for i in itertools.product([False, True],repeat=3)])
    conf_scenarios=np.insert(conf_scenarios,slice(1,2),True,axis=1)
    conf=pd.DataFrame(conf_scenarios)
    conf=conf[0].map(str)+' '+conf[1].map(str)+' '+conf[2].map(
                    str)+' '+conf[3].map(str)
    conf=conf.reset_index()
    conf=conf.rename(columns={'index':'conf_index',0:'conf'})
    
    house_types=pd.DataFrame(np.array(['SFH100','SFH45','SFH15']),columns=['House_type'])
    hp_types=pd.DataFrame(np.array(['GSHP','ASHP']),columns=['HP_type'])
    rad_types=pd.DataFrame(np.array(['under','rad']),columns=['Rad_type'])
    aux=aux.rename(columns={'name':'hh'}).reset_index()
    
    return[aux,PV,App_comb]    

# def get_table_inputs():
#     clusters=pd.read_csv('../../Input/clusters.csv',index_col=[0])
#     aux=pd.DataFrame()

#     for i in range(9):
#             aux=aux.append(clusters.loc[(clusters.country=='CH')&(clusters.cluster==i)][:(min(30,clusters.loc[(clusters.country=='CH')&(clusters.cluster==i),'name'].size))])


#     PV=[{'PV':3.2,'quartile':25,'country':'US'},
#         {'PV':5,'quartile':50,'country':'US'},
#         {'PV':6.4,'quartile':75,'country':'US'},
#         {'PV':3.2,'quartile':25,'country':'CH'},
#         {'PV':4.8,'quartile':50,'country':'CH'},
#         {'PV':6.9,'quartile':75,'country':'CH'}]
#     PV=pd.DataFrame(PV)


#     App_comb_scenarios=np.array([i for i in itertools.product([False, True],repeat=3)])
#     App_comb_scenarios=np.insert(App_comb_scenarios,slice(1,2),True,axis=1)
#     App_comb=pd.DataFrame(App_comb_scenarios)
#     App_comb=App_comb[0].map(str)+' '+App_comb[1].map(str)+' '+App_comb[2].map(
#                     str)+' '+App_comb[3].map(str)
#     App_comb=App_comb.reset_index()
#     App_comb=App_comb.rename(columns={'index':'App_index',0:'App_comb'})
#     conf_scenarios=np.array([i for i in itertools.product([False, True],repeat=3)])
#     conf_scenarios=np.insert(conf_scenarios,slice(1,2),True,axis=1)
#     conf=pd.DataFrame(conf_scenarios)
#     conf=conf[0].map(str)+' '+conf[1].map(str)+' '+conf[2].map(
#                     str)+' '+conf[3].map(str)
#     conf=conf.reset_index()
#     conf=conf.rename(columns={'index':'conf_index',0:'conf'})

#     house_types=pd.DataFrame(np.array(['SFH100','SFH45','SFH15']),columns=['House_type'])
#     hp_types=pd.DataFrame(np.array(['GSHP','ASHP']),columns=['HP_type'])
#     rad_types=pd.DataFrame(np.array(['under','rad']),columns=['Rad_type'])
#     aux=aux.rename(columns={'name':'hh'}).reset_index()
#     return[aux,PV,App_comb]
def get_table_inputs2():
    dwellings_US=np.array(['79', '466', '1', '539', '161', '122', '325', '327',
                    '538','403', '204', '164'])
    dwellings_CH=np.array(['110141955911' ,'1127347129716', '110698529950',
                       '1127343129682', '110699130179', '110696328886',
                       '110145356508', '110144156211', '110697229401',
                       '110697029296', '110698730039','110144756389'])
    country=np.hstack((np.tile('CH',12),np.tile('US',12)))
    cluster=np.tile(np.arange(0,12),2)
    clusters={'hh':np.hstack((dwellings_CH,dwellings_US)),'country':country,
              'cluster':cluster}
    clusters=pd.DataFrame(clusters)
    PV=[{'PV':3.2,'quartile':25,'country':'US'},
        {'PV':5,'quartile':50,'country':'US'},
        {'PV':6.4,'quartile':75,'country':'US'},
        {'PV':3.2,'quartile':25,'country':'CH'},
        {'PV':4.8,'quartile':50,'country':'CH'},
        {'PV':6.9,'quartile':75,'country':'CH'}]
    PV=pd.DataFrame(PV)
    App_comb_scenarios=np.array([i for i in itertools.product([False, True],repeat=3)])
    App_comb_scenarios=np.insert(App_comb_scenarios,slice(1,2),True,axis=1)
    App_comb=pd.DataFrame(App_comb_scenarios)
    App_comb=App_comb[0].map(str)+' '+App_comb[1].map(str)+' '+App_comb[2].map(
                    str)+' '+App_comb[3].map(str)
    App_comb=App_comb.reset_index()
    App_comb=App_comb.rename(columns={'index':'App_index',0:'App_comb'})
    clusters.hh=clusters.hh.astype(float)
    return[clusters,PV,App_comb]

def get_prices_FC(country,App_comb,PV_nom,df_base,df_batt,dt,curtailment):
    print("FC Prices")
    
    if country=='US':
        Capacity_tariff=10.14
    else:
        Capacity_tariff=9.39
    df_base['rem_load']=(df_base.loc[:,'E_demand']-df_base.loc[:,'E_PV'])
    df_base['surplus']=-df_base['rem_load']
    df_base.rem_load[df_base.rem_load<0]=0
    df_base.surplus[df_base.surplus>PV_nom/(1/dt*1.2)]=PV_nom/(1/dt*1.2)
    df_base.surplus[df_base.surplus<0]=0
    df_base['curt']=df_base.E_PV*0
    bill_power=0
    bill_power_PV=0
    bill_power_batt=0
    if App_comb[1]:
        df_base.curt[df_base.surplus>PV_nom*curtailment*dt]=df_base.surplus[df_base.surplus>PV_nom*curtailment*dt]-PV_nom*curtailment*dt
        df_base.curt[df_base.curt<0]=0
    if App_comb[4]:
        
        P_max_month_PV=df_base.groupby([df_base.index.month]).max().loc[:,['rem_load','surplus']].max(axis=1)/dt       
        bill_power_PV=P_max_month_PV*Capacity_tariff
        P_max_month=df_base.groupby([df_base.index.month]).E_demand.max()/dt
        bill_power=P_max_month_PV*Capacity_tariff
        P_max_month_batt=df_batt.groupby([df_batt.index.month]).max().loc[:,['E_cons','E_PV_grid']].max(axis=1)/dt
        bill_power_batt=P_max_month_batt*Capacity_tariff



    bill_energy_min_PV=df_base.rem_load*df_base.price
    bill_energy_day_PV=bill_energy_min_PV.groupby([df_base.index.month, df_base.index.day]).sum()

    bill_energy_min=df_base.E_demand*df_base.price
    bill_energy_day=bill_energy_min.groupby([df_base.index.month, df_base.index.day]).sum()

    exported_energy=(df_base.surplus-df_base.curt)*df_base.Export_price
    exported_energy_day=exported_energy.groupby([df_base.index.month, df_base.index.day]).sum()
    exported_energy_day_batt=df_batt.E_PV_grid*df_batt.Export_price
    bill_PV=bill_energy_day_PV-exported_energy_day#+bill_power_PV
    bill=bill_energy_day#+bill_power
    bill_batt=(df_batt.E_cons*df_batt.price-exported_energy_day_batt).groupby([df_batt.index.month, df_base.index.day]).sum()
    bill=(bill.unstack().sum(axis=1)+bill_power).reset_index(drop=True)
    bill_PV=(bill_PV.unstack().sum(axis=1)+bill_power_PV).reset_index(drop=True)
    bill_batt=(bill_batt.unstack().sum(axis=1)+bill_power_batt).reset_index(drop=True)
    if App_comb[0]:
        exported_energy_day_batt=exported_energy_day_batt+df_batt.E_dis_FC*0.95#inv eff
        bill_batt=(df_batt.E_cons*df_batt.price-exported_energy_day_batt).groupby([df_batt.index.month, df_base.index.day]).sum()
        bill_batt=(bill_batt.unstack().sum(axis=1)+bill_power_batt).reset_index(drop=True)
        bill_FC=df_batt.E_grid_batt_FC*df_batt.FC_price_down+df_batt.FC_price_up*df_batt.E_dis_FC*0.95
        bill_FC=bill_FC.groupby([df_batt.index.month, df_base.index.day]).sum().unstack().sum(axis=1).reset_index(drop=True)
        print(bill_batt)
        print(bill_FC)
        bill_batt=bill_batt-bill_FC
        print(bill_batt)
    return [bill,bill_PV,bill_batt,bill_FC]
def get_base_prices(country,App_comb,PV_nom,df_base,df_batt,dt,curtailment):
    print("Base Prices")
    
    if country=='US':
        Capacity_tariff=10.14
    else:
        Capacity_tariff=9.39
    df_base['rem_load']=(df_base.loc[:,'E_demand']-df_base.loc[:,'E_PV'])
    df_base['surplus']=-df_base['rem_load']
    df_base.rem_load[df_base.rem_load<0]=0
    df_base.surplus[df_base.surplus>PV_nom/(1/dt*1.2)]=PV_nom/(1/dt*1.2)
    df_base.surplus[df_base.surplus<0]=0
    df_base['curt']=df_base.E_PV*0
    bill_power=0
    bill_power_PV=0
    bill_power_batt=0
    if App_comb[1]:
        df_base.curt[df_base.surplus>PV_nom*curtailment*dt]=df_base.surplus[df_base.surplus>PV_nom*curtailment*dt]-PV_nom*curtailment*dt
        df_base.curt[df_base.curt<0]=0
    if App_comb[4]:
        
        P_max_month_PV=df_base.groupby([df_base.index.month]).max().loc[:,['rem_load','surplus']].max(axis=1)/dt       
        bill_power_PV=P_max_month_PV*Capacity_tariff
        P_max_month=df_base.groupby([df_base.index.month]).E_demand.max()/dt
        bill_power=P_max_month_PV*Capacity_tariff
        P_max_month_batt=df_batt.groupby([df_batt.index.month]).max().loc[:,['E_cons','E_PV_grid']].max(axis=1)/dt
        bill_power_batt=P_max_month_batt*Capacity_tariff



    bill_energy_min_PV=df_base.rem_load*df_base.price
    bill_energy_day_PV=bill_energy_min_PV.groupby([df_base.index.month, df_base.index.day]).sum()

    bill_energy_min=df_base.E_demand*df_base.price
    bill_energy_day=bill_energy_min.groupby([df_base.index.month, df_base.index.day]).sum()

    exported_energy=(df_base.surplus-df_base.curt)*df_base.Export_price
    exported_energy_day=exported_energy.groupby([df_base.index.month, df_base.index.day]).sum()
    exported_energy_day_batt=df_batt.E_PV_grid*df_batt.Export_price
    bill_PV=bill_energy_day_PV-exported_energy_day#+bill_power_PV
    bill=bill_energy_day#+bill_power
    bill_batt=(df_batt.E_cons*df_batt.price-exported_energy_day_batt).groupby([df_batt.index.month, df_base.index.day]).sum()
    bill=(bill.unstack().sum(axis=1)+bill_power).reset_index(drop=True)
    bill_PV=(bill_PV.unstack().sum(axis=1)+bill_power_PV).reset_index(drop=True)
    bill_batt=(bill_batt.unstack().sum(axis=1)+bill_power_batt).reset_index(drop=True)
            
    return [bill,bill_PV,bill_batt]
def get_main_results(dict_res,clusters,PV,App):
    """
    We are interested on some results such as
    %SC
    %DSC
    %BS
    EFC

    We want to know %PS,%LS,%CU,%PVSC per year.
    """
    print('Main results')
    dt=dict_res['delta_t']
    curtailment=dict_res['Curtailment']
    df=dict_res['df']
    #print(df)

    df=df.apply(pd.to_numeric, errors='ignore')
    agg_results=df.sum()
    

    agg_results=agg_results.drop(['SOC','Inv_P','Conv_P'])
    agg_results['SOC_mean']=df['SOC'].mean()/dict_res['Capacity']*100
    agg_results['SOC_max']=df['SOC'].max()/dict_res['Capacity']*100
    agg_results['SOC_min']=df['SOC'].min()/dict_res['Capacity']*100
    agg_results['DoD_mean']=dict_res['DoD'].mean()*100
    agg_results['DoD_max']=dict_res['DoD'].max()*100
    agg_results['DoD_min']=dict_res['DoD'].min()*100
    agg_results['DoD_min']=dict_res['DoD'].min()*100
    agg_results['last_cap']=dict_res['Cap_arr'][-1]
    agg_results['cap_fading']=(1-dict_res['Cap_arr'][-1]/
               dict_res['Capacity'])*100

    agg_results['last_SOH']=dict_res['SOH'][-1]
    agg_results['P_max_year_batt']=dict_res['P_max'].max()
    agg_results['P_max_year_nbatt']=df['E_demand'].max()/dt
    agg_results['P_drained_max']=df['E_cons'].max()/dt
    agg_results['P_injected_max']=df['E_PV_grid'].max()/dt
    
    if isinstance(dict_res['App_comb'], np.ndarray):
        print('is np')
        App_=App.App_index[App.App_comb==str(dict_res['App_comb'])[1:-1].replace("  "," ").strip()].values
        agg_results['App_comb']=App_[0]
    elif isinstance(dict_res['App_comb'], list):
        print('is list')
        App_=App.App_index[App.App_comb==str(dict_res['App_comb'])[1:-1].replace("  "," ").replace(',','')].values
        agg_results['App_comb']=App_[0]
    
    agg_results['Capacity']=dict_res['Capacity']

    
    agg_results['Tech']=dict_res['Tech']
    agg_results['PV_nom']=dict_res['PV_nom']
    
    agg_results['name']=dict_res['name'].split('_')[0]
    
    agg_results['cluster']=[]#clusters[clusters.hh==int(dict_res['name'].split('_')[0])].cluster.values
    
    agg_results['country']='CH'
    agg_results['quartile']=PV[(PV.PV==dict_res['PV_nom'])&
               (PV.country==dict_res['name'].split('_')[1])].quartile.values
   
    df_base=df.loc[:,['E_demand','E_PV','Export_price','price']]
    [base_bill,base_bill_PV,bill_batt,bill_FC]=get_prices_FC(dict_res['name'].split('_')[1],dict_res['App_comb'],dict_res['PV_nom'],df_base,df,dt,curtailment)
    #[base_bill,base_bill_PV,bill_batt]=get_prices_FC(dict_res['name'].split('_')[1],dict_res['App_comb'],dict_res['PV_nom'],df_base,df.loc[:,['E_PV_grid','E_cons','price','Export_price']],dt,curtailment)

    agg_results['results_PVbatt']=bill_batt.sum()
    agg_results['results_PV']=base_bill_PV.sum()
    agg_results['results']=base_bill.sum()
    agg_results['results_FC']=bill_FC.sum()
    
    sum_results=df.groupby([df.index.month]).sum().reset_index(drop=True)
    if dict_res['name'].split('_')[1]=='CH':
        date=pd.date_range(start='2017-01-01 00:00:00',end='2017-12-31 23:50:00',freq='1d',tz='Europe/Brussels')
    else:
        date=pd.date_range(start='2017-01-01 00:00:00',end='2017-12-31 23:50:00',freq='1d',tz='US/Central')
    print('bf')    
    aux=pd.DataFrame(np.vstack((dict_res['results'],dict_res['P_max'],
                            dict_res['DoD'],dict_res['cycle_cal_arr'])).T,
                            columns=['results_PVbatt','P_max','DoD',
                            'cycle_cal_arr']).set_index(date)
    print('af')
    agg_results['EFC_nolifetime']=(agg_results.E_dis)/dict_res['Capacity']
    
    if (App_==0) or (App_==1) or (App_==4) or (App_==5):
        agg_results['LS']=0
    else:
        if dict_res['name'].split('_')[1]=='US':
            cons=df.E_cons[df.price==df.price.max()].groupby(
                    df.E_cons[df.price==df.price.max()].index.month).sum()
            cons.index=cons.index-1
            rem=df.E_demand[df.price==df.price.max()].groupby(
                    df.E_demand[df.price==df.price.max()].index.month).sum()
            rem.index=rem.index-1
        else:
            cons=df.E_cons[df.price==df.price.max()].groupby(
                    df.E_cons[df.price==df.price.max()].index.month).sum().reset_index(drop=True)
            rem=df.E_demand[df.price==df.price.max()].groupby(
                    df.E_demand[df.price==df.price.max()].index.month).sum().reset_index(drop=True)
        agg_results['LS']=(1-cons.sum()/rem.sum())*100
    agg_results['TSC']=(agg_results.E_PV_load+agg_results.E_PV_batt)/agg_results.E_PV*100#[%]
    agg_results['DSC']=(agg_results.E_PV_load)/agg_results.E_PV*100#[%]
    agg_results['ISC']=(agg_results.E_PV_batt)/agg_results.E_PV*100#[%]
    agg_results['CU']=(agg_results.E_PV_curt)/agg_results.E_PV*100#[%]
    if (App_==0) or (App_==2) or (App_==4) or (App_==6):
        agg_results['PS_year']=0
    else:
        agg_results['PS_year']=(agg_results['P_max_year_batt']-agg_results[
                    'P_max_year_nbatt'])/agg_results['P_max_year_nbatt']*100

    agg_results['BS']=(agg_results.E_dis)/agg_results.E_demand*100#[%]
    agg_results['cycle_to_total']=dict_res['cycle_cal_arr'].sum()/len(dict_res['results'])
    agg_results['cases']=dict_res['cases']
    print(dict_res.keys())
    agg_results['Scenario']=dict_res['Scenario']
    agg_results['price']=agg_results['price']
    agg_results['Export_price']=agg_results['Export_price']
    agg_results['FC_div']=dict_res['FC_div']
                                  
    #print(agg_results)
    return[agg_results]