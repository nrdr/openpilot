#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_8253506042582469219);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_2344330990237256254);
void pose_H_mod_fun(double *state, double *out_1157215523194220986);
void pose_f_fun(double *state, double dt, double *out_6204252535340020659);
void pose_F_fun(double *state, double dt, double *out_3422125367295010588);
void pose_h_4(double *state, double *unused, double *out_2817870145355419988);
void pose_H_4(double *state, double *unused, double *out_7043089360779003781);
void pose_h_10(double *state, double *unused, double *out_3205891474748426047);
void pose_H_10(double *state, double *unused, double *out_7912524881714638743);
void pose_h_13(double *state, double *unused, double *out_4580396760279803780);
void pose_H_13(double *state, double *unused, double *out_3793023504613846906);
void pose_h_14(double *state, double *unused, double *out_4584687085492276109);
void pose_H_14(double *state, double *unused, double *out_7440413856591063306);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}