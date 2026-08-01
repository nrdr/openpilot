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
void err_fun(double *nom_x, double *delta_x, double *out_4054919672849218704) {
   out_4054919672849218704[0] = delta_x[0] + nom_x[0];
   out_4054919672849218704[1] = delta_x[1] + nom_x[1];
   out_4054919672849218704[2] = delta_x[2] + nom_x[2];
   out_4054919672849218704[3] = delta_x[3] + nom_x[3];
   out_4054919672849218704[4] = delta_x[4] + nom_x[4];
   out_4054919672849218704[5] = delta_x[5] + nom_x[5];
   out_4054919672849218704[6] = delta_x[6] + nom_x[6];
   out_4054919672849218704[7] = delta_x[7] + nom_x[7];
   out_4054919672849218704[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_8915081128527086766) {
   out_8915081128527086766[0] = -nom_x[0] + true_x[0];
   out_8915081128527086766[1] = -nom_x[1] + true_x[1];
   out_8915081128527086766[2] = -nom_x[2] + true_x[2];
   out_8915081128527086766[3] = -nom_x[3] + true_x[3];
   out_8915081128527086766[4] = -nom_x[4] + true_x[4];
   out_8915081128527086766[5] = -nom_x[5] + true_x[5];
   out_8915081128527086766[6] = -nom_x[6] + true_x[6];
   out_8915081128527086766[7] = -nom_x[7] + true_x[7];
   out_8915081128527086766[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_4619144397706641630) {
   out_4619144397706641630[0] = 1.0;
   out_4619144397706641630[1] = 0.0;
   out_4619144397706641630[2] = 0.0;
   out_4619144397706641630[3] = 0.0;
   out_4619144397706641630[4] = 0.0;
   out_4619144397706641630[5] = 0.0;
   out_4619144397706641630[6] = 0.0;
   out_4619144397706641630[7] = 0.0;
   out_4619144397706641630[8] = 0.0;
   out_4619144397706641630[9] = 0.0;
   out_4619144397706641630[10] = 1.0;
   out_4619144397706641630[11] = 0.0;
   out_4619144397706641630[12] = 0.0;
   out_4619144397706641630[13] = 0.0;
   out_4619144397706641630[14] = 0.0;
   out_4619144397706641630[15] = 0.0;
   out_4619144397706641630[16] = 0.0;
   out_4619144397706641630[17] = 0.0;
   out_4619144397706641630[18] = 0.0;
   out_4619144397706641630[19] = 0.0;
   out_4619144397706641630[20] = 1.0;
   out_4619144397706641630[21] = 0.0;
   out_4619144397706641630[22] = 0.0;
   out_4619144397706641630[23] = 0.0;
   out_4619144397706641630[24] = 0.0;
   out_4619144397706641630[25] = 0.0;
   out_4619144397706641630[26] = 0.0;
   out_4619144397706641630[27] = 0.0;
   out_4619144397706641630[28] = 0.0;
   out_4619144397706641630[29] = 0.0;
   out_4619144397706641630[30] = 1.0;
   out_4619144397706641630[31] = 0.0;
   out_4619144397706641630[32] = 0.0;
   out_4619144397706641630[33] = 0.0;
   out_4619144397706641630[34] = 0.0;
   out_4619144397706641630[35] = 0.0;
   out_4619144397706641630[36] = 0.0;
   out_4619144397706641630[37] = 0.0;
   out_4619144397706641630[38] = 0.0;
   out_4619144397706641630[39] = 0.0;
   out_4619144397706641630[40] = 1.0;
   out_4619144397706641630[41] = 0.0;
   out_4619144397706641630[42] = 0.0;
   out_4619144397706641630[43] = 0.0;
   out_4619144397706641630[44] = 0.0;
   out_4619144397706641630[45] = 0.0;
   out_4619144397706641630[46] = 0.0;
   out_4619144397706641630[47] = 0.0;
   out_4619144397706641630[48] = 0.0;
   out_4619144397706641630[49] = 0.0;
   out_4619144397706641630[50] = 1.0;
   out_4619144397706641630[51] = 0.0;
   out_4619144397706641630[52] = 0.0;
   out_4619144397706641630[53] = 0.0;
   out_4619144397706641630[54] = 0.0;
   out_4619144397706641630[55] = 0.0;
   out_4619144397706641630[56] = 0.0;
   out_4619144397706641630[57] = 0.0;
   out_4619144397706641630[58] = 0.0;
   out_4619144397706641630[59] = 0.0;
   out_4619144397706641630[60] = 1.0;
   out_4619144397706641630[61] = 0.0;
   out_4619144397706641630[62] = 0.0;
   out_4619144397706641630[63] = 0.0;
   out_4619144397706641630[64] = 0.0;
   out_4619144397706641630[65] = 0.0;
   out_4619144397706641630[66] = 0.0;
   out_4619144397706641630[67] = 0.0;
   out_4619144397706641630[68] = 0.0;
   out_4619144397706641630[69] = 0.0;
   out_4619144397706641630[70] = 1.0;
   out_4619144397706641630[71] = 0.0;
   out_4619144397706641630[72] = 0.0;
   out_4619144397706641630[73] = 0.0;
   out_4619144397706641630[74] = 0.0;
   out_4619144397706641630[75] = 0.0;
   out_4619144397706641630[76] = 0.0;
   out_4619144397706641630[77] = 0.0;
   out_4619144397706641630[78] = 0.0;
   out_4619144397706641630[79] = 0.0;
   out_4619144397706641630[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_2483477866184858462) {
   out_2483477866184858462[0] = state[0];
   out_2483477866184858462[1] = state[1];
   out_2483477866184858462[2] = state[2];
   out_2483477866184858462[3] = state[3];
   out_2483477866184858462[4] = state[4];
   out_2483477866184858462[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_2483477866184858462[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_2483477866184858462[7] = state[7];
   out_2483477866184858462[8] = state[8];
}
void F_fun(double *state, double dt, double *out_264038838668788068) {
   out_264038838668788068[0] = 1;
   out_264038838668788068[1] = 0;
   out_264038838668788068[2] = 0;
   out_264038838668788068[3] = 0;
   out_264038838668788068[4] = 0;
   out_264038838668788068[5] = 0;
   out_264038838668788068[6] = 0;
   out_264038838668788068[7] = 0;
   out_264038838668788068[8] = 0;
   out_264038838668788068[9] = 0;
   out_264038838668788068[10] = 1;
   out_264038838668788068[11] = 0;
   out_264038838668788068[12] = 0;
   out_264038838668788068[13] = 0;
   out_264038838668788068[14] = 0;
   out_264038838668788068[15] = 0;
   out_264038838668788068[16] = 0;
   out_264038838668788068[17] = 0;
   out_264038838668788068[18] = 0;
   out_264038838668788068[19] = 0;
   out_264038838668788068[20] = 1;
   out_264038838668788068[21] = 0;
   out_264038838668788068[22] = 0;
   out_264038838668788068[23] = 0;
   out_264038838668788068[24] = 0;
   out_264038838668788068[25] = 0;
   out_264038838668788068[26] = 0;
   out_264038838668788068[27] = 0;
   out_264038838668788068[28] = 0;
   out_264038838668788068[29] = 0;
   out_264038838668788068[30] = 1;
   out_264038838668788068[31] = 0;
   out_264038838668788068[32] = 0;
   out_264038838668788068[33] = 0;
   out_264038838668788068[34] = 0;
   out_264038838668788068[35] = 0;
   out_264038838668788068[36] = 0;
   out_264038838668788068[37] = 0;
   out_264038838668788068[38] = 0;
   out_264038838668788068[39] = 0;
   out_264038838668788068[40] = 1;
   out_264038838668788068[41] = 0;
   out_264038838668788068[42] = 0;
   out_264038838668788068[43] = 0;
   out_264038838668788068[44] = 0;
   out_264038838668788068[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_264038838668788068[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_264038838668788068[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_264038838668788068[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_264038838668788068[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_264038838668788068[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_264038838668788068[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_264038838668788068[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_264038838668788068[53] = -9.8100000000000005*dt;
   out_264038838668788068[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_264038838668788068[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_264038838668788068[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_264038838668788068[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_264038838668788068[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_264038838668788068[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_264038838668788068[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_264038838668788068[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_264038838668788068[62] = 0;
   out_264038838668788068[63] = 0;
   out_264038838668788068[64] = 0;
   out_264038838668788068[65] = 0;
   out_264038838668788068[66] = 0;
   out_264038838668788068[67] = 0;
   out_264038838668788068[68] = 0;
   out_264038838668788068[69] = 0;
   out_264038838668788068[70] = 1;
   out_264038838668788068[71] = 0;
   out_264038838668788068[72] = 0;
   out_264038838668788068[73] = 0;
   out_264038838668788068[74] = 0;
   out_264038838668788068[75] = 0;
   out_264038838668788068[76] = 0;
   out_264038838668788068[77] = 0;
   out_264038838668788068[78] = 0;
   out_264038838668788068[79] = 0;
   out_264038838668788068[80] = 1;
}
void h_25(double *state, double *unused, double *out_8091982411933785706) {
   out_8091982411933785706[0] = state[6];
}
void H_25(double *state, double *unused, double *out_1096163747717149953) {
   out_1096163747717149953[0] = 0;
   out_1096163747717149953[1] = 0;
   out_1096163747717149953[2] = 0;
   out_1096163747717149953[3] = 0;
   out_1096163747717149953[4] = 0;
   out_1096163747717149953[5] = 0;
   out_1096163747717149953[6] = 1;
   out_1096163747717149953[7] = 0;
   out_1096163747717149953[8] = 0;
}
void h_24(double *state, double *unused, double *out_8508139400512276422) {
   out_8508139400512276422[0] = state[4];
   out_8508139400512276422[1] = state[5];
}
void H_24(double *state, double *unused, double *out_2905548330913358680) {
   out_2905548330913358680[0] = 0;
   out_2905548330913358680[1] = 0;
   out_2905548330913358680[2] = 0;
   out_2905548330913358680[3] = 0;
   out_2905548330913358680[4] = 1;
   out_2905548330913358680[5] = 0;
   out_2905548330913358680[6] = 0;
   out_2905548330913358680[7] = 0;
   out_2905548330913358680[8] = 0;
   out_2905548330913358680[9] = 0;
   out_2905548330913358680[10] = 0;
   out_2905548330913358680[11] = 0;
   out_2905548330913358680[12] = 0;
   out_2905548330913358680[13] = 0;
   out_2905548330913358680[14] = 1;
   out_2905548330913358680[15] = 0;
   out_2905548330913358680[16] = 0;
   out_2905548330913358680[17] = 0;
}
void h_30(double *state, double *unused, double *out_1124667247252753212) {
   out_1124667247252753212[0] = state[4];
}
void H_30(double *state, double *unused, double *out_5820526593774466802) {
   out_5820526593774466802[0] = 0;
   out_5820526593774466802[1] = 0;
   out_5820526593774466802[2] = 0;
   out_5820526593774466802[3] = 0;
   out_5820526593774466802[4] = 1;
   out_5820526593774466802[5] = 0;
   out_5820526593774466802[6] = 0;
   out_5820526593774466802[7] = 0;
   out_5820526593774466802[8] = 0;
}
void h_26(double *state, double *unused, double *out_3837712750428540020) {
   out_3837712750428540020[0] = state[7];
}
void H_26(double *state, double *unused, double *out_4837667066591206177) {
   out_4837667066591206177[0] = 0;
   out_4837667066591206177[1] = 0;
   out_4837667066591206177[2] = 0;
   out_4837667066591206177[3] = 0;
   out_4837667066591206177[4] = 0;
   out_4837667066591206177[5] = 0;
   out_4837667066591206177[6] = 0;
   out_4837667066591206177[7] = 1;
   out_4837667066591206177[8] = 0;
}
void h_27(double *state, double *unused, double *out_3090309144272940061) {
   out_3090309144272940061[0] = state[3];
}
void H_27(double *state, double *unused, double *out_3400266006660814934) {
   out_3400266006660814934[0] = 0;
   out_3400266006660814934[1] = 0;
   out_3400266006660814934[2] = 0;
   out_3400266006660814934[3] = 1;
   out_3400266006660814934[4] = 0;
   out_3400266006660814934[5] = 0;
   out_3400266006660814934[6] = 0;
   out_3400266006660814934[7] = 0;
   out_3400266006660814934[8] = 0;
}
void h_29(double *state, double *unused, double *out_142583153917455100) {
   out_142583153917455100[0] = state[1];
}
void H_29(double *state, double *unused, double *out_6330757938088858986) {
   out_6330757938088858986[0] = 0;
   out_6330757938088858986[1] = 1;
   out_6330757938088858986[2] = 0;
   out_6330757938088858986[3] = 0;
   out_6330757938088858986[4] = 0;
   out_6330757938088858986[5] = 0;
   out_6330757938088858986[6] = 0;
   out_6330757938088858986[7] = 0;
   out_6330757938088858986[8] = 0;
}
void h_28(double *state, double *unused, double *out_1911364123387905584) {
   out_1911364123387905584[0] = state[0];
}
void H_28(double *state, double *unused, double *out_1248358921019328412) {
   out_1248358921019328412[0] = 1;
   out_1248358921019328412[1] = 0;
   out_1248358921019328412[2] = 0;
   out_1248358921019328412[3] = 0;
   out_1248358921019328412[4] = 0;
   out_1248358921019328412[5] = 0;
   out_1248358921019328412[6] = 0;
   out_1248358921019328412[7] = 0;
   out_1248358921019328412[8] = 0;
}
void h_31(double *state, double *unused, double *out_6493078185347264258) {
   out_6493078185347264258[0] = state[8];
}
void H_31(double *state, double *unused, double *out_1065517785840189525) {
   out_1065517785840189525[0] = 0;
   out_1065517785840189525[1] = 0;
   out_1065517785840189525[2] = 0;
   out_1065517785840189525[3] = 0;
   out_1065517785840189525[4] = 0;
   out_1065517785840189525[5] = 0;
   out_1065517785840189525[6] = 0;
   out_1065517785840189525[7] = 0;
   out_1065517785840189525[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_4054919672849218704) {
  err_fun(nom_x, delta_x, out_4054919672849218704);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8915081128527086766) {
  inv_err_fun(nom_x, true_x, out_8915081128527086766);
}
void car_H_mod_fun(double *state, double *out_4619144397706641630) {
  H_mod_fun(state, out_4619144397706641630);
}
void car_f_fun(double *state, double dt, double *out_2483477866184858462) {
  f_fun(state,  dt, out_2483477866184858462);
}
void car_F_fun(double *state, double dt, double *out_264038838668788068) {
  F_fun(state,  dt, out_264038838668788068);
}
void car_h_25(double *state, double *unused, double *out_8091982411933785706) {
  h_25(state, unused, out_8091982411933785706);
}
void car_H_25(double *state, double *unused, double *out_1096163747717149953) {
  H_25(state, unused, out_1096163747717149953);
}
void car_h_24(double *state, double *unused, double *out_8508139400512276422) {
  h_24(state, unused, out_8508139400512276422);
}
void car_H_24(double *state, double *unused, double *out_2905548330913358680) {
  H_24(state, unused, out_2905548330913358680);
}
void car_h_30(double *state, double *unused, double *out_1124667247252753212) {
  h_30(state, unused, out_1124667247252753212);
}
void car_H_30(double *state, double *unused, double *out_5820526593774466802) {
  H_30(state, unused, out_5820526593774466802);
}
void car_h_26(double *state, double *unused, double *out_3837712750428540020) {
  h_26(state, unused, out_3837712750428540020);
}
void car_H_26(double *state, double *unused, double *out_4837667066591206177) {
  H_26(state, unused, out_4837667066591206177);
}
void car_h_27(double *state, double *unused, double *out_3090309144272940061) {
  h_27(state, unused, out_3090309144272940061);
}
void car_H_27(double *state, double *unused, double *out_3400266006660814934) {
  H_27(state, unused, out_3400266006660814934);
}
void car_h_29(double *state, double *unused, double *out_142583153917455100) {
  h_29(state, unused, out_142583153917455100);
}
void car_H_29(double *state, double *unused, double *out_6330757938088858986) {
  H_29(state, unused, out_6330757938088858986);
}
void car_h_28(double *state, double *unused, double *out_1911364123387905584) {
  h_28(state, unused, out_1911364123387905584);
}
void car_H_28(double *state, double *unused, double *out_1248358921019328412) {
  H_28(state, unused, out_1248358921019328412);
}
void car_h_31(double *state, double *unused, double *out_6493078185347264258) {
  h_31(state, unused, out_6493078185347264258);
}
void car_H_31(double *state, double *unused, double *out_1065517785840189525) {
  H_31(state, unused, out_1065517785840189525);
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
