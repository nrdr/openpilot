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
void car_err_fun(double *nom_x, double *delta_x, double *out_1937171401964887448);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8623208480402510856);
void car_H_mod_fun(double *state, double *out_5195459774287487890);
void car_f_fun(double *state, double dt, double *out_3416588175527017726);
void car_F_fun(double *state, double dt, double *out_4650294569433468939);
void car_h_25(double *state, double *unused, double *out_1746813054384403481);
void car_H_25(double *state, double *unused, double *out_1913198722745912190);
void car_h_24(double *state, double *unused, double *out_4499001988919102230);
void car_H_24(double *state, double *unused, double *out_259450876259587376);
void car_h_30(double *state, double *unused, double *out_1903999722735532626);
void car_H_30(double *state, double *unused, double *out_8829889064237528945);
void car_h_26(double *state, double *unused, double *out_1132786328708800059);
void car_H_26(double *state, double *unused, double *out_1828304596128144034);
void car_h_27(double *state, double *unused, double *out_2678547860913828052);
void car_H_27(double *state, double *unused, double *out_390903536197752791);
void car_h_29(double *state, double *unused, double *out_3594447557471213586);
void car_H_29(double *state, double *unused, double *out_2104266263067303824);
void car_h_28(double *state, double *unused, double *out_8321277731994784887);
void car_H_28(double *state, double *unused, double *out_140635991501977573);
void car_h_31(double *state, double *unused, double *out_5713745709864484844);
void car_H_31(double *state, double *unused, double *out_1943844684622872618);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}