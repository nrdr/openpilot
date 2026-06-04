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
void err_fun(double *nom_x, double *delta_x, double *out_6558187156506406544) {
   out_6558187156506406544[0] = delta_x[0] + nom_x[0];
   out_6558187156506406544[1] = delta_x[1] + nom_x[1];
   out_6558187156506406544[2] = delta_x[2] + nom_x[2];
   out_6558187156506406544[3] = delta_x[3] + nom_x[3];
   out_6558187156506406544[4] = delta_x[4] + nom_x[4];
   out_6558187156506406544[5] = delta_x[5] + nom_x[5];
   out_6558187156506406544[6] = delta_x[6] + nom_x[6];
   out_6558187156506406544[7] = delta_x[7] + nom_x[7];
   out_6558187156506406544[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_9123744096185346010) {
   out_9123744096185346010[0] = -nom_x[0] + true_x[0];
   out_9123744096185346010[1] = -nom_x[1] + true_x[1];
   out_9123744096185346010[2] = -nom_x[2] + true_x[2];
   out_9123744096185346010[3] = -nom_x[3] + true_x[3];
   out_9123744096185346010[4] = -nom_x[4] + true_x[4];
   out_9123744096185346010[5] = -nom_x[5] + true_x[5];
   out_9123744096185346010[6] = -nom_x[6] + true_x[6];
   out_9123744096185346010[7] = -nom_x[7] + true_x[7];
   out_9123744096185346010[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_8155804854245815792) {
   out_8155804854245815792[0] = 1.0;
   out_8155804854245815792[1] = 0.0;
   out_8155804854245815792[2] = 0.0;
   out_8155804854245815792[3] = 0.0;
   out_8155804854245815792[4] = 0.0;
   out_8155804854245815792[5] = 0.0;
   out_8155804854245815792[6] = 0.0;
   out_8155804854245815792[7] = 0.0;
   out_8155804854245815792[8] = 0.0;
   out_8155804854245815792[9] = 0.0;
   out_8155804854245815792[10] = 1.0;
   out_8155804854245815792[11] = 0.0;
   out_8155804854245815792[12] = 0.0;
   out_8155804854245815792[13] = 0.0;
   out_8155804854245815792[14] = 0.0;
   out_8155804854245815792[15] = 0.0;
   out_8155804854245815792[16] = 0.0;
   out_8155804854245815792[17] = 0.0;
   out_8155804854245815792[18] = 0.0;
   out_8155804854245815792[19] = 0.0;
   out_8155804854245815792[20] = 1.0;
   out_8155804854245815792[21] = 0.0;
   out_8155804854245815792[22] = 0.0;
   out_8155804854245815792[23] = 0.0;
   out_8155804854245815792[24] = 0.0;
   out_8155804854245815792[25] = 0.0;
   out_8155804854245815792[26] = 0.0;
   out_8155804854245815792[27] = 0.0;
   out_8155804854245815792[28] = 0.0;
   out_8155804854245815792[29] = 0.0;
   out_8155804854245815792[30] = 1.0;
   out_8155804854245815792[31] = 0.0;
   out_8155804854245815792[32] = 0.0;
   out_8155804854245815792[33] = 0.0;
   out_8155804854245815792[34] = 0.0;
   out_8155804854245815792[35] = 0.0;
   out_8155804854245815792[36] = 0.0;
   out_8155804854245815792[37] = 0.0;
   out_8155804854245815792[38] = 0.0;
   out_8155804854245815792[39] = 0.0;
   out_8155804854245815792[40] = 1.0;
   out_8155804854245815792[41] = 0.0;
   out_8155804854245815792[42] = 0.0;
   out_8155804854245815792[43] = 0.0;
   out_8155804854245815792[44] = 0.0;
   out_8155804854245815792[45] = 0.0;
   out_8155804854245815792[46] = 0.0;
   out_8155804854245815792[47] = 0.0;
   out_8155804854245815792[48] = 0.0;
   out_8155804854245815792[49] = 0.0;
   out_8155804854245815792[50] = 1.0;
   out_8155804854245815792[51] = 0.0;
   out_8155804854245815792[52] = 0.0;
   out_8155804854245815792[53] = 0.0;
   out_8155804854245815792[54] = 0.0;
   out_8155804854245815792[55] = 0.0;
   out_8155804854245815792[56] = 0.0;
   out_8155804854245815792[57] = 0.0;
   out_8155804854245815792[58] = 0.0;
   out_8155804854245815792[59] = 0.0;
   out_8155804854245815792[60] = 1.0;
   out_8155804854245815792[61] = 0.0;
   out_8155804854245815792[62] = 0.0;
   out_8155804854245815792[63] = 0.0;
   out_8155804854245815792[64] = 0.0;
   out_8155804854245815792[65] = 0.0;
   out_8155804854245815792[66] = 0.0;
   out_8155804854245815792[67] = 0.0;
   out_8155804854245815792[68] = 0.0;
   out_8155804854245815792[69] = 0.0;
   out_8155804854245815792[70] = 1.0;
   out_8155804854245815792[71] = 0.0;
   out_8155804854245815792[72] = 0.0;
   out_8155804854245815792[73] = 0.0;
   out_8155804854245815792[74] = 0.0;
   out_8155804854245815792[75] = 0.0;
   out_8155804854245815792[76] = 0.0;
   out_8155804854245815792[77] = 0.0;
   out_8155804854245815792[78] = 0.0;
   out_8155804854245815792[79] = 0.0;
   out_8155804854245815792[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3910178064661819655) {
   out_3910178064661819655[0] = state[0];
   out_3910178064661819655[1] = state[1];
   out_3910178064661819655[2] = state[2];
   out_3910178064661819655[3] = state[3];
   out_3910178064661819655[4] = state[4];
   out_3910178064661819655[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_3910178064661819655[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3910178064661819655[7] = state[7];
   out_3910178064661819655[8] = state[8];
}
void F_fun(double *state, double dt, double *out_8475894658360832836) {
   out_8475894658360832836[0] = 1;
   out_8475894658360832836[1] = 0;
   out_8475894658360832836[2] = 0;
   out_8475894658360832836[3] = 0;
   out_8475894658360832836[4] = 0;
   out_8475894658360832836[5] = 0;
   out_8475894658360832836[6] = 0;
   out_8475894658360832836[7] = 0;
   out_8475894658360832836[8] = 0;
   out_8475894658360832836[9] = 0;
   out_8475894658360832836[10] = 1;
   out_8475894658360832836[11] = 0;
   out_8475894658360832836[12] = 0;
   out_8475894658360832836[13] = 0;
   out_8475894658360832836[14] = 0;
   out_8475894658360832836[15] = 0;
   out_8475894658360832836[16] = 0;
   out_8475894658360832836[17] = 0;
   out_8475894658360832836[18] = 0;
   out_8475894658360832836[19] = 0;
   out_8475894658360832836[20] = 1;
   out_8475894658360832836[21] = 0;
   out_8475894658360832836[22] = 0;
   out_8475894658360832836[23] = 0;
   out_8475894658360832836[24] = 0;
   out_8475894658360832836[25] = 0;
   out_8475894658360832836[26] = 0;
   out_8475894658360832836[27] = 0;
   out_8475894658360832836[28] = 0;
   out_8475894658360832836[29] = 0;
   out_8475894658360832836[30] = 1;
   out_8475894658360832836[31] = 0;
   out_8475894658360832836[32] = 0;
   out_8475894658360832836[33] = 0;
   out_8475894658360832836[34] = 0;
   out_8475894658360832836[35] = 0;
   out_8475894658360832836[36] = 0;
   out_8475894658360832836[37] = 0;
   out_8475894658360832836[38] = 0;
   out_8475894658360832836[39] = 0;
   out_8475894658360832836[40] = 1;
   out_8475894658360832836[41] = 0;
   out_8475894658360832836[42] = 0;
   out_8475894658360832836[43] = 0;
   out_8475894658360832836[44] = 0;
   out_8475894658360832836[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_8475894658360832836[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_8475894658360832836[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8475894658360832836[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8475894658360832836[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_8475894658360832836[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_8475894658360832836[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_8475894658360832836[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_8475894658360832836[53] = -9.8100000000000005*dt;
   out_8475894658360832836[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_8475894658360832836[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_8475894658360832836[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8475894658360832836[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8475894658360832836[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_8475894658360832836[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_8475894658360832836[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_8475894658360832836[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8475894658360832836[62] = 0;
   out_8475894658360832836[63] = 0;
   out_8475894658360832836[64] = 0;
   out_8475894658360832836[65] = 0;
   out_8475894658360832836[66] = 0;
   out_8475894658360832836[67] = 0;
   out_8475894658360832836[68] = 0;
   out_8475894658360832836[69] = 0;
   out_8475894658360832836[70] = 1;
   out_8475894658360832836[71] = 0;
   out_8475894658360832836[72] = 0;
   out_8475894658360832836[73] = 0;
   out_8475894658360832836[74] = 0;
   out_8475894658360832836[75] = 0;
   out_8475894658360832836[76] = 0;
   out_8475894658360832836[77] = 0;
   out_8475894658360832836[78] = 0;
   out_8475894658360832836[79] = 0;
   out_8475894658360832836[80] = 1;
}
void h_25(double *state, double *unused, double *out_5967448892281792710) {
   out_5967448892281792710[0] = state[6];
}
void H_25(double *state, double *unused, double *out_5496108376535866715) {
   out_5496108376535866715[0] = 0;
   out_5496108376535866715[1] = 0;
   out_5496108376535866715[2] = 0;
   out_5496108376535866715[3] = 0;
   out_5496108376535866715[4] = 0;
   out_5496108376535866715[5] = 0;
   out_5496108376535866715[6] = 1;
   out_5496108376535866715[7] = 0;
   out_5496108376535866715[8] = 0;
}
void h_24(double *state, double *unused, double *out_2080633378133349492) {
   out_2080633378133349492[0] = state[4];
   out_2080633378133349492[1] = state[5];
}
void H_24(double *state, double *unused, double *out_3648758333415010447) {
   out_3648758333415010447[0] = 0;
   out_3648758333415010447[1] = 0;
   out_3648758333415010447[2] = 0;
   out_3648758333415010447[3] = 0;
   out_3648758333415010447[4] = 1;
   out_3648758333415010447[5] = 0;
   out_3648758333415010447[6] = 0;
   out_3648758333415010447[7] = 0;
   out_3648758333415010447[8] = 0;
   out_3648758333415010447[9] = 0;
   out_3648758333415010447[10] = 0;
   out_3648758333415010447[11] = 0;
   out_3648758333415010447[12] = 0;
   out_3648758333415010447[13] = 0;
   out_3648758333415010447[14] = 1;
   out_3648758333415010447[15] = 0;
   out_3648758333415010447[16] = 0;
   out_3648758333415010447[17] = 0;
}
void h_30(double *state, double *unused, double *out_3019722901926307749) {
   out_3019722901926307749[0] = state[4];
}
void H_30(double *state, double *unused, double *out_8014441335043115342) {
   out_8014441335043115342[0] = 0;
   out_8014441335043115342[1] = 0;
   out_8014441335043115342[2] = 0;
   out_8014441335043115342[3] = 0;
   out_8014441335043115342[4] = 1;
   out_8014441335043115342[5] = 0;
   out_8014441335043115342[6] = 0;
   out_8014441335043115342[7] = 0;
   out_8014441335043115342[8] = 0;
}
void h_26(double *state, double *unused, double *out_4001806995261605861) {
   out_4001806995261605861[0] = state[7];
}
void H_26(double *state, double *unused, double *out_1754605057661810491) {
   out_1754605057661810491[0] = 0;
   out_1754605057661810491[1] = 0;
   out_1754605057661810491[2] = 0;
   out_1754605057661810491[3] = 0;
   out_1754605057661810491[4] = 0;
   out_1754605057661810491[5] = 0;
   out_1754605057661810491[6] = 0;
   out_1754605057661810491[7] = 1;
   out_1754605057661810491[8] = 0;
}
void h_27(double *state, double *unused, double *out_7327076423291162538) {
   out_7327076423291162538[0] = state[3];
}
void H_27(double *state, double *unused, double *out_5839678023242690431) {
   out_5839678023242690431[0] = 0;
   out_5839678023242690431[1] = 0;
   out_5839678023242690431[2] = 0;
   out_5839678023242690431[3] = 1;
   out_5839678023242690431[4] = 0;
   out_5839678023242690431[5] = 0;
   out_5839678023242690431[6] = 0;
   out_5839678023242690431[7] = 0;
   out_5839678023242690431[8] = 0;
}
void h_29(double *state, double *unused, double *out_1981950365734537896) {
   out_1981950365734537896[0] = state[1];
}
void H_29(double *state, double *unused, double *out_8524672679357507526) {
   out_8524672679357507526[0] = 0;
   out_8524672679357507526[1] = 1;
   out_8524672679357507526[2] = 0;
   out_8524672679357507526[3] = 0;
   out_8524672679357507526[4] = 0;
   out_8524672679357507526[5] = 0;
   out_8524672679357507526[6] = 0;
   out_8524672679357507526[7] = 0;
   out_8524672679357507526[8] = 0;
}
void h_28(double *state, double *unused, double *out_2901715507992931005) {
   out_2901715507992931005[0] = state[0];
}
void H_28(double *state, double *unused, double *out_3442273662287976952) {
   out_3442273662287976952[0] = 1;
   out_3442273662287976952[1] = 0;
   out_3442273662287976952[2] = 0;
   out_3442273662287976952[3] = 0;
   out_3442273662287976952[4] = 0;
   out_3442273662287976952[5] = 0;
   out_3442273662287976952[6] = 0;
   out_3442273662287976952[7] = 0;
   out_3442273662287976952[8] = 0;
}
void h_31(double *state, double *unused, double *out_4565484434131335742) {
   out_4565484434131335742[0] = state[8];
}
void H_31(double *state, double *unused, double *out_1128396955428459015) {
   out_1128396955428459015[0] = 0;
   out_1128396955428459015[1] = 0;
   out_1128396955428459015[2] = 0;
   out_1128396955428459015[3] = 0;
   out_1128396955428459015[4] = 0;
   out_1128396955428459015[5] = 0;
   out_1128396955428459015[6] = 0;
   out_1128396955428459015[7] = 0;
   out_1128396955428459015[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_6558187156506406544) {
  err_fun(nom_x, delta_x, out_6558187156506406544);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_9123744096185346010) {
  inv_err_fun(nom_x, true_x, out_9123744096185346010);
}
void car_H_mod_fun(double *state, double *out_8155804854245815792) {
  H_mod_fun(state, out_8155804854245815792);
}
void car_f_fun(double *state, double dt, double *out_3910178064661819655) {
  f_fun(state,  dt, out_3910178064661819655);
}
void car_F_fun(double *state, double dt, double *out_8475894658360832836) {
  F_fun(state,  dt, out_8475894658360832836);
}
void car_h_25(double *state, double *unused, double *out_5967448892281792710) {
  h_25(state, unused, out_5967448892281792710);
}
void car_H_25(double *state, double *unused, double *out_5496108376535866715) {
  H_25(state, unused, out_5496108376535866715);
}
void car_h_24(double *state, double *unused, double *out_2080633378133349492) {
  h_24(state, unused, out_2080633378133349492);
}
void car_H_24(double *state, double *unused, double *out_3648758333415010447) {
  H_24(state, unused, out_3648758333415010447);
}
void car_h_30(double *state, double *unused, double *out_3019722901926307749) {
  h_30(state, unused, out_3019722901926307749);
}
void car_H_30(double *state, double *unused, double *out_8014441335043115342) {
  H_30(state, unused, out_8014441335043115342);
}
void car_h_26(double *state, double *unused, double *out_4001806995261605861) {
  h_26(state, unused, out_4001806995261605861);
}
void car_H_26(double *state, double *unused, double *out_1754605057661810491) {
  H_26(state, unused, out_1754605057661810491);
}
void car_h_27(double *state, double *unused, double *out_7327076423291162538) {
  h_27(state, unused, out_7327076423291162538);
}
void car_H_27(double *state, double *unused, double *out_5839678023242690431) {
  H_27(state, unused, out_5839678023242690431);
}
void car_h_29(double *state, double *unused, double *out_1981950365734537896) {
  h_29(state, unused, out_1981950365734537896);
}
void car_H_29(double *state, double *unused, double *out_8524672679357507526) {
  H_29(state, unused, out_8524672679357507526);
}
void car_h_28(double *state, double *unused, double *out_2901715507992931005) {
  h_28(state, unused, out_2901715507992931005);
}
void car_H_28(double *state, double *unused, double *out_3442273662287976952) {
  H_28(state, unused, out_3442273662287976952);
}
void car_h_31(double *state, double *unused, double *out_4565484434131335742) {
  h_31(state, unused, out_4565484434131335742);
}
void car_H_31(double *state, double *unused, double *out_1128396955428459015) {
  H_31(state, unused, out_1128396955428459015);
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
