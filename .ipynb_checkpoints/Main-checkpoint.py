# -*- coding: utf-8 -*-
## @namespace main_paper
# Created on Wed Feb 28 09:47:22 2018
# Author
# Alejandro Pena-Bello
# alejandro.penabello@unige.ch
# Main script used for the paper Optimization of PV-coupled battery systems for combining applications: impact of battery technology and location (Pena-Bello et al 2018 to be published).
# The study focuses on residential PV-coupled battery systems. We study the different applications which residential batteries can perform from a consumer perspective. Applications such as avoidance of PV curtailment, demand load-shifting and demand peak shaving are considered along  with the base application, PV self-consumption. Moreover, six different battery technologies currently available in the market are considered as well as three sizes (3 kWh, 7 kWh and 14 kWh). We analyze the impact of the type of demand profile and type of tariff structure by comparing results across dwellings in Switzerland and in the U.S.
# The battery schedule is optimized for every day (i.e. 24 h optimization framework), we assume perfect day-ahead forecast of the electricity demand load and solar PV generation in order to determine the maximum economic potential regardless of the forecast strategy used. Aging was treated as an exogenous parameter, calculated on daily basis and was not subject of optimization. Data with 15-minute temporal resolution were used for simulations. The model objective function have two components, the energy-based and the power-based component, as the tariff structure depends on the applications considered, a boolean parameter activate the power-based factor of the bill when is necessary.
# Every optimization was run for one year and then the results were linearly-extrapolated to reach the battery end of life. Therefore, the analysis is done with same prices for all years across battery lifetime. We assume 30\% of capacity depletion as the end of life.
# The script works in Linux and Windows
# This script works was tested with pyomo version 5.4.3
# INPUTS
# ------
# OUTPUTS
# -------
# TODO
# ----
# User Interface, including path to save the results and choose countries, load curves, etc.
# Simplify by merging select_data and load_data and probably load_param.
# Requirements
# ------------
#  Pandas, numpy, sys, glob, os, csv, pickle, functools, argparse, itertools, time, math, pyomo and multiprocessing

test=False
import os
import pandas as pd
import argparse
import numpy as np
import itertools
import sys
import glob
import multiprocessing as mp
import time
from functools import wraps
from pathlib import Path
import traceback
import csv

import post_proc as pp
def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print ("Total time running %s: %s seconds" %
               (function.__name__, str(t1-t0))
               )
        return result
    return function_timer

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)
def expand_grid(dct):
    rows = itertools.product(*dct.values())
    return pd.DataFrame.from_records(rows, columns=dct.keys())
def load_param(combinations):
    '''
    Description
    -----------
    Load all parameters into a dictionary, if aging is present (True) or not
    (False), percentage of curtailment, Inverter and Converter efficiency, time
    resolution (0.25), number of years or days if only some days want to be
    optimized, applications, capacities and technologies to optimize.

    Applications are defined as a Boolean vector, where a True activates the
    corresponding application. PVSC is assumed to be always used. The order
    is as follows: [PVCT, PVSC, DLS, DPS]
	i.e Frequency control, Avoidance of PV curtailment, PV self-consumption,
	Demand load shifting and demand peak shaving.
    [0,0,1,0,0]-0
    [0,0,1,0,1]-1
    [0,0,1,1,0]-2
    [0,0,1,1,1]-3
    [0,1,1,0,0]-4
    [0,1,1,0,1]-5
    [0,1,1,1,0]-6
    [0,1,1,1,1]-7
    [1,0,1,0,0]-8
    [1,0,1,0,1]-9
    [1,0,1,1,0]-10
    [1,0,1,1,1]-11
    [1,1,1,0,0]-12
    [1,1,1,0,1]-13
    [1,1,1,1,0]-14
    [1,1,1,1,1]-15


    Parameters
    ----------
    PV_nominal_power : int

    Returns
    ------
    param: dict
    Comments
    -----
    week 18 day 120 is transtion from cooling to heating
    week 40 day 274 is transtion from cooling to heating
    '''
    print('##############')
    print('load data')
    id_dwell=str(int(combinations['name']))
    [clusters,PV,App_comb_df]=pp.get_table_inputs()
    id_dwell=str(combinations['name'])
    print('****************')
    print(id_dwell)
    
    conf=[True,False,False,False]
    #PV_nom=PV[PV.PV==combinations['PV_nom']].PV.values[0]
    #quartile=PV[(PV.PV==combinations['PV_nom'])&(PV.country==combinations['country'])].quartile.values[0]
    App_comb=[str2bool(i) for i in App_comb_df[App_comb_df.index==int(combinations['App_comb'])].App_comb.values[0].split(' ')]
    print(App_comb)
    
    fields_el=['index',id_dwell,'E_PV','Price_flat','Price_DT','Price_flat_mod','Price_DT_mod','Export_price']
    if combinations['country']=='CH':
        Capacity_tariff=9.39*12/365
        filename=Path("../../Input/IRES_CH_all2.csv")
        df = pd.read_csv(filename,engine='python',sep=',|;',index_col=[0],
                            parse_dates=[0],infer_datetime_format=True, usecols=fields_el)
        if np.issubdtype(df.index.dtype, np.datetime64):
            df.index=df.index.tz_localize('UTC').tz_convert('Europe/Brussels')
        else:
            df.index=pd.to_datetime(df.index,utc=True)
            df.index=df.index.tz_convert('Europe/Brussels')
        #df.columns=new_cols
        
    elif combinations['country']=='US':
        Capacity_tariff=10.14*12/365
        filename=Path("../../Input/IRES_US_all.csv")
        df = pd.read_csv(filename,engine='python',sep=',|;',index_col=[0],
                            parse_dates=[0],infer_datetime_format=True, usecols=fields_el)
        if np.issubdtype(df.index.dtype, np.datetime64):
            df.index=df.index.tz_localize('UTC').tz_convert('US/Central')
        else:
            df.index=pd.to_datetime(df.index,utc=True)
            df.index=df.index.tz_convert('US/Central')+ pd.Timedelta('06:00:00')
    df=df.rename(columns={id_dwell: 'E_demand'})   
    print(df.head(2))
    PV_nom=(df.loc[:,'E_demand'].sum()/1000).round(1)  
    Capacity=PV_nom
    print('afterPV')
#####################################################
    aging=True
    Inverter_power=round(PV_nom/1.2,1)
    Curtailment=0.5
    Inverter_Efficiency=0.95
    Converter_Efficiency=0.98
    dt=0.25
    nyears=1
    days=365
    testing=False
    
    week=1
######################################################
    quartile=0
    print('PV_nom is {}, quartile is {} and App_combination is {}'.format(PV_nom,quartile,App_comb))
    ndays=days*nyears
    data_input=pd.concat([df.loc[:,'E_demand'],
                         df.loc[:,'E_PV']*PV_nom,
                         df.loc[:,'Price_flat'],df.loc[:,'Price_DT'],
                         df.loc[:,'Price_flat_mod'],
                         df.loc[:,'Price_DT_mod'],
                         df.loc[:,'Export_price']],axis=1)
    print('bf test')
    if testing:
        data_input=data_input[data_input.index.week==week]
        nyears=1
        days=7
        ndays=7
    print('bf')
    param={'conf':conf,
    'aging':aging,'Inv_power':Inverter_power,
    'Curtailment':Curtailment,'Inverter_eff':Inverter_Efficiency,
    'Converter_Efficiency_Batt':Converter_Efficiency,
    'delta_t':dt,'nyears':nyears,
    'days':days,'ndays':ndays,'Capacity':Capacity,'Tech':combinations['Tech'],  'App_comb':App_comb,'cases':combinations['cases'],'testing':testing,'name':id_dwell+'_'+combinations['country']+'_PV'+str(PV_nom),
    'PV_nom':PV_nom,'Capacity_tariff':Capacity_tariff,'Scenario':combinations['Scenario']}
    print(param)
    print('out of param')
    return param,data_input

def pooling2(combinations):
    '''
    Description
    -----------
    Calls other functions, load the data and Core_LP.
    Parameters
    ----------
    selected_dwellings : dict

    Returns
    ------
    bool
        True if successful, False otherwise.
    '''
    from Core_LP import single_opt2
    
    print('##########################################')
    print('pooling')
    print(combinations)
    print('##########################################')
    param,data_input=load_param(combinations)
    #try:
    if param['nyears']>1:
            data_input=pd.DataFrame(pd.np.tile(pd.np.array(data_input).T,
                                   param['nyears']).T,columns=data_input.columns)
    print('#############pool################')

    [df,aux_dict]=single_opt2(param,data_input)
    print('out of optimization')
    
        #    except IOError as e:
#        print ("I/O error({0}): {1}".format(e.errno, e.strerror))
#        raise

#    except :
#        print ("Back to main.")
    return

@fn_timer
def main():
    '''
    Main function of the main script. Allows the user to select the country
	(CH or US). For the moment is done automatically if working in windows
	the country is US. It opens a pool of 4 processes to process in parallel, if several dwellings are assessed.
    '''

    print(os.getcwd())
    print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
    print('Welcome to basopra')
    print('Here you will able to get the optimization of a single family house in the U.S. using a 7 kWh LFP-based battery')

    try:

        filename=Path('../../Output/aggregated_results.csv')
        if 'aggregated_results.csv' in os.listdir('../../Output/'):
            df_done=pd.read_csv(filename,sep=';|,',engine='python',index_col=None).drop_duplicates()
            aux=df_done.groupby([df_done.App_comb,df_done.Tech,df_done.name,df_done.country,df_done.cases]).size().reset_index()
        else:
            with open(filename, 'w+', newline='') as f:
                columns=['Bool_char', 'Bool_dis', 'E_PV_batt', 'E_PV_curt', 'E_PV_grid',
       'E_PV_load', 'E_char', 'E_cons', 'E_dis', 'E_grid_batt', 'E_grid_load',
       'E_loss_Batt', 'E_loss_conv', 'E_loss_inv', 'E_loss_inv_PV',
       'E_loss_inv_batt', 'E_loss_inv_grid', 'E_demand', 'E_PV',
       'Export_price', 'price', 'SOC_mean', 'SOC_max', 'SOC_min', 'DoD_mean',
       'DoD_max', 'DoD_min', 'last_cap', 'cap_fading', 'last_SOH',
       'P_max_year_batt', 'P_max_year_nbatt', 'P_drained_max',
       'P_injected_max', 'App_comb', 'Capacity', 'Tech', 'PV_nom', 'name',
       'cluster', 'country', 'quartile', 'results_PVbatt', 'results_PV',
       'results', 'EFC_nolifetime', 'LS', 'TSC', 'DSC', 'ISC', 'CU', 'PS_year',
       'BS', 'cycle_to_total', 'cases', 'Scenario']
                writer = csv.writer(f, delimiter=';')
                writer.writerow(columns)
            df_done=pd.read_csv(filename,sep=';|,',engine='python',index_col=None).drop_duplicates()
            aux=df_done.groupby([df_done.Capacity,df_done.App_comb,df_done.Tech,df_done.PV_nom,df_done.cluster,df_done.country,df_done.cases]).size().reset_index()
    except IOError:
        print("error linea 254 Main")
    finally:
        print(df_done.columns)
        dct={'App_comb':[0,1,7],'Tech':['NMC'],'country':['CH'],'cases':['mean'],'Scenario':['base'],'name':[110144756386]}#, 110145456526, 110696328892, 110145056438, 110145556546, 110141955877, 110142355945, 110143556105, 110141755846, 110145556555, 110696428978, 110142556018, 110142556015, 110141955907, 110142956059, 110696428966, 110145056441, 110143756118, 110142556012, 110141955908, 110145456529, 110142756042, 110142956062, 110141755849, 110145156462, 110141955884, 110145656570, 110696128849, 110143556103, 110696528996, 110145156456, 110696428975, 110141955910, 110143756122, 110142956056, 110142556016, 110145656567, 110141755858, 110145556537, 110143556106, 110141755828, 110141955889, 110696529037, 110143556108, 110696529024, 110145156471, 110696428987, 110142956065, 110141955911, 110142756041, 110143756126, 110141755831, 110141955899, 110696629065, 110145656579, 110145556549, 110141755860, 110143556107, 110696629055, 110143956140, 110145256495, 110142956066, 110696528990, 110142956052, 110141755832, 110142756046, 110141955901, 110141755830, 110696128842, 110141755861, 110143956150, 110144156214, 110146056594, 110696629071, 110143956143, 110143156074, 110145556534, 110142956053, 110141755834, 110143156076, 110696528993, 110141755836, 110141755862, 110141955905, 110696428972, 110696328876, 110144156225, 110144156209, 110144356271, 110696729128, 110141755829, 110143156078, 110696529030, 110141755838, 110141755863, 110142956064, 110141755837, 110143756124, 110141955909, 110696529016, 110144356270, 110696428969, 110144156211, 110144556314, 110696829164, 110144356264, 110141755844, 110141755856, 110696629062, 110143356092, 110141755839, 110141955879, 110142756043, 110144156229, 110143956145, 110696529022, 110145056447, 110696428981, 110144356274, 110696929262, 110145356516, 110141755848, 110141755857, 110144556317, 110141955878, 110141955880, 110144356269, 110141755841, 110144356267, 110696529011, 110143756116, 110144556318, 110696529044, 110145156459, 110696929272, 110141755851, 110145456522, 110141955887, 110141955898, 110144856397, 110141755845, 110696729099, 110144156205, 110144556322, 110141955882, 110696629051, 110145156468, 110144756379, 110144556313, 110697129330, 110141755855, 110696128845, 110141955906, 110141955895, 110144856399, 110141755847, 110141955885, 110145256483, 110696729119, 110144156221, 110141755840, 110144756372, 110145256492, 110697129336, 110144856404, 110141955890, 110142756044, 110141755852, 110141955897, 110696128853, 110141955902, 110145156465, 110696729133, 110142556013, 110144756376, 110144356272, 110145356508, 110145356503, 110145056435, 110697229401, 110141955891, 110142756047, 110141755854, 110142355940, 110141755833, 110141955912, 110145256480, 110696128862, 110142956063, 110144856407, 110145356511, 110144756381, 110696128837, 110145056453, 110697229432, 110141955893, 110142956058, 110141755859, 110142355944, 110141755850, 110142355943, 110145056432, 110145456520, 110145456531, 110696428960, 110143556102, 110696328886, 110144756384, 110145356505, 110697329468, 110141755835, 110145356499, 110696128835, 110697129383, 110144556316, 110141755843, 110696128856, 110696529013, 110697229396, 110144556320, 110142355939, 110696128864, 110696529027, 110141755842, 110144756374, 110142355941, 110141755853, 110696328884, 110696529040, 110144756389, 110142355942, 110696428984, 110142355947, 110144856401, 110142756045, 110142355946, 110696529047, 110144856411, 110142556017, 110142956055, 110696629073, 110145056430, 110142956057, 110696629086, 110143156075, 110145256477, 110142956061, 110696729091, 110143156077, 110145256489, 110143156073, 110696829172, 110143556104, 110145356514, 110143556101, 110696829200, 110143956137, 110145456524, 110143756120, 110143956153, 110696929206, 110145856588, 110143956148, 110144156217, 110697029296, 110146056597, 110144856395, 110144556315, 110697129333, 110146156603, 110696829179, 110698129805, 110697829679, 110697129359, 110697329461, 110696629081, 110697529565, 110696128859, 110698429916, 110696529000, 110697129362, 110696829183, 110698129812, 110697329465, 110697829690, 110697529569, 110698529920, 110696929276, 110696529004, 110696829190, 110698229816, 110697829698, 110697129366, 110696929280, 110698529926, 110697529571, 110696529007, 110697829700, 110696829194, 110698229819, 110697329472, 110697129369, 110696929283, 110696729096, 110698529930, 110696328873, 110697529574, 110696829197, 110697929712, 110697329474, 110697129372, 110698529934, 110698229823, 110696929286, 110697629584, 110697929717, 110696729103, 110697129375, 110697329477, 110696328879, 110145556543, 110698229825, 110697629587, 110698529936, 110696929290, 110696929203, 110697929723, 110697329480, 110696328882, 110696729107, 110698529939, 110697129381, 110697629595, 110698229830, 110696729111, 110697329483, 110697929727, 110698529942, 110697629599, 110697029301, 110698229835, 110697329486, 110696929209, 110696729115, 110697929733, 110698529945, 110697629603, 110697029304, 110698229838, 110696328889, 110697329488, 110696929213, 110697929735, 110698529950, 110697029308, 110697629607, 110698329851, 110696729124, 110697229406, 110696929216, 110697429491, 110697929737, 110698529953, 110697029312, 110698329854, 110697629610, 110696529033, 110696729126, 110697429495, 110696328899, 110697229408, 110696929220, 110697029314, 110698629959, 110697929745, 110698329858, 110145656576, 110697629613, 110697429498, 110696929224, 110697029318, 110697229411, 110698629962, 110698029749, 110698329861, 110697729616, 110696428963, 110697429503, 110698029755, 110698629965, 110696929228, 110697029321, 110697229419, 110698329867, 110697729619, 110696729137, 110698029760, 110698629973, 110698329871, 110697429509, 110697029326, 110697229423, 110696929232, 110697729624, 110696729140, 110698629977, 110698029765, 110697429513, 110698329876, 110697229425, 110696929236, 110697729630, 110696729145, 110698029768, 110698629981, 110697229429, 110697429516, 110698329880, 110697729634, 110696929241, 110696729150, 110698629985, 110697529529, 110698029770, 110698329884, 110697729637, 110696929245, 110696729154, 110697129340, 110698629989, 110697529533, 110698029774, 110696629058, 110697329441, 110698429896, 110697729644, 110696929249, 110696729157, 110698629992, 110697529538, 110697129344, 110698029777, 110697329444, 110698429899, 110697729648, 110696929256, 110696829161, 110697529546, 110698730003, 110697129348, 110698129789, 110697329446, 110698429902, 110696929258, 110697729654, 110698730006, 110697529550, 110696629067, 110697129350, 110698129793, 110697329450, 110698429906, 110697829664, 110698730009, 110697529557, 110697129353, 110697329454, 110698129799, 110696929265, 110698429909, 110697829670, 110698730012, 110697529561, 110696829176, 110697129356, 110698129801, 110697329456, 110696929268, 110698429912, 110697829674, 110699030128, 110698730016, 1127344129687, 110699330235, 1127341129661, 1127347129714, 1127351129754, 110699030131, 110698730035, 1127344129688, 110699330237, 1127341129662, 1127347129715, 1127351129756, 110699030135, 110699330238, 110698730039, 1127344129689, 1127341129663, 1127347129716, 1127351129757, 110699030138, 1127341129664, 110699330239, 1127344129690, 110698730043, 1127351129758, 1127347129717, 1127344129691, 110698830051, 110699030142, 1127342129667, 110699330240, 1127351129760, 1127347129719, 110698830053, 110699030146, 1127344129692, 110699330241, 1127342129668, 1127352129767, 1127347129720, 110699130150, 1127344129693, 110698830056, 110699430242, 1127348127591, 1127342129669, 1127353129781, 110699130153, 110698830059, 1127345127588, 110699430243, 1127354129797, 1127348129725, 1127342129670, 110699130162, 110698830061, 110699430245, 1127345129695, 1127348129726, 1127354129799, 1127342129671, 110698830063, 110699130166, 110699430246, 1127345129697, 1127348129729, 1127355129783, 1127342129672, 110698830065, 110699130169, 1127345129698, 110699430248, 1127355129784, 1127348129730, 1127342129673, 110699130172, 110698830067, 1127345129700, 110699430252, 1127355129786, 1127348129731, 1127342129674, 110699130179, 1127345129701, 110698830069, 110699430254, 1127349127592, 1127343129675, 1127345129702, 110699130183, 110698830071, 110699430256, 1127349129734, 1127343129676, 110699130188, 1127345129703, 110698830073, 110699430258, 1127349129735, 1127343129677, 110699130193, 1127345129704, 110698830079, 110699430260, 1127349129736, 1127343129678, 110699130197, 1127345129705, 110698930092, 1127349129739, 110699430262, 1127343129679, 110699230205, 110698930096, 1127346127589, 1127349129743, 110699430264, 1127343129680, 110699230217, 110698930100, 1127350127593, 1127346129706, 1127341129655, 1127343129681, 110699230221, 1127350129746, 110698930104, 1127346129707, 1127341129656, 1127343129682, 110699230224, 110698930108, 1127346129708, 1127350129747, 1127341129657, 1127343129683, 110699230227, 110698930113, 1127346129709, 1127351127594, 1127341129658, 1127344127587, 110699230230, 110698930117, 1127346129710, 1127341129659, 1127351129752, 1127344129685, 110699230232, 110699030125, 1127346129712, 1127351129753, 1127341129660, 1127344129686]}
        #dct={'App_comb':[0,1,7],'Tech':['NMC'],'country':['US'],'cases':['mean'],'Scenario':['base'],'name':[ 180, 325, 270, 397, 300, 33, 377, 349, 123, 156, 209, 242, 1, 98, 66, 399, 378, 126, 350, 157, 211, 301, 35, 181, 2, 274, 67, 101, 326, 244, 379, 212, 351, 400, 302, 36, 159, 129, 185, 3, 68, 103, 327, 277, 246, 380, 304, 186, 39, 213, 104, 354, 401, 130, 4, 160, 69, 247, 328, 282, 381, 188, 307, 40, 215, 105, 355, 70, 403, 283, 5, 329, 161, 248, 132, 382, 191, 42, 309, 356, 106, 216, 74, 284, 133, 9, 330, 163, 253, 405, 383, 312, 43, 359, 108, 192, 217, 75, 286, 134, 11, 406, 255, 164, 331, 384, 314, 48, 362, 110, 194, 218, 287, 136, 12, 77, 414, 257, 166, 332, 386, 316, 49, 363, 197, 289, 111, 219, 142, 415, 79, 14, 259, 167, 334, 387, 317, 52, 199, 364, 290, 224, 417, 113, 81, 143, 15, 168, 260, 336, 388, 53, 319, 200, 367, 292, 226, 418, 115, 85, 18, 144, 171, 262, 339, 390, 54, 371, 201, 87, 320, 116, 228, 423, 293, 19, 173, 146, 263, 340, 391, 55, 372, 203, 118, 321, 90, 424, 231, 294, 23, 147, 175, 265, 341, 393, 59, 373, 204, 238, 91, 322, 295, 119, 425, 26, 150, 266, 343, 178, 394, 374, 61, 239, 93, 426, 297, 206, 120, 323, 153, 27, 267, 344, 179, 396, 376, 241, 431, 63, 298, 95, 122, 208, 155, 324, 31, 268, 432, 462, 493, 551, 528, 433, 464, 552, 494, 531, 438, 466, 554, 496, 533, 439, 470, 557, 500, 536, 441, 471, 502, 537, 443, 473, 510, 538, 446, 475, 513, 539, 449, 476, 514, 541, 450, 477, 515, 542, 451, 517, 480, 543, 452, 519, 482, 544, 453, 520, 483, 545, 454, 484, 521, 546, 455, 488, 522, 547, 458, 492, 523, 548, 460, 525, 549]}
        

        Total_combs=expand_grid(dct)
        print(df_done.head())
        print(aux.head())

        Combs_todo=aux.merge(Total_combs,how='outer',indicator=True)#Warning

        Combs_todo=Combs_todo[Combs_todo['_merge']=='right_only']
        Combs_todo=Combs_todo.loc[:,Combs_todo.columns[:-1]]
        print(Combs_todo)
        Combs_todo=Combs_todo.dropna(axis=1)
        Combs_todo=[dict(Combs_todo.loc[i,:]) for i in Combs_todo.index]
        print(len(Combs_todo))
        if test:
            Combs_todo=Combs_todo[0]
        print(len(Combs_todo))
        mp.freeze_support()
        pool=mp.Pool(processes=1)
        #selected_dwellings=select_data(Combs_todo)
        #print(selected_dwellings)
        #print(Combs_todo)
        pool.map(pooling2,Combs_todo)
        pool.close()
        pool.join()
        print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')

if __name__== '__main__':
    main()
