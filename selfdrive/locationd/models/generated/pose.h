#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_8244834270034669277);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5687769365300631080);
void pose_H_mod_fun(double *state, double *out_5729207129571741933);
void pose_f_fun(double *state, double dt, double *out_5327017859701626059);
void pose_F_fun(double *state, double dt, double *out_8075335770489140637);
void pose_h_4(double *state, double *unused, double *out_3181184218861517088);
void pose_H_4(double *state, double *unused, double *out_6784719679909297658);
void pose_h_10(double *state, double *unused, double *out_2256141700394740444);
void pose_H_10(double *state, double *unused, double *out_271565957382003015);
void pose_h_13(double *state, double *unused, double *out_5753684260181993321);
void pose_H_13(double *state, double *unused, double *out_3572445854576964857);
void pose_h_14(double *state, double *unused, double *out_4183173073051920193);
void pose_H_14(double *state, double *unused, double *out_8579235961504881662);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}