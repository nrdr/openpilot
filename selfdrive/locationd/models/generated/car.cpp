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
void err_fun(double *nom_x, double *delta_x, double *out_2854927516327151793) {
   out_2854927516327151793[0] = delta_x[0] + nom_x[0];
   out_2854927516327151793[1] = delta_x[1] + nom_x[1];
   out_2854927516327151793[2] = delta_x[2] + nom_x[2];
   out_2854927516327151793[3] = delta_x[3] + nom_x[3];
   out_2854927516327151793[4] = delta_x[4] + nom_x[4];
   out_2854927516327151793[5] = delta_x[5] + nom_x[5];
   out_2854927516327151793[6] = delta_x[6] + nom_x[6];
   out_2854927516327151793[7] = delta_x[7] + nom_x[7];
   out_2854927516327151793[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1130521926089760612) {
   out_1130521926089760612[0] = -nom_x[0] + true_x[0];
   out_1130521926089760612[1] = -nom_x[1] + true_x[1];
   out_1130521926089760612[2] = -nom_x[2] + true_x[2];
   out_1130521926089760612[3] = -nom_x[3] + true_x[3];
   out_1130521926089760612[4] = -nom_x[4] + true_x[4];
   out_1130521926089760612[5] = -nom_x[5] + true_x[5];
   out_1130521926089760612[6] = -nom_x[6] + true_x[6];
   out_1130521926089760612[7] = -nom_x[7] + true_x[7];
   out_1130521926089760612[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_4978678687017002222) {
   out_4978678687017002222[0] = 1.0;
   out_4978678687017002222[1] = 0.0;
   out_4978678687017002222[2] = 0.0;
   out_4978678687017002222[3] = 0.0;
   out_4978678687017002222[4] = 0.0;
   out_4978678687017002222[5] = 0.0;
   out_4978678687017002222[6] = 0.0;
   out_4978678687017002222[7] = 0.0;
   out_4978678687017002222[8] = 0.0;
   out_4978678687017002222[9] = 0.0;
   out_4978678687017002222[10] = 1.0;
   out_4978678687017002222[11] = 0.0;
   out_4978678687017002222[12] = 0.0;
   out_4978678687017002222[13] = 0.0;
   out_4978678687017002222[14] = 0.0;
   out_4978678687017002222[15] = 0.0;
   out_4978678687017002222[16] = 0.0;
   out_4978678687017002222[17] = 0.0;
   out_4978678687017002222[18] = 0.0;
   out_4978678687017002222[19] = 0.0;
   out_4978678687017002222[20] = 1.0;
   out_4978678687017002222[21] = 0.0;
   out_4978678687017002222[22] = 0.0;
   out_4978678687017002222[23] = 0.0;
   out_4978678687017002222[24] = 0.0;
   out_4978678687017002222[25] = 0.0;
   out_4978678687017002222[26] = 0.0;
   out_4978678687017002222[27] = 0.0;
   out_4978678687017002222[28] = 0.0;
   out_4978678687017002222[29] = 0.0;
   out_4978678687017002222[30] = 1.0;
   out_4978678687017002222[31] = 0.0;
   out_4978678687017002222[32] = 0.0;
   out_4978678687017002222[33] = 0.0;
   out_4978678687017002222[34] = 0.0;
   out_4978678687017002222[35] = 0.0;
   out_4978678687017002222[36] = 0.0;
   out_4978678687017002222[37] = 0.0;
   out_4978678687017002222[38] = 0.0;
   out_4978678687017002222[39] = 0.0;
   out_4978678687017002222[40] = 1.0;
   out_4978678687017002222[41] = 0.0;
   out_4978678687017002222[42] = 0.0;
   out_4978678687017002222[43] = 0.0;
   out_4978678687017002222[44] = 0.0;
   out_4978678687017002222[45] = 0.0;
   out_4978678687017002222[46] = 0.0;
   out_4978678687017002222[47] = 0.0;
   out_4978678687017002222[48] = 0.0;
   out_4978678687017002222[49] = 0.0;
   out_4978678687017002222[50] = 1.0;
   out_4978678687017002222[51] = 0.0;
   out_4978678687017002222[52] = 0.0;
   out_4978678687017002222[53] = 0.0;
   out_4978678687017002222[54] = 0.0;
   out_4978678687017002222[55] = 0.0;
   out_4978678687017002222[56] = 0.0;
   out_4978678687017002222[57] = 0.0;
   out_4978678687017002222[58] = 0.0;
   out_4978678687017002222[59] = 0.0;
   out_4978678687017002222[60] = 1.0;
   out_4978678687017002222[61] = 0.0;
   out_4978678687017002222[62] = 0.0;
   out_4978678687017002222[63] = 0.0;
   out_4978678687017002222[64] = 0.0;
   out_4978678687017002222[65] = 0.0;
   out_4978678687017002222[66] = 0.0;
   out_4978678687017002222[67] = 0.0;
   out_4978678687017002222[68] = 0.0;
   out_4978678687017002222[69] = 0.0;
   out_4978678687017002222[70] = 1.0;
   out_4978678687017002222[71] = 0.0;
   out_4978678687017002222[72] = 0.0;
   out_4978678687017002222[73] = 0.0;
   out_4978678687017002222[74] = 0.0;
   out_4978678687017002222[75] = 0.0;
   out_4978678687017002222[76] = 0.0;
   out_4978678687017002222[77] = 0.0;
   out_4978678687017002222[78] = 0.0;
   out_4978678687017002222[79] = 0.0;
   out_4978678687017002222[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_8100988434300506514) {
   out_8100988434300506514[0] = state[0];
   out_8100988434300506514[1] = state[1];
   out_8100988434300506514[2] = state[2];
   out_8100988434300506514[3] = state[3];
   out_8100988434300506514[4] = state[4];
   out_8100988434300506514[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_8100988434300506514[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_8100988434300506514[7] = state[7];
   out_8100988434300506514[8] = state[8];
}
void F_fun(double *state, double dt, double *out_6800099434940831409) {
   out_6800099434940831409[0] = 1;
   out_6800099434940831409[1] = 0;
   out_6800099434940831409[2] = 0;
   out_6800099434940831409[3] = 0;
   out_6800099434940831409[4] = 0;
   out_6800099434940831409[5] = 0;
   out_6800099434940831409[6] = 0;
   out_6800099434940831409[7] = 0;
   out_6800099434940831409[8] = 0;
   out_6800099434940831409[9] = 0;
   out_6800099434940831409[10] = 1;
   out_6800099434940831409[11] = 0;
   out_6800099434940831409[12] = 0;
   out_6800099434940831409[13] = 0;
   out_6800099434940831409[14] = 0;
   out_6800099434940831409[15] = 0;
   out_6800099434940831409[16] = 0;
   out_6800099434940831409[17] = 0;
   out_6800099434940831409[18] = 0;
   out_6800099434940831409[19] = 0;
   out_6800099434940831409[20] = 1;
   out_6800099434940831409[21] = 0;
   out_6800099434940831409[22] = 0;
   out_6800099434940831409[23] = 0;
   out_6800099434940831409[24] = 0;
   out_6800099434940831409[25] = 0;
   out_6800099434940831409[26] = 0;
   out_6800099434940831409[27] = 0;
   out_6800099434940831409[28] = 0;
   out_6800099434940831409[29] = 0;
   out_6800099434940831409[30] = 1;
   out_6800099434940831409[31] = 0;
   out_6800099434940831409[32] = 0;
   out_6800099434940831409[33] = 0;
   out_6800099434940831409[34] = 0;
   out_6800099434940831409[35] = 0;
   out_6800099434940831409[36] = 0;
   out_6800099434940831409[37] = 0;
   out_6800099434940831409[38] = 0;
   out_6800099434940831409[39] = 0;
   out_6800099434940831409[40] = 1;
   out_6800099434940831409[41] = 0;
   out_6800099434940831409[42] = 0;
   out_6800099434940831409[43] = 0;
   out_6800099434940831409[44] = 0;
   out_6800099434940831409[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_6800099434940831409[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_6800099434940831409[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_6800099434940831409[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_6800099434940831409[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_6800099434940831409[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_6800099434940831409[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_6800099434940831409[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_6800099434940831409[53] = -9.8100000000000005*dt;
   out_6800099434940831409[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_6800099434940831409[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_6800099434940831409[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6800099434940831409[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6800099434940831409[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_6800099434940831409[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_6800099434940831409[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_6800099434940831409[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6800099434940831409[62] = 0;
   out_6800099434940831409[63] = 0;
   out_6800099434940831409[64] = 0;
   out_6800099434940831409[65] = 0;
   out_6800099434940831409[66] = 0;
   out_6800099434940831409[67] = 0;
   out_6800099434940831409[68] = 0;
   out_6800099434940831409[69] = 0;
   out_6800099434940831409[70] = 1;
   out_6800099434940831409[71] = 0;
   out_6800099434940831409[72] = 0;
   out_6800099434940831409[73] = 0;
   out_6800099434940831409[74] = 0;
   out_6800099434940831409[75] = 0;
   out_6800099434940831409[76] = 0;
   out_6800099434940831409[77] = 0;
   out_6800099434940831409[78] = 0;
   out_6800099434940831409[79] = 0;
   out_6800099434940831409[80] = 1;
}
void h_25(double *state, double *unused, double *out_1228877845259856380) {
   out_1228877845259856380[0] = state[6];
}
void H_25(double *state, double *unused, double *out_2833798363700061852) {
   out_2833798363700061852[0] = 0;
   out_2833798363700061852[1] = 0;
   out_2833798363700061852[2] = 0;
   out_2833798363700061852[3] = 0;
   out_2833798363700061852[4] = 0;
   out_2833798363700061852[5] = 0;
   out_2833798363700061852[6] = 1;
   out_2833798363700061852[7] = 0;
   out_2833798363700061852[8] = 0;
}
void h_24(double *state, double *unused, double *out_7853944336883139384) {
   out_7853944336883139384[0] = state[4];
   out_7853944336883139384[1] = state[5];
}
void H_24(double *state, double *unused, double *out_9034831043551223278) {
   out_9034831043551223278[0] = 0;
   out_9034831043551223278[1] = 0;
   out_9034831043551223278[2] = 0;
   out_9034831043551223278[3] = 0;
   out_9034831043551223278[4] = 1;
   out_9034831043551223278[5] = 0;
   out_9034831043551223278[6] = 0;
   out_9034831043551223278[7] = 0;
   out_9034831043551223278[8] = 0;
   out_9034831043551223278[9] = 0;
   out_9034831043551223278[10] = 0;
   out_9034831043551223278[11] = 0;
   out_9034831043551223278[12] = 0;
   out_9034831043551223278[13] = 0;
   out_9034831043551223278[14] = 1;
   out_9034831043551223278[15] = 0;
   out_9034831043551223278[16] = 0;
   out_9034831043551223278[17] = 0;
}
void h_30(double *state, double *unused, double *out_7999713071610207316) {
   out_7999713071610207316[0] = state[4];
}
void H_30(double *state, double *unused, double *out_315465405192813225) {
   out_315465405192813225[0] = 0;
   out_315465405192813225[1] = 0;
   out_315465405192813225[2] = 0;
   out_315465405192813225[3] = 0;
   out_315465405192813225[4] = 1;
   out_315465405192813225[5] = 0;
   out_315465405192813225[6] = 0;
   out_315465405192813225[7] = 0;
   out_315465405192813225[8] = 0;
}
void h_26(double *state, double *unused, double *out_1650721537833347160) {
   out_1650721537833347160[0] = state[7];
}
void H_26(double *state, double *unused, double *out_6575301682574118076) {
   out_6575301682574118076[0] = 0;
   out_6575301682574118076[1] = 0;
   out_6575301682574118076[2] = 0;
   out_6575301682574118076[3] = 0;
   out_6575301682574118076[4] = 0;
   out_6575301682574118076[5] = 0;
   out_6575301682574118076[6] = 0;
   out_6575301682574118076[7] = 1;
   out_6575301682574118076[8] = 0;
}
void h_27(double *state, double *unused, double *out_3772795422400989265) {
   out_3772795422400989265[0] = state[3];
}
void H_27(double *state, double *unused, double *out_1908128665991129992) {
   out_1908128665991129992[0] = 0;
   out_1908128665991129992[1] = 0;
   out_1908128665991129992[2] = 0;
   out_1908128665991129992[3] = 1;
   out_1908128665991129992[4] = 0;
   out_1908128665991129992[5] = 0;
   out_1908128665991129992[6] = 0;
   out_1908128665991129992[7] = 0;
   out_1908128665991129992[8] = 0;
}
void h_29(double *state, double *unused, double *out_4047989484685495154) {
   out_4047989484685495154[0] = state[1];
}
void H_29(double *state, double *unused, double *out_194765939121578959) {
   out_194765939121578959[0] = 0;
   out_194765939121578959[1] = 1;
   out_194765939121578959[2] = 0;
   out_194765939121578959[3] = 0;
   out_194765939121578959[4] = 0;
   out_194765939121578959[5] = 0;
   out_194765939121578959[6] = 0;
   out_194765939121578959[7] = 0;
   out_194765939121578959[8] = 0;
}
void h_28(double *state, double *unused, double *out_1569071813485041298) {
   out_1569071813485041298[0] = state[0];
}
void H_28(double *state, double *unused, double *out_4887633077947951615) {
   out_4887633077947951615[0] = 1;
   out_4887633077947951615[1] = 0;
   out_4887633077947951615[2] = 0;
   out_4887633077947951615[3] = 0;
   out_4887633077947951615[4] = 0;
   out_4887633077947951615[5] = 0;
   out_4887633077947951615[6] = 0;
   out_4887633077947951615[7] = 0;
   out_4887633077947951615[8] = 0;
}
void h_31(double *state, double *unused, double *out_4866327373513878730) {
   out_4866327373513878730[0] = state[8];
}
void H_31(double *state, double *unused, double *out_7201509784807469552) {
   out_7201509784807469552[0] = 0;
   out_7201509784807469552[1] = 0;
   out_7201509784807469552[2] = 0;
   out_7201509784807469552[3] = 0;
   out_7201509784807469552[4] = 0;
   out_7201509784807469552[5] = 0;
   out_7201509784807469552[6] = 0;
   out_7201509784807469552[7] = 0;
   out_7201509784807469552[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_2854927516327151793) {
  err_fun(nom_x, delta_x, out_2854927516327151793);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1130521926089760612) {
  inv_err_fun(nom_x, true_x, out_1130521926089760612);
}
void car_H_mod_fun(double *state, double *out_4978678687017002222) {
  H_mod_fun(state, out_4978678687017002222);
}
void car_f_fun(double *state, double dt, double *out_8100988434300506514) {
  f_fun(state,  dt, out_8100988434300506514);
}
void car_F_fun(double *state, double dt, double *out_6800099434940831409) {
  F_fun(state,  dt, out_6800099434940831409);
}
void car_h_25(double *state, double *unused, double *out_1228877845259856380) {
  h_25(state, unused, out_1228877845259856380);
}
void car_H_25(double *state, double *unused, double *out_2833798363700061852) {
  H_25(state, unused, out_2833798363700061852);
}
void car_h_24(double *state, double *unused, double *out_7853944336883139384) {
  h_24(state, unused, out_7853944336883139384);
}
void car_H_24(double *state, double *unused, double *out_9034831043551223278) {
  H_24(state, unused, out_9034831043551223278);
}
void car_h_30(double *state, double *unused, double *out_7999713071610207316) {
  h_30(state, unused, out_7999713071610207316);
}
void car_H_30(double *state, double *unused, double *out_315465405192813225) {
  H_30(state, unused, out_315465405192813225);
}
void car_h_26(double *state, double *unused, double *out_1650721537833347160) {
  h_26(state, unused, out_1650721537833347160);
}
void car_H_26(double *state, double *unused, double *out_6575301682574118076) {
  H_26(state, unused, out_6575301682574118076);
}
void car_h_27(double *state, double *unused, double *out_3772795422400989265) {
  h_27(state, unused, out_3772795422400989265);
}
void car_H_27(double *state, double *unused, double *out_1908128665991129992) {
  H_27(state, unused, out_1908128665991129992);
}
void car_h_29(double *state, double *unused, double *out_4047989484685495154) {
  h_29(state, unused, out_4047989484685495154);
}
void car_H_29(double *state, double *unused, double *out_194765939121578959) {
  H_29(state, unused, out_194765939121578959);
}
void car_h_28(double *state, double *unused, double *out_1569071813485041298) {
  h_28(state, unused, out_1569071813485041298);
}
void car_H_28(double *state, double *unused, double *out_4887633077947951615) {
  H_28(state, unused, out_4887633077947951615);
}
void car_h_31(double *state, double *unused, double *out_4866327373513878730) {
  h_31(state, unused, out_4866327373513878730);
}
void car_H_31(double *state, double *unused, double *out_7201509784807469552) {
  H_31(state, unused, out_7201509784807469552);
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
