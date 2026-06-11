#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_7709211145934123991);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_3942366649005103634);
void pose_H_mod_fun(double *state, double *out_7024720103031486995);
void pose_f_fun(double *state, double dt, double *out_8735071172480870357);
void pose_F_fun(double *state, double dt, double *out_823961402091764503);
void pose_h_4(double *state, double *unused, double *out_5737604937341341534);
void pose_H_4(double *state, double *unused, double *out_6269505585638983886);
void pose_h_10(double *state, double *unused, double *out_5255790841188854786);
void pose_H_10(double *state, double *unused, double *out_4631033678897535887);
void pose_h_13(double *state, double *unused, double *out_6690590361496767190);
void pose_H_13(double *state, double *unused, double *out_3057231760306651085);
void pose_h_14(double *state, double *unused, double *out_3232252269187951923);
void pose_H_14(double *state, double *unused, double *out_6704622112283867485);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}