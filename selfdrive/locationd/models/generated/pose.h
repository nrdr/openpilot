#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_7150551631592866018);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_2794293729781716576);
void pose_H_mod_fun(double *state, double *out_8150336989101570986);
void pose_f_fun(double *state, double dt, double *out_7007205599395941006);
void pose_F_fun(double *state, double dt, double *out_6961192590068817781);
void pose_h_4(double *state, double *unused, double *out_4316151876385378585);
void pose_H_4(double *state, double *unused, double *out_2672320983204381838);
void pose_h_10(double *state, double *unused, double *out_2925814787623901053);
void pose_H_10(double *state, double *unused, double *out_6143953899361439027);
void pose_h_13(double *state, double *unused, double *out_8822311255157966507);
void pose_H_13(double *state, double *unused, double *out_5884594808536714639);
void pose_h_14(double *state, double *unused, double *out_293817740766290370);
void pose_H_14(double *state, double *unused, double *out_6635561839543866367);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}