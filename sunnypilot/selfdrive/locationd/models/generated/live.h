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
void live_H(double *in_vec, double *out_8940205530638367243);
void live_err_fun(double *nom_x, double *delta_x, double *out_1503788811998879125);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_4759536416550712059);
void live_H_mod_fun(double *state, double *out_8326314613581628050);
void live_f_fun(double *state, double dt, double *out_6664669615054917537);
void live_F_fun(double *state, double dt, double *out_7819384932223495240);
void live_h_4(double *state, double *unused, double *out_5411917409783468316);
void live_H_4(double *state, double *unused, double *out_242727927828823287);
void live_h_9(double *state, double *unused, double *out_3658644674852721895);
void live_H_9(double *state, double *unused, double *out_7529946863093270757);
void live_h_10(double *state, double *unused, double *out_5525971665190453024);
void live_H_10(double *state, double *unused, double *out_1889206646727467220);
void live_h_12(double *state, double *unused, double *out_3686897459098874006);
void live_H_12(double *state, double *unused, double *out_6138530449213909709);
void live_h_35(double *state, double *unused, double *out_6820218212527191510);
void live_H_35(double *state, double *unused, double *out_7791324799873264128);
void live_h_32(double *state, double *unused, double *out_2885338342851954729);
void live_H_32(double *state, double *unused, double *out_609309252470478407);
void live_h_13(double *state, double *unused, double *out_2566720173446584037);
void live_H_13(double *state, double *unused, double *out_3508965939178834011);
void live_h_14(double *state, double *unused, double *out_3658644674852721895);
void live_H_14(double *state, double *unused, double *out_7529946863093270757);
void live_h_33(double *state, double *unused, double *out_8567211826111197295);
void live_H_33(double *state, double *unused, double *out_4640767795234406524);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}