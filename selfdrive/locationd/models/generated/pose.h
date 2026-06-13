#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_4130250514567188612);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_3862262940710197433);
void pose_H_mod_fun(double *state, double *out_7881665640335314858);
void pose_f_fun(double *state, double dt, double *out_4623446334203055766);
void pose_F_fun(double *state, double dt, double *out_4287027390918098086);
void pose_h_4(double *state, double *unused, double *out_2134370447906294768);
void pose_H_4(double *state, double *unused, double *out_8745379707467939897);
void pose_h_10(double *state, double *unused, double *out_7905342496395142587);
void pose_H_10(double *state, double *unused, double *out_1049153498394893392);
void pose_h_13(double *state, double *unused, double *out_7764029234789399873);
void pose_H_13(double *state, double *unused, double *out_6489090540909278918);
void pose_h_14(double *state, double *unused, double *out_719626587722978942);
void pose_H_14(double *state, double *unused, double *out_5738123509902127190);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}