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
void car_err_fun(double *nom_x, double *delta_x, double *out_6723804722312945773);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1637419203022386435);
void car_H_mod_fun(double *state, double *out_3837177300373436874);
void car_f_fun(double *state, double dt, double *out_1069481376239403552);
void car_F_fun(double *state, double dt, double *out_811488727004941991);
void car_h_25(double *state, double *unused, double *out_2604343454635407771);
void car_H_25(double *state, double *unused, double *out_1066514524811227966);
void car_h_24(double *state, double *unused, double *out_7708663193811877711);
void car_H_24(double *state, double *unused, double *out_3243728948418377939);
void car_h_30(double *state, double *unused, double *out_7277894899904281788);
void car_H_30(double *state, double *unused, double *out_3584847483318476593);
void car_h_26(double *state, double *unused, double *out_4569985351655594620);
void car_H_26(double *state, double *unused, double *out_2674988794062828258);
void car_h_27(double *state, double *unused, double *out_7606016722296253416);
void car_H_27(double *state, double *unused, double *out_1410084171518051682);
void car_h_29(double *state, double *unused, double *out_157248534524419025);
void car_H_29(double *state, double *unused, double *out_4095078827632868777);
void car_h_28(double *state, double *unused, double *out_1375952449710587349);
void car_H_28(double *state, double *unused, double *out_987320189436661797);
void car_h_31(double *state, double *unused, double *out_3365251309365753549);
void car_H_31(double *state, double *unused, double *out_3301196896296179734);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}