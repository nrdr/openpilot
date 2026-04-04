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
void err_fun(double *nom_x, double *delta_x, double *out_8689376007771914630) {
   out_8689376007771914630[0] = delta_x[0] + nom_x[0];
   out_8689376007771914630[1] = delta_x[1] + nom_x[1];
   out_8689376007771914630[2] = delta_x[2] + nom_x[2];
   out_8689376007771914630[3] = delta_x[3] + nom_x[3];
   out_8689376007771914630[4] = delta_x[4] + nom_x[4];
   out_8689376007771914630[5] = delta_x[5] + nom_x[5];
   out_8689376007771914630[6] = delta_x[6] + nom_x[6];
   out_8689376007771914630[7] = delta_x[7] + nom_x[7];
   out_8689376007771914630[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_9185173267100820525) {
   out_9185173267100820525[0] = -nom_x[0] + true_x[0];
   out_9185173267100820525[1] = -nom_x[1] + true_x[1];
   out_9185173267100820525[2] = -nom_x[2] + true_x[2];
   out_9185173267100820525[3] = -nom_x[3] + true_x[3];
   out_9185173267100820525[4] = -nom_x[4] + true_x[4];
   out_9185173267100820525[5] = -nom_x[5] + true_x[5];
   out_9185173267100820525[6] = -nom_x[6] + true_x[6];
   out_9185173267100820525[7] = -nom_x[7] + true_x[7];
   out_9185173267100820525[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_2260146128448476382) {
   out_2260146128448476382[0] = 1.0;
   out_2260146128448476382[1] = 0.0;
   out_2260146128448476382[2] = 0.0;
   out_2260146128448476382[3] = 0.0;
   out_2260146128448476382[4] = 0.0;
   out_2260146128448476382[5] = 0.0;
   out_2260146128448476382[6] = 0.0;
   out_2260146128448476382[7] = 0.0;
   out_2260146128448476382[8] = 0.0;
   out_2260146128448476382[9] = 0.0;
   out_2260146128448476382[10] = 1.0;
   out_2260146128448476382[11] = 0.0;
   out_2260146128448476382[12] = 0.0;
   out_2260146128448476382[13] = 0.0;
   out_2260146128448476382[14] = 0.0;
   out_2260146128448476382[15] = 0.0;
   out_2260146128448476382[16] = 0.0;
   out_2260146128448476382[17] = 0.0;
   out_2260146128448476382[18] = 0.0;
   out_2260146128448476382[19] = 0.0;
   out_2260146128448476382[20] = 1.0;
   out_2260146128448476382[21] = 0.0;
   out_2260146128448476382[22] = 0.0;
   out_2260146128448476382[23] = 0.0;
   out_2260146128448476382[24] = 0.0;
   out_2260146128448476382[25] = 0.0;
   out_2260146128448476382[26] = 0.0;
   out_2260146128448476382[27] = 0.0;
   out_2260146128448476382[28] = 0.0;
   out_2260146128448476382[29] = 0.0;
   out_2260146128448476382[30] = 1.0;
   out_2260146128448476382[31] = 0.0;
   out_2260146128448476382[32] = 0.0;
   out_2260146128448476382[33] = 0.0;
   out_2260146128448476382[34] = 0.0;
   out_2260146128448476382[35] = 0.0;
   out_2260146128448476382[36] = 0.0;
   out_2260146128448476382[37] = 0.0;
   out_2260146128448476382[38] = 0.0;
   out_2260146128448476382[39] = 0.0;
   out_2260146128448476382[40] = 1.0;
   out_2260146128448476382[41] = 0.0;
   out_2260146128448476382[42] = 0.0;
   out_2260146128448476382[43] = 0.0;
   out_2260146128448476382[44] = 0.0;
   out_2260146128448476382[45] = 0.0;
   out_2260146128448476382[46] = 0.0;
   out_2260146128448476382[47] = 0.0;
   out_2260146128448476382[48] = 0.0;
   out_2260146128448476382[49] = 0.0;
   out_2260146128448476382[50] = 1.0;
   out_2260146128448476382[51] = 0.0;
   out_2260146128448476382[52] = 0.0;
   out_2260146128448476382[53] = 0.0;
   out_2260146128448476382[54] = 0.0;
   out_2260146128448476382[55] = 0.0;
   out_2260146128448476382[56] = 0.0;
   out_2260146128448476382[57] = 0.0;
   out_2260146128448476382[58] = 0.0;
   out_2260146128448476382[59] = 0.0;
   out_2260146128448476382[60] = 1.0;
   out_2260146128448476382[61] = 0.0;
   out_2260146128448476382[62] = 0.0;
   out_2260146128448476382[63] = 0.0;
   out_2260146128448476382[64] = 0.0;
   out_2260146128448476382[65] = 0.0;
   out_2260146128448476382[66] = 0.0;
   out_2260146128448476382[67] = 0.0;
   out_2260146128448476382[68] = 0.0;
   out_2260146128448476382[69] = 0.0;
   out_2260146128448476382[70] = 1.0;
   out_2260146128448476382[71] = 0.0;
   out_2260146128448476382[72] = 0.0;
   out_2260146128448476382[73] = 0.0;
   out_2260146128448476382[74] = 0.0;
   out_2260146128448476382[75] = 0.0;
   out_2260146128448476382[76] = 0.0;
   out_2260146128448476382[77] = 0.0;
   out_2260146128448476382[78] = 0.0;
   out_2260146128448476382[79] = 0.0;
   out_2260146128448476382[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_2158220440628955836) {
   out_2158220440628955836[0] = state[0];
   out_2158220440628955836[1] = state[1];
   out_2158220440628955836[2] = state[2];
   out_2158220440628955836[3] = state[3];
   out_2158220440628955836[4] = state[4];
   out_2158220440628955836[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_2158220440628955836[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_2158220440628955836[7] = state[7];
   out_2158220440628955836[8] = state[8];
}
void F_fun(double *state, double dt, double *out_616665486939110306) {
   out_616665486939110306[0] = 1;
   out_616665486939110306[1] = 0;
   out_616665486939110306[2] = 0;
   out_616665486939110306[3] = 0;
   out_616665486939110306[4] = 0;
   out_616665486939110306[5] = 0;
   out_616665486939110306[6] = 0;
   out_616665486939110306[7] = 0;
   out_616665486939110306[8] = 0;
   out_616665486939110306[9] = 0;
   out_616665486939110306[10] = 1;
   out_616665486939110306[11] = 0;
   out_616665486939110306[12] = 0;
   out_616665486939110306[13] = 0;
   out_616665486939110306[14] = 0;
   out_616665486939110306[15] = 0;
   out_616665486939110306[16] = 0;
   out_616665486939110306[17] = 0;
   out_616665486939110306[18] = 0;
   out_616665486939110306[19] = 0;
   out_616665486939110306[20] = 1;
   out_616665486939110306[21] = 0;
   out_616665486939110306[22] = 0;
   out_616665486939110306[23] = 0;
   out_616665486939110306[24] = 0;
   out_616665486939110306[25] = 0;
   out_616665486939110306[26] = 0;
   out_616665486939110306[27] = 0;
   out_616665486939110306[28] = 0;
   out_616665486939110306[29] = 0;
   out_616665486939110306[30] = 1;
   out_616665486939110306[31] = 0;
   out_616665486939110306[32] = 0;
   out_616665486939110306[33] = 0;
   out_616665486939110306[34] = 0;
   out_616665486939110306[35] = 0;
   out_616665486939110306[36] = 0;
   out_616665486939110306[37] = 0;
   out_616665486939110306[38] = 0;
   out_616665486939110306[39] = 0;
   out_616665486939110306[40] = 1;
   out_616665486939110306[41] = 0;
   out_616665486939110306[42] = 0;
   out_616665486939110306[43] = 0;
   out_616665486939110306[44] = 0;
   out_616665486939110306[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_616665486939110306[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_616665486939110306[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_616665486939110306[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_616665486939110306[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_616665486939110306[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_616665486939110306[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_616665486939110306[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_616665486939110306[53] = -9.8100000000000005*dt;
   out_616665486939110306[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_616665486939110306[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_616665486939110306[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_616665486939110306[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_616665486939110306[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_616665486939110306[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_616665486939110306[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_616665486939110306[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_616665486939110306[62] = 0;
   out_616665486939110306[63] = 0;
   out_616665486939110306[64] = 0;
   out_616665486939110306[65] = 0;
   out_616665486939110306[66] = 0;
   out_616665486939110306[67] = 0;
   out_616665486939110306[68] = 0;
   out_616665486939110306[69] = 0;
   out_616665486939110306[70] = 1;
   out_616665486939110306[71] = 0;
   out_616665486939110306[72] = 0;
   out_616665486939110306[73] = 0;
   out_616665486939110306[74] = 0;
   out_616665486939110306[75] = 0;
   out_616665486939110306[76] = 0;
   out_616665486939110306[77] = 0;
   out_616665486939110306[78] = 0;
   out_616665486939110306[79] = 0;
   out_616665486939110306[80] = 1;
}
void h_25(double *state, double *unused, double *out_6409895638825259551) {
   out_6409895638825259551[0] = state[6];
}
void H_25(double *state, double *unused, double *out_5783126778437968059) {
   out_5783126778437968059[0] = 0;
   out_5783126778437968059[1] = 0;
   out_5783126778437968059[2] = 0;
   out_5783126778437968059[3] = 0;
   out_5783126778437968059[4] = 0;
   out_5783126778437968059[5] = 0;
   out_5783126778437968059[6] = 1;
   out_5783126778437968059[7] = 0;
   out_5783126778437968059[8] = 0;
}
void h_24(double *state, double *unused, double *out_624020570893641793) {
   out_624020570893641793[0] = state[4];
   out_624020570893641793[1] = state[5];
}
void H_24(double *state, double *unused, double *out_9105691696469260421) {
   out_9105691696469260421[0] = 0;
   out_9105691696469260421[1] = 0;
   out_9105691696469260421[2] = 0;
   out_9105691696469260421[3] = 0;
   out_9105691696469260421[4] = 1;
   out_9105691696469260421[5] = 0;
   out_9105691696469260421[6] = 0;
   out_9105691696469260421[7] = 0;
   out_9105691696469260421[8] = 0;
   out_9105691696469260421[9] = 0;
   out_9105691696469260421[10] = 0;
   out_9105691696469260421[11] = 0;
   out_9105691696469260421[12] = 0;
   out_9105691696469260421[13] = 0;
   out_9105691696469260421[14] = 1;
   out_9105691696469260421[15] = 0;
   out_9105691696469260421[16] = 0;
   out_9105691696469260421[17] = 0;
}
void h_30(double *state, double *unused, double *out_5266013208533941129) {
   out_5266013208533941129[0] = state[4];
}
void H_30(double *state, double *unused, double *out_5653787831294727989) {
   out_5653787831294727989[0] = 0;
   out_5653787831294727989[1] = 0;
   out_5653787831294727989[2] = 0;
   out_5653787831294727989[3] = 0;
   out_5653787831294727989[4] = 1;
   out_5653787831294727989[5] = 0;
   out_5653787831294727989[6] = 0;
   out_5653787831294727989[7] = 0;
   out_5653787831294727989[8] = 0;
}
void h_26(double *state, double *unused, double *out_6956461043269622089) {
   out_6956461043269622089[0] = state[7];
}
void H_26(double *state, double *unused, double *out_2041623459563911835) {
   out_2041623459563911835[0] = 0;
   out_2041623459563911835[1] = 0;
   out_2041623459563911835[2] = 0;
   out_2041623459563911835[3] = 0;
   out_2041623459563911835[4] = 0;
   out_2041623459563911835[5] = 0;
   out_2041623459563911835[6] = 0;
   out_2041623459563911835[7] = 1;
   out_2041623459563911835[8] = 0;
}
void h_27(double *state, double *unused, double *out_1408222371164413906) {
   out_1408222371164413906[0] = state[3];
}
void H_27(double *state, double *unused, double *out_3479024519494303078) {
   out_3479024519494303078[0] = 0;
   out_3479024519494303078[1] = 0;
   out_3479024519494303078[2] = 0;
   out_3479024519494303078[3] = 1;
   out_3479024519494303078[4] = 0;
   out_3479024519494303078[5] = 0;
   out_3479024519494303078[6] = 0;
   out_3479024519494303078[7] = 0;
   out_3479024519494303078[8] = 0;
}
void h_29(double *state, double *unused, double *out_1133028308879908017) {
   out_1133028308879908017[0] = state[1];
}
void H_29(double *state, double *unused, double *out_6164019175609120173) {
   out_6164019175609120173[0] = 0;
   out_6164019175609120173[1] = 1;
   out_6164019175609120173[2] = 0;
   out_6164019175609120173[3] = 0;
   out_6164019175609120173[4] = 0;
   out_6164019175609120173[5] = 0;
   out_6164019175609120173[6] = 0;
   out_6164019175609120173[7] = 0;
   out_6164019175609120173[8] = 0;
}
void h_28(double *state, double *unused, double *out_2351732224066076341) {
   out_2351732224066076341[0] = state[0];
}
void H_28(double *state, double *unused, double *out_3316737224444778529) {
   out_3316737224444778529[0] = 1;
   out_3316737224444778529[1] = 0;
   out_3316737224444778529[2] = 0;
   out_3316737224444778529[3] = 0;
   out_3316737224444778529[4] = 0;
   out_3316737224444778529[5] = 0;
   out_3316737224444778529[6] = 0;
   out_3316737224444778529[7] = 0;
   out_3316737224444778529[8] = 0;
}
void h_31(double *state, double *unused, double *out_9089122444528807104) {
   out_9089122444528807104[0] = state[8];
}
void H_31(double *state, double *unused, double *out_5813772740314928487) {
   out_5813772740314928487[0] = 0;
   out_5813772740314928487[1] = 0;
   out_5813772740314928487[2] = 0;
   out_5813772740314928487[3] = 0;
   out_5813772740314928487[4] = 0;
   out_5813772740314928487[5] = 0;
   out_5813772740314928487[6] = 0;
   out_5813772740314928487[7] = 0;
   out_5813772740314928487[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_8689376007771914630) {
  err_fun(nom_x, delta_x, out_8689376007771914630);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_9185173267100820525) {
  inv_err_fun(nom_x, true_x, out_9185173267100820525);
}
void car_H_mod_fun(double *state, double *out_2260146128448476382) {
  H_mod_fun(state, out_2260146128448476382);
}
void car_f_fun(double *state, double dt, double *out_2158220440628955836) {
  f_fun(state,  dt, out_2158220440628955836);
}
void car_F_fun(double *state, double dt, double *out_616665486939110306) {
  F_fun(state,  dt, out_616665486939110306);
}
void car_h_25(double *state, double *unused, double *out_6409895638825259551) {
  h_25(state, unused, out_6409895638825259551);
}
void car_H_25(double *state, double *unused, double *out_5783126778437968059) {
  H_25(state, unused, out_5783126778437968059);
}
void car_h_24(double *state, double *unused, double *out_624020570893641793) {
  h_24(state, unused, out_624020570893641793);
}
void car_H_24(double *state, double *unused, double *out_9105691696469260421) {
  H_24(state, unused, out_9105691696469260421);
}
void car_h_30(double *state, double *unused, double *out_5266013208533941129) {
  h_30(state, unused, out_5266013208533941129);
}
void car_H_30(double *state, double *unused, double *out_5653787831294727989) {
  H_30(state, unused, out_5653787831294727989);
}
void car_h_26(double *state, double *unused, double *out_6956461043269622089) {
  h_26(state, unused, out_6956461043269622089);
}
void car_H_26(double *state, double *unused, double *out_2041623459563911835) {
  H_26(state, unused, out_2041623459563911835);
}
void car_h_27(double *state, double *unused, double *out_1408222371164413906) {
  h_27(state, unused, out_1408222371164413906);
}
void car_H_27(double *state, double *unused, double *out_3479024519494303078) {
  H_27(state, unused, out_3479024519494303078);
}
void car_h_29(double *state, double *unused, double *out_1133028308879908017) {
  h_29(state, unused, out_1133028308879908017);
}
void car_H_29(double *state, double *unused, double *out_6164019175609120173) {
  H_29(state, unused, out_6164019175609120173);
}
void car_h_28(double *state, double *unused, double *out_2351732224066076341) {
  h_28(state, unused, out_2351732224066076341);
}
void car_H_28(double *state, double *unused, double *out_3316737224444778529) {
  H_28(state, unused, out_3316737224444778529);
}
void car_h_31(double *state, double *unused, double *out_9089122444528807104) {
  h_31(state, unused, out_9089122444528807104);
}
void car_H_31(double *state, double *unused, double *out_5813772740314928487) {
  H_31(state, unused, out_5813772740314928487);
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
