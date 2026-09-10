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
void car_err_fun(double *nom_x, double *delta_x, double *out_4871606819898921082);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3126068905594632492);
void car_H_mod_fun(double *state, double *out_2333321478402207250);
void car_f_fun(double *state, double dt, double *out_5908808645708551227);
void car_F_fun(double *state, double dt, double *out_504805921377357218);
void car_h_25(double *state, double *unused, double *out_773763266032655983);
void car_H_25(double *state, double *unused, double *out_5050193195117761655);
void car_h_24(double *state, double *unused, double *out_3935012482718175291);
void car_H_24(double *state, double *unused, double *out_5446838499471621150);
void car_h_30(double *state, double *unused, double *out_9033103330958353749);
void car_H_30(double *state, double *unused, double *out_2531860236610513028);
void car_h_26(double *state, double *unused, double *out_6757574513345301615);
void car_H_26(double *state, double *unused, double *out_1745667225356961054);
void car_h_27(double *state, double *unused, double *out_170447381356178466);
void car_H_27(double *state, double *unused, double *out_308266165426569811);
void car_h_29(double *state, double *unused, double *out_2777278608999306495);
void car_H_29(double *state, double *unused, double *out_2021628892296120844);
void car_h_28(double *state, double *unused, double *out_2982999484626031849);
void car_H_28(double *state, double *unused, double *out_7104027909365651418);
void car_h_31(double *state, double *unused, double *out_5997071960317694953);
void car_H_31(double *state, double *unused, double *out_2026482055394055598);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}