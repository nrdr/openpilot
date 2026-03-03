#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_4430854607241578209);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_8029849703839127827);
void pose_H_mod_fun(double *state, double *out_4301683494632340000);
void pose_f_fun(double *state, double dt, double *out_4902648027499170863);
void pose_F_fun(double *state, double dt, double *out_6172052704526337973);
void pose_h_4(double *state, double *unused, double *out_5496881137641670048);
void pose_H_4(double *state, double *unused, double *out_8296978772325252895);
void pose_h_10(double *state, double *unused, double *out_4392166538936845360);
void pose_H_10(double *state, double *unused, double *out_3969889714076716852);
void pose_h_13(double *state, double *unused, double *out_7956955057143480558);
void pose_H_13(double *state, double *unused, double *out_6937491476051965920);
void pose_h_14(double *state, double *unused, double *out_4392676402397196917);
void pose_H_14(double *state, double *unused, double *out_6186524445044814192);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}