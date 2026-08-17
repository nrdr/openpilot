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
void car_err_fun(double *nom_x, double *delta_x, double *out_6950710126288337597);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8581347787117461250);
void car_H_mod_fun(double *state, double *out_3544901094272927164);
void car_f_fun(double *state, double dt, double *out_5766199025975452508);
void car_F_fun(double *state, double dt, double *out_7363505390948469561);
void car_h_25(double *state, double *unused, double *out_1637789479634843610);
void car_H_25(double *state, double *unused, double *out_2952121865617102787);
void car_h_24(double *state, double *unused, double *out_3717944162013752891);
void car_H_24(double *state, double *unused, double *out_7820936730644809639);
void car_h_30(double *state, double *unused, double *out_1480602811283714465);
void car_H_30(double *state, double *unused, double *out_7479818195744710985);
void car_h_26(double *state, double *unused, double *out_4517388862728047150);
void car_H_26(double *state, double *unused, double *out_6693625184491159011);
void car_h_27(double *state, double *unused, double *out_6639462747295689255);
void car_H_27(double *state, double *unused, double *out_8792162566164415720);
void car_h_29(double *state, double *unused, double *out_6482276078944560110);
void car_H_29(double *state, double *unused, double *out_6969586851430318801);
void car_h_28(double *state, double *unused, double *out_6740863807695519638);
void car_H_28(double *state, double *unused, double *out_6394758205209702241);
void car_h_31(double *state, double *unused, double *out_9098348243883731935);
void car_H_31(double *state, double *unused, double *out_7319833286724510487);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}