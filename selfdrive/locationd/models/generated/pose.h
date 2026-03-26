#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_4192685534810622048);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5779284205001834883);
void pose_H_mod_fun(double *state, double *out_7935155873385146551);
void pose_f_fun(double *state, double dt, double *out_1369858821784309025);
void pose_F_fun(double *state, double dt, double *out_7622300413093662135);
void pose_h_4(double *state, double *unused, double *out_3773389396917783373);
void pose_H_4(double *state, double *unused, double *out_6737208391502248447);
void pose_h_10(double *state, double *unused, double *out_1400728838140262320);
void pose_H_10(double *state, double *unused, double *out_8006133557618840022);
void pose_h_13(double *state, double *unused, double *out_6743657915002124092);
void pose_H_13(double *state, double *unused, double *out_7875780218904779145);
void pose_h_14(double *state, double *unused, double *out_72437106472348557);
void pose_H_14(double *state, double *unused, double *out_8626747249911930873);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}