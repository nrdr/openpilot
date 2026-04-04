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
void live_H(double *in_vec, double *out_8099090280617265557);
void live_err_fun(double *nom_x, double *delta_x, double *out_8616936622381152792);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_6372220603140263472);
void live_H_mod_fun(double *state, double *out_551687567464173381);
void live_f_fun(double *state, double dt, double *out_3974209228624480001);
void live_F_fun(double *state, double dt, double *out_1984298082522184441);
void live_h_4(double *state, double *unused, double *out_8788603450120353834);
void live_H_4(double *state, double *unused, double *out_3683573872076633409);
void live_h_9(double *state, double *unused, double *out_8950408347128931388);
void live_H_9(double *state, double *unused, double *out_3603645063187814061);
void live_h_10(double *state, double *unused, double *out_1692190802086146600);
void live_H_10(double *state, double *unused, double *out_5760154506558122350);
void live_h_12(double *state, double *unused, double *out_7198110186115264477);
void live_H_12(double *state, double *unused, double *out_3062474847029039742);
void live_h_35(double *state, double *unused, double *out_7114103103964691035);
void live_H_35(double *state, double *unused, double *out_316911814704026033);
void live_h_32(double *state, double *unused, double *out_3772583737617202307);
void live_H_32(double *state, double *unused, double *out_1623926522628982768);
void live_h_13(double *state, double *unused, double *out_3252718479061451818);
void live_H_13(double *state, double *unused, double *out_8739592071808218130);
void live_h_14(double *state, double *unused, double *out_8950408347128931388);
void live_H_14(double *state, double *unused, double *out_3603645063187814061);
void live_h_33(double *state, double *unused, double *out_4773055308605215211);
void live_H_33(double *state, double *unused, double *out_2833645189934831571);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}