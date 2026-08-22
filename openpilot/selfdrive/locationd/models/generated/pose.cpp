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
void err_fun(double *nom_x, double *delta_x, double *out_7950841656255825399) {
   out_7950841656255825399[0] = delta_x[0] + nom_x[0];
   out_7950841656255825399[1] = delta_x[1] + nom_x[1];
   out_7950841656255825399[2] = delta_x[2] + nom_x[2];
   out_7950841656255825399[3] = delta_x[3] + nom_x[3];
   out_7950841656255825399[4] = delta_x[4] + nom_x[4];
   out_7950841656255825399[5] = delta_x[5] + nom_x[5];
   out_7950841656255825399[6] = delta_x[6] + nom_x[6];
   out_7950841656255825399[7] = delta_x[7] + nom_x[7];
   out_7950841656255825399[8] = delta_x[8] + nom_x[8];
   out_7950841656255825399[9] = delta_x[9] + nom_x[9];
   out_7950841656255825399[10] = delta_x[10] + nom_x[10];
   out_7950841656255825399[11] = delta_x[11] + nom_x[11];
   out_7950841656255825399[12] = delta_x[12] + nom_x[12];
   out_7950841656255825399[13] = delta_x[13] + nom_x[13];
   out_7950841656255825399[14] = delta_x[14] + nom_x[14];
   out_7950841656255825399[15] = delta_x[15] + nom_x[15];
   out_7950841656255825399[16] = delta_x[16] + nom_x[16];
   out_7950841656255825399[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1038560697701516954) {
   out_1038560697701516954[0] = -nom_x[0] + true_x[0];
   out_1038560697701516954[1] = -nom_x[1] + true_x[1];
   out_1038560697701516954[2] = -nom_x[2] + true_x[2];
   out_1038560697701516954[3] = -nom_x[3] + true_x[3];
   out_1038560697701516954[4] = -nom_x[4] + true_x[4];
   out_1038560697701516954[5] = -nom_x[5] + true_x[5];
   out_1038560697701516954[6] = -nom_x[6] + true_x[6];
   out_1038560697701516954[7] = -nom_x[7] + true_x[7];
   out_1038560697701516954[8] = -nom_x[8] + true_x[8];
   out_1038560697701516954[9] = -nom_x[9] + true_x[9];
   out_1038560697701516954[10] = -nom_x[10] + true_x[10];
   out_1038560697701516954[11] = -nom_x[11] + true_x[11];
   out_1038560697701516954[12] = -nom_x[12] + true_x[12];
   out_1038560697701516954[13] = -nom_x[13] + true_x[13];
   out_1038560697701516954[14] = -nom_x[14] + true_x[14];
   out_1038560697701516954[15] = -nom_x[15] + true_x[15];
   out_1038560697701516954[16] = -nom_x[16] + true_x[16];
   out_1038560697701516954[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_7368662583295686451) {
   out_7368662583295686451[0] = 1.0;
   out_7368662583295686451[1] = 0.0;
   out_7368662583295686451[2] = 0.0;
   out_7368662583295686451[3] = 0.0;
   out_7368662583295686451[4] = 0.0;
   out_7368662583295686451[5] = 0.0;
   out_7368662583295686451[6] = 0.0;
   out_7368662583295686451[7] = 0.0;
   out_7368662583295686451[8] = 0.0;
   out_7368662583295686451[9] = 0.0;
   out_7368662583295686451[10] = 0.0;
   out_7368662583295686451[11] = 0.0;
   out_7368662583295686451[12] = 0.0;
   out_7368662583295686451[13] = 0.0;
   out_7368662583295686451[14] = 0.0;
   out_7368662583295686451[15] = 0.0;
   out_7368662583295686451[16] = 0.0;
   out_7368662583295686451[17] = 0.0;
   out_7368662583295686451[18] = 0.0;
   out_7368662583295686451[19] = 1.0;
   out_7368662583295686451[20] = 0.0;
   out_7368662583295686451[21] = 0.0;
   out_7368662583295686451[22] = 0.0;
   out_7368662583295686451[23] = 0.0;
   out_7368662583295686451[24] = 0.0;
   out_7368662583295686451[25] = 0.0;
   out_7368662583295686451[26] = 0.0;
   out_7368662583295686451[27] = 0.0;
   out_7368662583295686451[28] = 0.0;
   out_7368662583295686451[29] = 0.0;
   out_7368662583295686451[30] = 0.0;
   out_7368662583295686451[31] = 0.0;
   out_7368662583295686451[32] = 0.0;
   out_7368662583295686451[33] = 0.0;
   out_7368662583295686451[34] = 0.0;
   out_7368662583295686451[35] = 0.0;
   out_7368662583295686451[36] = 0.0;
   out_7368662583295686451[37] = 0.0;
   out_7368662583295686451[38] = 1.0;
   out_7368662583295686451[39] = 0.0;
   out_7368662583295686451[40] = 0.0;
   out_7368662583295686451[41] = 0.0;
   out_7368662583295686451[42] = 0.0;
   out_7368662583295686451[43] = 0.0;
   out_7368662583295686451[44] = 0.0;
   out_7368662583295686451[45] = 0.0;
   out_7368662583295686451[46] = 0.0;
   out_7368662583295686451[47] = 0.0;
   out_7368662583295686451[48] = 0.0;
   out_7368662583295686451[49] = 0.0;
   out_7368662583295686451[50] = 0.0;
   out_7368662583295686451[51] = 0.0;
   out_7368662583295686451[52] = 0.0;
   out_7368662583295686451[53] = 0.0;
   out_7368662583295686451[54] = 0.0;
   out_7368662583295686451[55] = 0.0;
   out_7368662583295686451[56] = 0.0;
   out_7368662583295686451[57] = 1.0;
   out_7368662583295686451[58] = 0.0;
   out_7368662583295686451[59] = 0.0;
   out_7368662583295686451[60] = 0.0;
   out_7368662583295686451[61] = 0.0;
   out_7368662583295686451[62] = 0.0;
   out_7368662583295686451[63] = 0.0;
   out_7368662583295686451[64] = 0.0;
   out_7368662583295686451[65] = 0.0;
   out_7368662583295686451[66] = 0.0;
   out_7368662583295686451[67] = 0.0;
   out_7368662583295686451[68] = 0.0;
   out_7368662583295686451[69] = 0.0;
   out_7368662583295686451[70] = 0.0;
   out_7368662583295686451[71] = 0.0;
   out_7368662583295686451[72] = 0.0;
   out_7368662583295686451[73] = 0.0;
   out_7368662583295686451[74] = 0.0;
   out_7368662583295686451[75] = 0.0;
   out_7368662583295686451[76] = 1.0;
   out_7368662583295686451[77] = 0.0;
   out_7368662583295686451[78] = 0.0;
   out_7368662583295686451[79] = 0.0;
   out_7368662583295686451[80] = 0.0;
   out_7368662583295686451[81] = 0.0;
   out_7368662583295686451[82] = 0.0;
   out_7368662583295686451[83] = 0.0;
   out_7368662583295686451[84] = 0.0;
   out_7368662583295686451[85] = 0.0;
   out_7368662583295686451[86] = 0.0;
   out_7368662583295686451[87] = 0.0;
   out_7368662583295686451[88] = 0.0;
   out_7368662583295686451[89] = 0.0;
   out_7368662583295686451[90] = 0.0;
   out_7368662583295686451[91] = 0.0;
   out_7368662583295686451[92] = 0.0;
   out_7368662583295686451[93] = 0.0;
   out_7368662583295686451[94] = 0.0;
   out_7368662583295686451[95] = 1.0;
   out_7368662583295686451[96] = 0.0;
   out_7368662583295686451[97] = 0.0;
   out_7368662583295686451[98] = 0.0;
   out_7368662583295686451[99] = 0.0;
   out_7368662583295686451[100] = 0.0;
   out_7368662583295686451[101] = 0.0;
   out_7368662583295686451[102] = 0.0;
   out_7368662583295686451[103] = 0.0;
   out_7368662583295686451[104] = 0.0;
   out_7368662583295686451[105] = 0.0;
   out_7368662583295686451[106] = 0.0;
   out_7368662583295686451[107] = 0.0;
   out_7368662583295686451[108] = 0.0;
   out_7368662583295686451[109] = 0.0;
   out_7368662583295686451[110] = 0.0;
   out_7368662583295686451[111] = 0.0;
   out_7368662583295686451[112] = 0.0;
   out_7368662583295686451[113] = 0.0;
   out_7368662583295686451[114] = 1.0;
   out_7368662583295686451[115] = 0.0;
   out_7368662583295686451[116] = 0.0;
   out_7368662583295686451[117] = 0.0;
   out_7368662583295686451[118] = 0.0;
   out_7368662583295686451[119] = 0.0;
   out_7368662583295686451[120] = 0.0;
   out_7368662583295686451[121] = 0.0;
   out_7368662583295686451[122] = 0.0;
   out_7368662583295686451[123] = 0.0;
   out_7368662583295686451[124] = 0.0;
   out_7368662583295686451[125] = 0.0;
   out_7368662583295686451[126] = 0.0;
   out_7368662583295686451[127] = 0.0;
   out_7368662583295686451[128] = 0.0;
   out_7368662583295686451[129] = 0.0;
   out_7368662583295686451[130] = 0.0;
   out_7368662583295686451[131] = 0.0;
   out_7368662583295686451[132] = 0.0;
   out_7368662583295686451[133] = 1.0;
   out_7368662583295686451[134] = 0.0;
   out_7368662583295686451[135] = 0.0;
   out_7368662583295686451[136] = 0.0;
   out_7368662583295686451[137] = 0.0;
   out_7368662583295686451[138] = 0.0;
   out_7368662583295686451[139] = 0.0;
   out_7368662583295686451[140] = 0.0;
   out_7368662583295686451[141] = 0.0;
   out_7368662583295686451[142] = 0.0;
   out_7368662583295686451[143] = 0.0;
   out_7368662583295686451[144] = 0.0;
   out_7368662583295686451[145] = 0.0;
   out_7368662583295686451[146] = 0.0;
   out_7368662583295686451[147] = 0.0;
   out_7368662583295686451[148] = 0.0;
   out_7368662583295686451[149] = 0.0;
   out_7368662583295686451[150] = 0.0;
   out_7368662583295686451[151] = 0.0;
   out_7368662583295686451[152] = 1.0;
   out_7368662583295686451[153] = 0.0;
   out_7368662583295686451[154] = 0.0;
   out_7368662583295686451[155] = 0.0;
   out_7368662583295686451[156] = 0.0;
   out_7368662583295686451[157] = 0.0;
   out_7368662583295686451[158] = 0.0;
   out_7368662583295686451[159] = 0.0;
   out_7368662583295686451[160] = 0.0;
   out_7368662583295686451[161] = 0.0;
   out_7368662583295686451[162] = 0.0;
   out_7368662583295686451[163] = 0.0;
   out_7368662583295686451[164] = 0.0;
   out_7368662583295686451[165] = 0.0;
   out_7368662583295686451[166] = 0.0;
   out_7368662583295686451[167] = 0.0;
   out_7368662583295686451[168] = 0.0;
   out_7368662583295686451[169] = 0.0;
   out_7368662583295686451[170] = 0.0;
   out_7368662583295686451[171] = 1.0;
   out_7368662583295686451[172] = 0.0;
   out_7368662583295686451[173] = 0.0;
   out_7368662583295686451[174] = 0.0;
   out_7368662583295686451[175] = 0.0;
   out_7368662583295686451[176] = 0.0;
   out_7368662583295686451[177] = 0.0;
   out_7368662583295686451[178] = 0.0;
   out_7368662583295686451[179] = 0.0;
   out_7368662583295686451[180] = 0.0;
   out_7368662583295686451[181] = 0.0;
   out_7368662583295686451[182] = 0.0;
   out_7368662583295686451[183] = 0.0;
   out_7368662583295686451[184] = 0.0;
   out_7368662583295686451[185] = 0.0;
   out_7368662583295686451[186] = 0.0;
   out_7368662583295686451[187] = 0.0;
   out_7368662583295686451[188] = 0.0;
   out_7368662583295686451[189] = 0.0;
   out_7368662583295686451[190] = 1.0;
   out_7368662583295686451[191] = 0.0;
   out_7368662583295686451[192] = 0.0;
   out_7368662583295686451[193] = 0.0;
   out_7368662583295686451[194] = 0.0;
   out_7368662583295686451[195] = 0.0;
   out_7368662583295686451[196] = 0.0;
   out_7368662583295686451[197] = 0.0;
   out_7368662583295686451[198] = 0.0;
   out_7368662583295686451[199] = 0.0;
   out_7368662583295686451[200] = 0.0;
   out_7368662583295686451[201] = 0.0;
   out_7368662583295686451[202] = 0.0;
   out_7368662583295686451[203] = 0.0;
   out_7368662583295686451[204] = 0.0;
   out_7368662583295686451[205] = 0.0;
   out_7368662583295686451[206] = 0.0;
   out_7368662583295686451[207] = 0.0;
   out_7368662583295686451[208] = 0.0;
   out_7368662583295686451[209] = 1.0;
   out_7368662583295686451[210] = 0.0;
   out_7368662583295686451[211] = 0.0;
   out_7368662583295686451[212] = 0.0;
   out_7368662583295686451[213] = 0.0;
   out_7368662583295686451[214] = 0.0;
   out_7368662583295686451[215] = 0.0;
   out_7368662583295686451[216] = 0.0;
   out_7368662583295686451[217] = 0.0;
   out_7368662583295686451[218] = 0.0;
   out_7368662583295686451[219] = 0.0;
   out_7368662583295686451[220] = 0.0;
   out_7368662583295686451[221] = 0.0;
   out_7368662583295686451[222] = 0.0;
   out_7368662583295686451[223] = 0.0;
   out_7368662583295686451[224] = 0.0;
   out_7368662583295686451[225] = 0.0;
   out_7368662583295686451[226] = 0.0;
   out_7368662583295686451[227] = 0.0;
   out_7368662583295686451[228] = 1.0;
   out_7368662583295686451[229] = 0.0;
   out_7368662583295686451[230] = 0.0;
   out_7368662583295686451[231] = 0.0;
   out_7368662583295686451[232] = 0.0;
   out_7368662583295686451[233] = 0.0;
   out_7368662583295686451[234] = 0.0;
   out_7368662583295686451[235] = 0.0;
   out_7368662583295686451[236] = 0.0;
   out_7368662583295686451[237] = 0.0;
   out_7368662583295686451[238] = 0.0;
   out_7368662583295686451[239] = 0.0;
   out_7368662583295686451[240] = 0.0;
   out_7368662583295686451[241] = 0.0;
   out_7368662583295686451[242] = 0.0;
   out_7368662583295686451[243] = 0.0;
   out_7368662583295686451[244] = 0.0;
   out_7368662583295686451[245] = 0.0;
   out_7368662583295686451[246] = 0.0;
   out_7368662583295686451[247] = 1.0;
   out_7368662583295686451[248] = 0.0;
   out_7368662583295686451[249] = 0.0;
   out_7368662583295686451[250] = 0.0;
   out_7368662583295686451[251] = 0.0;
   out_7368662583295686451[252] = 0.0;
   out_7368662583295686451[253] = 0.0;
   out_7368662583295686451[254] = 0.0;
   out_7368662583295686451[255] = 0.0;
   out_7368662583295686451[256] = 0.0;
   out_7368662583295686451[257] = 0.0;
   out_7368662583295686451[258] = 0.0;
   out_7368662583295686451[259] = 0.0;
   out_7368662583295686451[260] = 0.0;
   out_7368662583295686451[261] = 0.0;
   out_7368662583295686451[262] = 0.0;
   out_7368662583295686451[263] = 0.0;
   out_7368662583295686451[264] = 0.0;
   out_7368662583295686451[265] = 0.0;
   out_7368662583295686451[266] = 1.0;
   out_7368662583295686451[267] = 0.0;
   out_7368662583295686451[268] = 0.0;
   out_7368662583295686451[269] = 0.0;
   out_7368662583295686451[270] = 0.0;
   out_7368662583295686451[271] = 0.0;
   out_7368662583295686451[272] = 0.0;
   out_7368662583295686451[273] = 0.0;
   out_7368662583295686451[274] = 0.0;
   out_7368662583295686451[275] = 0.0;
   out_7368662583295686451[276] = 0.0;
   out_7368662583295686451[277] = 0.0;
   out_7368662583295686451[278] = 0.0;
   out_7368662583295686451[279] = 0.0;
   out_7368662583295686451[280] = 0.0;
   out_7368662583295686451[281] = 0.0;
   out_7368662583295686451[282] = 0.0;
   out_7368662583295686451[283] = 0.0;
   out_7368662583295686451[284] = 0.0;
   out_7368662583295686451[285] = 1.0;
   out_7368662583295686451[286] = 0.0;
   out_7368662583295686451[287] = 0.0;
   out_7368662583295686451[288] = 0.0;
   out_7368662583295686451[289] = 0.0;
   out_7368662583295686451[290] = 0.0;
   out_7368662583295686451[291] = 0.0;
   out_7368662583295686451[292] = 0.0;
   out_7368662583295686451[293] = 0.0;
   out_7368662583295686451[294] = 0.0;
   out_7368662583295686451[295] = 0.0;
   out_7368662583295686451[296] = 0.0;
   out_7368662583295686451[297] = 0.0;
   out_7368662583295686451[298] = 0.0;
   out_7368662583295686451[299] = 0.0;
   out_7368662583295686451[300] = 0.0;
   out_7368662583295686451[301] = 0.0;
   out_7368662583295686451[302] = 0.0;
   out_7368662583295686451[303] = 0.0;
   out_7368662583295686451[304] = 1.0;
   out_7368662583295686451[305] = 0.0;
   out_7368662583295686451[306] = 0.0;
   out_7368662583295686451[307] = 0.0;
   out_7368662583295686451[308] = 0.0;
   out_7368662583295686451[309] = 0.0;
   out_7368662583295686451[310] = 0.0;
   out_7368662583295686451[311] = 0.0;
   out_7368662583295686451[312] = 0.0;
   out_7368662583295686451[313] = 0.0;
   out_7368662583295686451[314] = 0.0;
   out_7368662583295686451[315] = 0.0;
   out_7368662583295686451[316] = 0.0;
   out_7368662583295686451[317] = 0.0;
   out_7368662583295686451[318] = 0.0;
   out_7368662583295686451[319] = 0.0;
   out_7368662583295686451[320] = 0.0;
   out_7368662583295686451[321] = 0.0;
   out_7368662583295686451[322] = 0.0;
   out_7368662583295686451[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_7152923552696196830) {
   out_7152923552696196830[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_7152923552696196830[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_7152923552696196830[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_7152923552696196830[3] = dt*state[12] + state[3];
   out_7152923552696196830[4] = dt*state[13] + state[4];
   out_7152923552696196830[5] = dt*state[14] + state[5];
   out_7152923552696196830[6] = state[6];
   out_7152923552696196830[7] = state[7];
   out_7152923552696196830[8] = state[8];
   out_7152923552696196830[9] = state[9];
   out_7152923552696196830[10] = state[10];
   out_7152923552696196830[11] = state[11];
   out_7152923552696196830[12] = state[12];
   out_7152923552696196830[13] = state[13];
   out_7152923552696196830[14] = state[14];
   out_7152923552696196830[15] = state[15];
   out_7152923552696196830[16] = state[16];
   out_7152923552696196830[17] = state[17];
}
void F_fun(double *state, double dt, double *out_1783079396843657897) {
   out_1783079396843657897[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1783079396843657897[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1783079396843657897[2] = 0;
   out_1783079396843657897[3] = 0;
   out_1783079396843657897[4] = 0;
   out_1783079396843657897[5] = 0;
   out_1783079396843657897[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1783079396843657897[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1783079396843657897[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1783079396843657897[9] = 0;
   out_1783079396843657897[10] = 0;
   out_1783079396843657897[11] = 0;
   out_1783079396843657897[12] = 0;
   out_1783079396843657897[13] = 0;
   out_1783079396843657897[14] = 0;
   out_1783079396843657897[15] = 0;
   out_1783079396843657897[16] = 0;
   out_1783079396843657897[17] = 0;
   out_1783079396843657897[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_1783079396843657897[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_1783079396843657897[20] = 0;
   out_1783079396843657897[21] = 0;
   out_1783079396843657897[22] = 0;
   out_1783079396843657897[23] = 0;
   out_1783079396843657897[24] = 0;
   out_1783079396843657897[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_1783079396843657897[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_1783079396843657897[27] = 0;
   out_1783079396843657897[28] = 0;
   out_1783079396843657897[29] = 0;
   out_1783079396843657897[30] = 0;
   out_1783079396843657897[31] = 0;
   out_1783079396843657897[32] = 0;
   out_1783079396843657897[33] = 0;
   out_1783079396843657897[34] = 0;
   out_1783079396843657897[35] = 0;
   out_1783079396843657897[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1783079396843657897[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1783079396843657897[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1783079396843657897[39] = 0;
   out_1783079396843657897[40] = 0;
   out_1783079396843657897[41] = 0;
   out_1783079396843657897[42] = 0;
   out_1783079396843657897[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1783079396843657897[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1783079396843657897[45] = 0;
   out_1783079396843657897[46] = 0;
   out_1783079396843657897[47] = 0;
   out_1783079396843657897[48] = 0;
   out_1783079396843657897[49] = 0;
   out_1783079396843657897[50] = 0;
   out_1783079396843657897[51] = 0;
   out_1783079396843657897[52] = 0;
   out_1783079396843657897[53] = 0;
   out_1783079396843657897[54] = 0;
   out_1783079396843657897[55] = 0;
   out_1783079396843657897[56] = 0;
   out_1783079396843657897[57] = 1;
   out_1783079396843657897[58] = 0;
   out_1783079396843657897[59] = 0;
   out_1783079396843657897[60] = 0;
   out_1783079396843657897[61] = 0;
   out_1783079396843657897[62] = 0;
   out_1783079396843657897[63] = 0;
   out_1783079396843657897[64] = 0;
   out_1783079396843657897[65] = 0;
   out_1783079396843657897[66] = dt;
   out_1783079396843657897[67] = 0;
   out_1783079396843657897[68] = 0;
   out_1783079396843657897[69] = 0;
   out_1783079396843657897[70] = 0;
   out_1783079396843657897[71] = 0;
   out_1783079396843657897[72] = 0;
   out_1783079396843657897[73] = 0;
   out_1783079396843657897[74] = 0;
   out_1783079396843657897[75] = 0;
   out_1783079396843657897[76] = 1;
   out_1783079396843657897[77] = 0;
   out_1783079396843657897[78] = 0;
   out_1783079396843657897[79] = 0;
   out_1783079396843657897[80] = 0;
   out_1783079396843657897[81] = 0;
   out_1783079396843657897[82] = 0;
   out_1783079396843657897[83] = 0;
   out_1783079396843657897[84] = 0;
   out_1783079396843657897[85] = dt;
   out_1783079396843657897[86] = 0;
   out_1783079396843657897[87] = 0;
   out_1783079396843657897[88] = 0;
   out_1783079396843657897[89] = 0;
   out_1783079396843657897[90] = 0;
   out_1783079396843657897[91] = 0;
   out_1783079396843657897[92] = 0;
   out_1783079396843657897[93] = 0;
   out_1783079396843657897[94] = 0;
   out_1783079396843657897[95] = 1;
   out_1783079396843657897[96] = 0;
   out_1783079396843657897[97] = 0;
   out_1783079396843657897[98] = 0;
   out_1783079396843657897[99] = 0;
   out_1783079396843657897[100] = 0;
   out_1783079396843657897[101] = 0;
   out_1783079396843657897[102] = 0;
   out_1783079396843657897[103] = 0;
   out_1783079396843657897[104] = dt;
   out_1783079396843657897[105] = 0;
   out_1783079396843657897[106] = 0;
   out_1783079396843657897[107] = 0;
   out_1783079396843657897[108] = 0;
   out_1783079396843657897[109] = 0;
   out_1783079396843657897[110] = 0;
   out_1783079396843657897[111] = 0;
   out_1783079396843657897[112] = 0;
   out_1783079396843657897[113] = 0;
   out_1783079396843657897[114] = 1;
   out_1783079396843657897[115] = 0;
   out_1783079396843657897[116] = 0;
   out_1783079396843657897[117] = 0;
   out_1783079396843657897[118] = 0;
   out_1783079396843657897[119] = 0;
   out_1783079396843657897[120] = 0;
   out_1783079396843657897[121] = 0;
   out_1783079396843657897[122] = 0;
   out_1783079396843657897[123] = 0;
   out_1783079396843657897[124] = 0;
   out_1783079396843657897[125] = 0;
   out_1783079396843657897[126] = 0;
   out_1783079396843657897[127] = 0;
   out_1783079396843657897[128] = 0;
   out_1783079396843657897[129] = 0;
   out_1783079396843657897[130] = 0;
   out_1783079396843657897[131] = 0;
   out_1783079396843657897[132] = 0;
   out_1783079396843657897[133] = 1;
   out_1783079396843657897[134] = 0;
   out_1783079396843657897[135] = 0;
   out_1783079396843657897[136] = 0;
   out_1783079396843657897[137] = 0;
   out_1783079396843657897[138] = 0;
   out_1783079396843657897[139] = 0;
   out_1783079396843657897[140] = 0;
   out_1783079396843657897[141] = 0;
   out_1783079396843657897[142] = 0;
   out_1783079396843657897[143] = 0;
   out_1783079396843657897[144] = 0;
   out_1783079396843657897[145] = 0;
   out_1783079396843657897[146] = 0;
   out_1783079396843657897[147] = 0;
   out_1783079396843657897[148] = 0;
   out_1783079396843657897[149] = 0;
   out_1783079396843657897[150] = 0;
   out_1783079396843657897[151] = 0;
   out_1783079396843657897[152] = 1;
   out_1783079396843657897[153] = 0;
   out_1783079396843657897[154] = 0;
   out_1783079396843657897[155] = 0;
   out_1783079396843657897[156] = 0;
   out_1783079396843657897[157] = 0;
   out_1783079396843657897[158] = 0;
   out_1783079396843657897[159] = 0;
   out_1783079396843657897[160] = 0;
   out_1783079396843657897[161] = 0;
   out_1783079396843657897[162] = 0;
   out_1783079396843657897[163] = 0;
   out_1783079396843657897[164] = 0;
   out_1783079396843657897[165] = 0;
   out_1783079396843657897[166] = 0;
   out_1783079396843657897[167] = 0;
   out_1783079396843657897[168] = 0;
   out_1783079396843657897[169] = 0;
   out_1783079396843657897[170] = 0;
   out_1783079396843657897[171] = 1;
   out_1783079396843657897[172] = 0;
   out_1783079396843657897[173] = 0;
   out_1783079396843657897[174] = 0;
   out_1783079396843657897[175] = 0;
   out_1783079396843657897[176] = 0;
   out_1783079396843657897[177] = 0;
   out_1783079396843657897[178] = 0;
   out_1783079396843657897[179] = 0;
   out_1783079396843657897[180] = 0;
   out_1783079396843657897[181] = 0;
   out_1783079396843657897[182] = 0;
   out_1783079396843657897[183] = 0;
   out_1783079396843657897[184] = 0;
   out_1783079396843657897[185] = 0;
   out_1783079396843657897[186] = 0;
   out_1783079396843657897[187] = 0;
   out_1783079396843657897[188] = 0;
   out_1783079396843657897[189] = 0;
   out_1783079396843657897[190] = 1;
   out_1783079396843657897[191] = 0;
   out_1783079396843657897[192] = 0;
   out_1783079396843657897[193] = 0;
   out_1783079396843657897[194] = 0;
   out_1783079396843657897[195] = 0;
   out_1783079396843657897[196] = 0;
   out_1783079396843657897[197] = 0;
   out_1783079396843657897[198] = 0;
   out_1783079396843657897[199] = 0;
   out_1783079396843657897[200] = 0;
   out_1783079396843657897[201] = 0;
   out_1783079396843657897[202] = 0;
   out_1783079396843657897[203] = 0;
   out_1783079396843657897[204] = 0;
   out_1783079396843657897[205] = 0;
   out_1783079396843657897[206] = 0;
   out_1783079396843657897[207] = 0;
   out_1783079396843657897[208] = 0;
   out_1783079396843657897[209] = 1;
   out_1783079396843657897[210] = 0;
   out_1783079396843657897[211] = 0;
   out_1783079396843657897[212] = 0;
   out_1783079396843657897[213] = 0;
   out_1783079396843657897[214] = 0;
   out_1783079396843657897[215] = 0;
   out_1783079396843657897[216] = 0;
   out_1783079396843657897[217] = 0;
   out_1783079396843657897[218] = 0;
   out_1783079396843657897[219] = 0;
   out_1783079396843657897[220] = 0;
   out_1783079396843657897[221] = 0;
   out_1783079396843657897[222] = 0;
   out_1783079396843657897[223] = 0;
   out_1783079396843657897[224] = 0;
   out_1783079396843657897[225] = 0;
   out_1783079396843657897[226] = 0;
   out_1783079396843657897[227] = 0;
   out_1783079396843657897[228] = 1;
   out_1783079396843657897[229] = 0;
   out_1783079396843657897[230] = 0;
   out_1783079396843657897[231] = 0;
   out_1783079396843657897[232] = 0;
   out_1783079396843657897[233] = 0;
   out_1783079396843657897[234] = 0;
   out_1783079396843657897[235] = 0;
   out_1783079396843657897[236] = 0;
   out_1783079396843657897[237] = 0;
   out_1783079396843657897[238] = 0;
   out_1783079396843657897[239] = 0;
   out_1783079396843657897[240] = 0;
   out_1783079396843657897[241] = 0;
   out_1783079396843657897[242] = 0;
   out_1783079396843657897[243] = 0;
   out_1783079396843657897[244] = 0;
   out_1783079396843657897[245] = 0;
   out_1783079396843657897[246] = 0;
   out_1783079396843657897[247] = 1;
   out_1783079396843657897[248] = 0;
   out_1783079396843657897[249] = 0;
   out_1783079396843657897[250] = 0;
   out_1783079396843657897[251] = 0;
   out_1783079396843657897[252] = 0;
   out_1783079396843657897[253] = 0;
   out_1783079396843657897[254] = 0;
   out_1783079396843657897[255] = 0;
   out_1783079396843657897[256] = 0;
   out_1783079396843657897[257] = 0;
   out_1783079396843657897[258] = 0;
   out_1783079396843657897[259] = 0;
   out_1783079396843657897[260] = 0;
   out_1783079396843657897[261] = 0;
   out_1783079396843657897[262] = 0;
   out_1783079396843657897[263] = 0;
   out_1783079396843657897[264] = 0;
   out_1783079396843657897[265] = 0;
   out_1783079396843657897[266] = 1;
   out_1783079396843657897[267] = 0;
   out_1783079396843657897[268] = 0;
   out_1783079396843657897[269] = 0;
   out_1783079396843657897[270] = 0;
   out_1783079396843657897[271] = 0;
   out_1783079396843657897[272] = 0;
   out_1783079396843657897[273] = 0;
   out_1783079396843657897[274] = 0;
   out_1783079396843657897[275] = 0;
   out_1783079396843657897[276] = 0;
   out_1783079396843657897[277] = 0;
   out_1783079396843657897[278] = 0;
   out_1783079396843657897[279] = 0;
   out_1783079396843657897[280] = 0;
   out_1783079396843657897[281] = 0;
   out_1783079396843657897[282] = 0;
   out_1783079396843657897[283] = 0;
   out_1783079396843657897[284] = 0;
   out_1783079396843657897[285] = 1;
   out_1783079396843657897[286] = 0;
   out_1783079396843657897[287] = 0;
   out_1783079396843657897[288] = 0;
   out_1783079396843657897[289] = 0;
   out_1783079396843657897[290] = 0;
   out_1783079396843657897[291] = 0;
   out_1783079396843657897[292] = 0;
   out_1783079396843657897[293] = 0;
   out_1783079396843657897[294] = 0;
   out_1783079396843657897[295] = 0;
   out_1783079396843657897[296] = 0;
   out_1783079396843657897[297] = 0;
   out_1783079396843657897[298] = 0;
   out_1783079396843657897[299] = 0;
   out_1783079396843657897[300] = 0;
   out_1783079396843657897[301] = 0;
   out_1783079396843657897[302] = 0;
   out_1783079396843657897[303] = 0;
   out_1783079396843657897[304] = 1;
   out_1783079396843657897[305] = 0;
   out_1783079396843657897[306] = 0;
   out_1783079396843657897[307] = 0;
   out_1783079396843657897[308] = 0;
   out_1783079396843657897[309] = 0;
   out_1783079396843657897[310] = 0;
   out_1783079396843657897[311] = 0;
   out_1783079396843657897[312] = 0;
   out_1783079396843657897[313] = 0;
   out_1783079396843657897[314] = 0;
   out_1783079396843657897[315] = 0;
   out_1783079396843657897[316] = 0;
   out_1783079396843657897[317] = 0;
   out_1783079396843657897[318] = 0;
   out_1783079396843657897[319] = 0;
   out_1783079396843657897[320] = 0;
   out_1783079396843657897[321] = 0;
   out_1783079396843657897[322] = 0;
   out_1783079396843657897[323] = 1;
}
void h_4(double *state, double *unused, double *out_7141288839189123597) {
   out_7141288839189123597[0] = state[6] + state[9];
   out_7141288839189123597[1] = state[7] + state[10];
   out_7141288839189123597[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_8122823585350399058) {
   out_8122823585350399058[0] = 0;
   out_8122823585350399058[1] = 0;
   out_8122823585350399058[2] = 0;
   out_8122823585350399058[3] = 0;
   out_8122823585350399058[4] = 0;
   out_8122823585350399058[5] = 0;
   out_8122823585350399058[6] = 1;
   out_8122823585350399058[7] = 0;
   out_8122823585350399058[8] = 0;
   out_8122823585350399058[9] = 1;
   out_8122823585350399058[10] = 0;
   out_8122823585350399058[11] = 0;
   out_8122823585350399058[12] = 0;
   out_8122823585350399058[13] = 0;
   out_8122823585350399058[14] = 0;
   out_8122823585350399058[15] = 0;
   out_8122823585350399058[16] = 0;
   out_8122823585350399058[17] = 0;
   out_8122823585350399058[18] = 0;
   out_8122823585350399058[19] = 0;
   out_8122823585350399058[20] = 0;
   out_8122823585350399058[21] = 0;
   out_8122823585350399058[22] = 0;
   out_8122823585350399058[23] = 0;
   out_8122823585350399058[24] = 0;
   out_8122823585350399058[25] = 1;
   out_8122823585350399058[26] = 0;
   out_8122823585350399058[27] = 0;
   out_8122823585350399058[28] = 1;
   out_8122823585350399058[29] = 0;
   out_8122823585350399058[30] = 0;
   out_8122823585350399058[31] = 0;
   out_8122823585350399058[32] = 0;
   out_8122823585350399058[33] = 0;
   out_8122823585350399058[34] = 0;
   out_8122823585350399058[35] = 0;
   out_8122823585350399058[36] = 0;
   out_8122823585350399058[37] = 0;
   out_8122823585350399058[38] = 0;
   out_8122823585350399058[39] = 0;
   out_8122823585350399058[40] = 0;
   out_8122823585350399058[41] = 0;
   out_8122823585350399058[42] = 0;
   out_8122823585350399058[43] = 0;
   out_8122823585350399058[44] = 1;
   out_8122823585350399058[45] = 0;
   out_8122823585350399058[46] = 0;
   out_8122823585350399058[47] = 1;
   out_8122823585350399058[48] = 0;
   out_8122823585350399058[49] = 0;
   out_8122823585350399058[50] = 0;
   out_8122823585350399058[51] = 0;
   out_8122823585350399058[52] = 0;
   out_8122823585350399058[53] = 0;
}
void h_10(double *state, double *unused, double *out_2925053845163599483) {
   out_2925053845163599483[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_2925053845163599483[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_2925053845163599483[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_360848949412854679) {
   out_360848949412854679[0] = 0;
   out_360848949412854679[1] = 9.8100000000000005*cos(state[1]);
   out_360848949412854679[2] = 0;
   out_360848949412854679[3] = 0;
   out_360848949412854679[4] = -state[8];
   out_360848949412854679[5] = state[7];
   out_360848949412854679[6] = 0;
   out_360848949412854679[7] = state[5];
   out_360848949412854679[8] = -state[4];
   out_360848949412854679[9] = 0;
   out_360848949412854679[10] = 0;
   out_360848949412854679[11] = 0;
   out_360848949412854679[12] = 1;
   out_360848949412854679[13] = 0;
   out_360848949412854679[14] = 0;
   out_360848949412854679[15] = 1;
   out_360848949412854679[16] = 0;
   out_360848949412854679[17] = 0;
   out_360848949412854679[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_360848949412854679[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_360848949412854679[20] = 0;
   out_360848949412854679[21] = state[8];
   out_360848949412854679[22] = 0;
   out_360848949412854679[23] = -state[6];
   out_360848949412854679[24] = -state[5];
   out_360848949412854679[25] = 0;
   out_360848949412854679[26] = state[3];
   out_360848949412854679[27] = 0;
   out_360848949412854679[28] = 0;
   out_360848949412854679[29] = 0;
   out_360848949412854679[30] = 0;
   out_360848949412854679[31] = 1;
   out_360848949412854679[32] = 0;
   out_360848949412854679[33] = 0;
   out_360848949412854679[34] = 1;
   out_360848949412854679[35] = 0;
   out_360848949412854679[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_360848949412854679[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_360848949412854679[38] = 0;
   out_360848949412854679[39] = -state[7];
   out_360848949412854679[40] = state[6];
   out_360848949412854679[41] = 0;
   out_360848949412854679[42] = state[4];
   out_360848949412854679[43] = -state[3];
   out_360848949412854679[44] = 0;
   out_360848949412854679[45] = 0;
   out_360848949412854679[46] = 0;
   out_360848949412854679[47] = 0;
   out_360848949412854679[48] = 0;
   out_360848949412854679[49] = 0;
   out_360848949412854679[50] = 1;
   out_360848949412854679[51] = 0;
   out_360848949412854679[52] = 0;
   out_360848949412854679[53] = 1;
}
void h_13(double *state, double *unused, double *out_7295945181203287929) {
   out_7295945181203287929[0] = state[3];
   out_7295945181203287929[1] = state[4];
   out_7295945181203287929[2] = state[5];
}
void H_13(double *state, double *unused, double *out_7111646663026819757) {
   out_7111646663026819757[0] = 0;
   out_7111646663026819757[1] = 0;
   out_7111646663026819757[2] = 0;
   out_7111646663026819757[3] = 1;
   out_7111646663026819757[4] = 0;
   out_7111646663026819757[5] = 0;
   out_7111646663026819757[6] = 0;
   out_7111646663026819757[7] = 0;
   out_7111646663026819757[8] = 0;
   out_7111646663026819757[9] = 0;
   out_7111646663026819757[10] = 0;
   out_7111646663026819757[11] = 0;
   out_7111646663026819757[12] = 0;
   out_7111646663026819757[13] = 0;
   out_7111646663026819757[14] = 0;
   out_7111646663026819757[15] = 0;
   out_7111646663026819757[16] = 0;
   out_7111646663026819757[17] = 0;
   out_7111646663026819757[18] = 0;
   out_7111646663026819757[19] = 0;
   out_7111646663026819757[20] = 0;
   out_7111646663026819757[21] = 0;
   out_7111646663026819757[22] = 1;
   out_7111646663026819757[23] = 0;
   out_7111646663026819757[24] = 0;
   out_7111646663026819757[25] = 0;
   out_7111646663026819757[26] = 0;
   out_7111646663026819757[27] = 0;
   out_7111646663026819757[28] = 0;
   out_7111646663026819757[29] = 0;
   out_7111646663026819757[30] = 0;
   out_7111646663026819757[31] = 0;
   out_7111646663026819757[32] = 0;
   out_7111646663026819757[33] = 0;
   out_7111646663026819757[34] = 0;
   out_7111646663026819757[35] = 0;
   out_7111646663026819757[36] = 0;
   out_7111646663026819757[37] = 0;
   out_7111646663026819757[38] = 0;
   out_7111646663026819757[39] = 0;
   out_7111646663026819757[40] = 0;
   out_7111646663026819757[41] = 1;
   out_7111646663026819757[42] = 0;
   out_7111646663026819757[43] = 0;
   out_7111646663026819757[44] = 0;
   out_7111646663026819757[45] = 0;
   out_7111646663026819757[46] = 0;
   out_7111646663026819757[47] = 0;
   out_7111646663026819757[48] = 0;
   out_7111646663026819757[49] = 0;
   out_7111646663026819757[50] = 0;
   out_7111646663026819757[51] = 0;
   out_7111646663026819757[52] = 0;
   out_7111646663026819757[53] = 0;
}
void h_14(double *state, double *unused, double *out_9068419937336893414) {
   out_9068419937336893414[0] = state[6];
   out_9068419937336893414[1] = state[7];
   out_9068419937336893414[2] = state[8];
}
void H_14(double *state, double *unused, double *out_6360679632019668029) {
   out_6360679632019668029[0] = 0;
   out_6360679632019668029[1] = 0;
   out_6360679632019668029[2] = 0;
   out_6360679632019668029[3] = 0;
   out_6360679632019668029[4] = 0;
   out_6360679632019668029[5] = 0;
   out_6360679632019668029[6] = 1;
   out_6360679632019668029[7] = 0;
   out_6360679632019668029[8] = 0;
   out_6360679632019668029[9] = 0;
   out_6360679632019668029[10] = 0;
   out_6360679632019668029[11] = 0;
   out_6360679632019668029[12] = 0;
   out_6360679632019668029[13] = 0;
   out_6360679632019668029[14] = 0;
   out_6360679632019668029[15] = 0;
   out_6360679632019668029[16] = 0;
   out_6360679632019668029[17] = 0;
   out_6360679632019668029[18] = 0;
   out_6360679632019668029[19] = 0;
   out_6360679632019668029[20] = 0;
   out_6360679632019668029[21] = 0;
   out_6360679632019668029[22] = 0;
   out_6360679632019668029[23] = 0;
   out_6360679632019668029[24] = 0;
   out_6360679632019668029[25] = 1;
   out_6360679632019668029[26] = 0;
   out_6360679632019668029[27] = 0;
   out_6360679632019668029[28] = 0;
   out_6360679632019668029[29] = 0;
   out_6360679632019668029[30] = 0;
   out_6360679632019668029[31] = 0;
   out_6360679632019668029[32] = 0;
   out_6360679632019668029[33] = 0;
   out_6360679632019668029[34] = 0;
   out_6360679632019668029[35] = 0;
   out_6360679632019668029[36] = 0;
   out_6360679632019668029[37] = 0;
   out_6360679632019668029[38] = 0;
   out_6360679632019668029[39] = 0;
   out_6360679632019668029[40] = 0;
   out_6360679632019668029[41] = 0;
   out_6360679632019668029[42] = 0;
   out_6360679632019668029[43] = 0;
   out_6360679632019668029[44] = 1;
   out_6360679632019668029[45] = 0;
   out_6360679632019668029[46] = 0;
   out_6360679632019668029[47] = 0;
   out_6360679632019668029[48] = 0;
   out_6360679632019668029[49] = 0;
   out_6360679632019668029[50] = 0;
   out_6360679632019668029[51] = 0;
   out_6360679632019668029[52] = 0;
   out_6360679632019668029[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_7950841656255825399) {
  err_fun(nom_x, delta_x, out_7950841656255825399);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1038560697701516954) {
  inv_err_fun(nom_x, true_x, out_1038560697701516954);
}
void pose_H_mod_fun(double *state, double *out_7368662583295686451) {
  H_mod_fun(state, out_7368662583295686451);
}
void pose_f_fun(double *state, double dt, double *out_7152923552696196830) {
  f_fun(state,  dt, out_7152923552696196830);
}
void pose_F_fun(double *state, double dt, double *out_1783079396843657897) {
  F_fun(state,  dt, out_1783079396843657897);
}
void pose_h_4(double *state, double *unused, double *out_7141288839189123597) {
  h_4(state, unused, out_7141288839189123597);
}
void pose_H_4(double *state, double *unused, double *out_8122823585350399058) {
  H_4(state, unused, out_8122823585350399058);
}
void pose_h_10(double *state, double *unused, double *out_2925053845163599483) {
  h_10(state, unused, out_2925053845163599483);
}
void pose_H_10(double *state, double *unused, double *out_360848949412854679) {
  H_10(state, unused, out_360848949412854679);
}
void pose_h_13(double *state, double *unused, double *out_7295945181203287929) {
  h_13(state, unused, out_7295945181203287929);
}
void pose_H_13(double *state, double *unused, double *out_7111646663026819757) {
  H_13(state, unused, out_7111646663026819757);
}
void pose_h_14(double *state, double *unused, double *out_9068419937336893414) {
  h_14(state, unused, out_9068419937336893414);
}
void pose_H_14(double *state, double *unused, double *out_6360679632019668029) {
  H_14(state, unused, out_6360679632019668029);
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
