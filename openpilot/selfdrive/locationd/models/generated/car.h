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
void car_err_fun(double *nom_x, double *delta_x, double *out_8512377944699046552);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6577279479399491155);
void car_H_mod_fun(double *state, double *out_7435623757384982931);
void car_f_fun(double *state, double dt, double *out_5311008828912692131);
void car_F_fun(double *state, double dt, double *out_9039631374788334585);
void car_h_25(double *state, double *unused, double *out_4369287738774083452);
void car_H_25(double *state, double *unused, double *out_1817932090412331448);
void car_h_24(double *state, double *unused, double *out_4308943977605512295);
void car_H_24(double *state, double *unused, double *out_354717508593168118);
void car_h_30(double *state, double *unused, double *out_6469084566834324480);
void car_H_30(double *state, double *unused, double *out_8734622431903948203);
void car_h_26(double *state, double *unused, double *out_3581376351729874269);
void car_H_26(double *state, double *unused, double *out_1923571228461724776);
void car_h_27(double *state, double *unused, double *out_4036369080870143201);
void car_H_27(double *state, double *unused, double *out_6559859120103523292);
void car_h_29(double *state, double *unused, double *out_5438333539020600169);
void car_H_29(double *state, double *unused, double *out_4846496393233972259);
void car_h_28(double *state, double *unused, double *out_8317932922113803709);
void car_H_28(double *state, double *unused, double *out_235902623835558315);
void car_h_31(double *state, double *unused, double *out_5547018248750061118);
void car_H_31(double *state, double *unused, double *out_1848578052289291876);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}