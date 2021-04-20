## Configuring the script
The following can be configured in the "secret/scada_points.xlsx" file 
* Display name of a Bus can be controlled using the "substation" column of "bus_voltages" sheet. Sign change can be enabled by setting value as 1 in "is_flipped" column
* Display name of a Bus Reactor / Line Reactor can be controlled using the "substation" column of "reactors" sheet. Sign change can be enabled by setting value as 1 in "is_flipped" column
* Display name of a ICT / GT can be controlled using the "substation" column of "transformers" sheet. Sign change can be enabled by setting value as 1 in "is_flipped" column

## Configured entities information
*Bus* - Substation, Base Voltage, State, Voltage Point, Name, sign convention

*Bus Reactor* - State, MVAR point, Name, sign convention

*Generator* - State, GT MVAR injection point, Name, sign convention

*ICT/GT* - Substation, State, HV MVAR injection point, Name, sign convention

## Algorithm
* Iterate through all states
* Read all the voltage levels of the state and find the percentage of number of substations with voltage above 1.05 pu (config)
* Read the Bus Reactor MVARs of each state and find the bus reactors that are not in service, i.e., MVAR < 5 (config)
* Read each Generator MVAR injection of the state and find the generators that are not absorbing MVAR, i.e., MVAR > 3 (config)
* Read each ICT/GT HV MVAR injection of the state and find the ICTs where HV MVAR injection is present, i.e., HV MVAR injection > 5 (config)
