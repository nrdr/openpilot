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
void err_fun(double *nom_x, double *delta_x, double *out_760253992355356602) {
   out_760253992355356602[0] = delta_x[0] + nom_x[0];
   out_760253992355356602[1] = delta_x[1] + nom_x[1];
   out_760253992355356602[2] = delta_x[2] + nom_x[2];
   out_760253992355356602[3] = delta_x[3] + nom_x[3];
   out_760253992355356602[4] = delta_x[4] + nom_x[4];
   out_760253992355356602[5] = delta_x[5] + nom_x[5];
   out_760253992355356602[6] = delta_x[6] + nom_x[6];
   out_760253992355356602[7] = delta_x[7] + nom_x[7];
   out_760253992355356602[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4983548601721046404) {
   out_4983548601721046404[0] = -nom_x[0] + true_x[0];
   out_4983548601721046404[1] = -nom_x[1] + true_x[1];
   out_4983548601721046404[2] = -nom_x[2] + true_x[2];
   out_4983548601721046404[3] = -nom_x[3] + true_x[3];
   out_4983548601721046404[4] = -nom_x[4] + true_x[4];
   out_4983548601721046404[5] = -nom_x[5] + true_x[5];
   out_4983548601721046404[6] = -nom_x[6] + true_x[6];
   out_4983548601721046404[7] = -nom_x[7] + true_x[7];
   out_4983548601721046404[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_8995833010704521871) {
   out_8995833010704521871[0] = 1.0;
   out_8995833010704521871[1] = 0.0;
   out_8995833010704521871[2] = 0.0;
   out_8995833010704521871[3] = 0.0;
   out_8995833010704521871[4] = 0.0;
   out_8995833010704521871[5] = 0.0;
   out_8995833010704521871[6] = 0.0;
   out_8995833010704521871[7] = 0.0;
   out_8995833010704521871[8] = 0.0;
   out_8995833010704521871[9] = 0.0;
   out_8995833010704521871[10] = 1.0;
   out_8995833010704521871[11] = 0.0;
   out_8995833010704521871[12] = 0.0;
   out_8995833010704521871[13] = 0.0;
   out_8995833010704521871[14] = 0.0;
   out_8995833010704521871[15] = 0.0;
   out_8995833010704521871[16] = 0.0;
   out_8995833010704521871[17] = 0.0;
   out_8995833010704521871[18] = 0.0;
   out_8995833010704521871[19] = 0.0;
   out_8995833010704521871[20] = 1.0;
   out_8995833010704521871[21] = 0.0;
   out_8995833010704521871[22] = 0.0;
   out_8995833010704521871[23] = 0.0;
   out_8995833010704521871[24] = 0.0;
   out_8995833010704521871[25] = 0.0;
   out_8995833010704521871[26] = 0.0;
   out_8995833010704521871[27] = 0.0;
   out_8995833010704521871[28] = 0.0;
   out_8995833010704521871[29] = 0.0;
   out_8995833010704521871[30] = 1.0;
   out_8995833010704521871[31] = 0.0;
   out_8995833010704521871[32] = 0.0;
   out_8995833010704521871[33] = 0.0;
   out_8995833010704521871[34] = 0.0;
   out_8995833010704521871[35] = 0.0;
   out_8995833010704521871[36] = 0.0;
   out_8995833010704521871[37] = 0.0;
   out_8995833010704521871[38] = 0.0;
   out_8995833010704521871[39] = 0.0;
   out_8995833010704521871[40] = 1.0;
   out_8995833010704521871[41] = 0.0;
   out_8995833010704521871[42] = 0.0;
   out_8995833010704521871[43] = 0.0;
   out_8995833010704521871[44] = 0.0;
   out_8995833010704521871[45] = 0.0;
   out_8995833010704521871[46] = 0.0;
   out_8995833010704521871[47] = 0.0;
   out_8995833010704521871[48] = 0.0;
   out_8995833010704521871[49] = 0.0;
   out_8995833010704521871[50] = 1.0;
   out_8995833010704521871[51] = 0.0;
   out_8995833010704521871[52] = 0.0;
   out_8995833010704521871[53] = 0.0;
   out_8995833010704521871[54] = 0.0;
   out_8995833010704521871[55] = 0.0;
   out_8995833010704521871[56] = 0.0;
   out_8995833010704521871[57] = 0.0;
   out_8995833010704521871[58] = 0.0;
   out_8995833010704521871[59] = 0.0;
   out_8995833010704521871[60] = 1.0;
   out_8995833010704521871[61] = 0.0;
   out_8995833010704521871[62] = 0.0;
   out_8995833010704521871[63] = 0.0;
   out_8995833010704521871[64] = 0.0;
   out_8995833010704521871[65] = 0.0;
   out_8995833010704521871[66] = 0.0;
   out_8995833010704521871[67] = 0.0;
   out_8995833010704521871[68] = 0.0;
   out_8995833010704521871[69] = 0.0;
   out_8995833010704521871[70] = 1.0;
   out_8995833010704521871[71] = 0.0;
   out_8995833010704521871[72] = 0.0;
   out_8995833010704521871[73] = 0.0;
   out_8995833010704521871[74] = 0.0;
   out_8995833010704521871[75] = 0.0;
   out_8995833010704521871[76] = 0.0;
   out_8995833010704521871[77] = 0.0;
   out_8995833010704521871[78] = 0.0;
   out_8995833010704521871[79] = 0.0;
   out_8995833010704521871[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_4562655195590537984) {
   out_4562655195590537984[0] = state[0];
   out_4562655195590537984[1] = state[1];
   out_4562655195590537984[2] = state[2];
   out_4562655195590537984[3] = state[3];
   out_4562655195590537984[4] = state[4];
   out_4562655195590537984[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_4562655195590537984[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_4562655195590537984[7] = state[7];
   out_4562655195590537984[8] = state[8];
}
void F_fun(double *state, double dt, double *out_6423431565507769528) {
   out_6423431565507769528[0] = 1;
   out_6423431565507769528[1] = 0;
   out_6423431565507769528[2] = 0;
   out_6423431565507769528[3] = 0;
   out_6423431565507769528[4] = 0;
   out_6423431565507769528[5] = 0;
   out_6423431565507769528[6] = 0;
   out_6423431565507769528[7] = 0;
   out_6423431565507769528[8] = 0;
   out_6423431565507769528[9] = 0;
   out_6423431565507769528[10] = 1;
   out_6423431565507769528[11] = 0;
   out_6423431565507769528[12] = 0;
   out_6423431565507769528[13] = 0;
   out_6423431565507769528[14] = 0;
   out_6423431565507769528[15] = 0;
   out_6423431565507769528[16] = 0;
   out_6423431565507769528[17] = 0;
   out_6423431565507769528[18] = 0;
   out_6423431565507769528[19] = 0;
   out_6423431565507769528[20] = 1;
   out_6423431565507769528[21] = 0;
   out_6423431565507769528[22] = 0;
   out_6423431565507769528[23] = 0;
   out_6423431565507769528[24] = 0;
   out_6423431565507769528[25] = 0;
   out_6423431565507769528[26] = 0;
   out_6423431565507769528[27] = 0;
   out_6423431565507769528[28] = 0;
   out_6423431565507769528[29] = 0;
   out_6423431565507769528[30] = 1;
   out_6423431565507769528[31] = 0;
   out_6423431565507769528[32] = 0;
   out_6423431565507769528[33] = 0;
   out_6423431565507769528[34] = 0;
   out_6423431565507769528[35] = 0;
   out_6423431565507769528[36] = 0;
   out_6423431565507769528[37] = 0;
   out_6423431565507769528[38] = 0;
   out_6423431565507769528[39] = 0;
   out_6423431565507769528[40] = 1;
   out_6423431565507769528[41] = 0;
   out_6423431565507769528[42] = 0;
   out_6423431565507769528[43] = 0;
   out_6423431565507769528[44] = 0;
   out_6423431565507769528[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_6423431565507769528[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_6423431565507769528[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_6423431565507769528[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_6423431565507769528[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_6423431565507769528[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_6423431565507769528[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_6423431565507769528[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_6423431565507769528[53] = -9.8100000000000005*dt;
   out_6423431565507769528[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_6423431565507769528[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_6423431565507769528[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6423431565507769528[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6423431565507769528[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_6423431565507769528[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_6423431565507769528[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_6423431565507769528[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6423431565507769528[62] = 0;
   out_6423431565507769528[63] = 0;
   out_6423431565507769528[64] = 0;
   out_6423431565507769528[65] = 0;
   out_6423431565507769528[66] = 0;
   out_6423431565507769528[67] = 0;
   out_6423431565507769528[68] = 0;
   out_6423431565507769528[69] = 0;
   out_6423431565507769528[70] = 1;
   out_6423431565507769528[71] = 0;
   out_6423431565507769528[72] = 0;
   out_6423431565507769528[73] = 0;
   out_6423431565507769528[74] = 0;
   out_6423431565507769528[75] = 0;
   out_6423431565507769528[76] = 0;
   out_6423431565507769528[77] = 0;
   out_6423431565507769528[78] = 0;
   out_6423431565507769528[79] = 0;
   out_6423431565507769528[80] = 1;
}
void h_25(double *state, double *unused, double *out_8281489855210528984) {
   out_8281489855210528984[0] = state[6];
}
void H_25(double *state, double *unused, double *out_257722837092792508) {
   out_257722837092792508[0] = 0;
   out_257722837092792508[1] = 0;
   out_257722837092792508[2] = 0;
   out_257722837092792508[3] = 0;
   out_257722837092792508[4] = 0;
   out_257722837092792508[5] = 0;
   out_257722837092792508[6] = 1;
   out_257722837092792508[7] = 0;
   out_257722837092792508[8] = 0;
}
void h_24(double *state, double *unused, double *out_5654195456743599601) {
   out_5654195456743599601[0] = state[4];
   out_5654195456743599601[1] = state[5];
}
void H_24(double *state, double *unused, double *out_2483430621071661070) {
   out_2483430621071661070[0] = 0;
   out_2483430621071661070[1] = 0;
   out_2483430621071661070[2] = 0;
   out_2483430621071661070[3] = 0;
   out_2483430621071661070[4] = 1;
   out_2483430621071661070[5] = 0;
   out_2483430621071661070[6] = 0;
   out_2483430621071661070[7] = 0;
   out_2483430621071661070[8] = 0;
   out_2483430621071661070[9] = 0;
   out_2483430621071661070[10] = 0;
   out_2483430621071661070[11] = 0;
   out_2483430621071661070[12] = 0;
   out_2483430621071661070[13] = 0;
   out_2483430621071661070[14] = 1;
   out_2483430621071661070[15] = 0;
   out_2483430621071661070[16] = 0;
   out_2483430621071661070[17] = 0;
}
void h_30(double *state, double *unused, double *out_8438676523561658129) {
   out_8438676523561658129[0] = state[4];
}
void H_30(double *state, double *unused, double *out_7174413178584409263) {
   out_7174413178584409263[0] = 0;
   out_7174413178584409263[1] = 0;
   out_7174413178584409263[2] = 0;
   out_7174413178584409263[3] = 0;
   out_7174413178584409263[4] = 1;
   out_7174413178584409263[5] = 0;
   out_7174413178584409263[6] = 0;
   out_7174413178584409263[7] = 0;
   out_7174413178584409263[8] = 0;
}
void h_26(double *state, double *unused, double *out_1419904868343052079) {
   out_1419904868343052079[0] = state[7];
}
void H_26(double *state, double *unused, double *out_3562248806853593109) {
   out_3562248806853593109[0] = 0;
   out_3562248806853593109[1] = 0;
   out_3562248806853593109[2] = 0;
   out_3562248806853593109[3] = 0;
   out_3562248806853593109[4] = 0;
   out_3562248806853593109[5] = 0;
   out_3562248806853593109[6] = 0;
   out_3562248806853593109[7] = 1;
   out_3562248806853593109[8] = 0;
}
void h_27(double *state, double *unused, double *out_1905364559686504598) {
   out_1905364559686504598[0] = state[3];
}
void H_27(double *state, double *unused, double *out_4999649866783984352) {
   out_4999649866783984352[0] = 0;
   out_4999649866783984352[1] = 0;
   out_4999649866783984352[2] = 0;
   out_4999649866783984352[3] = 1;
   out_4999649866783984352[4] = 0;
   out_4999649866783984352[5] = 0;
   out_4999649866783984352[6] = 0;
   out_4999649866783984352[7] = 0;
   out_4999649866783984352[8] = 0;
}
void h_29(double *state, double *unused, double *out_3005304846354827708) {
   out_3005304846354827708[0] = state[1];
}
void H_29(double *state, double *unused, double *out_7684644522898801447) {
   out_7684644522898801447[0] = 0;
   out_7684644522898801447[1] = 1;
   out_7684644522898801447[2] = 0;
   out_7684644522898801447[3] = 0;
   out_7684644522898801447[4] = 0;
   out_7684644522898801447[5] = 0;
   out_7684644522898801447[6] = 0;
   out_7684644522898801447[7] = 0;
   out_7684644522898801447[8] = 0;
}
void h_28(double *state, double *unused, double *out_8832630219803516209) {
   out_8832630219803516209[0] = state[0];
}
void H_28(double *state, double *unused, double *out_1796111877155097255) {
   out_1796111877155097255[0] = 1;
   out_1796111877155097255[1] = 0;
   out_1796111877155097255[2] = 0;
   out_1796111877155097255[3] = 0;
   out_1796111877155097255[4] = 0;
   out_1796111877155097255[5] = 0;
   out_1796111877155097255[6] = 0;
   out_1796111877155097255[7] = 0;
   out_1796111877155097255[8] = 0;
}
void h_31(double *state, double *unused, double *out_6225098197673216166) {
   out_6225098197673216166[0] = state[8];
}
void H_31(double *state, double *unused, double *out_7334398087604609761) {
   out_7334398087604609761[0] = 0;
   out_7334398087604609761[1] = 0;
   out_7334398087604609761[2] = 0;
   out_7334398087604609761[3] = 0;
   out_7334398087604609761[4] = 0;
   out_7334398087604609761[5] = 0;
   out_7334398087604609761[6] = 0;
   out_7334398087604609761[7] = 0;
   out_7334398087604609761[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_760253992355356602) {
  err_fun(nom_x, delta_x, out_760253992355356602);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4983548601721046404) {
  inv_err_fun(nom_x, true_x, out_4983548601721046404);
}
void car_H_mod_fun(double *state, double *out_8995833010704521871) {
  H_mod_fun(state, out_8995833010704521871);
}
void car_f_fun(double *state, double dt, double *out_4562655195590537984) {
  f_fun(state,  dt, out_4562655195590537984);
}
void car_F_fun(double *state, double dt, double *out_6423431565507769528) {
  F_fun(state,  dt, out_6423431565507769528);
}
void car_h_25(double *state, double *unused, double *out_8281489855210528984) {
  h_25(state, unused, out_8281489855210528984);
}
void car_H_25(double *state, double *unused, double *out_257722837092792508) {
  H_25(state, unused, out_257722837092792508);
}
void car_h_24(double *state, double *unused, double *out_5654195456743599601) {
  h_24(state, unused, out_5654195456743599601);
}
void car_H_24(double *state, double *unused, double *out_2483430621071661070) {
  H_24(state, unused, out_2483430621071661070);
}
void car_h_30(double *state, double *unused, double *out_8438676523561658129) {
  h_30(state, unused, out_8438676523561658129);
}
void car_H_30(double *state, double *unused, double *out_7174413178584409263) {
  H_30(state, unused, out_7174413178584409263);
}
void car_h_26(double *state, double *unused, double *out_1419904868343052079) {
  h_26(state, unused, out_1419904868343052079);
}
void car_H_26(double *state, double *unused, double *out_3562248806853593109) {
  H_26(state, unused, out_3562248806853593109);
}
void car_h_27(double *state, double *unused, double *out_1905364559686504598) {
  h_27(state, unused, out_1905364559686504598);
}
void car_H_27(double *state, double *unused, double *out_4999649866783984352) {
  H_27(state, unused, out_4999649866783984352);
}
void car_h_29(double *state, double *unused, double *out_3005304846354827708) {
  h_29(state, unused, out_3005304846354827708);
}
void car_H_29(double *state, double *unused, double *out_7684644522898801447) {
  H_29(state, unused, out_7684644522898801447);
}
void car_h_28(double *state, double *unused, double *out_8832630219803516209) {
  h_28(state, unused, out_8832630219803516209);
}
void car_H_28(double *state, double *unused, double *out_1796111877155097255) {
  H_28(state, unused, out_1796111877155097255);
}
void car_h_31(double *state, double *unused, double *out_6225098197673216166) {
  h_31(state, unused, out_6225098197673216166);
}
void car_H_31(double *state, double *unused, double *out_7334398087604609761) {
  H_31(state, unused, out_7334398087604609761);
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
