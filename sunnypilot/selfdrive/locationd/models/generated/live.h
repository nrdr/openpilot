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
void live_H(double *in_vec, double *out_8948341959620309107);
void live_err_fun(double *nom_x, double *delta_x, double *out_4299704501033999804);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_6063975753215514881);
void live_H_mod_fun(double *state, double *out_6484473106077637597);
void live_f_fun(double *state, double dt, double *out_7972032257608009931);
void live_F_fun(double *state, double dt, double *out_2006188400547034667);
void live_h_4(double *state, double *unused, double *out_5851191942038428821);
void live_H_4(double *state, double *unused, double *out_1953197759695837924);
void live_h_9(double *state, double *unused, double *out_6264004844987479300);
void live_H_9(double *state, double *unused, double *out_2194387406325428569);
void live_h_10(double *state, double *unused, double *out_2838427997212206072);
void live_H_10(double *state, double *unused, double *out_7801443411236313696);
void live_h_12(double *state, double *unused, double *out_2821863544528861965);
void live_H_12(double *state, double *unused, double *out_6972654167727799719);
void live_h_35(double *state, double *unused, double *out_4666119564541390184);
void live_H_35(double *state, double *unused, double *out_5319859817068445300);
void live_h_32(double *state, double *unused, double *out_5023400774179753624);
void live_H_32(double *state, double *unused, double *out_7260698154401454101);
void live_h_13(double *state, double *unused, double *out_5322531791932379688);
void live_H_13(double *state, double *unused, double *out_4109118369085705515);
void live_h_14(double *state, double *unused, double *out_6264004844987479300);
void live_H_14(double *state, double *unused, double *out_2194387406325428569);
void live_h_33(double *state, double *unused, double *out_7486391817844954677);
void live_H_33(double *state, double *unused, double *out_8470416821707302904);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}