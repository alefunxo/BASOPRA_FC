#!/usr/bin/python3
# -*- coding: utf-8 -*-
## @namespace Core_LP
# Created on Tue Oct 31 11:11:33 2017
# Author
# Alejandro Pena-Bello
# alejandro.penabello@unige.ch
# script used for the paper Optimization of PV-coupled battery systems for combining applications: impact of battery technology and location (Pena-Bello et al 2018 to be published).
# This script prepares the input for the LP algorithm and get the output in a dataframe, finally it saves the output.
# Description
# -----------
# INPUTS
# ------
# OUTPUTS
# -------
# TODO
# ----
# User Interface, including path to save the results and choose countries, load curves, etc.
# Requirements
# ------------
# Pandas, numpy, pyomo, pickle, math, sys,glob, time

import pandas as pd
import paper_classes as pc
from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition
from pyomo.core import Var
import time
import numpy as np
import LP as optim
import math
import pickle
import sys
import glob
from functools import wraps
import csv
import os
import tempfile
import post_proc as pp
import matplotlib.pyplot as plt
import threading

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

def Get_output(instance):
    '''
    Gets the model output and transforms it into a pandas dataframe
	with the desired names.
    Parameters
    ----------
    instance : instance of pyomo
    Returns
    -------
    df : DataFrame
    P_max_ : vector of daily maximum power
    '''
    #to write in a csv goes faster than actualize a df
    global_lock = threading.Lock()
    while global_lock.locked():
        continue
    global_lock.acquire()
    np.random.seed()
    filename='out'+str(np.random.randint(1, 10, 10))[1:-1].replace(" ", "")+'.csv'
    with open(filename, 'a') as f:
        writer = csv.writer(f, delimiter=';')
        for v in instance.component_objects(Var, active=True):
          varobject = getattr(instance, str(v))
          for index in varobject:
              if str(v) =='P_max_day':
                  P_max_=(v[index].value)
              else:
                  writer.writerow([index, varobject[index].value, v])
    df=pd.read_csv(filename,sep=';',names=['val','var'])
    os.remove(filename)
    global_lock.release()
    df=df.pivot_table(values='val', columns='var',index=df.index)
    df=df.drop(-1)
    #print(filename)
    return [df,P_max_]
@fn_timer
def Optimize(data_input,param):
    """
    This function calls the LP and controls the aging. The aging is then
    calculated in daily basis and the capacity updated. When the battery
    reaches the EoL the loop breaks. 'days' allows to optimize multiple days at once.

    Parameters
    ----------
    Capacity : float
    Tech : string
    App_comb : array
    Capacity_tariff : float
    data_input: DataFrame
    param: dict
    PV_nom: float

    Returns
    -------
    df : DataFrame
    aux_Cap_arr : array
    SOH_arr : array
    Cycle_aging_factor : array
    P_max_arr : array
    results_arr : array
    cycle_cal_arr : array
    DoD_arr : array
    """

    days=1
    dt=param['delta_t']
    end_d=int(param['ndays']*24/dt)
    window=int(24*days/dt)
    print('%%%%%%%%% Optimizing %%%%%%%%%%%%%%%')
    if param['cases']==False:
        Batt=pc.Battery_tech(Capacity=param['Capacity'],Technology=param['Tech'])
        #print('###############')
        #print('Battery tech')
        #print(Batt.Technology)
        #print(Batt.Efficiency)
    else:
        Batt=pc.Battery_case(Capacity=param['Capacity'],Technology=param['Tech'],case=param['cases'])
        #print('###############')
        #print('Battery case')
        #print(Batt.Technology)
        #print(Batt.case)
        #print(Batt.Efficiency)
    aux_Cap_arr=np.zeros(param['ndays'])
    SOC_max_arr=np.zeros(param['ndays'])
    SOH_arr=np.zeros(param['ndays'])
    P_max_arr=np.zeros(param['ndays'])
    cycle_cal_arr=np.zeros(param['ndays'])
    results_arr=[]
    DoD_arr=np.zeros(param['ndays'])
    aux_Cap=Batt.Capacity
    SOC_max_=Batt.SOC_max
    SOH_aux=1
    for i in range(int(param['ndays']/days)):
        print(i, end='')
        if i==0:
            aux_Cap_aged=Batt.Capacity
            aux_SOC_max=Batt.SOC_max
            SOH=1
        else:
            aux_Cap_aged=aux_Cap
            aux_SOC_max=SOC_max_
            SOH=SOH_aux
        data_input_=data_input[data_input.index.dayofyear==data_input.index.dayofyear[0]+i]
        if param['App_comb'][3]==True:#DLS
            if param['App_comb'][4]==True:#DPS
                retail_price_dict=dict(enumerate(data_input_.Price_DT_mod))
            else:
                retail_price_dict=dict(enumerate(data_input_.Price_DT))
        else:
            if param['App_comb'][4]==True:
                retail_price_dict=dict(enumerate(data_input_.Price_flat_mod))
            else:
                retail_price_dict=dict(enumerate(data_input_.Price_flat))
        for col in data_input_.keys():
            param.update({col:dict(enumerate(data_input_[col]))})
        Set_declare=np.arange(-1,data_input_.shape[0])
        #if i==0:
#         print(param['FC_price_up'])
       
        
        param.update({'dayofyear':data_input.index.dayofyear[0]+i,
                      'SOC_max':aux_SOC_max,
    		'Batt':Batt,
    		'Set_declare':Set_declare,
    		'retail_price':retail_price_dict,
    		'App_comb_mod':dict(enumerate(param['App_comb']))})
            #Max_inj is in kW
        param['Max_inj']=param['Curtailment']*param['PV_nom']
        #print(param)
        #print(data_input.Export_price)
        global_lock = threading.Lock()
        while global_lock.locked():
            continue
        global_lock.acquire()
        instance = optim.Concrete_model(param)
        if sys.platform=='win32':
            opt = SolverFactory('cplex')
            opt.options["threads"]=1
            opt.options["mipgap"]=0.01
            opt.options["TimeLimit"] = 30
        else:
            opt = SolverFactory('cplex',executable='/opt/ibm/ILOG/'
                            'CPLEX_Studio1271/cplex/bin/x86-64_linux/cplex')
            opt.options["threads"]=1
            opt.options["mipgap"]=0.01
            opt.options["TimeLimit"] = 30
        results = opt.solve(instance,tee=True)
        global_lock.release()
        #results.write(num=1)

        if (results.solver.status == SolverStatus.ok) :#and (results.solver.termination_condition == TerminationCondition.optimal):#if more than 30s then it is not optimal, but still useful

        # Do something when the solution is optimal and feasible
            print('enter normally')
            [df_1,P_max]=Get_output(instance)
            if param['aging']:
                [SOC_max_,aux_Cap,SOH_aux,Cycle_aging_factor,cycle_cal,DoD]=aging_day(
                df_1.E_char+df_1.E_char_FC,SOH,Batt.SOC_min,Batt,aux_Cap_aged)
                DoD_arr[i]=DoD
                cycle_cal_arr[i]=cycle_cal
                P_max_arr[i]=P_max
                aux_Cap_arr[i]=aux_Cap
                SOC_max_arr[i]=SOC_max_
                SOH_arr[i]=SOH_aux
            else:
                DoD_arr[i]=(df_1.E_dis+df_1.E_dis_FC).sum()/Batt.Capacity
                cycle_cal_arr[i]=0
                P_max_arr[i]=P_max
                aux_Cap_arr[i]=aux_Cap
                SOC_max_arr[i]=SOC_max_
                SOH_arr[i]=SOH_aux
                Cycle_aging_factor=0
            results_arr.append(instance.total_cost())
            if i==0:#initialize
                df=pd.DataFrame(df_1)
            elif i==param['ndays']-1:#if we go until the end of the days
                df=df.append(df_1,ignore_index=True)
                if SOH<=0:
                    break
                if param['ndays']/365>Batt.Battery_cal_life:
                    break
            else:#if SOH or ndays are greater than the limit
                df=df.append(df_1,ignore_index=True)
                if SOH<=0:
                    df=df.append(df_1,ignore_index=True)
                    end_d=df.shape[0]
                    break
                if i/365>Batt.Battery_cal_life:
                    df=df.append(df_1,ignore_index=True)
                    break
        elif (results.solver.termination_condition == TerminationCondition.infeasible):
            results.write(num=1)
            # Do something when model is infeasible
            print('Termination condition',results.solver.termination_condition)
            return (None,None,None,None,None,None,None,None,results)
        else:
            results.write(num=1)
            # Something else is wrong
            print ('Solver Status is here: ',  results.solver.status)
            return (None,None,None,None,None,None,None,None,results)
    end_d=df.shape[0]
    df=pd.concat([df,data_input.loc[data_input.index[:end_d],['E_demand','E_PV','Export_price']].reset_index()],axis=1)
    if param['App_comb'][3]==True:#DLS
        if param['App_comb'][4]==True:#DPS
            print('DLS and DPS')
            df['price']=data_input.Price_DT_mod.reset_index(drop=True)[:end_d].values
        else:
            print('DLS')
            df['price']=data_input.Price_DT.reset_index(drop=True)[:end_d].values
    else:
        if param['App_comb'][4]==True:
            print('DPS')
            df['price']=data_input.Price_flat_mod.reset_index(drop=True)[:end_d].values
        else:
            print('No DLS nor DPS')
            df['price']=data_input.Price_flat.reset_index(drop=True)[:end_d].values
    if param['App_comb'][0]==True:#FC
            print('FC')
            df['FC_price_down']=data_input.FC_price_down.reset_index(drop=True)[:end_d].values
            df['FC_price_up']=data_input.FC_price_up.reset_index(drop=True)[:end_d].values
            #df['FC_activation_up']=data_input.FC_activation_up.reset_index(drop=True)[:end_d].values
            #df['FC_activation_down']=data_input.FC_activation_down.reset_index(drop=True)[:end_d].values
    
    df['Inv_P']=((df.E_PV_load+df.E_dis+df.E_PV_grid+df.E_loss_inv+df.E_dis_FC)/dt)
    
    df['Conv_P']=((df.E_PV_load+df.E_PV_batt+df.E_PV_grid+df.E_PV_batt_FC
                  +df.E_loss_conv)/dt)
    
    print(df.head())
    df.set_index('index',inplace=True)
    print('bf aux_dict')
    aux_dict={'aux_Cap_arr':aux_Cap_arr,'SOH_arr':SOH_arr,'Cycle_aging_factor':Cycle_aging_factor,'P_max_arr':P_max_arr,
              'results_arr':results_arr,'cycle_cal_arr':cycle_cal_arr,'DoD_arr':DoD_arr,'results':results}
    print('af aux dict')
    return (df,aux_dict)
def get_cycle_aging(DoD,Technology):
    '''
    The cycle aging factors are defined for each technology according
	to the DoD using an exponential function close to the Woehler curve.
    Parameters
    ----------
    DoD : float
    Technology : string

    Returns
    -------
    Cycle_aging_factor : float
    '''
    if Technology=='LTO':#Xalt 60Ah LTO Model F920-0006
        Cycle_aging_factor=1/(math.exp((math.log(DoD)-math.log(771.51))/-0.604)-45300)#R2=.9977
    elif Technology=='LFP':#https://doi.org/10.1016/j.apenergy.2013.09.003
        Cycle_aging_factor=1/(math.exp((math.log(DoD)-math.log(70.869))/-0.54)+1961.37135)#R2=.917
    elif Technology=='NCA':#Saft Evolion
        #Cycle_aging_factor=1/(math.exp((math.log(DoD)-math.log(1216.7))/-0.869)-289.736058)#R2=.9675 SAFT
        Cycle_aging_factor=1/(math.exp((math.log(DoD)-math.log(1216.7))/-0.869)+4449.67011)#TRINA BESS
    elif Technology=='NMC':#Tesla Truong et al. 2016
        Cycle_aging_factor=1/(math.exp((math.log(DoD)-math.log(1E8))/-2.168))
    elif Technology=='ALA':#Sacred sun FCP-1000 lead carbon
        Cycle_aging_factor=1/(math.exp((math.log(DoD)-math.log(37403))/-1.306)+330.656417)#R2=.9983
    elif Technology=='VRLA':#Sonnenschein
        Cycle_aging_factor=1/(math.exp((math.log(DoD)-math.log(667.61))/-.988))#R2=0.99995
    elif Technology=='test':
        Cycle_aging_factor=1/(math.exp((math.log(DoD)-math.log(238.86))/-0.875)+4482.74484)#R2=.961
    return Cycle_aging_factor

def aging_day(daily_ESB,SOH,SOC_min,Batt,aux_Cap):
    """"
    A linear relationship between the capacity loss with the maximum battery
    life (years) was chosen. The values of calendric lifetime provide a
    reference value for storage degradation to 70% SOH at 20 °C temperature,
    when no charge throughput is applied [1].

    The temperature is assumed to be controlled and its effect on the battery
    aging minimized. As for the cyclic aging, we use a similar approach as the
    presented by Magnor et al. assuming different Woehler curves for different
    battery technologies [2]. The Woehler curves are provided in the
    specifications for some technologies (e.g. NCA), when the curve is not
    provided, we use other manufacturer curve, which use the same technology
    and adapt it to the referenced number of cycles of the real manufacturer.
    The cyclic agingis then the number of cycles per day at the given DoD,
    divided by the maximum number of cycles at a given DoD.

    [1] H. C. Hesse, R. Martins, P. Musilek, M. Naumann, C. N. Truong, and A.
    Jossen, “Economic Optimization of Component Sizing for Residential
    Battery Storage Systems,” Energies, vol. 10, no. 7, p. 835, Jun. 2017.

    [2]D. U. Sauer, P. Merk, M. Ecker, J. B. Gerschler, and D. Magnor, “Concept
    of a Battery Aging Model for Lithium-Ion Batteries Considering the Lifetime
    Dependency on the Operation Strategy,” 24th Eur. Photovolt. Sol. Energy
    Conf. 21-25 Sept. 2009 Hambg. Ger., pp. 3128–3134, Nov. 2009.

    cycle_cal indicates which aging dominates in the day if 1 cycle is dominating.
    Parameters
    ----------
    daily_ESB : array
    SOH : float
    SOC_min : float
    Batt : class
    aux_Cap : float

    Returns
    -------
    SOC_max : float
    aux_Cap : float
    SOH : float
    Cycle_aging_factor : float
    cycle_cal : int
    DoD : float
    """
    #aging is daily
    Cal_aging_factor=1/(Batt.Battery_cal_life*24*365)
    aux_DOD=(Batt.SOC_max-Batt.SOC_min)/Batt.Capacity
    DoD=daily_ESB.sum()/Batt.Capacity
    if DoD==0:
        Cycle_aging_factor=get_cycle_aging(DoD+0.00001,Batt.Technology)
    elif DoD<=1:
        Cycle_aging_factor=get_cycle_aging(DoD,Batt.Technology)
    else:
        aux_DoD=DoD-int(DoD)
        Cycle_aging_factor=get_cycle_aging(aux_DoD,Batt.Technology)
        for i in range(int(DoD)):
            Cycle_aging_factor+=get_cycle_aging(1,Batt.Technology)
    #Linearize SOH in [0,1]
    #SOH=0 if EoL (70% CNom)
    SOH=1/.3*aux_Cap/Batt.Capacity-7/3
    aging=max(Cycle_aging_factor,Cal_aging_factor*24)
    aux_Cap=Batt.Capacity*(1-0.3*(1-SOH+aging))
    if Cycle_aging_factor>(Cal_aging_factor*24):
        cycle_cal=1
    else:
        cycle_cal=0
    SOC_max=Batt.SOC_min+aux_Cap*(aux_DOD)
    return [SOC_max,aux_Cap,SOH,Cycle_aging_factor,cycle_cal,DoD]
def Merge(dict1, dict2): 
    res = {**dict1, **dict2} 
    return res 
def aggregate_results(df,aux_dict,param):
    '''
    Takes the results from the whole year optimization and gets the aggregated results.
    Parameters
    ----------
    df : DataFrame
    param: dict
    aux_dict: dict

    Returns
    -------
    bool
        True if successful, False otherwise.
    '''
    #attention E_batt_load
    #Attention with the configuration changes in the columns.
    #Remember if charging from csvs there is a back_to_dict function
    print('agg1')
    try:
        param.update({'df':df})

        param = Merge(param, aux_dict)
        param['DoD'] = param.pop('DoD_arr')
        param['Cap_arr']=param.pop('aux_Cap_arr')
        param['SOH']=param.pop('SOH_arr')
        param['P_max']=param.pop('P_max_arr')
        param['results']=param.pop('results_arr')
        App_comb=param['App_comb']
        col = ["%i" % x for x in App_comb]
        name_comb=col[0]+col[1]+col[2]+col[3]+col[4]
        col2 = ["%i" % x for x in param['conf']]

        name_conf=col2[0]+col2[1]+col2[2]+col2[3]
        [clusters,PV,App]=pp.get_table_inputs()
        [agg_results]=pp.get_main_results(param,clusters,PV,App)
        print(agg_results.head())
        global_lock = threading.Lock()
        while global_lock.locked():
            continue
        global_lock.acquire()
        #Should be saved in a DB
        filename='/data/home/alejandropena/P4/Sept_2021/Output/aggregated_results.csv'
        print('Inside agg_results')
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(agg_results.values)
        global_lock.release()
        print('aggregated saved')

    except IOError as e:
        print('Had some issues with the aggregated results')
        print ("I/O error({0}): {1}".format(e.errno, e.strerror))

    except ValueError as b:
        print('Had some issues with the aggregated results')
        print ("Could not convert data to an integer." + str(b))

    except:
        print('Had some issues with the aggregated results')
        print ("Unexpected error:", sys.exc_info()[0])
        print ("Unexpected error2:", sys.stderr)

    return

def save_obj(obj, name ):
    with open('Output/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def save_results(df,aux_dict,param):
    '''
    Save the results in pickle format using the corresponding timezone.
	The file is saved in the same directory the program is saved.
	The name is structured as follows: df_name_tech_App_Cap_conf.pickle
    Parameters
    ----------
    df : DataFrame
    param: dict
    aux_dict: dict

    Returns
    -------
    bool
        True if successful, False otherwise.
    '''
    try:
        print('saving results')
        App_comb=param['App_comb']
        col = ["%i" % x for x in App_comb]
        name_comb=col[0]+col[1]+col[2]+col[3]+col[4]
        col2 = ["%i" % x for x in param['conf']]
        name_conf=col2[0]+col2[1]+col2[2]+col2[3]
        print('after')
        filename_save=('/data/home/alejandropena/P4/Sept_2021/Output/df_%(name)s_%(Tech)s_%(App_comb)s_%(Cap)s_%(conf)s_%(FC_div)s.csv'%{'name':param['name'],'Tech':param['Tech'],'App_comb':name_comb,'Cap':int(param['Capacity']),'conf':name_conf,'FC_div':param['FC_div']})
        df.to_csv(filename_save)
        print('df_saved')
        save_obj(aux_dict, 'aux_dict' )
        print('aux_dict')
        save_obj(param, 'param' )
        print('param')
        return
    except:
        print('Save Failed')
        return

def save_obj(obj, name ):
    with open('/data/home/alejandropena/P4/Sept_2021/Output/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def single_opt2(param, data_input):
    """"
    Iterates over capacities, technologies and applications and calls the module to save the results.
    Parameters
    ----------
    param: dict
    data_input: DataFrame

    Returns
    -------
    df : DataFrame
    Cap_arr : array
    SOH : float
    Cycle_aging_factor : float
    P_max : float
    results : float
    cycle_cal_arr :array
    """
    
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@')
    print('single opt')
    print('bf')
    aux_app_comb=param['App_comb']#afterwards is modified to send to LP
    print('af')
    df,aux_dict=Optimize(data_input,param)
    param.update({'App_comb':aux_app_comb})
    print('enter to save')
    #save_results(df,aux_dict,param)
    if param['testing']==False:
        print('enter to agg')
        aggregate_results(df,aux_dict,param)
    else:
        print(data_input.head())
        save_results(df,aux_dict,param)
    print('so3')
    return  [df,aux_dict]

