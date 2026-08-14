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
void err_fun(double *nom_x, double *delta_x, double *out_6367311460737761297) {
   out_6367311460737761297[0] = delta_x[0] + nom_x[0];
   out_6367311460737761297[1] = delta_x[1] + nom_x[1];
   out_6367311460737761297[2] = delta_x[2] + nom_x[2];
   out_6367311460737761297[3] = delta_x[3] + nom_x[3];
   out_6367311460737761297[4] = delta_x[4] + nom_x[4];
   out_6367311460737761297[5] = delta_x[5] + nom_x[5];
   out_6367311460737761297[6] = delta_x[6] + nom_x[6];
   out_6367311460737761297[7] = delta_x[7] + nom_x[7];
   out_6367311460737761297[8] = delta_x[8] + nom_x[8];
   out_6367311460737761297[9] = delta_x[9] + nom_x[9];
   out_6367311460737761297[10] = delta_x[10] + nom_x[10];
   out_6367311460737761297[11] = delta_x[11] + nom_x[11];
   out_6367311460737761297[12] = delta_x[12] + nom_x[12];
   out_6367311460737761297[13] = delta_x[13] + nom_x[13];
   out_6367311460737761297[14] = delta_x[14] + nom_x[14];
   out_6367311460737761297[15] = delta_x[15] + nom_x[15];
   out_6367311460737761297[16] = delta_x[16] + nom_x[16];
   out_6367311460737761297[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5441199093300877780) {
   out_5441199093300877780[0] = -nom_x[0] + true_x[0];
   out_5441199093300877780[1] = -nom_x[1] + true_x[1];
   out_5441199093300877780[2] = -nom_x[2] + true_x[2];
   out_5441199093300877780[3] = -nom_x[3] + true_x[3];
   out_5441199093300877780[4] = -nom_x[4] + true_x[4];
   out_5441199093300877780[5] = -nom_x[5] + true_x[5];
   out_5441199093300877780[6] = -nom_x[6] + true_x[6];
   out_5441199093300877780[7] = -nom_x[7] + true_x[7];
   out_5441199093300877780[8] = -nom_x[8] + true_x[8];
   out_5441199093300877780[9] = -nom_x[9] + true_x[9];
   out_5441199093300877780[10] = -nom_x[10] + true_x[10];
   out_5441199093300877780[11] = -nom_x[11] + true_x[11];
   out_5441199093300877780[12] = -nom_x[12] + true_x[12];
   out_5441199093300877780[13] = -nom_x[13] + true_x[13];
   out_5441199093300877780[14] = -nom_x[14] + true_x[14];
   out_5441199093300877780[15] = -nom_x[15] + true_x[15];
   out_5441199093300877780[16] = -nom_x[16] + true_x[16];
   out_5441199093300877780[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_1340515713036728892) {
   out_1340515713036728892[0] = 1.0;
   out_1340515713036728892[1] = 0.0;
   out_1340515713036728892[2] = 0.0;
   out_1340515713036728892[3] = 0.0;
   out_1340515713036728892[4] = 0.0;
   out_1340515713036728892[5] = 0.0;
   out_1340515713036728892[6] = 0.0;
   out_1340515713036728892[7] = 0.0;
   out_1340515713036728892[8] = 0.0;
   out_1340515713036728892[9] = 0.0;
   out_1340515713036728892[10] = 0.0;
   out_1340515713036728892[11] = 0.0;
   out_1340515713036728892[12] = 0.0;
   out_1340515713036728892[13] = 0.0;
   out_1340515713036728892[14] = 0.0;
   out_1340515713036728892[15] = 0.0;
   out_1340515713036728892[16] = 0.0;
   out_1340515713036728892[17] = 0.0;
   out_1340515713036728892[18] = 0.0;
   out_1340515713036728892[19] = 1.0;
   out_1340515713036728892[20] = 0.0;
   out_1340515713036728892[21] = 0.0;
   out_1340515713036728892[22] = 0.0;
   out_1340515713036728892[23] = 0.0;
   out_1340515713036728892[24] = 0.0;
   out_1340515713036728892[25] = 0.0;
   out_1340515713036728892[26] = 0.0;
   out_1340515713036728892[27] = 0.0;
   out_1340515713036728892[28] = 0.0;
   out_1340515713036728892[29] = 0.0;
   out_1340515713036728892[30] = 0.0;
   out_1340515713036728892[31] = 0.0;
   out_1340515713036728892[32] = 0.0;
   out_1340515713036728892[33] = 0.0;
   out_1340515713036728892[34] = 0.0;
   out_1340515713036728892[35] = 0.0;
   out_1340515713036728892[36] = 0.0;
   out_1340515713036728892[37] = 0.0;
   out_1340515713036728892[38] = 1.0;
   out_1340515713036728892[39] = 0.0;
   out_1340515713036728892[40] = 0.0;
   out_1340515713036728892[41] = 0.0;
   out_1340515713036728892[42] = 0.0;
   out_1340515713036728892[43] = 0.0;
   out_1340515713036728892[44] = 0.0;
   out_1340515713036728892[45] = 0.0;
   out_1340515713036728892[46] = 0.0;
   out_1340515713036728892[47] = 0.0;
   out_1340515713036728892[48] = 0.0;
   out_1340515713036728892[49] = 0.0;
   out_1340515713036728892[50] = 0.0;
   out_1340515713036728892[51] = 0.0;
   out_1340515713036728892[52] = 0.0;
   out_1340515713036728892[53] = 0.0;
   out_1340515713036728892[54] = 0.0;
   out_1340515713036728892[55] = 0.0;
   out_1340515713036728892[56] = 0.0;
   out_1340515713036728892[57] = 1.0;
   out_1340515713036728892[58] = 0.0;
   out_1340515713036728892[59] = 0.0;
   out_1340515713036728892[60] = 0.0;
   out_1340515713036728892[61] = 0.0;
   out_1340515713036728892[62] = 0.0;
   out_1340515713036728892[63] = 0.0;
   out_1340515713036728892[64] = 0.0;
   out_1340515713036728892[65] = 0.0;
   out_1340515713036728892[66] = 0.0;
   out_1340515713036728892[67] = 0.0;
   out_1340515713036728892[68] = 0.0;
   out_1340515713036728892[69] = 0.0;
   out_1340515713036728892[70] = 0.0;
   out_1340515713036728892[71] = 0.0;
   out_1340515713036728892[72] = 0.0;
   out_1340515713036728892[73] = 0.0;
   out_1340515713036728892[74] = 0.0;
   out_1340515713036728892[75] = 0.0;
   out_1340515713036728892[76] = 1.0;
   out_1340515713036728892[77] = 0.0;
   out_1340515713036728892[78] = 0.0;
   out_1340515713036728892[79] = 0.0;
   out_1340515713036728892[80] = 0.0;
   out_1340515713036728892[81] = 0.0;
   out_1340515713036728892[82] = 0.0;
   out_1340515713036728892[83] = 0.0;
   out_1340515713036728892[84] = 0.0;
   out_1340515713036728892[85] = 0.0;
   out_1340515713036728892[86] = 0.0;
   out_1340515713036728892[87] = 0.0;
   out_1340515713036728892[88] = 0.0;
   out_1340515713036728892[89] = 0.0;
   out_1340515713036728892[90] = 0.0;
   out_1340515713036728892[91] = 0.0;
   out_1340515713036728892[92] = 0.0;
   out_1340515713036728892[93] = 0.0;
   out_1340515713036728892[94] = 0.0;
   out_1340515713036728892[95] = 1.0;
   out_1340515713036728892[96] = 0.0;
   out_1340515713036728892[97] = 0.0;
   out_1340515713036728892[98] = 0.0;
   out_1340515713036728892[99] = 0.0;
   out_1340515713036728892[100] = 0.0;
   out_1340515713036728892[101] = 0.0;
   out_1340515713036728892[102] = 0.0;
   out_1340515713036728892[103] = 0.0;
   out_1340515713036728892[104] = 0.0;
   out_1340515713036728892[105] = 0.0;
   out_1340515713036728892[106] = 0.0;
   out_1340515713036728892[107] = 0.0;
   out_1340515713036728892[108] = 0.0;
   out_1340515713036728892[109] = 0.0;
   out_1340515713036728892[110] = 0.0;
   out_1340515713036728892[111] = 0.0;
   out_1340515713036728892[112] = 0.0;
   out_1340515713036728892[113] = 0.0;
   out_1340515713036728892[114] = 1.0;
   out_1340515713036728892[115] = 0.0;
   out_1340515713036728892[116] = 0.0;
   out_1340515713036728892[117] = 0.0;
   out_1340515713036728892[118] = 0.0;
   out_1340515713036728892[119] = 0.0;
   out_1340515713036728892[120] = 0.0;
   out_1340515713036728892[121] = 0.0;
   out_1340515713036728892[122] = 0.0;
   out_1340515713036728892[123] = 0.0;
   out_1340515713036728892[124] = 0.0;
   out_1340515713036728892[125] = 0.0;
   out_1340515713036728892[126] = 0.0;
   out_1340515713036728892[127] = 0.0;
   out_1340515713036728892[128] = 0.0;
   out_1340515713036728892[129] = 0.0;
   out_1340515713036728892[130] = 0.0;
   out_1340515713036728892[131] = 0.0;
   out_1340515713036728892[132] = 0.0;
   out_1340515713036728892[133] = 1.0;
   out_1340515713036728892[134] = 0.0;
   out_1340515713036728892[135] = 0.0;
   out_1340515713036728892[136] = 0.0;
   out_1340515713036728892[137] = 0.0;
   out_1340515713036728892[138] = 0.0;
   out_1340515713036728892[139] = 0.0;
   out_1340515713036728892[140] = 0.0;
   out_1340515713036728892[141] = 0.0;
   out_1340515713036728892[142] = 0.0;
   out_1340515713036728892[143] = 0.0;
   out_1340515713036728892[144] = 0.0;
   out_1340515713036728892[145] = 0.0;
   out_1340515713036728892[146] = 0.0;
   out_1340515713036728892[147] = 0.0;
   out_1340515713036728892[148] = 0.0;
   out_1340515713036728892[149] = 0.0;
   out_1340515713036728892[150] = 0.0;
   out_1340515713036728892[151] = 0.0;
   out_1340515713036728892[152] = 1.0;
   out_1340515713036728892[153] = 0.0;
   out_1340515713036728892[154] = 0.0;
   out_1340515713036728892[155] = 0.0;
   out_1340515713036728892[156] = 0.0;
   out_1340515713036728892[157] = 0.0;
   out_1340515713036728892[158] = 0.0;
   out_1340515713036728892[159] = 0.0;
   out_1340515713036728892[160] = 0.0;
   out_1340515713036728892[161] = 0.0;
   out_1340515713036728892[162] = 0.0;
   out_1340515713036728892[163] = 0.0;
   out_1340515713036728892[164] = 0.0;
   out_1340515713036728892[165] = 0.0;
   out_1340515713036728892[166] = 0.0;
   out_1340515713036728892[167] = 0.0;
   out_1340515713036728892[168] = 0.0;
   out_1340515713036728892[169] = 0.0;
   out_1340515713036728892[170] = 0.0;
   out_1340515713036728892[171] = 1.0;
   out_1340515713036728892[172] = 0.0;
   out_1340515713036728892[173] = 0.0;
   out_1340515713036728892[174] = 0.0;
   out_1340515713036728892[175] = 0.0;
   out_1340515713036728892[176] = 0.0;
   out_1340515713036728892[177] = 0.0;
   out_1340515713036728892[178] = 0.0;
   out_1340515713036728892[179] = 0.0;
   out_1340515713036728892[180] = 0.0;
   out_1340515713036728892[181] = 0.0;
   out_1340515713036728892[182] = 0.0;
   out_1340515713036728892[183] = 0.0;
   out_1340515713036728892[184] = 0.0;
   out_1340515713036728892[185] = 0.0;
   out_1340515713036728892[186] = 0.0;
   out_1340515713036728892[187] = 0.0;
   out_1340515713036728892[188] = 0.0;
   out_1340515713036728892[189] = 0.0;
   out_1340515713036728892[190] = 1.0;
   out_1340515713036728892[191] = 0.0;
   out_1340515713036728892[192] = 0.0;
   out_1340515713036728892[193] = 0.0;
   out_1340515713036728892[194] = 0.0;
   out_1340515713036728892[195] = 0.0;
   out_1340515713036728892[196] = 0.0;
   out_1340515713036728892[197] = 0.0;
   out_1340515713036728892[198] = 0.0;
   out_1340515713036728892[199] = 0.0;
   out_1340515713036728892[200] = 0.0;
   out_1340515713036728892[201] = 0.0;
   out_1340515713036728892[202] = 0.0;
   out_1340515713036728892[203] = 0.0;
   out_1340515713036728892[204] = 0.0;
   out_1340515713036728892[205] = 0.0;
   out_1340515713036728892[206] = 0.0;
   out_1340515713036728892[207] = 0.0;
   out_1340515713036728892[208] = 0.0;
   out_1340515713036728892[209] = 1.0;
   out_1340515713036728892[210] = 0.0;
   out_1340515713036728892[211] = 0.0;
   out_1340515713036728892[212] = 0.0;
   out_1340515713036728892[213] = 0.0;
   out_1340515713036728892[214] = 0.0;
   out_1340515713036728892[215] = 0.0;
   out_1340515713036728892[216] = 0.0;
   out_1340515713036728892[217] = 0.0;
   out_1340515713036728892[218] = 0.0;
   out_1340515713036728892[219] = 0.0;
   out_1340515713036728892[220] = 0.0;
   out_1340515713036728892[221] = 0.0;
   out_1340515713036728892[222] = 0.0;
   out_1340515713036728892[223] = 0.0;
   out_1340515713036728892[224] = 0.0;
   out_1340515713036728892[225] = 0.0;
   out_1340515713036728892[226] = 0.0;
   out_1340515713036728892[227] = 0.0;
   out_1340515713036728892[228] = 1.0;
   out_1340515713036728892[229] = 0.0;
   out_1340515713036728892[230] = 0.0;
   out_1340515713036728892[231] = 0.0;
   out_1340515713036728892[232] = 0.0;
   out_1340515713036728892[233] = 0.0;
   out_1340515713036728892[234] = 0.0;
   out_1340515713036728892[235] = 0.0;
   out_1340515713036728892[236] = 0.0;
   out_1340515713036728892[237] = 0.0;
   out_1340515713036728892[238] = 0.0;
   out_1340515713036728892[239] = 0.0;
   out_1340515713036728892[240] = 0.0;
   out_1340515713036728892[241] = 0.0;
   out_1340515713036728892[242] = 0.0;
   out_1340515713036728892[243] = 0.0;
   out_1340515713036728892[244] = 0.0;
   out_1340515713036728892[245] = 0.0;
   out_1340515713036728892[246] = 0.0;
   out_1340515713036728892[247] = 1.0;
   out_1340515713036728892[248] = 0.0;
   out_1340515713036728892[249] = 0.0;
   out_1340515713036728892[250] = 0.0;
   out_1340515713036728892[251] = 0.0;
   out_1340515713036728892[252] = 0.0;
   out_1340515713036728892[253] = 0.0;
   out_1340515713036728892[254] = 0.0;
   out_1340515713036728892[255] = 0.0;
   out_1340515713036728892[256] = 0.0;
   out_1340515713036728892[257] = 0.0;
   out_1340515713036728892[258] = 0.0;
   out_1340515713036728892[259] = 0.0;
   out_1340515713036728892[260] = 0.0;
   out_1340515713036728892[261] = 0.0;
   out_1340515713036728892[262] = 0.0;
   out_1340515713036728892[263] = 0.0;
   out_1340515713036728892[264] = 0.0;
   out_1340515713036728892[265] = 0.0;
   out_1340515713036728892[266] = 1.0;
   out_1340515713036728892[267] = 0.0;
   out_1340515713036728892[268] = 0.0;
   out_1340515713036728892[269] = 0.0;
   out_1340515713036728892[270] = 0.0;
   out_1340515713036728892[271] = 0.0;
   out_1340515713036728892[272] = 0.0;
   out_1340515713036728892[273] = 0.0;
   out_1340515713036728892[274] = 0.0;
   out_1340515713036728892[275] = 0.0;
   out_1340515713036728892[276] = 0.0;
   out_1340515713036728892[277] = 0.0;
   out_1340515713036728892[278] = 0.0;
   out_1340515713036728892[279] = 0.0;
   out_1340515713036728892[280] = 0.0;
   out_1340515713036728892[281] = 0.0;
   out_1340515713036728892[282] = 0.0;
   out_1340515713036728892[283] = 0.0;
   out_1340515713036728892[284] = 0.0;
   out_1340515713036728892[285] = 1.0;
   out_1340515713036728892[286] = 0.0;
   out_1340515713036728892[287] = 0.0;
   out_1340515713036728892[288] = 0.0;
   out_1340515713036728892[289] = 0.0;
   out_1340515713036728892[290] = 0.0;
   out_1340515713036728892[291] = 0.0;
   out_1340515713036728892[292] = 0.0;
   out_1340515713036728892[293] = 0.0;
   out_1340515713036728892[294] = 0.0;
   out_1340515713036728892[295] = 0.0;
   out_1340515713036728892[296] = 0.0;
   out_1340515713036728892[297] = 0.0;
   out_1340515713036728892[298] = 0.0;
   out_1340515713036728892[299] = 0.0;
   out_1340515713036728892[300] = 0.0;
   out_1340515713036728892[301] = 0.0;
   out_1340515713036728892[302] = 0.0;
   out_1340515713036728892[303] = 0.0;
   out_1340515713036728892[304] = 1.0;
   out_1340515713036728892[305] = 0.0;
   out_1340515713036728892[306] = 0.0;
   out_1340515713036728892[307] = 0.0;
   out_1340515713036728892[308] = 0.0;
   out_1340515713036728892[309] = 0.0;
   out_1340515713036728892[310] = 0.0;
   out_1340515713036728892[311] = 0.0;
   out_1340515713036728892[312] = 0.0;
   out_1340515713036728892[313] = 0.0;
   out_1340515713036728892[314] = 0.0;
   out_1340515713036728892[315] = 0.0;
   out_1340515713036728892[316] = 0.0;
   out_1340515713036728892[317] = 0.0;
   out_1340515713036728892[318] = 0.0;
   out_1340515713036728892[319] = 0.0;
   out_1340515713036728892[320] = 0.0;
   out_1340515713036728892[321] = 0.0;
   out_1340515713036728892[322] = 0.0;
   out_1340515713036728892[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_3671753857095520812) {
   out_3671753857095520812[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_3671753857095520812[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_3671753857095520812[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_3671753857095520812[3] = dt*state[12] + state[3];
   out_3671753857095520812[4] = dt*state[13] + state[4];
   out_3671753857095520812[5] = dt*state[14] + state[5];
   out_3671753857095520812[6] = state[6];
   out_3671753857095520812[7] = state[7];
   out_3671753857095520812[8] = state[8];
   out_3671753857095520812[9] = state[9];
   out_3671753857095520812[10] = state[10];
   out_3671753857095520812[11] = state[11];
   out_3671753857095520812[12] = state[12];
   out_3671753857095520812[13] = state[13];
   out_3671753857095520812[14] = state[14];
   out_3671753857095520812[15] = state[15];
   out_3671753857095520812[16] = state[16];
   out_3671753857095520812[17] = state[17];
}
void F_fun(double *state, double dt, double *out_6105292692276061193) {
   out_6105292692276061193[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6105292692276061193[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6105292692276061193[2] = 0;
   out_6105292692276061193[3] = 0;
   out_6105292692276061193[4] = 0;
   out_6105292692276061193[5] = 0;
   out_6105292692276061193[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6105292692276061193[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6105292692276061193[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6105292692276061193[9] = 0;
   out_6105292692276061193[10] = 0;
   out_6105292692276061193[11] = 0;
   out_6105292692276061193[12] = 0;
   out_6105292692276061193[13] = 0;
   out_6105292692276061193[14] = 0;
   out_6105292692276061193[15] = 0;
   out_6105292692276061193[16] = 0;
   out_6105292692276061193[17] = 0;
   out_6105292692276061193[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6105292692276061193[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6105292692276061193[20] = 0;
   out_6105292692276061193[21] = 0;
   out_6105292692276061193[22] = 0;
   out_6105292692276061193[23] = 0;
   out_6105292692276061193[24] = 0;
   out_6105292692276061193[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6105292692276061193[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6105292692276061193[27] = 0;
   out_6105292692276061193[28] = 0;
   out_6105292692276061193[29] = 0;
   out_6105292692276061193[30] = 0;
   out_6105292692276061193[31] = 0;
   out_6105292692276061193[32] = 0;
   out_6105292692276061193[33] = 0;
   out_6105292692276061193[34] = 0;
   out_6105292692276061193[35] = 0;
   out_6105292692276061193[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6105292692276061193[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6105292692276061193[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6105292692276061193[39] = 0;
   out_6105292692276061193[40] = 0;
   out_6105292692276061193[41] = 0;
   out_6105292692276061193[42] = 0;
   out_6105292692276061193[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6105292692276061193[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6105292692276061193[45] = 0;
   out_6105292692276061193[46] = 0;
   out_6105292692276061193[47] = 0;
   out_6105292692276061193[48] = 0;
   out_6105292692276061193[49] = 0;
   out_6105292692276061193[50] = 0;
   out_6105292692276061193[51] = 0;
   out_6105292692276061193[52] = 0;
   out_6105292692276061193[53] = 0;
   out_6105292692276061193[54] = 0;
   out_6105292692276061193[55] = 0;
   out_6105292692276061193[56] = 0;
   out_6105292692276061193[57] = 1;
   out_6105292692276061193[58] = 0;
   out_6105292692276061193[59] = 0;
   out_6105292692276061193[60] = 0;
   out_6105292692276061193[61] = 0;
   out_6105292692276061193[62] = 0;
   out_6105292692276061193[63] = 0;
   out_6105292692276061193[64] = 0;
   out_6105292692276061193[65] = 0;
   out_6105292692276061193[66] = dt;
   out_6105292692276061193[67] = 0;
   out_6105292692276061193[68] = 0;
   out_6105292692276061193[69] = 0;
   out_6105292692276061193[70] = 0;
   out_6105292692276061193[71] = 0;
   out_6105292692276061193[72] = 0;
   out_6105292692276061193[73] = 0;
   out_6105292692276061193[74] = 0;
   out_6105292692276061193[75] = 0;
   out_6105292692276061193[76] = 1;
   out_6105292692276061193[77] = 0;
   out_6105292692276061193[78] = 0;
   out_6105292692276061193[79] = 0;
   out_6105292692276061193[80] = 0;
   out_6105292692276061193[81] = 0;
   out_6105292692276061193[82] = 0;
   out_6105292692276061193[83] = 0;
   out_6105292692276061193[84] = 0;
   out_6105292692276061193[85] = dt;
   out_6105292692276061193[86] = 0;
   out_6105292692276061193[87] = 0;
   out_6105292692276061193[88] = 0;
   out_6105292692276061193[89] = 0;
   out_6105292692276061193[90] = 0;
   out_6105292692276061193[91] = 0;
   out_6105292692276061193[92] = 0;
   out_6105292692276061193[93] = 0;
   out_6105292692276061193[94] = 0;
   out_6105292692276061193[95] = 1;
   out_6105292692276061193[96] = 0;
   out_6105292692276061193[97] = 0;
   out_6105292692276061193[98] = 0;
   out_6105292692276061193[99] = 0;
   out_6105292692276061193[100] = 0;
   out_6105292692276061193[101] = 0;
   out_6105292692276061193[102] = 0;
   out_6105292692276061193[103] = 0;
   out_6105292692276061193[104] = dt;
   out_6105292692276061193[105] = 0;
   out_6105292692276061193[106] = 0;
   out_6105292692276061193[107] = 0;
   out_6105292692276061193[108] = 0;
   out_6105292692276061193[109] = 0;
   out_6105292692276061193[110] = 0;
   out_6105292692276061193[111] = 0;
   out_6105292692276061193[112] = 0;
   out_6105292692276061193[113] = 0;
   out_6105292692276061193[114] = 1;
   out_6105292692276061193[115] = 0;
   out_6105292692276061193[116] = 0;
   out_6105292692276061193[117] = 0;
   out_6105292692276061193[118] = 0;
   out_6105292692276061193[119] = 0;
   out_6105292692276061193[120] = 0;
   out_6105292692276061193[121] = 0;
   out_6105292692276061193[122] = 0;
   out_6105292692276061193[123] = 0;
   out_6105292692276061193[124] = 0;
   out_6105292692276061193[125] = 0;
   out_6105292692276061193[126] = 0;
   out_6105292692276061193[127] = 0;
   out_6105292692276061193[128] = 0;
   out_6105292692276061193[129] = 0;
   out_6105292692276061193[130] = 0;
   out_6105292692276061193[131] = 0;
   out_6105292692276061193[132] = 0;
   out_6105292692276061193[133] = 1;
   out_6105292692276061193[134] = 0;
   out_6105292692276061193[135] = 0;
   out_6105292692276061193[136] = 0;
   out_6105292692276061193[137] = 0;
   out_6105292692276061193[138] = 0;
   out_6105292692276061193[139] = 0;
   out_6105292692276061193[140] = 0;
   out_6105292692276061193[141] = 0;
   out_6105292692276061193[142] = 0;
   out_6105292692276061193[143] = 0;
   out_6105292692276061193[144] = 0;
   out_6105292692276061193[145] = 0;
   out_6105292692276061193[146] = 0;
   out_6105292692276061193[147] = 0;
   out_6105292692276061193[148] = 0;
   out_6105292692276061193[149] = 0;
   out_6105292692276061193[150] = 0;
   out_6105292692276061193[151] = 0;
   out_6105292692276061193[152] = 1;
   out_6105292692276061193[153] = 0;
   out_6105292692276061193[154] = 0;
   out_6105292692276061193[155] = 0;
   out_6105292692276061193[156] = 0;
   out_6105292692276061193[157] = 0;
   out_6105292692276061193[158] = 0;
   out_6105292692276061193[159] = 0;
   out_6105292692276061193[160] = 0;
   out_6105292692276061193[161] = 0;
   out_6105292692276061193[162] = 0;
   out_6105292692276061193[163] = 0;
   out_6105292692276061193[164] = 0;
   out_6105292692276061193[165] = 0;
   out_6105292692276061193[166] = 0;
   out_6105292692276061193[167] = 0;
   out_6105292692276061193[168] = 0;
   out_6105292692276061193[169] = 0;
   out_6105292692276061193[170] = 0;
   out_6105292692276061193[171] = 1;
   out_6105292692276061193[172] = 0;
   out_6105292692276061193[173] = 0;
   out_6105292692276061193[174] = 0;
   out_6105292692276061193[175] = 0;
   out_6105292692276061193[176] = 0;
   out_6105292692276061193[177] = 0;
   out_6105292692276061193[178] = 0;
   out_6105292692276061193[179] = 0;
   out_6105292692276061193[180] = 0;
   out_6105292692276061193[181] = 0;
   out_6105292692276061193[182] = 0;
   out_6105292692276061193[183] = 0;
   out_6105292692276061193[184] = 0;
   out_6105292692276061193[185] = 0;
   out_6105292692276061193[186] = 0;
   out_6105292692276061193[187] = 0;
   out_6105292692276061193[188] = 0;
   out_6105292692276061193[189] = 0;
   out_6105292692276061193[190] = 1;
   out_6105292692276061193[191] = 0;
   out_6105292692276061193[192] = 0;
   out_6105292692276061193[193] = 0;
   out_6105292692276061193[194] = 0;
   out_6105292692276061193[195] = 0;
   out_6105292692276061193[196] = 0;
   out_6105292692276061193[197] = 0;
   out_6105292692276061193[198] = 0;
   out_6105292692276061193[199] = 0;
   out_6105292692276061193[200] = 0;
   out_6105292692276061193[201] = 0;
   out_6105292692276061193[202] = 0;
   out_6105292692276061193[203] = 0;
   out_6105292692276061193[204] = 0;
   out_6105292692276061193[205] = 0;
   out_6105292692276061193[206] = 0;
   out_6105292692276061193[207] = 0;
   out_6105292692276061193[208] = 0;
   out_6105292692276061193[209] = 1;
   out_6105292692276061193[210] = 0;
   out_6105292692276061193[211] = 0;
   out_6105292692276061193[212] = 0;
   out_6105292692276061193[213] = 0;
   out_6105292692276061193[214] = 0;
   out_6105292692276061193[215] = 0;
   out_6105292692276061193[216] = 0;
   out_6105292692276061193[217] = 0;
   out_6105292692276061193[218] = 0;
   out_6105292692276061193[219] = 0;
   out_6105292692276061193[220] = 0;
   out_6105292692276061193[221] = 0;
   out_6105292692276061193[222] = 0;
   out_6105292692276061193[223] = 0;
   out_6105292692276061193[224] = 0;
   out_6105292692276061193[225] = 0;
   out_6105292692276061193[226] = 0;
   out_6105292692276061193[227] = 0;
   out_6105292692276061193[228] = 1;
   out_6105292692276061193[229] = 0;
   out_6105292692276061193[230] = 0;
   out_6105292692276061193[231] = 0;
   out_6105292692276061193[232] = 0;
   out_6105292692276061193[233] = 0;
   out_6105292692276061193[234] = 0;
   out_6105292692276061193[235] = 0;
   out_6105292692276061193[236] = 0;
   out_6105292692276061193[237] = 0;
   out_6105292692276061193[238] = 0;
   out_6105292692276061193[239] = 0;
   out_6105292692276061193[240] = 0;
   out_6105292692276061193[241] = 0;
   out_6105292692276061193[242] = 0;
   out_6105292692276061193[243] = 0;
   out_6105292692276061193[244] = 0;
   out_6105292692276061193[245] = 0;
   out_6105292692276061193[246] = 0;
   out_6105292692276061193[247] = 1;
   out_6105292692276061193[248] = 0;
   out_6105292692276061193[249] = 0;
   out_6105292692276061193[250] = 0;
   out_6105292692276061193[251] = 0;
   out_6105292692276061193[252] = 0;
   out_6105292692276061193[253] = 0;
   out_6105292692276061193[254] = 0;
   out_6105292692276061193[255] = 0;
   out_6105292692276061193[256] = 0;
   out_6105292692276061193[257] = 0;
   out_6105292692276061193[258] = 0;
   out_6105292692276061193[259] = 0;
   out_6105292692276061193[260] = 0;
   out_6105292692276061193[261] = 0;
   out_6105292692276061193[262] = 0;
   out_6105292692276061193[263] = 0;
   out_6105292692276061193[264] = 0;
   out_6105292692276061193[265] = 0;
   out_6105292692276061193[266] = 1;
   out_6105292692276061193[267] = 0;
   out_6105292692276061193[268] = 0;
   out_6105292692276061193[269] = 0;
   out_6105292692276061193[270] = 0;
   out_6105292692276061193[271] = 0;
   out_6105292692276061193[272] = 0;
   out_6105292692276061193[273] = 0;
   out_6105292692276061193[274] = 0;
   out_6105292692276061193[275] = 0;
   out_6105292692276061193[276] = 0;
   out_6105292692276061193[277] = 0;
   out_6105292692276061193[278] = 0;
   out_6105292692276061193[279] = 0;
   out_6105292692276061193[280] = 0;
   out_6105292692276061193[281] = 0;
   out_6105292692276061193[282] = 0;
   out_6105292692276061193[283] = 0;
   out_6105292692276061193[284] = 0;
   out_6105292692276061193[285] = 1;
   out_6105292692276061193[286] = 0;
   out_6105292692276061193[287] = 0;
   out_6105292692276061193[288] = 0;
   out_6105292692276061193[289] = 0;
   out_6105292692276061193[290] = 0;
   out_6105292692276061193[291] = 0;
   out_6105292692276061193[292] = 0;
   out_6105292692276061193[293] = 0;
   out_6105292692276061193[294] = 0;
   out_6105292692276061193[295] = 0;
   out_6105292692276061193[296] = 0;
   out_6105292692276061193[297] = 0;
   out_6105292692276061193[298] = 0;
   out_6105292692276061193[299] = 0;
   out_6105292692276061193[300] = 0;
   out_6105292692276061193[301] = 0;
   out_6105292692276061193[302] = 0;
   out_6105292692276061193[303] = 0;
   out_6105292692276061193[304] = 1;
   out_6105292692276061193[305] = 0;
   out_6105292692276061193[306] = 0;
   out_6105292692276061193[307] = 0;
   out_6105292692276061193[308] = 0;
   out_6105292692276061193[309] = 0;
   out_6105292692276061193[310] = 0;
   out_6105292692276061193[311] = 0;
   out_6105292692276061193[312] = 0;
   out_6105292692276061193[313] = 0;
   out_6105292692276061193[314] = 0;
   out_6105292692276061193[315] = 0;
   out_6105292692276061193[316] = 0;
   out_6105292692276061193[317] = 0;
   out_6105292692276061193[318] = 0;
   out_6105292692276061193[319] = 0;
   out_6105292692276061193[320] = 0;
   out_6105292692276061193[321] = 0;
   out_6105292692276061193[322] = 0;
   out_6105292692276061193[323] = 1;
}
void h_4(double *state, double *unused, double *out_9135824683183967603) {
   out_9135824683183967603[0] = state[6] + state[9];
   out_9135824683183967603[1] = state[7] + state[10];
   out_9135824683183967603[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_4507566093715229829) {
   out_4507566093715229829[0] = 0;
   out_4507566093715229829[1] = 0;
   out_4507566093715229829[2] = 0;
   out_4507566093715229829[3] = 0;
   out_4507566093715229829[4] = 0;
   out_4507566093715229829[5] = 0;
   out_4507566093715229829[6] = 1;
   out_4507566093715229829[7] = 0;
   out_4507566093715229829[8] = 0;
   out_4507566093715229829[9] = 1;
   out_4507566093715229829[10] = 0;
   out_4507566093715229829[11] = 0;
   out_4507566093715229829[12] = 0;
   out_4507566093715229829[13] = 0;
   out_4507566093715229829[14] = 0;
   out_4507566093715229829[15] = 0;
   out_4507566093715229829[16] = 0;
   out_4507566093715229829[17] = 0;
   out_4507566093715229829[18] = 0;
   out_4507566093715229829[19] = 0;
   out_4507566093715229829[20] = 0;
   out_4507566093715229829[21] = 0;
   out_4507566093715229829[22] = 0;
   out_4507566093715229829[23] = 0;
   out_4507566093715229829[24] = 0;
   out_4507566093715229829[25] = 1;
   out_4507566093715229829[26] = 0;
   out_4507566093715229829[27] = 0;
   out_4507566093715229829[28] = 1;
   out_4507566093715229829[29] = 0;
   out_4507566093715229829[30] = 0;
   out_4507566093715229829[31] = 0;
   out_4507566093715229829[32] = 0;
   out_4507566093715229829[33] = 0;
   out_4507566093715229829[34] = 0;
   out_4507566093715229829[35] = 0;
   out_4507566093715229829[36] = 0;
   out_4507566093715229829[37] = 0;
   out_4507566093715229829[38] = 0;
   out_4507566093715229829[39] = 0;
   out_4507566093715229829[40] = 0;
   out_4507566093715229829[41] = 0;
   out_4507566093715229829[42] = 0;
   out_4507566093715229829[43] = 0;
   out_4507566093715229829[44] = 1;
   out_4507566093715229829[45] = 0;
   out_4507566093715229829[46] = 0;
   out_4507566093715229829[47] = 1;
   out_4507566093715229829[48] = 0;
   out_4507566093715229829[49] = 0;
   out_4507566093715229829[50] = 0;
   out_4507566093715229829[51] = 0;
   out_4507566093715229829[52] = 0;
   out_4507566093715229829[53] = 0;
}
void h_10(double *state, double *unused, double *out_9062434780767682717) {
   out_9062434780767682717[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_9062434780767682717[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_9062434780767682717[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_198935129897566355) {
   out_198935129897566355[0] = 0;
   out_198935129897566355[1] = 9.8100000000000005*cos(state[1]);
   out_198935129897566355[2] = 0;
   out_198935129897566355[3] = 0;
   out_198935129897566355[4] = -state[8];
   out_198935129897566355[5] = state[7];
   out_198935129897566355[6] = 0;
   out_198935129897566355[7] = state[5];
   out_198935129897566355[8] = -state[4];
   out_198935129897566355[9] = 0;
   out_198935129897566355[10] = 0;
   out_198935129897566355[11] = 0;
   out_198935129897566355[12] = 1;
   out_198935129897566355[13] = 0;
   out_198935129897566355[14] = 0;
   out_198935129897566355[15] = 1;
   out_198935129897566355[16] = 0;
   out_198935129897566355[17] = 0;
   out_198935129897566355[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_198935129897566355[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_198935129897566355[20] = 0;
   out_198935129897566355[21] = state[8];
   out_198935129897566355[22] = 0;
   out_198935129897566355[23] = -state[6];
   out_198935129897566355[24] = -state[5];
   out_198935129897566355[25] = 0;
   out_198935129897566355[26] = state[3];
   out_198935129897566355[27] = 0;
   out_198935129897566355[28] = 0;
   out_198935129897566355[29] = 0;
   out_198935129897566355[30] = 0;
   out_198935129897566355[31] = 1;
   out_198935129897566355[32] = 0;
   out_198935129897566355[33] = 0;
   out_198935129897566355[34] = 1;
   out_198935129897566355[35] = 0;
   out_198935129897566355[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_198935129897566355[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_198935129897566355[38] = 0;
   out_198935129897566355[39] = -state[7];
   out_198935129897566355[40] = state[6];
   out_198935129897566355[41] = 0;
   out_198935129897566355[42] = state[4];
   out_198935129897566355[43] = -state[3];
   out_198935129897566355[44] = 0;
   out_198935129897566355[45] = 0;
   out_198935129897566355[46] = 0;
   out_198935129897566355[47] = 0;
   out_198935129897566355[48] = 0;
   out_198935129897566355[49] = 0;
   out_198935129897566355[50] = 1;
   out_198935129897566355[51] = 0;
   out_198935129897566355[52] = 0;
   out_198935129897566355[53] = 1;
}
void h_13(double *state, double *unused, double *out_8160348284583123661) {
   out_8160348284583123661[0] = state[3];
   out_8160348284583123661[1] = state[4];
   out_8160348284583123661[2] = state[5];
}
void H_13(double *state, double *unused, double *out_1295292268382897028) {
   out_1295292268382897028[0] = 0;
   out_1295292268382897028[1] = 0;
   out_1295292268382897028[2] = 0;
   out_1295292268382897028[3] = 1;
   out_1295292268382897028[4] = 0;
   out_1295292268382897028[5] = 0;
   out_1295292268382897028[6] = 0;
   out_1295292268382897028[7] = 0;
   out_1295292268382897028[8] = 0;
   out_1295292268382897028[9] = 0;
   out_1295292268382897028[10] = 0;
   out_1295292268382897028[11] = 0;
   out_1295292268382897028[12] = 0;
   out_1295292268382897028[13] = 0;
   out_1295292268382897028[14] = 0;
   out_1295292268382897028[15] = 0;
   out_1295292268382897028[16] = 0;
   out_1295292268382897028[17] = 0;
   out_1295292268382897028[18] = 0;
   out_1295292268382897028[19] = 0;
   out_1295292268382897028[20] = 0;
   out_1295292268382897028[21] = 0;
   out_1295292268382897028[22] = 1;
   out_1295292268382897028[23] = 0;
   out_1295292268382897028[24] = 0;
   out_1295292268382897028[25] = 0;
   out_1295292268382897028[26] = 0;
   out_1295292268382897028[27] = 0;
   out_1295292268382897028[28] = 0;
   out_1295292268382897028[29] = 0;
   out_1295292268382897028[30] = 0;
   out_1295292268382897028[31] = 0;
   out_1295292268382897028[32] = 0;
   out_1295292268382897028[33] = 0;
   out_1295292268382897028[34] = 0;
   out_1295292268382897028[35] = 0;
   out_1295292268382897028[36] = 0;
   out_1295292268382897028[37] = 0;
   out_1295292268382897028[38] = 0;
   out_1295292268382897028[39] = 0;
   out_1295292268382897028[40] = 0;
   out_1295292268382897028[41] = 1;
   out_1295292268382897028[42] = 0;
   out_1295292268382897028[43] = 0;
   out_1295292268382897028[44] = 0;
   out_1295292268382897028[45] = 0;
   out_1295292268382897028[46] = 0;
   out_1295292268382897028[47] = 0;
   out_1295292268382897028[48] = 0;
   out_1295292268382897028[49] = 0;
   out_1295292268382897028[50] = 0;
   out_1295292268382897028[51] = 0;
   out_1295292268382897028[52] = 0;
   out_1295292268382897028[53] = 0;
}
void h_14(double *state, double *unused, double *out_4269604812988335508) {
   out_4269604812988335508[0] = state[6];
   out_4269604812988335508[1] = state[7];
   out_4269604812988335508[2] = state[8];
}
void H_14(double *state, double *unused, double *out_544325237375745300) {
   out_544325237375745300[0] = 0;
   out_544325237375745300[1] = 0;
   out_544325237375745300[2] = 0;
   out_544325237375745300[3] = 0;
   out_544325237375745300[4] = 0;
   out_544325237375745300[5] = 0;
   out_544325237375745300[6] = 1;
   out_544325237375745300[7] = 0;
   out_544325237375745300[8] = 0;
   out_544325237375745300[9] = 0;
   out_544325237375745300[10] = 0;
   out_544325237375745300[11] = 0;
   out_544325237375745300[12] = 0;
   out_544325237375745300[13] = 0;
   out_544325237375745300[14] = 0;
   out_544325237375745300[15] = 0;
   out_544325237375745300[16] = 0;
   out_544325237375745300[17] = 0;
   out_544325237375745300[18] = 0;
   out_544325237375745300[19] = 0;
   out_544325237375745300[20] = 0;
   out_544325237375745300[21] = 0;
   out_544325237375745300[22] = 0;
   out_544325237375745300[23] = 0;
   out_544325237375745300[24] = 0;
   out_544325237375745300[25] = 1;
   out_544325237375745300[26] = 0;
   out_544325237375745300[27] = 0;
   out_544325237375745300[28] = 0;
   out_544325237375745300[29] = 0;
   out_544325237375745300[30] = 0;
   out_544325237375745300[31] = 0;
   out_544325237375745300[32] = 0;
   out_544325237375745300[33] = 0;
   out_544325237375745300[34] = 0;
   out_544325237375745300[35] = 0;
   out_544325237375745300[36] = 0;
   out_544325237375745300[37] = 0;
   out_544325237375745300[38] = 0;
   out_544325237375745300[39] = 0;
   out_544325237375745300[40] = 0;
   out_544325237375745300[41] = 0;
   out_544325237375745300[42] = 0;
   out_544325237375745300[43] = 0;
   out_544325237375745300[44] = 1;
   out_544325237375745300[45] = 0;
   out_544325237375745300[46] = 0;
   out_544325237375745300[47] = 0;
   out_544325237375745300[48] = 0;
   out_544325237375745300[49] = 0;
   out_544325237375745300[50] = 0;
   out_544325237375745300[51] = 0;
   out_544325237375745300[52] = 0;
   out_544325237375745300[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_6367311460737761297) {
  err_fun(nom_x, delta_x, out_6367311460737761297);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5441199093300877780) {
  inv_err_fun(nom_x, true_x, out_5441199093300877780);
}
void pose_H_mod_fun(double *state, double *out_1340515713036728892) {
  H_mod_fun(state, out_1340515713036728892);
}
void pose_f_fun(double *state, double dt, double *out_3671753857095520812) {
  f_fun(state,  dt, out_3671753857095520812);
}
void pose_F_fun(double *state, double dt, double *out_6105292692276061193) {
  F_fun(state,  dt, out_6105292692276061193);
}
void pose_h_4(double *state, double *unused, double *out_9135824683183967603) {
  h_4(state, unused, out_9135824683183967603);
}
void pose_H_4(double *state, double *unused, double *out_4507566093715229829) {
  H_4(state, unused, out_4507566093715229829);
}
void pose_h_10(double *state, double *unused, double *out_9062434780767682717) {
  h_10(state, unused, out_9062434780767682717);
}
void pose_H_10(double *state, double *unused, double *out_198935129897566355) {
  H_10(state, unused, out_198935129897566355);
}
void pose_h_13(double *state, double *unused, double *out_8160348284583123661) {
  h_13(state, unused, out_8160348284583123661);
}
void pose_H_13(double *state, double *unused, double *out_1295292268382897028) {
  H_13(state, unused, out_1295292268382897028);
}
void pose_h_14(double *state, double *unused, double *out_4269604812988335508) {
  h_14(state, unused, out_4269604812988335508);
}
void pose_H_14(double *state, double *unused, double *out_544325237375745300) {
  H_14(state, unused, out_544325237375745300);
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
