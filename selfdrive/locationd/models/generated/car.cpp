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
void err_fun(double *nom_x, double *delta_x, double *out_1070978885467264368) {
   out_1070978885467264368[0] = delta_x[0] + nom_x[0];
   out_1070978885467264368[1] = delta_x[1] + nom_x[1];
   out_1070978885467264368[2] = delta_x[2] + nom_x[2];
   out_1070978885467264368[3] = delta_x[3] + nom_x[3];
   out_1070978885467264368[4] = delta_x[4] + nom_x[4];
   out_1070978885467264368[5] = delta_x[5] + nom_x[5];
   out_1070978885467264368[6] = delta_x[6] + nom_x[6];
   out_1070978885467264368[7] = delta_x[7] + nom_x[7];
   out_1070978885467264368[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7207906360374068549) {
   out_7207906360374068549[0] = -nom_x[0] + true_x[0];
   out_7207906360374068549[1] = -nom_x[1] + true_x[1];
   out_7207906360374068549[2] = -nom_x[2] + true_x[2];
   out_7207906360374068549[3] = -nom_x[3] + true_x[3];
   out_7207906360374068549[4] = -nom_x[4] + true_x[4];
   out_7207906360374068549[5] = -nom_x[5] + true_x[5];
   out_7207906360374068549[6] = -nom_x[6] + true_x[6];
   out_7207906360374068549[7] = -nom_x[7] + true_x[7];
   out_7207906360374068549[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_6799220741010781739) {
   out_6799220741010781739[0] = 1.0;
   out_6799220741010781739[1] = 0.0;
   out_6799220741010781739[2] = 0.0;
   out_6799220741010781739[3] = 0.0;
   out_6799220741010781739[4] = 0.0;
   out_6799220741010781739[5] = 0.0;
   out_6799220741010781739[6] = 0.0;
   out_6799220741010781739[7] = 0.0;
   out_6799220741010781739[8] = 0.0;
   out_6799220741010781739[9] = 0.0;
   out_6799220741010781739[10] = 1.0;
   out_6799220741010781739[11] = 0.0;
   out_6799220741010781739[12] = 0.0;
   out_6799220741010781739[13] = 0.0;
   out_6799220741010781739[14] = 0.0;
   out_6799220741010781739[15] = 0.0;
   out_6799220741010781739[16] = 0.0;
   out_6799220741010781739[17] = 0.0;
   out_6799220741010781739[18] = 0.0;
   out_6799220741010781739[19] = 0.0;
   out_6799220741010781739[20] = 1.0;
   out_6799220741010781739[21] = 0.0;
   out_6799220741010781739[22] = 0.0;
   out_6799220741010781739[23] = 0.0;
   out_6799220741010781739[24] = 0.0;
   out_6799220741010781739[25] = 0.0;
   out_6799220741010781739[26] = 0.0;
   out_6799220741010781739[27] = 0.0;
   out_6799220741010781739[28] = 0.0;
   out_6799220741010781739[29] = 0.0;
   out_6799220741010781739[30] = 1.0;
   out_6799220741010781739[31] = 0.0;
   out_6799220741010781739[32] = 0.0;
   out_6799220741010781739[33] = 0.0;
   out_6799220741010781739[34] = 0.0;
   out_6799220741010781739[35] = 0.0;
   out_6799220741010781739[36] = 0.0;
   out_6799220741010781739[37] = 0.0;
   out_6799220741010781739[38] = 0.0;
   out_6799220741010781739[39] = 0.0;
   out_6799220741010781739[40] = 1.0;
   out_6799220741010781739[41] = 0.0;
   out_6799220741010781739[42] = 0.0;
   out_6799220741010781739[43] = 0.0;
   out_6799220741010781739[44] = 0.0;
   out_6799220741010781739[45] = 0.0;
   out_6799220741010781739[46] = 0.0;
   out_6799220741010781739[47] = 0.0;
   out_6799220741010781739[48] = 0.0;
   out_6799220741010781739[49] = 0.0;
   out_6799220741010781739[50] = 1.0;
   out_6799220741010781739[51] = 0.0;
   out_6799220741010781739[52] = 0.0;
   out_6799220741010781739[53] = 0.0;
   out_6799220741010781739[54] = 0.0;
   out_6799220741010781739[55] = 0.0;
   out_6799220741010781739[56] = 0.0;
   out_6799220741010781739[57] = 0.0;
   out_6799220741010781739[58] = 0.0;
   out_6799220741010781739[59] = 0.0;
   out_6799220741010781739[60] = 1.0;
   out_6799220741010781739[61] = 0.0;
   out_6799220741010781739[62] = 0.0;
   out_6799220741010781739[63] = 0.0;
   out_6799220741010781739[64] = 0.0;
   out_6799220741010781739[65] = 0.0;
   out_6799220741010781739[66] = 0.0;
   out_6799220741010781739[67] = 0.0;
   out_6799220741010781739[68] = 0.0;
   out_6799220741010781739[69] = 0.0;
   out_6799220741010781739[70] = 1.0;
   out_6799220741010781739[71] = 0.0;
   out_6799220741010781739[72] = 0.0;
   out_6799220741010781739[73] = 0.0;
   out_6799220741010781739[74] = 0.0;
   out_6799220741010781739[75] = 0.0;
   out_6799220741010781739[76] = 0.0;
   out_6799220741010781739[77] = 0.0;
   out_6799220741010781739[78] = 0.0;
   out_6799220741010781739[79] = 0.0;
   out_6799220741010781739[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3613739950576570122) {
   out_3613739950576570122[0] = state[0];
   out_3613739950576570122[1] = state[1];
   out_3613739950576570122[2] = state[2];
   out_3613739950576570122[3] = state[3];
   out_3613739950576570122[4] = state[4];
   out_3613739950576570122[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_3613739950576570122[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3613739950576570122[7] = state[7];
   out_3613739950576570122[8] = state[8];
}
void F_fun(double *state, double dt, double *out_2385579972732080229) {
   out_2385579972732080229[0] = 1;
   out_2385579972732080229[1] = 0;
   out_2385579972732080229[2] = 0;
   out_2385579972732080229[3] = 0;
   out_2385579972732080229[4] = 0;
   out_2385579972732080229[5] = 0;
   out_2385579972732080229[6] = 0;
   out_2385579972732080229[7] = 0;
   out_2385579972732080229[8] = 0;
   out_2385579972732080229[9] = 0;
   out_2385579972732080229[10] = 1;
   out_2385579972732080229[11] = 0;
   out_2385579972732080229[12] = 0;
   out_2385579972732080229[13] = 0;
   out_2385579972732080229[14] = 0;
   out_2385579972732080229[15] = 0;
   out_2385579972732080229[16] = 0;
   out_2385579972732080229[17] = 0;
   out_2385579972732080229[18] = 0;
   out_2385579972732080229[19] = 0;
   out_2385579972732080229[20] = 1;
   out_2385579972732080229[21] = 0;
   out_2385579972732080229[22] = 0;
   out_2385579972732080229[23] = 0;
   out_2385579972732080229[24] = 0;
   out_2385579972732080229[25] = 0;
   out_2385579972732080229[26] = 0;
   out_2385579972732080229[27] = 0;
   out_2385579972732080229[28] = 0;
   out_2385579972732080229[29] = 0;
   out_2385579972732080229[30] = 1;
   out_2385579972732080229[31] = 0;
   out_2385579972732080229[32] = 0;
   out_2385579972732080229[33] = 0;
   out_2385579972732080229[34] = 0;
   out_2385579972732080229[35] = 0;
   out_2385579972732080229[36] = 0;
   out_2385579972732080229[37] = 0;
   out_2385579972732080229[38] = 0;
   out_2385579972732080229[39] = 0;
   out_2385579972732080229[40] = 1;
   out_2385579972732080229[41] = 0;
   out_2385579972732080229[42] = 0;
   out_2385579972732080229[43] = 0;
   out_2385579972732080229[44] = 0;
   out_2385579972732080229[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_2385579972732080229[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_2385579972732080229[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2385579972732080229[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2385579972732080229[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_2385579972732080229[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_2385579972732080229[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_2385579972732080229[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_2385579972732080229[53] = -9.8100000000000005*dt;
   out_2385579972732080229[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_2385579972732080229[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_2385579972732080229[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2385579972732080229[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2385579972732080229[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_2385579972732080229[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_2385579972732080229[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_2385579972732080229[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2385579972732080229[62] = 0;
   out_2385579972732080229[63] = 0;
   out_2385579972732080229[64] = 0;
   out_2385579972732080229[65] = 0;
   out_2385579972732080229[66] = 0;
   out_2385579972732080229[67] = 0;
   out_2385579972732080229[68] = 0;
   out_2385579972732080229[69] = 0;
   out_2385579972732080229[70] = 1;
   out_2385579972732080229[71] = 0;
   out_2385579972732080229[72] = 0;
   out_2385579972732080229[73] = 0;
   out_2385579972732080229[74] = 0;
   out_2385579972732080229[75] = 0;
   out_2385579972732080229[76] = 0;
   out_2385579972732080229[77] = 0;
   out_2385579972732080229[78] = 0;
   out_2385579972732080229[79] = 0;
   out_2385579972732080229[80] = 1;
}
void h_25(double *state, double *unused, double *out_7988561007480328364) {
   out_7988561007480328364[0] = state[6];
}
void H_25(double *state, double *unused, double *out_8124542682709278200) {
   out_8124542682709278200[0] = 0;
   out_8124542682709278200[1] = 0;
   out_8124542682709278200[2] = 0;
   out_8124542682709278200[3] = 0;
   out_8124542682709278200[4] = 0;
   out_8124542682709278200[5] = 0;
   out_8124542682709278200[6] = 1;
   out_8124542682709278200[7] = 0;
   out_8124542682709278200[8] = 0;
}
void h_24(double *state, double *unused, double *out_4668255431603815818) {
   out_4668255431603815818[0] = state[4];
   out_4668255431603815818[1] = state[5];
}
void H_24(double *state, double *unused, double *out_4566617083906955064) {
   out_4566617083906955064[0] = 0;
   out_4566617083906955064[1] = 0;
   out_4566617083906955064[2] = 0;
   out_4566617083906955064[3] = 0;
   out_4566617083906955064[4] = 1;
   out_4566617083906955064[5] = 0;
   out_4566617083906955064[6] = 0;
   out_4566617083906955064[7] = 0;
   out_4566617083906955064[8] = 0;
   out_4566617083906955064[9] = 0;
   out_4566617083906955064[10] = 0;
   out_4566617083906955064[11] = 0;
   out_4566617083906955064[12] = 0;
   out_4566617083906955064[13] = 0;
   out_4566617083906955064[14] = 1;
   out_4566617083906955064[15] = 0;
   out_4566617083906955064[16] = 0;
   out_4566617083906955064[17] = 0;
}
void h_30(double *state, double *unused, double *out_8263755069764834253) {
   out_8263755069764834253[0] = state[4];
}
void H_30(double *state, double *unused, double *out_5606209724202029573) {
   out_5606209724202029573[0] = 0;
   out_5606209724202029573[1] = 0;
   out_5606209724202029573[2] = 0;
   out_5606209724202029573[3] = 0;
   out_5606209724202029573[4] = 1;
   out_5606209724202029573[5] = 0;
   out_5606209724202029573[6] = 0;
   out_5606209724202029573[7] = 0;
   out_5606209724202029573[8] = 0;
}
void h_26(double *state, double *unused, double *out_7578583683136019712) {
   out_7578583683136019712[0] = state[7];
}
void H_26(double *state, double *unused, double *out_6580698072126217192) {
   out_6580698072126217192[0] = 0;
   out_6580698072126217192[1] = 0;
   out_6580698072126217192[2] = 0;
   out_6580698072126217192[3] = 0;
   out_6580698072126217192[4] = 0;
   out_6580698072126217192[5] = 0;
   out_6580698072126217192[6] = 0;
   out_6580698072126217192[7] = 1;
   out_6580698072126217192[8] = 0;
}
void h_27(double *state, double *unused, double *out_4355663630496028862) {
   out_4355663630496028862[0] = state[3];
}
void H_27(double *state, double *unused, double *out_3382615653018086356) {
   out_3382615653018086356[0] = 0;
   out_3382615653018086356[1] = 0;
   out_3382615653018086356[2] = 0;
   out_3382615653018086356[3] = 1;
   out_3382615653018086356[4] = 0;
   out_3382615653018086356[5] = 0;
   out_3382615653018086356[6] = 0;
   out_3382615653018086356[7] = 0;
   out_3382615653018086356[8] = 0;
}
void h_29(double *state, double *unused, double *out_4540259132863760528) {
   out_4540259132863760528[0] = state[1];
}
void H_29(double *state, double *unused, double *out_5095978379887637389) {
   out_5095978379887637389[0] = 0;
   out_5095978379887637389[1] = 1;
   out_5095978379887637389[2] = 0;
   out_5095978379887637389[3] = 0;
   out_5095978379887637389[4] = 0;
   out_5095978379887637389[5] = 0;
   out_5095978379887637389[6] = 0;
   out_5095978379887637389[7] = 0;
   out_5095978379887637389[8] = 0;
}
void h_28(double *state, double *unused, double *out_646009637164816783) {
   out_646009637164816783[0] = state[0];
}
void H_28(double *state, double *unused, double *out_8268366676752383653) {
   out_8268366676752383653[0] = 1;
   out_8268366676752383653[1] = 0;
   out_8268366676752383653[2] = 0;
   out_8268366676752383653[3] = 0;
   out_8268366676752383653[4] = 0;
   out_8268366676752383653[5] = 0;
   out_8268366676752383653[6] = 0;
   out_8268366676752383653[7] = 0;
   out_8268366676752383653[8] = 0;
}
void h_31(double *state, double *unused, double *out_1320465781545372070) {
   out_1320465781545372070[0] = state[8];
}
void H_31(double *state, double *unused, double *out_8093896720832317772) {
   out_8093896720832317772[0] = 0;
   out_8093896720832317772[1] = 0;
   out_8093896720832317772[2] = 0;
   out_8093896720832317772[3] = 0;
   out_8093896720832317772[4] = 0;
   out_8093896720832317772[5] = 0;
   out_8093896720832317772[6] = 0;
   out_8093896720832317772[7] = 0;
   out_8093896720832317772[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_1070978885467264368) {
  err_fun(nom_x, delta_x, out_1070978885467264368);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7207906360374068549) {
  inv_err_fun(nom_x, true_x, out_7207906360374068549);
}
void car_H_mod_fun(double *state, double *out_6799220741010781739) {
  H_mod_fun(state, out_6799220741010781739);
}
void car_f_fun(double *state, double dt, double *out_3613739950576570122) {
  f_fun(state,  dt, out_3613739950576570122);
}
void car_F_fun(double *state, double dt, double *out_2385579972732080229) {
  F_fun(state,  dt, out_2385579972732080229);
}
void car_h_25(double *state, double *unused, double *out_7988561007480328364) {
  h_25(state, unused, out_7988561007480328364);
}
void car_H_25(double *state, double *unused, double *out_8124542682709278200) {
  H_25(state, unused, out_8124542682709278200);
}
void car_h_24(double *state, double *unused, double *out_4668255431603815818) {
  h_24(state, unused, out_4668255431603815818);
}
void car_H_24(double *state, double *unused, double *out_4566617083906955064) {
  H_24(state, unused, out_4566617083906955064);
}
void car_h_30(double *state, double *unused, double *out_8263755069764834253) {
  h_30(state, unused, out_8263755069764834253);
}
void car_H_30(double *state, double *unused, double *out_5606209724202029573) {
  H_30(state, unused, out_5606209724202029573);
}
void car_h_26(double *state, double *unused, double *out_7578583683136019712) {
  h_26(state, unused, out_7578583683136019712);
}
void car_H_26(double *state, double *unused, double *out_6580698072126217192) {
  H_26(state, unused, out_6580698072126217192);
}
void car_h_27(double *state, double *unused, double *out_4355663630496028862) {
  h_27(state, unused, out_4355663630496028862);
}
void car_H_27(double *state, double *unused, double *out_3382615653018086356) {
  H_27(state, unused, out_3382615653018086356);
}
void car_h_29(double *state, double *unused, double *out_4540259132863760528) {
  h_29(state, unused, out_4540259132863760528);
}
void car_H_29(double *state, double *unused, double *out_5095978379887637389) {
  H_29(state, unused, out_5095978379887637389);
}
void car_h_28(double *state, double *unused, double *out_646009637164816783) {
  h_28(state, unused, out_646009637164816783);
}
void car_H_28(double *state, double *unused, double *out_8268366676752383653) {
  H_28(state, unused, out_8268366676752383653);
}
void car_h_31(double *state, double *unused, double *out_1320465781545372070) {
  h_31(state, unused, out_1320465781545372070);
}
void car_H_31(double *state, double *unused, double *out_8093896720832317772) {
  H_31(state, unused, out_8093896720832317772);
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
