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
void err_fun(double *nom_x, double *delta_x, double *out_8713671304942996477) {
   out_8713671304942996477[0] = delta_x[0] + nom_x[0];
   out_8713671304942996477[1] = delta_x[1] + nom_x[1];
   out_8713671304942996477[2] = delta_x[2] + nom_x[2];
   out_8713671304942996477[3] = delta_x[3] + nom_x[3];
   out_8713671304942996477[4] = delta_x[4] + nom_x[4];
   out_8713671304942996477[5] = delta_x[5] + nom_x[5];
   out_8713671304942996477[6] = delta_x[6] + nom_x[6];
   out_8713671304942996477[7] = delta_x[7] + nom_x[7];
   out_8713671304942996477[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_3600257385094944910) {
   out_3600257385094944910[0] = -nom_x[0] + true_x[0];
   out_3600257385094944910[1] = -nom_x[1] + true_x[1];
   out_3600257385094944910[2] = -nom_x[2] + true_x[2];
   out_3600257385094944910[3] = -nom_x[3] + true_x[3];
   out_3600257385094944910[4] = -nom_x[4] + true_x[4];
   out_3600257385094944910[5] = -nom_x[5] + true_x[5];
   out_3600257385094944910[6] = -nom_x[6] + true_x[6];
   out_3600257385094944910[7] = -nom_x[7] + true_x[7];
   out_3600257385094944910[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_9147766036788271094) {
   out_9147766036788271094[0] = 1.0;
   out_9147766036788271094[1] = 0.0;
   out_9147766036788271094[2] = 0.0;
   out_9147766036788271094[3] = 0.0;
   out_9147766036788271094[4] = 0.0;
   out_9147766036788271094[5] = 0.0;
   out_9147766036788271094[6] = 0.0;
   out_9147766036788271094[7] = 0.0;
   out_9147766036788271094[8] = 0.0;
   out_9147766036788271094[9] = 0.0;
   out_9147766036788271094[10] = 1.0;
   out_9147766036788271094[11] = 0.0;
   out_9147766036788271094[12] = 0.0;
   out_9147766036788271094[13] = 0.0;
   out_9147766036788271094[14] = 0.0;
   out_9147766036788271094[15] = 0.0;
   out_9147766036788271094[16] = 0.0;
   out_9147766036788271094[17] = 0.0;
   out_9147766036788271094[18] = 0.0;
   out_9147766036788271094[19] = 0.0;
   out_9147766036788271094[20] = 1.0;
   out_9147766036788271094[21] = 0.0;
   out_9147766036788271094[22] = 0.0;
   out_9147766036788271094[23] = 0.0;
   out_9147766036788271094[24] = 0.0;
   out_9147766036788271094[25] = 0.0;
   out_9147766036788271094[26] = 0.0;
   out_9147766036788271094[27] = 0.0;
   out_9147766036788271094[28] = 0.0;
   out_9147766036788271094[29] = 0.0;
   out_9147766036788271094[30] = 1.0;
   out_9147766036788271094[31] = 0.0;
   out_9147766036788271094[32] = 0.0;
   out_9147766036788271094[33] = 0.0;
   out_9147766036788271094[34] = 0.0;
   out_9147766036788271094[35] = 0.0;
   out_9147766036788271094[36] = 0.0;
   out_9147766036788271094[37] = 0.0;
   out_9147766036788271094[38] = 0.0;
   out_9147766036788271094[39] = 0.0;
   out_9147766036788271094[40] = 1.0;
   out_9147766036788271094[41] = 0.0;
   out_9147766036788271094[42] = 0.0;
   out_9147766036788271094[43] = 0.0;
   out_9147766036788271094[44] = 0.0;
   out_9147766036788271094[45] = 0.0;
   out_9147766036788271094[46] = 0.0;
   out_9147766036788271094[47] = 0.0;
   out_9147766036788271094[48] = 0.0;
   out_9147766036788271094[49] = 0.0;
   out_9147766036788271094[50] = 1.0;
   out_9147766036788271094[51] = 0.0;
   out_9147766036788271094[52] = 0.0;
   out_9147766036788271094[53] = 0.0;
   out_9147766036788271094[54] = 0.0;
   out_9147766036788271094[55] = 0.0;
   out_9147766036788271094[56] = 0.0;
   out_9147766036788271094[57] = 0.0;
   out_9147766036788271094[58] = 0.0;
   out_9147766036788271094[59] = 0.0;
   out_9147766036788271094[60] = 1.0;
   out_9147766036788271094[61] = 0.0;
   out_9147766036788271094[62] = 0.0;
   out_9147766036788271094[63] = 0.0;
   out_9147766036788271094[64] = 0.0;
   out_9147766036788271094[65] = 0.0;
   out_9147766036788271094[66] = 0.0;
   out_9147766036788271094[67] = 0.0;
   out_9147766036788271094[68] = 0.0;
   out_9147766036788271094[69] = 0.0;
   out_9147766036788271094[70] = 1.0;
   out_9147766036788271094[71] = 0.0;
   out_9147766036788271094[72] = 0.0;
   out_9147766036788271094[73] = 0.0;
   out_9147766036788271094[74] = 0.0;
   out_9147766036788271094[75] = 0.0;
   out_9147766036788271094[76] = 0.0;
   out_9147766036788271094[77] = 0.0;
   out_9147766036788271094[78] = 0.0;
   out_9147766036788271094[79] = 0.0;
   out_9147766036788271094[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_4342466864191827990) {
   out_4342466864191827990[0] = state[0];
   out_4342466864191827990[1] = state[1];
   out_4342466864191827990[2] = state[2];
   out_4342466864191827990[3] = state[3];
   out_4342466864191827990[4] = state[4];
   out_4342466864191827990[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_4342466864191827990[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_4342466864191827990[7] = state[7];
   out_4342466864191827990[8] = state[8];
}
void F_fun(double *state, double dt, double *out_4614465668667211337) {
   out_4614465668667211337[0] = 1;
   out_4614465668667211337[1] = 0;
   out_4614465668667211337[2] = 0;
   out_4614465668667211337[3] = 0;
   out_4614465668667211337[4] = 0;
   out_4614465668667211337[5] = 0;
   out_4614465668667211337[6] = 0;
   out_4614465668667211337[7] = 0;
   out_4614465668667211337[8] = 0;
   out_4614465668667211337[9] = 0;
   out_4614465668667211337[10] = 1;
   out_4614465668667211337[11] = 0;
   out_4614465668667211337[12] = 0;
   out_4614465668667211337[13] = 0;
   out_4614465668667211337[14] = 0;
   out_4614465668667211337[15] = 0;
   out_4614465668667211337[16] = 0;
   out_4614465668667211337[17] = 0;
   out_4614465668667211337[18] = 0;
   out_4614465668667211337[19] = 0;
   out_4614465668667211337[20] = 1;
   out_4614465668667211337[21] = 0;
   out_4614465668667211337[22] = 0;
   out_4614465668667211337[23] = 0;
   out_4614465668667211337[24] = 0;
   out_4614465668667211337[25] = 0;
   out_4614465668667211337[26] = 0;
   out_4614465668667211337[27] = 0;
   out_4614465668667211337[28] = 0;
   out_4614465668667211337[29] = 0;
   out_4614465668667211337[30] = 1;
   out_4614465668667211337[31] = 0;
   out_4614465668667211337[32] = 0;
   out_4614465668667211337[33] = 0;
   out_4614465668667211337[34] = 0;
   out_4614465668667211337[35] = 0;
   out_4614465668667211337[36] = 0;
   out_4614465668667211337[37] = 0;
   out_4614465668667211337[38] = 0;
   out_4614465668667211337[39] = 0;
   out_4614465668667211337[40] = 1;
   out_4614465668667211337[41] = 0;
   out_4614465668667211337[42] = 0;
   out_4614465668667211337[43] = 0;
   out_4614465668667211337[44] = 0;
   out_4614465668667211337[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_4614465668667211337[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_4614465668667211337[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_4614465668667211337[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_4614465668667211337[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_4614465668667211337[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_4614465668667211337[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_4614465668667211337[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_4614465668667211337[53] = -9.8100000000000005*dt;
   out_4614465668667211337[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_4614465668667211337[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_4614465668667211337[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4614465668667211337[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4614465668667211337[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_4614465668667211337[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_4614465668667211337[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_4614465668667211337[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4614465668667211337[62] = 0;
   out_4614465668667211337[63] = 0;
   out_4614465668667211337[64] = 0;
   out_4614465668667211337[65] = 0;
   out_4614465668667211337[66] = 0;
   out_4614465668667211337[67] = 0;
   out_4614465668667211337[68] = 0;
   out_4614465668667211337[69] = 0;
   out_4614465668667211337[70] = 1;
   out_4614465668667211337[71] = 0;
   out_4614465668667211337[72] = 0;
   out_4614465668667211337[73] = 0;
   out_4614465668667211337[74] = 0;
   out_4614465668667211337[75] = 0;
   out_4614465668667211337[76] = 0;
   out_4614465668667211337[77] = 0;
   out_4614465668667211337[78] = 0;
   out_4614465668667211337[79] = 0;
   out_4614465668667211337[80] = 1;
}
void h_25(double *state, double *unused, double *out_4833672742345990691) {
   out_4833672742345990691[0] = state[6];
}
void H_25(double *state, double *unused, double *out_5624785386798779417) {
   out_5624785386798779417[0] = 0;
   out_5624785386798779417[1] = 0;
   out_5624785386798779417[2] = 0;
   out_5624785386798779417[3] = 0;
   out_5624785386798779417[4] = 0;
   out_5624785386798779417[5] = 0;
   out_5624785386798779417[6] = 1;
   out_5624785386798779417[7] = 0;
   out_5624785386798779417[8] = 0;
}
void h_24(double *state, double *unused, double *out_4504560578349803309) {
   out_4504560578349803309[0] = state[4];
   out_4504560578349803309[1] = state[5];
}
void H_24(double *state, double *unused, double *out_1029420071309406340) {
   out_1029420071309406340[0] = 0;
   out_1029420071309406340[1] = 0;
   out_1029420071309406340[2] = 0;
   out_1029420071309406340[3] = 0;
   out_1029420071309406340[4] = 1;
   out_1029420071309406340[5] = 0;
   out_1029420071309406340[6] = 0;
   out_1029420071309406340[7] = 0;
   out_1029420071309406340[8] = 0;
   out_1029420071309406340[9] = 0;
   out_1029420071309406340[10] = 0;
   out_1029420071309406340[11] = 0;
   out_1029420071309406340[12] = 0;
   out_1029420071309406340[13] = 0;
   out_1029420071309406340[14] = 1;
   out_1029420071309406340[15] = 0;
   out_1029420071309406340[16] = 0;
   out_1029420071309406340[17] = 0;
}
void h_30(double *state, double *unused, double *out_5849806074542888484) {
   out_5849806074542888484[0] = state[4];
}
void H_30(double *state, double *unused, double *out_8294262356783164001) {
   out_8294262356783164001[0] = 0;
   out_8294262356783164001[1] = 0;
   out_8294262356783164001[2] = 0;
   out_8294262356783164001[3] = 0;
   out_8294262356783164001[4] = 1;
   out_8294262356783164001[5] = 0;
   out_8294262356783164001[6] = 0;
   out_8294262356783164001[7] = 0;
   out_8294262356783164001[8] = 0;
}
void h_26(double *state, double *unused, double *out_783388555824545761) {
   out_783388555824545761[0] = state[7];
}
void H_26(double *state, double *unused, double *out_9080455368036715975) {
   out_9080455368036715975[0] = 0;
   out_9080455368036715975[1] = 0;
   out_9080455368036715975[2] = 0;
   out_9080455368036715975[3] = 0;
   out_9080455368036715975[4] = 0;
   out_9080455368036715975[5] = 0;
   out_9080455368036715975[6] = 0;
   out_9080455368036715975[7] = 1;
   out_9080455368036715975[8] = 0;
}
void h_27(double *state, double *unused, double *out_7870458793790323376) {
   out_7870458793790323376[0] = state[3];
}
void H_27(double *state, double *unused, double *out_7928887645742444398) {
   out_7928887645742444398[0] = 0;
   out_7928887645742444398[1] = 0;
   out_7928887645742444398[2] = 0;
   out_7928887645742444398[3] = 1;
   out_7928887645742444398[4] = 0;
   out_7928887645742444398[5] = 0;
   out_7928887645742444398[6] = 0;
   out_7928887645742444398[7] = 0;
   out_7928887645742444398[8] = 0;
}
void h_29(double *state, double *unused, double *out_7595264731505817487) {
   out_7595264731505817487[0] = state[1];
}
void H_29(double *state, double *unused, double *out_8804493701097556185) {
   out_8804493701097556185[0] = 0;
   out_8804493701097556185[1] = 1;
   out_8804493701097556185[2] = 0;
   out_8804493701097556185[3] = 0;
   out_8804493701097556185[4] = 0;
   out_8804493701097556185[5] = 0;
   out_8804493701097556185[6] = 0;
   out_8804493701097556185[7] = 0;
   out_8804493701097556185[8] = 0;
}
void h_28(double *state, double *unused, double *out_2644551577954998429) {
   out_2644551577954998429[0] = state[0];
}
void H_28(double *state, double *unused, double *out_3722094684028025611) {
   out_3722094684028025611[0] = 1;
   out_3722094684028025611[1] = 0;
   out_3722094684028025611[2] = 0;
   out_3722094684028025611[3] = 0;
   out_3722094684028025611[4] = 0;
   out_3722094684028025611[5] = 0;
   out_3722094684028025611[6] = 0;
   out_3722094684028025611[7] = 0;
   out_3722094684028025611[8] = 0;
}
void h_31(double *state, double *unused, double *out_1937162484004360245) {
   out_1937162484004360245[0] = state[8];
}
void H_31(double *state, double *unused, double *out_5594139424921818989) {
   out_5594139424921818989[0] = 0;
   out_5594139424921818989[1] = 0;
   out_5594139424921818989[2] = 0;
   out_5594139424921818989[3] = 0;
   out_5594139424921818989[4] = 0;
   out_5594139424921818989[5] = 0;
   out_5594139424921818989[6] = 0;
   out_5594139424921818989[7] = 0;
   out_5594139424921818989[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_8713671304942996477) {
  err_fun(nom_x, delta_x, out_8713671304942996477);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3600257385094944910) {
  inv_err_fun(nom_x, true_x, out_3600257385094944910);
}
void car_H_mod_fun(double *state, double *out_9147766036788271094) {
  H_mod_fun(state, out_9147766036788271094);
}
void car_f_fun(double *state, double dt, double *out_4342466864191827990) {
  f_fun(state,  dt, out_4342466864191827990);
}
void car_F_fun(double *state, double dt, double *out_4614465668667211337) {
  F_fun(state,  dt, out_4614465668667211337);
}
void car_h_25(double *state, double *unused, double *out_4833672742345990691) {
  h_25(state, unused, out_4833672742345990691);
}
void car_H_25(double *state, double *unused, double *out_5624785386798779417) {
  H_25(state, unused, out_5624785386798779417);
}
void car_h_24(double *state, double *unused, double *out_4504560578349803309) {
  h_24(state, unused, out_4504560578349803309);
}
void car_H_24(double *state, double *unused, double *out_1029420071309406340) {
  H_24(state, unused, out_1029420071309406340);
}
void car_h_30(double *state, double *unused, double *out_5849806074542888484) {
  h_30(state, unused, out_5849806074542888484);
}
void car_H_30(double *state, double *unused, double *out_8294262356783164001) {
  H_30(state, unused, out_8294262356783164001);
}
void car_h_26(double *state, double *unused, double *out_783388555824545761) {
  h_26(state, unused, out_783388555824545761);
}
void car_H_26(double *state, double *unused, double *out_9080455368036715975) {
  H_26(state, unused, out_9080455368036715975);
}
void car_h_27(double *state, double *unused, double *out_7870458793790323376) {
  h_27(state, unused, out_7870458793790323376);
}
void car_H_27(double *state, double *unused, double *out_7928887645742444398) {
  H_27(state, unused, out_7928887645742444398);
}
void car_h_29(double *state, double *unused, double *out_7595264731505817487) {
  h_29(state, unused, out_7595264731505817487);
}
void car_H_29(double *state, double *unused, double *out_8804493701097556185) {
  H_29(state, unused, out_8804493701097556185);
}
void car_h_28(double *state, double *unused, double *out_2644551577954998429) {
  h_28(state, unused, out_2644551577954998429);
}
void car_H_28(double *state, double *unused, double *out_3722094684028025611) {
  H_28(state, unused, out_3722094684028025611);
}
void car_h_31(double *state, double *unused, double *out_1937162484004360245) {
  h_31(state, unused, out_1937162484004360245);
}
void car_H_31(double *state, double *unused, double *out_5594139424921818989) {
  H_31(state, unused, out_5594139424921818989);
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
