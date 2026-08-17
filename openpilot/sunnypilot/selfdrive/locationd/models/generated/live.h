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
void live_H(double *in_vec, double *out_5371198434298083471);
void live_err_fun(double *nom_x, double *delta_x, double *out_857469500247309286);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_2658255644554600878);
void live_H_mod_fun(double *state, double *out_3948934617639328320);
void live_f_fun(double *state, double dt, double *out_2645775662927499447);
void live_F_fun(double *state, double dt, double *out_4989110455173277588);
void live_h_4(double *state, double *unused, double *out_8436331368387019870);
void live_H_4(double *state, double *unused, double *out_4119163280182454060);
void live_h_9(double *state, double *unused, double *out_3886782163743290342);
void live_H_9(double *state, double *unused, double *out_7040361858262650086);
void live_h_10(double *state, double *unused, double *out_4445271283345487137);
void live_H_10(double *state, double *unused, double *out_7994053868468811079);
void live_h_12(double *state, double *unused, double *out_6004152949730683566);
void live_H_12(double *state, double *unused, double *out_9138619688214415855);
void live_h_35(double *state, double *unused, double *out_4735035633599723422);
void live_H_35(double *state, double *unused, double *out_7485825337555061436);
void live_h_32(double *state, double *unused, double *out_6798580222435201956);
void live_H_32(double *state, double *unused, double *out_9020080398821481379);
void live_h_13(double *state, double *unused, double *out_8173777524598496161);
void live_H_13(double *state, double *unused, double *out_1851125892824586880);
void live_h_14(double *state, double *unused, double *out_3886782163743290342);
void live_H_14(double *state, double *unused, double *out_7040361858262650086);
void live_h_33(double *state, double *unused, double *out_3494882841377005287);
void live_H_33(double *state, double *unused, double *out_7810361731515632576);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}