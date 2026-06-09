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
void err_fun(double *nom_x, double *delta_x, double *out_427394908214603769) {
   out_427394908214603769[0] = delta_x[0] + nom_x[0];
   out_427394908214603769[1] = delta_x[1] + nom_x[1];
   out_427394908214603769[2] = delta_x[2] + nom_x[2];
   out_427394908214603769[3] = delta_x[3] + nom_x[3];
   out_427394908214603769[4] = delta_x[4] + nom_x[4];
   out_427394908214603769[5] = delta_x[5] + nom_x[5];
   out_427394908214603769[6] = delta_x[6] + nom_x[6];
   out_427394908214603769[7] = delta_x[7] + nom_x[7];
   out_427394908214603769[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6917755431586495523) {
   out_6917755431586495523[0] = -nom_x[0] + true_x[0];
   out_6917755431586495523[1] = -nom_x[1] + true_x[1];
   out_6917755431586495523[2] = -nom_x[2] + true_x[2];
   out_6917755431586495523[3] = -nom_x[3] + true_x[3];
   out_6917755431586495523[4] = -nom_x[4] + true_x[4];
   out_6917755431586495523[5] = -nom_x[5] + true_x[5];
   out_6917755431586495523[6] = -nom_x[6] + true_x[6];
   out_6917755431586495523[7] = -nom_x[7] + true_x[7];
   out_6917755431586495523[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_5029836486716929516) {
   out_5029836486716929516[0] = 1.0;
   out_5029836486716929516[1] = 0.0;
   out_5029836486716929516[2] = 0.0;
   out_5029836486716929516[3] = 0.0;
   out_5029836486716929516[4] = 0.0;
   out_5029836486716929516[5] = 0.0;
   out_5029836486716929516[6] = 0.0;
   out_5029836486716929516[7] = 0.0;
   out_5029836486716929516[8] = 0.0;
   out_5029836486716929516[9] = 0.0;
   out_5029836486716929516[10] = 1.0;
   out_5029836486716929516[11] = 0.0;
   out_5029836486716929516[12] = 0.0;
   out_5029836486716929516[13] = 0.0;
   out_5029836486716929516[14] = 0.0;
   out_5029836486716929516[15] = 0.0;
   out_5029836486716929516[16] = 0.0;
   out_5029836486716929516[17] = 0.0;
   out_5029836486716929516[18] = 0.0;
   out_5029836486716929516[19] = 0.0;
   out_5029836486716929516[20] = 1.0;
   out_5029836486716929516[21] = 0.0;
   out_5029836486716929516[22] = 0.0;
   out_5029836486716929516[23] = 0.0;
   out_5029836486716929516[24] = 0.0;
   out_5029836486716929516[25] = 0.0;
   out_5029836486716929516[26] = 0.0;
   out_5029836486716929516[27] = 0.0;
   out_5029836486716929516[28] = 0.0;
   out_5029836486716929516[29] = 0.0;
   out_5029836486716929516[30] = 1.0;
   out_5029836486716929516[31] = 0.0;
   out_5029836486716929516[32] = 0.0;
   out_5029836486716929516[33] = 0.0;
   out_5029836486716929516[34] = 0.0;
   out_5029836486716929516[35] = 0.0;
   out_5029836486716929516[36] = 0.0;
   out_5029836486716929516[37] = 0.0;
   out_5029836486716929516[38] = 0.0;
   out_5029836486716929516[39] = 0.0;
   out_5029836486716929516[40] = 1.0;
   out_5029836486716929516[41] = 0.0;
   out_5029836486716929516[42] = 0.0;
   out_5029836486716929516[43] = 0.0;
   out_5029836486716929516[44] = 0.0;
   out_5029836486716929516[45] = 0.0;
   out_5029836486716929516[46] = 0.0;
   out_5029836486716929516[47] = 0.0;
   out_5029836486716929516[48] = 0.0;
   out_5029836486716929516[49] = 0.0;
   out_5029836486716929516[50] = 1.0;
   out_5029836486716929516[51] = 0.0;
   out_5029836486716929516[52] = 0.0;
   out_5029836486716929516[53] = 0.0;
   out_5029836486716929516[54] = 0.0;
   out_5029836486716929516[55] = 0.0;
   out_5029836486716929516[56] = 0.0;
   out_5029836486716929516[57] = 0.0;
   out_5029836486716929516[58] = 0.0;
   out_5029836486716929516[59] = 0.0;
   out_5029836486716929516[60] = 1.0;
   out_5029836486716929516[61] = 0.0;
   out_5029836486716929516[62] = 0.0;
   out_5029836486716929516[63] = 0.0;
   out_5029836486716929516[64] = 0.0;
   out_5029836486716929516[65] = 0.0;
   out_5029836486716929516[66] = 0.0;
   out_5029836486716929516[67] = 0.0;
   out_5029836486716929516[68] = 0.0;
   out_5029836486716929516[69] = 0.0;
   out_5029836486716929516[70] = 1.0;
   out_5029836486716929516[71] = 0.0;
   out_5029836486716929516[72] = 0.0;
   out_5029836486716929516[73] = 0.0;
   out_5029836486716929516[74] = 0.0;
   out_5029836486716929516[75] = 0.0;
   out_5029836486716929516[76] = 0.0;
   out_5029836486716929516[77] = 0.0;
   out_5029836486716929516[78] = 0.0;
   out_5029836486716929516[79] = 0.0;
   out_5029836486716929516[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_8683428782768045604) {
   out_8683428782768045604[0] = state[0];
   out_8683428782768045604[1] = state[1];
   out_8683428782768045604[2] = state[2];
   out_8683428782768045604[3] = state[3];
   out_8683428782768045604[4] = state[4];
   out_8683428782768045604[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_8683428782768045604[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_8683428782768045604[7] = state[7];
   out_8683428782768045604[8] = state[8];
}
void F_fun(double *state, double dt, double *out_2206128918366291311) {
   out_2206128918366291311[0] = 1;
   out_2206128918366291311[1] = 0;
   out_2206128918366291311[2] = 0;
   out_2206128918366291311[3] = 0;
   out_2206128918366291311[4] = 0;
   out_2206128918366291311[5] = 0;
   out_2206128918366291311[6] = 0;
   out_2206128918366291311[7] = 0;
   out_2206128918366291311[8] = 0;
   out_2206128918366291311[9] = 0;
   out_2206128918366291311[10] = 1;
   out_2206128918366291311[11] = 0;
   out_2206128918366291311[12] = 0;
   out_2206128918366291311[13] = 0;
   out_2206128918366291311[14] = 0;
   out_2206128918366291311[15] = 0;
   out_2206128918366291311[16] = 0;
   out_2206128918366291311[17] = 0;
   out_2206128918366291311[18] = 0;
   out_2206128918366291311[19] = 0;
   out_2206128918366291311[20] = 1;
   out_2206128918366291311[21] = 0;
   out_2206128918366291311[22] = 0;
   out_2206128918366291311[23] = 0;
   out_2206128918366291311[24] = 0;
   out_2206128918366291311[25] = 0;
   out_2206128918366291311[26] = 0;
   out_2206128918366291311[27] = 0;
   out_2206128918366291311[28] = 0;
   out_2206128918366291311[29] = 0;
   out_2206128918366291311[30] = 1;
   out_2206128918366291311[31] = 0;
   out_2206128918366291311[32] = 0;
   out_2206128918366291311[33] = 0;
   out_2206128918366291311[34] = 0;
   out_2206128918366291311[35] = 0;
   out_2206128918366291311[36] = 0;
   out_2206128918366291311[37] = 0;
   out_2206128918366291311[38] = 0;
   out_2206128918366291311[39] = 0;
   out_2206128918366291311[40] = 1;
   out_2206128918366291311[41] = 0;
   out_2206128918366291311[42] = 0;
   out_2206128918366291311[43] = 0;
   out_2206128918366291311[44] = 0;
   out_2206128918366291311[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_2206128918366291311[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_2206128918366291311[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2206128918366291311[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2206128918366291311[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_2206128918366291311[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_2206128918366291311[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_2206128918366291311[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_2206128918366291311[53] = -9.8100000000000005*dt;
   out_2206128918366291311[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_2206128918366291311[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_2206128918366291311[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2206128918366291311[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2206128918366291311[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_2206128918366291311[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_2206128918366291311[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_2206128918366291311[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2206128918366291311[62] = 0;
   out_2206128918366291311[63] = 0;
   out_2206128918366291311[64] = 0;
   out_2206128918366291311[65] = 0;
   out_2206128918366291311[66] = 0;
   out_2206128918366291311[67] = 0;
   out_2206128918366291311[68] = 0;
   out_2206128918366291311[69] = 0;
   out_2206128918366291311[70] = 1;
   out_2206128918366291311[71] = 0;
   out_2206128918366291311[72] = 0;
   out_2206128918366291311[73] = 0;
   out_2206128918366291311[74] = 0;
   out_2206128918366291311[75] = 0;
   out_2206128918366291311[76] = 0;
   out_2206128918366291311[77] = 0;
   out_2206128918366291311[78] = 0;
   out_2206128918366291311[79] = 0;
   out_2206128918366291311[80] = 1;
}
void h_25(double *state, double *unused, double *out_2868926674989135743) {
   out_2868926674989135743[0] = state[6];
}
void H_25(double *state, double *unused, double *out_4223719361080384863) {
   out_4223719361080384863[0] = 0;
   out_4223719361080384863[1] = 0;
   out_4223719361080384863[2] = 0;
   out_4223719361080384863[3] = 0;
   out_4223719361080384863[4] = 0;
   out_4223719361080384863[5] = 0;
   out_4223719361080384863[6] = 1;
   out_4223719361080384863[7] = 0;
   out_4223719361080384863[8] = 0;
}
void h_24(double *state, double *unused, double *out_3559695939338705622) {
   out_3559695939338705622[0] = state[4];
   out_3559695939338705622[1] = state[5];
}
void H_24(double *state, double *unused, double *out_2051069762074885297) {
   out_2051069762074885297[0] = 0;
   out_2051069762074885297[1] = 0;
   out_2051069762074885297[2] = 0;
   out_2051069762074885297[3] = 0;
   out_2051069762074885297[4] = 1;
   out_2051069762074885297[5] = 0;
   out_2051069762074885297[6] = 0;
   out_2051069762074885297[7] = 0;
   out_2051069762074885297[8] = 0;
   out_2051069762074885297[9] = 0;
   out_2051069762074885297[10] = 0;
   out_2051069762074885297[11] = 0;
   out_2051069762074885297[12] = 0;
   out_2051069762074885297[13] = 0;
   out_2051069762074885297[14] = 1;
   out_2051069762074885297[15] = 0;
   out_2051069762074885297[16] = 0;
   out_2051069762074885297[17] = 0;
}
void h_30(double *state, double *unused, double *out_5012345975764913442) {
   out_5012345975764913442[0] = state[4];
}
void H_30(double *state, double *unused, double *out_7306334371137549998) {
   out_7306334371137549998[0] = 0;
   out_7306334371137549998[1] = 0;
   out_7306334371137549998[2] = 0;
   out_7306334371137549998[3] = 0;
   out_7306334371137549998[4] = 1;
   out_7306334371137549998[5] = 0;
   out_7306334371137549998[6] = 0;
   out_7306334371137549998[7] = 0;
   out_7306334371137549998[8] = 0;
}
void h_26(double *state, double *unused, double *out_4184796142913956623) {
   out_4184796142913956623[0] = state[7];
}
void H_26(double *state, double *unused, double *out_482216042206328639) {
   out_482216042206328639[0] = 0;
   out_482216042206328639[1] = 0;
   out_482216042206328639[2] = 0;
   out_482216042206328639[3] = 0;
   out_482216042206328639[4] = 0;
   out_482216042206328639[5] = 0;
   out_482216042206328639[6] = 0;
   out_482216042206328639[7] = 1;
   out_482216042206328639[8] = 0;
}
void h_27(double *state, double *unused, double *out_2132746592671709902) {
   out_2132746592671709902[0] = state[3];
}
void H_27(double *state, double *unused, double *out_8965646390771576707) {
   out_8965646390771576707[0] = 0;
   out_8965646390771576707[1] = 0;
   out_8965646390771576707[2] = 0;
   out_8965646390771576707[3] = 1;
   out_8965646390771576707[4] = 0;
   out_8965646390771576707[5] = 0;
   out_8965646390771576707[6] = 0;
   out_8965646390771576707[7] = 0;
   out_8965646390771576707[8] = 0;
}
void h_29(double *state, double *unused, double *out_1975559924320580757) {
   out_1975559924320580757[0] = state[1];
}
void H_29(double *state, double *unused, double *out_7252283663902025674) {
   out_7252283663902025674[0] = 0;
   out_7252283663902025674[1] = 1;
   out_7252283663902025674[2] = 0;
   out_7252283663902025674[3] = 0;
   out_7252283663902025674[4] = 0;
   out_7252283663902025674[5] = 0;
   out_7252283663902025674[6] = 0;
   out_7252283663902025674[7] = 0;
   out_7252283663902025674[8] = 0;
}
void h_28(double *state, double *unused, double *out_2829633405009583330) {
   out_2829633405009583330[0] = state[0];
}
void H_28(double *state, double *unused, double *out_2169884646832495100) {
   out_2169884646832495100[0] = 1;
   out_2169884646832495100[1] = 0;
   out_2169884646832495100[2] = 0;
   out_2169884646832495100[3] = 0;
   out_2169884646832495100[4] = 0;
   out_2169884646832495100[5] = 0;
   out_2169884646832495100[6] = 0;
   out_2169884646832495100[7] = 0;
   out_2169884646832495100[8] = 0;
}
void h_31(double *state, double *unused, double *out_1418295282360252576) {
   out_1418295282360252576[0] = state[8];
}
void H_31(double *state, double *unused, double *out_4254365322957345291) {
   out_4254365322957345291[0] = 0;
   out_4254365322957345291[1] = 0;
   out_4254365322957345291[2] = 0;
   out_4254365322957345291[3] = 0;
   out_4254365322957345291[4] = 0;
   out_4254365322957345291[5] = 0;
   out_4254365322957345291[6] = 0;
   out_4254365322957345291[7] = 0;
   out_4254365322957345291[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_427394908214603769) {
  err_fun(nom_x, delta_x, out_427394908214603769);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6917755431586495523) {
  inv_err_fun(nom_x, true_x, out_6917755431586495523);
}
void car_H_mod_fun(double *state, double *out_5029836486716929516) {
  H_mod_fun(state, out_5029836486716929516);
}
void car_f_fun(double *state, double dt, double *out_8683428782768045604) {
  f_fun(state,  dt, out_8683428782768045604);
}
void car_F_fun(double *state, double dt, double *out_2206128918366291311) {
  F_fun(state,  dt, out_2206128918366291311);
}
void car_h_25(double *state, double *unused, double *out_2868926674989135743) {
  h_25(state, unused, out_2868926674989135743);
}
void car_H_25(double *state, double *unused, double *out_4223719361080384863) {
  H_25(state, unused, out_4223719361080384863);
}
void car_h_24(double *state, double *unused, double *out_3559695939338705622) {
  h_24(state, unused, out_3559695939338705622);
}
void car_H_24(double *state, double *unused, double *out_2051069762074885297) {
  H_24(state, unused, out_2051069762074885297);
}
void car_h_30(double *state, double *unused, double *out_5012345975764913442) {
  h_30(state, unused, out_5012345975764913442);
}
void car_H_30(double *state, double *unused, double *out_7306334371137549998) {
  H_30(state, unused, out_7306334371137549998);
}
void car_h_26(double *state, double *unused, double *out_4184796142913956623) {
  h_26(state, unused, out_4184796142913956623);
}
void car_H_26(double *state, double *unused, double *out_482216042206328639) {
  H_26(state, unused, out_482216042206328639);
}
void car_h_27(double *state, double *unused, double *out_2132746592671709902) {
  h_27(state, unused, out_2132746592671709902);
}
void car_H_27(double *state, double *unused, double *out_8965646390771576707) {
  H_27(state, unused, out_8965646390771576707);
}
void car_h_29(double *state, double *unused, double *out_1975559924320580757) {
  h_29(state, unused, out_1975559924320580757);
}
void car_H_29(double *state, double *unused, double *out_7252283663902025674) {
  H_29(state, unused, out_7252283663902025674);
}
void car_h_28(double *state, double *unused, double *out_2829633405009583330) {
  h_28(state, unused, out_2829633405009583330);
}
void car_H_28(double *state, double *unused, double *out_2169884646832495100) {
  H_28(state, unused, out_2169884646832495100);
}
void car_h_31(double *state, double *unused, double *out_1418295282360252576) {
  h_31(state, unused, out_1418295282360252576);
}
void car_H_31(double *state, double *unused, double *out_4254365322957345291) {
  H_31(state, unused, out_4254365322957345291);
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
