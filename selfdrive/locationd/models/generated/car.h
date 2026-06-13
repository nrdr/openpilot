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
void car_err_fun(double *nom_x, double *delta_x, double *out_1133780562410706743);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4674975851193082904);
void car_H_mod_fun(double *state, double *out_318329653000957007);
void car_f_fun(double *state, double dt, double *out_1557131492089968397);
void car_F_fun(double *state, double dt, double *out_5093893007673167724);
void car_h_25(double *state, double *unused, double *out_9012832394529810438);
void car_H_25(double *state, double *unused, double *out_187004789199339705);
void car_h_24(double *state, double *unused, double *out_6747949908627279692);
void car_H_24(double *state, double *unused, double *out_6762576595790857806);
void car_h_30(double *state, double *unused, double *out_1809616437543824468);
void car_H_30(double *state, double *unused, double *out_7103695130690956460);
void car_h_26(double *state, double *unused, double *out_3192056830117021177);
void car_H_26(double *state, double *unused, double *out_3554498529674716519);
void car_h_27(double *state, double *unused, double *out_6890003829158494444);
void car_H_27(double *state, double *unused, double *out_4928931818890531549);
void car_h_29(double *state, double *unused, double *out_570554935090393881);
void car_H_29(double *state, double *unused, double *out_7613926475005348644);
void car_h_28(double *state, double *unused, double *out_634179107199447190);
void car_H_28(double *state, double *unused, double *out_1866829925048550058);
void car_h_31(double *state, double *unused, double *out_1973352914930852853);
void car_H_31(double *state, double *unused, double *out_217650751076300133);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}