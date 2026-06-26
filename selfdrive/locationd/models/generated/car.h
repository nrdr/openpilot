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
void car_err_fun(double *nom_x, double *delta_x, double *out_4389560420667368012);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1199878704872894309);
void car_H_mod_fun(double *state, double *out_6417922497196987730);
void car_f_fun(double *state, double dt, double *out_1669924709419634396);
void car_F_fun(double *state, double dt, double *out_4839400418837824584);
void car_h_25(double *state, double *unused, double *out_3961494978192292931);
void car_H_25(double *state, double *unused, double *out_7125129751327899046);
void car_h_24(double *state, double *unused, double *out_7397304961143838739);
void car_H_24(double *state, double *unused, double *out_4947915327720749073);
void car_h_30(double *state, double *unused, double *out_3360076820578929377);
void car_H_30(double *state, double *unused, double *out_4606796792820650419);
void car_h_26(double *state, double *unused, double *out_1641596447081916268);
void car_H_26(double *state, double *unused, double *out_7580111003507596346);
void car_h_27(double *state, double *unused, double *out_5464705683076782243);
void car_H_27(double *state, double *unused, double *out_2383202721636707202);
void car_h_29(double *state, double *unused, double *out_5621892351427911388);
void car_H_29(double *state, double *unused, double *out_4096565448506258235);
void car_h_28(double *state, double *unused, double *out_463032415415936598);
void car_H_28(double *state, double *unused, double *out_9178964465575788809);
void car_h_31(double *state, double *unused, double *out_6721983838696586244);
void car_H_31(double *state, double *unused, double *out_6953902901274244870);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}