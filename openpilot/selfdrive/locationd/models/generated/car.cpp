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
void err_fun(double *nom_x, double *delta_x, double *out_8512377944699046552) {
   out_8512377944699046552[0] = delta_x[0] + nom_x[0];
   out_8512377944699046552[1] = delta_x[1] + nom_x[1];
   out_8512377944699046552[2] = delta_x[2] + nom_x[2];
   out_8512377944699046552[3] = delta_x[3] + nom_x[3];
   out_8512377944699046552[4] = delta_x[4] + nom_x[4];
   out_8512377944699046552[5] = delta_x[5] + nom_x[5];
   out_8512377944699046552[6] = delta_x[6] + nom_x[6];
   out_8512377944699046552[7] = delta_x[7] + nom_x[7];
   out_8512377944699046552[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6577279479399491155) {
   out_6577279479399491155[0] = -nom_x[0] + true_x[0];
   out_6577279479399491155[1] = -nom_x[1] + true_x[1];
   out_6577279479399491155[2] = -nom_x[2] + true_x[2];
   out_6577279479399491155[3] = -nom_x[3] + true_x[3];
   out_6577279479399491155[4] = -nom_x[4] + true_x[4];
   out_6577279479399491155[5] = -nom_x[5] + true_x[5];
   out_6577279479399491155[6] = -nom_x[6] + true_x[6];
   out_6577279479399491155[7] = -nom_x[7] + true_x[7];
   out_6577279479399491155[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_7435623757384982931) {
   out_7435623757384982931[0] = 1.0;
   out_7435623757384982931[1] = 0.0;
   out_7435623757384982931[2] = 0.0;
   out_7435623757384982931[3] = 0.0;
   out_7435623757384982931[4] = 0.0;
   out_7435623757384982931[5] = 0.0;
   out_7435623757384982931[6] = 0.0;
   out_7435623757384982931[7] = 0.0;
   out_7435623757384982931[8] = 0.0;
   out_7435623757384982931[9] = 0.0;
   out_7435623757384982931[10] = 1.0;
   out_7435623757384982931[11] = 0.0;
   out_7435623757384982931[12] = 0.0;
   out_7435623757384982931[13] = 0.0;
   out_7435623757384982931[14] = 0.0;
   out_7435623757384982931[15] = 0.0;
   out_7435623757384982931[16] = 0.0;
   out_7435623757384982931[17] = 0.0;
   out_7435623757384982931[18] = 0.0;
   out_7435623757384982931[19] = 0.0;
   out_7435623757384982931[20] = 1.0;
   out_7435623757384982931[21] = 0.0;
   out_7435623757384982931[22] = 0.0;
   out_7435623757384982931[23] = 0.0;
   out_7435623757384982931[24] = 0.0;
   out_7435623757384982931[25] = 0.0;
   out_7435623757384982931[26] = 0.0;
   out_7435623757384982931[27] = 0.0;
   out_7435623757384982931[28] = 0.0;
   out_7435623757384982931[29] = 0.0;
   out_7435623757384982931[30] = 1.0;
   out_7435623757384982931[31] = 0.0;
   out_7435623757384982931[32] = 0.0;
   out_7435623757384982931[33] = 0.0;
   out_7435623757384982931[34] = 0.0;
   out_7435623757384982931[35] = 0.0;
   out_7435623757384982931[36] = 0.0;
   out_7435623757384982931[37] = 0.0;
   out_7435623757384982931[38] = 0.0;
   out_7435623757384982931[39] = 0.0;
   out_7435623757384982931[40] = 1.0;
   out_7435623757384982931[41] = 0.0;
   out_7435623757384982931[42] = 0.0;
   out_7435623757384982931[43] = 0.0;
   out_7435623757384982931[44] = 0.0;
   out_7435623757384982931[45] = 0.0;
   out_7435623757384982931[46] = 0.0;
   out_7435623757384982931[47] = 0.0;
   out_7435623757384982931[48] = 0.0;
   out_7435623757384982931[49] = 0.0;
   out_7435623757384982931[50] = 1.0;
   out_7435623757384982931[51] = 0.0;
   out_7435623757384982931[52] = 0.0;
   out_7435623757384982931[53] = 0.0;
   out_7435623757384982931[54] = 0.0;
   out_7435623757384982931[55] = 0.0;
   out_7435623757384982931[56] = 0.0;
   out_7435623757384982931[57] = 0.0;
   out_7435623757384982931[58] = 0.0;
   out_7435623757384982931[59] = 0.0;
   out_7435623757384982931[60] = 1.0;
   out_7435623757384982931[61] = 0.0;
   out_7435623757384982931[62] = 0.0;
   out_7435623757384982931[63] = 0.0;
   out_7435623757384982931[64] = 0.0;
   out_7435623757384982931[65] = 0.0;
   out_7435623757384982931[66] = 0.0;
   out_7435623757384982931[67] = 0.0;
   out_7435623757384982931[68] = 0.0;
   out_7435623757384982931[69] = 0.0;
   out_7435623757384982931[70] = 1.0;
   out_7435623757384982931[71] = 0.0;
   out_7435623757384982931[72] = 0.0;
   out_7435623757384982931[73] = 0.0;
   out_7435623757384982931[74] = 0.0;
   out_7435623757384982931[75] = 0.0;
   out_7435623757384982931[76] = 0.0;
   out_7435623757384982931[77] = 0.0;
   out_7435623757384982931[78] = 0.0;
   out_7435623757384982931[79] = 0.0;
   out_7435623757384982931[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_5311008828912692131) {
   out_5311008828912692131[0] = state[0];
   out_5311008828912692131[1] = state[1];
   out_5311008828912692131[2] = state[2];
   out_5311008828912692131[3] = state[3];
   out_5311008828912692131[4] = state[4];
   out_5311008828912692131[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_5311008828912692131[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_5311008828912692131[7] = state[7];
   out_5311008828912692131[8] = state[8];
}
void F_fun(double *state, double dt, double *out_9039631374788334585) {
   out_9039631374788334585[0] = 1;
   out_9039631374788334585[1] = 0;
   out_9039631374788334585[2] = 0;
   out_9039631374788334585[3] = 0;
   out_9039631374788334585[4] = 0;
   out_9039631374788334585[5] = 0;
   out_9039631374788334585[6] = 0;
   out_9039631374788334585[7] = 0;
   out_9039631374788334585[8] = 0;
   out_9039631374788334585[9] = 0;
   out_9039631374788334585[10] = 1;
   out_9039631374788334585[11] = 0;
   out_9039631374788334585[12] = 0;
   out_9039631374788334585[13] = 0;
   out_9039631374788334585[14] = 0;
   out_9039631374788334585[15] = 0;
   out_9039631374788334585[16] = 0;
   out_9039631374788334585[17] = 0;
   out_9039631374788334585[18] = 0;
   out_9039631374788334585[19] = 0;
   out_9039631374788334585[20] = 1;
   out_9039631374788334585[21] = 0;
   out_9039631374788334585[22] = 0;
   out_9039631374788334585[23] = 0;
   out_9039631374788334585[24] = 0;
   out_9039631374788334585[25] = 0;
   out_9039631374788334585[26] = 0;
   out_9039631374788334585[27] = 0;
   out_9039631374788334585[28] = 0;
   out_9039631374788334585[29] = 0;
   out_9039631374788334585[30] = 1;
   out_9039631374788334585[31] = 0;
   out_9039631374788334585[32] = 0;
   out_9039631374788334585[33] = 0;
   out_9039631374788334585[34] = 0;
   out_9039631374788334585[35] = 0;
   out_9039631374788334585[36] = 0;
   out_9039631374788334585[37] = 0;
   out_9039631374788334585[38] = 0;
   out_9039631374788334585[39] = 0;
   out_9039631374788334585[40] = 1;
   out_9039631374788334585[41] = 0;
   out_9039631374788334585[42] = 0;
   out_9039631374788334585[43] = 0;
   out_9039631374788334585[44] = 0;
   out_9039631374788334585[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_9039631374788334585[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_9039631374788334585[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_9039631374788334585[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_9039631374788334585[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_9039631374788334585[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_9039631374788334585[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_9039631374788334585[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_9039631374788334585[53] = -9.8100000000000005*dt;
   out_9039631374788334585[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_9039631374788334585[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_9039631374788334585[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_9039631374788334585[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_9039631374788334585[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_9039631374788334585[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_9039631374788334585[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_9039631374788334585[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_9039631374788334585[62] = 0;
   out_9039631374788334585[63] = 0;
   out_9039631374788334585[64] = 0;
   out_9039631374788334585[65] = 0;
   out_9039631374788334585[66] = 0;
   out_9039631374788334585[67] = 0;
   out_9039631374788334585[68] = 0;
   out_9039631374788334585[69] = 0;
   out_9039631374788334585[70] = 1;
   out_9039631374788334585[71] = 0;
   out_9039631374788334585[72] = 0;
   out_9039631374788334585[73] = 0;
   out_9039631374788334585[74] = 0;
   out_9039631374788334585[75] = 0;
   out_9039631374788334585[76] = 0;
   out_9039631374788334585[77] = 0;
   out_9039631374788334585[78] = 0;
   out_9039631374788334585[79] = 0;
   out_9039631374788334585[80] = 1;
}
void h_25(double *state, double *unused, double *out_4369287738774083452) {
   out_4369287738774083452[0] = state[6];
}
void H_25(double *state, double *unused, double *out_1817932090412331448) {
   out_1817932090412331448[0] = 0;
   out_1817932090412331448[1] = 0;
   out_1817932090412331448[2] = 0;
   out_1817932090412331448[3] = 0;
   out_1817932090412331448[4] = 0;
   out_1817932090412331448[5] = 0;
   out_1817932090412331448[6] = 1;
   out_1817932090412331448[7] = 0;
   out_1817932090412331448[8] = 0;
}
void h_24(double *state, double *unused, double *out_4308943977605512295) {
   out_4308943977605512295[0] = state[4];
   out_4308943977605512295[1] = state[5];
}
void H_24(double *state, double *unused, double *out_354717508593168118) {
   out_354717508593168118[0] = 0;
   out_354717508593168118[1] = 0;
   out_354717508593168118[2] = 0;
   out_354717508593168118[3] = 0;
   out_354717508593168118[4] = 1;
   out_354717508593168118[5] = 0;
   out_354717508593168118[6] = 0;
   out_354717508593168118[7] = 0;
   out_354717508593168118[8] = 0;
   out_354717508593168118[9] = 0;
   out_354717508593168118[10] = 0;
   out_354717508593168118[11] = 0;
   out_354717508593168118[12] = 0;
   out_354717508593168118[13] = 0;
   out_354717508593168118[14] = 1;
   out_354717508593168118[15] = 0;
   out_354717508593168118[16] = 0;
   out_354717508593168118[17] = 0;
}
void h_30(double *state, double *unused, double *out_6469084566834324480) {
   out_6469084566834324480[0] = state[4];
}
void H_30(double *state, double *unused, double *out_8734622431903948203) {
   out_8734622431903948203[0] = 0;
   out_8734622431903948203[1] = 0;
   out_8734622431903948203[2] = 0;
   out_8734622431903948203[3] = 0;
   out_8734622431903948203[4] = 1;
   out_8734622431903948203[5] = 0;
   out_8734622431903948203[6] = 0;
   out_8734622431903948203[7] = 0;
   out_8734622431903948203[8] = 0;
}
void h_26(double *state, double *unused, double *out_3581376351729874269) {
   out_3581376351729874269[0] = state[7];
}
void H_26(double *state, double *unused, double *out_1923571228461724776) {
   out_1923571228461724776[0] = 0;
   out_1923571228461724776[1] = 0;
   out_1923571228461724776[2] = 0;
   out_1923571228461724776[3] = 0;
   out_1923571228461724776[4] = 0;
   out_1923571228461724776[5] = 0;
   out_1923571228461724776[6] = 0;
   out_1923571228461724776[7] = 1;
   out_1923571228461724776[8] = 0;
}
void h_27(double *state, double *unused, double *out_4036369080870143201) {
   out_4036369080870143201[0] = state[3];
}
void H_27(double *state, double *unused, double *out_6559859120103523292) {
   out_6559859120103523292[0] = 0;
   out_6559859120103523292[1] = 0;
   out_6559859120103523292[2] = 0;
   out_6559859120103523292[3] = 1;
   out_6559859120103523292[4] = 0;
   out_6559859120103523292[5] = 0;
   out_6559859120103523292[6] = 0;
   out_6559859120103523292[7] = 0;
   out_6559859120103523292[8] = 0;
}
void h_29(double *state, double *unused, double *out_5438333539020600169) {
   out_5438333539020600169[0] = state[1];
}
void H_29(double *state, double *unused, double *out_4846496393233972259) {
   out_4846496393233972259[0] = 0;
   out_4846496393233972259[1] = 1;
   out_4846496393233972259[2] = 0;
   out_4846496393233972259[3] = 0;
   out_4846496393233972259[4] = 0;
   out_4846496393233972259[5] = 0;
   out_4846496393233972259[6] = 0;
   out_4846496393233972259[7] = 0;
   out_4846496393233972259[8] = 0;
}
void h_28(double *state, double *unused, double *out_8317932922113803709) {
   out_8317932922113803709[0] = state[0];
}
void H_28(double *state, double *unused, double *out_235902623835558315) {
   out_235902623835558315[0] = 1;
   out_235902623835558315[1] = 0;
   out_235902623835558315[2] = 0;
   out_235902623835558315[3] = 0;
   out_235902623835558315[4] = 0;
   out_235902623835558315[5] = 0;
   out_235902623835558315[6] = 0;
   out_235902623835558315[7] = 0;
   out_235902623835558315[8] = 0;
}
void h_31(double *state, double *unused, double *out_5547018248750061118) {
   out_5547018248750061118[0] = state[8];
}
void H_31(double *state, double *unused, double *out_1848578052289291876) {
   out_1848578052289291876[0] = 0;
   out_1848578052289291876[1] = 0;
   out_1848578052289291876[2] = 0;
   out_1848578052289291876[3] = 0;
   out_1848578052289291876[4] = 0;
   out_1848578052289291876[5] = 0;
   out_1848578052289291876[6] = 0;
   out_1848578052289291876[7] = 0;
   out_1848578052289291876[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_8512377944699046552) {
  err_fun(nom_x, delta_x, out_8512377944699046552);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6577279479399491155) {
  inv_err_fun(nom_x, true_x, out_6577279479399491155);
}
void car_H_mod_fun(double *state, double *out_7435623757384982931) {
  H_mod_fun(state, out_7435623757384982931);
}
void car_f_fun(double *state, double dt, double *out_5311008828912692131) {
  f_fun(state,  dt, out_5311008828912692131);
}
void car_F_fun(double *state, double dt, double *out_9039631374788334585) {
  F_fun(state,  dt, out_9039631374788334585);
}
void car_h_25(double *state, double *unused, double *out_4369287738774083452) {
  h_25(state, unused, out_4369287738774083452);
}
void car_H_25(double *state, double *unused, double *out_1817932090412331448) {
  H_25(state, unused, out_1817932090412331448);
}
void car_h_24(double *state, double *unused, double *out_4308943977605512295) {
  h_24(state, unused, out_4308943977605512295);
}
void car_H_24(double *state, double *unused, double *out_354717508593168118) {
  H_24(state, unused, out_354717508593168118);
}
void car_h_30(double *state, double *unused, double *out_6469084566834324480) {
  h_30(state, unused, out_6469084566834324480);
}
void car_H_30(double *state, double *unused, double *out_8734622431903948203) {
  H_30(state, unused, out_8734622431903948203);
}
void car_h_26(double *state, double *unused, double *out_3581376351729874269) {
  h_26(state, unused, out_3581376351729874269);
}
void car_H_26(double *state, double *unused, double *out_1923571228461724776) {
  H_26(state, unused, out_1923571228461724776);
}
void car_h_27(double *state, double *unused, double *out_4036369080870143201) {
  h_27(state, unused, out_4036369080870143201);
}
void car_H_27(double *state, double *unused, double *out_6559859120103523292) {
  H_27(state, unused, out_6559859120103523292);
}
void car_h_29(double *state, double *unused, double *out_5438333539020600169) {
  h_29(state, unused, out_5438333539020600169);
}
void car_H_29(double *state, double *unused, double *out_4846496393233972259) {
  H_29(state, unused, out_4846496393233972259);
}
void car_h_28(double *state, double *unused, double *out_8317932922113803709) {
  h_28(state, unused, out_8317932922113803709);
}
void car_H_28(double *state, double *unused, double *out_235902623835558315) {
  H_28(state, unused, out_235902623835558315);
}
void car_h_31(double *state, double *unused, double *out_5547018248750061118) {
  h_31(state, unused, out_5547018248750061118);
}
void car_H_31(double *state, double *unused, double *out_1848578052289291876) {
  H_31(state, unused, out_1848578052289291876);
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
