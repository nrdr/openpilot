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
void car_err_fun(double *nom_x, double *delta_x, double *out_8483021428746320765);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7116095168868427330);
void car_H_mod_fun(double *state, double *out_7967624822341296814);
void car_f_fun(double *state, double dt, double *out_7719046304768792394);
void car_F_fun(double *state, double dt, double *out_93541883228193728);
void car_h_25(double *state, double *unused, double *out_6239424513673374840);
void car_H_25(double *state, double *unused, double *out_6956138601378763125);
void car_h_24(double *state, double *unused, double *out_3510022705588126587);
void car_H_24(double *state, double *unused, double *out_6744096145364279457);
void car_h_30(double *state, double *unused, double *out_3999822813953269926);
void car_H_30(double *state, double *unused, double *out_39448259887146370);
void car_h_26(double *state, double *unused, double *out_6379994186587488275);
void car_H_26(double *state, double *unused, double *out_7749102153456732267);
void car_h_27(double *state, double *unused, double *out_8843829834482072491);
void car_H_27(double *state, double *unused, double *out_2214211571687571281);
void car_h_29(double *state, double *unused, double *out_4982146358053570839);
void car_H_29(double *state, double *unused, double *out_470783084427245814);
void car_h_28(double *state, double *unused, double *out_255667152677231083);
void car_H_28(double *state, double *unused, double *out_9009973315626652888);
void car_h_31(double *state, double *unused, double *out_6082237845322245695);
void car_H_31(double *state, double *unused, double *out_6925492639501802697);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}