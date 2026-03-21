#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_8464988186513175073);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1852709291048557817);
void pose_H_mod_fun(double *state, double *out_538340367000647943);
void pose_f_fun(double *state, double dt, double *out_7368455278738031076);
void pose_F_fun(double *state, double dt, double *out_5829154861726366619);
void pose_h_4(double *state, double *unused, double *out_849879868882736857);
void pose_H_4(double *state, double *unused, double *out_4614178018038432792);
void pose_h_10(double *state, double *unused, double *out_4738835720535906003);
void pose_H_10(double *state, double *unused, double *out_5846382860599074085);
void pose_h_13(double *state, double *unused, double *out_5334730689834359579);
void pose_H_13(double *state, double *unused, double *out_7826451843370765593);
void pose_h_14(double *state, double *unused, double *out_7621092473786206501);
void pose_H_14(double *state, double *unused, double *out_1531389585743060496);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}