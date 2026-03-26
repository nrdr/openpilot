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
void err_fun(double *nom_x, double *delta_x, double *out_7807076482345369651) {
   out_7807076482345369651[0] = delta_x[0] + nom_x[0];
   out_7807076482345369651[1] = delta_x[1] + nom_x[1];
   out_7807076482345369651[2] = delta_x[2] + nom_x[2];
   out_7807076482345369651[3] = delta_x[3] + nom_x[3];
   out_7807076482345369651[4] = delta_x[4] + nom_x[4];
   out_7807076482345369651[5] = delta_x[5] + nom_x[5];
   out_7807076482345369651[6] = delta_x[6] + nom_x[6];
   out_7807076482345369651[7] = delta_x[7] + nom_x[7];
   out_7807076482345369651[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1796239112381471799) {
   out_1796239112381471799[0] = -nom_x[0] + true_x[0];
   out_1796239112381471799[1] = -nom_x[1] + true_x[1];
   out_1796239112381471799[2] = -nom_x[2] + true_x[2];
   out_1796239112381471799[3] = -nom_x[3] + true_x[3];
   out_1796239112381471799[4] = -nom_x[4] + true_x[4];
   out_1796239112381471799[5] = -nom_x[5] + true_x[5];
   out_1796239112381471799[6] = -nom_x[6] + true_x[6];
   out_1796239112381471799[7] = -nom_x[7] + true_x[7];
   out_1796239112381471799[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_3897023893221819704) {
   out_3897023893221819704[0] = 1.0;
   out_3897023893221819704[1] = 0.0;
   out_3897023893221819704[2] = 0.0;
   out_3897023893221819704[3] = 0.0;
   out_3897023893221819704[4] = 0.0;
   out_3897023893221819704[5] = 0.0;
   out_3897023893221819704[6] = 0.0;
   out_3897023893221819704[7] = 0.0;
   out_3897023893221819704[8] = 0.0;
   out_3897023893221819704[9] = 0.0;
   out_3897023893221819704[10] = 1.0;
   out_3897023893221819704[11] = 0.0;
   out_3897023893221819704[12] = 0.0;
   out_3897023893221819704[13] = 0.0;
   out_3897023893221819704[14] = 0.0;
   out_3897023893221819704[15] = 0.0;
   out_3897023893221819704[16] = 0.0;
   out_3897023893221819704[17] = 0.0;
   out_3897023893221819704[18] = 0.0;
   out_3897023893221819704[19] = 0.0;
   out_3897023893221819704[20] = 1.0;
   out_3897023893221819704[21] = 0.0;
   out_3897023893221819704[22] = 0.0;
   out_3897023893221819704[23] = 0.0;
   out_3897023893221819704[24] = 0.0;
   out_3897023893221819704[25] = 0.0;
   out_3897023893221819704[26] = 0.0;
   out_3897023893221819704[27] = 0.0;
   out_3897023893221819704[28] = 0.0;
   out_3897023893221819704[29] = 0.0;
   out_3897023893221819704[30] = 1.0;
   out_3897023893221819704[31] = 0.0;
   out_3897023893221819704[32] = 0.0;
   out_3897023893221819704[33] = 0.0;
   out_3897023893221819704[34] = 0.0;
   out_3897023893221819704[35] = 0.0;
   out_3897023893221819704[36] = 0.0;
   out_3897023893221819704[37] = 0.0;
   out_3897023893221819704[38] = 0.0;
   out_3897023893221819704[39] = 0.0;
   out_3897023893221819704[40] = 1.0;
   out_3897023893221819704[41] = 0.0;
   out_3897023893221819704[42] = 0.0;
   out_3897023893221819704[43] = 0.0;
   out_3897023893221819704[44] = 0.0;
   out_3897023893221819704[45] = 0.0;
   out_3897023893221819704[46] = 0.0;
   out_3897023893221819704[47] = 0.0;
   out_3897023893221819704[48] = 0.0;
   out_3897023893221819704[49] = 0.0;
   out_3897023893221819704[50] = 1.0;
   out_3897023893221819704[51] = 0.0;
   out_3897023893221819704[52] = 0.0;
   out_3897023893221819704[53] = 0.0;
   out_3897023893221819704[54] = 0.0;
   out_3897023893221819704[55] = 0.0;
   out_3897023893221819704[56] = 0.0;
   out_3897023893221819704[57] = 0.0;
   out_3897023893221819704[58] = 0.0;
   out_3897023893221819704[59] = 0.0;
   out_3897023893221819704[60] = 1.0;
   out_3897023893221819704[61] = 0.0;
   out_3897023893221819704[62] = 0.0;
   out_3897023893221819704[63] = 0.0;
   out_3897023893221819704[64] = 0.0;
   out_3897023893221819704[65] = 0.0;
   out_3897023893221819704[66] = 0.0;
   out_3897023893221819704[67] = 0.0;
   out_3897023893221819704[68] = 0.0;
   out_3897023893221819704[69] = 0.0;
   out_3897023893221819704[70] = 1.0;
   out_3897023893221819704[71] = 0.0;
   out_3897023893221819704[72] = 0.0;
   out_3897023893221819704[73] = 0.0;
   out_3897023893221819704[74] = 0.0;
   out_3897023893221819704[75] = 0.0;
   out_3897023893221819704[76] = 0.0;
   out_3897023893221819704[77] = 0.0;
   out_3897023893221819704[78] = 0.0;
   out_3897023893221819704[79] = 0.0;
   out_3897023893221819704[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_2582961016816185380) {
   out_2582961016816185380[0] = state[0];
   out_2582961016816185380[1] = state[1];
   out_2582961016816185380[2] = state[2];
   out_2582961016816185380[3] = state[3];
   out_2582961016816185380[4] = state[4];
   out_2582961016816185380[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_2582961016816185380[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_2582961016816185380[7] = state[7];
   out_2582961016816185380[8] = state[8];
}
void F_fun(double *state, double dt, double *out_7148735030780216289) {
   out_7148735030780216289[0] = 1;
   out_7148735030780216289[1] = 0;
   out_7148735030780216289[2] = 0;
   out_7148735030780216289[3] = 0;
   out_7148735030780216289[4] = 0;
   out_7148735030780216289[5] = 0;
   out_7148735030780216289[6] = 0;
   out_7148735030780216289[7] = 0;
   out_7148735030780216289[8] = 0;
   out_7148735030780216289[9] = 0;
   out_7148735030780216289[10] = 1;
   out_7148735030780216289[11] = 0;
   out_7148735030780216289[12] = 0;
   out_7148735030780216289[13] = 0;
   out_7148735030780216289[14] = 0;
   out_7148735030780216289[15] = 0;
   out_7148735030780216289[16] = 0;
   out_7148735030780216289[17] = 0;
   out_7148735030780216289[18] = 0;
   out_7148735030780216289[19] = 0;
   out_7148735030780216289[20] = 1;
   out_7148735030780216289[21] = 0;
   out_7148735030780216289[22] = 0;
   out_7148735030780216289[23] = 0;
   out_7148735030780216289[24] = 0;
   out_7148735030780216289[25] = 0;
   out_7148735030780216289[26] = 0;
   out_7148735030780216289[27] = 0;
   out_7148735030780216289[28] = 0;
   out_7148735030780216289[29] = 0;
   out_7148735030780216289[30] = 1;
   out_7148735030780216289[31] = 0;
   out_7148735030780216289[32] = 0;
   out_7148735030780216289[33] = 0;
   out_7148735030780216289[34] = 0;
   out_7148735030780216289[35] = 0;
   out_7148735030780216289[36] = 0;
   out_7148735030780216289[37] = 0;
   out_7148735030780216289[38] = 0;
   out_7148735030780216289[39] = 0;
   out_7148735030780216289[40] = 1;
   out_7148735030780216289[41] = 0;
   out_7148735030780216289[42] = 0;
   out_7148735030780216289[43] = 0;
   out_7148735030780216289[44] = 0;
   out_7148735030780216289[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_7148735030780216289[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_7148735030780216289[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7148735030780216289[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7148735030780216289[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_7148735030780216289[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_7148735030780216289[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_7148735030780216289[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_7148735030780216289[53] = -9.8100000000000005*dt;
   out_7148735030780216289[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_7148735030780216289[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_7148735030780216289[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7148735030780216289[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7148735030780216289[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_7148735030780216289[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_7148735030780216289[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_7148735030780216289[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7148735030780216289[62] = 0;
   out_7148735030780216289[63] = 0;
   out_7148735030780216289[64] = 0;
   out_7148735030780216289[65] = 0;
   out_7148735030780216289[66] = 0;
   out_7148735030780216289[67] = 0;
   out_7148735030780216289[68] = 0;
   out_7148735030780216289[69] = 0;
   out_7148735030780216289[70] = 1;
   out_7148735030780216289[71] = 0;
   out_7148735030780216289[72] = 0;
   out_7148735030780216289[73] = 0;
   out_7148735030780216289[74] = 0;
   out_7148735030780216289[75] = 0;
   out_7148735030780216289[76] = 0;
   out_7148735030780216289[77] = 0;
   out_7148735030780216289[78] = 0;
   out_7148735030780216289[79] = 0;
   out_7148735030780216289[80] = 1;
}
void h_25(double *state, double *unused, double *out_1352881618571586937) {
   out_1352881618571586937[0] = state[6];
}
void H_25(double *state, double *unused, double *out_5296164332690417533) {
   out_5296164332690417533[0] = 0;
   out_5296164332690417533[1] = 0;
   out_5296164332690417533[2] = 0;
   out_5296164332690417533[3] = 0;
   out_5296164332690417533[4] = 0;
   out_5296164332690417533[5] = 0;
   out_5296164332690417533[6] = 1;
   out_5296164332690417533[7] = 0;
   out_5296164332690417533[8] = 0;
}
void h_24(double *state, double *unused, double *out_535289742976937669) {
   out_535289742976937669[0] = state[4];
   out_535289742976937669[1] = state[5];
}
void H_24(double *state, double *unused, double *out_1358041125417768224) {
   out_1358041125417768224[0] = 0;
   out_1358041125417768224[1] = 0;
   out_1358041125417768224[2] = 0;
   out_1358041125417768224[3] = 0;
   out_1358041125417768224[4] = 1;
   out_1358041125417768224[5] = 0;
   out_1358041125417768224[6] = 0;
   out_1358041125417768224[7] = 0;
   out_1358041125417768224[8] = 0;
   out_1358041125417768224[9] = 0;
   out_1358041125417768224[10] = 0;
   out_1358041125417768224[11] = 0;
   out_1358041125417768224[12] = 0;
   out_1358041125417768224[13] = 0;
   out_1358041125417768224[14] = 1;
   out_1358041125417768224[15] = 0;
   out_1358041125417768224[16] = 0;
   out_1358041125417768224[17] = 0;
}
void h_30(double *state, double *unused, double *out_5417953607778763999) {
   out_5417953607778763999[0] = state[4];
}
void H_30(double *state, double *unused, double *out_8622883410891525885) {
   out_8622883410891525885[0] = 0;
   out_8622883410891525885[1] = 0;
   out_8622883410891525885[2] = 0;
   out_8622883410891525885[3] = 0;
   out_8622883410891525885[4] = 1;
   out_8622883410891525885[5] = 0;
   out_8622883410891525885[6] = 0;
   out_8622883410891525885[7] = 0;
   out_8622883410891525885[8] = 0;
}
void h_26(double *state, double *unused, double *out_4250209806702622262) {
   out_4250209806702622262[0] = state[7];
}
void H_26(double *state, double *unused, double *out_9037667651564473757) {
   out_9037667651564473757[0] = 0;
   out_9037667651564473757[1] = 0;
   out_9037667651564473757[2] = 0;
   out_9037667651564473757[3] = 0;
   out_9037667651564473757[4] = 0;
   out_9037667651564473757[5] = 0;
   out_9037667651564473757[6] = 0;
   out_9037667651564473757[7] = 1;
   out_9037667651564473757[8] = 0;
}
void h_27(double *state, double *unused, double *out_337566216164094023) {
   out_337566216164094023[0] = state[3];
}
void H_27(double *state, double *unused, double *out_6448120099091100974) {
   out_6448120099091100974[0] = 0;
   out_6448120099091100974[1] = 0;
   out_6448120099091100974[2] = 0;
   out_6448120099091100974[3] = 1;
   out_6448120099091100974[4] = 0;
   out_6448120099091100974[5] = 0;
   out_6448120099091100974[6] = 0;
   out_6448120099091100974[7] = 0;
   out_6448120099091100974[8] = 0;
}
void h_29(double *state, double *unused, double *out_8230505711048617382) {
   out_8230505711048617382[0] = state[1];
}
void H_29(double *state, double *unused, double *out_9133114755205918069) {
   out_9133114755205918069[0] = 0;
   out_9133114755205918069[1] = 1;
   out_9133114755205918069[2] = 0;
   out_9133114755205918069[3] = 0;
   out_9133114755205918069[4] = 0;
   out_9133114755205918069[5] = 0;
   out_9133114755205918069[6] = 0;
   out_9133114755205918069[7] = 0;
   out_9133114755205918069[8] = 0;
}
void h_28(double *state, double *unused, double *out_4664107051496751622) {
   out_4664107051496751622[0] = state[0];
}
void H_28(double *state, double *unused, double *out_7349999046938307296) {
   out_7349999046938307296[0] = 1;
   out_7349999046938307296[1] = 0;
   out_7349999046938307296[2] = 0;
   out_7349999046938307296[3] = 0;
   out_7349999046938307296[4] = 0;
   out_7349999046938307296[5] = 0;
   out_7349999046938307296[6] = 0;
   out_7349999046938307296[7] = 0;
   out_7349999046938307296[8] = 0;
}
void h_31(double *state, double *unused, double *out_2803513011200470104) {
   out_2803513011200470104[0] = state[8];
}
void H_31(double *state, double *unused, double *out_8782868319911726383) {
   out_8782868319911726383[0] = 0;
   out_8782868319911726383[1] = 0;
   out_8782868319911726383[2] = 0;
   out_8782868319911726383[3] = 0;
   out_8782868319911726383[4] = 0;
   out_8782868319911726383[5] = 0;
   out_8782868319911726383[6] = 0;
   out_8782868319911726383[7] = 0;
   out_8782868319911726383[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_7807076482345369651) {
  err_fun(nom_x, delta_x, out_7807076482345369651);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1796239112381471799) {
  inv_err_fun(nom_x, true_x, out_1796239112381471799);
}
void car_H_mod_fun(double *state, double *out_3897023893221819704) {
  H_mod_fun(state, out_3897023893221819704);
}
void car_f_fun(double *state, double dt, double *out_2582961016816185380) {
  f_fun(state,  dt, out_2582961016816185380);
}
void car_F_fun(double *state, double dt, double *out_7148735030780216289) {
  F_fun(state,  dt, out_7148735030780216289);
}
void car_h_25(double *state, double *unused, double *out_1352881618571586937) {
  h_25(state, unused, out_1352881618571586937);
}
void car_H_25(double *state, double *unused, double *out_5296164332690417533) {
  H_25(state, unused, out_5296164332690417533);
}
void car_h_24(double *state, double *unused, double *out_535289742976937669) {
  h_24(state, unused, out_535289742976937669);
}
void car_H_24(double *state, double *unused, double *out_1358041125417768224) {
  H_24(state, unused, out_1358041125417768224);
}
void car_h_30(double *state, double *unused, double *out_5417953607778763999) {
  h_30(state, unused, out_5417953607778763999);
}
void car_H_30(double *state, double *unused, double *out_8622883410891525885) {
  H_30(state, unused, out_8622883410891525885);
}
void car_h_26(double *state, double *unused, double *out_4250209806702622262) {
  h_26(state, unused, out_4250209806702622262);
}
void car_H_26(double *state, double *unused, double *out_9037667651564473757) {
  H_26(state, unused, out_9037667651564473757);
}
void car_h_27(double *state, double *unused, double *out_337566216164094023) {
  h_27(state, unused, out_337566216164094023);
}
void car_H_27(double *state, double *unused, double *out_6448120099091100974) {
  H_27(state, unused, out_6448120099091100974);
}
void car_h_29(double *state, double *unused, double *out_8230505711048617382) {
  h_29(state, unused, out_8230505711048617382);
}
void car_H_29(double *state, double *unused, double *out_9133114755205918069) {
  H_29(state, unused, out_9133114755205918069);
}
void car_h_28(double *state, double *unused, double *out_4664107051496751622) {
  h_28(state, unused, out_4664107051496751622);
}
void car_H_28(double *state, double *unused, double *out_7349999046938307296) {
  H_28(state, unused, out_7349999046938307296);
}
void car_h_31(double *state, double *unused, double *out_2803513011200470104) {
  h_31(state, unused, out_2803513011200470104);
}
void car_H_31(double *state, double *unused, double *out_8782868319911726383) {
  H_31(state, unused, out_8782868319911726383);
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
