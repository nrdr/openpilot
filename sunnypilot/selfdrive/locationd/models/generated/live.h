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
void live_H(double *in_vec, double *out_3128500701950320118);
void live_err_fun(double *nom_x, double *delta_x, double *out_143648692785365278);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_2227672531299395008);
void live_H_mod_fun(double *state, double *out_3320355528959229199);
void live_f_fun(double *state, double dt, double *out_3987538073591765688);
void live_F_fun(double *state, double dt, double *out_2991481152338814488);
void live_h_4(double *state, double *unused, double *out_5773000536822356378);
void live_H_4(double *state, double *unused, double *out_3797458956685637764);
void live_h_9(double *state, double *unused, double *out_2506107600459347575);
void live_H_9(double *state, double *unused, double *out_3556269310056047119);
void live_h_10(double *state, double *unused, double *out_5429011505930073045);
void live_H_10(double *state, double *unused, double *out_727823685000703239);
void live_h_12(double *state, double *unused, double *out_6516847845489985517);
void live_H_12(double *state, double *unused, double *out_1221997451346324031);
void live_h_35(double *state, double *unused, double *out_8890140958858761964);
void live_H_35(double *state, double *unused, double *out_3967560483671337740);
void live_h_32(double *state, double *unused, double *out_7606759713818620676);
void live_H_32(double *state, double *unused, double *out_6751218648089755333);
void live_h_13(double *state, double *unused, double *out_953323954439828957);
void live_H_13(double *state, double *unused, double *out_6958853592359104966);
void live_h_14(double *state, double *unused, double *out_2506107600459347575);
void live_H_14(double *state, double *unused, double *out_3556269310056047119);
void live_h_33(double *state, double *unused, double *out_6051632307469375900);
void live_H_33(double *state, double *unused, double *out_7118117488310195344);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}