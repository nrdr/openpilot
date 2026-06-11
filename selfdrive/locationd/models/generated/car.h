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
void car_err_fun(double *nom_x, double *delta_x, double *out_6787215922179600543);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6360714375878173456);
void car_H_mod_fun(double *state, double *out_8179962768019912306);
void car_f_fun(double *state, double dt, double *out_519966246064059535);
void car_F_fun(double *state, double dt, double *out_3124210133510146644);
void car_h_25(double *state, double *unused, double *out_4133024183340150425);
void car_H_25(double *state, double *unused, double *out_1013225457892324931);
void car_h_24(double *state, double *unused, double *out_3391899593912198426);
void car_H_24(double *state, double *unused, double *out_3185875056897824497);
void car_h_30(double *state, double *unused, double *out_3346447755699384264);
void car_H_30(double *state, double *unused, double *out_1505107500614923696);
void car_h_26(double *state, double *unused, double *out_9213411574954820401);
void car_H_26(double *state, double *unused, double *out_4754728776766381155);
void car_h_27(double *state, double *unused, double *out_1011865879775497112);
void car_H_27(double *state, double *unused, double *out_3728701571798866913);
void car_h_29(double *state, double *unused, double *out_1287059942060003001);
void car_H_29(double *state, double *unused, double *out_2015338844929315880);
void car_h_28(double *state, double *unused, double *out_566195834839143975);
void car_H_28(double *state, double *unused, double *out_3067060172140214694);
void car_h_31(double *state, double *unused, double *out_4506853293378391459);
void car_H_31(double *state, double *unused, double *out_5380936878999732631);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}