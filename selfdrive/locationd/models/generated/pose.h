#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_5956790764081545981);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_4313117768787886850);
void pose_H_mod_fun(double *state, double *out_1837758063541038755);
void pose_f_fun(double *state, double dt, double *out_520388946504101152);
void pose_F_fun(double *state, double dt, double *out_6289216028855659852);
void pose_h_4(double *state, double *unused, double *out_3915395617755416407);
void pose_H_4(double *state, double *unused, double *out_7596001590254828369);
void pose_h_10(double *state, double *unused, double *out_6204857596332608039);
void pose_H_10(double *state, double *unused, double *out_4868523555828362229);
void pose_h_13(double *state, double *unused, double *out_3430543055391911867);
void pose_H_13(double *state, double *unused, double *out_4383727764922495568);
void pose_h_14(double *state, double *unused, double *out_2629434873033650575);
void pose_H_14(double *state, double *unused, double *out_3632760733915343840);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}