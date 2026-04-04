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
void car_err_fun(double *nom_x, double *delta_x, double *out_8689376007771914630);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_9185173267100820525);
void car_H_mod_fun(double *state, double *out_2260146128448476382);
void car_f_fun(double *state, double dt, double *out_2158220440628955836);
void car_F_fun(double *state, double dt, double *out_616665486939110306);
void car_h_25(double *state, double *unused, double *out_6409895638825259551);
void car_H_25(double *state, double *unused, double *out_5783126778437968059);
void car_h_24(double *state, double *unused, double *out_624020570893641793);
void car_H_24(double *state, double *unused, double *out_9105691696469260421);
void car_h_30(double *state, double *unused, double *out_5266013208533941129);
void car_H_30(double *state, double *unused, double *out_5653787831294727989);
void car_h_26(double *state, double *unused, double *out_6956461043269622089);
void car_H_26(double *state, double *unused, double *out_2041623459563911835);
void car_h_27(double *state, double *unused, double *out_1408222371164413906);
void car_H_27(double *state, double *unused, double *out_3479024519494303078);
void car_h_29(double *state, double *unused, double *out_1133028308879908017);
void car_H_29(double *state, double *unused, double *out_6164019175609120173);
void car_h_28(double *state, double *unused, double *out_2351732224066076341);
void car_H_28(double *state, double *unused, double *out_3316737224444778529);
void car_h_31(double *state, double *unused, double *out_9089122444528807104);
void car_H_31(double *state, double *unused, double *out_5813772740314928487);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}