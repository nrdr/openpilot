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
void err_fun(double *nom_x, double *delta_x, double *out_7855544638909347154) {
   out_7855544638909347154[0] = delta_x[0] + nom_x[0];
   out_7855544638909347154[1] = delta_x[1] + nom_x[1];
   out_7855544638909347154[2] = delta_x[2] + nom_x[2];
   out_7855544638909347154[3] = delta_x[3] + nom_x[3];
   out_7855544638909347154[4] = delta_x[4] + nom_x[4];
   out_7855544638909347154[5] = delta_x[5] + nom_x[5];
   out_7855544638909347154[6] = delta_x[6] + nom_x[6];
   out_7855544638909347154[7] = delta_x[7] + nom_x[7];
   out_7855544638909347154[8] = delta_x[8] + nom_x[8];
   out_7855544638909347154[9] = delta_x[9] + nom_x[9];
   out_7855544638909347154[10] = delta_x[10] + nom_x[10];
   out_7855544638909347154[11] = delta_x[11] + nom_x[11];
   out_7855544638909347154[12] = delta_x[12] + nom_x[12];
   out_7855544638909347154[13] = delta_x[13] + nom_x[13];
   out_7855544638909347154[14] = delta_x[14] + nom_x[14];
   out_7855544638909347154[15] = delta_x[15] + nom_x[15];
   out_7855544638909347154[16] = delta_x[16] + nom_x[16];
   out_7855544638909347154[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_8154377992469345659) {
   out_8154377992469345659[0] = -nom_x[0] + true_x[0];
   out_8154377992469345659[1] = -nom_x[1] + true_x[1];
   out_8154377992469345659[2] = -nom_x[2] + true_x[2];
   out_8154377992469345659[3] = -nom_x[3] + true_x[3];
   out_8154377992469345659[4] = -nom_x[4] + true_x[4];
   out_8154377992469345659[5] = -nom_x[5] + true_x[5];
   out_8154377992469345659[6] = -nom_x[6] + true_x[6];
   out_8154377992469345659[7] = -nom_x[7] + true_x[7];
   out_8154377992469345659[8] = -nom_x[8] + true_x[8];
   out_8154377992469345659[9] = -nom_x[9] + true_x[9];
   out_8154377992469345659[10] = -nom_x[10] + true_x[10];
   out_8154377992469345659[11] = -nom_x[11] + true_x[11];
   out_8154377992469345659[12] = -nom_x[12] + true_x[12];
   out_8154377992469345659[13] = -nom_x[13] + true_x[13];
   out_8154377992469345659[14] = -nom_x[14] + true_x[14];
   out_8154377992469345659[15] = -nom_x[15] + true_x[15];
   out_8154377992469345659[16] = -nom_x[16] + true_x[16];
   out_8154377992469345659[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_6969728399034555931) {
   out_6969728399034555931[0] = 1.0;
   out_6969728399034555931[1] = 0.0;
   out_6969728399034555931[2] = 0.0;
   out_6969728399034555931[3] = 0.0;
   out_6969728399034555931[4] = 0.0;
   out_6969728399034555931[5] = 0.0;
   out_6969728399034555931[6] = 0.0;
   out_6969728399034555931[7] = 0.0;
   out_6969728399034555931[8] = 0.0;
   out_6969728399034555931[9] = 0.0;
   out_6969728399034555931[10] = 0.0;
   out_6969728399034555931[11] = 0.0;
   out_6969728399034555931[12] = 0.0;
   out_6969728399034555931[13] = 0.0;
   out_6969728399034555931[14] = 0.0;
   out_6969728399034555931[15] = 0.0;
   out_6969728399034555931[16] = 0.0;
   out_6969728399034555931[17] = 0.0;
   out_6969728399034555931[18] = 0.0;
   out_6969728399034555931[19] = 1.0;
   out_6969728399034555931[20] = 0.0;
   out_6969728399034555931[21] = 0.0;
   out_6969728399034555931[22] = 0.0;
   out_6969728399034555931[23] = 0.0;
   out_6969728399034555931[24] = 0.0;
   out_6969728399034555931[25] = 0.0;
   out_6969728399034555931[26] = 0.0;
   out_6969728399034555931[27] = 0.0;
   out_6969728399034555931[28] = 0.0;
   out_6969728399034555931[29] = 0.0;
   out_6969728399034555931[30] = 0.0;
   out_6969728399034555931[31] = 0.0;
   out_6969728399034555931[32] = 0.0;
   out_6969728399034555931[33] = 0.0;
   out_6969728399034555931[34] = 0.0;
   out_6969728399034555931[35] = 0.0;
   out_6969728399034555931[36] = 0.0;
   out_6969728399034555931[37] = 0.0;
   out_6969728399034555931[38] = 1.0;
   out_6969728399034555931[39] = 0.0;
   out_6969728399034555931[40] = 0.0;
   out_6969728399034555931[41] = 0.0;
   out_6969728399034555931[42] = 0.0;
   out_6969728399034555931[43] = 0.0;
   out_6969728399034555931[44] = 0.0;
   out_6969728399034555931[45] = 0.0;
   out_6969728399034555931[46] = 0.0;
   out_6969728399034555931[47] = 0.0;
   out_6969728399034555931[48] = 0.0;
   out_6969728399034555931[49] = 0.0;
   out_6969728399034555931[50] = 0.0;
   out_6969728399034555931[51] = 0.0;
   out_6969728399034555931[52] = 0.0;
   out_6969728399034555931[53] = 0.0;
   out_6969728399034555931[54] = 0.0;
   out_6969728399034555931[55] = 0.0;
   out_6969728399034555931[56] = 0.0;
   out_6969728399034555931[57] = 1.0;
   out_6969728399034555931[58] = 0.0;
   out_6969728399034555931[59] = 0.0;
   out_6969728399034555931[60] = 0.0;
   out_6969728399034555931[61] = 0.0;
   out_6969728399034555931[62] = 0.0;
   out_6969728399034555931[63] = 0.0;
   out_6969728399034555931[64] = 0.0;
   out_6969728399034555931[65] = 0.0;
   out_6969728399034555931[66] = 0.0;
   out_6969728399034555931[67] = 0.0;
   out_6969728399034555931[68] = 0.0;
   out_6969728399034555931[69] = 0.0;
   out_6969728399034555931[70] = 0.0;
   out_6969728399034555931[71] = 0.0;
   out_6969728399034555931[72] = 0.0;
   out_6969728399034555931[73] = 0.0;
   out_6969728399034555931[74] = 0.0;
   out_6969728399034555931[75] = 0.0;
   out_6969728399034555931[76] = 1.0;
   out_6969728399034555931[77] = 0.0;
   out_6969728399034555931[78] = 0.0;
   out_6969728399034555931[79] = 0.0;
   out_6969728399034555931[80] = 0.0;
   out_6969728399034555931[81] = 0.0;
   out_6969728399034555931[82] = 0.0;
   out_6969728399034555931[83] = 0.0;
   out_6969728399034555931[84] = 0.0;
   out_6969728399034555931[85] = 0.0;
   out_6969728399034555931[86] = 0.0;
   out_6969728399034555931[87] = 0.0;
   out_6969728399034555931[88] = 0.0;
   out_6969728399034555931[89] = 0.0;
   out_6969728399034555931[90] = 0.0;
   out_6969728399034555931[91] = 0.0;
   out_6969728399034555931[92] = 0.0;
   out_6969728399034555931[93] = 0.0;
   out_6969728399034555931[94] = 0.0;
   out_6969728399034555931[95] = 1.0;
   out_6969728399034555931[96] = 0.0;
   out_6969728399034555931[97] = 0.0;
   out_6969728399034555931[98] = 0.0;
   out_6969728399034555931[99] = 0.0;
   out_6969728399034555931[100] = 0.0;
   out_6969728399034555931[101] = 0.0;
   out_6969728399034555931[102] = 0.0;
   out_6969728399034555931[103] = 0.0;
   out_6969728399034555931[104] = 0.0;
   out_6969728399034555931[105] = 0.0;
   out_6969728399034555931[106] = 0.0;
   out_6969728399034555931[107] = 0.0;
   out_6969728399034555931[108] = 0.0;
   out_6969728399034555931[109] = 0.0;
   out_6969728399034555931[110] = 0.0;
   out_6969728399034555931[111] = 0.0;
   out_6969728399034555931[112] = 0.0;
   out_6969728399034555931[113] = 0.0;
   out_6969728399034555931[114] = 1.0;
   out_6969728399034555931[115] = 0.0;
   out_6969728399034555931[116] = 0.0;
   out_6969728399034555931[117] = 0.0;
   out_6969728399034555931[118] = 0.0;
   out_6969728399034555931[119] = 0.0;
   out_6969728399034555931[120] = 0.0;
   out_6969728399034555931[121] = 0.0;
   out_6969728399034555931[122] = 0.0;
   out_6969728399034555931[123] = 0.0;
   out_6969728399034555931[124] = 0.0;
   out_6969728399034555931[125] = 0.0;
   out_6969728399034555931[126] = 0.0;
   out_6969728399034555931[127] = 0.0;
   out_6969728399034555931[128] = 0.0;
   out_6969728399034555931[129] = 0.0;
   out_6969728399034555931[130] = 0.0;
   out_6969728399034555931[131] = 0.0;
   out_6969728399034555931[132] = 0.0;
   out_6969728399034555931[133] = 1.0;
   out_6969728399034555931[134] = 0.0;
   out_6969728399034555931[135] = 0.0;
   out_6969728399034555931[136] = 0.0;
   out_6969728399034555931[137] = 0.0;
   out_6969728399034555931[138] = 0.0;
   out_6969728399034555931[139] = 0.0;
   out_6969728399034555931[140] = 0.0;
   out_6969728399034555931[141] = 0.0;
   out_6969728399034555931[142] = 0.0;
   out_6969728399034555931[143] = 0.0;
   out_6969728399034555931[144] = 0.0;
   out_6969728399034555931[145] = 0.0;
   out_6969728399034555931[146] = 0.0;
   out_6969728399034555931[147] = 0.0;
   out_6969728399034555931[148] = 0.0;
   out_6969728399034555931[149] = 0.0;
   out_6969728399034555931[150] = 0.0;
   out_6969728399034555931[151] = 0.0;
   out_6969728399034555931[152] = 1.0;
   out_6969728399034555931[153] = 0.0;
   out_6969728399034555931[154] = 0.0;
   out_6969728399034555931[155] = 0.0;
   out_6969728399034555931[156] = 0.0;
   out_6969728399034555931[157] = 0.0;
   out_6969728399034555931[158] = 0.0;
   out_6969728399034555931[159] = 0.0;
   out_6969728399034555931[160] = 0.0;
   out_6969728399034555931[161] = 0.0;
   out_6969728399034555931[162] = 0.0;
   out_6969728399034555931[163] = 0.0;
   out_6969728399034555931[164] = 0.0;
   out_6969728399034555931[165] = 0.0;
   out_6969728399034555931[166] = 0.0;
   out_6969728399034555931[167] = 0.0;
   out_6969728399034555931[168] = 0.0;
   out_6969728399034555931[169] = 0.0;
   out_6969728399034555931[170] = 0.0;
   out_6969728399034555931[171] = 1.0;
   out_6969728399034555931[172] = 0.0;
   out_6969728399034555931[173] = 0.0;
   out_6969728399034555931[174] = 0.0;
   out_6969728399034555931[175] = 0.0;
   out_6969728399034555931[176] = 0.0;
   out_6969728399034555931[177] = 0.0;
   out_6969728399034555931[178] = 0.0;
   out_6969728399034555931[179] = 0.0;
   out_6969728399034555931[180] = 0.0;
   out_6969728399034555931[181] = 0.0;
   out_6969728399034555931[182] = 0.0;
   out_6969728399034555931[183] = 0.0;
   out_6969728399034555931[184] = 0.0;
   out_6969728399034555931[185] = 0.0;
   out_6969728399034555931[186] = 0.0;
   out_6969728399034555931[187] = 0.0;
   out_6969728399034555931[188] = 0.0;
   out_6969728399034555931[189] = 0.0;
   out_6969728399034555931[190] = 1.0;
   out_6969728399034555931[191] = 0.0;
   out_6969728399034555931[192] = 0.0;
   out_6969728399034555931[193] = 0.0;
   out_6969728399034555931[194] = 0.0;
   out_6969728399034555931[195] = 0.0;
   out_6969728399034555931[196] = 0.0;
   out_6969728399034555931[197] = 0.0;
   out_6969728399034555931[198] = 0.0;
   out_6969728399034555931[199] = 0.0;
   out_6969728399034555931[200] = 0.0;
   out_6969728399034555931[201] = 0.0;
   out_6969728399034555931[202] = 0.0;
   out_6969728399034555931[203] = 0.0;
   out_6969728399034555931[204] = 0.0;
   out_6969728399034555931[205] = 0.0;
   out_6969728399034555931[206] = 0.0;
   out_6969728399034555931[207] = 0.0;
   out_6969728399034555931[208] = 0.0;
   out_6969728399034555931[209] = 1.0;
   out_6969728399034555931[210] = 0.0;
   out_6969728399034555931[211] = 0.0;
   out_6969728399034555931[212] = 0.0;
   out_6969728399034555931[213] = 0.0;
   out_6969728399034555931[214] = 0.0;
   out_6969728399034555931[215] = 0.0;
   out_6969728399034555931[216] = 0.0;
   out_6969728399034555931[217] = 0.0;
   out_6969728399034555931[218] = 0.0;
   out_6969728399034555931[219] = 0.0;
   out_6969728399034555931[220] = 0.0;
   out_6969728399034555931[221] = 0.0;
   out_6969728399034555931[222] = 0.0;
   out_6969728399034555931[223] = 0.0;
   out_6969728399034555931[224] = 0.0;
   out_6969728399034555931[225] = 0.0;
   out_6969728399034555931[226] = 0.0;
   out_6969728399034555931[227] = 0.0;
   out_6969728399034555931[228] = 1.0;
   out_6969728399034555931[229] = 0.0;
   out_6969728399034555931[230] = 0.0;
   out_6969728399034555931[231] = 0.0;
   out_6969728399034555931[232] = 0.0;
   out_6969728399034555931[233] = 0.0;
   out_6969728399034555931[234] = 0.0;
   out_6969728399034555931[235] = 0.0;
   out_6969728399034555931[236] = 0.0;
   out_6969728399034555931[237] = 0.0;
   out_6969728399034555931[238] = 0.0;
   out_6969728399034555931[239] = 0.0;
   out_6969728399034555931[240] = 0.0;
   out_6969728399034555931[241] = 0.0;
   out_6969728399034555931[242] = 0.0;
   out_6969728399034555931[243] = 0.0;
   out_6969728399034555931[244] = 0.0;
   out_6969728399034555931[245] = 0.0;
   out_6969728399034555931[246] = 0.0;
   out_6969728399034555931[247] = 1.0;
   out_6969728399034555931[248] = 0.0;
   out_6969728399034555931[249] = 0.0;
   out_6969728399034555931[250] = 0.0;
   out_6969728399034555931[251] = 0.0;
   out_6969728399034555931[252] = 0.0;
   out_6969728399034555931[253] = 0.0;
   out_6969728399034555931[254] = 0.0;
   out_6969728399034555931[255] = 0.0;
   out_6969728399034555931[256] = 0.0;
   out_6969728399034555931[257] = 0.0;
   out_6969728399034555931[258] = 0.0;
   out_6969728399034555931[259] = 0.0;
   out_6969728399034555931[260] = 0.0;
   out_6969728399034555931[261] = 0.0;
   out_6969728399034555931[262] = 0.0;
   out_6969728399034555931[263] = 0.0;
   out_6969728399034555931[264] = 0.0;
   out_6969728399034555931[265] = 0.0;
   out_6969728399034555931[266] = 1.0;
   out_6969728399034555931[267] = 0.0;
   out_6969728399034555931[268] = 0.0;
   out_6969728399034555931[269] = 0.0;
   out_6969728399034555931[270] = 0.0;
   out_6969728399034555931[271] = 0.0;
   out_6969728399034555931[272] = 0.0;
   out_6969728399034555931[273] = 0.0;
   out_6969728399034555931[274] = 0.0;
   out_6969728399034555931[275] = 0.0;
   out_6969728399034555931[276] = 0.0;
   out_6969728399034555931[277] = 0.0;
   out_6969728399034555931[278] = 0.0;
   out_6969728399034555931[279] = 0.0;
   out_6969728399034555931[280] = 0.0;
   out_6969728399034555931[281] = 0.0;
   out_6969728399034555931[282] = 0.0;
   out_6969728399034555931[283] = 0.0;
   out_6969728399034555931[284] = 0.0;
   out_6969728399034555931[285] = 1.0;
   out_6969728399034555931[286] = 0.0;
   out_6969728399034555931[287] = 0.0;
   out_6969728399034555931[288] = 0.0;
   out_6969728399034555931[289] = 0.0;
   out_6969728399034555931[290] = 0.0;
   out_6969728399034555931[291] = 0.0;
   out_6969728399034555931[292] = 0.0;
   out_6969728399034555931[293] = 0.0;
   out_6969728399034555931[294] = 0.0;
   out_6969728399034555931[295] = 0.0;
   out_6969728399034555931[296] = 0.0;
   out_6969728399034555931[297] = 0.0;
   out_6969728399034555931[298] = 0.0;
   out_6969728399034555931[299] = 0.0;
   out_6969728399034555931[300] = 0.0;
   out_6969728399034555931[301] = 0.0;
   out_6969728399034555931[302] = 0.0;
   out_6969728399034555931[303] = 0.0;
   out_6969728399034555931[304] = 1.0;
   out_6969728399034555931[305] = 0.0;
   out_6969728399034555931[306] = 0.0;
   out_6969728399034555931[307] = 0.0;
   out_6969728399034555931[308] = 0.0;
   out_6969728399034555931[309] = 0.0;
   out_6969728399034555931[310] = 0.0;
   out_6969728399034555931[311] = 0.0;
   out_6969728399034555931[312] = 0.0;
   out_6969728399034555931[313] = 0.0;
   out_6969728399034555931[314] = 0.0;
   out_6969728399034555931[315] = 0.0;
   out_6969728399034555931[316] = 0.0;
   out_6969728399034555931[317] = 0.0;
   out_6969728399034555931[318] = 0.0;
   out_6969728399034555931[319] = 0.0;
   out_6969728399034555931[320] = 0.0;
   out_6969728399034555931[321] = 0.0;
   out_6969728399034555931[322] = 0.0;
   out_6969728399034555931[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_1236007422603849478) {
   out_1236007422603849478[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_1236007422603849478[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_1236007422603849478[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_1236007422603849478[3] = dt*state[12] + state[3];
   out_1236007422603849478[4] = dt*state[13] + state[4];
   out_1236007422603849478[5] = dt*state[14] + state[5];
   out_1236007422603849478[6] = state[6];
   out_1236007422603849478[7] = state[7];
   out_1236007422603849478[8] = state[8];
   out_1236007422603849478[9] = state[9];
   out_1236007422603849478[10] = state[10];
   out_1236007422603849478[11] = state[11];
   out_1236007422603849478[12] = state[12];
   out_1236007422603849478[13] = state[13];
   out_1236007422603849478[14] = state[14];
   out_1236007422603849478[15] = state[15];
   out_1236007422603849478[16] = state[16];
   out_1236007422603849478[17] = state[17];
}
void F_fun(double *state, double dt, double *out_5168773265456939650) {
   out_5168773265456939650[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5168773265456939650[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5168773265456939650[2] = 0;
   out_5168773265456939650[3] = 0;
   out_5168773265456939650[4] = 0;
   out_5168773265456939650[5] = 0;
   out_5168773265456939650[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5168773265456939650[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5168773265456939650[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5168773265456939650[9] = 0;
   out_5168773265456939650[10] = 0;
   out_5168773265456939650[11] = 0;
   out_5168773265456939650[12] = 0;
   out_5168773265456939650[13] = 0;
   out_5168773265456939650[14] = 0;
   out_5168773265456939650[15] = 0;
   out_5168773265456939650[16] = 0;
   out_5168773265456939650[17] = 0;
   out_5168773265456939650[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5168773265456939650[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5168773265456939650[20] = 0;
   out_5168773265456939650[21] = 0;
   out_5168773265456939650[22] = 0;
   out_5168773265456939650[23] = 0;
   out_5168773265456939650[24] = 0;
   out_5168773265456939650[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5168773265456939650[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5168773265456939650[27] = 0;
   out_5168773265456939650[28] = 0;
   out_5168773265456939650[29] = 0;
   out_5168773265456939650[30] = 0;
   out_5168773265456939650[31] = 0;
   out_5168773265456939650[32] = 0;
   out_5168773265456939650[33] = 0;
   out_5168773265456939650[34] = 0;
   out_5168773265456939650[35] = 0;
   out_5168773265456939650[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5168773265456939650[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5168773265456939650[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5168773265456939650[39] = 0;
   out_5168773265456939650[40] = 0;
   out_5168773265456939650[41] = 0;
   out_5168773265456939650[42] = 0;
   out_5168773265456939650[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5168773265456939650[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5168773265456939650[45] = 0;
   out_5168773265456939650[46] = 0;
   out_5168773265456939650[47] = 0;
   out_5168773265456939650[48] = 0;
   out_5168773265456939650[49] = 0;
   out_5168773265456939650[50] = 0;
   out_5168773265456939650[51] = 0;
   out_5168773265456939650[52] = 0;
   out_5168773265456939650[53] = 0;
   out_5168773265456939650[54] = 0;
   out_5168773265456939650[55] = 0;
   out_5168773265456939650[56] = 0;
   out_5168773265456939650[57] = 1;
   out_5168773265456939650[58] = 0;
   out_5168773265456939650[59] = 0;
   out_5168773265456939650[60] = 0;
   out_5168773265456939650[61] = 0;
   out_5168773265456939650[62] = 0;
   out_5168773265456939650[63] = 0;
   out_5168773265456939650[64] = 0;
   out_5168773265456939650[65] = 0;
   out_5168773265456939650[66] = dt;
   out_5168773265456939650[67] = 0;
   out_5168773265456939650[68] = 0;
   out_5168773265456939650[69] = 0;
   out_5168773265456939650[70] = 0;
   out_5168773265456939650[71] = 0;
   out_5168773265456939650[72] = 0;
   out_5168773265456939650[73] = 0;
   out_5168773265456939650[74] = 0;
   out_5168773265456939650[75] = 0;
   out_5168773265456939650[76] = 1;
   out_5168773265456939650[77] = 0;
   out_5168773265456939650[78] = 0;
   out_5168773265456939650[79] = 0;
   out_5168773265456939650[80] = 0;
   out_5168773265456939650[81] = 0;
   out_5168773265456939650[82] = 0;
   out_5168773265456939650[83] = 0;
   out_5168773265456939650[84] = 0;
   out_5168773265456939650[85] = dt;
   out_5168773265456939650[86] = 0;
   out_5168773265456939650[87] = 0;
   out_5168773265456939650[88] = 0;
   out_5168773265456939650[89] = 0;
   out_5168773265456939650[90] = 0;
   out_5168773265456939650[91] = 0;
   out_5168773265456939650[92] = 0;
   out_5168773265456939650[93] = 0;
   out_5168773265456939650[94] = 0;
   out_5168773265456939650[95] = 1;
   out_5168773265456939650[96] = 0;
   out_5168773265456939650[97] = 0;
   out_5168773265456939650[98] = 0;
   out_5168773265456939650[99] = 0;
   out_5168773265456939650[100] = 0;
   out_5168773265456939650[101] = 0;
   out_5168773265456939650[102] = 0;
   out_5168773265456939650[103] = 0;
   out_5168773265456939650[104] = dt;
   out_5168773265456939650[105] = 0;
   out_5168773265456939650[106] = 0;
   out_5168773265456939650[107] = 0;
   out_5168773265456939650[108] = 0;
   out_5168773265456939650[109] = 0;
   out_5168773265456939650[110] = 0;
   out_5168773265456939650[111] = 0;
   out_5168773265456939650[112] = 0;
   out_5168773265456939650[113] = 0;
   out_5168773265456939650[114] = 1;
   out_5168773265456939650[115] = 0;
   out_5168773265456939650[116] = 0;
   out_5168773265456939650[117] = 0;
   out_5168773265456939650[118] = 0;
   out_5168773265456939650[119] = 0;
   out_5168773265456939650[120] = 0;
   out_5168773265456939650[121] = 0;
   out_5168773265456939650[122] = 0;
   out_5168773265456939650[123] = 0;
   out_5168773265456939650[124] = 0;
   out_5168773265456939650[125] = 0;
   out_5168773265456939650[126] = 0;
   out_5168773265456939650[127] = 0;
   out_5168773265456939650[128] = 0;
   out_5168773265456939650[129] = 0;
   out_5168773265456939650[130] = 0;
   out_5168773265456939650[131] = 0;
   out_5168773265456939650[132] = 0;
   out_5168773265456939650[133] = 1;
   out_5168773265456939650[134] = 0;
   out_5168773265456939650[135] = 0;
   out_5168773265456939650[136] = 0;
   out_5168773265456939650[137] = 0;
   out_5168773265456939650[138] = 0;
   out_5168773265456939650[139] = 0;
   out_5168773265456939650[140] = 0;
   out_5168773265456939650[141] = 0;
   out_5168773265456939650[142] = 0;
   out_5168773265456939650[143] = 0;
   out_5168773265456939650[144] = 0;
   out_5168773265456939650[145] = 0;
   out_5168773265456939650[146] = 0;
   out_5168773265456939650[147] = 0;
   out_5168773265456939650[148] = 0;
   out_5168773265456939650[149] = 0;
   out_5168773265456939650[150] = 0;
   out_5168773265456939650[151] = 0;
   out_5168773265456939650[152] = 1;
   out_5168773265456939650[153] = 0;
   out_5168773265456939650[154] = 0;
   out_5168773265456939650[155] = 0;
   out_5168773265456939650[156] = 0;
   out_5168773265456939650[157] = 0;
   out_5168773265456939650[158] = 0;
   out_5168773265456939650[159] = 0;
   out_5168773265456939650[160] = 0;
   out_5168773265456939650[161] = 0;
   out_5168773265456939650[162] = 0;
   out_5168773265456939650[163] = 0;
   out_5168773265456939650[164] = 0;
   out_5168773265456939650[165] = 0;
   out_5168773265456939650[166] = 0;
   out_5168773265456939650[167] = 0;
   out_5168773265456939650[168] = 0;
   out_5168773265456939650[169] = 0;
   out_5168773265456939650[170] = 0;
   out_5168773265456939650[171] = 1;
   out_5168773265456939650[172] = 0;
   out_5168773265456939650[173] = 0;
   out_5168773265456939650[174] = 0;
   out_5168773265456939650[175] = 0;
   out_5168773265456939650[176] = 0;
   out_5168773265456939650[177] = 0;
   out_5168773265456939650[178] = 0;
   out_5168773265456939650[179] = 0;
   out_5168773265456939650[180] = 0;
   out_5168773265456939650[181] = 0;
   out_5168773265456939650[182] = 0;
   out_5168773265456939650[183] = 0;
   out_5168773265456939650[184] = 0;
   out_5168773265456939650[185] = 0;
   out_5168773265456939650[186] = 0;
   out_5168773265456939650[187] = 0;
   out_5168773265456939650[188] = 0;
   out_5168773265456939650[189] = 0;
   out_5168773265456939650[190] = 1;
   out_5168773265456939650[191] = 0;
   out_5168773265456939650[192] = 0;
   out_5168773265456939650[193] = 0;
   out_5168773265456939650[194] = 0;
   out_5168773265456939650[195] = 0;
   out_5168773265456939650[196] = 0;
   out_5168773265456939650[197] = 0;
   out_5168773265456939650[198] = 0;
   out_5168773265456939650[199] = 0;
   out_5168773265456939650[200] = 0;
   out_5168773265456939650[201] = 0;
   out_5168773265456939650[202] = 0;
   out_5168773265456939650[203] = 0;
   out_5168773265456939650[204] = 0;
   out_5168773265456939650[205] = 0;
   out_5168773265456939650[206] = 0;
   out_5168773265456939650[207] = 0;
   out_5168773265456939650[208] = 0;
   out_5168773265456939650[209] = 1;
   out_5168773265456939650[210] = 0;
   out_5168773265456939650[211] = 0;
   out_5168773265456939650[212] = 0;
   out_5168773265456939650[213] = 0;
   out_5168773265456939650[214] = 0;
   out_5168773265456939650[215] = 0;
   out_5168773265456939650[216] = 0;
   out_5168773265456939650[217] = 0;
   out_5168773265456939650[218] = 0;
   out_5168773265456939650[219] = 0;
   out_5168773265456939650[220] = 0;
   out_5168773265456939650[221] = 0;
   out_5168773265456939650[222] = 0;
   out_5168773265456939650[223] = 0;
   out_5168773265456939650[224] = 0;
   out_5168773265456939650[225] = 0;
   out_5168773265456939650[226] = 0;
   out_5168773265456939650[227] = 0;
   out_5168773265456939650[228] = 1;
   out_5168773265456939650[229] = 0;
   out_5168773265456939650[230] = 0;
   out_5168773265456939650[231] = 0;
   out_5168773265456939650[232] = 0;
   out_5168773265456939650[233] = 0;
   out_5168773265456939650[234] = 0;
   out_5168773265456939650[235] = 0;
   out_5168773265456939650[236] = 0;
   out_5168773265456939650[237] = 0;
   out_5168773265456939650[238] = 0;
   out_5168773265456939650[239] = 0;
   out_5168773265456939650[240] = 0;
   out_5168773265456939650[241] = 0;
   out_5168773265456939650[242] = 0;
   out_5168773265456939650[243] = 0;
   out_5168773265456939650[244] = 0;
   out_5168773265456939650[245] = 0;
   out_5168773265456939650[246] = 0;
   out_5168773265456939650[247] = 1;
   out_5168773265456939650[248] = 0;
   out_5168773265456939650[249] = 0;
   out_5168773265456939650[250] = 0;
   out_5168773265456939650[251] = 0;
   out_5168773265456939650[252] = 0;
   out_5168773265456939650[253] = 0;
   out_5168773265456939650[254] = 0;
   out_5168773265456939650[255] = 0;
   out_5168773265456939650[256] = 0;
   out_5168773265456939650[257] = 0;
   out_5168773265456939650[258] = 0;
   out_5168773265456939650[259] = 0;
   out_5168773265456939650[260] = 0;
   out_5168773265456939650[261] = 0;
   out_5168773265456939650[262] = 0;
   out_5168773265456939650[263] = 0;
   out_5168773265456939650[264] = 0;
   out_5168773265456939650[265] = 0;
   out_5168773265456939650[266] = 1;
   out_5168773265456939650[267] = 0;
   out_5168773265456939650[268] = 0;
   out_5168773265456939650[269] = 0;
   out_5168773265456939650[270] = 0;
   out_5168773265456939650[271] = 0;
   out_5168773265456939650[272] = 0;
   out_5168773265456939650[273] = 0;
   out_5168773265456939650[274] = 0;
   out_5168773265456939650[275] = 0;
   out_5168773265456939650[276] = 0;
   out_5168773265456939650[277] = 0;
   out_5168773265456939650[278] = 0;
   out_5168773265456939650[279] = 0;
   out_5168773265456939650[280] = 0;
   out_5168773265456939650[281] = 0;
   out_5168773265456939650[282] = 0;
   out_5168773265456939650[283] = 0;
   out_5168773265456939650[284] = 0;
   out_5168773265456939650[285] = 1;
   out_5168773265456939650[286] = 0;
   out_5168773265456939650[287] = 0;
   out_5168773265456939650[288] = 0;
   out_5168773265456939650[289] = 0;
   out_5168773265456939650[290] = 0;
   out_5168773265456939650[291] = 0;
   out_5168773265456939650[292] = 0;
   out_5168773265456939650[293] = 0;
   out_5168773265456939650[294] = 0;
   out_5168773265456939650[295] = 0;
   out_5168773265456939650[296] = 0;
   out_5168773265456939650[297] = 0;
   out_5168773265456939650[298] = 0;
   out_5168773265456939650[299] = 0;
   out_5168773265456939650[300] = 0;
   out_5168773265456939650[301] = 0;
   out_5168773265456939650[302] = 0;
   out_5168773265456939650[303] = 0;
   out_5168773265456939650[304] = 1;
   out_5168773265456939650[305] = 0;
   out_5168773265456939650[306] = 0;
   out_5168773265456939650[307] = 0;
   out_5168773265456939650[308] = 0;
   out_5168773265456939650[309] = 0;
   out_5168773265456939650[310] = 0;
   out_5168773265456939650[311] = 0;
   out_5168773265456939650[312] = 0;
   out_5168773265456939650[313] = 0;
   out_5168773265456939650[314] = 0;
   out_5168773265456939650[315] = 0;
   out_5168773265456939650[316] = 0;
   out_5168773265456939650[317] = 0;
   out_5168773265456939650[318] = 0;
   out_5168773265456939650[319] = 0;
   out_5168773265456939650[320] = 0;
   out_5168773265456939650[321] = 0;
   out_5168773265456939650[322] = 0;
   out_5168773265456939650[323] = 1;
}
void h_4(double *state, double *unused, double *out_5296109952650410830) {
   out_5296109952650410830[0] = state[6] + state[9];
   out_5296109952650410830[1] = state[7] + state[10];
   out_5296109952650410830[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_5914215848697000206) {
   out_5914215848697000206[0] = 0;
   out_5914215848697000206[1] = 0;
   out_5914215848697000206[2] = 0;
   out_5914215848697000206[3] = 0;
   out_5914215848697000206[4] = 0;
   out_5914215848697000206[5] = 0;
   out_5914215848697000206[6] = 1;
   out_5914215848697000206[7] = 0;
   out_5914215848697000206[8] = 0;
   out_5914215848697000206[9] = 1;
   out_5914215848697000206[10] = 0;
   out_5914215848697000206[11] = 0;
   out_5914215848697000206[12] = 0;
   out_5914215848697000206[13] = 0;
   out_5914215848697000206[14] = 0;
   out_5914215848697000206[15] = 0;
   out_5914215848697000206[16] = 0;
   out_5914215848697000206[17] = 0;
   out_5914215848697000206[18] = 0;
   out_5914215848697000206[19] = 0;
   out_5914215848697000206[20] = 0;
   out_5914215848697000206[21] = 0;
   out_5914215848697000206[22] = 0;
   out_5914215848697000206[23] = 0;
   out_5914215848697000206[24] = 0;
   out_5914215848697000206[25] = 1;
   out_5914215848697000206[26] = 0;
   out_5914215848697000206[27] = 0;
   out_5914215848697000206[28] = 1;
   out_5914215848697000206[29] = 0;
   out_5914215848697000206[30] = 0;
   out_5914215848697000206[31] = 0;
   out_5914215848697000206[32] = 0;
   out_5914215848697000206[33] = 0;
   out_5914215848697000206[34] = 0;
   out_5914215848697000206[35] = 0;
   out_5914215848697000206[36] = 0;
   out_5914215848697000206[37] = 0;
   out_5914215848697000206[38] = 0;
   out_5914215848697000206[39] = 0;
   out_5914215848697000206[40] = 0;
   out_5914215848697000206[41] = 0;
   out_5914215848697000206[42] = 0;
   out_5914215848697000206[43] = 0;
   out_5914215848697000206[44] = 1;
   out_5914215848697000206[45] = 0;
   out_5914215848697000206[46] = 0;
   out_5914215848697000206[47] = 1;
   out_5914215848697000206[48] = 0;
   out_5914215848697000206[49] = 0;
   out_5914215848697000206[50] = 0;
   out_5914215848697000206[51] = 0;
   out_5914215848697000206[52] = 0;
   out_5914215848697000206[53] = 0;
}
void h_10(double *state, double *unused, double *out_3519904827121473616) {
   out_3519904827121473616[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_3519904827121473616[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_3519904827121473616[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_952577601439605767) {
   out_952577601439605767[0] = 0;
   out_952577601439605767[1] = 9.8100000000000005*cos(state[1]);
   out_952577601439605767[2] = 0;
   out_952577601439605767[3] = 0;
   out_952577601439605767[4] = -state[8];
   out_952577601439605767[5] = state[7];
   out_952577601439605767[6] = 0;
   out_952577601439605767[7] = state[5];
   out_952577601439605767[8] = -state[4];
   out_952577601439605767[9] = 0;
   out_952577601439605767[10] = 0;
   out_952577601439605767[11] = 0;
   out_952577601439605767[12] = 1;
   out_952577601439605767[13] = 0;
   out_952577601439605767[14] = 0;
   out_952577601439605767[15] = 1;
   out_952577601439605767[16] = 0;
   out_952577601439605767[17] = 0;
   out_952577601439605767[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_952577601439605767[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_952577601439605767[20] = 0;
   out_952577601439605767[21] = state[8];
   out_952577601439605767[22] = 0;
   out_952577601439605767[23] = -state[6];
   out_952577601439605767[24] = -state[5];
   out_952577601439605767[25] = 0;
   out_952577601439605767[26] = state[3];
   out_952577601439605767[27] = 0;
   out_952577601439605767[28] = 0;
   out_952577601439605767[29] = 0;
   out_952577601439605767[30] = 0;
   out_952577601439605767[31] = 1;
   out_952577601439605767[32] = 0;
   out_952577601439605767[33] = 0;
   out_952577601439605767[34] = 1;
   out_952577601439605767[35] = 0;
   out_952577601439605767[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_952577601439605767[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_952577601439605767[38] = 0;
   out_952577601439605767[39] = -state[7];
   out_952577601439605767[40] = state[6];
   out_952577601439605767[41] = 0;
   out_952577601439605767[42] = state[4];
   out_952577601439605767[43] = -state[3];
   out_952577601439605767[44] = 0;
   out_952577601439605767[45] = 0;
   out_952577601439605767[46] = 0;
   out_952577601439605767[47] = 0;
   out_952577601439605767[48] = 0;
   out_952577601439605767[49] = 0;
   out_952577601439605767[50] = 1;
   out_952577601439605767[51] = 0;
   out_952577601439605767[52] = 0;
   out_952577601439605767[53] = 1;
}
void h_13(double *state, double *unused, double *out_1248641924569735485) {
   out_1248641924569735485[0] = state[3];
   out_1248641924569735485[1] = state[4];
   out_1248641924569735485[2] = state[5];
}
void H_13(double *state, double *unused, double *out_9126489674029333007) {
   out_9126489674029333007[0] = 0;
   out_9126489674029333007[1] = 0;
   out_9126489674029333007[2] = 0;
   out_9126489674029333007[3] = 1;
   out_9126489674029333007[4] = 0;
   out_9126489674029333007[5] = 0;
   out_9126489674029333007[6] = 0;
   out_9126489674029333007[7] = 0;
   out_9126489674029333007[8] = 0;
   out_9126489674029333007[9] = 0;
   out_9126489674029333007[10] = 0;
   out_9126489674029333007[11] = 0;
   out_9126489674029333007[12] = 0;
   out_9126489674029333007[13] = 0;
   out_9126489674029333007[14] = 0;
   out_9126489674029333007[15] = 0;
   out_9126489674029333007[16] = 0;
   out_9126489674029333007[17] = 0;
   out_9126489674029333007[18] = 0;
   out_9126489674029333007[19] = 0;
   out_9126489674029333007[20] = 0;
   out_9126489674029333007[21] = 0;
   out_9126489674029333007[22] = 1;
   out_9126489674029333007[23] = 0;
   out_9126489674029333007[24] = 0;
   out_9126489674029333007[25] = 0;
   out_9126489674029333007[26] = 0;
   out_9126489674029333007[27] = 0;
   out_9126489674029333007[28] = 0;
   out_9126489674029333007[29] = 0;
   out_9126489674029333007[30] = 0;
   out_9126489674029333007[31] = 0;
   out_9126489674029333007[32] = 0;
   out_9126489674029333007[33] = 0;
   out_9126489674029333007[34] = 0;
   out_9126489674029333007[35] = 0;
   out_9126489674029333007[36] = 0;
   out_9126489674029333007[37] = 0;
   out_9126489674029333007[38] = 0;
   out_9126489674029333007[39] = 0;
   out_9126489674029333007[40] = 0;
   out_9126489674029333007[41] = 1;
   out_9126489674029333007[42] = 0;
   out_9126489674029333007[43] = 0;
   out_9126489674029333007[44] = 0;
   out_9126489674029333007[45] = 0;
   out_9126489674029333007[46] = 0;
   out_9126489674029333007[47] = 0;
   out_9126489674029333007[48] = 0;
   out_9126489674029333007[49] = 0;
   out_9126489674029333007[50] = 0;
   out_9126489674029333007[51] = 0;
   out_9126489674029333007[52] = 0;
   out_9126489674029333007[53] = 0;
}
void h_14(double *state, double *unused, double *out_6137258297331957672) {
   out_6137258297331957672[0] = state[6];
   out_6137258297331957672[1] = state[7];
   out_6137258297331957672[2] = state[8];
}
void H_14(double *state, double *unused, double *out_8569287368673066881) {
   out_8569287368673066881[0] = 0;
   out_8569287368673066881[1] = 0;
   out_8569287368673066881[2] = 0;
   out_8569287368673066881[3] = 0;
   out_8569287368673066881[4] = 0;
   out_8569287368673066881[5] = 0;
   out_8569287368673066881[6] = 1;
   out_8569287368673066881[7] = 0;
   out_8569287368673066881[8] = 0;
   out_8569287368673066881[9] = 0;
   out_8569287368673066881[10] = 0;
   out_8569287368673066881[11] = 0;
   out_8569287368673066881[12] = 0;
   out_8569287368673066881[13] = 0;
   out_8569287368673066881[14] = 0;
   out_8569287368673066881[15] = 0;
   out_8569287368673066881[16] = 0;
   out_8569287368673066881[17] = 0;
   out_8569287368673066881[18] = 0;
   out_8569287368673066881[19] = 0;
   out_8569287368673066881[20] = 0;
   out_8569287368673066881[21] = 0;
   out_8569287368673066881[22] = 0;
   out_8569287368673066881[23] = 0;
   out_8569287368673066881[24] = 0;
   out_8569287368673066881[25] = 1;
   out_8569287368673066881[26] = 0;
   out_8569287368673066881[27] = 0;
   out_8569287368673066881[28] = 0;
   out_8569287368673066881[29] = 0;
   out_8569287368673066881[30] = 0;
   out_8569287368673066881[31] = 0;
   out_8569287368673066881[32] = 0;
   out_8569287368673066881[33] = 0;
   out_8569287368673066881[34] = 0;
   out_8569287368673066881[35] = 0;
   out_8569287368673066881[36] = 0;
   out_8569287368673066881[37] = 0;
   out_8569287368673066881[38] = 0;
   out_8569287368673066881[39] = 0;
   out_8569287368673066881[40] = 0;
   out_8569287368673066881[41] = 0;
   out_8569287368673066881[42] = 0;
   out_8569287368673066881[43] = 0;
   out_8569287368673066881[44] = 1;
   out_8569287368673066881[45] = 0;
   out_8569287368673066881[46] = 0;
   out_8569287368673066881[47] = 0;
   out_8569287368673066881[48] = 0;
   out_8569287368673066881[49] = 0;
   out_8569287368673066881[50] = 0;
   out_8569287368673066881[51] = 0;
   out_8569287368673066881[52] = 0;
   out_8569287368673066881[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_7855544638909347154) {
  err_fun(nom_x, delta_x, out_7855544638909347154);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_8154377992469345659) {
  inv_err_fun(nom_x, true_x, out_8154377992469345659);
}
void pose_H_mod_fun(double *state, double *out_6969728399034555931) {
  H_mod_fun(state, out_6969728399034555931);
}
void pose_f_fun(double *state, double dt, double *out_1236007422603849478) {
  f_fun(state,  dt, out_1236007422603849478);
}
void pose_F_fun(double *state, double dt, double *out_5168773265456939650) {
  F_fun(state,  dt, out_5168773265456939650);
}
void pose_h_4(double *state, double *unused, double *out_5296109952650410830) {
  h_4(state, unused, out_5296109952650410830);
}
void pose_H_4(double *state, double *unused, double *out_5914215848697000206) {
  H_4(state, unused, out_5914215848697000206);
}
void pose_h_10(double *state, double *unused, double *out_3519904827121473616) {
  h_10(state, unused, out_3519904827121473616);
}
void pose_H_10(double *state, double *unused, double *out_952577601439605767) {
  H_10(state, unused, out_952577601439605767);
}
void pose_h_13(double *state, double *unused, double *out_1248641924569735485) {
  h_13(state, unused, out_1248641924569735485);
}
void pose_H_13(double *state, double *unused, double *out_9126489674029333007) {
  H_13(state, unused, out_9126489674029333007);
}
void pose_h_14(double *state, double *unused, double *out_6137258297331957672) {
  h_14(state, unused, out_6137258297331957672);
}
void pose_H_14(double *state, double *unused, double *out_8569287368673066881) {
  H_14(state, unused, out_8569287368673066881);
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
