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
void car_err_fun(double *nom_x, double *delta_x, double *out_1150556946497607115);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6384736535090160916);
void car_H_mod_fun(double *state, double *out_8501357178821987276);
void car_f_fun(double *state, double dt, double *out_1001507699327886070);
void car_F_fun(double *state, double dt, double *out_679377826983824795);
void car_h_25(double *state, double *unused, double *out_7405352995896305810);
void car_H_25(double *state, double *unused, double *out_6422406244898072663);
void car_h_24(double *state, double *unused, double *out_7209079107772895242);
void car_H_24(double *state, double *unused, double *out_2864480646095749527);
void car_h_30(double *state, double *unused, double *out_4074075913132213312);
void car_H_30(double *state, double *unused, double *out_494284096593544092);
void car_h_26(double *state, double *unused, double *out_888304084549079920);
void car_H_26(double *state, double *unused, double *out_8282834509937422729);
void car_h_27(double *state, double *unused, double *out_6039717810152400161);
void car_H_27(double *state, double *unused, double *out_1680479215206880819);
void car_h_29(double *state, double *unused, double *out_4946467499308263130);
void car_H_29(double *state, double *unused, double *out_1004515440907936276);
void car_h_28(double *state, double *unused, double *out_1038044542491554516);
void car_H_28(double *state, double *unused, double *out_8476240959145962426);
void car_h_31(double *state, double *unused, double *out_3278125820992573365);
void car_H_31(double *state, double *unused, double *out_6391760283021112235);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}