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
void live_H(double *in_vec, double *out_5570991021350812638);
void live_err_fun(double *nom_x, double *delta_x, double *out_4013589763866125000);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_7423609559971004050);
void live_H_mod_fun(double *state, double *out_110895816257072451);
void live_f_fun(double *state, double dt, double *out_1938736518378276662);
void live_F_fun(double *state, double dt, double *out_8826082474097981256);
void live_h_4(double *state, double *unused, double *out_1964678385143555185);
void live_H_4(double *state, double *unused, double *out_106476345097059805);
void live_h_9(double *state, double *unused, double *out_5032816012659509064);
void live_H_9(double *state, double *unused, double *out_347665991726650450);
void live_h_10(double *state, double *unused, double *out_7392002951821209719);
void live_H_10(double *state, double *unused, double *out_8640717357006092169);
void live_h_12(double *state, double *unused, double *out_819586881894991911);
void live_H_12(double *state, double *unused, double *out_5125932753129021600);
void live_h_35(double *state, double *unused, double *out_4107342883905163536);
void live_H_35(double *state, double *unused, double *out_3473138402469667181);
void live_h_32(double *state, double *unused, double *out_6875507043096842834);
void live_H_32(double *state, double *unused, double *out_3441726101224449175);
void live_h_13(double *state, double *unused, double *out_638591192476449481);
void live_H_13(double *state, double *unused, double *out_4968516629316975778);
void live_h_14(double *state, double *unused, double *out_5032816012659509064);
void live_H_14(double *state, double *unused, double *out_347665991726650450);
void live_h_33(double *state, double *unused, double *out_9061296782159654476);
void live_H_33(double *state, double *unused, double *out_6623695407108524785);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}