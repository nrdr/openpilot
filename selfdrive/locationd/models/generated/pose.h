#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_6395110133292861521);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5574902989131587335);
void pose_H_mod_fun(double *state, double *out_6860086072787592800);
void pose_f_fun(double *state, double dt, double *out_6157473931416548839);
void pose_F_fun(double *state, double dt, double *out_2563232569638129684);
void pose_h_4(double *state, double *unused, double *out_9057789463521636950);
void pose_H_4(double *state, double *unused, double *out_6434139615882878081);
void pose_h_10(double *state, double *unused, double *out_439040734435285181);
void pose_H_10(double *state, double *unused, double *out_1840785913394498883);
void pose_h_13(double *state, double *unused, double *out_7181492765475252926);
void pose_H_13(double *state, double *unused, double *out_3221865790550545280);
void pose_h_14(double *state, double *unused, double *out_1398557426791028034);
void pose_H_14(double *state, double *unused, double *out_2470898759543393552);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}