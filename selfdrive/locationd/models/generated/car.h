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
void car_err_fun(double *nom_x, double *delta_x, double *out_8605772291161719487);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4228750367841829642);
void car_H_mod_fun(double *state, double *out_5142586022554558866);
void car_f_fun(double *state, double dt, double *out_880788400512161224);
void car_F_fun(double *state, double dt, double *out_833648737121717376);
void car_h_25(double *state, double *unused, double *out_1185806909084788592);
void car_H_25(double *state, double *unused, double *out_1619605372565067189);
void car_h_24(double *state, double *unused, double *out_7335919933373101635);
void car_H_24(double *state, double *unused, double *out_1938320226237255947);
void car_h_30(double *state, double *unused, double *out_4823256437338810942);
void car_H_30(double *state, double *unused, double *out_898727585942181438);
void car_h_26(double *state, double *unused, double *out_178416830322034703);
void car_H_26(double *state, double *unused, double *out_5361108691439123413);
void car_h_27(double *state, double *unused, double *out_8543100244756070698);
void car_H_27(double *state, double *unused, double *out_3122321657126124655);
void car_h_29(double *state, double *unused, double *out_8397580420535415727);
void car_H_29(double *state, double *unused, double *out_1408958930256573622);
void car_h_28(double *state, double *unused, double *out_2794488995261206528);
void car_H_28(double *state, double *unused, double *out_3673440086812956952);
void car_h_31(double *state, double *unused, double *out_5781508255596243902);
void car_H_31(double *state, double *unused, double *out_1588959410688106761);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}