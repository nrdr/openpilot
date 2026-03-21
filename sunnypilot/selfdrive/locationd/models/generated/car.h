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
void car_err_fun(double *nom_x, double *delta_x, double *out_1553445728791412940);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6999435887956597333);
void car_H_mod_fun(double *state, double *out_6886426107079341067);
void car_f_fun(double *state, double dt, double *out_2629482357883749034);
void car_F_fun(double *state, double dt, double *out_7990705530243511971);
void car_h_25(double *state, double *unused, double *out_1968300025718050649);
void car_H_25(double *state, double *unused, double *out_8037269327984845401);
void car_h_24(double *state, double *unused, double *out_6877344855371313053);
void car_H_24(double *state, double *unused, double *out_3833902939133188114);
void car_h_30(double *state, double *unused, double *out_2125486694069179794);
void car_H_30(double *state, double *unused, double *out_7891141787217457588);
void car_h_26(double *state, double *unused, double *out_2612659355437634136);
void car_H_26(double *state, double *unused, double *out_7104948775963905614);
void car_h_27(double *state, double *unused, double *out_5005086077162383334);
void car_H_27(double *state, double *unused, double *out_5667547716033514371);
void car_h_29(double *state, double *unused, double *out_6670822770196817346);
void car_H_29(double *state, double *unused, double *out_7380910442903065404);
void car_h_28(double *state, double *unused, double *out_3412809501537689);
void car_H_28(double *state, double *unused, double *out_5983434613736955638);
void car_h_31(double *state, double *unused, double *out_8556127952194345812);
void car_H_31(double *state, double *unused, double *out_8067915289861805829);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}