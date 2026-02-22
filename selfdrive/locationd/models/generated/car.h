#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_err_fun(double *nom_x, double *delta_x, double *out_5639649317650519640);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3905676933826881602);
void car_H_mod_fun(double *state, double *out_7673742840829234825);
void car_f_fun(double *state, double dt, double *out_4328182976435702364);
void car_F_fun(double *state, double dt, double *out_5012898421281444787);
void car_h_25(double *state, double *unused, double *out_1973473835841134157);
void car_H_25(double *state, double *unused, double *out_1176719880939204874);
void car_h_24(double *state, double *unused, double *out_2056423373714747634);
void car_H_24(double *state, double *unused, double *out_706262398895866150);
void car_h_30(double *state, double *unused, double *out_1472091962479660102);
void car_H_30(double *state, double *unused, double *out_3350976449188403324);
void car_h_26(double *state, double *unused, double *out_2831719493489029930);
void car_H_26(double *state, double *unused, double *out_2564783437934851350);
void car_h_27(double *state, double *unused, double *out_991389742505836045);
void car_H_27(double *state, double *unused, double *out_1127382378004460107);
void car_h_29(double *state, double *unused, double *out_6889882908248213140);
void car_H_29(double *state, double *unused, double *out_2840745104874011140);
void car_h_28(double *state, double *unused, double *out_5455929932221819979);
void car_H_28(double *state, double *unused, double *out_7923144121943541714);
void car_h_31(double *state, double *unused, double *out_2503597671097058302);
void car_H_31(double *state, double *unused, double *out_1207365842816165302);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}