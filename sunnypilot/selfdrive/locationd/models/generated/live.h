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
void live_H(double *in_vec, double *out_3036418726057858401);
void live_err_fun(double *nom_x, double *delta_x, double *out_6400138726301442272);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_1826329445122271833);
void live_H_mod_fun(double *state, double *out_6457974291552442414);
void live_f_fun(double *state, double dt, double *out_309690422349444880);
void live_F_fun(double *state, double dt, double *out_6719147208926103400);
void live_h_4(double *state, double *unused, double *out_6859405535659575437);
void live_H_4(double *state, double *unused, double *out_2162200994531178713);
void live_h_9(double *state, double *unused, double *out_8102520702996192418);
void live_H_9(double *state, double *unused, double *out_1921011347901588068);
void live_h_10(double *state, double *unused, double *out_6321616552123052879);
void live_H_10(double *state, double *unused, double *out_6628923036192789032);
void live_h_12(double *state, double *unused, double *out_1098947779970719853);
void live_H_12(double *state, double *unused, double *out_1541101969483585046);
void live_h_35(double *state, double *unused, double *out_6122567248414074843);
void live_H_35(double *state, double *unused, double *out_1204461062841428663);
void live_h_32(double *state, double *unused, double *out_3721890745470161692);
void live_H_32(double *state, double *unused, double *out_3420087588005132818);
void live_h_13(double *state, double *unused, double *out_2662241102507448224);
void live_H_13(double *state, double *unused, double *out_4612763812111293304);
void live_h_14(double *state, double *unused, double *out_8102520702996192418);
void live_H_14(double *state, double *unused, double *out_1921011347901588068);
void live_h_33(double *state, double *unused, double *out_4393459599567144712);
void live_H_33(double *state, double *unused, double *out_4355018067480286267);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}