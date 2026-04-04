#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_6954349063036595351);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_682628527898263653);
void pose_H_mod_fun(double *state, double *out_1843936589147875527);
void pose_f_fun(double *state, double dt, double *out_4568297489233837757);
void pose_F_fun(double *state, double dt, double *out_8898375213134066991);
void pose_h_4(double *state, double *unused, double *out_7637245117322563109);
void pose_H_4(double *state, double *unused, double *out_7021791425393278159);
void pose_h_10(double *state, double *unused, double *out_5758875815588475648);
void pose_H_10(double *state, double *unused, double *out_967659597114898975);
void pose_h_13(double *state, double *unused, double *out_1246309401103887941);
void pose_H_13(double *state, double *unused, double *out_3809517600060945358);
void pose_h_14(double *state, double *unused, double *out_8756863864319304456);
void pose_H_14(double *state, double *unused, double *out_3058550569053793630);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}