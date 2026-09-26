#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_7950841656255825399);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1038560697701516954);
void pose_H_mod_fun(double *state, double *out_7368662583295686451);
void pose_f_fun(double *state, double dt, double *out_7152923552696196830);
void pose_F_fun(double *state, double dt, double *out_1783079396843657897);
void pose_h_4(double *state, double *unused, double *out_7141288839189123597);
void pose_H_4(double *state, double *unused, double *out_8122823585350399058);
void pose_h_10(double *state, double *unused, double *out_2925053845163599483);
void pose_H_10(double *state, double *unused, double *out_360848949412854679);
void pose_h_13(double *state, double *unused, double *out_7295945181203287929);
void pose_H_13(double *state, double *unused, double *out_7111646663026819757);
void pose_h_14(double *state, double *unused, double *out_9068419937336893414);
void pose_H_14(double *state, double *unused, double *out_6360679632019668029);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}