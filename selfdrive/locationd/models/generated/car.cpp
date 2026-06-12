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
void err_fun(double *nom_x, double *delta_x, double *out_8483021428746320765) {
   out_8483021428746320765[0] = delta_x[0] + nom_x[0];
   out_8483021428746320765[1] = delta_x[1] + nom_x[1];
   out_8483021428746320765[2] = delta_x[2] + nom_x[2];
   out_8483021428746320765[3] = delta_x[3] + nom_x[3];
   out_8483021428746320765[4] = delta_x[4] + nom_x[4];
   out_8483021428746320765[5] = delta_x[5] + nom_x[5];
   out_8483021428746320765[6] = delta_x[6] + nom_x[6];
   out_8483021428746320765[7] = delta_x[7] + nom_x[7];
   out_8483021428746320765[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7116095168868427330) {
   out_7116095168868427330[0] = -nom_x[0] + true_x[0];
   out_7116095168868427330[1] = -nom_x[1] + true_x[1];
   out_7116095168868427330[2] = -nom_x[2] + true_x[2];
   out_7116095168868427330[3] = -nom_x[3] + true_x[3];
   out_7116095168868427330[4] = -nom_x[4] + true_x[4];
   out_7116095168868427330[5] = -nom_x[5] + true_x[5];
   out_7116095168868427330[6] = -nom_x[6] + true_x[6];
   out_7116095168868427330[7] = -nom_x[7] + true_x[7];
   out_7116095168868427330[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_7967624822341296814) {
   out_7967624822341296814[0] = 1.0;
   out_7967624822341296814[1] = 0.0;
   out_7967624822341296814[2] = 0.0;
   out_7967624822341296814[3] = 0.0;
   out_7967624822341296814[4] = 0.0;
   out_7967624822341296814[5] = 0.0;
   out_7967624822341296814[6] = 0.0;
   out_7967624822341296814[7] = 0.0;
   out_7967624822341296814[8] = 0.0;
   out_7967624822341296814[9] = 0.0;
   out_7967624822341296814[10] = 1.0;
   out_7967624822341296814[11] = 0.0;
   out_7967624822341296814[12] = 0.0;
   out_7967624822341296814[13] = 0.0;
   out_7967624822341296814[14] = 0.0;
   out_7967624822341296814[15] = 0.0;
   out_7967624822341296814[16] = 0.0;
   out_7967624822341296814[17] = 0.0;
   out_7967624822341296814[18] = 0.0;
   out_7967624822341296814[19] = 0.0;
   out_7967624822341296814[20] = 1.0;
   out_7967624822341296814[21] = 0.0;
   out_7967624822341296814[22] = 0.0;
   out_7967624822341296814[23] = 0.0;
   out_7967624822341296814[24] = 0.0;
   out_7967624822341296814[25] = 0.0;
   out_7967624822341296814[26] = 0.0;
   out_7967624822341296814[27] = 0.0;
   out_7967624822341296814[28] = 0.0;
   out_7967624822341296814[29] = 0.0;
   out_7967624822341296814[30] = 1.0;
   out_7967624822341296814[31] = 0.0;
   out_7967624822341296814[32] = 0.0;
   out_7967624822341296814[33] = 0.0;
   out_7967624822341296814[34] = 0.0;
   out_7967624822341296814[35] = 0.0;
   out_7967624822341296814[36] = 0.0;
   out_7967624822341296814[37] = 0.0;
   out_7967624822341296814[38] = 0.0;
   out_7967624822341296814[39] = 0.0;
   out_7967624822341296814[40] = 1.0;
   out_7967624822341296814[41] = 0.0;
   out_7967624822341296814[42] = 0.0;
   out_7967624822341296814[43] = 0.0;
   out_7967624822341296814[44] = 0.0;
   out_7967624822341296814[45] = 0.0;
   out_7967624822341296814[46] = 0.0;
   out_7967624822341296814[47] = 0.0;
   out_7967624822341296814[48] = 0.0;
   out_7967624822341296814[49] = 0.0;
   out_7967624822341296814[50] = 1.0;
   out_7967624822341296814[51] = 0.0;
   out_7967624822341296814[52] = 0.0;
   out_7967624822341296814[53] = 0.0;
   out_7967624822341296814[54] = 0.0;
   out_7967624822341296814[55] = 0.0;
   out_7967624822341296814[56] = 0.0;
   out_7967624822341296814[57] = 0.0;
   out_7967624822341296814[58] = 0.0;
   out_7967624822341296814[59] = 0.0;
   out_7967624822341296814[60] = 1.0;
   out_7967624822341296814[61] = 0.0;
   out_7967624822341296814[62] = 0.0;
   out_7967624822341296814[63] = 0.0;
   out_7967624822341296814[64] = 0.0;
   out_7967624822341296814[65] = 0.0;
   out_7967624822341296814[66] = 0.0;
   out_7967624822341296814[67] = 0.0;
   out_7967624822341296814[68] = 0.0;
   out_7967624822341296814[69] = 0.0;
   out_7967624822341296814[70] = 1.0;
   out_7967624822341296814[71] = 0.0;
   out_7967624822341296814[72] = 0.0;
   out_7967624822341296814[73] = 0.0;
   out_7967624822341296814[74] = 0.0;
   out_7967624822341296814[75] = 0.0;
   out_7967624822341296814[76] = 0.0;
   out_7967624822341296814[77] = 0.0;
   out_7967624822341296814[78] = 0.0;
   out_7967624822341296814[79] = 0.0;
   out_7967624822341296814[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_7719046304768792394) {
   out_7719046304768792394[0] = state[0];
   out_7719046304768792394[1] = state[1];
   out_7719046304768792394[2] = state[2];
   out_7719046304768792394[3] = state[3];
   out_7719046304768792394[4] = state[4];
   out_7719046304768792394[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_7719046304768792394[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_7719046304768792394[7] = state[7];
   out_7719046304768792394[8] = state[8];
}
void F_fun(double *state, double dt, double *out_93541883228193728) {
   out_93541883228193728[0] = 1;
   out_93541883228193728[1] = 0;
   out_93541883228193728[2] = 0;
   out_93541883228193728[3] = 0;
   out_93541883228193728[4] = 0;
   out_93541883228193728[5] = 0;
   out_93541883228193728[6] = 0;
   out_93541883228193728[7] = 0;
   out_93541883228193728[8] = 0;
   out_93541883228193728[9] = 0;
   out_93541883228193728[10] = 1;
   out_93541883228193728[11] = 0;
   out_93541883228193728[12] = 0;
   out_93541883228193728[13] = 0;
   out_93541883228193728[14] = 0;
   out_93541883228193728[15] = 0;
   out_93541883228193728[16] = 0;
   out_93541883228193728[17] = 0;
   out_93541883228193728[18] = 0;
   out_93541883228193728[19] = 0;
   out_93541883228193728[20] = 1;
   out_93541883228193728[21] = 0;
   out_93541883228193728[22] = 0;
   out_93541883228193728[23] = 0;
   out_93541883228193728[24] = 0;
   out_93541883228193728[25] = 0;
   out_93541883228193728[26] = 0;
   out_93541883228193728[27] = 0;
   out_93541883228193728[28] = 0;
   out_93541883228193728[29] = 0;
   out_93541883228193728[30] = 1;
   out_93541883228193728[31] = 0;
   out_93541883228193728[32] = 0;
   out_93541883228193728[33] = 0;
   out_93541883228193728[34] = 0;
   out_93541883228193728[35] = 0;
   out_93541883228193728[36] = 0;
   out_93541883228193728[37] = 0;
   out_93541883228193728[38] = 0;
   out_93541883228193728[39] = 0;
   out_93541883228193728[40] = 1;
   out_93541883228193728[41] = 0;
   out_93541883228193728[42] = 0;
   out_93541883228193728[43] = 0;
   out_93541883228193728[44] = 0;
   out_93541883228193728[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_93541883228193728[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_93541883228193728[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_93541883228193728[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_93541883228193728[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_93541883228193728[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_93541883228193728[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_93541883228193728[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_93541883228193728[53] = -9.8100000000000005*dt;
   out_93541883228193728[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_93541883228193728[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_93541883228193728[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_93541883228193728[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_93541883228193728[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_93541883228193728[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_93541883228193728[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_93541883228193728[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_93541883228193728[62] = 0;
   out_93541883228193728[63] = 0;
   out_93541883228193728[64] = 0;
   out_93541883228193728[65] = 0;
   out_93541883228193728[66] = 0;
   out_93541883228193728[67] = 0;
   out_93541883228193728[68] = 0;
   out_93541883228193728[69] = 0;
   out_93541883228193728[70] = 1;
   out_93541883228193728[71] = 0;
   out_93541883228193728[72] = 0;
   out_93541883228193728[73] = 0;
   out_93541883228193728[74] = 0;
   out_93541883228193728[75] = 0;
   out_93541883228193728[76] = 0;
   out_93541883228193728[77] = 0;
   out_93541883228193728[78] = 0;
   out_93541883228193728[79] = 0;
   out_93541883228193728[80] = 1;
}
void h_25(double *state, double *unused, double *out_6239424513673374840) {
   out_6239424513673374840[0] = state[6];
}
void H_25(double *state, double *unused, double *out_6956138601378763125) {
   out_6956138601378763125[0] = 0;
   out_6956138601378763125[1] = 0;
   out_6956138601378763125[2] = 0;
   out_6956138601378763125[3] = 0;
   out_6956138601378763125[4] = 0;
   out_6956138601378763125[5] = 0;
   out_6956138601378763125[6] = 1;
   out_6956138601378763125[7] = 0;
   out_6956138601378763125[8] = 0;
}
void h_24(double *state, double *unused, double *out_3510022705588126587) {
   out_3510022705588126587[0] = state[4];
   out_3510022705588126587[1] = state[5];
}
void H_24(double *state, double *unused, double *out_6744096145364279457) {
   out_6744096145364279457[0] = 0;
   out_6744096145364279457[1] = 0;
   out_6744096145364279457[2] = 0;
   out_6744096145364279457[3] = 0;
   out_6744096145364279457[4] = 1;
   out_6744096145364279457[5] = 0;
   out_6744096145364279457[6] = 0;
   out_6744096145364279457[7] = 0;
   out_6744096145364279457[8] = 0;
   out_6744096145364279457[9] = 0;
   out_6744096145364279457[10] = 0;
   out_6744096145364279457[11] = 0;
   out_6744096145364279457[12] = 0;
   out_6744096145364279457[13] = 0;
   out_6744096145364279457[14] = 1;
   out_6744096145364279457[15] = 0;
   out_6744096145364279457[16] = 0;
   out_6744096145364279457[17] = 0;
}
void h_30(double *state, double *unused, double *out_3999822813953269926) {
   out_3999822813953269926[0] = state[4];
}
void H_30(double *state, double *unused, double *out_39448259887146370) {
   out_39448259887146370[0] = 0;
   out_39448259887146370[1] = 0;
   out_39448259887146370[2] = 0;
   out_39448259887146370[3] = 0;
   out_39448259887146370[4] = 1;
   out_39448259887146370[5] = 0;
   out_39448259887146370[6] = 0;
   out_39448259887146370[7] = 0;
   out_39448259887146370[8] = 0;
}
void h_26(double *state, double *unused, double *out_6379994186587488275) {
   out_6379994186587488275[0] = state[7];
}
void H_26(double *state, double *unused, double *out_7749102153456732267) {
   out_7749102153456732267[0] = 0;
   out_7749102153456732267[1] = 0;
   out_7749102153456732267[2] = 0;
   out_7749102153456732267[3] = 0;
   out_7749102153456732267[4] = 0;
   out_7749102153456732267[5] = 0;
   out_7749102153456732267[6] = 0;
   out_7749102153456732267[7] = 1;
   out_7749102153456732267[8] = 0;
}
void h_27(double *state, double *unused, double *out_8843829834482072491) {
   out_8843829834482072491[0] = state[3];
}
void H_27(double *state, double *unused, double *out_2214211571687571281) {
   out_2214211571687571281[0] = 0;
   out_2214211571687571281[1] = 0;
   out_2214211571687571281[2] = 0;
   out_2214211571687571281[3] = 1;
   out_2214211571687571281[4] = 0;
   out_2214211571687571281[5] = 0;
   out_2214211571687571281[6] = 0;
   out_2214211571687571281[7] = 0;
   out_2214211571687571281[8] = 0;
}
void h_29(double *state, double *unused, double *out_4982146358053570839) {
   out_4982146358053570839[0] = state[1];
}
void H_29(double *state, double *unused, double *out_470783084427245814) {
   out_470783084427245814[0] = 0;
   out_470783084427245814[1] = 1;
   out_470783084427245814[2] = 0;
   out_470783084427245814[3] = 0;
   out_470783084427245814[4] = 0;
   out_470783084427245814[5] = 0;
   out_470783084427245814[6] = 0;
   out_470783084427245814[7] = 0;
   out_470783084427245814[8] = 0;
}
void h_28(double *state, double *unused, double *out_255667152677231083) {
   out_255667152677231083[0] = state[0];
}
void H_28(double *state, double *unused, double *out_9009973315626652888) {
   out_9009973315626652888[0] = 1;
   out_9009973315626652888[1] = 0;
   out_9009973315626652888[2] = 0;
   out_9009973315626652888[3] = 0;
   out_9009973315626652888[4] = 0;
   out_9009973315626652888[5] = 0;
   out_9009973315626652888[6] = 0;
   out_9009973315626652888[7] = 0;
   out_9009973315626652888[8] = 0;
}
void h_31(double *state, double *unused, double *out_6082237845322245695) {
   out_6082237845322245695[0] = state[8];
}
void H_31(double *state, double *unused, double *out_6925492639501802697) {
   out_6925492639501802697[0] = 0;
   out_6925492639501802697[1] = 0;
   out_6925492639501802697[2] = 0;
   out_6925492639501802697[3] = 0;
   out_6925492639501802697[4] = 0;
   out_6925492639501802697[5] = 0;
   out_6925492639501802697[6] = 0;
   out_6925492639501802697[7] = 0;
   out_6925492639501802697[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_8483021428746320765) {
  err_fun(nom_x, delta_x, out_8483021428746320765);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7116095168868427330) {
  inv_err_fun(nom_x, true_x, out_7116095168868427330);
}
void car_H_mod_fun(double *state, double *out_7967624822341296814) {
  H_mod_fun(state, out_7967624822341296814);
}
void car_f_fun(double *state, double dt, double *out_7719046304768792394) {
  f_fun(state,  dt, out_7719046304768792394);
}
void car_F_fun(double *state, double dt, double *out_93541883228193728) {
  F_fun(state,  dt, out_93541883228193728);
}
void car_h_25(double *state, double *unused, double *out_6239424513673374840) {
  h_25(state, unused, out_6239424513673374840);
}
void car_H_25(double *state, double *unused, double *out_6956138601378763125) {
  H_25(state, unused, out_6956138601378763125);
}
void car_h_24(double *state, double *unused, double *out_3510022705588126587) {
  h_24(state, unused, out_3510022705588126587);
}
void car_H_24(double *state, double *unused, double *out_6744096145364279457) {
  H_24(state, unused, out_6744096145364279457);
}
void car_h_30(double *state, double *unused, double *out_3999822813953269926) {
  h_30(state, unused, out_3999822813953269926);
}
void car_H_30(double *state, double *unused, double *out_39448259887146370) {
  H_30(state, unused, out_39448259887146370);
}
void car_h_26(double *state, double *unused, double *out_6379994186587488275) {
  h_26(state, unused, out_6379994186587488275);
}
void car_H_26(double *state, double *unused, double *out_7749102153456732267) {
  H_26(state, unused, out_7749102153456732267);
}
void car_h_27(double *state, double *unused, double *out_8843829834482072491) {
  h_27(state, unused, out_8843829834482072491);
}
void car_H_27(double *state, double *unused, double *out_2214211571687571281) {
  H_27(state, unused, out_2214211571687571281);
}
void car_h_29(double *state, double *unused, double *out_4982146358053570839) {
  h_29(state, unused, out_4982146358053570839);
}
void car_H_29(double *state, double *unused, double *out_470783084427245814) {
  H_29(state, unused, out_470783084427245814);
}
void car_h_28(double *state, double *unused, double *out_255667152677231083) {
  h_28(state, unused, out_255667152677231083);
}
void car_H_28(double *state, double *unused, double *out_9009973315626652888) {
  H_28(state, unused, out_9009973315626652888);
}
void car_h_31(double *state, double *unused, double *out_6082237845322245695) {
  h_31(state, unused, out_6082237845322245695);
}
void car_H_31(double *state, double *unused, double *out_6925492639501802697) {
  H_31(state, unused, out_6925492639501802697);
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
