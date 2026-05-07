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
void car_err_fun(double *nom_x, double *delta_x, double *out_1038389500972116158);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6418752408535262595);
void car_H_mod_fun(double *state, double *out_2855368609596965229);
void car_f_fun(double *state, double dt, double *out_1397092929687677159);
void car_F_fun(double *state, double dt, double *out_7780451684963738443);
void car_h_25(double *state, double *unused, double *out_894848580994361563);
void car_H_25(double *state, double *unused, double *out_6378349259586456906);
void car_h_24(double *state, double *unused, double *out_6711296683837743925);
void car_H_24(double *state, double *unused, double *out_5414189356014908953);
void car_h_30(double *state, double *unused, double *out_619654518709855674);
void car_H_30(double *state, double *unused, double *out_6249010312443216836);
void car_h_26(double *state, double *unused, double *out_6497940006268570762);
void car_H_26(double *state, double *unused, double *out_2636845940712400682);
void car_h_27(double *state, double *unused, double *out_7293890098408210709);
void car_H_27(double *state, double *unused, double *out_4074247000642791925);
void car_h_29(double *state, double *unused, double *out_3432206621979709057);
void car_H_29(double *state, double *unused, double *out_2360884273773240892);
void car_h_28(double *state, double *unused, double *out_5622082467174375208);
void car_H_28(double *state, double *unused, double *out_2721514743296289682);
void car_h_31(double *state, double *unused, double *out_6998090913890161796);
void car_H_31(double *state, double *unused, double *out_6408995221463417334);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}