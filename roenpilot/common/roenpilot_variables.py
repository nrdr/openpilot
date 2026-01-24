# longitudinal

# acceleration

# ISO 15622:2018
MAX_ISO_ACCEL_LOW_SPEED = 4.0 # m/s^2
MAX_ISO_ACCEL_STEADY_STATE = 2.0 # m/s^2
ISO_MAX_VALS = [MAX_ISO_ACCEL_LOW_SPEED, MAX_ISO_ACCEL_LOW_SPEED, MAX_ISO_ACCEL_STEADY_STATE]

# FP Sport Mode
A_CRUISE_MAX_VALS_SPORT = [3.0, 2.5, 2.0, 1.5, 1.0, 0.8, 0.6]

# FP Eco Mode
A_CRUISE_MAX_VALS_ECO =   [2.0, 1.5, 1.0, 0.8, 0.6, 0.4, 0.2]

# velocity

# ISO 15622:2018
ISO_VELOCITY_START = 0. # m/s
ISO_VELOCITY_TRANSITION = 5. # m/s
ISO_VELOCITY_STEADY_STATE = 20. # m/s
ISO_MAX_BP = [ISO_VELOCITY_START, ISO_VELOCITY_TRANSITION, ISO_VELOCITY_STEADY_STATE]

# FP Custom Breakpoints
A_CRUISE_MAX_BP_CUSTOM =  [0.0,  5., 10., 15., 20., 25., 40.]

# lateral

# acceleration
MINIMUM_LATERAL_ACCELERATION = 1.3        # m/s^2, typical minimum lateral acceleration when taking curves
