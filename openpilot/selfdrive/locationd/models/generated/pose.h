#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_4907159739794112728);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_9092805515226665715);
void pose_H_mod_fun(double *state, double *out_8838383476203492205);
void pose_f_fun(double *state, double dt, double *out_1879607716571020306);
void pose_F_fun(double *state, double dt, double *out_5462626924138888369);
void pose_h_4(double *state, double *unused, double *out_1348371912510502215);
void pose_H_4(double *state, double *unused, double *out_5836553387662151839);
void pose_h_10(double *state, double *unused, double *out_9044662776552187559);
void pose_H_10(double *state, double *unused, double *out_4253353556758477164);
void pose_h_13(double *state, double *unused, double *out_4638407917494187653);
void pose_H_13(double *state, double *unused, double *out_2624279562329819038);
void pose_h_14(double *state, double *unused, double *out_6781244107497221472);
void pose_H_14(double *state, double *unused, double *out_8919341819957524135);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}