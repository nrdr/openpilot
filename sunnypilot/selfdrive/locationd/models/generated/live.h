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
void live_H(double *in_vec, double *out_1529688808216430989);
void live_err_fun(double *nom_x, double *delta_x, double *out_4967044224042164881);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_1330948206107006698);
void live_H_mod_fun(double *state, double *out_720753714689346523);
void live_f_fun(double *state, double dt, double *out_572746295893429925);
void live_F_fun(double *state, double dt, double *out_8373366643163461823);
void live_h_4(double *state, double *unused, double *out_108803483581900950);
void live_H_4(double *state, double *unused, double *out_3501902408861882273);
void live_h_9(double *state, double *unused, double *out_8773294212679573632);
void live_H_9(double *state, double *unused, double *out_3785316526402565197);
void live_h_10(double *state, double *unused, double *out_7877403160791345148);
void live_H_10(double *state, double *unused, double *out_5365216036759972962);
void live_h_12(double *state, double *unused, double *out_7171038250359548107);
void live_H_12(double *state, double *unused, double *out_1517553999170079522);
void live_h_35(double *state, double *unused, double *out_6673120447055671613);
void live_H_35(double *state, double *unused, double *out_4263117031495093231);
void live_h_32(double *state, double *unused, double *out_8914367309149069123);
void live_H_32(double *state, double *unused, double *out_3950495336607648203);
void live_h_13(double *state, double *unused, double *out_141191134789401673);
void live_H_13(double *state, double *unused, double *out_7383755605372026342);
void live_h_14(double *state, double *unused, double *out_8773294212679573632);
void live_H_14(double *state, double *unused, double *out_3785316526402565197);
void live_h_33(double *state, double *unused, double *out_7735323486667170577);
void live_H_33(double *state, double *unused, double *out_3015316653149582707);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}