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
void car_err_fun(double *nom_x, double *delta_x, double *out_750716713605572752);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5646158869804097554);
void car_H_mod_fun(double *state, double *out_5316612585990664431);
void car_f_fun(double *state, double dt, double *out_5939119196305302943);
void car_F_fun(double *state, double dt, double *out_8185668144906963481);
void car_h_25(double *state, double *unused, double *out_2353961728868478623);
void car_H_25(double *state, double *unused, double *out_6265733508019146640);
void car_h_24(double *state, double *unused, double *out_5979104720135345830);
void car_H_24(double *state, double *unused, double *out_5795276025975807916);
void car_h_30(double *state, double *unused, double *out_1283487799385543727);
void car_H_30(double *state, double *unused, double *out_6136394560875906570);
void car_h_26(double *state, double *unused, double *out_2226997652287206162);
void car_H_26(double *state, double *unused, double *out_2524230189145090416);
void car_h_27(double *state, double *unused, double *out_1596111583707659813);
void car_H_27(double *state, double *unused, double *out_3961631249075481659);
void car_h_29(double *state, double *unused, double *out_6285161067046389372);
void car_H_29(double *state, double *unused, double *out_2248268522205930626);
void car_h_28(double *state, double *unused, double *out_992795699031182296);
void car_H_28(double *state, double *unused, double *out_2834130494863599948);
void car_h_31(double *state, double *unused, double *out_8901233231985561197);
void car_H_31(double *state, double *unused, double *out_6296379469896107068);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}