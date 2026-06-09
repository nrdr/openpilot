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
void car_err_fun(double *nom_x, double *delta_x, double *out_2240929505196870859);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6399928478461651909);
void car_H_mod_fun(double *state, double *out_1595360535879665735);
void car_f_fun(double *state, double dt, double *out_8997069209869168713);
void car_F_fun(double *state, double dt, double *out_7229959409724562911);
void car_h_25(double *state, double *unused, double *out_2914933031606639147);
void car_H_25(double *state, double *unused, double *out_6325977497094194070);
void car_h_24(double *state, double *unused, double *out_3259994416654587251);
void car_H_24(double *state, double *unused, double *out_4153327898088694504);
void car_h_30(double *state, double *unused, double *out_967176657284623868);
void car_H_30(double *state, double *unused, double *out_8844310455601442697);
void car_h_26(double *state, double *unused, double *out_5279274400175549600);
void car_H_26(double *state, double *unused, double *out_2584474178220137846);
void car_h_27(double *state, double *unused, double *out_762909623257804728);
void car_H_27(double *state, double *unused, double *out_6669547143801017786);
void car_h_29(double *state, double *unused, double *out_23666804382961433);
void car_H_29(double *state, double *unused, double *out_9092202273793716735);
void car_h_28(double *state, double *unused, double *out_4879820247823152107);
void car_H_28(double *state, double *unused, double *out_4272142782846304307);
void car_h_31(double *state, double *unused, double *out_1998682365902022068);
void car_H_31(double *state, double *unused, double *out_1958266075986786370);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}