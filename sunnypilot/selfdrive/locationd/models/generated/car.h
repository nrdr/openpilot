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
void car_err_fun(double *nom_x, double *delta_x, double *out_7807076482345369651);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1796239112381471799);
void car_H_mod_fun(double *state, double *out_3897023893221819704);
void car_f_fun(double *state, double dt, double *out_2582961016816185380);
void car_F_fun(double *state, double dt, double *out_7148735030780216289);
void car_h_25(double *state, double *unused, double *out_1352881618571586937);
void car_H_25(double *state, double *unused, double *out_5296164332690417533);
void car_h_24(double *state, double *unused, double *out_535289742976937669);
void car_H_24(double *state, double *unused, double *out_1358041125417768224);
void car_h_30(double *state, double *unused, double *out_5417953607778763999);
void car_H_30(double *state, double *unused, double *out_8622883410891525885);
void car_h_26(double *state, double *unused, double *out_4250209806702622262);
void car_H_26(double *state, double *unused, double *out_9037667651564473757);
void car_h_27(double *state, double *unused, double *out_337566216164094023);
void car_H_27(double *state, double *unused, double *out_6448120099091100974);
void car_h_29(double *state, double *unused, double *out_8230505711048617382);
void car_H_29(double *state, double *unused, double *out_9133114755205918069);
void car_h_28(double *state, double *unused, double *out_4664107051496751622);
void car_H_28(double *state, double *unused, double *out_7349999046938307296);
void car_h_31(double *state, double *unused, double *out_2803513011200470104);
void car_H_31(double *state, double *unused, double *out_8782868319911726383);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}