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
void car_err_fun(double *nom_x, double *delta_x, double *out_5162780191316530393);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4565764756772444199);
void car_H_mod_fun(double *state, double *out_1740013399271589656);
void car_f_fun(double *state, double dt, double *out_7662437844463834993);
void car_F_fun(double *state, double dt, double *out_3728435986983010203);
void car_h_25(double *state, double *unused, double *out_861668583978050454);
void car_H_25(double *state, double *unused, double *out_7513542448525724723);
void car_h_24(double *state, double *unused, double *out_870364197288317554);
void car_H_24(double *state, double *unused, double *out_5340892849520225157);
void car_h_30(double *state, double *unused, double *out_2775780944275971896);
void car_H_30(double *state, double *unused, double *out_8414868666676578266);
void car_h_26(double *state, double *unused, double *out_2225892323384873749);
void car_H_26(double *state, double *unused, double *out_3772039129651668499);
void car_h_27(double *state, double *unused, double *out_8603106317724660397);
void car_H_27(double *state, double *unused, double *out_6191274595492635049);
void car_h_29(double *state, double *unused, double *out_1689054295919507569);
void car_H_29(double *state, double *unused, double *out_7904637322362186082);
void car_h_28(double *state, double *unused, double *out_4841964488324045574);
void car_H_28(double *state, double *unused, double *out_5459707734277834960);
void car_h_31(double *state, double *unused, double *out_5052064442692697919);
void car_H_31(double *state, double *unused, double *out_3145831027418317023);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}