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
void live_H(double *in_vec, double *out_1467078053003343317);
void live_err_fun(double *nom_x, double *delta_x, double *out_9098634665855941294);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_8860653482060593261);
void live_H_mod_fun(double *state, double *out_3680676448785546161);
void live_f_fun(double *state, double dt, double *out_3283045121280332156);
void live_F_fun(double *state, double dt, double *out_8777195921412517690);
void live_h_4(double *state, double *unused, double *out_2094680521585394788);
void live_H_4(double *state, double *unused, double *out_7038435171555769042);
void live_h_9(double *state, double *unused, double *out_6988238914777504879);
void live_H_9(double *state, double *unused, double *out_7279624818185359687);
void live_h_10(double *state, double *unused, double *out_5583613770534798398);
void live_H_10(double *state, double *unused, double *out_5967947010106624075);
void live_h_12(double *state, double *unused, double *out_2519302758512928591);
void live_H_12(double *state, double *unused, double *out_6388852494121820779);
void live_h_35(double *state, double *unused, double *out_3350975828148237958);
void live_H_35(double *state, double *unused, double *out_8041646844781175198);
void live_h_32(double *state, double *unused, double *out_8919770490892273644);
void live_H_32(double *state, double *unused, double *out_3955911156684252098);
void live_h_13(double *state, double *unused, double *out_2011274580288083383);
void live_H_13(double *state, double *unused, double *out_1171916528339428935);
void live_h_14(double *state, double *unused, double *out_6988238914777504879);
void live_H_14(double *state, double *unused, double *out_7279624818185359687);
void live_h_33(double *state, double *unused, double *out_5246169956302038538);
void live_H_33(double *state, double *unused, double *out_4891089840142317594);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}