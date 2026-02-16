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
 *                       Code generated with SymPy 1.12                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_9079002193507214447) {
   out_9079002193507214447[0] = delta_x[0] + nom_x[0];
   out_9079002193507214447[1] = delta_x[1] + nom_x[1];
   out_9079002193507214447[2] = delta_x[2] + nom_x[2];
   out_9079002193507214447[3] = delta_x[3] + nom_x[3];
   out_9079002193507214447[4] = delta_x[4] + nom_x[4];
   out_9079002193507214447[5] = delta_x[5] + nom_x[5];
   out_9079002193507214447[6] = delta_x[6] + nom_x[6];
   out_9079002193507214447[7] = delta_x[7] + nom_x[7];
   out_9079002193507214447[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_28192897299460748) {
   out_28192897299460748[0] = -nom_x[0] + true_x[0];
   out_28192897299460748[1] = -nom_x[1] + true_x[1];
   out_28192897299460748[2] = -nom_x[2] + true_x[2];
   out_28192897299460748[3] = -nom_x[3] + true_x[3];
   out_28192897299460748[4] = -nom_x[4] + true_x[4];
   out_28192897299460748[5] = -nom_x[5] + true_x[5];
   out_28192897299460748[6] = -nom_x[6] + true_x[6];
   out_28192897299460748[7] = -nom_x[7] + true_x[7];
   out_28192897299460748[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_1429112410127945448) {
   out_1429112410127945448[0] = 1.0;
   out_1429112410127945448[1] = 0;
   out_1429112410127945448[2] = 0;
   out_1429112410127945448[3] = 0;
   out_1429112410127945448[4] = 0;
   out_1429112410127945448[5] = 0;
   out_1429112410127945448[6] = 0;
   out_1429112410127945448[7] = 0;
   out_1429112410127945448[8] = 0;
   out_1429112410127945448[9] = 0;
   out_1429112410127945448[10] = 1.0;
   out_1429112410127945448[11] = 0;
   out_1429112410127945448[12] = 0;
   out_1429112410127945448[13] = 0;
   out_1429112410127945448[14] = 0;
   out_1429112410127945448[15] = 0;
   out_1429112410127945448[16] = 0;
   out_1429112410127945448[17] = 0;
   out_1429112410127945448[18] = 0;
   out_1429112410127945448[19] = 0;
   out_1429112410127945448[20] = 1.0;
   out_1429112410127945448[21] = 0;
   out_1429112410127945448[22] = 0;
   out_1429112410127945448[23] = 0;
   out_1429112410127945448[24] = 0;
   out_1429112410127945448[25] = 0;
   out_1429112410127945448[26] = 0;
   out_1429112410127945448[27] = 0;
   out_1429112410127945448[28] = 0;
   out_1429112410127945448[29] = 0;
   out_1429112410127945448[30] = 1.0;
   out_1429112410127945448[31] = 0;
   out_1429112410127945448[32] = 0;
   out_1429112410127945448[33] = 0;
   out_1429112410127945448[34] = 0;
   out_1429112410127945448[35] = 0;
   out_1429112410127945448[36] = 0;
   out_1429112410127945448[37] = 0;
   out_1429112410127945448[38] = 0;
   out_1429112410127945448[39] = 0;
   out_1429112410127945448[40] = 1.0;
   out_1429112410127945448[41] = 0;
   out_1429112410127945448[42] = 0;
   out_1429112410127945448[43] = 0;
   out_1429112410127945448[44] = 0;
   out_1429112410127945448[45] = 0;
   out_1429112410127945448[46] = 0;
   out_1429112410127945448[47] = 0;
   out_1429112410127945448[48] = 0;
   out_1429112410127945448[49] = 0;
   out_1429112410127945448[50] = 1.0;
   out_1429112410127945448[51] = 0;
   out_1429112410127945448[52] = 0;
   out_1429112410127945448[53] = 0;
   out_1429112410127945448[54] = 0;
   out_1429112410127945448[55] = 0;
   out_1429112410127945448[56] = 0;
   out_1429112410127945448[57] = 0;
   out_1429112410127945448[58] = 0;
   out_1429112410127945448[59] = 0;
   out_1429112410127945448[60] = 1.0;
   out_1429112410127945448[61] = 0;
   out_1429112410127945448[62] = 0;
   out_1429112410127945448[63] = 0;
   out_1429112410127945448[64] = 0;
   out_1429112410127945448[65] = 0;
   out_1429112410127945448[66] = 0;
   out_1429112410127945448[67] = 0;
   out_1429112410127945448[68] = 0;
   out_1429112410127945448[69] = 0;
   out_1429112410127945448[70] = 1.0;
   out_1429112410127945448[71] = 0;
   out_1429112410127945448[72] = 0;
   out_1429112410127945448[73] = 0;
   out_1429112410127945448[74] = 0;
   out_1429112410127945448[75] = 0;
   out_1429112410127945448[76] = 0;
   out_1429112410127945448[77] = 0;
   out_1429112410127945448[78] = 0;
   out_1429112410127945448[79] = 0;
   out_1429112410127945448[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_8589483517240840993) {
   out_8589483517240840993[0] = state[0];
   out_8589483517240840993[1] = state[1];
   out_8589483517240840993[2] = state[2];
   out_8589483517240840993[3] = state[3];
   out_8589483517240840993[4] = state[4];
   out_8589483517240840993[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_8589483517240840993[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_8589483517240840993[7] = state[7];
   out_8589483517240840993[8] = state[8];
}
void F_fun(double *state, double dt, double *out_7186420185024843086) {
   out_7186420185024843086[0] = 1;
   out_7186420185024843086[1] = 0;
   out_7186420185024843086[2] = 0;
   out_7186420185024843086[3] = 0;
   out_7186420185024843086[4] = 0;
   out_7186420185024843086[5] = 0;
   out_7186420185024843086[6] = 0;
   out_7186420185024843086[7] = 0;
   out_7186420185024843086[8] = 0;
   out_7186420185024843086[9] = 0;
   out_7186420185024843086[10] = 1;
   out_7186420185024843086[11] = 0;
   out_7186420185024843086[12] = 0;
   out_7186420185024843086[13] = 0;
   out_7186420185024843086[14] = 0;
   out_7186420185024843086[15] = 0;
   out_7186420185024843086[16] = 0;
   out_7186420185024843086[17] = 0;
   out_7186420185024843086[18] = 0;
   out_7186420185024843086[19] = 0;
   out_7186420185024843086[20] = 1;
   out_7186420185024843086[21] = 0;
   out_7186420185024843086[22] = 0;
   out_7186420185024843086[23] = 0;
   out_7186420185024843086[24] = 0;
   out_7186420185024843086[25] = 0;
   out_7186420185024843086[26] = 0;
   out_7186420185024843086[27] = 0;
   out_7186420185024843086[28] = 0;
   out_7186420185024843086[29] = 0;
   out_7186420185024843086[30] = 1;
   out_7186420185024843086[31] = 0;
   out_7186420185024843086[32] = 0;
   out_7186420185024843086[33] = 0;
   out_7186420185024843086[34] = 0;
   out_7186420185024843086[35] = 0;
   out_7186420185024843086[36] = 0;
   out_7186420185024843086[37] = 0;
   out_7186420185024843086[38] = 0;
   out_7186420185024843086[39] = 0;
   out_7186420185024843086[40] = 1;
   out_7186420185024843086[41] = 0;
   out_7186420185024843086[42] = 0;
   out_7186420185024843086[43] = 0;
   out_7186420185024843086[44] = 0;
   out_7186420185024843086[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_7186420185024843086[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_7186420185024843086[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7186420185024843086[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_7186420185024843086[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_7186420185024843086[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_7186420185024843086[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_7186420185024843086[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_7186420185024843086[53] = -9.8000000000000007*dt;
   out_7186420185024843086[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_7186420185024843086[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_7186420185024843086[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7186420185024843086[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7186420185024843086[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_7186420185024843086[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_7186420185024843086[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_7186420185024843086[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_7186420185024843086[62] = 0;
   out_7186420185024843086[63] = 0;
   out_7186420185024843086[64] = 0;
   out_7186420185024843086[65] = 0;
   out_7186420185024843086[66] = 0;
   out_7186420185024843086[67] = 0;
   out_7186420185024843086[68] = 0;
   out_7186420185024843086[69] = 0;
   out_7186420185024843086[70] = 1;
   out_7186420185024843086[71] = 0;
   out_7186420185024843086[72] = 0;
   out_7186420185024843086[73] = 0;
   out_7186420185024843086[74] = 0;
   out_7186420185024843086[75] = 0;
   out_7186420185024843086[76] = 0;
   out_7186420185024843086[77] = 0;
   out_7186420185024843086[78] = 0;
   out_7186420185024843086[79] = 0;
   out_7186420185024843086[80] = 1;
}
void h_25(double *state, double *unused, double *out_9042730217037280690) {
   out_9042730217037280690[0] = state[6];
}
void H_25(double *state, double *unused, double *out_7718077913416356474) {
   out_7718077913416356474[0] = 0;
   out_7718077913416356474[1] = 0;
   out_7718077913416356474[2] = 0;
   out_7718077913416356474[3] = 0;
   out_7718077913416356474[4] = 0;
   out_7718077913416356474[5] = 0;
   out_7718077913416356474[6] = 1;
   out_7718077913416356474[7] = 0;
   out_7718077913416356474[8] = 0;
}
void h_24(double *state, double *unused, double *out_8810898373805104119) {
   out_8810898373805104119[0] = state[4];
   out_8810898373805104119[1] = state[5];
}
void H_24(double *state, double *unused, double *out_5545428314410856908) {
   out_5545428314410856908[0] = 0;
   out_5545428314410856908[1] = 0;
   out_5545428314410856908[2] = 0;
   out_5545428314410856908[3] = 0;
   out_5545428314410856908[4] = 1;
   out_5545428314410856908[5] = 0;
   out_5545428314410856908[6] = 0;
   out_5545428314410856908[7] = 0;
   out_5545428314410856908[8] = 0;
   out_5545428314410856908[9] = 0;
   out_5545428314410856908[10] = 0;
   out_5545428314410856908[11] = 0;
   out_5545428314410856908[12] = 0;
   out_5545428314410856908[13] = 0;
   out_5545428314410856908[14] = 1;
   out_5545428314410856908[15] = 0;
   out_5545428314410856908[16] = 0;
   out_5545428314410856908[17] = 0;
}
void h_30(double *state, double *unused, double *out_3128997190366532317) {
   out_3128997190366532317[0] = state[4];
}
void H_30(double *state, double *unused, double *out_8210333201785946515) {
   out_8210333201785946515[0] = 0;
   out_8210333201785946515[1] = 0;
   out_8210333201785946515[2] = 0;
   out_8210333201785946515[3] = 0;
   out_8210333201785946515[4] = 1;
   out_8210333201785946515[5] = 0;
   out_8210333201785946515[6] = 0;
   out_8210333201785946515[7] = 0;
   out_8210333201785946515[8] = 0;
}
void h_26(double *state, double *unused, double *out_1268954890915096695) {
   out_1268954890915096695[0] = state[7];
}
void H_26(double *state, double *unused, double *out_7424140190532394541) {
   out_7424140190532394541[0] = 0;
   out_7424140190532394541[1] = 0;
   out_7424140190532394541[2] = 0;
   out_7424140190532394541[3] = 0;
   out_7424140190532394541[4] = 0;
   out_7424140190532394541[5] = 0;
   out_7424140190532394541[6] = 0;
   out_7424140190532394541[7] = 1;
   out_7424140190532394541[8] = 0;
}
void h_27(double *state, double *unused, double *out_2643688699623431544) {
   out_2643688699623431544[0] = state[3];
}
void H_27(double *state, double *unused, double *out_5986739130602003298) {
   out_5986739130602003298[0] = 0;
   out_5986739130602003298[1] = 0;
   out_5986739130602003298[2] = 0;
   out_5986739130602003298[3] = 1;
   out_5986739130602003298[4] = 0;
   out_5986739130602003298[5] = 0;
   out_5986739130602003298[6] = 0;
   out_5986739130602003298[7] = 0;
   out_5986739130602003298[8] = 0;
}
void h_29(double *state, double *unused, double *out_2185487337464869882) {
   out_2185487337464869882[0] = state[1];
}
void H_29(double *state, double *unused, double *out_7700101857471554331) {
   out_7700101857471554331[0] = 0;
   out_7700101857471554331[1] = 1;
   out_7700101857471554331[2] = 0;
   out_7700101857471554331[3] = 0;
   out_7700101857471554331[4] = 0;
   out_7700101857471554331[5] = 0;
   out_7700101857471554331[6] = 0;
   out_7700101857471554331[7] = 0;
   out_7700101857471554331[8] = 0;
}
void h_28(double *state, double *unused, double *out_3247004584299909061) {
   out_3247004584299909061[0] = state[0];
}
void H_28(double *state, double *unused, double *out_5664243199168466711) {
   out_5664243199168466711[0] = 1;
   out_5664243199168466711[1] = 0;
   out_5664243199168466711[2] = 0;
   out_5664243199168466711[3] = 0;
   out_5664243199168466711[4] = 0;
   out_5664243199168466711[5] = 0;
   out_5664243199168466711[6] = 0;
   out_5664243199168466711[7] = 0;
   out_5664243199168466711[8] = 0;
}
void h_31(double *state, double *unused, double *out_92965819725873521) {
   out_92965819725873521[0] = state[8];
}
void H_31(double *state, double *unused, double *out_8050348292765746017) {
   out_8050348292765746017[0] = 0;
   out_8050348292765746017[1] = 0;
   out_8050348292765746017[2] = 0;
   out_8050348292765746017[3] = 0;
   out_8050348292765746017[4] = 0;
   out_8050348292765746017[5] = 0;
   out_8050348292765746017[6] = 0;
   out_8050348292765746017[7] = 0;
   out_8050348292765746017[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_9079002193507214447) {
  err_fun(nom_x, delta_x, out_9079002193507214447);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_28192897299460748) {
  inv_err_fun(nom_x, true_x, out_28192897299460748);
}
void car_H_mod_fun(double *state, double *out_1429112410127945448) {
  H_mod_fun(state, out_1429112410127945448);
}
void car_f_fun(double *state, double dt, double *out_8589483517240840993) {
  f_fun(state,  dt, out_8589483517240840993);
}
void car_F_fun(double *state, double dt, double *out_7186420185024843086) {
  F_fun(state,  dt, out_7186420185024843086);
}
void car_h_25(double *state, double *unused, double *out_9042730217037280690) {
  h_25(state, unused, out_9042730217037280690);
}
void car_H_25(double *state, double *unused, double *out_7718077913416356474) {
  H_25(state, unused, out_7718077913416356474);
}
void car_h_24(double *state, double *unused, double *out_8810898373805104119) {
  h_24(state, unused, out_8810898373805104119);
}
void car_H_24(double *state, double *unused, double *out_5545428314410856908) {
  H_24(state, unused, out_5545428314410856908);
}
void car_h_30(double *state, double *unused, double *out_3128997190366532317) {
  h_30(state, unused, out_3128997190366532317);
}
void car_H_30(double *state, double *unused, double *out_8210333201785946515) {
  H_30(state, unused, out_8210333201785946515);
}
void car_h_26(double *state, double *unused, double *out_1268954890915096695) {
  h_26(state, unused, out_1268954890915096695);
}
void car_H_26(double *state, double *unused, double *out_7424140190532394541) {
  H_26(state, unused, out_7424140190532394541);
}
void car_h_27(double *state, double *unused, double *out_2643688699623431544) {
  h_27(state, unused, out_2643688699623431544);
}
void car_H_27(double *state, double *unused, double *out_5986739130602003298) {
  H_27(state, unused, out_5986739130602003298);
}
void car_h_29(double *state, double *unused, double *out_2185487337464869882) {
  h_29(state, unused, out_2185487337464869882);
}
void car_H_29(double *state, double *unused, double *out_7700101857471554331) {
  H_29(state, unused, out_7700101857471554331);
}
void car_h_28(double *state, double *unused, double *out_3247004584299909061) {
  h_28(state, unused, out_3247004584299909061);
}
void car_H_28(double *state, double *unused, double *out_5664243199168466711) {
  H_28(state, unused, out_5664243199168466711);
}
void car_h_31(double *state, double *unused, double *out_92965819725873521) {
  h_31(state, unused, out_92965819725873521);
}
void car_H_31(double *state, double *unused, double *out_8050348292765746017) {
  H_31(state, unused, out_8050348292765746017);
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
