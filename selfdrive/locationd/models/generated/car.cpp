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
void err_fun(double *nom_x, double *delta_x, double *out_5658036703693658224) {
   out_5658036703693658224[0] = delta_x[0] + nom_x[0];
   out_5658036703693658224[1] = delta_x[1] + nom_x[1];
   out_5658036703693658224[2] = delta_x[2] + nom_x[2];
   out_5658036703693658224[3] = delta_x[3] + nom_x[3];
   out_5658036703693658224[4] = delta_x[4] + nom_x[4];
   out_5658036703693658224[5] = delta_x[5] + nom_x[5];
   out_5658036703693658224[6] = delta_x[6] + nom_x[6];
   out_5658036703693658224[7] = delta_x[7] + nom_x[7];
   out_5658036703693658224[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_2378388429853024968) {
   out_2378388429853024968[0] = -nom_x[0] + true_x[0];
   out_2378388429853024968[1] = -nom_x[1] + true_x[1];
   out_2378388429853024968[2] = -nom_x[2] + true_x[2];
   out_2378388429853024968[3] = -nom_x[3] + true_x[3];
   out_2378388429853024968[4] = -nom_x[4] + true_x[4];
   out_2378388429853024968[5] = -nom_x[5] + true_x[5];
   out_2378388429853024968[6] = -nom_x[6] + true_x[6];
   out_2378388429853024968[7] = -nom_x[7] + true_x[7];
   out_2378388429853024968[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_4573538855915977510) {
   out_4573538855915977510[0] = 1.0;
   out_4573538855915977510[1] = 0.0;
   out_4573538855915977510[2] = 0.0;
   out_4573538855915977510[3] = 0.0;
   out_4573538855915977510[4] = 0.0;
   out_4573538855915977510[5] = 0.0;
   out_4573538855915977510[6] = 0.0;
   out_4573538855915977510[7] = 0.0;
   out_4573538855915977510[8] = 0.0;
   out_4573538855915977510[9] = 0.0;
   out_4573538855915977510[10] = 1.0;
   out_4573538855915977510[11] = 0.0;
   out_4573538855915977510[12] = 0.0;
   out_4573538855915977510[13] = 0.0;
   out_4573538855915977510[14] = 0.0;
   out_4573538855915977510[15] = 0.0;
   out_4573538855915977510[16] = 0.0;
   out_4573538855915977510[17] = 0.0;
   out_4573538855915977510[18] = 0.0;
   out_4573538855915977510[19] = 0.0;
   out_4573538855915977510[20] = 1.0;
   out_4573538855915977510[21] = 0.0;
   out_4573538855915977510[22] = 0.0;
   out_4573538855915977510[23] = 0.0;
   out_4573538855915977510[24] = 0.0;
   out_4573538855915977510[25] = 0.0;
   out_4573538855915977510[26] = 0.0;
   out_4573538855915977510[27] = 0.0;
   out_4573538855915977510[28] = 0.0;
   out_4573538855915977510[29] = 0.0;
   out_4573538855915977510[30] = 1.0;
   out_4573538855915977510[31] = 0.0;
   out_4573538855915977510[32] = 0.0;
   out_4573538855915977510[33] = 0.0;
   out_4573538855915977510[34] = 0.0;
   out_4573538855915977510[35] = 0.0;
   out_4573538855915977510[36] = 0.0;
   out_4573538855915977510[37] = 0.0;
   out_4573538855915977510[38] = 0.0;
   out_4573538855915977510[39] = 0.0;
   out_4573538855915977510[40] = 1.0;
   out_4573538855915977510[41] = 0.0;
   out_4573538855915977510[42] = 0.0;
   out_4573538855915977510[43] = 0.0;
   out_4573538855915977510[44] = 0.0;
   out_4573538855915977510[45] = 0.0;
   out_4573538855915977510[46] = 0.0;
   out_4573538855915977510[47] = 0.0;
   out_4573538855915977510[48] = 0.0;
   out_4573538855915977510[49] = 0.0;
   out_4573538855915977510[50] = 1.0;
   out_4573538855915977510[51] = 0.0;
   out_4573538855915977510[52] = 0.0;
   out_4573538855915977510[53] = 0.0;
   out_4573538855915977510[54] = 0.0;
   out_4573538855915977510[55] = 0.0;
   out_4573538855915977510[56] = 0.0;
   out_4573538855915977510[57] = 0.0;
   out_4573538855915977510[58] = 0.0;
   out_4573538855915977510[59] = 0.0;
   out_4573538855915977510[60] = 1.0;
   out_4573538855915977510[61] = 0.0;
   out_4573538855915977510[62] = 0.0;
   out_4573538855915977510[63] = 0.0;
   out_4573538855915977510[64] = 0.0;
   out_4573538855915977510[65] = 0.0;
   out_4573538855915977510[66] = 0.0;
   out_4573538855915977510[67] = 0.0;
   out_4573538855915977510[68] = 0.0;
   out_4573538855915977510[69] = 0.0;
   out_4573538855915977510[70] = 1.0;
   out_4573538855915977510[71] = 0.0;
   out_4573538855915977510[72] = 0.0;
   out_4573538855915977510[73] = 0.0;
   out_4573538855915977510[74] = 0.0;
   out_4573538855915977510[75] = 0.0;
   out_4573538855915977510[76] = 0.0;
   out_4573538855915977510[77] = 0.0;
   out_4573538855915977510[78] = 0.0;
   out_4573538855915977510[79] = 0.0;
   out_4573538855915977510[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_857475065003488353) {
   out_857475065003488353[0] = state[0];
   out_857475065003488353[1] = state[1];
   out_857475065003488353[2] = state[2];
   out_857475065003488353[3] = state[3];
   out_857475065003488353[4] = state[4];
   out_857475065003488353[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_857475065003488353[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_857475065003488353[7] = state[7];
   out_857475065003488353[8] = state[8];
}
void F_fun(double *state, double dt, double *out_861520061507436680) {
   out_861520061507436680[0] = 1;
   out_861520061507436680[1] = 0;
   out_861520061507436680[2] = 0;
   out_861520061507436680[3] = 0;
   out_861520061507436680[4] = 0;
   out_861520061507436680[5] = 0;
   out_861520061507436680[6] = 0;
   out_861520061507436680[7] = 0;
   out_861520061507436680[8] = 0;
   out_861520061507436680[9] = 0;
   out_861520061507436680[10] = 1;
   out_861520061507436680[11] = 0;
   out_861520061507436680[12] = 0;
   out_861520061507436680[13] = 0;
   out_861520061507436680[14] = 0;
   out_861520061507436680[15] = 0;
   out_861520061507436680[16] = 0;
   out_861520061507436680[17] = 0;
   out_861520061507436680[18] = 0;
   out_861520061507436680[19] = 0;
   out_861520061507436680[20] = 1;
   out_861520061507436680[21] = 0;
   out_861520061507436680[22] = 0;
   out_861520061507436680[23] = 0;
   out_861520061507436680[24] = 0;
   out_861520061507436680[25] = 0;
   out_861520061507436680[26] = 0;
   out_861520061507436680[27] = 0;
   out_861520061507436680[28] = 0;
   out_861520061507436680[29] = 0;
   out_861520061507436680[30] = 1;
   out_861520061507436680[31] = 0;
   out_861520061507436680[32] = 0;
   out_861520061507436680[33] = 0;
   out_861520061507436680[34] = 0;
   out_861520061507436680[35] = 0;
   out_861520061507436680[36] = 0;
   out_861520061507436680[37] = 0;
   out_861520061507436680[38] = 0;
   out_861520061507436680[39] = 0;
   out_861520061507436680[40] = 1;
   out_861520061507436680[41] = 0;
   out_861520061507436680[42] = 0;
   out_861520061507436680[43] = 0;
   out_861520061507436680[44] = 0;
   out_861520061507436680[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_861520061507436680[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_861520061507436680[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_861520061507436680[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_861520061507436680[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_861520061507436680[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_861520061507436680[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_861520061507436680[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_861520061507436680[53] = -9.8100000000000005*dt;
   out_861520061507436680[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_861520061507436680[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_861520061507436680[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_861520061507436680[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_861520061507436680[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_861520061507436680[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_861520061507436680[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_861520061507436680[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_861520061507436680[62] = 0;
   out_861520061507436680[63] = 0;
   out_861520061507436680[64] = 0;
   out_861520061507436680[65] = 0;
   out_861520061507436680[66] = 0;
   out_861520061507436680[67] = 0;
   out_861520061507436680[68] = 0;
   out_861520061507436680[69] = 0;
   out_861520061507436680[70] = 1;
   out_861520061507436680[71] = 0;
   out_861520061507436680[72] = 0;
   out_861520061507436680[73] = 0;
   out_861520061507436680[74] = 0;
   out_861520061507436680[75] = 0;
   out_861520061507436680[76] = 0;
   out_861520061507436680[77] = 0;
   out_861520061507436680[78] = 0;
   out_861520061507436680[79] = 0;
   out_861520061507436680[80] = 1;
}
void h_25(double *state, double *unused, double *out_5081030669612635808) {
   out_5081030669612635808[0] = state[6];
}
void H_25(double *state, double *unused, double *out_1050558205926485833) {
   out_1050558205926485833[0] = 0;
   out_1050558205926485833[1] = 0;
   out_1050558205926485833[2] = 0;
   out_1050558205926485833[3] = 0;
   out_1050558205926485833[4] = 0;
   out_1050558205926485833[5] = 0;
   out_1050558205926485833[6] = 1;
   out_1050558205926485833[7] = 0;
   out_1050558205926485833[8] = 0;
}
void h_24(double *state, double *unused, double *out_6877732608566867147) {
   out_6877732608566867147[0] = state[4];
   out_6877732608566867147[1] = state[5];
}
void H_24(double *state, double *unused, double *out_5797067532892994867) {
   out_5797067532892994867[0] = 0;
   out_5797067532892994867[1] = 0;
   out_5797067532892994867[2] = 0;
   out_5797067532892994867[3] = 0;
   out_5797067532892994867[4] = 1;
   out_5797067532892994867[5] = 0;
   out_5797067532892994867[6] = 0;
   out_5797067532892994867[7] = 0;
   out_5797067532892994867[8] = 0;
   out_5797067532892994867[9] = 0;
   out_5797067532892994867[10] = 0;
   out_5797067532892994867[11] = 0;
   out_5797067532892994867[12] = 0;
   out_5797067532892994867[13] = 0;
   out_5797067532892994867[14] = 1;
   out_5797067532892994867[15] = 0;
   out_5797067532892994867[16] = 0;
   out_5797067532892994867[17] = 0;
}
void h_30(double *state, double *unused, double *out_4805836607328129919) {
   out_4805836607328129919[0] = state[4];
}
void H_30(double *state, double *unused, double *out_5866132135565130922) {
   out_5866132135565130922[0] = 0;
   out_5866132135565130922[1] = 0;
   out_5866132135565130922[2] = 0;
   out_5866132135565130922[3] = 0;
   out_5866132135565130922[4] = 1;
   out_5866132135565130922[5] = 0;
   out_5866132135565130922[6] = 0;
   out_5866132135565130922[7] = 0;
   out_5866132135565130922[8] = 0;
}
void h_26(double *state, double *unused, double *out_8639234198720576052) {
   out_8639234198720576052[0] = state[7];
}
void H_26(double *state, double *unused, double *out_4792061524800542057) {
   out_4792061524800542057[0] = 0;
   out_4792061524800542057[1] = 0;
   out_4792061524800542057[2] = 0;
   out_4792061524800542057[3] = 0;
   out_4792061524800542057[4] = 0;
   out_4792061524800542057[5] = 0;
   out_4792061524800542057[6] = 0;
   out_4792061524800542057[7] = 1;
   out_4792061524800542057[8] = 0;
}
void h_27(double *state, double *unused, double *out_274550784286540057) {
   out_274550784286540057[0] = state[3];
}
void H_27(double *state, double *unused, double *out_3354660464870150814) {
   out_3354660464870150814[0] = 0;
   out_3354660464870150814[1] = 0;
   out_3354660464870150814[2] = 0;
   out_3354660464870150814[3] = 1;
   out_3354660464870150814[4] = 0;
   out_3354660464870150814[5] = 0;
   out_3354660464870150814[6] = 0;
   out_3354660464870150814[7] = 0;
   out_3354660464870150814[8] = 0;
}
void h_29(double *state, double *unused, double *out_195836660332715726) {
   out_195836660332715726[0] = state[1];
}
void H_29(double *state, double *unused, double *out_1978006096895154978) {
   out_1978006096895154978[0] = 0;
   out_1978006096895154978[1] = 1;
   out_1978006096895154978[2] = 0;
   out_1978006096895154978[3] = 0;
   out_1978006096895154978[4] = 0;
   out_1978006096895154978[5] = 0;
   out_1978006096895154978[6] = 0;
   out_1978006096895154978[7] = 0;
   out_1978006096895154978[8] = 0;
}
void h_28(double *state, double *unused, double *out_893193016789601680) {
   out_893193016789601680[0] = state[0];
}
void H_28(double *state, double *unused, double *out_3104392920174375596) {
   out_3104392920174375596[0] = 1;
   out_3104392920174375596[1] = 0;
   out_3104392920174375596[2] = 0;
   out_3104392920174375596[3] = 0;
   out_3104392920174375596[4] = 0;
   out_3104392920174375596[5] = 0;
   out_3104392920174375596[6] = 0;
   out_3104392920174375596[7] = 0;
   out_3104392920174375596[8] = 0;
}
void h_31(double *state, double *unused, double *out_7210266208256255679) {
   out_7210266208256255679[0] = state[8];
}
void H_31(double *state, double *unused, double *out_1019912244049525405) {
   out_1019912244049525405[0] = 0;
   out_1019912244049525405[1] = 0;
   out_1019912244049525405[2] = 0;
   out_1019912244049525405[3] = 0;
   out_1019912244049525405[4] = 0;
   out_1019912244049525405[5] = 0;
   out_1019912244049525405[6] = 0;
   out_1019912244049525405[7] = 0;
   out_1019912244049525405[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_5658036703693658224) {
  err_fun(nom_x, delta_x, out_5658036703693658224);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_2378388429853024968) {
  inv_err_fun(nom_x, true_x, out_2378388429853024968);
}
void car_H_mod_fun(double *state, double *out_4573538855915977510) {
  H_mod_fun(state, out_4573538855915977510);
}
void car_f_fun(double *state, double dt, double *out_857475065003488353) {
  f_fun(state,  dt, out_857475065003488353);
}
void car_F_fun(double *state, double dt, double *out_861520061507436680) {
  F_fun(state,  dt, out_861520061507436680);
}
void car_h_25(double *state, double *unused, double *out_5081030669612635808) {
  h_25(state, unused, out_5081030669612635808);
}
void car_H_25(double *state, double *unused, double *out_1050558205926485833) {
  H_25(state, unused, out_1050558205926485833);
}
void car_h_24(double *state, double *unused, double *out_6877732608566867147) {
  h_24(state, unused, out_6877732608566867147);
}
void car_H_24(double *state, double *unused, double *out_5797067532892994867) {
  H_24(state, unused, out_5797067532892994867);
}
void car_h_30(double *state, double *unused, double *out_4805836607328129919) {
  h_30(state, unused, out_4805836607328129919);
}
void car_H_30(double *state, double *unused, double *out_5866132135565130922) {
  H_30(state, unused, out_5866132135565130922);
}
void car_h_26(double *state, double *unused, double *out_8639234198720576052) {
  h_26(state, unused, out_8639234198720576052);
}
void car_H_26(double *state, double *unused, double *out_4792061524800542057) {
  H_26(state, unused, out_4792061524800542057);
}
void car_h_27(double *state, double *unused, double *out_274550784286540057) {
  h_27(state, unused, out_274550784286540057);
}
void car_H_27(double *state, double *unused, double *out_3354660464870150814) {
  H_27(state, unused, out_3354660464870150814);
}
void car_h_29(double *state, double *unused, double *out_195836660332715726) {
  h_29(state, unused, out_195836660332715726);
}
void car_H_29(double *state, double *unused, double *out_1978006096895154978) {
  H_29(state, unused, out_1978006096895154978);
}
void car_h_28(double *state, double *unused, double *out_893193016789601680) {
  h_28(state, unused, out_893193016789601680);
}
void car_H_28(double *state, double *unused, double *out_3104392920174375596) {
  H_28(state, unused, out_3104392920174375596);
}
void car_h_31(double *state, double *unused, double *out_7210266208256255679) {
  h_31(state, unused, out_7210266208256255679);
}
void car_H_31(double *state, double *unused, double *out_1019912244049525405) {
  H_31(state, unused, out_1019912244049525405);
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
