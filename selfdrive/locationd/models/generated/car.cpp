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
void err_fun(double *nom_x, double *delta_x, double *out_1839793480075446944) {
   out_1839793480075446944[0] = delta_x[0] + nom_x[0];
   out_1839793480075446944[1] = delta_x[1] + nom_x[1];
   out_1839793480075446944[2] = delta_x[2] + nom_x[2];
   out_1839793480075446944[3] = delta_x[3] + nom_x[3];
   out_1839793480075446944[4] = delta_x[4] + nom_x[4];
   out_1839793480075446944[5] = delta_x[5] + nom_x[5];
   out_1839793480075446944[6] = delta_x[6] + nom_x[6];
   out_1839793480075446944[7] = delta_x[7] + nom_x[7];
   out_1839793480075446944[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6348115372523587908) {
   out_6348115372523587908[0] = -nom_x[0] + true_x[0];
   out_6348115372523587908[1] = -nom_x[1] + true_x[1];
   out_6348115372523587908[2] = -nom_x[2] + true_x[2];
   out_6348115372523587908[3] = -nom_x[3] + true_x[3];
   out_6348115372523587908[4] = -nom_x[4] + true_x[4];
   out_6348115372523587908[5] = -nom_x[5] + true_x[5];
   out_6348115372523587908[6] = -nom_x[6] + true_x[6];
   out_6348115372523587908[7] = -nom_x[7] + true_x[7];
   out_6348115372523587908[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_3044097129650960971) {
   out_3044097129650960971[0] = 1.0;
   out_3044097129650960971[1] = 0.0;
   out_3044097129650960971[2] = 0.0;
   out_3044097129650960971[3] = 0.0;
   out_3044097129650960971[4] = 0.0;
   out_3044097129650960971[5] = 0.0;
   out_3044097129650960971[6] = 0.0;
   out_3044097129650960971[7] = 0.0;
   out_3044097129650960971[8] = 0.0;
   out_3044097129650960971[9] = 0.0;
   out_3044097129650960971[10] = 1.0;
   out_3044097129650960971[11] = 0.0;
   out_3044097129650960971[12] = 0.0;
   out_3044097129650960971[13] = 0.0;
   out_3044097129650960971[14] = 0.0;
   out_3044097129650960971[15] = 0.0;
   out_3044097129650960971[16] = 0.0;
   out_3044097129650960971[17] = 0.0;
   out_3044097129650960971[18] = 0.0;
   out_3044097129650960971[19] = 0.0;
   out_3044097129650960971[20] = 1.0;
   out_3044097129650960971[21] = 0.0;
   out_3044097129650960971[22] = 0.0;
   out_3044097129650960971[23] = 0.0;
   out_3044097129650960971[24] = 0.0;
   out_3044097129650960971[25] = 0.0;
   out_3044097129650960971[26] = 0.0;
   out_3044097129650960971[27] = 0.0;
   out_3044097129650960971[28] = 0.0;
   out_3044097129650960971[29] = 0.0;
   out_3044097129650960971[30] = 1.0;
   out_3044097129650960971[31] = 0.0;
   out_3044097129650960971[32] = 0.0;
   out_3044097129650960971[33] = 0.0;
   out_3044097129650960971[34] = 0.0;
   out_3044097129650960971[35] = 0.0;
   out_3044097129650960971[36] = 0.0;
   out_3044097129650960971[37] = 0.0;
   out_3044097129650960971[38] = 0.0;
   out_3044097129650960971[39] = 0.0;
   out_3044097129650960971[40] = 1.0;
   out_3044097129650960971[41] = 0.0;
   out_3044097129650960971[42] = 0.0;
   out_3044097129650960971[43] = 0.0;
   out_3044097129650960971[44] = 0.0;
   out_3044097129650960971[45] = 0.0;
   out_3044097129650960971[46] = 0.0;
   out_3044097129650960971[47] = 0.0;
   out_3044097129650960971[48] = 0.0;
   out_3044097129650960971[49] = 0.0;
   out_3044097129650960971[50] = 1.0;
   out_3044097129650960971[51] = 0.0;
   out_3044097129650960971[52] = 0.0;
   out_3044097129650960971[53] = 0.0;
   out_3044097129650960971[54] = 0.0;
   out_3044097129650960971[55] = 0.0;
   out_3044097129650960971[56] = 0.0;
   out_3044097129650960971[57] = 0.0;
   out_3044097129650960971[58] = 0.0;
   out_3044097129650960971[59] = 0.0;
   out_3044097129650960971[60] = 1.0;
   out_3044097129650960971[61] = 0.0;
   out_3044097129650960971[62] = 0.0;
   out_3044097129650960971[63] = 0.0;
   out_3044097129650960971[64] = 0.0;
   out_3044097129650960971[65] = 0.0;
   out_3044097129650960971[66] = 0.0;
   out_3044097129650960971[67] = 0.0;
   out_3044097129650960971[68] = 0.0;
   out_3044097129650960971[69] = 0.0;
   out_3044097129650960971[70] = 1.0;
   out_3044097129650960971[71] = 0.0;
   out_3044097129650960971[72] = 0.0;
   out_3044097129650960971[73] = 0.0;
   out_3044097129650960971[74] = 0.0;
   out_3044097129650960971[75] = 0.0;
   out_3044097129650960971[76] = 0.0;
   out_3044097129650960971[77] = 0.0;
   out_3044097129650960971[78] = 0.0;
   out_3044097129650960971[79] = 0.0;
   out_3044097129650960971[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_8786810168446307735) {
   out_8786810168446307735[0] = state[0];
   out_8786810168446307735[1] = state[1];
   out_8786810168446307735[2] = state[2];
   out_8786810168446307735[3] = state[3];
   out_8786810168446307735[4] = state[4];
   out_8786810168446307735[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_8786810168446307735[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_8786810168446307735[7] = state[7];
   out_8786810168446307735[8] = state[8];
}
void F_fun(double *state, double dt, double *out_781864656834108608) {
   out_781864656834108608[0] = 1;
   out_781864656834108608[1] = 0;
   out_781864656834108608[2] = 0;
   out_781864656834108608[3] = 0;
   out_781864656834108608[4] = 0;
   out_781864656834108608[5] = 0;
   out_781864656834108608[6] = 0;
   out_781864656834108608[7] = 0;
   out_781864656834108608[8] = 0;
   out_781864656834108608[9] = 0;
   out_781864656834108608[10] = 1;
   out_781864656834108608[11] = 0;
   out_781864656834108608[12] = 0;
   out_781864656834108608[13] = 0;
   out_781864656834108608[14] = 0;
   out_781864656834108608[15] = 0;
   out_781864656834108608[16] = 0;
   out_781864656834108608[17] = 0;
   out_781864656834108608[18] = 0;
   out_781864656834108608[19] = 0;
   out_781864656834108608[20] = 1;
   out_781864656834108608[21] = 0;
   out_781864656834108608[22] = 0;
   out_781864656834108608[23] = 0;
   out_781864656834108608[24] = 0;
   out_781864656834108608[25] = 0;
   out_781864656834108608[26] = 0;
   out_781864656834108608[27] = 0;
   out_781864656834108608[28] = 0;
   out_781864656834108608[29] = 0;
   out_781864656834108608[30] = 1;
   out_781864656834108608[31] = 0;
   out_781864656834108608[32] = 0;
   out_781864656834108608[33] = 0;
   out_781864656834108608[34] = 0;
   out_781864656834108608[35] = 0;
   out_781864656834108608[36] = 0;
   out_781864656834108608[37] = 0;
   out_781864656834108608[38] = 0;
   out_781864656834108608[39] = 0;
   out_781864656834108608[40] = 1;
   out_781864656834108608[41] = 0;
   out_781864656834108608[42] = 0;
   out_781864656834108608[43] = 0;
   out_781864656834108608[44] = 0;
   out_781864656834108608[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_781864656834108608[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_781864656834108608[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_781864656834108608[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_781864656834108608[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_781864656834108608[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_781864656834108608[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_781864656834108608[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_781864656834108608[53] = -9.8100000000000005*dt;
   out_781864656834108608[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_781864656834108608[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_781864656834108608[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_781864656834108608[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_781864656834108608[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_781864656834108608[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_781864656834108608[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_781864656834108608[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_781864656834108608[62] = 0;
   out_781864656834108608[63] = 0;
   out_781864656834108608[64] = 0;
   out_781864656834108608[65] = 0;
   out_781864656834108608[66] = 0;
   out_781864656834108608[67] = 0;
   out_781864656834108608[68] = 0;
   out_781864656834108608[69] = 0;
   out_781864656834108608[70] = 1;
   out_781864656834108608[71] = 0;
   out_781864656834108608[72] = 0;
   out_781864656834108608[73] = 0;
   out_781864656834108608[74] = 0;
   out_781864656834108608[75] = 0;
   out_781864656834108608[76] = 0;
   out_781864656834108608[77] = 0;
   out_781864656834108608[78] = 0;
   out_781864656834108608[79] = 0;
   out_781864656834108608[80] = 1;
}
void h_25(double *state, double *unused, double *out_4107541327329523197) {
   out_4107541327329523197[0] = state[6];
}
void H_25(double *state, double *unused, double *out_762758392799024188) {
   out_762758392799024188[0] = 0;
   out_762758392799024188[1] = 0;
   out_762758392799024188[2] = 0;
   out_762758392799024188[3] = 0;
   out_762758392799024188[4] = 0;
   out_762758392799024188[5] = 0;
   out_762758392799024188[6] = 1;
   out_762758392799024188[7] = 0;
   out_762758392799024188[8] = 0;
}
void h_24(double *state, double *unused, double *out_2286857433249008733) {
   out_2286857433249008733[0] = state[4];
   out_2286857433249008733[1] = state[5];
}
void H_24(double *state, double *unused, double *out_1462949391179844374) {
   out_1462949391179844374[0] = 0;
   out_1462949391179844374[1] = 0;
   out_1462949391179844374[2] = 0;
   out_1462949391179844374[3] = 0;
   out_1462949391179844374[4] = 1;
   out_1462949391179844374[5] = 0;
   out_1462949391179844374[6] = 0;
   out_1462949391179844374[7] = 0;
   out_1462949391179844374[8] = 0;
   out_1462949391179844374[9] = 0;
   out_1462949391179844374[10] = 0;
   out_1462949391179844374[11] = 0;
   out_1462949391179844374[12] = 0;
   out_1462949391179844374[13] = 0;
   out_1462949391179844374[14] = 1;
   out_1462949391179844374[15] = 0;
   out_1462949391179844374[16] = 0;
   out_1462949391179844374[17] = 0;
}
void h_30(double *state, double *unused, double *out_3655723929491149244) {
   out_3655723929491149244[0] = state[4];
}
void H_30(double *state, double *unused, double *out_6153931948692592567) {
   out_6153931948692592567[0] = 0;
   out_6153931948692592567[1] = 0;
   out_6153931948692592567[2] = 0;
   out_6153931948692592567[3] = 0;
   out_6153931948692592567[4] = 1;
   out_6153931948692592567[5] = 0;
   out_6153931948692592567[6] = 0;
   out_6153931948692592567[7] = 0;
   out_6153931948692592567[8] = 0;
}
void h_26(double *state, double *unused, double *out_8912734656659687284) {
   out_8912734656659687284[0] = state[7];
}
void H_26(double *state, double *unused, double *out_4504261711673080412) {
   out_4504261711673080412[0] = 0;
   out_4504261711673080412[1] = 0;
   out_4504261711673080412[2] = 0;
   out_4504261711673080412[3] = 0;
   out_4504261711673080412[4] = 0;
   out_4504261711673080412[5] = 0;
   out_4504261711673080412[6] = 0;
   out_4504261711673080412[7] = 1;
   out_4504261711673080412[8] = 0;
}
void h_27(double *state, double *unused, double *out_5621365826511336093) {
   out_5621365826511336093[0] = state[3];
}
void H_27(double *state, double *unused, double *out_3066860651742689169) {
   out_3066860651742689169[0] = 0;
   out_3066860651742689169[1] = 0;
   out_3066860651742689169[2] = 0;
   out_3066860651742689169[3] = 1;
   out_3066860651742689169[4] = 0;
   out_3066860651742689169[5] = 0;
   out_3066860651742689169[6] = 0;
   out_3066860651742689169[7] = 0;
   out_3066860651742689169[8] = 0;
}
void h_29(double *state, double *unused, double *out_5364819482949327198) {
   out_5364819482949327198[0] = state[1];
}
void H_29(double *state, double *unused, double *out_381865995627872074) {
   out_381865995627872074[0] = 0;
   out_381865995627872074[1] = 1;
   out_381865995627872074[2] = 0;
   out_381865995627872074[3] = 0;
   out_381865995627872074[4] = 0;
   out_381865995627872074[5] = 0;
   out_381865995627872074[6] = 0;
   out_381865995627872074[7] = 0;
   out_381865995627872074[8] = 0;
}
void h_28(double *state, double *unused, double *out_619692558850490448) {
   out_619692558850490448[0] = state[0];
}
void H_28(double *state, double *unused, double *out_1581764275937454177) {
   out_1581764275937454177[0] = 1;
   out_1581764275937454177[1] = 0;
   out_1581764275937454177[2] = 0;
   out_1581764275937454177[3] = 0;
   out_1581764275937454177[4] = 0;
   out_1581764275937454177[5] = 0;
   out_1581764275937454177[6] = 0;
   out_1581764275937454177[7] = 0;
   out_1581764275937454177[8] = 0;
}
void h_31(double *state, double *unused, double *out_3773731323424525988) {
   out_3773731323424525988[0] = state[8];
}
void H_31(double *state, double *unused, double *out_732112430922063760) {
   out_732112430922063760[0] = 0;
   out_732112430922063760[1] = 0;
   out_732112430922063760[2] = 0;
   out_732112430922063760[3] = 0;
   out_732112430922063760[4] = 0;
   out_732112430922063760[5] = 0;
   out_732112430922063760[6] = 0;
   out_732112430922063760[7] = 0;
   out_732112430922063760[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_1839793480075446944) {
  err_fun(nom_x, delta_x, out_1839793480075446944);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6348115372523587908) {
  inv_err_fun(nom_x, true_x, out_6348115372523587908);
}
void car_H_mod_fun(double *state, double *out_3044097129650960971) {
  H_mod_fun(state, out_3044097129650960971);
}
void car_f_fun(double *state, double dt, double *out_8786810168446307735) {
  f_fun(state,  dt, out_8786810168446307735);
}
void car_F_fun(double *state, double dt, double *out_781864656834108608) {
  F_fun(state,  dt, out_781864656834108608);
}
void car_h_25(double *state, double *unused, double *out_4107541327329523197) {
  h_25(state, unused, out_4107541327329523197);
}
void car_H_25(double *state, double *unused, double *out_762758392799024188) {
  H_25(state, unused, out_762758392799024188);
}
void car_h_24(double *state, double *unused, double *out_2286857433249008733) {
  h_24(state, unused, out_2286857433249008733);
}
void car_H_24(double *state, double *unused, double *out_1462949391179844374) {
  H_24(state, unused, out_1462949391179844374);
}
void car_h_30(double *state, double *unused, double *out_3655723929491149244) {
  h_30(state, unused, out_3655723929491149244);
}
void car_H_30(double *state, double *unused, double *out_6153931948692592567) {
  H_30(state, unused, out_6153931948692592567);
}
void car_h_26(double *state, double *unused, double *out_8912734656659687284) {
  h_26(state, unused, out_8912734656659687284);
}
void car_H_26(double *state, double *unused, double *out_4504261711673080412) {
  H_26(state, unused, out_4504261711673080412);
}
void car_h_27(double *state, double *unused, double *out_5621365826511336093) {
  h_27(state, unused, out_5621365826511336093);
}
void car_H_27(double *state, double *unused, double *out_3066860651742689169) {
  H_27(state, unused, out_3066860651742689169);
}
void car_h_29(double *state, double *unused, double *out_5364819482949327198) {
  h_29(state, unused, out_5364819482949327198);
}
void car_H_29(double *state, double *unused, double *out_381865995627872074) {
  H_29(state, unused, out_381865995627872074);
}
void car_h_28(double *state, double *unused, double *out_619692558850490448) {
  h_28(state, unused, out_619692558850490448);
}
void car_H_28(double *state, double *unused, double *out_1581764275937454177) {
  H_28(state, unused, out_1581764275937454177);
}
void car_h_31(double *state, double *unused, double *out_3773731323424525988) {
  h_31(state, unused, out_3773731323424525988);
}
void car_H_31(double *state, double *unused, double *out_732112430922063760) {
  H_31(state, unused, out_732112430922063760);
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
