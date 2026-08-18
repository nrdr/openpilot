#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_7855544638909347154);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_8154377992469345659);
void pose_H_mod_fun(double *state, double *out_6969728399034555931);
void pose_f_fun(double *state, double dt, double *out_1236007422603849478);
void pose_F_fun(double *state, double dt, double *out_5168773265456939650);
void pose_h_4(double *state, double *unused, double *out_5296109952650410830);
void pose_H_4(double *state, double *unused, double *out_5914215848697000206);
void pose_h_10(double *state, double *unused, double *out_3519904827121473616);
void pose_H_10(double *state, double *unused, double *out_952577601439605767);
void pose_h_13(double *state, double *unused, double *out_1248641924569735485);
void pose_H_13(double *state, double *unused, double *out_9126489674029333007);
void pose_h_14(double *state, double *unused, double *out_6137258297331957672);
void pose_H_14(double *state, double *unused, double *out_8569287368673066881);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}