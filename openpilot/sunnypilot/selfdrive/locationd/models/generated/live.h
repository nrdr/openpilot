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
void live_H(double *in_vec, double *out_6459051464895103137);
void live_err_fun(double *nom_x, double *delta_x, double *out_8892930710527702071);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_7373878126429598371);
void live_H_mod_fun(double *state, double *out_1271749442849608360);
void live_f_fun(double *state, double dt, double *out_5459521233089108389);
void live_F_fun(double *state, double dt, double *out_5750363842593034199);
void live_h_4(double *state, double *unused, double *out_1110755172737957733);
void live_H_4(double *state, double *unused, double *out_2402806860357706331);
void live_h_9(double *state, double *unused, double *out_8455483958049326389);
void live_H_9(double *state, double *unused, double *out_8756718278087397815);
void live_h_10(double *state, double *unused, double *out_4812109505538478256);
void live_H_10(double *state, double *unused, double *out_6223786743676133683);
void live_h_12(double *state, double *unused, double *out_334317335133721542);
void live_H_12(double *state, double *unused, double *out_3978451516685026665);
void live_h_35(double *state, double *unused, double *out_4742649265013077361);
void live_H_35(double *state, double *unused, double *out_8278917772994869781);
void live_h_32(double *state, double *unused, double *out_8463521793619228880);
void live_H_32(double *state, double *unused, double *out_8147752988054129312);
void live_h_13(double *state, double *unused, double *out_6477074143049903468);
void live_H_13(double *state, double *unused, double *out_4311403132850531581);
void live_h_14(double *state, double *unused, double *out_8455483958049326389);
void live_H_14(double *state, double *unused, double *out_8756718278087397815);
void live_h_33(double *state, double *unused, double *out_1861083314689194525);
void live_H_33(double *state, double *unused, double *out_1917668520278844648);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}