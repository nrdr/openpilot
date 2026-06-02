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
void car_err_fun(double *nom_x, double *delta_x, double *out_8832626908720954561);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_2522883866214001661);
void car_H_mod_fun(double *state, double *out_277385038656934078);
void car_f_fun(double *state, double dt, double *out_9092085706175131249);
void car_F_fun(double *state, double dt, double *out_1249960539446179337);
void car_h_25(double *state, double *unused, double *out_2673705911985982000);
void car_H_25(double *state, double *unused, double *out_3800433677302299226);
void car_h_24(double *state, double *unused, double *out_2831627246909073010);
void car_H_24(double *state, double *unused, double *out_2010951953720477739);
void car_h_30(double *state, double *unused, double *out_963743616268040350);
void car_H_30(double *state, double *unused, double *out_1282100718795050599);
void car_h_26(double *state, double *unused, double *out_205893471107221540);
void car_H_26(double *state, double *unused, double *out_7541936996176355450);
void car_h_27(double *state, double *unused, double *out_1751655003312249533);
void car_H_27(double *state, double *unused, double *out_941493352388892618);
void car_h_29(double *state, double *unused, double *out_6189650832103365297);
void car_H_29(double *state, double *unused, double *out_771869374480658415);
void car_h_28(double *state, double *unused, double *out_6654001816331977120);
void car_H_28(double *state, double *unused, double *out_5854268391550188989);
void car_h_31(double *state, double *unused, double *out_2948899974270487889);
void car_H_31(double *state, double *unused, double *out_3769787715425338798);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}