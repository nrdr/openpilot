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
void err_fun(double *nom_x, double *delta_x, double *out_5394216099023030170) {
   out_5394216099023030170[0] = delta_x[0] + nom_x[0];
   out_5394216099023030170[1] = delta_x[1] + nom_x[1];
   out_5394216099023030170[2] = delta_x[2] + nom_x[2];
   out_5394216099023030170[3] = delta_x[3] + nom_x[3];
   out_5394216099023030170[4] = delta_x[4] + nom_x[4];
   out_5394216099023030170[5] = delta_x[5] + nom_x[5];
   out_5394216099023030170[6] = delta_x[6] + nom_x[6];
   out_5394216099023030170[7] = delta_x[7] + nom_x[7];
   out_5394216099023030170[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1268510137061119882) {
   out_1268510137061119882[0] = -nom_x[0] + true_x[0];
   out_1268510137061119882[1] = -nom_x[1] + true_x[1];
   out_1268510137061119882[2] = -nom_x[2] + true_x[2];
   out_1268510137061119882[3] = -nom_x[3] + true_x[3];
   out_1268510137061119882[4] = -nom_x[4] + true_x[4];
   out_1268510137061119882[5] = -nom_x[5] + true_x[5];
   out_1268510137061119882[6] = -nom_x[6] + true_x[6];
   out_1268510137061119882[7] = -nom_x[7] + true_x[7];
   out_1268510137061119882[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_27038522722598530) {
   out_27038522722598530[0] = 1.0;
   out_27038522722598530[1] = 0.0;
   out_27038522722598530[2] = 0.0;
   out_27038522722598530[3] = 0.0;
   out_27038522722598530[4] = 0.0;
   out_27038522722598530[5] = 0.0;
   out_27038522722598530[6] = 0.0;
   out_27038522722598530[7] = 0.0;
   out_27038522722598530[8] = 0.0;
   out_27038522722598530[9] = 0.0;
   out_27038522722598530[10] = 1.0;
   out_27038522722598530[11] = 0.0;
   out_27038522722598530[12] = 0.0;
   out_27038522722598530[13] = 0.0;
   out_27038522722598530[14] = 0.0;
   out_27038522722598530[15] = 0.0;
   out_27038522722598530[16] = 0.0;
   out_27038522722598530[17] = 0.0;
   out_27038522722598530[18] = 0.0;
   out_27038522722598530[19] = 0.0;
   out_27038522722598530[20] = 1.0;
   out_27038522722598530[21] = 0.0;
   out_27038522722598530[22] = 0.0;
   out_27038522722598530[23] = 0.0;
   out_27038522722598530[24] = 0.0;
   out_27038522722598530[25] = 0.0;
   out_27038522722598530[26] = 0.0;
   out_27038522722598530[27] = 0.0;
   out_27038522722598530[28] = 0.0;
   out_27038522722598530[29] = 0.0;
   out_27038522722598530[30] = 1.0;
   out_27038522722598530[31] = 0.0;
   out_27038522722598530[32] = 0.0;
   out_27038522722598530[33] = 0.0;
   out_27038522722598530[34] = 0.0;
   out_27038522722598530[35] = 0.0;
   out_27038522722598530[36] = 0.0;
   out_27038522722598530[37] = 0.0;
   out_27038522722598530[38] = 0.0;
   out_27038522722598530[39] = 0.0;
   out_27038522722598530[40] = 1.0;
   out_27038522722598530[41] = 0.0;
   out_27038522722598530[42] = 0.0;
   out_27038522722598530[43] = 0.0;
   out_27038522722598530[44] = 0.0;
   out_27038522722598530[45] = 0.0;
   out_27038522722598530[46] = 0.0;
   out_27038522722598530[47] = 0.0;
   out_27038522722598530[48] = 0.0;
   out_27038522722598530[49] = 0.0;
   out_27038522722598530[50] = 1.0;
   out_27038522722598530[51] = 0.0;
   out_27038522722598530[52] = 0.0;
   out_27038522722598530[53] = 0.0;
   out_27038522722598530[54] = 0.0;
   out_27038522722598530[55] = 0.0;
   out_27038522722598530[56] = 0.0;
   out_27038522722598530[57] = 0.0;
   out_27038522722598530[58] = 0.0;
   out_27038522722598530[59] = 0.0;
   out_27038522722598530[60] = 1.0;
   out_27038522722598530[61] = 0.0;
   out_27038522722598530[62] = 0.0;
   out_27038522722598530[63] = 0.0;
   out_27038522722598530[64] = 0.0;
   out_27038522722598530[65] = 0.0;
   out_27038522722598530[66] = 0.0;
   out_27038522722598530[67] = 0.0;
   out_27038522722598530[68] = 0.0;
   out_27038522722598530[69] = 0.0;
   out_27038522722598530[70] = 1.0;
   out_27038522722598530[71] = 0.0;
   out_27038522722598530[72] = 0.0;
   out_27038522722598530[73] = 0.0;
   out_27038522722598530[74] = 0.0;
   out_27038522722598530[75] = 0.0;
   out_27038522722598530[76] = 0.0;
   out_27038522722598530[77] = 0.0;
   out_27038522722598530[78] = 0.0;
   out_27038522722598530[79] = 0.0;
   out_27038522722598530[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_6605105798485234217) {
   out_6605105798485234217[0] = state[0];
   out_6605105798485234217[1] = state[1];
   out_6605105798485234217[2] = state[2];
   out_6605105798485234217[3] = state[3];
   out_6605105798485234217[4] = state[4];
   out_6605105798485234217[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_6605105798485234217[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_6605105798485234217[7] = state[7];
   out_6605105798485234217[8] = state[8];
}
void F_fun(double *state, double dt, double *out_1879544495240993634) {
   out_1879544495240993634[0] = 1;
   out_1879544495240993634[1] = 0;
   out_1879544495240993634[2] = 0;
   out_1879544495240993634[3] = 0;
   out_1879544495240993634[4] = 0;
   out_1879544495240993634[5] = 0;
   out_1879544495240993634[6] = 0;
   out_1879544495240993634[7] = 0;
   out_1879544495240993634[8] = 0;
   out_1879544495240993634[9] = 0;
   out_1879544495240993634[10] = 1;
   out_1879544495240993634[11] = 0;
   out_1879544495240993634[12] = 0;
   out_1879544495240993634[13] = 0;
   out_1879544495240993634[14] = 0;
   out_1879544495240993634[15] = 0;
   out_1879544495240993634[16] = 0;
   out_1879544495240993634[17] = 0;
   out_1879544495240993634[18] = 0;
   out_1879544495240993634[19] = 0;
   out_1879544495240993634[20] = 1;
   out_1879544495240993634[21] = 0;
   out_1879544495240993634[22] = 0;
   out_1879544495240993634[23] = 0;
   out_1879544495240993634[24] = 0;
   out_1879544495240993634[25] = 0;
   out_1879544495240993634[26] = 0;
   out_1879544495240993634[27] = 0;
   out_1879544495240993634[28] = 0;
   out_1879544495240993634[29] = 0;
   out_1879544495240993634[30] = 1;
   out_1879544495240993634[31] = 0;
   out_1879544495240993634[32] = 0;
   out_1879544495240993634[33] = 0;
   out_1879544495240993634[34] = 0;
   out_1879544495240993634[35] = 0;
   out_1879544495240993634[36] = 0;
   out_1879544495240993634[37] = 0;
   out_1879544495240993634[38] = 0;
   out_1879544495240993634[39] = 0;
   out_1879544495240993634[40] = 1;
   out_1879544495240993634[41] = 0;
   out_1879544495240993634[42] = 0;
   out_1879544495240993634[43] = 0;
   out_1879544495240993634[44] = 0;
   out_1879544495240993634[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_1879544495240993634[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_1879544495240993634[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_1879544495240993634[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_1879544495240993634[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_1879544495240993634[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_1879544495240993634[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_1879544495240993634[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_1879544495240993634[53] = -9.8100000000000005*dt;
   out_1879544495240993634[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_1879544495240993634[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_1879544495240993634[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1879544495240993634[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1879544495240993634[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_1879544495240993634[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_1879544495240993634[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_1879544495240993634[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1879544495240993634[62] = 0;
   out_1879544495240993634[63] = 0;
   out_1879544495240993634[64] = 0;
   out_1879544495240993634[65] = 0;
   out_1879544495240993634[66] = 0;
   out_1879544495240993634[67] = 0;
   out_1879544495240993634[68] = 0;
   out_1879544495240993634[69] = 0;
   out_1879544495240993634[70] = 1;
   out_1879544495240993634[71] = 0;
   out_1879544495240993634[72] = 0;
   out_1879544495240993634[73] = 0;
   out_1879544495240993634[74] = 0;
   out_1879544495240993634[75] = 0;
   out_1879544495240993634[76] = 0;
   out_1879544495240993634[77] = 0;
   out_1879544495240993634[78] = 0;
   out_1879544495240993634[79] = 0;
   out_1879544495240993634[80] = 1;
}
void h_25(double *state, double *unused, double *out_5624646906532576969) {
   out_5624646906532576969[0] = state[6];
}
void H_25(double *state, double *unused, double *out_5366051290200112092) {
   out_5366051290200112092[0] = 0;
   out_5366051290200112092[1] = 0;
   out_5366051290200112092[2] = 0;
   out_5366051290200112092[3] = 0;
   out_5366051290200112092[4] = 0;
   out_5366051290200112092[5] = 0;
   out_5366051290200112092[6] = 1;
   out_5366051290200112092[7] = 0;
   out_5366051290200112092[8] = 0;
}
void h_24(double *state, double *unused, double *out_1782389657789830899) {
   out_1782389657789830899[0] = state[4];
   out_1782389657789830899[1] = state[5];
}
void H_24(double *state, double *unused, double *out_7053867726069216283) {
   out_7053867726069216283[0] = 0;
   out_7053867726069216283[1] = 0;
   out_7053867726069216283[2] = 0;
   out_7053867726069216283[3] = 0;
   out_7053867726069216283[4] = 1;
   out_7053867726069216283[5] = 0;
   out_7053867726069216283[6] = 0;
   out_7053867726069216283[7] = 0;
   out_7053867726069216283[8] = 0;
   out_7053867726069216283[9] = 0;
   out_7053867726069216283[10] = 0;
   out_7053867726069216283[11] = 0;
   out_7053867726069216283[12] = 0;
   out_7053867726069216283[13] = 0;
   out_7053867726069216283[14] = 1;
   out_7053867726069216283[15] = 0;
   out_7053867726069216283[16] = 0;
   out_7053867726069216283[17] = 0;
}
void h_30(double *state, double *unused, double *out_7075278299161460136) {
   out_7075278299161460136[0] = state[4];
}
void H_30(double *state, double *unused, double *out_5236712343056872022) {
   out_5236712343056872022[0] = 0;
   out_5236712343056872022[1] = 0;
   out_5236712343056872022[2] = 0;
   out_5236712343056872022[3] = 0;
   out_5236712343056872022[4] = 1;
   out_5236712343056872022[5] = 0;
   out_5236712343056872022[6] = 0;
   out_5236712343056872022[7] = 0;
   out_5236712343056872022[8] = 0;
}
void h_26(double *state, double *unused, double *out_5728735903467134645) {
   out_5728735903467134645[0] = state[7];
}
void H_26(double *state, double *unused, double *out_1624547971326055868) {
   out_1624547971326055868[0] = 0;
   out_1624547971326055868[1] = 0;
   out_1624547971326055868[2] = 0;
   out_1624547971326055868[3] = 0;
   out_1624547971326055868[4] = 0;
   out_1624547971326055868[5] = 0;
   out_1624547971326055868[6] = 0;
   out_1624547971326055868[7] = 1;
   out_1624547971326055868[8] = 0;
}
void h_27(double *state, double *unused, double *out_1994890907546790160) {
   out_1994890907546790160[0] = state[3];
}
void H_27(double *state, double *unused, double *out_3061949031256447111) {
   out_3061949031256447111[0] = 0;
   out_3061949031256447111[1] = 0;
   out_3061949031256447111[2] = 0;
   out_3061949031256447111[3] = 1;
   out_3061949031256447111[4] = 0;
   out_3061949031256447111[5] = 0;
   out_3061949031256447111[6] = 0;
   out_3061949031256447111[7] = 0;
   out_3061949031256447111[8] = 0;
}
void h_29(double *state, double *unused, double *out_5886381743207259025) {
   out_5886381743207259025[0] = state[1];
}
void H_29(double *state, double *unused, double *out_1348586304386896078) {
   out_1348586304386896078[0] = 0;
   out_1348586304386896078[1] = 1;
   out_1348586304386896078[2] = 0;
   out_1348586304386896078[3] = 0;
   out_1348586304386896078[4] = 0;
   out_1348586304386896078[5] = 0;
   out_1348586304386896078[6] = 0;
   out_1348586304386896078[7] = 0;
   out_1348586304386896078[8] = 0;
}
void h_28(double *state, double *unused, double *out_8202048695027411215) {
   out_8202048695027411215[0] = state[0];
}
void H_28(double *state, double *unused, double *out_3733812712682634496) {
   out_3733812712682634496[0] = 1;
   out_3733812712682634496[1] = 0;
   out_3733812712682634496[2] = 0;
   out_3733812712682634496[3] = 0;
   out_3733812712682634496[4] = 0;
   out_3733812712682634496[5] = 0;
   out_3733812712682634496[6] = 0;
   out_3733812712682634496[7] = 0;
   out_3733812712682634496[8] = 0;
}
void h_31(double *state, double *unused, double *out_3252169063166594161) {
   out_3252169063166594161[0] = state[8];
}
void H_31(double *state, double *unused, double *out_5396697252077072520) {
   out_5396697252077072520[0] = 0;
   out_5396697252077072520[1] = 0;
   out_5396697252077072520[2] = 0;
   out_5396697252077072520[3] = 0;
   out_5396697252077072520[4] = 0;
   out_5396697252077072520[5] = 0;
   out_5396697252077072520[6] = 0;
   out_5396697252077072520[7] = 0;
   out_5396697252077072520[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_5394216099023030170) {
  err_fun(nom_x, delta_x, out_5394216099023030170);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1268510137061119882) {
  inv_err_fun(nom_x, true_x, out_1268510137061119882);
}
void car_H_mod_fun(double *state, double *out_27038522722598530) {
  H_mod_fun(state, out_27038522722598530);
}
void car_f_fun(double *state, double dt, double *out_6605105798485234217) {
  f_fun(state,  dt, out_6605105798485234217);
}
void car_F_fun(double *state, double dt, double *out_1879544495240993634) {
  F_fun(state,  dt, out_1879544495240993634);
}
void car_h_25(double *state, double *unused, double *out_5624646906532576969) {
  h_25(state, unused, out_5624646906532576969);
}
void car_H_25(double *state, double *unused, double *out_5366051290200112092) {
  H_25(state, unused, out_5366051290200112092);
}
void car_h_24(double *state, double *unused, double *out_1782389657789830899) {
  h_24(state, unused, out_1782389657789830899);
}
void car_H_24(double *state, double *unused, double *out_7053867726069216283) {
  H_24(state, unused, out_7053867726069216283);
}
void car_h_30(double *state, double *unused, double *out_7075278299161460136) {
  h_30(state, unused, out_7075278299161460136);
}
void car_H_30(double *state, double *unused, double *out_5236712343056872022) {
  H_30(state, unused, out_5236712343056872022);
}
void car_h_26(double *state, double *unused, double *out_5728735903467134645) {
  h_26(state, unused, out_5728735903467134645);
}
void car_H_26(double *state, double *unused, double *out_1624547971326055868) {
  H_26(state, unused, out_1624547971326055868);
}
void car_h_27(double *state, double *unused, double *out_1994890907546790160) {
  h_27(state, unused, out_1994890907546790160);
}
void car_H_27(double *state, double *unused, double *out_3061949031256447111) {
  H_27(state, unused, out_3061949031256447111);
}
void car_h_29(double *state, double *unused, double *out_5886381743207259025) {
  h_29(state, unused, out_5886381743207259025);
}
void car_H_29(double *state, double *unused, double *out_1348586304386896078) {
  H_29(state, unused, out_1348586304386896078);
}
void car_h_28(double *state, double *unused, double *out_8202048695027411215) {
  h_28(state, unused, out_8202048695027411215);
}
void car_H_28(double *state, double *unused, double *out_3733812712682634496) {
  H_28(state, unused, out_3733812712682634496);
}
void car_h_31(double *state, double *unused, double *out_3252169063166594161) {
  h_31(state, unused, out_3252169063166594161);
}
void car_H_31(double *state, double *unused, double *out_5396697252077072520) {
  H_31(state, unused, out_5396697252077072520);
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
