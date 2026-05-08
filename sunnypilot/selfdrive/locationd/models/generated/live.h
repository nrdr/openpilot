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
void live_H(double *in_vec, double *out_8711676374769334264);
void live_err_fun(double *nom_x, double *delta_x, double *out_7618496504359522686);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_4513261443866179615);
void live_H_mod_fun(double *state, double *out_7444727955537705513);
void live_f_fun(double *state, double dt, double *out_6908568461116465442);
void live_F_fun(double *state, double dt, double *out_5988740027661105780);
void live_h_4(double *state, double *unused, double *out_256368173306910944);
void live_H_4(double *state, double *unused, double *out_262843534581450194);
void live_h_9(double *state, double *unused, double *out_8670740592921009329);
void live_H_9(double *state, double *unused, double *out_2626018017698629148);
void live_h_10(double *state, double *unused, double *out_2177213017769715891);
void live_H_10(double *state, double *unused, double *out_3124420855332114810);
void live_h_12(double *state, double *unused, double *out_7751351794045848934);
void live_H_12(double *state, double *unused, double *out_7404284779101000298);
void live_h_35(double *state, double *unused, double *out_4279803989205901742);
void live_H_35(double *state, double *unused, double *out_3103818522791157182);
void live_h_32(double *state, double *unused, double *out_6468988921202204804);
void live_H_32(double *state, double *unused, double *out_5808843035692907119);
void live_h_13(double *state, double *unused, double *out_6949501099429757161);
void live_H_13(double *state, double *unused, double *out_8555726005803675121);
void live_h_14(double *state, double *unused, double *out_8670740592921009329);
void live_H_14(double *state, double *unused, double *out_2626018017698629148);
void live_h_33(double *state, double *unused, double *out_1037117650582024952);
void live_H_33(double *state, double *unused, double *out_6254375527430014786);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}