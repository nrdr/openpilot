#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void live_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_9(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_12(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_35(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_32(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_33(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_H(double *in_vec, double *out_6683805272034203612);
void live_err_fun(double *nom_x, double *delta_x, double *out_267681058375514280);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_3022918018003022960);
void live_H_mod_fun(double *state, double *out_8389684320123776834);
void live_f_fun(double *state, double dt, double *out_9204775005299095507);
void live_F_fun(double *state, double dt, double *out_2489853488989643987);
void live_h_4(double *state, double *unused, double *out_8363842912407982022);
void live_H_4(double *state, double *unused, double *out_7270585390890124971);
void live_h_9(double *state, double *unused, double *out_4603502370876193682);
void live_H_9(double *state, double *unused, double *out_3888939747554979175);
void live_h_10(double *state, double *unused, double *out_3091103127278111177);
void live_H_10(double *state, double *unused, double *out_1868837234128108069);
void live_h_12(double *state, double *unused, double *out_166867343808313556);
void live_H_12(double *state, double *unused, double *out_3509030369136976153);
void live_h_35(double *state, double *unused, double *out_9022802437464334833);
void live_H_35(double *state, double *unused, double *out_763467336811962444);
void live_h_32(double *state, double *unused, double *out_8424496584199416451);
void live_H_32(double *state, double *unused, double *out_5037837035395650114);
void live_h_13(double *state, double *unused, double *out_5196079234089042587);
void live_H_13(double *state, double *unused, double *out_6888455424177227192);
void live_h_14(double *state, double *unused, double *out_4603502370876193682);
void live_H_14(double *state, double *unused, double *out_3888939747554979175);
void live_h_33(double *state, double *unused, double *out_4459527346829147900);
void live_H_33(double *state, double *unused, double *out_2387089667826895160);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}