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
void live_H(double *in_vec, double *out_618532831730904574);
void live_err_fun(double *nom_x, double *delta_x, double *out_7574003599898666436);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_8974096979235848208);
void live_H_mod_fun(double *state, double *out_2123905216018727101);
void live_f_fun(double *state, double dt, double *out_6060447419256006998);
void live_F_fun(double *state, double dt, double *out_6620056552854461326);
void live_h_4(double *state, double *unused, double *out_3326015762016290916);
void live_H_4(double *state, double *unused, double *out_2252225211289884121);
void live_h_9(double *state, double *unused, double *out_3878394168554544708);
void live_H_9(double *state, double *unused, double *out_2493414857919474766);
void live_h_10(double *state, double *unused, double *out_7917513474022082247);
void live_H_10(double *state, double *unused, double *out_8116415592447393913);
void live_h_12(double *state, double *unused, double *out_4768493217722319308);
void live_H_12(double *state, double *unused, double *out_7271681619321845916);
void live_h_35(double *state, double *unused, double *out_4162076674502017546);
void live_H_35(double *state, double *unused, double *out_5618887268662491497);
void live_h_32(double *state, double *unused, double *out_4315097490076407561);
void live_H_32(double *state, double *unused, double *out_6592871880688640758);
void live_h_13(double *state, double *unused, double *out_2860830632957595733);
void live_H_13(double *state, double *unused, double *out_2349710728936114349);
void live_h_14(double *state, double *unused, double *out_3878394168554544708);
void live_H_14(double *state, double *unused, double *out_2493414857919474766);
void live_h_33(double *state, double *unused, double *out_5723982898332034956);
void live_H_33(double *state, double *unused, double *out_8769444273301349101);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}