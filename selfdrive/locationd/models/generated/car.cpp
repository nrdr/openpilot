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
void err_fun(double *nom_x, double *delta_x, double *out_1937171401964887448) {
   out_1937171401964887448[0] = delta_x[0] + nom_x[0];
   out_1937171401964887448[1] = delta_x[1] + nom_x[1];
   out_1937171401964887448[2] = delta_x[2] + nom_x[2];
   out_1937171401964887448[3] = delta_x[3] + nom_x[3];
   out_1937171401964887448[4] = delta_x[4] + nom_x[4];
   out_1937171401964887448[5] = delta_x[5] + nom_x[5];
   out_1937171401964887448[6] = delta_x[6] + nom_x[6];
   out_1937171401964887448[7] = delta_x[7] + nom_x[7];
   out_1937171401964887448[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_8623208480402510856) {
   out_8623208480402510856[0] = -nom_x[0] + true_x[0];
   out_8623208480402510856[1] = -nom_x[1] + true_x[1];
   out_8623208480402510856[2] = -nom_x[2] + true_x[2];
   out_8623208480402510856[3] = -nom_x[3] + true_x[3];
   out_8623208480402510856[4] = -nom_x[4] + true_x[4];
   out_8623208480402510856[5] = -nom_x[5] + true_x[5];
   out_8623208480402510856[6] = -nom_x[6] + true_x[6];
   out_8623208480402510856[7] = -nom_x[7] + true_x[7];
   out_8623208480402510856[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_5195459774287487890) {
   out_5195459774287487890[0] = 1.0;
   out_5195459774287487890[1] = 0.0;
   out_5195459774287487890[2] = 0.0;
   out_5195459774287487890[3] = 0.0;
   out_5195459774287487890[4] = 0.0;
   out_5195459774287487890[5] = 0.0;
   out_5195459774287487890[6] = 0.0;
   out_5195459774287487890[7] = 0.0;
   out_5195459774287487890[8] = 0.0;
   out_5195459774287487890[9] = 0.0;
   out_5195459774287487890[10] = 1.0;
   out_5195459774287487890[11] = 0.0;
   out_5195459774287487890[12] = 0.0;
   out_5195459774287487890[13] = 0.0;
   out_5195459774287487890[14] = 0.0;
   out_5195459774287487890[15] = 0.0;
   out_5195459774287487890[16] = 0.0;
   out_5195459774287487890[17] = 0.0;
   out_5195459774287487890[18] = 0.0;
   out_5195459774287487890[19] = 0.0;
   out_5195459774287487890[20] = 1.0;
   out_5195459774287487890[21] = 0.0;
   out_5195459774287487890[22] = 0.0;
   out_5195459774287487890[23] = 0.0;
   out_5195459774287487890[24] = 0.0;
   out_5195459774287487890[25] = 0.0;
   out_5195459774287487890[26] = 0.0;
   out_5195459774287487890[27] = 0.0;
   out_5195459774287487890[28] = 0.0;
   out_5195459774287487890[29] = 0.0;
   out_5195459774287487890[30] = 1.0;
   out_5195459774287487890[31] = 0.0;
   out_5195459774287487890[32] = 0.0;
   out_5195459774287487890[33] = 0.0;
   out_5195459774287487890[34] = 0.0;
   out_5195459774287487890[35] = 0.0;
   out_5195459774287487890[36] = 0.0;
   out_5195459774287487890[37] = 0.0;
   out_5195459774287487890[38] = 0.0;
   out_5195459774287487890[39] = 0.0;
   out_5195459774287487890[40] = 1.0;
   out_5195459774287487890[41] = 0.0;
   out_5195459774287487890[42] = 0.0;
   out_5195459774287487890[43] = 0.0;
   out_5195459774287487890[44] = 0.0;
   out_5195459774287487890[45] = 0.0;
   out_5195459774287487890[46] = 0.0;
   out_5195459774287487890[47] = 0.0;
   out_5195459774287487890[48] = 0.0;
   out_5195459774287487890[49] = 0.0;
   out_5195459774287487890[50] = 1.0;
   out_5195459774287487890[51] = 0.0;
   out_5195459774287487890[52] = 0.0;
   out_5195459774287487890[53] = 0.0;
   out_5195459774287487890[54] = 0.0;
   out_5195459774287487890[55] = 0.0;
   out_5195459774287487890[56] = 0.0;
   out_5195459774287487890[57] = 0.0;
   out_5195459774287487890[58] = 0.0;
   out_5195459774287487890[59] = 0.0;
   out_5195459774287487890[60] = 1.0;
   out_5195459774287487890[61] = 0.0;
   out_5195459774287487890[62] = 0.0;
   out_5195459774287487890[63] = 0.0;
   out_5195459774287487890[64] = 0.0;
   out_5195459774287487890[65] = 0.0;
   out_5195459774287487890[66] = 0.0;
   out_5195459774287487890[67] = 0.0;
   out_5195459774287487890[68] = 0.0;
   out_5195459774287487890[69] = 0.0;
   out_5195459774287487890[70] = 1.0;
   out_5195459774287487890[71] = 0.0;
   out_5195459774287487890[72] = 0.0;
   out_5195459774287487890[73] = 0.0;
   out_5195459774287487890[74] = 0.0;
   out_5195459774287487890[75] = 0.0;
   out_5195459774287487890[76] = 0.0;
   out_5195459774287487890[77] = 0.0;
   out_5195459774287487890[78] = 0.0;
   out_5195459774287487890[79] = 0.0;
   out_5195459774287487890[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3416588175527017726) {
   out_3416588175527017726[0] = state[0];
   out_3416588175527017726[1] = state[1];
   out_3416588175527017726[2] = state[2];
   out_3416588175527017726[3] = state[3];
   out_3416588175527017726[4] = state[4];
   out_3416588175527017726[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_3416588175527017726[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3416588175527017726[7] = state[7];
   out_3416588175527017726[8] = state[8];
}
void F_fun(double *state, double dt, double *out_4650294569433468939) {
   out_4650294569433468939[0] = 1;
   out_4650294569433468939[1] = 0;
   out_4650294569433468939[2] = 0;
   out_4650294569433468939[3] = 0;
   out_4650294569433468939[4] = 0;
   out_4650294569433468939[5] = 0;
   out_4650294569433468939[6] = 0;
   out_4650294569433468939[7] = 0;
   out_4650294569433468939[8] = 0;
   out_4650294569433468939[9] = 0;
   out_4650294569433468939[10] = 1;
   out_4650294569433468939[11] = 0;
   out_4650294569433468939[12] = 0;
   out_4650294569433468939[13] = 0;
   out_4650294569433468939[14] = 0;
   out_4650294569433468939[15] = 0;
   out_4650294569433468939[16] = 0;
   out_4650294569433468939[17] = 0;
   out_4650294569433468939[18] = 0;
   out_4650294569433468939[19] = 0;
   out_4650294569433468939[20] = 1;
   out_4650294569433468939[21] = 0;
   out_4650294569433468939[22] = 0;
   out_4650294569433468939[23] = 0;
   out_4650294569433468939[24] = 0;
   out_4650294569433468939[25] = 0;
   out_4650294569433468939[26] = 0;
   out_4650294569433468939[27] = 0;
   out_4650294569433468939[28] = 0;
   out_4650294569433468939[29] = 0;
   out_4650294569433468939[30] = 1;
   out_4650294569433468939[31] = 0;
   out_4650294569433468939[32] = 0;
   out_4650294569433468939[33] = 0;
   out_4650294569433468939[34] = 0;
   out_4650294569433468939[35] = 0;
   out_4650294569433468939[36] = 0;
   out_4650294569433468939[37] = 0;
   out_4650294569433468939[38] = 0;
   out_4650294569433468939[39] = 0;
   out_4650294569433468939[40] = 1;
   out_4650294569433468939[41] = 0;
   out_4650294569433468939[42] = 0;
   out_4650294569433468939[43] = 0;
   out_4650294569433468939[44] = 0;
   out_4650294569433468939[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_4650294569433468939[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_4650294569433468939[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_4650294569433468939[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_4650294569433468939[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_4650294569433468939[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_4650294569433468939[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_4650294569433468939[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_4650294569433468939[53] = -9.8100000000000005*dt;
   out_4650294569433468939[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_4650294569433468939[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_4650294569433468939[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4650294569433468939[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4650294569433468939[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_4650294569433468939[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_4650294569433468939[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_4650294569433468939[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4650294569433468939[62] = 0;
   out_4650294569433468939[63] = 0;
   out_4650294569433468939[64] = 0;
   out_4650294569433468939[65] = 0;
   out_4650294569433468939[66] = 0;
   out_4650294569433468939[67] = 0;
   out_4650294569433468939[68] = 0;
   out_4650294569433468939[69] = 0;
   out_4650294569433468939[70] = 1;
   out_4650294569433468939[71] = 0;
   out_4650294569433468939[72] = 0;
   out_4650294569433468939[73] = 0;
   out_4650294569433468939[74] = 0;
   out_4650294569433468939[75] = 0;
   out_4650294569433468939[76] = 0;
   out_4650294569433468939[77] = 0;
   out_4650294569433468939[78] = 0;
   out_4650294569433468939[79] = 0;
   out_4650294569433468939[80] = 1;
}
void h_25(double *state, double *unused, double *out_1746813054384403481) {
   out_1746813054384403481[0] = state[6];
}
void H_25(double *state, double *unused, double *out_1913198722745912190) {
   out_1913198722745912190[0] = 0;
   out_1913198722745912190[1] = 0;
   out_1913198722745912190[2] = 0;
   out_1913198722745912190[3] = 0;
   out_1913198722745912190[4] = 0;
   out_1913198722745912190[5] = 0;
   out_1913198722745912190[6] = 1;
   out_1913198722745912190[7] = 0;
   out_1913198722745912190[8] = 0;
}
void h_24(double *state, double *unused, double *out_4499001988919102230) {
   out_4499001988919102230[0] = state[4];
   out_4499001988919102230[1] = state[5];
}
void H_24(double *state, double *unused, double *out_259450876259587376) {
   out_259450876259587376[0] = 0;
   out_259450876259587376[1] = 0;
   out_259450876259587376[2] = 0;
   out_259450876259587376[3] = 0;
   out_259450876259587376[4] = 1;
   out_259450876259587376[5] = 0;
   out_259450876259587376[6] = 0;
   out_259450876259587376[7] = 0;
   out_259450876259587376[8] = 0;
   out_259450876259587376[9] = 0;
   out_259450876259587376[10] = 0;
   out_259450876259587376[11] = 0;
   out_259450876259587376[12] = 0;
   out_259450876259587376[13] = 0;
   out_259450876259587376[14] = 1;
   out_259450876259587376[15] = 0;
   out_259450876259587376[16] = 0;
   out_259450876259587376[17] = 0;
}
void h_30(double *state, double *unused, double *out_1903999722735532626) {
   out_1903999722735532626[0] = state[4];
}
void H_30(double *state, double *unused, double *out_8829889064237528945) {
   out_8829889064237528945[0] = 0;
   out_8829889064237528945[1] = 0;
   out_8829889064237528945[2] = 0;
   out_8829889064237528945[3] = 0;
   out_8829889064237528945[4] = 1;
   out_8829889064237528945[5] = 0;
   out_8829889064237528945[6] = 0;
   out_8829889064237528945[7] = 0;
   out_8829889064237528945[8] = 0;
}
void h_26(double *state, double *unused, double *out_1132786328708800059) {
   out_1132786328708800059[0] = state[7];
}
void H_26(double *state, double *unused, double *out_1828304596128144034) {
   out_1828304596128144034[0] = 0;
   out_1828304596128144034[1] = 0;
   out_1828304596128144034[2] = 0;
   out_1828304596128144034[3] = 0;
   out_1828304596128144034[4] = 0;
   out_1828304596128144034[5] = 0;
   out_1828304596128144034[6] = 0;
   out_1828304596128144034[7] = 1;
   out_1828304596128144034[8] = 0;
}
void h_27(double *state, double *unused, double *out_2678547860913828052) {
   out_2678547860913828052[0] = state[3];
}
void H_27(double *state, double *unused, double *out_390903536197752791) {
   out_390903536197752791[0] = 0;
   out_390903536197752791[1] = 0;
   out_390903536197752791[2] = 0;
   out_390903536197752791[3] = 1;
   out_390903536197752791[4] = 0;
   out_390903536197752791[5] = 0;
   out_390903536197752791[6] = 0;
   out_390903536197752791[7] = 0;
   out_390903536197752791[8] = 0;
}
void h_29(double *state, double *unused, double *out_3594447557471213586) {
   out_3594447557471213586[0] = state[1];
}
void H_29(double *state, double *unused, double *out_2104266263067303824) {
   out_2104266263067303824[0] = 0;
   out_2104266263067303824[1] = 1;
   out_2104266263067303824[2] = 0;
   out_2104266263067303824[3] = 0;
   out_2104266263067303824[4] = 0;
   out_2104266263067303824[5] = 0;
   out_2104266263067303824[6] = 0;
   out_2104266263067303824[7] = 0;
   out_2104266263067303824[8] = 0;
}
void h_28(double *state, double *unused, double *out_8321277731994784887) {
   out_8321277731994784887[0] = state[0];
}
void H_28(double *state, double *unused, double *out_140635991501977573) {
   out_140635991501977573[0] = 1;
   out_140635991501977573[1] = 0;
   out_140635991501977573[2] = 0;
   out_140635991501977573[3] = 0;
   out_140635991501977573[4] = 0;
   out_140635991501977573[5] = 0;
   out_140635991501977573[6] = 0;
   out_140635991501977573[7] = 0;
   out_140635991501977573[8] = 0;
}
void h_31(double *state, double *unused, double *out_5713745709864484844) {
   out_5713745709864484844[0] = state[8];
}
void H_31(double *state, double *unused, double *out_1943844684622872618) {
   out_1943844684622872618[0] = 0;
   out_1943844684622872618[1] = 0;
   out_1943844684622872618[2] = 0;
   out_1943844684622872618[3] = 0;
   out_1943844684622872618[4] = 0;
   out_1943844684622872618[5] = 0;
   out_1943844684622872618[6] = 0;
   out_1943844684622872618[7] = 0;
   out_1943844684622872618[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_1937171401964887448) {
  err_fun(nom_x, delta_x, out_1937171401964887448);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8623208480402510856) {
  inv_err_fun(nom_x, true_x, out_8623208480402510856);
}
void car_H_mod_fun(double *state, double *out_5195459774287487890) {
  H_mod_fun(state, out_5195459774287487890);
}
void car_f_fun(double *state, double dt, double *out_3416588175527017726) {
  f_fun(state,  dt, out_3416588175527017726);
}
void car_F_fun(double *state, double dt, double *out_4650294569433468939) {
  F_fun(state,  dt, out_4650294569433468939);
}
void car_h_25(double *state, double *unused, double *out_1746813054384403481) {
  h_25(state, unused, out_1746813054384403481);
}
void car_H_25(double *state, double *unused, double *out_1913198722745912190) {
  H_25(state, unused, out_1913198722745912190);
}
void car_h_24(double *state, double *unused, double *out_4499001988919102230) {
  h_24(state, unused, out_4499001988919102230);
}
void car_H_24(double *state, double *unused, double *out_259450876259587376) {
  H_24(state, unused, out_259450876259587376);
}
void car_h_30(double *state, double *unused, double *out_1903999722735532626) {
  h_30(state, unused, out_1903999722735532626);
}
void car_H_30(double *state, double *unused, double *out_8829889064237528945) {
  H_30(state, unused, out_8829889064237528945);
}
void car_h_26(double *state, double *unused, double *out_1132786328708800059) {
  h_26(state, unused, out_1132786328708800059);
}
void car_H_26(double *state, double *unused, double *out_1828304596128144034) {
  H_26(state, unused, out_1828304596128144034);
}
void car_h_27(double *state, double *unused, double *out_2678547860913828052) {
  h_27(state, unused, out_2678547860913828052);
}
void car_H_27(double *state, double *unused, double *out_390903536197752791) {
  H_27(state, unused, out_390903536197752791);
}
void car_h_29(double *state, double *unused, double *out_3594447557471213586) {
  h_29(state, unused, out_3594447557471213586);
}
void car_H_29(double *state, double *unused, double *out_2104266263067303824) {
  H_29(state, unused, out_2104266263067303824);
}
void car_h_28(double *state, double *unused, double *out_8321277731994784887) {
  h_28(state, unused, out_8321277731994784887);
}
void car_H_28(double *state, double *unused, double *out_140635991501977573) {
  H_28(state, unused, out_140635991501977573);
}
void car_h_31(double *state, double *unused, double *out_5713745709864484844) {
  h_31(state, unused, out_5713745709864484844);
}
void car_H_31(double *state, double *unused, double *out_1943844684622872618) {
  H_31(state, unused, out_1943844684622872618);
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
