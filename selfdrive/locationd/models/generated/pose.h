#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_2192517159883214491);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_7620744679476459470);
void pose_H_mod_fun(double *state, double *out_7476444296888154553);
void pose_f_fun(double *state, double dt, double *out_5554352162049920971);
void pose_F_fun(double *state, double dt, double *out_6614407721487933261);
void pose_h_4(double *state, double *unused, double *out_5876735221666534963);
void pose_H_4(double *state, double *unused, double *out_5817781391782316328);
void pose_h_10(double *state, double *unused, double *out_7879293322521614101);
void pose_H_10(double *state, double *unused, double *out_6097031029555240174);
void pose_h_13(double *state, double *unused, double *out_3226875223116851983);
void pose_H_13(double *state, double *unused, double *out_2605507566449983527);
void pose_h_14(double *state, double *unused, double *out_4838960397532814427);
void pose_H_14(double *state, double *unused, double *out_1854540535442831799);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}