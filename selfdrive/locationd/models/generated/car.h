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
void car_err_fun(double *nom_x, double *delta_x, double *out_1070978885467264368);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7207906360374068549);
void car_H_mod_fun(double *state, double *out_6799220741010781739);
void car_f_fun(double *state, double dt, double *out_3613739950576570122);
void car_F_fun(double *state, double dt, double *out_2385579972732080229);
void car_h_25(double *state, double *unused, double *out_7988561007480328364);
void car_H_25(double *state, double *unused, double *out_8124542682709278200);
void car_h_24(double *state, double *unused, double *out_4668255431603815818);
void car_H_24(double *state, double *unused, double *out_4566617083906955064);
void car_h_30(double *state, double *unused, double *out_8263755069764834253);
void car_H_30(double *state, double *unused, double *out_5606209724202029573);
void car_h_26(double *state, double *unused, double *out_7578583683136019712);
void car_H_26(double *state, double *unused, double *out_6580698072126217192);
void car_h_27(double *state, double *unused, double *out_4355663630496028862);
void car_H_27(double *state, double *unused, double *out_3382615653018086356);
void car_h_29(double *state, double *unused, double *out_4540259132863760528);
void car_H_29(double *state, double *unused, double *out_5095978379887637389);
void car_h_28(double *state, double *unused, double *out_646009637164816783);
void car_H_28(double *state, double *unused, double *out_8268366676752383653);
void car_h_31(double *state, double *unused, double *out_1320465781545372070);
void car_H_31(double *state, double *unused, double *out_8093896720832317772);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}