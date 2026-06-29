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
void live_H(double *in_vec, double *out_1542702498246132933);
void live_err_fun(double *nom_x, double *delta_x, double *out_1628107869486205435);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_8818675949722627390);
void live_H_mod_fun(double *state, double *out_8930299427766296616);
void live_f_fun(double *state, double dt, double *out_2836727706664481825);
void live_F_fun(double *state, double dt, double *out_7419719310526099148);
void live_h_4(double *state, double *unused, double *out_5588436466555746320);
void live_H_4(double *state, double *unused, double *out_5007889912038706029);
void live_h_9(double *state, double *unused, double *out_9171270006103434512);
void live_H_9(double *state, double *unused, double *out_2279329023225741441);
void live_h_10(double *state, double *unused, double *out_7293117378072894229);
void live_H_10(double *state, double *unused, double *out_2854248433486463475);
void live_h_12(double *state, double *unused, double *out_8947861304080540179);
void live_H_12(double *state, double *unused, double *out_7057595784628112591);
void live_h_35(double *state, double *unused, double *out_9059851006148412664);
void live_H_35(double *state, double *unused, double *out_8643585256756425316);
void live_h_32(double *state, double *unused, double *out_7388883405106442311);
void live_H_32(double *state, double *unused, double *out_5462154041220019412);
void live_h_13(double *state, double *unused, double *out_1621310789514956082);
void live_H_13(double *state, double *unused, double *out_7391170188486985172);
void live_h_14(double *state, double *unused, double *out_9171270006103434512);
void live_H_14(double *state, double *unused, double *out_2279329023225741441);
void live_h_33(double *state, double *unused, double *out_8097753901180277245);
void live_H_33(double *state, double *unused, double *out_5493028252117567712);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}