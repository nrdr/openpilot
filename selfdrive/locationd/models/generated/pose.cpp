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
void err_fun(double *nom_x, double *delta_x, double *out_8464988186513175073) {
   out_8464988186513175073[0] = delta_x[0] + nom_x[0];
   out_8464988186513175073[1] = delta_x[1] + nom_x[1];
   out_8464988186513175073[2] = delta_x[2] + nom_x[2];
   out_8464988186513175073[3] = delta_x[3] + nom_x[3];
   out_8464988186513175073[4] = delta_x[4] + nom_x[4];
   out_8464988186513175073[5] = delta_x[5] + nom_x[5];
   out_8464988186513175073[6] = delta_x[6] + nom_x[6];
   out_8464988186513175073[7] = delta_x[7] + nom_x[7];
   out_8464988186513175073[8] = delta_x[8] + nom_x[8];
   out_8464988186513175073[9] = delta_x[9] + nom_x[9];
   out_8464988186513175073[10] = delta_x[10] + nom_x[10];
   out_8464988186513175073[11] = delta_x[11] + nom_x[11];
   out_8464988186513175073[12] = delta_x[12] + nom_x[12];
   out_8464988186513175073[13] = delta_x[13] + nom_x[13];
   out_8464988186513175073[14] = delta_x[14] + nom_x[14];
   out_8464988186513175073[15] = delta_x[15] + nom_x[15];
   out_8464988186513175073[16] = delta_x[16] + nom_x[16];
   out_8464988186513175073[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1852709291048557817) {
   out_1852709291048557817[0] = -nom_x[0] + true_x[0];
   out_1852709291048557817[1] = -nom_x[1] + true_x[1];
   out_1852709291048557817[2] = -nom_x[2] + true_x[2];
   out_1852709291048557817[3] = -nom_x[3] + true_x[3];
   out_1852709291048557817[4] = -nom_x[4] + true_x[4];
   out_1852709291048557817[5] = -nom_x[5] + true_x[5];
   out_1852709291048557817[6] = -nom_x[6] + true_x[6];
   out_1852709291048557817[7] = -nom_x[7] + true_x[7];
   out_1852709291048557817[8] = -nom_x[8] + true_x[8];
   out_1852709291048557817[9] = -nom_x[9] + true_x[9];
   out_1852709291048557817[10] = -nom_x[10] + true_x[10];
   out_1852709291048557817[11] = -nom_x[11] + true_x[11];
   out_1852709291048557817[12] = -nom_x[12] + true_x[12];
   out_1852709291048557817[13] = -nom_x[13] + true_x[13];
   out_1852709291048557817[14] = -nom_x[14] + true_x[14];
   out_1852709291048557817[15] = -nom_x[15] + true_x[15];
   out_1852709291048557817[16] = -nom_x[16] + true_x[16];
   out_1852709291048557817[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_538340367000647943) {
   out_538340367000647943[0] = 1.0;
   out_538340367000647943[1] = 0.0;
   out_538340367000647943[2] = 0.0;
   out_538340367000647943[3] = 0.0;
   out_538340367000647943[4] = 0.0;
   out_538340367000647943[5] = 0.0;
   out_538340367000647943[6] = 0.0;
   out_538340367000647943[7] = 0.0;
   out_538340367000647943[8] = 0.0;
   out_538340367000647943[9] = 0.0;
   out_538340367000647943[10] = 0.0;
   out_538340367000647943[11] = 0.0;
   out_538340367000647943[12] = 0.0;
   out_538340367000647943[13] = 0.0;
   out_538340367000647943[14] = 0.0;
   out_538340367000647943[15] = 0.0;
   out_538340367000647943[16] = 0.0;
   out_538340367000647943[17] = 0.0;
   out_538340367000647943[18] = 0.0;
   out_538340367000647943[19] = 1.0;
   out_538340367000647943[20] = 0.0;
   out_538340367000647943[21] = 0.0;
   out_538340367000647943[22] = 0.0;
   out_538340367000647943[23] = 0.0;
   out_538340367000647943[24] = 0.0;
   out_538340367000647943[25] = 0.0;
   out_538340367000647943[26] = 0.0;
   out_538340367000647943[27] = 0.0;
   out_538340367000647943[28] = 0.0;
   out_538340367000647943[29] = 0.0;
   out_538340367000647943[30] = 0.0;
   out_538340367000647943[31] = 0.0;
   out_538340367000647943[32] = 0.0;
   out_538340367000647943[33] = 0.0;
   out_538340367000647943[34] = 0.0;
   out_538340367000647943[35] = 0.0;
   out_538340367000647943[36] = 0.0;
   out_538340367000647943[37] = 0.0;
   out_538340367000647943[38] = 1.0;
   out_538340367000647943[39] = 0.0;
   out_538340367000647943[40] = 0.0;
   out_538340367000647943[41] = 0.0;
   out_538340367000647943[42] = 0.0;
   out_538340367000647943[43] = 0.0;
   out_538340367000647943[44] = 0.0;
   out_538340367000647943[45] = 0.0;
   out_538340367000647943[46] = 0.0;
   out_538340367000647943[47] = 0.0;
   out_538340367000647943[48] = 0.0;
   out_538340367000647943[49] = 0.0;
   out_538340367000647943[50] = 0.0;
   out_538340367000647943[51] = 0.0;
   out_538340367000647943[52] = 0.0;
   out_538340367000647943[53] = 0.0;
   out_538340367000647943[54] = 0.0;
   out_538340367000647943[55] = 0.0;
   out_538340367000647943[56] = 0.0;
   out_538340367000647943[57] = 1.0;
   out_538340367000647943[58] = 0.0;
   out_538340367000647943[59] = 0.0;
   out_538340367000647943[60] = 0.0;
   out_538340367000647943[61] = 0.0;
   out_538340367000647943[62] = 0.0;
   out_538340367000647943[63] = 0.0;
   out_538340367000647943[64] = 0.0;
   out_538340367000647943[65] = 0.0;
   out_538340367000647943[66] = 0.0;
   out_538340367000647943[67] = 0.0;
   out_538340367000647943[68] = 0.0;
   out_538340367000647943[69] = 0.0;
   out_538340367000647943[70] = 0.0;
   out_538340367000647943[71] = 0.0;
   out_538340367000647943[72] = 0.0;
   out_538340367000647943[73] = 0.0;
   out_538340367000647943[74] = 0.0;
   out_538340367000647943[75] = 0.0;
   out_538340367000647943[76] = 1.0;
   out_538340367000647943[77] = 0.0;
   out_538340367000647943[78] = 0.0;
   out_538340367000647943[79] = 0.0;
   out_538340367000647943[80] = 0.0;
   out_538340367000647943[81] = 0.0;
   out_538340367000647943[82] = 0.0;
   out_538340367000647943[83] = 0.0;
   out_538340367000647943[84] = 0.0;
   out_538340367000647943[85] = 0.0;
   out_538340367000647943[86] = 0.0;
   out_538340367000647943[87] = 0.0;
   out_538340367000647943[88] = 0.0;
   out_538340367000647943[89] = 0.0;
   out_538340367000647943[90] = 0.0;
   out_538340367000647943[91] = 0.0;
   out_538340367000647943[92] = 0.0;
   out_538340367000647943[93] = 0.0;
   out_538340367000647943[94] = 0.0;
   out_538340367000647943[95] = 1.0;
   out_538340367000647943[96] = 0.0;
   out_538340367000647943[97] = 0.0;
   out_538340367000647943[98] = 0.0;
   out_538340367000647943[99] = 0.0;
   out_538340367000647943[100] = 0.0;
   out_538340367000647943[101] = 0.0;
   out_538340367000647943[102] = 0.0;
   out_538340367000647943[103] = 0.0;
   out_538340367000647943[104] = 0.0;
   out_538340367000647943[105] = 0.0;
   out_538340367000647943[106] = 0.0;
   out_538340367000647943[107] = 0.0;
   out_538340367000647943[108] = 0.0;
   out_538340367000647943[109] = 0.0;
   out_538340367000647943[110] = 0.0;
   out_538340367000647943[111] = 0.0;
   out_538340367000647943[112] = 0.0;
   out_538340367000647943[113] = 0.0;
   out_538340367000647943[114] = 1.0;
   out_538340367000647943[115] = 0.0;
   out_538340367000647943[116] = 0.0;
   out_538340367000647943[117] = 0.0;
   out_538340367000647943[118] = 0.0;
   out_538340367000647943[119] = 0.0;
   out_538340367000647943[120] = 0.0;
   out_538340367000647943[121] = 0.0;
   out_538340367000647943[122] = 0.0;
   out_538340367000647943[123] = 0.0;
   out_538340367000647943[124] = 0.0;
   out_538340367000647943[125] = 0.0;
   out_538340367000647943[126] = 0.0;
   out_538340367000647943[127] = 0.0;
   out_538340367000647943[128] = 0.0;
   out_538340367000647943[129] = 0.0;
   out_538340367000647943[130] = 0.0;
   out_538340367000647943[131] = 0.0;
   out_538340367000647943[132] = 0.0;
   out_538340367000647943[133] = 1.0;
   out_538340367000647943[134] = 0.0;
   out_538340367000647943[135] = 0.0;
   out_538340367000647943[136] = 0.0;
   out_538340367000647943[137] = 0.0;
   out_538340367000647943[138] = 0.0;
   out_538340367000647943[139] = 0.0;
   out_538340367000647943[140] = 0.0;
   out_538340367000647943[141] = 0.0;
   out_538340367000647943[142] = 0.0;
   out_538340367000647943[143] = 0.0;
   out_538340367000647943[144] = 0.0;
   out_538340367000647943[145] = 0.0;
   out_538340367000647943[146] = 0.0;
   out_538340367000647943[147] = 0.0;
   out_538340367000647943[148] = 0.0;
   out_538340367000647943[149] = 0.0;
   out_538340367000647943[150] = 0.0;
   out_538340367000647943[151] = 0.0;
   out_538340367000647943[152] = 1.0;
   out_538340367000647943[153] = 0.0;
   out_538340367000647943[154] = 0.0;
   out_538340367000647943[155] = 0.0;
   out_538340367000647943[156] = 0.0;
   out_538340367000647943[157] = 0.0;
   out_538340367000647943[158] = 0.0;
   out_538340367000647943[159] = 0.0;
   out_538340367000647943[160] = 0.0;
   out_538340367000647943[161] = 0.0;
   out_538340367000647943[162] = 0.0;
   out_538340367000647943[163] = 0.0;
   out_538340367000647943[164] = 0.0;
   out_538340367000647943[165] = 0.0;
   out_538340367000647943[166] = 0.0;
   out_538340367000647943[167] = 0.0;
   out_538340367000647943[168] = 0.0;
   out_538340367000647943[169] = 0.0;
   out_538340367000647943[170] = 0.0;
   out_538340367000647943[171] = 1.0;
   out_538340367000647943[172] = 0.0;
   out_538340367000647943[173] = 0.0;
   out_538340367000647943[174] = 0.0;
   out_538340367000647943[175] = 0.0;
   out_538340367000647943[176] = 0.0;
   out_538340367000647943[177] = 0.0;
   out_538340367000647943[178] = 0.0;
   out_538340367000647943[179] = 0.0;
   out_538340367000647943[180] = 0.0;
   out_538340367000647943[181] = 0.0;
   out_538340367000647943[182] = 0.0;
   out_538340367000647943[183] = 0.0;
   out_538340367000647943[184] = 0.0;
   out_538340367000647943[185] = 0.0;
   out_538340367000647943[186] = 0.0;
   out_538340367000647943[187] = 0.0;
   out_538340367000647943[188] = 0.0;
   out_538340367000647943[189] = 0.0;
   out_538340367000647943[190] = 1.0;
   out_538340367000647943[191] = 0.0;
   out_538340367000647943[192] = 0.0;
   out_538340367000647943[193] = 0.0;
   out_538340367000647943[194] = 0.0;
   out_538340367000647943[195] = 0.0;
   out_538340367000647943[196] = 0.0;
   out_538340367000647943[197] = 0.0;
   out_538340367000647943[198] = 0.0;
   out_538340367000647943[199] = 0.0;
   out_538340367000647943[200] = 0.0;
   out_538340367000647943[201] = 0.0;
   out_538340367000647943[202] = 0.0;
   out_538340367000647943[203] = 0.0;
   out_538340367000647943[204] = 0.0;
   out_538340367000647943[205] = 0.0;
   out_538340367000647943[206] = 0.0;
   out_538340367000647943[207] = 0.0;
   out_538340367000647943[208] = 0.0;
   out_538340367000647943[209] = 1.0;
   out_538340367000647943[210] = 0.0;
   out_538340367000647943[211] = 0.0;
   out_538340367000647943[212] = 0.0;
   out_538340367000647943[213] = 0.0;
   out_538340367000647943[214] = 0.0;
   out_538340367000647943[215] = 0.0;
   out_538340367000647943[216] = 0.0;
   out_538340367000647943[217] = 0.0;
   out_538340367000647943[218] = 0.0;
   out_538340367000647943[219] = 0.0;
   out_538340367000647943[220] = 0.0;
   out_538340367000647943[221] = 0.0;
   out_538340367000647943[222] = 0.0;
   out_538340367000647943[223] = 0.0;
   out_538340367000647943[224] = 0.0;
   out_538340367000647943[225] = 0.0;
   out_538340367000647943[226] = 0.0;
   out_538340367000647943[227] = 0.0;
   out_538340367000647943[228] = 1.0;
   out_538340367000647943[229] = 0.0;
   out_538340367000647943[230] = 0.0;
   out_538340367000647943[231] = 0.0;
   out_538340367000647943[232] = 0.0;
   out_538340367000647943[233] = 0.0;
   out_538340367000647943[234] = 0.0;
   out_538340367000647943[235] = 0.0;
   out_538340367000647943[236] = 0.0;
   out_538340367000647943[237] = 0.0;
   out_538340367000647943[238] = 0.0;
   out_538340367000647943[239] = 0.0;
   out_538340367000647943[240] = 0.0;
   out_538340367000647943[241] = 0.0;
   out_538340367000647943[242] = 0.0;
   out_538340367000647943[243] = 0.0;
   out_538340367000647943[244] = 0.0;
   out_538340367000647943[245] = 0.0;
   out_538340367000647943[246] = 0.0;
   out_538340367000647943[247] = 1.0;
   out_538340367000647943[248] = 0.0;
   out_538340367000647943[249] = 0.0;
   out_538340367000647943[250] = 0.0;
   out_538340367000647943[251] = 0.0;
   out_538340367000647943[252] = 0.0;
   out_538340367000647943[253] = 0.0;
   out_538340367000647943[254] = 0.0;
   out_538340367000647943[255] = 0.0;
   out_538340367000647943[256] = 0.0;
   out_538340367000647943[257] = 0.0;
   out_538340367000647943[258] = 0.0;
   out_538340367000647943[259] = 0.0;
   out_538340367000647943[260] = 0.0;
   out_538340367000647943[261] = 0.0;
   out_538340367000647943[262] = 0.0;
   out_538340367000647943[263] = 0.0;
   out_538340367000647943[264] = 0.0;
   out_538340367000647943[265] = 0.0;
   out_538340367000647943[266] = 1.0;
   out_538340367000647943[267] = 0.0;
   out_538340367000647943[268] = 0.0;
   out_538340367000647943[269] = 0.0;
   out_538340367000647943[270] = 0.0;
   out_538340367000647943[271] = 0.0;
   out_538340367000647943[272] = 0.0;
   out_538340367000647943[273] = 0.0;
   out_538340367000647943[274] = 0.0;
   out_538340367000647943[275] = 0.0;
   out_538340367000647943[276] = 0.0;
   out_538340367000647943[277] = 0.0;
   out_538340367000647943[278] = 0.0;
   out_538340367000647943[279] = 0.0;
   out_538340367000647943[280] = 0.0;
   out_538340367000647943[281] = 0.0;
   out_538340367000647943[282] = 0.0;
   out_538340367000647943[283] = 0.0;
   out_538340367000647943[284] = 0.0;
   out_538340367000647943[285] = 1.0;
   out_538340367000647943[286] = 0.0;
   out_538340367000647943[287] = 0.0;
   out_538340367000647943[288] = 0.0;
   out_538340367000647943[289] = 0.0;
   out_538340367000647943[290] = 0.0;
   out_538340367000647943[291] = 0.0;
   out_538340367000647943[292] = 0.0;
   out_538340367000647943[293] = 0.0;
   out_538340367000647943[294] = 0.0;
   out_538340367000647943[295] = 0.0;
   out_538340367000647943[296] = 0.0;
   out_538340367000647943[297] = 0.0;
   out_538340367000647943[298] = 0.0;
   out_538340367000647943[299] = 0.0;
   out_538340367000647943[300] = 0.0;
   out_538340367000647943[301] = 0.0;
   out_538340367000647943[302] = 0.0;
   out_538340367000647943[303] = 0.0;
   out_538340367000647943[304] = 1.0;
   out_538340367000647943[305] = 0.0;
   out_538340367000647943[306] = 0.0;
   out_538340367000647943[307] = 0.0;
   out_538340367000647943[308] = 0.0;
   out_538340367000647943[309] = 0.0;
   out_538340367000647943[310] = 0.0;
   out_538340367000647943[311] = 0.0;
   out_538340367000647943[312] = 0.0;
   out_538340367000647943[313] = 0.0;
   out_538340367000647943[314] = 0.0;
   out_538340367000647943[315] = 0.0;
   out_538340367000647943[316] = 0.0;
   out_538340367000647943[317] = 0.0;
   out_538340367000647943[318] = 0.0;
   out_538340367000647943[319] = 0.0;
   out_538340367000647943[320] = 0.0;
   out_538340367000647943[321] = 0.0;
   out_538340367000647943[322] = 0.0;
   out_538340367000647943[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_7368455278738031076) {
   out_7368455278738031076[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_7368455278738031076[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_7368455278738031076[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_7368455278738031076[3] = dt*state[12] + state[3];
   out_7368455278738031076[4] = dt*state[13] + state[4];
   out_7368455278738031076[5] = dt*state[14] + state[5];
   out_7368455278738031076[6] = state[6];
   out_7368455278738031076[7] = state[7];
   out_7368455278738031076[8] = state[8];
   out_7368455278738031076[9] = state[9];
   out_7368455278738031076[10] = state[10];
   out_7368455278738031076[11] = state[11];
   out_7368455278738031076[12] = state[12];
   out_7368455278738031076[13] = state[13];
   out_7368455278738031076[14] = state[14];
   out_7368455278738031076[15] = state[15];
   out_7368455278738031076[16] = state[16];
   out_7368455278738031076[17] = state[17];
}
void F_fun(double *state, double dt, double *out_5829154861726366619) {
   out_5829154861726366619[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5829154861726366619[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5829154861726366619[2] = 0;
   out_5829154861726366619[3] = 0;
   out_5829154861726366619[4] = 0;
   out_5829154861726366619[5] = 0;
   out_5829154861726366619[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5829154861726366619[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5829154861726366619[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5829154861726366619[9] = 0;
   out_5829154861726366619[10] = 0;
   out_5829154861726366619[11] = 0;
   out_5829154861726366619[12] = 0;
   out_5829154861726366619[13] = 0;
   out_5829154861726366619[14] = 0;
   out_5829154861726366619[15] = 0;
   out_5829154861726366619[16] = 0;
   out_5829154861726366619[17] = 0;
   out_5829154861726366619[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5829154861726366619[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5829154861726366619[20] = 0;
   out_5829154861726366619[21] = 0;
   out_5829154861726366619[22] = 0;
   out_5829154861726366619[23] = 0;
   out_5829154861726366619[24] = 0;
   out_5829154861726366619[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5829154861726366619[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5829154861726366619[27] = 0;
   out_5829154861726366619[28] = 0;
   out_5829154861726366619[29] = 0;
   out_5829154861726366619[30] = 0;
   out_5829154861726366619[31] = 0;
   out_5829154861726366619[32] = 0;
   out_5829154861726366619[33] = 0;
   out_5829154861726366619[34] = 0;
   out_5829154861726366619[35] = 0;
   out_5829154861726366619[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5829154861726366619[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5829154861726366619[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5829154861726366619[39] = 0;
   out_5829154861726366619[40] = 0;
   out_5829154861726366619[41] = 0;
   out_5829154861726366619[42] = 0;
   out_5829154861726366619[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5829154861726366619[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5829154861726366619[45] = 0;
   out_5829154861726366619[46] = 0;
   out_5829154861726366619[47] = 0;
   out_5829154861726366619[48] = 0;
   out_5829154861726366619[49] = 0;
   out_5829154861726366619[50] = 0;
   out_5829154861726366619[51] = 0;
   out_5829154861726366619[52] = 0;
   out_5829154861726366619[53] = 0;
   out_5829154861726366619[54] = 0;
   out_5829154861726366619[55] = 0;
   out_5829154861726366619[56] = 0;
   out_5829154861726366619[57] = 1;
   out_5829154861726366619[58] = 0;
   out_5829154861726366619[59] = 0;
   out_5829154861726366619[60] = 0;
   out_5829154861726366619[61] = 0;
   out_5829154861726366619[62] = 0;
   out_5829154861726366619[63] = 0;
   out_5829154861726366619[64] = 0;
   out_5829154861726366619[65] = 0;
   out_5829154861726366619[66] = dt;
   out_5829154861726366619[67] = 0;
   out_5829154861726366619[68] = 0;
   out_5829154861726366619[69] = 0;
   out_5829154861726366619[70] = 0;
   out_5829154861726366619[71] = 0;
   out_5829154861726366619[72] = 0;
   out_5829154861726366619[73] = 0;
   out_5829154861726366619[74] = 0;
   out_5829154861726366619[75] = 0;
   out_5829154861726366619[76] = 1;
   out_5829154861726366619[77] = 0;
   out_5829154861726366619[78] = 0;
   out_5829154861726366619[79] = 0;
   out_5829154861726366619[80] = 0;
   out_5829154861726366619[81] = 0;
   out_5829154861726366619[82] = 0;
   out_5829154861726366619[83] = 0;
   out_5829154861726366619[84] = 0;
   out_5829154861726366619[85] = dt;
   out_5829154861726366619[86] = 0;
   out_5829154861726366619[87] = 0;
   out_5829154861726366619[88] = 0;
   out_5829154861726366619[89] = 0;
   out_5829154861726366619[90] = 0;
   out_5829154861726366619[91] = 0;
   out_5829154861726366619[92] = 0;
   out_5829154861726366619[93] = 0;
   out_5829154861726366619[94] = 0;
   out_5829154861726366619[95] = 1;
   out_5829154861726366619[96] = 0;
   out_5829154861726366619[97] = 0;
   out_5829154861726366619[98] = 0;
   out_5829154861726366619[99] = 0;
   out_5829154861726366619[100] = 0;
   out_5829154861726366619[101] = 0;
   out_5829154861726366619[102] = 0;
   out_5829154861726366619[103] = 0;
   out_5829154861726366619[104] = dt;
   out_5829154861726366619[105] = 0;
   out_5829154861726366619[106] = 0;
   out_5829154861726366619[107] = 0;
   out_5829154861726366619[108] = 0;
   out_5829154861726366619[109] = 0;
   out_5829154861726366619[110] = 0;
   out_5829154861726366619[111] = 0;
   out_5829154861726366619[112] = 0;
   out_5829154861726366619[113] = 0;
   out_5829154861726366619[114] = 1;
   out_5829154861726366619[115] = 0;
   out_5829154861726366619[116] = 0;
   out_5829154861726366619[117] = 0;
   out_5829154861726366619[118] = 0;
   out_5829154861726366619[119] = 0;
   out_5829154861726366619[120] = 0;
   out_5829154861726366619[121] = 0;
   out_5829154861726366619[122] = 0;
   out_5829154861726366619[123] = 0;
   out_5829154861726366619[124] = 0;
   out_5829154861726366619[125] = 0;
   out_5829154861726366619[126] = 0;
   out_5829154861726366619[127] = 0;
   out_5829154861726366619[128] = 0;
   out_5829154861726366619[129] = 0;
   out_5829154861726366619[130] = 0;
   out_5829154861726366619[131] = 0;
   out_5829154861726366619[132] = 0;
   out_5829154861726366619[133] = 1;
   out_5829154861726366619[134] = 0;
   out_5829154861726366619[135] = 0;
   out_5829154861726366619[136] = 0;
   out_5829154861726366619[137] = 0;
   out_5829154861726366619[138] = 0;
   out_5829154861726366619[139] = 0;
   out_5829154861726366619[140] = 0;
   out_5829154861726366619[141] = 0;
   out_5829154861726366619[142] = 0;
   out_5829154861726366619[143] = 0;
   out_5829154861726366619[144] = 0;
   out_5829154861726366619[145] = 0;
   out_5829154861726366619[146] = 0;
   out_5829154861726366619[147] = 0;
   out_5829154861726366619[148] = 0;
   out_5829154861726366619[149] = 0;
   out_5829154861726366619[150] = 0;
   out_5829154861726366619[151] = 0;
   out_5829154861726366619[152] = 1;
   out_5829154861726366619[153] = 0;
   out_5829154861726366619[154] = 0;
   out_5829154861726366619[155] = 0;
   out_5829154861726366619[156] = 0;
   out_5829154861726366619[157] = 0;
   out_5829154861726366619[158] = 0;
   out_5829154861726366619[159] = 0;
   out_5829154861726366619[160] = 0;
   out_5829154861726366619[161] = 0;
   out_5829154861726366619[162] = 0;
   out_5829154861726366619[163] = 0;
   out_5829154861726366619[164] = 0;
   out_5829154861726366619[165] = 0;
   out_5829154861726366619[166] = 0;
   out_5829154861726366619[167] = 0;
   out_5829154861726366619[168] = 0;
   out_5829154861726366619[169] = 0;
   out_5829154861726366619[170] = 0;
   out_5829154861726366619[171] = 1;
   out_5829154861726366619[172] = 0;
   out_5829154861726366619[173] = 0;
   out_5829154861726366619[174] = 0;
   out_5829154861726366619[175] = 0;
   out_5829154861726366619[176] = 0;
   out_5829154861726366619[177] = 0;
   out_5829154861726366619[178] = 0;
   out_5829154861726366619[179] = 0;
   out_5829154861726366619[180] = 0;
   out_5829154861726366619[181] = 0;
   out_5829154861726366619[182] = 0;
   out_5829154861726366619[183] = 0;
   out_5829154861726366619[184] = 0;
   out_5829154861726366619[185] = 0;
   out_5829154861726366619[186] = 0;
   out_5829154861726366619[187] = 0;
   out_5829154861726366619[188] = 0;
   out_5829154861726366619[189] = 0;
   out_5829154861726366619[190] = 1;
   out_5829154861726366619[191] = 0;
   out_5829154861726366619[192] = 0;
   out_5829154861726366619[193] = 0;
   out_5829154861726366619[194] = 0;
   out_5829154861726366619[195] = 0;
   out_5829154861726366619[196] = 0;
   out_5829154861726366619[197] = 0;
   out_5829154861726366619[198] = 0;
   out_5829154861726366619[199] = 0;
   out_5829154861726366619[200] = 0;
   out_5829154861726366619[201] = 0;
   out_5829154861726366619[202] = 0;
   out_5829154861726366619[203] = 0;
   out_5829154861726366619[204] = 0;
   out_5829154861726366619[205] = 0;
   out_5829154861726366619[206] = 0;
   out_5829154861726366619[207] = 0;
   out_5829154861726366619[208] = 0;
   out_5829154861726366619[209] = 1;
   out_5829154861726366619[210] = 0;
   out_5829154861726366619[211] = 0;
   out_5829154861726366619[212] = 0;
   out_5829154861726366619[213] = 0;
   out_5829154861726366619[214] = 0;
   out_5829154861726366619[215] = 0;
   out_5829154861726366619[216] = 0;
   out_5829154861726366619[217] = 0;
   out_5829154861726366619[218] = 0;
   out_5829154861726366619[219] = 0;
   out_5829154861726366619[220] = 0;
   out_5829154861726366619[221] = 0;
   out_5829154861726366619[222] = 0;
   out_5829154861726366619[223] = 0;
   out_5829154861726366619[224] = 0;
   out_5829154861726366619[225] = 0;
   out_5829154861726366619[226] = 0;
   out_5829154861726366619[227] = 0;
   out_5829154861726366619[228] = 1;
   out_5829154861726366619[229] = 0;
   out_5829154861726366619[230] = 0;
   out_5829154861726366619[231] = 0;
   out_5829154861726366619[232] = 0;
   out_5829154861726366619[233] = 0;
   out_5829154861726366619[234] = 0;
   out_5829154861726366619[235] = 0;
   out_5829154861726366619[236] = 0;
   out_5829154861726366619[237] = 0;
   out_5829154861726366619[238] = 0;
   out_5829154861726366619[239] = 0;
   out_5829154861726366619[240] = 0;
   out_5829154861726366619[241] = 0;
   out_5829154861726366619[242] = 0;
   out_5829154861726366619[243] = 0;
   out_5829154861726366619[244] = 0;
   out_5829154861726366619[245] = 0;
   out_5829154861726366619[246] = 0;
   out_5829154861726366619[247] = 1;
   out_5829154861726366619[248] = 0;
   out_5829154861726366619[249] = 0;
   out_5829154861726366619[250] = 0;
   out_5829154861726366619[251] = 0;
   out_5829154861726366619[252] = 0;
   out_5829154861726366619[253] = 0;
   out_5829154861726366619[254] = 0;
   out_5829154861726366619[255] = 0;
   out_5829154861726366619[256] = 0;
   out_5829154861726366619[257] = 0;
   out_5829154861726366619[258] = 0;
   out_5829154861726366619[259] = 0;
   out_5829154861726366619[260] = 0;
   out_5829154861726366619[261] = 0;
   out_5829154861726366619[262] = 0;
   out_5829154861726366619[263] = 0;
   out_5829154861726366619[264] = 0;
   out_5829154861726366619[265] = 0;
   out_5829154861726366619[266] = 1;
   out_5829154861726366619[267] = 0;
   out_5829154861726366619[268] = 0;
   out_5829154861726366619[269] = 0;
   out_5829154861726366619[270] = 0;
   out_5829154861726366619[271] = 0;
   out_5829154861726366619[272] = 0;
   out_5829154861726366619[273] = 0;
   out_5829154861726366619[274] = 0;
   out_5829154861726366619[275] = 0;
   out_5829154861726366619[276] = 0;
   out_5829154861726366619[277] = 0;
   out_5829154861726366619[278] = 0;
   out_5829154861726366619[279] = 0;
   out_5829154861726366619[280] = 0;
   out_5829154861726366619[281] = 0;
   out_5829154861726366619[282] = 0;
   out_5829154861726366619[283] = 0;
   out_5829154861726366619[284] = 0;
   out_5829154861726366619[285] = 1;
   out_5829154861726366619[286] = 0;
   out_5829154861726366619[287] = 0;
   out_5829154861726366619[288] = 0;
   out_5829154861726366619[289] = 0;
   out_5829154861726366619[290] = 0;
   out_5829154861726366619[291] = 0;
   out_5829154861726366619[292] = 0;
   out_5829154861726366619[293] = 0;
   out_5829154861726366619[294] = 0;
   out_5829154861726366619[295] = 0;
   out_5829154861726366619[296] = 0;
   out_5829154861726366619[297] = 0;
   out_5829154861726366619[298] = 0;
   out_5829154861726366619[299] = 0;
   out_5829154861726366619[300] = 0;
   out_5829154861726366619[301] = 0;
   out_5829154861726366619[302] = 0;
   out_5829154861726366619[303] = 0;
   out_5829154861726366619[304] = 1;
   out_5829154861726366619[305] = 0;
   out_5829154861726366619[306] = 0;
   out_5829154861726366619[307] = 0;
   out_5829154861726366619[308] = 0;
   out_5829154861726366619[309] = 0;
   out_5829154861726366619[310] = 0;
   out_5829154861726366619[311] = 0;
   out_5829154861726366619[312] = 0;
   out_5829154861726366619[313] = 0;
   out_5829154861726366619[314] = 0;
   out_5829154861726366619[315] = 0;
   out_5829154861726366619[316] = 0;
   out_5829154861726366619[317] = 0;
   out_5829154861726366619[318] = 0;
   out_5829154861726366619[319] = 0;
   out_5829154861726366619[320] = 0;
   out_5829154861726366619[321] = 0;
   out_5829154861726366619[322] = 0;
   out_5829154861726366619[323] = 1;
}
void h_4(double *state, double *unused, double *out_849879868882736857) {
   out_849879868882736857[0] = state[6] + state[9];
   out_849879868882736857[1] = state[7] + state[10];
   out_849879868882736857[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_4614178018038432792) {
   out_4614178018038432792[0] = 0;
   out_4614178018038432792[1] = 0;
   out_4614178018038432792[2] = 0;
   out_4614178018038432792[3] = 0;
   out_4614178018038432792[4] = 0;
   out_4614178018038432792[5] = 0;
   out_4614178018038432792[6] = 1;
   out_4614178018038432792[7] = 0;
   out_4614178018038432792[8] = 0;
   out_4614178018038432792[9] = 1;
   out_4614178018038432792[10] = 0;
   out_4614178018038432792[11] = 0;
   out_4614178018038432792[12] = 0;
   out_4614178018038432792[13] = 0;
   out_4614178018038432792[14] = 0;
   out_4614178018038432792[15] = 0;
   out_4614178018038432792[16] = 0;
   out_4614178018038432792[17] = 0;
   out_4614178018038432792[18] = 0;
   out_4614178018038432792[19] = 0;
   out_4614178018038432792[20] = 0;
   out_4614178018038432792[21] = 0;
   out_4614178018038432792[22] = 0;
   out_4614178018038432792[23] = 0;
   out_4614178018038432792[24] = 0;
   out_4614178018038432792[25] = 1;
   out_4614178018038432792[26] = 0;
   out_4614178018038432792[27] = 0;
   out_4614178018038432792[28] = 1;
   out_4614178018038432792[29] = 0;
   out_4614178018038432792[30] = 0;
   out_4614178018038432792[31] = 0;
   out_4614178018038432792[32] = 0;
   out_4614178018038432792[33] = 0;
   out_4614178018038432792[34] = 0;
   out_4614178018038432792[35] = 0;
   out_4614178018038432792[36] = 0;
   out_4614178018038432792[37] = 0;
   out_4614178018038432792[38] = 0;
   out_4614178018038432792[39] = 0;
   out_4614178018038432792[40] = 0;
   out_4614178018038432792[41] = 0;
   out_4614178018038432792[42] = 0;
   out_4614178018038432792[43] = 0;
   out_4614178018038432792[44] = 1;
   out_4614178018038432792[45] = 0;
   out_4614178018038432792[46] = 0;
   out_4614178018038432792[47] = 1;
   out_4614178018038432792[48] = 0;
   out_4614178018038432792[49] = 0;
   out_4614178018038432792[50] = 0;
   out_4614178018038432792[51] = 0;
   out_4614178018038432792[52] = 0;
   out_4614178018038432792[53] = 0;
}
void h_10(double *state, double *unused, double *out_4738835720535906003) {
   out_4738835720535906003[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_4738835720535906003[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_4738835720535906003[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_5846382860599074085) {
   out_5846382860599074085[0] = 0;
   out_5846382860599074085[1] = 9.8100000000000005*cos(state[1]);
   out_5846382860599074085[2] = 0;
   out_5846382860599074085[3] = 0;
   out_5846382860599074085[4] = -state[8];
   out_5846382860599074085[5] = state[7];
   out_5846382860599074085[6] = 0;
   out_5846382860599074085[7] = state[5];
   out_5846382860599074085[8] = -state[4];
   out_5846382860599074085[9] = 0;
   out_5846382860599074085[10] = 0;
   out_5846382860599074085[11] = 0;
   out_5846382860599074085[12] = 1;
   out_5846382860599074085[13] = 0;
   out_5846382860599074085[14] = 0;
   out_5846382860599074085[15] = 1;
   out_5846382860599074085[16] = 0;
   out_5846382860599074085[17] = 0;
   out_5846382860599074085[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_5846382860599074085[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_5846382860599074085[20] = 0;
   out_5846382860599074085[21] = state[8];
   out_5846382860599074085[22] = 0;
   out_5846382860599074085[23] = -state[6];
   out_5846382860599074085[24] = -state[5];
   out_5846382860599074085[25] = 0;
   out_5846382860599074085[26] = state[3];
   out_5846382860599074085[27] = 0;
   out_5846382860599074085[28] = 0;
   out_5846382860599074085[29] = 0;
   out_5846382860599074085[30] = 0;
   out_5846382860599074085[31] = 1;
   out_5846382860599074085[32] = 0;
   out_5846382860599074085[33] = 0;
   out_5846382860599074085[34] = 1;
   out_5846382860599074085[35] = 0;
   out_5846382860599074085[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_5846382860599074085[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_5846382860599074085[38] = 0;
   out_5846382860599074085[39] = -state[7];
   out_5846382860599074085[40] = state[6];
   out_5846382860599074085[41] = 0;
   out_5846382860599074085[42] = state[4];
   out_5846382860599074085[43] = -state[3];
   out_5846382860599074085[44] = 0;
   out_5846382860599074085[45] = 0;
   out_5846382860599074085[46] = 0;
   out_5846382860599074085[47] = 0;
   out_5846382860599074085[48] = 0;
   out_5846382860599074085[49] = 0;
   out_5846382860599074085[50] = 1;
   out_5846382860599074085[51] = 0;
   out_5846382860599074085[52] = 0;
   out_5846382860599074085[53] = 1;
}
void h_13(double *state, double *unused, double *out_5334730689834359579) {
   out_5334730689834359579[0] = state[3];
   out_5334730689834359579[1] = state[4];
   out_5334730689834359579[2] = state[5];
}
void H_13(double *state, double *unused, double *out_7826451843370765593) {
   out_7826451843370765593[0] = 0;
   out_7826451843370765593[1] = 0;
   out_7826451843370765593[2] = 0;
   out_7826451843370765593[3] = 1;
   out_7826451843370765593[4] = 0;
   out_7826451843370765593[5] = 0;
   out_7826451843370765593[6] = 0;
   out_7826451843370765593[7] = 0;
   out_7826451843370765593[8] = 0;
   out_7826451843370765593[9] = 0;
   out_7826451843370765593[10] = 0;
   out_7826451843370765593[11] = 0;
   out_7826451843370765593[12] = 0;
   out_7826451843370765593[13] = 0;
   out_7826451843370765593[14] = 0;
   out_7826451843370765593[15] = 0;
   out_7826451843370765593[16] = 0;
   out_7826451843370765593[17] = 0;
   out_7826451843370765593[18] = 0;
   out_7826451843370765593[19] = 0;
   out_7826451843370765593[20] = 0;
   out_7826451843370765593[21] = 0;
   out_7826451843370765593[22] = 1;
   out_7826451843370765593[23] = 0;
   out_7826451843370765593[24] = 0;
   out_7826451843370765593[25] = 0;
   out_7826451843370765593[26] = 0;
   out_7826451843370765593[27] = 0;
   out_7826451843370765593[28] = 0;
   out_7826451843370765593[29] = 0;
   out_7826451843370765593[30] = 0;
   out_7826451843370765593[31] = 0;
   out_7826451843370765593[32] = 0;
   out_7826451843370765593[33] = 0;
   out_7826451843370765593[34] = 0;
   out_7826451843370765593[35] = 0;
   out_7826451843370765593[36] = 0;
   out_7826451843370765593[37] = 0;
   out_7826451843370765593[38] = 0;
   out_7826451843370765593[39] = 0;
   out_7826451843370765593[40] = 0;
   out_7826451843370765593[41] = 1;
   out_7826451843370765593[42] = 0;
   out_7826451843370765593[43] = 0;
   out_7826451843370765593[44] = 0;
   out_7826451843370765593[45] = 0;
   out_7826451843370765593[46] = 0;
   out_7826451843370765593[47] = 0;
   out_7826451843370765593[48] = 0;
   out_7826451843370765593[49] = 0;
   out_7826451843370765593[50] = 0;
   out_7826451843370765593[51] = 0;
   out_7826451843370765593[52] = 0;
   out_7826451843370765593[53] = 0;
}
void h_14(double *state, double *unused, double *out_7621092473786206501) {
   out_7621092473786206501[0] = state[6];
   out_7621092473786206501[1] = state[7];
   out_7621092473786206501[2] = state[8];
}
void H_14(double *state, double *unused, double *out_1531389585743060496) {
   out_1531389585743060496[0] = 0;
   out_1531389585743060496[1] = 0;
   out_1531389585743060496[2] = 0;
   out_1531389585743060496[3] = 0;
   out_1531389585743060496[4] = 0;
   out_1531389585743060496[5] = 0;
   out_1531389585743060496[6] = 1;
   out_1531389585743060496[7] = 0;
   out_1531389585743060496[8] = 0;
   out_1531389585743060496[9] = 0;
   out_1531389585743060496[10] = 0;
   out_1531389585743060496[11] = 0;
   out_1531389585743060496[12] = 0;
   out_1531389585743060496[13] = 0;
   out_1531389585743060496[14] = 0;
   out_1531389585743060496[15] = 0;
   out_1531389585743060496[16] = 0;
   out_1531389585743060496[17] = 0;
   out_1531389585743060496[18] = 0;
   out_1531389585743060496[19] = 0;
   out_1531389585743060496[20] = 0;
   out_1531389585743060496[21] = 0;
   out_1531389585743060496[22] = 0;
   out_1531389585743060496[23] = 0;
   out_1531389585743060496[24] = 0;
   out_1531389585743060496[25] = 1;
   out_1531389585743060496[26] = 0;
   out_1531389585743060496[27] = 0;
   out_1531389585743060496[28] = 0;
   out_1531389585743060496[29] = 0;
   out_1531389585743060496[30] = 0;
   out_1531389585743060496[31] = 0;
   out_1531389585743060496[32] = 0;
   out_1531389585743060496[33] = 0;
   out_1531389585743060496[34] = 0;
   out_1531389585743060496[35] = 0;
   out_1531389585743060496[36] = 0;
   out_1531389585743060496[37] = 0;
   out_1531389585743060496[38] = 0;
   out_1531389585743060496[39] = 0;
   out_1531389585743060496[40] = 0;
   out_1531389585743060496[41] = 0;
   out_1531389585743060496[42] = 0;
   out_1531389585743060496[43] = 0;
   out_1531389585743060496[44] = 1;
   out_1531389585743060496[45] = 0;
   out_1531389585743060496[46] = 0;
   out_1531389585743060496[47] = 0;
   out_1531389585743060496[48] = 0;
   out_1531389585743060496[49] = 0;
   out_1531389585743060496[50] = 0;
   out_1531389585743060496[51] = 0;
   out_1531389585743060496[52] = 0;
   out_1531389585743060496[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_8464988186513175073) {
  err_fun(nom_x, delta_x, out_8464988186513175073);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1852709291048557817) {
  inv_err_fun(nom_x, true_x, out_1852709291048557817);
}
void pose_H_mod_fun(double *state, double *out_538340367000647943) {
  H_mod_fun(state, out_538340367000647943);
}
void pose_f_fun(double *state, double dt, double *out_7368455278738031076) {
  f_fun(state,  dt, out_7368455278738031076);
}
void pose_F_fun(double *state, double dt, double *out_5829154861726366619) {
  F_fun(state,  dt, out_5829154861726366619);
}
void pose_h_4(double *state, double *unused, double *out_849879868882736857) {
  h_4(state, unused, out_849879868882736857);
}
void pose_H_4(double *state, double *unused, double *out_4614178018038432792) {
  H_4(state, unused, out_4614178018038432792);
}
void pose_h_10(double *state, double *unused, double *out_4738835720535906003) {
  h_10(state, unused, out_4738835720535906003);
}
void pose_H_10(double *state, double *unused, double *out_5846382860599074085) {
  H_10(state, unused, out_5846382860599074085);
}
void pose_h_13(double *state, double *unused, double *out_5334730689834359579) {
  h_13(state, unused, out_5334730689834359579);
}
void pose_H_13(double *state, double *unused, double *out_7826451843370765593) {
  H_13(state, unused, out_7826451843370765593);
}
void pose_h_14(double *state, double *unused, double *out_7621092473786206501) {
  h_14(state, unused, out_7621092473786206501);
}
void pose_H_14(double *state, double *unused, double *out_1531389585743060496) {
  H_14(state, unused, out_1531389585743060496);
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
