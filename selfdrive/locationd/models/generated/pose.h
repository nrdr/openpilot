#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_6269171790765846050);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1497934558633100347);
void pose_H_mod_fun(double *state, double *out_7862392065184069712);
void pose_f_fun(double *state, double dt, double *out_4855847476055627778);
void pose_F_fun(double *state, double dt, double *out_1703318423524786966);
void pose_h_4(double *state, double *unused, double *out_7821603690376207235);
void pose_H_4(double *state, double *unused, double *out_1639990342467660562);
void pose_h_10(double *state, double *unused, double *out_4627608962100745909);
void pose_H_10(double *state, double *unused, double *out_5548344007433806154);
void pose_h_13(double *state, double *unused, double *out_5105456950148742445);
void pose_H_13(double *state, double *unused, double *out_4852264167799993363);
void pose_h_14(double *state, double *unused, double *out_7814084012328434224);
void pose_H_14(double *state, double *unused, double *out_5603231198807145091);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}