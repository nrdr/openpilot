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
void err_fun(double *nom_x, double *delta_x, double *out_6723804722312945773) {
   out_6723804722312945773[0] = delta_x[0] + nom_x[0];
   out_6723804722312945773[1] = delta_x[1] + nom_x[1];
   out_6723804722312945773[2] = delta_x[2] + nom_x[2];
   out_6723804722312945773[3] = delta_x[3] + nom_x[3];
   out_6723804722312945773[4] = delta_x[4] + nom_x[4];
   out_6723804722312945773[5] = delta_x[5] + nom_x[5];
   out_6723804722312945773[6] = delta_x[6] + nom_x[6];
   out_6723804722312945773[7] = delta_x[7] + nom_x[7];
   out_6723804722312945773[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1637419203022386435) {
   out_1637419203022386435[0] = -nom_x[0] + true_x[0];
   out_1637419203022386435[1] = -nom_x[1] + true_x[1];
   out_1637419203022386435[2] = -nom_x[2] + true_x[2];
   out_1637419203022386435[3] = -nom_x[3] + true_x[3];
   out_1637419203022386435[4] = -nom_x[4] + true_x[4];
   out_1637419203022386435[5] = -nom_x[5] + true_x[5];
   out_1637419203022386435[6] = -nom_x[6] + true_x[6];
   out_1637419203022386435[7] = -nom_x[7] + true_x[7];
   out_1637419203022386435[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_3837177300373436874) {
   out_3837177300373436874[0] = 1.0;
   out_3837177300373436874[1] = 0.0;
   out_3837177300373436874[2] = 0.0;
   out_3837177300373436874[3] = 0.0;
   out_3837177300373436874[4] = 0.0;
   out_3837177300373436874[5] = 0.0;
   out_3837177300373436874[6] = 0.0;
   out_3837177300373436874[7] = 0.0;
   out_3837177300373436874[8] = 0.0;
   out_3837177300373436874[9] = 0.0;
   out_3837177300373436874[10] = 1.0;
   out_3837177300373436874[11] = 0.0;
   out_3837177300373436874[12] = 0.0;
   out_3837177300373436874[13] = 0.0;
   out_3837177300373436874[14] = 0.0;
   out_3837177300373436874[15] = 0.0;
   out_3837177300373436874[16] = 0.0;
   out_3837177300373436874[17] = 0.0;
   out_3837177300373436874[18] = 0.0;
   out_3837177300373436874[19] = 0.0;
   out_3837177300373436874[20] = 1.0;
   out_3837177300373436874[21] = 0.0;
   out_3837177300373436874[22] = 0.0;
   out_3837177300373436874[23] = 0.0;
   out_3837177300373436874[24] = 0.0;
   out_3837177300373436874[25] = 0.0;
   out_3837177300373436874[26] = 0.0;
   out_3837177300373436874[27] = 0.0;
   out_3837177300373436874[28] = 0.0;
   out_3837177300373436874[29] = 0.0;
   out_3837177300373436874[30] = 1.0;
   out_3837177300373436874[31] = 0.0;
   out_3837177300373436874[32] = 0.0;
   out_3837177300373436874[33] = 0.0;
   out_3837177300373436874[34] = 0.0;
   out_3837177300373436874[35] = 0.0;
   out_3837177300373436874[36] = 0.0;
   out_3837177300373436874[37] = 0.0;
   out_3837177300373436874[38] = 0.0;
   out_3837177300373436874[39] = 0.0;
   out_3837177300373436874[40] = 1.0;
   out_3837177300373436874[41] = 0.0;
   out_3837177300373436874[42] = 0.0;
   out_3837177300373436874[43] = 0.0;
   out_3837177300373436874[44] = 0.0;
   out_3837177300373436874[45] = 0.0;
   out_3837177300373436874[46] = 0.0;
   out_3837177300373436874[47] = 0.0;
   out_3837177300373436874[48] = 0.0;
   out_3837177300373436874[49] = 0.0;
   out_3837177300373436874[50] = 1.0;
   out_3837177300373436874[51] = 0.0;
   out_3837177300373436874[52] = 0.0;
   out_3837177300373436874[53] = 0.0;
   out_3837177300373436874[54] = 0.0;
   out_3837177300373436874[55] = 0.0;
   out_3837177300373436874[56] = 0.0;
   out_3837177300373436874[57] = 0.0;
   out_3837177300373436874[58] = 0.0;
   out_3837177300373436874[59] = 0.0;
   out_3837177300373436874[60] = 1.0;
   out_3837177300373436874[61] = 0.0;
   out_3837177300373436874[62] = 0.0;
   out_3837177300373436874[63] = 0.0;
   out_3837177300373436874[64] = 0.0;
   out_3837177300373436874[65] = 0.0;
   out_3837177300373436874[66] = 0.0;
   out_3837177300373436874[67] = 0.0;
   out_3837177300373436874[68] = 0.0;
   out_3837177300373436874[69] = 0.0;
   out_3837177300373436874[70] = 1.0;
   out_3837177300373436874[71] = 0.0;
   out_3837177300373436874[72] = 0.0;
   out_3837177300373436874[73] = 0.0;
   out_3837177300373436874[74] = 0.0;
   out_3837177300373436874[75] = 0.0;
   out_3837177300373436874[76] = 0.0;
   out_3837177300373436874[77] = 0.0;
   out_3837177300373436874[78] = 0.0;
   out_3837177300373436874[79] = 0.0;
   out_3837177300373436874[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_1069481376239403552) {
   out_1069481376239403552[0] = state[0];
   out_1069481376239403552[1] = state[1];
   out_1069481376239403552[2] = state[2];
   out_1069481376239403552[3] = state[3];
   out_1069481376239403552[4] = state[4];
   out_1069481376239403552[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_1069481376239403552[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_1069481376239403552[7] = state[7];
   out_1069481376239403552[8] = state[8];
}
void F_fun(double *state, double dt, double *out_811488727004941991) {
   out_811488727004941991[0] = 1;
   out_811488727004941991[1] = 0;
   out_811488727004941991[2] = 0;
   out_811488727004941991[3] = 0;
   out_811488727004941991[4] = 0;
   out_811488727004941991[5] = 0;
   out_811488727004941991[6] = 0;
   out_811488727004941991[7] = 0;
   out_811488727004941991[8] = 0;
   out_811488727004941991[9] = 0;
   out_811488727004941991[10] = 1;
   out_811488727004941991[11] = 0;
   out_811488727004941991[12] = 0;
   out_811488727004941991[13] = 0;
   out_811488727004941991[14] = 0;
   out_811488727004941991[15] = 0;
   out_811488727004941991[16] = 0;
   out_811488727004941991[17] = 0;
   out_811488727004941991[18] = 0;
   out_811488727004941991[19] = 0;
   out_811488727004941991[20] = 1;
   out_811488727004941991[21] = 0;
   out_811488727004941991[22] = 0;
   out_811488727004941991[23] = 0;
   out_811488727004941991[24] = 0;
   out_811488727004941991[25] = 0;
   out_811488727004941991[26] = 0;
   out_811488727004941991[27] = 0;
   out_811488727004941991[28] = 0;
   out_811488727004941991[29] = 0;
   out_811488727004941991[30] = 1;
   out_811488727004941991[31] = 0;
   out_811488727004941991[32] = 0;
   out_811488727004941991[33] = 0;
   out_811488727004941991[34] = 0;
   out_811488727004941991[35] = 0;
   out_811488727004941991[36] = 0;
   out_811488727004941991[37] = 0;
   out_811488727004941991[38] = 0;
   out_811488727004941991[39] = 0;
   out_811488727004941991[40] = 1;
   out_811488727004941991[41] = 0;
   out_811488727004941991[42] = 0;
   out_811488727004941991[43] = 0;
   out_811488727004941991[44] = 0;
   out_811488727004941991[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_811488727004941991[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_811488727004941991[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_811488727004941991[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_811488727004941991[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_811488727004941991[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_811488727004941991[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_811488727004941991[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_811488727004941991[53] = -9.8100000000000005*dt;
   out_811488727004941991[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_811488727004941991[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_811488727004941991[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_811488727004941991[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_811488727004941991[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_811488727004941991[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_811488727004941991[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_811488727004941991[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_811488727004941991[62] = 0;
   out_811488727004941991[63] = 0;
   out_811488727004941991[64] = 0;
   out_811488727004941991[65] = 0;
   out_811488727004941991[66] = 0;
   out_811488727004941991[67] = 0;
   out_811488727004941991[68] = 0;
   out_811488727004941991[69] = 0;
   out_811488727004941991[70] = 1;
   out_811488727004941991[71] = 0;
   out_811488727004941991[72] = 0;
   out_811488727004941991[73] = 0;
   out_811488727004941991[74] = 0;
   out_811488727004941991[75] = 0;
   out_811488727004941991[76] = 0;
   out_811488727004941991[77] = 0;
   out_811488727004941991[78] = 0;
   out_811488727004941991[79] = 0;
   out_811488727004941991[80] = 1;
}
void h_25(double *state, double *unused, double *out_2604343454635407771) {
   out_2604343454635407771[0] = state[6];
}
void H_25(double *state, double *unused, double *out_1066514524811227966) {
   out_1066514524811227966[0] = 0;
   out_1066514524811227966[1] = 0;
   out_1066514524811227966[2] = 0;
   out_1066514524811227966[3] = 0;
   out_1066514524811227966[4] = 0;
   out_1066514524811227966[5] = 0;
   out_1066514524811227966[6] = 1;
   out_1066514524811227966[7] = 0;
   out_1066514524811227966[8] = 0;
}
void h_24(double *state, double *unused, double *out_7708663193811877711) {
   out_7708663193811877711[0] = state[4];
   out_7708663193811877711[1] = state[5];
}
void H_24(double *state, double *unused, double *out_3243728948418377939) {
   out_3243728948418377939[0] = 0;
   out_3243728948418377939[1] = 0;
   out_3243728948418377939[2] = 0;
   out_3243728948418377939[3] = 0;
   out_3243728948418377939[4] = 1;
   out_3243728948418377939[5] = 0;
   out_3243728948418377939[6] = 0;
   out_3243728948418377939[7] = 0;
   out_3243728948418377939[8] = 0;
   out_3243728948418377939[9] = 0;
   out_3243728948418377939[10] = 0;
   out_3243728948418377939[11] = 0;
   out_3243728948418377939[12] = 0;
   out_3243728948418377939[13] = 0;
   out_3243728948418377939[14] = 1;
   out_3243728948418377939[15] = 0;
   out_3243728948418377939[16] = 0;
   out_3243728948418377939[17] = 0;
}
void h_30(double *state, double *unused, double *out_7277894899904281788) {
   out_7277894899904281788[0] = state[4];
}
void H_30(double *state, double *unused, double *out_3584847483318476593) {
   out_3584847483318476593[0] = 0;
   out_3584847483318476593[1] = 0;
   out_3584847483318476593[2] = 0;
   out_3584847483318476593[3] = 0;
   out_3584847483318476593[4] = 1;
   out_3584847483318476593[5] = 0;
   out_3584847483318476593[6] = 0;
   out_3584847483318476593[7] = 0;
   out_3584847483318476593[8] = 0;
}
void h_26(double *state, double *unused, double *out_4569985351655594620) {
   out_4569985351655594620[0] = state[7];
}
void H_26(double *state, double *unused, double *out_2674988794062828258) {
   out_2674988794062828258[0] = 0;
   out_2674988794062828258[1] = 0;
   out_2674988794062828258[2] = 0;
   out_2674988794062828258[3] = 0;
   out_2674988794062828258[4] = 0;
   out_2674988794062828258[5] = 0;
   out_2674988794062828258[6] = 0;
   out_2674988794062828258[7] = 1;
   out_2674988794062828258[8] = 0;
}
void h_27(double *state, double *unused, double *out_7606016722296253416) {
   out_7606016722296253416[0] = state[3];
}
void H_27(double *state, double *unused, double *out_1410084171518051682) {
   out_1410084171518051682[0] = 0;
   out_1410084171518051682[1] = 0;
   out_1410084171518051682[2] = 0;
   out_1410084171518051682[3] = 1;
   out_1410084171518051682[4] = 0;
   out_1410084171518051682[5] = 0;
   out_1410084171518051682[6] = 0;
   out_1410084171518051682[7] = 0;
   out_1410084171518051682[8] = 0;
}
void h_29(double *state, double *unused, double *out_157248534524419025) {
   out_157248534524419025[0] = state[1];
}
void H_29(double *state, double *unused, double *out_4095078827632868777) {
   out_4095078827632868777[0] = 0;
   out_4095078827632868777[1] = 1;
   out_4095078827632868777[2] = 0;
   out_4095078827632868777[3] = 0;
   out_4095078827632868777[4] = 0;
   out_4095078827632868777[5] = 0;
   out_4095078827632868777[6] = 0;
   out_4095078827632868777[7] = 0;
   out_4095078827632868777[8] = 0;
}
void h_28(double *state, double *unused, double *out_1375952449710587349) {
   out_1375952449710587349[0] = state[0];
}
void H_28(double *state, double *unused, double *out_987320189436661797) {
   out_987320189436661797[0] = 1;
   out_987320189436661797[1] = 0;
   out_987320189436661797[2] = 0;
   out_987320189436661797[3] = 0;
   out_987320189436661797[4] = 0;
   out_987320189436661797[5] = 0;
   out_987320189436661797[6] = 0;
   out_987320189436661797[7] = 0;
   out_987320189436661797[8] = 0;
}
void h_31(double *state, double *unused, double *out_3365251309365753549) {
   out_3365251309365753549[0] = state[8];
}
void H_31(double *state, double *unused, double *out_3301196896296179734) {
   out_3301196896296179734[0] = 0;
   out_3301196896296179734[1] = 0;
   out_3301196896296179734[2] = 0;
   out_3301196896296179734[3] = 0;
   out_3301196896296179734[4] = 0;
   out_3301196896296179734[5] = 0;
   out_3301196896296179734[6] = 0;
   out_3301196896296179734[7] = 0;
   out_3301196896296179734[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_6723804722312945773) {
  err_fun(nom_x, delta_x, out_6723804722312945773);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1637419203022386435) {
  inv_err_fun(nom_x, true_x, out_1637419203022386435);
}
void car_H_mod_fun(double *state, double *out_3837177300373436874) {
  H_mod_fun(state, out_3837177300373436874);
}
void car_f_fun(double *state, double dt, double *out_1069481376239403552) {
  f_fun(state,  dt, out_1069481376239403552);
}
void car_F_fun(double *state, double dt, double *out_811488727004941991) {
  F_fun(state,  dt, out_811488727004941991);
}
void car_h_25(double *state, double *unused, double *out_2604343454635407771) {
  h_25(state, unused, out_2604343454635407771);
}
void car_H_25(double *state, double *unused, double *out_1066514524811227966) {
  H_25(state, unused, out_1066514524811227966);
}
void car_h_24(double *state, double *unused, double *out_7708663193811877711) {
  h_24(state, unused, out_7708663193811877711);
}
void car_H_24(double *state, double *unused, double *out_3243728948418377939) {
  H_24(state, unused, out_3243728948418377939);
}
void car_h_30(double *state, double *unused, double *out_7277894899904281788) {
  h_30(state, unused, out_7277894899904281788);
}
void car_H_30(double *state, double *unused, double *out_3584847483318476593) {
  H_30(state, unused, out_3584847483318476593);
}
void car_h_26(double *state, double *unused, double *out_4569985351655594620) {
  h_26(state, unused, out_4569985351655594620);
}
void car_H_26(double *state, double *unused, double *out_2674988794062828258) {
  H_26(state, unused, out_2674988794062828258);
}
void car_h_27(double *state, double *unused, double *out_7606016722296253416) {
  h_27(state, unused, out_7606016722296253416);
}
void car_H_27(double *state, double *unused, double *out_1410084171518051682) {
  H_27(state, unused, out_1410084171518051682);
}
void car_h_29(double *state, double *unused, double *out_157248534524419025) {
  h_29(state, unused, out_157248534524419025);
}
void car_H_29(double *state, double *unused, double *out_4095078827632868777) {
  H_29(state, unused, out_4095078827632868777);
}
void car_h_28(double *state, double *unused, double *out_1375952449710587349) {
  h_28(state, unused, out_1375952449710587349);
}
void car_H_28(double *state, double *unused, double *out_987320189436661797) {
  H_28(state, unused, out_987320189436661797);
}
void car_h_31(double *state, double *unused, double *out_3365251309365753549) {
  h_31(state, unused, out_3365251309365753549);
}
void car_H_31(double *state, double *unused, double *out_3301196896296179734) {
  H_31(state, unused, out_3301196896296179734);
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
