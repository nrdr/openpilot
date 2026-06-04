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
void car_err_fun(double *nom_x, double *delta_x, double *out_6558187156506406544);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_9123744096185346010);
void car_H_mod_fun(double *state, double *out_8155804854245815792);
void car_f_fun(double *state, double dt, double *out_3910178064661819655);
void car_F_fun(double *state, double dt, double *out_8475894658360832836);
void car_h_25(double *state, double *unused, double *out_5967448892281792710);
void car_H_25(double *state, double *unused, double *out_5496108376535866715);
void car_h_24(double *state, double *unused, double *out_2080633378133349492);
void car_H_24(double *state, double *unused, double *out_3648758333415010447);
void car_h_30(double *state, double *unused, double *out_3019722901926307749);
void car_H_30(double *state, double *unused, double *out_8014441335043115342);
void car_h_26(double *state, double *unused, double *out_4001806995261605861);
void car_H_26(double *state, double *unused, double *out_1754605057661810491);
void car_h_27(double *state, double *unused, double *out_7327076423291162538);
void car_H_27(double *state, double *unused, double *out_5839678023242690431);
void car_h_29(double *state, double *unused, double *out_1981950365734537896);
void car_H_29(double *state, double *unused, double *out_8524672679357507526);
void car_h_28(double *state, double *unused, double *out_2901715507992931005);
void car_H_28(double *state, double *unused, double *out_3442273662287976952);
void car_h_31(double *state, double *unused, double *out_4565484434131335742);
void car_H_31(double *state, double *unused, double *out_1128396955428459015);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}