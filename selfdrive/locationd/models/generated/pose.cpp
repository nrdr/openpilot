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
void err_fun(double *nom_x, double *delta_x, double *out_2990975860512923391) {
   out_2990975860512923391[0] = delta_x[0] + nom_x[0];
   out_2990975860512923391[1] = delta_x[1] + nom_x[1];
   out_2990975860512923391[2] = delta_x[2] + nom_x[2];
   out_2990975860512923391[3] = delta_x[3] + nom_x[3];
   out_2990975860512923391[4] = delta_x[4] + nom_x[4];
   out_2990975860512923391[5] = delta_x[5] + nom_x[5];
   out_2990975860512923391[6] = delta_x[6] + nom_x[6];
   out_2990975860512923391[7] = delta_x[7] + nom_x[7];
   out_2990975860512923391[8] = delta_x[8] + nom_x[8];
   out_2990975860512923391[9] = delta_x[9] + nom_x[9];
   out_2990975860512923391[10] = delta_x[10] + nom_x[10];
   out_2990975860512923391[11] = delta_x[11] + nom_x[11];
   out_2990975860512923391[12] = delta_x[12] + nom_x[12];
   out_2990975860512923391[13] = delta_x[13] + nom_x[13];
   out_2990975860512923391[14] = delta_x[14] + nom_x[14];
   out_2990975860512923391[15] = delta_x[15] + nom_x[15];
   out_2990975860512923391[16] = delta_x[16] + nom_x[16];
   out_2990975860512923391[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_8589403635603503433) {
   out_8589403635603503433[0] = -nom_x[0] + true_x[0];
   out_8589403635603503433[1] = -nom_x[1] + true_x[1];
   out_8589403635603503433[2] = -nom_x[2] + true_x[2];
   out_8589403635603503433[3] = -nom_x[3] + true_x[3];
   out_8589403635603503433[4] = -nom_x[4] + true_x[4];
   out_8589403635603503433[5] = -nom_x[5] + true_x[5];
   out_8589403635603503433[6] = -nom_x[6] + true_x[6];
   out_8589403635603503433[7] = -nom_x[7] + true_x[7];
   out_8589403635603503433[8] = -nom_x[8] + true_x[8];
   out_8589403635603503433[9] = -nom_x[9] + true_x[9];
   out_8589403635603503433[10] = -nom_x[10] + true_x[10];
   out_8589403635603503433[11] = -nom_x[11] + true_x[11];
   out_8589403635603503433[12] = -nom_x[12] + true_x[12];
   out_8589403635603503433[13] = -nom_x[13] + true_x[13];
   out_8589403635603503433[14] = -nom_x[14] + true_x[14];
   out_8589403635603503433[15] = -nom_x[15] + true_x[15];
   out_8589403635603503433[16] = -nom_x[16] + true_x[16];
   out_8589403635603503433[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_2750295583345837463) {
   out_2750295583345837463[0] = 1.0;
   out_2750295583345837463[1] = 0.0;
   out_2750295583345837463[2] = 0.0;
   out_2750295583345837463[3] = 0.0;
   out_2750295583345837463[4] = 0.0;
   out_2750295583345837463[5] = 0.0;
   out_2750295583345837463[6] = 0.0;
   out_2750295583345837463[7] = 0.0;
   out_2750295583345837463[8] = 0.0;
   out_2750295583345837463[9] = 0.0;
   out_2750295583345837463[10] = 0.0;
   out_2750295583345837463[11] = 0.0;
   out_2750295583345837463[12] = 0.0;
   out_2750295583345837463[13] = 0.0;
   out_2750295583345837463[14] = 0.0;
   out_2750295583345837463[15] = 0.0;
   out_2750295583345837463[16] = 0.0;
   out_2750295583345837463[17] = 0.0;
   out_2750295583345837463[18] = 0.0;
   out_2750295583345837463[19] = 1.0;
   out_2750295583345837463[20] = 0.0;
   out_2750295583345837463[21] = 0.0;
   out_2750295583345837463[22] = 0.0;
   out_2750295583345837463[23] = 0.0;
   out_2750295583345837463[24] = 0.0;
   out_2750295583345837463[25] = 0.0;
   out_2750295583345837463[26] = 0.0;
   out_2750295583345837463[27] = 0.0;
   out_2750295583345837463[28] = 0.0;
   out_2750295583345837463[29] = 0.0;
   out_2750295583345837463[30] = 0.0;
   out_2750295583345837463[31] = 0.0;
   out_2750295583345837463[32] = 0.0;
   out_2750295583345837463[33] = 0.0;
   out_2750295583345837463[34] = 0.0;
   out_2750295583345837463[35] = 0.0;
   out_2750295583345837463[36] = 0.0;
   out_2750295583345837463[37] = 0.0;
   out_2750295583345837463[38] = 1.0;
   out_2750295583345837463[39] = 0.0;
   out_2750295583345837463[40] = 0.0;
   out_2750295583345837463[41] = 0.0;
   out_2750295583345837463[42] = 0.0;
   out_2750295583345837463[43] = 0.0;
   out_2750295583345837463[44] = 0.0;
   out_2750295583345837463[45] = 0.0;
   out_2750295583345837463[46] = 0.0;
   out_2750295583345837463[47] = 0.0;
   out_2750295583345837463[48] = 0.0;
   out_2750295583345837463[49] = 0.0;
   out_2750295583345837463[50] = 0.0;
   out_2750295583345837463[51] = 0.0;
   out_2750295583345837463[52] = 0.0;
   out_2750295583345837463[53] = 0.0;
   out_2750295583345837463[54] = 0.0;
   out_2750295583345837463[55] = 0.0;
   out_2750295583345837463[56] = 0.0;
   out_2750295583345837463[57] = 1.0;
   out_2750295583345837463[58] = 0.0;
   out_2750295583345837463[59] = 0.0;
   out_2750295583345837463[60] = 0.0;
   out_2750295583345837463[61] = 0.0;
   out_2750295583345837463[62] = 0.0;
   out_2750295583345837463[63] = 0.0;
   out_2750295583345837463[64] = 0.0;
   out_2750295583345837463[65] = 0.0;
   out_2750295583345837463[66] = 0.0;
   out_2750295583345837463[67] = 0.0;
   out_2750295583345837463[68] = 0.0;
   out_2750295583345837463[69] = 0.0;
   out_2750295583345837463[70] = 0.0;
   out_2750295583345837463[71] = 0.0;
   out_2750295583345837463[72] = 0.0;
   out_2750295583345837463[73] = 0.0;
   out_2750295583345837463[74] = 0.0;
   out_2750295583345837463[75] = 0.0;
   out_2750295583345837463[76] = 1.0;
   out_2750295583345837463[77] = 0.0;
   out_2750295583345837463[78] = 0.0;
   out_2750295583345837463[79] = 0.0;
   out_2750295583345837463[80] = 0.0;
   out_2750295583345837463[81] = 0.0;
   out_2750295583345837463[82] = 0.0;
   out_2750295583345837463[83] = 0.0;
   out_2750295583345837463[84] = 0.0;
   out_2750295583345837463[85] = 0.0;
   out_2750295583345837463[86] = 0.0;
   out_2750295583345837463[87] = 0.0;
   out_2750295583345837463[88] = 0.0;
   out_2750295583345837463[89] = 0.0;
   out_2750295583345837463[90] = 0.0;
   out_2750295583345837463[91] = 0.0;
   out_2750295583345837463[92] = 0.0;
   out_2750295583345837463[93] = 0.0;
   out_2750295583345837463[94] = 0.0;
   out_2750295583345837463[95] = 1.0;
   out_2750295583345837463[96] = 0.0;
   out_2750295583345837463[97] = 0.0;
   out_2750295583345837463[98] = 0.0;
   out_2750295583345837463[99] = 0.0;
   out_2750295583345837463[100] = 0.0;
   out_2750295583345837463[101] = 0.0;
   out_2750295583345837463[102] = 0.0;
   out_2750295583345837463[103] = 0.0;
   out_2750295583345837463[104] = 0.0;
   out_2750295583345837463[105] = 0.0;
   out_2750295583345837463[106] = 0.0;
   out_2750295583345837463[107] = 0.0;
   out_2750295583345837463[108] = 0.0;
   out_2750295583345837463[109] = 0.0;
   out_2750295583345837463[110] = 0.0;
   out_2750295583345837463[111] = 0.0;
   out_2750295583345837463[112] = 0.0;
   out_2750295583345837463[113] = 0.0;
   out_2750295583345837463[114] = 1.0;
   out_2750295583345837463[115] = 0.0;
   out_2750295583345837463[116] = 0.0;
   out_2750295583345837463[117] = 0.0;
   out_2750295583345837463[118] = 0.0;
   out_2750295583345837463[119] = 0.0;
   out_2750295583345837463[120] = 0.0;
   out_2750295583345837463[121] = 0.0;
   out_2750295583345837463[122] = 0.0;
   out_2750295583345837463[123] = 0.0;
   out_2750295583345837463[124] = 0.0;
   out_2750295583345837463[125] = 0.0;
   out_2750295583345837463[126] = 0.0;
   out_2750295583345837463[127] = 0.0;
   out_2750295583345837463[128] = 0.0;
   out_2750295583345837463[129] = 0.0;
   out_2750295583345837463[130] = 0.0;
   out_2750295583345837463[131] = 0.0;
   out_2750295583345837463[132] = 0.0;
   out_2750295583345837463[133] = 1.0;
   out_2750295583345837463[134] = 0.0;
   out_2750295583345837463[135] = 0.0;
   out_2750295583345837463[136] = 0.0;
   out_2750295583345837463[137] = 0.0;
   out_2750295583345837463[138] = 0.0;
   out_2750295583345837463[139] = 0.0;
   out_2750295583345837463[140] = 0.0;
   out_2750295583345837463[141] = 0.0;
   out_2750295583345837463[142] = 0.0;
   out_2750295583345837463[143] = 0.0;
   out_2750295583345837463[144] = 0.0;
   out_2750295583345837463[145] = 0.0;
   out_2750295583345837463[146] = 0.0;
   out_2750295583345837463[147] = 0.0;
   out_2750295583345837463[148] = 0.0;
   out_2750295583345837463[149] = 0.0;
   out_2750295583345837463[150] = 0.0;
   out_2750295583345837463[151] = 0.0;
   out_2750295583345837463[152] = 1.0;
   out_2750295583345837463[153] = 0.0;
   out_2750295583345837463[154] = 0.0;
   out_2750295583345837463[155] = 0.0;
   out_2750295583345837463[156] = 0.0;
   out_2750295583345837463[157] = 0.0;
   out_2750295583345837463[158] = 0.0;
   out_2750295583345837463[159] = 0.0;
   out_2750295583345837463[160] = 0.0;
   out_2750295583345837463[161] = 0.0;
   out_2750295583345837463[162] = 0.0;
   out_2750295583345837463[163] = 0.0;
   out_2750295583345837463[164] = 0.0;
   out_2750295583345837463[165] = 0.0;
   out_2750295583345837463[166] = 0.0;
   out_2750295583345837463[167] = 0.0;
   out_2750295583345837463[168] = 0.0;
   out_2750295583345837463[169] = 0.0;
   out_2750295583345837463[170] = 0.0;
   out_2750295583345837463[171] = 1.0;
   out_2750295583345837463[172] = 0.0;
   out_2750295583345837463[173] = 0.0;
   out_2750295583345837463[174] = 0.0;
   out_2750295583345837463[175] = 0.0;
   out_2750295583345837463[176] = 0.0;
   out_2750295583345837463[177] = 0.0;
   out_2750295583345837463[178] = 0.0;
   out_2750295583345837463[179] = 0.0;
   out_2750295583345837463[180] = 0.0;
   out_2750295583345837463[181] = 0.0;
   out_2750295583345837463[182] = 0.0;
   out_2750295583345837463[183] = 0.0;
   out_2750295583345837463[184] = 0.0;
   out_2750295583345837463[185] = 0.0;
   out_2750295583345837463[186] = 0.0;
   out_2750295583345837463[187] = 0.0;
   out_2750295583345837463[188] = 0.0;
   out_2750295583345837463[189] = 0.0;
   out_2750295583345837463[190] = 1.0;
   out_2750295583345837463[191] = 0.0;
   out_2750295583345837463[192] = 0.0;
   out_2750295583345837463[193] = 0.0;
   out_2750295583345837463[194] = 0.0;
   out_2750295583345837463[195] = 0.0;
   out_2750295583345837463[196] = 0.0;
   out_2750295583345837463[197] = 0.0;
   out_2750295583345837463[198] = 0.0;
   out_2750295583345837463[199] = 0.0;
   out_2750295583345837463[200] = 0.0;
   out_2750295583345837463[201] = 0.0;
   out_2750295583345837463[202] = 0.0;
   out_2750295583345837463[203] = 0.0;
   out_2750295583345837463[204] = 0.0;
   out_2750295583345837463[205] = 0.0;
   out_2750295583345837463[206] = 0.0;
   out_2750295583345837463[207] = 0.0;
   out_2750295583345837463[208] = 0.0;
   out_2750295583345837463[209] = 1.0;
   out_2750295583345837463[210] = 0.0;
   out_2750295583345837463[211] = 0.0;
   out_2750295583345837463[212] = 0.0;
   out_2750295583345837463[213] = 0.0;
   out_2750295583345837463[214] = 0.0;
   out_2750295583345837463[215] = 0.0;
   out_2750295583345837463[216] = 0.0;
   out_2750295583345837463[217] = 0.0;
   out_2750295583345837463[218] = 0.0;
   out_2750295583345837463[219] = 0.0;
   out_2750295583345837463[220] = 0.0;
   out_2750295583345837463[221] = 0.0;
   out_2750295583345837463[222] = 0.0;
   out_2750295583345837463[223] = 0.0;
   out_2750295583345837463[224] = 0.0;
   out_2750295583345837463[225] = 0.0;
   out_2750295583345837463[226] = 0.0;
   out_2750295583345837463[227] = 0.0;
   out_2750295583345837463[228] = 1.0;
   out_2750295583345837463[229] = 0.0;
   out_2750295583345837463[230] = 0.0;
   out_2750295583345837463[231] = 0.0;
   out_2750295583345837463[232] = 0.0;
   out_2750295583345837463[233] = 0.0;
   out_2750295583345837463[234] = 0.0;
   out_2750295583345837463[235] = 0.0;
   out_2750295583345837463[236] = 0.0;
   out_2750295583345837463[237] = 0.0;
   out_2750295583345837463[238] = 0.0;
   out_2750295583345837463[239] = 0.0;
   out_2750295583345837463[240] = 0.0;
   out_2750295583345837463[241] = 0.0;
   out_2750295583345837463[242] = 0.0;
   out_2750295583345837463[243] = 0.0;
   out_2750295583345837463[244] = 0.0;
   out_2750295583345837463[245] = 0.0;
   out_2750295583345837463[246] = 0.0;
   out_2750295583345837463[247] = 1.0;
   out_2750295583345837463[248] = 0.0;
   out_2750295583345837463[249] = 0.0;
   out_2750295583345837463[250] = 0.0;
   out_2750295583345837463[251] = 0.0;
   out_2750295583345837463[252] = 0.0;
   out_2750295583345837463[253] = 0.0;
   out_2750295583345837463[254] = 0.0;
   out_2750295583345837463[255] = 0.0;
   out_2750295583345837463[256] = 0.0;
   out_2750295583345837463[257] = 0.0;
   out_2750295583345837463[258] = 0.0;
   out_2750295583345837463[259] = 0.0;
   out_2750295583345837463[260] = 0.0;
   out_2750295583345837463[261] = 0.0;
   out_2750295583345837463[262] = 0.0;
   out_2750295583345837463[263] = 0.0;
   out_2750295583345837463[264] = 0.0;
   out_2750295583345837463[265] = 0.0;
   out_2750295583345837463[266] = 1.0;
   out_2750295583345837463[267] = 0.0;
   out_2750295583345837463[268] = 0.0;
   out_2750295583345837463[269] = 0.0;
   out_2750295583345837463[270] = 0.0;
   out_2750295583345837463[271] = 0.0;
   out_2750295583345837463[272] = 0.0;
   out_2750295583345837463[273] = 0.0;
   out_2750295583345837463[274] = 0.0;
   out_2750295583345837463[275] = 0.0;
   out_2750295583345837463[276] = 0.0;
   out_2750295583345837463[277] = 0.0;
   out_2750295583345837463[278] = 0.0;
   out_2750295583345837463[279] = 0.0;
   out_2750295583345837463[280] = 0.0;
   out_2750295583345837463[281] = 0.0;
   out_2750295583345837463[282] = 0.0;
   out_2750295583345837463[283] = 0.0;
   out_2750295583345837463[284] = 0.0;
   out_2750295583345837463[285] = 1.0;
   out_2750295583345837463[286] = 0.0;
   out_2750295583345837463[287] = 0.0;
   out_2750295583345837463[288] = 0.0;
   out_2750295583345837463[289] = 0.0;
   out_2750295583345837463[290] = 0.0;
   out_2750295583345837463[291] = 0.0;
   out_2750295583345837463[292] = 0.0;
   out_2750295583345837463[293] = 0.0;
   out_2750295583345837463[294] = 0.0;
   out_2750295583345837463[295] = 0.0;
   out_2750295583345837463[296] = 0.0;
   out_2750295583345837463[297] = 0.0;
   out_2750295583345837463[298] = 0.0;
   out_2750295583345837463[299] = 0.0;
   out_2750295583345837463[300] = 0.0;
   out_2750295583345837463[301] = 0.0;
   out_2750295583345837463[302] = 0.0;
   out_2750295583345837463[303] = 0.0;
   out_2750295583345837463[304] = 1.0;
   out_2750295583345837463[305] = 0.0;
   out_2750295583345837463[306] = 0.0;
   out_2750295583345837463[307] = 0.0;
   out_2750295583345837463[308] = 0.0;
   out_2750295583345837463[309] = 0.0;
   out_2750295583345837463[310] = 0.0;
   out_2750295583345837463[311] = 0.0;
   out_2750295583345837463[312] = 0.0;
   out_2750295583345837463[313] = 0.0;
   out_2750295583345837463[314] = 0.0;
   out_2750295583345837463[315] = 0.0;
   out_2750295583345837463[316] = 0.0;
   out_2750295583345837463[317] = 0.0;
   out_2750295583345837463[318] = 0.0;
   out_2750295583345837463[319] = 0.0;
   out_2750295583345837463[320] = 0.0;
   out_2750295583345837463[321] = 0.0;
   out_2750295583345837463[322] = 0.0;
   out_2750295583345837463[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_2722954666226833811) {
   out_2722954666226833811[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_2722954666226833811[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_2722954666226833811[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_2722954666226833811[3] = dt*state[12] + state[3];
   out_2722954666226833811[4] = dt*state[13] + state[4];
   out_2722954666226833811[5] = dt*state[14] + state[5];
   out_2722954666226833811[6] = state[6];
   out_2722954666226833811[7] = state[7];
   out_2722954666226833811[8] = state[8];
   out_2722954666226833811[9] = state[9];
   out_2722954666226833811[10] = state[10];
   out_2722954666226833811[11] = state[11];
   out_2722954666226833811[12] = state[12];
   out_2722954666226833811[13] = state[13];
   out_2722954666226833811[14] = state[14];
   out_2722954666226833811[15] = state[15];
   out_2722954666226833811[16] = state[16];
   out_2722954666226833811[17] = state[17];
}
void F_fun(double *state, double dt, double *out_5728593125393536167) {
   out_5728593125393536167[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5728593125393536167[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5728593125393536167[2] = 0;
   out_5728593125393536167[3] = 0;
   out_5728593125393536167[4] = 0;
   out_5728593125393536167[5] = 0;
   out_5728593125393536167[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5728593125393536167[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5728593125393536167[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5728593125393536167[9] = 0;
   out_5728593125393536167[10] = 0;
   out_5728593125393536167[11] = 0;
   out_5728593125393536167[12] = 0;
   out_5728593125393536167[13] = 0;
   out_5728593125393536167[14] = 0;
   out_5728593125393536167[15] = 0;
   out_5728593125393536167[16] = 0;
   out_5728593125393536167[17] = 0;
   out_5728593125393536167[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5728593125393536167[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5728593125393536167[20] = 0;
   out_5728593125393536167[21] = 0;
   out_5728593125393536167[22] = 0;
   out_5728593125393536167[23] = 0;
   out_5728593125393536167[24] = 0;
   out_5728593125393536167[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5728593125393536167[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5728593125393536167[27] = 0;
   out_5728593125393536167[28] = 0;
   out_5728593125393536167[29] = 0;
   out_5728593125393536167[30] = 0;
   out_5728593125393536167[31] = 0;
   out_5728593125393536167[32] = 0;
   out_5728593125393536167[33] = 0;
   out_5728593125393536167[34] = 0;
   out_5728593125393536167[35] = 0;
   out_5728593125393536167[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5728593125393536167[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5728593125393536167[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5728593125393536167[39] = 0;
   out_5728593125393536167[40] = 0;
   out_5728593125393536167[41] = 0;
   out_5728593125393536167[42] = 0;
   out_5728593125393536167[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5728593125393536167[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5728593125393536167[45] = 0;
   out_5728593125393536167[46] = 0;
   out_5728593125393536167[47] = 0;
   out_5728593125393536167[48] = 0;
   out_5728593125393536167[49] = 0;
   out_5728593125393536167[50] = 0;
   out_5728593125393536167[51] = 0;
   out_5728593125393536167[52] = 0;
   out_5728593125393536167[53] = 0;
   out_5728593125393536167[54] = 0;
   out_5728593125393536167[55] = 0;
   out_5728593125393536167[56] = 0;
   out_5728593125393536167[57] = 1;
   out_5728593125393536167[58] = 0;
   out_5728593125393536167[59] = 0;
   out_5728593125393536167[60] = 0;
   out_5728593125393536167[61] = 0;
   out_5728593125393536167[62] = 0;
   out_5728593125393536167[63] = 0;
   out_5728593125393536167[64] = 0;
   out_5728593125393536167[65] = 0;
   out_5728593125393536167[66] = dt;
   out_5728593125393536167[67] = 0;
   out_5728593125393536167[68] = 0;
   out_5728593125393536167[69] = 0;
   out_5728593125393536167[70] = 0;
   out_5728593125393536167[71] = 0;
   out_5728593125393536167[72] = 0;
   out_5728593125393536167[73] = 0;
   out_5728593125393536167[74] = 0;
   out_5728593125393536167[75] = 0;
   out_5728593125393536167[76] = 1;
   out_5728593125393536167[77] = 0;
   out_5728593125393536167[78] = 0;
   out_5728593125393536167[79] = 0;
   out_5728593125393536167[80] = 0;
   out_5728593125393536167[81] = 0;
   out_5728593125393536167[82] = 0;
   out_5728593125393536167[83] = 0;
   out_5728593125393536167[84] = 0;
   out_5728593125393536167[85] = dt;
   out_5728593125393536167[86] = 0;
   out_5728593125393536167[87] = 0;
   out_5728593125393536167[88] = 0;
   out_5728593125393536167[89] = 0;
   out_5728593125393536167[90] = 0;
   out_5728593125393536167[91] = 0;
   out_5728593125393536167[92] = 0;
   out_5728593125393536167[93] = 0;
   out_5728593125393536167[94] = 0;
   out_5728593125393536167[95] = 1;
   out_5728593125393536167[96] = 0;
   out_5728593125393536167[97] = 0;
   out_5728593125393536167[98] = 0;
   out_5728593125393536167[99] = 0;
   out_5728593125393536167[100] = 0;
   out_5728593125393536167[101] = 0;
   out_5728593125393536167[102] = 0;
   out_5728593125393536167[103] = 0;
   out_5728593125393536167[104] = dt;
   out_5728593125393536167[105] = 0;
   out_5728593125393536167[106] = 0;
   out_5728593125393536167[107] = 0;
   out_5728593125393536167[108] = 0;
   out_5728593125393536167[109] = 0;
   out_5728593125393536167[110] = 0;
   out_5728593125393536167[111] = 0;
   out_5728593125393536167[112] = 0;
   out_5728593125393536167[113] = 0;
   out_5728593125393536167[114] = 1;
   out_5728593125393536167[115] = 0;
   out_5728593125393536167[116] = 0;
   out_5728593125393536167[117] = 0;
   out_5728593125393536167[118] = 0;
   out_5728593125393536167[119] = 0;
   out_5728593125393536167[120] = 0;
   out_5728593125393536167[121] = 0;
   out_5728593125393536167[122] = 0;
   out_5728593125393536167[123] = 0;
   out_5728593125393536167[124] = 0;
   out_5728593125393536167[125] = 0;
   out_5728593125393536167[126] = 0;
   out_5728593125393536167[127] = 0;
   out_5728593125393536167[128] = 0;
   out_5728593125393536167[129] = 0;
   out_5728593125393536167[130] = 0;
   out_5728593125393536167[131] = 0;
   out_5728593125393536167[132] = 0;
   out_5728593125393536167[133] = 1;
   out_5728593125393536167[134] = 0;
   out_5728593125393536167[135] = 0;
   out_5728593125393536167[136] = 0;
   out_5728593125393536167[137] = 0;
   out_5728593125393536167[138] = 0;
   out_5728593125393536167[139] = 0;
   out_5728593125393536167[140] = 0;
   out_5728593125393536167[141] = 0;
   out_5728593125393536167[142] = 0;
   out_5728593125393536167[143] = 0;
   out_5728593125393536167[144] = 0;
   out_5728593125393536167[145] = 0;
   out_5728593125393536167[146] = 0;
   out_5728593125393536167[147] = 0;
   out_5728593125393536167[148] = 0;
   out_5728593125393536167[149] = 0;
   out_5728593125393536167[150] = 0;
   out_5728593125393536167[151] = 0;
   out_5728593125393536167[152] = 1;
   out_5728593125393536167[153] = 0;
   out_5728593125393536167[154] = 0;
   out_5728593125393536167[155] = 0;
   out_5728593125393536167[156] = 0;
   out_5728593125393536167[157] = 0;
   out_5728593125393536167[158] = 0;
   out_5728593125393536167[159] = 0;
   out_5728593125393536167[160] = 0;
   out_5728593125393536167[161] = 0;
   out_5728593125393536167[162] = 0;
   out_5728593125393536167[163] = 0;
   out_5728593125393536167[164] = 0;
   out_5728593125393536167[165] = 0;
   out_5728593125393536167[166] = 0;
   out_5728593125393536167[167] = 0;
   out_5728593125393536167[168] = 0;
   out_5728593125393536167[169] = 0;
   out_5728593125393536167[170] = 0;
   out_5728593125393536167[171] = 1;
   out_5728593125393536167[172] = 0;
   out_5728593125393536167[173] = 0;
   out_5728593125393536167[174] = 0;
   out_5728593125393536167[175] = 0;
   out_5728593125393536167[176] = 0;
   out_5728593125393536167[177] = 0;
   out_5728593125393536167[178] = 0;
   out_5728593125393536167[179] = 0;
   out_5728593125393536167[180] = 0;
   out_5728593125393536167[181] = 0;
   out_5728593125393536167[182] = 0;
   out_5728593125393536167[183] = 0;
   out_5728593125393536167[184] = 0;
   out_5728593125393536167[185] = 0;
   out_5728593125393536167[186] = 0;
   out_5728593125393536167[187] = 0;
   out_5728593125393536167[188] = 0;
   out_5728593125393536167[189] = 0;
   out_5728593125393536167[190] = 1;
   out_5728593125393536167[191] = 0;
   out_5728593125393536167[192] = 0;
   out_5728593125393536167[193] = 0;
   out_5728593125393536167[194] = 0;
   out_5728593125393536167[195] = 0;
   out_5728593125393536167[196] = 0;
   out_5728593125393536167[197] = 0;
   out_5728593125393536167[198] = 0;
   out_5728593125393536167[199] = 0;
   out_5728593125393536167[200] = 0;
   out_5728593125393536167[201] = 0;
   out_5728593125393536167[202] = 0;
   out_5728593125393536167[203] = 0;
   out_5728593125393536167[204] = 0;
   out_5728593125393536167[205] = 0;
   out_5728593125393536167[206] = 0;
   out_5728593125393536167[207] = 0;
   out_5728593125393536167[208] = 0;
   out_5728593125393536167[209] = 1;
   out_5728593125393536167[210] = 0;
   out_5728593125393536167[211] = 0;
   out_5728593125393536167[212] = 0;
   out_5728593125393536167[213] = 0;
   out_5728593125393536167[214] = 0;
   out_5728593125393536167[215] = 0;
   out_5728593125393536167[216] = 0;
   out_5728593125393536167[217] = 0;
   out_5728593125393536167[218] = 0;
   out_5728593125393536167[219] = 0;
   out_5728593125393536167[220] = 0;
   out_5728593125393536167[221] = 0;
   out_5728593125393536167[222] = 0;
   out_5728593125393536167[223] = 0;
   out_5728593125393536167[224] = 0;
   out_5728593125393536167[225] = 0;
   out_5728593125393536167[226] = 0;
   out_5728593125393536167[227] = 0;
   out_5728593125393536167[228] = 1;
   out_5728593125393536167[229] = 0;
   out_5728593125393536167[230] = 0;
   out_5728593125393536167[231] = 0;
   out_5728593125393536167[232] = 0;
   out_5728593125393536167[233] = 0;
   out_5728593125393536167[234] = 0;
   out_5728593125393536167[235] = 0;
   out_5728593125393536167[236] = 0;
   out_5728593125393536167[237] = 0;
   out_5728593125393536167[238] = 0;
   out_5728593125393536167[239] = 0;
   out_5728593125393536167[240] = 0;
   out_5728593125393536167[241] = 0;
   out_5728593125393536167[242] = 0;
   out_5728593125393536167[243] = 0;
   out_5728593125393536167[244] = 0;
   out_5728593125393536167[245] = 0;
   out_5728593125393536167[246] = 0;
   out_5728593125393536167[247] = 1;
   out_5728593125393536167[248] = 0;
   out_5728593125393536167[249] = 0;
   out_5728593125393536167[250] = 0;
   out_5728593125393536167[251] = 0;
   out_5728593125393536167[252] = 0;
   out_5728593125393536167[253] = 0;
   out_5728593125393536167[254] = 0;
   out_5728593125393536167[255] = 0;
   out_5728593125393536167[256] = 0;
   out_5728593125393536167[257] = 0;
   out_5728593125393536167[258] = 0;
   out_5728593125393536167[259] = 0;
   out_5728593125393536167[260] = 0;
   out_5728593125393536167[261] = 0;
   out_5728593125393536167[262] = 0;
   out_5728593125393536167[263] = 0;
   out_5728593125393536167[264] = 0;
   out_5728593125393536167[265] = 0;
   out_5728593125393536167[266] = 1;
   out_5728593125393536167[267] = 0;
   out_5728593125393536167[268] = 0;
   out_5728593125393536167[269] = 0;
   out_5728593125393536167[270] = 0;
   out_5728593125393536167[271] = 0;
   out_5728593125393536167[272] = 0;
   out_5728593125393536167[273] = 0;
   out_5728593125393536167[274] = 0;
   out_5728593125393536167[275] = 0;
   out_5728593125393536167[276] = 0;
   out_5728593125393536167[277] = 0;
   out_5728593125393536167[278] = 0;
   out_5728593125393536167[279] = 0;
   out_5728593125393536167[280] = 0;
   out_5728593125393536167[281] = 0;
   out_5728593125393536167[282] = 0;
   out_5728593125393536167[283] = 0;
   out_5728593125393536167[284] = 0;
   out_5728593125393536167[285] = 1;
   out_5728593125393536167[286] = 0;
   out_5728593125393536167[287] = 0;
   out_5728593125393536167[288] = 0;
   out_5728593125393536167[289] = 0;
   out_5728593125393536167[290] = 0;
   out_5728593125393536167[291] = 0;
   out_5728593125393536167[292] = 0;
   out_5728593125393536167[293] = 0;
   out_5728593125393536167[294] = 0;
   out_5728593125393536167[295] = 0;
   out_5728593125393536167[296] = 0;
   out_5728593125393536167[297] = 0;
   out_5728593125393536167[298] = 0;
   out_5728593125393536167[299] = 0;
   out_5728593125393536167[300] = 0;
   out_5728593125393536167[301] = 0;
   out_5728593125393536167[302] = 0;
   out_5728593125393536167[303] = 0;
   out_5728593125393536167[304] = 1;
   out_5728593125393536167[305] = 0;
   out_5728593125393536167[306] = 0;
   out_5728593125393536167[307] = 0;
   out_5728593125393536167[308] = 0;
   out_5728593125393536167[309] = 0;
   out_5728593125393536167[310] = 0;
   out_5728593125393536167[311] = 0;
   out_5728593125393536167[312] = 0;
   out_5728593125393536167[313] = 0;
   out_5728593125393536167[314] = 0;
   out_5728593125393536167[315] = 0;
   out_5728593125393536167[316] = 0;
   out_5728593125393536167[317] = 0;
   out_5728593125393536167[318] = 0;
   out_5728593125393536167[319] = 0;
   out_5728593125393536167[320] = 0;
   out_5728593125393536167[321] = 0;
   out_5728593125393536167[322] = 0;
   out_5728593125393536167[323] = 1;
}
void h_4(double *state, double *unused, double *out_7945281333303209547) {
   out_7945281333303209547[0] = state[6] + state[9];
   out_7945281333303209547[1] = state[7] + state[10];
   out_7945281333303209547[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_5280460880052190141) {
   out_5280460880052190141[0] = 0;
   out_5280460880052190141[1] = 0;
   out_5280460880052190141[2] = 0;
   out_5280460880052190141[3] = 0;
   out_5280460880052190141[4] = 0;
   out_5280460880052190141[5] = 0;
   out_5280460880052190141[6] = 1;
   out_5280460880052190141[7] = 0;
   out_5280460880052190141[8] = 0;
   out_5280460880052190141[9] = 1;
   out_5280460880052190141[10] = 0;
   out_5280460880052190141[11] = 0;
   out_5280460880052190141[12] = 0;
   out_5280460880052190141[13] = 0;
   out_5280460880052190141[14] = 0;
   out_5280460880052190141[15] = 0;
   out_5280460880052190141[16] = 0;
   out_5280460880052190141[17] = 0;
   out_5280460880052190141[18] = 0;
   out_5280460880052190141[19] = 0;
   out_5280460880052190141[20] = 0;
   out_5280460880052190141[21] = 0;
   out_5280460880052190141[22] = 0;
   out_5280460880052190141[23] = 0;
   out_5280460880052190141[24] = 0;
   out_5280460880052190141[25] = 1;
   out_5280460880052190141[26] = 0;
   out_5280460880052190141[27] = 0;
   out_5280460880052190141[28] = 1;
   out_5280460880052190141[29] = 0;
   out_5280460880052190141[30] = 0;
   out_5280460880052190141[31] = 0;
   out_5280460880052190141[32] = 0;
   out_5280460880052190141[33] = 0;
   out_5280460880052190141[34] = 0;
   out_5280460880052190141[35] = 0;
   out_5280460880052190141[36] = 0;
   out_5280460880052190141[37] = 0;
   out_5280460880052190141[38] = 0;
   out_5280460880052190141[39] = 0;
   out_5280460880052190141[40] = 0;
   out_5280460880052190141[41] = 0;
   out_5280460880052190141[42] = 0;
   out_5280460880052190141[43] = 0;
   out_5280460880052190141[44] = 1;
   out_5280460880052190141[45] = 0;
   out_5280460880052190141[46] = 0;
   out_5280460880052190141[47] = 1;
   out_5280460880052190141[48] = 0;
   out_5280460880052190141[49] = 0;
   out_5280460880052190141[50] = 0;
   out_5280460880052190141[51] = 0;
   out_5280460880052190141[52] = 0;
   out_5280460880052190141[53] = 0;
}
void h_10(double *state, double *unused, double *out_1469163044313279183) {
   out_1469163044313279183[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_1469163044313279183[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_1469163044313279183[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_4991129487684167274) {
   out_4991129487684167274[0] = 0;
   out_4991129487684167274[1] = 9.8100000000000005*cos(state[1]);
   out_4991129487684167274[2] = 0;
   out_4991129487684167274[3] = 0;
   out_4991129487684167274[4] = -state[8];
   out_4991129487684167274[5] = state[7];
   out_4991129487684167274[6] = 0;
   out_4991129487684167274[7] = state[5];
   out_4991129487684167274[8] = -state[4];
   out_4991129487684167274[9] = 0;
   out_4991129487684167274[10] = 0;
   out_4991129487684167274[11] = 0;
   out_4991129487684167274[12] = 1;
   out_4991129487684167274[13] = 0;
   out_4991129487684167274[14] = 0;
   out_4991129487684167274[15] = 1;
   out_4991129487684167274[16] = 0;
   out_4991129487684167274[17] = 0;
   out_4991129487684167274[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_4991129487684167274[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_4991129487684167274[20] = 0;
   out_4991129487684167274[21] = state[8];
   out_4991129487684167274[22] = 0;
   out_4991129487684167274[23] = -state[6];
   out_4991129487684167274[24] = -state[5];
   out_4991129487684167274[25] = 0;
   out_4991129487684167274[26] = state[3];
   out_4991129487684167274[27] = 0;
   out_4991129487684167274[28] = 0;
   out_4991129487684167274[29] = 0;
   out_4991129487684167274[30] = 0;
   out_4991129487684167274[31] = 1;
   out_4991129487684167274[32] = 0;
   out_4991129487684167274[33] = 0;
   out_4991129487684167274[34] = 1;
   out_4991129487684167274[35] = 0;
   out_4991129487684167274[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_4991129487684167274[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_4991129487684167274[38] = 0;
   out_4991129487684167274[39] = -state[7];
   out_4991129487684167274[40] = state[6];
   out_4991129487684167274[41] = 0;
   out_4991129487684167274[42] = state[4];
   out_4991129487684167274[43] = -state[3];
   out_4991129487684167274[44] = 0;
   out_4991129487684167274[45] = 0;
   out_4991129487684167274[46] = 0;
   out_4991129487684167274[47] = 0;
   out_4991129487684167274[48] = 0;
   out_4991129487684167274[49] = 0;
   out_4991129487684167274[50] = 1;
   out_4991129487684167274[51] = 0;
   out_4991129487684167274[52] = 0;
   out_4991129487684167274[53] = 1;
}
void h_13(double *state, double *unused, double *out_4398527889198662382) {
   out_4398527889198662382[0] = state[3];
   out_4398527889198662382[1] = state[4];
   out_4398527889198662382[2] = state[5];
}
void H_13(double *state, double *unused, double *out_8492734705384522942) {
   out_8492734705384522942[0] = 0;
   out_8492734705384522942[1] = 0;
   out_8492734705384522942[2] = 0;
   out_8492734705384522942[3] = 1;
   out_8492734705384522942[4] = 0;
   out_8492734705384522942[5] = 0;
   out_8492734705384522942[6] = 0;
   out_8492734705384522942[7] = 0;
   out_8492734705384522942[8] = 0;
   out_8492734705384522942[9] = 0;
   out_8492734705384522942[10] = 0;
   out_8492734705384522942[11] = 0;
   out_8492734705384522942[12] = 0;
   out_8492734705384522942[13] = 0;
   out_8492734705384522942[14] = 0;
   out_8492734705384522942[15] = 0;
   out_8492734705384522942[16] = 0;
   out_8492734705384522942[17] = 0;
   out_8492734705384522942[18] = 0;
   out_8492734705384522942[19] = 0;
   out_8492734705384522942[20] = 0;
   out_8492734705384522942[21] = 0;
   out_8492734705384522942[22] = 1;
   out_8492734705384522942[23] = 0;
   out_8492734705384522942[24] = 0;
   out_8492734705384522942[25] = 0;
   out_8492734705384522942[26] = 0;
   out_8492734705384522942[27] = 0;
   out_8492734705384522942[28] = 0;
   out_8492734705384522942[29] = 0;
   out_8492734705384522942[30] = 0;
   out_8492734705384522942[31] = 0;
   out_8492734705384522942[32] = 0;
   out_8492734705384522942[33] = 0;
   out_8492734705384522942[34] = 0;
   out_8492734705384522942[35] = 0;
   out_8492734705384522942[36] = 0;
   out_8492734705384522942[37] = 0;
   out_8492734705384522942[38] = 0;
   out_8492734705384522942[39] = 0;
   out_8492734705384522942[40] = 0;
   out_8492734705384522942[41] = 1;
   out_8492734705384522942[42] = 0;
   out_8492734705384522942[43] = 0;
   out_8492734705384522942[44] = 0;
   out_8492734705384522942[45] = 0;
   out_8492734705384522942[46] = 0;
   out_8492734705384522942[47] = 0;
   out_8492734705384522942[48] = 0;
   out_8492734705384522942[49] = 0;
   out_8492734705384522942[50] = 0;
   out_8492734705384522942[51] = 0;
   out_8492734705384522942[52] = 0;
   out_8492734705384522942[53] = 0;
}
void h_14(double *state, double *unused, double *out_8724855652154765618) {
   out_8724855652154765618[0] = state[6];
   out_8724855652154765618[1] = state[7];
   out_8724855652154765618[2] = state[8];
}
void H_14(double *state, double *unused, double *out_9203042337317876946) {
   out_9203042337317876946[0] = 0;
   out_9203042337317876946[1] = 0;
   out_9203042337317876946[2] = 0;
   out_9203042337317876946[3] = 0;
   out_9203042337317876946[4] = 0;
   out_9203042337317876946[5] = 0;
   out_9203042337317876946[6] = 1;
   out_9203042337317876946[7] = 0;
   out_9203042337317876946[8] = 0;
   out_9203042337317876946[9] = 0;
   out_9203042337317876946[10] = 0;
   out_9203042337317876946[11] = 0;
   out_9203042337317876946[12] = 0;
   out_9203042337317876946[13] = 0;
   out_9203042337317876946[14] = 0;
   out_9203042337317876946[15] = 0;
   out_9203042337317876946[16] = 0;
   out_9203042337317876946[17] = 0;
   out_9203042337317876946[18] = 0;
   out_9203042337317876946[19] = 0;
   out_9203042337317876946[20] = 0;
   out_9203042337317876946[21] = 0;
   out_9203042337317876946[22] = 0;
   out_9203042337317876946[23] = 0;
   out_9203042337317876946[24] = 0;
   out_9203042337317876946[25] = 1;
   out_9203042337317876946[26] = 0;
   out_9203042337317876946[27] = 0;
   out_9203042337317876946[28] = 0;
   out_9203042337317876946[29] = 0;
   out_9203042337317876946[30] = 0;
   out_9203042337317876946[31] = 0;
   out_9203042337317876946[32] = 0;
   out_9203042337317876946[33] = 0;
   out_9203042337317876946[34] = 0;
   out_9203042337317876946[35] = 0;
   out_9203042337317876946[36] = 0;
   out_9203042337317876946[37] = 0;
   out_9203042337317876946[38] = 0;
   out_9203042337317876946[39] = 0;
   out_9203042337317876946[40] = 0;
   out_9203042337317876946[41] = 0;
   out_9203042337317876946[42] = 0;
   out_9203042337317876946[43] = 0;
   out_9203042337317876946[44] = 1;
   out_9203042337317876946[45] = 0;
   out_9203042337317876946[46] = 0;
   out_9203042337317876946[47] = 0;
   out_9203042337317876946[48] = 0;
   out_9203042337317876946[49] = 0;
   out_9203042337317876946[50] = 0;
   out_9203042337317876946[51] = 0;
   out_9203042337317876946[52] = 0;
   out_9203042337317876946[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_2990975860512923391) {
  err_fun(nom_x, delta_x, out_2990975860512923391);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_8589403635603503433) {
  inv_err_fun(nom_x, true_x, out_8589403635603503433);
}
void pose_H_mod_fun(double *state, double *out_2750295583345837463) {
  H_mod_fun(state, out_2750295583345837463);
}
void pose_f_fun(double *state, double dt, double *out_2722954666226833811) {
  f_fun(state,  dt, out_2722954666226833811);
}
void pose_F_fun(double *state, double dt, double *out_5728593125393536167) {
  F_fun(state,  dt, out_5728593125393536167);
}
void pose_h_4(double *state, double *unused, double *out_7945281333303209547) {
  h_4(state, unused, out_7945281333303209547);
}
void pose_H_4(double *state, double *unused, double *out_5280460880052190141) {
  H_4(state, unused, out_5280460880052190141);
}
void pose_h_10(double *state, double *unused, double *out_1469163044313279183) {
  h_10(state, unused, out_1469163044313279183);
}
void pose_H_10(double *state, double *unused, double *out_4991129487684167274) {
  H_10(state, unused, out_4991129487684167274);
}
void pose_h_13(double *state, double *unused, double *out_4398527889198662382) {
  h_13(state, unused, out_4398527889198662382);
}
void pose_H_13(double *state, double *unused, double *out_8492734705384522942) {
  H_13(state, unused, out_8492734705384522942);
}
void pose_h_14(double *state, double *unused, double *out_8724855652154765618) {
  h_14(state, unused, out_8724855652154765618);
}
void pose_H_14(double *state, double *unused, double *out_9203042337317876946) {
  H_14(state, unused, out_9203042337317876946);
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
