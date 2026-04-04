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
void err_fun(double *nom_x, double *delta_x, double *out_1590755408767672601) {
   out_1590755408767672601[0] = delta_x[0] + nom_x[0];
   out_1590755408767672601[1] = delta_x[1] + nom_x[1];
   out_1590755408767672601[2] = delta_x[2] + nom_x[2];
   out_1590755408767672601[3] = delta_x[3] + nom_x[3];
   out_1590755408767672601[4] = delta_x[4] + nom_x[4];
   out_1590755408767672601[5] = delta_x[5] + nom_x[5];
   out_1590755408767672601[6] = delta_x[6] + nom_x[6];
   out_1590755408767672601[7] = delta_x[7] + nom_x[7];
   out_1590755408767672601[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1209319377282347077) {
   out_1209319377282347077[0] = -nom_x[0] + true_x[0];
   out_1209319377282347077[1] = -nom_x[1] + true_x[1];
   out_1209319377282347077[2] = -nom_x[2] + true_x[2];
   out_1209319377282347077[3] = -nom_x[3] + true_x[3];
   out_1209319377282347077[4] = -nom_x[4] + true_x[4];
   out_1209319377282347077[5] = -nom_x[5] + true_x[5];
   out_1209319377282347077[6] = -nom_x[6] + true_x[6];
   out_1209319377282347077[7] = -nom_x[7] + true_x[7];
   out_1209319377282347077[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_2794585081193416972) {
   out_2794585081193416972[0] = 1.0;
   out_2794585081193416972[1] = 0.0;
   out_2794585081193416972[2] = 0.0;
   out_2794585081193416972[3] = 0.0;
   out_2794585081193416972[4] = 0.0;
   out_2794585081193416972[5] = 0.0;
   out_2794585081193416972[6] = 0.0;
   out_2794585081193416972[7] = 0.0;
   out_2794585081193416972[8] = 0.0;
   out_2794585081193416972[9] = 0.0;
   out_2794585081193416972[10] = 1.0;
   out_2794585081193416972[11] = 0.0;
   out_2794585081193416972[12] = 0.0;
   out_2794585081193416972[13] = 0.0;
   out_2794585081193416972[14] = 0.0;
   out_2794585081193416972[15] = 0.0;
   out_2794585081193416972[16] = 0.0;
   out_2794585081193416972[17] = 0.0;
   out_2794585081193416972[18] = 0.0;
   out_2794585081193416972[19] = 0.0;
   out_2794585081193416972[20] = 1.0;
   out_2794585081193416972[21] = 0.0;
   out_2794585081193416972[22] = 0.0;
   out_2794585081193416972[23] = 0.0;
   out_2794585081193416972[24] = 0.0;
   out_2794585081193416972[25] = 0.0;
   out_2794585081193416972[26] = 0.0;
   out_2794585081193416972[27] = 0.0;
   out_2794585081193416972[28] = 0.0;
   out_2794585081193416972[29] = 0.0;
   out_2794585081193416972[30] = 1.0;
   out_2794585081193416972[31] = 0.0;
   out_2794585081193416972[32] = 0.0;
   out_2794585081193416972[33] = 0.0;
   out_2794585081193416972[34] = 0.0;
   out_2794585081193416972[35] = 0.0;
   out_2794585081193416972[36] = 0.0;
   out_2794585081193416972[37] = 0.0;
   out_2794585081193416972[38] = 0.0;
   out_2794585081193416972[39] = 0.0;
   out_2794585081193416972[40] = 1.0;
   out_2794585081193416972[41] = 0.0;
   out_2794585081193416972[42] = 0.0;
   out_2794585081193416972[43] = 0.0;
   out_2794585081193416972[44] = 0.0;
   out_2794585081193416972[45] = 0.0;
   out_2794585081193416972[46] = 0.0;
   out_2794585081193416972[47] = 0.0;
   out_2794585081193416972[48] = 0.0;
   out_2794585081193416972[49] = 0.0;
   out_2794585081193416972[50] = 1.0;
   out_2794585081193416972[51] = 0.0;
   out_2794585081193416972[52] = 0.0;
   out_2794585081193416972[53] = 0.0;
   out_2794585081193416972[54] = 0.0;
   out_2794585081193416972[55] = 0.0;
   out_2794585081193416972[56] = 0.0;
   out_2794585081193416972[57] = 0.0;
   out_2794585081193416972[58] = 0.0;
   out_2794585081193416972[59] = 0.0;
   out_2794585081193416972[60] = 1.0;
   out_2794585081193416972[61] = 0.0;
   out_2794585081193416972[62] = 0.0;
   out_2794585081193416972[63] = 0.0;
   out_2794585081193416972[64] = 0.0;
   out_2794585081193416972[65] = 0.0;
   out_2794585081193416972[66] = 0.0;
   out_2794585081193416972[67] = 0.0;
   out_2794585081193416972[68] = 0.0;
   out_2794585081193416972[69] = 0.0;
   out_2794585081193416972[70] = 1.0;
   out_2794585081193416972[71] = 0.0;
   out_2794585081193416972[72] = 0.0;
   out_2794585081193416972[73] = 0.0;
   out_2794585081193416972[74] = 0.0;
   out_2794585081193416972[75] = 0.0;
   out_2794585081193416972[76] = 0.0;
   out_2794585081193416972[77] = 0.0;
   out_2794585081193416972[78] = 0.0;
   out_2794585081193416972[79] = 0.0;
   out_2794585081193416972[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_1208708832429879679) {
   out_1208708832429879679[0] = state[0];
   out_1208708832429879679[1] = state[1];
   out_1208708832429879679[2] = state[2];
   out_1208708832429879679[3] = state[3];
   out_1208708832429879679[4] = state[4];
   out_1208708832429879679[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_1208708832429879679[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_1208708832429879679[7] = state[7];
   out_1208708832429879679[8] = state[8];
}
void F_fun(double *state, double dt, double *out_6751886823644579436) {
   out_6751886823644579436[0] = 1;
   out_6751886823644579436[1] = 0;
   out_6751886823644579436[2] = 0;
   out_6751886823644579436[3] = 0;
   out_6751886823644579436[4] = 0;
   out_6751886823644579436[5] = 0;
   out_6751886823644579436[6] = 0;
   out_6751886823644579436[7] = 0;
   out_6751886823644579436[8] = 0;
   out_6751886823644579436[9] = 0;
   out_6751886823644579436[10] = 1;
   out_6751886823644579436[11] = 0;
   out_6751886823644579436[12] = 0;
   out_6751886823644579436[13] = 0;
   out_6751886823644579436[14] = 0;
   out_6751886823644579436[15] = 0;
   out_6751886823644579436[16] = 0;
   out_6751886823644579436[17] = 0;
   out_6751886823644579436[18] = 0;
   out_6751886823644579436[19] = 0;
   out_6751886823644579436[20] = 1;
   out_6751886823644579436[21] = 0;
   out_6751886823644579436[22] = 0;
   out_6751886823644579436[23] = 0;
   out_6751886823644579436[24] = 0;
   out_6751886823644579436[25] = 0;
   out_6751886823644579436[26] = 0;
   out_6751886823644579436[27] = 0;
   out_6751886823644579436[28] = 0;
   out_6751886823644579436[29] = 0;
   out_6751886823644579436[30] = 1;
   out_6751886823644579436[31] = 0;
   out_6751886823644579436[32] = 0;
   out_6751886823644579436[33] = 0;
   out_6751886823644579436[34] = 0;
   out_6751886823644579436[35] = 0;
   out_6751886823644579436[36] = 0;
   out_6751886823644579436[37] = 0;
   out_6751886823644579436[38] = 0;
   out_6751886823644579436[39] = 0;
   out_6751886823644579436[40] = 1;
   out_6751886823644579436[41] = 0;
   out_6751886823644579436[42] = 0;
   out_6751886823644579436[43] = 0;
   out_6751886823644579436[44] = 0;
   out_6751886823644579436[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_6751886823644579436[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_6751886823644579436[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_6751886823644579436[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_6751886823644579436[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_6751886823644579436[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_6751886823644579436[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_6751886823644579436[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_6751886823644579436[53] = -9.8100000000000005*dt;
   out_6751886823644579436[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_6751886823644579436[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_6751886823644579436[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6751886823644579436[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6751886823644579436[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_6751886823644579436[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_6751886823644579436[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_6751886823644579436[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6751886823644579436[62] = 0;
   out_6751886823644579436[63] = 0;
   out_6751886823644579436[64] = 0;
   out_6751886823644579436[65] = 0;
   out_6751886823644579436[66] = 0;
   out_6751886823644579436[67] = 0;
   out_6751886823644579436[68] = 0;
   out_6751886823644579436[69] = 0;
   out_6751886823644579436[70] = 1;
   out_6751886823644579436[71] = 0;
   out_6751886823644579436[72] = 0;
   out_6751886823644579436[73] = 0;
   out_6751886823644579436[74] = 0;
   out_6751886823644579436[75] = 0;
   out_6751886823644579436[76] = 0;
   out_6751886823644579436[77] = 0;
   out_6751886823644579436[78] = 0;
   out_6751886823644579436[79] = 0;
   out_6751886823644579436[80] = 1;
}
void h_25(double *state, double *unused, double *out_6838891315424905032) {
   out_6838891315424905032[0] = state[6];
}
void H_25(double *state, double *unused, double *out_3743706003221899181) {
   out_3743706003221899181[0] = 0;
   out_3743706003221899181[1] = 0;
   out_3743706003221899181[2] = 0;
   out_3743706003221899181[3] = 0;
   out_3743706003221899181[4] = 0;
   out_3743706003221899181[5] = 0;
   out_3743706003221899181[6] = 1;
   out_3743706003221899181[7] = 0;
   out_3743706003221899181[8] = 0;
}
void h_24(double *state, double *unused, double *out_4852083295210749522) {
   out_4852083295210749522[0] = state[4];
   out_4852083295210749522[1] = state[5];
}
void H_24(double *state, double *unused, double *out_5474972884418457210) {
   out_5474972884418457210[0] = 0;
   out_5474972884418457210[1] = 0;
   out_5474972884418457210[2] = 0;
   out_5474972884418457210[3] = 0;
   out_5474972884418457210[4] = 1;
   out_5474972884418457210[5] = 0;
   out_5474972884418457210[6] = 0;
   out_5474972884418457210[7] = 0;
   out_5474972884418457210[8] = 0;
   out_5474972884418457210[9] = 0;
   out_5474972884418457210[10] = 0;
   out_5474972884418457210[11] = 0;
   out_5474972884418457210[12] = 0;
   out_5474972884418457210[13] = 0;
   out_5474972884418457210[14] = 1;
   out_5474972884418457210[15] = 0;
   out_5474972884418457210[16] = 0;
   out_5474972884418457210[17] = 0;
}
void h_30(double *state, double *unused, double *out_7970403230030624234) {
   out_7970403230030624234[0] = state[4];
}
void H_30(double *state, double *unused, double *out_783990326905709017) {
   out_783990326905709017[0] = 0;
   out_783990326905709017[1] = 0;
   out_783990326905709017[2] = 0;
   out_783990326905709017[3] = 0;
   out_783990326905709017[4] = 1;
   out_783990326905709017[5] = 0;
   out_783990326905709017[6] = 0;
   out_783990326905709017[7] = 0;
   out_783990326905709017[8] = 0;
}
void h_26(double *state, double *unused, double *out_1011565941976216531) {
   out_1011565941976216531[0] = state[7];
}
void H_26(double *state, double *unused, double *out_2202684347842957) {
   out_2202684347842957[0] = 0;
   out_2202684347842957[1] = 0;
   out_2202684347842957[2] = 0;
   out_2202684347842957[3] = 0;
   out_2202684347842957[4] = 0;
   out_2202684347842957[5] = 0;
   out_2202684347842957[6] = 0;
   out_2202684347842957[7] = 1;
   out_2202684347842957[8] = 0;
}
void h_27(double *state, double *unused, double *out_4234485994616207381) {
   out_4234485994616207381[0] = state[3];
}
void H_27(double *state, double *unused, double *out_1439603744278234200) {
   out_1439603744278234200[0] = 0;
   out_1439603744278234200[1] = 0;
   out_1439603744278234200[2] = 0;
   out_1439603744278234200[3] = 1;
   out_1439603744278234200[4] = 0;
   out_1439603744278234200[5] = 0;
   out_1439603744278234200[6] = 0;
   out_1439603744278234200[7] = 0;
   out_1439603744278234200[8] = 0;
}
void h_29(double *state, double *unused, double *out_2968729962369778589) {
   out_2968729962369778589[0] = state[1];
}
void H_29(double *state, double *unused, double *out_273758982591316833) {
   out_273758982591316833[0] = 0;
   out_273758982591316833[1] = 1;
   out_273758982591316833[2] = 0;
   out_273758982591316833[3] = 0;
   out_273758982591316833[4] = 0;
   out_273758982591316833[5] = 0;
   out_273758982591316833[6] = 0;
   out_273758982591316833[7] = 0;
   out_273758982591316833[8] = 0;
}
void h_28(double *state, double *unused, double *out_3200657439812493432) {
   out_3200657439812493432[0] = state[0];
}
void H_28(double *state, double *unused, double *out_5356157999660847407) {
   out_5356157999660847407[0] = 1;
   out_5356157999660847407[1] = 0;
   out_5356157999660847407[2] = 0;
   out_5356157999660847407[3] = 0;
   out_5356157999660847407[4] = 0;
   out_5356157999660847407[5] = 0;
   out_5356157999660847407[6] = 0;
   out_5356157999660847407[7] = 0;
   out_5356157999660847407[8] = 0;
}
void h_31(double *state, double *unused, double *out_1042381335329144153) {
   out_1042381335329144153[0] = state[8];
}
void H_31(double *state, double *unused, double *out_3774351965098859609) {
   out_3774351965098859609[0] = 0;
   out_3774351965098859609[1] = 0;
   out_3774351965098859609[2] = 0;
   out_3774351965098859609[3] = 0;
   out_3774351965098859609[4] = 0;
   out_3774351965098859609[5] = 0;
   out_3774351965098859609[6] = 0;
   out_3774351965098859609[7] = 0;
   out_3774351965098859609[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_1590755408767672601) {
  err_fun(nom_x, delta_x, out_1590755408767672601);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1209319377282347077) {
  inv_err_fun(nom_x, true_x, out_1209319377282347077);
}
void car_H_mod_fun(double *state, double *out_2794585081193416972) {
  H_mod_fun(state, out_2794585081193416972);
}
void car_f_fun(double *state, double dt, double *out_1208708832429879679) {
  f_fun(state,  dt, out_1208708832429879679);
}
void car_F_fun(double *state, double dt, double *out_6751886823644579436) {
  F_fun(state,  dt, out_6751886823644579436);
}
void car_h_25(double *state, double *unused, double *out_6838891315424905032) {
  h_25(state, unused, out_6838891315424905032);
}
void car_H_25(double *state, double *unused, double *out_3743706003221899181) {
  H_25(state, unused, out_3743706003221899181);
}
void car_h_24(double *state, double *unused, double *out_4852083295210749522) {
  h_24(state, unused, out_4852083295210749522);
}
void car_H_24(double *state, double *unused, double *out_5474972884418457210) {
  H_24(state, unused, out_5474972884418457210);
}
void car_h_30(double *state, double *unused, double *out_7970403230030624234) {
  h_30(state, unused, out_7970403230030624234);
}
void car_H_30(double *state, double *unused, double *out_783990326905709017) {
  H_30(state, unused, out_783990326905709017);
}
void car_h_26(double *state, double *unused, double *out_1011565941976216531) {
  h_26(state, unused, out_1011565941976216531);
}
void car_H_26(double *state, double *unused, double *out_2202684347842957) {
  H_26(state, unused, out_2202684347842957);
}
void car_h_27(double *state, double *unused, double *out_4234485994616207381) {
  h_27(state, unused, out_4234485994616207381);
}
void car_H_27(double *state, double *unused, double *out_1439603744278234200) {
  H_27(state, unused, out_1439603744278234200);
}
void car_h_29(double *state, double *unused, double *out_2968729962369778589) {
  h_29(state, unused, out_2968729962369778589);
}
void car_H_29(double *state, double *unused, double *out_273758982591316833) {
  H_29(state, unused, out_273758982591316833);
}
void car_h_28(double *state, double *unused, double *out_3200657439812493432) {
  h_28(state, unused, out_3200657439812493432);
}
void car_H_28(double *state, double *unused, double *out_5356157999660847407) {
  H_28(state, unused, out_5356157999660847407);
}
void car_h_31(double *state, double *unused, double *out_1042381335329144153) {
  h_31(state, unused, out_1042381335329144153);
}
void car_H_31(double *state, double *unused, double *out_3774351965098859609) {
  H_31(state, unused, out_3774351965098859609);
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
