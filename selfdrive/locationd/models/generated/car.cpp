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
void err_fun(double *nom_x, double *delta_x, double *out_6787215922179600543) {
   out_6787215922179600543[0] = delta_x[0] + nom_x[0];
   out_6787215922179600543[1] = delta_x[1] + nom_x[1];
   out_6787215922179600543[2] = delta_x[2] + nom_x[2];
   out_6787215922179600543[3] = delta_x[3] + nom_x[3];
   out_6787215922179600543[4] = delta_x[4] + nom_x[4];
   out_6787215922179600543[5] = delta_x[5] + nom_x[5];
   out_6787215922179600543[6] = delta_x[6] + nom_x[6];
   out_6787215922179600543[7] = delta_x[7] + nom_x[7];
   out_6787215922179600543[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6360714375878173456) {
   out_6360714375878173456[0] = -nom_x[0] + true_x[0];
   out_6360714375878173456[1] = -nom_x[1] + true_x[1];
   out_6360714375878173456[2] = -nom_x[2] + true_x[2];
   out_6360714375878173456[3] = -nom_x[3] + true_x[3];
   out_6360714375878173456[4] = -nom_x[4] + true_x[4];
   out_6360714375878173456[5] = -nom_x[5] + true_x[5];
   out_6360714375878173456[6] = -nom_x[6] + true_x[6];
   out_6360714375878173456[7] = -nom_x[7] + true_x[7];
   out_6360714375878173456[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_8179962768019912306) {
   out_8179962768019912306[0] = 1.0;
   out_8179962768019912306[1] = 0.0;
   out_8179962768019912306[2] = 0.0;
   out_8179962768019912306[3] = 0.0;
   out_8179962768019912306[4] = 0.0;
   out_8179962768019912306[5] = 0.0;
   out_8179962768019912306[6] = 0.0;
   out_8179962768019912306[7] = 0.0;
   out_8179962768019912306[8] = 0.0;
   out_8179962768019912306[9] = 0.0;
   out_8179962768019912306[10] = 1.0;
   out_8179962768019912306[11] = 0.0;
   out_8179962768019912306[12] = 0.0;
   out_8179962768019912306[13] = 0.0;
   out_8179962768019912306[14] = 0.0;
   out_8179962768019912306[15] = 0.0;
   out_8179962768019912306[16] = 0.0;
   out_8179962768019912306[17] = 0.0;
   out_8179962768019912306[18] = 0.0;
   out_8179962768019912306[19] = 0.0;
   out_8179962768019912306[20] = 1.0;
   out_8179962768019912306[21] = 0.0;
   out_8179962768019912306[22] = 0.0;
   out_8179962768019912306[23] = 0.0;
   out_8179962768019912306[24] = 0.0;
   out_8179962768019912306[25] = 0.0;
   out_8179962768019912306[26] = 0.0;
   out_8179962768019912306[27] = 0.0;
   out_8179962768019912306[28] = 0.0;
   out_8179962768019912306[29] = 0.0;
   out_8179962768019912306[30] = 1.0;
   out_8179962768019912306[31] = 0.0;
   out_8179962768019912306[32] = 0.0;
   out_8179962768019912306[33] = 0.0;
   out_8179962768019912306[34] = 0.0;
   out_8179962768019912306[35] = 0.0;
   out_8179962768019912306[36] = 0.0;
   out_8179962768019912306[37] = 0.0;
   out_8179962768019912306[38] = 0.0;
   out_8179962768019912306[39] = 0.0;
   out_8179962768019912306[40] = 1.0;
   out_8179962768019912306[41] = 0.0;
   out_8179962768019912306[42] = 0.0;
   out_8179962768019912306[43] = 0.0;
   out_8179962768019912306[44] = 0.0;
   out_8179962768019912306[45] = 0.0;
   out_8179962768019912306[46] = 0.0;
   out_8179962768019912306[47] = 0.0;
   out_8179962768019912306[48] = 0.0;
   out_8179962768019912306[49] = 0.0;
   out_8179962768019912306[50] = 1.0;
   out_8179962768019912306[51] = 0.0;
   out_8179962768019912306[52] = 0.0;
   out_8179962768019912306[53] = 0.0;
   out_8179962768019912306[54] = 0.0;
   out_8179962768019912306[55] = 0.0;
   out_8179962768019912306[56] = 0.0;
   out_8179962768019912306[57] = 0.0;
   out_8179962768019912306[58] = 0.0;
   out_8179962768019912306[59] = 0.0;
   out_8179962768019912306[60] = 1.0;
   out_8179962768019912306[61] = 0.0;
   out_8179962768019912306[62] = 0.0;
   out_8179962768019912306[63] = 0.0;
   out_8179962768019912306[64] = 0.0;
   out_8179962768019912306[65] = 0.0;
   out_8179962768019912306[66] = 0.0;
   out_8179962768019912306[67] = 0.0;
   out_8179962768019912306[68] = 0.0;
   out_8179962768019912306[69] = 0.0;
   out_8179962768019912306[70] = 1.0;
   out_8179962768019912306[71] = 0.0;
   out_8179962768019912306[72] = 0.0;
   out_8179962768019912306[73] = 0.0;
   out_8179962768019912306[74] = 0.0;
   out_8179962768019912306[75] = 0.0;
   out_8179962768019912306[76] = 0.0;
   out_8179962768019912306[77] = 0.0;
   out_8179962768019912306[78] = 0.0;
   out_8179962768019912306[79] = 0.0;
   out_8179962768019912306[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_519966246064059535) {
   out_519966246064059535[0] = state[0];
   out_519966246064059535[1] = state[1];
   out_519966246064059535[2] = state[2];
   out_519966246064059535[3] = state[3];
   out_519966246064059535[4] = state[4];
   out_519966246064059535[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_519966246064059535[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_519966246064059535[7] = state[7];
   out_519966246064059535[8] = state[8];
}
void F_fun(double *state, double dt, double *out_3124210133510146644) {
   out_3124210133510146644[0] = 1;
   out_3124210133510146644[1] = 0;
   out_3124210133510146644[2] = 0;
   out_3124210133510146644[3] = 0;
   out_3124210133510146644[4] = 0;
   out_3124210133510146644[5] = 0;
   out_3124210133510146644[6] = 0;
   out_3124210133510146644[7] = 0;
   out_3124210133510146644[8] = 0;
   out_3124210133510146644[9] = 0;
   out_3124210133510146644[10] = 1;
   out_3124210133510146644[11] = 0;
   out_3124210133510146644[12] = 0;
   out_3124210133510146644[13] = 0;
   out_3124210133510146644[14] = 0;
   out_3124210133510146644[15] = 0;
   out_3124210133510146644[16] = 0;
   out_3124210133510146644[17] = 0;
   out_3124210133510146644[18] = 0;
   out_3124210133510146644[19] = 0;
   out_3124210133510146644[20] = 1;
   out_3124210133510146644[21] = 0;
   out_3124210133510146644[22] = 0;
   out_3124210133510146644[23] = 0;
   out_3124210133510146644[24] = 0;
   out_3124210133510146644[25] = 0;
   out_3124210133510146644[26] = 0;
   out_3124210133510146644[27] = 0;
   out_3124210133510146644[28] = 0;
   out_3124210133510146644[29] = 0;
   out_3124210133510146644[30] = 1;
   out_3124210133510146644[31] = 0;
   out_3124210133510146644[32] = 0;
   out_3124210133510146644[33] = 0;
   out_3124210133510146644[34] = 0;
   out_3124210133510146644[35] = 0;
   out_3124210133510146644[36] = 0;
   out_3124210133510146644[37] = 0;
   out_3124210133510146644[38] = 0;
   out_3124210133510146644[39] = 0;
   out_3124210133510146644[40] = 1;
   out_3124210133510146644[41] = 0;
   out_3124210133510146644[42] = 0;
   out_3124210133510146644[43] = 0;
   out_3124210133510146644[44] = 0;
   out_3124210133510146644[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_3124210133510146644[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_3124210133510146644[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3124210133510146644[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3124210133510146644[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_3124210133510146644[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_3124210133510146644[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_3124210133510146644[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_3124210133510146644[53] = -9.8100000000000005*dt;
   out_3124210133510146644[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_3124210133510146644[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_3124210133510146644[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3124210133510146644[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3124210133510146644[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_3124210133510146644[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_3124210133510146644[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_3124210133510146644[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3124210133510146644[62] = 0;
   out_3124210133510146644[63] = 0;
   out_3124210133510146644[64] = 0;
   out_3124210133510146644[65] = 0;
   out_3124210133510146644[66] = 0;
   out_3124210133510146644[67] = 0;
   out_3124210133510146644[68] = 0;
   out_3124210133510146644[69] = 0;
   out_3124210133510146644[70] = 1;
   out_3124210133510146644[71] = 0;
   out_3124210133510146644[72] = 0;
   out_3124210133510146644[73] = 0;
   out_3124210133510146644[74] = 0;
   out_3124210133510146644[75] = 0;
   out_3124210133510146644[76] = 0;
   out_3124210133510146644[77] = 0;
   out_3124210133510146644[78] = 0;
   out_3124210133510146644[79] = 0;
   out_3124210133510146644[80] = 1;
}
void h_25(double *state, double *unused, double *out_4133024183340150425) {
   out_4133024183340150425[0] = state[6];
}
void H_25(double *state, double *unused, double *out_1013225457892324931) {
   out_1013225457892324931[0] = 0;
   out_1013225457892324931[1] = 0;
   out_1013225457892324931[2] = 0;
   out_1013225457892324931[3] = 0;
   out_1013225457892324931[4] = 0;
   out_1013225457892324931[5] = 0;
   out_1013225457892324931[6] = 1;
   out_1013225457892324931[7] = 0;
   out_1013225457892324931[8] = 0;
}
void h_24(double *state, double *unused, double *out_3391899593912198426) {
   out_3391899593912198426[0] = state[4];
   out_3391899593912198426[1] = state[5];
}
void H_24(double *state, double *unused, double *out_3185875056897824497) {
   out_3185875056897824497[0] = 0;
   out_3185875056897824497[1] = 0;
   out_3185875056897824497[2] = 0;
   out_3185875056897824497[3] = 0;
   out_3185875056897824497[4] = 1;
   out_3185875056897824497[5] = 0;
   out_3185875056897824497[6] = 0;
   out_3185875056897824497[7] = 0;
   out_3185875056897824497[8] = 0;
   out_3185875056897824497[9] = 0;
   out_3185875056897824497[10] = 0;
   out_3185875056897824497[11] = 0;
   out_3185875056897824497[12] = 0;
   out_3185875056897824497[13] = 0;
   out_3185875056897824497[14] = 1;
   out_3185875056897824497[15] = 0;
   out_3185875056897824497[16] = 0;
   out_3185875056897824497[17] = 0;
}
void h_30(double *state, double *unused, double *out_3346447755699384264) {
   out_3346447755699384264[0] = state[4];
}
void H_30(double *state, double *unused, double *out_1505107500614923696) {
   out_1505107500614923696[0] = 0;
   out_1505107500614923696[1] = 0;
   out_1505107500614923696[2] = 0;
   out_1505107500614923696[3] = 0;
   out_1505107500614923696[4] = 1;
   out_1505107500614923696[5] = 0;
   out_1505107500614923696[6] = 0;
   out_1505107500614923696[7] = 0;
   out_1505107500614923696[8] = 0;
}
void h_26(double *state, double *unused, double *out_9213411574954820401) {
   out_9213411574954820401[0] = state[7];
}
void H_26(double *state, double *unused, double *out_4754728776766381155) {
   out_4754728776766381155[0] = 0;
   out_4754728776766381155[1] = 0;
   out_4754728776766381155[2] = 0;
   out_4754728776766381155[3] = 0;
   out_4754728776766381155[4] = 0;
   out_4754728776766381155[5] = 0;
   out_4754728776766381155[6] = 0;
   out_4754728776766381155[7] = 1;
   out_4754728776766381155[8] = 0;
}
void h_27(double *state, double *unused, double *out_1011865879775497112) {
   out_1011865879775497112[0] = state[3];
}
void H_27(double *state, double *unused, double *out_3728701571798866913) {
   out_3728701571798866913[0] = 0;
   out_3728701571798866913[1] = 0;
   out_3728701571798866913[2] = 0;
   out_3728701571798866913[3] = 1;
   out_3728701571798866913[4] = 0;
   out_3728701571798866913[5] = 0;
   out_3728701571798866913[6] = 0;
   out_3728701571798866913[7] = 0;
   out_3728701571798866913[8] = 0;
}
void h_29(double *state, double *unused, double *out_1287059942060003001) {
   out_1287059942060003001[0] = state[1];
}
void H_29(double *state, double *unused, double *out_2015338844929315880) {
   out_2015338844929315880[0] = 0;
   out_2015338844929315880[1] = 1;
   out_2015338844929315880[2] = 0;
   out_2015338844929315880[3] = 0;
   out_2015338844929315880[4] = 0;
   out_2015338844929315880[5] = 0;
   out_2015338844929315880[6] = 0;
   out_2015338844929315880[7] = 0;
   out_2015338844929315880[8] = 0;
}
void h_28(double *state, double *unused, double *out_566195834839143975) {
   out_566195834839143975[0] = state[0];
}
void H_28(double *state, double *unused, double *out_3067060172140214694) {
   out_3067060172140214694[0] = 1;
   out_3067060172140214694[1] = 0;
   out_3067060172140214694[2] = 0;
   out_3067060172140214694[3] = 0;
   out_3067060172140214694[4] = 0;
   out_3067060172140214694[5] = 0;
   out_3067060172140214694[6] = 0;
   out_3067060172140214694[7] = 0;
   out_3067060172140214694[8] = 0;
}
void h_31(double *state, double *unused, double *out_4506853293378391459) {
   out_4506853293378391459[0] = state[8];
}
void H_31(double *state, double *unused, double *out_5380936878999732631) {
   out_5380936878999732631[0] = 0;
   out_5380936878999732631[1] = 0;
   out_5380936878999732631[2] = 0;
   out_5380936878999732631[3] = 0;
   out_5380936878999732631[4] = 0;
   out_5380936878999732631[5] = 0;
   out_5380936878999732631[6] = 0;
   out_5380936878999732631[7] = 0;
   out_5380936878999732631[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_6787215922179600543) {
  err_fun(nom_x, delta_x, out_6787215922179600543);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6360714375878173456) {
  inv_err_fun(nom_x, true_x, out_6360714375878173456);
}
void car_H_mod_fun(double *state, double *out_8179962768019912306) {
  H_mod_fun(state, out_8179962768019912306);
}
void car_f_fun(double *state, double dt, double *out_519966246064059535) {
  f_fun(state,  dt, out_519966246064059535);
}
void car_F_fun(double *state, double dt, double *out_3124210133510146644) {
  F_fun(state,  dt, out_3124210133510146644);
}
void car_h_25(double *state, double *unused, double *out_4133024183340150425) {
  h_25(state, unused, out_4133024183340150425);
}
void car_H_25(double *state, double *unused, double *out_1013225457892324931) {
  H_25(state, unused, out_1013225457892324931);
}
void car_h_24(double *state, double *unused, double *out_3391899593912198426) {
  h_24(state, unused, out_3391899593912198426);
}
void car_H_24(double *state, double *unused, double *out_3185875056897824497) {
  H_24(state, unused, out_3185875056897824497);
}
void car_h_30(double *state, double *unused, double *out_3346447755699384264) {
  h_30(state, unused, out_3346447755699384264);
}
void car_H_30(double *state, double *unused, double *out_1505107500614923696) {
  H_30(state, unused, out_1505107500614923696);
}
void car_h_26(double *state, double *unused, double *out_9213411574954820401) {
  h_26(state, unused, out_9213411574954820401);
}
void car_H_26(double *state, double *unused, double *out_4754728776766381155) {
  H_26(state, unused, out_4754728776766381155);
}
void car_h_27(double *state, double *unused, double *out_1011865879775497112) {
  h_27(state, unused, out_1011865879775497112);
}
void car_H_27(double *state, double *unused, double *out_3728701571798866913) {
  H_27(state, unused, out_3728701571798866913);
}
void car_h_29(double *state, double *unused, double *out_1287059942060003001) {
  h_29(state, unused, out_1287059942060003001);
}
void car_H_29(double *state, double *unused, double *out_2015338844929315880) {
  H_29(state, unused, out_2015338844929315880);
}
void car_h_28(double *state, double *unused, double *out_566195834839143975) {
  h_28(state, unused, out_566195834839143975);
}
void car_H_28(double *state, double *unused, double *out_3067060172140214694) {
  H_28(state, unused, out_3067060172140214694);
}
void car_h_31(double *state, double *unused, double *out_4506853293378391459) {
  h_31(state, unused, out_4506853293378391459);
}
void car_H_31(double *state, double *unused, double *out_5380936878999732631) {
  H_31(state, unused, out_5380936878999732631);
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
