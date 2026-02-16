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
void car_err_fun(double *nom_x, double *delta_x, double *out_9079002193507214447);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_28192897299460748);
void car_H_mod_fun(double *state, double *out_1429112410127945448);
void car_f_fun(double *state, double dt, double *out_8589483517240840993);
void car_F_fun(double *state, double dt, double *out_7186420185024843086);
void car_h_25(double *state, double *unused, double *out_9042730217037280690);
void car_H_25(double *state, double *unused, double *out_7718077913416356474);
void car_h_24(double *state, double *unused, double *out_8810898373805104119);
void car_H_24(double *state, double *unused, double *out_5545428314410856908);
void car_h_30(double *state, double *unused, double *out_3128997190366532317);
void car_H_30(double *state, double *unused, double *out_8210333201785946515);
void car_h_26(double *state, double *unused, double *out_1268954890915096695);
void car_H_26(double *state, double *unused, double *out_7424140190532394541);
void car_h_27(double *state, double *unused, double *out_2643688699623431544);
void car_H_27(double *state, double *unused, double *out_5986739130602003298);
void car_h_29(double *state, double *unused, double *out_2185487337464869882);
void car_H_29(double *state, double *unused, double *out_7700101857471554331);
void car_h_28(double *state, double *unused, double *out_3247004584299909061);
void car_H_28(double *state, double *unused, double *out_5664243199168466711);
void car_h_31(double *state, double *unused, double *out_92965819725873521);
void car_H_31(double *state, double *unused, double *out_8050348292765746017);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}