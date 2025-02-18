import pyomo.environ as en
from pyomo.opt import SolverFactory
import paper_classes as pp
import LP as LP


# Create instances with minimal values
batt = pp.Battery_tech(Capacity=10,Technology='NMC')



# Create a time set from -1 to 23 (with -1 as the initial condition)
time_set = list(range(-1, 24))

# Build the Data dictionary with minimal parameters for a full day.
# In this example heating is active but without thermal storage and DHW.
Data = {
    'Set_declare': time_set,
    'delta_t': 0.25,
    'dayofyear': 150,  # within 120-274
    'toy': 0,  # a value not equal to 1,2,3 to take the "else" branch when needed
    'conf': [True, False, False, False],  # [E_storage, heating, T_storage, DHW]
    'App_comb_mod': [1, 0, 1, 0, 0],  # [FC, PVAC, PVSC, DLS, DPS]
    'retail_price': {t: 0.2 for t in range(24)},
    'E_PV': {t: 1 if 8 <= t <= 16 else 0.0 for t in range(24)},
    'E_demand': {t: 1 for t in range(24)},
    'Export_price': {t: 0 for t in range(24)},
    'Capacity_tariff': 0.05,
    'Inv_power': 5,
    'Inverter_eff': 0.95,
    'Converter_Efficiency_Batt': 0.98,
    'Max_inj': 100,
    'Batt': batt,
    'Export_price':{t: 0.01 for t in range(24)},
    'FC_price_up':{t: 0.6 for t in range(24)},
    'FC_price_down':{t: 0.5 for t in range(24)},
    'SOC_max':1, # this is constantly modified in Core_LP with the aging, here to simplify we keep it at 100
    'FC_div':0.25
}


# Import the Concrete_model function from your script.
# It is assumed that the provided script with Concrete_model and all constraints is in scope.
model = LP.Concrete_model(Data)

# Create and run the solver (using GLPK as an example)
solver = SolverFactory('gurobi')
result = solver.solve(model, tee=True)
result.write(num=1)


# Display a few results: objective value, grid consumption, PV injection, and battery SOC.
print("Objective value:", en.value(model.total_cost))
for t in sorted(model.Time):
    grid_cons = en.value(model.E_cons[t])
    pv_inj = en.value(model.E_PV_grid[t])
    fc_inj = en.value(model.E_dis_FC[t])
    # Battery SOC is defined over m.tm (which includes the initial time -1)
    soc = en.value(model.SOC[t]) if t in model.SOC else None
    print(f"Hour {t}: Grid consumption = {grid_cons:.3f} kWh, PV injection = {pv_inj:.3f} kWh, FC injection = {fc_inj:.3f}, Battery SOC = {soc:.3f}")
