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
void live_H(double *in_vec, double *out_5014772208818921273);
void live_err_fun(double *nom_x, double *delta_x, double *out_2763896297973817617);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_7286531692802160161);
void live_H_mod_fun(double *state, double *out_72622962830682333);
void live_f_fun(double *state, double dt, double *out_103707240086611357);
void live_F_fun(double *state, double dt, double *out_1809822372248507860);
void live_h_4(double *state, double *unused, double *out_7446602383104459136);
void live_H_4(double *state, double *unused, double *out_8098050261566598318);
void live_h_9(double *state, double *unused, double *out_2645920156673123156);
void live_H_9(double *state, double *unused, double *out_5209188709286518976);
void live_h_10(double *state, double *unused, double *out_193161741758491705);
void live_H_10(double *state, double *unused, double *out_6141663491879650502);
void live_h_12(double *state, double *unused, double *out_7400362126928241990);
void live_H_12(double *state, double *unused, double *out_7476951236519004651);
void live_h_35(double *state, double *unused, double *out_7223761488479052568);
void live_H_35(double *state, double *unused, double *out_4731388204193990942);
void live_h_32(double *state, double *unused, double *out_4921828063116826194);
void live_H_32(double *state, double *unused, double *out_4600223419253250473);
void live_h_13(double *state, double *unused, double *out_4354065410006050912);
void live_H_13(double *state, double *unused, double *out_6537441296245571241);
void live_h_14(double *state, double *unused, double *out_2645920156673123156);
void live_H_14(double *state, double *unused, double *out_5209188709286518976);
void live_h_33(double *state, double *unused, double *out_7017661916828232859);
void live_H_33(double *state, double *unused, double *out_1580831199555133338);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}