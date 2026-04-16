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
void err_fun(double *nom_x, double *delta_x, double *out_5882928859993581409) {
   out_5882928859993581409[0] = delta_x[0] + nom_x[0];
   out_5882928859993581409[1] = delta_x[1] + nom_x[1];
   out_5882928859993581409[2] = delta_x[2] + nom_x[2];
   out_5882928859993581409[3] = delta_x[3] + nom_x[3];
   out_5882928859993581409[4] = delta_x[4] + nom_x[4];
   out_5882928859993581409[5] = delta_x[5] + nom_x[5];
   out_5882928859993581409[6] = delta_x[6] + nom_x[6];
   out_5882928859993581409[7] = delta_x[7] + nom_x[7];
   out_5882928859993581409[8] = delta_x[8] + nom_x[8];
   out_5882928859993581409[9] = delta_x[9] + nom_x[9];
   out_5882928859993581409[10] = delta_x[10] + nom_x[10];
   out_5882928859993581409[11] = delta_x[11] + nom_x[11];
   out_5882928859993581409[12] = delta_x[12] + nom_x[12];
   out_5882928859993581409[13] = delta_x[13] + nom_x[13];
   out_5882928859993581409[14] = delta_x[14] + nom_x[14];
   out_5882928859993581409[15] = delta_x[15] + nom_x[15];
   out_5882928859993581409[16] = delta_x[16] + nom_x[16];
   out_5882928859993581409[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1648621671757242144) {
   out_1648621671757242144[0] = -nom_x[0] + true_x[0];
   out_1648621671757242144[1] = -nom_x[1] + true_x[1];
   out_1648621671757242144[2] = -nom_x[2] + true_x[2];
   out_1648621671757242144[3] = -nom_x[3] + true_x[3];
   out_1648621671757242144[4] = -nom_x[4] + true_x[4];
   out_1648621671757242144[5] = -nom_x[5] + true_x[5];
   out_1648621671757242144[6] = -nom_x[6] + true_x[6];
   out_1648621671757242144[7] = -nom_x[7] + true_x[7];
   out_1648621671757242144[8] = -nom_x[8] + true_x[8];
   out_1648621671757242144[9] = -nom_x[9] + true_x[9];
   out_1648621671757242144[10] = -nom_x[10] + true_x[10];
   out_1648621671757242144[11] = -nom_x[11] + true_x[11];
   out_1648621671757242144[12] = -nom_x[12] + true_x[12];
   out_1648621671757242144[13] = -nom_x[13] + true_x[13];
   out_1648621671757242144[14] = -nom_x[14] + true_x[14];
   out_1648621671757242144[15] = -nom_x[15] + true_x[15];
   out_1648621671757242144[16] = -nom_x[16] + true_x[16];
   out_1648621671757242144[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_5699029555239033244) {
   out_5699029555239033244[0] = 1.0;
   out_5699029555239033244[1] = 0.0;
   out_5699029555239033244[2] = 0.0;
   out_5699029555239033244[3] = 0.0;
   out_5699029555239033244[4] = 0.0;
   out_5699029555239033244[5] = 0.0;
   out_5699029555239033244[6] = 0.0;
   out_5699029555239033244[7] = 0.0;
   out_5699029555239033244[8] = 0.0;
   out_5699029555239033244[9] = 0.0;
   out_5699029555239033244[10] = 0.0;
   out_5699029555239033244[11] = 0.0;
   out_5699029555239033244[12] = 0.0;
   out_5699029555239033244[13] = 0.0;
   out_5699029555239033244[14] = 0.0;
   out_5699029555239033244[15] = 0.0;
   out_5699029555239033244[16] = 0.0;
   out_5699029555239033244[17] = 0.0;
   out_5699029555239033244[18] = 0.0;
   out_5699029555239033244[19] = 1.0;
   out_5699029555239033244[20] = 0.0;
   out_5699029555239033244[21] = 0.0;
   out_5699029555239033244[22] = 0.0;
   out_5699029555239033244[23] = 0.0;
   out_5699029555239033244[24] = 0.0;
   out_5699029555239033244[25] = 0.0;
   out_5699029555239033244[26] = 0.0;
   out_5699029555239033244[27] = 0.0;
   out_5699029555239033244[28] = 0.0;
   out_5699029555239033244[29] = 0.0;
   out_5699029555239033244[30] = 0.0;
   out_5699029555239033244[31] = 0.0;
   out_5699029555239033244[32] = 0.0;
   out_5699029555239033244[33] = 0.0;
   out_5699029555239033244[34] = 0.0;
   out_5699029555239033244[35] = 0.0;
   out_5699029555239033244[36] = 0.0;
   out_5699029555239033244[37] = 0.0;
   out_5699029555239033244[38] = 1.0;
   out_5699029555239033244[39] = 0.0;
   out_5699029555239033244[40] = 0.0;
   out_5699029555239033244[41] = 0.0;
   out_5699029555239033244[42] = 0.0;
   out_5699029555239033244[43] = 0.0;
   out_5699029555239033244[44] = 0.0;
   out_5699029555239033244[45] = 0.0;
   out_5699029555239033244[46] = 0.0;
   out_5699029555239033244[47] = 0.0;
   out_5699029555239033244[48] = 0.0;
   out_5699029555239033244[49] = 0.0;
   out_5699029555239033244[50] = 0.0;
   out_5699029555239033244[51] = 0.0;
   out_5699029555239033244[52] = 0.0;
   out_5699029555239033244[53] = 0.0;
   out_5699029555239033244[54] = 0.0;
   out_5699029555239033244[55] = 0.0;
   out_5699029555239033244[56] = 0.0;
   out_5699029555239033244[57] = 1.0;
   out_5699029555239033244[58] = 0.0;
   out_5699029555239033244[59] = 0.0;
   out_5699029555239033244[60] = 0.0;
   out_5699029555239033244[61] = 0.0;
   out_5699029555239033244[62] = 0.0;
   out_5699029555239033244[63] = 0.0;
   out_5699029555239033244[64] = 0.0;
   out_5699029555239033244[65] = 0.0;
   out_5699029555239033244[66] = 0.0;
   out_5699029555239033244[67] = 0.0;
   out_5699029555239033244[68] = 0.0;
   out_5699029555239033244[69] = 0.0;
   out_5699029555239033244[70] = 0.0;
   out_5699029555239033244[71] = 0.0;
   out_5699029555239033244[72] = 0.0;
   out_5699029555239033244[73] = 0.0;
   out_5699029555239033244[74] = 0.0;
   out_5699029555239033244[75] = 0.0;
   out_5699029555239033244[76] = 1.0;
   out_5699029555239033244[77] = 0.0;
   out_5699029555239033244[78] = 0.0;
   out_5699029555239033244[79] = 0.0;
   out_5699029555239033244[80] = 0.0;
   out_5699029555239033244[81] = 0.0;
   out_5699029555239033244[82] = 0.0;
   out_5699029555239033244[83] = 0.0;
   out_5699029555239033244[84] = 0.0;
   out_5699029555239033244[85] = 0.0;
   out_5699029555239033244[86] = 0.0;
   out_5699029555239033244[87] = 0.0;
   out_5699029555239033244[88] = 0.0;
   out_5699029555239033244[89] = 0.0;
   out_5699029555239033244[90] = 0.0;
   out_5699029555239033244[91] = 0.0;
   out_5699029555239033244[92] = 0.0;
   out_5699029555239033244[93] = 0.0;
   out_5699029555239033244[94] = 0.0;
   out_5699029555239033244[95] = 1.0;
   out_5699029555239033244[96] = 0.0;
   out_5699029555239033244[97] = 0.0;
   out_5699029555239033244[98] = 0.0;
   out_5699029555239033244[99] = 0.0;
   out_5699029555239033244[100] = 0.0;
   out_5699029555239033244[101] = 0.0;
   out_5699029555239033244[102] = 0.0;
   out_5699029555239033244[103] = 0.0;
   out_5699029555239033244[104] = 0.0;
   out_5699029555239033244[105] = 0.0;
   out_5699029555239033244[106] = 0.0;
   out_5699029555239033244[107] = 0.0;
   out_5699029555239033244[108] = 0.0;
   out_5699029555239033244[109] = 0.0;
   out_5699029555239033244[110] = 0.0;
   out_5699029555239033244[111] = 0.0;
   out_5699029555239033244[112] = 0.0;
   out_5699029555239033244[113] = 0.0;
   out_5699029555239033244[114] = 1.0;
   out_5699029555239033244[115] = 0.0;
   out_5699029555239033244[116] = 0.0;
   out_5699029555239033244[117] = 0.0;
   out_5699029555239033244[118] = 0.0;
   out_5699029555239033244[119] = 0.0;
   out_5699029555239033244[120] = 0.0;
   out_5699029555239033244[121] = 0.0;
   out_5699029555239033244[122] = 0.0;
   out_5699029555239033244[123] = 0.0;
   out_5699029555239033244[124] = 0.0;
   out_5699029555239033244[125] = 0.0;
   out_5699029555239033244[126] = 0.0;
   out_5699029555239033244[127] = 0.0;
   out_5699029555239033244[128] = 0.0;
   out_5699029555239033244[129] = 0.0;
   out_5699029555239033244[130] = 0.0;
   out_5699029555239033244[131] = 0.0;
   out_5699029555239033244[132] = 0.0;
   out_5699029555239033244[133] = 1.0;
   out_5699029555239033244[134] = 0.0;
   out_5699029555239033244[135] = 0.0;
   out_5699029555239033244[136] = 0.0;
   out_5699029555239033244[137] = 0.0;
   out_5699029555239033244[138] = 0.0;
   out_5699029555239033244[139] = 0.0;
   out_5699029555239033244[140] = 0.0;
   out_5699029555239033244[141] = 0.0;
   out_5699029555239033244[142] = 0.0;
   out_5699029555239033244[143] = 0.0;
   out_5699029555239033244[144] = 0.0;
   out_5699029555239033244[145] = 0.0;
   out_5699029555239033244[146] = 0.0;
   out_5699029555239033244[147] = 0.0;
   out_5699029555239033244[148] = 0.0;
   out_5699029555239033244[149] = 0.0;
   out_5699029555239033244[150] = 0.0;
   out_5699029555239033244[151] = 0.0;
   out_5699029555239033244[152] = 1.0;
   out_5699029555239033244[153] = 0.0;
   out_5699029555239033244[154] = 0.0;
   out_5699029555239033244[155] = 0.0;
   out_5699029555239033244[156] = 0.0;
   out_5699029555239033244[157] = 0.0;
   out_5699029555239033244[158] = 0.0;
   out_5699029555239033244[159] = 0.0;
   out_5699029555239033244[160] = 0.0;
   out_5699029555239033244[161] = 0.0;
   out_5699029555239033244[162] = 0.0;
   out_5699029555239033244[163] = 0.0;
   out_5699029555239033244[164] = 0.0;
   out_5699029555239033244[165] = 0.0;
   out_5699029555239033244[166] = 0.0;
   out_5699029555239033244[167] = 0.0;
   out_5699029555239033244[168] = 0.0;
   out_5699029555239033244[169] = 0.0;
   out_5699029555239033244[170] = 0.0;
   out_5699029555239033244[171] = 1.0;
   out_5699029555239033244[172] = 0.0;
   out_5699029555239033244[173] = 0.0;
   out_5699029555239033244[174] = 0.0;
   out_5699029555239033244[175] = 0.0;
   out_5699029555239033244[176] = 0.0;
   out_5699029555239033244[177] = 0.0;
   out_5699029555239033244[178] = 0.0;
   out_5699029555239033244[179] = 0.0;
   out_5699029555239033244[180] = 0.0;
   out_5699029555239033244[181] = 0.0;
   out_5699029555239033244[182] = 0.0;
   out_5699029555239033244[183] = 0.0;
   out_5699029555239033244[184] = 0.0;
   out_5699029555239033244[185] = 0.0;
   out_5699029555239033244[186] = 0.0;
   out_5699029555239033244[187] = 0.0;
   out_5699029555239033244[188] = 0.0;
   out_5699029555239033244[189] = 0.0;
   out_5699029555239033244[190] = 1.0;
   out_5699029555239033244[191] = 0.0;
   out_5699029555239033244[192] = 0.0;
   out_5699029555239033244[193] = 0.0;
   out_5699029555239033244[194] = 0.0;
   out_5699029555239033244[195] = 0.0;
   out_5699029555239033244[196] = 0.0;
   out_5699029555239033244[197] = 0.0;
   out_5699029555239033244[198] = 0.0;
   out_5699029555239033244[199] = 0.0;
   out_5699029555239033244[200] = 0.0;
   out_5699029555239033244[201] = 0.0;
   out_5699029555239033244[202] = 0.0;
   out_5699029555239033244[203] = 0.0;
   out_5699029555239033244[204] = 0.0;
   out_5699029555239033244[205] = 0.0;
   out_5699029555239033244[206] = 0.0;
   out_5699029555239033244[207] = 0.0;
   out_5699029555239033244[208] = 0.0;
   out_5699029555239033244[209] = 1.0;
   out_5699029555239033244[210] = 0.0;
   out_5699029555239033244[211] = 0.0;
   out_5699029555239033244[212] = 0.0;
   out_5699029555239033244[213] = 0.0;
   out_5699029555239033244[214] = 0.0;
   out_5699029555239033244[215] = 0.0;
   out_5699029555239033244[216] = 0.0;
   out_5699029555239033244[217] = 0.0;
   out_5699029555239033244[218] = 0.0;
   out_5699029555239033244[219] = 0.0;
   out_5699029555239033244[220] = 0.0;
   out_5699029555239033244[221] = 0.0;
   out_5699029555239033244[222] = 0.0;
   out_5699029555239033244[223] = 0.0;
   out_5699029555239033244[224] = 0.0;
   out_5699029555239033244[225] = 0.0;
   out_5699029555239033244[226] = 0.0;
   out_5699029555239033244[227] = 0.0;
   out_5699029555239033244[228] = 1.0;
   out_5699029555239033244[229] = 0.0;
   out_5699029555239033244[230] = 0.0;
   out_5699029555239033244[231] = 0.0;
   out_5699029555239033244[232] = 0.0;
   out_5699029555239033244[233] = 0.0;
   out_5699029555239033244[234] = 0.0;
   out_5699029555239033244[235] = 0.0;
   out_5699029555239033244[236] = 0.0;
   out_5699029555239033244[237] = 0.0;
   out_5699029555239033244[238] = 0.0;
   out_5699029555239033244[239] = 0.0;
   out_5699029555239033244[240] = 0.0;
   out_5699029555239033244[241] = 0.0;
   out_5699029555239033244[242] = 0.0;
   out_5699029555239033244[243] = 0.0;
   out_5699029555239033244[244] = 0.0;
   out_5699029555239033244[245] = 0.0;
   out_5699029555239033244[246] = 0.0;
   out_5699029555239033244[247] = 1.0;
   out_5699029555239033244[248] = 0.0;
   out_5699029555239033244[249] = 0.0;
   out_5699029555239033244[250] = 0.0;
   out_5699029555239033244[251] = 0.0;
   out_5699029555239033244[252] = 0.0;
   out_5699029555239033244[253] = 0.0;
   out_5699029555239033244[254] = 0.0;
   out_5699029555239033244[255] = 0.0;
   out_5699029555239033244[256] = 0.0;
   out_5699029555239033244[257] = 0.0;
   out_5699029555239033244[258] = 0.0;
   out_5699029555239033244[259] = 0.0;
   out_5699029555239033244[260] = 0.0;
   out_5699029555239033244[261] = 0.0;
   out_5699029555239033244[262] = 0.0;
   out_5699029555239033244[263] = 0.0;
   out_5699029555239033244[264] = 0.0;
   out_5699029555239033244[265] = 0.0;
   out_5699029555239033244[266] = 1.0;
   out_5699029555239033244[267] = 0.0;
   out_5699029555239033244[268] = 0.0;
   out_5699029555239033244[269] = 0.0;
   out_5699029555239033244[270] = 0.0;
   out_5699029555239033244[271] = 0.0;
   out_5699029555239033244[272] = 0.0;
   out_5699029555239033244[273] = 0.0;
   out_5699029555239033244[274] = 0.0;
   out_5699029555239033244[275] = 0.0;
   out_5699029555239033244[276] = 0.0;
   out_5699029555239033244[277] = 0.0;
   out_5699029555239033244[278] = 0.0;
   out_5699029555239033244[279] = 0.0;
   out_5699029555239033244[280] = 0.0;
   out_5699029555239033244[281] = 0.0;
   out_5699029555239033244[282] = 0.0;
   out_5699029555239033244[283] = 0.0;
   out_5699029555239033244[284] = 0.0;
   out_5699029555239033244[285] = 1.0;
   out_5699029555239033244[286] = 0.0;
   out_5699029555239033244[287] = 0.0;
   out_5699029555239033244[288] = 0.0;
   out_5699029555239033244[289] = 0.0;
   out_5699029555239033244[290] = 0.0;
   out_5699029555239033244[291] = 0.0;
   out_5699029555239033244[292] = 0.0;
   out_5699029555239033244[293] = 0.0;
   out_5699029555239033244[294] = 0.0;
   out_5699029555239033244[295] = 0.0;
   out_5699029555239033244[296] = 0.0;
   out_5699029555239033244[297] = 0.0;
   out_5699029555239033244[298] = 0.0;
   out_5699029555239033244[299] = 0.0;
   out_5699029555239033244[300] = 0.0;
   out_5699029555239033244[301] = 0.0;
   out_5699029555239033244[302] = 0.0;
   out_5699029555239033244[303] = 0.0;
   out_5699029555239033244[304] = 1.0;
   out_5699029555239033244[305] = 0.0;
   out_5699029555239033244[306] = 0.0;
   out_5699029555239033244[307] = 0.0;
   out_5699029555239033244[308] = 0.0;
   out_5699029555239033244[309] = 0.0;
   out_5699029555239033244[310] = 0.0;
   out_5699029555239033244[311] = 0.0;
   out_5699029555239033244[312] = 0.0;
   out_5699029555239033244[313] = 0.0;
   out_5699029555239033244[314] = 0.0;
   out_5699029555239033244[315] = 0.0;
   out_5699029555239033244[316] = 0.0;
   out_5699029555239033244[317] = 0.0;
   out_5699029555239033244[318] = 0.0;
   out_5699029555239033244[319] = 0.0;
   out_5699029555239033244[320] = 0.0;
   out_5699029555239033244[321] = 0.0;
   out_5699029555239033244[322] = 0.0;
   out_5699029555239033244[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_96900936455516417) {
   out_96900936455516417[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_96900936455516417[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_96900936455516417[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_96900936455516417[3] = dt*state[12] + state[3];
   out_96900936455516417[4] = dt*state[13] + state[4];
   out_96900936455516417[5] = dt*state[14] + state[5];
   out_96900936455516417[6] = state[6];
   out_96900936455516417[7] = state[7];
   out_96900936455516417[8] = state[8];
   out_96900936455516417[9] = state[9];
   out_96900936455516417[10] = state[10];
   out_96900936455516417[11] = state[11];
   out_96900936455516417[12] = state[12];
   out_96900936455516417[13] = state[13];
   out_96900936455516417[14] = state[14];
   out_96900936455516417[15] = state[15];
   out_96900936455516417[16] = state[16];
   out_96900936455516417[17] = state[17];
}
void F_fun(double *state, double dt, double *out_5331787048708587552) {
   out_5331787048708587552[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5331787048708587552[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5331787048708587552[2] = 0;
   out_5331787048708587552[3] = 0;
   out_5331787048708587552[4] = 0;
   out_5331787048708587552[5] = 0;
   out_5331787048708587552[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5331787048708587552[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5331787048708587552[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5331787048708587552[9] = 0;
   out_5331787048708587552[10] = 0;
   out_5331787048708587552[11] = 0;
   out_5331787048708587552[12] = 0;
   out_5331787048708587552[13] = 0;
   out_5331787048708587552[14] = 0;
   out_5331787048708587552[15] = 0;
   out_5331787048708587552[16] = 0;
   out_5331787048708587552[17] = 0;
   out_5331787048708587552[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5331787048708587552[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5331787048708587552[20] = 0;
   out_5331787048708587552[21] = 0;
   out_5331787048708587552[22] = 0;
   out_5331787048708587552[23] = 0;
   out_5331787048708587552[24] = 0;
   out_5331787048708587552[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5331787048708587552[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5331787048708587552[27] = 0;
   out_5331787048708587552[28] = 0;
   out_5331787048708587552[29] = 0;
   out_5331787048708587552[30] = 0;
   out_5331787048708587552[31] = 0;
   out_5331787048708587552[32] = 0;
   out_5331787048708587552[33] = 0;
   out_5331787048708587552[34] = 0;
   out_5331787048708587552[35] = 0;
   out_5331787048708587552[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5331787048708587552[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5331787048708587552[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5331787048708587552[39] = 0;
   out_5331787048708587552[40] = 0;
   out_5331787048708587552[41] = 0;
   out_5331787048708587552[42] = 0;
   out_5331787048708587552[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5331787048708587552[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5331787048708587552[45] = 0;
   out_5331787048708587552[46] = 0;
   out_5331787048708587552[47] = 0;
   out_5331787048708587552[48] = 0;
   out_5331787048708587552[49] = 0;
   out_5331787048708587552[50] = 0;
   out_5331787048708587552[51] = 0;
   out_5331787048708587552[52] = 0;
   out_5331787048708587552[53] = 0;
   out_5331787048708587552[54] = 0;
   out_5331787048708587552[55] = 0;
   out_5331787048708587552[56] = 0;
   out_5331787048708587552[57] = 1;
   out_5331787048708587552[58] = 0;
   out_5331787048708587552[59] = 0;
   out_5331787048708587552[60] = 0;
   out_5331787048708587552[61] = 0;
   out_5331787048708587552[62] = 0;
   out_5331787048708587552[63] = 0;
   out_5331787048708587552[64] = 0;
   out_5331787048708587552[65] = 0;
   out_5331787048708587552[66] = dt;
   out_5331787048708587552[67] = 0;
   out_5331787048708587552[68] = 0;
   out_5331787048708587552[69] = 0;
   out_5331787048708587552[70] = 0;
   out_5331787048708587552[71] = 0;
   out_5331787048708587552[72] = 0;
   out_5331787048708587552[73] = 0;
   out_5331787048708587552[74] = 0;
   out_5331787048708587552[75] = 0;
   out_5331787048708587552[76] = 1;
   out_5331787048708587552[77] = 0;
   out_5331787048708587552[78] = 0;
   out_5331787048708587552[79] = 0;
   out_5331787048708587552[80] = 0;
   out_5331787048708587552[81] = 0;
   out_5331787048708587552[82] = 0;
   out_5331787048708587552[83] = 0;
   out_5331787048708587552[84] = 0;
   out_5331787048708587552[85] = dt;
   out_5331787048708587552[86] = 0;
   out_5331787048708587552[87] = 0;
   out_5331787048708587552[88] = 0;
   out_5331787048708587552[89] = 0;
   out_5331787048708587552[90] = 0;
   out_5331787048708587552[91] = 0;
   out_5331787048708587552[92] = 0;
   out_5331787048708587552[93] = 0;
   out_5331787048708587552[94] = 0;
   out_5331787048708587552[95] = 1;
   out_5331787048708587552[96] = 0;
   out_5331787048708587552[97] = 0;
   out_5331787048708587552[98] = 0;
   out_5331787048708587552[99] = 0;
   out_5331787048708587552[100] = 0;
   out_5331787048708587552[101] = 0;
   out_5331787048708587552[102] = 0;
   out_5331787048708587552[103] = 0;
   out_5331787048708587552[104] = dt;
   out_5331787048708587552[105] = 0;
   out_5331787048708587552[106] = 0;
   out_5331787048708587552[107] = 0;
   out_5331787048708587552[108] = 0;
   out_5331787048708587552[109] = 0;
   out_5331787048708587552[110] = 0;
   out_5331787048708587552[111] = 0;
   out_5331787048708587552[112] = 0;
   out_5331787048708587552[113] = 0;
   out_5331787048708587552[114] = 1;
   out_5331787048708587552[115] = 0;
   out_5331787048708587552[116] = 0;
   out_5331787048708587552[117] = 0;
   out_5331787048708587552[118] = 0;
   out_5331787048708587552[119] = 0;
   out_5331787048708587552[120] = 0;
   out_5331787048708587552[121] = 0;
   out_5331787048708587552[122] = 0;
   out_5331787048708587552[123] = 0;
   out_5331787048708587552[124] = 0;
   out_5331787048708587552[125] = 0;
   out_5331787048708587552[126] = 0;
   out_5331787048708587552[127] = 0;
   out_5331787048708587552[128] = 0;
   out_5331787048708587552[129] = 0;
   out_5331787048708587552[130] = 0;
   out_5331787048708587552[131] = 0;
   out_5331787048708587552[132] = 0;
   out_5331787048708587552[133] = 1;
   out_5331787048708587552[134] = 0;
   out_5331787048708587552[135] = 0;
   out_5331787048708587552[136] = 0;
   out_5331787048708587552[137] = 0;
   out_5331787048708587552[138] = 0;
   out_5331787048708587552[139] = 0;
   out_5331787048708587552[140] = 0;
   out_5331787048708587552[141] = 0;
   out_5331787048708587552[142] = 0;
   out_5331787048708587552[143] = 0;
   out_5331787048708587552[144] = 0;
   out_5331787048708587552[145] = 0;
   out_5331787048708587552[146] = 0;
   out_5331787048708587552[147] = 0;
   out_5331787048708587552[148] = 0;
   out_5331787048708587552[149] = 0;
   out_5331787048708587552[150] = 0;
   out_5331787048708587552[151] = 0;
   out_5331787048708587552[152] = 1;
   out_5331787048708587552[153] = 0;
   out_5331787048708587552[154] = 0;
   out_5331787048708587552[155] = 0;
   out_5331787048708587552[156] = 0;
   out_5331787048708587552[157] = 0;
   out_5331787048708587552[158] = 0;
   out_5331787048708587552[159] = 0;
   out_5331787048708587552[160] = 0;
   out_5331787048708587552[161] = 0;
   out_5331787048708587552[162] = 0;
   out_5331787048708587552[163] = 0;
   out_5331787048708587552[164] = 0;
   out_5331787048708587552[165] = 0;
   out_5331787048708587552[166] = 0;
   out_5331787048708587552[167] = 0;
   out_5331787048708587552[168] = 0;
   out_5331787048708587552[169] = 0;
   out_5331787048708587552[170] = 0;
   out_5331787048708587552[171] = 1;
   out_5331787048708587552[172] = 0;
   out_5331787048708587552[173] = 0;
   out_5331787048708587552[174] = 0;
   out_5331787048708587552[175] = 0;
   out_5331787048708587552[176] = 0;
   out_5331787048708587552[177] = 0;
   out_5331787048708587552[178] = 0;
   out_5331787048708587552[179] = 0;
   out_5331787048708587552[180] = 0;
   out_5331787048708587552[181] = 0;
   out_5331787048708587552[182] = 0;
   out_5331787048708587552[183] = 0;
   out_5331787048708587552[184] = 0;
   out_5331787048708587552[185] = 0;
   out_5331787048708587552[186] = 0;
   out_5331787048708587552[187] = 0;
   out_5331787048708587552[188] = 0;
   out_5331787048708587552[189] = 0;
   out_5331787048708587552[190] = 1;
   out_5331787048708587552[191] = 0;
   out_5331787048708587552[192] = 0;
   out_5331787048708587552[193] = 0;
   out_5331787048708587552[194] = 0;
   out_5331787048708587552[195] = 0;
   out_5331787048708587552[196] = 0;
   out_5331787048708587552[197] = 0;
   out_5331787048708587552[198] = 0;
   out_5331787048708587552[199] = 0;
   out_5331787048708587552[200] = 0;
   out_5331787048708587552[201] = 0;
   out_5331787048708587552[202] = 0;
   out_5331787048708587552[203] = 0;
   out_5331787048708587552[204] = 0;
   out_5331787048708587552[205] = 0;
   out_5331787048708587552[206] = 0;
   out_5331787048708587552[207] = 0;
   out_5331787048708587552[208] = 0;
   out_5331787048708587552[209] = 1;
   out_5331787048708587552[210] = 0;
   out_5331787048708587552[211] = 0;
   out_5331787048708587552[212] = 0;
   out_5331787048708587552[213] = 0;
   out_5331787048708587552[214] = 0;
   out_5331787048708587552[215] = 0;
   out_5331787048708587552[216] = 0;
   out_5331787048708587552[217] = 0;
   out_5331787048708587552[218] = 0;
   out_5331787048708587552[219] = 0;
   out_5331787048708587552[220] = 0;
   out_5331787048708587552[221] = 0;
   out_5331787048708587552[222] = 0;
   out_5331787048708587552[223] = 0;
   out_5331787048708587552[224] = 0;
   out_5331787048708587552[225] = 0;
   out_5331787048708587552[226] = 0;
   out_5331787048708587552[227] = 0;
   out_5331787048708587552[228] = 1;
   out_5331787048708587552[229] = 0;
   out_5331787048708587552[230] = 0;
   out_5331787048708587552[231] = 0;
   out_5331787048708587552[232] = 0;
   out_5331787048708587552[233] = 0;
   out_5331787048708587552[234] = 0;
   out_5331787048708587552[235] = 0;
   out_5331787048708587552[236] = 0;
   out_5331787048708587552[237] = 0;
   out_5331787048708587552[238] = 0;
   out_5331787048708587552[239] = 0;
   out_5331787048708587552[240] = 0;
   out_5331787048708587552[241] = 0;
   out_5331787048708587552[242] = 0;
   out_5331787048708587552[243] = 0;
   out_5331787048708587552[244] = 0;
   out_5331787048708587552[245] = 0;
   out_5331787048708587552[246] = 0;
   out_5331787048708587552[247] = 1;
   out_5331787048708587552[248] = 0;
   out_5331787048708587552[249] = 0;
   out_5331787048708587552[250] = 0;
   out_5331787048708587552[251] = 0;
   out_5331787048708587552[252] = 0;
   out_5331787048708587552[253] = 0;
   out_5331787048708587552[254] = 0;
   out_5331787048708587552[255] = 0;
   out_5331787048708587552[256] = 0;
   out_5331787048708587552[257] = 0;
   out_5331787048708587552[258] = 0;
   out_5331787048708587552[259] = 0;
   out_5331787048708587552[260] = 0;
   out_5331787048708587552[261] = 0;
   out_5331787048708587552[262] = 0;
   out_5331787048708587552[263] = 0;
   out_5331787048708587552[264] = 0;
   out_5331787048708587552[265] = 0;
   out_5331787048708587552[266] = 1;
   out_5331787048708587552[267] = 0;
   out_5331787048708587552[268] = 0;
   out_5331787048708587552[269] = 0;
   out_5331787048708587552[270] = 0;
   out_5331787048708587552[271] = 0;
   out_5331787048708587552[272] = 0;
   out_5331787048708587552[273] = 0;
   out_5331787048708587552[274] = 0;
   out_5331787048708587552[275] = 0;
   out_5331787048708587552[276] = 0;
   out_5331787048708587552[277] = 0;
   out_5331787048708587552[278] = 0;
   out_5331787048708587552[279] = 0;
   out_5331787048708587552[280] = 0;
   out_5331787048708587552[281] = 0;
   out_5331787048708587552[282] = 0;
   out_5331787048708587552[283] = 0;
   out_5331787048708587552[284] = 0;
   out_5331787048708587552[285] = 1;
   out_5331787048708587552[286] = 0;
   out_5331787048708587552[287] = 0;
   out_5331787048708587552[288] = 0;
   out_5331787048708587552[289] = 0;
   out_5331787048708587552[290] = 0;
   out_5331787048708587552[291] = 0;
   out_5331787048708587552[292] = 0;
   out_5331787048708587552[293] = 0;
   out_5331787048708587552[294] = 0;
   out_5331787048708587552[295] = 0;
   out_5331787048708587552[296] = 0;
   out_5331787048708587552[297] = 0;
   out_5331787048708587552[298] = 0;
   out_5331787048708587552[299] = 0;
   out_5331787048708587552[300] = 0;
   out_5331787048708587552[301] = 0;
   out_5331787048708587552[302] = 0;
   out_5331787048708587552[303] = 0;
   out_5331787048708587552[304] = 1;
   out_5331787048708587552[305] = 0;
   out_5331787048708587552[306] = 0;
   out_5331787048708587552[307] = 0;
   out_5331787048708587552[308] = 0;
   out_5331787048708587552[309] = 0;
   out_5331787048708587552[310] = 0;
   out_5331787048708587552[311] = 0;
   out_5331787048708587552[312] = 0;
   out_5331787048708587552[313] = 0;
   out_5331787048708587552[314] = 0;
   out_5331787048708587552[315] = 0;
   out_5331787048708587552[316] = 0;
   out_5331787048708587552[317] = 0;
   out_5331787048708587552[318] = 0;
   out_5331787048708587552[319] = 0;
   out_5331787048708587552[320] = 0;
   out_5331787048708587552[321] = 0;
   out_5331787048708587552[322] = 0;
   out_5331787048708587552[323] = 1;
}
void h_4(double *state, double *unused, double *out_5826361638936909921) {
   out_5826361638936909921[0] = state[6] + state[9];
   out_5826361638936909921[1] = state[7] + state[10];
   out_5826361638936909921[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_6896977037121931348) {
   out_6896977037121931348[0] = 0;
   out_6896977037121931348[1] = 0;
   out_6896977037121931348[2] = 0;
   out_6896977037121931348[3] = 0;
   out_6896977037121931348[4] = 0;
   out_6896977037121931348[5] = 0;
   out_6896977037121931348[6] = 1;
   out_6896977037121931348[7] = 0;
   out_6896977037121931348[8] = 0;
   out_6896977037121931348[9] = 1;
   out_6896977037121931348[10] = 0;
   out_6896977037121931348[11] = 0;
   out_6896977037121931348[12] = 0;
   out_6896977037121931348[13] = 0;
   out_6896977037121931348[14] = 0;
   out_6896977037121931348[15] = 0;
   out_6896977037121931348[16] = 0;
   out_6896977037121931348[17] = 0;
   out_6896977037121931348[18] = 0;
   out_6896977037121931348[19] = 0;
   out_6896977037121931348[20] = 0;
   out_6896977037121931348[21] = 0;
   out_6896977037121931348[22] = 0;
   out_6896977037121931348[23] = 0;
   out_6896977037121931348[24] = 0;
   out_6896977037121931348[25] = 1;
   out_6896977037121931348[26] = 0;
   out_6896977037121931348[27] = 0;
   out_6896977037121931348[28] = 1;
   out_6896977037121931348[29] = 0;
   out_6896977037121931348[30] = 0;
   out_6896977037121931348[31] = 0;
   out_6896977037121931348[32] = 0;
   out_6896977037121931348[33] = 0;
   out_6896977037121931348[34] = 0;
   out_6896977037121931348[35] = 0;
   out_6896977037121931348[36] = 0;
   out_6896977037121931348[37] = 0;
   out_6896977037121931348[38] = 0;
   out_6896977037121931348[39] = 0;
   out_6896977037121931348[40] = 0;
   out_6896977037121931348[41] = 0;
   out_6896977037121931348[42] = 0;
   out_6896977037121931348[43] = 0;
   out_6896977037121931348[44] = 1;
   out_6896977037121931348[45] = 0;
   out_6896977037121931348[46] = 0;
   out_6896977037121931348[47] = 1;
   out_6896977037121931348[48] = 0;
   out_6896977037121931348[49] = 0;
   out_6896977037121931348[50] = 0;
   out_6896977037121931348[51] = 0;
   out_6896977037121931348[52] = 0;
   out_6896977037121931348[53] = 0;
}
void h_10(double *state, double *unused, double *out_8355050653109599723) {
   out_8355050653109599723[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_8355050653109599723[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_8355050653109599723[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_6486938087483779055) {
   out_6486938087483779055[0] = 0;
   out_6486938087483779055[1] = 9.8100000000000005*cos(state[1]);
   out_6486938087483779055[2] = 0;
   out_6486938087483779055[3] = 0;
   out_6486938087483779055[4] = -state[8];
   out_6486938087483779055[5] = state[7];
   out_6486938087483779055[6] = 0;
   out_6486938087483779055[7] = state[5];
   out_6486938087483779055[8] = -state[4];
   out_6486938087483779055[9] = 0;
   out_6486938087483779055[10] = 0;
   out_6486938087483779055[11] = 0;
   out_6486938087483779055[12] = 1;
   out_6486938087483779055[13] = 0;
   out_6486938087483779055[14] = 0;
   out_6486938087483779055[15] = 1;
   out_6486938087483779055[16] = 0;
   out_6486938087483779055[17] = 0;
   out_6486938087483779055[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_6486938087483779055[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_6486938087483779055[20] = 0;
   out_6486938087483779055[21] = state[8];
   out_6486938087483779055[22] = 0;
   out_6486938087483779055[23] = -state[6];
   out_6486938087483779055[24] = -state[5];
   out_6486938087483779055[25] = 0;
   out_6486938087483779055[26] = state[3];
   out_6486938087483779055[27] = 0;
   out_6486938087483779055[28] = 0;
   out_6486938087483779055[29] = 0;
   out_6486938087483779055[30] = 0;
   out_6486938087483779055[31] = 1;
   out_6486938087483779055[32] = 0;
   out_6486938087483779055[33] = 0;
   out_6486938087483779055[34] = 1;
   out_6486938087483779055[35] = 0;
   out_6486938087483779055[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_6486938087483779055[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_6486938087483779055[38] = 0;
   out_6486938087483779055[39] = -state[7];
   out_6486938087483779055[40] = state[6];
   out_6486938087483779055[41] = 0;
   out_6486938087483779055[42] = state[4];
   out_6486938087483779055[43] = -state[3];
   out_6486938087483779055[44] = 0;
   out_6486938087483779055[45] = 0;
   out_6486938087483779055[46] = 0;
   out_6486938087483779055[47] = 0;
   out_6486938087483779055[48] = 0;
   out_6486938087483779055[49] = 0;
   out_6486938087483779055[50] = 1;
   out_6486938087483779055[51] = 0;
   out_6486938087483779055[52] = 0;
   out_6486938087483779055[53] = 1;
}
void h_13(double *state, double *unused, double *out_6117605580790890395) {
   out_6117605580790890395[0] = state[3];
   out_6117605580790890395[1] = state[4];
   out_6117605580790890395[2] = state[5];
}
void H_13(double *state, double *unused, double *out_3063221573819407324) {
   out_3063221573819407324[0] = 0;
   out_3063221573819407324[1] = 0;
   out_3063221573819407324[2] = 0;
   out_3063221573819407324[3] = 1;
   out_3063221573819407324[4] = 0;
   out_3063221573819407324[5] = 0;
   out_3063221573819407324[6] = 0;
   out_3063221573819407324[7] = 0;
   out_3063221573819407324[8] = 0;
   out_3063221573819407324[9] = 0;
   out_3063221573819407324[10] = 0;
   out_3063221573819407324[11] = 0;
   out_3063221573819407324[12] = 0;
   out_3063221573819407324[13] = 0;
   out_3063221573819407324[14] = 0;
   out_3063221573819407324[15] = 0;
   out_3063221573819407324[16] = 0;
   out_3063221573819407324[17] = 0;
   out_3063221573819407324[18] = 0;
   out_3063221573819407324[19] = 0;
   out_3063221573819407324[20] = 0;
   out_3063221573819407324[21] = 0;
   out_3063221573819407324[22] = 1;
   out_3063221573819407324[23] = 0;
   out_3063221573819407324[24] = 0;
   out_3063221573819407324[25] = 0;
   out_3063221573819407324[26] = 0;
   out_3063221573819407324[27] = 0;
   out_3063221573819407324[28] = 0;
   out_3063221573819407324[29] = 0;
   out_3063221573819407324[30] = 0;
   out_3063221573819407324[31] = 0;
   out_3063221573819407324[32] = 0;
   out_3063221573819407324[33] = 0;
   out_3063221573819407324[34] = 0;
   out_3063221573819407324[35] = 0;
   out_3063221573819407324[36] = 0;
   out_3063221573819407324[37] = 0;
   out_3063221573819407324[38] = 0;
   out_3063221573819407324[39] = 0;
   out_3063221573819407324[40] = 0;
   out_3063221573819407324[41] = 1;
   out_3063221573819407324[42] = 0;
   out_3063221573819407324[43] = 0;
   out_3063221573819407324[44] = 0;
   out_3063221573819407324[45] = 0;
   out_3063221573819407324[46] = 0;
   out_3063221573819407324[47] = 0;
   out_3063221573819407324[48] = 0;
   out_3063221573819407324[49] = 0;
   out_3063221573819407324[50] = 0;
   out_3063221573819407324[51] = 0;
   out_3063221573819407324[52] = 0;
   out_3063221573819407324[53] = 0;
}
void h_14(double *state, double *unused, double *out_3317020926144572200) {
   out_3317020926144572200[0] = state[6];
   out_3317020926144572200[1] = state[7];
   out_3317020926144572200[2] = state[8];
}
void H_14(double *state, double *unused, double *out_3814188604826559052) {
   out_3814188604826559052[0] = 0;
   out_3814188604826559052[1] = 0;
   out_3814188604826559052[2] = 0;
   out_3814188604826559052[3] = 0;
   out_3814188604826559052[4] = 0;
   out_3814188604826559052[5] = 0;
   out_3814188604826559052[6] = 1;
   out_3814188604826559052[7] = 0;
   out_3814188604826559052[8] = 0;
   out_3814188604826559052[9] = 0;
   out_3814188604826559052[10] = 0;
   out_3814188604826559052[11] = 0;
   out_3814188604826559052[12] = 0;
   out_3814188604826559052[13] = 0;
   out_3814188604826559052[14] = 0;
   out_3814188604826559052[15] = 0;
   out_3814188604826559052[16] = 0;
   out_3814188604826559052[17] = 0;
   out_3814188604826559052[18] = 0;
   out_3814188604826559052[19] = 0;
   out_3814188604826559052[20] = 0;
   out_3814188604826559052[21] = 0;
   out_3814188604826559052[22] = 0;
   out_3814188604826559052[23] = 0;
   out_3814188604826559052[24] = 0;
   out_3814188604826559052[25] = 1;
   out_3814188604826559052[26] = 0;
   out_3814188604826559052[27] = 0;
   out_3814188604826559052[28] = 0;
   out_3814188604826559052[29] = 0;
   out_3814188604826559052[30] = 0;
   out_3814188604826559052[31] = 0;
   out_3814188604826559052[32] = 0;
   out_3814188604826559052[33] = 0;
   out_3814188604826559052[34] = 0;
   out_3814188604826559052[35] = 0;
   out_3814188604826559052[36] = 0;
   out_3814188604826559052[37] = 0;
   out_3814188604826559052[38] = 0;
   out_3814188604826559052[39] = 0;
   out_3814188604826559052[40] = 0;
   out_3814188604826559052[41] = 0;
   out_3814188604826559052[42] = 0;
   out_3814188604826559052[43] = 0;
   out_3814188604826559052[44] = 1;
   out_3814188604826559052[45] = 0;
   out_3814188604826559052[46] = 0;
   out_3814188604826559052[47] = 0;
   out_3814188604826559052[48] = 0;
   out_3814188604826559052[49] = 0;
   out_3814188604826559052[50] = 0;
   out_3814188604826559052[51] = 0;
   out_3814188604826559052[52] = 0;
   out_3814188604826559052[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_5882928859993581409) {
  err_fun(nom_x, delta_x, out_5882928859993581409);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1648621671757242144) {
  inv_err_fun(nom_x, true_x, out_1648621671757242144);
}
void pose_H_mod_fun(double *state, double *out_5699029555239033244) {
  H_mod_fun(state, out_5699029555239033244);
}
void pose_f_fun(double *state, double dt, double *out_96900936455516417) {
  f_fun(state,  dt, out_96900936455516417);
}
void pose_F_fun(double *state, double dt, double *out_5331787048708587552) {
  F_fun(state,  dt, out_5331787048708587552);
}
void pose_h_4(double *state, double *unused, double *out_5826361638936909921) {
  h_4(state, unused, out_5826361638936909921);
}
void pose_H_4(double *state, double *unused, double *out_6896977037121931348) {
  H_4(state, unused, out_6896977037121931348);
}
void pose_h_10(double *state, double *unused, double *out_8355050653109599723) {
  h_10(state, unused, out_8355050653109599723);
}
void pose_H_10(double *state, double *unused, double *out_6486938087483779055) {
  H_10(state, unused, out_6486938087483779055);
}
void pose_h_13(double *state, double *unused, double *out_6117605580790890395) {
  h_13(state, unused, out_6117605580790890395);
}
void pose_H_13(double *state, double *unused, double *out_3063221573819407324) {
  H_13(state, unused, out_3063221573819407324);
}
void pose_h_14(double *state, double *unused, double *out_3317020926144572200) {
  h_14(state, unused, out_3317020926144572200);
}
void pose_H_14(double *state, double *unused, double *out_3814188604826559052) {
  H_14(state, unused, out_3814188604826559052);
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
