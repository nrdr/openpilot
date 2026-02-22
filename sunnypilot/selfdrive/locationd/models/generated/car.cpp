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
void err_fun(double *nom_x, double *delta_x, double *out_5090167770449267747) {
   out_5090167770449267747[0] = delta_x[0] + nom_x[0];
   out_5090167770449267747[1] = delta_x[1] + nom_x[1];
   out_5090167770449267747[2] = delta_x[2] + nom_x[2];
   out_5090167770449267747[3] = delta_x[3] + nom_x[3];
   out_5090167770449267747[4] = delta_x[4] + nom_x[4];
   out_5090167770449267747[5] = delta_x[5] + nom_x[5];
   out_5090167770449267747[6] = delta_x[6] + nom_x[6];
   out_5090167770449267747[7] = delta_x[7] + nom_x[7];
   out_5090167770449267747[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_2214359751135662810) {
   out_2214359751135662810[0] = -nom_x[0] + true_x[0];
   out_2214359751135662810[1] = -nom_x[1] + true_x[1];
   out_2214359751135662810[2] = -nom_x[2] + true_x[2];
   out_2214359751135662810[3] = -nom_x[3] + true_x[3];
   out_2214359751135662810[4] = -nom_x[4] + true_x[4];
   out_2214359751135662810[5] = -nom_x[5] + true_x[5];
   out_2214359751135662810[6] = -nom_x[6] + true_x[6];
   out_2214359751135662810[7] = -nom_x[7] + true_x[7];
   out_2214359751135662810[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_8824828869686346636) {
   out_8824828869686346636[0] = 1.0;
   out_8824828869686346636[1] = 0.0;
   out_8824828869686346636[2] = 0.0;
   out_8824828869686346636[3] = 0.0;
   out_8824828869686346636[4] = 0.0;
   out_8824828869686346636[5] = 0.0;
   out_8824828869686346636[6] = 0.0;
   out_8824828869686346636[7] = 0.0;
   out_8824828869686346636[8] = 0.0;
   out_8824828869686346636[9] = 0.0;
   out_8824828869686346636[10] = 1.0;
   out_8824828869686346636[11] = 0.0;
   out_8824828869686346636[12] = 0.0;
   out_8824828869686346636[13] = 0.0;
   out_8824828869686346636[14] = 0.0;
   out_8824828869686346636[15] = 0.0;
   out_8824828869686346636[16] = 0.0;
   out_8824828869686346636[17] = 0.0;
   out_8824828869686346636[18] = 0.0;
   out_8824828869686346636[19] = 0.0;
   out_8824828869686346636[20] = 1.0;
   out_8824828869686346636[21] = 0.0;
   out_8824828869686346636[22] = 0.0;
   out_8824828869686346636[23] = 0.0;
   out_8824828869686346636[24] = 0.0;
   out_8824828869686346636[25] = 0.0;
   out_8824828869686346636[26] = 0.0;
   out_8824828869686346636[27] = 0.0;
   out_8824828869686346636[28] = 0.0;
   out_8824828869686346636[29] = 0.0;
   out_8824828869686346636[30] = 1.0;
   out_8824828869686346636[31] = 0.0;
   out_8824828869686346636[32] = 0.0;
   out_8824828869686346636[33] = 0.0;
   out_8824828869686346636[34] = 0.0;
   out_8824828869686346636[35] = 0.0;
   out_8824828869686346636[36] = 0.0;
   out_8824828869686346636[37] = 0.0;
   out_8824828869686346636[38] = 0.0;
   out_8824828869686346636[39] = 0.0;
   out_8824828869686346636[40] = 1.0;
   out_8824828869686346636[41] = 0.0;
   out_8824828869686346636[42] = 0.0;
   out_8824828869686346636[43] = 0.0;
   out_8824828869686346636[44] = 0.0;
   out_8824828869686346636[45] = 0.0;
   out_8824828869686346636[46] = 0.0;
   out_8824828869686346636[47] = 0.0;
   out_8824828869686346636[48] = 0.0;
   out_8824828869686346636[49] = 0.0;
   out_8824828869686346636[50] = 1.0;
   out_8824828869686346636[51] = 0.0;
   out_8824828869686346636[52] = 0.0;
   out_8824828869686346636[53] = 0.0;
   out_8824828869686346636[54] = 0.0;
   out_8824828869686346636[55] = 0.0;
   out_8824828869686346636[56] = 0.0;
   out_8824828869686346636[57] = 0.0;
   out_8824828869686346636[58] = 0.0;
   out_8824828869686346636[59] = 0.0;
   out_8824828869686346636[60] = 1.0;
   out_8824828869686346636[61] = 0.0;
   out_8824828869686346636[62] = 0.0;
   out_8824828869686346636[63] = 0.0;
   out_8824828869686346636[64] = 0.0;
   out_8824828869686346636[65] = 0.0;
   out_8824828869686346636[66] = 0.0;
   out_8824828869686346636[67] = 0.0;
   out_8824828869686346636[68] = 0.0;
   out_8824828869686346636[69] = 0.0;
   out_8824828869686346636[70] = 1.0;
   out_8824828869686346636[71] = 0.0;
   out_8824828869686346636[72] = 0.0;
   out_8824828869686346636[73] = 0.0;
   out_8824828869686346636[74] = 0.0;
   out_8824828869686346636[75] = 0.0;
   out_8824828869686346636[76] = 0.0;
   out_8824828869686346636[77] = 0.0;
   out_8824828869686346636[78] = 0.0;
   out_8824828869686346636[79] = 0.0;
   out_8824828869686346636[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_7390949759775601083) {
   out_7390949759775601083[0] = state[0];
   out_7390949759775601083[1] = state[1];
   out_7390949759775601083[2] = state[2];
   out_7390949759775601083[3] = state[3];
   out_7390949759775601083[4] = state[4];
   out_7390949759775601083[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_7390949759775601083[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_7390949759775601083[7] = state[7];
   out_7390949759775601083[8] = state[8];
}
void F_fun(double *state, double dt, double *out_5580992667421940842) {
   out_5580992667421940842[0] = 1;
   out_5580992667421940842[1] = 0;
   out_5580992667421940842[2] = 0;
   out_5580992667421940842[3] = 0;
   out_5580992667421940842[4] = 0;
   out_5580992667421940842[5] = 0;
   out_5580992667421940842[6] = 0;
   out_5580992667421940842[7] = 0;
   out_5580992667421940842[8] = 0;
   out_5580992667421940842[9] = 0;
   out_5580992667421940842[10] = 1;
   out_5580992667421940842[11] = 0;
   out_5580992667421940842[12] = 0;
   out_5580992667421940842[13] = 0;
   out_5580992667421940842[14] = 0;
   out_5580992667421940842[15] = 0;
   out_5580992667421940842[16] = 0;
   out_5580992667421940842[17] = 0;
   out_5580992667421940842[18] = 0;
   out_5580992667421940842[19] = 0;
   out_5580992667421940842[20] = 1;
   out_5580992667421940842[21] = 0;
   out_5580992667421940842[22] = 0;
   out_5580992667421940842[23] = 0;
   out_5580992667421940842[24] = 0;
   out_5580992667421940842[25] = 0;
   out_5580992667421940842[26] = 0;
   out_5580992667421940842[27] = 0;
   out_5580992667421940842[28] = 0;
   out_5580992667421940842[29] = 0;
   out_5580992667421940842[30] = 1;
   out_5580992667421940842[31] = 0;
   out_5580992667421940842[32] = 0;
   out_5580992667421940842[33] = 0;
   out_5580992667421940842[34] = 0;
   out_5580992667421940842[35] = 0;
   out_5580992667421940842[36] = 0;
   out_5580992667421940842[37] = 0;
   out_5580992667421940842[38] = 0;
   out_5580992667421940842[39] = 0;
   out_5580992667421940842[40] = 1;
   out_5580992667421940842[41] = 0;
   out_5580992667421940842[42] = 0;
   out_5580992667421940842[43] = 0;
   out_5580992667421940842[44] = 0;
   out_5580992667421940842[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_5580992667421940842[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_5580992667421940842[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5580992667421940842[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_5580992667421940842[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_5580992667421940842[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_5580992667421940842[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_5580992667421940842[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_5580992667421940842[53] = -9.8100000000000005*dt;
   out_5580992667421940842[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_5580992667421940842[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_5580992667421940842[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5580992667421940842[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5580992667421940842[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_5580992667421940842[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_5580992667421940842[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_5580992667421940842[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_5580992667421940842[62] = 0;
   out_5580992667421940842[63] = 0;
   out_5580992667421940842[64] = 0;
   out_5580992667421940842[65] = 0;
   out_5580992667421940842[66] = 0;
   out_5580992667421940842[67] = 0;
   out_5580992667421940842[68] = 0;
   out_5580992667421940842[69] = 0;
   out_5580992667421940842[70] = 1;
   out_5580992667421940842[71] = 0;
   out_5580992667421940842[72] = 0;
   out_5580992667421940842[73] = 0;
   out_5580992667421940842[74] = 0;
   out_5580992667421940842[75] = 0;
   out_5580992667421940842[76] = 0;
   out_5580992667421940842[77] = 0;
   out_5580992667421940842[78] = 0;
   out_5580992667421940842[79] = 0;
   out_5580992667421940842[80] = 1;
}
void h_25(double *state, double *unused, double *out_873146183491989349) {
   out_873146183491989349[0] = state[6];
}
void H_25(double *state, double *unused, double *out_368359356225890601) {
   out_368359356225890601[0] = 0;
   out_368359356225890601[1] = 0;
   out_368359356225890601[2] = 0;
   out_368359356225890601[3] = 0;
   out_368359356225890601[4] = 0;
   out_368359356225890601[5] = 0;
   out_368359356225890601[6] = 1;
   out_368359356225890601[7] = 0;
   out_368359356225890601[8] = 0;
}
void h_24(double *state, double *unused, double *out_838029550239282357) {
   out_838029550239282357[0] = state[4];
   out_838029550239282357[1] = state[5];
}
void H_24(double *state, double *unused, double *out_6285846101882295156) {
   out_6285846101882295156[0] = 0;
   out_6285846101882295156[1] = 0;
   out_6285846101882295156[2] = 0;
   out_6285846101882295156[3] = 0;
   out_6285846101882295156[4] = 1;
   out_6285846101882295156[5] = 0;
   out_6285846101882295156[6] = 0;
   out_6285846101882295156[7] = 0;
   out_6285846101882295156[8] = 0;
   out_6285846101882295156[9] = 0;
   out_6285846101882295156[10] = 0;
   out_6285846101882295156[11] = 0;
   out_6285846101882295156[12] = 0;
   out_6285846101882295156[13] = 0;
   out_6285846101882295156[14] = 1;
   out_6285846101882295156[15] = 0;
   out_6285846101882295156[16] = 0;
   out_6285846101882295156[17] = 0;
}
void h_30(double *state, double *unused, double *out_4126629357105742333) {
   out_4126629357105742333[0] = state[4];
}
void H_30(double *state, double *unused, double *out_4896055686353498799) {
   out_4896055686353498799[0] = 0;
   out_4896055686353498799[1] = 0;
   out_4896055686353498799[2] = 0;
   out_4896055686353498799[3] = 0;
   out_4896055686353498799[4] = 1;
   out_4896055686353498799[5] = 0;
   out_4896055686353498799[6] = 0;
   out_4896055686353498799[7] = 0;
   out_4896055686353498799[8] = 0;
}
void h_26(double *state, double *unused, double *out_4954179189956699152) {
   out_4954179189956699152[0] = state[7];
}
void H_26(double *state, double *unused, double *out_4109862675099946825) {
   out_4109862675099946825[0] = 0;
   out_4109862675099946825[1] = 0;
   out_4109862675099946825[2] = 0;
   out_4109862675099946825[3] = 0;
   out_4109862675099946825[4] = 0;
   out_4109862675099946825[5] = 0;
   out_4109862675099946825[6] = 0;
   out_4109862675099946825[7] = 1;
   out_4109862675099946825[8] = 0;
}
void h_27(double *state, double *unused, double *out_1476462068168466866) {
   out_1476462068168466866[0] = state[3];
}
void H_27(double *state, double *unused, double *out_7070818998153923710) {
   out_7070818998153923710[0] = 0;
   out_7070818998153923710[1] = 0;
   out_7070818998153923710[2] = 0;
   out_7070818998153923710[3] = 1;
   out_7070818998153923710[4] = 0;
   out_7070818998153923710[5] = 0;
   out_7070818998153923710[6] = 0;
   out_7070818998153923710[7] = 0;
   out_7070818998153923710[8] = 0;
}
void h_29(double *state, double *unused, double *out_5113911596422489216) {
   out_5113911596422489216[0] = state[1];
}
void H_29(double *state, double *unused, double *out_4385824342039106615) {
   out_4385824342039106615[0] = 0;
   out_4385824342039106615[1] = 1;
   out_4385824342039106615[2] = 0;
   out_4385824342039106615[3] = 0;
   out_4385824342039106615[4] = 0;
   out_4385824342039106615[5] = 0;
   out_4385824342039106615[6] = 0;
   out_4385824342039106615[7] = 0;
   out_4385824342039106615[8] = 0;
}
void h_28(double *state, double *unused, double *out_1127943252640230785) {
   out_1127943252640230785[0] = state[0];
}
void H_28(double *state, double *unused, double *out_8978520714600914427) {
   out_8978520714600914427[0] = 1;
   out_8978520714600914427[1] = 0;
   out_8978520714600914427[2] = 0;
   out_8978520714600914427[3] = 0;
   out_8978520714600914427[4] = 0;
   out_8978520714600914427[5] = 0;
   out_8978520714600914427[6] = 0;
   out_8978520714600914427[7] = 0;
   out_8978520714600914427[8] = 0;
}
void h_31(double *state, double *unused, double *out_2764303344762033001) {
   out_2764303344762033001[0] = state[8];
}
void H_31(double *state, double *unused, double *out_4736070777333298301) {
   out_4736070777333298301[0] = 0;
   out_4736070777333298301[1] = 0;
   out_4736070777333298301[2] = 0;
   out_4736070777333298301[3] = 0;
   out_4736070777333298301[4] = 0;
   out_4736070777333298301[5] = 0;
   out_4736070777333298301[6] = 0;
   out_4736070777333298301[7] = 0;
   out_4736070777333298301[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_5090167770449267747) {
  err_fun(nom_x, delta_x, out_5090167770449267747);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_2214359751135662810) {
  inv_err_fun(nom_x, true_x, out_2214359751135662810);
}
void car_H_mod_fun(double *state, double *out_8824828869686346636) {
  H_mod_fun(state, out_8824828869686346636);
}
void car_f_fun(double *state, double dt, double *out_7390949759775601083) {
  f_fun(state,  dt, out_7390949759775601083);
}
void car_F_fun(double *state, double dt, double *out_5580992667421940842) {
  F_fun(state,  dt, out_5580992667421940842);
}
void car_h_25(double *state, double *unused, double *out_873146183491989349) {
  h_25(state, unused, out_873146183491989349);
}
void car_H_25(double *state, double *unused, double *out_368359356225890601) {
  H_25(state, unused, out_368359356225890601);
}
void car_h_24(double *state, double *unused, double *out_838029550239282357) {
  h_24(state, unused, out_838029550239282357);
}
void car_H_24(double *state, double *unused, double *out_6285846101882295156) {
  H_24(state, unused, out_6285846101882295156);
}
void car_h_30(double *state, double *unused, double *out_4126629357105742333) {
  h_30(state, unused, out_4126629357105742333);
}
void car_H_30(double *state, double *unused, double *out_4896055686353498799) {
  H_30(state, unused, out_4896055686353498799);
}
void car_h_26(double *state, double *unused, double *out_4954179189956699152) {
  h_26(state, unused, out_4954179189956699152);
}
void car_H_26(double *state, double *unused, double *out_4109862675099946825) {
  H_26(state, unused, out_4109862675099946825);
}
void car_h_27(double *state, double *unused, double *out_1476462068168466866) {
  h_27(state, unused, out_1476462068168466866);
}
void car_H_27(double *state, double *unused, double *out_7070818998153923710) {
  H_27(state, unused, out_7070818998153923710);
}
void car_h_29(double *state, double *unused, double *out_5113911596422489216) {
  h_29(state, unused, out_5113911596422489216);
}
void car_H_29(double *state, double *unused, double *out_4385824342039106615) {
  H_29(state, unused, out_4385824342039106615);
}
void car_h_28(double *state, double *unused, double *out_1127943252640230785) {
  h_28(state, unused, out_1127943252640230785);
}
void car_H_28(double *state, double *unused, double *out_8978520714600914427) {
  H_28(state, unused, out_8978520714600914427);
}
void car_h_31(double *state, double *unused, double *out_2764303344762033001) {
  h_31(state, unused, out_2764303344762033001);
}
void car_H_31(double *state, double *unused, double *out_4736070777333298301) {
  H_31(state, unused, out_4736070777333298301);
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
