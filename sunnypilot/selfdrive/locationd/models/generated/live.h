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
void live_H(double *in_vec, double *out_4512666438885581513);
void live_err_fun(double *nom_x, double *delta_x, double *out_4031180073159335682);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_4065542627235079063);
void live_H_mod_fun(double *state, double *out_5070283276953840313);
void live_f_fun(double *state, double dt, double *out_2545508911344917287);
void live_F_fun(double *state, double dt, double *out_343881439386011023);
void live_h_4(double *state, double *unused, double *out_3407031775047601428);
void live_H_4(double *state, double *unused, double *out_4053269861288040201);
void live_h_9(double *state, double *unused, double *out_7449819593555840892);
void live_H_9(double *state, double *unused, double *out_7106255277157063945);
void live_h_10(double *state, double *unused, double *out_2413392195942340603);
void live_H_10(double *state, double *unused, double *out_7801116977648397673);
void live_h_12(double *state, double *unused, double *out_5305111299919525959);
void live_H_12(double *state, double *unused, double *out_9072726269320001996);
void live_h_35(double *state, double *unused, double *out_3133912486578903006);
void live_H_35(double *state, double *unused, double *out_7419931918660647577);
void live_h_32(double *state, double *unused, double *out_5712592220098135410);
void live_H_32(double *state, double *unused, double *out_3201232680988738507);
void live_h_13(double *state, double *unused, double *out_2958422905186827684);
void live_H_13(double *state, double *unused, double *out_435927285041935528);
void live_h_14(double *state, double *unused, double *out_7449819593555840892);
void live_H_14(double *state, double *unused, double *out_7106255277157063945);
void live_h_33(double *state, double *unused, double *out_6823788475900224132);
void live_H_33(double *state, double *unused, double *out_7876255150410046435);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}