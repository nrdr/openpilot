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
void live_H(double *in_vec, double *out_1102546546097346885);
void live_err_fun(double *nom_x, double *delta_x, double *out_4263656922737171817);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_7667591008773522511);
void live_H_mod_fun(double *state, double *out_7772898297965727645);
void live_f_fun(double *state, double dt, double *out_4714945908128215909);
void live_F_fun(double *state, double dt, double *out_8559450820311833963);
void live_h_4(double *state, double *unused, double *out_5322079309545859486);
void live_H_4(double *state, double *unused, double *out_8924400505573446475);
void live_h_9(double *state, double *unused, double *out_4374322104072717934);
void live_H_9(double *state, double *unused, double *out_1637181570308999005);
void live_h_10(double *state, double *unused, double *out_6807060551239681054);
void live_H_10(double *state, double *unused, double *out_5696308071683091843);
void live_h_12(double *state, double *unused, double *out_8669544208143295183);
void live_H_12(double *state, double *unused, double *out_3141085191093372145);
void live_h_35(double *state, double *unused, double *out_5933843447274527715);
void live_H_35(double *state, double *unused, double *out_5886648223418385854);
void live_h_32(double *state, double *unused, double *out_8599879934053782994);
void live_H_32(double *state, double *unused, double *out_6860632835444535115);
void live_h_13(double *state, double *unused, double *out_54809952378967615);
void live_H_13(double *state, double *unused, double *out_6147070932988565746);
void live_h_14(double *state, double *unused, double *out_4374322104072717934);
void live_H_14(double *state, double *unused, double *out_1637181570308999005);
void live_h_33(double *state, double *unused, double *out_5522201317853853601);
void live_H_33(double *state, double *unused, double *out_4638847845072875330);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}