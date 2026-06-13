#include "pose.h"

namespace {
#define DIM 18
#define EDIM 18
#define MEDIM 18
typedef void (*Hfun)(double *, double *, double *);
const static double MAHA_THRESH_4 = 7.814727903251177;
const static double MAHA_THRESH_10 = 7.814727903251177;
const static double MAHA_THRESH_13 = 7.814727903251177;
const static double MAHA_THRESH_14 = 7.814727903251177;

/******************************************************************************
 *                      Code generated with SymPy 1.14.0                      *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_4130250514567188612) {
   out_4130250514567188612[0] = delta_x[0] + nom_x[0];
   out_4130250514567188612[1] = delta_x[1] + nom_x[1];
   out_4130250514567188612[2] = delta_x[2] + nom_x[2];
   out_4130250514567188612[3] = delta_x[3] + nom_x[3];
   out_4130250514567188612[4] = delta_x[4] + nom_x[4];
   out_4130250514567188612[5] = delta_x[5] + nom_x[5];
   out_4130250514567188612[6] = delta_x[6] + nom_x[6];
   out_4130250514567188612[7] = delta_x[7] + nom_x[7];
   out_4130250514567188612[8] = delta_x[8] + nom_x[8];
   out_4130250514567188612[9] = delta_x[9] + nom_x[9];
   out_4130250514567188612[10] = delta_x[10] + nom_x[10];
   out_4130250514567188612[11] = delta_x[11] + nom_x[11];
   out_4130250514567188612[12] = delta_x[12] + nom_x[12];
   out_4130250514567188612[13] = delta_x[13] + nom_x[13];
   out_4130250514567188612[14] = delta_x[14] + nom_x[14];
   out_4130250514567188612[15] = delta_x[15] + nom_x[15];
   out_4130250514567188612[16] = delta_x[16] + nom_x[16];
   out_4130250514567188612[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_3862262940710197433) {
   out_3862262940710197433[0] = -nom_x[0] + true_x[0];
   out_3862262940710197433[1] = -nom_x[1] + true_x[1];
   out_3862262940710197433[2] = -nom_x[2] + true_x[2];
   out_3862262940710197433[3] = -nom_x[3] + true_x[3];
   out_3862262940710197433[4] = -nom_x[4] + true_x[4];
   out_3862262940710197433[5] = -nom_x[5] + true_x[5];
   out_3862262940710197433[6] = -nom_x[6] + true_x[6];
   out_3862262940710197433[7] = -nom_x[7] + true_x[7];
   out_3862262940710197433[8] = -nom_x[8] + true_x[8];
   out_3862262940710197433[9] = -nom_x[9] + true_x[9];
   out_3862262940710197433[10] = -nom_x[10] + true_x[10];
   out_3862262940710197433[11] = -nom_x[11] + true_x[11];
   out_3862262940710197433[12] = -nom_x[12] + true_x[12];
   out_3862262940710197433[13] = -nom_x[13] + true_x[13];
   out_3862262940710197433[14] = -nom_x[14] + true_x[14];
   out_3862262940710197433[15] = -nom_x[15] + true_x[15];
   out_3862262940710197433[16] = -nom_x[16] + true_x[16];
   out_3862262940710197433[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_7881665640335314858) {
   out_7881665640335314858[0] = 1.0;
   out_7881665640335314858[1] = 0.0;
   out_7881665640335314858[2] = 0.0;
   out_7881665640335314858[3] = 0.0;
   out_7881665640335314858[4] = 0.0;
   out_7881665640335314858[5] = 0.0;
   out_7881665640335314858[6] = 0.0;
   out_7881665640335314858[7] = 0.0;
   out_7881665640335314858[8] = 0.0;
   out_7881665640335314858[9] = 0.0;
   out_7881665640335314858[10] = 0.0;
   out_7881665640335314858[11] = 0.0;
   out_7881665640335314858[12] = 0.0;
   out_7881665640335314858[13] = 0.0;
   out_7881665640335314858[14] = 0.0;
   out_7881665640335314858[15] = 0.0;
   out_7881665640335314858[16] = 0.0;
   out_7881665640335314858[17] = 0.0;
   out_7881665640335314858[18] = 0.0;
   out_7881665640335314858[19] = 1.0;
   out_7881665640335314858[20] = 0.0;
   out_7881665640335314858[21] = 0.0;
   out_7881665640335314858[22] = 0.0;
   out_7881665640335314858[23] = 0.0;
   out_7881665640335314858[24] = 0.0;
   out_7881665640335314858[25] = 0.0;
   out_7881665640335314858[26] = 0.0;
   out_7881665640335314858[27] = 0.0;
   out_7881665640335314858[28] = 0.0;
   out_7881665640335314858[29] = 0.0;
   out_7881665640335314858[30] = 0.0;
   out_7881665640335314858[31] = 0.0;
   out_7881665640335314858[32] = 0.0;
   out_7881665640335314858[33] = 0.0;
   out_7881665640335314858[34] = 0.0;
   out_7881665640335314858[35] = 0.0;
   out_7881665640335314858[36] = 0.0;
   out_7881665640335314858[37] = 0.0;
   out_7881665640335314858[38] = 1.0;
   out_7881665640335314858[39] = 0.0;
   out_7881665640335314858[40] = 0.0;
   out_7881665640335314858[41] = 0.0;
   out_7881665640335314858[42] = 0.0;
   out_7881665640335314858[43] = 0.0;
   out_7881665640335314858[44] = 0.0;
   out_7881665640335314858[45] = 0.0;
   out_7881665640335314858[46] = 0.0;
   out_7881665640335314858[47] = 0.0;
   out_7881665640335314858[48] = 0.0;
   out_7881665640335314858[49] = 0.0;
   out_7881665640335314858[50] = 0.0;
   out_7881665640335314858[51] = 0.0;
   out_7881665640335314858[52] = 0.0;
   out_7881665640335314858[53] = 0.0;
   out_7881665640335314858[54] = 0.0;
   out_7881665640335314858[55] = 0.0;
   out_7881665640335314858[56] = 0.0;
   out_7881665640335314858[57] = 1.0;
   out_7881665640335314858[58] = 0.0;
   out_7881665640335314858[59] = 0.0;
   out_7881665640335314858[60] = 0.0;
   out_7881665640335314858[61] = 0.0;
   out_7881665640335314858[62] = 0.0;
   out_7881665640335314858[63] = 0.0;
   out_7881665640335314858[64] = 0.0;
   out_7881665640335314858[65] = 0.0;
   out_7881665640335314858[66] = 0.0;
   out_7881665640335314858[67] = 0.0;
   out_7881665640335314858[68] = 0.0;
   out_7881665640335314858[69] = 0.0;
   out_7881665640335314858[70] = 0.0;
   out_7881665640335314858[71] = 0.0;
   out_7881665640335314858[72] = 0.0;
   out_7881665640335314858[73] = 0.0;
   out_7881665640335314858[74] = 0.0;
   out_7881665640335314858[75] = 0.0;
   out_7881665640335314858[76] = 1.0;
   out_7881665640335314858[77] = 0.0;
   out_7881665640335314858[78] = 0.0;
   out_7881665640335314858[79] = 0.0;
   out_7881665640335314858[80] = 0.0;
   out_7881665640335314858[81] = 0.0;
   out_7881665640335314858[82] = 0.0;
   out_7881665640335314858[83] = 0.0;
   out_7881665640335314858[84] = 0.0;
   out_7881665640335314858[85] = 0.0;
   out_7881665640335314858[86] = 0.0;
   out_7881665640335314858[87] = 0.0;
   out_7881665640335314858[88] = 0.0;
   out_7881665640335314858[89] = 0.0;
   out_7881665640335314858[90] = 0.0;
   out_7881665640335314858[91] = 0.0;
   out_7881665640335314858[92] = 0.0;
   out_7881665640335314858[93] = 0.0;
   out_7881665640335314858[94] = 0.0;
   out_7881665640335314858[95] = 1.0;
   out_7881665640335314858[96] = 0.0;
   out_7881665640335314858[97] = 0.0;
   out_7881665640335314858[98] = 0.0;
   out_7881665640335314858[99] = 0.0;
   out_7881665640335314858[100] = 0.0;
   out_7881665640335314858[101] = 0.0;
   out_7881665640335314858[102] = 0.0;
   out_7881665640335314858[103] = 0.0;
   out_7881665640335314858[104] = 0.0;
   out_7881665640335314858[105] = 0.0;
   out_7881665640335314858[106] = 0.0;
   out_7881665640335314858[107] = 0.0;
   out_7881665640335314858[108] = 0.0;
   out_7881665640335314858[109] = 0.0;
   out_7881665640335314858[110] = 0.0;
   out_7881665640335314858[111] = 0.0;
   out_7881665640335314858[112] = 0.0;
   out_7881665640335314858[113] = 0.0;
   out_7881665640335314858[114] = 1.0;
   out_7881665640335314858[115] = 0.0;
   out_7881665640335314858[116] = 0.0;
   out_7881665640335314858[117] = 0.0;
   out_7881665640335314858[118] = 0.0;
   out_7881665640335314858[119] = 0.0;
   out_7881665640335314858[120] = 0.0;
   out_7881665640335314858[121] = 0.0;
   out_7881665640335314858[122] = 0.0;
   out_7881665640335314858[123] = 0.0;
   out_7881665640335314858[124] = 0.0;
   out_7881665640335314858[125] = 0.0;
   out_7881665640335314858[126] = 0.0;
   out_7881665640335314858[127] = 0.0;
   out_7881665640335314858[128] = 0.0;
   out_7881665640335314858[129] = 0.0;
   out_7881665640335314858[130] = 0.0;
   out_7881665640335314858[131] = 0.0;
   out_7881665640335314858[132] = 0.0;
   out_7881665640335314858[133] = 1.0;
   out_7881665640335314858[134] = 0.0;
   out_7881665640335314858[135] = 0.0;
   out_7881665640335314858[136] = 0.0;
   out_7881665640335314858[137] = 0.0;
   out_7881665640335314858[138] = 0.0;
   out_7881665640335314858[139] = 0.0;
   out_7881665640335314858[140] = 0.0;
   out_7881665640335314858[141] = 0.0;
   out_7881665640335314858[142] = 0.0;
   out_7881665640335314858[143] = 0.0;
   out_7881665640335314858[144] = 0.0;
   out_7881665640335314858[145] = 0.0;
   out_7881665640335314858[146] = 0.0;
   out_7881665640335314858[147] = 0.0;
   out_7881665640335314858[148] = 0.0;
   out_7881665640335314858[149] = 0.0;
   out_7881665640335314858[150] = 0.0;
   out_7881665640335314858[151] = 0.0;
   out_7881665640335314858[152] = 1.0;
   out_7881665640335314858[153] = 0.0;
   out_7881665640335314858[154] = 0.0;
   out_7881665640335314858[155] = 0.0;
   out_7881665640335314858[156] = 0.0;
   out_7881665640335314858[157] = 0.0;
   out_7881665640335314858[158] = 0.0;
   out_7881665640335314858[159] = 0.0;
   out_7881665640335314858[160] = 0.0;
   out_7881665640335314858[161] = 0.0;
   out_7881665640335314858[162] = 0.0;
   out_7881665640335314858[163] = 0.0;
   out_7881665640335314858[164] = 0.0;
   out_7881665640335314858[165] = 0.0;
   out_7881665640335314858[166] = 0.0;
   out_7881665640335314858[167] = 0.0;
   out_7881665640335314858[168] = 0.0;
   out_7881665640335314858[169] = 0.0;
   out_7881665640335314858[170] = 0.0;
   out_7881665640335314858[171] = 1.0;
   out_7881665640335314858[172] = 0.0;
   out_7881665640335314858[173] = 0.0;
   out_7881665640335314858[174] = 0.0;
   out_7881665640335314858[175] = 0.0;
   out_7881665640335314858[176] = 0.0;
   out_7881665640335314858[177] = 0.0;
   out_7881665640335314858[178] = 0.0;
   out_7881665640335314858[179] = 0.0;
   out_7881665640335314858[180] = 0.0;
   out_7881665640335314858[181] = 0.0;
   out_7881665640335314858[182] = 0.0;
   out_7881665640335314858[183] = 0.0;
   out_7881665640335314858[184] = 0.0;
   out_7881665640335314858[185] = 0.0;
   out_7881665640335314858[186] = 0.0;
   out_7881665640335314858[187] = 0.0;
   out_7881665640335314858[188] = 0.0;
   out_7881665640335314858[189] = 0.0;
   out_7881665640335314858[190] = 1.0;
   out_7881665640335314858[191] = 0.0;
   out_7881665640335314858[192] = 0.0;
   out_7881665640335314858[193] = 0.0;
   out_7881665640335314858[194] = 0.0;
   out_7881665640335314858[195] = 0.0;
   out_7881665640335314858[196] = 0.0;
   out_7881665640335314858[197] = 0.0;
   out_7881665640335314858[198] = 0.0;
   out_7881665640335314858[199] = 0.0;
   out_7881665640335314858[200] = 0.0;
   out_7881665640335314858[201] = 0.0;
   out_7881665640335314858[202] = 0.0;
   out_7881665640335314858[203] = 0.0;
   out_7881665640335314858[204] = 0.0;
   out_7881665640335314858[205] = 0.0;
   out_7881665640335314858[206] = 0.0;
   out_7881665640335314858[207] = 0.0;
   out_7881665640335314858[208] = 0.0;
   out_7881665640335314858[209] = 1.0;
   out_7881665640335314858[210] = 0.0;
   out_7881665640335314858[211] = 0.0;
   out_7881665640335314858[212] = 0.0;
   out_7881665640335314858[213] = 0.0;
   out_7881665640335314858[214] = 0.0;
   out_7881665640335314858[215] = 0.0;
   out_7881665640335314858[216] = 0.0;
   out_7881665640335314858[217] = 0.0;
   out_7881665640335314858[218] = 0.0;
   out_7881665640335314858[219] = 0.0;
   out_7881665640335314858[220] = 0.0;
   out_7881665640335314858[221] = 0.0;
   out_7881665640335314858[222] = 0.0;
   out_7881665640335314858[223] = 0.0;
   out_7881665640335314858[224] = 0.0;
   out_7881665640335314858[225] = 0.0;
   out_7881665640335314858[226] = 0.0;
   out_7881665640335314858[227] = 0.0;
   out_7881665640335314858[228] = 1.0;
   out_7881665640335314858[229] = 0.0;
   out_7881665640335314858[230] = 0.0;
   out_7881665640335314858[231] = 0.0;
   out_7881665640335314858[232] = 0.0;
   out_7881665640335314858[233] = 0.0;
   out_7881665640335314858[234] = 0.0;
   out_7881665640335314858[235] = 0.0;
   out_7881665640335314858[236] = 0.0;
   out_7881665640335314858[237] = 0.0;
   out_7881665640335314858[238] = 0.0;
   out_7881665640335314858[239] = 0.0;
   out_7881665640335314858[240] = 0.0;
   out_7881665640335314858[241] = 0.0;
   out_7881665640335314858[242] = 0.0;
   out_7881665640335314858[243] = 0.0;
   out_7881665640335314858[244] = 0.0;
   out_7881665640335314858[245] = 0.0;
   out_7881665640335314858[246] = 0.0;
   out_7881665640335314858[247] = 1.0;
   out_7881665640335314858[248] = 0.0;
   out_7881665640335314858[249] = 0.0;
   out_7881665640335314858[250] = 0.0;
   out_7881665640335314858[251] = 0.0;
   out_7881665640335314858[252] = 0.0;
   out_7881665640335314858[253] = 0.0;
   out_7881665640335314858[254] = 0.0;
   out_7881665640335314858[255] = 0.0;
   out_7881665640335314858[256] = 0.0;
   out_7881665640335314858[257] = 0.0;
   out_7881665640335314858[258] = 0.0;
   out_7881665640335314858[259] = 0.0;
   out_7881665640335314858[260] = 0.0;
   out_7881665640335314858[261] = 0.0;
   out_7881665640335314858[262] = 0.0;
   out_7881665640335314858[263] = 0.0;
   out_7881665640335314858[264] = 0.0;
   out_7881665640335314858[265] = 0.0;
   out_7881665640335314858[266] = 1.0;
   out_7881665640335314858[267] = 0.0;
   out_7881665640335314858[268] = 0.0;
   out_7881665640335314858[269] = 0.0;
   out_7881665640335314858[270] = 0.0;
   out_7881665640335314858[271] = 0.0;
   out_7881665640335314858[272] = 0.0;
   out_7881665640335314858[273] = 0.0;
   out_7881665640335314858[274] = 0.0;
   out_7881665640335314858[275] = 0.0;
   out_7881665640335314858[276] = 0.0;
   out_7881665640335314858[277] = 0.0;
   out_7881665640335314858[278] = 0.0;
   out_7881665640335314858[279] = 0.0;
   out_7881665640335314858[280] = 0.0;
   out_7881665640335314858[281] = 0.0;
   out_7881665640335314858[282] = 0.0;
   out_7881665640335314858[283] = 0.0;
   out_7881665640335314858[284] = 0.0;
   out_7881665640335314858[285] = 1.0;
   out_7881665640335314858[286] = 0.0;
   out_7881665640335314858[287] = 0.0;
   out_7881665640335314858[288] = 0.0;
   out_7881665640335314858[289] = 0.0;
   out_7881665640335314858[290] = 0.0;
   out_7881665640335314858[291] = 0.0;
   out_7881665640335314858[292] = 0.0;
   out_7881665640335314858[293] = 0.0;
   out_7881665640335314858[294] = 0.0;
   out_7881665640335314858[295] = 0.0;
   out_7881665640335314858[296] = 0.0;
   out_7881665640335314858[297] = 0.0;
   out_7881665640335314858[298] = 0.0;
   out_7881665640335314858[299] = 0.0;
   out_7881665640335314858[300] = 0.0;
   out_7881665640335314858[301] = 0.0;
   out_7881665640335314858[302] = 0.0;
   out_7881665640335314858[303] = 0.0;
   out_7881665640335314858[304] = 1.0;
   out_7881665640335314858[305] = 0.0;
   out_7881665640335314858[306] = 0.0;
   out_7881665640335314858[307] = 0.0;
   out_7881665640335314858[308] = 0.0;
   out_7881665640335314858[309] = 0.0;
   out_7881665640335314858[310] = 0.0;
   out_7881665640335314858[311] = 0.0;
   out_7881665640335314858[312] = 0.0;
   out_7881665640335314858[313] = 0.0;
   out_7881665640335314858[314] = 0.0;
   out_7881665640335314858[315] = 0.0;
   out_7881665640335314858[316] = 0.0;
   out_7881665640335314858[317] = 0.0;
   out_7881665640335314858[318] = 0.0;
   out_7881665640335314858[319] = 0.0;
   out_7881665640335314858[320] = 0.0;
   out_7881665640335314858[321] = 0.0;
   out_7881665640335314858[322] = 0.0;
   out_7881665640335314858[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_4623446334203055766) {
   out_4623446334203055766[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_4623446334203055766[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_4623446334203055766[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_4623446334203055766[3] = dt*state[12] + state[3];
   out_4623446334203055766[4] = dt*state[13] + state[4];
   out_4623446334203055766[5] = dt*state[14] + state[5];
   out_4623446334203055766[6] = state[6];
   out_4623446334203055766[7] = state[7];
   out_4623446334203055766[8] = state[8];
   out_4623446334203055766[9] = state[9];
   out_4623446334203055766[10] = state[10];
   out_4623446334203055766[11] = state[11];
   out_4623446334203055766[12] = state[12];
   out_4623446334203055766[13] = state[13];
   out_4623446334203055766[14] = state[14];
   out_4623446334203055766[15] = state[15];
   out_4623446334203055766[16] = state[16];
   out_4623446334203055766[17] = state[17];
}
void F_fun(double *state, double dt, double *out_4287027390918098086) {
   out_4287027390918098086[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4287027390918098086[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4287027390918098086[2] = 0;
   out_4287027390918098086[3] = 0;
   out_4287027390918098086[4] = 0;
   out_4287027390918098086[5] = 0;
   out_4287027390918098086[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4287027390918098086[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4287027390918098086[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4287027390918098086[9] = 0;
   out_4287027390918098086[10] = 0;
   out_4287027390918098086[11] = 0;
   out_4287027390918098086[12] = 0;
   out_4287027390918098086[13] = 0;
   out_4287027390918098086[14] = 0;
   out_4287027390918098086[15] = 0;
   out_4287027390918098086[16] = 0;
   out_4287027390918098086[17] = 0;
   out_4287027390918098086[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4287027390918098086[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4287027390918098086[20] = 0;
   out_4287027390918098086[21] = 0;
   out_4287027390918098086[22] = 0;
   out_4287027390918098086[23] = 0;
   out_4287027390918098086[24] = 0;
   out_4287027390918098086[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4287027390918098086[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4287027390918098086[27] = 0;
   out_4287027390918098086[28] = 0;
   out_4287027390918098086[29] = 0;
   out_4287027390918098086[30] = 0;
   out_4287027390918098086[31] = 0;
   out_4287027390918098086[32] = 0;
   out_4287027390918098086[33] = 0;
   out_4287027390918098086[34] = 0;
   out_4287027390918098086[35] = 0;
   out_4287027390918098086[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4287027390918098086[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4287027390918098086[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4287027390918098086[39] = 0;
   out_4287027390918098086[40] = 0;
   out_4287027390918098086[41] = 0;
   out_4287027390918098086[42] = 0;
   out_4287027390918098086[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4287027390918098086[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4287027390918098086[45] = 0;
   out_4287027390918098086[46] = 0;
   out_4287027390918098086[47] = 0;
   out_4287027390918098086[48] = 0;
   out_4287027390918098086[49] = 0;
   out_4287027390918098086[50] = 0;
   out_4287027390918098086[51] = 0;
   out_4287027390918098086[52] = 0;
   out_4287027390918098086[53] = 0;
   out_4287027390918098086[54] = 0;
   out_4287027390918098086[55] = 0;
   out_4287027390918098086[56] = 0;
   out_4287027390918098086[57] = 1;
   out_4287027390918098086[58] = 0;
   out_4287027390918098086[59] = 0;
   out_4287027390918098086[60] = 0;
   out_4287027390918098086[61] = 0;
   out_4287027390918098086[62] = 0;
   out_4287027390918098086[63] = 0;
   out_4287027390918098086[64] = 0;
   out_4287027390918098086[65] = 0;
   out_4287027390918098086[66] = dt;
   out_4287027390918098086[67] = 0;
   out_4287027390918098086[68] = 0;
   out_4287027390918098086[69] = 0;
   out_4287027390918098086[70] = 0;
   out_4287027390918098086[71] = 0;
   out_4287027390918098086[72] = 0;
   out_4287027390918098086[73] = 0;
   out_4287027390918098086[74] = 0;
   out_4287027390918098086[75] = 0;
   out_4287027390918098086[76] = 1;
   out_4287027390918098086[77] = 0;
   out_4287027390918098086[78] = 0;
   out_4287027390918098086[79] = 0;
   out_4287027390918098086[80] = 0;
   out_4287027390918098086[81] = 0;
   out_4287027390918098086[82] = 0;
   out_4287027390918098086[83] = 0;
   out_4287027390918098086[84] = 0;
   out_4287027390918098086[85] = dt;
   out_4287027390918098086[86] = 0;
   out_4287027390918098086[87] = 0;
   out_4287027390918098086[88] = 0;
   out_4287027390918098086[89] = 0;
   out_4287027390918098086[90] = 0;
   out_4287027390918098086[91] = 0;
   out_4287027390918098086[92] = 0;
   out_4287027390918098086[93] = 0;
   out_4287027390918098086[94] = 0;
   out_4287027390918098086[95] = 1;
   out_4287027390918098086[96] = 0;
   out_4287027390918098086[97] = 0;
   out_4287027390918098086[98] = 0;
   out_4287027390918098086[99] = 0;
   out_4287027390918098086[100] = 0;
   out_4287027390918098086[101] = 0;
   out_4287027390918098086[102] = 0;
   out_4287027390918098086[103] = 0;
   out_4287027390918098086[104] = dt;
   out_4287027390918098086[105] = 0;
   out_4287027390918098086[106] = 0;
   out_4287027390918098086[107] = 0;
   out_4287027390918098086[108] = 0;
   out_4287027390918098086[109] = 0;
   out_4287027390918098086[110] = 0;
   out_4287027390918098086[111] = 0;
   out_4287027390918098086[112] = 0;
   out_4287027390918098086[113] = 0;
   out_4287027390918098086[114] = 1;
   out_4287027390918098086[115] = 0;
   out_4287027390918098086[116] = 0;
   out_4287027390918098086[117] = 0;
   out_4287027390918098086[118] = 0;
   out_4287027390918098086[119] = 0;
   out_4287027390918098086[120] = 0;
   out_4287027390918098086[121] = 0;
   out_4287027390918098086[122] = 0;
   out_4287027390918098086[123] = 0;
   out_4287027390918098086[124] = 0;
   out_4287027390918098086[125] = 0;
   out_4287027390918098086[126] = 0;
   out_4287027390918098086[127] = 0;
   out_4287027390918098086[128] = 0;
   out_4287027390918098086[129] = 0;
   out_4287027390918098086[130] = 0;
   out_4287027390918098086[131] = 0;
   out_4287027390918098086[132] = 0;
   out_4287027390918098086[133] = 1;
   out_4287027390918098086[134] = 0;
   out_4287027390918098086[135] = 0;
   out_4287027390918098086[136] = 0;
   out_4287027390918098086[137] = 0;
   out_4287027390918098086[138] = 0;
   out_4287027390918098086[139] = 0;
   out_4287027390918098086[140] = 0;
   out_4287027390918098086[141] = 0;
   out_4287027390918098086[142] = 0;
   out_4287027390918098086[143] = 0;
   out_4287027390918098086[144] = 0;
   out_4287027390918098086[145] = 0;
   out_4287027390918098086[146] = 0;
   out_4287027390918098086[147] = 0;
   out_4287027390918098086[148] = 0;
   out_4287027390918098086[149] = 0;
   out_4287027390918098086[150] = 0;
   out_4287027390918098086[151] = 0;
   out_4287027390918098086[152] = 1;
   out_4287027390918098086[153] = 0;
   out_4287027390918098086[154] = 0;
   out_4287027390918098086[155] = 0;
   out_4287027390918098086[156] = 0;
   out_4287027390918098086[157] = 0;
   out_4287027390918098086[158] = 0;
   out_4287027390918098086[159] = 0;
   out_4287027390918098086[160] = 0;
   out_4287027390918098086[161] = 0;
   out_4287027390918098086[162] = 0;
   out_4287027390918098086[163] = 0;
   out_4287027390918098086[164] = 0;
   out_4287027390918098086[165] = 0;
   out_4287027390918098086[166] = 0;
   out_4287027390918098086[167] = 0;
   out_4287027390918098086[168] = 0;
   out_4287027390918098086[169] = 0;
   out_4287027390918098086[170] = 0;
   out_4287027390918098086[171] = 1;
   out_4287027390918098086[172] = 0;
   out_4287027390918098086[173] = 0;
   out_4287027390918098086[174] = 0;
   out_4287027390918098086[175] = 0;
   out_4287027390918098086[176] = 0;
   out_4287027390918098086[177] = 0;
   out_4287027390918098086[178] = 0;
   out_4287027390918098086[179] = 0;
   out_4287027390918098086[180] = 0;
   out_4287027390918098086[181] = 0;
   out_4287027390918098086[182] = 0;
   out_4287027390918098086[183] = 0;
   out_4287027390918098086[184] = 0;
   out_4287027390918098086[185] = 0;
   out_4287027390918098086[186] = 0;
   out_4287027390918098086[187] = 0;
   out_4287027390918098086[188] = 0;
   out_4287027390918098086[189] = 0;
   out_4287027390918098086[190] = 1;
   out_4287027390918098086[191] = 0;
   out_4287027390918098086[192] = 0;
   out_4287027390918098086[193] = 0;
   out_4287027390918098086[194] = 0;
   out_4287027390918098086[195] = 0;
   out_4287027390918098086[196] = 0;
   out_4287027390918098086[197] = 0;
   out_4287027390918098086[198] = 0;
   out_4287027390918098086[199] = 0;
   out_4287027390918098086[200] = 0;
   out_4287027390918098086[201] = 0;
   out_4287027390918098086[202] = 0;
   out_4287027390918098086[203] = 0;
   out_4287027390918098086[204] = 0;
   out_4287027390918098086[205] = 0;
   out_4287027390918098086[206] = 0;
   out_4287027390918098086[207] = 0;
   out_4287027390918098086[208] = 0;
   out_4287027390918098086[209] = 1;
   out_4287027390918098086[210] = 0;
   out_4287027390918098086[211] = 0;
   out_4287027390918098086[212] = 0;
   out_4287027390918098086[213] = 0;
   out_4287027390918098086[214] = 0;
   out_4287027390918098086[215] = 0;
   out_4287027390918098086[216] = 0;
   out_4287027390918098086[217] = 0;
   out_4287027390918098086[218] = 0;
   out_4287027390918098086[219] = 0;
   out_4287027390918098086[220] = 0;
   out_4287027390918098086[221] = 0;
   out_4287027390918098086[222] = 0;
   out_4287027390918098086[223] = 0;
   out_4287027390918098086[224] = 0;
   out_4287027390918098086[225] = 0;
   out_4287027390918098086[226] = 0;
   out_4287027390918098086[227] = 0;
   out_4287027390918098086[228] = 1;
   out_4287027390918098086[229] = 0;
   out_4287027390918098086[230] = 0;
   out_4287027390918098086[231] = 0;
   out_4287027390918098086[232] = 0;
   out_4287027390918098086[233] = 0;
   out_4287027390918098086[234] = 0;
   out_4287027390918098086[235] = 0;
   out_4287027390918098086[236] = 0;
   out_4287027390918098086[237] = 0;
   out_4287027390918098086[238] = 0;
   out_4287027390918098086[239] = 0;
   out_4287027390918098086[240] = 0;
   out_4287027390918098086[241] = 0;
   out_4287027390918098086[242] = 0;
   out_4287027390918098086[243] = 0;
   out_4287027390918098086[244] = 0;
   out_4287027390918098086[245] = 0;
   out_4287027390918098086[246] = 0;
   out_4287027390918098086[247] = 1;
   out_4287027390918098086[248] = 0;
   out_4287027390918098086[249] = 0;
   out_4287027390918098086[250] = 0;
   out_4287027390918098086[251] = 0;
   out_4287027390918098086[252] = 0;
   out_4287027390918098086[253] = 0;
   out_4287027390918098086[254] = 0;
   out_4287027390918098086[255] = 0;
   out_4287027390918098086[256] = 0;
   out_4287027390918098086[257] = 0;
   out_4287027390918098086[258] = 0;
   out_4287027390918098086[259] = 0;
   out_4287027390918098086[260] = 0;
   out_4287027390918098086[261] = 0;
   out_4287027390918098086[262] = 0;
   out_4287027390918098086[263] = 0;
   out_4287027390918098086[264] = 0;
   out_4287027390918098086[265] = 0;
   out_4287027390918098086[266] = 1;
   out_4287027390918098086[267] = 0;
   out_4287027390918098086[268] = 0;
   out_4287027390918098086[269] = 0;
   out_4287027390918098086[270] = 0;
   out_4287027390918098086[271] = 0;
   out_4287027390918098086[272] = 0;
   out_4287027390918098086[273] = 0;
   out_4287027390918098086[274] = 0;
   out_4287027390918098086[275] = 0;
   out_4287027390918098086[276] = 0;
   out_4287027390918098086[277] = 0;
   out_4287027390918098086[278] = 0;
   out_4287027390918098086[279] = 0;
   out_4287027390918098086[280] = 0;
   out_4287027390918098086[281] = 0;
   out_4287027390918098086[282] = 0;
   out_4287027390918098086[283] = 0;
   out_4287027390918098086[284] = 0;
   out_4287027390918098086[285] = 1;
   out_4287027390918098086[286] = 0;
   out_4287027390918098086[287] = 0;
   out_4287027390918098086[288] = 0;
   out_4287027390918098086[289] = 0;
   out_4287027390918098086[290] = 0;
   out_4287027390918098086[291] = 0;
   out_4287027390918098086[292] = 0;
   out_4287027390918098086[293] = 0;
   out_4287027390918098086[294] = 0;
   out_4287027390918098086[295] = 0;
   out_4287027390918098086[296] = 0;
   out_4287027390918098086[297] = 0;
   out_4287027390918098086[298] = 0;
   out_4287027390918098086[299] = 0;
   out_4287027390918098086[300] = 0;
   out_4287027390918098086[301] = 0;
   out_4287027390918098086[302] = 0;
   out_4287027390918098086[303] = 0;
   out_4287027390918098086[304] = 1;
   out_4287027390918098086[305] = 0;
   out_4287027390918098086[306] = 0;
   out_4287027390918098086[307] = 0;
   out_4287027390918098086[308] = 0;
   out_4287027390918098086[309] = 0;
   out_4287027390918098086[310] = 0;
   out_4287027390918098086[311] = 0;
   out_4287027390918098086[312] = 0;
   out_4287027390918098086[313] = 0;
   out_4287027390918098086[314] = 0;
   out_4287027390918098086[315] = 0;
   out_4287027390918098086[316] = 0;
   out_4287027390918098086[317] = 0;
   out_4287027390918098086[318] = 0;
   out_4287027390918098086[319] = 0;
   out_4287027390918098086[320] = 0;
   out_4287027390918098086[321] = 0;
   out_4287027390918098086[322] = 0;
   out_4287027390918098086[323] = 1;
}
void h_4(double *state, double *unused, double *out_2134370447906294768) {
   out_2134370447906294768[0] = state[6] + state[9];
   out_2134370447906294768[1] = state[7] + state[10];
   out_2134370447906294768[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_8745379707467939897) {
   out_8745379707467939897[0] = 0;
   out_8745379707467939897[1] = 0;
   out_8745379707467939897[2] = 0;
   out_8745379707467939897[3] = 0;
   out_8745379707467939897[4] = 0;
   out_8745379707467939897[5] = 0;
   out_8745379707467939897[6] = 1;
   out_8745379707467939897[7] = 0;
   out_8745379707467939897[8] = 0;
   out_8745379707467939897[9] = 1;
   out_8745379707467939897[10] = 0;
   out_8745379707467939897[11] = 0;
   out_8745379707467939897[12] = 0;
   out_8745379707467939897[13] = 0;
   out_8745379707467939897[14] = 0;
   out_8745379707467939897[15] = 0;
   out_8745379707467939897[16] = 0;
   out_8745379707467939897[17] = 0;
   out_8745379707467939897[18] = 0;
   out_8745379707467939897[19] = 0;
   out_8745379707467939897[20] = 0;
   out_8745379707467939897[21] = 0;
   out_8745379707467939897[22] = 0;
   out_8745379707467939897[23] = 0;
   out_8745379707467939897[24] = 0;
   out_8745379707467939897[25] = 1;
   out_8745379707467939897[26] = 0;
   out_8745379707467939897[27] = 0;
   out_8745379707467939897[28] = 1;
   out_8745379707467939897[29] = 0;
   out_8745379707467939897[30] = 0;
   out_8745379707467939897[31] = 0;
   out_8745379707467939897[32] = 0;
   out_8745379707467939897[33] = 0;
   out_8745379707467939897[34] = 0;
   out_8745379707467939897[35] = 0;
   out_8745379707467939897[36] = 0;
   out_8745379707467939897[37] = 0;
   out_8745379707467939897[38] = 0;
   out_8745379707467939897[39] = 0;
   out_8745379707467939897[40] = 0;
   out_8745379707467939897[41] = 0;
   out_8745379707467939897[42] = 0;
   out_8745379707467939897[43] = 0;
   out_8745379707467939897[44] = 1;
   out_8745379707467939897[45] = 0;
   out_8745379707467939897[46] = 0;
   out_8745379707467939897[47] = 1;
   out_8745379707467939897[48] = 0;
   out_8745379707467939897[49] = 0;
   out_8745379707467939897[50] = 0;
   out_8745379707467939897[51] = 0;
   out_8745379707467939897[52] = 0;
   out_8745379707467939897[53] = 0;
}
void h_10(double *state, double *unused, double *out_7905342496395142587) {
   out_7905342496395142587[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_7905342496395142587[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_7905342496395142587[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_1049153498394893392) {
   out_1049153498394893392[0] = 0;
   out_1049153498394893392[1] = 9.8100000000000005*cos(state[1]);
   out_1049153498394893392[2] = 0;
   out_1049153498394893392[3] = 0;
   out_1049153498394893392[4] = -state[8];
   out_1049153498394893392[5] = state[7];
   out_1049153498394893392[6] = 0;
   out_1049153498394893392[7] = state[5];
   out_1049153498394893392[8] = -state[4];
   out_1049153498394893392[9] = 0;
   out_1049153498394893392[10] = 0;
   out_1049153498394893392[11] = 0;
   out_1049153498394893392[12] = 1;
   out_1049153498394893392[13] = 0;
   out_1049153498394893392[14] = 0;
   out_1049153498394893392[15] = 1;
   out_1049153498394893392[16] = 0;
   out_1049153498394893392[17] = 0;
   out_1049153498394893392[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_1049153498394893392[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_1049153498394893392[20] = 0;
   out_1049153498394893392[21] = state[8];
   out_1049153498394893392[22] = 0;
   out_1049153498394893392[23] = -state[6];
   out_1049153498394893392[24] = -state[5];
   out_1049153498394893392[25] = 0;
   out_1049153498394893392[26] = state[3];
   out_1049153498394893392[27] = 0;
   out_1049153498394893392[28] = 0;
   out_1049153498394893392[29] = 0;
   out_1049153498394893392[30] = 0;
   out_1049153498394893392[31] = 1;
   out_1049153498394893392[32] = 0;
   out_1049153498394893392[33] = 0;
   out_1049153498394893392[34] = 1;
   out_1049153498394893392[35] = 0;
   out_1049153498394893392[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_1049153498394893392[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_1049153498394893392[38] = 0;
   out_1049153498394893392[39] = -state[7];
   out_1049153498394893392[40] = state[6];
   out_1049153498394893392[41] = 0;
   out_1049153498394893392[42] = state[4];
   out_1049153498394893392[43] = -state[3];
   out_1049153498394893392[44] = 0;
   out_1049153498394893392[45] = 0;
   out_1049153498394893392[46] = 0;
   out_1049153498394893392[47] = 0;
   out_1049153498394893392[48] = 0;
   out_1049153498394893392[49] = 0;
   out_1049153498394893392[50] = 1;
   out_1049153498394893392[51] = 0;
   out_1049153498394893392[52] = 0;
   out_1049153498394893392[53] = 1;
}
void h_13(double *state, double *unused, double *out_7764029234789399873) {
   out_7764029234789399873[0] = state[3];
   out_7764029234789399873[1] = state[4];
   out_7764029234789399873[2] = state[5];
}
void H_13(double *state, double *unused, double *out_6489090540909278918) {
   out_6489090540909278918[0] = 0;
   out_6489090540909278918[1] = 0;
   out_6489090540909278918[2] = 0;
   out_6489090540909278918[3] = 1;
   out_6489090540909278918[4] = 0;
   out_6489090540909278918[5] = 0;
   out_6489090540909278918[6] = 0;
   out_6489090540909278918[7] = 0;
   out_6489090540909278918[8] = 0;
   out_6489090540909278918[9] = 0;
   out_6489090540909278918[10] = 0;
   out_6489090540909278918[11] = 0;
   out_6489090540909278918[12] = 0;
   out_6489090540909278918[13] = 0;
   out_6489090540909278918[14] = 0;
   out_6489090540909278918[15] = 0;
   out_6489090540909278918[16] = 0;
   out_6489090540909278918[17] = 0;
   out_6489090540909278918[18] = 0;
   out_6489090540909278918[19] = 0;
   out_6489090540909278918[20] = 0;
   out_6489090540909278918[21] = 0;
   out_6489090540909278918[22] = 1;
   out_6489090540909278918[23] = 0;
   out_6489090540909278918[24] = 0;
   out_6489090540909278918[25] = 0;
   out_6489090540909278918[26] = 0;
   out_6489090540909278918[27] = 0;
   out_6489090540909278918[28] = 0;
   out_6489090540909278918[29] = 0;
   out_6489090540909278918[30] = 0;
   out_6489090540909278918[31] = 0;
   out_6489090540909278918[32] = 0;
   out_6489090540909278918[33] = 0;
   out_6489090540909278918[34] = 0;
   out_6489090540909278918[35] = 0;
   out_6489090540909278918[36] = 0;
   out_6489090540909278918[37] = 0;
   out_6489090540909278918[38] = 0;
   out_6489090540909278918[39] = 0;
   out_6489090540909278918[40] = 0;
   out_6489090540909278918[41] = 1;
   out_6489090540909278918[42] = 0;
   out_6489090540909278918[43] = 0;
   out_6489090540909278918[44] = 0;
   out_6489090540909278918[45] = 0;
   out_6489090540909278918[46] = 0;
   out_6489090540909278918[47] = 0;
   out_6489090540909278918[48] = 0;
   out_6489090540909278918[49] = 0;
   out_6489090540909278918[50] = 0;
   out_6489090540909278918[51] = 0;
   out_6489090540909278918[52] = 0;
   out_6489090540909278918[53] = 0;
}
void h_14(double *state, double *unused, double *out_719626587722978942) {
   out_719626587722978942[0] = state[6];
   out_719626587722978942[1] = state[7];
   out_719626587722978942[2] = state[8];
}
void H_14(double *state, double *unused, double *out_5738123509902127190) {
   out_5738123509902127190[0] = 0;
   out_5738123509902127190[1] = 0;
   out_5738123509902127190[2] = 0;
   out_5738123509902127190[3] = 0;
   out_5738123509902127190[4] = 0;
   out_5738123509902127190[5] = 0;
   out_5738123509902127190[6] = 1;
   out_5738123509902127190[7] = 0;
   out_5738123509902127190[8] = 0;
   out_5738123509902127190[9] = 0;
   out_5738123509902127190[10] = 0;
   out_5738123509902127190[11] = 0;
   out_5738123509902127190[12] = 0;
   out_5738123509902127190[13] = 0;
   out_5738123509902127190[14] = 0;
   out_5738123509902127190[15] = 0;
   out_5738123509902127190[16] = 0;
   out_5738123509902127190[17] = 0;
   out_5738123509902127190[18] = 0;
   out_5738123509902127190[19] = 0;
   out_5738123509902127190[20] = 0;
   out_5738123509902127190[21] = 0;
   out_5738123509902127190[22] = 0;
   out_5738123509902127190[23] = 0;
   out_5738123509902127190[24] = 0;
   out_5738123509902127190[25] = 1;
   out_5738123509902127190[26] = 0;
   out_5738123509902127190[27] = 0;
   out_5738123509902127190[28] = 0;
   out_5738123509902127190[29] = 0;
   out_5738123509902127190[30] = 0;
   out_5738123509902127190[31] = 0;
   out_5738123509902127190[32] = 0;
   out_5738123509902127190[33] = 0;
   out_5738123509902127190[34] = 0;
   out_5738123509902127190[35] = 0;
   out_5738123509902127190[36] = 0;
   out_5738123509902127190[37] = 0;
   out_5738123509902127190[38] = 0;
   out_5738123509902127190[39] = 0;
   out_5738123509902127190[40] = 0;
   out_5738123509902127190[41] = 0;
   out_5738123509902127190[42] = 0;
   out_5738123509902127190[43] = 0;
   out_5738123509902127190[44] = 1;
   out_5738123509902127190[45] = 0;
   out_5738123509902127190[46] = 0;
   out_5738123509902127190[47] = 0;
   out_5738123509902127190[48] = 0;
   out_5738123509902127190[49] = 0;
   out_5738123509902127190[50] = 0;
   out_5738123509902127190[51] = 0;
   out_5738123509902127190[52] = 0;
   out_5738123509902127190[53] = 0;
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

void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_4, H_4, NULL, in_z, in_R, in_ea, MAHA_THRESH_4);
}
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_10, H_10, NULL, in_z, in_R, in_ea, MAHA_THRESH_10);
}
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_13, H_13, NULL, in_z, in_R, in_ea, MAHA_THRESH_13);
}
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_14, H_14, NULL, in_z, in_R, in_ea, MAHA_THRESH_14);
}
void pose_err_fun(double *nom_x, double *delta_x, double *out_4130250514567188612) {
  err_fun(nom_x, delta_x, out_4130250514567188612);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_3862262940710197433) {
  inv_err_fun(nom_x, true_x, out_3862262940710197433);
}
void pose_H_mod_fun(double *state, double *out_7881665640335314858) {
  H_mod_fun(state, out_7881665640335314858);
}
void pose_f_fun(double *state, double dt, double *out_4623446334203055766) {
  f_fun(state,  dt, out_4623446334203055766);
}
void pose_F_fun(double *state, double dt, double *out_4287027390918098086) {
  F_fun(state,  dt, out_4287027390918098086);
}
void pose_h_4(double *state, double *unused, double *out_2134370447906294768) {
  h_4(state, unused, out_2134370447906294768);
}
void pose_H_4(double *state, double *unused, double *out_8745379707467939897) {
  H_4(state, unused, out_8745379707467939897);
}
void pose_h_10(double *state, double *unused, double *out_7905342496395142587) {
  h_10(state, unused, out_7905342496395142587);
}
void pose_H_10(double *state, double *unused, double *out_1049153498394893392) {
  H_10(state, unused, out_1049153498394893392);
}
void pose_h_13(double *state, double *unused, double *out_7764029234789399873) {
  h_13(state, unused, out_7764029234789399873);
}
void pose_H_13(double *state, double *unused, double *out_6489090540909278918) {
  H_13(state, unused, out_6489090540909278918);
}
void pose_h_14(double *state, double *unused, double *out_719626587722978942) {
  h_14(state, unused, out_719626587722978942);
}
void pose_H_14(double *state, double *unused, double *out_5738123509902127190) {
  H_14(state, unused, out_5738123509902127190);
}
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt) {
  predict(in_x, in_P, in_Q, dt);
}
}

const EKF pose = {
  .name = "pose",
  .kinds = { 4, 10, 13, 14 },
  .feature_kinds = {  },
  .f_fun = pose_f_fun,
  .F_fun = pose_F_fun,
  .err_fun = pose_err_fun,
  .inv_err_fun = pose_inv_err_fun,
  .H_mod_fun = pose_H_mod_fun,
  .predict = pose_predict,
  .hs = {
    { 4, pose_h_4 },
    { 10, pose_h_10 },
    { 13, pose_h_13 },
    { 14, pose_h_14 },
  },
  .Hs = {
    { 4, pose_H_4 },
    { 10, pose_H_10 },
    { 13, pose_H_13 },
    { 14, pose_H_14 },
  },
  .updates = {
    { 4, pose_update_4 },
    { 10, pose_update_10 },
    { 13, pose_update_13 },
    { 14, pose_update_14 },
  },
  .Hes = {
  },
  .sets = {
  },
  .extra_routines = {
  },
};

ekf_lib_init(pose)
