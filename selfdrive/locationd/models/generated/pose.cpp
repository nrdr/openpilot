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
void err_fun(double *nom_x, double *delta_x, double *out_4554654253610197066) {
   out_4554654253610197066[0] = delta_x[0] + nom_x[0];
   out_4554654253610197066[1] = delta_x[1] + nom_x[1];
   out_4554654253610197066[2] = delta_x[2] + nom_x[2];
   out_4554654253610197066[3] = delta_x[3] + nom_x[3];
   out_4554654253610197066[4] = delta_x[4] + nom_x[4];
   out_4554654253610197066[5] = delta_x[5] + nom_x[5];
   out_4554654253610197066[6] = delta_x[6] + nom_x[6];
   out_4554654253610197066[7] = delta_x[7] + nom_x[7];
   out_4554654253610197066[8] = delta_x[8] + nom_x[8];
   out_4554654253610197066[9] = delta_x[9] + nom_x[9];
   out_4554654253610197066[10] = delta_x[10] + nom_x[10];
   out_4554654253610197066[11] = delta_x[11] + nom_x[11];
   out_4554654253610197066[12] = delta_x[12] + nom_x[12];
   out_4554654253610197066[13] = delta_x[13] + nom_x[13];
   out_4554654253610197066[14] = delta_x[14] + nom_x[14];
   out_4554654253610197066[15] = delta_x[15] + nom_x[15];
   out_4554654253610197066[16] = delta_x[16] + nom_x[16];
   out_4554654253610197066[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7859607288829869304) {
   out_7859607288829869304[0] = -nom_x[0] + true_x[0];
   out_7859607288829869304[1] = -nom_x[1] + true_x[1];
   out_7859607288829869304[2] = -nom_x[2] + true_x[2];
   out_7859607288829869304[3] = -nom_x[3] + true_x[3];
   out_7859607288829869304[4] = -nom_x[4] + true_x[4];
   out_7859607288829869304[5] = -nom_x[5] + true_x[5];
   out_7859607288829869304[6] = -nom_x[6] + true_x[6];
   out_7859607288829869304[7] = -nom_x[7] + true_x[7];
   out_7859607288829869304[8] = -nom_x[8] + true_x[8];
   out_7859607288829869304[9] = -nom_x[9] + true_x[9];
   out_7859607288829869304[10] = -nom_x[10] + true_x[10];
   out_7859607288829869304[11] = -nom_x[11] + true_x[11];
   out_7859607288829869304[12] = -nom_x[12] + true_x[12];
   out_7859607288829869304[13] = -nom_x[13] + true_x[13];
   out_7859607288829869304[14] = -nom_x[14] + true_x[14];
   out_7859607288829869304[15] = -nom_x[15] + true_x[15];
   out_7859607288829869304[16] = -nom_x[16] + true_x[16];
   out_7859607288829869304[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_7585864625755261889) {
   out_7585864625755261889[0] = 1.0;
   out_7585864625755261889[1] = 0.0;
   out_7585864625755261889[2] = 0.0;
   out_7585864625755261889[3] = 0.0;
   out_7585864625755261889[4] = 0.0;
   out_7585864625755261889[5] = 0.0;
   out_7585864625755261889[6] = 0.0;
   out_7585864625755261889[7] = 0.0;
   out_7585864625755261889[8] = 0.0;
   out_7585864625755261889[9] = 0.0;
   out_7585864625755261889[10] = 0.0;
   out_7585864625755261889[11] = 0.0;
   out_7585864625755261889[12] = 0.0;
   out_7585864625755261889[13] = 0.0;
   out_7585864625755261889[14] = 0.0;
   out_7585864625755261889[15] = 0.0;
   out_7585864625755261889[16] = 0.0;
   out_7585864625755261889[17] = 0.0;
   out_7585864625755261889[18] = 0.0;
   out_7585864625755261889[19] = 1.0;
   out_7585864625755261889[20] = 0.0;
   out_7585864625755261889[21] = 0.0;
   out_7585864625755261889[22] = 0.0;
   out_7585864625755261889[23] = 0.0;
   out_7585864625755261889[24] = 0.0;
   out_7585864625755261889[25] = 0.0;
   out_7585864625755261889[26] = 0.0;
   out_7585864625755261889[27] = 0.0;
   out_7585864625755261889[28] = 0.0;
   out_7585864625755261889[29] = 0.0;
   out_7585864625755261889[30] = 0.0;
   out_7585864625755261889[31] = 0.0;
   out_7585864625755261889[32] = 0.0;
   out_7585864625755261889[33] = 0.0;
   out_7585864625755261889[34] = 0.0;
   out_7585864625755261889[35] = 0.0;
   out_7585864625755261889[36] = 0.0;
   out_7585864625755261889[37] = 0.0;
   out_7585864625755261889[38] = 1.0;
   out_7585864625755261889[39] = 0.0;
   out_7585864625755261889[40] = 0.0;
   out_7585864625755261889[41] = 0.0;
   out_7585864625755261889[42] = 0.0;
   out_7585864625755261889[43] = 0.0;
   out_7585864625755261889[44] = 0.0;
   out_7585864625755261889[45] = 0.0;
   out_7585864625755261889[46] = 0.0;
   out_7585864625755261889[47] = 0.0;
   out_7585864625755261889[48] = 0.0;
   out_7585864625755261889[49] = 0.0;
   out_7585864625755261889[50] = 0.0;
   out_7585864625755261889[51] = 0.0;
   out_7585864625755261889[52] = 0.0;
   out_7585864625755261889[53] = 0.0;
   out_7585864625755261889[54] = 0.0;
   out_7585864625755261889[55] = 0.0;
   out_7585864625755261889[56] = 0.0;
   out_7585864625755261889[57] = 1.0;
   out_7585864625755261889[58] = 0.0;
   out_7585864625755261889[59] = 0.0;
   out_7585864625755261889[60] = 0.0;
   out_7585864625755261889[61] = 0.0;
   out_7585864625755261889[62] = 0.0;
   out_7585864625755261889[63] = 0.0;
   out_7585864625755261889[64] = 0.0;
   out_7585864625755261889[65] = 0.0;
   out_7585864625755261889[66] = 0.0;
   out_7585864625755261889[67] = 0.0;
   out_7585864625755261889[68] = 0.0;
   out_7585864625755261889[69] = 0.0;
   out_7585864625755261889[70] = 0.0;
   out_7585864625755261889[71] = 0.0;
   out_7585864625755261889[72] = 0.0;
   out_7585864625755261889[73] = 0.0;
   out_7585864625755261889[74] = 0.0;
   out_7585864625755261889[75] = 0.0;
   out_7585864625755261889[76] = 1.0;
   out_7585864625755261889[77] = 0.0;
   out_7585864625755261889[78] = 0.0;
   out_7585864625755261889[79] = 0.0;
   out_7585864625755261889[80] = 0.0;
   out_7585864625755261889[81] = 0.0;
   out_7585864625755261889[82] = 0.0;
   out_7585864625755261889[83] = 0.0;
   out_7585864625755261889[84] = 0.0;
   out_7585864625755261889[85] = 0.0;
   out_7585864625755261889[86] = 0.0;
   out_7585864625755261889[87] = 0.0;
   out_7585864625755261889[88] = 0.0;
   out_7585864625755261889[89] = 0.0;
   out_7585864625755261889[90] = 0.0;
   out_7585864625755261889[91] = 0.0;
   out_7585864625755261889[92] = 0.0;
   out_7585864625755261889[93] = 0.0;
   out_7585864625755261889[94] = 0.0;
   out_7585864625755261889[95] = 1.0;
   out_7585864625755261889[96] = 0.0;
   out_7585864625755261889[97] = 0.0;
   out_7585864625755261889[98] = 0.0;
   out_7585864625755261889[99] = 0.0;
   out_7585864625755261889[100] = 0.0;
   out_7585864625755261889[101] = 0.0;
   out_7585864625755261889[102] = 0.0;
   out_7585864625755261889[103] = 0.0;
   out_7585864625755261889[104] = 0.0;
   out_7585864625755261889[105] = 0.0;
   out_7585864625755261889[106] = 0.0;
   out_7585864625755261889[107] = 0.0;
   out_7585864625755261889[108] = 0.0;
   out_7585864625755261889[109] = 0.0;
   out_7585864625755261889[110] = 0.0;
   out_7585864625755261889[111] = 0.0;
   out_7585864625755261889[112] = 0.0;
   out_7585864625755261889[113] = 0.0;
   out_7585864625755261889[114] = 1.0;
   out_7585864625755261889[115] = 0.0;
   out_7585864625755261889[116] = 0.0;
   out_7585864625755261889[117] = 0.0;
   out_7585864625755261889[118] = 0.0;
   out_7585864625755261889[119] = 0.0;
   out_7585864625755261889[120] = 0.0;
   out_7585864625755261889[121] = 0.0;
   out_7585864625755261889[122] = 0.0;
   out_7585864625755261889[123] = 0.0;
   out_7585864625755261889[124] = 0.0;
   out_7585864625755261889[125] = 0.0;
   out_7585864625755261889[126] = 0.0;
   out_7585864625755261889[127] = 0.0;
   out_7585864625755261889[128] = 0.0;
   out_7585864625755261889[129] = 0.0;
   out_7585864625755261889[130] = 0.0;
   out_7585864625755261889[131] = 0.0;
   out_7585864625755261889[132] = 0.0;
   out_7585864625755261889[133] = 1.0;
   out_7585864625755261889[134] = 0.0;
   out_7585864625755261889[135] = 0.0;
   out_7585864625755261889[136] = 0.0;
   out_7585864625755261889[137] = 0.0;
   out_7585864625755261889[138] = 0.0;
   out_7585864625755261889[139] = 0.0;
   out_7585864625755261889[140] = 0.0;
   out_7585864625755261889[141] = 0.0;
   out_7585864625755261889[142] = 0.0;
   out_7585864625755261889[143] = 0.0;
   out_7585864625755261889[144] = 0.0;
   out_7585864625755261889[145] = 0.0;
   out_7585864625755261889[146] = 0.0;
   out_7585864625755261889[147] = 0.0;
   out_7585864625755261889[148] = 0.0;
   out_7585864625755261889[149] = 0.0;
   out_7585864625755261889[150] = 0.0;
   out_7585864625755261889[151] = 0.0;
   out_7585864625755261889[152] = 1.0;
   out_7585864625755261889[153] = 0.0;
   out_7585864625755261889[154] = 0.0;
   out_7585864625755261889[155] = 0.0;
   out_7585864625755261889[156] = 0.0;
   out_7585864625755261889[157] = 0.0;
   out_7585864625755261889[158] = 0.0;
   out_7585864625755261889[159] = 0.0;
   out_7585864625755261889[160] = 0.0;
   out_7585864625755261889[161] = 0.0;
   out_7585864625755261889[162] = 0.0;
   out_7585864625755261889[163] = 0.0;
   out_7585864625755261889[164] = 0.0;
   out_7585864625755261889[165] = 0.0;
   out_7585864625755261889[166] = 0.0;
   out_7585864625755261889[167] = 0.0;
   out_7585864625755261889[168] = 0.0;
   out_7585864625755261889[169] = 0.0;
   out_7585864625755261889[170] = 0.0;
   out_7585864625755261889[171] = 1.0;
   out_7585864625755261889[172] = 0.0;
   out_7585864625755261889[173] = 0.0;
   out_7585864625755261889[174] = 0.0;
   out_7585864625755261889[175] = 0.0;
   out_7585864625755261889[176] = 0.0;
   out_7585864625755261889[177] = 0.0;
   out_7585864625755261889[178] = 0.0;
   out_7585864625755261889[179] = 0.0;
   out_7585864625755261889[180] = 0.0;
   out_7585864625755261889[181] = 0.0;
   out_7585864625755261889[182] = 0.0;
   out_7585864625755261889[183] = 0.0;
   out_7585864625755261889[184] = 0.0;
   out_7585864625755261889[185] = 0.0;
   out_7585864625755261889[186] = 0.0;
   out_7585864625755261889[187] = 0.0;
   out_7585864625755261889[188] = 0.0;
   out_7585864625755261889[189] = 0.0;
   out_7585864625755261889[190] = 1.0;
   out_7585864625755261889[191] = 0.0;
   out_7585864625755261889[192] = 0.0;
   out_7585864625755261889[193] = 0.0;
   out_7585864625755261889[194] = 0.0;
   out_7585864625755261889[195] = 0.0;
   out_7585864625755261889[196] = 0.0;
   out_7585864625755261889[197] = 0.0;
   out_7585864625755261889[198] = 0.0;
   out_7585864625755261889[199] = 0.0;
   out_7585864625755261889[200] = 0.0;
   out_7585864625755261889[201] = 0.0;
   out_7585864625755261889[202] = 0.0;
   out_7585864625755261889[203] = 0.0;
   out_7585864625755261889[204] = 0.0;
   out_7585864625755261889[205] = 0.0;
   out_7585864625755261889[206] = 0.0;
   out_7585864625755261889[207] = 0.0;
   out_7585864625755261889[208] = 0.0;
   out_7585864625755261889[209] = 1.0;
   out_7585864625755261889[210] = 0.0;
   out_7585864625755261889[211] = 0.0;
   out_7585864625755261889[212] = 0.0;
   out_7585864625755261889[213] = 0.0;
   out_7585864625755261889[214] = 0.0;
   out_7585864625755261889[215] = 0.0;
   out_7585864625755261889[216] = 0.0;
   out_7585864625755261889[217] = 0.0;
   out_7585864625755261889[218] = 0.0;
   out_7585864625755261889[219] = 0.0;
   out_7585864625755261889[220] = 0.0;
   out_7585864625755261889[221] = 0.0;
   out_7585864625755261889[222] = 0.0;
   out_7585864625755261889[223] = 0.0;
   out_7585864625755261889[224] = 0.0;
   out_7585864625755261889[225] = 0.0;
   out_7585864625755261889[226] = 0.0;
   out_7585864625755261889[227] = 0.0;
   out_7585864625755261889[228] = 1.0;
   out_7585864625755261889[229] = 0.0;
   out_7585864625755261889[230] = 0.0;
   out_7585864625755261889[231] = 0.0;
   out_7585864625755261889[232] = 0.0;
   out_7585864625755261889[233] = 0.0;
   out_7585864625755261889[234] = 0.0;
   out_7585864625755261889[235] = 0.0;
   out_7585864625755261889[236] = 0.0;
   out_7585864625755261889[237] = 0.0;
   out_7585864625755261889[238] = 0.0;
   out_7585864625755261889[239] = 0.0;
   out_7585864625755261889[240] = 0.0;
   out_7585864625755261889[241] = 0.0;
   out_7585864625755261889[242] = 0.0;
   out_7585864625755261889[243] = 0.0;
   out_7585864625755261889[244] = 0.0;
   out_7585864625755261889[245] = 0.0;
   out_7585864625755261889[246] = 0.0;
   out_7585864625755261889[247] = 1.0;
   out_7585864625755261889[248] = 0.0;
   out_7585864625755261889[249] = 0.0;
   out_7585864625755261889[250] = 0.0;
   out_7585864625755261889[251] = 0.0;
   out_7585864625755261889[252] = 0.0;
   out_7585864625755261889[253] = 0.0;
   out_7585864625755261889[254] = 0.0;
   out_7585864625755261889[255] = 0.0;
   out_7585864625755261889[256] = 0.0;
   out_7585864625755261889[257] = 0.0;
   out_7585864625755261889[258] = 0.0;
   out_7585864625755261889[259] = 0.0;
   out_7585864625755261889[260] = 0.0;
   out_7585864625755261889[261] = 0.0;
   out_7585864625755261889[262] = 0.0;
   out_7585864625755261889[263] = 0.0;
   out_7585864625755261889[264] = 0.0;
   out_7585864625755261889[265] = 0.0;
   out_7585864625755261889[266] = 1.0;
   out_7585864625755261889[267] = 0.0;
   out_7585864625755261889[268] = 0.0;
   out_7585864625755261889[269] = 0.0;
   out_7585864625755261889[270] = 0.0;
   out_7585864625755261889[271] = 0.0;
   out_7585864625755261889[272] = 0.0;
   out_7585864625755261889[273] = 0.0;
   out_7585864625755261889[274] = 0.0;
   out_7585864625755261889[275] = 0.0;
   out_7585864625755261889[276] = 0.0;
   out_7585864625755261889[277] = 0.0;
   out_7585864625755261889[278] = 0.0;
   out_7585864625755261889[279] = 0.0;
   out_7585864625755261889[280] = 0.0;
   out_7585864625755261889[281] = 0.0;
   out_7585864625755261889[282] = 0.0;
   out_7585864625755261889[283] = 0.0;
   out_7585864625755261889[284] = 0.0;
   out_7585864625755261889[285] = 1.0;
   out_7585864625755261889[286] = 0.0;
   out_7585864625755261889[287] = 0.0;
   out_7585864625755261889[288] = 0.0;
   out_7585864625755261889[289] = 0.0;
   out_7585864625755261889[290] = 0.0;
   out_7585864625755261889[291] = 0.0;
   out_7585864625755261889[292] = 0.0;
   out_7585864625755261889[293] = 0.0;
   out_7585864625755261889[294] = 0.0;
   out_7585864625755261889[295] = 0.0;
   out_7585864625755261889[296] = 0.0;
   out_7585864625755261889[297] = 0.0;
   out_7585864625755261889[298] = 0.0;
   out_7585864625755261889[299] = 0.0;
   out_7585864625755261889[300] = 0.0;
   out_7585864625755261889[301] = 0.0;
   out_7585864625755261889[302] = 0.0;
   out_7585864625755261889[303] = 0.0;
   out_7585864625755261889[304] = 1.0;
   out_7585864625755261889[305] = 0.0;
   out_7585864625755261889[306] = 0.0;
   out_7585864625755261889[307] = 0.0;
   out_7585864625755261889[308] = 0.0;
   out_7585864625755261889[309] = 0.0;
   out_7585864625755261889[310] = 0.0;
   out_7585864625755261889[311] = 0.0;
   out_7585864625755261889[312] = 0.0;
   out_7585864625755261889[313] = 0.0;
   out_7585864625755261889[314] = 0.0;
   out_7585864625755261889[315] = 0.0;
   out_7585864625755261889[316] = 0.0;
   out_7585864625755261889[317] = 0.0;
   out_7585864625755261889[318] = 0.0;
   out_7585864625755261889[319] = 0.0;
   out_7585864625755261889[320] = 0.0;
   out_7585864625755261889[321] = 0.0;
   out_7585864625755261889[322] = 0.0;
   out_7585864625755261889[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_8989872321626802535) {
   out_8989872321626802535[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_8989872321626802535[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_8989872321626802535[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_8989872321626802535[3] = dt*state[12] + state[3];
   out_8989872321626802535[4] = dt*state[13] + state[4];
   out_8989872321626802535[5] = dt*state[14] + state[5];
   out_8989872321626802535[6] = state[6];
   out_8989872321626802535[7] = state[7];
   out_8989872321626802535[8] = state[8];
   out_8989872321626802535[9] = state[9];
   out_8989872321626802535[10] = state[10];
   out_8989872321626802535[11] = state[11];
   out_8989872321626802535[12] = state[12];
   out_8989872321626802535[13] = state[13];
   out_8989872321626802535[14] = state[14];
   out_8989872321626802535[15] = state[15];
   out_8989872321626802535[16] = state[16];
   out_8989872321626802535[17] = state[17];
}
void F_fun(double *state, double dt, double *out_8485858395715639244) {
   out_8485858395715639244[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8485858395715639244[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8485858395715639244[2] = 0;
   out_8485858395715639244[3] = 0;
   out_8485858395715639244[4] = 0;
   out_8485858395715639244[5] = 0;
   out_8485858395715639244[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8485858395715639244[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8485858395715639244[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8485858395715639244[9] = 0;
   out_8485858395715639244[10] = 0;
   out_8485858395715639244[11] = 0;
   out_8485858395715639244[12] = 0;
   out_8485858395715639244[13] = 0;
   out_8485858395715639244[14] = 0;
   out_8485858395715639244[15] = 0;
   out_8485858395715639244[16] = 0;
   out_8485858395715639244[17] = 0;
   out_8485858395715639244[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8485858395715639244[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8485858395715639244[20] = 0;
   out_8485858395715639244[21] = 0;
   out_8485858395715639244[22] = 0;
   out_8485858395715639244[23] = 0;
   out_8485858395715639244[24] = 0;
   out_8485858395715639244[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8485858395715639244[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8485858395715639244[27] = 0;
   out_8485858395715639244[28] = 0;
   out_8485858395715639244[29] = 0;
   out_8485858395715639244[30] = 0;
   out_8485858395715639244[31] = 0;
   out_8485858395715639244[32] = 0;
   out_8485858395715639244[33] = 0;
   out_8485858395715639244[34] = 0;
   out_8485858395715639244[35] = 0;
   out_8485858395715639244[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8485858395715639244[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8485858395715639244[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8485858395715639244[39] = 0;
   out_8485858395715639244[40] = 0;
   out_8485858395715639244[41] = 0;
   out_8485858395715639244[42] = 0;
   out_8485858395715639244[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8485858395715639244[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8485858395715639244[45] = 0;
   out_8485858395715639244[46] = 0;
   out_8485858395715639244[47] = 0;
   out_8485858395715639244[48] = 0;
   out_8485858395715639244[49] = 0;
   out_8485858395715639244[50] = 0;
   out_8485858395715639244[51] = 0;
   out_8485858395715639244[52] = 0;
   out_8485858395715639244[53] = 0;
   out_8485858395715639244[54] = 0;
   out_8485858395715639244[55] = 0;
   out_8485858395715639244[56] = 0;
   out_8485858395715639244[57] = 1;
   out_8485858395715639244[58] = 0;
   out_8485858395715639244[59] = 0;
   out_8485858395715639244[60] = 0;
   out_8485858395715639244[61] = 0;
   out_8485858395715639244[62] = 0;
   out_8485858395715639244[63] = 0;
   out_8485858395715639244[64] = 0;
   out_8485858395715639244[65] = 0;
   out_8485858395715639244[66] = dt;
   out_8485858395715639244[67] = 0;
   out_8485858395715639244[68] = 0;
   out_8485858395715639244[69] = 0;
   out_8485858395715639244[70] = 0;
   out_8485858395715639244[71] = 0;
   out_8485858395715639244[72] = 0;
   out_8485858395715639244[73] = 0;
   out_8485858395715639244[74] = 0;
   out_8485858395715639244[75] = 0;
   out_8485858395715639244[76] = 1;
   out_8485858395715639244[77] = 0;
   out_8485858395715639244[78] = 0;
   out_8485858395715639244[79] = 0;
   out_8485858395715639244[80] = 0;
   out_8485858395715639244[81] = 0;
   out_8485858395715639244[82] = 0;
   out_8485858395715639244[83] = 0;
   out_8485858395715639244[84] = 0;
   out_8485858395715639244[85] = dt;
   out_8485858395715639244[86] = 0;
   out_8485858395715639244[87] = 0;
   out_8485858395715639244[88] = 0;
   out_8485858395715639244[89] = 0;
   out_8485858395715639244[90] = 0;
   out_8485858395715639244[91] = 0;
   out_8485858395715639244[92] = 0;
   out_8485858395715639244[93] = 0;
   out_8485858395715639244[94] = 0;
   out_8485858395715639244[95] = 1;
   out_8485858395715639244[96] = 0;
   out_8485858395715639244[97] = 0;
   out_8485858395715639244[98] = 0;
   out_8485858395715639244[99] = 0;
   out_8485858395715639244[100] = 0;
   out_8485858395715639244[101] = 0;
   out_8485858395715639244[102] = 0;
   out_8485858395715639244[103] = 0;
   out_8485858395715639244[104] = dt;
   out_8485858395715639244[105] = 0;
   out_8485858395715639244[106] = 0;
   out_8485858395715639244[107] = 0;
   out_8485858395715639244[108] = 0;
   out_8485858395715639244[109] = 0;
   out_8485858395715639244[110] = 0;
   out_8485858395715639244[111] = 0;
   out_8485858395715639244[112] = 0;
   out_8485858395715639244[113] = 0;
   out_8485858395715639244[114] = 1;
   out_8485858395715639244[115] = 0;
   out_8485858395715639244[116] = 0;
   out_8485858395715639244[117] = 0;
   out_8485858395715639244[118] = 0;
   out_8485858395715639244[119] = 0;
   out_8485858395715639244[120] = 0;
   out_8485858395715639244[121] = 0;
   out_8485858395715639244[122] = 0;
   out_8485858395715639244[123] = 0;
   out_8485858395715639244[124] = 0;
   out_8485858395715639244[125] = 0;
   out_8485858395715639244[126] = 0;
   out_8485858395715639244[127] = 0;
   out_8485858395715639244[128] = 0;
   out_8485858395715639244[129] = 0;
   out_8485858395715639244[130] = 0;
   out_8485858395715639244[131] = 0;
   out_8485858395715639244[132] = 0;
   out_8485858395715639244[133] = 1;
   out_8485858395715639244[134] = 0;
   out_8485858395715639244[135] = 0;
   out_8485858395715639244[136] = 0;
   out_8485858395715639244[137] = 0;
   out_8485858395715639244[138] = 0;
   out_8485858395715639244[139] = 0;
   out_8485858395715639244[140] = 0;
   out_8485858395715639244[141] = 0;
   out_8485858395715639244[142] = 0;
   out_8485858395715639244[143] = 0;
   out_8485858395715639244[144] = 0;
   out_8485858395715639244[145] = 0;
   out_8485858395715639244[146] = 0;
   out_8485858395715639244[147] = 0;
   out_8485858395715639244[148] = 0;
   out_8485858395715639244[149] = 0;
   out_8485858395715639244[150] = 0;
   out_8485858395715639244[151] = 0;
   out_8485858395715639244[152] = 1;
   out_8485858395715639244[153] = 0;
   out_8485858395715639244[154] = 0;
   out_8485858395715639244[155] = 0;
   out_8485858395715639244[156] = 0;
   out_8485858395715639244[157] = 0;
   out_8485858395715639244[158] = 0;
   out_8485858395715639244[159] = 0;
   out_8485858395715639244[160] = 0;
   out_8485858395715639244[161] = 0;
   out_8485858395715639244[162] = 0;
   out_8485858395715639244[163] = 0;
   out_8485858395715639244[164] = 0;
   out_8485858395715639244[165] = 0;
   out_8485858395715639244[166] = 0;
   out_8485858395715639244[167] = 0;
   out_8485858395715639244[168] = 0;
   out_8485858395715639244[169] = 0;
   out_8485858395715639244[170] = 0;
   out_8485858395715639244[171] = 1;
   out_8485858395715639244[172] = 0;
   out_8485858395715639244[173] = 0;
   out_8485858395715639244[174] = 0;
   out_8485858395715639244[175] = 0;
   out_8485858395715639244[176] = 0;
   out_8485858395715639244[177] = 0;
   out_8485858395715639244[178] = 0;
   out_8485858395715639244[179] = 0;
   out_8485858395715639244[180] = 0;
   out_8485858395715639244[181] = 0;
   out_8485858395715639244[182] = 0;
   out_8485858395715639244[183] = 0;
   out_8485858395715639244[184] = 0;
   out_8485858395715639244[185] = 0;
   out_8485858395715639244[186] = 0;
   out_8485858395715639244[187] = 0;
   out_8485858395715639244[188] = 0;
   out_8485858395715639244[189] = 0;
   out_8485858395715639244[190] = 1;
   out_8485858395715639244[191] = 0;
   out_8485858395715639244[192] = 0;
   out_8485858395715639244[193] = 0;
   out_8485858395715639244[194] = 0;
   out_8485858395715639244[195] = 0;
   out_8485858395715639244[196] = 0;
   out_8485858395715639244[197] = 0;
   out_8485858395715639244[198] = 0;
   out_8485858395715639244[199] = 0;
   out_8485858395715639244[200] = 0;
   out_8485858395715639244[201] = 0;
   out_8485858395715639244[202] = 0;
   out_8485858395715639244[203] = 0;
   out_8485858395715639244[204] = 0;
   out_8485858395715639244[205] = 0;
   out_8485858395715639244[206] = 0;
   out_8485858395715639244[207] = 0;
   out_8485858395715639244[208] = 0;
   out_8485858395715639244[209] = 1;
   out_8485858395715639244[210] = 0;
   out_8485858395715639244[211] = 0;
   out_8485858395715639244[212] = 0;
   out_8485858395715639244[213] = 0;
   out_8485858395715639244[214] = 0;
   out_8485858395715639244[215] = 0;
   out_8485858395715639244[216] = 0;
   out_8485858395715639244[217] = 0;
   out_8485858395715639244[218] = 0;
   out_8485858395715639244[219] = 0;
   out_8485858395715639244[220] = 0;
   out_8485858395715639244[221] = 0;
   out_8485858395715639244[222] = 0;
   out_8485858395715639244[223] = 0;
   out_8485858395715639244[224] = 0;
   out_8485858395715639244[225] = 0;
   out_8485858395715639244[226] = 0;
   out_8485858395715639244[227] = 0;
   out_8485858395715639244[228] = 1;
   out_8485858395715639244[229] = 0;
   out_8485858395715639244[230] = 0;
   out_8485858395715639244[231] = 0;
   out_8485858395715639244[232] = 0;
   out_8485858395715639244[233] = 0;
   out_8485858395715639244[234] = 0;
   out_8485858395715639244[235] = 0;
   out_8485858395715639244[236] = 0;
   out_8485858395715639244[237] = 0;
   out_8485858395715639244[238] = 0;
   out_8485858395715639244[239] = 0;
   out_8485858395715639244[240] = 0;
   out_8485858395715639244[241] = 0;
   out_8485858395715639244[242] = 0;
   out_8485858395715639244[243] = 0;
   out_8485858395715639244[244] = 0;
   out_8485858395715639244[245] = 0;
   out_8485858395715639244[246] = 0;
   out_8485858395715639244[247] = 1;
   out_8485858395715639244[248] = 0;
   out_8485858395715639244[249] = 0;
   out_8485858395715639244[250] = 0;
   out_8485858395715639244[251] = 0;
   out_8485858395715639244[252] = 0;
   out_8485858395715639244[253] = 0;
   out_8485858395715639244[254] = 0;
   out_8485858395715639244[255] = 0;
   out_8485858395715639244[256] = 0;
   out_8485858395715639244[257] = 0;
   out_8485858395715639244[258] = 0;
   out_8485858395715639244[259] = 0;
   out_8485858395715639244[260] = 0;
   out_8485858395715639244[261] = 0;
   out_8485858395715639244[262] = 0;
   out_8485858395715639244[263] = 0;
   out_8485858395715639244[264] = 0;
   out_8485858395715639244[265] = 0;
   out_8485858395715639244[266] = 1;
   out_8485858395715639244[267] = 0;
   out_8485858395715639244[268] = 0;
   out_8485858395715639244[269] = 0;
   out_8485858395715639244[270] = 0;
   out_8485858395715639244[271] = 0;
   out_8485858395715639244[272] = 0;
   out_8485858395715639244[273] = 0;
   out_8485858395715639244[274] = 0;
   out_8485858395715639244[275] = 0;
   out_8485858395715639244[276] = 0;
   out_8485858395715639244[277] = 0;
   out_8485858395715639244[278] = 0;
   out_8485858395715639244[279] = 0;
   out_8485858395715639244[280] = 0;
   out_8485858395715639244[281] = 0;
   out_8485858395715639244[282] = 0;
   out_8485858395715639244[283] = 0;
   out_8485858395715639244[284] = 0;
   out_8485858395715639244[285] = 1;
   out_8485858395715639244[286] = 0;
   out_8485858395715639244[287] = 0;
   out_8485858395715639244[288] = 0;
   out_8485858395715639244[289] = 0;
   out_8485858395715639244[290] = 0;
   out_8485858395715639244[291] = 0;
   out_8485858395715639244[292] = 0;
   out_8485858395715639244[293] = 0;
   out_8485858395715639244[294] = 0;
   out_8485858395715639244[295] = 0;
   out_8485858395715639244[296] = 0;
   out_8485858395715639244[297] = 0;
   out_8485858395715639244[298] = 0;
   out_8485858395715639244[299] = 0;
   out_8485858395715639244[300] = 0;
   out_8485858395715639244[301] = 0;
   out_8485858395715639244[302] = 0;
   out_8485858395715639244[303] = 0;
   out_8485858395715639244[304] = 1;
   out_8485858395715639244[305] = 0;
   out_8485858395715639244[306] = 0;
   out_8485858395715639244[307] = 0;
   out_8485858395715639244[308] = 0;
   out_8485858395715639244[309] = 0;
   out_8485858395715639244[310] = 0;
   out_8485858395715639244[311] = 0;
   out_8485858395715639244[312] = 0;
   out_8485858395715639244[313] = 0;
   out_8485858395715639244[314] = 0;
   out_8485858395715639244[315] = 0;
   out_8485858395715639244[316] = 0;
   out_8485858395715639244[317] = 0;
   out_8485858395715639244[318] = 0;
   out_8485858395715639244[319] = 0;
   out_8485858395715639244[320] = 0;
   out_8485858395715639244[321] = 0;
   out_8485858395715639244[322] = 0;
   out_8485858395715639244[323] = 1;
}
void h_4(double *state, double *unused, double *out_2463733989185154553) {
   out_2463733989185154553[0] = state[6] + state[9];
   out_2463733989185154553[1] = state[7] + state[10];
   out_2463733989185154553[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_5708361062915208992) {
   out_5708361062915208992[0] = 0;
   out_5708361062915208992[1] = 0;
   out_5708361062915208992[2] = 0;
   out_5708361062915208992[3] = 0;
   out_5708361062915208992[4] = 0;
   out_5708361062915208992[5] = 0;
   out_5708361062915208992[6] = 1;
   out_5708361062915208992[7] = 0;
   out_5708361062915208992[8] = 0;
   out_5708361062915208992[9] = 1;
   out_5708361062915208992[10] = 0;
   out_5708361062915208992[11] = 0;
   out_5708361062915208992[12] = 0;
   out_5708361062915208992[13] = 0;
   out_5708361062915208992[14] = 0;
   out_5708361062915208992[15] = 0;
   out_5708361062915208992[16] = 0;
   out_5708361062915208992[17] = 0;
   out_5708361062915208992[18] = 0;
   out_5708361062915208992[19] = 0;
   out_5708361062915208992[20] = 0;
   out_5708361062915208992[21] = 0;
   out_5708361062915208992[22] = 0;
   out_5708361062915208992[23] = 0;
   out_5708361062915208992[24] = 0;
   out_5708361062915208992[25] = 1;
   out_5708361062915208992[26] = 0;
   out_5708361062915208992[27] = 0;
   out_5708361062915208992[28] = 1;
   out_5708361062915208992[29] = 0;
   out_5708361062915208992[30] = 0;
   out_5708361062915208992[31] = 0;
   out_5708361062915208992[32] = 0;
   out_5708361062915208992[33] = 0;
   out_5708361062915208992[34] = 0;
   out_5708361062915208992[35] = 0;
   out_5708361062915208992[36] = 0;
   out_5708361062915208992[37] = 0;
   out_5708361062915208992[38] = 0;
   out_5708361062915208992[39] = 0;
   out_5708361062915208992[40] = 0;
   out_5708361062915208992[41] = 0;
   out_5708361062915208992[42] = 0;
   out_5708361062915208992[43] = 0;
   out_5708361062915208992[44] = 1;
   out_5708361062915208992[45] = 0;
   out_5708361062915208992[46] = 0;
   out_5708361062915208992[47] = 1;
   out_5708361062915208992[48] = 0;
   out_5708361062915208992[49] = 0;
   out_5708361062915208992[50] = 0;
   out_5708361062915208992[51] = 0;
   out_5708361062915208992[52] = 0;
   out_5708361062915208992[53] = 0;
}
void h_10(double *state, double *unused, double *out_447107545250377170) {
   out_447107545250377170[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_447107545250377170[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_447107545250377170[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_219357948856653379) {
   out_219357948856653379[0] = 0;
   out_219357948856653379[1] = 9.8100000000000005*cos(state[1]);
   out_219357948856653379[2] = 0;
   out_219357948856653379[3] = 0;
   out_219357948856653379[4] = -state[8];
   out_219357948856653379[5] = state[7];
   out_219357948856653379[6] = 0;
   out_219357948856653379[7] = state[5];
   out_219357948856653379[8] = -state[4];
   out_219357948856653379[9] = 0;
   out_219357948856653379[10] = 0;
   out_219357948856653379[11] = 0;
   out_219357948856653379[12] = 1;
   out_219357948856653379[13] = 0;
   out_219357948856653379[14] = 0;
   out_219357948856653379[15] = 1;
   out_219357948856653379[16] = 0;
   out_219357948856653379[17] = 0;
   out_219357948856653379[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_219357948856653379[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_219357948856653379[20] = 0;
   out_219357948856653379[21] = state[8];
   out_219357948856653379[22] = 0;
   out_219357948856653379[23] = -state[6];
   out_219357948856653379[24] = -state[5];
   out_219357948856653379[25] = 0;
   out_219357948856653379[26] = state[3];
   out_219357948856653379[27] = 0;
   out_219357948856653379[28] = 0;
   out_219357948856653379[29] = 0;
   out_219357948856653379[30] = 0;
   out_219357948856653379[31] = 1;
   out_219357948856653379[32] = 0;
   out_219357948856653379[33] = 0;
   out_219357948856653379[34] = 1;
   out_219357948856653379[35] = 0;
   out_219357948856653379[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_219357948856653379[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_219357948856653379[38] = 0;
   out_219357948856653379[39] = -state[7];
   out_219357948856653379[40] = state[6];
   out_219357948856653379[41] = 0;
   out_219357948856653379[42] = state[4];
   out_219357948856653379[43] = -state[3];
   out_219357948856653379[44] = 0;
   out_219357948856653379[45] = 0;
   out_219357948856653379[46] = 0;
   out_219357948856653379[47] = 0;
   out_219357948856653379[48] = 0;
   out_219357948856653379[49] = 0;
   out_219357948856653379[50] = 1;
   out_219357948856653379[51] = 0;
   out_219357948856653379[52] = 0;
   out_219357948856653379[53] = 1;
}
void h_13(double *state, double *unused, double *out_1364887226416245912) {
   out_1364887226416245912[0] = state[3];
   out_1364887226416245912[1] = state[4];
   out_1364887226416245912[2] = state[5];
}
void H_13(double *state, double *unused, double *out_2496087237582876191) {
   out_2496087237582876191[0] = 0;
   out_2496087237582876191[1] = 0;
   out_2496087237582876191[2] = 0;
   out_2496087237582876191[3] = 1;
   out_2496087237582876191[4] = 0;
   out_2496087237582876191[5] = 0;
   out_2496087237582876191[6] = 0;
   out_2496087237582876191[7] = 0;
   out_2496087237582876191[8] = 0;
   out_2496087237582876191[9] = 0;
   out_2496087237582876191[10] = 0;
   out_2496087237582876191[11] = 0;
   out_2496087237582876191[12] = 0;
   out_2496087237582876191[13] = 0;
   out_2496087237582876191[14] = 0;
   out_2496087237582876191[15] = 0;
   out_2496087237582876191[16] = 0;
   out_2496087237582876191[17] = 0;
   out_2496087237582876191[18] = 0;
   out_2496087237582876191[19] = 0;
   out_2496087237582876191[20] = 0;
   out_2496087237582876191[21] = 0;
   out_2496087237582876191[22] = 1;
   out_2496087237582876191[23] = 0;
   out_2496087237582876191[24] = 0;
   out_2496087237582876191[25] = 0;
   out_2496087237582876191[26] = 0;
   out_2496087237582876191[27] = 0;
   out_2496087237582876191[28] = 0;
   out_2496087237582876191[29] = 0;
   out_2496087237582876191[30] = 0;
   out_2496087237582876191[31] = 0;
   out_2496087237582876191[32] = 0;
   out_2496087237582876191[33] = 0;
   out_2496087237582876191[34] = 0;
   out_2496087237582876191[35] = 0;
   out_2496087237582876191[36] = 0;
   out_2496087237582876191[37] = 0;
   out_2496087237582876191[38] = 0;
   out_2496087237582876191[39] = 0;
   out_2496087237582876191[40] = 0;
   out_2496087237582876191[41] = 1;
   out_2496087237582876191[42] = 0;
   out_2496087237582876191[43] = 0;
   out_2496087237582876191[44] = 0;
   out_2496087237582876191[45] = 0;
   out_2496087237582876191[46] = 0;
   out_2496087237582876191[47] = 0;
   out_2496087237582876191[48] = 0;
   out_2496087237582876191[49] = 0;
   out_2496087237582876191[50] = 0;
   out_2496087237582876191[51] = 0;
   out_2496087237582876191[52] = 0;
   out_2496087237582876191[53] = 0;
}
void h_14(double *state, double *unused, double *out_5491047812010955419) {
   out_5491047812010955419[0] = state[6];
   out_5491047812010955419[1] = state[7];
   out_5491047812010955419[2] = state[8];
}
void H_14(double *state, double *unused, double *out_8791149495210581288) {
   out_8791149495210581288[0] = 0;
   out_8791149495210581288[1] = 0;
   out_8791149495210581288[2] = 0;
   out_8791149495210581288[3] = 0;
   out_8791149495210581288[4] = 0;
   out_8791149495210581288[5] = 0;
   out_8791149495210581288[6] = 1;
   out_8791149495210581288[7] = 0;
   out_8791149495210581288[8] = 0;
   out_8791149495210581288[9] = 0;
   out_8791149495210581288[10] = 0;
   out_8791149495210581288[11] = 0;
   out_8791149495210581288[12] = 0;
   out_8791149495210581288[13] = 0;
   out_8791149495210581288[14] = 0;
   out_8791149495210581288[15] = 0;
   out_8791149495210581288[16] = 0;
   out_8791149495210581288[17] = 0;
   out_8791149495210581288[18] = 0;
   out_8791149495210581288[19] = 0;
   out_8791149495210581288[20] = 0;
   out_8791149495210581288[21] = 0;
   out_8791149495210581288[22] = 0;
   out_8791149495210581288[23] = 0;
   out_8791149495210581288[24] = 0;
   out_8791149495210581288[25] = 1;
   out_8791149495210581288[26] = 0;
   out_8791149495210581288[27] = 0;
   out_8791149495210581288[28] = 0;
   out_8791149495210581288[29] = 0;
   out_8791149495210581288[30] = 0;
   out_8791149495210581288[31] = 0;
   out_8791149495210581288[32] = 0;
   out_8791149495210581288[33] = 0;
   out_8791149495210581288[34] = 0;
   out_8791149495210581288[35] = 0;
   out_8791149495210581288[36] = 0;
   out_8791149495210581288[37] = 0;
   out_8791149495210581288[38] = 0;
   out_8791149495210581288[39] = 0;
   out_8791149495210581288[40] = 0;
   out_8791149495210581288[41] = 0;
   out_8791149495210581288[42] = 0;
   out_8791149495210581288[43] = 0;
   out_8791149495210581288[44] = 1;
   out_8791149495210581288[45] = 0;
   out_8791149495210581288[46] = 0;
   out_8791149495210581288[47] = 0;
   out_8791149495210581288[48] = 0;
   out_8791149495210581288[49] = 0;
   out_8791149495210581288[50] = 0;
   out_8791149495210581288[51] = 0;
   out_8791149495210581288[52] = 0;
   out_8791149495210581288[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_4554654253610197066) {
  err_fun(nom_x, delta_x, out_4554654253610197066);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_7859607288829869304) {
  inv_err_fun(nom_x, true_x, out_7859607288829869304);
}
void pose_H_mod_fun(double *state, double *out_7585864625755261889) {
  H_mod_fun(state, out_7585864625755261889);
}
void pose_f_fun(double *state, double dt, double *out_8989872321626802535) {
  f_fun(state,  dt, out_8989872321626802535);
}
void pose_F_fun(double *state, double dt, double *out_8485858395715639244) {
  F_fun(state,  dt, out_8485858395715639244);
}
void pose_h_4(double *state, double *unused, double *out_2463733989185154553) {
  h_4(state, unused, out_2463733989185154553);
}
void pose_H_4(double *state, double *unused, double *out_5708361062915208992) {
  H_4(state, unused, out_5708361062915208992);
}
void pose_h_10(double *state, double *unused, double *out_447107545250377170) {
  h_10(state, unused, out_447107545250377170);
}
void pose_H_10(double *state, double *unused, double *out_219357948856653379) {
  H_10(state, unused, out_219357948856653379);
}
void pose_h_13(double *state, double *unused, double *out_1364887226416245912) {
  h_13(state, unused, out_1364887226416245912);
}
void pose_H_13(double *state, double *unused, double *out_2496087237582876191) {
  H_13(state, unused, out_2496087237582876191);
}
void pose_h_14(double *state, double *unused, double *out_5491047812010955419) {
  h_14(state, unused, out_5491047812010955419);
}
void pose_H_14(double *state, double *unused, double *out_8791149495210581288) {
  H_14(state, unused, out_8791149495210581288);
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
