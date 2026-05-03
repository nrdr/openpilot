#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_7113141565155944071);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_4273806753012627861);
void pose_H_mod_fun(double *state, double *out_4327706851715669235);
void pose_f_fun(double *state, double dt, double *out_497730658810754078);
void pose_F_fun(double *state, double dt, double *out_6088738551748760158);
void pose_h_4(double *state, double *unused, double *out_2742355909746826294);
void pose_H_4(double *state, double *unused, double *out_3203571547522250360);
void pose_h_10(double *state, double *unused, double *out_5392750946095808839);
void pose_H_10(double *state, double *unused, double *out_6832887606116687430);
void pose_h_13(double *state, double *unused, double *out_7827281880185644605);
void pose_H_13(double *state, double *unused, double *out_8702277810082441);
void pose_h_14(double *state, double *unused, double *out_3917682265727873259);
void pose_H_14(double *state, double *unused, double *out_759669308817234169);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}