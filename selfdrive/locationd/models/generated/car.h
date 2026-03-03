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
void car_err_fun(double *nom_x, double *delta_x, double *out_5394216099023030170);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1268510137061119882);
void car_H_mod_fun(double *state, double *out_27038522722598530);
void car_f_fun(double *state, double dt, double *out_6605105798485234217);
void car_F_fun(double *state, double dt, double *out_1879544495240993634);
void car_h_25(double *state, double *unused, double *out_5624646906532576969);
void car_H_25(double *state, double *unused, double *out_5366051290200112092);
void car_h_24(double *state, double *unused, double *out_1782389657789830899);
void car_H_24(double *state, double *unused, double *out_7053867726069216283);
void car_h_30(double *state, double *unused, double *out_7075278299161460136);
void car_H_30(double *state, double *unused, double *out_5236712343056872022);
void car_h_26(double *state, double *unused, double *out_5728735903467134645);
void car_H_26(double *state, double *unused, double *out_1624547971326055868);
void car_h_27(double *state, double *unused, double *out_1994890907546790160);
void car_H_27(double *state, double *unused, double *out_3061949031256447111);
void car_h_29(double *state, double *unused, double *out_5886381743207259025);
void car_H_29(double *state, double *unused, double *out_1348586304386896078);
void car_h_28(double *state, double *unused, double *out_8202048695027411215);
void car_H_28(double *state, double *unused, double *out_3733812712682634496);
void car_h_31(double *state, double *unused, double *out_3252169063166594161);
void car_H_31(double *state, double *unused, double *out_5396697252077072520);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}