#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_984663319399588075);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_4620004245498130179);
void pose_H_mod_fun(double *state, double *out_2437383548313402487);
void pose_f_fun(double *state, double dt, double *out_459534224482781003);
void pose_F_fun(double *state, double dt, double *out_269745697958674308);
void pose_h_4(double *state, double *unused, double *out_3399047557472824354);
void pose_H_4(double *state, double *unused, double *out_3635331030196300591);
void pose_h_10(double *state, double *unused, double *out_2317846875808052133);
void pose_H_10(double *state, double *unused, double *out_18257956474410646);
void pose_h_13(double *state, double *unused, double *out_3170935602771856178);
void pose_H_13(double *state, double *unused, double *out_6847604855528633392);
void pose_h_14(double *state, double *unused, double *out_3292020991111463031);
void pose_H_14(double *state, double *unused, double *out_552542597900928295);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}