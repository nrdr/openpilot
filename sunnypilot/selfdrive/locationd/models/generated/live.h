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
void live_H(double *in_vec, double *out_2389208833482902619);
void live_err_fun(double *nom_x, double *delta_x, double *out_9144298840548456576);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_2017548937800011486);
void live_H_mod_fun(double *state, double *out_1948696714180442506);
void live_f_fun(double *state, double dt, double *out_9115038122057922510);
void live_F_fun(double *state, double dt, double *out_5289713018579489527);
void live_h_4(double *state, double *unused, double *out_3903146747389348299);
void live_H_4(double *state, double *unused, double *out_827201274497007119);
void live_h_9(double *state, double *unused, double *out_6953719350303596311);
void live_H_9(double *state, double *unused, double *out_586011627867416474);
void live_h_10(double *state, double *unused, double *out_7673381043859446341);
void live_H_10(double *state, double *unused, double *out_8181977835613672674);
void live_h_12(double *state, double *unused, double *out_4486444879177367101);
void live_H_12(double *state, double *unused, double *out_4192255133534954676);
void live_h_35(double *state, double *unused, double *out_2536370331435514193);
void live_H_35(double *state, double *unused, double *out_2539460782875600257);
void live_h_32(double *state, double *unused, double *out_8014081891612290555);
void live_H_32(double *state, double *unused, double *out_894621273164700655);
void live_h_13(double *state, double *unused, double *out_5444430567738801567);
void live_H_13(double *state, double *unused, double *out_8486826080354591894);
void live_h_14(double *state, double *unused, double *out_6953719350303596311);
void live_H_14(double *state, double *unused, double *out_586011627867416474);
void live_h_33(double *state, double *unused, double *out_3013907811955528635);
void live_H_33(double *state, double *unused, double *out_5690017787514457861);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}