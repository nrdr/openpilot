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
void live_H(double *in_vec, double *out_6135547622599143369);
void live_err_fun(double *nom_x, double *delta_x, double *out_2474099822945226414);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_416207936211138814);
void live_H_mod_fun(double *state, double *out_1331424751962839887);
void live_f_fun(double *state, double dt, double *out_6898832997664042401);
void live_F_fun(double *state, double dt, double *out_562528500906443605);
void live_h_4(double *state, double *unused, double *out_6150768739583799811);
void live_H_4(double *state, double *unused, double *out_1094003370714448544);
void live_h_9(double *state, double *unused, double *out_7691777894651695564);
void live_H_9(double *state, double *unused, double *out_5251171107069226027);
void live_h_10(double *state, double *unused, double *out_8526678818648411245);
void live_H_10(double *state, double *unused, double *out_4735474673886811119);
void live_h_12(double *state, double *unused, double *out_6444040462477740558);
void live_H_12(double *state, double *unused, double *out_472904345666854877);
void live_h_35(double *state, double *unused, double *out_4480136207103890606);
void live_H_35(double *state, double *unused, double *out_2272658686658158832);
void live_h_32(double *state, double *unused, double *out_7243008505597260793);
void live_H_32(double *state, double *unused, double *out_4642205817035957524);
void live_h_13(double *state, double *unused, double *out_5708623026986508581);
void live_H_13(double *state, double *unused, double *out_865636014924065382);
void live_h_14(double *state, double *unused, double *out_7691777894651695564);
void live_H_14(double *state, double *unused, double *out_5251171107069226027);
void live_h_33(double *state, double *unused, double *out_3278395025902833006);
void live_H_33(double *state, double *unused, double *out_5423215691297016436);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}