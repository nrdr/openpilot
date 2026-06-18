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
void live_H(double *in_vec, double *out_4130738966447008799);
void live_err_fun(double *nom_x, double *delta_x, double *out_34437356787997235);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_552804711757752428);
void live_H_mod_fun(double *state, double *out_603732984763349472);
void live_f_fun(double *state, double dt, double *out_1180416550040042437);
void live_F_fun(double *state, double dt, double *out_2737324782002112328);
void live_h_4(double *state, double *unused, double *out_2549547229480136069);
void live_H_4(double *state, double *unused, double *out_310896974127146190);
void live_h_9(double *state, double *unused, double *out_6174914403547324115);
void live_H_9(double *state, double *unused, double *out_6976321961137301280);
void live_h_10(double *state, double *unused, double *out_3820689350697016859);
void live_H_10(double *state, double *unused, double *out_4578164400832685808);
void live_h_12(double *state, double *unused, double *out_2189486101036330142);
void live_H_12(double *state, double *unused, double *out_6692155351169879186);
void live_h_35(double *state, double *unused, double *out_1440927071675790187);
void live_H_35(double *state, double *unused, double *out_7454122466229829314);
void live_h_32(double *state, double *unused, double *out_8877546282730427822);
void live_H_32(double *state, double *unused, double *out_3186929868186201655);
void live_h_13(double *state, double *unused, double *out_5393931367141153353);
void live_H_13(double *state, double *unused, double *out_7709747702992533521);
void live_h_14(double *state, double *unused, double *out_6174914403547324115);
void live_H_14(double *state, double *unused, double *out_6976321961137301280);
void live_h_33(double *state, double *unused, double *out_4749629470754310795);
void live_H_33(double *state, double *unused, double *out_6206322087884318790);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}