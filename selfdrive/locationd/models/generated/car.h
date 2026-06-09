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
void car_err_fun(double *nom_x, double *delta_x, double *out_427394908214603769);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6917755431586495523);
void car_H_mod_fun(double *state, double *out_5029836486716929516);
void car_f_fun(double *state, double dt, double *out_8683428782768045604);
void car_F_fun(double *state, double dt, double *out_2206128918366291311);
void car_h_25(double *state, double *unused, double *out_2868926674989135743);
void car_H_25(double *state, double *unused, double *out_4223719361080384863);
void car_h_24(double *state, double *unused, double *out_3559695939338705622);
void car_H_24(double *state, double *unused, double *out_2051069762074885297);
void car_h_30(double *state, double *unused, double *out_5012345975764913442);
void car_H_30(double *state, double *unused, double *out_7306334371137549998);
void car_h_26(double *state, double *unused, double *out_4184796142913956623);
void car_H_26(double *state, double *unused, double *out_482216042206328639);
void car_h_27(double *state, double *unused, double *out_2132746592671709902);
void car_H_27(double *state, double *unused, double *out_8965646390771576707);
void car_h_29(double *state, double *unused, double *out_1975559924320580757);
void car_H_29(double *state, double *unused, double *out_7252283663902025674);
void car_h_28(double *state, double *unused, double *out_2829633405009583330);
void car_H_28(double *state, double *unused, double *out_2169884646832495100);
void car_h_31(double *state, double *unused, double *out_1418295282360252576);
void car_H_31(double *state, double *unused, double *out_4254365322957345291);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}