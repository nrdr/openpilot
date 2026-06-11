#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void live_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_9(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_12(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_35(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_32(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_33(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_H(double *in_vec, double *out_7177297295412849942);
void live_err_fun(double *nom_x, double *delta_x, double *out_3785912956457762353);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_7262755009535558114);
void live_H_mod_fun(double *state, double *out_2832915773378135120);
void live_f_fun(double *state, double dt, double *out_8823172693583344416);
void live_F_fun(double *state, double dt, double *out_3595349451600640572);
void live_h_4(double *state, double *unused, double *out_5167307819157309520);
void live_H_4(double *state, double *unused, double *out_7021761023147116809);
void live_h_9(double *state, double *unused, double *out_3316803110409540821);
void live_H_9(double *state, double *unused, double *out_7262950669776707454);
void live_h_10(double *state, double *unused, double *out_2730206020748489003);
void live_H_10(double *state, double *unused, double *out_479270991295011768);
void live_h_12(double *state, double *unused, double *out_4493521867215019977);
void live_H_12(double *state, double *unused, double *out_6405526642530473012);
void live_h_35(double *state, double *unused, double *out_3167729871996962004);
void live_H_35(double *state, double *unused, double *out_8058320993189827431);
void live_h_32(double *state, double *unused, double *out_2758432760937889605);
void live_H_32(double *state, double *unused, double *out_2257016620982214873);
void live_h_13(double *state, double *unused, double *out_751521091155863533);
void live_H_13(double *state, double *unused, double *out_5413495008283922907);
void live_h_14(double *state, double *unused, double *out_3316803110409540821);
void live_H_14(double *state, double *unused, double *out_7262950669776707454);
void live_h_33(double *state, double *unused, double *out_8350668576590553061);
void live_H_33(double *state, double *unused, double *out_4907763988550969827);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}