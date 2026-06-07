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
void car_err_fun(double *nom_x, double *delta_x, double *out_6717507969388957699);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1494047623335630002);
void car_H_mod_fun(double *state, double *out_93510064572173015);
void car_f_fun(double *state, double dt, double *out_7214581727061175989);
void car_F_fun(double *state, double dt, double *out_7919137914284123017);
void car_h_25(double *state, double *unused, double *out_8206956957372498666);
void car_H_25(double *state, double *unused, double *out_3429470585417318662);
void car_h_24(double *state, double *unused, double *out_3355572179116912365);
void car_H_24(double *state, double *unused, double *out_1256820986411819096);
void car_h_30(double *state, double *unused, double *out_4713729679786029837);
void car_H_30(double *state, double *unused, double *out_8100583146800616199);
void car_h_26(double *state, double *unused, double *out_929000191294926998);
void car_H_26(double *state, double *unused, double *out_312032733456737562);
void car_h_27(double *state, double *unused, double *out_1960505899912325198);
void car_H_27(double *state, double *unused, double *out_8171397615108510506);
void car_h_29(double *state, double *unused, double *out_8731341126262676134);
void car_H_29(double *state, double *unused, double *out_6458034888238959473);
void car_h_28(double *state, double *unused, double *out_4148793542613315456);
void car_H_28(double *state, double *unused, double *out_1375635871169428899);
void car_h_31(double *state, double *unused, double *out_5511547774944287676);
void car_H_31(double *state, double *unused, double *out_3460116547294279090);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}