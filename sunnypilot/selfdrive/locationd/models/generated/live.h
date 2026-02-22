#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void live_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_9(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_12(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_35(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_32(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_33(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_H(double *in_vec, double *out_8275724124421838306);
void live_err_fun(double *nom_x, double *delta_x, double *out_5281953134742465917);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_8389618353569296630);
void live_H_mod_fun(double *state, double *out_385766017041418567);
void live_f_fun(double *state, double dt, double *out_9153850964309317692);
void live_F_fun(double *state, double dt, double *out_5081205746890401542);
void live_h_4(double *state, double *unused, double *out_457696398415644193);
void live_H_4(double *state, double *unused, double *out_9185402334340926634);
void live_h_9(double *state, double *unused, double *out_4077730396237907128);
void live_H_9(double *state, double *unused, double *out_8944212687711335989);
void live_h_10(double *state, double *unused, double *out_7235283978459188109);
void live_H_10(double *state, double *unused, double *out_5372126596347557306);
void live_h_12(double *state, double *unused, double *out_7229154012242781618);
void live_H_12(double *state, double *unused, double *out_4165945926308964839);
void live_h_35(double *state, double *unused, double *out_8381613750956709029);
void live_H_35(double *state, double *unused, double *out_1420382893983951130);
void live_h_32(double *state, double *unused, double *out_8002832140309851271);
void live_H_32(double *state, double *unused, double *out_1363275270434466463);
void live_h_13(double *state, double *unused, double *out_4227421234071877163);
void live_H_13(double *state, double *unused, double *out_1666394413924048529);
void live_h_14(double *state, double *unused, double *out_4077730396237907128);
void live_H_14(double *state, double *unused, double *out_8944212687711335989);
void live_h_33(double *state, double *unused, double *out_272557329078716578);
void live_H_33(double *state, double *unused, double *out_1730174110654906474);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}