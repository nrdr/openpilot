#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_5289520161060537688);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_8611651352423676881);
void pose_H_mod_fun(double *state, double *out_2960483098895628084);
void pose_f_fun(double *state, double dt, double *out_6109586615606219235);
void pose_F_fun(double *state, double dt, double *out_3005971387171110242);
void pose_h_4(double *state, double *unused, double *out_8555068318404903596);
void pose_H_4(double *state, double *unused, double *out_2206322096840915477);
void pose_h_10(double *state, double *unused, double *out_3926024267674485452);
void pose_H_10(double *state, double *unused, double *out_3320228119013668997);
void pose_h_13(double *state, double *unused, double *out_7226674194180226055);
void pose_H_13(double *state, double *unused, double *out_6040077560143439501);
void pose_h_14(double *state, double *unused, double *out_6511557007088322924);
void pose_H_14(double *state, double *unused, double *out_5289110529136287773);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}