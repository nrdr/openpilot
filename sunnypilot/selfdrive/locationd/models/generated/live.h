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
void live_H(double *in_vec, double *out_6645155946700032626);
void live_err_fun(double *nom_x, double *delta_x, double *out_177089234463896280);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_8874066381492537861);
void live_H_mod_fun(double *state, double *out_1138287493384580966);
void live_f_fun(double *state, double dt, double *out_5299749592198162624);
void live_F_fun(double *state, double dt, double *out_4833006427544483952);
void live_h_4(double *state, double *unused, double *out_650692703109561394);
void live_H_4(double *state, double *unused, double *out_8259443378263029274);
void live_h_9(double *state, double *unused, double *out_5576625170356308466);
void live_H_9(double *state, double *unused, double *out_2900081760182074872);
void live_h_10(double *state, double *unused, double *out_7506979527249190671);
void live_H_10(double *state, double *unused, double *out_1468831454093355526);
void live_h_12(double *state, double *unused, double *out_5158259945061299951);
void live_H_12(double *state, double *unused, double *out_1878185001220296278);
void live_h_35(double *state, double *unused, double *out_1152022906954678238);
void live_H_35(double *state, double *unused, double *out_4623748033545309987);
void live_h_32(double *state, double *unused, double *out_7705339847199609602);
void live_H_32(double *state, double *unused, double *out_8465478147784814568);
void live_h_13(double *state, double *unused, double *out_846941856865624161);
void live_H_13(double *state, double *unused, double *out_4904901257429915490);
void live_h_14(double *state, double *unused, double *out_5576625170356308466);
void live_H_14(double *state, double *unused, double *out_2900081760182074872);
void live_h_33(double *state, double *unused, double *out_5339384340008037740);
void live_H_33(double *state, double *unused, double *out_7774305038184167591);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}