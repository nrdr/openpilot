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
void car_err_fun(double *nom_x, double *delta_x, double *out_5847876798147549820);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_2883173862552733185);
void car_H_mod_fun(double *state, double *out_2377206742402566479);
void car_f_fun(double *state, double dt, double *out_3371715297155196682);
void car_F_fun(double *state, double dt, double *out_8228232517081691855);
void car_h_25(double *state, double *unused, double *out_793166355641725943);
void car_H_25(double *state, double *unused, double *out_6876349105394747900);
void car_h_24(double *state, double *unused, double *out_5030201579456436749);
void car_H_24(double *state, double *unused, double *out_5759009337292026751);
void car_h_30(double *state, double *unused, double *out_5362280840198934186);
void car_H_30(double *state, double *unused, double *out_9052062009807555089);
void car_h_26(double *state, double *unused, double *out_4758964955522456669);
void car_H_26(double *state, double *unused, double *out_3134845786520691676);
void car_h_27(double *state, double *unused, double *out_8228309790070426756);
void car_H_27(double *state, double *unused, double *out_6828467938623611872);
void car_h_29(double *state, double *unused, double *out_4288153769244620290);
void car_H_29(double *state, double *unused, double *out_8541830665493162905);
void car_h_28(double *state, double *unused, double *out_8398312210839592982);
void car_H_28(double *state, double *unused, double *out_4822514391146858137);
void car_h_31(double *state, double *unused, double *out_1068360417926231832);
void car_H_31(double *state, double *unused, double *out_6906995067271708328);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}