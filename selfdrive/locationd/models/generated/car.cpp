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
void err_fun(double *nom_x, double *delta_x, double *out_2240929505196870859) {
   out_2240929505196870859[0] = delta_x[0] + nom_x[0];
   out_2240929505196870859[1] = delta_x[1] + nom_x[1];
   out_2240929505196870859[2] = delta_x[2] + nom_x[2];
   out_2240929505196870859[3] = delta_x[3] + nom_x[3];
   out_2240929505196870859[4] = delta_x[4] + nom_x[4];
   out_2240929505196870859[5] = delta_x[5] + nom_x[5];
   out_2240929505196870859[6] = delta_x[6] + nom_x[6];
   out_2240929505196870859[7] = delta_x[7] + nom_x[7];
   out_2240929505196870859[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6399928478461651909) {
   out_6399928478461651909[0] = -nom_x[0] + true_x[0];
   out_6399928478461651909[1] = -nom_x[1] + true_x[1];
   out_6399928478461651909[2] = -nom_x[2] + true_x[2];
   out_6399928478461651909[3] = -nom_x[3] + true_x[3];
   out_6399928478461651909[4] = -nom_x[4] + true_x[4];
   out_6399928478461651909[5] = -nom_x[5] + true_x[5];
   out_6399928478461651909[6] = -nom_x[6] + true_x[6];
   out_6399928478461651909[7] = -nom_x[7] + true_x[7];
   out_6399928478461651909[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_1595360535879665735) {
   out_1595360535879665735[0] = 1.0;
   out_1595360535879665735[1] = 0.0;
   out_1595360535879665735[2] = 0.0;
   out_1595360535879665735[3] = 0.0;
   out_1595360535879665735[4] = 0.0;
   out_1595360535879665735[5] = 0.0;
   out_1595360535879665735[6] = 0.0;
   out_1595360535879665735[7] = 0.0;
   out_1595360535879665735[8] = 0.0;
   out_1595360535879665735[9] = 0.0;
   out_1595360535879665735[10] = 1.0;
   out_1595360535879665735[11] = 0.0;
   out_1595360535879665735[12] = 0.0;
   out_1595360535879665735[13] = 0.0;
   out_1595360535879665735[14] = 0.0;
   out_1595360535879665735[15] = 0.0;
   out_1595360535879665735[16] = 0.0;
   out_1595360535879665735[17] = 0.0;
   out_1595360535879665735[18] = 0.0;
   out_1595360535879665735[19] = 0.0;
   out_1595360535879665735[20] = 1.0;
   out_1595360535879665735[21] = 0.0;
   out_1595360535879665735[22] = 0.0;
   out_1595360535879665735[23] = 0.0;
   out_1595360535879665735[24] = 0.0;
   out_1595360535879665735[25] = 0.0;
   out_1595360535879665735[26] = 0.0;
   out_1595360535879665735[27] = 0.0;
   out_1595360535879665735[28] = 0.0;
   out_1595360535879665735[29] = 0.0;
   out_1595360535879665735[30] = 1.0;
   out_1595360535879665735[31] = 0.0;
   out_1595360535879665735[32] = 0.0;
   out_1595360535879665735[33] = 0.0;
   out_1595360535879665735[34] = 0.0;
   out_1595360535879665735[35] = 0.0;
   out_1595360535879665735[36] = 0.0;
   out_1595360535879665735[37] = 0.0;
   out_1595360535879665735[38] = 0.0;
   out_1595360535879665735[39] = 0.0;
   out_1595360535879665735[40] = 1.0;
   out_1595360535879665735[41] = 0.0;
   out_1595360535879665735[42] = 0.0;
   out_1595360535879665735[43] = 0.0;
   out_1595360535879665735[44] = 0.0;
   out_1595360535879665735[45] = 0.0;
   out_1595360535879665735[46] = 0.0;
   out_1595360535879665735[47] = 0.0;
   out_1595360535879665735[48] = 0.0;
   out_1595360535879665735[49] = 0.0;
   out_1595360535879665735[50] = 1.0;
   out_1595360535879665735[51] = 0.0;
   out_1595360535879665735[52] = 0.0;
   out_1595360535879665735[53] = 0.0;
   out_1595360535879665735[54] = 0.0;
   out_1595360535879665735[55] = 0.0;
   out_1595360535879665735[56] = 0.0;
   out_1595360535879665735[57] = 0.0;
   out_1595360535879665735[58] = 0.0;
   out_1595360535879665735[59] = 0.0;
   out_1595360535879665735[60] = 1.0;
   out_1595360535879665735[61] = 0.0;
   out_1595360535879665735[62] = 0.0;
   out_1595360535879665735[63] = 0.0;
   out_1595360535879665735[64] = 0.0;
   out_1595360535879665735[65] = 0.0;
   out_1595360535879665735[66] = 0.0;
   out_1595360535879665735[67] = 0.0;
   out_1595360535879665735[68] = 0.0;
   out_1595360535879665735[69] = 0.0;
   out_1595360535879665735[70] = 1.0;
   out_1595360535879665735[71] = 0.0;
   out_1595360535879665735[72] = 0.0;
   out_1595360535879665735[73] = 0.0;
   out_1595360535879665735[74] = 0.0;
   out_1595360535879665735[75] = 0.0;
   out_1595360535879665735[76] = 0.0;
   out_1595360535879665735[77] = 0.0;
   out_1595360535879665735[78] = 0.0;
   out_1595360535879665735[79] = 0.0;
   out_1595360535879665735[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_8997069209869168713) {
   out_8997069209869168713[0] = state[0];
   out_8997069209869168713[1] = state[1];
   out_8997069209869168713[2] = state[2];
   out_8997069209869168713[3] = state[3];
   out_8997069209869168713[4] = state[4];
   out_8997069209869168713[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_8997069209869168713[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_8997069209869168713[7] = state[7];
   out_8997069209869168713[8] = state[8];
}
void F_fun(double *state, double dt, double *out_7229959409724562911) {
   out_7229959409724562911[0] = 1;
   out_7229959409724562911[1] = 0;
   out_7229959409724562911[2] = 0;
   out_7229959409724562911[3] = 0;
   out_7229959409724562911[4] = 0;
   out_7229959409724562911[5] = 0;
   out_7229959409724562911[6] = 0;
   out_7229959409724562911[7] = 0;
   out_7229959409724562911[8] = 0;
   out_7229959409724562911[9] = 0;
   out_7229959409724562911[10] = 1;
   out_7229959409724562911[11] = 0;
   out_7229959409724562911[12] = 0;
   out_7229959409724562911[13] = 0;
   out_7229959409724562911[14] = 0;
   out_7229959409724562911[15] = 0;
   out_7229959409724562911[16] = 0;
   out_7229959409724562911[17] = 0;
   out_7229959409724562911[18] = 0;
   out_7229959409724562911[19] = 0;
   out_7229959409724562911[20] = 1;
   out_7229959409724562911[21] = 0;
   out_7229959409724562911[22] = 0;
   out_7229959409724562911[23] = 0;
   out_7229959409724562911[24] = 0;
   out_7229959409724562911[25] = 0;
   out_7229959409724562911[26] = 0;
   out_7229959409724562911[27] = 0;
   out_7229959409724562911[28] = 0;
   out_7229959409724562911[29] = 0;
   out_7229959409724562911[30] = 1;
   out_7229959409724562911[31] = 0;
   out_7229959409724562911[32] = 0;
   out_7229959409724562911[33] = 0;
   out_7229959409724562911[34] = 0;
   out_7229959409724562911[35] = 0;
   out_7229959409724562911[36] = 0;
   out_7229959409724562911[37] = 0;
   out_7229959409724562911[38] = 0;
   out_7229959409724562911[39] = 0;
   out_7229959409724562911[40] = 1;
   out_7229959409724562911[41] = 0;
   out_7229959409724562911[42] = 0;
   out_7229959409724562911[43] = 0;
   out_7229959409724562911[44] = 0;
   out_7229959409724562911[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_7229959409724562911[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_7229959409724562911[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7229959409724562911[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7229959409724562911[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_7229959409724562911[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_7229959409724562911[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_7229959409724562911[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_7229959409724562911[53] = -9.8100000000000005*dt;
   out_7229959409724562911[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_7229959409724562911[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_7229959409724562911[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7229959409724562911[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7229959409724562911[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_7229959409724562911[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_7229959409724562911[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_7229959409724562911[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7229959409724562911[62] = 0;
   out_7229959409724562911[63] = 0;
   out_7229959409724562911[64] = 0;
   out_7229959409724562911[65] = 0;
   out_7229959409724562911[66] = 0;
   out_7229959409724562911[67] = 0;
   out_7229959409724562911[68] = 0;
   out_7229959409724562911[69] = 0;
   out_7229959409724562911[70] = 1;
   out_7229959409724562911[71] = 0;
   out_7229959409724562911[72] = 0;
   out_7229959409724562911[73] = 0;
   out_7229959409724562911[74] = 0;
   out_7229959409724562911[75] = 0;
   out_7229959409724562911[76] = 0;
   out_7229959409724562911[77] = 0;
   out_7229959409724562911[78] = 0;
   out_7229959409724562911[79] = 0;
   out_7229959409724562911[80] = 1;
}
void h_25(double *state, double *unused, double *out_2914933031606639147) {
   out_2914933031606639147[0] = state[6];
}
void H_25(double *state, double *unused, double *out_6325977497094194070) {
   out_6325977497094194070[0] = 0;
   out_6325977497094194070[1] = 0;
   out_6325977497094194070[2] = 0;
   out_6325977497094194070[3] = 0;
   out_6325977497094194070[4] = 0;
   out_6325977497094194070[5] = 0;
   out_6325977497094194070[6] = 1;
   out_6325977497094194070[7] = 0;
   out_6325977497094194070[8] = 0;
}
void h_24(double *state, double *unused, double *out_3259994416654587251) {
   out_3259994416654587251[0] = state[4];
   out_3259994416654587251[1] = state[5];
}
void H_24(double *state, double *unused, double *out_4153327898088694504) {
   out_4153327898088694504[0] = 0;
   out_4153327898088694504[1] = 0;
   out_4153327898088694504[2] = 0;
   out_4153327898088694504[3] = 0;
   out_4153327898088694504[4] = 1;
   out_4153327898088694504[5] = 0;
   out_4153327898088694504[6] = 0;
   out_4153327898088694504[7] = 0;
   out_4153327898088694504[8] = 0;
   out_4153327898088694504[9] = 0;
   out_4153327898088694504[10] = 0;
   out_4153327898088694504[11] = 0;
   out_4153327898088694504[12] = 0;
   out_4153327898088694504[13] = 0;
   out_4153327898088694504[14] = 1;
   out_4153327898088694504[15] = 0;
   out_4153327898088694504[16] = 0;
   out_4153327898088694504[17] = 0;
}
void h_30(double *state, double *unused, double *out_967176657284623868) {
   out_967176657284623868[0] = state[4];
}
void H_30(double *state, double *unused, double *out_8844310455601442697) {
   out_8844310455601442697[0] = 0;
   out_8844310455601442697[1] = 0;
   out_8844310455601442697[2] = 0;
   out_8844310455601442697[3] = 0;
   out_8844310455601442697[4] = 1;
   out_8844310455601442697[5] = 0;
   out_8844310455601442697[6] = 0;
   out_8844310455601442697[7] = 0;
   out_8844310455601442697[8] = 0;
}
void h_26(double *state, double *unused, double *out_5279274400175549600) {
   out_5279274400175549600[0] = state[7];
}
void H_26(double *state, double *unused, double *out_2584474178220137846) {
   out_2584474178220137846[0] = 0;
   out_2584474178220137846[1] = 0;
   out_2584474178220137846[2] = 0;
   out_2584474178220137846[3] = 0;
   out_2584474178220137846[4] = 0;
   out_2584474178220137846[5] = 0;
   out_2584474178220137846[6] = 0;
   out_2584474178220137846[7] = 1;
   out_2584474178220137846[8] = 0;
}
void h_27(double *state, double *unused, double *out_762909623257804728) {
   out_762909623257804728[0] = state[3];
}
void H_27(double *state, double *unused, double *out_6669547143801017786) {
   out_6669547143801017786[0] = 0;
   out_6669547143801017786[1] = 0;
   out_6669547143801017786[2] = 0;
   out_6669547143801017786[3] = 1;
   out_6669547143801017786[4] = 0;
   out_6669547143801017786[5] = 0;
   out_6669547143801017786[6] = 0;
   out_6669547143801017786[7] = 0;
   out_6669547143801017786[8] = 0;
}
void h_29(double *state, double *unused, double *out_23666804382961433) {
   out_23666804382961433[0] = state[1];
}
void H_29(double *state, double *unused, double *out_9092202273793716735) {
   out_9092202273793716735[0] = 0;
   out_9092202273793716735[1] = 1;
   out_9092202273793716735[2] = 0;
   out_9092202273793716735[3] = 0;
   out_9092202273793716735[4] = 0;
   out_9092202273793716735[5] = 0;
   out_9092202273793716735[6] = 0;
   out_9092202273793716735[7] = 0;
   out_9092202273793716735[8] = 0;
}
void h_28(double *state, double *unused, double *out_4879820247823152107) {
   out_4879820247823152107[0] = state[0];
}
void H_28(double *state, double *unused, double *out_4272142782846304307) {
   out_4272142782846304307[0] = 1;
   out_4272142782846304307[1] = 0;
   out_4272142782846304307[2] = 0;
   out_4272142782846304307[3] = 0;
   out_4272142782846304307[4] = 0;
   out_4272142782846304307[5] = 0;
   out_4272142782846304307[6] = 0;
   out_4272142782846304307[7] = 0;
   out_4272142782846304307[8] = 0;
}
void h_31(double *state, double *unused, double *out_1998682365902022068) {
   out_1998682365902022068[0] = state[8];
}
void H_31(double *state, double *unused, double *out_1958266075986786370) {
   out_1958266075986786370[0] = 0;
   out_1958266075986786370[1] = 0;
   out_1958266075986786370[2] = 0;
   out_1958266075986786370[3] = 0;
   out_1958266075986786370[4] = 0;
   out_1958266075986786370[5] = 0;
   out_1958266075986786370[6] = 0;
   out_1958266075986786370[7] = 0;
   out_1958266075986786370[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_2240929505196870859) {
  err_fun(nom_x, delta_x, out_2240929505196870859);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6399928478461651909) {
  inv_err_fun(nom_x, true_x, out_6399928478461651909);
}
void car_H_mod_fun(double *state, double *out_1595360535879665735) {
  H_mod_fun(state, out_1595360535879665735);
}
void car_f_fun(double *state, double dt, double *out_8997069209869168713) {
  f_fun(state,  dt, out_8997069209869168713);
}
void car_F_fun(double *state, double dt, double *out_7229959409724562911) {
  F_fun(state,  dt, out_7229959409724562911);
}
void car_h_25(double *state, double *unused, double *out_2914933031606639147) {
  h_25(state, unused, out_2914933031606639147);
}
void car_H_25(double *state, double *unused, double *out_6325977497094194070) {
  H_25(state, unused, out_6325977497094194070);
}
void car_h_24(double *state, double *unused, double *out_3259994416654587251) {
  h_24(state, unused, out_3259994416654587251);
}
void car_H_24(double *state, double *unused, double *out_4153327898088694504) {
  H_24(state, unused, out_4153327898088694504);
}
void car_h_30(double *state, double *unused, double *out_967176657284623868) {
  h_30(state, unused, out_967176657284623868);
}
void car_H_30(double *state, double *unused, double *out_8844310455601442697) {
  H_30(state, unused, out_8844310455601442697);
}
void car_h_26(double *state, double *unused, double *out_5279274400175549600) {
  h_26(state, unused, out_5279274400175549600);
}
void car_H_26(double *state, double *unused, double *out_2584474178220137846) {
  H_26(state, unused, out_2584474178220137846);
}
void car_h_27(double *state, double *unused, double *out_762909623257804728) {
  h_27(state, unused, out_762909623257804728);
}
void car_H_27(double *state, double *unused, double *out_6669547143801017786) {
  H_27(state, unused, out_6669547143801017786);
}
void car_h_29(double *state, double *unused, double *out_23666804382961433) {
  h_29(state, unused, out_23666804382961433);
}
void car_H_29(double *state, double *unused, double *out_9092202273793716735) {
  H_29(state, unused, out_9092202273793716735);
}
void car_h_28(double *state, double *unused, double *out_4879820247823152107) {
  h_28(state, unused, out_4879820247823152107);
}
void car_H_28(double *state, double *unused, double *out_4272142782846304307) {
  H_28(state, unused, out_4272142782846304307);
}
void car_h_31(double *state, double *unused, double *out_1998682365902022068) {
  h_31(state, unused, out_1998682365902022068);
}
void car_H_31(double *state, double *unused, double *out_1958266075986786370) {
  H_31(state, unused, out_1958266075986786370);
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
