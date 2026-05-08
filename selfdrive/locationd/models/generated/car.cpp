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
void err_fun(double *nom_x, double *delta_x, double *out_7995441131431557096) {
   out_7995441131431557096[0] = delta_x[0] + nom_x[0];
   out_7995441131431557096[1] = delta_x[1] + nom_x[1];
   out_7995441131431557096[2] = delta_x[2] + nom_x[2];
   out_7995441131431557096[3] = delta_x[3] + nom_x[3];
   out_7995441131431557096[4] = delta_x[4] + nom_x[4];
   out_7995441131431557096[5] = delta_x[5] + nom_x[5];
   out_7995441131431557096[6] = delta_x[6] + nom_x[6];
   out_7995441131431557096[7] = delta_x[7] + nom_x[7];
   out_7995441131431557096[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4650361766683635891) {
   out_4650361766683635891[0] = -nom_x[0] + true_x[0];
   out_4650361766683635891[1] = -nom_x[1] + true_x[1];
   out_4650361766683635891[2] = -nom_x[2] + true_x[2];
   out_4650361766683635891[3] = -nom_x[3] + true_x[3];
   out_4650361766683635891[4] = -nom_x[4] + true_x[4];
   out_4650361766683635891[5] = -nom_x[5] + true_x[5];
   out_4650361766683635891[6] = -nom_x[6] + true_x[6];
   out_4650361766683635891[7] = -nom_x[7] + true_x[7];
   out_4650361766683635891[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_6454279744481307781) {
   out_6454279744481307781[0] = 1.0;
   out_6454279744481307781[1] = 0.0;
   out_6454279744481307781[2] = 0.0;
   out_6454279744481307781[3] = 0.0;
   out_6454279744481307781[4] = 0.0;
   out_6454279744481307781[5] = 0.0;
   out_6454279744481307781[6] = 0.0;
   out_6454279744481307781[7] = 0.0;
   out_6454279744481307781[8] = 0.0;
   out_6454279744481307781[9] = 0.0;
   out_6454279744481307781[10] = 1.0;
   out_6454279744481307781[11] = 0.0;
   out_6454279744481307781[12] = 0.0;
   out_6454279744481307781[13] = 0.0;
   out_6454279744481307781[14] = 0.0;
   out_6454279744481307781[15] = 0.0;
   out_6454279744481307781[16] = 0.0;
   out_6454279744481307781[17] = 0.0;
   out_6454279744481307781[18] = 0.0;
   out_6454279744481307781[19] = 0.0;
   out_6454279744481307781[20] = 1.0;
   out_6454279744481307781[21] = 0.0;
   out_6454279744481307781[22] = 0.0;
   out_6454279744481307781[23] = 0.0;
   out_6454279744481307781[24] = 0.0;
   out_6454279744481307781[25] = 0.0;
   out_6454279744481307781[26] = 0.0;
   out_6454279744481307781[27] = 0.0;
   out_6454279744481307781[28] = 0.0;
   out_6454279744481307781[29] = 0.0;
   out_6454279744481307781[30] = 1.0;
   out_6454279744481307781[31] = 0.0;
   out_6454279744481307781[32] = 0.0;
   out_6454279744481307781[33] = 0.0;
   out_6454279744481307781[34] = 0.0;
   out_6454279744481307781[35] = 0.0;
   out_6454279744481307781[36] = 0.0;
   out_6454279744481307781[37] = 0.0;
   out_6454279744481307781[38] = 0.0;
   out_6454279744481307781[39] = 0.0;
   out_6454279744481307781[40] = 1.0;
   out_6454279744481307781[41] = 0.0;
   out_6454279744481307781[42] = 0.0;
   out_6454279744481307781[43] = 0.0;
   out_6454279744481307781[44] = 0.0;
   out_6454279744481307781[45] = 0.0;
   out_6454279744481307781[46] = 0.0;
   out_6454279744481307781[47] = 0.0;
   out_6454279744481307781[48] = 0.0;
   out_6454279744481307781[49] = 0.0;
   out_6454279744481307781[50] = 1.0;
   out_6454279744481307781[51] = 0.0;
   out_6454279744481307781[52] = 0.0;
   out_6454279744481307781[53] = 0.0;
   out_6454279744481307781[54] = 0.0;
   out_6454279744481307781[55] = 0.0;
   out_6454279744481307781[56] = 0.0;
   out_6454279744481307781[57] = 0.0;
   out_6454279744481307781[58] = 0.0;
   out_6454279744481307781[59] = 0.0;
   out_6454279744481307781[60] = 1.0;
   out_6454279744481307781[61] = 0.0;
   out_6454279744481307781[62] = 0.0;
   out_6454279744481307781[63] = 0.0;
   out_6454279744481307781[64] = 0.0;
   out_6454279744481307781[65] = 0.0;
   out_6454279744481307781[66] = 0.0;
   out_6454279744481307781[67] = 0.0;
   out_6454279744481307781[68] = 0.0;
   out_6454279744481307781[69] = 0.0;
   out_6454279744481307781[70] = 1.0;
   out_6454279744481307781[71] = 0.0;
   out_6454279744481307781[72] = 0.0;
   out_6454279744481307781[73] = 0.0;
   out_6454279744481307781[74] = 0.0;
   out_6454279744481307781[75] = 0.0;
   out_6454279744481307781[76] = 0.0;
   out_6454279744481307781[77] = 0.0;
   out_6454279744481307781[78] = 0.0;
   out_6454279744481307781[79] = 0.0;
   out_6454279744481307781[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_1057486056378825346) {
   out_1057486056378825346[0] = state[0];
   out_1057486056378825346[1] = state[1];
   out_1057486056378825346[2] = state[2];
   out_1057486056378825346[3] = state[3];
   out_1057486056378825346[4] = state[4];
   out_1057486056378825346[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_1057486056378825346[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_1057486056378825346[7] = state[7];
   out_1057486056378825346[8] = state[8];
}
void F_fun(double *state, double dt, double *out_2762244256179971899) {
   out_2762244256179971899[0] = 1;
   out_2762244256179971899[1] = 0;
   out_2762244256179971899[2] = 0;
   out_2762244256179971899[3] = 0;
   out_2762244256179971899[4] = 0;
   out_2762244256179971899[5] = 0;
   out_2762244256179971899[6] = 0;
   out_2762244256179971899[7] = 0;
   out_2762244256179971899[8] = 0;
   out_2762244256179971899[9] = 0;
   out_2762244256179971899[10] = 1;
   out_2762244256179971899[11] = 0;
   out_2762244256179971899[12] = 0;
   out_2762244256179971899[13] = 0;
   out_2762244256179971899[14] = 0;
   out_2762244256179971899[15] = 0;
   out_2762244256179971899[16] = 0;
   out_2762244256179971899[17] = 0;
   out_2762244256179971899[18] = 0;
   out_2762244256179971899[19] = 0;
   out_2762244256179971899[20] = 1;
   out_2762244256179971899[21] = 0;
   out_2762244256179971899[22] = 0;
   out_2762244256179971899[23] = 0;
   out_2762244256179971899[24] = 0;
   out_2762244256179971899[25] = 0;
   out_2762244256179971899[26] = 0;
   out_2762244256179971899[27] = 0;
   out_2762244256179971899[28] = 0;
   out_2762244256179971899[29] = 0;
   out_2762244256179971899[30] = 1;
   out_2762244256179971899[31] = 0;
   out_2762244256179971899[32] = 0;
   out_2762244256179971899[33] = 0;
   out_2762244256179971899[34] = 0;
   out_2762244256179971899[35] = 0;
   out_2762244256179971899[36] = 0;
   out_2762244256179971899[37] = 0;
   out_2762244256179971899[38] = 0;
   out_2762244256179971899[39] = 0;
   out_2762244256179971899[40] = 1;
   out_2762244256179971899[41] = 0;
   out_2762244256179971899[42] = 0;
   out_2762244256179971899[43] = 0;
   out_2762244256179971899[44] = 0;
   out_2762244256179971899[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_2762244256179971899[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_2762244256179971899[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2762244256179971899[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2762244256179971899[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_2762244256179971899[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_2762244256179971899[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_2762244256179971899[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_2762244256179971899[53] = -9.8100000000000005*dt;
   out_2762244256179971899[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_2762244256179971899[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_2762244256179971899[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2762244256179971899[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2762244256179971899[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_2762244256179971899[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_2762244256179971899[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_2762244256179971899[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2762244256179971899[62] = 0;
   out_2762244256179971899[63] = 0;
   out_2762244256179971899[64] = 0;
   out_2762244256179971899[65] = 0;
   out_2762244256179971899[66] = 0;
   out_2762244256179971899[67] = 0;
   out_2762244256179971899[68] = 0;
   out_2762244256179971899[69] = 0;
   out_2762244256179971899[70] = 1;
   out_2762244256179971899[71] = 0;
   out_2762244256179971899[72] = 0;
   out_2762244256179971899[73] = 0;
   out_2762244256179971899[74] = 0;
   out_2762244256179971899[75] = 0;
   out_2762244256179971899[76] = 0;
   out_2762244256179971899[77] = 0;
   out_2762244256179971899[78] = 0;
   out_2762244256179971899[79] = 0;
   out_2762244256179971899[80] = 1;
}
void h_25(double *state, double *unused, double *out_1163064920451275624) {
   out_1163064920451275624[0] = state[6];
}
void H_25(double *state, double *unused, double *out_8601438681758688193) {
   out_8601438681758688193[0] = 0;
   out_8601438681758688193[1] = 0;
   out_8601438681758688193[2] = 0;
   out_8601438681758688193[3] = 0;
   out_8601438681758688193[4] = 0;
   out_8601438681758688193[5] = 0;
   out_8601438681758688193[6] = 1;
   out_8601438681758688193[7] = 0;
   out_8601438681758688193[8] = 0;
}
void h_24(double *state, double *unused, double *out_2922764778379292944) {
   out_2922764778379292944[0] = state[4];
   out_2922764778379292944[1] = state[5];
}
void H_24(double *state, double *unused, double *out_5024983887294875160) {
   out_5024983887294875160[0] = 0;
   out_5024983887294875160[1] = 0;
   out_5024983887294875160[2] = 0;
   out_5024983887294875160[3] = 0;
   out_5024983887294875160[4] = 1;
   out_5024983887294875160[5] = 0;
   out_5024983887294875160[6] = 0;
   out_5024983887294875160[7] = 0;
   out_5024983887294875160[8] = 0;
   out_5024983887294875160[9] = 0;
   out_5024983887294875160[10] = 0;
   out_5024983887294875160[11] = 0;
   out_5024983887294875160[12] = 0;
   out_5024983887294875160[13] = 0;
   out_5024983887294875160[14] = 1;
   out_5024983887294875160[15] = 0;
   out_5024983887294875160[16] = 0;
   out_5024983887294875160[17] = 0;
}
void h_30(double *state, double *unused, double *out_7933900146801626560) {
   out_7933900146801626560[0] = state[4];
}
void H_30(double *state, double *unused, double *out_8730777628901928263) {
   out_8730777628901928263[0] = 0;
   out_8730777628901928263[1] = 0;
   out_8730777628901928263[2] = 0;
   out_8730777628901928263[3] = 0;
   out_8730777628901928263[4] = 1;
   out_8730777628901928263[5] = 0;
   out_8730777628901928263[6] = 0;
   out_8730777628901928263[7] = 0;
   out_8730777628901928263[8] = 0;
}
void h_26(double *state, double *unused, double *out_5511170659247079411) {
   out_5511170659247079411[0] = state[7];
}
void H_26(double *state, double *unused, double *out_6103802073076807199) {
   out_6103802073076807199[0] = 0;
   out_6103802073076807199[1] = 0;
   out_6103802073076807199[2] = 0;
   out_6103802073076807199[3] = 0;
   out_6103802073076807199[4] = 0;
   out_6103802073076807199[5] = 0;
   out_6103802073076807199[6] = 0;
   out_6103802073076807199[7] = 1;
   out_6103802073076807199[8] = 0;
}
void h_27(double *state, double *unused, double *out_559749035774798107) {
   out_559749035774798107[0] = state[3];
}
void H_27(double *state, double *unused, double *out_7541203133007198442) {
   out_7541203133007198442[0] = 0;
   out_7541203133007198442[1] = 0;
   out_7541203133007198442[2] = 0;
   out_7541203133007198442[3] = 1;
   out_7541203133007198442[4] = 0;
   out_7541203133007198442[5] = 0;
   out_7541203133007198442[6] = 0;
   out_7541203133007198442[7] = 0;
   out_7541203133007198442[8] = 0;
}
void h_29(double *state, double *unused, double *out_4658052334054169971) {
   out_4658052334054169971[0] = state[1];
}
void H_29(double *state, double *unused, double *out_8220546284587536079) {
   out_8220546284587536079[0] = 0;
   out_8220546284587536079[1] = 1;
   out_8220546284587536079[2] = 0;
   out_8220546284587536079[3] = 0;
   out_8220546284587536079[4] = 0;
   out_8220546284587536079[5] = 0;
   out_8220546284587536079[6] = 0;
   out_8220546284587536079[7] = 0;
   out_8220546284587536079[8] = 0;
}
void h_28(double *state, double *unused, double *out_1503258888676460542) {
   out_1503258888676460542[0] = state[0];
}
void H_28(double *state, double *unused, double *out_5143798772052484963) {
   out_5143798772052484963[0] = 1;
   out_5143798772052484963[1] = 0;
   out_5143798772052484963[2] = 0;
   out_5143798772052484963[3] = 0;
   out_5143798772052484963[4] = 0;
   out_5143798772052484963[5] = 0;
   out_5143798772052484963[6] = 0;
   out_5143798772052484963[7] = 0;
   out_5143798772052484963[8] = 0;
}
void h_31(double *state, double *unused, double *out_6600200336369396817) {
   out_6600200336369396817[0] = state[8];
}
void H_31(double *state, double *unused, double *out_8570792719881727765) {
   out_8570792719881727765[0] = 0;
   out_8570792719881727765[1] = 0;
   out_8570792719881727765[2] = 0;
   out_8570792719881727765[3] = 0;
   out_8570792719881727765[4] = 0;
   out_8570792719881727765[5] = 0;
   out_8570792719881727765[6] = 0;
   out_8570792719881727765[7] = 0;
   out_8570792719881727765[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_7995441131431557096) {
  err_fun(nom_x, delta_x, out_7995441131431557096);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4650361766683635891) {
  inv_err_fun(nom_x, true_x, out_4650361766683635891);
}
void car_H_mod_fun(double *state, double *out_6454279744481307781) {
  H_mod_fun(state, out_6454279744481307781);
}
void car_f_fun(double *state, double dt, double *out_1057486056378825346) {
  f_fun(state,  dt, out_1057486056378825346);
}
void car_F_fun(double *state, double dt, double *out_2762244256179971899) {
  F_fun(state,  dt, out_2762244256179971899);
}
void car_h_25(double *state, double *unused, double *out_1163064920451275624) {
  h_25(state, unused, out_1163064920451275624);
}
void car_H_25(double *state, double *unused, double *out_8601438681758688193) {
  H_25(state, unused, out_8601438681758688193);
}
void car_h_24(double *state, double *unused, double *out_2922764778379292944) {
  h_24(state, unused, out_2922764778379292944);
}
void car_H_24(double *state, double *unused, double *out_5024983887294875160) {
  H_24(state, unused, out_5024983887294875160);
}
void car_h_30(double *state, double *unused, double *out_7933900146801626560) {
  h_30(state, unused, out_7933900146801626560);
}
void car_H_30(double *state, double *unused, double *out_8730777628901928263) {
  H_30(state, unused, out_8730777628901928263);
}
void car_h_26(double *state, double *unused, double *out_5511170659247079411) {
  h_26(state, unused, out_5511170659247079411);
}
void car_H_26(double *state, double *unused, double *out_6103802073076807199) {
  H_26(state, unused, out_6103802073076807199);
}
void car_h_27(double *state, double *unused, double *out_559749035774798107) {
  h_27(state, unused, out_559749035774798107);
}
void car_H_27(double *state, double *unused, double *out_7541203133007198442) {
  H_27(state, unused, out_7541203133007198442);
}
void car_h_29(double *state, double *unused, double *out_4658052334054169971) {
  h_29(state, unused, out_4658052334054169971);
}
void car_H_29(double *state, double *unused, double *out_8220546284587536079) {
  H_29(state, unused, out_8220546284587536079);
}
void car_h_28(double *state, double *unused, double *out_1503258888676460542) {
  h_28(state, unused, out_1503258888676460542);
}
void car_H_28(double *state, double *unused, double *out_5143798772052484963) {
  H_28(state, unused, out_5143798772052484963);
}
void car_h_31(double *state, double *unused, double *out_6600200336369396817) {
  h_31(state, unused, out_6600200336369396817);
}
void car_H_31(double *state, double *unused, double *out_8570792719881727765) {
  H_31(state, unused, out_8570792719881727765);
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
