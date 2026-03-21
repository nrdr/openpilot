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
void err_fun(double *nom_x, double *delta_x, double *out_1553445728791412940) {
   out_1553445728791412940[0] = delta_x[0] + nom_x[0];
   out_1553445728791412940[1] = delta_x[1] + nom_x[1];
   out_1553445728791412940[2] = delta_x[2] + nom_x[2];
   out_1553445728791412940[3] = delta_x[3] + nom_x[3];
   out_1553445728791412940[4] = delta_x[4] + nom_x[4];
   out_1553445728791412940[5] = delta_x[5] + nom_x[5];
   out_1553445728791412940[6] = delta_x[6] + nom_x[6];
   out_1553445728791412940[7] = delta_x[7] + nom_x[7];
   out_1553445728791412940[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6999435887956597333) {
   out_6999435887956597333[0] = -nom_x[0] + true_x[0];
   out_6999435887956597333[1] = -nom_x[1] + true_x[1];
   out_6999435887956597333[2] = -nom_x[2] + true_x[2];
   out_6999435887956597333[3] = -nom_x[3] + true_x[3];
   out_6999435887956597333[4] = -nom_x[4] + true_x[4];
   out_6999435887956597333[5] = -nom_x[5] + true_x[5];
   out_6999435887956597333[6] = -nom_x[6] + true_x[6];
   out_6999435887956597333[7] = -nom_x[7] + true_x[7];
   out_6999435887956597333[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_6886426107079341067) {
   out_6886426107079341067[0] = 1.0;
   out_6886426107079341067[1] = 0.0;
   out_6886426107079341067[2] = 0.0;
   out_6886426107079341067[3] = 0.0;
   out_6886426107079341067[4] = 0.0;
   out_6886426107079341067[5] = 0.0;
   out_6886426107079341067[6] = 0.0;
   out_6886426107079341067[7] = 0.0;
   out_6886426107079341067[8] = 0.0;
   out_6886426107079341067[9] = 0.0;
   out_6886426107079341067[10] = 1.0;
   out_6886426107079341067[11] = 0.0;
   out_6886426107079341067[12] = 0.0;
   out_6886426107079341067[13] = 0.0;
   out_6886426107079341067[14] = 0.0;
   out_6886426107079341067[15] = 0.0;
   out_6886426107079341067[16] = 0.0;
   out_6886426107079341067[17] = 0.0;
   out_6886426107079341067[18] = 0.0;
   out_6886426107079341067[19] = 0.0;
   out_6886426107079341067[20] = 1.0;
   out_6886426107079341067[21] = 0.0;
   out_6886426107079341067[22] = 0.0;
   out_6886426107079341067[23] = 0.0;
   out_6886426107079341067[24] = 0.0;
   out_6886426107079341067[25] = 0.0;
   out_6886426107079341067[26] = 0.0;
   out_6886426107079341067[27] = 0.0;
   out_6886426107079341067[28] = 0.0;
   out_6886426107079341067[29] = 0.0;
   out_6886426107079341067[30] = 1.0;
   out_6886426107079341067[31] = 0.0;
   out_6886426107079341067[32] = 0.0;
   out_6886426107079341067[33] = 0.0;
   out_6886426107079341067[34] = 0.0;
   out_6886426107079341067[35] = 0.0;
   out_6886426107079341067[36] = 0.0;
   out_6886426107079341067[37] = 0.0;
   out_6886426107079341067[38] = 0.0;
   out_6886426107079341067[39] = 0.0;
   out_6886426107079341067[40] = 1.0;
   out_6886426107079341067[41] = 0.0;
   out_6886426107079341067[42] = 0.0;
   out_6886426107079341067[43] = 0.0;
   out_6886426107079341067[44] = 0.0;
   out_6886426107079341067[45] = 0.0;
   out_6886426107079341067[46] = 0.0;
   out_6886426107079341067[47] = 0.0;
   out_6886426107079341067[48] = 0.0;
   out_6886426107079341067[49] = 0.0;
   out_6886426107079341067[50] = 1.0;
   out_6886426107079341067[51] = 0.0;
   out_6886426107079341067[52] = 0.0;
   out_6886426107079341067[53] = 0.0;
   out_6886426107079341067[54] = 0.0;
   out_6886426107079341067[55] = 0.0;
   out_6886426107079341067[56] = 0.0;
   out_6886426107079341067[57] = 0.0;
   out_6886426107079341067[58] = 0.0;
   out_6886426107079341067[59] = 0.0;
   out_6886426107079341067[60] = 1.0;
   out_6886426107079341067[61] = 0.0;
   out_6886426107079341067[62] = 0.0;
   out_6886426107079341067[63] = 0.0;
   out_6886426107079341067[64] = 0.0;
   out_6886426107079341067[65] = 0.0;
   out_6886426107079341067[66] = 0.0;
   out_6886426107079341067[67] = 0.0;
   out_6886426107079341067[68] = 0.0;
   out_6886426107079341067[69] = 0.0;
   out_6886426107079341067[70] = 1.0;
   out_6886426107079341067[71] = 0.0;
   out_6886426107079341067[72] = 0.0;
   out_6886426107079341067[73] = 0.0;
   out_6886426107079341067[74] = 0.0;
   out_6886426107079341067[75] = 0.0;
   out_6886426107079341067[76] = 0.0;
   out_6886426107079341067[77] = 0.0;
   out_6886426107079341067[78] = 0.0;
   out_6886426107079341067[79] = 0.0;
   out_6886426107079341067[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_2629482357883749034) {
   out_2629482357883749034[0] = state[0];
   out_2629482357883749034[1] = state[1];
   out_2629482357883749034[2] = state[2];
   out_2629482357883749034[3] = state[3];
   out_2629482357883749034[4] = state[4];
   out_2629482357883749034[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_2629482357883749034[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_2629482357883749034[7] = state[7];
   out_2629482357883749034[8] = state[8];
}
void F_fun(double *state, double dt, double *out_7990705530243511971) {
   out_7990705530243511971[0] = 1;
   out_7990705530243511971[1] = 0;
   out_7990705530243511971[2] = 0;
   out_7990705530243511971[3] = 0;
   out_7990705530243511971[4] = 0;
   out_7990705530243511971[5] = 0;
   out_7990705530243511971[6] = 0;
   out_7990705530243511971[7] = 0;
   out_7990705530243511971[8] = 0;
   out_7990705530243511971[9] = 0;
   out_7990705530243511971[10] = 1;
   out_7990705530243511971[11] = 0;
   out_7990705530243511971[12] = 0;
   out_7990705530243511971[13] = 0;
   out_7990705530243511971[14] = 0;
   out_7990705530243511971[15] = 0;
   out_7990705530243511971[16] = 0;
   out_7990705530243511971[17] = 0;
   out_7990705530243511971[18] = 0;
   out_7990705530243511971[19] = 0;
   out_7990705530243511971[20] = 1;
   out_7990705530243511971[21] = 0;
   out_7990705530243511971[22] = 0;
   out_7990705530243511971[23] = 0;
   out_7990705530243511971[24] = 0;
   out_7990705530243511971[25] = 0;
   out_7990705530243511971[26] = 0;
   out_7990705530243511971[27] = 0;
   out_7990705530243511971[28] = 0;
   out_7990705530243511971[29] = 0;
   out_7990705530243511971[30] = 1;
   out_7990705530243511971[31] = 0;
   out_7990705530243511971[32] = 0;
   out_7990705530243511971[33] = 0;
   out_7990705530243511971[34] = 0;
   out_7990705530243511971[35] = 0;
   out_7990705530243511971[36] = 0;
   out_7990705530243511971[37] = 0;
   out_7990705530243511971[38] = 0;
   out_7990705530243511971[39] = 0;
   out_7990705530243511971[40] = 1;
   out_7990705530243511971[41] = 0;
   out_7990705530243511971[42] = 0;
   out_7990705530243511971[43] = 0;
   out_7990705530243511971[44] = 0;
   out_7990705530243511971[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_7990705530243511971[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_7990705530243511971[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7990705530243511971[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7990705530243511971[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_7990705530243511971[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_7990705530243511971[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_7990705530243511971[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_7990705530243511971[53] = -9.8100000000000005*dt;
   out_7990705530243511971[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_7990705530243511971[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_7990705530243511971[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7990705530243511971[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7990705530243511971[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_7990705530243511971[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_7990705530243511971[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_7990705530243511971[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7990705530243511971[62] = 0;
   out_7990705530243511971[63] = 0;
   out_7990705530243511971[64] = 0;
   out_7990705530243511971[65] = 0;
   out_7990705530243511971[66] = 0;
   out_7990705530243511971[67] = 0;
   out_7990705530243511971[68] = 0;
   out_7990705530243511971[69] = 0;
   out_7990705530243511971[70] = 1;
   out_7990705530243511971[71] = 0;
   out_7990705530243511971[72] = 0;
   out_7990705530243511971[73] = 0;
   out_7990705530243511971[74] = 0;
   out_7990705530243511971[75] = 0;
   out_7990705530243511971[76] = 0;
   out_7990705530243511971[77] = 0;
   out_7990705530243511971[78] = 0;
   out_7990705530243511971[79] = 0;
   out_7990705530243511971[80] = 1;
}
void h_25(double *state, double *unused, double *out_1968300025718050649) {
   out_1968300025718050649[0] = state[6];
}
void H_25(double *state, double *unused, double *out_8037269327984845401) {
   out_8037269327984845401[0] = 0;
   out_8037269327984845401[1] = 0;
   out_8037269327984845401[2] = 0;
   out_8037269327984845401[3] = 0;
   out_8037269327984845401[4] = 0;
   out_8037269327984845401[5] = 0;
   out_8037269327984845401[6] = 1;
   out_8037269327984845401[7] = 0;
   out_8037269327984845401[8] = 0;
}
void h_24(double *state, double *unused, double *out_6877344855371313053) {
   out_6877344855371313053[0] = state[4];
   out_6877344855371313053[1] = state[5];
}
void H_24(double *state, double *unused, double *out_3833902939133188114) {
   out_3833902939133188114[0] = 0;
   out_3833902939133188114[1] = 0;
   out_3833902939133188114[2] = 0;
   out_3833902939133188114[3] = 0;
   out_3833902939133188114[4] = 1;
   out_3833902939133188114[5] = 0;
   out_3833902939133188114[6] = 0;
   out_3833902939133188114[7] = 0;
   out_3833902939133188114[8] = 0;
   out_3833902939133188114[9] = 0;
   out_3833902939133188114[10] = 0;
   out_3833902939133188114[11] = 0;
   out_3833902939133188114[12] = 0;
   out_3833902939133188114[13] = 0;
   out_3833902939133188114[14] = 1;
   out_3833902939133188114[15] = 0;
   out_3833902939133188114[16] = 0;
   out_3833902939133188114[17] = 0;
}
void h_30(double *state, double *unused, double *out_2125486694069179794) {
   out_2125486694069179794[0] = state[4];
}
void H_30(double *state, double *unused, double *out_7891141787217457588) {
   out_7891141787217457588[0] = 0;
   out_7891141787217457588[1] = 0;
   out_7891141787217457588[2] = 0;
   out_7891141787217457588[3] = 0;
   out_7891141787217457588[4] = 1;
   out_7891141787217457588[5] = 0;
   out_7891141787217457588[6] = 0;
   out_7891141787217457588[7] = 0;
   out_7891141787217457588[8] = 0;
}
void h_26(double *state, double *unused, double *out_2612659355437634136) {
   out_2612659355437634136[0] = state[7];
}
void H_26(double *state, double *unused, double *out_7104948775963905614) {
   out_7104948775963905614[0] = 0;
   out_7104948775963905614[1] = 0;
   out_7104948775963905614[2] = 0;
   out_7104948775963905614[3] = 0;
   out_7104948775963905614[4] = 0;
   out_7104948775963905614[5] = 0;
   out_7104948775963905614[6] = 0;
   out_7104948775963905614[7] = 1;
   out_7104948775963905614[8] = 0;
}
void h_27(double *state, double *unused, double *out_5005086077162383334) {
   out_5005086077162383334[0] = state[3];
}
void H_27(double *state, double *unused, double *out_5667547716033514371) {
   out_5667547716033514371[0] = 0;
   out_5667547716033514371[1] = 0;
   out_5667547716033514371[2] = 0;
   out_5667547716033514371[3] = 1;
   out_5667547716033514371[4] = 0;
   out_5667547716033514371[5] = 0;
   out_5667547716033514371[6] = 0;
   out_5667547716033514371[7] = 0;
   out_5667547716033514371[8] = 0;
}
void h_29(double *state, double *unused, double *out_6670822770196817346) {
   out_6670822770196817346[0] = state[1];
}
void H_29(double *state, double *unused, double *out_7380910442903065404) {
   out_7380910442903065404[0] = 0;
   out_7380910442903065404[1] = 1;
   out_7380910442903065404[2] = 0;
   out_7380910442903065404[3] = 0;
   out_7380910442903065404[4] = 0;
   out_7380910442903065404[5] = 0;
   out_7380910442903065404[6] = 0;
   out_7380910442903065404[7] = 0;
   out_7380910442903065404[8] = 0;
}
void h_28(double *state, double *unused, double *out_3412809501537689) {
   out_3412809501537689[0] = state[0];
}
void H_28(double *state, double *unused, double *out_5983434613736955638) {
   out_5983434613736955638[0] = 1;
   out_5983434613736955638[1] = 0;
   out_5983434613736955638[2] = 0;
   out_5983434613736955638[3] = 0;
   out_5983434613736955638[4] = 0;
   out_5983434613736955638[5] = 0;
   out_5983434613736955638[6] = 0;
   out_5983434613736955638[7] = 0;
   out_5983434613736955638[8] = 0;
}
void h_31(double *state, double *unused, double *out_8556127952194345812) {
   out_8556127952194345812[0] = state[8];
}
void H_31(double *state, double *unused, double *out_8067915289861805829) {
   out_8067915289861805829[0] = 0;
   out_8067915289861805829[1] = 0;
   out_8067915289861805829[2] = 0;
   out_8067915289861805829[3] = 0;
   out_8067915289861805829[4] = 0;
   out_8067915289861805829[5] = 0;
   out_8067915289861805829[6] = 0;
   out_8067915289861805829[7] = 0;
   out_8067915289861805829[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_1553445728791412940) {
  err_fun(nom_x, delta_x, out_1553445728791412940);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6999435887956597333) {
  inv_err_fun(nom_x, true_x, out_6999435887956597333);
}
void car_H_mod_fun(double *state, double *out_6886426107079341067) {
  H_mod_fun(state, out_6886426107079341067);
}
void car_f_fun(double *state, double dt, double *out_2629482357883749034) {
  f_fun(state,  dt, out_2629482357883749034);
}
void car_F_fun(double *state, double dt, double *out_7990705530243511971) {
  F_fun(state,  dt, out_7990705530243511971);
}
void car_h_25(double *state, double *unused, double *out_1968300025718050649) {
  h_25(state, unused, out_1968300025718050649);
}
void car_H_25(double *state, double *unused, double *out_8037269327984845401) {
  H_25(state, unused, out_8037269327984845401);
}
void car_h_24(double *state, double *unused, double *out_6877344855371313053) {
  h_24(state, unused, out_6877344855371313053);
}
void car_H_24(double *state, double *unused, double *out_3833902939133188114) {
  H_24(state, unused, out_3833902939133188114);
}
void car_h_30(double *state, double *unused, double *out_2125486694069179794) {
  h_30(state, unused, out_2125486694069179794);
}
void car_H_30(double *state, double *unused, double *out_7891141787217457588) {
  H_30(state, unused, out_7891141787217457588);
}
void car_h_26(double *state, double *unused, double *out_2612659355437634136) {
  h_26(state, unused, out_2612659355437634136);
}
void car_H_26(double *state, double *unused, double *out_7104948775963905614) {
  H_26(state, unused, out_7104948775963905614);
}
void car_h_27(double *state, double *unused, double *out_5005086077162383334) {
  h_27(state, unused, out_5005086077162383334);
}
void car_H_27(double *state, double *unused, double *out_5667547716033514371) {
  H_27(state, unused, out_5667547716033514371);
}
void car_h_29(double *state, double *unused, double *out_6670822770196817346) {
  h_29(state, unused, out_6670822770196817346);
}
void car_H_29(double *state, double *unused, double *out_7380910442903065404) {
  H_29(state, unused, out_7380910442903065404);
}
void car_h_28(double *state, double *unused, double *out_3412809501537689) {
  h_28(state, unused, out_3412809501537689);
}
void car_H_28(double *state, double *unused, double *out_5983434613736955638) {
  H_28(state, unused, out_5983434613736955638);
}
void car_h_31(double *state, double *unused, double *out_8556127952194345812) {
  h_31(state, unused, out_8556127952194345812);
}
void car_H_31(double *state, double *unused, double *out_8067915289861805829) {
  H_31(state, unused, out_8067915289861805829);
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
