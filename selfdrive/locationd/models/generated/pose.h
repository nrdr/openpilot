#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_7345200414518154806);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_283206327660277539);
void pose_H_mod_fun(double *state, double *out_2082368326476086218);
void pose_f_fun(double *state, double dt, double *out_5163268778687305893);
void pose_F_fun(double *state, double dt, double *out_2262566197447778253);
void pose_h_4(double *state, double *unused, double *out_7434247557157613397);
void pose_H_4(double *state, double *unused, double *out_5932809187836661446);
void pose_h_10(double *state, double *unused, double *out_7247789716920531684);
void pose_H_10(double *state, double *unused, double *out_5259832045949180196);
void pose_h_13(double *state, double *unused, double *out_7157875501104788200);
void pose_H_13(double *state, double *unused, double *out_4903303677556189241);
void pose_h_14(double *state, double *unused, double *out_3063669227662560702);
void pose_H_14(double *state, double *unused, double *out_8550694029533405641);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}