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
void car_err_fun(double *nom_x, double *delta_x, double *out_5914545950975006415);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8362401152188577782);
void car_H_mod_fun(double *state, double *out_6504767178938023689);
void car_f_fun(double *state, double dt, double *out_3220054145890219252);
void car_F_fun(double *state, double dt, double *out_5400409281172744351);
void car_h_25(double *state, double *unused, double *out_6651060439878130261);
void car_H_25(double *state, double *unused, double *out_1601075353753358849);
void car_h_24(double *state, double *unused, double *out_2927958275900255539);
void car_H_24(double *state, double *unused, double *out_576139069853791124);
void car_h_30(double *state, double *unused, double *out_3013610911624107911);
void car_H_30(double *state, double *unused, double *out_917257604753889778);
void car_h_26(double *state, double *unused, double *out_6636823697819446565);
void car_H_26(double *state, double *unused, double *out_5342578672627415073);
void car_h_27(double *state, double *unused, double *out_2813714461824580590);
void car_H_27(double *state, double *unused, double *out_3140851675937832995);
void car_h_29(double *state, double *unused, double *out_9034091644671594559);
void car_H_29(double *state, double *unused, double *out_1427488949068281962);
void car_h_28(double *state, double *unused, double *out_3417030346501058107);
void car_H_28(double *state, double *unused, double *out_3654910068001248612);
void car_h_31(double *state, double *unused, double *out_6926254502162636150);
void car_H_31(double *state, double *unused, double *out_5968786774860766549);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}