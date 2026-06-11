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
void car_err_fun(double *nom_x, double *delta_x, double *out_5658036703693658224);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_2378388429853024968);
void car_H_mod_fun(double *state, double *out_4573538855915977510);
void car_f_fun(double *state, double dt, double *out_857475065003488353);
void car_F_fun(double *state, double dt, double *out_861520061507436680);
void car_h_25(double *state, double *unused, double *out_5081030669612635808);
void car_H_25(double *state, double *unused, double *out_1050558205926485833);
void car_h_24(double *state, double *unused, double *out_6877732608566867147);
void car_H_24(double *state, double *unused, double *out_5797067532892994867);
void car_h_30(double *state, double *unused, double *out_4805836607328129919);
void car_H_30(double *state, double *unused, double *out_5866132135565130922);
void car_h_26(double *state, double *unused, double *out_8639234198720576052);
void car_H_26(double *state, double *unused, double *out_4792061524800542057);
void car_h_27(double *state, double *unused, double *out_274550784286540057);
void car_H_27(double *state, double *unused, double *out_3354660464870150814);
void car_h_29(double *state, double *unused, double *out_195836660332715726);
void car_H_29(double *state, double *unused, double *out_1978006096895154978);
void car_h_28(double *state, double *unused, double *out_893193016789601680);
void car_H_28(double *state, double *unused, double *out_3104392920174375596);
void car_h_31(double *state, double *unused, double *out_7210266208256255679);
void car_H_31(double *state, double *unused, double *out_1019912244049525405);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}