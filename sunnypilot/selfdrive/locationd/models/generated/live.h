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
void live_H(double *in_vec, double *out_5214829693899036770);
void live_err_fun(double *nom_x, double *delta_x, double *out_1507064929069052661);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_9015791635221210339);
void live_H_mod_fun(double *state, double *out_6602379224176641768);
void live_f_fun(double *state, double dt, double *out_7230114518331295846);
void live_F_fun(double *state, double dt, double *out_7848636269960535715);
void live_h_4(double *state, double *unused, double *out_4316297860194419210);
void live_H_4(double *state, double *unused, double *out_1806331083337528774);
void live_h_9(double *state, double *unused, double *out_6131252169739833127);
void live_H_9(double *state, double *unused, double *out_5480887851926918696);
void live_h_10(double *state, double *unused, double *out_5331987511214263527);
void live_H_10(double *state, double *unused, double *out_2321842914481053791);
void live_h_12(double *state, double *unused, double *out_3438348697226732368);
void live_H_12(double *state, double *unused, double *out_3213125324694433021);
void live_h_35(double *state, double *unused, double *out_3958768245541893402);
void live_H_35(double *state, double *unused, double *out_5958688357019446730);
void live_h_32(double *state, double *unused, double *out_4964629530707440273);
void live_H_32(double *state, double *unused, double *out_6686751344482492328);
void live_h_13(double *state, double *unused, double *out_985178628605044393);
void live_H_13(double *state, double *unused, double *out_8064946567246722987);
void live_h_14(double *state, double *unused, double *out_6131252169739833127);
void live_H_14(double *state, double *unused, double *out_5480887851926918696);
void live_h_33(double *state, double *unused, double *out_7470060434386367554);
void live_H_33(double *state, double *unused, double *out_9109245361658304334);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}