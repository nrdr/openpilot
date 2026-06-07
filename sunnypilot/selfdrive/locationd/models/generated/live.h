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
void live_H(double *in_vec, double *out_8299958186288395057);
void live_err_fun(double *nom_x, double *delta_x, double *out_3260833722657692865);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_4992457405468338621);
void live_H_mod_fun(double *state, double *out_902997691471336112);
void live_f_fun(double *state, double dt, double *out_3908486279749706947);
void live_F_fun(double *state, double dt, double *out_7197428388472595651);
void live_h_4(double *state, double *unused, double *out_6290310728528012633);
void live_H_4(double *state, double *unused, double *out_4255476534121803682);
void live_h_9(double *state, double *unused, double *out_4542855504763564130);
void live_H_9(double *state, double *unused, double *out_6904048604323300464);
void live_h_10(double *state, double *unused, double *out_3600197470332564412);
void live_H_10(double *state, double *unused, double *out_1540364513734939664);
void live_h_12(double *state, double *unused, double *out_2292638746041122962);
void live_H_12(double *state, double *unused, double *out_9171811131555786139);
void live_h_35(double *state, double *unused, double *out_4088484662149404945);
void live_H_35(double *state, double *unused, double *out_7622138591494411058);
void live_h_32(double *state, double *unused, double *out_3452447278615089823);
void live_H_32(double *state, double *unused, double *out_7753303376435151527);
void live_h_13(double *state, double *unused, double *out_8317229002214533788);
void live_H_13(double *state, double *unused, double *out_4799493024476848910);
void live_h_14(double *state, double *unused, double *out_4542855504763564130);
void live_H_14(double *state, double *unused, double *out_6904048604323300464);
void live_h_33(double *state, double *unused, double *out_303979410587844392);
void live_H_33(double *state, double *unused, double *out_7674048477576282954);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}