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
void err_fun(double *nom_x, double *delta_x, double *out_4902955493032499892) {
   out_4902955493032499892[0] = delta_x[0] + nom_x[0];
   out_4902955493032499892[1] = delta_x[1] + nom_x[1];
   out_4902955493032499892[2] = delta_x[2] + nom_x[2];
   out_4902955493032499892[3] = delta_x[3] + nom_x[3];
   out_4902955493032499892[4] = delta_x[4] + nom_x[4];
   out_4902955493032499892[5] = delta_x[5] + nom_x[5];
   out_4902955493032499892[6] = delta_x[6] + nom_x[6];
   out_4902955493032499892[7] = delta_x[7] + nom_x[7];
   out_4902955493032499892[8] = delta_x[8] + nom_x[8];
   out_4902955493032499892[9] = delta_x[9] + nom_x[9];
   out_4902955493032499892[10] = delta_x[10] + nom_x[10];
   out_4902955493032499892[11] = delta_x[11] + nom_x[11];
   out_4902955493032499892[12] = delta_x[12] + nom_x[12];
   out_4902955493032499892[13] = delta_x[13] + nom_x[13];
   out_4902955493032499892[14] = delta_x[14] + nom_x[14];
   out_4902955493032499892[15] = delta_x[15] + nom_x[15];
   out_4902955493032499892[16] = delta_x[16] + nom_x[16];
   out_4902955493032499892[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1560256026778240052) {
   out_1560256026778240052[0] = -nom_x[0] + true_x[0];
   out_1560256026778240052[1] = -nom_x[1] + true_x[1];
   out_1560256026778240052[2] = -nom_x[2] + true_x[2];
   out_1560256026778240052[3] = -nom_x[3] + true_x[3];
   out_1560256026778240052[4] = -nom_x[4] + true_x[4];
   out_1560256026778240052[5] = -nom_x[5] + true_x[5];
   out_1560256026778240052[6] = -nom_x[6] + true_x[6];
   out_1560256026778240052[7] = -nom_x[7] + true_x[7];
   out_1560256026778240052[8] = -nom_x[8] + true_x[8];
   out_1560256026778240052[9] = -nom_x[9] + true_x[9];
   out_1560256026778240052[10] = -nom_x[10] + true_x[10];
   out_1560256026778240052[11] = -nom_x[11] + true_x[11];
   out_1560256026778240052[12] = -nom_x[12] + true_x[12];
   out_1560256026778240052[13] = -nom_x[13] + true_x[13];
   out_1560256026778240052[14] = -nom_x[14] + true_x[14];
   out_1560256026778240052[15] = -nom_x[15] + true_x[15];
   out_1560256026778240052[16] = -nom_x[16] + true_x[16];
   out_1560256026778240052[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_1285602415841124817) {
   out_1285602415841124817[0] = 1.0;
   out_1285602415841124817[1] = 0.0;
   out_1285602415841124817[2] = 0.0;
   out_1285602415841124817[3] = 0.0;
   out_1285602415841124817[4] = 0.0;
   out_1285602415841124817[5] = 0.0;
   out_1285602415841124817[6] = 0.0;
   out_1285602415841124817[7] = 0.0;
   out_1285602415841124817[8] = 0.0;
   out_1285602415841124817[9] = 0.0;
   out_1285602415841124817[10] = 0.0;
   out_1285602415841124817[11] = 0.0;
   out_1285602415841124817[12] = 0.0;
   out_1285602415841124817[13] = 0.0;
   out_1285602415841124817[14] = 0.0;
   out_1285602415841124817[15] = 0.0;
   out_1285602415841124817[16] = 0.0;
   out_1285602415841124817[17] = 0.0;
   out_1285602415841124817[18] = 0.0;
   out_1285602415841124817[19] = 1.0;
   out_1285602415841124817[20] = 0.0;
   out_1285602415841124817[21] = 0.0;
   out_1285602415841124817[22] = 0.0;
   out_1285602415841124817[23] = 0.0;
   out_1285602415841124817[24] = 0.0;
   out_1285602415841124817[25] = 0.0;
   out_1285602415841124817[26] = 0.0;
   out_1285602415841124817[27] = 0.0;
   out_1285602415841124817[28] = 0.0;
   out_1285602415841124817[29] = 0.0;
   out_1285602415841124817[30] = 0.0;
   out_1285602415841124817[31] = 0.0;
   out_1285602415841124817[32] = 0.0;
   out_1285602415841124817[33] = 0.0;
   out_1285602415841124817[34] = 0.0;
   out_1285602415841124817[35] = 0.0;
   out_1285602415841124817[36] = 0.0;
   out_1285602415841124817[37] = 0.0;
   out_1285602415841124817[38] = 1.0;
   out_1285602415841124817[39] = 0.0;
   out_1285602415841124817[40] = 0.0;
   out_1285602415841124817[41] = 0.0;
   out_1285602415841124817[42] = 0.0;
   out_1285602415841124817[43] = 0.0;
   out_1285602415841124817[44] = 0.0;
   out_1285602415841124817[45] = 0.0;
   out_1285602415841124817[46] = 0.0;
   out_1285602415841124817[47] = 0.0;
   out_1285602415841124817[48] = 0.0;
   out_1285602415841124817[49] = 0.0;
   out_1285602415841124817[50] = 0.0;
   out_1285602415841124817[51] = 0.0;
   out_1285602415841124817[52] = 0.0;
   out_1285602415841124817[53] = 0.0;
   out_1285602415841124817[54] = 0.0;
   out_1285602415841124817[55] = 0.0;
   out_1285602415841124817[56] = 0.0;
   out_1285602415841124817[57] = 1.0;
   out_1285602415841124817[58] = 0.0;
   out_1285602415841124817[59] = 0.0;
   out_1285602415841124817[60] = 0.0;
   out_1285602415841124817[61] = 0.0;
   out_1285602415841124817[62] = 0.0;
   out_1285602415841124817[63] = 0.0;
   out_1285602415841124817[64] = 0.0;
   out_1285602415841124817[65] = 0.0;
   out_1285602415841124817[66] = 0.0;
   out_1285602415841124817[67] = 0.0;
   out_1285602415841124817[68] = 0.0;
   out_1285602415841124817[69] = 0.0;
   out_1285602415841124817[70] = 0.0;
   out_1285602415841124817[71] = 0.0;
   out_1285602415841124817[72] = 0.0;
   out_1285602415841124817[73] = 0.0;
   out_1285602415841124817[74] = 0.0;
   out_1285602415841124817[75] = 0.0;
   out_1285602415841124817[76] = 1.0;
   out_1285602415841124817[77] = 0.0;
   out_1285602415841124817[78] = 0.0;
   out_1285602415841124817[79] = 0.0;
   out_1285602415841124817[80] = 0.0;
   out_1285602415841124817[81] = 0.0;
   out_1285602415841124817[82] = 0.0;
   out_1285602415841124817[83] = 0.0;
   out_1285602415841124817[84] = 0.0;
   out_1285602415841124817[85] = 0.0;
   out_1285602415841124817[86] = 0.0;
   out_1285602415841124817[87] = 0.0;
   out_1285602415841124817[88] = 0.0;
   out_1285602415841124817[89] = 0.0;
   out_1285602415841124817[90] = 0.0;
   out_1285602415841124817[91] = 0.0;
   out_1285602415841124817[92] = 0.0;
   out_1285602415841124817[93] = 0.0;
   out_1285602415841124817[94] = 0.0;
   out_1285602415841124817[95] = 1.0;
   out_1285602415841124817[96] = 0.0;
   out_1285602415841124817[97] = 0.0;
   out_1285602415841124817[98] = 0.0;
   out_1285602415841124817[99] = 0.0;
   out_1285602415841124817[100] = 0.0;
   out_1285602415841124817[101] = 0.0;
   out_1285602415841124817[102] = 0.0;
   out_1285602415841124817[103] = 0.0;
   out_1285602415841124817[104] = 0.0;
   out_1285602415841124817[105] = 0.0;
   out_1285602415841124817[106] = 0.0;
   out_1285602415841124817[107] = 0.0;
   out_1285602415841124817[108] = 0.0;
   out_1285602415841124817[109] = 0.0;
   out_1285602415841124817[110] = 0.0;
   out_1285602415841124817[111] = 0.0;
   out_1285602415841124817[112] = 0.0;
   out_1285602415841124817[113] = 0.0;
   out_1285602415841124817[114] = 1.0;
   out_1285602415841124817[115] = 0.0;
   out_1285602415841124817[116] = 0.0;
   out_1285602415841124817[117] = 0.0;
   out_1285602415841124817[118] = 0.0;
   out_1285602415841124817[119] = 0.0;
   out_1285602415841124817[120] = 0.0;
   out_1285602415841124817[121] = 0.0;
   out_1285602415841124817[122] = 0.0;
   out_1285602415841124817[123] = 0.0;
   out_1285602415841124817[124] = 0.0;
   out_1285602415841124817[125] = 0.0;
   out_1285602415841124817[126] = 0.0;
   out_1285602415841124817[127] = 0.0;
   out_1285602415841124817[128] = 0.0;
   out_1285602415841124817[129] = 0.0;
   out_1285602415841124817[130] = 0.0;
   out_1285602415841124817[131] = 0.0;
   out_1285602415841124817[132] = 0.0;
   out_1285602415841124817[133] = 1.0;
   out_1285602415841124817[134] = 0.0;
   out_1285602415841124817[135] = 0.0;
   out_1285602415841124817[136] = 0.0;
   out_1285602415841124817[137] = 0.0;
   out_1285602415841124817[138] = 0.0;
   out_1285602415841124817[139] = 0.0;
   out_1285602415841124817[140] = 0.0;
   out_1285602415841124817[141] = 0.0;
   out_1285602415841124817[142] = 0.0;
   out_1285602415841124817[143] = 0.0;
   out_1285602415841124817[144] = 0.0;
   out_1285602415841124817[145] = 0.0;
   out_1285602415841124817[146] = 0.0;
   out_1285602415841124817[147] = 0.0;
   out_1285602415841124817[148] = 0.0;
   out_1285602415841124817[149] = 0.0;
   out_1285602415841124817[150] = 0.0;
   out_1285602415841124817[151] = 0.0;
   out_1285602415841124817[152] = 1.0;
   out_1285602415841124817[153] = 0.0;
   out_1285602415841124817[154] = 0.0;
   out_1285602415841124817[155] = 0.0;
   out_1285602415841124817[156] = 0.0;
   out_1285602415841124817[157] = 0.0;
   out_1285602415841124817[158] = 0.0;
   out_1285602415841124817[159] = 0.0;
   out_1285602415841124817[160] = 0.0;
   out_1285602415841124817[161] = 0.0;
   out_1285602415841124817[162] = 0.0;
   out_1285602415841124817[163] = 0.0;
   out_1285602415841124817[164] = 0.0;
   out_1285602415841124817[165] = 0.0;
   out_1285602415841124817[166] = 0.0;
   out_1285602415841124817[167] = 0.0;
   out_1285602415841124817[168] = 0.0;
   out_1285602415841124817[169] = 0.0;
   out_1285602415841124817[170] = 0.0;
   out_1285602415841124817[171] = 1.0;
   out_1285602415841124817[172] = 0.0;
   out_1285602415841124817[173] = 0.0;
   out_1285602415841124817[174] = 0.0;
   out_1285602415841124817[175] = 0.0;
   out_1285602415841124817[176] = 0.0;
   out_1285602415841124817[177] = 0.0;
   out_1285602415841124817[178] = 0.0;
   out_1285602415841124817[179] = 0.0;
   out_1285602415841124817[180] = 0.0;
   out_1285602415841124817[181] = 0.0;
   out_1285602415841124817[182] = 0.0;
   out_1285602415841124817[183] = 0.0;
   out_1285602415841124817[184] = 0.0;
   out_1285602415841124817[185] = 0.0;
   out_1285602415841124817[186] = 0.0;
   out_1285602415841124817[187] = 0.0;
   out_1285602415841124817[188] = 0.0;
   out_1285602415841124817[189] = 0.0;
   out_1285602415841124817[190] = 1.0;
   out_1285602415841124817[191] = 0.0;
   out_1285602415841124817[192] = 0.0;
   out_1285602415841124817[193] = 0.0;
   out_1285602415841124817[194] = 0.0;
   out_1285602415841124817[195] = 0.0;
   out_1285602415841124817[196] = 0.0;
   out_1285602415841124817[197] = 0.0;
   out_1285602415841124817[198] = 0.0;
   out_1285602415841124817[199] = 0.0;
   out_1285602415841124817[200] = 0.0;
   out_1285602415841124817[201] = 0.0;
   out_1285602415841124817[202] = 0.0;
   out_1285602415841124817[203] = 0.0;
   out_1285602415841124817[204] = 0.0;
   out_1285602415841124817[205] = 0.0;
   out_1285602415841124817[206] = 0.0;
   out_1285602415841124817[207] = 0.0;
   out_1285602415841124817[208] = 0.0;
   out_1285602415841124817[209] = 1.0;
   out_1285602415841124817[210] = 0.0;
   out_1285602415841124817[211] = 0.0;
   out_1285602415841124817[212] = 0.0;
   out_1285602415841124817[213] = 0.0;
   out_1285602415841124817[214] = 0.0;
   out_1285602415841124817[215] = 0.0;
   out_1285602415841124817[216] = 0.0;
   out_1285602415841124817[217] = 0.0;
   out_1285602415841124817[218] = 0.0;
   out_1285602415841124817[219] = 0.0;
   out_1285602415841124817[220] = 0.0;
   out_1285602415841124817[221] = 0.0;
   out_1285602415841124817[222] = 0.0;
   out_1285602415841124817[223] = 0.0;
   out_1285602415841124817[224] = 0.0;
   out_1285602415841124817[225] = 0.0;
   out_1285602415841124817[226] = 0.0;
   out_1285602415841124817[227] = 0.0;
   out_1285602415841124817[228] = 1.0;
   out_1285602415841124817[229] = 0.0;
   out_1285602415841124817[230] = 0.0;
   out_1285602415841124817[231] = 0.0;
   out_1285602415841124817[232] = 0.0;
   out_1285602415841124817[233] = 0.0;
   out_1285602415841124817[234] = 0.0;
   out_1285602415841124817[235] = 0.0;
   out_1285602415841124817[236] = 0.0;
   out_1285602415841124817[237] = 0.0;
   out_1285602415841124817[238] = 0.0;
   out_1285602415841124817[239] = 0.0;
   out_1285602415841124817[240] = 0.0;
   out_1285602415841124817[241] = 0.0;
   out_1285602415841124817[242] = 0.0;
   out_1285602415841124817[243] = 0.0;
   out_1285602415841124817[244] = 0.0;
   out_1285602415841124817[245] = 0.0;
   out_1285602415841124817[246] = 0.0;
   out_1285602415841124817[247] = 1.0;
   out_1285602415841124817[248] = 0.0;
   out_1285602415841124817[249] = 0.0;
   out_1285602415841124817[250] = 0.0;
   out_1285602415841124817[251] = 0.0;
   out_1285602415841124817[252] = 0.0;
   out_1285602415841124817[253] = 0.0;
   out_1285602415841124817[254] = 0.0;
   out_1285602415841124817[255] = 0.0;
   out_1285602415841124817[256] = 0.0;
   out_1285602415841124817[257] = 0.0;
   out_1285602415841124817[258] = 0.0;
   out_1285602415841124817[259] = 0.0;
   out_1285602415841124817[260] = 0.0;
   out_1285602415841124817[261] = 0.0;
   out_1285602415841124817[262] = 0.0;
   out_1285602415841124817[263] = 0.0;
   out_1285602415841124817[264] = 0.0;
   out_1285602415841124817[265] = 0.0;
   out_1285602415841124817[266] = 1.0;
   out_1285602415841124817[267] = 0.0;
   out_1285602415841124817[268] = 0.0;
   out_1285602415841124817[269] = 0.0;
   out_1285602415841124817[270] = 0.0;
   out_1285602415841124817[271] = 0.0;
   out_1285602415841124817[272] = 0.0;
   out_1285602415841124817[273] = 0.0;
   out_1285602415841124817[274] = 0.0;
   out_1285602415841124817[275] = 0.0;
   out_1285602415841124817[276] = 0.0;
   out_1285602415841124817[277] = 0.0;
   out_1285602415841124817[278] = 0.0;
   out_1285602415841124817[279] = 0.0;
   out_1285602415841124817[280] = 0.0;
   out_1285602415841124817[281] = 0.0;
   out_1285602415841124817[282] = 0.0;
   out_1285602415841124817[283] = 0.0;
   out_1285602415841124817[284] = 0.0;
   out_1285602415841124817[285] = 1.0;
   out_1285602415841124817[286] = 0.0;
   out_1285602415841124817[287] = 0.0;
   out_1285602415841124817[288] = 0.0;
   out_1285602415841124817[289] = 0.0;
   out_1285602415841124817[290] = 0.0;
   out_1285602415841124817[291] = 0.0;
   out_1285602415841124817[292] = 0.0;
   out_1285602415841124817[293] = 0.0;
   out_1285602415841124817[294] = 0.0;
   out_1285602415841124817[295] = 0.0;
   out_1285602415841124817[296] = 0.0;
   out_1285602415841124817[297] = 0.0;
   out_1285602415841124817[298] = 0.0;
   out_1285602415841124817[299] = 0.0;
   out_1285602415841124817[300] = 0.0;
   out_1285602415841124817[301] = 0.0;
   out_1285602415841124817[302] = 0.0;
   out_1285602415841124817[303] = 0.0;
   out_1285602415841124817[304] = 1.0;
   out_1285602415841124817[305] = 0.0;
   out_1285602415841124817[306] = 0.0;
   out_1285602415841124817[307] = 0.0;
   out_1285602415841124817[308] = 0.0;
   out_1285602415841124817[309] = 0.0;
   out_1285602415841124817[310] = 0.0;
   out_1285602415841124817[311] = 0.0;
   out_1285602415841124817[312] = 0.0;
   out_1285602415841124817[313] = 0.0;
   out_1285602415841124817[314] = 0.0;
   out_1285602415841124817[315] = 0.0;
   out_1285602415841124817[316] = 0.0;
   out_1285602415841124817[317] = 0.0;
   out_1285602415841124817[318] = 0.0;
   out_1285602415841124817[319] = 0.0;
   out_1285602415841124817[320] = 0.0;
   out_1285602415841124817[321] = 0.0;
   out_1285602415841124817[322] = 0.0;
   out_1285602415841124817[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_1401742083845182998) {
   out_1401742083845182998[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_1401742083845182998[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_1401742083845182998[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_1401742083845182998[3] = dt*state[12] + state[3];
   out_1401742083845182998[4] = dt*state[13] + state[4];
   out_1401742083845182998[5] = dt*state[14] + state[5];
   out_1401742083845182998[6] = state[6];
   out_1401742083845182998[7] = state[7];
   out_1401742083845182998[8] = state[8];
   out_1401742083845182998[9] = state[9];
   out_1401742083845182998[10] = state[10];
   out_1401742083845182998[11] = state[11];
   out_1401742083845182998[12] = state[12];
   out_1401742083845182998[13] = state[13];
   out_1401742083845182998[14] = state[14];
   out_1401742083845182998[15] = state[15];
   out_1401742083845182998[16] = state[16];
   out_1401742083845182998[17] = state[17];
}
void F_fun(double *state, double dt, double *out_5803079463852351769) {
   out_5803079463852351769[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5803079463852351769[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5803079463852351769[2] = 0;
   out_5803079463852351769[3] = 0;
   out_5803079463852351769[4] = 0;
   out_5803079463852351769[5] = 0;
   out_5803079463852351769[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5803079463852351769[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5803079463852351769[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5803079463852351769[9] = 0;
   out_5803079463852351769[10] = 0;
   out_5803079463852351769[11] = 0;
   out_5803079463852351769[12] = 0;
   out_5803079463852351769[13] = 0;
   out_5803079463852351769[14] = 0;
   out_5803079463852351769[15] = 0;
   out_5803079463852351769[16] = 0;
   out_5803079463852351769[17] = 0;
   out_5803079463852351769[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5803079463852351769[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5803079463852351769[20] = 0;
   out_5803079463852351769[21] = 0;
   out_5803079463852351769[22] = 0;
   out_5803079463852351769[23] = 0;
   out_5803079463852351769[24] = 0;
   out_5803079463852351769[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5803079463852351769[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5803079463852351769[27] = 0;
   out_5803079463852351769[28] = 0;
   out_5803079463852351769[29] = 0;
   out_5803079463852351769[30] = 0;
   out_5803079463852351769[31] = 0;
   out_5803079463852351769[32] = 0;
   out_5803079463852351769[33] = 0;
   out_5803079463852351769[34] = 0;
   out_5803079463852351769[35] = 0;
   out_5803079463852351769[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5803079463852351769[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5803079463852351769[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5803079463852351769[39] = 0;
   out_5803079463852351769[40] = 0;
   out_5803079463852351769[41] = 0;
   out_5803079463852351769[42] = 0;
   out_5803079463852351769[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5803079463852351769[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5803079463852351769[45] = 0;
   out_5803079463852351769[46] = 0;
   out_5803079463852351769[47] = 0;
   out_5803079463852351769[48] = 0;
   out_5803079463852351769[49] = 0;
   out_5803079463852351769[50] = 0;
   out_5803079463852351769[51] = 0;
   out_5803079463852351769[52] = 0;
   out_5803079463852351769[53] = 0;
   out_5803079463852351769[54] = 0;
   out_5803079463852351769[55] = 0;
   out_5803079463852351769[56] = 0;
   out_5803079463852351769[57] = 1;
   out_5803079463852351769[58] = 0;
   out_5803079463852351769[59] = 0;
   out_5803079463852351769[60] = 0;
   out_5803079463852351769[61] = 0;
   out_5803079463852351769[62] = 0;
   out_5803079463852351769[63] = 0;
   out_5803079463852351769[64] = 0;
   out_5803079463852351769[65] = 0;
   out_5803079463852351769[66] = dt;
   out_5803079463852351769[67] = 0;
   out_5803079463852351769[68] = 0;
   out_5803079463852351769[69] = 0;
   out_5803079463852351769[70] = 0;
   out_5803079463852351769[71] = 0;
   out_5803079463852351769[72] = 0;
   out_5803079463852351769[73] = 0;
   out_5803079463852351769[74] = 0;
   out_5803079463852351769[75] = 0;
   out_5803079463852351769[76] = 1;
   out_5803079463852351769[77] = 0;
   out_5803079463852351769[78] = 0;
   out_5803079463852351769[79] = 0;
   out_5803079463852351769[80] = 0;
   out_5803079463852351769[81] = 0;
   out_5803079463852351769[82] = 0;
   out_5803079463852351769[83] = 0;
   out_5803079463852351769[84] = 0;
   out_5803079463852351769[85] = dt;
   out_5803079463852351769[86] = 0;
   out_5803079463852351769[87] = 0;
   out_5803079463852351769[88] = 0;
   out_5803079463852351769[89] = 0;
   out_5803079463852351769[90] = 0;
   out_5803079463852351769[91] = 0;
   out_5803079463852351769[92] = 0;
   out_5803079463852351769[93] = 0;
   out_5803079463852351769[94] = 0;
   out_5803079463852351769[95] = 1;
   out_5803079463852351769[96] = 0;
   out_5803079463852351769[97] = 0;
   out_5803079463852351769[98] = 0;
   out_5803079463852351769[99] = 0;
   out_5803079463852351769[100] = 0;
   out_5803079463852351769[101] = 0;
   out_5803079463852351769[102] = 0;
   out_5803079463852351769[103] = 0;
   out_5803079463852351769[104] = dt;
   out_5803079463852351769[105] = 0;
   out_5803079463852351769[106] = 0;
   out_5803079463852351769[107] = 0;
   out_5803079463852351769[108] = 0;
   out_5803079463852351769[109] = 0;
   out_5803079463852351769[110] = 0;
   out_5803079463852351769[111] = 0;
   out_5803079463852351769[112] = 0;
   out_5803079463852351769[113] = 0;
   out_5803079463852351769[114] = 1;
   out_5803079463852351769[115] = 0;
   out_5803079463852351769[116] = 0;
   out_5803079463852351769[117] = 0;
   out_5803079463852351769[118] = 0;
   out_5803079463852351769[119] = 0;
   out_5803079463852351769[120] = 0;
   out_5803079463852351769[121] = 0;
   out_5803079463852351769[122] = 0;
   out_5803079463852351769[123] = 0;
   out_5803079463852351769[124] = 0;
   out_5803079463852351769[125] = 0;
   out_5803079463852351769[126] = 0;
   out_5803079463852351769[127] = 0;
   out_5803079463852351769[128] = 0;
   out_5803079463852351769[129] = 0;
   out_5803079463852351769[130] = 0;
   out_5803079463852351769[131] = 0;
   out_5803079463852351769[132] = 0;
   out_5803079463852351769[133] = 1;
   out_5803079463852351769[134] = 0;
   out_5803079463852351769[135] = 0;
   out_5803079463852351769[136] = 0;
   out_5803079463852351769[137] = 0;
   out_5803079463852351769[138] = 0;
   out_5803079463852351769[139] = 0;
   out_5803079463852351769[140] = 0;
   out_5803079463852351769[141] = 0;
   out_5803079463852351769[142] = 0;
   out_5803079463852351769[143] = 0;
   out_5803079463852351769[144] = 0;
   out_5803079463852351769[145] = 0;
   out_5803079463852351769[146] = 0;
   out_5803079463852351769[147] = 0;
   out_5803079463852351769[148] = 0;
   out_5803079463852351769[149] = 0;
   out_5803079463852351769[150] = 0;
   out_5803079463852351769[151] = 0;
   out_5803079463852351769[152] = 1;
   out_5803079463852351769[153] = 0;
   out_5803079463852351769[154] = 0;
   out_5803079463852351769[155] = 0;
   out_5803079463852351769[156] = 0;
   out_5803079463852351769[157] = 0;
   out_5803079463852351769[158] = 0;
   out_5803079463852351769[159] = 0;
   out_5803079463852351769[160] = 0;
   out_5803079463852351769[161] = 0;
   out_5803079463852351769[162] = 0;
   out_5803079463852351769[163] = 0;
   out_5803079463852351769[164] = 0;
   out_5803079463852351769[165] = 0;
   out_5803079463852351769[166] = 0;
   out_5803079463852351769[167] = 0;
   out_5803079463852351769[168] = 0;
   out_5803079463852351769[169] = 0;
   out_5803079463852351769[170] = 0;
   out_5803079463852351769[171] = 1;
   out_5803079463852351769[172] = 0;
   out_5803079463852351769[173] = 0;
   out_5803079463852351769[174] = 0;
   out_5803079463852351769[175] = 0;
   out_5803079463852351769[176] = 0;
   out_5803079463852351769[177] = 0;
   out_5803079463852351769[178] = 0;
   out_5803079463852351769[179] = 0;
   out_5803079463852351769[180] = 0;
   out_5803079463852351769[181] = 0;
   out_5803079463852351769[182] = 0;
   out_5803079463852351769[183] = 0;
   out_5803079463852351769[184] = 0;
   out_5803079463852351769[185] = 0;
   out_5803079463852351769[186] = 0;
   out_5803079463852351769[187] = 0;
   out_5803079463852351769[188] = 0;
   out_5803079463852351769[189] = 0;
   out_5803079463852351769[190] = 1;
   out_5803079463852351769[191] = 0;
   out_5803079463852351769[192] = 0;
   out_5803079463852351769[193] = 0;
   out_5803079463852351769[194] = 0;
   out_5803079463852351769[195] = 0;
   out_5803079463852351769[196] = 0;
   out_5803079463852351769[197] = 0;
   out_5803079463852351769[198] = 0;
   out_5803079463852351769[199] = 0;
   out_5803079463852351769[200] = 0;
   out_5803079463852351769[201] = 0;
   out_5803079463852351769[202] = 0;
   out_5803079463852351769[203] = 0;
   out_5803079463852351769[204] = 0;
   out_5803079463852351769[205] = 0;
   out_5803079463852351769[206] = 0;
   out_5803079463852351769[207] = 0;
   out_5803079463852351769[208] = 0;
   out_5803079463852351769[209] = 1;
   out_5803079463852351769[210] = 0;
   out_5803079463852351769[211] = 0;
   out_5803079463852351769[212] = 0;
   out_5803079463852351769[213] = 0;
   out_5803079463852351769[214] = 0;
   out_5803079463852351769[215] = 0;
   out_5803079463852351769[216] = 0;
   out_5803079463852351769[217] = 0;
   out_5803079463852351769[218] = 0;
   out_5803079463852351769[219] = 0;
   out_5803079463852351769[220] = 0;
   out_5803079463852351769[221] = 0;
   out_5803079463852351769[222] = 0;
   out_5803079463852351769[223] = 0;
   out_5803079463852351769[224] = 0;
   out_5803079463852351769[225] = 0;
   out_5803079463852351769[226] = 0;
   out_5803079463852351769[227] = 0;
   out_5803079463852351769[228] = 1;
   out_5803079463852351769[229] = 0;
   out_5803079463852351769[230] = 0;
   out_5803079463852351769[231] = 0;
   out_5803079463852351769[232] = 0;
   out_5803079463852351769[233] = 0;
   out_5803079463852351769[234] = 0;
   out_5803079463852351769[235] = 0;
   out_5803079463852351769[236] = 0;
   out_5803079463852351769[237] = 0;
   out_5803079463852351769[238] = 0;
   out_5803079463852351769[239] = 0;
   out_5803079463852351769[240] = 0;
   out_5803079463852351769[241] = 0;
   out_5803079463852351769[242] = 0;
   out_5803079463852351769[243] = 0;
   out_5803079463852351769[244] = 0;
   out_5803079463852351769[245] = 0;
   out_5803079463852351769[246] = 0;
   out_5803079463852351769[247] = 1;
   out_5803079463852351769[248] = 0;
   out_5803079463852351769[249] = 0;
   out_5803079463852351769[250] = 0;
   out_5803079463852351769[251] = 0;
   out_5803079463852351769[252] = 0;
   out_5803079463852351769[253] = 0;
   out_5803079463852351769[254] = 0;
   out_5803079463852351769[255] = 0;
   out_5803079463852351769[256] = 0;
   out_5803079463852351769[257] = 0;
   out_5803079463852351769[258] = 0;
   out_5803079463852351769[259] = 0;
   out_5803079463852351769[260] = 0;
   out_5803079463852351769[261] = 0;
   out_5803079463852351769[262] = 0;
   out_5803079463852351769[263] = 0;
   out_5803079463852351769[264] = 0;
   out_5803079463852351769[265] = 0;
   out_5803079463852351769[266] = 1;
   out_5803079463852351769[267] = 0;
   out_5803079463852351769[268] = 0;
   out_5803079463852351769[269] = 0;
   out_5803079463852351769[270] = 0;
   out_5803079463852351769[271] = 0;
   out_5803079463852351769[272] = 0;
   out_5803079463852351769[273] = 0;
   out_5803079463852351769[274] = 0;
   out_5803079463852351769[275] = 0;
   out_5803079463852351769[276] = 0;
   out_5803079463852351769[277] = 0;
   out_5803079463852351769[278] = 0;
   out_5803079463852351769[279] = 0;
   out_5803079463852351769[280] = 0;
   out_5803079463852351769[281] = 0;
   out_5803079463852351769[282] = 0;
   out_5803079463852351769[283] = 0;
   out_5803079463852351769[284] = 0;
   out_5803079463852351769[285] = 1;
   out_5803079463852351769[286] = 0;
   out_5803079463852351769[287] = 0;
   out_5803079463852351769[288] = 0;
   out_5803079463852351769[289] = 0;
   out_5803079463852351769[290] = 0;
   out_5803079463852351769[291] = 0;
   out_5803079463852351769[292] = 0;
   out_5803079463852351769[293] = 0;
   out_5803079463852351769[294] = 0;
   out_5803079463852351769[295] = 0;
   out_5803079463852351769[296] = 0;
   out_5803079463852351769[297] = 0;
   out_5803079463852351769[298] = 0;
   out_5803079463852351769[299] = 0;
   out_5803079463852351769[300] = 0;
   out_5803079463852351769[301] = 0;
   out_5803079463852351769[302] = 0;
   out_5803079463852351769[303] = 0;
   out_5803079463852351769[304] = 1;
   out_5803079463852351769[305] = 0;
   out_5803079463852351769[306] = 0;
   out_5803079463852351769[307] = 0;
   out_5803079463852351769[308] = 0;
   out_5803079463852351769[309] = 0;
   out_5803079463852351769[310] = 0;
   out_5803079463852351769[311] = 0;
   out_5803079463852351769[312] = 0;
   out_5803079463852351769[313] = 0;
   out_5803079463852351769[314] = 0;
   out_5803079463852351769[315] = 0;
   out_5803079463852351769[316] = 0;
   out_5803079463852351769[317] = 0;
   out_5803079463852351769[318] = 0;
   out_5803079463852351769[319] = 0;
   out_5803079463852351769[320] = 0;
   out_5803079463852351769[321] = 0;
   out_5803079463852351769[322] = 0;
   out_5803079463852351769[323] = 1;
}
void h_4(double *state, double *unused, double *out_7350079271554275604) {
   out_7350079271554275604[0] = state[6] + state[9];
   out_7350079271554275604[1] = state[7] + state[10];
   out_7350079271554275604[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_1244562880865227861) {
   out_1244562880865227861[0] = 0;
   out_1244562880865227861[1] = 0;
   out_1244562880865227861[2] = 0;
   out_1244562880865227861[3] = 0;
   out_1244562880865227861[4] = 0;
   out_1244562880865227861[5] = 0;
   out_1244562880865227861[6] = 1;
   out_1244562880865227861[7] = 0;
   out_1244562880865227861[8] = 0;
   out_1244562880865227861[9] = 1;
   out_1244562880865227861[10] = 0;
   out_1244562880865227861[11] = 0;
   out_1244562880865227861[12] = 0;
   out_1244562880865227861[13] = 0;
   out_1244562880865227861[14] = 0;
   out_1244562880865227861[15] = 0;
   out_1244562880865227861[16] = 0;
   out_1244562880865227861[17] = 0;
   out_1244562880865227861[18] = 0;
   out_1244562880865227861[19] = 0;
   out_1244562880865227861[20] = 0;
   out_1244562880865227861[21] = 0;
   out_1244562880865227861[22] = 0;
   out_1244562880865227861[23] = 0;
   out_1244562880865227861[24] = 0;
   out_1244562880865227861[25] = 1;
   out_1244562880865227861[26] = 0;
   out_1244562880865227861[27] = 0;
   out_1244562880865227861[28] = 1;
   out_1244562880865227861[29] = 0;
   out_1244562880865227861[30] = 0;
   out_1244562880865227861[31] = 0;
   out_1244562880865227861[32] = 0;
   out_1244562880865227861[33] = 0;
   out_1244562880865227861[34] = 0;
   out_1244562880865227861[35] = 0;
   out_1244562880865227861[36] = 0;
   out_1244562880865227861[37] = 0;
   out_1244562880865227861[38] = 0;
   out_1244562880865227861[39] = 0;
   out_1244562880865227861[40] = 0;
   out_1244562880865227861[41] = 0;
   out_1244562880865227861[42] = 0;
   out_1244562880865227861[43] = 0;
   out_1244562880865227861[44] = 1;
   out_1244562880865227861[45] = 0;
   out_1244562880865227861[46] = 0;
   out_1244562880865227861[47] = 1;
   out_1244562880865227861[48] = 0;
   out_1244562880865227861[49] = 0;
   out_1244562880865227861[50] = 0;
   out_1244562880865227861[51] = 0;
   out_1244562880865227861[52] = 0;
   out_1244562880865227861[53] = 0;
}
void h_10(double *state, double *unused, double *out_1091720193787975988) {
   out_1091720193787975988[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_1091720193787975988[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_1091720193787975988[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_3575012607807179771) {
   out_3575012607807179771[0] = 0;
   out_3575012607807179771[1] = 9.8100000000000005*cos(state[1]);
   out_3575012607807179771[2] = 0;
   out_3575012607807179771[3] = 0;
   out_3575012607807179771[4] = -state[8];
   out_3575012607807179771[5] = state[7];
   out_3575012607807179771[6] = 0;
   out_3575012607807179771[7] = state[5];
   out_3575012607807179771[8] = -state[4];
   out_3575012607807179771[9] = 0;
   out_3575012607807179771[10] = 0;
   out_3575012607807179771[11] = 0;
   out_3575012607807179771[12] = 1;
   out_3575012607807179771[13] = 0;
   out_3575012607807179771[14] = 0;
   out_3575012607807179771[15] = 1;
   out_3575012607807179771[16] = 0;
   out_3575012607807179771[17] = 0;
   out_3575012607807179771[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_3575012607807179771[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_3575012607807179771[20] = 0;
   out_3575012607807179771[21] = state[8];
   out_3575012607807179771[22] = 0;
   out_3575012607807179771[23] = -state[6];
   out_3575012607807179771[24] = -state[5];
   out_3575012607807179771[25] = 0;
   out_3575012607807179771[26] = state[3];
   out_3575012607807179771[27] = 0;
   out_3575012607807179771[28] = 0;
   out_3575012607807179771[29] = 0;
   out_3575012607807179771[30] = 0;
   out_3575012607807179771[31] = 1;
   out_3575012607807179771[32] = 0;
   out_3575012607807179771[33] = 0;
   out_3575012607807179771[34] = 1;
   out_3575012607807179771[35] = 0;
   out_3575012607807179771[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_3575012607807179771[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_3575012607807179771[38] = 0;
   out_3575012607807179771[39] = -state[7];
   out_3575012607807179771[40] = state[6];
   out_3575012607807179771[41] = 0;
   out_3575012607807179771[42] = state[4];
   out_3575012607807179771[43] = -state[3];
   out_3575012607807179771[44] = 0;
   out_3575012607807179771[45] = 0;
   out_3575012607807179771[46] = 0;
   out_3575012607807179771[47] = 0;
   out_3575012607807179771[48] = 0;
   out_3575012607807179771[49] = 0;
   out_3575012607807179771[50] = 1;
   out_3575012607807179771[51] = 0;
   out_3575012607807179771[52] = 0;
   out_3575012607807179771[53] = 1;
}
void h_13(double *state, double *unused, double *out_1983158614244864379) {
   out_1983158614244864379[0] = state[3];
   out_1983158614244864379[1] = state[4];
   out_1983158614244864379[2] = state[5];
}
void H_13(double *state, double *unused, double *out_8855194089181928790) {
   out_8855194089181928790[0] = 0;
   out_8855194089181928790[1] = 0;
   out_8855194089181928790[2] = 0;
   out_8855194089181928790[3] = 1;
   out_8855194089181928790[4] = 0;
   out_8855194089181928790[5] = 0;
   out_8855194089181928790[6] = 0;
   out_8855194089181928790[7] = 0;
   out_8855194089181928790[8] = 0;
   out_8855194089181928790[9] = 0;
   out_8855194089181928790[10] = 0;
   out_8855194089181928790[11] = 0;
   out_8855194089181928790[12] = 0;
   out_8855194089181928790[13] = 0;
   out_8855194089181928790[14] = 0;
   out_8855194089181928790[15] = 0;
   out_8855194089181928790[16] = 0;
   out_8855194089181928790[17] = 0;
   out_8855194089181928790[18] = 0;
   out_8855194089181928790[19] = 0;
   out_8855194089181928790[20] = 0;
   out_8855194089181928790[21] = 0;
   out_8855194089181928790[22] = 1;
   out_8855194089181928790[23] = 0;
   out_8855194089181928790[24] = 0;
   out_8855194089181928790[25] = 0;
   out_8855194089181928790[26] = 0;
   out_8855194089181928790[27] = 0;
   out_8855194089181928790[28] = 0;
   out_8855194089181928790[29] = 0;
   out_8855194089181928790[30] = 0;
   out_8855194089181928790[31] = 0;
   out_8855194089181928790[32] = 0;
   out_8855194089181928790[33] = 0;
   out_8855194089181928790[34] = 0;
   out_8855194089181928790[35] = 0;
   out_8855194089181928790[36] = 0;
   out_8855194089181928790[37] = 0;
   out_8855194089181928790[38] = 0;
   out_8855194089181928790[39] = 0;
   out_8855194089181928790[40] = 0;
   out_8855194089181928790[41] = 1;
   out_8855194089181928790[42] = 0;
   out_8855194089181928790[43] = 0;
   out_8855194089181928790[44] = 0;
   out_8855194089181928790[45] = 0;
   out_8855194089181928790[46] = 0;
   out_8855194089181928790[47] = 0;
   out_8855194089181928790[48] = 0;
   out_8855194089181928790[49] = 0;
   out_8855194089181928790[50] = 0;
   out_8855194089181928790[51] = 0;
   out_8855194089181928790[52] = 0;
   out_8855194089181928790[53] = 0;
}
void h_14(double *state, double *unused, double *out_2415928419685502096) {
   out_2415928419685502096[0] = state[6];
   out_2415928419685502096[1] = state[7];
   out_2415928419685502096[2] = state[8];
}
void H_14(double *state, double *unused, double *out_5207803737204712390) {
   out_5207803737204712390[0] = 0;
   out_5207803737204712390[1] = 0;
   out_5207803737204712390[2] = 0;
   out_5207803737204712390[3] = 0;
   out_5207803737204712390[4] = 0;
   out_5207803737204712390[5] = 0;
   out_5207803737204712390[6] = 1;
   out_5207803737204712390[7] = 0;
   out_5207803737204712390[8] = 0;
   out_5207803737204712390[9] = 0;
   out_5207803737204712390[10] = 0;
   out_5207803737204712390[11] = 0;
   out_5207803737204712390[12] = 0;
   out_5207803737204712390[13] = 0;
   out_5207803737204712390[14] = 0;
   out_5207803737204712390[15] = 0;
   out_5207803737204712390[16] = 0;
   out_5207803737204712390[17] = 0;
   out_5207803737204712390[18] = 0;
   out_5207803737204712390[19] = 0;
   out_5207803737204712390[20] = 0;
   out_5207803737204712390[21] = 0;
   out_5207803737204712390[22] = 0;
   out_5207803737204712390[23] = 0;
   out_5207803737204712390[24] = 0;
   out_5207803737204712390[25] = 1;
   out_5207803737204712390[26] = 0;
   out_5207803737204712390[27] = 0;
   out_5207803737204712390[28] = 0;
   out_5207803737204712390[29] = 0;
   out_5207803737204712390[30] = 0;
   out_5207803737204712390[31] = 0;
   out_5207803737204712390[32] = 0;
   out_5207803737204712390[33] = 0;
   out_5207803737204712390[34] = 0;
   out_5207803737204712390[35] = 0;
   out_5207803737204712390[36] = 0;
   out_5207803737204712390[37] = 0;
   out_5207803737204712390[38] = 0;
   out_5207803737204712390[39] = 0;
   out_5207803737204712390[40] = 0;
   out_5207803737204712390[41] = 0;
   out_5207803737204712390[42] = 0;
   out_5207803737204712390[43] = 0;
   out_5207803737204712390[44] = 1;
   out_5207803737204712390[45] = 0;
   out_5207803737204712390[46] = 0;
   out_5207803737204712390[47] = 0;
   out_5207803737204712390[48] = 0;
   out_5207803737204712390[49] = 0;
   out_5207803737204712390[50] = 0;
   out_5207803737204712390[51] = 0;
   out_5207803737204712390[52] = 0;
   out_5207803737204712390[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_4902955493032499892) {
  err_fun(nom_x, delta_x, out_4902955493032499892);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1560256026778240052) {
  inv_err_fun(nom_x, true_x, out_1560256026778240052);
}
void pose_H_mod_fun(double *state, double *out_1285602415841124817) {
  H_mod_fun(state, out_1285602415841124817);
}
void pose_f_fun(double *state, double dt, double *out_1401742083845182998) {
  f_fun(state,  dt, out_1401742083845182998);
}
void pose_F_fun(double *state, double dt, double *out_5803079463852351769) {
  F_fun(state,  dt, out_5803079463852351769);
}
void pose_h_4(double *state, double *unused, double *out_7350079271554275604) {
  h_4(state, unused, out_7350079271554275604);
}
void pose_H_4(double *state, double *unused, double *out_1244562880865227861) {
  H_4(state, unused, out_1244562880865227861);
}
void pose_h_10(double *state, double *unused, double *out_1091720193787975988) {
  h_10(state, unused, out_1091720193787975988);
}
void pose_H_10(double *state, double *unused, double *out_3575012607807179771) {
  H_10(state, unused, out_3575012607807179771);
}
void pose_h_13(double *state, double *unused, double *out_1983158614244864379) {
  h_13(state, unused, out_1983158614244864379);
}
void pose_H_13(double *state, double *unused, double *out_8855194089181928790) {
  H_13(state, unused, out_8855194089181928790);
}
void pose_h_14(double *state, double *unused, double *out_2415928419685502096) {
  h_14(state, unused, out_2415928419685502096);
}
void pose_H_14(double *state, double *unused, double *out_5207803737204712390) {
  H_14(state, unused, out_5207803737204712390);
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
