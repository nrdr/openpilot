#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_5792096138533243612);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_7145879757653058560);
void pose_H_mod_fun(double *state, double *out_3034674074733119560);
void pose_f_fun(double *state, double dt, double *out_5494423390909502238);
void pose_F_fun(double *state, double dt, double *out_7397549611683591868);
void pose_h_4(double *state, double *unused, double *out_4176955461475617995);
void pose_H_4(double *state, double *unused, double *out_737133135110788012);
void pose_h_10(double *state, double *unused, double *out_46181122683215881);
void pose_H_10(double *state, double *unused, double *out_1259791951393668272);
void pose_h_13(double *state, double *unused, double *out_4952163822481543057);
void pose_H_13(double *state, double *unused, double *out_3096622328191736012);
void pose_h_14(double *state, double *unused, double *out_4243659524338283765);
void pose_H_14(double *state, double *unused, double *out_2345655297184584284);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}