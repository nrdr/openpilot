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
void live_H(double *in_vec, double *out_3055848753841483261);
void live_err_fun(double *nom_x, double *delta_x, double *out_8927436461004586096);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_995081447553101873);
void live_H_mod_fun(double *state, double *out_4015743930468489701);
void live_f_fun(double *state, double dt, double *out_1679918631056837275);
void live_F_fun(double *state, double dt, double *out_892272803323792609);
void live_h_4(double *state, double *unused, double *out_2964403515825207716);
void live_H_4(double *state, double *unused, double *out_4086811027477964547);
void live_h_9(double *state, double *unused, double *out_4783281187358422302);
void live_H_9(double *state, double *unused, double *out_7072714110967139599);
void live_h_10(double *state, double *unused, double *out_2230359204991064088);
void live_H_10(double *state, double *unused, double *out_7329835556178099530);
void live_h_12(double *state, double *unused, double *out_4983684331037394902);
void live_H_12(double *state, double *unused, double *out_2294447349564768449);
void live_h_35(double *state, double *unused, double *out_1996488838897370389);
void live_H_35(double *state, double *unused, double *out_451115682760245260);
void live_h_32(double *state, double *unused, double *out_8412571845708200130);
void live_H_32(double *state, double *unused, double *out_6463748820933871096);
void live_h_13(double *state, double *unused, double *out_9197048324624115432);
void live_H_13(double *state, double *unused, double *out_2491663204952937077);
void live_h_14(double *state, double *unused, double *out_4783281187358422302);
void live_H_14(double *state, double *unused, double *out_7072714110967139599);
void live_h_33(double *state, double *unused, double *out_1122130445361000490);
void live_H_33(double *state, double *unused, double *out_3601672687399102864);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}