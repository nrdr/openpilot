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
void car_err_fun(double *nom_x, double *delta_x, double *out_7943227697497537519);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8231763659560642989);
void car_H_mod_fun(double *state, double *out_1772575113865111364);
void car_f_fun(double *state, double dt, double *out_9061986206676983437);
void car_F_fun(double *state, double dt, double *out_4940146509446460471);
void car_h_25(double *state, double *unused, double *out_5434694338703959964);
void car_H_25(double *state, double *unused, double *out_7420613112047125873);
void car_h_24(double *state, double *unused, double *out_1960804875757307856);
void car_H_24(double *state, double *unused, double *out_8853481362656926177);
void car_h_30(double *state, double *unused, double *out_5709888400988465853);
void car_H_30(double *state, double *unused, double *out_6498434631534817545);
void car_h_26(double *state, double *unused, double *out_392631034744728537);
void car_H_26(double *state, double *unused, double *out_7284627642788369519);
void car_h_27(double *state, double *unused, double *out_8010376467344746007);
void car_H_27(double *state, double *unused, double *out_8722028702718760762);
void car_h_29(double *state, double *unused, double *out_7735182405060240118);
void car_H_29(double *state, double *unused, double *out_7008665975849209729);
void car_h_28(double *state, double *unused, double *out_7831962285556107958);
void car_H_28(double *state, double *unused, double *out_8972296247414535980);
void car_h_31(double *state, double *unused, double *out_5591881007055089109);
void car_H_31(double *state, double *unused, double *out_6658419540555018043);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}