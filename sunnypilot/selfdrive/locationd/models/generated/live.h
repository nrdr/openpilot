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
void live_H(double *in_vec, double *out_3011646630973583044);
void live_err_fun(double *nom_x, double *delta_x, double *out_1511149081826283148);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_9200261143609610845);
void live_H_mod_fun(double *state, double *out_42660656178228858);
void live_f_fun(double *state, double dt, double *out_7913910528854127501);
void live_F_fun(double *state, double dt, double *out_5161730821922085353);
void live_h_4(double *state, double *unused, double *out_8051169575374330556);
void live_H_4(double *state, double *unused, double *out_2857569143436036617);
void live_h_9(double *state, double *unused, double *out_330167688965919285);
void live_H_9(double *state, double *unused, double *out_2616379496806445972);
void live_h_10(double *state, double *unused, double *out_2444597570137146349);
void live_H_10(double *state, double *unused, double *out_8368953648824249984);
void live_h_12(double *state, double *unused, double *out_638335462177984137);
void live_H_12(double *state, double *unused, double *out_2161887264595925178);
void live_h_35(double *state, double *unused, double *out_8721366272868562903);
void live_H_35(double *state, double *unused, double *out_509092913936570759);
void live_h_32(double *state, double *unused, double *out_4577849530445348219);
void live_H_32(double *state, double *unused, double *out_1483077525962720020);
void live_h_13(double *state, double *unused, double *out_4961080552867801778);
void live_H_13(double *state, double *unused, double *out_2408097237983068272);
void live_h_14(double *state, double *unused, double *out_330167688965919285);
void live_H_14(double *state, double *unused, double *out_2616379496806445972);
void live_h_33(double *state, double *unused, double *out_1741327876190558045);
void live_H_33(double *state, double *unused, double *out_3659649918575428363);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}