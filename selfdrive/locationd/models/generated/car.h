#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_err_fun(double *nom_x, double *delta_x, double *out_4054919672849218704);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8915081128527086766);
void car_H_mod_fun(double *state, double *out_4619144397706641630);
void car_f_fun(double *state, double dt, double *out_2483477866184858462);
void car_F_fun(double *state, double dt, double *out_264038838668788068);
void car_h_25(double *state, double *unused, double *out_8091982411933785706);
void car_H_25(double *state, double *unused, double *out_1096163747717149953);
void car_h_24(double *state, double *unused, double *out_8508139400512276422);
void car_H_24(double *state, double *unused, double *out_2905548330913358680);
void car_h_30(double *state, double *unused, double *out_1124667247252753212);
void car_H_30(double *state, double *unused, double *out_5820526593774466802);
void car_h_26(double *state, double *unused, double *out_3837712750428540020);
void car_H_26(double *state, double *unused, double *out_4837667066591206177);
void car_h_27(double *state, double *unused, double *out_3090309144272940061);
void car_H_27(double *state, double *unused, double *out_3400266006660814934);
void car_h_29(double *state, double *unused, double *out_142583153917455100);
void car_H_29(double *state, double *unused, double *out_6330757938088858986);
void car_h_28(double *state, double *unused, double *out_1911364123387905584);
void car_H_28(double *state, double *unused, double *out_1248358921019328412);
void car_h_31(double *state, double *unused, double *out_6493078185347264258);
void car_H_31(double *state, double *unused, double *out_1065517785840189525);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}