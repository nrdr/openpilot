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
void live_H(double *in_vec, double *out_2858993063142457269);
void live_err_fun(double *nom_x, double *delta_x, double *out_1899205853711625603);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_5477866396127576777);
void live_H_mod_fun(double *state, double *out_8523838669620830941);
void live_f_fun(double *state, double dt, double *out_7249694360712121235);
void live_F_fun(double *state, double dt, double *out_6963623318978781225);
void live_h_4(double *state, double *unused, double *out_8393517102248927738);
void live_H_4(double *state, double *unused, double *out_5526333662633462503);
void live_h_9(double *state, double *unused, double *out_5835323603885368090);
void live_H_9(double *state, double *unused, double *out_5285144016003871858);
void live_h_10(double *state, double *unused, double *out_6811634206222762431);
void live_H_10(double *state, double *unused, double *out_9163804836270788424);
void live_h_12(double *state, double *unused, double *out_1324082029952996012);
void live_H_12(double *state, double *unused, double *out_506877254601500708);
void live_h_35(double *state, double *unused, double *out_5712630714040932272);
void live_H_35(double *state, double *unused, double *out_2159671605260855127);
void live_h_32(double *state, double *unused, double *out_2900428996208123986);
void live_H_32(double *state, double *unused, double *out_5022343942141930594);
void live_h_13(double *state, double *unused, double *out_7350732988404282993);
void live_H_13(double *state, double *unused, double *out_3418854762709362613);
void live_h_14(double *state, double *unused, double *out_5835323603885368090);
void live_H_14(double *state, double *unused, double *out_5285144016003871858);
void live_h_33(double *state, double *unused, double *out_5667934544683579491);
void live_H_33(double *state, double *unused, double *out_990885399378002477);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}