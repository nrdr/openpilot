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
void car_err_fun(double *nom_x, double *delta_x, double *out_6502015734495733948);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_315300592301695071);
void car_H_mod_fun(double *state, double *out_3700698090332376439);
void car_f_fun(double *state, double dt, double *out_5551964765070894208);
void car_F_fun(double *state, double dt, double *out_3387046927581760157);
void car_h_25(double *state, double *unused, double *out_7748246721111864678);
void car_H_25(double *state, double *unused, double *out_1553539153054996027);
void car_h_24(double *state, double *unused, double *out_3014180275814606991);
void car_H_24(double *state, double *unused, double *out_7665139734585360364);
void car_h_30(double *state, double *unused, double *out_556697608256352882);
void car_H_30(double *state, double *unused, double *out_1424200205911755957);
void car_h_26(double *state, double *unused, double *out_5842343909157496264);
void car_H_26(double *state, double *unused, double *out_2187964165819060197);
void car_h_27(double *state, double *unused, double *out_8691756574013527113);
void car_H_27(double *state, double *unused, double *out_750563105888668954);
void car_h_29(double *state, double *unused, double *out_3841254473025276130);
void car_H_29(double *state, double *unused, double *out_2463925832758219987);
void car_h_28(double *state, double *unused, double *out_3355945982282175357);
void car_H_28(double *state, double *unused, double *out_7546324849827750561);
void car_h_31(double *state, double *unused, double *out_7061047824343664588);
void car_H_31(double *state, double *unused, double *out_1584185114931956455);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}