#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_8545056502495144785);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_6519300297558606633);
void pose_H_mod_fun(double *state, double *out_3957552065616892558);
void pose_f_fun(double *state, double dt, double *out_7276726461426660421);
void pose_F_fun(double *state, double dt, double *out_3384456444114612704);
void pose_h_4(double *state, double *unused, double *out_474367734226715198);
void pose_H_4(double *state, double *unused, double *out_1890529741135066163);
void pose_h_10(double *state, double *unused, double *out_4018312916377458673);
void pose_H_10(double *state, double *unused, double *out_8902627675171897633);
void pose_h_13(double *state, double *unused, double *out_679811619492670605);
void pose_H_13(double *state, double *unused, double *out_1321744084197266638);
void pose_h_14(double *state, double *unused, double *out_7920144005840861725);
void pose_H_14(double *state, double *unused, double *out_2072711115204418366);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}