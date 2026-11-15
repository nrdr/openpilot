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
void live_H(double *in_vec, double *out_6147462710355946381);
void live_err_fun(double *nom_x, double *delta_x, double *out_2536211488417901586);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_8760824268814220563);
void live_H_mod_fun(double *state, double *out_6292983617387996245);
void live_f_fun(double *state, double dt, double *out_7431124583616387030);
void live_F_fun(double *state, double dt, double *out_6691027753558815274);
void live_h_4(double *state, double *unused, double *out_2409149368843110848);
void live_H_4(double *state, double *unused, double *out_7553810432735845774);
void live_h_9(double *state, double *unused, double *out_6135759083812981851);
void live_H_9(double *state, double *unused, double *out_266591497471398304);
void live_h_10(double *state, double *unused, double *out_7035822671495905613);
void live_H_10(double *state, double *unused, double *out_4661826401481453263);
void live_h_12(double *state, double *unused, double *out_202386628064213722);
void live_H_12(double *state, double *unused, double *out_4511675263930972846);
void live_h_35(double *state, double *unused, double *out_6247539626617663833);
void live_H_35(double *state, double *unused, double *out_4187148375363238398);
void live_h_32(double *state, double *unused, double *out_7325229726952300372);
void live_H_32(double *state, double *unused, double *out_7641661437466406332);
void live_h_13(double *state, double *unused, double *out_6582043015243170147);
void live_H_13(double *state, double *unused, double *out_6558076644110356910);
void live_h_14(double *state, double *unused, double *out_6135759083812981851);
void live_H_14(double *state, double *unused, double *out_266591497471398304);
void live_h_33(double *state, double *unused, double *out_8091945779618002267);
void live_H_33(double *state, double *unused, double *out_1036591370724380794);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}