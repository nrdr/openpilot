#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_691514128797402705);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_2118645859809610286);
void pose_H_mod_fun(double *state, double *out_6073294327909702994);
void pose_f_fun(double *state, double dt, double *out_395315253084136488);
void pose_F_fun(double *state, double dt, double *out_3144799740001374156);
void pose_h_4(double *state, double *unused, double *out_7170570279272954882);
void pose_H_4(double *state, double *unused, double *out_2301487118065795422);
void pose_h_10(double *state, double *unused, double *out_2811610427292929098);
void pose_H_10(double *state, double *unused, double *out_4485692655108419471);
void pose_h_13(double *state, double *unused, double *out_5723609330334209216);
void pose_H_13(double *state, double *unused, double *out_910786707266537379);
void pose_h_14(double *state, double *unused, double *out_1904023991098828728);
void pose_H_14(double *state, double *unused, double *out_5384275550361167718);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}