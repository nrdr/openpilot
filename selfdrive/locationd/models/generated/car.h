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
void car_err_fun(double *nom_x, double *delta_x, double *out_4362699660511635051);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5242751605747536921);
void car_H_mod_fun(double *state, double *out_4674979810803532886);
void car_f_fun(double *state, double dt, double *out_3154690792987273928);
void car_F_fun(double *state, double dt, double *out_3170479804547101621);
void car_h_25(double *state, double *unused, double *out_2611331197064061038);
void car_H_25(double *state, double *unused, double *out_8976933419978149621);
void car_h_24(double *state, double *unused, double *out_3910887785984043827);
void car_H_24(double *state, double *unused, double *out_167933289972727541);
void car_h_30(double *state, double *unused, double *out_9199159123540356201);
void car_H_30(double *state, double *unused, double *out_6951477695224153368);
void car_h_26(double *state, double *unused, double *out_8304075097267532980);
void car_H_26(double *state, double *unused, double *out_5235430101104093397);
void car_h_27(double *state, double *unused, double *out_3214647081740538555);
void car_H_27(double *state, double *unused, double *out_2274473778050116512);
void car_h_29(double *state, double *unused, double *out_4245911682508349770);
void car_H_29(double *state, double *unused, double *out_4959468434164933607);
void car_h_28(double *state, double *unused, double *out_834475709106320206);
void car_H_28(double *state, double *unused, double *out_6923098705730259858);
void car_h_31(double *state, double *unused, double *out_2768517865415190183);
void car_H_31(double *state, double *unused, double *out_4609221998870741921);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}