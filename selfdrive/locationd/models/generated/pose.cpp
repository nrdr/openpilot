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
void err_fun(double *nom_x, double *delta_x, double *out_5956790764081545981) {
   out_5956790764081545981[0] = delta_x[0] + nom_x[0];
   out_5956790764081545981[1] = delta_x[1] + nom_x[1];
   out_5956790764081545981[2] = delta_x[2] + nom_x[2];
   out_5956790764081545981[3] = delta_x[3] + nom_x[3];
   out_5956790764081545981[4] = delta_x[4] + nom_x[4];
   out_5956790764081545981[5] = delta_x[5] + nom_x[5];
   out_5956790764081545981[6] = delta_x[6] + nom_x[6];
   out_5956790764081545981[7] = delta_x[7] + nom_x[7];
   out_5956790764081545981[8] = delta_x[8] + nom_x[8];
   out_5956790764081545981[9] = delta_x[9] + nom_x[9];
   out_5956790764081545981[10] = delta_x[10] + nom_x[10];
   out_5956790764081545981[11] = delta_x[11] + nom_x[11];
   out_5956790764081545981[12] = delta_x[12] + nom_x[12];
   out_5956790764081545981[13] = delta_x[13] + nom_x[13];
   out_5956790764081545981[14] = delta_x[14] + nom_x[14];
   out_5956790764081545981[15] = delta_x[15] + nom_x[15];
   out_5956790764081545981[16] = delta_x[16] + nom_x[16];
   out_5956790764081545981[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4313117768787886850) {
   out_4313117768787886850[0] = -nom_x[0] + true_x[0];
   out_4313117768787886850[1] = -nom_x[1] + true_x[1];
   out_4313117768787886850[2] = -nom_x[2] + true_x[2];
   out_4313117768787886850[3] = -nom_x[3] + true_x[3];
   out_4313117768787886850[4] = -nom_x[4] + true_x[4];
   out_4313117768787886850[5] = -nom_x[5] + true_x[5];
   out_4313117768787886850[6] = -nom_x[6] + true_x[6];
   out_4313117768787886850[7] = -nom_x[7] + true_x[7];
   out_4313117768787886850[8] = -nom_x[8] + true_x[8];
   out_4313117768787886850[9] = -nom_x[9] + true_x[9];
   out_4313117768787886850[10] = -nom_x[10] + true_x[10];
   out_4313117768787886850[11] = -nom_x[11] + true_x[11];
   out_4313117768787886850[12] = -nom_x[12] + true_x[12];
   out_4313117768787886850[13] = -nom_x[13] + true_x[13];
   out_4313117768787886850[14] = -nom_x[14] + true_x[14];
   out_4313117768787886850[15] = -nom_x[15] + true_x[15];
   out_4313117768787886850[16] = -nom_x[16] + true_x[16];
   out_4313117768787886850[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_1837758063541038755) {
   out_1837758063541038755[0] = 1.0;
   out_1837758063541038755[1] = 0.0;
   out_1837758063541038755[2] = 0.0;
   out_1837758063541038755[3] = 0.0;
   out_1837758063541038755[4] = 0.0;
   out_1837758063541038755[5] = 0.0;
   out_1837758063541038755[6] = 0.0;
   out_1837758063541038755[7] = 0.0;
   out_1837758063541038755[8] = 0.0;
   out_1837758063541038755[9] = 0.0;
   out_1837758063541038755[10] = 0.0;
   out_1837758063541038755[11] = 0.0;
   out_1837758063541038755[12] = 0.0;
   out_1837758063541038755[13] = 0.0;
   out_1837758063541038755[14] = 0.0;
   out_1837758063541038755[15] = 0.0;
   out_1837758063541038755[16] = 0.0;
   out_1837758063541038755[17] = 0.0;
   out_1837758063541038755[18] = 0.0;
   out_1837758063541038755[19] = 1.0;
   out_1837758063541038755[20] = 0.0;
   out_1837758063541038755[21] = 0.0;
   out_1837758063541038755[22] = 0.0;
   out_1837758063541038755[23] = 0.0;
   out_1837758063541038755[24] = 0.0;
   out_1837758063541038755[25] = 0.0;
   out_1837758063541038755[26] = 0.0;
   out_1837758063541038755[27] = 0.0;
   out_1837758063541038755[28] = 0.0;
   out_1837758063541038755[29] = 0.0;
   out_1837758063541038755[30] = 0.0;
   out_1837758063541038755[31] = 0.0;
   out_1837758063541038755[32] = 0.0;
   out_1837758063541038755[33] = 0.0;
   out_1837758063541038755[34] = 0.0;
   out_1837758063541038755[35] = 0.0;
   out_1837758063541038755[36] = 0.0;
   out_1837758063541038755[37] = 0.0;
   out_1837758063541038755[38] = 1.0;
   out_1837758063541038755[39] = 0.0;
   out_1837758063541038755[40] = 0.0;
   out_1837758063541038755[41] = 0.0;
   out_1837758063541038755[42] = 0.0;
   out_1837758063541038755[43] = 0.0;
   out_1837758063541038755[44] = 0.0;
   out_1837758063541038755[45] = 0.0;
   out_1837758063541038755[46] = 0.0;
   out_1837758063541038755[47] = 0.0;
   out_1837758063541038755[48] = 0.0;
   out_1837758063541038755[49] = 0.0;
   out_1837758063541038755[50] = 0.0;
   out_1837758063541038755[51] = 0.0;
   out_1837758063541038755[52] = 0.0;
   out_1837758063541038755[53] = 0.0;
   out_1837758063541038755[54] = 0.0;
   out_1837758063541038755[55] = 0.0;
   out_1837758063541038755[56] = 0.0;
   out_1837758063541038755[57] = 1.0;
   out_1837758063541038755[58] = 0.0;
   out_1837758063541038755[59] = 0.0;
   out_1837758063541038755[60] = 0.0;
   out_1837758063541038755[61] = 0.0;
   out_1837758063541038755[62] = 0.0;
   out_1837758063541038755[63] = 0.0;
   out_1837758063541038755[64] = 0.0;
   out_1837758063541038755[65] = 0.0;
   out_1837758063541038755[66] = 0.0;
   out_1837758063541038755[67] = 0.0;
   out_1837758063541038755[68] = 0.0;
   out_1837758063541038755[69] = 0.0;
   out_1837758063541038755[70] = 0.0;
   out_1837758063541038755[71] = 0.0;
   out_1837758063541038755[72] = 0.0;
   out_1837758063541038755[73] = 0.0;
   out_1837758063541038755[74] = 0.0;
   out_1837758063541038755[75] = 0.0;
   out_1837758063541038755[76] = 1.0;
   out_1837758063541038755[77] = 0.0;
   out_1837758063541038755[78] = 0.0;
   out_1837758063541038755[79] = 0.0;
   out_1837758063541038755[80] = 0.0;
   out_1837758063541038755[81] = 0.0;
   out_1837758063541038755[82] = 0.0;
   out_1837758063541038755[83] = 0.0;
   out_1837758063541038755[84] = 0.0;
   out_1837758063541038755[85] = 0.0;
   out_1837758063541038755[86] = 0.0;
   out_1837758063541038755[87] = 0.0;
   out_1837758063541038755[88] = 0.0;
   out_1837758063541038755[89] = 0.0;
   out_1837758063541038755[90] = 0.0;
   out_1837758063541038755[91] = 0.0;
   out_1837758063541038755[92] = 0.0;
   out_1837758063541038755[93] = 0.0;
   out_1837758063541038755[94] = 0.0;
   out_1837758063541038755[95] = 1.0;
   out_1837758063541038755[96] = 0.0;
   out_1837758063541038755[97] = 0.0;
   out_1837758063541038755[98] = 0.0;
   out_1837758063541038755[99] = 0.0;
   out_1837758063541038755[100] = 0.0;
   out_1837758063541038755[101] = 0.0;
   out_1837758063541038755[102] = 0.0;
   out_1837758063541038755[103] = 0.0;
   out_1837758063541038755[104] = 0.0;
   out_1837758063541038755[105] = 0.0;
   out_1837758063541038755[106] = 0.0;
   out_1837758063541038755[107] = 0.0;
   out_1837758063541038755[108] = 0.0;
   out_1837758063541038755[109] = 0.0;
   out_1837758063541038755[110] = 0.0;
   out_1837758063541038755[111] = 0.0;
   out_1837758063541038755[112] = 0.0;
   out_1837758063541038755[113] = 0.0;
   out_1837758063541038755[114] = 1.0;
   out_1837758063541038755[115] = 0.0;
   out_1837758063541038755[116] = 0.0;
   out_1837758063541038755[117] = 0.0;
   out_1837758063541038755[118] = 0.0;
   out_1837758063541038755[119] = 0.0;
   out_1837758063541038755[120] = 0.0;
   out_1837758063541038755[121] = 0.0;
   out_1837758063541038755[122] = 0.0;
   out_1837758063541038755[123] = 0.0;
   out_1837758063541038755[124] = 0.0;
   out_1837758063541038755[125] = 0.0;
   out_1837758063541038755[126] = 0.0;
   out_1837758063541038755[127] = 0.0;
   out_1837758063541038755[128] = 0.0;
   out_1837758063541038755[129] = 0.0;
   out_1837758063541038755[130] = 0.0;
   out_1837758063541038755[131] = 0.0;
   out_1837758063541038755[132] = 0.0;
   out_1837758063541038755[133] = 1.0;
   out_1837758063541038755[134] = 0.0;
   out_1837758063541038755[135] = 0.0;
   out_1837758063541038755[136] = 0.0;
   out_1837758063541038755[137] = 0.0;
   out_1837758063541038755[138] = 0.0;
   out_1837758063541038755[139] = 0.0;
   out_1837758063541038755[140] = 0.0;
   out_1837758063541038755[141] = 0.0;
   out_1837758063541038755[142] = 0.0;
   out_1837758063541038755[143] = 0.0;
   out_1837758063541038755[144] = 0.0;
   out_1837758063541038755[145] = 0.0;
   out_1837758063541038755[146] = 0.0;
   out_1837758063541038755[147] = 0.0;
   out_1837758063541038755[148] = 0.0;
   out_1837758063541038755[149] = 0.0;
   out_1837758063541038755[150] = 0.0;
   out_1837758063541038755[151] = 0.0;
   out_1837758063541038755[152] = 1.0;
   out_1837758063541038755[153] = 0.0;
   out_1837758063541038755[154] = 0.0;
   out_1837758063541038755[155] = 0.0;
   out_1837758063541038755[156] = 0.0;
   out_1837758063541038755[157] = 0.0;
   out_1837758063541038755[158] = 0.0;
   out_1837758063541038755[159] = 0.0;
   out_1837758063541038755[160] = 0.0;
   out_1837758063541038755[161] = 0.0;
   out_1837758063541038755[162] = 0.0;
   out_1837758063541038755[163] = 0.0;
   out_1837758063541038755[164] = 0.0;
   out_1837758063541038755[165] = 0.0;
   out_1837758063541038755[166] = 0.0;
   out_1837758063541038755[167] = 0.0;
   out_1837758063541038755[168] = 0.0;
   out_1837758063541038755[169] = 0.0;
   out_1837758063541038755[170] = 0.0;
   out_1837758063541038755[171] = 1.0;
   out_1837758063541038755[172] = 0.0;
   out_1837758063541038755[173] = 0.0;
   out_1837758063541038755[174] = 0.0;
   out_1837758063541038755[175] = 0.0;
   out_1837758063541038755[176] = 0.0;
   out_1837758063541038755[177] = 0.0;
   out_1837758063541038755[178] = 0.0;
   out_1837758063541038755[179] = 0.0;
   out_1837758063541038755[180] = 0.0;
   out_1837758063541038755[181] = 0.0;
   out_1837758063541038755[182] = 0.0;
   out_1837758063541038755[183] = 0.0;
   out_1837758063541038755[184] = 0.0;
   out_1837758063541038755[185] = 0.0;
   out_1837758063541038755[186] = 0.0;
   out_1837758063541038755[187] = 0.0;
   out_1837758063541038755[188] = 0.0;
   out_1837758063541038755[189] = 0.0;
   out_1837758063541038755[190] = 1.0;
   out_1837758063541038755[191] = 0.0;
   out_1837758063541038755[192] = 0.0;
   out_1837758063541038755[193] = 0.0;
   out_1837758063541038755[194] = 0.0;
   out_1837758063541038755[195] = 0.0;
   out_1837758063541038755[196] = 0.0;
   out_1837758063541038755[197] = 0.0;
   out_1837758063541038755[198] = 0.0;
   out_1837758063541038755[199] = 0.0;
   out_1837758063541038755[200] = 0.0;
   out_1837758063541038755[201] = 0.0;
   out_1837758063541038755[202] = 0.0;
   out_1837758063541038755[203] = 0.0;
   out_1837758063541038755[204] = 0.0;
   out_1837758063541038755[205] = 0.0;
   out_1837758063541038755[206] = 0.0;
   out_1837758063541038755[207] = 0.0;
   out_1837758063541038755[208] = 0.0;
   out_1837758063541038755[209] = 1.0;
   out_1837758063541038755[210] = 0.0;
   out_1837758063541038755[211] = 0.0;
   out_1837758063541038755[212] = 0.0;
   out_1837758063541038755[213] = 0.0;
   out_1837758063541038755[214] = 0.0;
   out_1837758063541038755[215] = 0.0;
   out_1837758063541038755[216] = 0.0;
   out_1837758063541038755[217] = 0.0;
   out_1837758063541038755[218] = 0.0;
   out_1837758063541038755[219] = 0.0;
   out_1837758063541038755[220] = 0.0;
   out_1837758063541038755[221] = 0.0;
   out_1837758063541038755[222] = 0.0;
   out_1837758063541038755[223] = 0.0;
   out_1837758063541038755[224] = 0.0;
   out_1837758063541038755[225] = 0.0;
   out_1837758063541038755[226] = 0.0;
   out_1837758063541038755[227] = 0.0;
   out_1837758063541038755[228] = 1.0;
   out_1837758063541038755[229] = 0.0;
   out_1837758063541038755[230] = 0.0;
   out_1837758063541038755[231] = 0.0;
   out_1837758063541038755[232] = 0.0;
   out_1837758063541038755[233] = 0.0;
   out_1837758063541038755[234] = 0.0;
   out_1837758063541038755[235] = 0.0;
   out_1837758063541038755[236] = 0.0;
   out_1837758063541038755[237] = 0.0;
   out_1837758063541038755[238] = 0.0;
   out_1837758063541038755[239] = 0.0;
   out_1837758063541038755[240] = 0.0;
   out_1837758063541038755[241] = 0.0;
   out_1837758063541038755[242] = 0.0;
   out_1837758063541038755[243] = 0.0;
   out_1837758063541038755[244] = 0.0;
   out_1837758063541038755[245] = 0.0;
   out_1837758063541038755[246] = 0.0;
   out_1837758063541038755[247] = 1.0;
   out_1837758063541038755[248] = 0.0;
   out_1837758063541038755[249] = 0.0;
   out_1837758063541038755[250] = 0.0;
   out_1837758063541038755[251] = 0.0;
   out_1837758063541038755[252] = 0.0;
   out_1837758063541038755[253] = 0.0;
   out_1837758063541038755[254] = 0.0;
   out_1837758063541038755[255] = 0.0;
   out_1837758063541038755[256] = 0.0;
   out_1837758063541038755[257] = 0.0;
   out_1837758063541038755[258] = 0.0;
   out_1837758063541038755[259] = 0.0;
   out_1837758063541038755[260] = 0.0;
   out_1837758063541038755[261] = 0.0;
   out_1837758063541038755[262] = 0.0;
   out_1837758063541038755[263] = 0.0;
   out_1837758063541038755[264] = 0.0;
   out_1837758063541038755[265] = 0.0;
   out_1837758063541038755[266] = 1.0;
   out_1837758063541038755[267] = 0.0;
   out_1837758063541038755[268] = 0.0;
   out_1837758063541038755[269] = 0.0;
   out_1837758063541038755[270] = 0.0;
   out_1837758063541038755[271] = 0.0;
   out_1837758063541038755[272] = 0.0;
   out_1837758063541038755[273] = 0.0;
   out_1837758063541038755[274] = 0.0;
   out_1837758063541038755[275] = 0.0;
   out_1837758063541038755[276] = 0.0;
   out_1837758063541038755[277] = 0.0;
   out_1837758063541038755[278] = 0.0;
   out_1837758063541038755[279] = 0.0;
   out_1837758063541038755[280] = 0.0;
   out_1837758063541038755[281] = 0.0;
   out_1837758063541038755[282] = 0.0;
   out_1837758063541038755[283] = 0.0;
   out_1837758063541038755[284] = 0.0;
   out_1837758063541038755[285] = 1.0;
   out_1837758063541038755[286] = 0.0;
   out_1837758063541038755[287] = 0.0;
   out_1837758063541038755[288] = 0.0;
   out_1837758063541038755[289] = 0.0;
   out_1837758063541038755[290] = 0.0;
   out_1837758063541038755[291] = 0.0;
   out_1837758063541038755[292] = 0.0;
   out_1837758063541038755[293] = 0.0;
   out_1837758063541038755[294] = 0.0;
   out_1837758063541038755[295] = 0.0;
   out_1837758063541038755[296] = 0.0;
   out_1837758063541038755[297] = 0.0;
   out_1837758063541038755[298] = 0.0;
   out_1837758063541038755[299] = 0.0;
   out_1837758063541038755[300] = 0.0;
   out_1837758063541038755[301] = 0.0;
   out_1837758063541038755[302] = 0.0;
   out_1837758063541038755[303] = 0.0;
   out_1837758063541038755[304] = 1.0;
   out_1837758063541038755[305] = 0.0;
   out_1837758063541038755[306] = 0.0;
   out_1837758063541038755[307] = 0.0;
   out_1837758063541038755[308] = 0.0;
   out_1837758063541038755[309] = 0.0;
   out_1837758063541038755[310] = 0.0;
   out_1837758063541038755[311] = 0.0;
   out_1837758063541038755[312] = 0.0;
   out_1837758063541038755[313] = 0.0;
   out_1837758063541038755[314] = 0.0;
   out_1837758063541038755[315] = 0.0;
   out_1837758063541038755[316] = 0.0;
   out_1837758063541038755[317] = 0.0;
   out_1837758063541038755[318] = 0.0;
   out_1837758063541038755[319] = 0.0;
   out_1837758063541038755[320] = 0.0;
   out_1837758063541038755[321] = 0.0;
   out_1837758063541038755[322] = 0.0;
   out_1837758063541038755[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_520388946504101152) {
   out_520388946504101152[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_520388946504101152[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_520388946504101152[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_520388946504101152[3] = dt*state[12] + state[3];
   out_520388946504101152[4] = dt*state[13] + state[4];
   out_520388946504101152[5] = dt*state[14] + state[5];
   out_520388946504101152[6] = state[6];
   out_520388946504101152[7] = state[7];
   out_520388946504101152[8] = state[8];
   out_520388946504101152[9] = state[9];
   out_520388946504101152[10] = state[10];
   out_520388946504101152[11] = state[11];
   out_520388946504101152[12] = state[12];
   out_520388946504101152[13] = state[13];
   out_520388946504101152[14] = state[14];
   out_520388946504101152[15] = state[15];
   out_520388946504101152[16] = state[16];
   out_520388946504101152[17] = state[17];
}
void F_fun(double *state, double dt, double *out_6289216028855659852) {
   out_6289216028855659852[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6289216028855659852[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6289216028855659852[2] = 0;
   out_6289216028855659852[3] = 0;
   out_6289216028855659852[4] = 0;
   out_6289216028855659852[5] = 0;
   out_6289216028855659852[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6289216028855659852[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6289216028855659852[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6289216028855659852[9] = 0;
   out_6289216028855659852[10] = 0;
   out_6289216028855659852[11] = 0;
   out_6289216028855659852[12] = 0;
   out_6289216028855659852[13] = 0;
   out_6289216028855659852[14] = 0;
   out_6289216028855659852[15] = 0;
   out_6289216028855659852[16] = 0;
   out_6289216028855659852[17] = 0;
   out_6289216028855659852[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6289216028855659852[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6289216028855659852[20] = 0;
   out_6289216028855659852[21] = 0;
   out_6289216028855659852[22] = 0;
   out_6289216028855659852[23] = 0;
   out_6289216028855659852[24] = 0;
   out_6289216028855659852[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6289216028855659852[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6289216028855659852[27] = 0;
   out_6289216028855659852[28] = 0;
   out_6289216028855659852[29] = 0;
   out_6289216028855659852[30] = 0;
   out_6289216028855659852[31] = 0;
   out_6289216028855659852[32] = 0;
   out_6289216028855659852[33] = 0;
   out_6289216028855659852[34] = 0;
   out_6289216028855659852[35] = 0;
   out_6289216028855659852[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6289216028855659852[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6289216028855659852[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6289216028855659852[39] = 0;
   out_6289216028855659852[40] = 0;
   out_6289216028855659852[41] = 0;
   out_6289216028855659852[42] = 0;
   out_6289216028855659852[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6289216028855659852[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6289216028855659852[45] = 0;
   out_6289216028855659852[46] = 0;
   out_6289216028855659852[47] = 0;
   out_6289216028855659852[48] = 0;
   out_6289216028855659852[49] = 0;
   out_6289216028855659852[50] = 0;
   out_6289216028855659852[51] = 0;
   out_6289216028855659852[52] = 0;
   out_6289216028855659852[53] = 0;
   out_6289216028855659852[54] = 0;
   out_6289216028855659852[55] = 0;
   out_6289216028855659852[56] = 0;
   out_6289216028855659852[57] = 1;
   out_6289216028855659852[58] = 0;
   out_6289216028855659852[59] = 0;
   out_6289216028855659852[60] = 0;
   out_6289216028855659852[61] = 0;
   out_6289216028855659852[62] = 0;
   out_6289216028855659852[63] = 0;
   out_6289216028855659852[64] = 0;
   out_6289216028855659852[65] = 0;
   out_6289216028855659852[66] = dt;
   out_6289216028855659852[67] = 0;
   out_6289216028855659852[68] = 0;
   out_6289216028855659852[69] = 0;
   out_6289216028855659852[70] = 0;
   out_6289216028855659852[71] = 0;
   out_6289216028855659852[72] = 0;
   out_6289216028855659852[73] = 0;
   out_6289216028855659852[74] = 0;
   out_6289216028855659852[75] = 0;
   out_6289216028855659852[76] = 1;
   out_6289216028855659852[77] = 0;
   out_6289216028855659852[78] = 0;
   out_6289216028855659852[79] = 0;
   out_6289216028855659852[80] = 0;
   out_6289216028855659852[81] = 0;
   out_6289216028855659852[82] = 0;
   out_6289216028855659852[83] = 0;
   out_6289216028855659852[84] = 0;
   out_6289216028855659852[85] = dt;
   out_6289216028855659852[86] = 0;
   out_6289216028855659852[87] = 0;
   out_6289216028855659852[88] = 0;
   out_6289216028855659852[89] = 0;
   out_6289216028855659852[90] = 0;
   out_6289216028855659852[91] = 0;
   out_6289216028855659852[92] = 0;
   out_6289216028855659852[93] = 0;
   out_6289216028855659852[94] = 0;
   out_6289216028855659852[95] = 1;
   out_6289216028855659852[96] = 0;
   out_6289216028855659852[97] = 0;
   out_6289216028855659852[98] = 0;
   out_6289216028855659852[99] = 0;
   out_6289216028855659852[100] = 0;
   out_6289216028855659852[101] = 0;
   out_6289216028855659852[102] = 0;
   out_6289216028855659852[103] = 0;
   out_6289216028855659852[104] = dt;
   out_6289216028855659852[105] = 0;
   out_6289216028855659852[106] = 0;
   out_6289216028855659852[107] = 0;
   out_6289216028855659852[108] = 0;
   out_6289216028855659852[109] = 0;
   out_6289216028855659852[110] = 0;
   out_6289216028855659852[111] = 0;
   out_6289216028855659852[112] = 0;
   out_6289216028855659852[113] = 0;
   out_6289216028855659852[114] = 1;
   out_6289216028855659852[115] = 0;
   out_6289216028855659852[116] = 0;
   out_6289216028855659852[117] = 0;
   out_6289216028855659852[118] = 0;
   out_6289216028855659852[119] = 0;
   out_6289216028855659852[120] = 0;
   out_6289216028855659852[121] = 0;
   out_6289216028855659852[122] = 0;
   out_6289216028855659852[123] = 0;
   out_6289216028855659852[124] = 0;
   out_6289216028855659852[125] = 0;
   out_6289216028855659852[126] = 0;
   out_6289216028855659852[127] = 0;
   out_6289216028855659852[128] = 0;
   out_6289216028855659852[129] = 0;
   out_6289216028855659852[130] = 0;
   out_6289216028855659852[131] = 0;
   out_6289216028855659852[132] = 0;
   out_6289216028855659852[133] = 1;
   out_6289216028855659852[134] = 0;
   out_6289216028855659852[135] = 0;
   out_6289216028855659852[136] = 0;
   out_6289216028855659852[137] = 0;
   out_6289216028855659852[138] = 0;
   out_6289216028855659852[139] = 0;
   out_6289216028855659852[140] = 0;
   out_6289216028855659852[141] = 0;
   out_6289216028855659852[142] = 0;
   out_6289216028855659852[143] = 0;
   out_6289216028855659852[144] = 0;
   out_6289216028855659852[145] = 0;
   out_6289216028855659852[146] = 0;
   out_6289216028855659852[147] = 0;
   out_6289216028855659852[148] = 0;
   out_6289216028855659852[149] = 0;
   out_6289216028855659852[150] = 0;
   out_6289216028855659852[151] = 0;
   out_6289216028855659852[152] = 1;
   out_6289216028855659852[153] = 0;
   out_6289216028855659852[154] = 0;
   out_6289216028855659852[155] = 0;
   out_6289216028855659852[156] = 0;
   out_6289216028855659852[157] = 0;
   out_6289216028855659852[158] = 0;
   out_6289216028855659852[159] = 0;
   out_6289216028855659852[160] = 0;
   out_6289216028855659852[161] = 0;
   out_6289216028855659852[162] = 0;
   out_6289216028855659852[163] = 0;
   out_6289216028855659852[164] = 0;
   out_6289216028855659852[165] = 0;
   out_6289216028855659852[166] = 0;
   out_6289216028855659852[167] = 0;
   out_6289216028855659852[168] = 0;
   out_6289216028855659852[169] = 0;
   out_6289216028855659852[170] = 0;
   out_6289216028855659852[171] = 1;
   out_6289216028855659852[172] = 0;
   out_6289216028855659852[173] = 0;
   out_6289216028855659852[174] = 0;
   out_6289216028855659852[175] = 0;
   out_6289216028855659852[176] = 0;
   out_6289216028855659852[177] = 0;
   out_6289216028855659852[178] = 0;
   out_6289216028855659852[179] = 0;
   out_6289216028855659852[180] = 0;
   out_6289216028855659852[181] = 0;
   out_6289216028855659852[182] = 0;
   out_6289216028855659852[183] = 0;
   out_6289216028855659852[184] = 0;
   out_6289216028855659852[185] = 0;
   out_6289216028855659852[186] = 0;
   out_6289216028855659852[187] = 0;
   out_6289216028855659852[188] = 0;
   out_6289216028855659852[189] = 0;
   out_6289216028855659852[190] = 1;
   out_6289216028855659852[191] = 0;
   out_6289216028855659852[192] = 0;
   out_6289216028855659852[193] = 0;
   out_6289216028855659852[194] = 0;
   out_6289216028855659852[195] = 0;
   out_6289216028855659852[196] = 0;
   out_6289216028855659852[197] = 0;
   out_6289216028855659852[198] = 0;
   out_6289216028855659852[199] = 0;
   out_6289216028855659852[200] = 0;
   out_6289216028855659852[201] = 0;
   out_6289216028855659852[202] = 0;
   out_6289216028855659852[203] = 0;
   out_6289216028855659852[204] = 0;
   out_6289216028855659852[205] = 0;
   out_6289216028855659852[206] = 0;
   out_6289216028855659852[207] = 0;
   out_6289216028855659852[208] = 0;
   out_6289216028855659852[209] = 1;
   out_6289216028855659852[210] = 0;
   out_6289216028855659852[211] = 0;
   out_6289216028855659852[212] = 0;
   out_6289216028855659852[213] = 0;
   out_6289216028855659852[214] = 0;
   out_6289216028855659852[215] = 0;
   out_6289216028855659852[216] = 0;
   out_6289216028855659852[217] = 0;
   out_6289216028855659852[218] = 0;
   out_6289216028855659852[219] = 0;
   out_6289216028855659852[220] = 0;
   out_6289216028855659852[221] = 0;
   out_6289216028855659852[222] = 0;
   out_6289216028855659852[223] = 0;
   out_6289216028855659852[224] = 0;
   out_6289216028855659852[225] = 0;
   out_6289216028855659852[226] = 0;
   out_6289216028855659852[227] = 0;
   out_6289216028855659852[228] = 1;
   out_6289216028855659852[229] = 0;
   out_6289216028855659852[230] = 0;
   out_6289216028855659852[231] = 0;
   out_6289216028855659852[232] = 0;
   out_6289216028855659852[233] = 0;
   out_6289216028855659852[234] = 0;
   out_6289216028855659852[235] = 0;
   out_6289216028855659852[236] = 0;
   out_6289216028855659852[237] = 0;
   out_6289216028855659852[238] = 0;
   out_6289216028855659852[239] = 0;
   out_6289216028855659852[240] = 0;
   out_6289216028855659852[241] = 0;
   out_6289216028855659852[242] = 0;
   out_6289216028855659852[243] = 0;
   out_6289216028855659852[244] = 0;
   out_6289216028855659852[245] = 0;
   out_6289216028855659852[246] = 0;
   out_6289216028855659852[247] = 1;
   out_6289216028855659852[248] = 0;
   out_6289216028855659852[249] = 0;
   out_6289216028855659852[250] = 0;
   out_6289216028855659852[251] = 0;
   out_6289216028855659852[252] = 0;
   out_6289216028855659852[253] = 0;
   out_6289216028855659852[254] = 0;
   out_6289216028855659852[255] = 0;
   out_6289216028855659852[256] = 0;
   out_6289216028855659852[257] = 0;
   out_6289216028855659852[258] = 0;
   out_6289216028855659852[259] = 0;
   out_6289216028855659852[260] = 0;
   out_6289216028855659852[261] = 0;
   out_6289216028855659852[262] = 0;
   out_6289216028855659852[263] = 0;
   out_6289216028855659852[264] = 0;
   out_6289216028855659852[265] = 0;
   out_6289216028855659852[266] = 1;
   out_6289216028855659852[267] = 0;
   out_6289216028855659852[268] = 0;
   out_6289216028855659852[269] = 0;
   out_6289216028855659852[270] = 0;
   out_6289216028855659852[271] = 0;
   out_6289216028855659852[272] = 0;
   out_6289216028855659852[273] = 0;
   out_6289216028855659852[274] = 0;
   out_6289216028855659852[275] = 0;
   out_6289216028855659852[276] = 0;
   out_6289216028855659852[277] = 0;
   out_6289216028855659852[278] = 0;
   out_6289216028855659852[279] = 0;
   out_6289216028855659852[280] = 0;
   out_6289216028855659852[281] = 0;
   out_6289216028855659852[282] = 0;
   out_6289216028855659852[283] = 0;
   out_6289216028855659852[284] = 0;
   out_6289216028855659852[285] = 1;
   out_6289216028855659852[286] = 0;
   out_6289216028855659852[287] = 0;
   out_6289216028855659852[288] = 0;
   out_6289216028855659852[289] = 0;
   out_6289216028855659852[290] = 0;
   out_6289216028855659852[291] = 0;
   out_6289216028855659852[292] = 0;
   out_6289216028855659852[293] = 0;
   out_6289216028855659852[294] = 0;
   out_6289216028855659852[295] = 0;
   out_6289216028855659852[296] = 0;
   out_6289216028855659852[297] = 0;
   out_6289216028855659852[298] = 0;
   out_6289216028855659852[299] = 0;
   out_6289216028855659852[300] = 0;
   out_6289216028855659852[301] = 0;
   out_6289216028855659852[302] = 0;
   out_6289216028855659852[303] = 0;
   out_6289216028855659852[304] = 1;
   out_6289216028855659852[305] = 0;
   out_6289216028855659852[306] = 0;
   out_6289216028855659852[307] = 0;
   out_6289216028855659852[308] = 0;
   out_6289216028855659852[309] = 0;
   out_6289216028855659852[310] = 0;
   out_6289216028855659852[311] = 0;
   out_6289216028855659852[312] = 0;
   out_6289216028855659852[313] = 0;
   out_6289216028855659852[314] = 0;
   out_6289216028855659852[315] = 0;
   out_6289216028855659852[316] = 0;
   out_6289216028855659852[317] = 0;
   out_6289216028855659852[318] = 0;
   out_6289216028855659852[319] = 0;
   out_6289216028855659852[320] = 0;
   out_6289216028855659852[321] = 0;
   out_6289216028855659852[322] = 0;
   out_6289216028855659852[323] = 1;
}
void h_4(double *state, double *unused, double *out_3915395617755416407) {
   out_3915395617755416407[0] = state[6] + state[9];
   out_3915395617755416407[1] = state[7] + state[10];
   out_3915395617755416407[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_7596001590254828369) {
   out_7596001590254828369[0] = 0;
   out_7596001590254828369[1] = 0;
   out_7596001590254828369[2] = 0;
   out_7596001590254828369[3] = 0;
   out_7596001590254828369[4] = 0;
   out_7596001590254828369[5] = 0;
   out_7596001590254828369[6] = 1;
   out_7596001590254828369[7] = 0;
   out_7596001590254828369[8] = 0;
   out_7596001590254828369[9] = 1;
   out_7596001590254828369[10] = 0;
   out_7596001590254828369[11] = 0;
   out_7596001590254828369[12] = 0;
   out_7596001590254828369[13] = 0;
   out_7596001590254828369[14] = 0;
   out_7596001590254828369[15] = 0;
   out_7596001590254828369[16] = 0;
   out_7596001590254828369[17] = 0;
   out_7596001590254828369[18] = 0;
   out_7596001590254828369[19] = 0;
   out_7596001590254828369[20] = 0;
   out_7596001590254828369[21] = 0;
   out_7596001590254828369[22] = 0;
   out_7596001590254828369[23] = 0;
   out_7596001590254828369[24] = 0;
   out_7596001590254828369[25] = 1;
   out_7596001590254828369[26] = 0;
   out_7596001590254828369[27] = 0;
   out_7596001590254828369[28] = 1;
   out_7596001590254828369[29] = 0;
   out_7596001590254828369[30] = 0;
   out_7596001590254828369[31] = 0;
   out_7596001590254828369[32] = 0;
   out_7596001590254828369[33] = 0;
   out_7596001590254828369[34] = 0;
   out_7596001590254828369[35] = 0;
   out_7596001590254828369[36] = 0;
   out_7596001590254828369[37] = 0;
   out_7596001590254828369[38] = 0;
   out_7596001590254828369[39] = 0;
   out_7596001590254828369[40] = 0;
   out_7596001590254828369[41] = 0;
   out_7596001590254828369[42] = 0;
   out_7596001590254828369[43] = 0;
   out_7596001590254828369[44] = 1;
   out_7596001590254828369[45] = 0;
   out_7596001590254828369[46] = 0;
   out_7596001590254828369[47] = 1;
   out_7596001590254828369[48] = 0;
   out_7596001590254828369[49] = 0;
   out_7596001590254828369[50] = 0;
   out_7596001590254828369[51] = 0;
   out_7596001590254828369[52] = 0;
   out_7596001590254828369[53] = 0;
}
void h_10(double *state, double *unused, double *out_6204857596332608039) {
   out_6204857596332608039[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_6204857596332608039[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_6204857596332608039[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_4868523555828362229) {
   out_4868523555828362229[0] = 0;
   out_4868523555828362229[1] = 9.8100000000000005*cos(state[1]);
   out_4868523555828362229[2] = 0;
   out_4868523555828362229[3] = 0;
   out_4868523555828362229[4] = -state[8];
   out_4868523555828362229[5] = state[7];
   out_4868523555828362229[6] = 0;
   out_4868523555828362229[7] = state[5];
   out_4868523555828362229[8] = -state[4];
   out_4868523555828362229[9] = 0;
   out_4868523555828362229[10] = 0;
   out_4868523555828362229[11] = 0;
   out_4868523555828362229[12] = 1;
   out_4868523555828362229[13] = 0;
   out_4868523555828362229[14] = 0;
   out_4868523555828362229[15] = 1;
   out_4868523555828362229[16] = 0;
   out_4868523555828362229[17] = 0;
   out_4868523555828362229[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_4868523555828362229[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_4868523555828362229[20] = 0;
   out_4868523555828362229[21] = state[8];
   out_4868523555828362229[22] = 0;
   out_4868523555828362229[23] = -state[6];
   out_4868523555828362229[24] = -state[5];
   out_4868523555828362229[25] = 0;
   out_4868523555828362229[26] = state[3];
   out_4868523555828362229[27] = 0;
   out_4868523555828362229[28] = 0;
   out_4868523555828362229[29] = 0;
   out_4868523555828362229[30] = 0;
   out_4868523555828362229[31] = 1;
   out_4868523555828362229[32] = 0;
   out_4868523555828362229[33] = 0;
   out_4868523555828362229[34] = 1;
   out_4868523555828362229[35] = 0;
   out_4868523555828362229[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_4868523555828362229[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_4868523555828362229[38] = 0;
   out_4868523555828362229[39] = -state[7];
   out_4868523555828362229[40] = state[6];
   out_4868523555828362229[41] = 0;
   out_4868523555828362229[42] = state[4];
   out_4868523555828362229[43] = -state[3];
   out_4868523555828362229[44] = 0;
   out_4868523555828362229[45] = 0;
   out_4868523555828362229[46] = 0;
   out_4868523555828362229[47] = 0;
   out_4868523555828362229[48] = 0;
   out_4868523555828362229[49] = 0;
   out_4868523555828362229[50] = 1;
   out_4868523555828362229[51] = 0;
   out_4868523555828362229[52] = 0;
   out_4868523555828362229[53] = 1;
}
void h_13(double *state, double *unused, double *out_3430543055391911867) {
   out_3430543055391911867[0] = state[3];
   out_3430543055391911867[1] = state[4];
   out_3430543055391911867[2] = state[5];
}
void H_13(double *state, double *unused, double *out_4383727764922495568) {
   out_4383727764922495568[0] = 0;
   out_4383727764922495568[1] = 0;
   out_4383727764922495568[2] = 0;
   out_4383727764922495568[3] = 1;
   out_4383727764922495568[4] = 0;
   out_4383727764922495568[5] = 0;
   out_4383727764922495568[6] = 0;
   out_4383727764922495568[7] = 0;
   out_4383727764922495568[8] = 0;
   out_4383727764922495568[9] = 0;
   out_4383727764922495568[10] = 0;
   out_4383727764922495568[11] = 0;
   out_4383727764922495568[12] = 0;
   out_4383727764922495568[13] = 0;
   out_4383727764922495568[14] = 0;
   out_4383727764922495568[15] = 0;
   out_4383727764922495568[16] = 0;
   out_4383727764922495568[17] = 0;
   out_4383727764922495568[18] = 0;
   out_4383727764922495568[19] = 0;
   out_4383727764922495568[20] = 0;
   out_4383727764922495568[21] = 0;
   out_4383727764922495568[22] = 1;
   out_4383727764922495568[23] = 0;
   out_4383727764922495568[24] = 0;
   out_4383727764922495568[25] = 0;
   out_4383727764922495568[26] = 0;
   out_4383727764922495568[27] = 0;
   out_4383727764922495568[28] = 0;
   out_4383727764922495568[29] = 0;
   out_4383727764922495568[30] = 0;
   out_4383727764922495568[31] = 0;
   out_4383727764922495568[32] = 0;
   out_4383727764922495568[33] = 0;
   out_4383727764922495568[34] = 0;
   out_4383727764922495568[35] = 0;
   out_4383727764922495568[36] = 0;
   out_4383727764922495568[37] = 0;
   out_4383727764922495568[38] = 0;
   out_4383727764922495568[39] = 0;
   out_4383727764922495568[40] = 0;
   out_4383727764922495568[41] = 1;
   out_4383727764922495568[42] = 0;
   out_4383727764922495568[43] = 0;
   out_4383727764922495568[44] = 0;
   out_4383727764922495568[45] = 0;
   out_4383727764922495568[46] = 0;
   out_4383727764922495568[47] = 0;
   out_4383727764922495568[48] = 0;
   out_4383727764922495568[49] = 0;
   out_4383727764922495568[50] = 0;
   out_4383727764922495568[51] = 0;
   out_4383727764922495568[52] = 0;
   out_4383727764922495568[53] = 0;
}
void h_14(double *state, double *unused, double *out_2629434873033650575) {
   out_2629434873033650575[0] = state[6];
   out_2629434873033650575[1] = state[7];
   out_2629434873033650575[2] = state[8];
}
void H_14(double *state, double *unused, double *out_3632760733915343840) {
   out_3632760733915343840[0] = 0;
   out_3632760733915343840[1] = 0;
   out_3632760733915343840[2] = 0;
   out_3632760733915343840[3] = 0;
   out_3632760733915343840[4] = 0;
   out_3632760733915343840[5] = 0;
   out_3632760733915343840[6] = 1;
   out_3632760733915343840[7] = 0;
   out_3632760733915343840[8] = 0;
   out_3632760733915343840[9] = 0;
   out_3632760733915343840[10] = 0;
   out_3632760733915343840[11] = 0;
   out_3632760733915343840[12] = 0;
   out_3632760733915343840[13] = 0;
   out_3632760733915343840[14] = 0;
   out_3632760733915343840[15] = 0;
   out_3632760733915343840[16] = 0;
   out_3632760733915343840[17] = 0;
   out_3632760733915343840[18] = 0;
   out_3632760733915343840[19] = 0;
   out_3632760733915343840[20] = 0;
   out_3632760733915343840[21] = 0;
   out_3632760733915343840[22] = 0;
   out_3632760733915343840[23] = 0;
   out_3632760733915343840[24] = 0;
   out_3632760733915343840[25] = 1;
   out_3632760733915343840[26] = 0;
   out_3632760733915343840[27] = 0;
   out_3632760733915343840[28] = 0;
   out_3632760733915343840[29] = 0;
   out_3632760733915343840[30] = 0;
   out_3632760733915343840[31] = 0;
   out_3632760733915343840[32] = 0;
   out_3632760733915343840[33] = 0;
   out_3632760733915343840[34] = 0;
   out_3632760733915343840[35] = 0;
   out_3632760733915343840[36] = 0;
   out_3632760733915343840[37] = 0;
   out_3632760733915343840[38] = 0;
   out_3632760733915343840[39] = 0;
   out_3632760733915343840[40] = 0;
   out_3632760733915343840[41] = 0;
   out_3632760733915343840[42] = 0;
   out_3632760733915343840[43] = 0;
   out_3632760733915343840[44] = 1;
   out_3632760733915343840[45] = 0;
   out_3632760733915343840[46] = 0;
   out_3632760733915343840[47] = 0;
   out_3632760733915343840[48] = 0;
   out_3632760733915343840[49] = 0;
   out_3632760733915343840[50] = 0;
   out_3632760733915343840[51] = 0;
   out_3632760733915343840[52] = 0;
   out_3632760733915343840[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_5956790764081545981) {
  err_fun(nom_x, delta_x, out_5956790764081545981);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_4313117768787886850) {
  inv_err_fun(nom_x, true_x, out_4313117768787886850);
}
void pose_H_mod_fun(double *state, double *out_1837758063541038755) {
  H_mod_fun(state, out_1837758063541038755);
}
void pose_f_fun(double *state, double dt, double *out_520388946504101152) {
  f_fun(state,  dt, out_520388946504101152);
}
void pose_F_fun(double *state, double dt, double *out_6289216028855659852) {
  F_fun(state,  dt, out_6289216028855659852);
}
void pose_h_4(double *state, double *unused, double *out_3915395617755416407) {
  h_4(state, unused, out_3915395617755416407);
}
void pose_H_4(double *state, double *unused, double *out_7596001590254828369) {
  H_4(state, unused, out_7596001590254828369);
}
void pose_h_10(double *state, double *unused, double *out_6204857596332608039) {
  h_10(state, unused, out_6204857596332608039);
}
void pose_H_10(double *state, double *unused, double *out_4868523555828362229) {
  H_10(state, unused, out_4868523555828362229);
}
void pose_h_13(double *state, double *unused, double *out_3430543055391911867) {
  h_13(state, unused, out_3430543055391911867);
}
void pose_H_13(double *state, double *unused, double *out_4383727764922495568) {
  H_13(state, unused, out_4383727764922495568);
}
void pose_h_14(double *state, double *unused, double *out_2629434873033650575) {
  h_14(state, unused, out_2629434873033650575);
}
void pose_H_14(double *state, double *unused, double *out_3632760733915343840) {
  H_14(state, unused, out_3632760733915343840);
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
