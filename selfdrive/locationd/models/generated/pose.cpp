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
void err_fun(double *nom_x, double *delta_x, double *out_7254010466112148474) {
   out_7254010466112148474[0] = delta_x[0] + nom_x[0];
   out_7254010466112148474[1] = delta_x[1] + nom_x[1];
   out_7254010466112148474[2] = delta_x[2] + nom_x[2];
   out_7254010466112148474[3] = delta_x[3] + nom_x[3];
   out_7254010466112148474[4] = delta_x[4] + nom_x[4];
   out_7254010466112148474[5] = delta_x[5] + nom_x[5];
   out_7254010466112148474[6] = delta_x[6] + nom_x[6];
   out_7254010466112148474[7] = delta_x[7] + nom_x[7];
   out_7254010466112148474[8] = delta_x[8] + nom_x[8];
   out_7254010466112148474[9] = delta_x[9] + nom_x[9];
   out_7254010466112148474[10] = delta_x[10] + nom_x[10];
   out_7254010466112148474[11] = delta_x[11] + nom_x[11];
   out_7254010466112148474[12] = delta_x[12] + nom_x[12];
   out_7254010466112148474[13] = delta_x[13] + nom_x[13];
   out_7254010466112148474[14] = delta_x[14] + nom_x[14];
   out_7254010466112148474[15] = delta_x[15] + nom_x[15];
   out_7254010466112148474[16] = delta_x[16] + nom_x[16];
   out_7254010466112148474[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7571376916876272361) {
   out_7571376916876272361[0] = -nom_x[0] + true_x[0];
   out_7571376916876272361[1] = -nom_x[1] + true_x[1];
   out_7571376916876272361[2] = -nom_x[2] + true_x[2];
   out_7571376916876272361[3] = -nom_x[3] + true_x[3];
   out_7571376916876272361[4] = -nom_x[4] + true_x[4];
   out_7571376916876272361[5] = -nom_x[5] + true_x[5];
   out_7571376916876272361[6] = -nom_x[6] + true_x[6];
   out_7571376916876272361[7] = -nom_x[7] + true_x[7];
   out_7571376916876272361[8] = -nom_x[8] + true_x[8];
   out_7571376916876272361[9] = -nom_x[9] + true_x[9];
   out_7571376916876272361[10] = -nom_x[10] + true_x[10];
   out_7571376916876272361[11] = -nom_x[11] + true_x[11];
   out_7571376916876272361[12] = -nom_x[12] + true_x[12];
   out_7571376916876272361[13] = -nom_x[13] + true_x[13];
   out_7571376916876272361[14] = -nom_x[14] + true_x[14];
   out_7571376916876272361[15] = -nom_x[15] + true_x[15];
   out_7571376916876272361[16] = -nom_x[16] + true_x[16];
   out_7571376916876272361[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_2541048523476695545) {
   out_2541048523476695545[0] = 1.0;
   out_2541048523476695545[1] = 0.0;
   out_2541048523476695545[2] = 0.0;
   out_2541048523476695545[3] = 0.0;
   out_2541048523476695545[4] = 0.0;
   out_2541048523476695545[5] = 0.0;
   out_2541048523476695545[6] = 0.0;
   out_2541048523476695545[7] = 0.0;
   out_2541048523476695545[8] = 0.0;
   out_2541048523476695545[9] = 0.0;
   out_2541048523476695545[10] = 0.0;
   out_2541048523476695545[11] = 0.0;
   out_2541048523476695545[12] = 0.0;
   out_2541048523476695545[13] = 0.0;
   out_2541048523476695545[14] = 0.0;
   out_2541048523476695545[15] = 0.0;
   out_2541048523476695545[16] = 0.0;
   out_2541048523476695545[17] = 0.0;
   out_2541048523476695545[18] = 0.0;
   out_2541048523476695545[19] = 1.0;
   out_2541048523476695545[20] = 0.0;
   out_2541048523476695545[21] = 0.0;
   out_2541048523476695545[22] = 0.0;
   out_2541048523476695545[23] = 0.0;
   out_2541048523476695545[24] = 0.0;
   out_2541048523476695545[25] = 0.0;
   out_2541048523476695545[26] = 0.0;
   out_2541048523476695545[27] = 0.0;
   out_2541048523476695545[28] = 0.0;
   out_2541048523476695545[29] = 0.0;
   out_2541048523476695545[30] = 0.0;
   out_2541048523476695545[31] = 0.0;
   out_2541048523476695545[32] = 0.0;
   out_2541048523476695545[33] = 0.0;
   out_2541048523476695545[34] = 0.0;
   out_2541048523476695545[35] = 0.0;
   out_2541048523476695545[36] = 0.0;
   out_2541048523476695545[37] = 0.0;
   out_2541048523476695545[38] = 1.0;
   out_2541048523476695545[39] = 0.0;
   out_2541048523476695545[40] = 0.0;
   out_2541048523476695545[41] = 0.0;
   out_2541048523476695545[42] = 0.0;
   out_2541048523476695545[43] = 0.0;
   out_2541048523476695545[44] = 0.0;
   out_2541048523476695545[45] = 0.0;
   out_2541048523476695545[46] = 0.0;
   out_2541048523476695545[47] = 0.0;
   out_2541048523476695545[48] = 0.0;
   out_2541048523476695545[49] = 0.0;
   out_2541048523476695545[50] = 0.0;
   out_2541048523476695545[51] = 0.0;
   out_2541048523476695545[52] = 0.0;
   out_2541048523476695545[53] = 0.0;
   out_2541048523476695545[54] = 0.0;
   out_2541048523476695545[55] = 0.0;
   out_2541048523476695545[56] = 0.0;
   out_2541048523476695545[57] = 1.0;
   out_2541048523476695545[58] = 0.0;
   out_2541048523476695545[59] = 0.0;
   out_2541048523476695545[60] = 0.0;
   out_2541048523476695545[61] = 0.0;
   out_2541048523476695545[62] = 0.0;
   out_2541048523476695545[63] = 0.0;
   out_2541048523476695545[64] = 0.0;
   out_2541048523476695545[65] = 0.0;
   out_2541048523476695545[66] = 0.0;
   out_2541048523476695545[67] = 0.0;
   out_2541048523476695545[68] = 0.0;
   out_2541048523476695545[69] = 0.0;
   out_2541048523476695545[70] = 0.0;
   out_2541048523476695545[71] = 0.0;
   out_2541048523476695545[72] = 0.0;
   out_2541048523476695545[73] = 0.0;
   out_2541048523476695545[74] = 0.0;
   out_2541048523476695545[75] = 0.0;
   out_2541048523476695545[76] = 1.0;
   out_2541048523476695545[77] = 0.0;
   out_2541048523476695545[78] = 0.0;
   out_2541048523476695545[79] = 0.0;
   out_2541048523476695545[80] = 0.0;
   out_2541048523476695545[81] = 0.0;
   out_2541048523476695545[82] = 0.0;
   out_2541048523476695545[83] = 0.0;
   out_2541048523476695545[84] = 0.0;
   out_2541048523476695545[85] = 0.0;
   out_2541048523476695545[86] = 0.0;
   out_2541048523476695545[87] = 0.0;
   out_2541048523476695545[88] = 0.0;
   out_2541048523476695545[89] = 0.0;
   out_2541048523476695545[90] = 0.0;
   out_2541048523476695545[91] = 0.0;
   out_2541048523476695545[92] = 0.0;
   out_2541048523476695545[93] = 0.0;
   out_2541048523476695545[94] = 0.0;
   out_2541048523476695545[95] = 1.0;
   out_2541048523476695545[96] = 0.0;
   out_2541048523476695545[97] = 0.0;
   out_2541048523476695545[98] = 0.0;
   out_2541048523476695545[99] = 0.0;
   out_2541048523476695545[100] = 0.0;
   out_2541048523476695545[101] = 0.0;
   out_2541048523476695545[102] = 0.0;
   out_2541048523476695545[103] = 0.0;
   out_2541048523476695545[104] = 0.0;
   out_2541048523476695545[105] = 0.0;
   out_2541048523476695545[106] = 0.0;
   out_2541048523476695545[107] = 0.0;
   out_2541048523476695545[108] = 0.0;
   out_2541048523476695545[109] = 0.0;
   out_2541048523476695545[110] = 0.0;
   out_2541048523476695545[111] = 0.0;
   out_2541048523476695545[112] = 0.0;
   out_2541048523476695545[113] = 0.0;
   out_2541048523476695545[114] = 1.0;
   out_2541048523476695545[115] = 0.0;
   out_2541048523476695545[116] = 0.0;
   out_2541048523476695545[117] = 0.0;
   out_2541048523476695545[118] = 0.0;
   out_2541048523476695545[119] = 0.0;
   out_2541048523476695545[120] = 0.0;
   out_2541048523476695545[121] = 0.0;
   out_2541048523476695545[122] = 0.0;
   out_2541048523476695545[123] = 0.0;
   out_2541048523476695545[124] = 0.0;
   out_2541048523476695545[125] = 0.0;
   out_2541048523476695545[126] = 0.0;
   out_2541048523476695545[127] = 0.0;
   out_2541048523476695545[128] = 0.0;
   out_2541048523476695545[129] = 0.0;
   out_2541048523476695545[130] = 0.0;
   out_2541048523476695545[131] = 0.0;
   out_2541048523476695545[132] = 0.0;
   out_2541048523476695545[133] = 1.0;
   out_2541048523476695545[134] = 0.0;
   out_2541048523476695545[135] = 0.0;
   out_2541048523476695545[136] = 0.0;
   out_2541048523476695545[137] = 0.0;
   out_2541048523476695545[138] = 0.0;
   out_2541048523476695545[139] = 0.0;
   out_2541048523476695545[140] = 0.0;
   out_2541048523476695545[141] = 0.0;
   out_2541048523476695545[142] = 0.0;
   out_2541048523476695545[143] = 0.0;
   out_2541048523476695545[144] = 0.0;
   out_2541048523476695545[145] = 0.0;
   out_2541048523476695545[146] = 0.0;
   out_2541048523476695545[147] = 0.0;
   out_2541048523476695545[148] = 0.0;
   out_2541048523476695545[149] = 0.0;
   out_2541048523476695545[150] = 0.0;
   out_2541048523476695545[151] = 0.0;
   out_2541048523476695545[152] = 1.0;
   out_2541048523476695545[153] = 0.0;
   out_2541048523476695545[154] = 0.0;
   out_2541048523476695545[155] = 0.0;
   out_2541048523476695545[156] = 0.0;
   out_2541048523476695545[157] = 0.0;
   out_2541048523476695545[158] = 0.0;
   out_2541048523476695545[159] = 0.0;
   out_2541048523476695545[160] = 0.0;
   out_2541048523476695545[161] = 0.0;
   out_2541048523476695545[162] = 0.0;
   out_2541048523476695545[163] = 0.0;
   out_2541048523476695545[164] = 0.0;
   out_2541048523476695545[165] = 0.0;
   out_2541048523476695545[166] = 0.0;
   out_2541048523476695545[167] = 0.0;
   out_2541048523476695545[168] = 0.0;
   out_2541048523476695545[169] = 0.0;
   out_2541048523476695545[170] = 0.0;
   out_2541048523476695545[171] = 1.0;
   out_2541048523476695545[172] = 0.0;
   out_2541048523476695545[173] = 0.0;
   out_2541048523476695545[174] = 0.0;
   out_2541048523476695545[175] = 0.0;
   out_2541048523476695545[176] = 0.0;
   out_2541048523476695545[177] = 0.0;
   out_2541048523476695545[178] = 0.0;
   out_2541048523476695545[179] = 0.0;
   out_2541048523476695545[180] = 0.0;
   out_2541048523476695545[181] = 0.0;
   out_2541048523476695545[182] = 0.0;
   out_2541048523476695545[183] = 0.0;
   out_2541048523476695545[184] = 0.0;
   out_2541048523476695545[185] = 0.0;
   out_2541048523476695545[186] = 0.0;
   out_2541048523476695545[187] = 0.0;
   out_2541048523476695545[188] = 0.0;
   out_2541048523476695545[189] = 0.0;
   out_2541048523476695545[190] = 1.0;
   out_2541048523476695545[191] = 0.0;
   out_2541048523476695545[192] = 0.0;
   out_2541048523476695545[193] = 0.0;
   out_2541048523476695545[194] = 0.0;
   out_2541048523476695545[195] = 0.0;
   out_2541048523476695545[196] = 0.0;
   out_2541048523476695545[197] = 0.0;
   out_2541048523476695545[198] = 0.0;
   out_2541048523476695545[199] = 0.0;
   out_2541048523476695545[200] = 0.0;
   out_2541048523476695545[201] = 0.0;
   out_2541048523476695545[202] = 0.0;
   out_2541048523476695545[203] = 0.0;
   out_2541048523476695545[204] = 0.0;
   out_2541048523476695545[205] = 0.0;
   out_2541048523476695545[206] = 0.0;
   out_2541048523476695545[207] = 0.0;
   out_2541048523476695545[208] = 0.0;
   out_2541048523476695545[209] = 1.0;
   out_2541048523476695545[210] = 0.0;
   out_2541048523476695545[211] = 0.0;
   out_2541048523476695545[212] = 0.0;
   out_2541048523476695545[213] = 0.0;
   out_2541048523476695545[214] = 0.0;
   out_2541048523476695545[215] = 0.0;
   out_2541048523476695545[216] = 0.0;
   out_2541048523476695545[217] = 0.0;
   out_2541048523476695545[218] = 0.0;
   out_2541048523476695545[219] = 0.0;
   out_2541048523476695545[220] = 0.0;
   out_2541048523476695545[221] = 0.0;
   out_2541048523476695545[222] = 0.0;
   out_2541048523476695545[223] = 0.0;
   out_2541048523476695545[224] = 0.0;
   out_2541048523476695545[225] = 0.0;
   out_2541048523476695545[226] = 0.0;
   out_2541048523476695545[227] = 0.0;
   out_2541048523476695545[228] = 1.0;
   out_2541048523476695545[229] = 0.0;
   out_2541048523476695545[230] = 0.0;
   out_2541048523476695545[231] = 0.0;
   out_2541048523476695545[232] = 0.0;
   out_2541048523476695545[233] = 0.0;
   out_2541048523476695545[234] = 0.0;
   out_2541048523476695545[235] = 0.0;
   out_2541048523476695545[236] = 0.0;
   out_2541048523476695545[237] = 0.0;
   out_2541048523476695545[238] = 0.0;
   out_2541048523476695545[239] = 0.0;
   out_2541048523476695545[240] = 0.0;
   out_2541048523476695545[241] = 0.0;
   out_2541048523476695545[242] = 0.0;
   out_2541048523476695545[243] = 0.0;
   out_2541048523476695545[244] = 0.0;
   out_2541048523476695545[245] = 0.0;
   out_2541048523476695545[246] = 0.0;
   out_2541048523476695545[247] = 1.0;
   out_2541048523476695545[248] = 0.0;
   out_2541048523476695545[249] = 0.0;
   out_2541048523476695545[250] = 0.0;
   out_2541048523476695545[251] = 0.0;
   out_2541048523476695545[252] = 0.0;
   out_2541048523476695545[253] = 0.0;
   out_2541048523476695545[254] = 0.0;
   out_2541048523476695545[255] = 0.0;
   out_2541048523476695545[256] = 0.0;
   out_2541048523476695545[257] = 0.0;
   out_2541048523476695545[258] = 0.0;
   out_2541048523476695545[259] = 0.0;
   out_2541048523476695545[260] = 0.0;
   out_2541048523476695545[261] = 0.0;
   out_2541048523476695545[262] = 0.0;
   out_2541048523476695545[263] = 0.0;
   out_2541048523476695545[264] = 0.0;
   out_2541048523476695545[265] = 0.0;
   out_2541048523476695545[266] = 1.0;
   out_2541048523476695545[267] = 0.0;
   out_2541048523476695545[268] = 0.0;
   out_2541048523476695545[269] = 0.0;
   out_2541048523476695545[270] = 0.0;
   out_2541048523476695545[271] = 0.0;
   out_2541048523476695545[272] = 0.0;
   out_2541048523476695545[273] = 0.0;
   out_2541048523476695545[274] = 0.0;
   out_2541048523476695545[275] = 0.0;
   out_2541048523476695545[276] = 0.0;
   out_2541048523476695545[277] = 0.0;
   out_2541048523476695545[278] = 0.0;
   out_2541048523476695545[279] = 0.0;
   out_2541048523476695545[280] = 0.0;
   out_2541048523476695545[281] = 0.0;
   out_2541048523476695545[282] = 0.0;
   out_2541048523476695545[283] = 0.0;
   out_2541048523476695545[284] = 0.0;
   out_2541048523476695545[285] = 1.0;
   out_2541048523476695545[286] = 0.0;
   out_2541048523476695545[287] = 0.0;
   out_2541048523476695545[288] = 0.0;
   out_2541048523476695545[289] = 0.0;
   out_2541048523476695545[290] = 0.0;
   out_2541048523476695545[291] = 0.0;
   out_2541048523476695545[292] = 0.0;
   out_2541048523476695545[293] = 0.0;
   out_2541048523476695545[294] = 0.0;
   out_2541048523476695545[295] = 0.0;
   out_2541048523476695545[296] = 0.0;
   out_2541048523476695545[297] = 0.0;
   out_2541048523476695545[298] = 0.0;
   out_2541048523476695545[299] = 0.0;
   out_2541048523476695545[300] = 0.0;
   out_2541048523476695545[301] = 0.0;
   out_2541048523476695545[302] = 0.0;
   out_2541048523476695545[303] = 0.0;
   out_2541048523476695545[304] = 1.0;
   out_2541048523476695545[305] = 0.0;
   out_2541048523476695545[306] = 0.0;
   out_2541048523476695545[307] = 0.0;
   out_2541048523476695545[308] = 0.0;
   out_2541048523476695545[309] = 0.0;
   out_2541048523476695545[310] = 0.0;
   out_2541048523476695545[311] = 0.0;
   out_2541048523476695545[312] = 0.0;
   out_2541048523476695545[313] = 0.0;
   out_2541048523476695545[314] = 0.0;
   out_2541048523476695545[315] = 0.0;
   out_2541048523476695545[316] = 0.0;
   out_2541048523476695545[317] = 0.0;
   out_2541048523476695545[318] = 0.0;
   out_2541048523476695545[319] = 0.0;
   out_2541048523476695545[320] = 0.0;
   out_2541048523476695545[321] = 0.0;
   out_2541048523476695545[322] = 0.0;
   out_2541048523476695545[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_3669044169232965943) {
   out_3669044169232965943[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_3669044169232965943[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_3669044169232965943[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_3669044169232965943[3] = dt*state[12] + state[3];
   out_3669044169232965943[4] = dt*state[13] + state[4];
   out_3669044169232965943[5] = dt*state[14] + state[5];
   out_3669044169232965943[6] = state[6];
   out_3669044169232965943[7] = state[7];
   out_3669044169232965943[8] = state[8];
   out_3669044169232965943[9] = state[9];
   out_3669044169232965943[10] = state[10];
   out_3669044169232965943[11] = state[11];
   out_3669044169232965943[12] = state[12];
   out_3669044169232965943[13] = state[13];
   out_3669044169232965943[14] = state[14];
   out_3669044169232965943[15] = state[15];
   out_3669044169232965943[16] = state[16];
   out_3669044169232965943[17] = state[17];
}
void F_fun(double *state, double dt, double *out_7678120840594066035) {
   out_7678120840594066035[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7678120840594066035[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7678120840594066035[2] = 0;
   out_7678120840594066035[3] = 0;
   out_7678120840594066035[4] = 0;
   out_7678120840594066035[5] = 0;
   out_7678120840594066035[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7678120840594066035[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7678120840594066035[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7678120840594066035[9] = 0;
   out_7678120840594066035[10] = 0;
   out_7678120840594066035[11] = 0;
   out_7678120840594066035[12] = 0;
   out_7678120840594066035[13] = 0;
   out_7678120840594066035[14] = 0;
   out_7678120840594066035[15] = 0;
   out_7678120840594066035[16] = 0;
   out_7678120840594066035[17] = 0;
   out_7678120840594066035[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7678120840594066035[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7678120840594066035[20] = 0;
   out_7678120840594066035[21] = 0;
   out_7678120840594066035[22] = 0;
   out_7678120840594066035[23] = 0;
   out_7678120840594066035[24] = 0;
   out_7678120840594066035[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7678120840594066035[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7678120840594066035[27] = 0;
   out_7678120840594066035[28] = 0;
   out_7678120840594066035[29] = 0;
   out_7678120840594066035[30] = 0;
   out_7678120840594066035[31] = 0;
   out_7678120840594066035[32] = 0;
   out_7678120840594066035[33] = 0;
   out_7678120840594066035[34] = 0;
   out_7678120840594066035[35] = 0;
   out_7678120840594066035[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7678120840594066035[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7678120840594066035[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7678120840594066035[39] = 0;
   out_7678120840594066035[40] = 0;
   out_7678120840594066035[41] = 0;
   out_7678120840594066035[42] = 0;
   out_7678120840594066035[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7678120840594066035[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7678120840594066035[45] = 0;
   out_7678120840594066035[46] = 0;
   out_7678120840594066035[47] = 0;
   out_7678120840594066035[48] = 0;
   out_7678120840594066035[49] = 0;
   out_7678120840594066035[50] = 0;
   out_7678120840594066035[51] = 0;
   out_7678120840594066035[52] = 0;
   out_7678120840594066035[53] = 0;
   out_7678120840594066035[54] = 0;
   out_7678120840594066035[55] = 0;
   out_7678120840594066035[56] = 0;
   out_7678120840594066035[57] = 1;
   out_7678120840594066035[58] = 0;
   out_7678120840594066035[59] = 0;
   out_7678120840594066035[60] = 0;
   out_7678120840594066035[61] = 0;
   out_7678120840594066035[62] = 0;
   out_7678120840594066035[63] = 0;
   out_7678120840594066035[64] = 0;
   out_7678120840594066035[65] = 0;
   out_7678120840594066035[66] = dt;
   out_7678120840594066035[67] = 0;
   out_7678120840594066035[68] = 0;
   out_7678120840594066035[69] = 0;
   out_7678120840594066035[70] = 0;
   out_7678120840594066035[71] = 0;
   out_7678120840594066035[72] = 0;
   out_7678120840594066035[73] = 0;
   out_7678120840594066035[74] = 0;
   out_7678120840594066035[75] = 0;
   out_7678120840594066035[76] = 1;
   out_7678120840594066035[77] = 0;
   out_7678120840594066035[78] = 0;
   out_7678120840594066035[79] = 0;
   out_7678120840594066035[80] = 0;
   out_7678120840594066035[81] = 0;
   out_7678120840594066035[82] = 0;
   out_7678120840594066035[83] = 0;
   out_7678120840594066035[84] = 0;
   out_7678120840594066035[85] = dt;
   out_7678120840594066035[86] = 0;
   out_7678120840594066035[87] = 0;
   out_7678120840594066035[88] = 0;
   out_7678120840594066035[89] = 0;
   out_7678120840594066035[90] = 0;
   out_7678120840594066035[91] = 0;
   out_7678120840594066035[92] = 0;
   out_7678120840594066035[93] = 0;
   out_7678120840594066035[94] = 0;
   out_7678120840594066035[95] = 1;
   out_7678120840594066035[96] = 0;
   out_7678120840594066035[97] = 0;
   out_7678120840594066035[98] = 0;
   out_7678120840594066035[99] = 0;
   out_7678120840594066035[100] = 0;
   out_7678120840594066035[101] = 0;
   out_7678120840594066035[102] = 0;
   out_7678120840594066035[103] = 0;
   out_7678120840594066035[104] = dt;
   out_7678120840594066035[105] = 0;
   out_7678120840594066035[106] = 0;
   out_7678120840594066035[107] = 0;
   out_7678120840594066035[108] = 0;
   out_7678120840594066035[109] = 0;
   out_7678120840594066035[110] = 0;
   out_7678120840594066035[111] = 0;
   out_7678120840594066035[112] = 0;
   out_7678120840594066035[113] = 0;
   out_7678120840594066035[114] = 1;
   out_7678120840594066035[115] = 0;
   out_7678120840594066035[116] = 0;
   out_7678120840594066035[117] = 0;
   out_7678120840594066035[118] = 0;
   out_7678120840594066035[119] = 0;
   out_7678120840594066035[120] = 0;
   out_7678120840594066035[121] = 0;
   out_7678120840594066035[122] = 0;
   out_7678120840594066035[123] = 0;
   out_7678120840594066035[124] = 0;
   out_7678120840594066035[125] = 0;
   out_7678120840594066035[126] = 0;
   out_7678120840594066035[127] = 0;
   out_7678120840594066035[128] = 0;
   out_7678120840594066035[129] = 0;
   out_7678120840594066035[130] = 0;
   out_7678120840594066035[131] = 0;
   out_7678120840594066035[132] = 0;
   out_7678120840594066035[133] = 1;
   out_7678120840594066035[134] = 0;
   out_7678120840594066035[135] = 0;
   out_7678120840594066035[136] = 0;
   out_7678120840594066035[137] = 0;
   out_7678120840594066035[138] = 0;
   out_7678120840594066035[139] = 0;
   out_7678120840594066035[140] = 0;
   out_7678120840594066035[141] = 0;
   out_7678120840594066035[142] = 0;
   out_7678120840594066035[143] = 0;
   out_7678120840594066035[144] = 0;
   out_7678120840594066035[145] = 0;
   out_7678120840594066035[146] = 0;
   out_7678120840594066035[147] = 0;
   out_7678120840594066035[148] = 0;
   out_7678120840594066035[149] = 0;
   out_7678120840594066035[150] = 0;
   out_7678120840594066035[151] = 0;
   out_7678120840594066035[152] = 1;
   out_7678120840594066035[153] = 0;
   out_7678120840594066035[154] = 0;
   out_7678120840594066035[155] = 0;
   out_7678120840594066035[156] = 0;
   out_7678120840594066035[157] = 0;
   out_7678120840594066035[158] = 0;
   out_7678120840594066035[159] = 0;
   out_7678120840594066035[160] = 0;
   out_7678120840594066035[161] = 0;
   out_7678120840594066035[162] = 0;
   out_7678120840594066035[163] = 0;
   out_7678120840594066035[164] = 0;
   out_7678120840594066035[165] = 0;
   out_7678120840594066035[166] = 0;
   out_7678120840594066035[167] = 0;
   out_7678120840594066035[168] = 0;
   out_7678120840594066035[169] = 0;
   out_7678120840594066035[170] = 0;
   out_7678120840594066035[171] = 1;
   out_7678120840594066035[172] = 0;
   out_7678120840594066035[173] = 0;
   out_7678120840594066035[174] = 0;
   out_7678120840594066035[175] = 0;
   out_7678120840594066035[176] = 0;
   out_7678120840594066035[177] = 0;
   out_7678120840594066035[178] = 0;
   out_7678120840594066035[179] = 0;
   out_7678120840594066035[180] = 0;
   out_7678120840594066035[181] = 0;
   out_7678120840594066035[182] = 0;
   out_7678120840594066035[183] = 0;
   out_7678120840594066035[184] = 0;
   out_7678120840594066035[185] = 0;
   out_7678120840594066035[186] = 0;
   out_7678120840594066035[187] = 0;
   out_7678120840594066035[188] = 0;
   out_7678120840594066035[189] = 0;
   out_7678120840594066035[190] = 1;
   out_7678120840594066035[191] = 0;
   out_7678120840594066035[192] = 0;
   out_7678120840594066035[193] = 0;
   out_7678120840594066035[194] = 0;
   out_7678120840594066035[195] = 0;
   out_7678120840594066035[196] = 0;
   out_7678120840594066035[197] = 0;
   out_7678120840594066035[198] = 0;
   out_7678120840594066035[199] = 0;
   out_7678120840594066035[200] = 0;
   out_7678120840594066035[201] = 0;
   out_7678120840594066035[202] = 0;
   out_7678120840594066035[203] = 0;
   out_7678120840594066035[204] = 0;
   out_7678120840594066035[205] = 0;
   out_7678120840594066035[206] = 0;
   out_7678120840594066035[207] = 0;
   out_7678120840594066035[208] = 0;
   out_7678120840594066035[209] = 1;
   out_7678120840594066035[210] = 0;
   out_7678120840594066035[211] = 0;
   out_7678120840594066035[212] = 0;
   out_7678120840594066035[213] = 0;
   out_7678120840594066035[214] = 0;
   out_7678120840594066035[215] = 0;
   out_7678120840594066035[216] = 0;
   out_7678120840594066035[217] = 0;
   out_7678120840594066035[218] = 0;
   out_7678120840594066035[219] = 0;
   out_7678120840594066035[220] = 0;
   out_7678120840594066035[221] = 0;
   out_7678120840594066035[222] = 0;
   out_7678120840594066035[223] = 0;
   out_7678120840594066035[224] = 0;
   out_7678120840594066035[225] = 0;
   out_7678120840594066035[226] = 0;
   out_7678120840594066035[227] = 0;
   out_7678120840594066035[228] = 1;
   out_7678120840594066035[229] = 0;
   out_7678120840594066035[230] = 0;
   out_7678120840594066035[231] = 0;
   out_7678120840594066035[232] = 0;
   out_7678120840594066035[233] = 0;
   out_7678120840594066035[234] = 0;
   out_7678120840594066035[235] = 0;
   out_7678120840594066035[236] = 0;
   out_7678120840594066035[237] = 0;
   out_7678120840594066035[238] = 0;
   out_7678120840594066035[239] = 0;
   out_7678120840594066035[240] = 0;
   out_7678120840594066035[241] = 0;
   out_7678120840594066035[242] = 0;
   out_7678120840594066035[243] = 0;
   out_7678120840594066035[244] = 0;
   out_7678120840594066035[245] = 0;
   out_7678120840594066035[246] = 0;
   out_7678120840594066035[247] = 1;
   out_7678120840594066035[248] = 0;
   out_7678120840594066035[249] = 0;
   out_7678120840594066035[250] = 0;
   out_7678120840594066035[251] = 0;
   out_7678120840594066035[252] = 0;
   out_7678120840594066035[253] = 0;
   out_7678120840594066035[254] = 0;
   out_7678120840594066035[255] = 0;
   out_7678120840594066035[256] = 0;
   out_7678120840594066035[257] = 0;
   out_7678120840594066035[258] = 0;
   out_7678120840594066035[259] = 0;
   out_7678120840594066035[260] = 0;
   out_7678120840594066035[261] = 0;
   out_7678120840594066035[262] = 0;
   out_7678120840594066035[263] = 0;
   out_7678120840594066035[264] = 0;
   out_7678120840594066035[265] = 0;
   out_7678120840594066035[266] = 1;
   out_7678120840594066035[267] = 0;
   out_7678120840594066035[268] = 0;
   out_7678120840594066035[269] = 0;
   out_7678120840594066035[270] = 0;
   out_7678120840594066035[271] = 0;
   out_7678120840594066035[272] = 0;
   out_7678120840594066035[273] = 0;
   out_7678120840594066035[274] = 0;
   out_7678120840594066035[275] = 0;
   out_7678120840594066035[276] = 0;
   out_7678120840594066035[277] = 0;
   out_7678120840594066035[278] = 0;
   out_7678120840594066035[279] = 0;
   out_7678120840594066035[280] = 0;
   out_7678120840594066035[281] = 0;
   out_7678120840594066035[282] = 0;
   out_7678120840594066035[283] = 0;
   out_7678120840594066035[284] = 0;
   out_7678120840594066035[285] = 1;
   out_7678120840594066035[286] = 0;
   out_7678120840594066035[287] = 0;
   out_7678120840594066035[288] = 0;
   out_7678120840594066035[289] = 0;
   out_7678120840594066035[290] = 0;
   out_7678120840594066035[291] = 0;
   out_7678120840594066035[292] = 0;
   out_7678120840594066035[293] = 0;
   out_7678120840594066035[294] = 0;
   out_7678120840594066035[295] = 0;
   out_7678120840594066035[296] = 0;
   out_7678120840594066035[297] = 0;
   out_7678120840594066035[298] = 0;
   out_7678120840594066035[299] = 0;
   out_7678120840594066035[300] = 0;
   out_7678120840594066035[301] = 0;
   out_7678120840594066035[302] = 0;
   out_7678120840594066035[303] = 0;
   out_7678120840594066035[304] = 1;
   out_7678120840594066035[305] = 0;
   out_7678120840594066035[306] = 0;
   out_7678120840594066035[307] = 0;
   out_7678120840594066035[308] = 0;
   out_7678120840594066035[309] = 0;
   out_7678120840594066035[310] = 0;
   out_7678120840594066035[311] = 0;
   out_7678120840594066035[312] = 0;
   out_7678120840594066035[313] = 0;
   out_7678120840594066035[314] = 0;
   out_7678120840594066035[315] = 0;
   out_7678120840594066035[316] = 0;
   out_7678120840594066035[317] = 0;
   out_7678120840594066035[318] = 0;
   out_7678120840594066035[319] = 0;
   out_7678120840594066035[320] = 0;
   out_7678120840594066035[321] = 0;
   out_7678120840594066035[322] = 0;
   out_7678120840594066035[323] = 1;
}
void h_4(double *state, double *unused, double *out_6972566205893694525) {
   out_6972566205893694525[0] = state[6] + state[9];
   out_6972566205893694525[1] = state[7] + state[10];
   out_6972566205893694525[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_6403313142581125797) {
   out_6403313142581125797[0] = 0;
   out_6403313142581125797[1] = 0;
   out_6403313142581125797[2] = 0;
   out_6403313142581125797[3] = 0;
   out_6403313142581125797[4] = 0;
   out_6403313142581125797[5] = 0;
   out_6403313142581125797[6] = 1;
   out_6403313142581125797[7] = 0;
   out_6403313142581125797[8] = 0;
   out_6403313142581125797[9] = 1;
   out_6403313142581125797[10] = 0;
   out_6403313142581125797[11] = 0;
   out_6403313142581125797[12] = 0;
   out_6403313142581125797[13] = 0;
   out_6403313142581125797[14] = 0;
   out_6403313142581125797[15] = 0;
   out_6403313142581125797[16] = 0;
   out_6403313142581125797[17] = 0;
   out_6403313142581125797[18] = 0;
   out_6403313142581125797[19] = 0;
   out_6403313142581125797[20] = 0;
   out_6403313142581125797[21] = 0;
   out_6403313142581125797[22] = 0;
   out_6403313142581125797[23] = 0;
   out_6403313142581125797[24] = 0;
   out_6403313142581125797[25] = 1;
   out_6403313142581125797[26] = 0;
   out_6403313142581125797[27] = 0;
   out_6403313142581125797[28] = 1;
   out_6403313142581125797[29] = 0;
   out_6403313142581125797[30] = 0;
   out_6403313142581125797[31] = 0;
   out_6403313142581125797[32] = 0;
   out_6403313142581125797[33] = 0;
   out_6403313142581125797[34] = 0;
   out_6403313142581125797[35] = 0;
   out_6403313142581125797[36] = 0;
   out_6403313142581125797[37] = 0;
   out_6403313142581125797[38] = 0;
   out_6403313142581125797[39] = 0;
   out_6403313142581125797[40] = 0;
   out_6403313142581125797[41] = 0;
   out_6403313142581125797[42] = 0;
   out_6403313142581125797[43] = 0;
   out_6403313142581125797[44] = 1;
   out_6403313142581125797[45] = 0;
   out_6403313142581125797[46] = 0;
   out_6403313142581125797[47] = 1;
   out_6403313142581125797[48] = 0;
   out_6403313142581125797[49] = 0;
   out_6403313142581125797[50] = 0;
   out_6403313142581125797[51] = 0;
   out_6403313142581125797[52] = 0;
   out_6403313142581125797[53] = 0;
}
void h_10(double *state, double *unused, double *out_932110130621909408) {
   out_932110130621909408[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_932110130621909408[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_932110130621909408[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_3725761758741894007) {
   out_3725761758741894007[0] = 0;
   out_3725761758741894007[1] = 9.8100000000000005*cos(state[1]);
   out_3725761758741894007[2] = 0;
   out_3725761758741894007[3] = 0;
   out_3725761758741894007[4] = -state[8];
   out_3725761758741894007[5] = state[7];
   out_3725761758741894007[6] = 0;
   out_3725761758741894007[7] = state[5];
   out_3725761758741894007[8] = -state[4];
   out_3725761758741894007[9] = 0;
   out_3725761758741894007[10] = 0;
   out_3725761758741894007[11] = 0;
   out_3725761758741894007[12] = 1;
   out_3725761758741894007[13] = 0;
   out_3725761758741894007[14] = 0;
   out_3725761758741894007[15] = 1;
   out_3725761758741894007[16] = 0;
   out_3725761758741894007[17] = 0;
   out_3725761758741894007[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_3725761758741894007[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_3725761758741894007[20] = 0;
   out_3725761758741894007[21] = state[8];
   out_3725761758741894007[22] = 0;
   out_3725761758741894007[23] = -state[6];
   out_3725761758741894007[24] = -state[5];
   out_3725761758741894007[25] = 0;
   out_3725761758741894007[26] = state[3];
   out_3725761758741894007[27] = 0;
   out_3725761758741894007[28] = 0;
   out_3725761758741894007[29] = 0;
   out_3725761758741894007[30] = 0;
   out_3725761758741894007[31] = 1;
   out_3725761758741894007[32] = 0;
   out_3725761758741894007[33] = 0;
   out_3725761758741894007[34] = 1;
   out_3725761758741894007[35] = 0;
   out_3725761758741894007[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_3725761758741894007[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_3725761758741894007[38] = 0;
   out_3725761758741894007[39] = -state[7];
   out_3725761758741894007[40] = state[6];
   out_3725761758741894007[41] = 0;
   out_3725761758741894007[42] = state[4];
   out_3725761758741894007[43] = -state[3];
   out_3725761758741894007[44] = 0;
   out_3725761758741894007[45] = 0;
   out_3725761758741894007[46] = 0;
   out_3725761758741894007[47] = 0;
   out_3725761758741894007[48] = 0;
   out_3725761758741894007[49] = 0;
   out_3725761758741894007[50] = 1;
   out_3725761758741894007[51] = 0;
   out_3725761758741894007[52] = 0;
   out_3725761758741894007[53] = 1;
}
void h_13(double *state, double *unused, double *out_2777222270862285990) {
   out_2777222270862285990[0] = state[3];
   out_2777222270862285990[1] = state[4];
   out_2777222270862285990[2] = state[5];
}
void H_13(double *state, double *unused, double *out_3191039317248792996) {
   out_3191039317248792996[0] = 0;
   out_3191039317248792996[1] = 0;
   out_3191039317248792996[2] = 0;
   out_3191039317248792996[3] = 1;
   out_3191039317248792996[4] = 0;
   out_3191039317248792996[5] = 0;
   out_3191039317248792996[6] = 0;
   out_3191039317248792996[7] = 0;
   out_3191039317248792996[8] = 0;
   out_3191039317248792996[9] = 0;
   out_3191039317248792996[10] = 0;
   out_3191039317248792996[11] = 0;
   out_3191039317248792996[12] = 0;
   out_3191039317248792996[13] = 0;
   out_3191039317248792996[14] = 0;
   out_3191039317248792996[15] = 0;
   out_3191039317248792996[16] = 0;
   out_3191039317248792996[17] = 0;
   out_3191039317248792996[18] = 0;
   out_3191039317248792996[19] = 0;
   out_3191039317248792996[20] = 0;
   out_3191039317248792996[21] = 0;
   out_3191039317248792996[22] = 1;
   out_3191039317248792996[23] = 0;
   out_3191039317248792996[24] = 0;
   out_3191039317248792996[25] = 0;
   out_3191039317248792996[26] = 0;
   out_3191039317248792996[27] = 0;
   out_3191039317248792996[28] = 0;
   out_3191039317248792996[29] = 0;
   out_3191039317248792996[30] = 0;
   out_3191039317248792996[31] = 0;
   out_3191039317248792996[32] = 0;
   out_3191039317248792996[33] = 0;
   out_3191039317248792996[34] = 0;
   out_3191039317248792996[35] = 0;
   out_3191039317248792996[36] = 0;
   out_3191039317248792996[37] = 0;
   out_3191039317248792996[38] = 0;
   out_3191039317248792996[39] = 0;
   out_3191039317248792996[40] = 0;
   out_3191039317248792996[41] = 1;
   out_3191039317248792996[42] = 0;
   out_3191039317248792996[43] = 0;
   out_3191039317248792996[44] = 0;
   out_3191039317248792996[45] = 0;
   out_3191039317248792996[46] = 0;
   out_3191039317248792996[47] = 0;
   out_3191039317248792996[48] = 0;
   out_3191039317248792996[49] = 0;
   out_3191039317248792996[50] = 0;
   out_3191039317248792996[51] = 0;
   out_3191039317248792996[52] = 0;
   out_3191039317248792996[53] = 0;
}
void h_14(double *state, double *unused, double *out_4613594682857435522) {
   out_4613594682857435522[0] = state[6];
   out_4613594682857435522[1] = state[7];
   out_4613594682857435522[2] = state[8];
}
void H_14(double *state, double *unused, double *out_2440072286241641268) {
   out_2440072286241641268[0] = 0;
   out_2440072286241641268[1] = 0;
   out_2440072286241641268[2] = 0;
   out_2440072286241641268[3] = 0;
   out_2440072286241641268[4] = 0;
   out_2440072286241641268[5] = 0;
   out_2440072286241641268[6] = 1;
   out_2440072286241641268[7] = 0;
   out_2440072286241641268[8] = 0;
   out_2440072286241641268[9] = 0;
   out_2440072286241641268[10] = 0;
   out_2440072286241641268[11] = 0;
   out_2440072286241641268[12] = 0;
   out_2440072286241641268[13] = 0;
   out_2440072286241641268[14] = 0;
   out_2440072286241641268[15] = 0;
   out_2440072286241641268[16] = 0;
   out_2440072286241641268[17] = 0;
   out_2440072286241641268[18] = 0;
   out_2440072286241641268[19] = 0;
   out_2440072286241641268[20] = 0;
   out_2440072286241641268[21] = 0;
   out_2440072286241641268[22] = 0;
   out_2440072286241641268[23] = 0;
   out_2440072286241641268[24] = 0;
   out_2440072286241641268[25] = 1;
   out_2440072286241641268[26] = 0;
   out_2440072286241641268[27] = 0;
   out_2440072286241641268[28] = 0;
   out_2440072286241641268[29] = 0;
   out_2440072286241641268[30] = 0;
   out_2440072286241641268[31] = 0;
   out_2440072286241641268[32] = 0;
   out_2440072286241641268[33] = 0;
   out_2440072286241641268[34] = 0;
   out_2440072286241641268[35] = 0;
   out_2440072286241641268[36] = 0;
   out_2440072286241641268[37] = 0;
   out_2440072286241641268[38] = 0;
   out_2440072286241641268[39] = 0;
   out_2440072286241641268[40] = 0;
   out_2440072286241641268[41] = 0;
   out_2440072286241641268[42] = 0;
   out_2440072286241641268[43] = 0;
   out_2440072286241641268[44] = 1;
   out_2440072286241641268[45] = 0;
   out_2440072286241641268[46] = 0;
   out_2440072286241641268[47] = 0;
   out_2440072286241641268[48] = 0;
   out_2440072286241641268[49] = 0;
   out_2440072286241641268[50] = 0;
   out_2440072286241641268[51] = 0;
   out_2440072286241641268[52] = 0;
   out_2440072286241641268[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_7254010466112148474) {
  err_fun(nom_x, delta_x, out_7254010466112148474);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_7571376916876272361) {
  inv_err_fun(nom_x, true_x, out_7571376916876272361);
}
void pose_H_mod_fun(double *state, double *out_2541048523476695545) {
  H_mod_fun(state, out_2541048523476695545);
}
void pose_f_fun(double *state, double dt, double *out_3669044169232965943) {
  f_fun(state,  dt, out_3669044169232965943);
}
void pose_F_fun(double *state, double dt, double *out_7678120840594066035) {
  F_fun(state,  dt, out_7678120840594066035);
}
void pose_h_4(double *state, double *unused, double *out_6972566205893694525) {
  h_4(state, unused, out_6972566205893694525);
}
void pose_H_4(double *state, double *unused, double *out_6403313142581125797) {
  H_4(state, unused, out_6403313142581125797);
}
void pose_h_10(double *state, double *unused, double *out_932110130621909408) {
  h_10(state, unused, out_932110130621909408);
}
void pose_H_10(double *state, double *unused, double *out_3725761758741894007) {
  H_10(state, unused, out_3725761758741894007);
}
void pose_h_13(double *state, double *unused, double *out_2777222270862285990) {
  h_13(state, unused, out_2777222270862285990);
}
void pose_H_13(double *state, double *unused, double *out_3191039317248792996) {
  H_13(state, unused, out_3191039317248792996);
}
void pose_h_14(double *state, double *unused, double *out_4613594682857435522) {
  h_14(state, unused, out_4613594682857435522);
}
void pose_H_14(double *state, double *unused, double *out_2440072286241641268) {
  H_14(state, unused, out_2440072286241641268);
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
