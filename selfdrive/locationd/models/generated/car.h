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
void car_err_fun(double *nom_x, double *delta_x, double *out_8137803062968279058);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4803320297930984943);
void car_H_mod_fun(double *state, double *out_250780943344312618);
void car_f_fun(double *state, double dt, double *out_5023554550498675071);
void car_F_fun(double *state, double dt, double *out_3517018389212170475);
void car_h_25(double *state, double *unused, double *out_8788151648350399353);
void car_H_25(double *state, double *unused, double *out_3773761593333804295);
void car_h_24(double *state, double *unused, double *out_4617115616065835450);
void car_H_24(double *state, double *unused, double *out_5950976016940954268);
void car_h_30(double *state, double *unused, double *out_3908301040633649848);
void car_H_30(double *state, double *unused, double *out_6292094551841052922);
void car_h_26(double *state, double *unused, double *out_8870681038314943080);
void car_H_26(double *state, double *unused, double *out_32258274459748071);
void car_h_27(double *state, double *unused, double *out_8988688432248319824);
void car_H_27(double *state, double *unused, double *out_1469659334390139314);
void car_h_29(double *state, double *unused, double *out_149028852435531358);
void car_H_29(double *state, double *unused, double *out_243703392479411719);
void car_h_28(double *state, double *unused, double *out_4456382373800386147);
void car_H_28(double *state, double *unused, double *out_1719926879085914532);
void car_h_31(double *state, double *unused, double *out_7610421138374421687);
void car_H_31(double *state, double *unused, double *out_3804407555210764723);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}