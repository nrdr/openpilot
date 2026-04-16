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
void car_err_fun(double *nom_x, double *delta_x, double *out_6914020720384558746);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8514798395213178956);
void car_H_mod_fun(double *state, double *out_5803926359982974418);
void car_f_fun(double *state, double dt, double *out_6397895696464282109);
void car_F_fun(double *state, double dt, double *out_2165626238860456832);
void car_h_25(double *state, double *unused, double *out_8926923116900114537);
void car_H_25(double *state, double *unused, double *out_900234534798309578);
void car_h_24(double *state, double *unused, double *out_6062068703488888029);
void car_H_24(double *state, double *unused, double *out_55237926014614179);
void car_h_30(double *state, double *unused, double *out_1638548306055387894);
void car_H_30(double *state, double *unused, double *out_1618098423708939049);
void car_h_26(double *state, double *unused, double *out_2466098138906344713);
void car_H_26(double *state, double *unused, double *out_4641737853672365802);
void car_h_27(double *state, double *unused, double *out_3964543119218821305);
void car_H_27(double *state, double *unused, double *out_556664888091485862);
void car_h_29(double *state, double *unused, double *out_2806292107131529631);
void car_H_29(double *state, double *unused, double *out_2128329768023331233);
void car_h_28(double *state, double *unused, double *out_5685891490224733171);
void car_H_28(double *state, double *unused, double *out_2954069249046199341);
void car_h_31(double *state, double *unused, double *out_413501244186858827);
void car_H_31(double *state, double *unused, double *out_5267945955905717278);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}