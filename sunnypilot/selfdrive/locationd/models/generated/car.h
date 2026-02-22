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
void car_err_fun(double *nom_x, double *delta_x, double *out_5090167770449267747);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_2214359751135662810);
void car_H_mod_fun(double *state, double *out_8824828869686346636);
void car_f_fun(double *state, double dt, double *out_7390949759775601083);
void car_F_fun(double *state, double dt, double *out_5580992667421940842);
void car_h_25(double *state, double *unused, double *out_873146183491989349);
void car_H_25(double *state, double *unused, double *out_368359356225890601);
void car_h_24(double *state, double *unused, double *out_838029550239282357);
void car_H_24(double *state, double *unused, double *out_6285846101882295156);
void car_h_30(double *state, double *unused, double *out_4126629357105742333);
void car_H_30(double *state, double *unused, double *out_4896055686353498799);
void car_h_26(double *state, double *unused, double *out_4954179189956699152);
void car_H_26(double *state, double *unused, double *out_4109862675099946825);
void car_h_27(double *state, double *unused, double *out_1476462068168466866);
void car_H_27(double *state, double *unused, double *out_7070818998153923710);
void car_h_29(double *state, double *unused, double *out_5113911596422489216);
void car_H_29(double *state, double *unused, double *out_4385824342039106615);
void car_h_28(double *state, double *unused, double *out_1127943252640230785);
void car_H_28(double *state, double *unused, double *out_8978520714600914427);
void car_h_31(double *state, double *unused, double *out_2764303344762033001);
void car_H_31(double *state, double *unused, double *out_4736070777333298301);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}