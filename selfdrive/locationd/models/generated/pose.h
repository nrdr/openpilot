#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_1395186704351471913);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_9198727305711896910);
void pose_H_mod_fun(double *state, double *out_3093613195444398718);
void pose_f_fun(double *state, double dt, double *out_1996627188251084581);
void pose_F_fun(double *state, double dt, double *out_7555202558844146792);
void pose_h_4(double *state, double *unused, double *out_5476937082898018351);
void pose_H_4(double *state, double *unused, double *out_6294023096545868742);
void pose_h_10(double *state, double *unused, double *out_6657021705980566751);
void pose_H_10(double *state, double *unused, double *out_6597046473621448693);
void pose_h_13(double *state, double *unused, double *out_6585329472009713103);
void pose_H_13(double *state, double *unused, double *out_5729421176864024638);
void pose_h_14(double *state, double *unused, double *out_8914797937571097614);
void pose_H_14(double *state, double *unused, double *out_9069932544868310578);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}