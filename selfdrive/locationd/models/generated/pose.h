#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_4554654253610197066);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_7859607288829869304);
void pose_H_mod_fun(double *state, double *out_7585864625755261889);
void pose_f_fun(double *state, double dt, double *out_8989872321626802535);
void pose_F_fun(double *state, double dt, double *out_8485858395715639244);
void pose_h_4(double *state, double *unused, double *out_2463733989185154553);
void pose_H_4(double *state, double *unused, double *out_5708361062915208992);
void pose_h_10(double *state, double *unused, double *out_447107545250377170);
void pose_H_10(double *state, double *unused, double *out_219357948856653379);
void pose_h_13(double *state, double *unused, double *out_1364887226416245912);
void pose_H_13(double *state, double *unused, double *out_2496087237582876191);
void pose_h_14(double *state, double *unused, double *out_5491047812010955419);
void pose_H_14(double *state, double *unused, double *out_8791149495210581288);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}