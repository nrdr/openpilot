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
void live_H(double *in_vec, double *out_7357978864012424758);
void live_err_fun(double *nom_x, double *delta_x, double *out_4510816013994229079);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_693364033156212986);
void live_H_mod_fun(double *state, double *out_3626045406928708157);
void live_f_fun(double *state, double dt, double *out_1807678677906719269);
void live_F_fun(double *state, double dt, double *out_8230882510434730599);
void live_h_4(double *state, double *unused, double *out_9169220998073879834);
void live_H_4(double *state, double *unused, double *out_5980211420275049604);
void live_h_9(double *state, double *unused, double *out_7753744905734496729);
void live_H_9(double *state, double *unused, double *out_5739021773645458959);
void live_h_10(double *state, double *unused, double *out_8547842195429402351);
void live_H_10(double *state, double *unused, double *out_990119551641999297);
void live_h_12(double *state, double *unused, double *out_2300727362347954732);
void live_H_12(double *state, double *unused, double *out_960755012243087809);
void live_h_35(double *state, double *unused, double *out_3968565363033700031);
void live_H_35(double *state, double *unused, double *out_1784808020081925900);
void live_h_32(double *state, double *unused, double *out_1572753770168411700);
void live_H_32(double *state, double *unused, double *out_2482384577961701759);
void live_h_13(double *state, double *unused, double *out_8945005335716539218);
void live_H_13(double *state, double *unused, double *out_5876065989058085324);
void live_h_14(double *state, double *unused, double *out_7753744905734496729);
void live_H_14(double *state, double *unused, double *out_5739021773645458959);
void live_h_33(double *state, double *unused, double *out_6312945760054954886);
void live_H_33(double *state, double *unused, double *out_4935365024720783504);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}