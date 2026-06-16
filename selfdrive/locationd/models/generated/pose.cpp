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
void err_fun(double *nom_x, double *delta_x, double *out_165995497420240335) {
   out_165995497420240335[0] = delta_x[0] + nom_x[0];
   out_165995497420240335[1] = delta_x[1] + nom_x[1];
   out_165995497420240335[2] = delta_x[2] + nom_x[2];
   out_165995497420240335[3] = delta_x[3] + nom_x[3];
   out_165995497420240335[4] = delta_x[4] + nom_x[4];
   out_165995497420240335[5] = delta_x[5] + nom_x[5];
   out_165995497420240335[6] = delta_x[6] + nom_x[6];
   out_165995497420240335[7] = delta_x[7] + nom_x[7];
   out_165995497420240335[8] = delta_x[8] + nom_x[8];
   out_165995497420240335[9] = delta_x[9] + nom_x[9];
   out_165995497420240335[10] = delta_x[10] + nom_x[10];
   out_165995497420240335[11] = delta_x[11] + nom_x[11];
   out_165995497420240335[12] = delta_x[12] + nom_x[12];
   out_165995497420240335[13] = delta_x[13] + nom_x[13];
   out_165995497420240335[14] = delta_x[14] + nom_x[14];
   out_165995497420240335[15] = delta_x[15] + nom_x[15];
   out_165995497420240335[16] = delta_x[16] + nom_x[16];
   out_165995497420240335[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_2659251340504186577) {
   out_2659251340504186577[0] = -nom_x[0] + true_x[0];
   out_2659251340504186577[1] = -nom_x[1] + true_x[1];
   out_2659251340504186577[2] = -nom_x[2] + true_x[2];
   out_2659251340504186577[3] = -nom_x[3] + true_x[3];
   out_2659251340504186577[4] = -nom_x[4] + true_x[4];
   out_2659251340504186577[5] = -nom_x[5] + true_x[5];
   out_2659251340504186577[6] = -nom_x[6] + true_x[6];
   out_2659251340504186577[7] = -nom_x[7] + true_x[7];
   out_2659251340504186577[8] = -nom_x[8] + true_x[8];
   out_2659251340504186577[9] = -nom_x[9] + true_x[9];
   out_2659251340504186577[10] = -nom_x[10] + true_x[10];
   out_2659251340504186577[11] = -nom_x[11] + true_x[11];
   out_2659251340504186577[12] = -nom_x[12] + true_x[12];
   out_2659251340504186577[13] = -nom_x[13] + true_x[13];
   out_2659251340504186577[14] = -nom_x[14] + true_x[14];
   out_2659251340504186577[15] = -nom_x[15] + true_x[15];
   out_2659251340504186577[16] = -nom_x[16] + true_x[16];
   out_2659251340504186577[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_2311774637070926029) {
   out_2311774637070926029[0] = 1.0;
   out_2311774637070926029[1] = 0.0;
   out_2311774637070926029[2] = 0.0;
   out_2311774637070926029[3] = 0.0;
   out_2311774637070926029[4] = 0.0;
   out_2311774637070926029[5] = 0.0;
   out_2311774637070926029[6] = 0.0;
   out_2311774637070926029[7] = 0.0;
   out_2311774637070926029[8] = 0.0;
   out_2311774637070926029[9] = 0.0;
   out_2311774637070926029[10] = 0.0;
   out_2311774637070926029[11] = 0.0;
   out_2311774637070926029[12] = 0.0;
   out_2311774637070926029[13] = 0.0;
   out_2311774637070926029[14] = 0.0;
   out_2311774637070926029[15] = 0.0;
   out_2311774637070926029[16] = 0.0;
   out_2311774637070926029[17] = 0.0;
   out_2311774637070926029[18] = 0.0;
   out_2311774637070926029[19] = 1.0;
   out_2311774637070926029[20] = 0.0;
   out_2311774637070926029[21] = 0.0;
   out_2311774637070926029[22] = 0.0;
   out_2311774637070926029[23] = 0.0;
   out_2311774637070926029[24] = 0.0;
   out_2311774637070926029[25] = 0.0;
   out_2311774637070926029[26] = 0.0;
   out_2311774637070926029[27] = 0.0;
   out_2311774637070926029[28] = 0.0;
   out_2311774637070926029[29] = 0.0;
   out_2311774637070926029[30] = 0.0;
   out_2311774637070926029[31] = 0.0;
   out_2311774637070926029[32] = 0.0;
   out_2311774637070926029[33] = 0.0;
   out_2311774637070926029[34] = 0.0;
   out_2311774637070926029[35] = 0.0;
   out_2311774637070926029[36] = 0.0;
   out_2311774637070926029[37] = 0.0;
   out_2311774637070926029[38] = 1.0;
   out_2311774637070926029[39] = 0.0;
   out_2311774637070926029[40] = 0.0;
   out_2311774637070926029[41] = 0.0;
   out_2311774637070926029[42] = 0.0;
   out_2311774637070926029[43] = 0.0;
   out_2311774637070926029[44] = 0.0;
   out_2311774637070926029[45] = 0.0;
   out_2311774637070926029[46] = 0.0;
   out_2311774637070926029[47] = 0.0;
   out_2311774637070926029[48] = 0.0;
   out_2311774637070926029[49] = 0.0;
   out_2311774637070926029[50] = 0.0;
   out_2311774637070926029[51] = 0.0;
   out_2311774637070926029[52] = 0.0;
   out_2311774637070926029[53] = 0.0;
   out_2311774637070926029[54] = 0.0;
   out_2311774637070926029[55] = 0.0;
   out_2311774637070926029[56] = 0.0;
   out_2311774637070926029[57] = 1.0;
   out_2311774637070926029[58] = 0.0;
   out_2311774637070926029[59] = 0.0;
   out_2311774637070926029[60] = 0.0;
   out_2311774637070926029[61] = 0.0;
   out_2311774637070926029[62] = 0.0;
   out_2311774637070926029[63] = 0.0;
   out_2311774637070926029[64] = 0.0;
   out_2311774637070926029[65] = 0.0;
   out_2311774637070926029[66] = 0.0;
   out_2311774637070926029[67] = 0.0;
   out_2311774637070926029[68] = 0.0;
   out_2311774637070926029[69] = 0.0;
   out_2311774637070926029[70] = 0.0;
   out_2311774637070926029[71] = 0.0;
   out_2311774637070926029[72] = 0.0;
   out_2311774637070926029[73] = 0.0;
   out_2311774637070926029[74] = 0.0;
   out_2311774637070926029[75] = 0.0;
   out_2311774637070926029[76] = 1.0;
   out_2311774637070926029[77] = 0.0;
   out_2311774637070926029[78] = 0.0;
   out_2311774637070926029[79] = 0.0;
   out_2311774637070926029[80] = 0.0;
   out_2311774637070926029[81] = 0.0;
   out_2311774637070926029[82] = 0.0;
   out_2311774637070926029[83] = 0.0;
   out_2311774637070926029[84] = 0.0;
   out_2311774637070926029[85] = 0.0;
   out_2311774637070926029[86] = 0.0;
   out_2311774637070926029[87] = 0.0;
   out_2311774637070926029[88] = 0.0;
   out_2311774637070926029[89] = 0.0;
   out_2311774637070926029[90] = 0.0;
   out_2311774637070926029[91] = 0.0;
   out_2311774637070926029[92] = 0.0;
   out_2311774637070926029[93] = 0.0;
   out_2311774637070926029[94] = 0.0;
   out_2311774637070926029[95] = 1.0;
   out_2311774637070926029[96] = 0.0;
   out_2311774637070926029[97] = 0.0;
   out_2311774637070926029[98] = 0.0;
   out_2311774637070926029[99] = 0.0;
   out_2311774637070926029[100] = 0.0;
   out_2311774637070926029[101] = 0.0;
   out_2311774637070926029[102] = 0.0;
   out_2311774637070926029[103] = 0.0;
   out_2311774637070926029[104] = 0.0;
   out_2311774637070926029[105] = 0.0;
   out_2311774637070926029[106] = 0.0;
   out_2311774637070926029[107] = 0.0;
   out_2311774637070926029[108] = 0.0;
   out_2311774637070926029[109] = 0.0;
   out_2311774637070926029[110] = 0.0;
   out_2311774637070926029[111] = 0.0;
   out_2311774637070926029[112] = 0.0;
   out_2311774637070926029[113] = 0.0;
   out_2311774637070926029[114] = 1.0;
   out_2311774637070926029[115] = 0.0;
   out_2311774637070926029[116] = 0.0;
   out_2311774637070926029[117] = 0.0;
   out_2311774637070926029[118] = 0.0;
   out_2311774637070926029[119] = 0.0;
   out_2311774637070926029[120] = 0.0;
   out_2311774637070926029[121] = 0.0;
   out_2311774637070926029[122] = 0.0;
   out_2311774637070926029[123] = 0.0;
   out_2311774637070926029[124] = 0.0;
   out_2311774637070926029[125] = 0.0;
   out_2311774637070926029[126] = 0.0;
   out_2311774637070926029[127] = 0.0;
   out_2311774637070926029[128] = 0.0;
   out_2311774637070926029[129] = 0.0;
   out_2311774637070926029[130] = 0.0;
   out_2311774637070926029[131] = 0.0;
   out_2311774637070926029[132] = 0.0;
   out_2311774637070926029[133] = 1.0;
   out_2311774637070926029[134] = 0.0;
   out_2311774637070926029[135] = 0.0;
   out_2311774637070926029[136] = 0.0;
   out_2311774637070926029[137] = 0.0;
   out_2311774637070926029[138] = 0.0;
   out_2311774637070926029[139] = 0.0;
   out_2311774637070926029[140] = 0.0;
   out_2311774637070926029[141] = 0.0;
   out_2311774637070926029[142] = 0.0;
   out_2311774637070926029[143] = 0.0;
   out_2311774637070926029[144] = 0.0;
   out_2311774637070926029[145] = 0.0;
   out_2311774637070926029[146] = 0.0;
   out_2311774637070926029[147] = 0.0;
   out_2311774637070926029[148] = 0.0;
   out_2311774637070926029[149] = 0.0;
   out_2311774637070926029[150] = 0.0;
   out_2311774637070926029[151] = 0.0;
   out_2311774637070926029[152] = 1.0;
   out_2311774637070926029[153] = 0.0;
   out_2311774637070926029[154] = 0.0;
   out_2311774637070926029[155] = 0.0;
   out_2311774637070926029[156] = 0.0;
   out_2311774637070926029[157] = 0.0;
   out_2311774637070926029[158] = 0.0;
   out_2311774637070926029[159] = 0.0;
   out_2311774637070926029[160] = 0.0;
   out_2311774637070926029[161] = 0.0;
   out_2311774637070926029[162] = 0.0;
   out_2311774637070926029[163] = 0.0;
   out_2311774637070926029[164] = 0.0;
   out_2311774637070926029[165] = 0.0;
   out_2311774637070926029[166] = 0.0;
   out_2311774637070926029[167] = 0.0;
   out_2311774637070926029[168] = 0.0;
   out_2311774637070926029[169] = 0.0;
   out_2311774637070926029[170] = 0.0;
   out_2311774637070926029[171] = 1.0;
   out_2311774637070926029[172] = 0.0;
   out_2311774637070926029[173] = 0.0;
   out_2311774637070926029[174] = 0.0;
   out_2311774637070926029[175] = 0.0;
   out_2311774637070926029[176] = 0.0;
   out_2311774637070926029[177] = 0.0;
   out_2311774637070926029[178] = 0.0;
   out_2311774637070926029[179] = 0.0;
   out_2311774637070926029[180] = 0.0;
   out_2311774637070926029[181] = 0.0;
   out_2311774637070926029[182] = 0.0;
   out_2311774637070926029[183] = 0.0;
   out_2311774637070926029[184] = 0.0;
   out_2311774637070926029[185] = 0.0;
   out_2311774637070926029[186] = 0.0;
   out_2311774637070926029[187] = 0.0;
   out_2311774637070926029[188] = 0.0;
   out_2311774637070926029[189] = 0.0;
   out_2311774637070926029[190] = 1.0;
   out_2311774637070926029[191] = 0.0;
   out_2311774637070926029[192] = 0.0;
   out_2311774637070926029[193] = 0.0;
   out_2311774637070926029[194] = 0.0;
   out_2311774637070926029[195] = 0.0;
   out_2311774637070926029[196] = 0.0;
   out_2311774637070926029[197] = 0.0;
   out_2311774637070926029[198] = 0.0;
   out_2311774637070926029[199] = 0.0;
   out_2311774637070926029[200] = 0.0;
   out_2311774637070926029[201] = 0.0;
   out_2311774637070926029[202] = 0.0;
   out_2311774637070926029[203] = 0.0;
   out_2311774637070926029[204] = 0.0;
   out_2311774637070926029[205] = 0.0;
   out_2311774637070926029[206] = 0.0;
   out_2311774637070926029[207] = 0.0;
   out_2311774637070926029[208] = 0.0;
   out_2311774637070926029[209] = 1.0;
   out_2311774637070926029[210] = 0.0;
   out_2311774637070926029[211] = 0.0;
   out_2311774637070926029[212] = 0.0;
   out_2311774637070926029[213] = 0.0;
   out_2311774637070926029[214] = 0.0;
   out_2311774637070926029[215] = 0.0;
   out_2311774637070926029[216] = 0.0;
   out_2311774637070926029[217] = 0.0;
   out_2311774637070926029[218] = 0.0;
   out_2311774637070926029[219] = 0.0;
   out_2311774637070926029[220] = 0.0;
   out_2311774637070926029[221] = 0.0;
   out_2311774637070926029[222] = 0.0;
   out_2311774637070926029[223] = 0.0;
   out_2311774637070926029[224] = 0.0;
   out_2311774637070926029[225] = 0.0;
   out_2311774637070926029[226] = 0.0;
   out_2311774637070926029[227] = 0.0;
   out_2311774637070926029[228] = 1.0;
   out_2311774637070926029[229] = 0.0;
   out_2311774637070926029[230] = 0.0;
   out_2311774637070926029[231] = 0.0;
   out_2311774637070926029[232] = 0.0;
   out_2311774637070926029[233] = 0.0;
   out_2311774637070926029[234] = 0.0;
   out_2311774637070926029[235] = 0.0;
   out_2311774637070926029[236] = 0.0;
   out_2311774637070926029[237] = 0.0;
   out_2311774637070926029[238] = 0.0;
   out_2311774637070926029[239] = 0.0;
   out_2311774637070926029[240] = 0.0;
   out_2311774637070926029[241] = 0.0;
   out_2311774637070926029[242] = 0.0;
   out_2311774637070926029[243] = 0.0;
   out_2311774637070926029[244] = 0.0;
   out_2311774637070926029[245] = 0.0;
   out_2311774637070926029[246] = 0.0;
   out_2311774637070926029[247] = 1.0;
   out_2311774637070926029[248] = 0.0;
   out_2311774637070926029[249] = 0.0;
   out_2311774637070926029[250] = 0.0;
   out_2311774637070926029[251] = 0.0;
   out_2311774637070926029[252] = 0.0;
   out_2311774637070926029[253] = 0.0;
   out_2311774637070926029[254] = 0.0;
   out_2311774637070926029[255] = 0.0;
   out_2311774637070926029[256] = 0.0;
   out_2311774637070926029[257] = 0.0;
   out_2311774637070926029[258] = 0.0;
   out_2311774637070926029[259] = 0.0;
   out_2311774637070926029[260] = 0.0;
   out_2311774637070926029[261] = 0.0;
   out_2311774637070926029[262] = 0.0;
   out_2311774637070926029[263] = 0.0;
   out_2311774637070926029[264] = 0.0;
   out_2311774637070926029[265] = 0.0;
   out_2311774637070926029[266] = 1.0;
   out_2311774637070926029[267] = 0.0;
   out_2311774637070926029[268] = 0.0;
   out_2311774637070926029[269] = 0.0;
   out_2311774637070926029[270] = 0.0;
   out_2311774637070926029[271] = 0.0;
   out_2311774637070926029[272] = 0.0;
   out_2311774637070926029[273] = 0.0;
   out_2311774637070926029[274] = 0.0;
   out_2311774637070926029[275] = 0.0;
   out_2311774637070926029[276] = 0.0;
   out_2311774637070926029[277] = 0.0;
   out_2311774637070926029[278] = 0.0;
   out_2311774637070926029[279] = 0.0;
   out_2311774637070926029[280] = 0.0;
   out_2311774637070926029[281] = 0.0;
   out_2311774637070926029[282] = 0.0;
   out_2311774637070926029[283] = 0.0;
   out_2311774637070926029[284] = 0.0;
   out_2311774637070926029[285] = 1.0;
   out_2311774637070926029[286] = 0.0;
   out_2311774637070926029[287] = 0.0;
   out_2311774637070926029[288] = 0.0;
   out_2311774637070926029[289] = 0.0;
   out_2311774637070926029[290] = 0.0;
   out_2311774637070926029[291] = 0.0;
   out_2311774637070926029[292] = 0.0;
   out_2311774637070926029[293] = 0.0;
   out_2311774637070926029[294] = 0.0;
   out_2311774637070926029[295] = 0.0;
   out_2311774637070926029[296] = 0.0;
   out_2311774637070926029[297] = 0.0;
   out_2311774637070926029[298] = 0.0;
   out_2311774637070926029[299] = 0.0;
   out_2311774637070926029[300] = 0.0;
   out_2311774637070926029[301] = 0.0;
   out_2311774637070926029[302] = 0.0;
   out_2311774637070926029[303] = 0.0;
   out_2311774637070926029[304] = 1.0;
   out_2311774637070926029[305] = 0.0;
   out_2311774637070926029[306] = 0.0;
   out_2311774637070926029[307] = 0.0;
   out_2311774637070926029[308] = 0.0;
   out_2311774637070926029[309] = 0.0;
   out_2311774637070926029[310] = 0.0;
   out_2311774637070926029[311] = 0.0;
   out_2311774637070926029[312] = 0.0;
   out_2311774637070926029[313] = 0.0;
   out_2311774637070926029[314] = 0.0;
   out_2311774637070926029[315] = 0.0;
   out_2311774637070926029[316] = 0.0;
   out_2311774637070926029[317] = 0.0;
   out_2311774637070926029[318] = 0.0;
   out_2311774637070926029[319] = 0.0;
   out_2311774637070926029[320] = 0.0;
   out_2311774637070926029[321] = 0.0;
   out_2311774637070926029[322] = 0.0;
   out_2311774637070926029[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_7546479248053883876) {
   out_7546479248053883876[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_7546479248053883876[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_7546479248053883876[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_7546479248053883876[3] = dt*state[12] + state[3];
   out_7546479248053883876[4] = dt*state[13] + state[4];
   out_7546479248053883876[5] = dt*state[14] + state[5];
   out_7546479248053883876[6] = state[6];
   out_7546479248053883876[7] = state[7];
   out_7546479248053883876[8] = state[8];
   out_7546479248053883876[9] = state[9];
   out_7546479248053883876[10] = state[10];
   out_7546479248053883876[11] = state[11];
   out_7546479248053883876[12] = state[12];
   out_7546479248053883876[13] = state[13];
   out_7546479248053883876[14] = state[14];
   out_7546479248053883876[15] = state[15];
   out_7546479248053883876[16] = state[16];
   out_7546479248053883876[17] = state[17];
}
void F_fun(double *state, double dt, double *out_7580047345257263534) {
   out_7580047345257263534[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7580047345257263534[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7580047345257263534[2] = 0;
   out_7580047345257263534[3] = 0;
   out_7580047345257263534[4] = 0;
   out_7580047345257263534[5] = 0;
   out_7580047345257263534[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7580047345257263534[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7580047345257263534[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7580047345257263534[9] = 0;
   out_7580047345257263534[10] = 0;
   out_7580047345257263534[11] = 0;
   out_7580047345257263534[12] = 0;
   out_7580047345257263534[13] = 0;
   out_7580047345257263534[14] = 0;
   out_7580047345257263534[15] = 0;
   out_7580047345257263534[16] = 0;
   out_7580047345257263534[17] = 0;
   out_7580047345257263534[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7580047345257263534[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7580047345257263534[20] = 0;
   out_7580047345257263534[21] = 0;
   out_7580047345257263534[22] = 0;
   out_7580047345257263534[23] = 0;
   out_7580047345257263534[24] = 0;
   out_7580047345257263534[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7580047345257263534[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7580047345257263534[27] = 0;
   out_7580047345257263534[28] = 0;
   out_7580047345257263534[29] = 0;
   out_7580047345257263534[30] = 0;
   out_7580047345257263534[31] = 0;
   out_7580047345257263534[32] = 0;
   out_7580047345257263534[33] = 0;
   out_7580047345257263534[34] = 0;
   out_7580047345257263534[35] = 0;
   out_7580047345257263534[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7580047345257263534[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7580047345257263534[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7580047345257263534[39] = 0;
   out_7580047345257263534[40] = 0;
   out_7580047345257263534[41] = 0;
   out_7580047345257263534[42] = 0;
   out_7580047345257263534[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7580047345257263534[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7580047345257263534[45] = 0;
   out_7580047345257263534[46] = 0;
   out_7580047345257263534[47] = 0;
   out_7580047345257263534[48] = 0;
   out_7580047345257263534[49] = 0;
   out_7580047345257263534[50] = 0;
   out_7580047345257263534[51] = 0;
   out_7580047345257263534[52] = 0;
   out_7580047345257263534[53] = 0;
   out_7580047345257263534[54] = 0;
   out_7580047345257263534[55] = 0;
   out_7580047345257263534[56] = 0;
   out_7580047345257263534[57] = 1;
   out_7580047345257263534[58] = 0;
   out_7580047345257263534[59] = 0;
   out_7580047345257263534[60] = 0;
   out_7580047345257263534[61] = 0;
   out_7580047345257263534[62] = 0;
   out_7580047345257263534[63] = 0;
   out_7580047345257263534[64] = 0;
   out_7580047345257263534[65] = 0;
   out_7580047345257263534[66] = dt;
   out_7580047345257263534[67] = 0;
   out_7580047345257263534[68] = 0;
   out_7580047345257263534[69] = 0;
   out_7580047345257263534[70] = 0;
   out_7580047345257263534[71] = 0;
   out_7580047345257263534[72] = 0;
   out_7580047345257263534[73] = 0;
   out_7580047345257263534[74] = 0;
   out_7580047345257263534[75] = 0;
   out_7580047345257263534[76] = 1;
   out_7580047345257263534[77] = 0;
   out_7580047345257263534[78] = 0;
   out_7580047345257263534[79] = 0;
   out_7580047345257263534[80] = 0;
   out_7580047345257263534[81] = 0;
   out_7580047345257263534[82] = 0;
   out_7580047345257263534[83] = 0;
   out_7580047345257263534[84] = 0;
   out_7580047345257263534[85] = dt;
   out_7580047345257263534[86] = 0;
   out_7580047345257263534[87] = 0;
   out_7580047345257263534[88] = 0;
   out_7580047345257263534[89] = 0;
   out_7580047345257263534[90] = 0;
   out_7580047345257263534[91] = 0;
   out_7580047345257263534[92] = 0;
   out_7580047345257263534[93] = 0;
   out_7580047345257263534[94] = 0;
   out_7580047345257263534[95] = 1;
   out_7580047345257263534[96] = 0;
   out_7580047345257263534[97] = 0;
   out_7580047345257263534[98] = 0;
   out_7580047345257263534[99] = 0;
   out_7580047345257263534[100] = 0;
   out_7580047345257263534[101] = 0;
   out_7580047345257263534[102] = 0;
   out_7580047345257263534[103] = 0;
   out_7580047345257263534[104] = dt;
   out_7580047345257263534[105] = 0;
   out_7580047345257263534[106] = 0;
   out_7580047345257263534[107] = 0;
   out_7580047345257263534[108] = 0;
   out_7580047345257263534[109] = 0;
   out_7580047345257263534[110] = 0;
   out_7580047345257263534[111] = 0;
   out_7580047345257263534[112] = 0;
   out_7580047345257263534[113] = 0;
   out_7580047345257263534[114] = 1;
   out_7580047345257263534[115] = 0;
   out_7580047345257263534[116] = 0;
   out_7580047345257263534[117] = 0;
   out_7580047345257263534[118] = 0;
   out_7580047345257263534[119] = 0;
   out_7580047345257263534[120] = 0;
   out_7580047345257263534[121] = 0;
   out_7580047345257263534[122] = 0;
   out_7580047345257263534[123] = 0;
   out_7580047345257263534[124] = 0;
   out_7580047345257263534[125] = 0;
   out_7580047345257263534[126] = 0;
   out_7580047345257263534[127] = 0;
   out_7580047345257263534[128] = 0;
   out_7580047345257263534[129] = 0;
   out_7580047345257263534[130] = 0;
   out_7580047345257263534[131] = 0;
   out_7580047345257263534[132] = 0;
   out_7580047345257263534[133] = 1;
   out_7580047345257263534[134] = 0;
   out_7580047345257263534[135] = 0;
   out_7580047345257263534[136] = 0;
   out_7580047345257263534[137] = 0;
   out_7580047345257263534[138] = 0;
   out_7580047345257263534[139] = 0;
   out_7580047345257263534[140] = 0;
   out_7580047345257263534[141] = 0;
   out_7580047345257263534[142] = 0;
   out_7580047345257263534[143] = 0;
   out_7580047345257263534[144] = 0;
   out_7580047345257263534[145] = 0;
   out_7580047345257263534[146] = 0;
   out_7580047345257263534[147] = 0;
   out_7580047345257263534[148] = 0;
   out_7580047345257263534[149] = 0;
   out_7580047345257263534[150] = 0;
   out_7580047345257263534[151] = 0;
   out_7580047345257263534[152] = 1;
   out_7580047345257263534[153] = 0;
   out_7580047345257263534[154] = 0;
   out_7580047345257263534[155] = 0;
   out_7580047345257263534[156] = 0;
   out_7580047345257263534[157] = 0;
   out_7580047345257263534[158] = 0;
   out_7580047345257263534[159] = 0;
   out_7580047345257263534[160] = 0;
   out_7580047345257263534[161] = 0;
   out_7580047345257263534[162] = 0;
   out_7580047345257263534[163] = 0;
   out_7580047345257263534[164] = 0;
   out_7580047345257263534[165] = 0;
   out_7580047345257263534[166] = 0;
   out_7580047345257263534[167] = 0;
   out_7580047345257263534[168] = 0;
   out_7580047345257263534[169] = 0;
   out_7580047345257263534[170] = 0;
   out_7580047345257263534[171] = 1;
   out_7580047345257263534[172] = 0;
   out_7580047345257263534[173] = 0;
   out_7580047345257263534[174] = 0;
   out_7580047345257263534[175] = 0;
   out_7580047345257263534[176] = 0;
   out_7580047345257263534[177] = 0;
   out_7580047345257263534[178] = 0;
   out_7580047345257263534[179] = 0;
   out_7580047345257263534[180] = 0;
   out_7580047345257263534[181] = 0;
   out_7580047345257263534[182] = 0;
   out_7580047345257263534[183] = 0;
   out_7580047345257263534[184] = 0;
   out_7580047345257263534[185] = 0;
   out_7580047345257263534[186] = 0;
   out_7580047345257263534[187] = 0;
   out_7580047345257263534[188] = 0;
   out_7580047345257263534[189] = 0;
   out_7580047345257263534[190] = 1;
   out_7580047345257263534[191] = 0;
   out_7580047345257263534[192] = 0;
   out_7580047345257263534[193] = 0;
   out_7580047345257263534[194] = 0;
   out_7580047345257263534[195] = 0;
   out_7580047345257263534[196] = 0;
   out_7580047345257263534[197] = 0;
   out_7580047345257263534[198] = 0;
   out_7580047345257263534[199] = 0;
   out_7580047345257263534[200] = 0;
   out_7580047345257263534[201] = 0;
   out_7580047345257263534[202] = 0;
   out_7580047345257263534[203] = 0;
   out_7580047345257263534[204] = 0;
   out_7580047345257263534[205] = 0;
   out_7580047345257263534[206] = 0;
   out_7580047345257263534[207] = 0;
   out_7580047345257263534[208] = 0;
   out_7580047345257263534[209] = 1;
   out_7580047345257263534[210] = 0;
   out_7580047345257263534[211] = 0;
   out_7580047345257263534[212] = 0;
   out_7580047345257263534[213] = 0;
   out_7580047345257263534[214] = 0;
   out_7580047345257263534[215] = 0;
   out_7580047345257263534[216] = 0;
   out_7580047345257263534[217] = 0;
   out_7580047345257263534[218] = 0;
   out_7580047345257263534[219] = 0;
   out_7580047345257263534[220] = 0;
   out_7580047345257263534[221] = 0;
   out_7580047345257263534[222] = 0;
   out_7580047345257263534[223] = 0;
   out_7580047345257263534[224] = 0;
   out_7580047345257263534[225] = 0;
   out_7580047345257263534[226] = 0;
   out_7580047345257263534[227] = 0;
   out_7580047345257263534[228] = 1;
   out_7580047345257263534[229] = 0;
   out_7580047345257263534[230] = 0;
   out_7580047345257263534[231] = 0;
   out_7580047345257263534[232] = 0;
   out_7580047345257263534[233] = 0;
   out_7580047345257263534[234] = 0;
   out_7580047345257263534[235] = 0;
   out_7580047345257263534[236] = 0;
   out_7580047345257263534[237] = 0;
   out_7580047345257263534[238] = 0;
   out_7580047345257263534[239] = 0;
   out_7580047345257263534[240] = 0;
   out_7580047345257263534[241] = 0;
   out_7580047345257263534[242] = 0;
   out_7580047345257263534[243] = 0;
   out_7580047345257263534[244] = 0;
   out_7580047345257263534[245] = 0;
   out_7580047345257263534[246] = 0;
   out_7580047345257263534[247] = 1;
   out_7580047345257263534[248] = 0;
   out_7580047345257263534[249] = 0;
   out_7580047345257263534[250] = 0;
   out_7580047345257263534[251] = 0;
   out_7580047345257263534[252] = 0;
   out_7580047345257263534[253] = 0;
   out_7580047345257263534[254] = 0;
   out_7580047345257263534[255] = 0;
   out_7580047345257263534[256] = 0;
   out_7580047345257263534[257] = 0;
   out_7580047345257263534[258] = 0;
   out_7580047345257263534[259] = 0;
   out_7580047345257263534[260] = 0;
   out_7580047345257263534[261] = 0;
   out_7580047345257263534[262] = 0;
   out_7580047345257263534[263] = 0;
   out_7580047345257263534[264] = 0;
   out_7580047345257263534[265] = 0;
   out_7580047345257263534[266] = 1;
   out_7580047345257263534[267] = 0;
   out_7580047345257263534[268] = 0;
   out_7580047345257263534[269] = 0;
   out_7580047345257263534[270] = 0;
   out_7580047345257263534[271] = 0;
   out_7580047345257263534[272] = 0;
   out_7580047345257263534[273] = 0;
   out_7580047345257263534[274] = 0;
   out_7580047345257263534[275] = 0;
   out_7580047345257263534[276] = 0;
   out_7580047345257263534[277] = 0;
   out_7580047345257263534[278] = 0;
   out_7580047345257263534[279] = 0;
   out_7580047345257263534[280] = 0;
   out_7580047345257263534[281] = 0;
   out_7580047345257263534[282] = 0;
   out_7580047345257263534[283] = 0;
   out_7580047345257263534[284] = 0;
   out_7580047345257263534[285] = 1;
   out_7580047345257263534[286] = 0;
   out_7580047345257263534[287] = 0;
   out_7580047345257263534[288] = 0;
   out_7580047345257263534[289] = 0;
   out_7580047345257263534[290] = 0;
   out_7580047345257263534[291] = 0;
   out_7580047345257263534[292] = 0;
   out_7580047345257263534[293] = 0;
   out_7580047345257263534[294] = 0;
   out_7580047345257263534[295] = 0;
   out_7580047345257263534[296] = 0;
   out_7580047345257263534[297] = 0;
   out_7580047345257263534[298] = 0;
   out_7580047345257263534[299] = 0;
   out_7580047345257263534[300] = 0;
   out_7580047345257263534[301] = 0;
   out_7580047345257263534[302] = 0;
   out_7580047345257263534[303] = 0;
   out_7580047345257263534[304] = 1;
   out_7580047345257263534[305] = 0;
   out_7580047345257263534[306] = 0;
   out_7580047345257263534[307] = 0;
   out_7580047345257263534[308] = 0;
   out_7580047345257263534[309] = 0;
   out_7580047345257263534[310] = 0;
   out_7580047345257263534[311] = 0;
   out_7580047345257263534[312] = 0;
   out_7580047345257263534[313] = 0;
   out_7580047345257263534[314] = 0;
   out_7580047345257263534[315] = 0;
   out_7580047345257263534[316] = 0;
   out_7580047345257263534[317] = 0;
   out_7580047345257263534[318] = 0;
   out_7580047345257263534[319] = 0;
   out_7580047345257263534[320] = 0;
   out_7580047345257263534[321] = 0;
   out_7580047345257263534[322] = 0;
   out_7580047345257263534[323] = 1;
}
void h_4(double *state, double *unused, double *out_2020815176821902235) {
   out_2020815176821902235[0] = state[6] + state[9];
   out_2020815176821902235[1] = state[7] + state[10];
   out_2020815176821902235[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_6632587028986895313) {
   out_6632587028986895313[0] = 0;
   out_6632587028986895313[1] = 0;
   out_6632587028986895313[2] = 0;
   out_6632587028986895313[3] = 0;
   out_6632587028986895313[4] = 0;
   out_6632587028986895313[5] = 0;
   out_6632587028986895313[6] = 1;
   out_6632587028986895313[7] = 0;
   out_6632587028986895313[8] = 0;
   out_6632587028986895313[9] = 1;
   out_6632587028986895313[10] = 0;
   out_6632587028986895313[11] = 0;
   out_6632587028986895313[12] = 0;
   out_6632587028986895313[13] = 0;
   out_6632587028986895313[14] = 0;
   out_6632587028986895313[15] = 0;
   out_6632587028986895313[16] = 0;
   out_6632587028986895313[17] = 0;
   out_6632587028986895313[18] = 0;
   out_6632587028986895313[19] = 0;
   out_6632587028986895313[20] = 0;
   out_6632587028986895313[21] = 0;
   out_6632587028986895313[22] = 0;
   out_6632587028986895313[23] = 0;
   out_6632587028986895313[24] = 0;
   out_6632587028986895313[25] = 1;
   out_6632587028986895313[26] = 0;
   out_6632587028986895313[27] = 0;
   out_6632587028986895313[28] = 1;
   out_6632587028986895313[29] = 0;
   out_6632587028986895313[30] = 0;
   out_6632587028986895313[31] = 0;
   out_6632587028986895313[32] = 0;
   out_6632587028986895313[33] = 0;
   out_6632587028986895313[34] = 0;
   out_6632587028986895313[35] = 0;
   out_6632587028986895313[36] = 0;
   out_6632587028986895313[37] = 0;
   out_6632587028986895313[38] = 0;
   out_6632587028986895313[39] = 0;
   out_6632587028986895313[40] = 0;
   out_6632587028986895313[41] = 0;
   out_6632587028986895313[42] = 0;
   out_6632587028986895313[43] = 0;
   out_6632587028986895313[44] = 1;
   out_6632587028986895313[45] = 0;
   out_6632587028986895313[46] = 0;
   out_6632587028986895313[47] = 1;
   out_6632587028986895313[48] = 0;
   out_6632587028986895313[49] = 0;
   out_6632587028986895313[50] = 0;
   out_6632587028986895313[51] = 0;
   out_6632587028986895313[52] = 0;
   out_6632587028986895313[53] = 0;
}
void h_10(double *state, double *unused, double *out_5957214524665520889) {
   out_5957214524665520889[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_5957214524665520889[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_5957214524665520889[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_3029068608548230730) {
   out_3029068608548230730[0] = 0;
   out_3029068608548230730[1] = 9.8100000000000005*cos(state[1]);
   out_3029068608548230730[2] = 0;
   out_3029068608548230730[3] = 0;
   out_3029068608548230730[4] = -state[8];
   out_3029068608548230730[5] = state[7];
   out_3029068608548230730[6] = 0;
   out_3029068608548230730[7] = state[5];
   out_3029068608548230730[8] = -state[4];
   out_3029068608548230730[9] = 0;
   out_3029068608548230730[10] = 0;
   out_3029068608548230730[11] = 0;
   out_3029068608548230730[12] = 1;
   out_3029068608548230730[13] = 0;
   out_3029068608548230730[14] = 0;
   out_3029068608548230730[15] = 1;
   out_3029068608548230730[16] = 0;
   out_3029068608548230730[17] = 0;
   out_3029068608548230730[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_3029068608548230730[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_3029068608548230730[20] = 0;
   out_3029068608548230730[21] = state[8];
   out_3029068608548230730[22] = 0;
   out_3029068608548230730[23] = -state[6];
   out_3029068608548230730[24] = -state[5];
   out_3029068608548230730[25] = 0;
   out_3029068608548230730[26] = state[3];
   out_3029068608548230730[27] = 0;
   out_3029068608548230730[28] = 0;
   out_3029068608548230730[29] = 0;
   out_3029068608548230730[30] = 0;
   out_3029068608548230730[31] = 1;
   out_3029068608548230730[32] = 0;
   out_3029068608548230730[33] = 0;
   out_3029068608548230730[34] = 1;
   out_3029068608548230730[35] = 0;
   out_3029068608548230730[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_3029068608548230730[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_3029068608548230730[38] = 0;
   out_3029068608548230730[39] = -state[7];
   out_3029068608548230730[40] = state[6];
   out_3029068608548230730[41] = 0;
   out_3029068608548230730[42] = state[4];
   out_3029068608548230730[43] = -state[3];
   out_3029068608548230730[44] = 0;
   out_3029068608548230730[45] = 0;
   out_3029068608548230730[46] = 0;
   out_3029068608548230730[47] = 0;
   out_3029068608548230730[48] = 0;
   out_3029068608548230730[49] = 0;
   out_3029068608548230730[50] = 1;
   out_3029068608548230730[51] = 0;
   out_3029068608548230730[52] = 0;
   out_3029068608548230730[53] = 1;
}
void h_13(double *state, double *unused, double *out_7047283842734815329) {
   out_7047283842734815329[0] = state[3];
   out_7047283842734815329[1] = state[4];
   out_7047283842734815329[2] = state[5];
}
void H_13(double *state, double *unused, double *out_3420313203654562512) {
   out_3420313203654562512[0] = 0;
   out_3420313203654562512[1] = 0;
   out_3420313203654562512[2] = 0;
   out_3420313203654562512[3] = 1;
   out_3420313203654562512[4] = 0;
   out_3420313203654562512[5] = 0;
   out_3420313203654562512[6] = 0;
   out_3420313203654562512[7] = 0;
   out_3420313203654562512[8] = 0;
   out_3420313203654562512[9] = 0;
   out_3420313203654562512[10] = 0;
   out_3420313203654562512[11] = 0;
   out_3420313203654562512[12] = 0;
   out_3420313203654562512[13] = 0;
   out_3420313203654562512[14] = 0;
   out_3420313203654562512[15] = 0;
   out_3420313203654562512[16] = 0;
   out_3420313203654562512[17] = 0;
   out_3420313203654562512[18] = 0;
   out_3420313203654562512[19] = 0;
   out_3420313203654562512[20] = 0;
   out_3420313203654562512[21] = 0;
   out_3420313203654562512[22] = 1;
   out_3420313203654562512[23] = 0;
   out_3420313203654562512[24] = 0;
   out_3420313203654562512[25] = 0;
   out_3420313203654562512[26] = 0;
   out_3420313203654562512[27] = 0;
   out_3420313203654562512[28] = 0;
   out_3420313203654562512[29] = 0;
   out_3420313203654562512[30] = 0;
   out_3420313203654562512[31] = 0;
   out_3420313203654562512[32] = 0;
   out_3420313203654562512[33] = 0;
   out_3420313203654562512[34] = 0;
   out_3420313203654562512[35] = 0;
   out_3420313203654562512[36] = 0;
   out_3420313203654562512[37] = 0;
   out_3420313203654562512[38] = 0;
   out_3420313203654562512[39] = 0;
   out_3420313203654562512[40] = 0;
   out_3420313203654562512[41] = 1;
   out_3420313203654562512[42] = 0;
   out_3420313203654562512[43] = 0;
   out_3420313203654562512[44] = 0;
   out_3420313203654562512[45] = 0;
   out_3420313203654562512[46] = 0;
   out_3420313203654562512[47] = 0;
   out_3420313203654562512[48] = 0;
   out_3420313203654562512[49] = 0;
   out_3420313203654562512[50] = 0;
   out_3420313203654562512[51] = 0;
   out_3420313203654562512[52] = 0;
   out_3420313203654562512[53] = 0;
}
void h_14(double *state, double *unused, double *out_1328437834424237699) {
   out_1328437834424237699[0] = state[6];
   out_1328437834424237699[1] = state[7];
   out_1328437834424237699[2] = state[8];
}
void H_14(double *state, double *unused, double *out_4333011229442915879) {
   out_4333011229442915879[0] = 0;
   out_4333011229442915879[1] = 0;
   out_4333011229442915879[2] = 0;
   out_4333011229442915879[3] = 0;
   out_4333011229442915879[4] = 0;
   out_4333011229442915879[5] = 0;
   out_4333011229442915879[6] = 1;
   out_4333011229442915879[7] = 0;
   out_4333011229442915879[8] = 0;
   out_4333011229442915879[9] = 0;
   out_4333011229442915879[10] = 0;
   out_4333011229442915879[11] = 0;
   out_4333011229442915879[12] = 0;
   out_4333011229442915879[13] = 0;
   out_4333011229442915879[14] = 0;
   out_4333011229442915879[15] = 0;
   out_4333011229442915879[16] = 0;
   out_4333011229442915879[17] = 0;
   out_4333011229442915879[18] = 0;
   out_4333011229442915879[19] = 0;
   out_4333011229442915879[20] = 0;
   out_4333011229442915879[21] = 0;
   out_4333011229442915879[22] = 0;
   out_4333011229442915879[23] = 0;
   out_4333011229442915879[24] = 0;
   out_4333011229442915879[25] = 1;
   out_4333011229442915879[26] = 0;
   out_4333011229442915879[27] = 0;
   out_4333011229442915879[28] = 0;
   out_4333011229442915879[29] = 0;
   out_4333011229442915879[30] = 0;
   out_4333011229442915879[31] = 0;
   out_4333011229442915879[32] = 0;
   out_4333011229442915879[33] = 0;
   out_4333011229442915879[34] = 0;
   out_4333011229442915879[35] = 0;
   out_4333011229442915879[36] = 0;
   out_4333011229442915879[37] = 0;
   out_4333011229442915879[38] = 0;
   out_4333011229442915879[39] = 0;
   out_4333011229442915879[40] = 0;
   out_4333011229442915879[41] = 0;
   out_4333011229442915879[42] = 0;
   out_4333011229442915879[43] = 0;
   out_4333011229442915879[44] = 1;
   out_4333011229442915879[45] = 0;
   out_4333011229442915879[46] = 0;
   out_4333011229442915879[47] = 0;
   out_4333011229442915879[48] = 0;
   out_4333011229442915879[49] = 0;
   out_4333011229442915879[50] = 0;
   out_4333011229442915879[51] = 0;
   out_4333011229442915879[52] = 0;
   out_4333011229442915879[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_165995497420240335) {
  err_fun(nom_x, delta_x, out_165995497420240335);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_2659251340504186577) {
  inv_err_fun(nom_x, true_x, out_2659251340504186577);
}
void pose_H_mod_fun(double *state, double *out_2311774637070926029) {
  H_mod_fun(state, out_2311774637070926029);
}
void pose_f_fun(double *state, double dt, double *out_7546479248053883876) {
  f_fun(state,  dt, out_7546479248053883876);
}
void pose_F_fun(double *state, double dt, double *out_7580047345257263534) {
  F_fun(state,  dt, out_7580047345257263534);
}
void pose_h_4(double *state, double *unused, double *out_2020815176821902235) {
  h_4(state, unused, out_2020815176821902235);
}
void pose_H_4(double *state, double *unused, double *out_6632587028986895313) {
  H_4(state, unused, out_6632587028986895313);
}
void pose_h_10(double *state, double *unused, double *out_5957214524665520889) {
  h_10(state, unused, out_5957214524665520889);
}
void pose_H_10(double *state, double *unused, double *out_3029068608548230730) {
  H_10(state, unused, out_3029068608548230730);
}
void pose_h_13(double *state, double *unused, double *out_7047283842734815329) {
  h_13(state, unused, out_7047283842734815329);
}
void pose_H_13(double *state, double *unused, double *out_3420313203654562512) {
  H_13(state, unused, out_3420313203654562512);
}
void pose_h_14(double *state, double *unused, double *out_1328437834424237699) {
  h_14(state, unused, out_1328437834424237699);
}
void pose_H_14(double *state, double *unused, double *out_4333011229442915879) {
  H_14(state, unused, out_4333011229442915879);
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
