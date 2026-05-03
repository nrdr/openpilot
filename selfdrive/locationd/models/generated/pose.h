#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_6247163002975687744);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_2784495282432373016);
void pose_H_mod_fun(double *state, double *out_662979392671356586);
void pose_f_fun(double *state, double dt, double *out_5358842043988680887);
void pose_F_fun(double *state, double dt, double *out_6970610951587922797);
void pose_h_4(double *state, double *unused, double *out_3613363558024225199);
void pose_H_4(double *state, double *unused, double *out_8770780261124510538);
void pose_h_10(double *state, double *unused, double *out_7325246586980236980);
void pose_H_10(double *state, double *unused, double *out_8143750738918534214);
void pose_h_13(double *state, double *unused, double *out_4440237870440636920);
void pose_H_13(double *state, double *unused, double *out_5558506435792177737);
void pose_h_14(double *state, double *unused, double *out_854572314087465107);
void pose_H_14(double *state, double *unused, double *out_4807539404785026009);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}