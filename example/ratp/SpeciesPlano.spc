9	! Number of leaf inclination angle classes
0.220     0.207     0.182     0.149     0.111     0.073     0.040     0.015     0.003 PLANO
2	! Number of wavelength bands
0.085	0.425	!	PAR	NIR	scattering coefficients
0.01	0.0071	!	Parameters of boundary layer conductance : ga = A1 wind_speed + A2
2.002e-3	0.740e-3	! Parameters of Jarvis model: effect of leaf nitrogen content : gsmax = A1 Na + A2
1	3	-3.752e-7	1.1051e-3	0.183		! Parameters of Jarvis model: effect of leaf PAR irradiance : fgsPAR = f(PAR, µmol m-2 s-1) 
1	3	 2.32e-4	 -4.02e-2	2.07		! Parameters of Jarvis model: effect of air CO2 pressure : fgsPAR = f(CA, Pa) 
1	3	-4.82e-3	0.24165		-2.029		! Parameters of Jarvis model: effect of leaf temperature : fgsPAR = f(LT, °C) 
-1.8e-4	1.18	! Parameters of Jarvis model: effect of leaf surface VPD : gsmax = A1 VPD (Pa) + A2
20.0	6.		! Parameters of Farquhar's model: Vcmax25°C (µmol CO2 m-2 s-1) = A1 Na (g m-2) + A2
52.0	15.		! Parameters of Farquhar's model: Jmax25°C (µmol e m-2 s-1) = A1 Na (g m-2) + A2
0.25	0.05	! Parameters of Farquhar's model: Rd25°C (µmol CO2 m-2 s-1) = A1 Na (g m-2) + A2, Rd > 0
