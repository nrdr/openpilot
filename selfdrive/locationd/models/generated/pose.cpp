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
void err_fun(double *nom_x, double *delta_x, double *out_7150551631592866018) {
   out_7150551631592866018[0] = delta_x[0] + nom_x[0];
   out_7150551631592866018[1] = delta_x[1] + nom_x[1];
   out_7150551631592866018[2] = delta_x[2] + nom_x[2];
   out_7150551631592866018[3] = delta_x[3] + nom_x[3];
   out_7150551631592866018[4] = delta_x[4] + nom_x[4];
   out_7150551631592866018[5] = delta_x[5] + nom_x[5];
   out_7150551631592866018[6] = delta_x[6] + nom_x[6];
   out_7150551631592866018[7] = delta_x[7] + nom_x[7];
   out_7150551631592866018[8] = delta_x[8] + nom_x[8];
   out_7150551631592866018[9] = delta_x[9] + nom_x[9];
   out_7150551631592866018[10] = delta_x[10] + nom_x[10];
   out_7150551631592866018[11] = delta_x[11] + nom_x[11];
   out_7150551631592866018[12] = delta_x[12] + nom_x[12];
   out_7150551631592866018[13] = delta_x[13] + nom_x[13];
   out_7150551631592866018[14] = delta_x[14] + nom_x[14];
   out_7150551631592866018[15] = delta_x[15] + nom_x[15];
   out_7150551631592866018[16] = delta_x[16] + nom_x[16];
   out_7150551631592866018[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_2794293729781716576) {
   out_2794293729781716576[0] = -nom_x[0] + true_x[0];
   out_2794293729781716576[1] = -nom_x[1] + true_x[1];
   out_2794293729781716576[2] = -nom_x[2] + true_x[2];
   out_2794293729781716576[3] = -nom_x[3] + true_x[3];
   out_2794293729781716576[4] = -nom_x[4] + true_x[4];
   out_2794293729781716576[5] = -nom_x[5] + true_x[5];
   out_2794293729781716576[6] = -nom_x[6] + true_x[6];
   out_2794293729781716576[7] = -nom_x[7] + true_x[7];
   out_2794293729781716576[8] = -nom_x[8] + true_x[8];
   out_2794293729781716576[9] = -nom_x[9] + true_x[9];
   out_2794293729781716576[10] = -nom_x[10] + true_x[10];
   out_2794293729781716576[11] = -nom_x[11] + true_x[11];
   out_2794293729781716576[12] = -nom_x[12] + true_x[12];
   out_2794293729781716576[13] = -nom_x[13] + true_x[13];
   out_2794293729781716576[14] = -nom_x[14] + true_x[14];
   out_2794293729781716576[15] = -nom_x[15] + true_x[15];
   out_2794293729781716576[16] = -nom_x[16] + true_x[16];
   out_2794293729781716576[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_8150336989101570986) {
   out_8150336989101570986[0] = 1.0;
   out_8150336989101570986[1] = 0.0;
   out_8150336989101570986[2] = 0.0;
   out_8150336989101570986[3] = 0.0;
   out_8150336989101570986[4] = 0.0;
   out_8150336989101570986[5] = 0.0;
   out_8150336989101570986[6] = 0.0;
   out_8150336989101570986[7] = 0.0;
   out_8150336989101570986[8] = 0.0;
   out_8150336989101570986[9] = 0.0;
   out_8150336989101570986[10] = 0.0;
   out_8150336989101570986[11] = 0.0;
   out_8150336989101570986[12] = 0.0;
   out_8150336989101570986[13] = 0.0;
   out_8150336989101570986[14] = 0.0;
   out_8150336989101570986[15] = 0.0;
   out_8150336989101570986[16] = 0.0;
   out_8150336989101570986[17] = 0.0;
   out_8150336989101570986[18] = 0.0;
   out_8150336989101570986[19] = 1.0;
   out_8150336989101570986[20] = 0.0;
   out_8150336989101570986[21] = 0.0;
   out_8150336989101570986[22] = 0.0;
   out_8150336989101570986[23] = 0.0;
   out_8150336989101570986[24] = 0.0;
   out_8150336989101570986[25] = 0.0;
   out_8150336989101570986[26] = 0.0;
   out_8150336989101570986[27] = 0.0;
   out_8150336989101570986[28] = 0.0;
   out_8150336989101570986[29] = 0.0;
   out_8150336989101570986[30] = 0.0;
   out_8150336989101570986[31] = 0.0;
   out_8150336989101570986[32] = 0.0;
   out_8150336989101570986[33] = 0.0;
   out_8150336989101570986[34] = 0.0;
   out_8150336989101570986[35] = 0.0;
   out_8150336989101570986[36] = 0.0;
   out_8150336989101570986[37] = 0.0;
   out_8150336989101570986[38] = 1.0;
   out_8150336989101570986[39] = 0.0;
   out_8150336989101570986[40] = 0.0;
   out_8150336989101570986[41] = 0.0;
   out_8150336989101570986[42] = 0.0;
   out_8150336989101570986[43] = 0.0;
   out_8150336989101570986[44] = 0.0;
   out_8150336989101570986[45] = 0.0;
   out_8150336989101570986[46] = 0.0;
   out_8150336989101570986[47] = 0.0;
   out_8150336989101570986[48] = 0.0;
   out_8150336989101570986[49] = 0.0;
   out_8150336989101570986[50] = 0.0;
   out_8150336989101570986[51] = 0.0;
   out_8150336989101570986[52] = 0.0;
   out_8150336989101570986[53] = 0.0;
   out_8150336989101570986[54] = 0.0;
   out_8150336989101570986[55] = 0.0;
   out_8150336989101570986[56] = 0.0;
   out_8150336989101570986[57] = 1.0;
   out_8150336989101570986[58] = 0.0;
   out_8150336989101570986[59] = 0.0;
   out_8150336989101570986[60] = 0.0;
   out_8150336989101570986[61] = 0.0;
   out_8150336989101570986[62] = 0.0;
   out_8150336989101570986[63] = 0.0;
   out_8150336989101570986[64] = 0.0;
   out_8150336989101570986[65] = 0.0;
   out_8150336989101570986[66] = 0.0;
   out_8150336989101570986[67] = 0.0;
   out_8150336989101570986[68] = 0.0;
   out_8150336989101570986[69] = 0.0;
   out_8150336989101570986[70] = 0.0;
   out_8150336989101570986[71] = 0.0;
   out_8150336989101570986[72] = 0.0;
   out_8150336989101570986[73] = 0.0;
   out_8150336989101570986[74] = 0.0;
   out_8150336989101570986[75] = 0.0;
   out_8150336989101570986[76] = 1.0;
   out_8150336989101570986[77] = 0.0;
   out_8150336989101570986[78] = 0.0;
   out_8150336989101570986[79] = 0.0;
   out_8150336989101570986[80] = 0.0;
   out_8150336989101570986[81] = 0.0;
   out_8150336989101570986[82] = 0.0;
   out_8150336989101570986[83] = 0.0;
   out_8150336989101570986[84] = 0.0;
   out_8150336989101570986[85] = 0.0;
   out_8150336989101570986[86] = 0.0;
   out_8150336989101570986[87] = 0.0;
   out_8150336989101570986[88] = 0.0;
   out_8150336989101570986[89] = 0.0;
   out_8150336989101570986[90] = 0.0;
   out_8150336989101570986[91] = 0.0;
   out_8150336989101570986[92] = 0.0;
   out_8150336989101570986[93] = 0.0;
   out_8150336989101570986[94] = 0.0;
   out_8150336989101570986[95] = 1.0;
   out_8150336989101570986[96] = 0.0;
   out_8150336989101570986[97] = 0.0;
   out_8150336989101570986[98] = 0.0;
   out_8150336989101570986[99] = 0.0;
   out_8150336989101570986[100] = 0.0;
   out_8150336989101570986[101] = 0.0;
   out_8150336989101570986[102] = 0.0;
   out_8150336989101570986[103] = 0.0;
   out_8150336989101570986[104] = 0.0;
   out_8150336989101570986[105] = 0.0;
   out_8150336989101570986[106] = 0.0;
   out_8150336989101570986[107] = 0.0;
   out_8150336989101570986[108] = 0.0;
   out_8150336989101570986[109] = 0.0;
   out_8150336989101570986[110] = 0.0;
   out_8150336989101570986[111] = 0.0;
   out_8150336989101570986[112] = 0.0;
   out_8150336989101570986[113] = 0.0;
   out_8150336989101570986[114] = 1.0;
   out_8150336989101570986[115] = 0.0;
   out_8150336989101570986[116] = 0.0;
   out_8150336989101570986[117] = 0.0;
   out_8150336989101570986[118] = 0.0;
   out_8150336989101570986[119] = 0.0;
   out_8150336989101570986[120] = 0.0;
   out_8150336989101570986[121] = 0.0;
   out_8150336989101570986[122] = 0.0;
   out_8150336989101570986[123] = 0.0;
   out_8150336989101570986[124] = 0.0;
   out_8150336989101570986[125] = 0.0;
   out_8150336989101570986[126] = 0.0;
   out_8150336989101570986[127] = 0.0;
   out_8150336989101570986[128] = 0.0;
   out_8150336989101570986[129] = 0.0;
   out_8150336989101570986[130] = 0.0;
   out_8150336989101570986[131] = 0.0;
   out_8150336989101570986[132] = 0.0;
   out_8150336989101570986[133] = 1.0;
   out_8150336989101570986[134] = 0.0;
   out_8150336989101570986[135] = 0.0;
   out_8150336989101570986[136] = 0.0;
   out_8150336989101570986[137] = 0.0;
   out_8150336989101570986[138] = 0.0;
   out_8150336989101570986[139] = 0.0;
   out_8150336989101570986[140] = 0.0;
   out_8150336989101570986[141] = 0.0;
   out_8150336989101570986[142] = 0.0;
   out_8150336989101570986[143] = 0.0;
   out_8150336989101570986[144] = 0.0;
   out_8150336989101570986[145] = 0.0;
   out_8150336989101570986[146] = 0.0;
   out_8150336989101570986[147] = 0.0;
   out_8150336989101570986[148] = 0.0;
   out_8150336989101570986[149] = 0.0;
   out_8150336989101570986[150] = 0.0;
   out_8150336989101570986[151] = 0.0;
   out_8150336989101570986[152] = 1.0;
   out_8150336989101570986[153] = 0.0;
   out_8150336989101570986[154] = 0.0;
   out_8150336989101570986[155] = 0.0;
   out_8150336989101570986[156] = 0.0;
   out_8150336989101570986[157] = 0.0;
   out_8150336989101570986[158] = 0.0;
   out_8150336989101570986[159] = 0.0;
   out_8150336989101570986[160] = 0.0;
   out_8150336989101570986[161] = 0.0;
   out_8150336989101570986[162] = 0.0;
   out_8150336989101570986[163] = 0.0;
   out_8150336989101570986[164] = 0.0;
   out_8150336989101570986[165] = 0.0;
   out_8150336989101570986[166] = 0.0;
   out_8150336989101570986[167] = 0.0;
   out_8150336989101570986[168] = 0.0;
   out_8150336989101570986[169] = 0.0;
   out_8150336989101570986[170] = 0.0;
   out_8150336989101570986[171] = 1.0;
   out_8150336989101570986[172] = 0.0;
   out_8150336989101570986[173] = 0.0;
   out_8150336989101570986[174] = 0.0;
   out_8150336989101570986[175] = 0.0;
   out_8150336989101570986[176] = 0.0;
   out_8150336989101570986[177] = 0.0;
   out_8150336989101570986[178] = 0.0;
   out_8150336989101570986[179] = 0.0;
   out_8150336989101570986[180] = 0.0;
   out_8150336989101570986[181] = 0.0;
   out_8150336989101570986[182] = 0.0;
   out_8150336989101570986[183] = 0.0;
   out_8150336989101570986[184] = 0.0;
   out_8150336989101570986[185] = 0.0;
   out_8150336989101570986[186] = 0.0;
   out_8150336989101570986[187] = 0.0;
   out_8150336989101570986[188] = 0.0;
   out_8150336989101570986[189] = 0.0;
   out_8150336989101570986[190] = 1.0;
   out_8150336989101570986[191] = 0.0;
   out_8150336989101570986[192] = 0.0;
   out_8150336989101570986[193] = 0.0;
   out_8150336989101570986[194] = 0.0;
   out_8150336989101570986[195] = 0.0;
   out_8150336989101570986[196] = 0.0;
   out_8150336989101570986[197] = 0.0;
   out_8150336989101570986[198] = 0.0;
   out_8150336989101570986[199] = 0.0;
   out_8150336989101570986[200] = 0.0;
   out_8150336989101570986[201] = 0.0;
   out_8150336989101570986[202] = 0.0;
   out_8150336989101570986[203] = 0.0;
   out_8150336989101570986[204] = 0.0;
   out_8150336989101570986[205] = 0.0;
   out_8150336989101570986[206] = 0.0;
   out_8150336989101570986[207] = 0.0;
   out_8150336989101570986[208] = 0.0;
   out_8150336989101570986[209] = 1.0;
   out_8150336989101570986[210] = 0.0;
   out_8150336989101570986[211] = 0.0;
   out_8150336989101570986[212] = 0.0;
   out_8150336989101570986[213] = 0.0;
   out_8150336989101570986[214] = 0.0;
   out_8150336989101570986[215] = 0.0;
   out_8150336989101570986[216] = 0.0;
   out_8150336989101570986[217] = 0.0;
   out_8150336989101570986[218] = 0.0;
   out_8150336989101570986[219] = 0.0;
   out_8150336989101570986[220] = 0.0;
   out_8150336989101570986[221] = 0.0;
   out_8150336989101570986[222] = 0.0;
   out_8150336989101570986[223] = 0.0;
   out_8150336989101570986[224] = 0.0;
   out_8150336989101570986[225] = 0.0;
   out_8150336989101570986[226] = 0.0;
   out_8150336989101570986[227] = 0.0;
   out_8150336989101570986[228] = 1.0;
   out_8150336989101570986[229] = 0.0;
   out_8150336989101570986[230] = 0.0;
   out_8150336989101570986[231] = 0.0;
   out_8150336989101570986[232] = 0.0;
   out_8150336989101570986[233] = 0.0;
   out_8150336989101570986[234] = 0.0;
   out_8150336989101570986[235] = 0.0;
   out_8150336989101570986[236] = 0.0;
   out_8150336989101570986[237] = 0.0;
   out_8150336989101570986[238] = 0.0;
   out_8150336989101570986[239] = 0.0;
   out_8150336989101570986[240] = 0.0;
   out_8150336989101570986[241] = 0.0;
   out_8150336989101570986[242] = 0.0;
   out_8150336989101570986[243] = 0.0;
   out_8150336989101570986[244] = 0.0;
   out_8150336989101570986[245] = 0.0;
   out_8150336989101570986[246] = 0.0;
   out_8150336989101570986[247] = 1.0;
   out_8150336989101570986[248] = 0.0;
   out_8150336989101570986[249] = 0.0;
   out_8150336989101570986[250] = 0.0;
   out_8150336989101570986[251] = 0.0;
   out_8150336989101570986[252] = 0.0;
   out_8150336989101570986[253] = 0.0;
   out_8150336989101570986[254] = 0.0;
   out_8150336989101570986[255] = 0.0;
   out_8150336989101570986[256] = 0.0;
   out_8150336989101570986[257] = 0.0;
   out_8150336989101570986[258] = 0.0;
   out_8150336989101570986[259] = 0.0;
   out_8150336989101570986[260] = 0.0;
   out_8150336989101570986[261] = 0.0;
   out_8150336989101570986[262] = 0.0;
   out_8150336989101570986[263] = 0.0;
   out_8150336989101570986[264] = 0.0;
   out_8150336989101570986[265] = 0.0;
   out_8150336989101570986[266] = 1.0;
   out_8150336989101570986[267] = 0.0;
   out_8150336989101570986[268] = 0.0;
   out_8150336989101570986[269] = 0.0;
   out_8150336989101570986[270] = 0.0;
   out_8150336989101570986[271] = 0.0;
   out_8150336989101570986[272] = 0.0;
   out_8150336989101570986[273] = 0.0;
   out_8150336989101570986[274] = 0.0;
   out_8150336989101570986[275] = 0.0;
   out_8150336989101570986[276] = 0.0;
   out_8150336989101570986[277] = 0.0;
   out_8150336989101570986[278] = 0.0;
   out_8150336989101570986[279] = 0.0;
   out_8150336989101570986[280] = 0.0;
   out_8150336989101570986[281] = 0.0;
   out_8150336989101570986[282] = 0.0;
   out_8150336989101570986[283] = 0.0;
   out_8150336989101570986[284] = 0.0;
   out_8150336989101570986[285] = 1.0;
   out_8150336989101570986[286] = 0.0;
   out_8150336989101570986[287] = 0.0;
   out_8150336989101570986[288] = 0.0;
   out_8150336989101570986[289] = 0.0;
   out_8150336989101570986[290] = 0.0;
   out_8150336989101570986[291] = 0.0;
   out_8150336989101570986[292] = 0.0;
   out_8150336989101570986[293] = 0.0;
   out_8150336989101570986[294] = 0.0;
   out_8150336989101570986[295] = 0.0;
   out_8150336989101570986[296] = 0.0;
   out_8150336989101570986[297] = 0.0;
   out_8150336989101570986[298] = 0.0;
   out_8150336989101570986[299] = 0.0;
   out_8150336989101570986[300] = 0.0;
   out_8150336989101570986[301] = 0.0;
   out_8150336989101570986[302] = 0.0;
   out_8150336989101570986[303] = 0.0;
   out_8150336989101570986[304] = 1.0;
   out_8150336989101570986[305] = 0.0;
   out_8150336989101570986[306] = 0.0;
   out_8150336989101570986[307] = 0.0;
   out_8150336989101570986[308] = 0.0;
   out_8150336989101570986[309] = 0.0;
   out_8150336989101570986[310] = 0.0;
   out_8150336989101570986[311] = 0.0;
   out_8150336989101570986[312] = 0.0;
   out_8150336989101570986[313] = 0.0;
   out_8150336989101570986[314] = 0.0;
   out_8150336989101570986[315] = 0.0;
   out_8150336989101570986[316] = 0.0;
   out_8150336989101570986[317] = 0.0;
   out_8150336989101570986[318] = 0.0;
   out_8150336989101570986[319] = 0.0;
   out_8150336989101570986[320] = 0.0;
   out_8150336989101570986[321] = 0.0;
   out_8150336989101570986[322] = 0.0;
   out_8150336989101570986[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_7007205599395941006) {
   out_7007205599395941006[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_7007205599395941006[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_7007205599395941006[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_7007205599395941006[3] = dt*state[12] + state[3];
   out_7007205599395941006[4] = dt*state[13] + state[4];
   out_7007205599395941006[5] = dt*state[14] + state[5];
   out_7007205599395941006[6] = state[6];
   out_7007205599395941006[7] = state[7];
   out_7007205599395941006[8] = state[8];
   out_7007205599395941006[9] = state[9];
   out_7007205599395941006[10] = state[10];
   out_7007205599395941006[11] = state[11];
   out_7007205599395941006[12] = state[12];
   out_7007205599395941006[13] = state[13];
   out_7007205599395941006[14] = state[14];
   out_7007205599395941006[15] = state[15];
   out_7007205599395941006[16] = state[16];
   out_7007205599395941006[17] = state[17];
}
void F_fun(double *state, double dt, double *out_6961192590068817781) {
   out_6961192590068817781[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6961192590068817781[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6961192590068817781[2] = 0;
   out_6961192590068817781[3] = 0;
   out_6961192590068817781[4] = 0;
   out_6961192590068817781[5] = 0;
   out_6961192590068817781[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6961192590068817781[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6961192590068817781[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6961192590068817781[9] = 0;
   out_6961192590068817781[10] = 0;
   out_6961192590068817781[11] = 0;
   out_6961192590068817781[12] = 0;
   out_6961192590068817781[13] = 0;
   out_6961192590068817781[14] = 0;
   out_6961192590068817781[15] = 0;
   out_6961192590068817781[16] = 0;
   out_6961192590068817781[17] = 0;
   out_6961192590068817781[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6961192590068817781[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6961192590068817781[20] = 0;
   out_6961192590068817781[21] = 0;
   out_6961192590068817781[22] = 0;
   out_6961192590068817781[23] = 0;
   out_6961192590068817781[24] = 0;
   out_6961192590068817781[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6961192590068817781[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6961192590068817781[27] = 0;
   out_6961192590068817781[28] = 0;
   out_6961192590068817781[29] = 0;
   out_6961192590068817781[30] = 0;
   out_6961192590068817781[31] = 0;
   out_6961192590068817781[32] = 0;
   out_6961192590068817781[33] = 0;
   out_6961192590068817781[34] = 0;
   out_6961192590068817781[35] = 0;
   out_6961192590068817781[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6961192590068817781[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6961192590068817781[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6961192590068817781[39] = 0;
   out_6961192590068817781[40] = 0;
   out_6961192590068817781[41] = 0;
   out_6961192590068817781[42] = 0;
   out_6961192590068817781[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6961192590068817781[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6961192590068817781[45] = 0;
   out_6961192590068817781[46] = 0;
   out_6961192590068817781[47] = 0;
   out_6961192590068817781[48] = 0;
   out_6961192590068817781[49] = 0;
   out_6961192590068817781[50] = 0;
   out_6961192590068817781[51] = 0;
   out_6961192590068817781[52] = 0;
   out_6961192590068817781[53] = 0;
   out_6961192590068817781[54] = 0;
   out_6961192590068817781[55] = 0;
   out_6961192590068817781[56] = 0;
   out_6961192590068817781[57] = 1;
   out_6961192590068817781[58] = 0;
   out_6961192590068817781[59] = 0;
   out_6961192590068817781[60] = 0;
   out_6961192590068817781[61] = 0;
   out_6961192590068817781[62] = 0;
   out_6961192590068817781[63] = 0;
   out_6961192590068817781[64] = 0;
   out_6961192590068817781[65] = 0;
   out_6961192590068817781[66] = dt;
   out_6961192590068817781[67] = 0;
   out_6961192590068817781[68] = 0;
   out_6961192590068817781[69] = 0;
   out_6961192590068817781[70] = 0;
   out_6961192590068817781[71] = 0;
   out_6961192590068817781[72] = 0;
   out_6961192590068817781[73] = 0;
   out_6961192590068817781[74] = 0;
   out_6961192590068817781[75] = 0;
   out_6961192590068817781[76] = 1;
   out_6961192590068817781[77] = 0;
   out_6961192590068817781[78] = 0;
   out_6961192590068817781[79] = 0;
   out_6961192590068817781[80] = 0;
   out_6961192590068817781[81] = 0;
   out_6961192590068817781[82] = 0;
   out_6961192590068817781[83] = 0;
   out_6961192590068817781[84] = 0;
   out_6961192590068817781[85] = dt;
   out_6961192590068817781[86] = 0;
   out_6961192590068817781[87] = 0;
   out_6961192590068817781[88] = 0;
   out_6961192590068817781[89] = 0;
   out_6961192590068817781[90] = 0;
   out_6961192590068817781[91] = 0;
   out_6961192590068817781[92] = 0;
   out_6961192590068817781[93] = 0;
   out_6961192590068817781[94] = 0;
   out_6961192590068817781[95] = 1;
   out_6961192590068817781[96] = 0;
   out_6961192590068817781[97] = 0;
   out_6961192590068817781[98] = 0;
   out_6961192590068817781[99] = 0;
   out_6961192590068817781[100] = 0;
   out_6961192590068817781[101] = 0;
   out_6961192590068817781[102] = 0;
   out_6961192590068817781[103] = 0;
   out_6961192590068817781[104] = dt;
   out_6961192590068817781[105] = 0;
   out_6961192590068817781[106] = 0;
   out_6961192590068817781[107] = 0;
   out_6961192590068817781[108] = 0;
   out_6961192590068817781[109] = 0;
   out_6961192590068817781[110] = 0;
   out_6961192590068817781[111] = 0;
   out_6961192590068817781[112] = 0;
   out_6961192590068817781[113] = 0;
   out_6961192590068817781[114] = 1;
   out_6961192590068817781[115] = 0;
   out_6961192590068817781[116] = 0;
   out_6961192590068817781[117] = 0;
   out_6961192590068817781[118] = 0;
   out_6961192590068817781[119] = 0;
   out_6961192590068817781[120] = 0;
   out_6961192590068817781[121] = 0;
   out_6961192590068817781[122] = 0;
   out_6961192590068817781[123] = 0;
   out_6961192590068817781[124] = 0;
   out_6961192590068817781[125] = 0;
   out_6961192590068817781[126] = 0;
   out_6961192590068817781[127] = 0;
   out_6961192590068817781[128] = 0;
   out_6961192590068817781[129] = 0;
   out_6961192590068817781[130] = 0;
   out_6961192590068817781[131] = 0;
   out_6961192590068817781[132] = 0;
   out_6961192590068817781[133] = 1;
   out_6961192590068817781[134] = 0;
   out_6961192590068817781[135] = 0;
   out_6961192590068817781[136] = 0;
   out_6961192590068817781[137] = 0;
   out_6961192590068817781[138] = 0;
   out_6961192590068817781[139] = 0;
   out_6961192590068817781[140] = 0;
   out_6961192590068817781[141] = 0;
   out_6961192590068817781[142] = 0;
   out_6961192590068817781[143] = 0;
   out_6961192590068817781[144] = 0;
   out_6961192590068817781[145] = 0;
   out_6961192590068817781[146] = 0;
   out_6961192590068817781[147] = 0;
   out_6961192590068817781[148] = 0;
   out_6961192590068817781[149] = 0;
   out_6961192590068817781[150] = 0;
   out_6961192590068817781[151] = 0;
   out_6961192590068817781[152] = 1;
   out_6961192590068817781[153] = 0;
   out_6961192590068817781[154] = 0;
   out_6961192590068817781[155] = 0;
   out_6961192590068817781[156] = 0;
   out_6961192590068817781[157] = 0;
   out_6961192590068817781[158] = 0;
   out_6961192590068817781[159] = 0;
   out_6961192590068817781[160] = 0;
   out_6961192590068817781[161] = 0;
   out_6961192590068817781[162] = 0;
   out_6961192590068817781[163] = 0;
   out_6961192590068817781[164] = 0;
   out_6961192590068817781[165] = 0;
   out_6961192590068817781[166] = 0;
   out_6961192590068817781[167] = 0;
   out_6961192590068817781[168] = 0;
   out_6961192590068817781[169] = 0;
   out_6961192590068817781[170] = 0;
   out_6961192590068817781[171] = 1;
   out_6961192590068817781[172] = 0;
   out_6961192590068817781[173] = 0;
   out_6961192590068817781[174] = 0;
   out_6961192590068817781[175] = 0;
   out_6961192590068817781[176] = 0;
   out_6961192590068817781[177] = 0;
   out_6961192590068817781[178] = 0;
   out_6961192590068817781[179] = 0;
   out_6961192590068817781[180] = 0;
   out_6961192590068817781[181] = 0;
   out_6961192590068817781[182] = 0;
   out_6961192590068817781[183] = 0;
   out_6961192590068817781[184] = 0;
   out_6961192590068817781[185] = 0;
   out_6961192590068817781[186] = 0;
   out_6961192590068817781[187] = 0;
   out_6961192590068817781[188] = 0;
   out_6961192590068817781[189] = 0;
   out_6961192590068817781[190] = 1;
   out_6961192590068817781[191] = 0;
   out_6961192590068817781[192] = 0;
   out_6961192590068817781[193] = 0;
   out_6961192590068817781[194] = 0;
   out_6961192590068817781[195] = 0;
   out_6961192590068817781[196] = 0;
   out_6961192590068817781[197] = 0;
   out_6961192590068817781[198] = 0;
   out_6961192590068817781[199] = 0;
   out_6961192590068817781[200] = 0;
   out_6961192590068817781[201] = 0;
   out_6961192590068817781[202] = 0;
   out_6961192590068817781[203] = 0;
   out_6961192590068817781[204] = 0;
   out_6961192590068817781[205] = 0;
   out_6961192590068817781[206] = 0;
   out_6961192590068817781[207] = 0;
   out_6961192590068817781[208] = 0;
   out_6961192590068817781[209] = 1;
   out_6961192590068817781[210] = 0;
   out_6961192590068817781[211] = 0;
   out_6961192590068817781[212] = 0;
   out_6961192590068817781[213] = 0;
   out_6961192590068817781[214] = 0;
   out_6961192590068817781[215] = 0;
   out_6961192590068817781[216] = 0;
   out_6961192590068817781[217] = 0;
   out_6961192590068817781[218] = 0;
   out_6961192590068817781[219] = 0;
   out_6961192590068817781[220] = 0;
   out_6961192590068817781[221] = 0;
   out_6961192590068817781[222] = 0;
   out_6961192590068817781[223] = 0;
   out_6961192590068817781[224] = 0;
   out_6961192590068817781[225] = 0;
   out_6961192590068817781[226] = 0;
   out_6961192590068817781[227] = 0;
   out_6961192590068817781[228] = 1;
   out_6961192590068817781[229] = 0;
   out_6961192590068817781[230] = 0;
   out_6961192590068817781[231] = 0;
   out_6961192590068817781[232] = 0;
   out_6961192590068817781[233] = 0;
   out_6961192590068817781[234] = 0;
   out_6961192590068817781[235] = 0;
   out_6961192590068817781[236] = 0;
   out_6961192590068817781[237] = 0;
   out_6961192590068817781[238] = 0;
   out_6961192590068817781[239] = 0;
   out_6961192590068817781[240] = 0;
   out_6961192590068817781[241] = 0;
   out_6961192590068817781[242] = 0;
   out_6961192590068817781[243] = 0;
   out_6961192590068817781[244] = 0;
   out_6961192590068817781[245] = 0;
   out_6961192590068817781[246] = 0;
   out_6961192590068817781[247] = 1;
   out_6961192590068817781[248] = 0;
   out_6961192590068817781[249] = 0;
   out_6961192590068817781[250] = 0;
   out_6961192590068817781[251] = 0;
   out_6961192590068817781[252] = 0;
   out_6961192590068817781[253] = 0;
   out_6961192590068817781[254] = 0;
   out_6961192590068817781[255] = 0;
   out_6961192590068817781[256] = 0;
   out_6961192590068817781[257] = 0;
   out_6961192590068817781[258] = 0;
   out_6961192590068817781[259] = 0;
   out_6961192590068817781[260] = 0;
   out_6961192590068817781[261] = 0;
   out_6961192590068817781[262] = 0;
   out_6961192590068817781[263] = 0;
   out_6961192590068817781[264] = 0;
   out_6961192590068817781[265] = 0;
   out_6961192590068817781[266] = 1;
   out_6961192590068817781[267] = 0;
   out_6961192590068817781[268] = 0;
   out_6961192590068817781[269] = 0;
   out_6961192590068817781[270] = 0;
   out_6961192590068817781[271] = 0;
   out_6961192590068817781[272] = 0;
   out_6961192590068817781[273] = 0;
   out_6961192590068817781[274] = 0;
   out_6961192590068817781[275] = 0;
   out_6961192590068817781[276] = 0;
   out_6961192590068817781[277] = 0;
   out_6961192590068817781[278] = 0;
   out_6961192590068817781[279] = 0;
   out_6961192590068817781[280] = 0;
   out_6961192590068817781[281] = 0;
   out_6961192590068817781[282] = 0;
   out_6961192590068817781[283] = 0;
   out_6961192590068817781[284] = 0;
   out_6961192590068817781[285] = 1;
   out_6961192590068817781[286] = 0;
   out_6961192590068817781[287] = 0;
   out_6961192590068817781[288] = 0;
   out_6961192590068817781[289] = 0;
   out_6961192590068817781[290] = 0;
   out_6961192590068817781[291] = 0;
   out_6961192590068817781[292] = 0;
   out_6961192590068817781[293] = 0;
   out_6961192590068817781[294] = 0;
   out_6961192590068817781[295] = 0;
   out_6961192590068817781[296] = 0;
   out_6961192590068817781[297] = 0;
   out_6961192590068817781[298] = 0;
   out_6961192590068817781[299] = 0;
   out_6961192590068817781[300] = 0;
   out_6961192590068817781[301] = 0;
   out_6961192590068817781[302] = 0;
   out_6961192590068817781[303] = 0;
   out_6961192590068817781[304] = 1;
   out_6961192590068817781[305] = 0;
   out_6961192590068817781[306] = 0;
   out_6961192590068817781[307] = 0;
   out_6961192590068817781[308] = 0;
   out_6961192590068817781[309] = 0;
   out_6961192590068817781[310] = 0;
   out_6961192590068817781[311] = 0;
   out_6961192590068817781[312] = 0;
   out_6961192590068817781[313] = 0;
   out_6961192590068817781[314] = 0;
   out_6961192590068817781[315] = 0;
   out_6961192590068817781[316] = 0;
   out_6961192590068817781[317] = 0;
   out_6961192590068817781[318] = 0;
   out_6961192590068817781[319] = 0;
   out_6961192590068817781[320] = 0;
   out_6961192590068817781[321] = 0;
   out_6961192590068817781[322] = 0;
   out_6961192590068817781[323] = 1;
}
void h_4(double *state, double *unused, double *out_4316151876385378585) {
   out_4316151876385378585[0] = state[6] + state[9];
   out_4316151876385378585[1] = state[7] + state[10];
   out_4316151876385378585[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_2672320983204381838) {
   out_2672320983204381838[0] = 0;
   out_2672320983204381838[1] = 0;
   out_2672320983204381838[2] = 0;
   out_2672320983204381838[3] = 0;
   out_2672320983204381838[4] = 0;
   out_2672320983204381838[5] = 0;
   out_2672320983204381838[6] = 1;
   out_2672320983204381838[7] = 0;
   out_2672320983204381838[8] = 0;
   out_2672320983204381838[9] = 1;
   out_2672320983204381838[10] = 0;
   out_2672320983204381838[11] = 0;
   out_2672320983204381838[12] = 0;
   out_2672320983204381838[13] = 0;
   out_2672320983204381838[14] = 0;
   out_2672320983204381838[15] = 0;
   out_2672320983204381838[16] = 0;
   out_2672320983204381838[17] = 0;
   out_2672320983204381838[18] = 0;
   out_2672320983204381838[19] = 0;
   out_2672320983204381838[20] = 0;
   out_2672320983204381838[21] = 0;
   out_2672320983204381838[22] = 0;
   out_2672320983204381838[23] = 0;
   out_2672320983204381838[24] = 0;
   out_2672320983204381838[25] = 1;
   out_2672320983204381838[26] = 0;
   out_2672320983204381838[27] = 0;
   out_2672320983204381838[28] = 1;
   out_2672320983204381838[29] = 0;
   out_2672320983204381838[30] = 0;
   out_2672320983204381838[31] = 0;
   out_2672320983204381838[32] = 0;
   out_2672320983204381838[33] = 0;
   out_2672320983204381838[34] = 0;
   out_2672320983204381838[35] = 0;
   out_2672320983204381838[36] = 0;
   out_2672320983204381838[37] = 0;
   out_2672320983204381838[38] = 0;
   out_2672320983204381838[39] = 0;
   out_2672320983204381838[40] = 0;
   out_2672320983204381838[41] = 0;
   out_2672320983204381838[42] = 0;
   out_2672320983204381838[43] = 0;
   out_2672320983204381838[44] = 1;
   out_2672320983204381838[45] = 0;
   out_2672320983204381838[46] = 0;
   out_2672320983204381838[47] = 1;
   out_2672320983204381838[48] = 0;
   out_2672320983204381838[49] = 0;
   out_2672320983204381838[50] = 0;
   out_2672320983204381838[51] = 0;
   out_2672320983204381838[52] = 0;
   out_2672320983204381838[53] = 0;
}
void h_10(double *state, double *unused, double *out_2925814787623901053) {
   out_2925814787623901053[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_2925814787623901053[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_2925814787623901053[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_6143953899361439027) {
   out_6143953899361439027[0] = 0;
   out_6143953899361439027[1] = 9.8100000000000005*cos(state[1]);
   out_6143953899361439027[2] = 0;
   out_6143953899361439027[3] = 0;
   out_6143953899361439027[4] = -state[8];
   out_6143953899361439027[5] = state[7];
   out_6143953899361439027[6] = 0;
   out_6143953899361439027[7] = state[5];
   out_6143953899361439027[8] = -state[4];
   out_6143953899361439027[9] = 0;
   out_6143953899361439027[10] = 0;
   out_6143953899361439027[11] = 0;
   out_6143953899361439027[12] = 1;
   out_6143953899361439027[13] = 0;
   out_6143953899361439027[14] = 0;
   out_6143953899361439027[15] = 1;
   out_6143953899361439027[16] = 0;
   out_6143953899361439027[17] = 0;
   out_6143953899361439027[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_6143953899361439027[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_6143953899361439027[20] = 0;
   out_6143953899361439027[21] = state[8];
   out_6143953899361439027[22] = 0;
   out_6143953899361439027[23] = -state[6];
   out_6143953899361439027[24] = -state[5];
   out_6143953899361439027[25] = 0;
   out_6143953899361439027[26] = state[3];
   out_6143953899361439027[27] = 0;
   out_6143953899361439027[28] = 0;
   out_6143953899361439027[29] = 0;
   out_6143953899361439027[30] = 0;
   out_6143953899361439027[31] = 1;
   out_6143953899361439027[32] = 0;
   out_6143953899361439027[33] = 0;
   out_6143953899361439027[34] = 1;
   out_6143953899361439027[35] = 0;
   out_6143953899361439027[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_6143953899361439027[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_6143953899361439027[38] = 0;
   out_6143953899361439027[39] = -state[7];
   out_6143953899361439027[40] = state[6];
   out_6143953899361439027[41] = 0;
   out_6143953899361439027[42] = state[4];
   out_6143953899361439027[43] = -state[3];
   out_6143953899361439027[44] = 0;
   out_6143953899361439027[45] = 0;
   out_6143953899361439027[46] = 0;
   out_6143953899361439027[47] = 0;
   out_6143953899361439027[48] = 0;
   out_6143953899361439027[49] = 0;
   out_6143953899361439027[50] = 1;
   out_6143953899361439027[51] = 0;
   out_6143953899361439027[52] = 0;
   out_6143953899361439027[53] = 1;
}
void h_13(double *state, double *unused, double *out_8822311255157966507) {
   out_8822311255157966507[0] = state[3];
   out_8822311255157966507[1] = state[4];
   out_8822311255157966507[2] = state[5];
}
void H_13(double *state, double *unused, double *out_5884594808536714639) {
   out_5884594808536714639[0] = 0;
   out_5884594808536714639[1] = 0;
   out_5884594808536714639[2] = 0;
   out_5884594808536714639[3] = 1;
   out_5884594808536714639[4] = 0;
   out_5884594808536714639[5] = 0;
   out_5884594808536714639[6] = 0;
   out_5884594808536714639[7] = 0;
   out_5884594808536714639[8] = 0;
   out_5884594808536714639[9] = 0;
   out_5884594808536714639[10] = 0;
   out_5884594808536714639[11] = 0;
   out_5884594808536714639[12] = 0;
   out_5884594808536714639[13] = 0;
   out_5884594808536714639[14] = 0;
   out_5884594808536714639[15] = 0;
   out_5884594808536714639[16] = 0;
   out_5884594808536714639[17] = 0;
   out_5884594808536714639[18] = 0;
   out_5884594808536714639[19] = 0;
   out_5884594808536714639[20] = 0;
   out_5884594808536714639[21] = 0;
   out_5884594808536714639[22] = 1;
   out_5884594808536714639[23] = 0;
   out_5884594808536714639[24] = 0;
   out_5884594808536714639[25] = 0;
   out_5884594808536714639[26] = 0;
   out_5884594808536714639[27] = 0;
   out_5884594808536714639[28] = 0;
   out_5884594808536714639[29] = 0;
   out_5884594808536714639[30] = 0;
   out_5884594808536714639[31] = 0;
   out_5884594808536714639[32] = 0;
   out_5884594808536714639[33] = 0;
   out_5884594808536714639[34] = 0;
   out_5884594808536714639[35] = 0;
   out_5884594808536714639[36] = 0;
   out_5884594808536714639[37] = 0;
   out_5884594808536714639[38] = 0;
   out_5884594808536714639[39] = 0;
   out_5884594808536714639[40] = 0;
   out_5884594808536714639[41] = 1;
   out_5884594808536714639[42] = 0;
   out_5884594808536714639[43] = 0;
   out_5884594808536714639[44] = 0;
   out_5884594808536714639[45] = 0;
   out_5884594808536714639[46] = 0;
   out_5884594808536714639[47] = 0;
   out_5884594808536714639[48] = 0;
   out_5884594808536714639[49] = 0;
   out_5884594808536714639[50] = 0;
   out_5884594808536714639[51] = 0;
   out_5884594808536714639[52] = 0;
   out_5884594808536714639[53] = 0;
}
void h_14(double *state, double *unused, double *out_293817740766290370) {
   out_293817740766290370[0] = state[6];
   out_293817740766290370[1] = state[7];
   out_293817740766290370[2] = state[8];
}
void H_14(double *state, double *unused, double *out_6635561839543866367) {
   out_6635561839543866367[0] = 0;
   out_6635561839543866367[1] = 0;
   out_6635561839543866367[2] = 0;
   out_6635561839543866367[3] = 0;
   out_6635561839543866367[4] = 0;
   out_6635561839543866367[5] = 0;
   out_6635561839543866367[6] = 1;
   out_6635561839543866367[7] = 0;
   out_6635561839543866367[8] = 0;
   out_6635561839543866367[9] = 0;
   out_6635561839543866367[10] = 0;
   out_6635561839543866367[11] = 0;
   out_6635561839543866367[12] = 0;
   out_6635561839543866367[13] = 0;
   out_6635561839543866367[14] = 0;
   out_6635561839543866367[15] = 0;
   out_6635561839543866367[16] = 0;
   out_6635561839543866367[17] = 0;
   out_6635561839543866367[18] = 0;
   out_6635561839543866367[19] = 0;
   out_6635561839543866367[20] = 0;
   out_6635561839543866367[21] = 0;
   out_6635561839543866367[22] = 0;
   out_6635561839543866367[23] = 0;
   out_6635561839543866367[24] = 0;
   out_6635561839543866367[25] = 1;
   out_6635561839543866367[26] = 0;
   out_6635561839543866367[27] = 0;
   out_6635561839543866367[28] = 0;
   out_6635561839543866367[29] = 0;
   out_6635561839543866367[30] = 0;
   out_6635561839543866367[31] = 0;
   out_6635561839543866367[32] = 0;
   out_6635561839543866367[33] = 0;
   out_6635561839543866367[34] = 0;
   out_6635561839543866367[35] = 0;
   out_6635561839543866367[36] = 0;
   out_6635561839543866367[37] = 0;
   out_6635561839543866367[38] = 0;
   out_6635561839543866367[39] = 0;
   out_6635561839543866367[40] = 0;
   out_6635561839543866367[41] = 0;
   out_6635561839543866367[42] = 0;
   out_6635561839543866367[43] = 0;
   out_6635561839543866367[44] = 1;
   out_6635561839543866367[45] = 0;
   out_6635561839543866367[46] = 0;
   out_6635561839543866367[47] = 0;
   out_6635561839543866367[48] = 0;
   out_6635561839543866367[49] = 0;
   out_6635561839543866367[50] = 0;
   out_6635561839543866367[51] = 0;
   out_6635561839543866367[52] = 0;
   out_6635561839543866367[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_7150551631592866018) {
  err_fun(nom_x, delta_x, out_7150551631592866018);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_2794293729781716576) {
  inv_err_fun(nom_x, true_x, out_2794293729781716576);
}
void pose_H_mod_fun(double *state, double *out_8150336989101570986) {
  H_mod_fun(state, out_8150336989101570986);
}
void pose_f_fun(double *state, double dt, double *out_7007205599395941006) {
  f_fun(state,  dt, out_7007205599395941006);
}
void pose_F_fun(double *state, double dt, double *out_6961192590068817781) {
  F_fun(state,  dt, out_6961192590068817781);
}
void pose_h_4(double *state, double *unused, double *out_4316151876385378585) {
  h_4(state, unused, out_4316151876385378585);
}
void pose_H_4(double *state, double *unused, double *out_2672320983204381838) {
  H_4(state, unused, out_2672320983204381838);
}
void pose_h_10(double *state, double *unused, double *out_2925814787623901053) {
  h_10(state, unused, out_2925814787623901053);
}
void pose_H_10(double *state, double *unused, double *out_6143953899361439027) {
  H_10(state, unused, out_6143953899361439027);
}
void pose_h_13(double *state, double *unused, double *out_8822311255157966507) {
  h_13(state, unused, out_8822311255157966507);
}
void pose_H_13(double *state, double *unused, double *out_5884594808536714639) {
  H_13(state, unused, out_5884594808536714639);
}
void pose_h_14(double *state, double *unused, double *out_293817740766290370) {
  h_14(state, unused, out_293817740766290370);
}
void pose_H_14(double *state, double *unused, double *out_6635561839543866367) {
  H_14(state, unused, out_6635561839543866367);
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
