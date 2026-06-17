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
void live_H(double *in_vec, double *out_9006696913720514802);
void live_err_fun(double *nom_x, double *delta_x, double *out_2868816020813261923);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_454761901846924242);
void live_H_mod_fun(double *state, double *out_8882917893773511436);
void live_f_fun(double *state, double dt, double *out_8459425565813000218);
void live_F_fun(double *state, double dt, double *out_2462555470322948476);
void live_h_4(double *state, double *unused, double *out_1641930072528105126);
void live_H_4(double *state, double *unused, double *out_4914350629007336384);
void live_h_9(double *state, double *unused, double *out_3171651838438005922);
void live_H_9(double *state, double *unused, double *out_9071518365362113867);
void live_h_10(double *state, double *unused, double *out_2211963976166732972);
void live_H_10(double *state, double *unused, double *out_8483617762846320735);
void live_h_12(double *state, double *unused, double *out_7411643359759580413);
void live_H_12(double *state, double *unused, double *out_4293251603959742717);
void live_h_35(double *state, double *unused, double *out_8652887395989388897);
void live_H_35(double *state, double *unused, double *out_1547688571634729008);
void live_h_32(double *state, double *unused, double *out_2561250194805103611);
void live_H_32(double *state, double *unused, double *out_1235969592783688585);
void live_h_13(double *state, double *unused, double *out_5757560602225286541);
void live_H_13(double *state, double *unused, double *out_4629214418281909789);
void live_h_14(double *state, double *unused, double *out_3171651838438005922);
void live_H_14(double *state, double *unused, double *out_9071518365362113867);
void live_h_33(double *state, double *unused, double *out_514664095202276709);
void live_H_33(double *state, double *unused, double *out_1602868433004128596);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}