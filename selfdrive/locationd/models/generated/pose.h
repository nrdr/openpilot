#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_6367311460737761297);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5441199093300877780);
void pose_H_mod_fun(double *state, double *out_1340515713036728892);
void pose_f_fun(double *state, double dt, double *out_3671753857095520812);
void pose_F_fun(double *state, double dt, double *out_6105292692276061193);
void pose_h_4(double *state, double *unused, double *out_9135824683183967603);
void pose_H_4(double *state, double *unused, double *out_4507566093715229829);
void pose_h_10(double *state, double *unused, double *out_9062434780767682717);
void pose_H_10(double *state, double *unused, double *out_198935129897566355);
void pose_h_13(double *state, double *unused, double *out_8160348284583123661);
void pose_H_13(double *state, double *unused, double *out_1295292268382897028);
void pose_h_14(double *state, double *unused, double *out_4269604812988335508);
void pose_H_14(double *state, double *unused, double *out_544325237375745300);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}