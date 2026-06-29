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
void err_fun(double *nom_x, double *delta_x, double *out_1150556946497607115) {
   out_1150556946497607115[0] = delta_x[0] + nom_x[0];
   out_1150556946497607115[1] = delta_x[1] + nom_x[1];
   out_1150556946497607115[2] = delta_x[2] + nom_x[2];
   out_1150556946497607115[3] = delta_x[3] + nom_x[3];
   out_1150556946497607115[4] = delta_x[4] + nom_x[4];
   out_1150556946497607115[5] = delta_x[5] + nom_x[5];
   out_1150556946497607115[6] = delta_x[6] + nom_x[6];
   out_1150556946497607115[7] = delta_x[7] + nom_x[7];
   out_1150556946497607115[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6384736535090160916) {
   out_6384736535090160916[0] = -nom_x[0] + true_x[0];
   out_6384736535090160916[1] = -nom_x[1] + true_x[1];
   out_6384736535090160916[2] = -nom_x[2] + true_x[2];
   out_6384736535090160916[3] = -nom_x[3] + true_x[3];
   out_6384736535090160916[4] = -nom_x[4] + true_x[4];
   out_6384736535090160916[5] = -nom_x[5] + true_x[5];
   out_6384736535090160916[6] = -nom_x[6] + true_x[6];
   out_6384736535090160916[7] = -nom_x[7] + true_x[7];
   out_6384736535090160916[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_8501357178821987276) {
   out_8501357178821987276[0] = 1.0;
   out_8501357178821987276[1] = 0.0;
   out_8501357178821987276[2] = 0.0;
   out_8501357178821987276[3] = 0.0;
   out_8501357178821987276[4] = 0.0;
   out_8501357178821987276[5] = 0.0;
   out_8501357178821987276[6] = 0.0;
   out_8501357178821987276[7] = 0.0;
   out_8501357178821987276[8] = 0.0;
   out_8501357178821987276[9] = 0.0;
   out_8501357178821987276[10] = 1.0;
   out_8501357178821987276[11] = 0.0;
   out_8501357178821987276[12] = 0.0;
   out_8501357178821987276[13] = 0.0;
   out_8501357178821987276[14] = 0.0;
   out_8501357178821987276[15] = 0.0;
   out_8501357178821987276[16] = 0.0;
   out_8501357178821987276[17] = 0.0;
   out_8501357178821987276[18] = 0.0;
   out_8501357178821987276[19] = 0.0;
   out_8501357178821987276[20] = 1.0;
   out_8501357178821987276[21] = 0.0;
   out_8501357178821987276[22] = 0.0;
   out_8501357178821987276[23] = 0.0;
   out_8501357178821987276[24] = 0.0;
   out_8501357178821987276[25] = 0.0;
   out_8501357178821987276[26] = 0.0;
   out_8501357178821987276[27] = 0.0;
   out_8501357178821987276[28] = 0.0;
   out_8501357178821987276[29] = 0.0;
   out_8501357178821987276[30] = 1.0;
   out_8501357178821987276[31] = 0.0;
   out_8501357178821987276[32] = 0.0;
   out_8501357178821987276[33] = 0.0;
   out_8501357178821987276[34] = 0.0;
   out_8501357178821987276[35] = 0.0;
   out_8501357178821987276[36] = 0.0;
   out_8501357178821987276[37] = 0.0;
   out_8501357178821987276[38] = 0.0;
   out_8501357178821987276[39] = 0.0;
   out_8501357178821987276[40] = 1.0;
   out_8501357178821987276[41] = 0.0;
   out_8501357178821987276[42] = 0.0;
   out_8501357178821987276[43] = 0.0;
   out_8501357178821987276[44] = 0.0;
   out_8501357178821987276[45] = 0.0;
   out_8501357178821987276[46] = 0.0;
   out_8501357178821987276[47] = 0.0;
   out_8501357178821987276[48] = 0.0;
   out_8501357178821987276[49] = 0.0;
   out_8501357178821987276[50] = 1.0;
   out_8501357178821987276[51] = 0.0;
   out_8501357178821987276[52] = 0.0;
   out_8501357178821987276[53] = 0.0;
   out_8501357178821987276[54] = 0.0;
   out_8501357178821987276[55] = 0.0;
   out_8501357178821987276[56] = 0.0;
   out_8501357178821987276[57] = 0.0;
   out_8501357178821987276[58] = 0.0;
   out_8501357178821987276[59] = 0.0;
   out_8501357178821987276[60] = 1.0;
   out_8501357178821987276[61] = 0.0;
   out_8501357178821987276[62] = 0.0;
   out_8501357178821987276[63] = 0.0;
   out_8501357178821987276[64] = 0.0;
   out_8501357178821987276[65] = 0.0;
   out_8501357178821987276[66] = 0.0;
   out_8501357178821987276[67] = 0.0;
   out_8501357178821987276[68] = 0.0;
   out_8501357178821987276[69] = 0.0;
   out_8501357178821987276[70] = 1.0;
   out_8501357178821987276[71] = 0.0;
   out_8501357178821987276[72] = 0.0;
   out_8501357178821987276[73] = 0.0;
   out_8501357178821987276[74] = 0.0;
   out_8501357178821987276[75] = 0.0;
   out_8501357178821987276[76] = 0.0;
   out_8501357178821987276[77] = 0.0;
   out_8501357178821987276[78] = 0.0;
   out_8501357178821987276[79] = 0.0;
   out_8501357178821987276[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_1001507699327886070) {
   out_1001507699327886070[0] = state[0];
   out_1001507699327886070[1] = state[1];
   out_1001507699327886070[2] = state[2];
   out_1001507699327886070[3] = state[3];
   out_1001507699327886070[4] = state[4];
   out_1001507699327886070[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_1001507699327886070[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_1001507699327886070[7] = state[7];
   out_1001507699327886070[8] = state[8];
}
void F_fun(double *state, double dt, double *out_679377826983824795) {
   out_679377826983824795[0] = 1;
   out_679377826983824795[1] = 0;
   out_679377826983824795[2] = 0;
   out_679377826983824795[3] = 0;
   out_679377826983824795[4] = 0;
   out_679377826983824795[5] = 0;
   out_679377826983824795[6] = 0;
   out_679377826983824795[7] = 0;
   out_679377826983824795[8] = 0;
   out_679377826983824795[9] = 0;
   out_679377826983824795[10] = 1;
   out_679377826983824795[11] = 0;
   out_679377826983824795[12] = 0;
   out_679377826983824795[13] = 0;
   out_679377826983824795[14] = 0;
   out_679377826983824795[15] = 0;
   out_679377826983824795[16] = 0;
   out_679377826983824795[17] = 0;
   out_679377826983824795[18] = 0;
   out_679377826983824795[19] = 0;
   out_679377826983824795[20] = 1;
   out_679377826983824795[21] = 0;
   out_679377826983824795[22] = 0;
   out_679377826983824795[23] = 0;
   out_679377826983824795[24] = 0;
   out_679377826983824795[25] = 0;
   out_679377826983824795[26] = 0;
   out_679377826983824795[27] = 0;
   out_679377826983824795[28] = 0;
   out_679377826983824795[29] = 0;
   out_679377826983824795[30] = 1;
   out_679377826983824795[31] = 0;
   out_679377826983824795[32] = 0;
   out_679377826983824795[33] = 0;
   out_679377826983824795[34] = 0;
   out_679377826983824795[35] = 0;
   out_679377826983824795[36] = 0;
   out_679377826983824795[37] = 0;
   out_679377826983824795[38] = 0;
   out_679377826983824795[39] = 0;
   out_679377826983824795[40] = 1;
   out_679377826983824795[41] = 0;
   out_679377826983824795[42] = 0;
   out_679377826983824795[43] = 0;
   out_679377826983824795[44] = 0;
   out_679377826983824795[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_679377826983824795[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_679377826983824795[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_679377826983824795[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_679377826983824795[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_679377826983824795[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_679377826983824795[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_679377826983824795[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_679377826983824795[53] = -9.8100000000000005*dt;
   out_679377826983824795[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_679377826983824795[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_679377826983824795[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_679377826983824795[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_679377826983824795[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_679377826983824795[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_679377826983824795[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_679377826983824795[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_679377826983824795[62] = 0;
   out_679377826983824795[63] = 0;
   out_679377826983824795[64] = 0;
   out_679377826983824795[65] = 0;
   out_679377826983824795[66] = 0;
   out_679377826983824795[67] = 0;
   out_679377826983824795[68] = 0;
   out_679377826983824795[69] = 0;
   out_679377826983824795[70] = 1;
   out_679377826983824795[71] = 0;
   out_679377826983824795[72] = 0;
   out_679377826983824795[73] = 0;
   out_679377826983824795[74] = 0;
   out_679377826983824795[75] = 0;
   out_679377826983824795[76] = 0;
   out_679377826983824795[77] = 0;
   out_679377826983824795[78] = 0;
   out_679377826983824795[79] = 0;
   out_679377826983824795[80] = 1;
}
void h_25(double *state, double *unused, double *out_7405352995896305810) {
   out_7405352995896305810[0] = state[6];
}
void H_25(double *state, double *unused, double *out_6422406244898072663) {
   out_6422406244898072663[0] = 0;
   out_6422406244898072663[1] = 0;
   out_6422406244898072663[2] = 0;
   out_6422406244898072663[3] = 0;
   out_6422406244898072663[4] = 0;
   out_6422406244898072663[5] = 0;
   out_6422406244898072663[6] = 1;
   out_6422406244898072663[7] = 0;
   out_6422406244898072663[8] = 0;
}
void h_24(double *state, double *unused, double *out_7209079107772895242) {
   out_7209079107772895242[0] = state[4];
   out_7209079107772895242[1] = state[5];
}
void H_24(double *state, double *unused, double *out_2864480646095749527) {
   out_2864480646095749527[0] = 0;
   out_2864480646095749527[1] = 0;
   out_2864480646095749527[2] = 0;
   out_2864480646095749527[3] = 0;
   out_2864480646095749527[4] = 1;
   out_2864480646095749527[5] = 0;
   out_2864480646095749527[6] = 0;
   out_2864480646095749527[7] = 0;
   out_2864480646095749527[8] = 0;
   out_2864480646095749527[9] = 0;
   out_2864480646095749527[10] = 0;
   out_2864480646095749527[11] = 0;
   out_2864480646095749527[12] = 0;
   out_2864480646095749527[13] = 0;
   out_2864480646095749527[14] = 1;
   out_2864480646095749527[15] = 0;
   out_2864480646095749527[16] = 0;
   out_2864480646095749527[17] = 0;
}
void h_30(double *state, double *unused, double *out_4074075913132213312) {
   out_4074075913132213312[0] = state[4];
}
void H_30(double *state, double *unused, double *out_494284096593544092) {
   out_494284096593544092[0] = 0;
   out_494284096593544092[1] = 0;
   out_494284096593544092[2] = 0;
   out_494284096593544092[3] = 0;
   out_494284096593544092[4] = 1;
   out_494284096593544092[5] = 0;
   out_494284096593544092[6] = 0;
   out_494284096593544092[7] = 0;
   out_494284096593544092[8] = 0;
}
void h_26(double *state, double *unused, double *out_888304084549079920) {
   out_888304084549079920[0] = state[7];
}
void H_26(double *state, double *unused, double *out_8282834509937422729) {
   out_8282834509937422729[0] = 0;
   out_8282834509937422729[1] = 0;
   out_8282834509937422729[2] = 0;
   out_8282834509937422729[3] = 0;
   out_8282834509937422729[4] = 0;
   out_8282834509937422729[5] = 0;
   out_8282834509937422729[6] = 0;
   out_8282834509937422729[7] = 1;
   out_8282834509937422729[8] = 0;
}
void h_27(double *state, double *unused, double *out_6039717810152400161) {
   out_6039717810152400161[0] = state[3];
}
void H_27(double *state, double *unused, double *out_1680479215206880819) {
   out_1680479215206880819[0] = 0;
   out_1680479215206880819[1] = 0;
   out_1680479215206880819[2] = 0;
   out_1680479215206880819[3] = 1;
   out_1680479215206880819[4] = 0;
   out_1680479215206880819[5] = 0;
   out_1680479215206880819[6] = 0;
   out_1680479215206880819[7] = 0;
   out_1680479215206880819[8] = 0;
}
void h_29(double *state, double *unused, double *out_4946467499308263130) {
   out_4946467499308263130[0] = state[1];
}
void H_29(double *state, double *unused, double *out_1004515440907936276) {
   out_1004515440907936276[0] = 0;
   out_1004515440907936276[1] = 1;
   out_1004515440907936276[2] = 0;
   out_1004515440907936276[3] = 0;
   out_1004515440907936276[4] = 0;
   out_1004515440907936276[5] = 0;
   out_1004515440907936276[6] = 0;
   out_1004515440907936276[7] = 0;
   out_1004515440907936276[8] = 0;
}
void h_28(double *state, double *unused, double *out_1038044542491554516) {
   out_1038044542491554516[0] = state[0];
}
void H_28(double *state, double *unused, double *out_8476240959145962426) {
   out_8476240959145962426[0] = 1;
   out_8476240959145962426[1] = 0;
   out_8476240959145962426[2] = 0;
   out_8476240959145962426[3] = 0;
   out_8476240959145962426[4] = 0;
   out_8476240959145962426[5] = 0;
   out_8476240959145962426[6] = 0;
   out_8476240959145962426[7] = 0;
   out_8476240959145962426[8] = 0;
}
void h_31(double *state, double *unused, double *out_3278125820992573365) {
   out_3278125820992573365[0] = state[8];
}
void H_31(double *state, double *unused, double *out_6391760283021112235) {
   out_6391760283021112235[0] = 0;
   out_6391760283021112235[1] = 0;
   out_6391760283021112235[2] = 0;
   out_6391760283021112235[3] = 0;
   out_6391760283021112235[4] = 0;
   out_6391760283021112235[5] = 0;
   out_6391760283021112235[6] = 0;
   out_6391760283021112235[7] = 0;
   out_6391760283021112235[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_1150556946497607115) {
  err_fun(nom_x, delta_x, out_1150556946497607115);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6384736535090160916) {
  inv_err_fun(nom_x, true_x, out_6384736535090160916);
}
void car_H_mod_fun(double *state, double *out_8501357178821987276) {
  H_mod_fun(state, out_8501357178821987276);
}
void car_f_fun(double *state, double dt, double *out_1001507699327886070) {
  f_fun(state,  dt, out_1001507699327886070);
}
void car_F_fun(double *state, double dt, double *out_679377826983824795) {
  F_fun(state,  dt, out_679377826983824795);
}
void car_h_25(double *state, double *unused, double *out_7405352995896305810) {
  h_25(state, unused, out_7405352995896305810);
}
void car_H_25(double *state, double *unused, double *out_6422406244898072663) {
  H_25(state, unused, out_6422406244898072663);
}
void car_h_24(double *state, double *unused, double *out_7209079107772895242) {
  h_24(state, unused, out_7209079107772895242);
}
void car_H_24(double *state, double *unused, double *out_2864480646095749527) {
  H_24(state, unused, out_2864480646095749527);
}
void car_h_30(double *state, double *unused, double *out_4074075913132213312) {
  h_30(state, unused, out_4074075913132213312);
}
void car_H_30(double *state, double *unused, double *out_494284096593544092) {
  H_30(state, unused, out_494284096593544092);
}
void car_h_26(double *state, double *unused, double *out_888304084549079920) {
  h_26(state, unused, out_888304084549079920);
}
void car_H_26(double *state, double *unused, double *out_8282834509937422729) {
  H_26(state, unused, out_8282834509937422729);
}
void car_h_27(double *state, double *unused, double *out_6039717810152400161) {
  h_27(state, unused, out_6039717810152400161);
}
void car_H_27(double *state, double *unused, double *out_1680479215206880819) {
  H_27(state, unused, out_1680479215206880819);
}
void car_h_29(double *state, double *unused, double *out_4946467499308263130) {
  h_29(state, unused, out_4946467499308263130);
}
void car_H_29(double *state, double *unused, double *out_1004515440907936276) {
  H_29(state, unused, out_1004515440907936276);
}
void car_h_28(double *state, double *unused, double *out_1038044542491554516) {
  h_28(state, unused, out_1038044542491554516);
}
void car_H_28(double *state, double *unused, double *out_8476240959145962426) {
  H_28(state, unused, out_8476240959145962426);
}
void car_h_31(double *state, double *unused, double *out_3278125820992573365) {
  h_31(state, unused, out_3278125820992573365);
}
void car_H_31(double *state, double *unused, double *out_6391760283021112235) {
  H_31(state, unused, out_6391760283021112235);
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
