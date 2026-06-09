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
void err_fun(double *nom_x, double *delta_x, double *out_3209558036827677652) {
   out_3209558036827677652[0] = delta_x[0] + nom_x[0];
   out_3209558036827677652[1] = delta_x[1] + nom_x[1];
   out_3209558036827677652[2] = delta_x[2] + nom_x[2];
   out_3209558036827677652[3] = delta_x[3] + nom_x[3];
   out_3209558036827677652[4] = delta_x[4] + nom_x[4];
   out_3209558036827677652[5] = delta_x[5] + nom_x[5];
   out_3209558036827677652[6] = delta_x[6] + nom_x[6];
   out_3209558036827677652[7] = delta_x[7] + nom_x[7];
   out_3209558036827677652[8] = delta_x[8] + nom_x[8];
   out_3209558036827677652[9] = delta_x[9] + nom_x[9];
   out_3209558036827677652[10] = delta_x[10] + nom_x[10];
   out_3209558036827677652[11] = delta_x[11] + nom_x[11];
   out_3209558036827677652[12] = delta_x[12] + nom_x[12];
   out_3209558036827677652[13] = delta_x[13] + nom_x[13];
   out_3209558036827677652[14] = delta_x[14] + nom_x[14];
   out_3209558036827677652[15] = delta_x[15] + nom_x[15];
   out_3209558036827677652[16] = delta_x[16] + nom_x[16];
   out_3209558036827677652[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5101632267130187312) {
   out_5101632267130187312[0] = -nom_x[0] + true_x[0];
   out_5101632267130187312[1] = -nom_x[1] + true_x[1];
   out_5101632267130187312[2] = -nom_x[2] + true_x[2];
   out_5101632267130187312[3] = -nom_x[3] + true_x[3];
   out_5101632267130187312[4] = -nom_x[4] + true_x[4];
   out_5101632267130187312[5] = -nom_x[5] + true_x[5];
   out_5101632267130187312[6] = -nom_x[6] + true_x[6];
   out_5101632267130187312[7] = -nom_x[7] + true_x[7];
   out_5101632267130187312[8] = -nom_x[8] + true_x[8];
   out_5101632267130187312[9] = -nom_x[9] + true_x[9];
   out_5101632267130187312[10] = -nom_x[10] + true_x[10];
   out_5101632267130187312[11] = -nom_x[11] + true_x[11];
   out_5101632267130187312[12] = -nom_x[12] + true_x[12];
   out_5101632267130187312[13] = -nom_x[13] + true_x[13];
   out_5101632267130187312[14] = -nom_x[14] + true_x[14];
   out_5101632267130187312[15] = -nom_x[15] + true_x[15];
   out_5101632267130187312[16] = -nom_x[16] + true_x[16];
   out_5101632267130187312[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_8780343526186803252) {
   out_8780343526186803252[0] = 1.0;
   out_8780343526186803252[1] = 0.0;
   out_8780343526186803252[2] = 0.0;
   out_8780343526186803252[3] = 0.0;
   out_8780343526186803252[4] = 0.0;
   out_8780343526186803252[5] = 0.0;
   out_8780343526186803252[6] = 0.0;
   out_8780343526186803252[7] = 0.0;
   out_8780343526186803252[8] = 0.0;
   out_8780343526186803252[9] = 0.0;
   out_8780343526186803252[10] = 0.0;
   out_8780343526186803252[11] = 0.0;
   out_8780343526186803252[12] = 0.0;
   out_8780343526186803252[13] = 0.0;
   out_8780343526186803252[14] = 0.0;
   out_8780343526186803252[15] = 0.0;
   out_8780343526186803252[16] = 0.0;
   out_8780343526186803252[17] = 0.0;
   out_8780343526186803252[18] = 0.0;
   out_8780343526186803252[19] = 1.0;
   out_8780343526186803252[20] = 0.0;
   out_8780343526186803252[21] = 0.0;
   out_8780343526186803252[22] = 0.0;
   out_8780343526186803252[23] = 0.0;
   out_8780343526186803252[24] = 0.0;
   out_8780343526186803252[25] = 0.0;
   out_8780343526186803252[26] = 0.0;
   out_8780343526186803252[27] = 0.0;
   out_8780343526186803252[28] = 0.0;
   out_8780343526186803252[29] = 0.0;
   out_8780343526186803252[30] = 0.0;
   out_8780343526186803252[31] = 0.0;
   out_8780343526186803252[32] = 0.0;
   out_8780343526186803252[33] = 0.0;
   out_8780343526186803252[34] = 0.0;
   out_8780343526186803252[35] = 0.0;
   out_8780343526186803252[36] = 0.0;
   out_8780343526186803252[37] = 0.0;
   out_8780343526186803252[38] = 1.0;
   out_8780343526186803252[39] = 0.0;
   out_8780343526186803252[40] = 0.0;
   out_8780343526186803252[41] = 0.0;
   out_8780343526186803252[42] = 0.0;
   out_8780343526186803252[43] = 0.0;
   out_8780343526186803252[44] = 0.0;
   out_8780343526186803252[45] = 0.0;
   out_8780343526186803252[46] = 0.0;
   out_8780343526186803252[47] = 0.0;
   out_8780343526186803252[48] = 0.0;
   out_8780343526186803252[49] = 0.0;
   out_8780343526186803252[50] = 0.0;
   out_8780343526186803252[51] = 0.0;
   out_8780343526186803252[52] = 0.0;
   out_8780343526186803252[53] = 0.0;
   out_8780343526186803252[54] = 0.0;
   out_8780343526186803252[55] = 0.0;
   out_8780343526186803252[56] = 0.0;
   out_8780343526186803252[57] = 1.0;
   out_8780343526186803252[58] = 0.0;
   out_8780343526186803252[59] = 0.0;
   out_8780343526186803252[60] = 0.0;
   out_8780343526186803252[61] = 0.0;
   out_8780343526186803252[62] = 0.0;
   out_8780343526186803252[63] = 0.0;
   out_8780343526186803252[64] = 0.0;
   out_8780343526186803252[65] = 0.0;
   out_8780343526186803252[66] = 0.0;
   out_8780343526186803252[67] = 0.0;
   out_8780343526186803252[68] = 0.0;
   out_8780343526186803252[69] = 0.0;
   out_8780343526186803252[70] = 0.0;
   out_8780343526186803252[71] = 0.0;
   out_8780343526186803252[72] = 0.0;
   out_8780343526186803252[73] = 0.0;
   out_8780343526186803252[74] = 0.0;
   out_8780343526186803252[75] = 0.0;
   out_8780343526186803252[76] = 1.0;
   out_8780343526186803252[77] = 0.0;
   out_8780343526186803252[78] = 0.0;
   out_8780343526186803252[79] = 0.0;
   out_8780343526186803252[80] = 0.0;
   out_8780343526186803252[81] = 0.0;
   out_8780343526186803252[82] = 0.0;
   out_8780343526186803252[83] = 0.0;
   out_8780343526186803252[84] = 0.0;
   out_8780343526186803252[85] = 0.0;
   out_8780343526186803252[86] = 0.0;
   out_8780343526186803252[87] = 0.0;
   out_8780343526186803252[88] = 0.0;
   out_8780343526186803252[89] = 0.0;
   out_8780343526186803252[90] = 0.0;
   out_8780343526186803252[91] = 0.0;
   out_8780343526186803252[92] = 0.0;
   out_8780343526186803252[93] = 0.0;
   out_8780343526186803252[94] = 0.0;
   out_8780343526186803252[95] = 1.0;
   out_8780343526186803252[96] = 0.0;
   out_8780343526186803252[97] = 0.0;
   out_8780343526186803252[98] = 0.0;
   out_8780343526186803252[99] = 0.0;
   out_8780343526186803252[100] = 0.0;
   out_8780343526186803252[101] = 0.0;
   out_8780343526186803252[102] = 0.0;
   out_8780343526186803252[103] = 0.0;
   out_8780343526186803252[104] = 0.0;
   out_8780343526186803252[105] = 0.0;
   out_8780343526186803252[106] = 0.0;
   out_8780343526186803252[107] = 0.0;
   out_8780343526186803252[108] = 0.0;
   out_8780343526186803252[109] = 0.0;
   out_8780343526186803252[110] = 0.0;
   out_8780343526186803252[111] = 0.0;
   out_8780343526186803252[112] = 0.0;
   out_8780343526186803252[113] = 0.0;
   out_8780343526186803252[114] = 1.0;
   out_8780343526186803252[115] = 0.0;
   out_8780343526186803252[116] = 0.0;
   out_8780343526186803252[117] = 0.0;
   out_8780343526186803252[118] = 0.0;
   out_8780343526186803252[119] = 0.0;
   out_8780343526186803252[120] = 0.0;
   out_8780343526186803252[121] = 0.0;
   out_8780343526186803252[122] = 0.0;
   out_8780343526186803252[123] = 0.0;
   out_8780343526186803252[124] = 0.0;
   out_8780343526186803252[125] = 0.0;
   out_8780343526186803252[126] = 0.0;
   out_8780343526186803252[127] = 0.0;
   out_8780343526186803252[128] = 0.0;
   out_8780343526186803252[129] = 0.0;
   out_8780343526186803252[130] = 0.0;
   out_8780343526186803252[131] = 0.0;
   out_8780343526186803252[132] = 0.0;
   out_8780343526186803252[133] = 1.0;
   out_8780343526186803252[134] = 0.0;
   out_8780343526186803252[135] = 0.0;
   out_8780343526186803252[136] = 0.0;
   out_8780343526186803252[137] = 0.0;
   out_8780343526186803252[138] = 0.0;
   out_8780343526186803252[139] = 0.0;
   out_8780343526186803252[140] = 0.0;
   out_8780343526186803252[141] = 0.0;
   out_8780343526186803252[142] = 0.0;
   out_8780343526186803252[143] = 0.0;
   out_8780343526186803252[144] = 0.0;
   out_8780343526186803252[145] = 0.0;
   out_8780343526186803252[146] = 0.0;
   out_8780343526186803252[147] = 0.0;
   out_8780343526186803252[148] = 0.0;
   out_8780343526186803252[149] = 0.0;
   out_8780343526186803252[150] = 0.0;
   out_8780343526186803252[151] = 0.0;
   out_8780343526186803252[152] = 1.0;
   out_8780343526186803252[153] = 0.0;
   out_8780343526186803252[154] = 0.0;
   out_8780343526186803252[155] = 0.0;
   out_8780343526186803252[156] = 0.0;
   out_8780343526186803252[157] = 0.0;
   out_8780343526186803252[158] = 0.0;
   out_8780343526186803252[159] = 0.0;
   out_8780343526186803252[160] = 0.0;
   out_8780343526186803252[161] = 0.0;
   out_8780343526186803252[162] = 0.0;
   out_8780343526186803252[163] = 0.0;
   out_8780343526186803252[164] = 0.0;
   out_8780343526186803252[165] = 0.0;
   out_8780343526186803252[166] = 0.0;
   out_8780343526186803252[167] = 0.0;
   out_8780343526186803252[168] = 0.0;
   out_8780343526186803252[169] = 0.0;
   out_8780343526186803252[170] = 0.0;
   out_8780343526186803252[171] = 1.0;
   out_8780343526186803252[172] = 0.0;
   out_8780343526186803252[173] = 0.0;
   out_8780343526186803252[174] = 0.0;
   out_8780343526186803252[175] = 0.0;
   out_8780343526186803252[176] = 0.0;
   out_8780343526186803252[177] = 0.0;
   out_8780343526186803252[178] = 0.0;
   out_8780343526186803252[179] = 0.0;
   out_8780343526186803252[180] = 0.0;
   out_8780343526186803252[181] = 0.0;
   out_8780343526186803252[182] = 0.0;
   out_8780343526186803252[183] = 0.0;
   out_8780343526186803252[184] = 0.0;
   out_8780343526186803252[185] = 0.0;
   out_8780343526186803252[186] = 0.0;
   out_8780343526186803252[187] = 0.0;
   out_8780343526186803252[188] = 0.0;
   out_8780343526186803252[189] = 0.0;
   out_8780343526186803252[190] = 1.0;
   out_8780343526186803252[191] = 0.0;
   out_8780343526186803252[192] = 0.0;
   out_8780343526186803252[193] = 0.0;
   out_8780343526186803252[194] = 0.0;
   out_8780343526186803252[195] = 0.0;
   out_8780343526186803252[196] = 0.0;
   out_8780343526186803252[197] = 0.0;
   out_8780343526186803252[198] = 0.0;
   out_8780343526186803252[199] = 0.0;
   out_8780343526186803252[200] = 0.0;
   out_8780343526186803252[201] = 0.0;
   out_8780343526186803252[202] = 0.0;
   out_8780343526186803252[203] = 0.0;
   out_8780343526186803252[204] = 0.0;
   out_8780343526186803252[205] = 0.0;
   out_8780343526186803252[206] = 0.0;
   out_8780343526186803252[207] = 0.0;
   out_8780343526186803252[208] = 0.0;
   out_8780343526186803252[209] = 1.0;
   out_8780343526186803252[210] = 0.0;
   out_8780343526186803252[211] = 0.0;
   out_8780343526186803252[212] = 0.0;
   out_8780343526186803252[213] = 0.0;
   out_8780343526186803252[214] = 0.0;
   out_8780343526186803252[215] = 0.0;
   out_8780343526186803252[216] = 0.0;
   out_8780343526186803252[217] = 0.0;
   out_8780343526186803252[218] = 0.0;
   out_8780343526186803252[219] = 0.0;
   out_8780343526186803252[220] = 0.0;
   out_8780343526186803252[221] = 0.0;
   out_8780343526186803252[222] = 0.0;
   out_8780343526186803252[223] = 0.0;
   out_8780343526186803252[224] = 0.0;
   out_8780343526186803252[225] = 0.0;
   out_8780343526186803252[226] = 0.0;
   out_8780343526186803252[227] = 0.0;
   out_8780343526186803252[228] = 1.0;
   out_8780343526186803252[229] = 0.0;
   out_8780343526186803252[230] = 0.0;
   out_8780343526186803252[231] = 0.0;
   out_8780343526186803252[232] = 0.0;
   out_8780343526186803252[233] = 0.0;
   out_8780343526186803252[234] = 0.0;
   out_8780343526186803252[235] = 0.0;
   out_8780343526186803252[236] = 0.0;
   out_8780343526186803252[237] = 0.0;
   out_8780343526186803252[238] = 0.0;
   out_8780343526186803252[239] = 0.0;
   out_8780343526186803252[240] = 0.0;
   out_8780343526186803252[241] = 0.0;
   out_8780343526186803252[242] = 0.0;
   out_8780343526186803252[243] = 0.0;
   out_8780343526186803252[244] = 0.0;
   out_8780343526186803252[245] = 0.0;
   out_8780343526186803252[246] = 0.0;
   out_8780343526186803252[247] = 1.0;
   out_8780343526186803252[248] = 0.0;
   out_8780343526186803252[249] = 0.0;
   out_8780343526186803252[250] = 0.0;
   out_8780343526186803252[251] = 0.0;
   out_8780343526186803252[252] = 0.0;
   out_8780343526186803252[253] = 0.0;
   out_8780343526186803252[254] = 0.0;
   out_8780343526186803252[255] = 0.0;
   out_8780343526186803252[256] = 0.0;
   out_8780343526186803252[257] = 0.0;
   out_8780343526186803252[258] = 0.0;
   out_8780343526186803252[259] = 0.0;
   out_8780343526186803252[260] = 0.0;
   out_8780343526186803252[261] = 0.0;
   out_8780343526186803252[262] = 0.0;
   out_8780343526186803252[263] = 0.0;
   out_8780343526186803252[264] = 0.0;
   out_8780343526186803252[265] = 0.0;
   out_8780343526186803252[266] = 1.0;
   out_8780343526186803252[267] = 0.0;
   out_8780343526186803252[268] = 0.0;
   out_8780343526186803252[269] = 0.0;
   out_8780343526186803252[270] = 0.0;
   out_8780343526186803252[271] = 0.0;
   out_8780343526186803252[272] = 0.0;
   out_8780343526186803252[273] = 0.0;
   out_8780343526186803252[274] = 0.0;
   out_8780343526186803252[275] = 0.0;
   out_8780343526186803252[276] = 0.0;
   out_8780343526186803252[277] = 0.0;
   out_8780343526186803252[278] = 0.0;
   out_8780343526186803252[279] = 0.0;
   out_8780343526186803252[280] = 0.0;
   out_8780343526186803252[281] = 0.0;
   out_8780343526186803252[282] = 0.0;
   out_8780343526186803252[283] = 0.0;
   out_8780343526186803252[284] = 0.0;
   out_8780343526186803252[285] = 1.0;
   out_8780343526186803252[286] = 0.0;
   out_8780343526186803252[287] = 0.0;
   out_8780343526186803252[288] = 0.0;
   out_8780343526186803252[289] = 0.0;
   out_8780343526186803252[290] = 0.0;
   out_8780343526186803252[291] = 0.0;
   out_8780343526186803252[292] = 0.0;
   out_8780343526186803252[293] = 0.0;
   out_8780343526186803252[294] = 0.0;
   out_8780343526186803252[295] = 0.0;
   out_8780343526186803252[296] = 0.0;
   out_8780343526186803252[297] = 0.0;
   out_8780343526186803252[298] = 0.0;
   out_8780343526186803252[299] = 0.0;
   out_8780343526186803252[300] = 0.0;
   out_8780343526186803252[301] = 0.0;
   out_8780343526186803252[302] = 0.0;
   out_8780343526186803252[303] = 0.0;
   out_8780343526186803252[304] = 1.0;
   out_8780343526186803252[305] = 0.0;
   out_8780343526186803252[306] = 0.0;
   out_8780343526186803252[307] = 0.0;
   out_8780343526186803252[308] = 0.0;
   out_8780343526186803252[309] = 0.0;
   out_8780343526186803252[310] = 0.0;
   out_8780343526186803252[311] = 0.0;
   out_8780343526186803252[312] = 0.0;
   out_8780343526186803252[313] = 0.0;
   out_8780343526186803252[314] = 0.0;
   out_8780343526186803252[315] = 0.0;
   out_8780343526186803252[316] = 0.0;
   out_8780343526186803252[317] = 0.0;
   out_8780343526186803252[318] = 0.0;
   out_8780343526186803252[319] = 0.0;
   out_8780343526186803252[320] = 0.0;
   out_8780343526186803252[321] = 0.0;
   out_8780343526186803252[322] = 0.0;
   out_8780343526186803252[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_9204844528415638616) {
   out_9204844528415638616[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_9204844528415638616[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_9204844528415638616[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_9204844528415638616[3] = dt*state[12] + state[3];
   out_9204844528415638616[4] = dt*state[13] + state[4];
   out_9204844528415638616[5] = dt*state[14] + state[5];
   out_9204844528415638616[6] = state[6];
   out_9204844528415638616[7] = state[7];
   out_9204844528415638616[8] = state[8];
   out_9204844528415638616[9] = state[9];
   out_9204844528415638616[10] = state[10];
   out_9204844528415638616[11] = state[11];
   out_9204844528415638616[12] = state[12];
   out_9204844528415638616[13] = state[13];
   out_9204844528415638616[14] = state[14];
   out_9204844528415638616[15] = state[15];
   out_9204844528415638616[16] = state[16];
   out_9204844528415638616[17] = state[17];
}
void F_fun(double *state, double dt, double *out_8963612579970952214) {
   out_8963612579970952214[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8963612579970952214[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8963612579970952214[2] = 0;
   out_8963612579970952214[3] = 0;
   out_8963612579970952214[4] = 0;
   out_8963612579970952214[5] = 0;
   out_8963612579970952214[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8963612579970952214[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8963612579970952214[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8963612579970952214[9] = 0;
   out_8963612579970952214[10] = 0;
   out_8963612579970952214[11] = 0;
   out_8963612579970952214[12] = 0;
   out_8963612579970952214[13] = 0;
   out_8963612579970952214[14] = 0;
   out_8963612579970952214[15] = 0;
   out_8963612579970952214[16] = 0;
   out_8963612579970952214[17] = 0;
   out_8963612579970952214[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8963612579970952214[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8963612579970952214[20] = 0;
   out_8963612579970952214[21] = 0;
   out_8963612579970952214[22] = 0;
   out_8963612579970952214[23] = 0;
   out_8963612579970952214[24] = 0;
   out_8963612579970952214[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8963612579970952214[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8963612579970952214[27] = 0;
   out_8963612579970952214[28] = 0;
   out_8963612579970952214[29] = 0;
   out_8963612579970952214[30] = 0;
   out_8963612579970952214[31] = 0;
   out_8963612579970952214[32] = 0;
   out_8963612579970952214[33] = 0;
   out_8963612579970952214[34] = 0;
   out_8963612579970952214[35] = 0;
   out_8963612579970952214[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8963612579970952214[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8963612579970952214[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8963612579970952214[39] = 0;
   out_8963612579970952214[40] = 0;
   out_8963612579970952214[41] = 0;
   out_8963612579970952214[42] = 0;
   out_8963612579970952214[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8963612579970952214[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8963612579970952214[45] = 0;
   out_8963612579970952214[46] = 0;
   out_8963612579970952214[47] = 0;
   out_8963612579970952214[48] = 0;
   out_8963612579970952214[49] = 0;
   out_8963612579970952214[50] = 0;
   out_8963612579970952214[51] = 0;
   out_8963612579970952214[52] = 0;
   out_8963612579970952214[53] = 0;
   out_8963612579970952214[54] = 0;
   out_8963612579970952214[55] = 0;
   out_8963612579970952214[56] = 0;
   out_8963612579970952214[57] = 1;
   out_8963612579970952214[58] = 0;
   out_8963612579970952214[59] = 0;
   out_8963612579970952214[60] = 0;
   out_8963612579970952214[61] = 0;
   out_8963612579970952214[62] = 0;
   out_8963612579970952214[63] = 0;
   out_8963612579970952214[64] = 0;
   out_8963612579970952214[65] = 0;
   out_8963612579970952214[66] = dt;
   out_8963612579970952214[67] = 0;
   out_8963612579970952214[68] = 0;
   out_8963612579970952214[69] = 0;
   out_8963612579970952214[70] = 0;
   out_8963612579970952214[71] = 0;
   out_8963612579970952214[72] = 0;
   out_8963612579970952214[73] = 0;
   out_8963612579970952214[74] = 0;
   out_8963612579970952214[75] = 0;
   out_8963612579970952214[76] = 1;
   out_8963612579970952214[77] = 0;
   out_8963612579970952214[78] = 0;
   out_8963612579970952214[79] = 0;
   out_8963612579970952214[80] = 0;
   out_8963612579970952214[81] = 0;
   out_8963612579970952214[82] = 0;
   out_8963612579970952214[83] = 0;
   out_8963612579970952214[84] = 0;
   out_8963612579970952214[85] = dt;
   out_8963612579970952214[86] = 0;
   out_8963612579970952214[87] = 0;
   out_8963612579970952214[88] = 0;
   out_8963612579970952214[89] = 0;
   out_8963612579970952214[90] = 0;
   out_8963612579970952214[91] = 0;
   out_8963612579970952214[92] = 0;
   out_8963612579970952214[93] = 0;
   out_8963612579970952214[94] = 0;
   out_8963612579970952214[95] = 1;
   out_8963612579970952214[96] = 0;
   out_8963612579970952214[97] = 0;
   out_8963612579970952214[98] = 0;
   out_8963612579970952214[99] = 0;
   out_8963612579970952214[100] = 0;
   out_8963612579970952214[101] = 0;
   out_8963612579970952214[102] = 0;
   out_8963612579970952214[103] = 0;
   out_8963612579970952214[104] = dt;
   out_8963612579970952214[105] = 0;
   out_8963612579970952214[106] = 0;
   out_8963612579970952214[107] = 0;
   out_8963612579970952214[108] = 0;
   out_8963612579970952214[109] = 0;
   out_8963612579970952214[110] = 0;
   out_8963612579970952214[111] = 0;
   out_8963612579970952214[112] = 0;
   out_8963612579970952214[113] = 0;
   out_8963612579970952214[114] = 1;
   out_8963612579970952214[115] = 0;
   out_8963612579970952214[116] = 0;
   out_8963612579970952214[117] = 0;
   out_8963612579970952214[118] = 0;
   out_8963612579970952214[119] = 0;
   out_8963612579970952214[120] = 0;
   out_8963612579970952214[121] = 0;
   out_8963612579970952214[122] = 0;
   out_8963612579970952214[123] = 0;
   out_8963612579970952214[124] = 0;
   out_8963612579970952214[125] = 0;
   out_8963612579970952214[126] = 0;
   out_8963612579970952214[127] = 0;
   out_8963612579970952214[128] = 0;
   out_8963612579970952214[129] = 0;
   out_8963612579970952214[130] = 0;
   out_8963612579970952214[131] = 0;
   out_8963612579970952214[132] = 0;
   out_8963612579970952214[133] = 1;
   out_8963612579970952214[134] = 0;
   out_8963612579970952214[135] = 0;
   out_8963612579970952214[136] = 0;
   out_8963612579970952214[137] = 0;
   out_8963612579970952214[138] = 0;
   out_8963612579970952214[139] = 0;
   out_8963612579970952214[140] = 0;
   out_8963612579970952214[141] = 0;
   out_8963612579970952214[142] = 0;
   out_8963612579970952214[143] = 0;
   out_8963612579970952214[144] = 0;
   out_8963612579970952214[145] = 0;
   out_8963612579970952214[146] = 0;
   out_8963612579970952214[147] = 0;
   out_8963612579970952214[148] = 0;
   out_8963612579970952214[149] = 0;
   out_8963612579970952214[150] = 0;
   out_8963612579970952214[151] = 0;
   out_8963612579970952214[152] = 1;
   out_8963612579970952214[153] = 0;
   out_8963612579970952214[154] = 0;
   out_8963612579970952214[155] = 0;
   out_8963612579970952214[156] = 0;
   out_8963612579970952214[157] = 0;
   out_8963612579970952214[158] = 0;
   out_8963612579970952214[159] = 0;
   out_8963612579970952214[160] = 0;
   out_8963612579970952214[161] = 0;
   out_8963612579970952214[162] = 0;
   out_8963612579970952214[163] = 0;
   out_8963612579970952214[164] = 0;
   out_8963612579970952214[165] = 0;
   out_8963612579970952214[166] = 0;
   out_8963612579970952214[167] = 0;
   out_8963612579970952214[168] = 0;
   out_8963612579970952214[169] = 0;
   out_8963612579970952214[170] = 0;
   out_8963612579970952214[171] = 1;
   out_8963612579970952214[172] = 0;
   out_8963612579970952214[173] = 0;
   out_8963612579970952214[174] = 0;
   out_8963612579970952214[175] = 0;
   out_8963612579970952214[176] = 0;
   out_8963612579970952214[177] = 0;
   out_8963612579970952214[178] = 0;
   out_8963612579970952214[179] = 0;
   out_8963612579970952214[180] = 0;
   out_8963612579970952214[181] = 0;
   out_8963612579970952214[182] = 0;
   out_8963612579970952214[183] = 0;
   out_8963612579970952214[184] = 0;
   out_8963612579970952214[185] = 0;
   out_8963612579970952214[186] = 0;
   out_8963612579970952214[187] = 0;
   out_8963612579970952214[188] = 0;
   out_8963612579970952214[189] = 0;
   out_8963612579970952214[190] = 1;
   out_8963612579970952214[191] = 0;
   out_8963612579970952214[192] = 0;
   out_8963612579970952214[193] = 0;
   out_8963612579970952214[194] = 0;
   out_8963612579970952214[195] = 0;
   out_8963612579970952214[196] = 0;
   out_8963612579970952214[197] = 0;
   out_8963612579970952214[198] = 0;
   out_8963612579970952214[199] = 0;
   out_8963612579970952214[200] = 0;
   out_8963612579970952214[201] = 0;
   out_8963612579970952214[202] = 0;
   out_8963612579970952214[203] = 0;
   out_8963612579970952214[204] = 0;
   out_8963612579970952214[205] = 0;
   out_8963612579970952214[206] = 0;
   out_8963612579970952214[207] = 0;
   out_8963612579970952214[208] = 0;
   out_8963612579970952214[209] = 1;
   out_8963612579970952214[210] = 0;
   out_8963612579970952214[211] = 0;
   out_8963612579970952214[212] = 0;
   out_8963612579970952214[213] = 0;
   out_8963612579970952214[214] = 0;
   out_8963612579970952214[215] = 0;
   out_8963612579970952214[216] = 0;
   out_8963612579970952214[217] = 0;
   out_8963612579970952214[218] = 0;
   out_8963612579970952214[219] = 0;
   out_8963612579970952214[220] = 0;
   out_8963612579970952214[221] = 0;
   out_8963612579970952214[222] = 0;
   out_8963612579970952214[223] = 0;
   out_8963612579970952214[224] = 0;
   out_8963612579970952214[225] = 0;
   out_8963612579970952214[226] = 0;
   out_8963612579970952214[227] = 0;
   out_8963612579970952214[228] = 1;
   out_8963612579970952214[229] = 0;
   out_8963612579970952214[230] = 0;
   out_8963612579970952214[231] = 0;
   out_8963612579970952214[232] = 0;
   out_8963612579970952214[233] = 0;
   out_8963612579970952214[234] = 0;
   out_8963612579970952214[235] = 0;
   out_8963612579970952214[236] = 0;
   out_8963612579970952214[237] = 0;
   out_8963612579970952214[238] = 0;
   out_8963612579970952214[239] = 0;
   out_8963612579970952214[240] = 0;
   out_8963612579970952214[241] = 0;
   out_8963612579970952214[242] = 0;
   out_8963612579970952214[243] = 0;
   out_8963612579970952214[244] = 0;
   out_8963612579970952214[245] = 0;
   out_8963612579970952214[246] = 0;
   out_8963612579970952214[247] = 1;
   out_8963612579970952214[248] = 0;
   out_8963612579970952214[249] = 0;
   out_8963612579970952214[250] = 0;
   out_8963612579970952214[251] = 0;
   out_8963612579970952214[252] = 0;
   out_8963612579970952214[253] = 0;
   out_8963612579970952214[254] = 0;
   out_8963612579970952214[255] = 0;
   out_8963612579970952214[256] = 0;
   out_8963612579970952214[257] = 0;
   out_8963612579970952214[258] = 0;
   out_8963612579970952214[259] = 0;
   out_8963612579970952214[260] = 0;
   out_8963612579970952214[261] = 0;
   out_8963612579970952214[262] = 0;
   out_8963612579970952214[263] = 0;
   out_8963612579970952214[264] = 0;
   out_8963612579970952214[265] = 0;
   out_8963612579970952214[266] = 1;
   out_8963612579970952214[267] = 0;
   out_8963612579970952214[268] = 0;
   out_8963612579970952214[269] = 0;
   out_8963612579970952214[270] = 0;
   out_8963612579970952214[271] = 0;
   out_8963612579970952214[272] = 0;
   out_8963612579970952214[273] = 0;
   out_8963612579970952214[274] = 0;
   out_8963612579970952214[275] = 0;
   out_8963612579970952214[276] = 0;
   out_8963612579970952214[277] = 0;
   out_8963612579970952214[278] = 0;
   out_8963612579970952214[279] = 0;
   out_8963612579970952214[280] = 0;
   out_8963612579970952214[281] = 0;
   out_8963612579970952214[282] = 0;
   out_8963612579970952214[283] = 0;
   out_8963612579970952214[284] = 0;
   out_8963612579970952214[285] = 1;
   out_8963612579970952214[286] = 0;
   out_8963612579970952214[287] = 0;
   out_8963612579970952214[288] = 0;
   out_8963612579970952214[289] = 0;
   out_8963612579970952214[290] = 0;
   out_8963612579970952214[291] = 0;
   out_8963612579970952214[292] = 0;
   out_8963612579970952214[293] = 0;
   out_8963612579970952214[294] = 0;
   out_8963612579970952214[295] = 0;
   out_8963612579970952214[296] = 0;
   out_8963612579970952214[297] = 0;
   out_8963612579970952214[298] = 0;
   out_8963612579970952214[299] = 0;
   out_8963612579970952214[300] = 0;
   out_8963612579970952214[301] = 0;
   out_8963612579970952214[302] = 0;
   out_8963612579970952214[303] = 0;
   out_8963612579970952214[304] = 1;
   out_8963612579970952214[305] = 0;
   out_8963612579970952214[306] = 0;
   out_8963612579970952214[307] = 0;
   out_8963612579970952214[308] = 0;
   out_8963612579970952214[309] = 0;
   out_8963612579970952214[310] = 0;
   out_8963612579970952214[311] = 0;
   out_8963612579970952214[312] = 0;
   out_8963612579970952214[313] = 0;
   out_8963612579970952214[314] = 0;
   out_8963612579970952214[315] = 0;
   out_8963612579970952214[316] = 0;
   out_8963612579970952214[317] = 0;
   out_8963612579970952214[318] = 0;
   out_8963612579970952214[319] = 0;
   out_8963612579970952214[320] = 0;
   out_8963612579970952214[321] = 0;
   out_8963612579970952214[322] = 0;
   out_8963612579970952214[323] = 1;
}
void h_4(double *state, double *unused, double *out_7153786749136804353) {
   out_7153786749136804353[0] = state[6] + state[9];
   out_7153786749136804353[1] = state[7] + state[10];
   out_7153786749136804353[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_5008536316342895680) {
   out_5008536316342895680[0] = 0;
   out_5008536316342895680[1] = 0;
   out_5008536316342895680[2] = 0;
   out_5008536316342895680[3] = 0;
   out_5008536316342895680[4] = 0;
   out_5008536316342895680[5] = 0;
   out_5008536316342895680[6] = 1;
   out_5008536316342895680[7] = 0;
   out_5008536316342895680[8] = 0;
   out_5008536316342895680[9] = 1;
   out_5008536316342895680[10] = 0;
   out_5008536316342895680[11] = 0;
   out_5008536316342895680[12] = 0;
   out_5008536316342895680[13] = 0;
   out_5008536316342895680[14] = 0;
   out_5008536316342895680[15] = 0;
   out_5008536316342895680[16] = 0;
   out_5008536316342895680[17] = 0;
   out_5008536316342895680[18] = 0;
   out_5008536316342895680[19] = 0;
   out_5008536316342895680[20] = 0;
   out_5008536316342895680[21] = 0;
   out_5008536316342895680[22] = 0;
   out_5008536316342895680[23] = 0;
   out_5008536316342895680[24] = 0;
   out_5008536316342895680[25] = 1;
   out_5008536316342895680[26] = 0;
   out_5008536316342895680[27] = 0;
   out_5008536316342895680[28] = 1;
   out_5008536316342895680[29] = 0;
   out_5008536316342895680[30] = 0;
   out_5008536316342895680[31] = 0;
   out_5008536316342895680[32] = 0;
   out_5008536316342895680[33] = 0;
   out_5008536316342895680[34] = 0;
   out_5008536316342895680[35] = 0;
   out_5008536316342895680[36] = 0;
   out_5008536316342895680[37] = 0;
   out_5008536316342895680[38] = 0;
   out_5008536316342895680[39] = 0;
   out_5008536316342895680[40] = 0;
   out_5008536316342895680[41] = 0;
   out_5008536316342895680[42] = 0;
   out_5008536316342895680[43] = 0;
   out_5008536316342895680[44] = 1;
   out_5008536316342895680[45] = 0;
   out_5008536316342895680[46] = 0;
   out_5008536316342895680[47] = 1;
   out_5008536316342895680[48] = 0;
   out_5008536316342895680[49] = 0;
   out_5008536316342895680[50] = 0;
   out_5008536316342895680[51] = 0;
   out_5008536316342895680[52] = 0;
   out_5008536316342895680[53] = 0;
}
void h_10(double *state, double *unused, double *out_5993916404490142272) {
   out_5993916404490142272[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_5993916404490142272[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_5993916404490142272[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_2637547737266629513) {
   out_2637547737266629513[0] = 0;
   out_2637547737266629513[1] = 9.8100000000000005*cos(state[1]);
   out_2637547737266629513[2] = 0;
   out_2637547737266629513[3] = 0;
   out_2637547737266629513[4] = -state[8];
   out_2637547737266629513[5] = state[7];
   out_2637547737266629513[6] = 0;
   out_2637547737266629513[7] = state[5];
   out_2637547737266629513[8] = -state[4];
   out_2637547737266629513[9] = 0;
   out_2637547737266629513[10] = 0;
   out_2637547737266629513[11] = 0;
   out_2637547737266629513[12] = 1;
   out_2637547737266629513[13] = 0;
   out_2637547737266629513[14] = 0;
   out_2637547737266629513[15] = 1;
   out_2637547737266629513[16] = 0;
   out_2637547737266629513[17] = 0;
   out_2637547737266629513[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_2637547737266629513[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_2637547737266629513[20] = 0;
   out_2637547737266629513[21] = state[8];
   out_2637547737266629513[22] = 0;
   out_2637547737266629513[23] = -state[6];
   out_2637547737266629513[24] = -state[5];
   out_2637547737266629513[25] = 0;
   out_2637547737266629513[26] = state[3];
   out_2637547737266629513[27] = 0;
   out_2637547737266629513[28] = 0;
   out_2637547737266629513[29] = 0;
   out_2637547737266629513[30] = 0;
   out_2637547737266629513[31] = 1;
   out_2637547737266629513[32] = 0;
   out_2637547737266629513[33] = 0;
   out_2637547737266629513[34] = 1;
   out_2637547737266629513[35] = 0;
   out_2637547737266629513[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_2637547737266629513[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_2637547737266629513[38] = 0;
   out_2637547737266629513[39] = -state[7];
   out_2637547737266629513[40] = state[6];
   out_2637547737266629513[41] = 0;
   out_2637547737266629513[42] = state[4];
   out_2637547737266629513[43] = -state[3];
   out_2637547737266629513[44] = 0;
   out_2637547737266629513[45] = 0;
   out_2637547737266629513[46] = 0;
   out_2637547737266629513[47] = 0;
   out_2637547737266629513[48] = 0;
   out_2637547737266629513[49] = 0;
   out_2637547737266629513[50] = 1;
   out_2637547737266629513[51] = 0;
   out_2637547737266629513[52] = 0;
   out_2637547737266629513[53] = 1;
}
void h_13(double *state, double *unused, double *out_5655346861848509209) {
   out_5655346861848509209[0] = state[3];
   out_5655346861848509209[1] = state[4];
   out_5655346861848509209[2] = state[5];
}
void H_13(double *state, double *unused, double *out_8842291779645419704) {
   out_8842291779645419704[0] = 0;
   out_8842291779645419704[1] = 0;
   out_8842291779645419704[2] = 0;
   out_8842291779645419704[3] = 1;
   out_8842291779645419704[4] = 0;
   out_8842291779645419704[5] = 0;
   out_8842291779645419704[6] = 0;
   out_8842291779645419704[7] = 0;
   out_8842291779645419704[8] = 0;
   out_8842291779645419704[9] = 0;
   out_8842291779645419704[10] = 0;
   out_8842291779645419704[11] = 0;
   out_8842291779645419704[12] = 0;
   out_8842291779645419704[13] = 0;
   out_8842291779645419704[14] = 0;
   out_8842291779645419704[15] = 0;
   out_8842291779645419704[16] = 0;
   out_8842291779645419704[17] = 0;
   out_8842291779645419704[18] = 0;
   out_8842291779645419704[19] = 0;
   out_8842291779645419704[20] = 0;
   out_8842291779645419704[21] = 0;
   out_8842291779645419704[22] = 1;
   out_8842291779645419704[23] = 0;
   out_8842291779645419704[24] = 0;
   out_8842291779645419704[25] = 0;
   out_8842291779645419704[26] = 0;
   out_8842291779645419704[27] = 0;
   out_8842291779645419704[28] = 0;
   out_8842291779645419704[29] = 0;
   out_8842291779645419704[30] = 0;
   out_8842291779645419704[31] = 0;
   out_8842291779645419704[32] = 0;
   out_8842291779645419704[33] = 0;
   out_8842291779645419704[34] = 0;
   out_8842291779645419704[35] = 0;
   out_8842291779645419704[36] = 0;
   out_8842291779645419704[37] = 0;
   out_8842291779645419704[38] = 0;
   out_8842291779645419704[39] = 0;
   out_8842291779645419704[40] = 0;
   out_8842291779645419704[41] = 1;
   out_8842291779645419704[42] = 0;
   out_8842291779645419704[43] = 0;
   out_8842291779645419704[44] = 0;
   out_8842291779645419704[45] = 0;
   out_8842291779645419704[46] = 0;
   out_8842291779645419704[47] = 0;
   out_8842291779645419704[48] = 0;
   out_8842291779645419704[49] = 0;
   out_8842291779645419704[50] = 0;
   out_8842291779645419704[51] = 0;
   out_8842291779645419704[52] = 0;
   out_8842291779645419704[53] = 0;
}
void h_14(double *state, double *unused, double *out_6295315712474168023) {
   out_6295315712474168023[0] = state[6];
   out_6295315712474168023[1] = state[7];
   out_6295315712474168023[2] = state[8];
}
void H_14(double *state, double *unused, double *out_8091324748638267976) {
   out_8091324748638267976[0] = 0;
   out_8091324748638267976[1] = 0;
   out_8091324748638267976[2] = 0;
   out_8091324748638267976[3] = 0;
   out_8091324748638267976[4] = 0;
   out_8091324748638267976[5] = 0;
   out_8091324748638267976[6] = 1;
   out_8091324748638267976[7] = 0;
   out_8091324748638267976[8] = 0;
   out_8091324748638267976[9] = 0;
   out_8091324748638267976[10] = 0;
   out_8091324748638267976[11] = 0;
   out_8091324748638267976[12] = 0;
   out_8091324748638267976[13] = 0;
   out_8091324748638267976[14] = 0;
   out_8091324748638267976[15] = 0;
   out_8091324748638267976[16] = 0;
   out_8091324748638267976[17] = 0;
   out_8091324748638267976[18] = 0;
   out_8091324748638267976[19] = 0;
   out_8091324748638267976[20] = 0;
   out_8091324748638267976[21] = 0;
   out_8091324748638267976[22] = 0;
   out_8091324748638267976[23] = 0;
   out_8091324748638267976[24] = 0;
   out_8091324748638267976[25] = 1;
   out_8091324748638267976[26] = 0;
   out_8091324748638267976[27] = 0;
   out_8091324748638267976[28] = 0;
   out_8091324748638267976[29] = 0;
   out_8091324748638267976[30] = 0;
   out_8091324748638267976[31] = 0;
   out_8091324748638267976[32] = 0;
   out_8091324748638267976[33] = 0;
   out_8091324748638267976[34] = 0;
   out_8091324748638267976[35] = 0;
   out_8091324748638267976[36] = 0;
   out_8091324748638267976[37] = 0;
   out_8091324748638267976[38] = 0;
   out_8091324748638267976[39] = 0;
   out_8091324748638267976[40] = 0;
   out_8091324748638267976[41] = 0;
   out_8091324748638267976[42] = 0;
   out_8091324748638267976[43] = 0;
   out_8091324748638267976[44] = 1;
   out_8091324748638267976[45] = 0;
   out_8091324748638267976[46] = 0;
   out_8091324748638267976[47] = 0;
   out_8091324748638267976[48] = 0;
   out_8091324748638267976[49] = 0;
   out_8091324748638267976[50] = 0;
   out_8091324748638267976[51] = 0;
   out_8091324748638267976[52] = 0;
   out_8091324748638267976[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_3209558036827677652) {
  err_fun(nom_x, delta_x, out_3209558036827677652);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5101632267130187312) {
  inv_err_fun(nom_x, true_x, out_5101632267130187312);
}
void pose_H_mod_fun(double *state, double *out_8780343526186803252) {
  H_mod_fun(state, out_8780343526186803252);
}
void pose_f_fun(double *state, double dt, double *out_9204844528415638616) {
  f_fun(state,  dt, out_9204844528415638616);
}
void pose_F_fun(double *state, double dt, double *out_8963612579970952214) {
  F_fun(state,  dt, out_8963612579970952214);
}
void pose_h_4(double *state, double *unused, double *out_7153786749136804353) {
  h_4(state, unused, out_7153786749136804353);
}
void pose_H_4(double *state, double *unused, double *out_5008536316342895680) {
  H_4(state, unused, out_5008536316342895680);
}
void pose_h_10(double *state, double *unused, double *out_5993916404490142272) {
  h_10(state, unused, out_5993916404490142272);
}
void pose_H_10(double *state, double *unused, double *out_2637547737266629513) {
  H_10(state, unused, out_2637547737266629513);
}
void pose_h_13(double *state, double *unused, double *out_5655346861848509209) {
  h_13(state, unused, out_5655346861848509209);
}
void pose_H_13(double *state, double *unused, double *out_8842291779645419704) {
  H_13(state, unused, out_8842291779645419704);
}
void pose_h_14(double *state, double *unused, double *out_6295315712474168023) {
  h_14(state, unused, out_6295315712474168023);
}
void pose_H_14(double *state, double *unused, double *out_8091324748638267976) {
  H_14(state, unused, out_8091324748638267976);
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
