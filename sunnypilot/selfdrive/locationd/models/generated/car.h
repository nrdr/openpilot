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
void car_err_fun(double *nom_x, double *delta_x, double *out_6354431385352312229);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3578996407475658948);
void car_H_mod_fun(double *state, double *out_8636216194094358869);
void car_f_fun(double *state, double dt, double *out_3209984340590427328);
void car_F_fun(double *state, double dt, double *out_164193611416397236);
void car_h_25(double *state, double *unused, double *out_5610039924323847659);
void car_H_25(double *state, double *unused, double *out_5113235544104867192);
void car_h_24(double *state, double *unused, double *out_9031090138526068658);
void car_H_24(double *state, double *unused, double *out_1555309945302544056);
void car_h_30(double *state, double *unused, double *out_1115488196390222746);
void car_H_30(double *state, double *unused, double *out_2594902585597618565);
void car_h_26(double *state, double *unused, double *out_1873338341551041556);
void car_H_26(double *state, double *unused, double *out_8854738862978923416);
void car_h_27(double *state, double *unused, double *out_2039305248987486683);
void car_H_27(double *state, double *unused, double *out_371308514413675348);
void car_h_29(double *state, double *unused, double *out_2058998049291885181);
void car_H_29(double *state, double *unused, double *out_2084671241283226381);
void car_h_28(double *state, double *unused, double *out_8733233628990240216);
void car_H_28(double *state, double *unused, double *out_7167070258352756955);
void car_h_31(double *state, double *unused, double *out_1160795302026503277);
void car_H_31(double *state, double *unused, double *out_5082589582227906764);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}