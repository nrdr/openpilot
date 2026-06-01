#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_5782186265648731279);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_7193052209322201941);
void pose_H_mod_fun(double *state, double *out_8077327556656833445);
void pose_f_fun(double *state, double dt, double *out_6245206989908436510);
void pose_F_fun(double *state, double dt, double *out_1848154903834159695);
void pose_h_4(double *state, double *unused, double *out_3938051956761627657);
void pose_H_4(double *state, double *unused, double *out_92837036171442255);
void pose_h_10(double *state, double *unused, double *out_1332736732351532351);
void pose_H_10(double *state, double *unused, double *out_8776981312520129519);
void pose_h_13(double *state, double *unused, double *out_6677041446263562296);
void pose_H_13(double *state, double *unused, double *out_3305110861503775056);
void pose_h_14(double *state, double *unused, double *out_6699636769910654615);
void pose_H_14(double *state, double *unused, double *out_342279490473441344);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}