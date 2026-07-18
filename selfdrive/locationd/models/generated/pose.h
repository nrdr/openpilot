#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_7254010466112148474);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_7571376916876272361);
void pose_H_mod_fun(double *state, double *out_2541048523476695545);
void pose_f_fun(double *state, double dt, double *out_3669044169232965943);
void pose_F_fun(double *state, double dt, double *out_7678120840594066035);
void pose_h_4(double *state, double *unused, double *out_6972566205893694525);
void pose_H_4(double *state, double *unused, double *out_6403313142581125797);
void pose_h_10(double *state, double *unused, double *out_932110130621909408);
void pose_H_10(double *state, double *unused, double *out_3725761758741894007);
void pose_h_13(double *state, double *unused, double *out_2777222270862285990);
void pose_H_13(double *state, double *unused, double *out_3191039317248792996);
void pose_h_14(double *state, double *unused, double *out_4613594682857435522);
void pose_H_14(double *state, double *unused, double *out_2440072286241641268);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}