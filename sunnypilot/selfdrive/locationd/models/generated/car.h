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
void car_err_fun(double *nom_x, double *delta_x, double *out_177103021785581557);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_280229844855458663);
void car_H_mod_fun(double *state, double *out_5987507050912750699);
void car_f_fun(double *state, double dt, double *out_8388899665404882739);
void car_F_fun(double *state, double dt, double *out_4658695639288576337);
void car_h_25(double *state, double *unused, double *out_4678207828654942345);
void car_H_25(double *state, double *unused, double *out_509515908977279252);
void car_h_24(double *state, double *unused, double *out_8502713115672552530);
void car_H_24(double *state, double *unused, double *out_5378330774004986104);
void car_h_30(double *state, double *unused, double *out_232461577386389961);
void car_H_30(double *state, double *unused, double *out_5037212239104887450);
void car_h_26(double *state, double *unused, double *out_6488286299345437215);
void car_H_26(double *state, double *unused, double *out_4251019227851335476);
void car_h_27(double *state, double *unused, double *out_2665177063350571240);
void car_H_27(double *state, double *unused, double *out_7211975550905312361);
void car_h_29(double *state, double *unused, double *out_213208467549963176);
void car_H_29(double *state, double *unused, double *out_4526980894790495266);
void car_h_28(double *state, double *unused, double *out_4513270737826376580);
void car_H_28(double *state, double *unused, double *out_8837364161849525776);
void car_h_31(double *state, double *unused, double *out_8453928196365624064);
void car_H_31(double *state, double *unused, double *out_4877227330084686952);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}