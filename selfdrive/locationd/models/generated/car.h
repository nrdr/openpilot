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
void car_err_fun(double *nom_x, double *delta_x, double *out_3321760492551468366);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3697485090417495632);
void car_H_mod_fun(double *state, double *out_4190227621087458402);
void car_f_fun(double *state, double dt, double *out_6456348943274406543);
void car_F_fun(double *state, double dt, double *out_4201765287475637381);
void car_h_25(double *state, double *unused, double *out_9136101134851125551);
void car_H_25(double *state, double *unused, double *out_7713208271076950079);
void car_h_24(double *state, double *unused, double *out_8665340836537612490);
void car_H_24(double *state, double *unused, double *out_7175610203830278401);
void car_h_30(double *state, double *unused, double *out_4641549406917500638);
void car_H_30(double *state, double *unused, double *out_3185511940949341881);
void car_h_26(double *state, double *unused, double *out_2793594027511200175);
void car_H_26(double *state, double *unused, double *out_3971704952202893855);
void car_h_27(double *state, double *unused, double *out_5860253322103668962);
void car_H_27(double *state, double *unused, double *out_5409106012133285098);
void car_h_29(double *state, double *unused, double *out_5585059259819163073);
void car_H_29(double *state, double *unused, double *out_3695743285263734065);
void car_h_28(double *state, double *unused, double *out_6187449234192033508);
void car_H_28(double *state, double *unused, double *out_1386655731805796509);
void car_h_31(double *state, double *unused, double *out_2365265908500774615);
void car_H_31(double *state, double *unused, double *out_7743854232953910507);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}