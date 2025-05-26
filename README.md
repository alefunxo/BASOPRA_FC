# BASOPRA_FC
Description
Daily battery schedule optimizer (i.e. 24 h optimization framework), assuming perfect day-ahead forecast of the electricity demand load and solar PV generation in order to determine the maximum economic potential regardless of the forecast strategy used. Include the use of different applications which residential batteries can perform from a consumer perspective. Applications such as avoidance of PV curtailment, demand load-shifting and demand peak shaving are considered along with the base application, PV self-consumption. Different battery technologies and sizes can be analyzed as well as different tariff structures.
Aging is treated as an exogenous parameter, calculated on daily basis and is not subject of optimization. Data with 15-minute, 30-minute and 1-hour temporal resolution may be used for simulations. The model objective function have two components, the energy-based and the power-based component, as the tariff structure depends on the applications considered, a boolean parameter activate the power-based factor of the bill when is necessary.

Here we include Frequency control to the pool of applications

📜 License Change Notice
Important: As of 26/05/2025, this project has been relicensed under the Apache License 2.0.

Previously, the code was licensed under the GNU General Public License (GPL). Since I am the sole author of all original source code in this repository, and no external GPL-licensed code has been included or derived from, I have chosen to relicense the project under the Apache License 2.0 to support broader use and integration.

Please refer to the LICENSE file for the current terms.
