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
void err_fun(double *nom_x, double *delta_x, double *out_1038389500972116158) {
   out_1038389500972116158[0] = delta_x[0] + nom_x[0];
   out_1038389500972116158[1] = delta_x[1] + nom_x[1];
   out_1038389500972116158[2] = delta_x[2] + nom_x[2];
   out_1038389500972116158[3] = delta_x[3] + nom_x[3];
   out_1038389500972116158[4] = delta_x[4] + nom_x[4];
   out_1038389500972116158[5] = delta_x[5] + nom_x[5];
   out_1038389500972116158[6] = delta_x[6] + nom_x[6];
   out_1038389500972116158[7] = delta_x[7] + nom_x[7];
   out_1038389500972116158[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6418752408535262595) {
   out_6418752408535262595[0] = -nom_x[0] + true_x[0];
   out_6418752408535262595[1] = -nom_x[1] + true_x[1];
   out_6418752408535262595[2] = -nom_x[2] + true_x[2];
   out_6418752408535262595[3] = -nom_x[3] + true_x[3];
   out_6418752408535262595[4] = -nom_x[4] + true_x[4];
   out_6418752408535262595[5] = -nom_x[5] + true_x[5];
   out_6418752408535262595[6] = -nom_x[6] + true_x[6];
   out_6418752408535262595[7] = -nom_x[7] + true_x[7];
   out_6418752408535262595[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_2855368609596965229) {
   out_2855368609596965229[0] = 1.0;
   out_2855368609596965229[1] = 0.0;
   out_2855368609596965229[2] = 0.0;
   out_2855368609596965229[3] = 0.0;
   out_2855368609596965229[4] = 0.0;
   out_2855368609596965229[5] = 0.0;
   out_2855368609596965229[6] = 0.0;
   out_2855368609596965229[7] = 0.0;
   out_2855368609596965229[8] = 0.0;
   out_2855368609596965229[9] = 0.0;
   out_2855368609596965229[10] = 1.0;
   out_2855368609596965229[11] = 0.0;
   out_2855368609596965229[12] = 0.0;
   out_2855368609596965229[13] = 0.0;
   out_2855368609596965229[14] = 0.0;
   out_2855368609596965229[15] = 0.0;
   out_2855368609596965229[16] = 0.0;
   out_2855368609596965229[17] = 0.0;
   out_2855368609596965229[18] = 0.0;
   out_2855368609596965229[19] = 0.0;
   out_2855368609596965229[20] = 1.0;
   out_2855368609596965229[21] = 0.0;
   out_2855368609596965229[22] = 0.0;
   out_2855368609596965229[23] = 0.0;
   out_2855368609596965229[24] = 0.0;
   out_2855368609596965229[25] = 0.0;
   out_2855368609596965229[26] = 0.0;
   out_2855368609596965229[27] = 0.0;
   out_2855368609596965229[28] = 0.0;
   out_2855368609596965229[29] = 0.0;
   out_2855368609596965229[30] = 1.0;
   out_2855368609596965229[31] = 0.0;
   out_2855368609596965229[32] = 0.0;
   out_2855368609596965229[33] = 0.0;
   out_2855368609596965229[34] = 0.0;
   out_2855368609596965229[35] = 0.0;
   out_2855368609596965229[36] = 0.0;
   out_2855368609596965229[37] = 0.0;
   out_2855368609596965229[38] = 0.0;
   out_2855368609596965229[39] = 0.0;
   out_2855368609596965229[40] = 1.0;
   out_2855368609596965229[41] = 0.0;
   out_2855368609596965229[42] = 0.0;
   out_2855368609596965229[43] = 0.0;
   out_2855368609596965229[44] = 0.0;
   out_2855368609596965229[45] = 0.0;
   out_2855368609596965229[46] = 0.0;
   out_2855368609596965229[47] = 0.0;
   out_2855368609596965229[48] = 0.0;
   out_2855368609596965229[49] = 0.0;
   out_2855368609596965229[50] = 1.0;
   out_2855368609596965229[51] = 0.0;
   out_2855368609596965229[52] = 0.0;
   out_2855368609596965229[53] = 0.0;
   out_2855368609596965229[54] = 0.0;
   out_2855368609596965229[55] = 0.0;
   out_2855368609596965229[56] = 0.0;
   out_2855368609596965229[57] = 0.0;
   out_2855368609596965229[58] = 0.0;
   out_2855368609596965229[59] = 0.0;
   out_2855368609596965229[60] = 1.0;
   out_2855368609596965229[61] = 0.0;
   out_2855368609596965229[62] = 0.0;
   out_2855368609596965229[63] = 0.0;
   out_2855368609596965229[64] = 0.0;
   out_2855368609596965229[65] = 0.0;
   out_2855368609596965229[66] = 0.0;
   out_2855368609596965229[67] = 0.0;
   out_2855368609596965229[68] = 0.0;
   out_2855368609596965229[69] = 0.0;
   out_2855368609596965229[70] = 1.0;
   out_2855368609596965229[71] = 0.0;
   out_2855368609596965229[72] = 0.0;
   out_2855368609596965229[73] = 0.0;
   out_2855368609596965229[74] = 0.0;
   out_2855368609596965229[75] = 0.0;
   out_2855368609596965229[76] = 0.0;
   out_2855368609596965229[77] = 0.0;
   out_2855368609596965229[78] = 0.0;
   out_2855368609596965229[79] = 0.0;
   out_2855368609596965229[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_1397092929687677159) {
   out_1397092929687677159[0] = state[0];
   out_1397092929687677159[1] = state[1];
   out_1397092929687677159[2] = state[2];
   out_1397092929687677159[3] = state[3];
   out_1397092929687677159[4] = state[4];
   out_1397092929687677159[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_1397092929687677159[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_1397092929687677159[7] = state[7];
   out_1397092929687677159[8] = state[8];
}
void F_fun(double *state, double dt, double *out_7780451684963738443) {
   out_7780451684963738443[0] = 1;
   out_7780451684963738443[1] = 0;
   out_7780451684963738443[2] = 0;
   out_7780451684963738443[3] = 0;
   out_7780451684963738443[4] = 0;
   out_7780451684963738443[5] = 0;
   out_7780451684963738443[6] = 0;
   out_7780451684963738443[7] = 0;
   out_7780451684963738443[8] = 0;
   out_7780451684963738443[9] = 0;
   out_7780451684963738443[10] = 1;
   out_7780451684963738443[11] = 0;
   out_7780451684963738443[12] = 0;
   out_7780451684963738443[13] = 0;
   out_7780451684963738443[14] = 0;
   out_7780451684963738443[15] = 0;
   out_7780451684963738443[16] = 0;
   out_7780451684963738443[17] = 0;
   out_7780451684963738443[18] = 0;
   out_7780451684963738443[19] = 0;
   out_7780451684963738443[20] = 1;
   out_7780451684963738443[21] = 0;
   out_7780451684963738443[22] = 0;
   out_7780451684963738443[23] = 0;
   out_7780451684963738443[24] = 0;
   out_7780451684963738443[25] = 0;
   out_7780451684963738443[26] = 0;
   out_7780451684963738443[27] = 0;
   out_7780451684963738443[28] = 0;
   out_7780451684963738443[29] = 0;
   out_7780451684963738443[30] = 1;
   out_7780451684963738443[31] = 0;
   out_7780451684963738443[32] = 0;
   out_7780451684963738443[33] = 0;
   out_7780451684963738443[34] = 0;
   out_7780451684963738443[35] = 0;
   out_7780451684963738443[36] = 0;
   out_7780451684963738443[37] = 0;
   out_7780451684963738443[38] = 0;
   out_7780451684963738443[39] = 0;
   out_7780451684963738443[40] = 1;
   out_7780451684963738443[41] = 0;
   out_7780451684963738443[42] = 0;
   out_7780451684963738443[43] = 0;
   out_7780451684963738443[44] = 0;
   out_7780451684963738443[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_7780451684963738443[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_7780451684963738443[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7780451684963738443[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7780451684963738443[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_7780451684963738443[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_7780451684963738443[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_7780451684963738443[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_7780451684963738443[53] = -9.8100000000000005*dt;
   out_7780451684963738443[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_7780451684963738443[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_7780451684963738443[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7780451684963738443[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7780451684963738443[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_7780451684963738443[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_7780451684963738443[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_7780451684963738443[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7780451684963738443[62] = 0;
   out_7780451684963738443[63] = 0;
   out_7780451684963738443[64] = 0;
   out_7780451684963738443[65] = 0;
   out_7780451684963738443[66] = 0;
   out_7780451684963738443[67] = 0;
   out_7780451684963738443[68] = 0;
   out_7780451684963738443[69] = 0;
   out_7780451684963738443[70] = 1;
   out_7780451684963738443[71] = 0;
   out_7780451684963738443[72] = 0;
   out_7780451684963738443[73] = 0;
   out_7780451684963738443[74] = 0;
   out_7780451684963738443[75] = 0;
   out_7780451684963738443[76] = 0;
   out_7780451684963738443[77] = 0;
   out_7780451684963738443[78] = 0;
   out_7780451684963738443[79] = 0;
   out_7780451684963738443[80] = 1;
}
void h_25(double *state, double *unused, double *out_894848580994361563) {
   out_894848580994361563[0] = state[6];
}
void H_25(double *state, double *unused, double *out_6378349259586456906) {
   out_6378349259586456906[0] = 0;
   out_6378349259586456906[1] = 0;
   out_6378349259586456906[2] = 0;
   out_6378349259586456906[3] = 0;
   out_6378349259586456906[4] = 0;
   out_6378349259586456906[5] = 0;
   out_6378349259586456906[6] = 1;
   out_6378349259586456906[7] = 0;
   out_6378349259586456906[8] = 0;
}
void h_24(double *state, double *unused, double *out_6711296683837743925) {
   out_6711296683837743925[0] = state[4];
   out_6711296683837743925[1] = state[5];
}
void H_24(double *state, double *unused, double *out_5414189356014908953) {
   out_5414189356014908953[0] = 0;
   out_5414189356014908953[1] = 0;
   out_5414189356014908953[2] = 0;
   out_5414189356014908953[3] = 0;
   out_5414189356014908953[4] = 1;
   out_5414189356014908953[5] = 0;
   out_5414189356014908953[6] = 0;
   out_5414189356014908953[7] = 0;
   out_5414189356014908953[8] = 0;
   out_5414189356014908953[9] = 0;
   out_5414189356014908953[10] = 0;
   out_5414189356014908953[11] = 0;
   out_5414189356014908953[12] = 0;
   out_5414189356014908953[13] = 0;
   out_5414189356014908953[14] = 1;
   out_5414189356014908953[15] = 0;
   out_5414189356014908953[16] = 0;
   out_5414189356014908953[17] = 0;
}
void h_30(double *state, double *unused, double *out_619654518709855674) {
   out_619654518709855674[0] = state[4];
}
void H_30(double *state, double *unused, double *out_6249010312443216836) {
   out_6249010312443216836[0] = 0;
   out_6249010312443216836[1] = 0;
   out_6249010312443216836[2] = 0;
   out_6249010312443216836[3] = 0;
   out_6249010312443216836[4] = 1;
   out_6249010312443216836[5] = 0;
   out_6249010312443216836[6] = 0;
   out_6249010312443216836[7] = 0;
   out_6249010312443216836[8] = 0;
}
void h_26(double *state, double *unused, double *out_6497940006268570762) {
   out_6497940006268570762[0] = state[7];
}
void H_26(double *state, double *unused, double *out_2636845940712400682) {
   out_2636845940712400682[0] = 0;
   out_2636845940712400682[1] = 0;
   out_2636845940712400682[2] = 0;
   out_2636845940712400682[3] = 0;
   out_2636845940712400682[4] = 0;
   out_2636845940712400682[5] = 0;
   out_2636845940712400682[6] = 0;
   out_2636845940712400682[7] = 1;
   out_2636845940712400682[8] = 0;
}
void h_27(double *state, double *unused, double *out_7293890098408210709) {
   out_7293890098408210709[0] = state[3];
}
void H_27(double *state, double *unused, double *out_4074247000642791925) {
   out_4074247000642791925[0] = 0;
   out_4074247000642791925[1] = 0;
   out_4074247000642791925[2] = 0;
   out_4074247000642791925[3] = 1;
   out_4074247000642791925[4] = 0;
   out_4074247000642791925[5] = 0;
   out_4074247000642791925[6] = 0;
   out_4074247000642791925[7] = 0;
   out_4074247000642791925[8] = 0;
}
void h_29(double *state, double *unused, double *out_3432206621979709057) {
   out_3432206621979709057[0] = state[1];
}
void H_29(double *state, double *unused, double *out_2360884273773240892) {
   out_2360884273773240892[0] = 0;
   out_2360884273773240892[1] = 1;
   out_2360884273773240892[2] = 0;
   out_2360884273773240892[3] = 0;
   out_2360884273773240892[4] = 0;
   out_2360884273773240892[5] = 0;
   out_2360884273773240892[6] = 0;
   out_2360884273773240892[7] = 0;
   out_2360884273773240892[8] = 0;
}
void h_28(double *state, double *unused, double *out_5622082467174375208) {
   out_5622082467174375208[0] = state[0];
}
void H_28(double *state, double *unused, double *out_2721514743296289682) {
   out_2721514743296289682[0] = 1;
   out_2721514743296289682[1] = 0;
   out_2721514743296289682[2] = 0;
   out_2721514743296289682[3] = 0;
   out_2721514743296289682[4] = 0;
   out_2721514743296289682[5] = 0;
   out_2721514743296289682[6] = 0;
   out_2721514743296289682[7] = 0;
   out_2721514743296289682[8] = 0;
}
void h_31(double *state, double *unused, double *out_6998090913890161796) {
   out_6998090913890161796[0] = state[8];
}
void H_31(double *state, double *unused, double *out_6408995221463417334) {
   out_6408995221463417334[0] = 0;
   out_6408995221463417334[1] = 0;
   out_6408995221463417334[2] = 0;
   out_6408995221463417334[3] = 0;
   out_6408995221463417334[4] = 0;
   out_6408995221463417334[5] = 0;
   out_6408995221463417334[6] = 0;
   out_6408995221463417334[7] = 0;
   out_6408995221463417334[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_1038389500972116158) {
  err_fun(nom_x, delta_x, out_1038389500972116158);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6418752408535262595) {
  inv_err_fun(nom_x, true_x, out_6418752408535262595);
}
void car_H_mod_fun(double *state, double *out_2855368609596965229) {
  H_mod_fun(state, out_2855368609596965229);
}
void car_f_fun(double *state, double dt, double *out_1397092929687677159) {
  f_fun(state,  dt, out_1397092929687677159);
}
void car_F_fun(double *state, double dt, double *out_7780451684963738443) {
  F_fun(state,  dt, out_7780451684963738443);
}
void car_h_25(double *state, double *unused, double *out_894848580994361563) {
  h_25(state, unused, out_894848580994361563);
}
void car_H_25(double *state, double *unused, double *out_6378349259586456906) {
  H_25(state, unused, out_6378349259586456906);
}
void car_h_24(double *state, double *unused, double *out_6711296683837743925) {
  h_24(state, unused, out_6711296683837743925);
}
void car_H_24(double *state, double *unused, double *out_5414189356014908953) {
  H_24(state, unused, out_5414189356014908953);
}
void car_h_30(double *state, double *unused, double *out_619654518709855674) {
  h_30(state, unused, out_619654518709855674);
}
void car_H_30(double *state, double *unused, double *out_6249010312443216836) {
  H_30(state, unused, out_6249010312443216836);
}
void car_h_26(double *state, double *unused, double *out_6497940006268570762) {
  h_26(state, unused, out_6497940006268570762);
}
void car_H_26(double *state, double *unused, double *out_2636845940712400682) {
  H_26(state, unused, out_2636845940712400682);
}
void car_h_27(double *state, double *unused, double *out_7293890098408210709) {
  h_27(state, unused, out_7293890098408210709);
}
void car_H_27(double *state, double *unused, double *out_4074247000642791925) {
  H_27(state, unused, out_4074247000642791925);
}
void car_h_29(double *state, double *unused, double *out_3432206621979709057) {
  h_29(state, unused, out_3432206621979709057);
}
void car_H_29(double *state, double *unused, double *out_2360884273773240892) {
  H_29(state, unused, out_2360884273773240892);
}
void car_h_28(double *state, double *unused, double *out_5622082467174375208) {
  h_28(state, unused, out_5622082467174375208);
}
void car_H_28(double *state, double *unused, double *out_2721514743296289682) {
  H_28(state, unused, out_2721514743296289682);
}
void car_h_31(double *state, double *unused, double *out_6998090913890161796) {
  h_31(state, unused, out_6998090913890161796);
}
void car_H_31(double *state, double *unused, double *out_6408995221463417334) {
  H_31(state, unused, out_6408995221463417334);
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
