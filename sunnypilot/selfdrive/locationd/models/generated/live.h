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
void live_H(double *in_vec, double *out_2074019777263460552);
void live_err_fun(double *nom_x, double *delta_x, double *out_8995784216348379192);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_1998127065847916603);
void live_H_mod_fun(double *state, double *out_7735574733773016711);
void live_f_fun(double *state, double dt, double *out_110706010868568711);
void live_F_fun(double *state, double dt, double *out_4588057761099372271);
void live_h_4(double *state, double *unused, double *out_3202641799041867407);
void live_H_4(double *state, double *unused, double *out_3786274131604041157);
void live_h_9(double *state, double *unused, double *out_2883459429363999103);
void live_H_9(double *state, double *unused, double *out_7373251006841062989);
void live_h_10(double *state, double *unused, double *out_8562402586263914787);
void live_H_10(double *state, double *unused, double *out_1805718974382827824);
void live_h_12(double *state, double *unused, double *out_6168864757353615801);
void live_H_12(double *state, double *unused, double *out_2594984245438691839);
void live_h_35(double *state, double *unused, double *out_5855623664376416055);
void live_H_35(double *state, double *unused, double *out_4247778596098046258);
void live_h_32(double *state, double *unused, double *out_7977689818546551552);
void live_H_32(double *state, double *unused, double *out_9093774526309657334);
void live_h_13(double *state, double *unused, double *out_7906943919737841246);
void live_H_13(double *state, double *unused, double *out_8299432268910494254);
void live_h_14(double *state, double *unused, double *out_2883459429363999103);
void live_H_14(double *state, double *unused, double *out_7373251006841062989);
void live_h_33(double *state, double *unused, double *out_684287335520866095);
void live_H_33(double *state, double *unused, double *out_1097221591459188654);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}