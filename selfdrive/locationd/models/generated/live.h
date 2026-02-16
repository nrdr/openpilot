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
void live_H(double *in_vec, double *out_1327444320473021588);
void live_err_fun(double *nom_x, double *delta_x, double *out_7795678917985884017);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_8256705946832377066);
void live_H_mod_fun(double *state, double *out_727042689000009139);
void live_f_fun(double *state, double dt, double *out_7043755894640092651);
void live_F_fun(double *state, double dt, double *out_418851942990016132);
void live_h_4(double *state, double *unused, double *out_7761760385916810576);
void live_H_4(double *state, double *unused, double *out_5572212077643507005);
void live_h_9(double *state, double *unused, double *out_1475447762172666203);
void live_H_9(double *state, double *unused, double *out_8717364259711267128);
void live_h_10(double *state, double *unused, double *out_1430085662680016336);
void live_H_10(double *state, double *unused, double *out_6871073983452005503);
void live_h_12(double *state, double *unused, double *out_2506182089240013632);
void live_H_12(double *state, double *unused, double *out_4951113052595913338);
void live_h_35(double *state, double *unused, double *out_3314474259025404423);
void live_H_35(double *state, double *unused, double *out_2205550020270899629);
void live_h_32(double *state, double *unused, double *out_6182025673689207078);
void live_H_32(double *state, double *unused, double *out_499474492630850308);
void live_h_13(double *state, double *unused, double *out_965941777158067824);
void live_H_13(double *state, double *unused, double *out_6007295783985880826);
void live_h_14(double *state, double *unused, double *out_1475447762172666203);
void live_H_14(double *state, double *unused, double *out_8717364259711267128);
void live_h_33(double *state, double *unused, double *out_763988180292726015);
void live_H_33(double *state, double *unused, double *out_945006984367957975);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}