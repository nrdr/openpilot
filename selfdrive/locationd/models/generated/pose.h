#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_2368389224522903581);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_6095247978319400369);
void pose_H_mod_fun(double *state, double *out_4445594867889321281);
void pose_f_fun(double *state, double dt, double *out_2757988731602945540);
void pose_F_fun(double *state, double dt, double *out_426903786628305371);
void pose_h_4(double *state, double *unused, double *out_6566999445586651777);
void pose_H_4(double *state, double *unused, double *out_7072626526129509529);
void pose_h_10(double *state, double *unused, double *out_1367284512135170002);
void pose_H_10(double *state, double *unused, double *out_6378919937591133006);
void pose_h_13(double *state, double *unused, double *out_8828797571683696909);
void pose_H_13(double *state, double *unused, double *out_3860352700797176728);
void pose_h_14(double *state, double *unused, double *out_3744289369958305134);
void pose_H_14(double *state, double *unused, double *out_3109385669790025000);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}