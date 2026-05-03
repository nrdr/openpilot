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
void car_err_fun(double *nom_x, double *delta_x, double *out_760253992355356602);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4983548601721046404);
void car_H_mod_fun(double *state, double *out_8995833010704521871);
void car_f_fun(double *state, double dt, double *out_4562655195590537984);
void car_F_fun(double *state, double dt, double *out_6423431565507769528);
void car_h_25(double *state, double *unused, double *out_8281489855210528984);
void car_H_25(double *state, double *unused, double *out_257722837092792508);
void car_h_24(double *state, double *unused, double *out_5654195456743599601);
void car_H_24(double *state, double *unused, double *out_2483430621071661070);
void car_h_30(double *state, double *unused, double *out_8438676523561658129);
void car_H_30(double *state, double *unused, double *out_7174413178584409263);
void car_h_26(double *state, double *unused, double *out_1419904868343052079);
void car_H_26(double *state, double *unused, double *out_3562248806853593109);
void car_h_27(double *state, double *unused, double *out_1905364559686504598);
void car_H_27(double *state, double *unused, double *out_4999649866783984352);
void car_h_29(double *state, double *unused, double *out_3005304846354827708);
void car_H_29(double *state, double *unused, double *out_7684644522898801447);
void car_h_28(double *state, double *unused, double *out_8832630219803516209);
void car_H_28(double *state, double *unused, double *out_1796111877155097255);
void car_h_31(double *state, double *unused, double *out_6225098197673216166);
void car_H_31(double *state, double *unused, double *out_7334398087604609761);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}