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
void err_fun(double *nom_x, double *delta_x, double *out_6502015734495733948) {
   out_6502015734495733948[0] = delta_x[0] + nom_x[0];
   out_6502015734495733948[1] = delta_x[1] + nom_x[1];
   out_6502015734495733948[2] = delta_x[2] + nom_x[2];
   out_6502015734495733948[3] = delta_x[3] + nom_x[3];
   out_6502015734495733948[4] = delta_x[4] + nom_x[4];
   out_6502015734495733948[5] = delta_x[5] + nom_x[5];
   out_6502015734495733948[6] = delta_x[6] + nom_x[6];
   out_6502015734495733948[7] = delta_x[7] + nom_x[7];
   out_6502015734495733948[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_315300592301695071) {
   out_315300592301695071[0] = -nom_x[0] + true_x[0];
   out_315300592301695071[1] = -nom_x[1] + true_x[1];
   out_315300592301695071[2] = -nom_x[2] + true_x[2];
   out_315300592301695071[3] = -nom_x[3] + true_x[3];
   out_315300592301695071[4] = -nom_x[4] + true_x[4];
   out_315300592301695071[5] = -nom_x[5] + true_x[5];
   out_315300592301695071[6] = -nom_x[6] + true_x[6];
   out_315300592301695071[7] = -nom_x[7] + true_x[7];
   out_315300592301695071[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_3700698090332376439) {
   out_3700698090332376439[0] = 1.0;
   out_3700698090332376439[1] = 0.0;
   out_3700698090332376439[2] = 0.0;
   out_3700698090332376439[3] = 0.0;
   out_3700698090332376439[4] = 0.0;
   out_3700698090332376439[5] = 0.0;
   out_3700698090332376439[6] = 0.0;
   out_3700698090332376439[7] = 0.0;
   out_3700698090332376439[8] = 0.0;
   out_3700698090332376439[9] = 0.0;
   out_3700698090332376439[10] = 1.0;
   out_3700698090332376439[11] = 0.0;
   out_3700698090332376439[12] = 0.0;
   out_3700698090332376439[13] = 0.0;
   out_3700698090332376439[14] = 0.0;
   out_3700698090332376439[15] = 0.0;
   out_3700698090332376439[16] = 0.0;
   out_3700698090332376439[17] = 0.0;
   out_3700698090332376439[18] = 0.0;
   out_3700698090332376439[19] = 0.0;
   out_3700698090332376439[20] = 1.0;
   out_3700698090332376439[21] = 0.0;
   out_3700698090332376439[22] = 0.0;
   out_3700698090332376439[23] = 0.0;
   out_3700698090332376439[24] = 0.0;
   out_3700698090332376439[25] = 0.0;
   out_3700698090332376439[26] = 0.0;
   out_3700698090332376439[27] = 0.0;
   out_3700698090332376439[28] = 0.0;
   out_3700698090332376439[29] = 0.0;
   out_3700698090332376439[30] = 1.0;
   out_3700698090332376439[31] = 0.0;
   out_3700698090332376439[32] = 0.0;
   out_3700698090332376439[33] = 0.0;
   out_3700698090332376439[34] = 0.0;
   out_3700698090332376439[35] = 0.0;
   out_3700698090332376439[36] = 0.0;
   out_3700698090332376439[37] = 0.0;
   out_3700698090332376439[38] = 0.0;
   out_3700698090332376439[39] = 0.0;
   out_3700698090332376439[40] = 1.0;
   out_3700698090332376439[41] = 0.0;
   out_3700698090332376439[42] = 0.0;
   out_3700698090332376439[43] = 0.0;
   out_3700698090332376439[44] = 0.0;
   out_3700698090332376439[45] = 0.0;
   out_3700698090332376439[46] = 0.0;
   out_3700698090332376439[47] = 0.0;
   out_3700698090332376439[48] = 0.0;
   out_3700698090332376439[49] = 0.0;
   out_3700698090332376439[50] = 1.0;
   out_3700698090332376439[51] = 0.0;
   out_3700698090332376439[52] = 0.0;
   out_3700698090332376439[53] = 0.0;
   out_3700698090332376439[54] = 0.0;
   out_3700698090332376439[55] = 0.0;
   out_3700698090332376439[56] = 0.0;
   out_3700698090332376439[57] = 0.0;
   out_3700698090332376439[58] = 0.0;
   out_3700698090332376439[59] = 0.0;
   out_3700698090332376439[60] = 1.0;
   out_3700698090332376439[61] = 0.0;
   out_3700698090332376439[62] = 0.0;
   out_3700698090332376439[63] = 0.0;
   out_3700698090332376439[64] = 0.0;
   out_3700698090332376439[65] = 0.0;
   out_3700698090332376439[66] = 0.0;
   out_3700698090332376439[67] = 0.0;
   out_3700698090332376439[68] = 0.0;
   out_3700698090332376439[69] = 0.0;
   out_3700698090332376439[70] = 1.0;
   out_3700698090332376439[71] = 0.0;
   out_3700698090332376439[72] = 0.0;
   out_3700698090332376439[73] = 0.0;
   out_3700698090332376439[74] = 0.0;
   out_3700698090332376439[75] = 0.0;
   out_3700698090332376439[76] = 0.0;
   out_3700698090332376439[77] = 0.0;
   out_3700698090332376439[78] = 0.0;
   out_3700698090332376439[79] = 0.0;
   out_3700698090332376439[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_5551964765070894208) {
   out_5551964765070894208[0] = state[0];
   out_5551964765070894208[1] = state[1];
   out_5551964765070894208[2] = state[2];
   out_5551964765070894208[3] = state[3];
   out_5551964765070894208[4] = state[4];
   out_5551964765070894208[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_5551964765070894208[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_5551964765070894208[7] = state[7];
   out_5551964765070894208[8] = state[8];
}
void F_fun(double *state, double dt, double *out_3387046927581760157) {
   out_3387046927581760157[0] = 1;
   out_3387046927581760157[1] = 0;
   out_3387046927581760157[2] = 0;
   out_3387046927581760157[3] = 0;
   out_3387046927581760157[4] = 0;
   out_3387046927581760157[5] = 0;
   out_3387046927581760157[6] = 0;
   out_3387046927581760157[7] = 0;
   out_3387046927581760157[8] = 0;
   out_3387046927581760157[9] = 0;
   out_3387046927581760157[10] = 1;
   out_3387046927581760157[11] = 0;
   out_3387046927581760157[12] = 0;
   out_3387046927581760157[13] = 0;
   out_3387046927581760157[14] = 0;
   out_3387046927581760157[15] = 0;
   out_3387046927581760157[16] = 0;
   out_3387046927581760157[17] = 0;
   out_3387046927581760157[18] = 0;
   out_3387046927581760157[19] = 0;
   out_3387046927581760157[20] = 1;
   out_3387046927581760157[21] = 0;
   out_3387046927581760157[22] = 0;
   out_3387046927581760157[23] = 0;
   out_3387046927581760157[24] = 0;
   out_3387046927581760157[25] = 0;
   out_3387046927581760157[26] = 0;
   out_3387046927581760157[27] = 0;
   out_3387046927581760157[28] = 0;
   out_3387046927581760157[29] = 0;
   out_3387046927581760157[30] = 1;
   out_3387046927581760157[31] = 0;
   out_3387046927581760157[32] = 0;
   out_3387046927581760157[33] = 0;
   out_3387046927581760157[34] = 0;
   out_3387046927581760157[35] = 0;
   out_3387046927581760157[36] = 0;
   out_3387046927581760157[37] = 0;
   out_3387046927581760157[38] = 0;
   out_3387046927581760157[39] = 0;
   out_3387046927581760157[40] = 1;
   out_3387046927581760157[41] = 0;
   out_3387046927581760157[42] = 0;
   out_3387046927581760157[43] = 0;
   out_3387046927581760157[44] = 0;
   out_3387046927581760157[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_3387046927581760157[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_3387046927581760157[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3387046927581760157[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3387046927581760157[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_3387046927581760157[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_3387046927581760157[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_3387046927581760157[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_3387046927581760157[53] = -9.8100000000000005*dt;
   out_3387046927581760157[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_3387046927581760157[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_3387046927581760157[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3387046927581760157[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3387046927581760157[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_3387046927581760157[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_3387046927581760157[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_3387046927581760157[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3387046927581760157[62] = 0;
   out_3387046927581760157[63] = 0;
   out_3387046927581760157[64] = 0;
   out_3387046927581760157[65] = 0;
   out_3387046927581760157[66] = 0;
   out_3387046927581760157[67] = 0;
   out_3387046927581760157[68] = 0;
   out_3387046927581760157[69] = 0;
   out_3387046927581760157[70] = 1;
   out_3387046927581760157[71] = 0;
   out_3387046927581760157[72] = 0;
   out_3387046927581760157[73] = 0;
   out_3387046927581760157[74] = 0;
   out_3387046927581760157[75] = 0;
   out_3387046927581760157[76] = 0;
   out_3387046927581760157[77] = 0;
   out_3387046927581760157[78] = 0;
   out_3387046927581760157[79] = 0;
   out_3387046927581760157[80] = 1;
}
void h_25(double *state, double *unused, double *out_7748246721111864678) {
   out_7748246721111864678[0] = state[6];
}
void H_25(double *state, double *unused, double *out_1553539153054996027) {
   out_1553539153054996027[0] = 0;
   out_1553539153054996027[1] = 0;
   out_1553539153054996027[2] = 0;
   out_1553539153054996027[3] = 0;
   out_1553539153054996027[4] = 0;
   out_1553539153054996027[5] = 0;
   out_1553539153054996027[6] = 1;
   out_1553539153054996027[7] = 0;
   out_1553539153054996027[8] = 0;
}
void h_24(double *state, double *unused, double *out_3014180275814606991) {
   out_3014180275814606991[0] = state[4];
   out_3014180275814606991[1] = state[5];
}
void H_24(double *state, double *unused, double *out_7665139734585360364) {
   out_7665139734585360364[0] = 0;
   out_7665139734585360364[1] = 0;
   out_7665139734585360364[2] = 0;
   out_7665139734585360364[3] = 0;
   out_7665139734585360364[4] = 1;
   out_7665139734585360364[5] = 0;
   out_7665139734585360364[6] = 0;
   out_7665139734585360364[7] = 0;
   out_7665139734585360364[8] = 0;
   out_7665139734585360364[9] = 0;
   out_7665139734585360364[10] = 0;
   out_7665139734585360364[11] = 0;
   out_7665139734585360364[12] = 0;
   out_7665139734585360364[13] = 0;
   out_7665139734585360364[14] = 1;
   out_7665139734585360364[15] = 0;
   out_7665139734585360364[16] = 0;
   out_7665139734585360364[17] = 0;
}
void h_30(double *state, double *unused, double *out_556697608256352882) {
   out_556697608256352882[0] = state[4];
}
void H_30(double *state, double *unused, double *out_1424200205911755957) {
   out_1424200205911755957[0] = 0;
   out_1424200205911755957[1] = 0;
   out_1424200205911755957[2] = 0;
   out_1424200205911755957[3] = 0;
   out_1424200205911755957[4] = 1;
   out_1424200205911755957[5] = 0;
   out_1424200205911755957[6] = 0;
   out_1424200205911755957[7] = 0;
   out_1424200205911755957[8] = 0;
}
void h_26(double *state, double *unused, double *out_5842343909157496264) {
   out_5842343909157496264[0] = state[7];
}
void H_26(double *state, double *unused, double *out_2187964165819060197) {
   out_2187964165819060197[0] = 0;
   out_2187964165819060197[1] = 0;
   out_2187964165819060197[2] = 0;
   out_2187964165819060197[3] = 0;
   out_2187964165819060197[4] = 0;
   out_2187964165819060197[5] = 0;
   out_2187964165819060197[6] = 0;
   out_2187964165819060197[7] = 1;
   out_2187964165819060197[8] = 0;
}
void h_27(double *state, double *unused, double *out_8691756574013527113) {
   out_8691756574013527113[0] = state[3];
}
void H_27(double *state, double *unused, double *out_750563105888668954) {
   out_750563105888668954[0] = 0;
   out_750563105888668954[1] = 0;
   out_750563105888668954[2] = 0;
   out_750563105888668954[3] = 1;
   out_750563105888668954[4] = 0;
   out_750563105888668954[5] = 0;
   out_750563105888668954[6] = 0;
   out_750563105888668954[7] = 0;
   out_750563105888668954[8] = 0;
}
void h_29(double *state, double *unused, double *out_3841254473025276130) {
   out_3841254473025276130[0] = state[1];
}
void H_29(double *state, double *unused, double *out_2463925832758219987) {
   out_2463925832758219987[0] = 0;
   out_2463925832758219987[1] = 1;
   out_2463925832758219987[2] = 0;
   out_2463925832758219987[3] = 0;
   out_2463925832758219987[4] = 0;
   out_2463925832758219987[5] = 0;
   out_2463925832758219987[6] = 0;
   out_2463925832758219987[7] = 0;
   out_2463925832758219987[8] = 0;
}
void h_28(double *state, double *unused, double *out_3355945982282175357) {
   out_3355945982282175357[0] = state[0];
}
void H_28(double *state, double *unused, double *out_7546324849827750561) {
   out_7546324849827750561[0] = 1;
   out_7546324849827750561[1] = 0;
   out_7546324849827750561[2] = 0;
   out_7546324849827750561[3] = 0;
   out_7546324849827750561[4] = 0;
   out_7546324849827750561[5] = 0;
   out_7546324849827750561[6] = 0;
   out_7546324849827750561[7] = 0;
   out_7546324849827750561[8] = 0;
}
void h_31(double *state, double *unused, double *out_7061047824343664588) {
   out_7061047824343664588[0] = state[8];
}
void H_31(double *state, double *unused, double *out_1584185114931956455) {
   out_1584185114931956455[0] = 0;
   out_1584185114931956455[1] = 0;
   out_1584185114931956455[2] = 0;
   out_1584185114931956455[3] = 0;
   out_1584185114931956455[4] = 0;
   out_1584185114931956455[5] = 0;
   out_1584185114931956455[6] = 0;
   out_1584185114931956455[7] = 0;
   out_1584185114931956455[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_6502015734495733948) {
  err_fun(nom_x, delta_x, out_6502015734495733948);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_315300592301695071) {
  inv_err_fun(nom_x, true_x, out_315300592301695071);
}
void car_H_mod_fun(double *state, double *out_3700698090332376439) {
  H_mod_fun(state, out_3700698090332376439);
}
void car_f_fun(double *state, double dt, double *out_5551964765070894208) {
  f_fun(state,  dt, out_5551964765070894208);
}
void car_F_fun(double *state, double dt, double *out_3387046927581760157) {
  F_fun(state,  dt, out_3387046927581760157);
}
void car_h_25(double *state, double *unused, double *out_7748246721111864678) {
  h_25(state, unused, out_7748246721111864678);
}
void car_H_25(double *state, double *unused, double *out_1553539153054996027) {
  H_25(state, unused, out_1553539153054996027);
}
void car_h_24(double *state, double *unused, double *out_3014180275814606991) {
  h_24(state, unused, out_3014180275814606991);
}
void car_H_24(double *state, double *unused, double *out_7665139734585360364) {
  H_24(state, unused, out_7665139734585360364);
}
void car_h_30(double *state, double *unused, double *out_556697608256352882) {
  h_30(state, unused, out_556697608256352882);
}
void car_H_30(double *state, double *unused, double *out_1424200205911755957) {
  H_30(state, unused, out_1424200205911755957);
}
void car_h_26(double *state, double *unused, double *out_5842343909157496264) {
  h_26(state, unused, out_5842343909157496264);
}
void car_H_26(double *state, double *unused, double *out_2187964165819060197) {
  H_26(state, unused, out_2187964165819060197);
}
void car_h_27(double *state, double *unused, double *out_8691756574013527113) {
  h_27(state, unused, out_8691756574013527113);
}
void car_H_27(double *state, double *unused, double *out_750563105888668954) {
  H_27(state, unused, out_750563105888668954);
}
void car_h_29(double *state, double *unused, double *out_3841254473025276130) {
  h_29(state, unused, out_3841254473025276130);
}
void car_H_29(double *state, double *unused, double *out_2463925832758219987) {
  H_29(state, unused, out_2463925832758219987);
}
void car_h_28(double *state, double *unused, double *out_3355945982282175357) {
  h_28(state, unused, out_3355945982282175357);
}
void car_H_28(double *state, double *unused, double *out_7546324849827750561) {
  H_28(state, unused, out_7546324849827750561);
}
void car_h_31(double *state, double *unused, double *out_7061047824343664588) {
  h_31(state, unused, out_7061047824343664588);
}
void car_H_31(double *state, double *unused, double *out_1584185114931956455) {
  H_31(state, unused, out_1584185114931956455);
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
