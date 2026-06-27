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
void err_fun(double *nom_x, double *delta_x, double *out_5591252770855935724) {
   out_5591252770855935724[0] = delta_x[0] + nom_x[0];
   out_5591252770855935724[1] = delta_x[1] + nom_x[1];
   out_5591252770855935724[2] = delta_x[2] + nom_x[2];
   out_5591252770855935724[3] = delta_x[3] + nom_x[3];
   out_5591252770855935724[4] = delta_x[4] + nom_x[4];
   out_5591252770855935724[5] = delta_x[5] + nom_x[5];
   out_5591252770855935724[6] = delta_x[6] + nom_x[6];
   out_5591252770855935724[7] = delta_x[7] + nom_x[7];
   out_5591252770855935724[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4117300928169881984) {
   out_4117300928169881984[0] = -nom_x[0] + true_x[0];
   out_4117300928169881984[1] = -nom_x[1] + true_x[1];
   out_4117300928169881984[2] = -nom_x[2] + true_x[2];
   out_4117300928169881984[3] = -nom_x[3] + true_x[3];
   out_4117300928169881984[4] = -nom_x[4] + true_x[4];
   out_4117300928169881984[5] = -nom_x[5] + true_x[5];
   out_4117300928169881984[6] = -nom_x[6] + true_x[6];
   out_4117300928169881984[7] = -nom_x[7] + true_x[7];
   out_4117300928169881984[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_5783550393054446142) {
   out_5783550393054446142[0] = 1.0;
   out_5783550393054446142[1] = 0.0;
   out_5783550393054446142[2] = 0.0;
   out_5783550393054446142[3] = 0.0;
   out_5783550393054446142[4] = 0.0;
   out_5783550393054446142[5] = 0.0;
   out_5783550393054446142[6] = 0.0;
   out_5783550393054446142[7] = 0.0;
   out_5783550393054446142[8] = 0.0;
   out_5783550393054446142[9] = 0.0;
   out_5783550393054446142[10] = 1.0;
   out_5783550393054446142[11] = 0.0;
   out_5783550393054446142[12] = 0.0;
   out_5783550393054446142[13] = 0.0;
   out_5783550393054446142[14] = 0.0;
   out_5783550393054446142[15] = 0.0;
   out_5783550393054446142[16] = 0.0;
   out_5783550393054446142[17] = 0.0;
   out_5783550393054446142[18] = 0.0;
   out_5783550393054446142[19] = 0.0;
   out_5783550393054446142[20] = 1.0;
   out_5783550393054446142[21] = 0.0;
   out_5783550393054446142[22] = 0.0;
   out_5783550393054446142[23] = 0.0;
   out_5783550393054446142[24] = 0.0;
   out_5783550393054446142[25] = 0.0;
   out_5783550393054446142[26] = 0.0;
   out_5783550393054446142[27] = 0.0;
   out_5783550393054446142[28] = 0.0;
   out_5783550393054446142[29] = 0.0;
   out_5783550393054446142[30] = 1.0;
   out_5783550393054446142[31] = 0.0;
   out_5783550393054446142[32] = 0.0;
   out_5783550393054446142[33] = 0.0;
   out_5783550393054446142[34] = 0.0;
   out_5783550393054446142[35] = 0.0;
   out_5783550393054446142[36] = 0.0;
   out_5783550393054446142[37] = 0.0;
   out_5783550393054446142[38] = 0.0;
   out_5783550393054446142[39] = 0.0;
   out_5783550393054446142[40] = 1.0;
   out_5783550393054446142[41] = 0.0;
   out_5783550393054446142[42] = 0.0;
   out_5783550393054446142[43] = 0.0;
   out_5783550393054446142[44] = 0.0;
   out_5783550393054446142[45] = 0.0;
   out_5783550393054446142[46] = 0.0;
   out_5783550393054446142[47] = 0.0;
   out_5783550393054446142[48] = 0.0;
   out_5783550393054446142[49] = 0.0;
   out_5783550393054446142[50] = 1.0;
   out_5783550393054446142[51] = 0.0;
   out_5783550393054446142[52] = 0.0;
   out_5783550393054446142[53] = 0.0;
   out_5783550393054446142[54] = 0.0;
   out_5783550393054446142[55] = 0.0;
   out_5783550393054446142[56] = 0.0;
   out_5783550393054446142[57] = 0.0;
   out_5783550393054446142[58] = 0.0;
   out_5783550393054446142[59] = 0.0;
   out_5783550393054446142[60] = 1.0;
   out_5783550393054446142[61] = 0.0;
   out_5783550393054446142[62] = 0.0;
   out_5783550393054446142[63] = 0.0;
   out_5783550393054446142[64] = 0.0;
   out_5783550393054446142[65] = 0.0;
   out_5783550393054446142[66] = 0.0;
   out_5783550393054446142[67] = 0.0;
   out_5783550393054446142[68] = 0.0;
   out_5783550393054446142[69] = 0.0;
   out_5783550393054446142[70] = 1.0;
   out_5783550393054446142[71] = 0.0;
   out_5783550393054446142[72] = 0.0;
   out_5783550393054446142[73] = 0.0;
   out_5783550393054446142[74] = 0.0;
   out_5783550393054446142[75] = 0.0;
   out_5783550393054446142[76] = 0.0;
   out_5783550393054446142[77] = 0.0;
   out_5783550393054446142[78] = 0.0;
   out_5783550393054446142[79] = 0.0;
   out_5783550393054446142[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3463430665265427786) {
   out_3463430665265427786[0] = state[0];
   out_3463430665265427786[1] = state[1];
   out_3463430665265427786[2] = state[2];
   out_3463430665265427786[3] = state[3];
   out_3463430665265427786[4] = state[4];
   out_3463430665265427786[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_3463430665265427786[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3463430665265427786[7] = state[7];
   out_3463430665265427786[8] = state[8];
}
void F_fun(double *state, double dt, double *out_7274748722386343746) {
   out_7274748722386343746[0] = 1;
   out_7274748722386343746[1] = 0;
   out_7274748722386343746[2] = 0;
   out_7274748722386343746[3] = 0;
   out_7274748722386343746[4] = 0;
   out_7274748722386343746[5] = 0;
   out_7274748722386343746[6] = 0;
   out_7274748722386343746[7] = 0;
   out_7274748722386343746[8] = 0;
   out_7274748722386343746[9] = 0;
   out_7274748722386343746[10] = 1;
   out_7274748722386343746[11] = 0;
   out_7274748722386343746[12] = 0;
   out_7274748722386343746[13] = 0;
   out_7274748722386343746[14] = 0;
   out_7274748722386343746[15] = 0;
   out_7274748722386343746[16] = 0;
   out_7274748722386343746[17] = 0;
   out_7274748722386343746[18] = 0;
   out_7274748722386343746[19] = 0;
   out_7274748722386343746[20] = 1;
   out_7274748722386343746[21] = 0;
   out_7274748722386343746[22] = 0;
   out_7274748722386343746[23] = 0;
   out_7274748722386343746[24] = 0;
   out_7274748722386343746[25] = 0;
   out_7274748722386343746[26] = 0;
   out_7274748722386343746[27] = 0;
   out_7274748722386343746[28] = 0;
   out_7274748722386343746[29] = 0;
   out_7274748722386343746[30] = 1;
   out_7274748722386343746[31] = 0;
   out_7274748722386343746[32] = 0;
   out_7274748722386343746[33] = 0;
   out_7274748722386343746[34] = 0;
   out_7274748722386343746[35] = 0;
   out_7274748722386343746[36] = 0;
   out_7274748722386343746[37] = 0;
   out_7274748722386343746[38] = 0;
   out_7274748722386343746[39] = 0;
   out_7274748722386343746[40] = 1;
   out_7274748722386343746[41] = 0;
   out_7274748722386343746[42] = 0;
   out_7274748722386343746[43] = 0;
   out_7274748722386343746[44] = 0;
   out_7274748722386343746[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_7274748722386343746[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_7274748722386343746[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7274748722386343746[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7274748722386343746[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_7274748722386343746[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_7274748722386343746[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_7274748722386343746[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_7274748722386343746[53] = -9.8100000000000005*dt;
   out_7274748722386343746[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_7274748722386343746[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_7274748722386343746[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7274748722386343746[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7274748722386343746[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_7274748722386343746[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_7274748722386343746[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_7274748722386343746[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7274748722386343746[62] = 0;
   out_7274748722386343746[63] = 0;
   out_7274748722386343746[64] = 0;
   out_7274748722386343746[65] = 0;
   out_7274748722386343746[66] = 0;
   out_7274748722386343746[67] = 0;
   out_7274748722386343746[68] = 0;
   out_7274748722386343746[69] = 0;
   out_7274748722386343746[70] = 1;
   out_7274748722386343746[71] = 0;
   out_7274748722386343746[72] = 0;
   out_7274748722386343746[73] = 0;
   out_7274748722386343746[74] = 0;
   out_7274748722386343746[75] = 0;
   out_7274748722386343746[76] = 0;
   out_7274748722386343746[77] = 0;
   out_7274748722386343746[78] = 0;
   out_7274748722386343746[79] = 0;
   out_7274748722386343746[80] = 1;
}
void h_25(double *state, double *unused, double *out_4674479974339004779) {
   out_4674479974339004779[0] = state[6];
}
void H_25(double *state, double *unused, double *out_3470005454742868237) {
   out_3470005454742868237[0] = 0;
   out_3470005454742868237[1] = 0;
   out_3470005454742868237[2] = 0;
   out_3470005454742868237[3] = 0;
   out_3470005454742868237[4] = 0;
   out_3470005454742868237[5] = 0;
   out_3470005454742868237[6] = 1;
   out_3470005454742868237[7] = 0;
   out_3470005454742868237[8] = 0;
}
void h_24(double *state, double *unused, double *out_56151919158375531) {
   out_56151919158375531[0] = state[4];
   out_56151919158375531[1] = state[5];
}
void H_24(double *state, double *unused, double *out_1297355855737368671) {
   out_1297355855737368671[0] = 0;
   out_1297355855737368671[1] = 0;
   out_1297355855737368671[2] = 0;
   out_1297355855737368671[3] = 0;
   out_1297355855737368671[4] = 1;
   out_1297355855737368671[5] = 0;
   out_1297355855737368671[6] = 0;
   out_1297355855737368671[7] = 0;
   out_1297355855737368671[8] = 0;
   out_1297355855737368671[9] = 0;
   out_1297355855737368671[10] = 0;
   out_1297355855737368671[11] = 0;
   out_1297355855737368671[12] = 0;
   out_1297355855737368671[13] = 0;
   out_1297355855737368671[14] = 1;
   out_1297355855737368671[15] = 0;
   out_1297355855737368671[16] = 0;
   out_1297355855737368671[17] = 0;
}
void h_30(double *state, double *unused, double *out_5890991448616497652) {
   out_5890991448616497652[0] = state[4];
}
void H_30(double *state, double *unused, double *out_5988338413250116864) {
   out_5988338413250116864[0] = 0;
   out_5988338413250116864[1] = 0;
   out_5988338413250116864[2] = 0;
   out_5988338413250116864[3] = 0;
   out_5988338413250116864[4] = 1;
   out_5988338413250116864[5] = 0;
   out_5988338413250116864[6] = 0;
   out_5988338413250116864[7] = 0;
   out_5988338413250116864[8] = 0;
}
void h_26(double *state, double *unused, double *out_7329845409257729017) {
   out_7329845409257729017[0] = state[7];
}
void H_26(double *state, double *unused, double *out_271497864131187987) {
   out_271497864131187987[0] = 0;
   out_271497864131187987[1] = 0;
   out_271497864131187987[2] = 0;
   out_271497864131187987[3] = 0;
   out_271497864131187987[4] = 0;
   out_271497864131187987[5] = 0;
   out_271497864131187987[6] = 0;
   out_271497864131187987[7] = 1;
   out_271497864131187987[8] = 0;
}
void h_27(double *state, double *unused, double *out_287900023342288453) {
   out_287900023342288453[0] = state[3];
}
void H_27(double *state, double *unused, double *out_8211932484434060081) {
   out_8211932484434060081[0] = 0;
   out_8211932484434060081[1] = 0;
   out_8211932484434060081[2] = 0;
   out_8211932484434060081[3] = 1;
   out_8211932484434060081[4] = 0;
   out_8211932484434060081[5] = 0;
   out_8211932484434060081[6] = 0;
   out_8211932484434060081[7] = 0;
   out_8211932484434060081[8] = 0;
}
void h_29(double *state, double *unused, double *out_12705961057782564) {
   out_12705961057782564[0] = state[1];
}
void H_29(double *state, double *unused, double *out_6498569757564509048) {
   out_6498569757564509048[0] = 0;
   out_6498569757564509048[1] = 1;
   out_6498569757564509048[2] = 0;
   out_6498569757564509048[3] = 0;
   out_6498569757564509048[4] = 0;
   out_6498569757564509048[5] = 0;
   out_6498569757564509048[6] = 0;
   out_6498569757564509048[7] = 0;
   out_6498569757564509048[8] = 0;
}
void h_28(double *state, double *unused, double *out_4334286006113819861) {
   out_4334286006113819861[0] = state[0];
}
void H_28(double *state, double *unused, double *out_1416170740494978474) {
   out_1416170740494978474[0] = 1;
   out_1416170740494978474[1] = 0;
   out_1416170740494978474[2] = 0;
   out_1416170740494978474[3] = 0;
   out_1416170740494978474[4] = 0;
   out_1416170740494978474[5] = 0;
   out_1416170740494978474[6] = 0;
   out_1416170740494978474[7] = 0;
   out_1416170740494978474[8] = 0;
}
void h_31(double *state, double *unused, double *out_2473691965817538343) {
   out_2473691965817538343[0] = state[8];
}
void H_31(double *state, double *unused, double *out_897705966364539463) {
   out_897705966364539463[0] = 0;
   out_897705966364539463[1] = 0;
   out_897705966364539463[2] = 0;
   out_897705966364539463[3] = 0;
   out_897705966364539463[4] = 0;
   out_897705966364539463[5] = 0;
   out_897705966364539463[6] = 0;
   out_897705966364539463[7] = 0;
   out_897705966364539463[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_5591252770855935724) {
  err_fun(nom_x, delta_x, out_5591252770855935724);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4117300928169881984) {
  inv_err_fun(nom_x, true_x, out_4117300928169881984);
}
void car_H_mod_fun(double *state, double *out_5783550393054446142) {
  H_mod_fun(state, out_5783550393054446142);
}
void car_f_fun(double *state, double dt, double *out_3463430665265427786) {
  f_fun(state,  dt, out_3463430665265427786);
}
void car_F_fun(double *state, double dt, double *out_7274748722386343746) {
  F_fun(state,  dt, out_7274748722386343746);
}
void car_h_25(double *state, double *unused, double *out_4674479974339004779) {
  h_25(state, unused, out_4674479974339004779);
}
void car_H_25(double *state, double *unused, double *out_3470005454742868237) {
  H_25(state, unused, out_3470005454742868237);
}
void car_h_24(double *state, double *unused, double *out_56151919158375531) {
  h_24(state, unused, out_56151919158375531);
}
void car_H_24(double *state, double *unused, double *out_1297355855737368671) {
  H_24(state, unused, out_1297355855737368671);
}
void car_h_30(double *state, double *unused, double *out_5890991448616497652) {
  h_30(state, unused, out_5890991448616497652);
}
void car_H_30(double *state, double *unused, double *out_5988338413250116864) {
  H_30(state, unused, out_5988338413250116864);
}
void car_h_26(double *state, double *unused, double *out_7329845409257729017) {
  h_26(state, unused, out_7329845409257729017);
}
void car_H_26(double *state, double *unused, double *out_271497864131187987) {
  H_26(state, unused, out_271497864131187987);
}
void car_h_27(double *state, double *unused, double *out_287900023342288453) {
  h_27(state, unused, out_287900023342288453);
}
void car_H_27(double *state, double *unused, double *out_8211932484434060081) {
  H_27(state, unused, out_8211932484434060081);
}
void car_h_29(double *state, double *unused, double *out_12705961057782564) {
  h_29(state, unused, out_12705961057782564);
}
void car_H_29(double *state, double *unused, double *out_6498569757564509048) {
  H_29(state, unused, out_6498569757564509048);
}
void car_h_28(double *state, double *unused, double *out_4334286006113819861) {
  h_28(state, unused, out_4334286006113819861);
}
void car_H_28(double *state, double *unused, double *out_1416170740494978474) {
  H_28(state, unused, out_1416170740494978474);
}
void car_h_31(double *state, double *unused, double *out_2473691965817538343) {
  h_31(state, unused, out_2473691965817538343);
}
void car_H_31(double *state, double *unused, double *out_897705966364539463) {
  H_31(state, unused, out_897705966364539463);
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
