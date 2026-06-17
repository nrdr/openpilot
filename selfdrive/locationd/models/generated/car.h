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
void car_err_fun(double *nom_x, double *delta_x, double *out_1839793480075446944);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6348115372523587908);
void car_H_mod_fun(double *state, double *out_3044097129650960971);
void car_f_fun(double *state, double dt, double *out_8786810168446307735);
void car_F_fun(double *state, double dt, double *out_781864656834108608);
void car_h_25(double *state, double *unused, double *out_4107541327329523197);
void car_H_25(double *state, double *unused, double *out_762758392799024188);
void car_h_24(double *state, double *unused, double *out_2286857433249008733);
void car_H_24(double *state, double *unused, double *out_1462949391179844374);
void car_h_30(double *state, double *unused, double *out_3655723929491149244);
void car_H_30(double *state, double *unused, double *out_6153931948692592567);
void car_h_26(double *state, double *unused, double *out_8912734656659687284);
void car_H_26(double *state, double *unused, double *out_4504261711673080412);
void car_h_27(double *state, double *unused, double *out_5621365826511336093);
void car_H_27(double *state, double *unused, double *out_3066860651742689169);
void car_h_29(double *state, double *unused, double *out_5364819482949327198);
void car_H_29(double *state, double *unused, double *out_381865995627872074);
void car_h_28(double *state, double *unused, double *out_619692558850490448);
void car_H_28(double *state, double *unused, double *out_1581764275937454177);
void car_h_31(double *state, double *unused, double *out_3773731323424525988);
void car_H_31(double *state, double *unused, double *out_732112430922063760);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}