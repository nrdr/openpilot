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
void live_H(double *in_vec, double *out_2276221186364774332);
void live_err_fun(double *nom_x, double *delta_x, double *out_2172411237781791657);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_6508502241557307595);
void live_H_mod_fun(double *state, double *out_8823134898497097093);
void live_f_fun(double *state, double dt, double *out_391111295151292151);
void live_F_fun(double *state, double dt, double *out_2226170640283360854);
void live_h_4(double *state, double *unused, double *out_8270546091230864706);
void live_H_4(double *state, double *unused, double *out_3668758719841907692);
void live_h_9(double *state, double *unused, double *out_4438721982435932441);
void live_H_9(double *state, double *unused, double *out_7490766418603196454);
void live_h_10(double *state, double *unused, double *out_8924883884762253013);
void live_H_10(double *state, double *unused, double *out_2382957815788875728);
void live_h_12(double *state, double *unused, double *out_483876791926769905);
void live_H_12(double *state, double *unused, double *out_2712499657200825304);
void live_h_35(double *state, double *unused, double *out_1318906460745872353);
void live_H_35(double *state, double *unused, double *out_7035420777214515068);
void live_h_32(double *state, double *unused, double *out_2558907244891007079);
void live_H_32(double *state, double *unused, double *out_2816721539542605998);
void live_h_13(double *state, double *unused, double *out_7425011303495092404);
void live_H_13(double *state, double *unused, double *out_5012276734700660674);
void live_h_14(double *state, double *unused, double *out_4438721982435932441);
void live_H_14(double *state, double *unused, double *out_7490766418603196454);
void live_h_33(double *state, double *unused, double *out_9187226868567733135);
void live_H_33(double *state, double *unused, double *out_1214737003221322119);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}