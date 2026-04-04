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
void car_err_fun(double *nom_x, double *delta_x, double *out_1590755408767672601);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1209319377282347077);
void car_H_mod_fun(double *state, double *out_2794585081193416972);
void car_f_fun(double *state, double dt, double *out_1208708832429879679);
void car_F_fun(double *state, double dt, double *out_6751886823644579436);
void car_h_25(double *state, double *unused, double *out_6838891315424905032);
void car_H_25(double *state, double *unused, double *out_3743706003221899181);
void car_h_24(double *state, double *unused, double *out_4852083295210749522);
void car_H_24(double *state, double *unused, double *out_5474972884418457210);
void car_h_30(double *state, double *unused, double *out_7970403230030624234);
void car_H_30(double *state, double *unused, double *out_783990326905709017);
void car_h_26(double *state, double *unused, double *out_1011565941976216531);
void car_H_26(double *state, double *unused, double *out_2202684347842957);
void car_h_27(double *state, double *unused, double *out_4234485994616207381);
void car_H_27(double *state, double *unused, double *out_1439603744278234200);
void car_h_29(double *state, double *unused, double *out_2968729962369778589);
void car_H_29(double *state, double *unused, double *out_273758982591316833);
void car_h_28(double *state, double *unused, double *out_3200657439812493432);
void car_H_28(double *state, double *unused, double *out_5356157999660847407);
void car_h_31(double *state, double *unused, double *out_1042381335329144153);
void car_H_31(double *state, double *unused, double *out_3774351965098859609);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}