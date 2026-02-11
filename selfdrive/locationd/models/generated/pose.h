#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_1395619254280121889);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_214512694638000517);
void pose_H_mod_fun(double *state, double *out_4178491048942550488);
void pose_f_fun(double *state, double dt, double *out_6955059668244195066);
void pose_F_fun(double *state, double dt, double *out_5780055978525304403);
void pose_h_4(double *state, double *unused, double *out_4735577956641194937);
void pose_H_4(double *state, double *unused, double *out_2358792323036253627);
void pose_h_10(double *state, double *unused, double *out_791674336687732538);
void pose_H_10(double *state, double *unused, double *out_6454210329134681661);
void pose_h_13(double *state, double *unused, double *out_1136153937435491358);
void pose_H_13(double *state, double *unused, double *out_2923394242718097731);
void pose_h_14(double *state, double *unused, double *out_7535707900612158623);
void pose_H_14(double *state, double *unused, double *out_723996109259118669);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}