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
void car_err_fun(double *nom_x, double *delta_x, double *out_8713671304942996477);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3600257385094944910);
void car_H_mod_fun(double *state, double *out_9147766036788271094);
void car_f_fun(double *state, double dt, double *out_4342466864191827990);
void car_F_fun(double *state, double dt, double *out_4614465668667211337);
void car_h_25(double *state, double *unused, double *out_4833672742345990691);
void car_H_25(double *state, double *unused, double *out_5624785386798779417);
void car_h_24(double *state, double *unused, double *out_4504560578349803309);
void car_H_24(double *state, double *unused, double *out_1029420071309406340);
void car_h_30(double *state, double *unused, double *out_5849806074542888484);
void car_H_30(double *state, double *unused, double *out_8294262356783164001);
void car_h_26(double *state, double *unused, double *out_783388555824545761);
void car_H_26(double *state, double *unused, double *out_9080455368036715975);
void car_h_27(double *state, double *unused, double *out_7870458793790323376);
void car_H_27(double *state, double *unused, double *out_7928887645742444398);
void car_h_29(double *state, double *unused, double *out_7595264731505817487);
void car_H_29(double *state, double *unused, double *out_8804493701097556185);
void car_h_28(double *state, double *unused, double *out_2644551577954998429);
void car_H_28(double *state, double *unused, double *out_3722094684028025611);
void car_h_31(double *state, double *unused, double *out_1937162484004360245);
void car_H_31(double *state, double *unused, double *out_5594139424921818989);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}