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
void live_H(double *in_vec, double *out_2854810654842821073);
void live_err_fun(double *nom_x, double *delta_x, double *out_1341856485886865860);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_2906985211883189842);
void live_H_mod_fun(double *state, double *out_2004288976045903336);
void live_f_fun(double *state, double dt, double *out_5822669858534757957);
void live_F_fun(double *state, double dt, double *out_8995835072960056703);
void live_h_4(double *state, double *unused, double *out_1473400842048682462);
void live_H_4(double *state, double *unused, double *out_242624528082169420);
void live_h_9(double *state, double *unused, double *out_5966160669624155901);
void live_H_9(double *state, double *unused, double *out_7044594407182278050);
void live_h_10(double *state, double *unused, double *out_7783626268506598272);
void live_H_10(double *state, double *unused, double *out_200256816117678591);
void live_h_12(double *state, double *unused, double *out_8657694423234092109);
void live_H_12(double *state, double *unused, double *out_6623882905124902416);
void live_h_35(double *state, double *unused, double *out_2336154314423969481);
void live_H_35(double *state, double *unused, double *out_3124037529290437956);
void live_h_32(double *state, double *unused, double *out_2569638415045578339);
void live_H_32(double *state, double *unused, double *out_3255202314231178425);
void live_h_13(double *state, double *unused, double *out_7547203726451557696);
void live_H_13(double *state, double *unused, double *out_1363769224610554394);
void live_h_14(double *state, double *unused, double *out_5966160669624155901);
void live_H_14(double *state, double *unused, double *out_7044594407182278050);
void live_h_33(double *state, double *unused, double *out_7338905993309045485);
void live_H_33(double *state, double *unused, double *out_6274594533929295560);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}