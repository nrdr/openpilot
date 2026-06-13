#include "car.h"

namespace {
#define DIM 9
#define EDIM 9
#define MEDIM 9
typedef void (*Hfun)(double *, double *, double *);

double mass;

void set_mass(double x){ mass = x;}

double rotational_inertia;

void set_rotational_inertia(double x){ rotational_inertia = x;}

double center_to_front;

void set_center_to_front(double x){ center_to_front = x;}

double center_to_rear;

void set_center_to_rear(double x){ center_to_rear = x;}

double stiffness_front;

void set_stiffness_front(double x){ stiffness_front = x;}

double stiffness_rear;

void set_stiffness_rear(double x){ stiffness_rear = x;}
const static double MAHA_THRESH_25 = 3.8414588206941227;
const static double MAHA_THRESH_24 = 5.991464547107981;
const static double MAHA_THRESH_30 = 3.8414588206941227;
const static double MAHA_THRESH_26 = 3.8414588206941227;
const static double MAHA_THRESH_27 = 3.8414588206941227;
const static double MAHA_THRESH_29 = 3.8414588206941227;
const static double MAHA_THRESH_28 = 3.8414588206941227;
const static double MAHA_THRESH_31 = 3.8414588206941227;

/******************************************************************************
 *                      Code generated with SymPy 1.14.0                      *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_1133780562410706743) {
   out_1133780562410706743[0] = delta_x[0] + nom_x[0];
   out_1133780562410706743[1] = delta_x[1] + nom_x[1];
   out_1133780562410706743[2] = delta_x[2] + nom_x[2];
   out_1133780562410706743[3] = delta_x[3] + nom_x[3];
   out_1133780562410706743[4] = delta_x[4] + nom_x[4];
   out_1133780562410706743[5] = delta_x[5] + nom_x[5];
   out_1133780562410706743[6] = delta_x[6] + nom_x[6];
   out_1133780562410706743[7] = delta_x[7] + nom_x[7];
   out_1133780562410706743[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4674975851193082904) {
   out_4674975851193082904[0] = -nom_x[0] + true_x[0];
   out_4674975851193082904[1] = -nom_x[1] + true_x[1];
   out_4674975851193082904[2] = -nom_x[2] + true_x[2];
   out_4674975851193082904[3] = -nom_x[3] + true_x[3];
   out_4674975851193082904[4] = -nom_x[4] + true_x[4];
   out_4674975851193082904[5] = -nom_x[5] + true_x[5];
   out_4674975851193082904[6] = -nom_x[6] + true_x[6];
   out_4674975851193082904[7] = -nom_x[7] + true_x[7];
   out_4674975851193082904[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_318329653000957007) {
   out_318329653000957007[0] = 1.0;
   out_318329653000957007[1] = 0.0;
   out_318329653000957007[2] = 0.0;
   out_318329653000957007[3] = 0.0;
   out_318329653000957007[4] = 0.0;
   out_318329653000957007[5] = 0.0;
   out_318329653000957007[6] = 0.0;
   out_318329653000957007[7] = 0.0;
   out_318329653000957007[8] = 0.0;
   out_318329653000957007[9] = 0.0;
   out_318329653000957007[10] = 1.0;
   out_318329653000957007[11] = 0.0;
   out_318329653000957007[12] = 0.0;
   out_318329653000957007[13] = 0.0;
   out_318329653000957007[14] = 0.0;
   out_318329653000957007[15] = 0.0;
   out_318329653000957007[16] = 0.0;
   out_318329653000957007[17] = 0.0;
   out_318329653000957007[18] = 0.0;
   out_318329653000957007[19] = 0.0;
   out_318329653000957007[20] = 1.0;
   out_318329653000957007[21] = 0.0;
   out_318329653000957007[22] = 0.0;
   out_318329653000957007[23] = 0.0;
   out_318329653000957007[24] = 0.0;
   out_318329653000957007[25] = 0.0;
   out_318329653000957007[26] = 0.0;
   out_318329653000957007[27] = 0.0;
   out_318329653000957007[28] = 0.0;
   out_318329653000957007[29] = 0.0;
   out_318329653000957007[30] = 1.0;
   out_318329653000957007[31] = 0.0;
   out_318329653000957007[32] = 0.0;
   out_318329653000957007[33] = 0.0;
   out_318329653000957007[34] = 0.0;
   out_318329653000957007[35] = 0.0;
   out_318329653000957007[36] = 0.0;
   out_318329653000957007[37] = 0.0;
   out_318329653000957007[38] = 0.0;
   out_318329653000957007[39] = 0.0;
   out_318329653000957007[40] = 1.0;
   out_318329653000957007[41] = 0.0;
   out_318329653000957007[42] = 0.0;
   out_318329653000957007[43] = 0.0;
   out_318329653000957007[44] = 0.0;
   out_318329653000957007[45] = 0.0;
   out_318329653000957007[46] = 0.0;
   out_318329653000957007[47] = 0.0;
   out_318329653000957007[48] = 0.0;
   out_318329653000957007[49] = 0.0;
   out_318329653000957007[50] = 1.0;
   out_318329653000957007[51] = 0.0;
   out_318329653000957007[52] = 0.0;
   out_318329653000957007[53] = 0.0;
   out_318329653000957007[54] = 0.0;
   out_318329653000957007[55] = 0.0;
   out_318329653000957007[56] = 0.0;
   out_318329653000957007[57] = 0.0;
   out_318329653000957007[58] = 0.0;
   out_318329653000957007[59] = 0.0;
   out_318329653000957007[60] = 1.0;
   out_318329653000957007[61] = 0.0;
   out_318329653000957007[62] = 0.0;
   out_318329653000957007[63] = 0.0;
   out_318329653000957007[64] = 0.0;
   out_318329653000957007[65] = 0.0;
   out_318329653000957007[66] = 0.0;
   out_318329653000957007[67] = 0.0;
   out_318329653000957007[68] = 0.0;
   out_318329653000957007[69] = 0.0;
   out_318329653000957007[70] = 1.0;
   out_318329653000957007[71] = 0.0;
   out_318329653000957007[72] = 0.0;
   out_318329653000957007[73] = 0.0;
   out_318329653000957007[74] = 0.0;
   out_318329653000957007[75] = 0.0;
   out_318329653000957007[76] = 0.0;
   out_318329653000957007[77] = 0.0;
   out_318329653000957007[78] = 0.0;
   out_318329653000957007[79] = 0.0;
   out_318329653000957007[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_1557131492089968397) {
   out_1557131492089968397[0] = state[0];
   out_1557131492089968397[1] = state[1];
   out_1557131492089968397[2] = state[2];
   out_1557131492089968397[3] = state[3];
   out_1557131492089968397[4] = state[4];
   out_1557131492089968397[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_1557131492089968397[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_1557131492089968397[7] = state[7];
   out_1557131492089968397[8] = state[8];
}
void F_fun(double *state, double dt, double *out_5093893007673167724) {
   out_5093893007673167724[0] = 1;
   out_5093893007673167724[1] = 0;
   out_5093893007673167724[2] = 0;
   out_5093893007673167724[3] = 0;
   out_5093893007673167724[4] = 0;
   out_5093893007673167724[5] = 0;
   out_5093893007673167724[6] = 0;
   out_5093893007673167724[7] = 0;
   out_5093893007673167724[8] = 0;
   out_5093893007673167724[9] = 0;
   out_5093893007673167724[10] = 1;
   out_5093893007673167724[11] = 0;
   out_5093893007673167724[12] = 0;
   out_5093893007673167724[13] = 0;
   out_5093893007673167724[14] = 0;
   out_5093893007673167724[15] = 0;
   out_5093893007673167724[16] = 0;
   out_5093893007673167724[17] = 0;
   out_5093893007673167724[18] = 0;
   out_5093893007673167724[19] = 0;
   out_5093893007673167724[20] = 1;
   out_5093893007673167724[21] = 0;
   out_5093893007673167724[22] = 0;
   out_5093893007673167724[23] = 0;
   out_5093893007673167724[24] = 0;
   out_5093893007673167724[25] = 0;
   out_5093893007673167724[26] = 0;
   out_5093893007673167724[27] = 0;
   out_5093893007673167724[28] = 0;
   out_5093893007673167724[29] = 0;
   out_5093893007673167724[30] = 1;
   out_5093893007673167724[31] = 0;
   out_5093893007673167724[32] = 0;
   out_5093893007673167724[33] = 0;
   out_5093893007673167724[34] = 0;
   out_5093893007673167724[35] = 0;
   out_5093893007673167724[36] = 0;
   out_5093893007673167724[37] = 0;
   out_5093893007673167724[38] = 0;
   out_5093893007673167724[39] = 0;
   out_5093893007673167724[40] = 1;
   out_5093893007673167724[41] = 0;
   out_5093893007673167724[42] = 0;
   out_5093893007673167724[43] = 0;
   out_5093893007673167724[44] = 0;
   out_5093893007673167724[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_5093893007673167724[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_5093893007673167724[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5093893007673167724[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5093893007673167724[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_5093893007673167724[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_5093893007673167724[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_5093893007673167724[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_5093893007673167724[53] = -9.8100000000000005*dt;
   out_5093893007673167724[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_5093893007673167724[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_5093893007673167724[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5093893007673167724[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5093893007673167724[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_5093893007673167724[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_5093893007673167724[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_5093893007673167724[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5093893007673167724[62] = 0;
   out_5093893007673167724[63] = 0;
   out_5093893007673167724[64] = 0;
   out_5093893007673167724[65] = 0;
   out_5093893007673167724[66] = 0;
   out_5093893007673167724[67] = 0;
   out_5093893007673167724[68] = 0;
   out_5093893007673167724[69] = 0;
   out_5093893007673167724[70] = 1;
   out_5093893007673167724[71] = 0;
   out_5093893007673167724[72] = 0;
   out_5093893007673167724[73] = 0;
   out_5093893007673167724[74] = 0;
   out_5093893007673167724[75] = 0;
   out_5093893007673167724[76] = 0;
   out_5093893007673167724[77] = 0;
   out_5093893007673167724[78] = 0;
   out_5093893007673167724[79] = 0;
   out_5093893007673167724[80] = 1;
}
void h_25(double *state, double *unused, double *out_9012832394529810438) {
   out_9012832394529810438[0] = state[6];
}
void H_25(double *state, double *unused, double *out_187004789199339705) {
   out_187004789199339705[0] = 0;
   out_187004789199339705[1] = 0;
   out_187004789199339705[2] = 0;
   out_187004789199339705[3] = 0;
   out_187004789199339705[4] = 0;
   out_187004789199339705[5] = 0;
   out_187004789199339705[6] = 1;
   out_187004789199339705[7] = 0;
   out_187004789199339705[8] = 0;
}
void h_24(double *state, double *unused, double *out_6747949908627279692) {
   out_6747949908627279692[0] = state[4];
   out_6747949908627279692[1] = state[5];
}
void H_24(double *state, double *unused, double *out_6762576595790857806) {
   out_6762576595790857806[0] = 0;
   out_6762576595790857806[1] = 0;
   out_6762576595790857806[2] = 0;
   out_6762576595790857806[3] = 0;
   out_6762576595790857806[4] = 1;
   out_6762576595790857806[5] = 0;
   out_6762576595790857806[6] = 0;
   out_6762576595790857806[7] = 0;
   out_6762576595790857806[8] = 0;
   out_6762576595790857806[9] = 0;
   out_6762576595790857806[10] = 0;
   out_6762576595790857806[11] = 0;
   out_6762576595790857806[12] = 0;
   out_6762576595790857806[13] = 0;
   out_6762576595790857806[14] = 1;
   out_6762576595790857806[15] = 0;
   out_6762576595790857806[16] = 0;
   out_6762576595790857806[17] = 0;
}
void h_30(double *state, double *unused, double *out_1809616437543824468) {
   out_1809616437543824468[0] = state[4];
}
void H_30(double *state, double *unused, double *out_7103695130690956460) {
   out_7103695130690956460[0] = 0;
   out_7103695130690956460[1] = 0;
   out_7103695130690956460[2] = 0;
   out_7103695130690956460[3] = 0;
   out_7103695130690956460[4] = 1;
   out_7103695130690956460[5] = 0;
   out_7103695130690956460[6] = 0;
   out_7103695130690956460[7] = 0;
   out_7103695130690956460[8] = 0;
}
void h_26(double *state, double *unused, double *out_3192056830117021177) {
   out_3192056830117021177[0] = state[7];
}
void H_26(double *state, double *unused, double *out_3554498529674716519) {
   out_3554498529674716519[0] = 0;
   out_3554498529674716519[1] = 0;
   out_3554498529674716519[2] = 0;
   out_3554498529674716519[3] = 0;
   out_3554498529674716519[4] = 0;
   out_3554498529674716519[5] = 0;
   out_3554498529674716519[6] = 0;
   out_3554498529674716519[7] = 1;
   out_3554498529674716519[8] = 0;
}
void h_27(double *state, double *unused, double *out_6890003829158494444) {
   out_6890003829158494444[0] = state[3];
}
void H_27(double *state, double *unused, double *out_4928931818890531549) {
   out_4928931818890531549[0] = 0;
   out_4928931818890531549[1] = 0;
   out_4928931818890531549[2] = 0;
   out_4928931818890531549[3] = 1;
   out_4928931818890531549[4] = 0;
   out_4928931818890531549[5] = 0;
   out_4928931818890531549[6] = 0;
   out_4928931818890531549[7] = 0;
   out_4928931818890531549[8] = 0;
}
void h_29(double *state, double *unused, double *out_570554935090393881) {
   out_570554935090393881[0] = state[1];
}
void H_29(double *state, double *unused, double *out_7613926475005348644) {
   out_7613926475005348644[0] = 0;
   out_7613926475005348644[1] = 1;
   out_7613926475005348644[2] = 0;
   out_7613926475005348644[3] = 0;
   out_7613926475005348644[4] = 0;
   out_7613926475005348644[5] = 0;
   out_7613926475005348644[6] = 0;
   out_7613926475005348644[7] = 0;
   out_7613926475005348644[8] = 0;
}
void h_28(double *state, double *unused, double *out_634179107199447190) {
   out_634179107199447190[0] = state[0];
}
void H_28(double *state, double *unused, double *out_1866829925048550058) {
   out_1866829925048550058[0] = 1;
   out_1866829925048550058[1] = 0;
   out_1866829925048550058[2] = 0;
   out_1866829925048550058[3] = 0;
   out_1866829925048550058[4] = 0;
   out_1866829925048550058[5] = 0;
   out_1866829925048550058[6] = 0;
   out_1866829925048550058[7] = 0;
   out_1866829925048550058[8] = 0;
}
void h_31(double *state, double *unused, double *out_1973352914930852853) {
   out_1973352914930852853[0] = state[8];
}
void H_31(double *state, double *unused, double *out_217650751076300133) {
   out_217650751076300133[0] = 0;
   out_217650751076300133[1] = 0;
   out_217650751076300133[2] = 0;
   out_217650751076300133[3] = 0;
   out_217650751076300133[4] = 0;
   out_217650751076300133[5] = 0;
   out_217650751076300133[6] = 0;
   out_217650751076300133[7] = 0;
   out_217650751076300133[8] = 1;
}
#include <eigen3/Eigen/Dense>
#include <iostream>

typedef Eigen::Matrix<double, DIM, DIM, Eigen::RowMajor> DDM;
typedef Eigen::Matrix<double, EDIM, EDIM, Eigen::RowMajor> EEM;
typedef Eigen::Matrix<double, DIM, EDIM, Eigen::RowMajor> DEM;

void predict(double *in_x, double *in_P, double *in_Q, double dt) {
  typedef Eigen::Matrix<double, MEDIM, MEDIM, Eigen::RowMajor> RRM;

  double nx[DIM] = {0};
  double in_F[EDIM*EDIM] = {0};

  // functions from sympy
  f_fun(in_x, dt, nx);
  F_fun(in_x, dt, in_F);


  EEM F(in_F);
  EEM P(in_P);
  EEM Q(in_Q);

  RRM F_main = F.topLeftCorner(MEDIM, MEDIM);
  P.topLeftCorner(MEDIM, MEDIM) = (F_main * P.topLeftCorner(MEDIM, MEDIM)) * F_main.transpose();
  P.topRightCorner(MEDIM, EDIM - MEDIM) = F_main * P.topRightCorner(MEDIM, EDIM - MEDIM);
  P.bottomLeftCorner(EDIM - MEDIM, MEDIM) = P.bottomLeftCorner(EDIM - MEDIM, MEDIM) * F_main.transpose();

  P = P + dt*Q;

  // copy out state
  memcpy(in_x, nx, DIM * sizeof(double));
  memcpy(in_P, P.data(), EDIM * EDIM * sizeof(double));
}

// note: extra_args dim only correct when null space projecting
// otherwise 1
template <int ZDIM, int EADIM, bool MAHA_TEST>
void update(double *in_x, double *in_P, Hfun h_fun, Hfun H_fun, Hfun Hea_fun, double *in_z, double *in_R, double *in_ea, double MAHA_THRESHOLD) {
  typedef Eigen::Matrix<double, ZDIM, ZDIM, Eigen::RowMajor> ZZM;
  typedef Eigen::Matrix<double, ZDIM, DIM, Eigen::RowMajor> ZDM;
  typedef Eigen::Matrix<double, Eigen::Dynamic, EDIM, Eigen::RowMajor> XEM;
  //typedef Eigen::Matrix<double, EDIM, ZDIM, Eigen::RowMajor> EZM;
  typedef Eigen::Matrix<double, Eigen::Dynamic, 1> X1M;
  typedef Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> XXM;

  double in_hx[ZDIM] = {0};
  double in_H[ZDIM * DIM] = {0};
  double in_H_mod[EDIM * DIM] = {0};
  double delta_x[EDIM] = {0};
  double x_new[DIM] = {0};


  // state x, P
  Eigen::Matrix<double, ZDIM, 1> z(in_z);
  EEM P(in_P);
  ZZM pre_R(in_R);

  // functions from sympy
  h_fun(in_x, in_ea, in_hx);
  H_fun(in_x, in_ea, in_H);
  ZDM pre_H(in_H);

  // get y (y = z - hx)
  Eigen::Matrix<double, ZDIM, 1> pre_y(in_hx); pre_y = z - pre_y;
  X1M y; XXM H; XXM R;
  if (Hea_fun){
    typedef Eigen::Matrix<double, ZDIM, EADIM, Eigen::RowMajor> ZAM;
    double in_Hea[ZDIM * EADIM] = {0};
    Hea_fun(in_x, in_ea, in_Hea);
    ZAM Hea(in_Hea);
    XXM A = Hea.transpose().fullPivLu().kernel();


    y = A.transpose() * pre_y;
    H = A.transpose() * pre_H;
    R = A.transpose() * pre_R * A;
  } else {
    y = pre_y;
    H = pre_H;
    R = pre_R;
  }
  // get modified H
  H_mod_fun(in_x, in_H_mod);
  DEM H_mod(in_H_mod);
  XEM H_err = H * H_mod;

  // Do mahalobis distance test
  if (MAHA_TEST){
    XXM a = (H_err * P * H_err.transpose() + R).inverse();
    double maha_dist = y.transpose() * a * y;
    if (maha_dist > MAHA_THRESHOLD){
      R = 1.0e16 * R;
    }
  }

  // Outlier resilient weighting
  double weight = 1;//(1.5)/(1 + y.squaredNorm()/R.sum());

  // kalman gains and I_KH
  XXM S = ((H_err * P) * H_err.transpose()) + R/weight;
  XEM KT = S.fullPivLu().solve(H_err * P.transpose());
  //EZM K = KT.transpose(); TODO: WHY DOES THIS NOT COMPILE?
  //EZM K = S.fullPivLu().solve(H_err * P.transpose()).transpose();
  //std::cout << "Here is the matrix rot:\n" << K << std::endl;
  EEM I_KH = Eigen::Matrix<double, EDIM, EDIM>::Identity() - (KT.transpose() * H_err);

  // update state by injecting dx
  Eigen::Matrix<double, EDIM, 1> dx(delta_x);
  dx  = (KT.transpose() * y);
  memcpy(delta_x, dx.data(), EDIM * sizeof(double));
  err_fun(in_x, delta_x, x_new);
  Eigen::Matrix<double, DIM, 1> x(x_new);

  // update cov
  P = ((I_KH * P) * I_KH.transpose()) + ((KT.transpose() * R) * KT);

  // copy out state
  memcpy(in_x, x.data(), DIM * sizeof(double));
  memcpy(in_P, P.data(), EDIM * EDIM * sizeof(double));
  memcpy(in_z, y.data(), y.rows() * sizeof(double));
}




}
extern "C" {

void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_25, H_25, NULL, in_z, in_R, in_ea, MAHA_THRESH_25);
}
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<2, 3, 0>(in_x, in_P, h_24, H_24, NULL, in_z, in_R, in_ea, MAHA_THRESH_24);
}
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_30, H_30, NULL, in_z, in_R, in_ea, MAHA_THRESH_30);
}
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_26, H_26, NULL, in_z, in_R, in_ea, MAHA_THRESH_26);
}
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_27, H_27, NULL, in_z, in_R, in_ea, MAHA_THRESH_27);
}
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_29, H_29, NULL, in_z, in_R, in_ea, MAHA_THRESH_29);
}
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_28, H_28, NULL, in_z, in_R, in_ea, MAHA_THRESH_28);
}
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_31, H_31, NULL, in_z, in_R, in_ea, MAHA_THRESH_31);
}
void car_err_fun(double *nom_x, double *delta_x, double *out_1133780562410706743) {
  err_fun(nom_x, delta_x, out_1133780562410706743);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4674975851193082904) {
  inv_err_fun(nom_x, true_x, out_4674975851193082904);
}
void car_H_mod_fun(double *state, double *out_318329653000957007) {
  H_mod_fun(state, out_318329653000957007);
}
void car_f_fun(double *state, double dt, double *out_1557131492089968397) {
  f_fun(state,  dt, out_1557131492089968397);
}
void car_F_fun(double *state, double dt, double *out_5093893007673167724) {
  F_fun(state,  dt, out_5093893007673167724);
}
void car_h_25(double *state, double *unused, double *out_9012832394529810438) {
  h_25(state, unused, out_9012832394529810438);
}
void car_H_25(double *state, double *unused, double *out_187004789199339705) {
  H_25(state, unused, out_187004789199339705);
}
void car_h_24(double *state, double *unused, double *out_6747949908627279692) {
  h_24(state, unused, out_6747949908627279692);
}
void car_H_24(double *state, double *unused, double *out_6762576595790857806) {
  H_24(state, unused, out_6762576595790857806);
}
void car_h_30(double *state, double *unused, double *out_1809616437543824468) {
  h_30(state, unused, out_1809616437543824468);
}
void car_H_30(double *state, double *unused, double *out_7103695130690956460) {
  H_30(state, unused, out_7103695130690956460);
}
void car_h_26(double *state, double *unused, double *out_3192056830117021177) {
  h_26(state, unused, out_3192056830117021177);
}
void car_H_26(double *state, double *unused, double *out_3554498529674716519) {
  H_26(state, unused, out_3554498529674716519);
}
void car_h_27(double *state, double *unused, double *out_6890003829158494444) {
  h_27(state, unused, out_6890003829158494444);
}
void car_H_27(double *state, double *unused, double *out_4928931818890531549) {
  H_27(state, unused, out_4928931818890531549);
}
void car_h_29(double *state, double *unused, double *out_570554935090393881) {
  h_29(state, unused, out_570554935090393881);
}
void car_H_29(double *state, double *unused, double *out_7613926475005348644) {
  H_29(state, unused, out_7613926475005348644);
}
void car_h_28(double *state, double *unused, double *out_634179107199447190) {
  h_28(state, unused, out_634179107199447190);
}
void car_H_28(double *state, double *unused, double *out_1866829925048550058) {
  H_28(state, unused, out_1866829925048550058);
}
void car_h_31(double *state, double *unused, double *out_1973352914930852853) {
  h_31(state, unused, out_1973352914930852853);
}
void car_H_31(double *state, double *unused, double *out_217650751076300133) {
  H_31(state, unused, out_217650751076300133);
}
void car_predict(double *in_x, double *in_P, double *in_Q, double dt) {
  predict(in_x, in_P, in_Q, dt);
}
void car_set_mass(double x) {
  set_mass(x);
}
void car_set_rotational_inertia(double x) {
  set_rotational_inertia(x);
}
void car_set_center_to_front(double x) {
  set_center_to_front(x);
}
void car_set_center_to_rear(double x) {
  set_center_to_rear(x);
}
void car_set_stiffness_front(double x) {
  set_stiffness_front(x);
}
void car_set_stiffness_rear(double x) {
  set_stiffness_rear(x);
}
}

const EKF car = {
  .name = "car",
  .kinds = { 25, 24, 30, 26, 27, 29, 28, 31 },
  .feature_kinds = {  },
  .f_fun = car_f_fun,
  .F_fun = car_F_fun,
  .err_fun = car_err_fun,
  .inv_err_fun = car_inv_err_fun,
  .H_mod_fun = car_H_mod_fun,
  .predict = car_predict,
  .hs = {
    { 25, car_h_25 },
    { 24, car_h_24 },
    { 30, car_h_30 },
    { 26, car_h_26 },
    { 27, car_h_27 },
    { 29, car_h_29 },
    { 28, car_h_28 },
    { 31, car_h_31 },
  },
  .Hs = {
    { 25, car_H_25 },
    { 24, car_H_24 },
    { 30, car_H_30 },
    { 26, car_H_26 },
    { 27, car_H_27 },
    { 29, car_H_29 },
    { 28, car_H_28 },
    { 31, car_H_31 },
  },
  .updates = {
    { 25, car_update_25 },
    { 24, car_update_24 },
    { 30, car_update_30 },
    { 26, car_update_26 },
    { 27, car_update_27 },
    { 29, car_update_29 },
    { 28, car_update_28 },
    { 31, car_update_31 },
  },
  .Hes = {
  },
  .sets = {
    { "mass", car_set_mass },
    { "rotational_inertia", car_set_rotational_inertia },
    { "center_to_front", car_set_center_to_front },
    { "center_to_rear", car_set_center_to_rear },
    { "stiffness_front", car_set_stiffness_front },
    { "stiffness_rear", car_set_stiffness_rear },
  },
  .extra_routines = {
  },
};

ekf_lib_init(car)
