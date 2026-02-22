#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_3540814927069874749);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_6824921044159080785);
void pose_H_mod_fun(double *state, double *out_1646016674355801401);
void pose_f_fun(double *state, double dt, double *out_1812064668052849173);
void pose_F_fun(double *state, double dt, double *out_8063307411811769324);
void pose_h_4(double *state, double *unused, double *out_2303598358625783284);
void pose_H_4(double *state, double *unused, double *out_4202065132396157320);
void pose_h_10(double *state, double *unused, double *out_8093621696167248788);
void pose_H_10(double *state, double *unused, double *out_17303435982620736);
void pose_h_13(double *state, double *unused, double *out_5450973548134688447);
void pose_H_13(double *state, double *unused, double *out_989791307063824519);
void pose_h_14(double *state, double *unused, double *out_6736526479382297115);
void pose_H_14(double *state, double *unused, double *out_238824276056672791);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}