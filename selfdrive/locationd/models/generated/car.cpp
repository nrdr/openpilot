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
void err_fun(double *nom_x, double *delta_x, double *out_8137803062968279058) {
   out_8137803062968279058[0] = delta_x[0] + nom_x[0];
   out_8137803062968279058[1] = delta_x[1] + nom_x[1];
   out_8137803062968279058[2] = delta_x[2] + nom_x[2];
   out_8137803062968279058[3] = delta_x[3] + nom_x[3];
   out_8137803062968279058[4] = delta_x[4] + nom_x[4];
   out_8137803062968279058[5] = delta_x[5] + nom_x[5];
   out_8137803062968279058[6] = delta_x[6] + nom_x[6];
   out_8137803062968279058[7] = delta_x[7] + nom_x[7];
   out_8137803062968279058[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4803320297930984943) {
   out_4803320297930984943[0] = -nom_x[0] + true_x[0];
   out_4803320297930984943[1] = -nom_x[1] + true_x[1];
   out_4803320297930984943[2] = -nom_x[2] + true_x[2];
   out_4803320297930984943[3] = -nom_x[3] + true_x[3];
   out_4803320297930984943[4] = -nom_x[4] + true_x[4];
   out_4803320297930984943[5] = -nom_x[5] + true_x[5];
   out_4803320297930984943[6] = -nom_x[6] + true_x[6];
   out_4803320297930984943[7] = -nom_x[7] + true_x[7];
   out_4803320297930984943[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_250780943344312618) {
   out_250780943344312618[0] = 1.0;
   out_250780943344312618[1] = 0.0;
   out_250780943344312618[2] = 0.0;
   out_250780943344312618[3] = 0.0;
   out_250780943344312618[4] = 0.0;
   out_250780943344312618[5] = 0.0;
   out_250780943344312618[6] = 0.0;
   out_250780943344312618[7] = 0.0;
   out_250780943344312618[8] = 0.0;
   out_250780943344312618[9] = 0.0;
   out_250780943344312618[10] = 1.0;
   out_250780943344312618[11] = 0.0;
   out_250780943344312618[12] = 0.0;
   out_250780943344312618[13] = 0.0;
   out_250780943344312618[14] = 0.0;
   out_250780943344312618[15] = 0.0;
   out_250780943344312618[16] = 0.0;
   out_250780943344312618[17] = 0.0;
   out_250780943344312618[18] = 0.0;
   out_250780943344312618[19] = 0.0;
   out_250780943344312618[20] = 1.0;
   out_250780943344312618[21] = 0.0;
   out_250780943344312618[22] = 0.0;
   out_250780943344312618[23] = 0.0;
   out_250780943344312618[24] = 0.0;
   out_250780943344312618[25] = 0.0;
   out_250780943344312618[26] = 0.0;
   out_250780943344312618[27] = 0.0;
   out_250780943344312618[28] = 0.0;
   out_250780943344312618[29] = 0.0;
   out_250780943344312618[30] = 1.0;
   out_250780943344312618[31] = 0.0;
   out_250780943344312618[32] = 0.0;
   out_250780943344312618[33] = 0.0;
   out_250780943344312618[34] = 0.0;
   out_250780943344312618[35] = 0.0;
   out_250780943344312618[36] = 0.0;
   out_250780943344312618[37] = 0.0;
   out_250780943344312618[38] = 0.0;
   out_250780943344312618[39] = 0.0;
   out_250780943344312618[40] = 1.0;
   out_250780943344312618[41] = 0.0;
   out_250780943344312618[42] = 0.0;
   out_250780943344312618[43] = 0.0;
   out_250780943344312618[44] = 0.0;
   out_250780943344312618[45] = 0.0;
   out_250780943344312618[46] = 0.0;
   out_250780943344312618[47] = 0.0;
   out_250780943344312618[48] = 0.0;
   out_250780943344312618[49] = 0.0;
   out_250780943344312618[50] = 1.0;
   out_250780943344312618[51] = 0.0;
   out_250780943344312618[52] = 0.0;
   out_250780943344312618[53] = 0.0;
   out_250780943344312618[54] = 0.0;
   out_250780943344312618[55] = 0.0;
   out_250780943344312618[56] = 0.0;
   out_250780943344312618[57] = 0.0;
   out_250780943344312618[58] = 0.0;
   out_250780943344312618[59] = 0.0;
   out_250780943344312618[60] = 1.0;
   out_250780943344312618[61] = 0.0;
   out_250780943344312618[62] = 0.0;
   out_250780943344312618[63] = 0.0;
   out_250780943344312618[64] = 0.0;
   out_250780943344312618[65] = 0.0;
   out_250780943344312618[66] = 0.0;
   out_250780943344312618[67] = 0.0;
   out_250780943344312618[68] = 0.0;
   out_250780943344312618[69] = 0.0;
   out_250780943344312618[70] = 1.0;
   out_250780943344312618[71] = 0.0;
   out_250780943344312618[72] = 0.0;
   out_250780943344312618[73] = 0.0;
   out_250780943344312618[74] = 0.0;
   out_250780943344312618[75] = 0.0;
   out_250780943344312618[76] = 0.0;
   out_250780943344312618[77] = 0.0;
   out_250780943344312618[78] = 0.0;
   out_250780943344312618[79] = 0.0;
   out_250780943344312618[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_5023554550498675071) {
   out_5023554550498675071[0] = state[0];
   out_5023554550498675071[1] = state[1];
   out_5023554550498675071[2] = state[2];
   out_5023554550498675071[3] = state[3];
   out_5023554550498675071[4] = state[4];
   out_5023554550498675071[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_5023554550498675071[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_5023554550498675071[7] = state[7];
   out_5023554550498675071[8] = state[8];
}
void F_fun(double *state, double dt, double *out_3517018389212170475) {
   out_3517018389212170475[0] = 1;
   out_3517018389212170475[1] = 0;
   out_3517018389212170475[2] = 0;
   out_3517018389212170475[3] = 0;
   out_3517018389212170475[4] = 0;
   out_3517018389212170475[5] = 0;
   out_3517018389212170475[6] = 0;
   out_3517018389212170475[7] = 0;
   out_3517018389212170475[8] = 0;
   out_3517018389212170475[9] = 0;
   out_3517018389212170475[10] = 1;
   out_3517018389212170475[11] = 0;
   out_3517018389212170475[12] = 0;
   out_3517018389212170475[13] = 0;
   out_3517018389212170475[14] = 0;
   out_3517018389212170475[15] = 0;
   out_3517018389212170475[16] = 0;
   out_3517018389212170475[17] = 0;
   out_3517018389212170475[18] = 0;
   out_3517018389212170475[19] = 0;
   out_3517018389212170475[20] = 1;
   out_3517018389212170475[21] = 0;
   out_3517018389212170475[22] = 0;
   out_3517018389212170475[23] = 0;
   out_3517018389212170475[24] = 0;
   out_3517018389212170475[25] = 0;
   out_3517018389212170475[26] = 0;
   out_3517018389212170475[27] = 0;
   out_3517018389212170475[28] = 0;
   out_3517018389212170475[29] = 0;
   out_3517018389212170475[30] = 1;
   out_3517018389212170475[31] = 0;
   out_3517018389212170475[32] = 0;
   out_3517018389212170475[33] = 0;
   out_3517018389212170475[34] = 0;
   out_3517018389212170475[35] = 0;
   out_3517018389212170475[36] = 0;
   out_3517018389212170475[37] = 0;
   out_3517018389212170475[38] = 0;
   out_3517018389212170475[39] = 0;
   out_3517018389212170475[40] = 1;
   out_3517018389212170475[41] = 0;
   out_3517018389212170475[42] = 0;
   out_3517018389212170475[43] = 0;
   out_3517018389212170475[44] = 0;
   out_3517018389212170475[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_3517018389212170475[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_3517018389212170475[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3517018389212170475[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3517018389212170475[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_3517018389212170475[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_3517018389212170475[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_3517018389212170475[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_3517018389212170475[53] = -9.8100000000000005*dt;
   out_3517018389212170475[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_3517018389212170475[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_3517018389212170475[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3517018389212170475[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3517018389212170475[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_3517018389212170475[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_3517018389212170475[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_3517018389212170475[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3517018389212170475[62] = 0;
   out_3517018389212170475[63] = 0;
   out_3517018389212170475[64] = 0;
   out_3517018389212170475[65] = 0;
   out_3517018389212170475[66] = 0;
   out_3517018389212170475[67] = 0;
   out_3517018389212170475[68] = 0;
   out_3517018389212170475[69] = 0;
   out_3517018389212170475[70] = 1;
   out_3517018389212170475[71] = 0;
   out_3517018389212170475[72] = 0;
   out_3517018389212170475[73] = 0;
   out_3517018389212170475[74] = 0;
   out_3517018389212170475[75] = 0;
   out_3517018389212170475[76] = 0;
   out_3517018389212170475[77] = 0;
   out_3517018389212170475[78] = 0;
   out_3517018389212170475[79] = 0;
   out_3517018389212170475[80] = 1;
}
void h_25(double *state, double *unused, double *out_8788151648350399353) {
   out_8788151648350399353[0] = state[6];
}
void H_25(double *state, double *unused, double *out_3773761593333804295) {
   out_3773761593333804295[0] = 0;
   out_3773761593333804295[1] = 0;
   out_3773761593333804295[2] = 0;
   out_3773761593333804295[3] = 0;
   out_3773761593333804295[4] = 0;
   out_3773761593333804295[5] = 0;
   out_3773761593333804295[6] = 1;
   out_3773761593333804295[7] = 0;
   out_3773761593333804295[8] = 0;
}
void h_24(double *state, double *unused, double *out_4617115616065835450) {
   out_4617115616065835450[0] = state[4];
   out_4617115616065835450[1] = state[5];
}
void H_24(double *state, double *unused, double *out_5950976016940954268) {
   out_5950976016940954268[0] = 0;
   out_5950976016940954268[1] = 0;
   out_5950976016940954268[2] = 0;
   out_5950976016940954268[3] = 0;
   out_5950976016940954268[4] = 1;
   out_5950976016940954268[5] = 0;
   out_5950976016940954268[6] = 0;
   out_5950976016940954268[7] = 0;
   out_5950976016940954268[8] = 0;
   out_5950976016940954268[9] = 0;
   out_5950976016940954268[10] = 0;
   out_5950976016940954268[11] = 0;
   out_5950976016940954268[12] = 0;
   out_5950976016940954268[13] = 0;
   out_5950976016940954268[14] = 1;
   out_5950976016940954268[15] = 0;
   out_5950976016940954268[16] = 0;
   out_5950976016940954268[17] = 0;
}
void h_30(double *state, double *unused, double *out_3908301040633649848) {
   out_3908301040633649848[0] = state[4];
}
void H_30(double *state, double *unused, double *out_6292094551841052922) {
   out_6292094551841052922[0] = 0;
   out_6292094551841052922[1] = 0;
   out_6292094551841052922[2] = 0;
   out_6292094551841052922[3] = 0;
   out_6292094551841052922[4] = 1;
   out_6292094551841052922[5] = 0;
   out_6292094551841052922[6] = 0;
   out_6292094551841052922[7] = 0;
   out_6292094551841052922[8] = 0;
}
void h_26(double *state, double *unused, double *out_8870681038314943080) {
   out_8870681038314943080[0] = state[7];
}
void H_26(double *state, double *unused, double *out_32258274459748071) {
   out_32258274459748071[0] = 0;
   out_32258274459748071[1] = 0;
   out_32258274459748071[2] = 0;
   out_32258274459748071[3] = 0;
   out_32258274459748071[4] = 0;
   out_32258274459748071[5] = 0;
   out_32258274459748071[6] = 0;
   out_32258274459748071[7] = 1;
   out_32258274459748071[8] = 0;
}
void h_27(double *state, double *unused, double *out_8988688432248319824) {
   out_8988688432248319824[0] = state[3];
}
void H_27(double *state, double *unused, double *out_1469659334390139314) {
   out_1469659334390139314[0] = 0;
   out_1469659334390139314[1] = 0;
   out_1469659334390139314[2] = 0;
   out_1469659334390139314[3] = 1;
   out_1469659334390139314[4] = 0;
   out_1469659334390139314[5] = 0;
   out_1469659334390139314[6] = 0;
   out_1469659334390139314[7] = 0;
   out_1469659334390139314[8] = 0;
}
void h_29(double *state, double *unused, double *out_149028852435531358) {
   out_149028852435531358[0] = state[1];
}
void H_29(double *state, double *unused, double *out_243703392479411719) {
   out_243703392479411719[0] = 0;
   out_243703392479411719[1] = 1;
   out_243703392479411719[2] = 0;
   out_243703392479411719[3] = 0;
   out_243703392479411719[4] = 0;
   out_243703392479411719[5] = 0;
   out_243703392479411719[6] = 0;
   out_243703392479411719[7] = 0;
   out_243703392479411719[8] = 0;
}
void h_28(double *state, double *unused, double *out_4456382373800386147) {
   out_4456382373800386147[0] = state[0];
}
void H_28(double *state, double *unused, double *out_1719926879085914532) {
   out_1719926879085914532[0] = 1;
   out_1719926879085914532[1] = 0;
   out_1719926879085914532[2] = 0;
   out_1719926879085914532[3] = 0;
   out_1719926879085914532[4] = 0;
   out_1719926879085914532[5] = 0;
   out_1719926879085914532[6] = 0;
   out_1719926879085914532[7] = 0;
   out_1719926879085914532[8] = 0;
}
void h_31(double *state, double *unused, double *out_7610421138374421687) {
   out_7610421138374421687[0] = state[8];
}
void H_31(double *state, double *unused, double *out_3804407555210764723) {
   out_3804407555210764723[0] = 0;
   out_3804407555210764723[1] = 0;
   out_3804407555210764723[2] = 0;
   out_3804407555210764723[3] = 0;
   out_3804407555210764723[4] = 0;
   out_3804407555210764723[5] = 0;
   out_3804407555210764723[6] = 0;
   out_3804407555210764723[7] = 0;
   out_3804407555210764723[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_8137803062968279058) {
  err_fun(nom_x, delta_x, out_8137803062968279058);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4803320297930984943) {
  inv_err_fun(nom_x, true_x, out_4803320297930984943);
}
void car_H_mod_fun(double *state, double *out_250780943344312618) {
  H_mod_fun(state, out_250780943344312618);
}
void car_f_fun(double *state, double dt, double *out_5023554550498675071) {
  f_fun(state,  dt, out_5023554550498675071);
}
void car_F_fun(double *state, double dt, double *out_3517018389212170475) {
  F_fun(state,  dt, out_3517018389212170475);
}
void car_h_25(double *state, double *unused, double *out_8788151648350399353) {
  h_25(state, unused, out_8788151648350399353);
}
void car_H_25(double *state, double *unused, double *out_3773761593333804295) {
  H_25(state, unused, out_3773761593333804295);
}
void car_h_24(double *state, double *unused, double *out_4617115616065835450) {
  h_24(state, unused, out_4617115616065835450);
}
void car_H_24(double *state, double *unused, double *out_5950976016940954268) {
  H_24(state, unused, out_5950976016940954268);
}
void car_h_30(double *state, double *unused, double *out_3908301040633649848) {
  h_30(state, unused, out_3908301040633649848);
}
void car_H_30(double *state, double *unused, double *out_6292094551841052922) {
  H_30(state, unused, out_6292094551841052922);
}
void car_h_26(double *state, double *unused, double *out_8870681038314943080) {
  h_26(state, unused, out_8870681038314943080);
}
void car_H_26(double *state, double *unused, double *out_32258274459748071) {
  H_26(state, unused, out_32258274459748071);
}
void car_h_27(double *state, double *unused, double *out_8988688432248319824) {
  h_27(state, unused, out_8988688432248319824);
}
void car_H_27(double *state, double *unused, double *out_1469659334390139314) {
  H_27(state, unused, out_1469659334390139314);
}
void car_h_29(double *state, double *unused, double *out_149028852435531358) {
  h_29(state, unused, out_149028852435531358);
}
void car_H_29(double *state, double *unused, double *out_243703392479411719) {
  H_29(state, unused, out_243703392479411719);
}
void car_h_28(double *state, double *unused, double *out_4456382373800386147) {
  h_28(state, unused, out_4456382373800386147);
}
void car_H_28(double *state, double *unused, double *out_1719926879085914532) {
  H_28(state, unused, out_1719926879085914532);
}
void car_h_31(double *state, double *unused, double *out_7610421138374421687) {
  h_31(state, unused, out_7610421138374421687);
}
void car_H_31(double *state, double *unused, double *out_3804407555210764723) {
  H_31(state, unused, out_3804407555210764723);
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
