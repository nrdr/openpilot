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
void err_fun(double *nom_x, double *delta_x, double *out_7709211145934123991) {
   out_7709211145934123991[0] = delta_x[0] + nom_x[0];
   out_7709211145934123991[1] = delta_x[1] + nom_x[1];
   out_7709211145934123991[2] = delta_x[2] + nom_x[2];
   out_7709211145934123991[3] = delta_x[3] + nom_x[3];
   out_7709211145934123991[4] = delta_x[4] + nom_x[4];
   out_7709211145934123991[5] = delta_x[5] + nom_x[5];
   out_7709211145934123991[6] = delta_x[6] + nom_x[6];
   out_7709211145934123991[7] = delta_x[7] + nom_x[7];
   out_7709211145934123991[8] = delta_x[8] + nom_x[8];
   out_7709211145934123991[9] = delta_x[9] + nom_x[9];
   out_7709211145934123991[10] = delta_x[10] + nom_x[10];
   out_7709211145934123991[11] = delta_x[11] + nom_x[11];
   out_7709211145934123991[12] = delta_x[12] + nom_x[12];
   out_7709211145934123991[13] = delta_x[13] + nom_x[13];
   out_7709211145934123991[14] = delta_x[14] + nom_x[14];
   out_7709211145934123991[15] = delta_x[15] + nom_x[15];
   out_7709211145934123991[16] = delta_x[16] + nom_x[16];
   out_7709211145934123991[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_3942366649005103634) {
   out_3942366649005103634[0] = -nom_x[0] + true_x[0];
   out_3942366649005103634[1] = -nom_x[1] + true_x[1];
   out_3942366649005103634[2] = -nom_x[2] + true_x[2];
   out_3942366649005103634[3] = -nom_x[3] + true_x[3];
   out_3942366649005103634[4] = -nom_x[4] + true_x[4];
   out_3942366649005103634[5] = -nom_x[5] + true_x[5];
   out_3942366649005103634[6] = -nom_x[6] + true_x[6];
   out_3942366649005103634[7] = -nom_x[7] + true_x[7];
   out_3942366649005103634[8] = -nom_x[8] + true_x[8];
   out_3942366649005103634[9] = -nom_x[9] + true_x[9];
   out_3942366649005103634[10] = -nom_x[10] + true_x[10];
   out_3942366649005103634[11] = -nom_x[11] + true_x[11];
   out_3942366649005103634[12] = -nom_x[12] + true_x[12];
   out_3942366649005103634[13] = -nom_x[13] + true_x[13];
   out_3942366649005103634[14] = -nom_x[14] + true_x[14];
   out_3942366649005103634[15] = -nom_x[15] + true_x[15];
   out_3942366649005103634[16] = -nom_x[16] + true_x[16];
   out_3942366649005103634[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_7024720103031486995) {
   out_7024720103031486995[0] = 1.0;
   out_7024720103031486995[1] = 0.0;
   out_7024720103031486995[2] = 0.0;
   out_7024720103031486995[3] = 0.0;
   out_7024720103031486995[4] = 0.0;
   out_7024720103031486995[5] = 0.0;
   out_7024720103031486995[6] = 0.0;
   out_7024720103031486995[7] = 0.0;
   out_7024720103031486995[8] = 0.0;
   out_7024720103031486995[9] = 0.0;
   out_7024720103031486995[10] = 0.0;
   out_7024720103031486995[11] = 0.0;
   out_7024720103031486995[12] = 0.0;
   out_7024720103031486995[13] = 0.0;
   out_7024720103031486995[14] = 0.0;
   out_7024720103031486995[15] = 0.0;
   out_7024720103031486995[16] = 0.0;
   out_7024720103031486995[17] = 0.0;
   out_7024720103031486995[18] = 0.0;
   out_7024720103031486995[19] = 1.0;
   out_7024720103031486995[20] = 0.0;
   out_7024720103031486995[21] = 0.0;
   out_7024720103031486995[22] = 0.0;
   out_7024720103031486995[23] = 0.0;
   out_7024720103031486995[24] = 0.0;
   out_7024720103031486995[25] = 0.0;
   out_7024720103031486995[26] = 0.0;
   out_7024720103031486995[27] = 0.0;
   out_7024720103031486995[28] = 0.0;
   out_7024720103031486995[29] = 0.0;
   out_7024720103031486995[30] = 0.0;
   out_7024720103031486995[31] = 0.0;
   out_7024720103031486995[32] = 0.0;
   out_7024720103031486995[33] = 0.0;
   out_7024720103031486995[34] = 0.0;
   out_7024720103031486995[35] = 0.0;
   out_7024720103031486995[36] = 0.0;
   out_7024720103031486995[37] = 0.0;
   out_7024720103031486995[38] = 1.0;
   out_7024720103031486995[39] = 0.0;
   out_7024720103031486995[40] = 0.0;
   out_7024720103031486995[41] = 0.0;
   out_7024720103031486995[42] = 0.0;
   out_7024720103031486995[43] = 0.0;
   out_7024720103031486995[44] = 0.0;
   out_7024720103031486995[45] = 0.0;
   out_7024720103031486995[46] = 0.0;
   out_7024720103031486995[47] = 0.0;
   out_7024720103031486995[48] = 0.0;
   out_7024720103031486995[49] = 0.0;
   out_7024720103031486995[50] = 0.0;
   out_7024720103031486995[51] = 0.0;
   out_7024720103031486995[52] = 0.0;
   out_7024720103031486995[53] = 0.0;
   out_7024720103031486995[54] = 0.0;
   out_7024720103031486995[55] = 0.0;
   out_7024720103031486995[56] = 0.0;
   out_7024720103031486995[57] = 1.0;
   out_7024720103031486995[58] = 0.0;
   out_7024720103031486995[59] = 0.0;
   out_7024720103031486995[60] = 0.0;
   out_7024720103031486995[61] = 0.0;
   out_7024720103031486995[62] = 0.0;
   out_7024720103031486995[63] = 0.0;
   out_7024720103031486995[64] = 0.0;
   out_7024720103031486995[65] = 0.0;
   out_7024720103031486995[66] = 0.0;
   out_7024720103031486995[67] = 0.0;
   out_7024720103031486995[68] = 0.0;
   out_7024720103031486995[69] = 0.0;
   out_7024720103031486995[70] = 0.0;
   out_7024720103031486995[71] = 0.0;
   out_7024720103031486995[72] = 0.0;
   out_7024720103031486995[73] = 0.0;
   out_7024720103031486995[74] = 0.0;
   out_7024720103031486995[75] = 0.0;
   out_7024720103031486995[76] = 1.0;
   out_7024720103031486995[77] = 0.0;
   out_7024720103031486995[78] = 0.0;
   out_7024720103031486995[79] = 0.0;
   out_7024720103031486995[80] = 0.0;
   out_7024720103031486995[81] = 0.0;
   out_7024720103031486995[82] = 0.0;
   out_7024720103031486995[83] = 0.0;
   out_7024720103031486995[84] = 0.0;
   out_7024720103031486995[85] = 0.0;
   out_7024720103031486995[86] = 0.0;
   out_7024720103031486995[87] = 0.0;
   out_7024720103031486995[88] = 0.0;
   out_7024720103031486995[89] = 0.0;
   out_7024720103031486995[90] = 0.0;
   out_7024720103031486995[91] = 0.0;
   out_7024720103031486995[92] = 0.0;
   out_7024720103031486995[93] = 0.0;
   out_7024720103031486995[94] = 0.0;
   out_7024720103031486995[95] = 1.0;
   out_7024720103031486995[96] = 0.0;
   out_7024720103031486995[97] = 0.0;
   out_7024720103031486995[98] = 0.0;
   out_7024720103031486995[99] = 0.0;
   out_7024720103031486995[100] = 0.0;
   out_7024720103031486995[101] = 0.0;
   out_7024720103031486995[102] = 0.0;
   out_7024720103031486995[103] = 0.0;
   out_7024720103031486995[104] = 0.0;
   out_7024720103031486995[105] = 0.0;
   out_7024720103031486995[106] = 0.0;
   out_7024720103031486995[107] = 0.0;
   out_7024720103031486995[108] = 0.0;
   out_7024720103031486995[109] = 0.0;
   out_7024720103031486995[110] = 0.0;
   out_7024720103031486995[111] = 0.0;
   out_7024720103031486995[112] = 0.0;
   out_7024720103031486995[113] = 0.0;
   out_7024720103031486995[114] = 1.0;
   out_7024720103031486995[115] = 0.0;
   out_7024720103031486995[116] = 0.0;
   out_7024720103031486995[117] = 0.0;
   out_7024720103031486995[118] = 0.0;
   out_7024720103031486995[119] = 0.0;
   out_7024720103031486995[120] = 0.0;
   out_7024720103031486995[121] = 0.0;
   out_7024720103031486995[122] = 0.0;
   out_7024720103031486995[123] = 0.0;
   out_7024720103031486995[124] = 0.0;
   out_7024720103031486995[125] = 0.0;
   out_7024720103031486995[126] = 0.0;
   out_7024720103031486995[127] = 0.0;
   out_7024720103031486995[128] = 0.0;
   out_7024720103031486995[129] = 0.0;
   out_7024720103031486995[130] = 0.0;
   out_7024720103031486995[131] = 0.0;
   out_7024720103031486995[132] = 0.0;
   out_7024720103031486995[133] = 1.0;
   out_7024720103031486995[134] = 0.0;
   out_7024720103031486995[135] = 0.0;
   out_7024720103031486995[136] = 0.0;
   out_7024720103031486995[137] = 0.0;
   out_7024720103031486995[138] = 0.0;
   out_7024720103031486995[139] = 0.0;
   out_7024720103031486995[140] = 0.0;
   out_7024720103031486995[141] = 0.0;
   out_7024720103031486995[142] = 0.0;
   out_7024720103031486995[143] = 0.0;
   out_7024720103031486995[144] = 0.0;
   out_7024720103031486995[145] = 0.0;
   out_7024720103031486995[146] = 0.0;
   out_7024720103031486995[147] = 0.0;
   out_7024720103031486995[148] = 0.0;
   out_7024720103031486995[149] = 0.0;
   out_7024720103031486995[150] = 0.0;
   out_7024720103031486995[151] = 0.0;
   out_7024720103031486995[152] = 1.0;
   out_7024720103031486995[153] = 0.0;
   out_7024720103031486995[154] = 0.0;
   out_7024720103031486995[155] = 0.0;
   out_7024720103031486995[156] = 0.0;
   out_7024720103031486995[157] = 0.0;
   out_7024720103031486995[158] = 0.0;
   out_7024720103031486995[159] = 0.0;
   out_7024720103031486995[160] = 0.0;
   out_7024720103031486995[161] = 0.0;
   out_7024720103031486995[162] = 0.0;
   out_7024720103031486995[163] = 0.0;
   out_7024720103031486995[164] = 0.0;
   out_7024720103031486995[165] = 0.0;
   out_7024720103031486995[166] = 0.0;
   out_7024720103031486995[167] = 0.0;
   out_7024720103031486995[168] = 0.0;
   out_7024720103031486995[169] = 0.0;
   out_7024720103031486995[170] = 0.0;
   out_7024720103031486995[171] = 1.0;
   out_7024720103031486995[172] = 0.0;
   out_7024720103031486995[173] = 0.0;
   out_7024720103031486995[174] = 0.0;
   out_7024720103031486995[175] = 0.0;
   out_7024720103031486995[176] = 0.0;
   out_7024720103031486995[177] = 0.0;
   out_7024720103031486995[178] = 0.0;
   out_7024720103031486995[179] = 0.0;
   out_7024720103031486995[180] = 0.0;
   out_7024720103031486995[181] = 0.0;
   out_7024720103031486995[182] = 0.0;
   out_7024720103031486995[183] = 0.0;
   out_7024720103031486995[184] = 0.0;
   out_7024720103031486995[185] = 0.0;
   out_7024720103031486995[186] = 0.0;
   out_7024720103031486995[187] = 0.0;
   out_7024720103031486995[188] = 0.0;
   out_7024720103031486995[189] = 0.0;
   out_7024720103031486995[190] = 1.0;
   out_7024720103031486995[191] = 0.0;
   out_7024720103031486995[192] = 0.0;
   out_7024720103031486995[193] = 0.0;
   out_7024720103031486995[194] = 0.0;
   out_7024720103031486995[195] = 0.0;
   out_7024720103031486995[196] = 0.0;
   out_7024720103031486995[197] = 0.0;
   out_7024720103031486995[198] = 0.0;
   out_7024720103031486995[199] = 0.0;
   out_7024720103031486995[200] = 0.0;
   out_7024720103031486995[201] = 0.0;
   out_7024720103031486995[202] = 0.0;
   out_7024720103031486995[203] = 0.0;
   out_7024720103031486995[204] = 0.0;
   out_7024720103031486995[205] = 0.0;
   out_7024720103031486995[206] = 0.0;
   out_7024720103031486995[207] = 0.0;
   out_7024720103031486995[208] = 0.0;
   out_7024720103031486995[209] = 1.0;
   out_7024720103031486995[210] = 0.0;
   out_7024720103031486995[211] = 0.0;
   out_7024720103031486995[212] = 0.0;
   out_7024720103031486995[213] = 0.0;
   out_7024720103031486995[214] = 0.0;
   out_7024720103031486995[215] = 0.0;
   out_7024720103031486995[216] = 0.0;
   out_7024720103031486995[217] = 0.0;
   out_7024720103031486995[218] = 0.0;
   out_7024720103031486995[219] = 0.0;
   out_7024720103031486995[220] = 0.0;
   out_7024720103031486995[221] = 0.0;
   out_7024720103031486995[222] = 0.0;
   out_7024720103031486995[223] = 0.0;
   out_7024720103031486995[224] = 0.0;
   out_7024720103031486995[225] = 0.0;
   out_7024720103031486995[226] = 0.0;
   out_7024720103031486995[227] = 0.0;
   out_7024720103031486995[228] = 1.0;
   out_7024720103031486995[229] = 0.0;
   out_7024720103031486995[230] = 0.0;
   out_7024720103031486995[231] = 0.0;
   out_7024720103031486995[232] = 0.0;
   out_7024720103031486995[233] = 0.0;
   out_7024720103031486995[234] = 0.0;
   out_7024720103031486995[235] = 0.0;
   out_7024720103031486995[236] = 0.0;
   out_7024720103031486995[237] = 0.0;
   out_7024720103031486995[238] = 0.0;
   out_7024720103031486995[239] = 0.0;
   out_7024720103031486995[240] = 0.0;
   out_7024720103031486995[241] = 0.0;
   out_7024720103031486995[242] = 0.0;
   out_7024720103031486995[243] = 0.0;
   out_7024720103031486995[244] = 0.0;
   out_7024720103031486995[245] = 0.0;
   out_7024720103031486995[246] = 0.0;
   out_7024720103031486995[247] = 1.0;
   out_7024720103031486995[248] = 0.0;
   out_7024720103031486995[249] = 0.0;
   out_7024720103031486995[250] = 0.0;
   out_7024720103031486995[251] = 0.0;
   out_7024720103031486995[252] = 0.0;
   out_7024720103031486995[253] = 0.0;
   out_7024720103031486995[254] = 0.0;
   out_7024720103031486995[255] = 0.0;
   out_7024720103031486995[256] = 0.0;
   out_7024720103031486995[257] = 0.0;
   out_7024720103031486995[258] = 0.0;
   out_7024720103031486995[259] = 0.0;
   out_7024720103031486995[260] = 0.0;
   out_7024720103031486995[261] = 0.0;
   out_7024720103031486995[262] = 0.0;
   out_7024720103031486995[263] = 0.0;
   out_7024720103031486995[264] = 0.0;
   out_7024720103031486995[265] = 0.0;
   out_7024720103031486995[266] = 1.0;
   out_7024720103031486995[267] = 0.0;
   out_7024720103031486995[268] = 0.0;
   out_7024720103031486995[269] = 0.0;
   out_7024720103031486995[270] = 0.0;
   out_7024720103031486995[271] = 0.0;
   out_7024720103031486995[272] = 0.0;
   out_7024720103031486995[273] = 0.0;
   out_7024720103031486995[274] = 0.0;
   out_7024720103031486995[275] = 0.0;
   out_7024720103031486995[276] = 0.0;
   out_7024720103031486995[277] = 0.0;
   out_7024720103031486995[278] = 0.0;
   out_7024720103031486995[279] = 0.0;
   out_7024720103031486995[280] = 0.0;
   out_7024720103031486995[281] = 0.0;
   out_7024720103031486995[282] = 0.0;
   out_7024720103031486995[283] = 0.0;
   out_7024720103031486995[284] = 0.0;
   out_7024720103031486995[285] = 1.0;
   out_7024720103031486995[286] = 0.0;
   out_7024720103031486995[287] = 0.0;
   out_7024720103031486995[288] = 0.0;
   out_7024720103031486995[289] = 0.0;
   out_7024720103031486995[290] = 0.0;
   out_7024720103031486995[291] = 0.0;
   out_7024720103031486995[292] = 0.0;
   out_7024720103031486995[293] = 0.0;
   out_7024720103031486995[294] = 0.0;
   out_7024720103031486995[295] = 0.0;
   out_7024720103031486995[296] = 0.0;
   out_7024720103031486995[297] = 0.0;
   out_7024720103031486995[298] = 0.0;
   out_7024720103031486995[299] = 0.0;
   out_7024720103031486995[300] = 0.0;
   out_7024720103031486995[301] = 0.0;
   out_7024720103031486995[302] = 0.0;
   out_7024720103031486995[303] = 0.0;
   out_7024720103031486995[304] = 1.0;
   out_7024720103031486995[305] = 0.0;
   out_7024720103031486995[306] = 0.0;
   out_7024720103031486995[307] = 0.0;
   out_7024720103031486995[308] = 0.0;
   out_7024720103031486995[309] = 0.0;
   out_7024720103031486995[310] = 0.0;
   out_7024720103031486995[311] = 0.0;
   out_7024720103031486995[312] = 0.0;
   out_7024720103031486995[313] = 0.0;
   out_7024720103031486995[314] = 0.0;
   out_7024720103031486995[315] = 0.0;
   out_7024720103031486995[316] = 0.0;
   out_7024720103031486995[317] = 0.0;
   out_7024720103031486995[318] = 0.0;
   out_7024720103031486995[319] = 0.0;
   out_7024720103031486995[320] = 0.0;
   out_7024720103031486995[321] = 0.0;
   out_7024720103031486995[322] = 0.0;
   out_7024720103031486995[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_8735071172480870357) {
   out_8735071172480870357[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_8735071172480870357[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_8735071172480870357[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_8735071172480870357[3] = dt*state[12] + state[3];
   out_8735071172480870357[4] = dt*state[13] + state[4];
   out_8735071172480870357[5] = dt*state[14] + state[5];
   out_8735071172480870357[6] = state[6];
   out_8735071172480870357[7] = state[7];
   out_8735071172480870357[8] = state[8];
   out_8735071172480870357[9] = state[9];
   out_8735071172480870357[10] = state[10];
   out_8735071172480870357[11] = state[11];
   out_8735071172480870357[12] = state[12];
   out_8735071172480870357[13] = state[13];
   out_8735071172480870357[14] = state[14];
   out_8735071172480870357[15] = state[15];
   out_8735071172480870357[16] = state[16];
   out_8735071172480870357[17] = state[17];
}
void F_fun(double *state, double dt, double *out_823961402091764503) {
   out_823961402091764503[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_823961402091764503[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_823961402091764503[2] = 0;
   out_823961402091764503[3] = 0;
   out_823961402091764503[4] = 0;
   out_823961402091764503[5] = 0;
   out_823961402091764503[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_823961402091764503[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_823961402091764503[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_823961402091764503[9] = 0;
   out_823961402091764503[10] = 0;
   out_823961402091764503[11] = 0;
   out_823961402091764503[12] = 0;
   out_823961402091764503[13] = 0;
   out_823961402091764503[14] = 0;
   out_823961402091764503[15] = 0;
   out_823961402091764503[16] = 0;
   out_823961402091764503[17] = 0;
   out_823961402091764503[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_823961402091764503[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_823961402091764503[20] = 0;
   out_823961402091764503[21] = 0;
   out_823961402091764503[22] = 0;
   out_823961402091764503[23] = 0;
   out_823961402091764503[24] = 0;
   out_823961402091764503[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_823961402091764503[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_823961402091764503[27] = 0;
   out_823961402091764503[28] = 0;
   out_823961402091764503[29] = 0;
   out_823961402091764503[30] = 0;
   out_823961402091764503[31] = 0;
   out_823961402091764503[32] = 0;
   out_823961402091764503[33] = 0;
   out_823961402091764503[34] = 0;
   out_823961402091764503[35] = 0;
   out_823961402091764503[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_823961402091764503[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_823961402091764503[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_823961402091764503[39] = 0;
   out_823961402091764503[40] = 0;
   out_823961402091764503[41] = 0;
   out_823961402091764503[42] = 0;
   out_823961402091764503[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_823961402091764503[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_823961402091764503[45] = 0;
   out_823961402091764503[46] = 0;
   out_823961402091764503[47] = 0;
   out_823961402091764503[48] = 0;
   out_823961402091764503[49] = 0;
   out_823961402091764503[50] = 0;
   out_823961402091764503[51] = 0;
   out_823961402091764503[52] = 0;
   out_823961402091764503[53] = 0;
   out_823961402091764503[54] = 0;
   out_823961402091764503[55] = 0;
   out_823961402091764503[56] = 0;
   out_823961402091764503[57] = 1;
   out_823961402091764503[58] = 0;
   out_823961402091764503[59] = 0;
   out_823961402091764503[60] = 0;
   out_823961402091764503[61] = 0;
   out_823961402091764503[62] = 0;
   out_823961402091764503[63] = 0;
   out_823961402091764503[64] = 0;
   out_823961402091764503[65] = 0;
   out_823961402091764503[66] = dt;
   out_823961402091764503[67] = 0;
   out_823961402091764503[68] = 0;
   out_823961402091764503[69] = 0;
   out_823961402091764503[70] = 0;
   out_823961402091764503[71] = 0;
   out_823961402091764503[72] = 0;
   out_823961402091764503[73] = 0;
   out_823961402091764503[74] = 0;
   out_823961402091764503[75] = 0;
   out_823961402091764503[76] = 1;
   out_823961402091764503[77] = 0;
   out_823961402091764503[78] = 0;
   out_823961402091764503[79] = 0;
   out_823961402091764503[80] = 0;
   out_823961402091764503[81] = 0;
   out_823961402091764503[82] = 0;
   out_823961402091764503[83] = 0;
   out_823961402091764503[84] = 0;
   out_823961402091764503[85] = dt;
   out_823961402091764503[86] = 0;
   out_823961402091764503[87] = 0;
   out_823961402091764503[88] = 0;
   out_823961402091764503[89] = 0;
   out_823961402091764503[90] = 0;
   out_823961402091764503[91] = 0;
   out_823961402091764503[92] = 0;
   out_823961402091764503[93] = 0;
   out_823961402091764503[94] = 0;
   out_823961402091764503[95] = 1;
   out_823961402091764503[96] = 0;
   out_823961402091764503[97] = 0;
   out_823961402091764503[98] = 0;
   out_823961402091764503[99] = 0;
   out_823961402091764503[100] = 0;
   out_823961402091764503[101] = 0;
   out_823961402091764503[102] = 0;
   out_823961402091764503[103] = 0;
   out_823961402091764503[104] = dt;
   out_823961402091764503[105] = 0;
   out_823961402091764503[106] = 0;
   out_823961402091764503[107] = 0;
   out_823961402091764503[108] = 0;
   out_823961402091764503[109] = 0;
   out_823961402091764503[110] = 0;
   out_823961402091764503[111] = 0;
   out_823961402091764503[112] = 0;
   out_823961402091764503[113] = 0;
   out_823961402091764503[114] = 1;
   out_823961402091764503[115] = 0;
   out_823961402091764503[116] = 0;
   out_823961402091764503[117] = 0;
   out_823961402091764503[118] = 0;
   out_823961402091764503[119] = 0;
   out_823961402091764503[120] = 0;
   out_823961402091764503[121] = 0;
   out_823961402091764503[122] = 0;
   out_823961402091764503[123] = 0;
   out_823961402091764503[124] = 0;
   out_823961402091764503[125] = 0;
   out_823961402091764503[126] = 0;
   out_823961402091764503[127] = 0;
   out_823961402091764503[128] = 0;
   out_823961402091764503[129] = 0;
   out_823961402091764503[130] = 0;
   out_823961402091764503[131] = 0;
   out_823961402091764503[132] = 0;
   out_823961402091764503[133] = 1;
   out_823961402091764503[134] = 0;
   out_823961402091764503[135] = 0;
   out_823961402091764503[136] = 0;
   out_823961402091764503[137] = 0;
   out_823961402091764503[138] = 0;
   out_823961402091764503[139] = 0;
   out_823961402091764503[140] = 0;
   out_823961402091764503[141] = 0;
   out_823961402091764503[142] = 0;
   out_823961402091764503[143] = 0;
   out_823961402091764503[144] = 0;
   out_823961402091764503[145] = 0;
   out_823961402091764503[146] = 0;
   out_823961402091764503[147] = 0;
   out_823961402091764503[148] = 0;
   out_823961402091764503[149] = 0;
   out_823961402091764503[150] = 0;
   out_823961402091764503[151] = 0;
   out_823961402091764503[152] = 1;
   out_823961402091764503[153] = 0;
   out_823961402091764503[154] = 0;
   out_823961402091764503[155] = 0;
   out_823961402091764503[156] = 0;
   out_823961402091764503[157] = 0;
   out_823961402091764503[158] = 0;
   out_823961402091764503[159] = 0;
   out_823961402091764503[160] = 0;
   out_823961402091764503[161] = 0;
   out_823961402091764503[162] = 0;
   out_823961402091764503[163] = 0;
   out_823961402091764503[164] = 0;
   out_823961402091764503[165] = 0;
   out_823961402091764503[166] = 0;
   out_823961402091764503[167] = 0;
   out_823961402091764503[168] = 0;
   out_823961402091764503[169] = 0;
   out_823961402091764503[170] = 0;
   out_823961402091764503[171] = 1;
   out_823961402091764503[172] = 0;
   out_823961402091764503[173] = 0;
   out_823961402091764503[174] = 0;
   out_823961402091764503[175] = 0;
   out_823961402091764503[176] = 0;
   out_823961402091764503[177] = 0;
   out_823961402091764503[178] = 0;
   out_823961402091764503[179] = 0;
   out_823961402091764503[180] = 0;
   out_823961402091764503[181] = 0;
   out_823961402091764503[182] = 0;
   out_823961402091764503[183] = 0;
   out_823961402091764503[184] = 0;
   out_823961402091764503[185] = 0;
   out_823961402091764503[186] = 0;
   out_823961402091764503[187] = 0;
   out_823961402091764503[188] = 0;
   out_823961402091764503[189] = 0;
   out_823961402091764503[190] = 1;
   out_823961402091764503[191] = 0;
   out_823961402091764503[192] = 0;
   out_823961402091764503[193] = 0;
   out_823961402091764503[194] = 0;
   out_823961402091764503[195] = 0;
   out_823961402091764503[196] = 0;
   out_823961402091764503[197] = 0;
   out_823961402091764503[198] = 0;
   out_823961402091764503[199] = 0;
   out_823961402091764503[200] = 0;
   out_823961402091764503[201] = 0;
   out_823961402091764503[202] = 0;
   out_823961402091764503[203] = 0;
   out_823961402091764503[204] = 0;
   out_823961402091764503[205] = 0;
   out_823961402091764503[206] = 0;
   out_823961402091764503[207] = 0;
   out_823961402091764503[208] = 0;
   out_823961402091764503[209] = 1;
   out_823961402091764503[210] = 0;
   out_823961402091764503[211] = 0;
   out_823961402091764503[212] = 0;
   out_823961402091764503[213] = 0;
   out_823961402091764503[214] = 0;
   out_823961402091764503[215] = 0;
   out_823961402091764503[216] = 0;
   out_823961402091764503[217] = 0;
   out_823961402091764503[218] = 0;
   out_823961402091764503[219] = 0;
   out_823961402091764503[220] = 0;
   out_823961402091764503[221] = 0;
   out_823961402091764503[222] = 0;
   out_823961402091764503[223] = 0;
   out_823961402091764503[224] = 0;
   out_823961402091764503[225] = 0;
   out_823961402091764503[226] = 0;
   out_823961402091764503[227] = 0;
   out_823961402091764503[228] = 1;
   out_823961402091764503[229] = 0;
   out_823961402091764503[230] = 0;
   out_823961402091764503[231] = 0;
   out_823961402091764503[232] = 0;
   out_823961402091764503[233] = 0;
   out_823961402091764503[234] = 0;
   out_823961402091764503[235] = 0;
   out_823961402091764503[236] = 0;
   out_823961402091764503[237] = 0;
   out_823961402091764503[238] = 0;
   out_823961402091764503[239] = 0;
   out_823961402091764503[240] = 0;
   out_823961402091764503[241] = 0;
   out_823961402091764503[242] = 0;
   out_823961402091764503[243] = 0;
   out_823961402091764503[244] = 0;
   out_823961402091764503[245] = 0;
   out_823961402091764503[246] = 0;
   out_823961402091764503[247] = 1;
   out_823961402091764503[248] = 0;
   out_823961402091764503[249] = 0;
   out_823961402091764503[250] = 0;
   out_823961402091764503[251] = 0;
   out_823961402091764503[252] = 0;
   out_823961402091764503[253] = 0;
   out_823961402091764503[254] = 0;
   out_823961402091764503[255] = 0;
   out_823961402091764503[256] = 0;
   out_823961402091764503[257] = 0;
   out_823961402091764503[258] = 0;
   out_823961402091764503[259] = 0;
   out_823961402091764503[260] = 0;
   out_823961402091764503[261] = 0;
   out_823961402091764503[262] = 0;
   out_823961402091764503[263] = 0;
   out_823961402091764503[264] = 0;
   out_823961402091764503[265] = 0;
   out_823961402091764503[266] = 1;
   out_823961402091764503[267] = 0;
   out_823961402091764503[268] = 0;
   out_823961402091764503[269] = 0;
   out_823961402091764503[270] = 0;
   out_823961402091764503[271] = 0;
   out_823961402091764503[272] = 0;
   out_823961402091764503[273] = 0;
   out_823961402091764503[274] = 0;
   out_823961402091764503[275] = 0;
   out_823961402091764503[276] = 0;
   out_823961402091764503[277] = 0;
   out_823961402091764503[278] = 0;
   out_823961402091764503[279] = 0;
   out_823961402091764503[280] = 0;
   out_823961402091764503[281] = 0;
   out_823961402091764503[282] = 0;
   out_823961402091764503[283] = 0;
   out_823961402091764503[284] = 0;
   out_823961402091764503[285] = 1;
   out_823961402091764503[286] = 0;
   out_823961402091764503[287] = 0;
   out_823961402091764503[288] = 0;
   out_823961402091764503[289] = 0;
   out_823961402091764503[290] = 0;
   out_823961402091764503[291] = 0;
   out_823961402091764503[292] = 0;
   out_823961402091764503[293] = 0;
   out_823961402091764503[294] = 0;
   out_823961402091764503[295] = 0;
   out_823961402091764503[296] = 0;
   out_823961402091764503[297] = 0;
   out_823961402091764503[298] = 0;
   out_823961402091764503[299] = 0;
   out_823961402091764503[300] = 0;
   out_823961402091764503[301] = 0;
   out_823961402091764503[302] = 0;
   out_823961402091764503[303] = 0;
   out_823961402091764503[304] = 1;
   out_823961402091764503[305] = 0;
   out_823961402091764503[306] = 0;
   out_823961402091764503[307] = 0;
   out_823961402091764503[308] = 0;
   out_823961402091764503[309] = 0;
   out_823961402091764503[310] = 0;
   out_823961402091764503[311] = 0;
   out_823961402091764503[312] = 0;
   out_823961402091764503[313] = 0;
   out_823961402091764503[314] = 0;
   out_823961402091764503[315] = 0;
   out_823961402091764503[316] = 0;
   out_823961402091764503[317] = 0;
   out_823961402091764503[318] = 0;
   out_823961402091764503[319] = 0;
   out_823961402091764503[320] = 0;
   out_823961402091764503[321] = 0;
   out_823961402091764503[322] = 0;
   out_823961402091764503[323] = 1;
}
void h_4(double *state, double *unused, double *out_5737604937341341534) {
   out_5737604937341341534[0] = state[6] + state[9];
   out_5737604937341341534[1] = state[7] + state[10];
   out_5737604937341341534[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_6269505585638983886) {
   out_6269505585638983886[0] = 0;
   out_6269505585638983886[1] = 0;
   out_6269505585638983886[2] = 0;
   out_6269505585638983886[3] = 0;
   out_6269505585638983886[4] = 0;
   out_6269505585638983886[5] = 0;
   out_6269505585638983886[6] = 1;
   out_6269505585638983886[7] = 0;
   out_6269505585638983886[8] = 0;
   out_6269505585638983886[9] = 1;
   out_6269505585638983886[10] = 0;
   out_6269505585638983886[11] = 0;
   out_6269505585638983886[12] = 0;
   out_6269505585638983886[13] = 0;
   out_6269505585638983886[14] = 0;
   out_6269505585638983886[15] = 0;
   out_6269505585638983886[16] = 0;
   out_6269505585638983886[17] = 0;
   out_6269505585638983886[18] = 0;
   out_6269505585638983886[19] = 0;
   out_6269505585638983886[20] = 0;
   out_6269505585638983886[21] = 0;
   out_6269505585638983886[22] = 0;
   out_6269505585638983886[23] = 0;
   out_6269505585638983886[24] = 0;
   out_6269505585638983886[25] = 1;
   out_6269505585638983886[26] = 0;
   out_6269505585638983886[27] = 0;
   out_6269505585638983886[28] = 1;
   out_6269505585638983886[29] = 0;
   out_6269505585638983886[30] = 0;
   out_6269505585638983886[31] = 0;
   out_6269505585638983886[32] = 0;
   out_6269505585638983886[33] = 0;
   out_6269505585638983886[34] = 0;
   out_6269505585638983886[35] = 0;
   out_6269505585638983886[36] = 0;
   out_6269505585638983886[37] = 0;
   out_6269505585638983886[38] = 0;
   out_6269505585638983886[39] = 0;
   out_6269505585638983886[40] = 0;
   out_6269505585638983886[41] = 0;
   out_6269505585638983886[42] = 0;
   out_6269505585638983886[43] = 0;
   out_6269505585638983886[44] = 1;
   out_6269505585638983886[45] = 0;
   out_6269505585638983886[46] = 0;
   out_6269505585638983886[47] = 1;
   out_6269505585638983886[48] = 0;
   out_6269505585638983886[49] = 0;
   out_6269505585638983886[50] = 0;
   out_6269505585638983886[51] = 0;
   out_6269505585638983886[52] = 0;
   out_6269505585638983886[53] = 0;
}
void h_10(double *state, double *unused, double *out_5255790841188854786) {
   out_5255790841188854786[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_5255790841188854786[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_5255790841188854786[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_4631033678897535887) {
   out_4631033678897535887[0] = 0;
   out_4631033678897535887[1] = 9.8100000000000005*cos(state[1]);
   out_4631033678897535887[2] = 0;
   out_4631033678897535887[3] = 0;
   out_4631033678897535887[4] = -state[8];
   out_4631033678897535887[5] = state[7];
   out_4631033678897535887[6] = 0;
   out_4631033678897535887[7] = state[5];
   out_4631033678897535887[8] = -state[4];
   out_4631033678897535887[9] = 0;
   out_4631033678897535887[10] = 0;
   out_4631033678897535887[11] = 0;
   out_4631033678897535887[12] = 1;
   out_4631033678897535887[13] = 0;
   out_4631033678897535887[14] = 0;
   out_4631033678897535887[15] = 1;
   out_4631033678897535887[16] = 0;
   out_4631033678897535887[17] = 0;
   out_4631033678897535887[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_4631033678897535887[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_4631033678897535887[20] = 0;
   out_4631033678897535887[21] = state[8];
   out_4631033678897535887[22] = 0;
   out_4631033678897535887[23] = -state[6];
   out_4631033678897535887[24] = -state[5];
   out_4631033678897535887[25] = 0;
   out_4631033678897535887[26] = state[3];
   out_4631033678897535887[27] = 0;
   out_4631033678897535887[28] = 0;
   out_4631033678897535887[29] = 0;
   out_4631033678897535887[30] = 0;
   out_4631033678897535887[31] = 1;
   out_4631033678897535887[32] = 0;
   out_4631033678897535887[33] = 0;
   out_4631033678897535887[34] = 1;
   out_4631033678897535887[35] = 0;
   out_4631033678897535887[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_4631033678897535887[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_4631033678897535887[38] = 0;
   out_4631033678897535887[39] = -state[7];
   out_4631033678897535887[40] = state[6];
   out_4631033678897535887[41] = 0;
   out_4631033678897535887[42] = state[4];
   out_4631033678897535887[43] = -state[3];
   out_4631033678897535887[44] = 0;
   out_4631033678897535887[45] = 0;
   out_4631033678897535887[46] = 0;
   out_4631033678897535887[47] = 0;
   out_4631033678897535887[48] = 0;
   out_4631033678897535887[49] = 0;
   out_4631033678897535887[50] = 1;
   out_4631033678897535887[51] = 0;
   out_4631033678897535887[52] = 0;
   out_4631033678897535887[53] = 1;
}
void h_13(double *state, double *unused, double *out_6690590361496767190) {
   out_6690590361496767190[0] = state[3];
   out_6690590361496767190[1] = state[4];
   out_6690590361496767190[2] = state[5];
}
void H_13(double *state, double *unused, double *out_3057231760306651085) {
   out_3057231760306651085[0] = 0;
   out_3057231760306651085[1] = 0;
   out_3057231760306651085[2] = 0;
   out_3057231760306651085[3] = 1;
   out_3057231760306651085[4] = 0;
   out_3057231760306651085[5] = 0;
   out_3057231760306651085[6] = 0;
   out_3057231760306651085[7] = 0;
   out_3057231760306651085[8] = 0;
   out_3057231760306651085[9] = 0;
   out_3057231760306651085[10] = 0;
   out_3057231760306651085[11] = 0;
   out_3057231760306651085[12] = 0;
   out_3057231760306651085[13] = 0;
   out_3057231760306651085[14] = 0;
   out_3057231760306651085[15] = 0;
   out_3057231760306651085[16] = 0;
   out_3057231760306651085[17] = 0;
   out_3057231760306651085[18] = 0;
   out_3057231760306651085[19] = 0;
   out_3057231760306651085[20] = 0;
   out_3057231760306651085[21] = 0;
   out_3057231760306651085[22] = 1;
   out_3057231760306651085[23] = 0;
   out_3057231760306651085[24] = 0;
   out_3057231760306651085[25] = 0;
   out_3057231760306651085[26] = 0;
   out_3057231760306651085[27] = 0;
   out_3057231760306651085[28] = 0;
   out_3057231760306651085[29] = 0;
   out_3057231760306651085[30] = 0;
   out_3057231760306651085[31] = 0;
   out_3057231760306651085[32] = 0;
   out_3057231760306651085[33] = 0;
   out_3057231760306651085[34] = 0;
   out_3057231760306651085[35] = 0;
   out_3057231760306651085[36] = 0;
   out_3057231760306651085[37] = 0;
   out_3057231760306651085[38] = 0;
   out_3057231760306651085[39] = 0;
   out_3057231760306651085[40] = 0;
   out_3057231760306651085[41] = 1;
   out_3057231760306651085[42] = 0;
   out_3057231760306651085[43] = 0;
   out_3057231760306651085[44] = 0;
   out_3057231760306651085[45] = 0;
   out_3057231760306651085[46] = 0;
   out_3057231760306651085[47] = 0;
   out_3057231760306651085[48] = 0;
   out_3057231760306651085[49] = 0;
   out_3057231760306651085[50] = 0;
   out_3057231760306651085[51] = 0;
   out_3057231760306651085[52] = 0;
   out_3057231760306651085[53] = 0;
}
void h_14(double *state, double *unused, double *out_3232252269187951923) {
   out_3232252269187951923[0] = state[6];
   out_3232252269187951923[1] = state[7];
   out_3232252269187951923[2] = state[8];
}
void H_14(double *state, double *unused, double *out_6704622112283867485) {
   out_6704622112283867485[0] = 0;
   out_6704622112283867485[1] = 0;
   out_6704622112283867485[2] = 0;
   out_6704622112283867485[3] = 0;
   out_6704622112283867485[4] = 0;
   out_6704622112283867485[5] = 0;
   out_6704622112283867485[6] = 1;
   out_6704622112283867485[7] = 0;
   out_6704622112283867485[8] = 0;
   out_6704622112283867485[9] = 0;
   out_6704622112283867485[10] = 0;
   out_6704622112283867485[11] = 0;
   out_6704622112283867485[12] = 0;
   out_6704622112283867485[13] = 0;
   out_6704622112283867485[14] = 0;
   out_6704622112283867485[15] = 0;
   out_6704622112283867485[16] = 0;
   out_6704622112283867485[17] = 0;
   out_6704622112283867485[18] = 0;
   out_6704622112283867485[19] = 0;
   out_6704622112283867485[20] = 0;
   out_6704622112283867485[21] = 0;
   out_6704622112283867485[22] = 0;
   out_6704622112283867485[23] = 0;
   out_6704622112283867485[24] = 0;
   out_6704622112283867485[25] = 1;
   out_6704622112283867485[26] = 0;
   out_6704622112283867485[27] = 0;
   out_6704622112283867485[28] = 0;
   out_6704622112283867485[29] = 0;
   out_6704622112283867485[30] = 0;
   out_6704622112283867485[31] = 0;
   out_6704622112283867485[32] = 0;
   out_6704622112283867485[33] = 0;
   out_6704622112283867485[34] = 0;
   out_6704622112283867485[35] = 0;
   out_6704622112283867485[36] = 0;
   out_6704622112283867485[37] = 0;
   out_6704622112283867485[38] = 0;
   out_6704622112283867485[39] = 0;
   out_6704622112283867485[40] = 0;
   out_6704622112283867485[41] = 0;
   out_6704622112283867485[42] = 0;
   out_6704622112283867485[43] = 0;
   out_6704622112283867485[44] = 1;
   out_6704622112283867485[45] = 0;
   out_6704622112283867485[46] = 0;
   out_6704622112283867485[47] = 0;
   out_6704622112283867485[48] = 0;
   out_6704622112283867485[49] = 0;
   out_6704622112283867485[50] = 0;
   out_6704622112283867485[51] = 0;
   out_6704622112283867485[52] = 0;
   out_6704622112283867485[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_7709211145934123991) {
  err_fun(nom_x, delta_x, out_7709211145934123991);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_3942366649005103634) {
  inv_err_fun(nom_x, true_x, out_3942366649005103634);
}
void pose_H_mod_fun(double *state, double *out_7024720103031486995) {
  H_mod_fun(state, out_7024720103031486995);
}
void pose_f_fun(double *state, double dt, double *out_8735071172480870357) {
  f_fun(state,  dt, out_8735071172480870357);
}
void pose_F_fun(double *state, double dt, double *out_823961402091764503) {
  F_fun(state,  dt, out_823961402091764503);
}
void pose_h_4(double *state, double *unused, double *out_5737604937341341534) {
  h_4(state, unused, out_5737604937341341534);
}
void pose_H_4(double *state, double *unused, double *out_6269505585638983886) {
  H_4(state, unused, out_6269505585638983886);
}
void pose_h_10(double *state, double *unused, double *out_5255790841188854786) {
  h_10(state, unused, out_5255790841188854786);
}
void pose_H_10(double *state, double *unused, double *out_4631033678897535887) {
  H_10(state, unused, out_4631033678897535887);
}
void pose_h_13(double *state, double *unused, double *out_6690590361496767190) {
  h_13(state, unused, out_6690590361496767190);
}
void pose_H_13(double *state, double *unused, double *out_3057231760306651085) {
  H_13(state, unused, out_3057231760306651085);
}
void pose_h_14(double *state, double *unused, double *out_3232252269187951923) {
  h_14(state, unused, out_3232252269187951923);
}
void pose_H_14(double *state, double *unused, double *out_6704622112283867485) {
  H_14(state, unused, out_6704622112283867485);
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
