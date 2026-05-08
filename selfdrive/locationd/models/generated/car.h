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
void car_err_fun(double *nom_x, double *delta_x, double *out_7995441131431557096);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4650361766683635891);
void car_H_mod_fun(double *state, double *out_6454279744481307781);
void car_f_fun(double *state, double dt, double *out_1057486056378825346);
void car_F_fun(double *state, double dt, double *out_2762244256179971899);
void car_h_25(double *state, double *unused, double *out_1163064920451275624);
void car_H_25(double *state, double *unused, double *out_8601438681758688193);
void car_h_24(double *state, double *unused, double *out_2922764778379292944);
void car_H_24(double *state, double *unused, double *out_5024983887294875160);
void car_h_30(double *state, double *unused, double *out_7933900146801626560);
void car_H_30(double *state, double *unused, double *out_8730777628901928263);
void car_h_26(double *state, double *unused, double *out_5511170659247079411);
void car_H_26(double *state, double *unused, double *out_6103802073076807199);
void car_h_27(double *state, double *unused, double *out_559749035774798107);
void car_H_27(double *state, double *unused, double *out_7541203133007198442);
void car_h_29(double *state, double *unused, double *out_4658052334054169971);
void car_H_29(double *state, double *unused, double *out_8220546284587536079);
void car_h_28(double *state, double *unused, double *out_1503258888676460542);
void car_H_28(double *state, double *unused, double *out_5143798772052484963);
void car_h_31(double *state, double *unused, double *out_6600200336369396817);
void car_H_31(double *state, double *unused, double *out_8570792719881727765);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}