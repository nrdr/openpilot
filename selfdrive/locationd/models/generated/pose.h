#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_5882928859993581409);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1648621671757242144);
void pose_H_mod_fun(double *state, double *out_5699029555239033244);
void pose_f_fun(double *state, double dt, double *out_96900936455516417);
void pose_F_fun(double *state, double dt, double *out_5331787048708587552);
void pose_h_4(double *state, double *unused, double *out_5826361638936909921);
void pose_H_4(double *state, double *unused, double *out_6896977037121931348);
void pose_h_10(double *state, double *unused, double *out_8355050653109599723);
void pose_H_10(double *state, double *unused, double *out_6486938087483779055);
void pose_h_13(double *state, double *unused, double *out_6117605580790890395);
void pose_H_13(double *state, double *unused, double *out_3063221573819407324);
void pose_h_14(double *state, double *unused, double *out_3317020926144572200);
void pose_H_14(double *state, double *unused, double *out_3814188604826559052);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}