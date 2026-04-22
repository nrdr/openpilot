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
void car_err_fun(double *nom_x, double *delta_x, double *out_8405065958417086303);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7508359302928735357);
void car_H_mod_fun(double *state, double *out_682534342215023977);
void car_f_fun(double *state, double dt, double *out_9135589611294496438);
void car_F_fun(double *state, double dt, double *out_2095188307217211618);
void car_h_25(double *state, double *unused, double *out_2546555325152015896);
void car_H_25(double *state, double *unused, double *out_266586579813458232);
void car_h_24(double *state, double *unused, double *out_428009811774810899);
void car_H_24(double *state, double *unused, double *out_8952092307826898159);
void car_h_30(double *state, double *unused, double *out_2298685954961374493);
void car_H_30(double *state, double *unused, double *out_4261109750314149966);
void car_h_26(double *state, double *unused, double *out_3056536100122193303);
void car_H_26(double *state, double *unused, double *out_3474916739060597992);
void car_h_27(double *state, double *unused, double *out_856107490416334936);
void car_H_27(double *state, double *unused, double *out_6435873062114574877);
void car_h_29(double *state, double *unused, double *out_7036832004468188423);
void car_H_29(double *state, double *unused, double *out_3750878405999757782);
void car_h_28(double *state, double *unused, double *out_2180678561027997749);
void car_H_28(double *state, double *unused, double *out_8833277423069288356);
void car_h_31(double *state, double *unused, double *out_3393465531401682430);
void car_H_31(double *state, double *unused, double *out_4101124841293949468);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}