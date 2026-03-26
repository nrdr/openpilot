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
void car_err_fun(double *nom_x, double *delta_x, double *out_4564822322339046809);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8056510067509240060);
void car_H_mod_fun(double *state, double *out_3316217084428840761);
void car_f_fun(double *state, double dt, double *out_8033193828085139716);
void car_F_fun(double *state, double dt, double *out_8465394485829840918);
void car_h_25(double *state, double *unused, double *out_1276217745223201951);
void car_H_25(double *state, double *unused, double *out_5876971141483396476);
void car_h_24(double *state, double *unused, double *out_8586393543172648165);
void car_H_24(double *state, double *unused, double *out_3651263357504527914);
void car_h_30(double *state, double *unused, double *out_6605054905530847234);
void car_H_30(double *state, double *unused, double *out_1039719200008220279);
void car_h_26(double *state, double *unused, double *out_1603381637870001589);
void car_H_26(double *state, double *unused, double *out_8828269613352098916);
void car_h_27(double *state, double *unused, double *out_3725455522437643694);
void car_H_27(double *state, double *unused, double *out_1135044111792204632);
void car_h_29(double *state, double *unused, double *out_3123852248310012056);
void car_H_29(double *state, double *unused, double *out_1549950544322612463);
void car_h_28(double *state, double *unused, double *out_7929045577640176143);
void car_H_28(double *state, double *unused, double *out_3532448472746918111);
void car_h_31(double *state, double *unused, double *out_174413647405681216);
void car_H_31(double *state, double *unused, double *out_5846325179606436048);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}