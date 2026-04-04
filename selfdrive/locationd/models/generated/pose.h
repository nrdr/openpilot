#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_2990975860512923391);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_8589403635603503433);
void pose_H_mod_fun(double *state, double *out_2750295583345837463);
void pose_f_fun(double *state, double dt, double *out_2722954666226833811);
void pose_F_fun(double *state, double dt, double *out_5728593125393536167);
void pose_h_4(double *state, double *unused, double *out_7945281333303209547);
void pose_H_4(double *state, double *unused, double *out_5280460880052190141);
void pose_h_10(double *state, double *unused, double *out_1469163044313279183);
void pose_H_10(double *state, double *unused, double *out_4991129487684167274);
void pose_h_13(double *state, double *unused, double *out_4398527889198662382);
void pose_H_13(double *state, double *unused, double *out_8492734705384522942);
void pose_h_14(double *state, double *unused, double *out_8724855652154765618);
void pose_H_14(double *state, double *unused, double *out_9203042337317876946);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}