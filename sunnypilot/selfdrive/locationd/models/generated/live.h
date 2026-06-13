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
void live_H(double *in_vec, double *out_1559796483142858470);
void live_err_fun(double *nom_x, double *delta_x, double *out_1158823509659926478);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_1918451660830380781);
void live_H_mod_fun(double *state, double *out_854640663204881499);
void live_f_fun(double *state, double dt, double *out_6539650260332625911);
void live_F_fun(double *state, double dt, double *out_7210910081196495631);
void live_h_4(double *state, double *unused, double *out_7567122221770474122);
void live_H_4(double *state, double *unused, double *out_1861414237467958017);
void live_h_9(double *state, double *unused, double *out_8225732610563390357);
void live_H_9(double *state, double *unused, double *out_1620224590838367372);
void live_h_10(double *state, double *unused, double *out_6051894379303879490);
void live_H_10(double *state, double *unused, double *out_1647805801540579403);
void live_h_12(double *state, double *unused, double *out_1564673250780725696);
void live_H_12(double *state, double *unused, double *out_3158042170564003778);
void live_h_35(double *state, double *unused, double *out_925673917519646386);
void live_H_35(double *state, double *unused, double *out_1505247819904649359);
void live_h_32(double *state, double *unused, double *out_3793089075367796544);
void live_H_32(double *state, double *unused, double *out_2835756955828457529);
void live_h_13(double *state, double *unused, double *out_3564152967080818994);
void live_H_13(double *state, double *unused, double *out_4390890797381276748);
void live_h_14(double *state, double *unused, double *out_8225732610563390357);
void live_H_14(double *state, double *unused, double *out_1620224590838367372);
void live_h_33(double *state, double *unused, double *out_2420257687766780384);
void live_H_33(double *state, double *unused, double *out_4655804824543506963);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}