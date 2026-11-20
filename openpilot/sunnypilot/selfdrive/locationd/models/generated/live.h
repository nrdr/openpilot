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
void live_H(double *in_vec, double *out_6196679513136842653);
void live_err_fun(double *nom_x, double *delta_x, double *out_2936348376915767954);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_145824877669358102);
void live_H_mod_fun(double *state, double *out_1905965230129749365);
void live_f_fun(double *state, double dt, double *out_372201579312861206);
void live_F_fun(double *state, double dt, double *out_411110204932439178);
void live_h_4(double *state, double *unused, double *out_8718152247374580907);
void live_H_4(double *state, double *unused, double *out_1494160266503799768);
void live_h_9(double *state, double *unused, double *out_955372783900519039);
void live_H_9(double *state, double *unused, double *out_8781379201768247238);
void live_h_10(double *state, double *unused, double *out_2682017855709925840);
void live_H_10(double *state, double *unused, double *out_6994718462341610928);
void live_h_12(double *state, double *unused, double *out_5591712799096854233);
void live_H_12(double *state, double *unused, double *out_6513616674535761563);
void live_h_35(double *state, double *unused, double *out_7794785283231326495);
void live_H_35(double *state, double *unused, double *out_9187564366848776344);
void live_h_32(double *state, double *unused, double *out_5003200156375512158);
void live_H_32(double *state, double *unused, double *out_6372698284012320776);
void live_h_13(double *state, double *unused, double *out_2460292891122419917);
void live_H_13(double *state, double *unused, double *out_2743087742156254538);
void live_h_14(double *state, double *unused, double *out_955372783900519039);
void live_H_14(double *state, double *unused, double *out_8781379201768247238);
void live_h_33(double *state, double *unused, double *out_2784098689088769788);
void live_H_33(double *state, double *unused, double *out_6037007362209918740);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}