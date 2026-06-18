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
void car_err_fun(double *nom_x, double *delta_x, double *out_3940156393065166812);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3426194382367611568);
void car_H_mod_fun(double *state, double *out_7294341194267152476);
void car_f_fun(double *state, double dt, double *out_1523374379885210999);
void car_F_fun(double *state, double dt, double *out_1648068028519236125);
void car_h_25(double *state, double *unused, double *out_2419667139866351454);
void car_H_25(double *state, double *unused, double *out_3601039148607245603);
void car_h_24(double *state, double *unused, double *out_3288435787392757444);
void car_H_24(double *state, double *unused, double *out_6645356358611593795);
void car_h_30(double *state, double *unused, double *out_327979143817357097);
void car_H_30(double *state, double *unused, double *out_3730378095750485673);
void car_h_26(double *state, double *unused, double *out_3364765195261689782);
void car_H_26(double *state, double *unused, double *out_7342542467481301827);
void car_h_27(double *state, double *unused, double *out_7645574355701676401);
void car_H_27(double *state, double *unused, double *out_5905141407550910584);
void car_h_29(double *state, double *unused, double *out_7163720189753852865);
void car_H_29(double *state, double *unused, double *out_3220146751436093489);
void car_h_28(double *state, double *unused, double *out_4240622734355885336);
void car_H_28(double *state, double *unused, double *out_8302545768505624063);
void car_h_31(double *state, double *unused, double *out_8169958524591853869);
void car_H_31(double *state, double *unused, double *out_3570393186730285175);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}