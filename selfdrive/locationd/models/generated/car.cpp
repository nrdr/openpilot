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
void err_fun(double *nom_x, double *delta_x, double *out_4362699660511635051) {
   out_4362699660511635051[0] = delta_x[0] + nom_x[0];
   out_4362699660511635051[1] = delta_x[1] + nom_x[1];
   out_4362699660511635051[2] = delta_x[2] + nom_x[2];
   out_4362699660511635051[3] = delta_x[3] + nom_x[3];
   out_4362699660511635051[4] = delta_x[4] + nom_x[4];
   out_4362699660511635051[5] = delta_x[5] + nom_x[5];
   out_4362699660511635051[6] = delta_x[6] + nom_x[6];
   out_4362699660511635051[7] = delta_x[7] + nom_x[7];
   out_4362699660511635051[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5242751605747536921) {
   out_5242751605747536921[0] = -nom_x[0] + true_x[0];
   out_5242751605747536921[1] = -nom_x[1] + true_x[1];
   out_5242751605747536921[2] = -nom_x[2] + true_x[2];
   out_5242751605747536921[3] = -nom_x[3] + true_x[3];
   out_5242751605747536921[4] = -nom_x[4] + true_x[4];
   out_5242751605747536921[5] = -nom_x[5] + true_x[5];
   out_5242751605747536921[6] = -nom_x[6] + true_x[6];
   out_5242751605747536921[7] = -nom_x[7] + true_x[7];
   out_5242751605747536921[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_4674979810803532886) {
   out_4674979810803532886[0] = 1.0;
   out_4674979810803532886[1] = 0.0;
   out_4674979810803532886[2] = 0.0;
   out_4674979810803532886[3] = 0.0;
   out_4674979810803532886[4] = 0.0;
   out_4674979810803532886[5] = 0.0;
   out_4674979810803532886[6] = 0.0;
   out_4674979810803532886[7] = 0.0;
   out_4674979810803532886[8] = 0.0;
   out_4674979810803532886[9] = 0.0;
   out_4674979810803532886[10] = 1.0;
   out_4674979810803532886[11] = 0.0;
   out_4674979810803532886[12] = 0.0;
   out_4674979810803532886[13] = 0.0;
   out_4674979810803532886[14] = 0.0;
   out_4674979810803532886[15] = 0.0;
   out_4674979810803532886[16] = 0.0;
   out_4674979810803532886[17] = 0.0;
   out_4674979810803532886[18] = 0.0;
   out_4674979810803532886[19] = 0.0;
   out_4674979810803532886[20] = 1.0;
   out_4674979810803532886[21] = 0.0;
   out_4674979810803532886[22] = 0.0;
   out_4674979810803532886[23] = 0.0;
   out_4674979810803532886[24] = 0.0;
   out_4674979810803532886[25] = 0.0;
   out_4674979810803532886[26] = 0.0;
   out_4674979810803532886[27] = 0.0;
   out_4674979810803532886[28] = 0.0;
   out_4674979810803532886[29] = 0.0;
   out_4674979810803532886[30] = 1.0;
   out_4674979810803532886[31] = 0.0;
   out_4674979810803532886[32] = 0.0;
   out_4674979810803532886[33] = 0.0;
   out_4674979810803532886[34] = 0.0;
   out_4674979810803532886[35] = 0.0;
   out_4674979810803532886[36] = 0.0;
   out_4674979810803532886[37] = 0.0;
   out_4674979810803532886[38] = 0.0;
   out_4674979810803532886[39] = 0.0;
   out_4674979810803532886[40] = 1.0;
   out_4674979810803532886[41] = 0.0;
   out_4674979810803532886[42] = 0.0;
   out_4674979810803532886[43] = 0.0;
   out_4674979810803532886[44] = 0.0;
   out_4674979810803532886[45] = 0.0;
   out_4674979810803532886[46] = 0.0;
   out_4674979810803532886[47] = 0.0;
   out_4674979810803532886[48] = 0.0;
   out_4674979810803532886[49] = 0.0;
   out_4674979810803532886[50] = 1.0;
   out_4674979810803532886[51] = 0.0;
   out_4674979810803532886[52] = 0.0;
   out_4674979810803532886[53] = 0.0;
   out_4674979810803532886[54] = 0.0;
   out_4674979810803532886[55] = 0.0;
   out_4674979810803532886[56] = 0.0;
   out_4674979810803532886[57] = 0.0;
   out_4674979810803532886[58] = 0.0;
   out_4674979810803532886[59] = 0.0;
   out_4674979810803532886[60] = 1.0;
   out_4674979810803532886[61] = 0.0;
   out_4674979810803532886[62] = 0.0;
   out_4674979810803532886[63] = 0.0;
   out_4674979810803532886[64] = 0.0;
   out_4674979810803532886[65] = 0.0;
   out_4674979810803532886[66] = 0.0;
   out_4674979810803532886[67] = 0.0;
   out_4674979810803532886[68] = 0.0;
   out_4674979810803532886[69] = 0.0;
   out_4674979810803532886[70] = 1.0;
   out_4674979810803532886[71] = 0.0;
   out_4674979810803532886[72] = 0.0;
   out_4674979810803532886[73] = 0.0;
   out_4674979810803532886[74] = 0.0;
   out_4674979810803532886[75] = 0.0;
   out_4674979810803532886[76] = 0.0;
   out_4674979810803532886[77] = 0.0;
   out_4674979810803532886[78] = 0.0;
   out_4674979810803532886[79] = 0.0;
   out_4674979810803532886[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3154690792987273928) {
   out_3154690792987273928[0] = state[0];
   out_3154690792987273928[1] = state[1];
   out_3154690792987273928[2] = state[2];
   out_3154690792987273928[3] = state[3];
   out_3154690792987273928[4] = state[4];
   out_3154690792987273928[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_3154690792987273928[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3154690792987273928[7] = state[7];
   out_3154690792987273928[8] = state[8];
}
void F_fun(double *state, double dt, double *out_3170479804547101621) {
   out_3170479804547101621[0] = 1;
   out_3170479804547101621[1] = 0;
   out_3170479804547101621[2] = 0;
   out_3170479804547101621[3] = 0;
   out_3170479804547101621[4] = 0;
   out_3170479804547101621[5] = 0;
   out_3170479804547101621[6] = 0;
   out_3170479804547101621[7] = 0;
   out_3170479804547101621[8] = 0;
   out_3170479804547101621[9] = 0;
   out_3170479804547101621[10] = 1;
   out_3170479804547101621[11] = 0;
   out_3170479804547101621[12] = 0;
   out_3170479804547101621[13] = 0;
   out_3170479804547101621[14] = 0;
   out_3170479804547101621[15] = 0;
   out_3170479804547101621[16] = 0;
   out_3170479804547101621[17] = 0;
   out_3170479804547101621[18] = 0;
   out_3170479804547101621[19] = 0;
   out_3170479804547101621[20] = 1;
   out_3170479804547101621[21] = 0;
   out_3170479804547101621[22] = 0;
   out_3170479804547101621[23] = 0;
   out_3170479804547101621[24] = 0;
   out_3170479804547101621[25] = 0;
   out_3170479804547101621[26] = 0;
   out_3170479804547101621[27] = 0;
   out_3170479804547101621[28] = 0;
   out_3170479804547101621[29] = 0;
   out_3170479804547101621[30] = 1;
   out_3170479804547101621[31] = 0;
   out_3170479804547101621[32] = 0;
   out_3170479804547101621[33] = 0;
   out_3170479804547101621[34] = 0;
   out_3170479804547101621[35] = 0;
   out_3170479804547101621[36] = 0;
   out_3170479804547101621[37] = 0;
   out_3170479804547101621[38] = 0;
   out_3170479804547101621[39] = 0;
   out_3170479804547101621[40] = 1;
   out_3170479804547101621[41] = 0;
   out_3170479804547101621[42] = 0;
   out_3170479804547101621[43] = 0;
   out_3170479804547101621[44] = 0;
   out_3170479804547101621[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_3170479804547101621[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_3170479804547101621[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3170479804547101621[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3170479804547101621[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_3170479804547101621[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_3170479804547101621[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_3170479804547101621[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_3170479804547101621[53] = -9.8100000000000005*dt;
   out_3170479804547101621[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_3170479804547101621[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_3170479804547101621[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3170479804547101621[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3170479804547101621[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_3170479804547101621[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_3170479804547101621[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_3170479804547101621[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3170479804547101621[62] = 0;
   out_3170479804547101621[63] = 0;
   out_3170479804547101621[64] = 0;
   out_3170479804547101621[65] = 0;
   out_3170479804547101621[66] = 0;
   out_3170479804547101621[67] = 0;
   out_3170479804547101621[68] = 0;
   out_3170479804547101621[69] = 0;
   out_3170479804547101621[70] = 1;
   out_3170479804547101621[71] = 0;
   out_3170479804547101621[72] = 0;
   out_3170479804547101621[73] = 0;
   out_3170479804547101621[74] = 0;
   out_3170479804547101621[75] = 0;
   out_3170479804547101621[76] = 0;
   out_3170479804547101621[77] = 0;
   out_3170479804547101621[78] = 0;
   out_3170479804547101621[79] = 0;
   out_3170479804547101621[80] = 1;
}
void h_25(double *state, double *unused, double *out_2611331197064061038) {
   out_2611331197064061038[0] = state[6];
}
void H_25(double *state, double *unused, double *out_8976933419978149621) {
   out_8976933419978149621[0] = 0;
   out_8976933419978149621[1] = 0;
   out_8976933419978149621[2] = 0;
   out_8976933419978149621[3] = 0;
   out_8976933419978149621[4] = 0;
   out_8976933419978149621[5] = 0;
   out_8976933419978149621[6] = 1;
   out_8976933419978149621[7] = 0;
   out_8976933419978149621[8] = 0;
}
void h_24(double *state, double *unused, double *out_3910887785984043827) {
   out_3910887785984043827[0] = state[4];
   out_3910887785984043827[1] = state[5];
}
void H_24(double *state, double *unused, double *out_167933289972727541) {
   out_167933289972727541[0] = 0;
   out_167933289972727541[1] = 0;
   out_167933289972727541[2] = 0;
   out_167933289972727541[3] = 0;
   out_167933289972727541[4] = 1;
   out_167933289972727541[5] = 0;
   out_167933289972727541[6] = 0;
   out_167933289972727541[7] = 0;
   out_167933289972727541[8] = 0;
   out_167933289972727541[9] = 0;
   out_167933289972727541[10] = 0;
   out_167933289972727541[11] = 0;
   out_167933289972727541[12] = 0;
   out_167933289972727541[13] = 0;
   out_167933289972727541[14] = 1;
   out_167933289972727541[15] = 0;
   out_167933289972727541[16] = 0;
   out_167933289972727541[17] = 0;
}
void h_30(double *state, double *unused, double *out_9199159123540356201) {
   out_9199159123540356201[0] = state[4];
}
void H_30(double *state, double *unused, double *out_6951477695224153368) {
   out_6951477695224153368[0] = 0;
   out_6951477695224153368[1] = 0;
   out_6951477695224153368[2] = 0;
   out_6951477695224153368[3] = 0;
   out_6951477695224153368[4] = 1;
   out_6951477695224153368[5] = 0;
   out_6951477695224153368[6] = 0;
   out_6951477695224153368[7] = 0;
   out_6951477695224153368[8] = 0;
}
void h_26(double *state, double *unused, double *out_8304075097267532980) {
   out_8304075097267532980[0] = state[7];
}
void H_26(double *state, double *unused, double *out_5235430101104093397) {
   out_5235430101104093397[0] = 0;
   out_5235430101104093397[1] = 0;
   out_5235430101104093397[2] = 0;
   out_5235430101104093397[3] = 0;
   out_5235430101104093397[4] = 0;
   out_5235430101104093397[5] = 0;
   out_5235430101104093397[6] = 0;
   out_5235430101104093397[7] = 1;
   out_5235430101104093397[8] = 0;
}
void h_27(double *state, double *unused, double *out_3214647081740538555) {
   out_3214647081740538555[0] = state[3];
}
void H_27(double *state, double *unused, double *out_2274473778050116512) {
   out_2274473778050116512[0] = 0;
   out_2274473778050116512[1] = 0;
   out_2274473778050116512[2] = 0;
   out_2274473778050116512[3] = 1;
   out_2274473778050116512[4] = 0;
   out_2274473778050116512[5] = 0;
   out_2274473778050116512[6] = 0;
   out_2274473778050116512[7] = 0;
   out_2274473778050116512[8] = 0;
}
void h_29(double *state, double *unused, double *out_4245911682508349770) {
   out_4245911682508349770[0] = state[1];
}
void H_29(double *state, double *unused, double *out_4959468434164933607) {
   out_4959468434164933607[0] = 0;
   out_4959468434164933607[1] = 1;
   out_4959468434164933607[2] = 0;
   out_4959468434164933607[3] = 0;
   out_4959468434164933607[4] = 0;
   out_4959468434164933607[5] = 0;
   out_4959468434164933607[6] = 0;
   out_4959468434164933607[7] = 0;
   out_4959468434164933607[8] = 0;
}
void h_28(double *state, double *unused, double *out_834475709106320206) {
   out_834475709106320206[0] = state[0];
}
void H_28(double *state, double *unused, double *out_6923098705730259858) {
   out_6923098705730259858[0] = 1;
   out_6923098705730259858[1] = 0;
   out_6923098705730259858[2] = 0;
   out_6923098705730259858[3] = 0;
   out_6923098705730259858[4] = 0;
   out_6923098705730259858[5] = 0;
   out_6923098705730259858[6] = 0;
   out_6923098705730259858[7] = 0;
   out_6923098705730259858[8] = 0;
}
void h_31(double *state, double *unused, double *out_2768517865415190183) {
   out_2768517865415190183[0] = state[8];
}
void H_31(double *state, double *unused, double *out_4609221998870741921) {
   out_4609221998870741921[0] = 0;
   out_4609221998870741921[1] = 0;
   out_4609221998870741921[2] = 0;
   out_4609221998870741921[3] = 0;
   out_4609221998870741921[4] = 0;
   out_4609221998870741921[5] = 0;
   out_4609221998870741921[6] = 0;
   out_4609221998870741921[7] = 0;
   out_4609221998870741921[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_4362699660511635051) {
  err_fun(nom_x, delta_x, out_4362699660511635051);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5242751605747536921) {
  inv_err_fun(nom_x, true_x, out_5242751605747536921);
}
void car_H_mod_fun(double *state, double *out_4674979810803532886) {
  H_mod_fun(state, out_4674979810803532886);
}
void car_f_fun(double *state, double dt, double *out_3154690792987273928) {
  f_fun(state,  dt, out_3154690792987273928);
}
void car_F_fun(double *state, double dt, double *out_3170479804547101621) {
  F_fun(state,  dt, out_3170479804547101621);
}
void car_h_25(double *state, double *unused, double *out_2611331197064061038) {
  h_25(state, unused, out_2611331197064061038);
}
void car_H_25(double *state, double *unused, double *out_8976933419978149621) {
  H_25(state, unused, out_8976933419978149621);
}
void car_h_24(double *state, double *unused, double *out_3910887785984043827) {
  h_24(state, unused, out_3910887785984043827);
}
void car_H_24(double *state, double *unused, double *out_167933289972727541) {
  H_24(state, unused, out_167933289972727541);
}
void car_h_30(double *state, double *unused, double *out_9199159123540356201) {
  h_30(state, unused, out_9199159123540356201);
}
void car_H_30(double *state, double *unused, double *out_6951477695224153368) {
  H_30(state, unused, out_6951477695224153368);
}
void car_h_26(double *state, double *unused, double *out_8304075097267532980) {
  h_26(state, unused, out_8304075097267532980);
}
void car_H_26(double *state, double *unused, double *out_5235430101104093397) {
  H_26(state, unused, out_5235430101104093397);
}
void car_h_27(double *state, double *unused, double *out_3214647081740538555) {
  h_27(state, unused, out_3214647081740538555);
}
void car_H_27(double *state, double *unused, double *out_2274473778050116512) {
  H_27(state, unused, out_2274473778050116512);
}
void car_h_29(double *state, double *unused, double *out_4245911682508349770) {
  h_29(state, unused, out_4245911682508349770);
}
void car_H_29(double *state, double *unused, double *out_4959468434164933607) {
  H_29(state, unused, out_4959468434164933607);
}
void car_h_28(double *state, double *unused, double *out_834475709106320206) {
  h_28(state, unused, out_834475709106320206);
}
void car_H_28(double *state, double *unused, double *out_6923098705730259858) {
  H_28(state, unused, out_6923098705730259858);
}
void car_h_31(double *state, double *unused, double *out_2768517865415190183) {
  h_31(state, unused, out_2768517865415190183);
}
void car_H_31(double *state, double *unused, double *out_4609221998870741921) {
  H_31(state, unused, out_4609221998870741921);
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
