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
void err_fun(double *nom_x, double *delta_x, double *out_2368389224522903581) {
   out_2368389224522903581[0] = delta_x[0] + nom_x[0];
   out_2368389224522903581[1] = delta_x[1] + nom_x[1];
   out_2368389224522903581[2] = delta_x[2] + nom_x[2];
   out_2368389224522903581[3] = delta_x[3] + nom_x[3];
   out_2368389224522903581[4] = delta_x[4] + nom_x[4];
   out_2368389224522903581[5] = delta_x[5] + nom_x[5];
   out_2368389224522903581[6] = delta_x[6] + nom_x[6];
   out_2368389224522903581[7] = delta_x[7] + nom_x[7];
   out_2368389224522903581[8] = delta_x[8] + nom_x[8];
   out_2368389224522903581[9] = delta_x[9] + nom_x[9];
   out_2368389224522903581[10] = delta_x[10] + nom_x[10];
   out_2368389224522903581[11] = delta_x[11] + nom_x[11];
   out_2368389224522903581[12] = delta_x[12] + nom_x[12];
   out_2368389224522903581[13] = delta_x[13] + nom_x[13];
   out_2368389224522903581[14] = delta_x[14] + nom_x[14];
   out_2368389224522903581[15] = delta_x[15] + nom_x[15];
   out_2368389224522903581[16] = delta_x[16] + nom_x[16];
   out_2368389224522903581[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6095247978319400369) {
   out_6095247978319400369[0] = -nom_x[0] + true_x[0];
   out_6095247978319400369[1] = -nom_x[1] + true_x[1];
   out_6095247978319400369[2] = -nom_x[2] + true_x[2];
   out_6095247978319400369[3] = -nom_x[3] + true_x[3];
   out_6095247978319400369[4] = -nom_x[4] + true_x[4];
   out_6095247978319400369[5] = -nom_x[5] + true_x[5];
   out_6095247978319400369[6] = -nom_x[6] + true_x[6];
   out_6095247978319400369[7] = -nom_x[7] + true_x[7];
   out_6095247978319400369[8] = -nom_x[8] + true_x[8];
   out_6095247978319400369[9] = -nom_x[9] + true_x[9];
   out_6095247978319400369[10] = -nom_x[10] + true_x[10];
   out_6095247978319400369[11] = -nom_x[11] + true_x[11];
   out_6095247978319400369[12] = -nom_x[12] + true_x[12];
   out_6095247978319400369[13] = -nom_x[13] + true_x[13];
   out_6095247978319400369[14] = -nom_x[14] + true_x[14];
   out_6095247978319400369[15] = -nom_x[15] + true_x[15];
   out_6095247978319400369[16] = -nom_x[16] + true_x[16];
   out_6095247978319400369[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_4445594867889321281) {
   out_4445594867889321281[0] = 1.0;
   out_4445594867889321281[1] = 0.0;
   out_4445594867889321281[2] = 0.0;
   out_4445594867889321281[3] = 0.0;
   out_4445594867889321281[4] = 0.0;
   out_4445594867889321281[5] = 0.0;
   out_4445594867889321281[6] = 0.0;
   out_4445594867889321281[7] = 0.0;
   out_4445594867889321281[8] = 0.0;
   out_4445594867889321281[9] = 0.0;
   out_4445594867889321281[10] = 0.0;
   out_4445594867889321281[11] = 0.0;
   out_4445594867889321281[12] = 0.0;
   out_4445594867889321281[13] = 0.0;
   out_4445594867889321281[14] = 0.0;
   out_4445594867889321281[15] = 0.0;
   out_4445594867889321281[16] = 0.0;
   out_4445594867889321281[17] = 0.0;
   out_4445594867889321281[18] = 0.0;
   out_4445594867889321281[19] = 1.0;
   out_4445594867889321281[20] = 0.0;
   out_4445594867889321281[21] = 0.0;
   out_4445594867889321281[22] = 0.0;
   out_4445594867889321281[23] = 0.0;
   out_4445594867889321281[24] = 0.0;
   out_4445594867889321281[25] = 0.0;
   out_4445594867889321281[26] = 0.0;
   out_4445594867889321281[27] = 0.0;
   out_4445594867889321281[28] = 0.0;
   out_4445594867889321281[29] = 0.0;
   out_4445594867889321281[30] = 0.0;
   out_4445594867889321281[31] = 0.0;
   out_4445594867889321281[32] = 0.0;
   out_4445594867889321281[33] = 0.0;
   out_4445594867889321281[34] = 0.0;
   out_4445594867889321281[35] = 0.0;
   out_4445594867889321281[36] = 0.0;
   out_4445594867889321281[37] = 0.0;
   out_4445594867889321281[38] = 1.0;
   out_4445594867889321281[39] = 0.0;
   out_4445594867889321281[40] = 0.0;
   out_4445594867889321281[41] = 0.0;
   out_4445594867889321281[42] = 0.0;
   out_4445594867889321281[43] = 0.0;
   out_4445594867889321281[44] = 0.0;
   out_4445594867889321281[45] = 0.0;
   out_4445594867889321281[46] = 0.0;
   out_4445594867889321281[47] = 0.0;
   out_4445594867889321281[48] = 0.0;
   out_4445594867889321281[49] = 0.0;
   out_4445594867889321281[50] = 0.0;
   out_4445594867889321281[51] = 0.0;
   out_4445594867889321281[52] = 0.0;
   out_4445594867889321281[53] = 0.0;
   out_4445594867889321281[54] = 0.0;
   out_4445594867889321281[55] = 0.0;
   out_4445594867889321281[56] = 0.0;
   out_4445594867889321281[57] = 1.0;
   out_4445594867889321281[58] = 0.0;
   out_4445594867889321281[59] = 0.0;
   out_4445594867889321281[60] = 0.0;
   out_4445594867889321281[61] = 0.0;
   out_4445594867889321281[62] = 0.0;
   out_4445594867889321281[63] = 0.0;
   out_4445594867889321281[64] = 0.0;
   out_4445594867889321281[65] = 0.0;
   out_4445594867889321281[66] = 0.0;
   out_4445594867889321281[67] = 0.0;
   out_4445594867889321281[68] = 0.0;
   out_4445594867889321281[69] = 0.0;
   out_4445594867889321281[70] = 0.0;
   out_4445594867889321281[71] = 0.0;
   out_4445594867889321281[72] = 0.0;
   out_4445594867889321281[73] = 0.0;
   out_4445594867889321281[74] = 0.0;
   out_4445594867889321281[75] = 0.0;
   out_4445594867889321281[76] = 1.0;
   out_4445594867889321281[77] = 0.0;
   out_4445594867889321281[78] = 0.0;
   out_4445594867889321281[79] = 0.0;
   out_4445594867889321281[80] = 0.0;
   out_4445594867889321281[81] = 0.0;
   out_4445594867889321281[82] = 0.0;
   out_4445594867889321281[83] = 0.0;
   out_4445594867889321281[84] = 0.0;
   out_4445594867889321281[85] = 0.0;
   out_4445594867889321281[86] = 0.0;
   out_4445594867889321281[87] = 0.0;
   out_4445594867889321281[88] = 0.0;
   out_4445594867889321281[89] = 0.0;
   out_4445594867889321281[90] = 0.0;
   out_4445594867889321281[91] = 0.0;
   out_4445594867889321281[92] = 0.0;
   out_4445594867889321281[93] = 0.0;
   out_4445594867889321281[94] = 0.0;
   out_4445594867889321281[95] = 1.0;
   out_4445594867889321281[96] = 0.0;
   out_4445594867889321281[97] = 0.0;
   out_4445594867889321281[98] = 0.0;
   out_4445594867889321281[99] = 0.0;
   out_4445594867889321281[100] = 0.0;
   out_4445594867889321281[101] = 0.0;
   out_4445594867889321281[102] = 0.0;
   out_4445594867889321281[103] = 0.0;
   out_4445594867889321281[104] = 0.0;
   out_4445594867889321281[105] = 0.0;
   out_4445594867889321281[106] = 0.0;
   out_4445594867889321281[107] = 0.0;
   out_4445594867889321281[108] = 0.0;
   out_4445594867889321281[109] = 0.0;
   out_4445594867889321281[110] = 0.0;
   out_4445594867889321281[111] = 0.0;
   out_4445594867889321281[112] = 0.0;
   out_4445594867889321281[113] = 0.0;
   out_4445594867889321281[114] = 1.0;
   out_4445594867889321281[115] = 0.0;
   out_4445594867889321281[116] = 0.0;
   out_4445594867889321281[117] = 0.0;
   out_4445594867889321281[118] = 0.0;
   out_4445594867889321281[119] = 0.0;
   out_4445594867889321281[120] = 0.0;
   out_4445594867889321281[121] = 0.0;
   out_4445594867889321281[122] = 0.0;
   out_4445594867889321281[123] = 0.0;
   out_4445594867889321281[124] = 0.0;
   out_4445594867889321281[125] = 0.0;
   out_4445594867889321281[126] = 0.0;
   out_4445594867889321281[127] = 0.0;
   out_4445594867889321281[128] = 0.0;
   out_4445594867889321281[129] = 0.0;
   out_4445594867889321281[130] = 0.0;
   out_4445594867889321281[131] = 0.0;
   out_4445594867889321281[132] = 0.0;
   out_4445594867889321281[133] = 1.0;
   out_4445594867889321281[134] = 0.0;
   out_4445594867889321281[135] = 0.0;
   out_4445594867889321281[136] = 0.0;
   out_4445594867889321281[137] = 0.0;
   out_4445594867889321281[138] = 0.0;
   out_4445594867889321281[139] = 0.0;
   out_4445594867889321281[140] = 0.0;
   out_4445594867889321281[141] = 0.0;
   out_4445594867889321281[142] = 0.0;
   out_4445594867889321281[143] = 0.0;
   out_4445594867889321281[144] = 0.0;
   out_4445594867889321281[145] = 0.0;
   out_4445594867889321281[146] = 0.0;
   out_4445594867889321281[147] = 0.0;
   out_4445594867889321281[148] = 0.0;
   out_4445594867889321281[149] = 0.0;
   out_4445594867889321281[150] = 0.0;
   out_4445594867889321281[151] = 0.0;
   out_4445594867889321281[152] = 1.0;
   out_4445594867889321281[153] = 0.0;
   out_4445594867889321281[154] = 0.0;
   out_4445594867889321281[155] = 0.0;
   out_4445594867889321281[156] = 0.0;
   out_4445594867889321281[157] = 0.0;
   out_4445594867889321281[158] = 0.0;
   out_4445594867889321281[159] = 0.0;
   out_4445594867889321281[160] = 0.0;
   out_4445594867889321281[161] = 0.0;
   out_4445594867889321281[162] = 0.0;
   out_4445594867889321281[163] = 0.0;
   out_4445594867889321281[164] = 0.0;
   out_4445594867889321281[165] = 0.0;
   out_4445594867889321281[166] = 0.0;
   out_4445594867889321281[167] = 0.0;
   out_4445594867889321281[168] = 0.0;
   out_4445594867889321281[169] = 0.0;
   out_4445594867889321281[170] = 0.0;
   out_4445594867889321281[171] = 1.0;
   out_4445594867889321281[172] = 0.0;
   out_4445594867889321281[173] = 0.0;
   out_4445594867889321281[174] = 0.0;
   out_4445594867889321281[175] = 0.0;
   out_4445594867889321281[176] = 0.0;
   out_4445594867889321281[177] = 0.0;
   out_4445594867889321281[178] = 0.0;
   out_4445594867889321281[179] = 0.0;
   out_4445594867889321281[180] = 0.0;
   out_4445594867889321281[181] = 0.0;
   out_4445594867889321281[182] = 0.0;
   out_4445594867889321281[183] = 0.0;
   out_4445594867889321281[184] = 0.0;
   out_4445594867889321281[185] = 0.0;
   out_4445594867889321281[186] = 0.0;
   out_4445594867889321281[187] = 0.0;
   out_4445594867889321281[188] = 0.0;
   out_4445594867889321281[189] = 0.0;
   out_4445594867889321281[190] = 1.0;
   out_4445594867889321281[191] = 0.0;
   out_4445594867889321281[192] = 0.0;
   out_4445594867889321281[193] = 0.0;
   out_4445594867889321281[194] = 0.0;
   out_4445594867889321281[195] = 0.0;
   out_4445594867889321281[196] = 0.0;
   out_4445594867889321281[197] = 0.0;
   out_4445594867889321281[198] = 0.0;
   out_4445594867889321281[199] = 0.0;
   out_4445594867889321281[200] = 0.0;
   out_4445594867889321281[201] = 0.0;
   out_4445594867889321281[202] = 0.0;
   out_4445594867889321281[203] = 0.0;
   out_4445594867889321281[204] = 0.0;
   out_4445594867889321281[205] = 0.0;
   out_4445594867889321281[206] = 0.0;
   out_4445594867889321281[207] = 0.0;
   out_4445594867889321281[208] = 0.0;
   out_4445594867889321281[209] = 1.0;
   out_4445594867889321281[210] = 0.0;
   out_4445594867889321281[211] = 0.0;
   out_4445594867889321281[212] = 0.0;
   out_4445594867889321281[213] = 0.0;
   out_4445594867889321281[214] = 0.0;
   out_4445594867889321281[215] = 0.0;
   out_4445594867889321281[216] = 0.0;
   out_4445594867889321281[217] = 0.0;
   out_4445594867889321281[218] = 0.0;
   out_4445594867889321281[219] = 0.0;
   out_4445594867889321281[220] = 0.0;
   out_4445594867889321281[221] = 0.0;
   out_4445594867889321281[222] = 0.0;
   out_4445594867889321281[223] = 0.0;
   out_4445594867889321281[224] = 0.0;
   out_4445594867889321281[225] = 0.0;
   out_4445594867889321281[226] = 0.0;
   out_4445594867889321281[227] = 0.0;
   out_4445594867889321281[228] = 1.0;
   out_4445594867889321281[229] = 0.0;
   out_4445594867889321281[230] = 0.0;
   out_4445594867889321281[231] = 0.0;
   out_4445594867889321281[232] = 0.0;
   out_4445594867889321281[233] = 0.0;
   out_4445594867889321281[234] = 0.0;
   out_4445594867889321281[235] = 0.0;
   out_4445594867889321281[236] = 0.0;
   out_4445594867889321281[237] = 0.0;
   out_4445594867889321281[238] = 0.0;
   out_4445594867889321281[239] = 0.0;
   out_4445594867889321281[240] = 0.0;
   out_4445594867889321281[241] = 0.0;
   out_4445594867889321281[242] = 0.0;
   out_4445594867889321281[243] = 0.0;
   out_4445594867889321281[244] = 0.0;
   out_4445594867889321281[245] = 0.0;
   out_4445594867889321281[246] = 0.0;
   out_4445594867889321281[247] = 1.0;
   out_4445594867889321281[248] = 0.0;
   out_4445594867889321281[249] = 0.0;
   out_4445594867889321281[250] = 0.0;
   out_4445594867889321281[251] = 0.0;
   out_4445594867889321281[252] = 0.0;
   out_4445594867889321281[253] = 0.0;
   out_4445594867889321281[254] = 0.0;
   out_4445594867889321281[255] = 0.0;
   out_4445594867889321281[256] = 0.0;
   out_4445594867889321281[257] = 0.0;
   out_4445594867889321281[258] = 0.0;
   out_4445594867889321281[259] = 0.0;
   out_4445594867889321281[260] = 0.0;
   out_4445594867889321281[261] = 0.0;
   out_4445594867889321281[262] = 0.0;
   out_4445594867889321281[263] = 0.0;
   out_4445594867889321281[264] = 0.0;
   out_4445594867889321281[265] = 0.0;
   out_4445594867889321281[266] = 1.0;
   out_4445594867889321281[267] = 0.0;
   out_4445594867889321281[268] = 0.0;
   out_4445594867889321281[269] = 0.0;
   out_4445594867889321281[270] = 0.0;
   out_4445594867889321281[271] = 0.0;
   out_4445594867889321281[272] = 0.0;
   out_4445594867889321281[273] = 0.0;
   out_4445594867889321281[274] = 0.0;
   out_4445594867889321281[275] = 0.0;
   out_4445594867889321281[276] = 0.0;
   out_4445594867889321281[277] = 0.0;
   out_4445594867889321281[278] = 0.0;
   out_4445594867889321281[279] = 0.0;
   out_4445594867889321281[280] = 0.0;
   out_4445594867889321281[281] = 0.0;
   out_4445594867889321281[282] = 0.0;
   out_4445594867889321281[283] = 0.0;
   out_4445594867889321281[284] = 0.0;
   out_4445594867889321281[285] = 1.0;
   out_4445594867889321281[286] = 0.0;
   out_4445594867889321281[287] = 0.0;
   out_4445594867889321281[288] = 0.0;
   out_4445594867889321281[289] = 0.0;
   out_4445594867889321281[290] = 0.0;
   out_4445594867889321281[291] = 0.0;
   out_4445594867889321281[292] = 0.0;
   out_4445594867889321281[293] = 0.0;
   out_4445594867889321281[294] = 0.0;
   out_4445594867889321281[295] = 0.0;
   out_4445594867889321281[296] = 0.0;
   out_4445594867889321281[297] = 0.0;
   out_4445594867889321281[298] = 0.0;
   out_4445594867889321281[299] = 0.0;
   out_4445594867889321281[300] = 0.0;
   out_4445594867889321281[301] = 0.0;
   out_4445594867889321281[302] = 0.0;
   out_4445594867889321281[303] = 0.0;
   out_4445594867889321281[304] = 1.0;
   out_4445594867889321281[305] = 0.0;
   out_4445594867889321281[306] = 0.0;
   out_4445594867889321281[307] = 0.0;
   out_4445594867889321281[308] = 0.0;
   out_4445594867889321281[309] = 0.0;
   out_4445594867889321281[310] = 0.0;
   out_4445594867889321281[311] = 0.0;
   out_4445594867889321281[312] = 0.0;
   out_4445594867889321281[313] = 0.0;
   out_4445594867889321281[314] = 0.0;
   out_4445594867889321281[315] = 0.0;
   out_4445594867889321281[316] = 0.0;
   out_4445594867889321281[317] = 0.0;
   out_4445594867889321281[318] = 0.0;
   out_4445594867889321281[319] = 0.0;
   out_4445594867889321281[320] = 0.0;
   out_4445594867889321281[321] = 0.0;
   out_4445594867889321281[322] = 0.0;
   out_4445594867889321281[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_2757988731602945540) {
   out_2757988731602945540[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_2757988731602945540[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_2757988731602945540[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_2757988731602945540[3] = dt*state[12] + state[3];
   out_2757988731602945540[4] = dt*state[13] + state[4];
   out_2757988731602945540[5] = dt*state[14] + state[5];
   out_2757988731602945540[6] = state[6];
   out_2757988731602945540[7] = state[7];
   out_2757988731602945540[8] = state[8];
   out_2757988731602945540[9] = state[9];
   out_2757988731602945540[10] = state[10];
   out_2757988731602945540[11] = state[11];
   out_2757988731602945540[12] = state[12];
   out_2757988731602945540[13] = state[13];
   out_2757988731602945540[14] = state[14];
   out_2757988731602945540[15] = state[15];
   out_2757988731602945540[16] = state[16];
   out_2757988731602945540[17] = state[17];
}
void F_fun(double *state, double dt, double *out_426903786628305371) {
   out_426903786628305371[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_426903786628305371[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_426903786628305371[2] = 0;
   out_426903786628305371[3] = 0;
   out_426903786628305371[4] = 0;
   out_426903786628305371[5] = 0;
   out_426903786628305371[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_426903786628305371[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_426903786628305371[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_426903786628305371[9] = 0;
   out_426903786628305371[10] = 0;
   out_426903786628305371[11] = 0;
   out_426903786628305371[12] = 0;
   out_426903786628305371[13] = 0;
   out_426903786628305371[14] = 0;
   out_426903786628305371[15] = 0;
   out_426903786628305371[16] = 0;
   out_426903786628305371[17] = 0;
   out_426903786628305371[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_426903786628305371[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_426903786628305371[20] = 0;
   out_426903786628305371[21] = 0;
   out_426903786628305371[22] = 0;
   out_426903786628305371[23] = 0;
   out_426903786628305371[24] = 0;
   out_426903786628305371[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_426903786628305371[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_426903786628305371[27] = 0;
   out_426903786628305371[28] = 0;
   out_426903786628305371[29] = 0;
   out_426903786628305371[30] = 0;
   out_426903786628305371[31] = 0;
   out_426903786628305371[32] = 0;
   out_426903786628305371[33] = 0;
   out_426903786628305371[34] = 0;
   out_426903786628305371[35] = 0;
   out_426903786628305371[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_426903786628305371[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_426903786628305371[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_426903786628305371[39] = 0;
   out_426903786628305371[40] = 0;
   out_426903786628305371[41] = 0;
   out_426903786628305371[42] = 0;
   out_426903786628305371[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_426903786628305371[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_426903786628305371[45] = 0;
   out_426903786628305371[46] = 0;
   out_426903786628305371[47] = 0;
   out_426903786628305371[48] = 0;
   out_426903786628305371[49] = 0;
   out_426903786628305371[50] = 0;
   out_426903786628305371[51] = 0;
   out_426903786628305371[52] = 0;
   out_426903786628305371[53] = 0;
   out_426903786628305371[54] = 0;
   out_426903786628305371[55] = 0;
   out_426903786628305371[56] = 0;
   out_426903786628305371[57] = 1;
   out_426903786628305371[58] = 0;
   out_426903786628305371[59] = 0;
   out_426903786628305371[60] = 0;
   out_426903786628305371[61] = 0;
   out_426903786628305371[62] = 0;
   out_426903786628305371[63] = 0;
   out_426903786628305371[64] = 0;
   out_426903786628305371[65] = 0;
   out_426903786628305371[66] = dt;
   out_426903786628305371[67] = 0;
   out_426903786628305371[68] = 0;
   out_426903786628305371[69] = 0;
   out_426903786628305371[70] = 0;
   out_426903786628305371[71] = 0;
   out_426903786628305371[72] = 0;
   out_426903786628305371[73] = 0;
   out_426903786628305371[74] = 0;
   out_426903786628305371[75] = 0;
   out_426903786628305371[76] = 1;
   out_426903786628305371[77] = 0;
   out_426903786628305371[78] = 0;
   out_426903786628305371[79] = 0;
   out_426903786628305371[80] = 0;
   out_426903786628305371[81] = 0;
   out_426903786628305371[82] = 0;
   out_426903786628305371[83] = 0;
   out_426903786628305371[84] = 0;
   out_426903786628305371[85] = dt;
   out_426903786628305371[86] = 0;
   out_426903786628305371[87] = 0;
   out_426903786628305371[88] = 0;
   out_426903786628305371[89] = 0;
   out_426903786628305371[90] = 0;
   out_426903786628305371[91] = 0;
   out_426903786628305371[92] = 0;
   out_426903786628305371[93] = 0;
   out_426903786628305371[94] = 0;
   out_426903786628305371[95] = 1;
   out_426903786628305371[96] = 0;
   out_426903786628305371[97] = 0;
   out_426903786628305371[98] = 0;
   out_426903786628305371[99] = 0;
   out_426903786628305371[100] = 0;
   out_426903786628305371[101] = 0;
   out_426903786628305371[102] = 0;
   out_426903786628305371[103] = 0;
   out_426903786628305371[104] = dt;
   out_426903786628305371[105] = 0;
   out_426903786628305371[106] = 0;
   out_426903786628305371[107] = 0;
   out_426903786628305371[108] = 0;
   out_426903786628305371[109] = 0;
   out_426903786628305371[110] = 0;
   out_426903786628305371[111] = 0;
   out_426903786628305371[112] = 0;
   out_426903786628305371[113] = 0;
   out_426903786628305371[114] = 1;
   out_426903786628305371[115] = 0;
   out_426903786628305371[116] = 0;
   out_426903786628305371[117] = 0;
   out_426903786628305371[118] = 0;
   out_426903786628305371[119] = 0;
   out_426903786628305371[120] = 0;
   out_426903786628305371[121] = 0;
   out_426903786628305371[122] = 0;
   out_426903786628305371[123] = 0;
   out_426903786628305371[124] = 0;
   out_426903786628305371[125] = 0;
   out_426903786628305371[126] = 0;
   out_426903786628305371[127] = 0;
   out_426903786628305371[128] = 0;
   out_426903786628305371[129] = 0;
   out_426903786628305371[130] = 0;
   out_426903786628305371[131] = 0;
   out_426903786628305371[132] = 0;
   out_426903786628305371[133] = 1;
   out_426903786628305371[134] = 0;
   out_426903786628305371[135] = 0;
   out_426903786628305371[136] = 0;
   out_426903786628305371[137] = 0;
   out_426903786628305371[138] = 0;
   out_426903786628305371[139] = 0;
   out_426903786628305371[140] = 0;
   out_426903786628305371[141] = 0;
   out_426903786628305371[142] = 0;
   out_426903786628305371[143] = 0;
   out_426903786628305371[144] = 0;
   out_426903786628305371[145] = 0;
   out_426903786628305371[146] = 0;
   out_426903786628305371[147] = 0;
   out_426903786628305371[148] = 0;
   out_426903786628305371[149] = 0;
   out_426903786628305371[150] = 0;
   out_426903786628305371[151] = 0;
   out_426903786628305371[152] = 1;
   out_426903786628305371[153] = 0;
   out_426903786628305371[154] = 0;
   out_426903786628305371[155] = 0;
   out_426903786628305371[156] = 0;
   out_426903786628305371[157] = 0;
   out_426903786628305371[158] = 0;
   out_426903786628305371[159] = 0;
   out_426903786628305371[160] = 0;
   out_426903786628305371[161] = 0;
   out_426903786628305371[162] = 0;
   out_426903786628305371[163] = 0;
   out_426903786628305371[164] = 0;
   out_426903786628305371[165] = 0;
   out_426903786628305371[166] = 0;
   out_426903786628305371[167] = 0;
   out_426903786628305371[168] = 0;
   out_426903786628305371[169] = 0;
   out_426903786628305371[170] = 0;
   out_426903786628305371[171] = 1;
   out_426903786628305371[172] = 0;
   out_426903786628305371[173] = 0;
   out_426903786628305371[174] = 0;
   out_426903786628305371[175] = 0;
   out_426903786628305371[176] = 0;
   out_426903786628305371[177] = 0;
   out_426903786628305371[178] = 0;
   out_426903786628305371[179] = 0;
   out_426903786628305371[180] = 0;
   out_426903786628305371[181] = 0;
   out_426903786628305371[182] = 0;
   out_426903786628305371[183] = 0;
   out_426903786628305371[184] = 0;
   out_426903786628305371[185] = 0;
   out_426903786628305371[186] = 0;
   out_426903786628305371[187] = 0;
   out_426903786628305371[188] = 0;
   out_426903786628305371[189] = 0;
   out_426903786628305371[190] = 1;
   out_426903786628305371[191] = 0;
   out_426903786628305371[192] = 0;
   out_426903786628305371[193] = 0;
   out_426903786628305371[194] = 0;
   out_426903786628305371[195] = 0;
   out_426903786628305371[196] = 0;
   out_426903786628305371[197] = 0;
   out_426903786628305371[198] = 0;
   out_426903786628305371[199] = 0;
   out_426903786628305371[200] = 0;
   out_426903786628305371[201] = 0;
   out_426903786628305371[202] = 0;
   out_426903786628305371[203] = 0;
   out_426903786628305371[204] = 0;
   out_426903786628305371[205] = 0;
   out_426903786628305371[206] = 0;
   out_426903786628305371[207] = 0;
   out_426903786628305371[208] = 0;
   out_426903786628305371[209] = 1;
   out_426903786628305371[210] = 0;
   out_426903786628305371[211] = 0;
   out_426903786628305371[212] = 0;
   out_426903786628305371[213] = 0;
   out_426903786628305371[214] = 0;
   out_426903786628305371[215] = 0;
   out_426903786628305371[216] = 0;
   out_426903786628305371[217] = 0;
   out_426903786628305371[218] = 0;
   out_426903786628305371[219] = 0;
   out_426903786628305371[220] = 0;
   out_426903786628305371[221] = 0;
   out_426903786628305371[222] = 0;
   out_426903786628305371[223] = 0;
   out_426903786628305371[224] = 0;
   out_426903786628305371[225] = 0;
   out_426903786628305371[226] = 0;
   out_426903786628305371[227] = 0;
   out_426903786628305371[228] = 1;
   out_426903786628305371[229] = 0;
   out_426903786628305371[230] = 0;
   out_426903786628305371[231] = 0;
   out_426903786628305371[232] = 0;
   out_426903786628305371[233] = 0;
   out_426903786628305371[234] = 0;
   out_426903786628305371[235] = 0;
   out_426903786628305371[236] = 0;
   out_426903786628305371[237] = 0;
   out_426903786628305371[238] = 0;
   out_426903786628305371[239] = 0;
   out_426903786628305371[240] = 0;
   out_426903786628305371[241] = 0;
   out_426903786628305371[242] = 0;
   out_426903786628305371[243] = 0;
   out_426903786628305371[244] = 0;
   out_426903786628305371[245] = 0;
   out_426903786628305371[246] = 0;
   out_426903786628305371[247] = 1;
   out_426903786628305371[248] = 0;
   out_426903786628305371[249] = 0;
   out_426903786628305371[250] = 0;
   out_426903786628305371[251] = 0;
   out_426903786628305371[252] = 0;
   out_426903786628305371[253] = 0;
   out_426903786628305371[254] = 0;
   out_426903786628305371[255] = 0;
   out_426903786628305371[256] = 0;
   out_426903786628305371[257] = 0;
   out_426903786628305371[258] = 0;
   out_426903786628305371[259] = 0;
   out_426903786628305371[260] = 0;
   out_426903786628305371[261] = 0;
   out_426903786628305371[262] = 0;
   out_426903786628305371[263] = 0;
   out_426903786628305371[264] = 0;
   out_426903786628305371[265] = 0;
   out_426903786628305371[266] = 1;
   out_426903786628305371[267] = 0;
   out_426903786628305371[268] = 0;
   out_426903786628305371[269] = 0;
   out_426903786628305371[270] = 0;
   out_426903786628305371[271] = 0;
   out_426903786628305371[272] = 0;
   out_426903786628305371[273] = 0;
   out_426903786628305371[274] = 0;
   out_426903786628305371[275] = 0;
   out_426903786628305371[276] = 0;
   out_426903786628305371[277] = 0;
   out_426903786628305371[278] = 0;
   out_426903786628305371[279] = 0;
   out_426903786628305371[280] = 0;
   out_426903786628305371[281] = 0;
   out_426903786628305371[282] = 0;
   out_426903786628305371[283] = 0;
   out_426903786628305371[284] = 0;
   out_426903786628305371[285] = 1;
   out_426903786628305371[286] = 0;
   out_426903786628305371[287] = 0;
   out_426903786628305371[288] = 0;
   out_426903786628305371[289] = 0;
   out_426903786628305371[290] = 0;
   out_426903786628305371[291] = 0;
   out_426903786628305371[292] = 0;
   out_426903786628305371[293] = 0;
   out_426903786628305371[294] = 0;
   out_426903786628305371[295] = 0;
   out_426903786628305371[296] = 0;
   out_426903786628305371[297] = 0;
   out_426903786628305371[298] = 0;
   out_426903786628305371[299] = 0;
   out_426903786628305371[300] = 0;
   out_426903786628305371[301] = 0;
   out_426903786628305371[302] = 0;
   out_426903786628305371[303] = 0;
   out_426903786628305371[304] = 1;
   out_426903786628305371[305] = 0;
   out_426903786628305371[306] = 0;
   out_426903786628305371[307] = 0;
   out_426903786628305371[308] = 0;
   out_426903786628305371[309] = 0;
   out_426903786628305371[310] = 0;
   out_426903786628305371[311] = 0;
   out_426903786628305371[312] = 0;
   out_426903786628305371[313] = 0;
   out_426903786628305371[314] = 0;
   out_426903786628305371[315] = 0;
   out_426903786628305371[316] = 0;
   out_426903786628305371[317] = 0;
   out_426903786628305371[318] = 0;
   out_426903786628305371[319] = 0;
   out_426903786628305371[320] = 0;
   out_426903786628305371[321] = 0;
   out_426903786628305371[322] = 0;
   out_426903786628305371[323] = 1;
}
void h_4(double *state, double *unused, double *out_6566999445586651777) {
   out_6566999445586651777[0] = state[6] + state[9];
   out_6566999445586651777[1] = state[7] + state[10];
   out_6566999445586651777[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_7072626526129509529) {
   out_7072626526129509529[0] = 0;
   out_7072626526129509529[1] = 0;
   out_7072626526129509529[2] = 0;
   out_7072626526129509529[3] = 0;
   out_7072626526129509529[4] = 0;
   out_7072626526129509529[5] = 0;
   out_7072626526129509529[6] = 1;
   out_7072626526129509529[7] = 0;
   out_7072626526129509529[8] = 0;
   out_7072626526129509529[9] = 1;
   out_7072626526129509529[10] = 0;
   out_7072626526129509529[11] = 0;
   out_7072626526129509529[12] = 0;
   out_7072626526129509529[13] = 0;
   out_7072626526129509529[14] = 0;
   out_7072626526129509529[15] = 0;
   out_7072626526129509529[16] = 0;
   out_7072626526129509529[17] = 0;
   out_7072626526129509529[18] = 0;
   out_7072626526129509529[19] = 0;
   out_7072626526129509529[20] = 0;
   out_7072626526129509529[21] = 0;
   out_7072626526129509529[22] = 0;
   out_7072626526129509529[23] = 0;
   out_7072626526129509529[24] = 0;
   out_7072626526129509529[25] = 1;
   out_7072626526129509529[26] = 0;
   out_7072626526129509529[27] = 0;
   out_7072626526129509529[28] = 1;
   out_7072626526129509529[29] = 0;
   out_7072626526129509529[30] = 0;
   out_7072626526129509529[31] = 0;
   out_7072626526129509529[32] = 0;
   out_7072626526129509529[33] = 0;
   out_7072626526129509529[34] = 0;
   out_7072626526129509529[35] = 0;
   out_7072626526129509529[36] = 0;
   out_7072626526129509529[37] = 0;
   out_7072626526129509529[38] = 0;
   out_7072626526129509529[39] = 0;
   out_7072626526129509529[40] = 0;
   out_7072626526129509529[41] = 0;
   out_7072626526129509529[42] = 0;
   out_7072626526129509529[43] = 0;
   out_7072626526129509529[44] = 1;
   out_7072626526129509529[45] = 0;
   out_7072626526129509529[46] = 0;
   out_7072626526129509529[47] = 1;
   out_7072626526129509529[48] = 0;
   out_7072626526129509529[49] = 0;
   out_7072626526129509529[50] = 0;
   out_7072626526129509529[51] = 0;
   out_7072626526129509529[52] = 0;
   out_7072626526129509529[53] = 0;
}
void h_10(double *state, double *unused, double *out_1367284512135170002) {
   out_1367284512135170002[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_1367284512135170002[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_1367284512135170002[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_6378919937591133006) {
   out_6378919937591133006[0] = 0;
   out_6378919937591133006[1] = 9.8100000000000005*cos(state[1]);
   out_6378919937591133006[2] = 0;
   out_6378919937591133006[3] = 0;
   out_6378919937591133006[4] = -state[8];
   out_6378919937591133006[5] = state[7];
   out_6378919937591133006[6] = 0;
   out_6378919937591133006[7] = state[5];
   out_6378919937591133006[8] = -state[4];
   out_6378919937591133006[9] = 0;
   out_6378919937591133006[10] = 0;
   out_6378919937591133006[11] = 0;
   out_6378919937591133006[12] = 1;
   out_6378919937591133006[13] = 0;
   out_6378919937591133006[14] = 0;
   out_6378919937591133006[15] = 1;
   out_6378919937591133006[16] = 0;
   out_6378919937591133006[17] = 0;
   out_6378919937591133006[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_6378919937591133006[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_6378919937591133006[20] = 0;
   out_6378919937591133006[21] = state[8];
   out_6378919937591133006[22] = 0;
   out_6378919937591133006[23] = -state[6];
   out_6378919937591133006[24] = -state[5];
   out_6378919937591133006[25] = 0;
   out_6378919937591133006[26] = state[3];
   out_6378919937591133006[27] = 0;
   out_6378919937591133006[28] = 0;
   out_6378919937591133006[29] = 0;
   out_6378919937591133006[30] = 0;
   out_6378919937591133006[31] = 1;
   out_6378919937591133006[32] = 0;
   out_6378919937591133006[33] = 0;
   out_6378919937591133006[34] = 1;
   out_6378919937591133006[35] = 0;
   out_6378919937591133006[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_6378919937591133006[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_6378919937591133006[38] = 0;
   out_6378919937591133006[39] = -state[7];
   out_6378919937591133006[40] = state[6];
   out_6378919937591133006[41] = 0;
   out_6378919937591133006[42] = state[4];
   out_6378919937591133006[43] = -state[3];
   out_6378919937591133006[44] = 0;
   out_6378919937591133006[45] = 0;
   out_6378919937591133006[46] = 0;
   out_6378919937591133006[47] = 0;
   out_6378919937591133006[48] = 0;
   out_6378919937591133006[49] = 0;
   out_6378919937591133006[50] = 1;
   out_6378919937591133006[51] = 0;
   out_6378919937591133006[52] = 0;
   out_6378919937591133006[53] = 1;
}
void h_13(double *state, double *unused, double *out_8828797571683696909) {
   out_8828797571683696909[0] = state[3];
   out_8828797571683696909[1] = state[4];
   out_8828797571683696909[2] = state[5];
}
void H_13(double *state, double *unused, double *out_3860352700797176728) {
   out_3860352700797176728[0] = 0;
   out_3860352700797176728[1] = 0;
   out_3860352700797176728[2] = 0;
   out_3860352700797176728[3] = 1;
   out_3860352700797176728[4] = 0;
   out_3860352700797176728[5] = 0;
   out_3860352700797176728[6] = 0;
   out_3860352700797176728[7] = 0;
   out_3860352700797176728[8] = 0;
   out_3860352700797176728[9] = 0;
   out_3860352700797176728[10] = 0;
   out_3860352700797176728[11] = 0;
   out_3860352700797176728[12] = 0;
   out_3860352700797176728[13] = 0;
   out_3860352700797176728[14] = 0;
   out_3860352700797176728[15] = 0;
   out_3860352700797176728[16] = 0;
   out_3860352700797176728[17] = 0;
   out_3860352700797176728[18] = 0;
   out_3860352700797176728[19] = 0;
   out_3860352700797176728[20] = 0;
   out_3860352700797176728[21] = 0;
   out_3860352700797176728[22] = 1;
   out_3860352700797176728[23] = 0;
   out_3860352700797176728[24] = 0;
   out_3860352700797176728[25] = 0;
   out_3860352700797176728[26] = 0;
   out_3860352700797176728[27] = 0;
   out_3860352700797176728[28] = 0;
   out_3860352700797176728[29] = 0;
   out_3860352700797176728[30] = 0;
   out_3860352700797176728[31] = 0;
   out_3860352700797176728[32] = 0;
   out_3860352700797176728[33] = 0;
   out_3860352700797176728[34] = 0;
   out_3860352700797176728[35] = 0;
   out_3860352700797176728[36] = 0;
   out_3860352700797176728[37] = 0;
   out_3860352700797176728[38] = 0;
   out_3860352700797176728[39] = 0;
   out_3860352700797176728[40] = 0;
   out_3860352700797176728[41] = 1;
   out_3860352700797176728[42] = 0;
   out_3860352700797176728[43] = 0;
   out_3860352700797176728[44] = 0;
   out_3860352700797176728[45] = 0;
   out_3860352700797176728[46] = 0;
   out_3860352700797176728[47] = 0;
   out_3860352700797176728[48] = 0;
   out_3860352700797176728[49] = 0;
   out_3860352700797176728[50] = 0;
   out_3860352700797176728[51] = 0;
   out_3860352700797176728[52] = 0;
   out_3860352700797176728[53] = 0;
}
void h_14(double *state, double *unused, double *out_3744289369958305134) {
   out_3744289369958305134[0] = state[6];
   out_3744289369958305134[1] = state[7];
   out_3744289369958305134[2] = state[8];
}
void H_14(double *state, double *unused, double *out_3109385669790025000) {
   out_3109385669790025000[0] = 0;
   out_3109385669790025000[1] = 0;
   out_3109385669790025000[2] = 0;
   out_3109385669790025000[3] = 0;
   out_3109385669790025000[4] = 0;
   out_3109385669790025000[5] = 0;
   out_3109385669790025000[6] = 1;
   out_3109385669790025000[7] = 0;
   out_3109385669790025000[8] = 0;
   out_3109385669790025000[9] = 0;
   out_3109385669790025000[10] = 0;
   out_3109385669790025000[11] = 0;
   out_3109385669790025000[12] = 0;
   out_3109385669790025000[13] = 0;
   out_3109385669790025000[14] = 0;
   out_3109385669790025000[15] = 0;
   out_3109385669790025000[16] = 0;
   out_3109385669790025000[17] = 0;
   out_3109385669790025000[18] = 0;
   out_3109385669790025000[19] = 0;
   out_3109385669790025000[20] = 0;
   out_3109385669790025000[21] = 0;
   out_3109385669790025000[22] = 0;
   out_3109385669790025000[23] = 0;
   out_3109385669790025000[24] = 0;
   out_3109385669790025000[25] = 1;
   out_3109385669790025000[26] = 0;
   out_3109385669790025000[27] = 0;
   out_3109385669790025000[28] = 0;
   out_3109385669790025000[29] = 0;
   out_3109385669790025000[30] = 0;
   out_3109385669790025000[31] = 0;
   out_3109385669790025000[32] = 0;
   out_3109385669790025000[33] = 0;
   out_3109385669790025000[34] = 0;
   out_3109385669790025000[35] = 0;
   out_3109385669790025000[36] = 0;
   out_3109385669790025000[37] = 0;
   out_3109385669790025000[38] = 0;
   out_3109385669790025000[39] = 0;
   out_3109385669790025000[40] = 0;
   out_3109385669790025000[41] = 0;
   out_3109385669790025000[42] = 0;
   out_3109385669790025000[43] = 0;
   out_3109385669790025000[44] = 1;
   out_3109385669790025000[45] = 0;
   out_3109385669790025000[46] = 0;
   out_3109385669790025000[47] = 0;
   out_3109385669790025000[48] = 0;
   out_3109385669790025000[49] = 0;
   out_3109385669790025000[50] = 0;
   out_3109385669790025000[51] = 0;
   out_3109385669790025000[52] = 0;
   out_3109385669790025000[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_2368389224522903581) {
  err_fun(nom_x, delta_x, out_2368389224522903581);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_6095247978319400369) {
  inv_err_fun(nom_x, true_x, out_6095247978319400369);
}
void pose_H_mod_fun(double *state, double *out_4445594867889321281) {
  H_mod_fun(state, out_4445594867889321281);
}
void pose_f_fun(double *state, double dt, double *out_2757988731602945540) {
  f_fun(state,  dt, out_2757988731602945540);
}
void pose_F_fun(double *state, double dt, double *out_426903786628305371) {
  F_fun(state,  dt, out_426903786628305371);
}
void pose_h_4(double *state, double *unused, double *out_6566999445586651777) {
  h_4(state, unused, out_6566999445586651777);
}
void pose_H_4(double *state, double *unused, double *out_7072626526129509529) {
  H_4(state, unused, out_7072626526129509529);
}
void pose_h_10(double *state, double *unused, double *out_1367284512135170002) {
  h_10(state, unused, out_1367284512135170002);
}
void pose_H_10(double *state, double *unused, double *out_6378919937591133006) {
  H_10(state, unused, out_6378919937591133006);
}
void pose_h_13(double *state, double *unused, double *out_8828797571683696909) {
  h_13(state, unused, out_8828797571683696909);
}
void pose_H_13(double *state, double *unused, double *out_3860352700797176728) {
  H_13(state, unused, out_3860352700797176728);
}
void pose_h_14(double *state, double *unused, double *out_3744289369958305134) {
  h_14(state, unused, out_3744289369958305134);
}
void pose_H_14(double *state, double *unused, double *out_3109385669790025000) {
  H_14(state, unused, out_3109385669790025000);
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
