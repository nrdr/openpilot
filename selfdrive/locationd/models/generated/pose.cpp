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
void err_fun(double *nom_x, double *delta_x, double *out_8545056502495144785) {
   out_8545056502495144785[0] = delta_x[0] + nom_x[0];
   out_8545056502495144785[1] = delta_x[1] + nom_x[1];
   out_8545056502495144785[2] = delta_x[2] + nom_x[2];
   out_8545056502495144785[3] = delta_x[3] + nom_x[3];
   out_8545056502495144785[4] = delta_x[4] + nom_x[4];
   out_8545056502495144785[5] = delta_x[5] + nom_x[5];
   out_8545056502495144785[6] = delta_x[6] + nom_x[6];
   out_8545056502495144785[7] = delta_x[7] + nom_x[7];
   out_8545056502495144785[8] = delta_x[8] + nom_x[8];
   out_8545056502495144785[9] = delta_x[9] + nom_x[9];
   out_8545056502495144785[10] = delta_x[10] + nom_x[10];
   out_8545056502495144785[11] = delta_x[11] + nom_x[11];
   out_8545056502495144785[12] = delta_x[12] + nom_x[12];
   out_8545056502495144785[13] = delta_x[13] + nom_x[13];
   out_8545056502495144785[14] = delta_x[14] + nom_x[14];
   out_8545056502495144785[15] = delta_x[15] + nom_x[15];
   out_8545056502495144785[16] = delta_x[16] + nom_x[16];
   out_8545056502495144785[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6519300297558606633) {
   out_6519300297558606633[0] = -nom_x[0] + true_x[0];
   out_6519300297558606633[1] = -nom_x[1] + true_x[1];
   out_6519300297558606633[2] = -nom_x[2] + true_x[2];
   out_6519300297558606633[3] = -nom_x[3] + true_x[3];
   out_6519300297558606633[4] = -nom_x[4] + true_x[4];
   out_6519300297558606633[5] = -nom_x[5] + true_x[5];
   out_6519300297558606633[6] = -nom_x[6] + true_x[6];
   out_6519300297558606633[7] = -nom_x[7] + true_x[7];
   out_6519300297558606633[8] = -nom_x[8] + true_x[8];
   out_6519300297558606633[9] = -nom_x[9] + true_x[9];
   out_6519300297558606633[10] = -nom_x[10] + true_x[10];
   out_6519300297558606633[11] = -nom_x[11] + true_x[11];
   out_6519300297558606633[12] = -nom_x[12] + true_x[12];
   out_6519300297558606633[13] = -nom_x[13] + true_x[13];
   out_6519300297558606633[14] = -nom_x[14] + true_x[14];
   out_6519300297558606633[15] = -nom_x[15] + true_x[15];
   out_6519300297558606633[16] = -nom_x[16] + true_x[16];
   out_6519300297558606633[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_3957552065616892558) {
   out_3957552065616892558[0] = 1.0;
   out_3957552065616892558[1] = 0.0;
   out_3957552065616892558[2] = 0.0;
   out_3957552065616892558[3] = 0.0;
   out_3957552065616892558[4] = 0.0;
   out_3957552065616892558[5] = 0.0;
   out_3957552065616892558[6] = 0.0;
   out_3957552065616892558[7] = 0.0;
   out_3957552065616892558[8] = 0.0;
   out_3957552065616892558[9] = 0.0;
   out_3957552065616892558[10] = 0.0;
   out_3957552065616892558[11] = 0.0;
   out_3957552065616892558[12] = 0.0;
   out_3957552065616892558[13] = 0.0;
   out_3957552065616892558[14] = 0.0;
   out_3957552065616892558[15] = 0.0;
   out_3957552065616892558[16] = 0.0;
   out_3957552065616892558[17] = 0.0;
   out_3957552065616892558[18] = 0.0;
   out_3957552065616892558[19] = 1.0;
   out_3957552065616892558[20] = 0.0;
   out_3957552065616892558[21] = 0.0;
   out_3957552065616892558[22] = 0.0;
   out_3957552065616892558[23] = 0.0;
   out_3957552065616892558[24] = 0.0;
   out_3957552065616892558[25] = 0.0;
   out_3957552065616892558[26] = 0.0;
   out_3957552065616892558[27] = 0.0;
   out_3957552065616892558[28] = 0.0;
   out_3957552065616892558[29] = 0.0;
   out_3957552065616892558[30] = 0.0;
   out_3957552065616892558[31] = 0.0;
   out_3957552065616892558[32] = 0.0;
   out_3957552065616892558[33] = 0.0;
   out_3957552065616892558[34] = 0.0;
   out_3957552065616892558[35] = 0.0;
   out_3957552065616892558[36] = 0.0;
   out_3957552065616892558[37] = 0.0;
   out_3957552065616892558[38] = 1.0;
   out_3957552065616892558[39] = 0.0;
   out_3957552065616892558[40] = 0.0;
   out_3957552065616892558[41] = 0.0;
   out_3957552065616892558[42] = 0.0;
   out_3957552065616892558[43] = 0.0;
   out_3957552065616892558[44] = 0.0;
   out_3957552065616892558[45] = 0.0;
   out_3957552065616892558[46] = 0.0;
   out_3957552065616892558[47] = 0.0;
   out_3957552065616892558[48] = 0.0;
   out_3957552065616892558[49] = 0.0;
   out_3957552065616892558[50] = 0.0;
   out_3957552065616892558[51] = 0.0;
   out_3957552065616892558[52] = 0.0;
   out_3957552065616892558[53] = 0.0;
   out_3957552065616892558[54] = 0.0;
   out_3957552065616892558[55] = 0.0;
   out_3957552065616892558[56] = 0.0;
   out_3957552065616892558[57] = 1.0;
   out_3957552065616892558[58] = 0.0;
   out_3957552065616892558[59] = 0.0;
   out_3957552065616892558[60] = 0.0;
   out_3957552065616892558[61] = 0.0;
   out_3957552065616892558[62] = 0.0;
   out_3957552065616892558[63] = 0.0;
   out_3957552065616892558[64] = 0.0;
   out_3957552065616892558[65] = 0.0;
   out_3957552065616892558[66] = 0.0;
   out_3957552065616892558[67] = 0.0;
   out_3957552065616892558[68] = 0.0;
   out_3957552065616892558[69] = 0.0;
   out_3957552065616892558[70] = 0.0;
   out_3957552065616892558[71] = 0.0;
   out_3957552065616892558[72] = 0.0;
   out_3957552065616892558[73] = 0.0;
   out_3957552065616892558[74] = 0.0;
   out_3957552065616892558[75] = 0.0;
   out_3957552065616892558[76] = 1.0;
   out_3957552065616892558[77] = 0.0;
   out_3957552065616892558[78] = 0.0;
   out_3957552065616892558[79] = 0.0;
   out_3957552065616892558[80] = 0.0;
   out_3957552065616892558[81] = 0.0;
   out_3957552065616892558[82] = 0.0;
   out_3957552065616892558[83] = 0.0;
   out_3957552065616892558[84] = 0.0;
   out_3957552065616892558[85] = 0.0;
   out_3957552065616892558[86] = 0.0;
   out_3957552065616892558[87] = 0.0;
   out_3957552065616892558[88] = 0.0;
   out_3957552065616892558[89] = 0.0;
   out_3957552065616892558[90] = 0.0;
   out_3957552065616892558[91] = 0.0;
   out_3957552065616892558[92] = 0.0;
   out_3957552065616892558[93] = 0.0;
   out_3957552065616892558[94] = 0.0;
   out_3957552065616892558[95] = 1.0;
   out_3957552065616892558[96] = 0.0;
   out_3957552065616892558[97] = 0.0;
   out_3957552065616892558[98] = 0.0;
   out_3957552065616892558[99] = 0.0;
   out_3957552065616892558[100] = 0.0;
   out_3957552065616892558[101] = 0.0;
   out_3957552065616892558[102] = 0.0;
   out_3957552065616892558[103] = 0.0;
   out_3957552065616892558[104] = 0.0;
   out_3957552065616892558[105] = 0.0;
   out_3957552065616892558[106] = 0.0;
   out_3957552065616892558[107] = 0.0;
   out_3957552065616892558[108] = 0.0;
   out_3957552065616892558[109] = 0.0;
   out_3957552065616892558[110] = 0.0;
   out_3957552065616892558[111] = 0.0;
   out_3957552065616892558[112] = 0.0;
   out_3957552065616892558[113] = 0.0;
   out_3957552065616892558[114] = 1.0;
   out_3957552065616892558[115] = 0.0;
   out_3957552065616892558[116] = 0.0;
   out_3957552065616892558[117] = 0.0;
   out_3957552065616892558[118] = 0.0;
   out_3957552065616892558[119] = 0.0;
   out_3957552065616892558[120] = 0.0;
   out_3957552065616892558[121] = 0.0;
   out_3957552065616892558[122] = 0.0;
   out_3957552065616892558[123] = 0.0;
   out_3957552065616892558[124] = 0.0;
   out_3957552065616892558[125] = 0.0;
   out_3957552065616892558[126] = 0.0;
   out_3957552065616892558[127] = 0.0;
   out_3957552065616892558[128] = 0.0;
   out_3957552065616892558[129] = 0.0;
   out_3957552065616892558[130] = 0.0;
   out_3957552065616892558[131] = 0.0;
   out_3957552065616892558[132] = 0.0;
   out_3957552065616892558[133] = 1.0;
   out_3957552065616892558[134] = 0.0;
   out_3957552065616892558[135] = 0.0;
   out_3957552065616892558[136] = 0.0;
   out_3957552065616892558[137] = 0.0;
   out_3957552065616892558[138] = 0.0;
   out_3957552065616892558[139] = 0.0;
   out_3957552065616892558[140] = 0.0;
   out_3957552065616892558[141] = 0.0;
   out_3957552065616892558[142] = 0.0;
   out_3957552065616892558[143] = 0.0;
   out_3957552065616892558[144] = 0.0;
   out_3957552065616892558[145] = 0.0;
   out_3957552065616892558[146] = 0.0;
   out_3957552065616892558[147] = 0.0;
   out_3957552065616892558[148] = 0.0;
   out_3957552065616892558[149] = 0.0;
   out_3957552065616892558[150] = 0.0;
   out_3957552065616892558[151] = 0.0;
   out_3957552065616892558[152] = 1.0;
   out_3957552065616892558[153] = 0.0;
   out_3957552065616892558[154] = 0.0;
   out_3957552065616892558[155] = 0.0;
   out_3957552065616892558[156] = 0.0;
   out_3957552065616892558[157] = 0.0;
   out_3957552065616892558[158] = 0.0;
   out_3957552065616892558[159] = 0.0;
   out_3957552065616892558[160] = 0.0;
   out_3957552065616892558[161] = 0.0;
   out_3957552065616892558[162] = 0.0;
   out_3957552065616892558[163] = 0.0;
   out_3957552065616892558[164] = 0.0;
   out_3957552065616892558[165] = 0.0;
   out_3957552065616892558[166] = 0.0;
   out_3957552065616892558[167] = 0.0;
   out_3957552065616892558[168] = 0.0;
   out_3957552065616892558[169] = 0.0;
   out_3957552065616892558[170] = 0.0;
   out_3957552065616892558[171] = 1.0;
   out_3957552065616892558[172] = 0.0;
   out_3957552065616892558[173] = 0.0;
   out_3957552065616892558[174] = 0.0;
   out_3957552065616892558[175] = 0.0;
   out_3957552065616892558[176] = 0.0;
   out_3957552065616892558[177] = 0.0;
   out_3957552065616892558[178] = 0.0;
   out_3957552065616892558[179] = 0.0;
   out_3957552065616892558[180] = 0.0;
   out_3957552065616892558[181] = 0.0;
   out_3957552065616892558[182] = 0.0;
   out_3957552065616892558[183] = 0.0;
   out_3957552065616892558[184] = 0.0;
   out_3957552065616892558[185] = 0.0;
   out_3957552065616892558[186] = 0.0;
   out_3957552065616892558[187] = 0.0;
   out_3957552065616892558[188] = 0.0;
   out_3957552065616892558[189] = 0.0;
   out_3957552065616892558[190] = 1.0;
   out_3957552065616892558[191] = 0.0;
   out_3957552065616892558[192] = 0.0;
   out_3957552065616892558[193] = 0.0;
   out_3957552065616892558[194] = 0.0;
   out_3957552065616892558[195] = 0.0;
   out_3957552065616892558[196] = 0.0;
   out_3957552065616892558[197] = 0.0;
   out_3957552065616892558[198] = 0.0;
   out_3957552065616892558[199] = 0.0;
   out_3957552065616892558[200] = 0.0;
   out_3957552065616892558[201] = 0.0;
   out_3957552065616892558[202] = 0.0;
   out_3957552065616892558[203] = 0.0;
   out_3957552065616892558[204] = 0.0;
   out_3957552065616892558[205] = 0.0;
   out_3957552065616892558[206] = 0.0;
   out_3957552065616892558[207] = 0.0;
   out_3957552065616892558[208] = 0.0;
   out_3957552065616892558[209] = 1.0;
   out_3957552065616892558[210] = 0.0;
   out_3957552065616892558[211] = 0.0;
   out_3957552065616892558[212] = 0.0;
   out_3957552065616892558[213] = 0.0;
   out_3957552065616892558[214] = 0.0;
   out_3957552065616892558[215] = 0.0;
   out_3957552065616892558[216] = 0.0;
   out_3957552065616892558[217] = 0.0;
   out_3957552065616892558[218] = 0.0;
   out_3957552065616892558[219] = 0.0;
   out_3957552065616892558[220] = 0.0;
   out_3957552065616892558[221] = 0.0;
   out_3957552065616892558[222] = 0.0;
   out_3957552065616892558[223] = 0.0;
   out_3957552065616892558[224] = 0.0;
   out_3957552065616892558[225] = 0.0;
   out_3957552065616892558[226] = 0.0;
   out_3957552065616892558[227] = 0.0;
   out_3957552065616892558[228] = 1.0;
   out_3957552065616892558[229] = 0.0;
   out_3957552065616892558[230] = 0.0;
   out_3957552065616892558[231] = 0.0;
   out_3957552065616892558[232] = 0.0;
   out_3957552065616892558[233] = 0.0;
   out_3957552065616892558[234] = 0.0;
   out_3957552065616892558[235] = 0.0;
   out_3957552065616892558[236] = 0.0;
   out_3957552065616892558[237] = 0.0;
   out_3957552065616892558[238] = 0.0;
   out_3957552065616892558[239] = 0.0;
   out_3957552065616892558[240] = 0.0;
   out_3957552065616892558[241] = 0.0;
   out_3957552065616892558[242] = 0.0;
   out_3957552065616892558[243] = 0.0;
   out_3957552065616892558[244] = 0.0;
   out_3957552065616892558[245] = 0.0;
   out_3957552065616892558[246] = 0.0;
   out_3957552065616892558[247] = 1.0;
   out_3957552065616892558[248] = 0.0;
   out_3957552065616892558[249] = 0.0;
   out_3957552065616892558[250] = 0.0;
   out_3957552065616892558[251] = 0.0;
   out_3957552065616892558[252] = 0.0;
   out_3957552065616892558[253] = 0.0;
   out_3957552065616892558[254] = 0.0;
   out_3957552065616892558[255] = 0.0;
   out_3957552065616892558[256] = 0.0;
   out_3957552065616892558[257] = 0.0;
   out_3957552065616892558[258] = 0.0;
   out_3957552065616892558[259] = 0.0;
   out_3957552065616892558[260] = 0.0;
   out_3957552065616892558[261] = 0.0;
   out_3957552065616892558[262] = 0.0;
   out_3957552065616892558[263] = 0.0;
   out_3957552065616892558[264] = 0.0;
   out_3957552065616892558[265] = 0.0;
   out_3957552065616892558[266] = 1.0;
   out_3957552065616892558[267] = 0.0;
   out_3957552065616892558[268] = 0.0;
   out_3957552065616892558[269] = 0.0;
   out_3957552065616892558[270] = 0.0;
   out_3957552065616892558[271] = 0.0;
   out_3957552065616892558[272] = 0.0;
   out_3957552065616892558[273] = 0.0;
   out_3957552065616892558[274] = 0.0;
   out_3957552065616892558[275] = 0.0;
   out_3957552065616892558[276] = 0.0;
   out_3957552065616892558[277] = 0.0;
   out_3957552065616892558[278] = 0.0;
   out_3957552065616892558[279] = 0.0;
   out_3957552065616892558[280] = 0.0;
   out_3957552065616892558[281] = 0.0;
   out_3957552065616892558[282] = 0.0;
   out_3957552065616892558[283] = 0.0;
   out_3957552065616892558[284] = 0.0;
   out_3957552065616892558[285] = 1.0;
   out_3957552065616892558[286] = 0.0;
   out_3957552065616892558[287] = 0.0;
   out_3957552065616892558[288] = 0.0;
   out_3957552065616892558[289] = 0.0;
   out_3957552065616892558[290] = 0.0;
   out_3957552065616892558[291] = 0.0;
   out_3957552065616892558[292] = 0.0;
   out_3957552065616892558[293] = 0.0;
   out_3957552065616892558[294] = 0.0;
   out_3957552065616892558[295] = 0.0;
   out_3957552065616892558[296] = 0.0;
   out_3957552065616892558[297] = 0.0;
   out_3957552065616892558[298] = 0.0;
   out_3957552065616892558[299] = 0.0;
   out_3957552065616892558[300] = 0.0;
   out_3957552065616892558[301] = 0.0;
   out_3957552065616892558[302] = 0.0;
   out_3957552065616892558[303] = 0.0;
   out_3957552065616892558[304] = 1.0;
   out_3957552065616892558[305] = 0.0;
   out_3957552065616892558[306] = 0.0;
   out_3957552065616892558[307] = 0.0;
   out_3957552065616892558[308] = 0.0;
   out_3957552065616892558[309] = 0.0;
   out_3957552065616892558[310] = 0.0;
   out_3957552065616892558[311] = 0.0;
   out_3957552065616892558[312] = 0.0;
   out_3957552065616892558[313] = 0.0;
   out_3957552065616892558[314] = 0.0;
   out_3957552065616892558[315] = 0.0;
   out_3957552065616892558[316] = 0.0;
   out_3957552065616892558[317] = 0.0;
   out_3957552065616892558[318] = 0.0;
   out_3957552065616892558[319] = 0.0;
   out_3957552065616892558[320] = 0.0;
   out_3957552065616892558[321] = 0.0;
   out_3957552065616892558[322] = 0.0;
   out_3957552065616892558[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_7276726461426660421) {
   out_7276726461426660421[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_7276726461426660421[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_7276726461426660421[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_7276726461426660421[3] = dt*state[12] + state[3];
   out_7276726461426660421[4] = dt*state[13] + state[4];
   out_7276726461426660421[5] = dt*state[14] + state[5];
   out_7276726461426660421[6] = state[6];
   out_7276726461426660421[7] = state[7];
   out_7276726461426660421[8] = state[8];
   out_7276726461426660421[9] = state[9];
   out_7276726461426660421[10] = state[10];
   out_7276726461426660421[11] = state[11];
   out_7276726461426660421[12] = state[12];
   out_7276726461426660421[13] = state[13];
   out_7276726461426660421[14] = state[14];
   out_7276726461426660421[15] = state[15];
   out_7276726461426660421[16] = state[16];
   out_7276726461426660421[17] = state[17];
}
void F_fun(double *state, double dt, double *out_3384456444114612704) {
   out_3384456444114612704[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3384456444114612704[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3384456444114612704[2] = 0;
   out_3384456444114612704[3] = 0;
   out_3384456444114612704[4] = 0;
   out_3384456444114612704[5] = 0;
   out_3384456444114612704[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3384456444114612704[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3384456444114612704[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3384456444114612704[9] = 0;
   out_3384456444114612704[10] = 0;
   out_3384456444114612704[11] = 0;
   out_3384456444114612704[12] = 0;
   out_3384456444114612704[13] = 0;
   out_3384456444114612704[14] = 0;
   out_3384456444114612704[15] = 0;
   out_3384456444114612704[16] = 0;
   out_3384456444114612704[17] = 0;
   out_3384456444114612704[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3384456444114612704[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3384456444114612704[20] = 0;
   out_3384456444114612704[21] = 0;
   out_3384456444114612704[22] = 0;
   out_3384456444114612704[23] = 0;
   out_3384456444114612704[24] = 0;
   out_3384456444114612704[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3384456444114612704[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3384456444114612704[27] = 0;
   out_3384456444114612704[28] = 0;
   out_3384456444114612704[29] = 0;
   out_3384456444114612704[30] = 0;
   out_3384456444114612704[31] = 0;
   out_3384456444114612704[32] = 0;
   out_3384456444114612704[33] = 0;
   out_3384456444114612704[34] = 0;
   out_3384456444114612704[35] = 0;
   out_3384456444114612704[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3384456444114612704[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3384456444114612704[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3384456444114612704[39] = 0;
   out_3384456444114612704[40] = 0;
   out_3384456444114612704[41] = 0;
   out_3384456444114612704[42] = 0;
   out_3384456444114612704[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3384456444114612704[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3384456444114612704[45] = 0;
   out_3384456444114612704[46] = 0;
   out_3384456444114612704[47] = 0;
   out_3384456444114612704[48] = 0;
   out_3384456444114612704[49] = 0;
   out_3384456444114612704[50] = 0;
   out_3384456444114612704[51] = 0;
   out_3384456444114612704[52] = 0;
   out_3384456444114612704[53] = 0;
   out_3384456444114612704[54] = 0;
   out_3384456444114612704[55] = 0;
   out_3384456444114612704[56] = 0;
   out_3384456444114612704[57] = 1;
   out_3384456444114612704[58] = 0;
   out_3384456444114612704[59] = 0;
   out_3384456444114612704[60] = 0;
   out_3384456444114612704[61] = 0;
   out_3384456444114612704[62] = 0;
   out_3384456444114612704[63] = 0;
   out_3384456444114612704[64] = 0;
   out_3384456444114612704[65] = 0;
   out_3384456444114612704[66] = dt;
   out_3384456444114612704[67] = 0;
   out_3384456444114612704[68] = 0;
   out_3384456444114612704[69] = 0;
   out_3384456444114612704[70] = 0;
   out_3384456444114612704[71] = 0;
   out_3384456444114612704[72] = 0;
   out_3384456444114612704[73] = 0;
   out_3384456444114612704[74] = 0;
   out_3384456444114612704[75] = 0;
   out_3384456444114612704[76] = 1;
   out_3384456444114612704[77] = 0;
   out_3384456444114612704[78] = 0;
   out_3384456444114612704[79] = 0;
   out_3384456444114612704[80] = 0;
   out_3384456444114612704[81] = 0;
   out_3384456444114612704[82] = 0;
   out_3384456444114612704[83] = 0;
   out_3384456444114612704[84] = 0;
   out_3384456444114612704[85] = dt;
   out_3384456444114612704[86] = 0;
   out_3384456444114612704[87] = 0;
   out_3384456444114612704[88] = 0;
   out_3384456444114612704[89] = 0;
   out_3384456444114612704[90] = 0;
   out_3384456444114612704[91] = 0;
   out_3384456444114612704[92] = 0;
   out_3384456444114612704[93] = 0;
   out_3384456444114612704[94] = 0;
   out_3384456444114612704[95] = 1;
   out_3384456444114612704[96] = 0;
   out_3384456444114612704[97] = 0;
   out_3384456444114612704[98] = 0;
   out_3384456444114612704[99] = 0;
   out_3384456444114612704[100] = 0;
   out_3384456444114612704[101] = 0;
   out_3384456444114612704[102] = 0;
   out_3384456444114612704[103] = 0;
   out_3384456444114612704[104] = dt;
   out_3384456444114612704[105] = 0;
   out_3384456444114612704[106] = 0;
   out_3384456444114612704[107] = 0;
   out_3384456444114612704[108] = 0;
   out_3384456444114612704[109] = 0;
   out_3384456444114612704[110] = 0;
   out_3384456444114612704[111] = 0;
   out_3384456444114612704[112] = 0;
   out_3384456444114612704[113] = 0;
   out_3384456444114612704[114] = 1;
   out_3384456444114612704[115] = 0;
   out_3384456444114612704[116] = 0;
   out_3384456444114612704[117] = 0;
   out_3384456444114612704[118] = 0;
   out_3384456444114612704[119] = 0;
   out_3384456444114612704[120] = 0;
   out_3384456444114612704[121] = 0;
   out_3384456444114612704[122] = 0;
   out_3384456444114612704[123] = 0;
   out_3384456444114612704[124] = 0;
   out_3384456444114612704[125] = 0;
   out_3384456444114612704[126] = 0;
   out_3384456444114612704[127] = 0;
   out_3384456444114612704[128] = 0;
   out_3384456444114612704[129] = 0;
   out_3384456444114612704[130] = 0;
   out_3384456444114612704[131] = 0;
   out_3384456444114612704[132] = 0;
   out_3384456444114612704[133] = 1;
   out_3384456444114612704[134] = 0;
   out_3384456444114612704[135] = 0;
   out_3384456444114612704[136] = 0;
   out_3384456444114612704[137] = 0;
   out_3384456444114612704[138] = 0;
   out_3384456444114612704[139] = 0;
   out_3384456444114612704[140] = 0;
   out_3384456444114612704[141] = 0;
   out_3384456444114612704[142] = 0;
   out_3384456444114612704[143] = 0;
   out_3384456444114612704[144] = 0;
   out_3384456444114612704[145] = 0;
   out_3384456444114612704[146] = 0;
   out_3384456444114612704[147] = 0;
   out_3384456444114612704[148] = 0;
   out_3384456444114612704[149] = 0;
   out_3384456444114612704[150] = 0;
   out_3384456444114612704[151] = 0;
   out_3384456444114612704[152] = 1;
   out_3384456444114612704[153] = 0;
   out_3384456444114612704[154] = 0;
   out_3384456444114612704[155] = 0;
   out_3384456444114612704[156] = 0;
   out_3384456444114612704[157] = 0;
   out_3384456444114612704[158] = 0;
   out_3384456444114612704[159] = 0;
   out_3384456444114612704[160] = 0;
   out_3384456444114612704[161] = 0;
   out_3384456444114612704[162] = 0;
   out_3384456444114612704[163] = 0;
   out_3384456444114612704[164] = 0;
   out_3384456444114612704[165] = 0;
   out_3384456444114612704[166] = 0;
   out_3384456444114612704[167] = 0;
   out_3384456444114612704[168] = 0;
   out_3384456444114612704[169] = 0;
   out_3384456444114612704[170] = 0;
   out_3384456444114612704[171] = 1;
   out_3384456444114612704[172] = 0;
   out_3384456444114612704[173] = 0;
   out_3384456444114612704[174] = 0;
   out_3384456444114612704[175] = 0;
   out_3384456444114612704[176] = 0;
   out_3384456444114612704[177] = 0;
   out_3384456444114612704[178] = 0;
   out_3384456444114612704[179] = 0;
   out_3384456444114612704[180] = 0;
   out_3384456444114612704[181] = 0;
   out_3384456444114612704[182] = 0;
   out_3384456444114612704[183] = 0;
   out_3384456444114612704[184] = 0;
   out_3384456444114612704[185] = 0;
   out_3384456444114612704[186] = 0;
   out_3384456444114612704[187] = 0;
   out_3384456444114612704[188] = 0;
   out_3384456444114612704[189] = 0;
   out_3384456444114612704[190] = 1;
   out_3384456444114612704[191] = 0;
   out_3384456444114612704[192] = 0;
   out_3384456444114612704[193] = 0;
   out_3384456444114612704[194] = 0;
   out_3384456444114612704[195] = 0;
   out_3384456444114612704[196] = 0;
   out_3384456444114612704[197] = 0;
   out_3384456444114612704[198] = 0;
   out_3384456444114612704[199] = 0;
   out_3384456444114612704[200] = 0;
   out_3384456444114612704[201] = 0;
   out_3384456444114612704[202] = 0;
   out_3384456444114612704[203] = 0;
   out_3384456444114612704[204] = 0;
   out_3384456444114612704[205] = 0;
   out_3384456444114612704[206] = 0;
   out_3384456444114612704[207] = 0;
   out_3384456444114612704[208] = 0;
   out_3384456444114612704[209] = 1;
   out_3384456444114612704[210] = 0;
   out_3384456444114612704[211] = 0;
   out_3384456444114612704[212] = 0;
   out_3384456444114612704[213] = 0;
   out_3384456444114612704[214] = 0;
   out_3384456444114612704[215] = 0;
   out_3384456444114612704[216] = 0;
   out_3384456444114612704[217] = 0;
   out_3384456444114612704[218] = 0;
   out_3384456444114612704[219] = 0;
   out_3384456444114612704[220] = 0;
   out_3384456444114612704[221] = 0;
   out_3384456444114612704[222] = 0;
   out_3384456444114612704[223] = 0;
   out_3384456444114612704[224] = 0;
   out_3384456444114612704[225] = 0;
   out_3384456444114612704[226] = 0;
   out_3384456444114612704[227] = 0;
   out_3384456444114612704[228] = 1;
   out_3384456444114612704[229] = 0;
   out_3384456444114612704[230] = 0;
   out_3384456444114612704[231] = 0;
   out_3384456444114612704[232] = 0;
   out_3384456444114612704[233] = 0;
   out_3384456444114612704[234] = 0;
   out_3384456444114612704[235] = 0;
   out_3384456444114612704[236] = 0;
   out_3384456444114612704[237] = 0;
   out_3384456444114612704[238] = 0;
   out_3384456444114612704[239] = 0;
   out_3384456444114612704[240] = 0;
   out_3384456444114612704[241] = 0;
   out_3384456444114612704[242] = 0;
   out_3384456444114612704[243] = 0;
   out_3384456444114612704[244] = 0;
   out_3384456444114612704[245] = 0;
   out_3384456444114612704[246] = 0;
   out_3384456444114612704[247] = 1;
   out_3384456444114612704[248] = 0;
   out_3384456444114612704[249] = 0;
   out_3384456444114612704[250] = 0;
   out_3384456444114612704[251] = 0;
   out_3384456444114612704[252] = 0;
   out_3384456444114612704[253] = 0;
   out_3384456444114612704[254] = 0;
   out_3384456444114612704[255] = 0;
   out_3384456444114612704[256] = 0;
   out_3384456444114612704[257] = 0;
   out_3384456444114612704[258] = 0;
   out_3384456444114612704[259] = 0;
   out_3384456444114612704[260] = 0;
   out_3384456444114612704[261] = 0;
   out_3384456444114612704[262] = 0;
   out_3384456444114612704[263] = 0;
   out_3384456444114612704[264] = 0;
   out_3384456444114612704[265] = 0;
   out_3384456444114612704[266] = 1;
   out_3384456444114612704[267] = 0;
   out_3384456444114612704[268] = 0;
   out_3384456444114612704[269] = 0;
   out_3384456444114612704[270] = 0;
   out_3384456444114612704[271] = 0;
   out_3384456444114612704[272] = 0;
   out_3384456444114612704[273] = 0;
   out_3384456444114612704[274] = 0;
   out_3384456444114612704[275] = 0;
   out_3384456444114612704[276] = 0;
   out_3384456444114612704[277] = 0;
   out_3384456444114612704[278] = 0;
   out_3384456444114612704[279] = 0;
   out_3384456444114612704[280] = 0;
   out_3384456444114612704[281] = 0;
   out_3384456444114612704[282] = 0;
   out_3384456444114612704[283] = 0;
   out_3384456444114612704[284] = 0;
   out_3384456444114612704[285] = 1;
   out_3384456444114612704[286] = 0;
   out_3384456444114612704[287] = 0;
   out_3384456444114612704[288] = 0;
   out_3384456444114612704[289] = 0;
   out_3384456444114612704[290] = 0;
   out_3384456444114612704[291] = 0;
   out_3384456444114612704[292] = 0;
   out_3384456444114612704[293] = 0;
   out_3384456444114612704[294] = 0;
   out_3384456444114612704[295] = 0;
   out_3384456444114612704[296] = 0;
   out_3384456444114612704[297] = 0;
   out_3384456444114612704[298] = 0;
   out_3384456444114612704[299] = 0;
   out_3384456444114612704[300] = 0;
   out_3384456444114612704[301] = 0;
   out_3384456444114612704[302] = 0;
   out_3384456444114612704[303] = 0;
   out_3384456444114612704[304] = 1;
   out_3384456444114612704[305] = 0;
   out_3384456444114612704[306] = 0;
   out_3384456444114612704[307] = 0;
   out_3384456444114612704[308] = 0;
   out_3384456444114612704[309] = 0;
   out_3384456444114612704[310] = 0;
   out_3384456444114612704[311] = 0;
   out_3384456444114612704[312] = 0;
   out_3384456444114612704[313] = 0;
   out_3384456444114612704[314] = 0;
   out_3384456444114612704[315] = 0;
   out_3384456444114612704[316] = 0;
   out_3384456444114612704[317] = 0;
   out_3384456444114612704[318] = 0;
   out_3384456444114612704[319] = 0;
   out_3384456444114612704[320] = 0;
   out_3384456444114612704[321] = 0;
   out_3384456444114612704[322] = 0;
   out_3384456444114612704[323] = 1;
}
void h_4(double *state, double *unused, double *out_474367734226715198) {
   out_474367734226715198[0] = state[6] + state[9];
   out_474367734226715198[1] = state[7] + state[10];
   out_474367734226715198[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_1890529741135066163) {
   out_1890529741135066163[0] = 0;
   out_1890529741135066163[1] = 0;
   out_1890529741135066163[2] = 0;
   out_1890529741135066163[3] = 0;
   out_1890529741135066163[4] = 0;
   out_1890529741135066163[5] = 0;
   out_1890529741135066163[6] = 1;
   out_1890529741135066163[7] = 0;
   out_1890529741135066163[8] = 0;
   out_1890529741135066163[9] = 1;
   out_1890529741135066163[10] = 0;
   out_1890529741135066163[11] = 0;
   out_1890529741135066163[12] = 0;
   out_1890529741135066163[13] = 0;
   out_1890529741135066163[14] = 0;
   out_1890529741135066163[15] = 0;
   out_1890529741135066163[16] = 0;
   out_1890529741135066163[17] = 0;
   out_1890529741135066163[18] = 0;
   out_1890529741135066163[19] = 0;
   out_1890529741135066163[20] = 0;
   out_1890529741135066163[21] = 0;
   out_1890529741135066163[22] = 0;
   out_1890529741135066163[23] = 0;
   out_1890529741135066163[24] = 0;
   out_1890529741135066163[25] = 1;
   out_1890529741135066163[26] = 0;
   out_1890529741135066163[27] = 0;
   out_1890529741135066163[28] = 1;
   out_1890529741135066163[29] = 0;
   out_1890529741135066163[30] = 0;
   out_1890529741135066163[31] = 0;
   out_1890529741135066163[32] = 0;
   out_1890529741135066163[33] = 0;
   out_1890529741135066163[34] = 0;
   out_1890529741135066163[35] = 0;
   out_1890529741135066163[36] = 0;
   out_1890529741135066163[37] = 0;
   out_1890529741135066163[38] = 0;
   out_1890529741135066163[39] = 0;
   out_1890529741135066163[40] = 0;
   out_1890529741135066163[41] = 0;
   out_1890529741135066163[42] = 0;
   out_1890529741135066163[43] = 0;
   out_1890529741135066163[44] = 1;
   out_1890529741135066163[45] = 0;
   out_1890529741135066163[46] = 0;
   out_1890529741135066163[47] = 1;
   out_1890529741135066163[48] = 0;
   out_1890529741135066163[49] = 0;
   out_1890529741135066163[50] = 0;
   out_1890529741135066163[51] = 0;
   out_1890529741135066163[52] = 0;
   out_1890529741135066163[53] = 0;
}
void h_10(double *state, double *unused, double *out_4018312916377458673) {
   out_4018312916377458673[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_4018312916377458673[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_4018312916377458673[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_8902627675171897633) {
   out_8902627675171897633[0] = 0;
   out_8902627675171897633[1] = 9.8100000000000005*cos(state[1]);
   out_8902627675171897633[2] = 0;
   out_8902627675171897633[3] = 0;
   out_8902627675171897633[4] = -state[8];
   out_8902627675171897633[5] = state[7];
   out_8902627675171897633[6] = 0;
   out_8902627675171897633[7] = state[5];
   out_8902627675171897633[8] = -state[4];
   out_8902627675171897633[9] = 0;
   out_8902627675171897633[10] = 0;
   out_8902627675171897633[11] = 0;
   out_8902627675171897633[12] = 1;
   out_8902627675171897633[13] = 0;
   out_8902627675171897633[14] = 0;
   out_8902627675171897633[15] = 1;
   out_8902627675171897633[16] = 0;
   out_8902627675171897633[17] = 0;
   out_8902627675171897633[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_8902627675171897633[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_8902627675171897633[20] = 0;
   out_8902627675171897633[21] = state[8];
   out_8902627675171897633[22] = 0;
   out_8902627675171897633[23] = -state[6];
   out_8902627675171897633[24] = -state[5];
   out_8902627675171897633[25] = 0;
   out_8902627675171897633[26] = state[3];
   out_8902627675171897633[27] = 0;
   out_8902627675171897633[28] = 0;
   out_8902627675171897633[29] = 0;
   out_8902627675171897633[30] = 0;
   out_8902627675171897633[31] = 1;
   out_8902627675171897633[32] = 0;
   out_8902627675171897633[33] = 0;
   out_8902627675171897633[34] = 1;
   out_8902627675171897633[35] = 0;
   out_8902627675171897633[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_8902627675171897633[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_8902627675171897633[38] = 0;
   out_8902627675171897633[39] = -state[7];
   out_8902627675171897633[40] = state[6];
   out_8902627675171897633[41] = 0;
   out_8902627675171897633[42] = state[4];
   out_8902627675171897633[43] = -state[3];
   out_8902627675171897633[44] = 0;
   out_8902627675171897633[45] = 0;
   out_8902627675171897633[46] = 0;
   out_8902627675171897633[47] = 0;
   out_8902627675171897633[48] = 0;
   out_8902627675171897633[49] = 0;
   out_8902627675171897633[50] = 1;
   out_8902627675171897633[51] = 0;
   out_8902627675171897633[52] = 0;
   out_8902627675171897633[53] = 1;
}
void h_13(double *state, double *unused, double *out_679811619492670605) {
   out_679811619492670605[0] = state[3];
   out_679811619492670605[1] = state[4];
   out_679811619492670605[2] = state[5];
}
void H_13(double *state, double *unused, double *out_1321744084197266638) {
   out_1321744084197266638[0] = 0;
   out_1321744084197266638[1] = 0;
   out_1321744084197266638[2] = 0;
   out_1321744084197266638[3] = 1;
   out_1321744084197266638[4] = 0;
   out_1321744084197266638[5] = 0;
   out_1321744084197266638[6] = 0;
   out_1321744084197266638[7] = 0;
   out_1321744084197266638[8] = 0;
   out_1321744084197266638[9] = 0;
   out_1321744084197266638[10] = 0;
   out_1321744084197266638[11] = 0;
   out_1321744084197266638[12] = 0;
   out_1321744084197266638[13] = 0;
   out_1321744084197266638[14] = 0;
   out_1321744084197266638[15] = 0;
   out_1321744084197266638[16] = 0;
   out_1321744084197266638[17] = 0;
   out_1321744084197266638[18] = 0;
   out_1321744084197266638[19] = 0;
   out_1321744084197266638[20] = 0;
   out_1321744084197266638[21] = 0;
   out_1321744084197266638[22] = 1;
   out_1321744084197266638[23] = 0;
   out_1321744084197266638[24] = 0;
   out_1321744084197266638[25] = 0;
   out_1321744084197266638[26] = 0;
   out_1321744084197266638[27] = 0;
   out_1321744084197266638[28] = 0;
   out_1321744084197266638[29] = 0;
   out_1321744084197266638[30] = 0;
   out_1321744084197266638[31] = 0;
   out_1321744084197266638[32] = 0;
   out_1321744084197266638[33] = 0;
   out_1321744084197266638[34] = 0;
   out_1321744084197266638[35] = 0;
   out_1321744084197266638[36] = 0;
   out_1321744084197266638[37] = 0;
   out_1321744084197266638[38] = 0;
   out_1321744084197266638[39] = 0;
   out_1321744084197266638[40] = 0;
   out_1321744084197266638[41] = 1;
   out_1321744084197266638[42] = 0;
   out_1321744084197266638[43] = 0;
   out_1321744084197266638[44] = 0;
   out_1321744084197266638[45] = 0;
   out_1321744084197266638[46] = 0;
   out_1321744084197266638[47] = 0;
   out_1321744084197266638[48] = 0;
   out_1321744084197266638[49] = 0;
   out_1321744084197266638[50] = 0;
   out_1321744084197266638[51] = 0;
   out_1321744084197266638[52] = 0;
   out_1321744084197266638[53] = 0;
}
void h_14(double *state, double *unused, double *out_7920144005840861725) {
   out_7920144005840861725[0] = state[6];
   out_7920144005840861725[1] = state[7];
   out_7920144005840861725[2] = state[8];
}
void H_14(double *state, double *unused, double *out_2072711115204418366) {
   out_2072711115204418366[0] = 0;
   out_2072711115204418366[1] = 0;
   out_2072711115204418366[2] = 0;
   out_2072711115204418366[3] = 0;
   out_2072711115204418366[4] = 0;
   out_2072711115204418366[5] = 0;
   out_2072711115204418366[6] = 1;
   out_2072711115204418366[7] = 0;
   out_2072711115204418366[8] = 0;
   out_2072711115204418366[9] = 0;
   out_2072711115204418366[10] = 0;
   out_2072711115204418366[11] = 0;
   out_2072711115204418366[12] = 0;
   out_2072711115204418366[13] = 0;
   out_2072711115204418366[14] = 0;
   out_2072711115204418366[15] = 0;
   out_2072711115204418366[16] = 0;
   out_2072711115204418366[17] = 0;
   out_2072711115204418366[18] = 0;
   out_2072711115204418366[19] = 0;
   out_2072711115204418366[20] = 0;
   out_2072711115204418366[21] = 0;
   out_2072711115204418366[22] = 0;
   out_2072711115204418366[23] = 0;
   out_2072711115204418366[24] = 0;
   out_2072711115204418366[25] = 1;
   out_2072711115204418366[26] = 0;
   out_2072711115204418366[27] = 0;
   out_2072711115204418366[28] = 0;
   out_2072711115204418366[29] = 0;
   out_2072711115204418366[30] = 0;
   out_2072711115204418366[31] = 0;
   out_2072711115204418366[32] = 0;
   out_2072711115204418366[33] = 0;
   out_2072711115204418366[34] = 0;
   out_2072711115204418366[35] = 0;
   out_2072711115204418366[36] = 0;
   out_2072711115204418366[37] = 0;
   out_2072711115204418366[38] = 0;
   out_2072711115204418366[39] = 0;
   out_2072711115204418366[40] = 0;
   out_2072711115204418366[41] = 0;
   out_2072711115204418366[42] = 0;
   out_2072711115204418366[43] = 0;
   out_2072711115204418366[44] = 1;
   out_2072711115204418366[45] = 0;
   out_2072711115204418366[46] = 0;
   out_2072711115204418366[47] = 0;
   out_2072711115204418366[48] = 0;
   out_2072711115204418366[49] = 0;
   out_2072711115204418366[50] = 0;
   out_2072711115204418366[51] = 0;
   out_2072711115204418366[52] = 0;
   out_2072711115204418366[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_8545056502495144785) {
  err_fun(nom_x, delta_x, out_8545056502495144785);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_6519300297558606633) {
  inv_err_fun(nom_x, true_x, out_6519300297558606633);
}
void pose_H_mod_fun(double *state, double *out_3957552065616892558) {
  H_mod_fun(state, out_3957552065616892558);
}
void pose_f_fun(double *state, double dt, double *out_7276726461426660421) {
  f_fun(state,  dt, out_7276726461426660421);
}
void pose_F_fun(double *state, double dt, double *out_3384456444114612704) {
  F_fun(state,  dt, out_3384456444114612704);
}
void pose_h_4(double *state, double *unused, double *out_474367734226715198) {
  h_4(state, unused, out_474367734226715198);
}
void pose_H_4(double *state, double *unused, double *out_1890529741135066163) {
  H_4(state, unused, out_1890529741135066163);
}
void pose_h_10(double *state, double *unused, double *out_4018312916377458673) {
  h_10(state, unused, out_4018312916377458673);
}
void pose_H_10(double *state, double *unused, double *out_8902627675171897633) {
  H_10(state, unused, out_8902627675171897633);
}
void pose_h_13(double *state, double *unused, double *out_679811619492670605) {
  h_13(state, unused, out_679811619492670605);
}
void pose_H_13(double *state, double *unused, double *out_1321744084197266638) {
  H_13(state, unused, out_1321744084197266638);
}
void pose_h_14(double *state, double *unused, double *out_7920144005840861725) {
  h_14(state, unused, out_7920144005840861725);
}
void pose_H_14(double *state, double *unused, double *out_2072711115204418366) {
  H_14(state, unused, out_2072711115204418366);
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
