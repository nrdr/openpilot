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
void err_fun(double *nom_x, double *delta_x, double *out_750716713605572752) {
   out_750716713605572752[0] = delta_x[0] + nom_x[0];
   out_750716713605572752[1] = delta_x[1] + nom_x[1];
   out_750716713605572752[2] = delta_x[2] + nom_x[2];
   out_750716713605572752[3] = delta_x[3] + nom_x[3];
   out_750716713605572752[4] = delta_x[4] + nom_x[4];
   out_750716713605572752[5] = delta_x[5] + nom_x[5];
   out_750716713605572752[6] = delta_x[6] + nom_x[6];
   out_750716713605572752[7] = delta_x[7] + nom_x[7];
   out_750716713605572752[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5646158869804097554) {
   out_5646158869804097554[0] = -nom_x[0] + true_x[0];
   out_5646158869804097554[1] = -nom_x[1] + true_x[1];
   out_5646158869804097554[2] = -nom_x[2] + true_x[2];
   out_5646158869804097554[3] = -nom_x[3] + true_x[3];
   out_5646158869804097554[4] = -nom_x[4] + true_x[4];
   out_5646158869804097554[5] = -nom_x[5] + true_x[5];
   out_5646158869804097554[6] = -nom_x[6] + true_x[6];
   out_5646158869804097554[7] = -nom_x[7] + true_x[7];
   out_5646158869804097554[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_5316612585990664431) {
   out_5316612585990664431[0] = 1.0;
   out_5316612585990664431[1] = 0.0;
   out_5316612585990664431[2] = 0.0;
   out_5316612585990664431[3] = 0.0;
   out_5316612585990664431[4] = 0.0;
   out_5316612585990664431[5] = 0.0;
   out_5316612585990664431[6] = 0.0;
   out_5316612585990664431[7] = 0.0;
   out_5316612585990664431[8] = 0.0;
   out_5316612585990664431[9] = 0.0;
   out_5316612585990664431[10] = 1.0;
   out_5316612585990664431[11] = 0.0;
   out_5316612585990664431[12] = 0.0;
   out_5316612585990664431[13] = 0.0;
   out_5316612585990664431[14] = 0.0;
   out_5316612585990664431[15] = 0.0;
   out_5316612585990664431[16] = 0.0;
   out_5316612585990664431[17] = 0.0;
   out_5316612585990664431[18] = 0.0;
   out_5316612585990664431[19] = 0.0;
   out_5316612585990664431[20] = 1.0;
   out_5316612585990664431[21] = 0.0;
   out_5316612585990664431[22] = 0.0;
   out_5316612585990664431[23] = 0.0;
   out_5316612585990664431[24] = 0.0;
   out_5316612585990664431[25] = 0.0;
   out_5316612585990664431[26] = 0.0;
   out_5316612585990664431[27] = 0.0;
   out_5316612585990664431[28] = 0.0;
   out_5316612585990664431[29] = 0.0;
   out_5316612585990664431[30] = 1.0;
   out_5316612585990664431[31] = 0.0;
   out_5316612585990664431[32] = 0.0;
   out_5316612585990664431[33] = 0.0;
   out_5316612585990664431[34] = 0.0;
   out_5316612585990664431[35] = 0.0;
   out_5316612585990664431[36] = 0.0;
   out_5316612585990664431[37] = 0.0;
   out_5316612585990664431[38] = 0.0;
   out_5316612585990664431[39] = 0.0;
   out_5316612585990664431[40] = 1.0;
   out_5316612585990664431[41] = 0.0;
   out_5316612585990664431[42] = 0.0;
   out_5316612585990664431[43] = 0.0;
   out_5316612585990664431[44] = 0.0;
   out_5316612585990664431[45] = 0.0;
   out_5316612585990664431[46] = 0.0;
   out_5316612585990664431[47] = 0.0;
   out_5316612585990664431[48] = 0.0;
   out_5316612585990664431[49] = 0.0;
   out_5316612585990664431[50] = 1.0;
   out_5316612585990664431[51] = 0.0;
   out_5316612585990664431[52] = 0.0;
   out_5316612585990664431[53] = 0.0;
   out_5316612585990664431[54] = 0.0;
   out_5316612585990664431[55] = 0.0;
   out_5316612585990664431[56] = 0.0;
   out_5316612585990664431[57] = 0.0;
   out_5316612585990664431[58] = 0.0;
   out_5316612585990664431[59] = 0.0;
   out_5316612585990664431[60] = 1.0;
   out_5316612585990664431[61] = 0.0;
   out_5316612585990664431[62] = 0.0;
   out_5316612585990664431[63] = 0.0;
   out_5316612585990664431[64] = 0.0;
   out_5316612585990664431[65] = 0.0;
   out_5316612585990664431[66] = 0.0;
   out_5316612585990664431[67] = 0.0;
   out_5316612585990664431[68] = 0.0;
   out_5316612585990664431[69] = 0.0;
   out_5316612585990664431[70] = 1.0;
   out_5316612585990664431[71] = 0.0;
   out_5316612585990664431[72] = 0.0;
   out_5316612585990664431[73] = 0.0;
   out_5316612585990664431[74] = 0.0;
   out_5316612585990664431[75] = 0.0;
   out_5316612585990664431[76] = 0.0;
   out_5316612585990664431[77] = 0.0;
   out_5316612585990664431[78] = 0.0;
   out_5316612585990664431[79] = 0.0;
   out_5316612585990664431[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_5939119196305302943) {
   out_5939119196305302943[0] = state[0];
   out_5939119196305302943[1] = state[1];
   out_5939119196305302943[2] = state[2];
   out_5939119196305302943[3] = state[3];
   out_5939119196305302943[4] = state[4];
   out_5939119196305302943[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_5939119196305302943[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_5939119196305302943[7] = state[7];
   out_5939119196305302943[8] = state[8];
}
void F_fun(double *state, double dt, double *out_8185668144906963481) {
   out_8185668144906963481[0] = 1;
   out_8185668144906963481[1] = 0;
   out_8185668144906963481[2] = 0;
   out_8185668144906963481[3] = 0;
   out_8185668144906963481[4] = 0;
   out_8185668144906963481[5] = 0;
   out_8185668144906963481[6] = 0;
   out_8185668144906963481[7] = 0;
   out_8185668144906963481[8] = 0;
   out_8185668144906963481[9] = 0;
   out_8185668144906963481[10] = 1;
   out_8185668144906963481[11] = 0;
   out_8185668144906963481[12] = 0;
   out_8185668144906963481[13] = 0;
   out_8185668144906963481[14] = 0;
   out_8185668144906963481[15] = 0;
   out_8185668144906963481[16] = 0;
   out_8185668144906963481[17] = 0;
   out_8185668144906963481[18] = 0;
   out_8185668144906963481[19] = 0;
   out_8185668144906963481[20] = 1;
   out_8185668144906963481[21] = 0;
   out_8185668144906963481[22] = 0;
   out_8185668144906963481[23] = 0;
   out_8185668144906963481[24] = 0;
   out_8185668144906963481[25] = 0;
   out_8185668144906963481[26] = 0;
   out_8185668144906963481[27] = 0;
   out_8185668144906963481[28] = 0;
   out_8185668144906963481[29] = 0;
   out_8185668144906963481[30] = 1;
   out_8185668144906963481[31] = 0;
   out_8185668144906963481[32] = 0;
   out_8185668144906963481[33] = 0;
   out_8185668144906963481[34] = 0;
   out_8185668144906963481[35] = 0;
   out_8185668144906963481[36] = 0;
   out_8185668144906963481[37] = 0;
   out_8185668144906963481[38] = 0;
   out_8185668144906963481[39] = 0;
   out_8185668144906963481[40] = 1;
   out_8185668144906963481[41] = 0;
   out_8185668144906963481[42] = 0;
   out_8185668144906963481[43] = 0;
   out_8185668144906963481[44] = 0;
   out_8185668144906963481[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_8185668144906963481[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_8185668144906963481[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8185668144906963481[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_8185668144906963481[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_8185668144906963481[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_8185668144906963481[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_8185668144906963481[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_8185668144906963481[53] = -9.8100000000000005*dt;
   out_8185668144906963481[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_8185668144906963481[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_8185668144906963481[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8185668144906963481[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8185668144906963481[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_8185668144906963481[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_8185668144906963481[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_8185668144906963481[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_8185668144906963481[62] = 0;
   out_8185668144906963481[63] = 0;
   out_8185668144906963481[64] = 0;
   out_8185668144906963481[65] = 0;
   out_8185668144906963481[66] = 0;
   out_8185668144906963481[67] = 0;
   out_8185668144906963481[68] = 0;
   out_8185668144906963481[69] = 0;
   out_8185668144906963481[70] = 1;
   out_8185668144906963481[71] = 0;
   out_8185668144906963481[72] = 0;
   out_8185668144906963481[73] = 0;
   out_8185668144906963481[74] = 0;
   out_8185668144906963481[75] = 0;
   out_8185668144906963481[76] = 0;
   out_8185668144906963481[77] = 0;
   out_8185668144906963481[78] = 0;
   out_8185668144906963481[79] = 0;
   out_8185668144906963481[80] = 1;
}
void h_25(double *state, double *unused, double *out_2353961728868478623) {
   out_2353961728868478623[0] = state[6];
}
void H_25(double *state, double *unused, double *out_6265733508019146640) {
   out_6265733508019146640[0] = 0;
   out_6265733508019146640[1] = 0;
   out_6265733508019146640[2] = 0;
   out_6265733508019146640[3] = 0;
   out_6265733508019146640[4] = 0;
   out_6265733508019146640[5] = 0;
   out_6265733508019146640[6] = 1;
   out_6265733508019146640[7] = 0;
   out_6265733508019146640[8] = 0;
}
void h_24(double *state, double *unused, double *out_5979104720135345830) {
   out_5979104720135345830[0] = state[4];
   out_5979104720135345830[1] = state[5];
}
void H_24(double *state, double *unused, double *out_5795276025975807916) {
   out_5795276025975807916[0] = 0;
   out_5795276025975807916[1] = 0;
   out_5795276025975807916[2] = 0;
   out_5795276025975807916[3] = 0;
   out_5795276025975807916[4] = 1;
   out_5795276025975807916[5] = 0;
   out_5795276025975807916[6] = 0;
   out_5795276025975807916[7] = 0;
   out_5795276025975807916[8] = 0;
   out_5795276025975807916[9] = 0;
   out_5795276025975807916[10] = 0;
   out_5795276025975807916[11] = 0;
   out_5795276025975807916[12] = 0;
   out_5795276025975807916[13] = 0;
   out_5795276025975807916[14] = 1;
   out_5795276025975807916[15] = 0;
   out_5795276025975807916[16] = 0;
   out_5795276025975807916[17] = 0;
}
void h_30(double *state, double *unused, double *out_1283487799385543727) {
   out_1283487799385543727[0] = state[4];
}
void H_30(double *state, double *unused, double *out_6136394560875906570) {
   out_6136394560875906570[0] = 0;
   out_6136394560875906570[1] = 0;
   out_6136394560875906570[2] = 0;
   out_6136394560875906570[3] = 0;
   out_6136394560875906570[4] = 1;
   out_6136394560875906570[5] = 0;
   out_6136394560875906570[6] = 0;
   out_6136394560875906570[7] = 0;
   out_6136394560875906570[8] = 0;
}
void h_26(double *state, double *unused, double *out_2226997652287206162) {
   out_2226997652287206162[0] = state[7];
}
void H_26(double *state, double *unused, double *out_2524230189145090416) {
   out_2524230189145090416[0] = 0;
   out_2524230189145090416[1] = 0;
   out_2524230189145090416[2] = 0;
   out_2524230189145090416[3] = 0;
   out_2524230189145090416[4] = 0;
   out_2524230189145090416[5] = 0;
   out_2524230189145090416[6] = 0;
   out_2524230189145090416[7] = 1;
   out_2524230189145090416[8] = 0;
}
void h_27(double *state, double *unused, double *out_1596111583707659813) {
   out_1596111583707659813[0] = state[3];
}
void H_27(double *state, double *unused, double *out_3961631249075481659) {
   out_3961631249075481659[0] = 0;
   out_3961631249075481659[1] = 0;
   out_3961631249075481659[2] = 0;
   out_3961631249075481659[3] = 1;
   out_3961631249075481659[4] = 0;
   out_3961631249075481659[5] = 0;
   out_3961631249075481659[6] = 0;
   out_3961631249075481659[7] = 0;
   out_3961631249075481659[8] = 0;
}
void h_29(double *state, double *unused, double *out_6285161067046389372) {
   out_6285161067046389372[0] = state[1];
}
void H_29(double *state, double *unused, double *out_2248268522205930626) {
   out_2248268522205930626[0] = 0;
   out_2248268522205930626[1] = 1;
   out_2248268522205930626[2] = 0;
   out_2248268522205930626[3] = 0;
   out_2248268522205930626[4] = 0;
   out_2248268522205930626[5] = 0;
   out_2248268522205930626[6] = 0;
   out_2248268522205930626[7] = 0;
   out_2248268522205930626[8] = 0;
}
void h_28(double *state, double *unused, double *out_992795699031182296) {
   out_992795699031182296[0] = state[0];
}
void H_28(double *state, double *unused, double *out_2834130494863599948) {
   out_2834130494863599948[0] = 1;
   out_2834130494863599948[1] = 0;
   out_2834130494863599948[2] = 0;
   out_2834130494863599948[3] = 0;
   out_2834130494863599948[4] = 0;
   out_2834130494863599948[5] = 0;
   out_2834130494863599948[6] = 0;
   out_2834130494863599948[7] = 0;
   out_2834130494863599948[8] = 0;
}
void h_31(double *state, double *unused, double *out_8901233231985561197) {
   out_8901233231985561197[0] = state[8];
}
void H_31(double *state, double *unused, double *out_6296379469896107068) {
   out_6296379469896107068[0] = 0;
   out_6296379469896107068[1] = 0;
   out_6296379469896107068[2] = 0;
   out_6296379469896107068[3] = 0;
   out_6296379469896107068[4] = 0;
   out_6296379469896107068[5] = 0;
   out_6296379469896107068[6] = 0;
   out_6296379469896107068[7] = 0;
   out_6296379469896107068[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_750716713605572752) {
  err_fun(nom_x, delta_x, out_750716713605572752);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5646158869804097554) {
  inv_err_fun(nom_x, true_x, out_5646158869804097554);
}
void car_H_mod_fun(double *state, double *out_5316612585990664431) {
  H_mod_fun(state, out_5316612585990664431);
}
void car_f_fun(double *state, double dt, double *out_5939119196305302943) {
  f_fun(state,  dt, out_5939119196305302943);
}
void car_F_fun(double *state, double dt, double *out_8185668144906963481) {
  F_fun(state,  dt, out_8185668144906963481);
}
void car_h_25(double *state, double *unused, double *out_2353961728868478623) {
  h_25(state, unused, out_2353961728868478623);
}
void car_H_25(double *state, double *unused, double *out_6265733508019146640) {
  H_25(state, unused, out_6265733508019146640);
}
void car_h_24(double *state, double *unused, double *out_5979104720135345830) {
  h_24(state, unused, out_5979104720135345830);
}
void car_H_24(double *state, double *unused, double *out_5795276025975807916) {
  H_24(state, unused, out_5795276025975807916);
}
void car_h_30(double *state, double *unused, double *out_1283487799385543727) {
  h_30(state, unused, out_1283487799385543727);
}
void car_H_30(double *state, double *unused, double *out_6136394560875906570) {
  H_30(state, unused, out_6136394560875906570);
}
void car_h_26(double *state, double *unused, double *out_2226997652287206162) {
  h_26(state, unused, out_2226997652287206162);
}
void car_H_26(double *state, double *unused, double *out_2524230189145090416) {
  H_26(state, unused, out_2524230189145090416);
}
void car_h_27(double *state, double *unused, double *out_1596111583707659813) {
  h_27(state, unused, out_1596111583707659813);
}
void car_H_27(double *state, double *unused, double *out_3961631249075481659) {
  H_27(state, unused, out_3961631249075481659);
}
void car_h_29(double *state, double *unused, double *out_6285161067046389372) {
  h_29(state, unused, out_6285161067046389372);
}
void car_H_29(double *state, double *unused, double *out_2248268522205930626) {
  H_29(state, unused, out_2248268522205930626);
}
void car_h_28(double *state, double *unused, double *out_992795699031182296) {
  h_28(state, unused, out_992795699031182296);
}
void car_H_28(double *state, double *unused, double *out_2834130494863599948) {
  H_28(state, unused, out_2834130494863599948);
}
void car_h_31(double *state, double *unused, double *out_8901233231985561197) {
  h_31(state, unused, out_8901233231985561197);
}
void car_H_31(double *state, double *unused, double *out_6296379469896107068) {
  H_31(state, unused, out_6296379469896107068);
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
