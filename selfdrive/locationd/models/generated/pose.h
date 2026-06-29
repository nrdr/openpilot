#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_3891534798634327778);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5649509494944615681);
void pose_H_mod_fun(double *state, double *out_7794314942061694640);
void pose_f_fun(double *state, double dt, double *out_8869893727485620911);
void pose_F_fun(double *state, double dt, double *out_8161571396865937044);
void pose_h_4(double *state, double *unused, double *out_246670649264504437);
void pose_H_4(double *state, double *unused, double *out_6037802094718540612);
void pose_h_10(double *state, double *unused, double *out_3326189525576215270);
void pose_H_10(double *state, double *unused, double *out_5195608496361205355);
void pose_h_13(double *state, double *unused, double *out_5017380501583283993);
void pose_H_13(double *state, double *unused, double *out_2825528269386207811);
void pose_h_14(double *state, double *unused, double *out_5006204601247985119);
void pose_H_14(double *state, double *unused, double *out_2074561238379056083);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}