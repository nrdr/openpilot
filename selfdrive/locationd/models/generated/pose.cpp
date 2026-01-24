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
void err_fun(double *nom_x, double *delta_x, double *out_984663319399588075) {
   out_984663319399588075[0] = delta_x[0] + nom_x[0];
   out_984663319399588075[1] = delta_x[1] + nom_x[1];
   out_984663319399588075[2] = delta_x[2] + nom_x[2];
   out_984663319399588075[3] = delta_x[3] + nom_x[3];
   out_984663319399588075[4] = delta_x[4] + nom_x[4];
   out_984663319399588075[5] = delta_x[5] + nom_x[5];
   out_984663319399588075[6] = delta_x[6] + nom_x[6];
   out_984663319399588075[7] = delta_x[7] + nom_x[7];
   out_984663319399588075[8] = delta_x[8] + nom_x[8];
   out_984663319399588075[9] = delta_x[9] + nom_x[9];
   out_984663319399588075[10] = delta_x[10] + nom_x[10];
   out_984663319399588075[11] = delta_x[11] + nom_x[11];
   out_984663319399588075[12] = delta_x[12] + nom_x[12];
   out_984663319399588075[13] = delta_x[13] + nom_x[13];
   out_984663319399588075[14] = delta_x[14] + nom_x[14];
   out_984663319399588075[15] = delta_x[15] + nom_x[15];
   out_984663319399588075[16] = delta_x[16] + nom_x[16];
   out_984663319399588075[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4620004245498130179) {
   out_4620004245498130179[0] = -nom_x[0] + true_x[0];
   out_4620004245498130179[1] = -nom_x[1] + true_x[1];
   out_4620004245498130179[2] = -nom_x[2] + true_x[2];
   out_4620004245498130179[3] = -nom_x[3] + true_x[3];
   out_4620004245498130179[4] = -nom_x[4] + true_x[4];
   out_4620004245498130179[5] = -nom_x[5] + true_x[5];
   out_4620004245498130179[6] = -nom_x[6] + true_x[6];
   out_4620004245498130179[7] = -nom_x[7] + true_x[7];
   out_4620004245498130179[8] = -nom_x[8] + true_x[8];
   out_4620004245498130179[9] = -nom_x[9] + true_x[9];
   out_4620004245498130179[10] = -nom_x[10] + true_x[10];
   out_4620004245498130179[11] = -nom_x[11] + true_x[11];
   out_4620004245498130179[12] = -nom_x[12] + true_x[12];
   out_4620004245498130179[13] = -nom_x[13] + true_x[13];
   out_4620004245498130179[14] = -nom_x[14] + true_x[14];
   out_4620004245498130179[15] = -nom_x[15] + true_x[15];
   out_4620004245498130179[16] = -nom_x[16] + true_x[16];
   out_4620004245498130179[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_2437383548313402487) {
   out_2437383548313402487[0] = 1.0;
   out_2437383548313402487[1] = 0.0;
   out_2437383548313402487[2] = 0.0;
   out_2437383548313402487[3] = 0.0;
   out_2437383548313402487[4] = 0.0;
   out_2437383548313402487[5] = 0.0;
   out_2437383548313402487[6] = 0.0;
   out_2437383548313402487[7] = 0.0;
   out_2437383548313402487[8] = 0.0;
   out_2437383548313402487[9] = 0.0;
   out_2437383548313402487[10] = 0.0;
   out_2437383548313402487[11] = 0.0;
   out_2437383548313402487[12] = 0.0;
   out_2437383548313402487[13] = 0.0;
   out_2437383548313402487[14] = 0.0;
   out_2437383548313402487[15] = 0.0;
   out_2437383548313402487[16] = 0.0;
   out_2437383548313402487[17] = 0.0;
   out_2437383548313402487[18] = 0.0;
   out_2437383548313402487[19] = 1.0;
   out_2437383548313402487[20] = 0.0;
   out_2437383548313402487[21] = 0.0;
   out_2437383548313402487[22] = 0.0;
   out_2437383548313402487[23] = 0.0;
   out_2437383548313402487[24] = 0.0;
   out_2437383548313402487[25] = 0.0;
   out_2437383548313402487[26] = 0.0;
   out_2437383548313402487[27] = 0.0;
   out_2437383548313402487[28] = 0.0;
   out_2437383548313402487[29] = 0.0;
   out_2437383548313402487[30] = 0.0;
   out_2437383548313402487[31] = 0.0;
   out_2437383548313402487[32] = 0.0;
   out_2437383548313402487[33] = 0.0;
   out_2437383548313402487[34] = 0.0;
   out_2437383548313402487[35] = 0.0;
   out_2437383548313402487[36] = 0.0;
   out_2437383548313402487[37] = 0.0;
   out_2437383548313402487[38] = 1.0;
   out_2437383548313402487[39] = 0.0;
   out_2437383548313402487[40] = 0.0;
   out_2437383548313402487[41] = 0.0;
   out_2437383548313402487[42] = 0.0;
   out_2437383548313402487[43] = 0.0;
   out_2437383548313402487[44] = 0.0;
   out_2437383548313402487[45] = 0.0;
   out_2437383548313402487[46] = 0.0;
   out_2437383548313402487[47] = 0.0;
   out_2437383548313402487[48] = 0.0;
   out_2437383548313402487[49] = 0.0;
   out_2437383548313402487[50] = 0.0;
   out_2437383548313402487[51] = 0.0;
   out_2437383548313402487[52] = 0.0;
   out_2437383548313402487[53] = 0.0;
   out_2437383548313402487[54] = 0.0;
   out_2437383548313402487[55] = 0.0;
   out_2437383548313402487[56] = 0.0;
   out_2437383548313402487[57] = 1.0;
   out_2437383548313402487[58] = 0.0;
   out_2437383548313402487[59] = 0.0;
   out_2437383548313402487[60] = 0.0;
   out_2437383548313402487[61] = 0.0;
   out_2437383548313402487[62] = 0.0;
   out_2437383548313402487[63] = 0.0;
   out_2437383548313402487[64] = 0.0;
   out_2437383548313402487[65] = 0.0;
   out_2437383548313402487[66] = 0.0;
   out_2437383548313402487[67] = 0.0;
   out_2437383548313402487[68] = 0.0;
   out_2437383548313402487[69] = 0.0;
   out_2437383548313402487[70] = 0.0;
   out_2437383548313402487[71] = 0.0;
   out_2437383548313402487[72] = 0.0;
   out_2437383548313402487[73] = 0.0;
   out_2437383548313402487[74] = 0.0;
   out_2437383548313402487[75] = 0.0;
   out_2437383548313402487[76] = 1.0;
   out_2437383548313402487[77] = 0.0;
   out_2437383548313402487[78] = 0.0;
   out_2437383548313402487[79] = 0.0;
   out_2437383548313402487[80] = 0.0;
   out_2437383548313402487[81] = 0.0;
   out_2437383548313402487[82] = 0.0;
   out_2437383548313402487[83] = 0.0;
   out_2437383548313402487[84] = 0.0;
   out_2437383548313402487[85] = 0.0;
   out_2437383548313402487[86] = 0.0;
   out_2437383548313402487[87] = 0.0;
   out_2437383548313402487[88] = 0.0;
   out_2437383548313402487[89] = 0.0;
   out_2437383548313402487[90] = 0.0;
   out_2437383548313402487[91] = 0.0;
   out_2437383548313402487[92] = 0.0;
   out_2437383548313402487[93] = 0.0;
   out_2437383548313402487[94] = 0.0;
   out_2437383548313402487[95] = 1.0;
   out_2437383548313402487[96] = 0.0;
   out_2437383548313402487[97] = 0.0;
   out_2437383548313402487[98] = 0.0;
   out_2437383548313402487[99] = 0.0;
   out_2437383548313402487[100] = 0.0;
   out_2437383548313402487[101] = 0.0;
   out_2437383548313402487[102] = 0.0;
   out_2437383548313402487[103] = 0.0;
   out_2437383548313402487[104] = 0.0;
   out_2437383548313402487[105] = 0.0;
   out_2437383548313402487[106] = 0.0;
   out_2437383548313402487[107] = 0.0;
   out_2437383548313402487[108] = 0.0;
   out_2437383548313402487[109] = 0.0;
   out_2437383548313402487[110] = 0.0;
   out_2437383548313402487[111] = 0.0;
   out_2437383548313402487[112] = 0.0;
   out_2437383548313402487[113] = 0.0;
   out_2437383548313402487[114] = 1.0;
   out_2437383548313402487[115] = 0.0;
   out_2437383548313402487[116] = 0.0;
   out_2437383548313402487[117] = 0.0;
   out_2437383548313402487[118] = 0.0;
   out_2437383548313402487[119] = 0.0;
   out_2437383548313402487[120] = 0.0;
   out_2437383548313402487[121] = 0.0;
   out_2437383548313402487[122] = 0.0;
   out_2437383548313402487[123] = 0.0;
   out_2437383548313402487[124] = 0.0;
   out_2437383548313402487[125] = 0.0;
   out_2437383548313402487[126] = 0.0;
   out_2437383548313402487[127] = 0.0;
   out_2437383548313402487[128] = 0.0;
   out_2437383548313402487[129] = 0.0;
   out_2437383548313402487[130] = 0.0;
   out_2437383548313402487[131] = 0.0;
   out_2437383548313402487[132] = 0.0;
   out_2437383548313402487[133] = 1.0;
   out_2437383548313402487[134] = 0.0;
   out_2437383548313402487[135] = 0.0;
   out_2437383548313402487[136] = 0.0;
   out_2437383548313402487[137] = 0.0;
   out_2437383548313402487[138] = 0.0;
   out_2437383548313402487[139] = 0.0;
   out_2437383548313402487[140] = 0.0;
   out_2437383548313402487[141] = 0.0;
   out_2437383548313402487[142] = 0.0;
   out_2437383548313402487[143] = 0.0;
   out_2437383548313402487[144] = 0.0;
   out_2437383548313402487[145] = 0.0;
   out_2437383548313402487[146] = 0.0;
   out_2437383548313402487[147] = 0.0;
   out_2437383548313402487[148] = 0.0;
   out_2437383548313402487[149] = 0.0;
   out_2437383548313402487[150] = 0.0;
   out_2437383548313402487[151] = 0.0;
   out_2437383548313402487[152] = 1.0;
   out_2437383548313402487[153] = 0.0;
   out_2437383548313402487[154] = 0.0;
   out_2437383548313402487[155] = 0.0;
   out_2437383548313402487[156] = 0.0;
   out_2437383548313402487[157] = 0.0;
   out_2437383548313402487[158] = 0.0;
   out_2437383548313402487[159] = 0.0;
   out_2437383548313402487[160] = 0.0;
   out_2437383548313402487[161] = 0.0;
   out_2437383548313402487[162] = 0.0;
   out_2437383548313402487[163] = 0.0;
   out_2437383548313402487[164] = 0.0;
   out_2437383548313402487[165] = 0.0;
   out_2437383548313402487[166] = 0.0;
   out_2437383548313402487[167] = 0.0;
   out_2437383548313402487[168] = 0.0;
   out_2437383548313402487[169] = 0.0;
   out_2437383548313402487[170] = 0.0;
   out_2437383548313402487[171] = 1.0;
   out_2437383548313402487[172] = 0.0;
   out_2437383548313402487[173] = 0.0;
   out_2437383548313402487[174] = 0.0;
   out_2437383548313402487[175] = 0.0;
   out_2437383548313402487[176] = 0.0;
   out_2437383548313402487[177] = 0.0;
   out_2437383548313402487[178] = 0.0;
   out_2437383548313402487[179] = 0.0;
   out_2437383548313402487[180] = 0.0;
   out_2437383548313402487[181] = 0.0;
   out_2437383548313402487[182] = 0.0;
   out_2437383548313402487[183] = 0.0;
   out_2437383548313402487[184] = 0.0;
   out_2437383548313402487[185] = 0.0;
   out_2437383548313402487[186] = 0.0;
   out_2437383548313402487[187] = 0.0;
   out_2437383548313402487[188] = 0.0;
   out_2437383548313402487[189] = 0.0;
   out_2437383548313402487[190] = 1.0;
   out_2437383548313402487[191] = 0.0;
   out_2437383548313402487[192] = 0.0;
   out_2437383548313402487[193] = 0.0;
   out_2437383548313402487[194] = 0.0;
   out_2437383548313402487[195] = 0.0;
   out_2437383548313402487[196] = 0.0;
   out_2437383548313402487[197] = 0.0;
   out_2437383548313402487[198] = 0.0;
   out_2437383548313402487[199] = 0.0;
   out_2437383548313402487[200] = 0.0;
   out_2437383548313402487[201] = 0.0;
   out_2437383548313402487[202] = 0.0;
   out_2437383548313402487[203] = 0.0;
   out_2437383548313402487[204] = 0.0;
   out_2437383548313402487[205] = 0.0;
   out_2437383548313402487[206] = 0.0;
   out_2437383548313402487[207] = 0.0;
   out_2437383548313402487[208] = 0.0;
   out_2437383548313402487[209] = 1.0;
   out_2437383548313402487[210] = 0.0;
   out_2437383548313402487[211] = 0.0;
   out_2437383548313402487[212] = 0.0;
   out_2437383548313402487[213] = 0.0;
   out_2437383548313402487[214] = 0.0;
   out_2437383548313402487[215] = 0.0;
   out_2437383548313402487[216] = 0.0;
   out_2437383548313402487[217] = 0.0;
   out_2437383548313402487[218] = 0.0;
   out_2437383548313402487[219] = 0.0;
   out_2437383548313402487[220] = 0.0;
   out_2437383548313402487[221] = 0.0;
   out_2437383548313402487[222] = 0.0;
   out_2437383548313402487[223] = 0.0;
   out_2437383548313402487[224] = 0.0;
   out_2437383548313402487[225] = 0.0;
   out_2437383548313402487[226] = 0.0;
   out_2437383548313402487[227] = 0.0;
   out_2437383548313402487[228] = 1.0;
   out_2437383548313402487[229] = 0.0;
   out_2437383548313402487[230] = 0.0;
   out_2437383548313402487[231] = 0.0;
   out_2437383548313402487[232] = 0.0;
   out_2437383548313402487[233] = 0.0;
   out_2437383548313402487[234] = 0.0;
   out_2437383548313402487[235] = 0.0;
   out_2437383548313402487[236] = 0.0;
   out_2437383548313402487[237] = 0.0;
   out_2437383548313402487[238] = 0.0;
   out_2437383548313402487[239] = 0.0;
   out_2437383548313402487[240] = 0.0;
   out_2437383548313402487[241] = 0.0;
   out_2437383548313402487[242] = 0.0;
   out_2437383548313402487[243] = 0.0;
   out_2437383548313402487[244] = 0.0;
   out_2437383548313402487[245] = 0.0;
   out_2437383548313402487[246] = 0.0;
   out_2437383548313402487[247] = 1.0;
   out_2437383548313402487[248] = 0.0;
   out_2437383548313402487[249] = 0.0;
   out_2437383548313402487[250] = 0.0;
   out_2437383548313402487[251] = 0.0;
   out_2437383548313402487[252] = 0.0;
   out_2437383548313402487[253] = 0.0;
   out_2437383548313402487[254] = 0.0;
   out_2437383548313402487[255] = 0.0;
   out_2437383548313402487[256] = 0.0;
   out_2437383548313402487[257] = 0.0;
   out_2437383548313402487[258] = 0.0;
   out_2437383548313402487[259] = 0.0;
   out_2437383548313402487[260] = 0.0;
   out_2437383548313402487[261] = 0.0;
   out_2437383548313402487[262] = 0.0;
   out_2437383548313402487[263] = 0.0;
   out_2437383548313402487[264] = 0.0;
   out_2437383548313402487[265] = 0.0;
   out_2437383548313402487[266] = 1.0;
   out_2437383548313402487[267] = 0.0;
   out_2437383548313402487[268] = 0.0;
   out_2437383548313402487[269] = 0.0;
   out_2437383548313402487[270] = 0.0;
   out_2437383548313402487[271] = 0.0;
   out_2437383548313402487[272] = 0.0;
   out_2437383548313402487[273] = 0.0;
   out_2437383548313402487[274] = 0.0;
   out_2437383548313402487[275] = 0.0;
   out_2437383548313402487[276] = 0.0;
   out_2437383548313402487[277] = 0.0;
   out_2437383548313402487[278] = 0.0;
   out_2437383548313402487[279] = 0.0;
   out_2437383548313402487[280] = 0.0;
   out_2437383548313402487[281] = 0.0;
   out_2437383548313402487[282] = 0.0;
   out_2437383548313402487[283] = 0.0;
   out_2437383548313402487[284] = 0.0;
   out_2437383548313402487[285] = 1.0;
   out_2437383548313402487[286] = 0.0;
   out_2437383548313402487[287] = 0.0;
   out_2437383548313402487[288] = 0.0;
   out_2437383548313402487[289] = 0.0;
   out_2437383548313402487[290] = 0.0;
   out_2437383548313402487[291] = 0.0;
   out_2437383548313402487[292] = 0.0;
   out_2437383548313402487[293] = 0.0;
   out_2437383548313402487[294] = 0.0;
   out_2437383548313402487[295] = 0.0;
   out_2437383548313402487[296] = 0.0;
   out_2437383548313402487[297] = 0.0;
   out_2437383548313402487[298] = 0.0;
   out_2437383548313402487[299] = 0.0;
   out_2437383548313402487[300] = 0.0;
   out_2437383548313402487[301] = 0.0;
   out_2437383548313402487[302] = 0.0;
   out_2437383548313402487[303] = 0.0;
   out_2437383548313402487[304] = 1.0;
   out_2437383548313402487[305] = 0.0;
   out_2437383548313402487[306] = 0.0;
   out_2437383548313402487[307] = 0.0;
   out_2437383548313402487[308] = 0.0;
   out_2437383548313402487[309] = 0.0;
   out_2437383548313402487[310] = 0.0;
   out_2437383548313402487[311] = 0.0;
   out_2437383548313402487[312] = 0.0;
   out_2437383548313402487[313] = 0.0;
   out_2437383548313402487[314] = 0.0;
   out_2437383548313402487[315] = 0.0;
   out_2437383548313402487[316] = 0.0;
   out_2437383548313402487[317] = 0.0;
   out_2437383548313402487[318] = 0.0;
   out_2437383548313402487[319] = 0.0;
   out_2437383548313402487[320] = 0.0;
   out_2437383548313402487[321] = 0.0;
   out_2437383548313402487[322] = 0.0;
   out_2437383548313402487[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_459534224482781003) {
   out_459534224482781003[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_459534224482781003[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_459534224482781003[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_459534224482781003[3] = dt*state[12] + state[3];
   out_459534224482781003[4] = dt*state[13] + state[4];
   out_459534224482781003[5] = dt*state[14] + state[5];
   out_459534224482781003[6] = state[6];
   out_459534224482781003[7] = state[7];
   out_459534224482781003[8] = state[8];
   out_459534224482781003[9] = state[9];
   out_459534224482781003[10] = state[10];
   out_459534224482781003[11] = state[11];
   out_459534224482781003[12] = state[12];
   out_459534224482781003[13] = state[13];
   out_459534224482781003[14] = state[14];
   out_459534224482781003[15] = state[15];
   out_459534224482781003[16] = state[16];
   out_459534224482781003[17] = state[17];
}
void F_fun(double *state, double dt, double *out_269745697958674308) {
   out_269745697958674308[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_269745697958674308[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_269745697958674308[2] = 0;
   out_269745697958674308[3] = 0;
   out_269745697958674308[4] = 0;
   out_269745697958674308[5] = 0;
   out_269745697958674308[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_269745697958674308[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_269745697958674308[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_269745697958674308[9] = 0;
   out_269745697958674308[10] = 0;
   out_269745697958674308[11] = 0;
   out_269745697958674308[12] = 0;
   out_269745697958674308[13] = 0;
   out_269745697958674308[14] = 0;
   out_269745697958674308[15] = 0;
   out_269745697958674308[16] = 0;
   out_269745697958674308[17] = 0;
   out_269745697958674308[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_269745697958674308[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_269745697958674308[20] = 0;
   out_269745697958674308[21] = 0;
   out_269745697958674308[22] = 0;
   out_269745697958674308[23] = 0;
   out_269745697958674308[24] = 0;
   out_269745697958674308[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_269745697958674308[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_269745697958674308[27] = 0;
   out_269745697958674308[28] = 0;
   out_269745697958674308[29] = 0;
   out_269745697958674308[30] = 0;
   out_269745697958674308[31] = 0;
   out_269745697958674308[32] = 0;
   out_269745697958674308[33] = 0;
   out_269745697958674308[34] = 0;
   out_269745697958674308[35] = 0;
   out_269745697958674308[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_269745697958674308[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_269745697958674308[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_269745697958674308[39] = 0;
   out_269745697958674308[40] = 0;
   out_269745697958674308[41] = 0;
   out_269745697958674308[42] = 0;
   out_269745697958674308[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_269745697958674308[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_269745697958674308[45] = 0;
   out_269745697958674308[46] = 0;
   out_269745697958674308[47] = 0;
   out_269745697958674308[48] = 0;
   out_269745697958674308[49] = 0;
   out_269745697958674308[50] = 0;
   out_269745697958674308[51] = 0;
   out_269745697958674308[52] = 0;
   out_269745697958674308[53] = 0;
   out_269745697958674308[54] = 0;
   out_269745697958674308[55] = 0;
   out_269745697958674308[56] = 0;
   out_269745697958674308[57] = 1;
   out_269745697958674308[58] = 0;
   out_269745697958674308[59] = 0;
   out_269745697958674308[60] = 0;
   out_269745697958674308[61] = 0;
   out_269745697958674308[62] = 0;
   out_269745697958674308[63] = 0;
   out_269745697958674308[64] = 0;
   out_269745697958674308[65] = 0;
   out_269745697958674308[66] = dt;
   out_269745697958674308[67] = 0;
   out_269745697958674308[68] = 0;
   out_269745697958674308[69] = 0;
   out_269745697958674308[70] = 0;
   out_269745697958674308[71] = 0;
   out_269745697958674308[72] = 0;
   out_269745697958674308[73] = 0;
   out_269745697958674308[74] = 0;
   out_269745697958674308[75] = 0;
   out_269745697958674308[76] = 1;
   out_269745697958674308[77] = 0;
   out_269745697958674308[78] = 0;
   out_269745697958674308[79] = 0;
   out_269745697958674308[80] = 0;
   out_269745697958674308[81] = 0;
   out_269745697958674308[82] = 0;
   out_269745697958674308[83] = 0;
   out_269745697958674308[84] = 0;
   out_269745697958674308[85] = dt;
   out_269745697958674308[86] = 0;
   out_269745697958674308[87] = 0;
   out_269745697958674308[88] = 0;
   out_269745697958674308[89] = 0;
   out_269745697958674308[90] = 0;
   out_269745697958674308[91] = 0;
   out_269745697958674308[92] = 0;
   out_269745697958674308[93] = 0;
   out_269745697958674308[94] = 0;
   out_269745697958674308[95] = 1;
   out_269745697958674308[96] = 0;
   out_269745697958674308[97] = 0;
   out_269745697958674308[98] = 0;
   out_269745697958674308[99] = 0;
   out_269745697958674308[100] = 0;
   out_269745697958674308[101] = 0;
   out_269745697958674308[102] = 0;
   out_269745697958674308[103] = 0;
   out_269745697958674308[104] = dt;
   out_269745697958674308[105] = 0;
   out_269745697958674308[106] = 0;
   out_269745697958674308[107] = 0;
   out_269745697958674308[108] = 0;
   out_269745697958674308[109] = 0;
   out_269745697958674308[110] = 0;
   out_269745697958674308[111] = 0;
   out_269745697958674308[112] = 0;
   out_269745697958674308[113] = 0;
   out_269745697958674308[114] = 1;
   out_269745697958674308[115] = 0;
   out_269745697958674308[116] = 0;
   out_269745697958674308[117] = 0;
   out_269745697958674308[118] = 0;
   out_269745697958674308[119] = 0;
   out_269745697958674308[120] = 0;
   out_269745697958674308[121] = 0;
   out_269745697958674308[122] = 0;
   out_269745697958674308[123] = 0;
   out_269745697958674308[124] = 0;
   out_269745697958674308[125] = 0;
   out_269745697958674308[126] = 0;
   out_269745697958674308[127] = 0;
   out_269745697958674308[128] = 0;
   out_269745697958674308[129] = 0;
   out_269745697958674308[130] = 0;
   out_269745697958674308[131] = 0;
   out_269745697958674308[132] = 0;
   out_269745697958674308[133] = 1;
   out_269745697958674308[134] = 0;
   out_269745697958674308[135] = 0;
   out_269745697958674308[136] = 0;
   out_269745697958674308[137] = 0;
   out_269745697958674308[138] = 0;
   out_269745697958674308[139] = 0;
   out_269745697958674308[140] = 0;
   out_269745697958674308[141] = 0;
   out_269745697958674308[142] = 0;
   out_269745697958674308[143] = 0;
   out_269745697958674308[144] = 0;
   out_269745697958674308[145] = 0;
   out_269745697958674308[146] = 0;
   out_269745697958674308[147] = 0;
   out_269745697958674308[148] = 0;
   out_269745697958674308[149] = 0;
   out_269745697958674308[150] = 0;
   out_269745697958674308[151] = 0;
   out_269745697958674308[152] = 1;
   out_269745697958674308[153] = 0;
   out_269745697958674308[154] = 0;
   out_269745697958674308[155] = 0;
   out_269745697958674308[156] = 0;
   out_269745697958674308[157] = 0;
   out_269745697958674308[158] = 0;
   out_269745697958674308[159] = 0;
   out_269745697958674308[160] = 0;
   out_269745697958674308[161] = 0;
   out_269745697958674308[162] = 0;
   out_269745697958674308[163] = 0;
   out_269745697958674308[164] = 0;
   out_269745697958674308[165] = 0;
   out_269745697958674308[166] = 0;
   out_269745697958674308[167] = 0;
   out_269745697958674308[168] = 0;
   out_269745697958674308[169] = 0;
   out_269745697958674308[170] = 0;
   out_269745697958674308[171] = 1;
   out_269745697958674308[172] = 0;
   out_269745697958674308[173] = 0;
   out_269745697958674308[174] = 0;
   out_269745697958674308[175] = 0;
   out_269745697958674308[176] = 0;
   out_269745697958674308[177] = 0;
   out_269745697958674308[178] = 0;
   out_269745697958674308[179] = 0;
   out_269745697958674308[180] = 0;
   out_269745697958674308[181] = 0;
   out_269745697958674308[182] = 0;
   out_269745697958674308[183] = 0;
   out_269745697958674308[184] = 0;
   out_269745697958674308[185] = 0;
   out_269745697958674308[186] = 0;
   out_269745697958674308[187] = 0;
   out_269745697958674308[188] = 0;
   out_269745697958674308[189] = 0;
   out_269745697958674308[190] = 1;
   out_269745697958674308[191] = 0;
   out_269745697958674308[192] = 0;
   out_269745697958674308[193] = 0;
   out_269745697958674308[194] = 0;
   out_269745697958674308[195] = 0;
   out_269745697958674308[196] = 0;
   out_269745697958674308[197] = 0;
   out_269745697958674308[198] = 0;
   out_269745697958674308[199] = 0;
   out_269745697958674308[200] = 0;
   out_269745697958674308[201] = 0;
   out_269745697958674308[202] = 0;
   out_269745697958674308[203] = 0;
   out_269745697958674308[204] = 0;
   out_269745697958674308[205] = 0;
   out_269745697958674308[206] = 0;
   out_269745697958674308[207] = 0;
   out_269745697958674308[208] = 0;
   out_269745697958674308[209] = 1;
   out_269745697958674308[210] = 0;
   out_269745697958674308[211] = 0;
   out_269745697958674308[212] = 0;
   out_269745697958674308[213] = 0;
   out_269745697958674308[214] = 0;
   out_269745697958674308[215] = 0;
   out_269745697958674308[216] = 0;
   out_269745697958674308[217] = 0;
   out_269745697958674308[218] = 0;
   out_269745697958674308[219] = 0;
   out_269745697958674308[220] = 0;
   out_269745697958674308[221] = 0;
   out_269745697958674308[222] = 0;
   out_269745697958674308[223] = 0;
   out_269745697958674308[224] = 0;
   out_269745697958674308[225] = 0;
   out_269745697958674308[226] = 0;
   out_269745697958674308[227] = 0;
   out_269745697958674308[228] = 1;
   out_269745697958674308[229] = 0;
   out_269745697958674308[230] = 0;
   out_269745697958674308[231] = 0;
   out_269745697958674308[232] = 0;
   out_269745697958674308[233] = 0;
   out_269745697958674308[234] = 0;
   out_269745697958674308[235] = 0;
   out_269745697958674308[236] = 0;
   out_269745697958674308[237] = 0;
   out_269745697958674308[238] = 0;
   out_269745697958674308[239] = 0;
   out_269745697958674308[240] = 0;
   out_269745697958674308[241] = 0;
   out_269745697958674308[242] = 0;
   out_269745697958674308[243] = 0;
   out_269745697958674308[244] = 0;
   out_269745697958674308[245] = 0;
   out_269745697958674308[246] = 0;
   out_269745697958674308[247] = 1;
   out_269745697958674308[248] = 0;
   out_269745697958674308[249] = 0;
   out_269745697958674308[250] = 0;
   out_269745697958674308[251] = 0;
   out_269745697958674308[252] = 0;
   out_269745697958674308[253] = 0;
   out_269745697958674308[254] = 0;
   out_269745697958674308[255] = 0;
   out_269745697958674308[256] = 0;
   out_269745697958674308[257] = 0;
   out_269745697958674308[258] = 0;
   out_269745697958674308[259] = 0;
   out_269745697958674308[260] = 0;
   out_269745697958674308[261] = 0;
   out_269745697958674308[262] = 0;
   out_269745697958674308[263] = 0;
   out_269745697958674308[264] = 0;
   out_269745697958674308[265] = 0;
   out_269745697958674308[266] = 1;
   out_269745697958674308[267] = 0;
   out_269745697958674308[268] = 0;
   out_269745697958674308[269] = 0;
   out_269745697958674308[270] = 0;
   out_269745697958674308[271] = 0;
   out_269745697958674308[272] = 0;
   out_269745697958674308[273] = 0;
   out_269745697958674308[274] = 0;
   out_269745697958674308[275] = 0;
   out_269745697958674308[276] = 0;
   out_269745697958674308[277] = 0;
   out_269745697958674308[278] = 0;
   out_269745697958674308[279] = 0;
   out_269745697958674308[280] = 0;
   out_269745697958674308[281] = 0;
   out_269745697958674308[282] = 0;
   out_269745697958674308[283] = 0;
   out_269745697958674308[284] = 0;
   out_269745697958674308[285] = 1;
   out_269745697958674308[286] = 0;
   out_269745697958674308[287] = 0;
   out_269745697958674308[288] = 0;
   out_269745697958674308[289] = 0;
   out_269745697958674308[290] = 0;
   out_269745697958674308[291] = 0;
   out_269745697958674308[292] = 0;
   out_269745697958674308[293] = 0;
   out_269745697958674308[294] = 0;
   out_269745697958674308[295] = 0;
   out_269745697958674308[296] = 0;
   out_269745697958674308[297] = 0;
   out_269745697958674308[298] = 0;
   out_269745697958674308[299] = 0;
   out_269745697958674308[300] = 0;
   out_269745697958674308[301] = 0;
   out_269745697958674308[302] = 0;
   out_269745697958674308[303] = 0;
   out_269745697958674308[304] = 1;
   out_269745697958674308[305] = 0;
   out_269745697958674308[306] = 0;
   out_269745697958674308[307] = 0;
   out_269745697958674308[308] = 0;
   out_269745697958674308[309] = 0;
   out_269745697958674308[310] = 0;
   out_269745697958674308[311] = 0;
   out_269745697958674308[312] = 0;
   out_269745697958674308[313] = 0;
   out_269745697958674308[314] = 0;
   out_269745697958674308[315] = 0;
   out_269745697958674308[316] = 0;
   out_269745697958674308[317] = 0;
   out_269745697958674308[318] = 0;
   out_269745697958674308[319] = 0;
   out_269745697958674308[320] = 0;
   out_269745697958674308[321] = 0;
   out_269745697958674308[322] = 0;
   out_269745697958674308[323] = 1;
}
void h_4(double *state, double *unused, double *out_3399047557472824354) {
   out_3399047557472824354[0] = state[6] + state[9];
   out_3399047557472824354[1] = state[7] + state[10];
   out_3399047557472824354[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_3635331030196300591) {
   out_3635331030196300591[0] = 0;
   out_3635331030196300591[1] = 0;
   out_3635331030196300591[2] = 0;
   out_3635331030196300591[3] = 0;
   out_3635331030196300591[4] = 0;
   out_3635331030196300591[5] = 0;
   out_3635331030196300591[6] = 1;
   out_3635331030196300591[7] = 0;
   out_3635331030196300591[8] = 0;
   out_3635331030196300591[9] = 1;
   out_3635331030196300591[10] = 0;
   out_3635331030196300591[11] = 0;
   out_3635331030196300591[12] = 0;
   out_3635331030196300591[13] = 0;
   out_3635331030196300591[14] = 0;
   out_3635331030196300591[15] = 0;
   out_3635331030196300591[16] = 0;
   out_3635331030196300591[17] = 0;
   out_3635331030196300591[18] = 0;
   out_3635331030196300591[19] = 0;
   out_3635331030196300591[20] = 0;
   out_3635331030196300591[21] = 0;
   out_3635331030196300591[22] = 0;
   out_3635331030196300591[23] = 0;
   out_3635331030196300591[24] = 0;
   out_3635331030196300591[25] = 1;
   out_3635331030196300591[26] = 0;
   out_3635331030196300591[27] = 0;
   out_3635331030196300591[28] = 1;
   out_3635331030196300591[29] = 0;
   out_3635331030196300591[30] = 0;
   out_3635331030196300591[31] = 0;
   out_3635331030196300591[32] = 0;
   out_3635331030196300591[33] = 0;
   out_3635331030196300591[34] = 0;
   out_3635331030196300591[35] = 0;
   out_3635331030196300591[36] = 0;
   out_3635331030196300591[37] = 0;
   out_3635331030196300591[38] = 0;
   out_3635331030196300591[39] = 0;
   out_3635331030196300591[40] = 0;
   out_3635331030196300591[41] = 0;
   out_3635331030196300591[42] = 0;
   out_3635331030196300591[43] = 0;
   out_3635331030196300591[44] = 1;
   out_3635331030196300591[45] = 0;
   out_3635331030196300591[46] = 0;
   out_3635331030196300591[47] = 1;
   out_3635331030196300591[48] = 0;
   out_3635331030196300591[49] = 0;
   out_3635331030196300591[50] = 0;
   out_3635331030196300591[51] = 0;
   out_3635331030196300591[52] = 0;
   out_3635331030196300591[53] = 0;
}
void h_10(double *state, double *unused, double *out_2317846875808052133) {
   out_2317846875808052133[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_2317846875808052133[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_2317846875808052133[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_18257956474410646) {
   out_18257956474410646[0] = 0;
   out_18257956474410646[1] = 9.8100000000000005*cos(state[1]);
   out_18257956474410646[2] = 0;
   out_18257956474410646[3] = 0;
   out_18257956474410646[4] = -state[8];
   out_18257956474410646[5] = state[7];
   out_18257956474410646[6] = 0;
   out_18257956474410646[7] = state[5];
   out_18257956474410646[8] = -state[4];
   out_18257956474410646[9] = 0;
   out_18257956474410646[10] = 0;
   out_18257956474410646[11] = 0;
   out_18257956474410646[12] = 1;
   out_18257956474410646[13] = 0;
   out_18257956474410646[14] = 0;
   out_18257956474410646[15] = 1;
   out_18257956474410646[16] = 0;
   out_18257956474410646[17] = 0;
   out_18257956474410646[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_18257956474410646[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_18257956474410646[20] = 0;
   out_18257956474410646[21] = state[8];
   out_18257956474410646[22] = 0;
   out_18257956474410646[23] = -state[6];
   out_18257956474410646[24] = -state[5];
   out_18257956474410646[25] = 0;
   out_18257956474410646[26] = state[3];
   out_18257956474410646[27] = 0;
   out_18257956474410646[28] = 0;
   out_18257956474410646[29] = 0;
   out_18257956474410646[30] = 0;
   out_18257956474410646[31] = 1;
   out_18257956474410646[32] = 0;
   out_18257956474410646[33] = 0;
   out_18257956474410646[34] = 1;
   out_18257956474410646[35] = 0;
   out_18257956474410646[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_18257956474410646[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_18257956474410646[38] = 0;
   out_18257956474410646[39] = -state[7];
   out_18257956474410646[40] = state[6];
   out_18257956474410646[41] = 0;
   out_18257956474410646[42] = state[4];
   out_18257956474410646[43] = -state[3];
   out_18257956474410646[44] = 0;
   out_18257956474410646[45] = 0;
   out_18257956474410646[46] = 0;
   out_18257956474410646[47] = 0;
   out_18257956474410646[48] = 0;
   out_18257956474410646[49] = 0;
   out_18257956474410646[50] = 1;
   out_18257956474410646[51] = 0;
   out_18257956474410646[52] = 0;
   out_18257956474410646[53] = 1;
}
void h_13(double *state, double *unused, double *out_3170935602771856178) {
   out_3170935602771856178[0] = state[3];
   out_3170935602771856178[1] = state[4];
   out_3170935602771856178[2] = state[5];
}
void H_13(double *state, double *unused, double *out_6847604855528633392) {
   out_6847604855528633392[0] = 0;
   out_6847604855528633392[1] = 0;
   out_6847604855528633392[2] = 0;
   out_6847604855528633392[3] = 1;
   out_6847604855528633392[4] = 0;
   out_6847604855528633392[5] = 0;
   out_6847604855528633392[6] = 0;
   out_6847604855528633392[7] = 0;
   out_6847604855528633392[8] = 0;
   out_6847604855528633392[9] = 0;
   out_6847604855528633392[10] = 0;
   out_6847604855528633392[11] = 0;
   out_6847604855528633392[12] = 0;
   out_6847604855528633392[13] = 0;
   out_6847604855528633392[14] = 0;
   out_6847604855528633392[15] = 0;
   out_6847604855528633392[16] = 0;
   out_6847604855528633392[17] = 0;
   out_6847604855528633392[18] = 0;
   out_6847604855528633392[19] = 0;
   out_6847604855528633392[20] = 0;
   out_6847604855528633392[21] = 0;
   out_6847604855528633392[22] = 1;
   out_6847604855528633392[23] = 0;
   out_6847604855528633392[24] = 0;
   out_6847604855528633392[25] = 0;
   out_6847604855528633392[26] = 0;
   out_6847604855528633392[27] = 0;
   out_6847604855528633392[28] = 0;
   out_6847604855528633392[29] = 0;
   out_6847604855528633392[30] = 0;
   out_6847604855528633392[31] = 0;
   out_6847604855528633392[32] = 0;
   out_6847604855528633392[33] = 0;
   out_6847604855528633392[34] = 0;
   out_6847604855528633392[35] = 0;
   out_6847604855528633392[36] = 0;
   out_6847604855528633392[37] = 0;
   out_6847604855528633392[38] = 0;
   out_6847604855528633392[39] = 0;
   out_6847604855528633392[40] = 0;
   out_6847604855528633392[41] = 1;
   out_6847604855528633392[42] = 0;
   out_6847604855528633392[43] = 0;
   out_6847604855528633392[44] = 0;
   out_6847604855528633392[45] = 0;
   out_6847604855528633392[46] = 0;
   out_6847604855528633392[47] = 0;
   out_6847604855528633392[48] = 0;
   out_6847604855528633392[49] = 0;
   out_6847604855528633392[50] = 0;
   out_6847604855528633392[51] = 0;
   out_6847604855528633392[52] = 0;
   out_6847604855528633392[53] = 0;
}
void h_14(double *state, double *unused, double *out_3292020991111463031) {
   out_3292020991111463031[0] = state[6];
   out_3292020991111463031[1] = state[7];
   out_3292020991111463031[2] = state[8];
}
void H_14(double *state, double *unused, double *out_552542597900928295) {
   out_552542597900928295[0] = 0;
   out_552542597900928295[1] = 0;
   out_552542597900928295[2] = 0;
   out_552542597900928295[3] = 0;
   out_552542597900928295[4] = 0;
   out_552542597900928295[5] = 0;
   out_552542597900928295[6] = 1;
   out_552542597900928295[7] = 0;
   out_552542597900928295[8] = 0;
   out_552542597900928295[9] = 0;
   out_552542597900928295[10] = 0;
   out_552542597900928295[11] = 0;
   out_552542597900928295[12] = 0;
   out_552542597900928295[13] = 0;
   out_552542597900928295[14] = 0;
   out_552542597900928295[15] = 0;
   out_552542597900928295[16] = 0;
   out_552542597900928295[17] = 0;
   out_552542597900928295[18] = 0;
   out_552542597900928295[19] = 0;
   out_552542597900928295[20] = 0;
   out_552542597900928295[21] = 0;
   out_552542597900928295[22] = 0;
   out_552542597900928295[23] = 0;
   out_552542597900928295[24] = 0;
   out_552542597900928295[25] = 1;
   out_552542597900928295[26] = 0;
   out_552542597900928295[27] = 0;
   out_552542597900928295[28] = 0;
   out_552542597900928295[29] = 0;
   out_552542597900928295[30] = 0;
   out_552542597900928295[31] = 0;
   out_552542597900928295[32] = 0;
   out_552542597900928295[33] = 0;
   out_552542597900928295[34] = 0;
   out_552542597900928295[35] = 0;
   out_552542597900928295[36] = 0;
   out_552542597900928295[37] = 0;
   out_552542597900928295[38] = 0;
   out_552542597900928295[39] = 0;
   out_552542597900928295[40] = 0;
   out_552542597900928295[41] = 0;
   out_552542597900928295[42] = 0;
   out_552542597900928295[43] = 0;
   out_552542597900928295[44] = 1;
   out_552542597900928295[45] = 0;
   out_552542597900928295[46] = 0;
   out_552542597900928295[47] = 0;
   out_552542597900928295[48] = 0;
   out_552542597900928295[49] = 0;
   out_552542597900928295[50] = 0;
   out_552542597900928295[51] = 0;
   out_552542597900928295[52] = 0;
   out_552542597900928295[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_984663319399588075) {
  err_fun(nom_x, delta_x, out_984663319399588075);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_4620004245498130179) {
  inv_err_fun(nom_x, true_x, out_4620004245498130179);
}
void pose_H_mod_fun(double *state, double *out_2437383548313402487) {
  H_mod_fun(state, out_2437383548313402487);
}
void pose_f_fun(double *state, double dt, double *out_459534224482781003) {
  f_fun(state,  dt, out_459534224482781003);
}
void pose_F_fun(double *state, double dt, double *out_269745697958674308) {
  F_fun(state,  dt, out_269745697958674308);
}
void pose_h_4(double *state, double *unused, double *out_3399047557472824354) {
  h_4(state, unused, out_3399047557472824354);
}
void pose_H_4(double *state, double *unused, double *out_3635331030196300591) {
  H_4(state, unused, out_3635331030196300591);
}
void pose_h_10(double *state, double *unused, double *out_2317846875808052133) {
  h_10(state, unused, out_2317846875808052133);
}
void pose_H_10(double *state, double *unused, double *out_18257956474410646) {
  H_10(state, unused, out_18257956474410646);
}
void pose_h_13(double *state, double *unused, double *out_3170935602771856178) {
  h_13(state, unused, out_3170935602771856178);
}
void pose_H_13(double *state, double *unused, double *out_6847604855528633392) {
  H_13(state, unused, out_6847604855528633392);
}
void pose_h_14(double *state, double *unused, double *out_3292020991111463031) {
  h_14(state, unused, out_3292020991111463031);
}
void pose_H_14(double *state, double *unused, double *out_552542597900928295) {
  H_14(state, unused, out_552542597900928295);
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
