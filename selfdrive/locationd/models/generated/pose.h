#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_2591816007629674382);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5111003568722884551);
void pose_H_mod_fun(double *state, double *out_5953397541332519964);
void pose_f_fun(double *state, double dt, double *out_754329157820044725);
void pose_F_fun(double *state, double dt, double *out_6133369954690992745);
void pose_h_4(double *state, double *unused, double *out_516041222348960560);
void pose_H_4(double *state, double *unused, double *out_1338770504403203600);
void pose_h_10(double *state, double *unused, double *out_2447986843515870103);
void pose_H_10(double *state, double *unused, double *out_7155285139208376669);
void pose_h_13(double *state, double *unused, double *out_4078955435366114031);
void pose_H_13(double *state, double *unused, double *out_1873503320929129201);
void pose_h_14(double *state, double *unused, double *out_8824687956191096942);
void pose_H_14(double *state, double *unused, double *out_2624470351936280929);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}