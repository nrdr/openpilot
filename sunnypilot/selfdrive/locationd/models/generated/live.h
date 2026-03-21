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
void live_H(double *in_vec, double *out_2524381842152133424);
void live_err_fun(double *nom_x, double *delta_x, double *out_4743954093650827909);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_6541192548427371848);
void live_H_mod_fun(double *state, double *out_6948399102000392402);
void live_f_fun(double *state, double dt, double *out_5420927852494057357);
void live_F_fun(double *state, double dt, double *out_480988481017209032);
void live_h_4(double *state, double *unused, double *out_2152418127975099250);
void live_H_4(double *state, double *unused, double *out_3027082177242871994);
void live_h_9(double *state, double *unused, double *out_7175597113754865552);
void live_H_9(double *state, double *unused, double *out_2785892530613281349);
void live_h_10(double *state, double *unused, double *out_9063048154823698983);
void live_H_10(double *state, double *unused, double *out_2046773163460130080);
void live_h_12(double *state, double *unused, double *out_9028464020484168633);
void live_H_12(double *state, double *unused, double *out_2405983152195278327);
void live_h_35(double *state, double *unused, double *out_1308561108190389167);
void live_H_35(double *state, double *unused, double *out_339579880129735382);
void live_h_32(double *state, double *unused, double *out_6514839435315817707);
void live_H_32(double *state, double *unused, double *out_4001424895603371506);
void live_h_13(double *state, double *unused, double *out_8075551276184815346);
void live_H_13(double *state, double *unused, double *out_1419709876789956939);
void live_h_14(double *state, double *unused, double *out_7175597113754865552);
void live_H_14(double *state, double *unused, double *out_2785892530613281349);
void live_h_33(double *state, double *unused, double *out_7986090924341803166);
void live_H_33(double *state, double *unused, double *out_3490136884768592986);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}