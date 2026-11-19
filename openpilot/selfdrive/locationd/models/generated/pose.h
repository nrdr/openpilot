#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_4541492771646069759);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_3364276346708699962);
void pose_H_mod_fun(double *state, double *out_7182100953115386674);
void pose_f_fun(double *state, double dt, double *out_6957551748977013851);
void pose_F_fun(double *state, double dt, double *out_5301176885049343435);
void pose_h_4(double *state, double *unused, double *out_3098701076704019746);
void pose_H_4(double *state, double *unused, double *out_368172970598732889);
void pose_h_10(double *state, double *unused, double *out_5402423064051119791);
void pose_H_10(double *state, double *unused, double *out_3989863782830359753);
void pose_h_13(double *state, double *unused, double *out_8642008707511601712);
void pose_H_13(double *state, double *unused, double *out_7242458237717968040);
void pose_h_14(double *state, double *unused, double *out_1963635100147538950);
void pose_H_14(double *state, double *unused, double *out_3450961402894105185);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}