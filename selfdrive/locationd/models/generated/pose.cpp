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
void err_fun(double *nom_x, double *delta_x, double *out_5782186265648731279) {
   out_5782186265648731279[0] = delta_x[0] + nom_x[0];
   out_5782186265648731279[1] = delta_x[1] + nom_x[1];
   out_5782186265648731279[2] = delta_x[2] + nom_x[2];
   out_5782186265648731279[3] = delta_x[3] + nom_x[3];
   out_5782186265648731279[4] = delta_x[4] + nom_x[4];
   out_5782186265648731279[5] = delta_x[5] + nom_x[5];
   out_5782186265648731279[6] = delta_x[6] + nom_x[6];
   out_5782186265648731279[7] = delta_x[7] + nom_x[7];
   out_5782186265648731279[8] = delta_x[8] + nom_x[8];
   out_5782186265648731279[9] = delta_x[9] + nom_x[9];
   out_5782186265648731279[10] = delta_x[10] + nom_x[10];
   out_5782186265648731279[11] = delta_x[11] + nom_x[11];
   out_5782186265648731279[12] = delta_x[12] + nom_x[12];
   out_5782186265648731279[13] = delta_x[13] + nom_x[13];
   out_5782186265648731279[14] = delta_x[14] + nom_x[14];
   out_5782186265648731279[15] = delta_x[15] + nom_x[15];
   out_5782186265648731279[16] = delta_x[16] + nom_x[16];
   out_5782186265648731279[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7193052209322201941) {
   out_7193052209322201941[0] = -nom_x[0] + true_x[0];
   out_7193052209322201941[1] = -nom_x[1] + true_x[1];
   out_7193052209322201941[2] = -nom_x[2] + true_x[2];
   out_7193052209322201941[3] = -nom_x[3] + true_x[3];
   out_7193052209322201941[4] = -nom_x[4] + true_x[4];
   out_7193052209322201941[5] = -nom_x[5] + true_x[5];
   out_7193052209322201941[6] = -nom_x[6] + true_x[6];
   out_7193052209322201941[7] = -nom_x[7] + true_x[7];
   out_7193052209322201941[8] = -nom_x[8] + true_x[8];
   out_7193052209322201941[9] = -nom_x[9] + true_x[9];
   out_7193052209322201941[10] = -nom_x[10] + true_x[10];
   out_7193052209322201941[11] = -nom_x[11] + true_x[11];
   out_7193052209322201941[12] = -nom_x[12] + true_x[12];
   out_7193052209322201941[13] = -nom_x[13] + true_x[13];
   out_7193052209322201941[14] = -nom_x[14] + true_x[14];
   out_7193052209322201941[15] = -nom_x[15] + true_x[15];
   out_7193052209322201941[16] = -nom_x[16] + true_x[16];
   out_7193052209322201941[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_8077327556656833445) {
   out_8077327556656833445[0] = 1.0;
   out_8077327556656833445[1] = 0.0;
   out_8077327556656833445[2] = 0.0;
   out_8077327556656833445[3] = 0.0;
   out_8077327556656833445[4] = 0.0;
   out_8077327556656833445[5] = 0.0;
   out_8077327556656833445[6] = 0.0;
   out_8077327556656833445[7] = 0.0;
   out_8077327556656833445[8] = 0.0;
   out_8077327556656833445[9] = 0.0;
   out_8077327556656833445[10] = 0.0;
   out_8077327556656833445[11] = 0.0;
   out_8077327556656833445[12] = 0.0;
   out_8077327556656833445[13] = 0.0;
   out_8077327556656833445[14] = 0.0;
   out_8077327556656833445[15] = 0.0;
   out_8077327556656833445[16] = 0.0;
   out_8077327556656833445[17] = 0.0;
   out_8077327556656833445[18] = 0.0;
   out_8077327556656833445[19] = 1.0;
   out_8077327556656833445[20] = 0.0;
   out_8077327556656833445[21] = 0.0;
   out_8077327556656833445[22] = 0.0;
   out_8077327556656833445[23] = 0.0;
   out_8077327556656833445[24] = 0.0;
   out_8077327556656833445[25] = 0.0;
   out_8077327556656833445[26] = 0.0;
   out_8077327556656833445[27] = 0.0;
   out_8077327556656833445[28] = 0.0;
   out_8077327556656833445[29] = 0.0;
   out_8077327556656833445[30] = 0.0;
   out_8077327556656833445[31] = 0.0;
   out_8077327556656833445[32] = 0.0;
   out_8077327556656833445[33] = 0.0;
   out_8077327556656833445[34] = 0.0;
   out_8077327556656833445[35] = 0.0;
   out_8077327556656833445[36] = 0.0;
   out_8077327556656833445[37] = 0.0;
   out_8077327556656833445[38] = 1.0;
   out_8077327556656833445[39] = 0.0;
   out_8077327556656833445[40] = 0.0;
   out_8077327556656833445[41] = 0.0;
   out_8077327556656833445[42] = 0.0;
   out_8077327556656833445[43] = 0.0;
   out_8077327556656833445[44] = 0.0;
   out_8077327556656833445[45] = 0.0;
   out_8077327556656833445[46] = 0.0;
   out_8077327556656833445[47] = 0.0;
   out_8077327556656833445[48] = 0.0;
   out_8077327556656833445[49] = 0.0;
   out_8077327556656833445[50] = 0.0;
   out_8077327556656833445[51] = 0.0;
   out_8077327556656833445[52] = 0.0;
   out_8077327556656833445[53] = 0.0;
   out_8077327556656833445[54] = 0.0;
   out_8077327556656833445[55] = 0.0;
   out_8077327556656833445[56] = 0.0;
   out_8077327556656833445[57] = 1.0;
   out_8077327556656833445[58] = 0.0;
   out_8077327556656833445[59] = 0.0;
   out_8077327556656833445[60] = 0.0;
   out_8077327556656833445[61] = 0.0;
   out_8077327556656833445[62] = 0.0;
   out_8077327556656833445[63] = 0.0;
   out_8077327556656833445[64] = 0.0;
   out_8077327556656833445[65] = 0.0;
   out_8077327556656833445[66] = 0.0;
   out_8077327556656833445[67] = 0.0;
   out_8077327556656833445[68] = 0.0;
   out_8077327556656833445[69] = 0.0;
   out_8077327556656833445[70] = 0.0;
   out_8077327556656833445[71] = 0.0;
   out_8077327556656833445[72] = 0.0;
   out_8077327556656833445[73] = 0.0;
   out_8077327556656833445[74] = 0.0;
   out_8077327556656833445[75] = 0.0;
   out_8077327556656833445[76] = 1.0;
   out_8077327556656833445[77] = 0.0;
   out_8077327556656833445[78] = 0.0;
   out_8077327556656833445[79] = 0.0;
   out_8077327556656833445[80] = 0.0;
   out_8077327556656833445[81] = 0.0;
   out_8077327556656833445[82] = 0.0;
   out_8077327556656833445[83] = 0.0;
   out_8077327556656833445[84] = 0.0;
   out_8077327556656833445[85] = 0.0;
   out_8077327556656833445[86] = 0.0;
   out_8077327556656833445[87] = 0.0;
   out_8077327556656833445[88] = 0.0;
   out_8077327556656833445[89] = 0.0;
   out_8077327556656833445[90] = 0.0;
   out_8077327556656833445[91] = 0.0;
   out_8077327556656833445[92] = 0.0;
   out_8077327556656833445[93] = 0.0;
   out_8077327556656833445[94] = 0.0;
   out_8077327556656833445[95] = 1.0;
   out_8077327556656833445[96] = 0.0;
   out_8077327556656833445[97] = 0.0;
   out_8077327556656833445[98] = 0.0;
   out_8077327556656833445[99] = 0.0;
   out_8077327556656833445[100] = 0.0;
   out_8077327556656833445[101] = 0.0;
   out_8077327556656833445[102] = 0.0;
   out_8077327556656833445[103] = 0.0;
   out_8077327556656833445[104] = 0.0;
   out_8077327556656833445[105] = 0.0;
   out_8077327556656833445[106] = 0.0;
   out_8077327556656833445[107] = 0.0;
   out_8077327556656833445[108] = 0.0;
   out_8077327556656833445[109] = 0.0;
   out_8077327556656833445[110] = 0.0;
   out_8077327556656833445[111] = 0.0;
   out_8077327556656833445[112] = 0.0;
   out_8077327556656833445[113] = 0.0;
   out_8077327556656833445[114] = 1.0;
   out_8077327556656833445[115] = 0.0;
   out_8077327556656833445[116] = 0.0;
   out_8077327556656833445[117] = 0.0;
   out_8077327556656833445[118] = 0.0;
   out_8077327556656833445[119] = 0.0;
   out_8077327556656833445[120] = 0.0;
   out_8077327556656833445[121] = 0.0;
   out_8077327556656833445[122] = 0.0;
   out_8077327556656833445[123] = 0.0;
   out_8077327556656833445[124] = 0.0;
   out_8077327556656833445[125] = 0.0;
   out_8077327556656833445[126] = 0.0;
   out_8077327556656833445[127] = 0.0;
   out_8077327556656833445[128] = 0.0;
   out_8077327556656833445[129] = 0.0;
   out_8077327556656833445[130] = 0.0;
   out_8077327556656833445[131] = 0.0;
   out_8077327556656833445[132] = 0.0;
   out_8077327556656833445[133] = 1.0;
   out_8077327556656833445[134] = 0.0;
   out_8077327556656833445[135] = 0.0;
   out_8077327556656833445[136] = 0.0;
   out_8077327556656833445[137] = 0.0;
   out_8077327556656833445[138] = 0.0;
   out_8077327556656833445[139] = 0.0;
   out_8077327556656833445[140] = 0.0;
   out_8077327556656833445[141] = 0.0;
   out_8077327556656833445[142] = 0.0;
   out_8077327556656833445[143] = 0.0;
   out_8077327556656833445[144] = 0.0;
   out_8077327556656833445[145] = 0.0;
   out_8077327556656833445[146] = 0.0;
   out_8077327556656833445[147] = 0.0;
   out_8077327556656833445[148] = 0.0;
   out_8077327556656833445[149] = 0.0;
   out_8077327556656833445[150] = 0.0;
   out_8077327556656833445[151] = 0.0;
   out_8077327556656833445[152] = 1.0;
   out_8077327556656833445[153] = 0.0;
   out_8077327556656833445[154] = 0.0;
   out_8077327556656833445[155] = 0.0;
   out_8077327556656833445[156] = 0.0;
   out_8077327556656833445[157] = 0.0;
   out_8077327556656833445[158] = 0.0;
   out_8077327556656833445[159] = 0.0;
   out_8077327556656833445[160] = 0.0;
   out_8077327556656833445[161] = 0.0;
   out_8077327556656833445[162] = 0.0;
   out_8077327556656833445[163] = 0.0;
   out_8077327556656833445[164] = 0.0;
   out_8077327556656833445[165] = 0.0;
   out_8077327556656833445[166] = 0.0;
   out_8077327556656833445[167] = 0.0;
   out_8077327556656833445[168] = 0.0;
   out_8077327556656833445[169] = 0.0;
   out_8077327556656833445[170] = 0.0;
   out_8077327556656833445[171] = 1.0;
   out_8077327556656833445[172] = 0.0;
   out_8077327556656833445[173] = 0.0;
   out_8077327556656833445[174] = 0.0;
   out_8077327556656833445[175] = 0.0;
   out_8077327556656833445[176] = 0.0;
   out_8077327556656833445[177] = 0.0;
   out_8077327556656833445[178] = 0.0;
   out_8077327556656833445[179] = 0.0;
   out_8077327556656833445[180] = 0.0;
   out_8077327556656833445[181] = 0.0;
   out_8077327556656833445[182] = 0.0;
   out_8077327556656833445[183] = 0.0;
   out_8077327556656833445[184] = 0.0;
   out_8077327556656833445[185] = 0.0;
   out_8077327556656833445[186] = 0.0;
   out_8077327556656833445[187] = 0.0;
   out_8077327556656833445[188] = 0.0;
   out_8077327556656833445[189] = 0.0;
   out_8077327556656833445[190] = 1.0;
   out_8077327556656833445[191] = 0.0;
   out_8077327556656833445[192] = 0.0;
   out_8077327556656833445[193] = 0.0;
   out_8077327556656833445[194] = 0.0;
   out_8077327556656833445[195] = 0.0;
   out_8077327556656833445[196] = 0.0;
   out_8077327556656833445[197] = 0.0;
   out_8077327556656833445[198] = 0.0;
   out_8077327556656833445[199] = 0.0;
   out_8077327556656833445[200] = 0.0;
   out_8077327556656833445[201] = 0.0;
   out_8077327556656833445[202] = 0.0;
   out_8077327556656833445[203] = 0.0;
   out_8077327556656833445[204] = 0.0;
   out_8077327556656833445[205] = 0.0;
   out_8077327556656833445[206] = 0.0;
   out_8077327556656833445[207] = 0.0;
   out_8077327556656833445[208] = 0.0;
   out_8077327556656833445[209] = 1.0;
   out_8077327556656833445[210] = 0.0;
   out_8077327556656833445[211] = 0.0;
   out_8077327556656833445[212] = 0.0;
   out_8077327556656833445[213] = 0.0;
   out_8077327556656833445[214] = 0.0;
   out_8077327556656833445[215] = 0.0;
   out_8077327556656833445[216] = 0.0;
   out_8077327556656833445[217] = 0.0;
   out_8077327556656833445[218] = 0.0;
   out_8077327556656833445[219] = 0.0;
   out_8077327556656833445[220] = 0.0;
   out_8077327556656833445[221] = 0.0;
   out_8077327556656833445[222] = 0.0;
   out_8077327556656833445[223] = 0.0;
   out_8077327556656833445[224] = 0.0;
   out_8077327556656833445[225] = 0.0;
   out_8077327556656833445[226] = 0.0;
   out_8077327556656833445[227] = 0.0;
   out_8077327556656833445[228] = 1.0;
   out_8077327556656833445[229] = 0.0;
   out_8077327556656833445[230] = 0.0;
   out_8077327556656833445[231] = 0.0;
   out_8077327556656833445[232] = 0.0;
   out_8077327556656833445[233] = 0.0;
   out_8077327556656833445[234] = 0.0;
   out_8077327556656833445[235] = 0.0;
   out_8077327556656833445[236] = 0.0;
   out_8077327556656833445[237] = 0.0;
   out_8077327556656833445[238] = 0.0;
   out_8077327556656833445[239] = 0.0;
   out_8077327556656833445[240] = 0.0;
   out_8077327556656833445[241] = 0.0;
   out_8077327556656833445[242] = 0.0;
   out_8077327556656833445[243] = 0.0;
   out_8077327556656833445[244] = 0.0;
   out_8077327556656833445[245] = 0.0;
   out_8077327556656833445[246] = 0.0;
   out_8077327556656833445[247] = 1.0;
   out_8077327556656833445[248] = 0.0;
   out_8077327556656833445[249] = 0.0;
   out_8077327556656833445[250] = 0.0;
   out_8077327556656833445[251] = 0.0;
   out_8077327556656833445[252] = 0.0;
   out_8077327556656833445[253] = 0.0;
   out_8077327556656833445[254] = 0.0;
   out_8077327556656833445[255] = 0.0;
   out_8077327556656833445[256] = 0.0;
   out_8077327556656833445[257] = 0.0;
   out_8077327556656833445[258] = 0.0;
   out_8077327556656833445[259] = 0.0;
   out_8077327556656833445[260] = 0.0;
   out_8077327556656833445[261] = 0.0;
   out_8077327556656833445[262] = 0.0;
   out_8077327556656833445[263] = 0.0;
   out_8077327556656833445[264] = 0.0;
   out_8077327556656833445[265] = 0.0;
   out_8077327556656833445[266] = 1.0;
   out_8077327556656833445[267] = 0.0;
   out_8077327556656833445[268] = 0.0;
   out_8077327556656833445[269] = 0.0;
   out_8077327556656833445[270] = 0.0;
   out_8077327556656833445[271] = 0.0;
   out_8077327556656833445[272] = 0.0;
   out_8077327556656833445[273] = 0.0;
   out_8077327556656833445[274] = 0.0;
   out_8077327556656833445[275] = 0.0;
   out_8077327556656833445[276] = 0.0;
   out_8077327556656833445[277] = 0.0;
   out_8077327556656833445[278] = 0.0;
   out_8077327556656833445[279] = 0.0;
   out_8077327556656833445[280] = 0.0;
   out_8077327556656833445[281] = 0.0;
   out_8077327556656833445[282] = 0.0;
   out_8077327556656833445[283] = 0.0;
   out_8077327556656833445[284] = 0.0;
   out_8077327556656833445[285] = 1.0;
   out_8077327556656833445[286] = 0.0;
   out_8077327556656833445[287] = 0.0;
   out_8077327556656833445[288] = 0.0;
   out_8077327556656833445[289] = 0.0;
   out_8077327556656833445[290] = 0.0;
   out_8077327556656833445[291] = 0.0;
   out_8077327556656833445[292] = 0.0;
   out_8077327556656833445[293] = 0.0;
   out_8077327556656833445[294] = 0.0;
   out_8077327556656833445[295] = 0.0;
   out_8077327556656833445[296] = 0.0;
   out_8077327556656833445[297] = 0.0;
   out_8077327556656833445[298] = 0.0;
   out_8077327556656833445[299] = 0.0;
   out_8077327556656833445[300] = 0.0;
   out_8077327556656833445[301] = 0.0;
   out_8077327556656833445[302] = 0.0;
   out_8077327556656833445[303] = 0.0;
   out_8077327556656833445[304] = 1.0;
   out_8077327556656833445[305] = 0.0;
   out_8077327556656833445[306] = 0.0;
   out_8077327556656833445[307] = 0.0;
   out_8077327556656833445[308] = 0.0;
   out_8077327556656833445[309] = 0.0;
   out_8077327556656833445[310] = 0.0;
   out_8077327556656833445[311] = 0.0;
   out_8077327556656833445[312] = 0.0;
   out_8077327556656833445[313] = 0.0;
   out_8077327556656833445[314] = 0.0;
   out_8077327556656833445[315] = 0.0;
   out_8077327556656833445[316] = 0.0;
   out_8077327556656833445[317] = 0.0;
   out_8077327556656833445[318] = 0.0;
   out_8077327556656833445[319] = 0.0;
   out_8077327556656833445[320] = 0.0;
   out_8077327556656833445[321] = 0.0;
   out_8077327556656833445[322] = 0.0;
   out_8077327556656833445[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_6245206989908436510) {
   out_6245206989908436510[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_6245206989908436510[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_6245206989908436510[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_6245206989908436510[3] = dt*state[12] + state[3];
   out_6245206989908436510[4] = dt*state[13] + state[4];
   out_6245206989908436510[5] = dt*state[14] + state[5];
   out_6245206989908436510[6] = state[6];
   out_6245206989908436510[7] = state[7];
   out_6245206989908436510[8] = state[8];
   out_6245206989908436510[9] = state[9];
   out_6245206989908436510[10] = state[10];
   out_6245206989908436510[11] = state[11];
   out_6245206989908436510[12] = state[12];
   out_6245206989908436510[13] = state[13];
   out_6245206989908436510[14] = state[14];
   out_6245206989908436510[15] = state[15];
   out_6245206989908436510[16] = state[16];
   out_6245206989908436510[17] = state[17];
}
void F_fun(double *state, double dt, double *out_1848154903834159695) {
   out_1848154903834159695[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1848154903834159695[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1848154903834159695[2] = 0;
   out_1848154903834159695[3] = 0;
   out_1848154903834159695[4] = 0;
   out_1848154903834159695[5] = 0;
   out_1848154903834159695[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1848154903834159695[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1848154903834159695[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1848154903834159695[9] = 0;
   out_1848154903834159695[10] = 0;
   out_1848154903834159695[11] = 0;
   out_1848154903834159695[12] = 0;
   out_1848154903834159695[13] = 0;
   out_1848154903834159695[14] = 0;
   out_1848154903834159695[15] = 0;
   out_1848154903834159695[16] = 0;
   out_1848154903834159695[17] = 0;
   out_1848154903834159695[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_1848154903834159695[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_1848154903834159695[20] = 0;
   out_1848154903834159695[21] = 0;
   out_1848154903834159695[22] = 0;
   out_1848154903834159695[23] = 0;
   out_1848154903834159695[24] = 0;
   out_1848154903834159695[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_1848154903834159695[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_1848154903834159695[27] = 0;
   out_1848154903834159695[28] = 0;
   out_1848154903834159695[29] = 0;
   out_1848154903834159695[30] = 0;
   out_1848154903834159695[31] = 0;
   out_1848154903834159695[32] = 0;
   out_1848154903834159695[33] = 0;
   out_1848154903834159695[34] = 0;
   out_1848154903834159695[35] = 0;
   out_1848154903834159695[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1848154903834159695[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1848154903834159695[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1848154903834159695[39] = 0;
   out_1848154903834159695[40] = 0;
   out_1848154903834159695[41] = 0;
   out_1848154903834159695[42] = 0;
   out_1848154903834159695[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1848154903834159695[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1848154903834159695[45] = 0;
   out_1848154903834159695[46] = 0;
   out_1848154903834159695[47] = 0;
   out_1848154903834159695[48] = 0;
   out_1848154903834159695[49] = 0;
   out_1848154903834159695[50] = 0;
   out_1848154903834159695[51] = 0;
   out_1848154903834159695[52] = 0;
   out_1848154903834159695[53] = 0;
   out_1848154903834159695[54] = 0;
   out_1848154903834159695[55] = 0;
   out_1848154903834159695[56] = 0;
   out_1848154903834159695[57] = 1;
   out_1848154903834159695[58] = 0;
   out_1848154903834159695[59] = 0;
   out_1848154903834159695[60] = 0;
   out_1848154903834159695[61] = 0;
   out_1848154903834159695[62] = 0;
   out_1848154903834159695[63] = 0;
   out_1848154903834159695[64] = 0;
   out_1848154903834159695[65] = 0;
   out_1848154903834159695[66] = dt;
   out_1848154903834159695[67] = 0;
   out_1848154903834159695[68] = 0;
   out_1848154903834159695[69] = 0;
   out_1848154903834159695[70] = 0;
   out_1848154903834159695[71] = 0;
   out_1848154903834159695[72] = 0;
   out_1848154903834159695[73] = 0;
   out_1848154903834159695[74] = 0;
   out_1848154903834159695[75] = 0;
   out_1848154903834159695[76] = 1;
   out_1848154903834159695[77] = 0;
   out_1848154903834159695[78] = 0;
   out_1848154903834159695[79] = 0;
   out_1848154903834159695[80] = 0;
   out_1848154903834159695[81] = 0;
   out_1848154903834159695[82] = 0;
   out_1848154903834159695[83] = 0;
   out_1848154903834159695[84] = 0;
   out_1848154903834159695[85] = dt;
   out_1848154903834159695[86] = 0;
   out_1848154903834159695[87] = 0;
   out_1848154903834159695[88] = 0;
   out_1848154903834159695[89] = 0;
   out_1848154903834159695[90] = 0;
   out_1848154903834159695[91] = 0;
   out_1848154903834159695[92] = 0;
   out_1848154903834159695[93] = 0;
   out_1848154903834159695[94] = 0;
   out_1848154903834159695[95] = 1;
   out_1848154903834159695[96] = 0;
   out_1848154903834159695[97] = 0;
   out_1848154903834159695[98] = 0;
   out_1848154903834159695[99] = 0;
   out_1848154903834159695[100] = 0;
   out_1848154903834159695[101] = 0;
   out_1848154903834159695[102] = 0;
   out_1848154903834159695[103] = 0;
   out_1848154903834159695[104] = dt;
   out_1848154903834159695[105] = 0;
   out_1848154903834159695[106] = 0;
   out_1848154903834159695[107] = 0;
   out_1848154903834159695[108] = 0;
   out_1848154903834159695[109] = 0;
   out_1848154903834159695[110] = 0;
   out_1848154903834159695[111] = 0;
   out_1848154903834159695[112] = 0;
   out_1848154903834159695[113] = 0;
   out_1848154903834159695[114] = 1;
   out_1848154903834159695[115] = 0;
   out_1848154903834159695[116] = 0;
   out_1848154903834159695[117] = 0;
   out_1848154903834159695[118] = 0;
   out_1848154903834159695[119] = 0;
   out_1848154903834159695[120] = 0;
   out_1848154903834159695[121] = 0;
   out_1848154903834159695[122] = 0;
   out_1848154903834159695[123] = 0;
   out_1848154903834159695[124] = 0;
   out_1848154903834159695[125] = 0;
   out_1848154903834159695[126] = 0;
   out_1848154903834159695[127] = 0;
   out_1848154903834159695[128] = 0;
   out_1848154903834159695[129] = 0;
   out_1848154903834159695[130] = 0;
   out_1848154903834159695[131] = 0;
   out_1848154903834159695[132] = 0;
   out_1848154903834159695[133] = 1;
   out_1848154903834159695[134] = 0;
   out_1848154903834159695[135] = 0;
   out_1848154903834159695[136] = 0;
   out_1848154903834159695[137] = 0;
   out_1848154903834159695[138] = 0;
   out_1848154903834159695[139] = 0;
   out_1848154903834159695[140] = 0;
   out_1848154903834159695[141] = 0;
   out_1848154903834159695[142] = 0;
   out_1848154903834159695[143] = 0;
   out_1848154903834159695[144] = 0;
   out_1848154903834159695[145] = 0;
   out_1848154903834159695[146] = 0;
   out_1848154903834159695[147] = 0;
   out_1848154903834159695[148] = 0;
   out_1848154903834159695[149] = 0;
   out_1848154903834159695[150] = 0;
   out_1848154903834159695[151] = 0;
   out_1848154903834159695[152] = 1;
   out_1848154903834159695[153] = 0;
   out_1848154903834159695[154] = 0;
   out_1848154903834159695[155] = 0;
   out_1848154903834159695[156] = 0;
   out_1848154903834159695[157] = 0;
   out_1848154903834159695[158] = 0;
   out_1848154903834159695[159] = 0;
   out_1848154903834159695[160] = 0;
   out_1848154903834159695[161] = 0;
   out_1848154903834159695[162] = 0;
   out_1848154903834159695[163] = 0;
   out_1848154903834159695[164] = 0;
   out_1848154903834159695[165] = 0;
   out_1848154903834159695[166] = 0;
   out_1848154903834159695[167] = 0;
   out_1848154903834159695[168] = 0;
   out_1848154903834159695[169] = 0;
   out_1848154903834159695[170] = 0;
   out_1848154903834159695[171] = 1;
   out_1848154903834159695[172] = 0;
   out_1848154903834159695[173] = 0;
   out_1848154903834159695[174] = 0;
   out_1848154903834159695[175] = 0;
   out_1848154903834159695[176] = 0;
   out_1848154903834159695[177] = 0;
   out_1848154903834159695[178] = 0;
   out_1848154903834159695[179] = 0;
   out_1848154903834159695[180] = 0;
   out_1848154903834159695[181] = 0;
   out_1848154903834159695[182] = 0;
   out_1848154903834159695[183] = 0;
   out_1848154903834159695[184] = 0;
   out_1848154903834159695[185] = 0;
   out_1848154903834159695[186] = 0;
   out_1848154903834159695[187] = 0;
   out_1848154903834159695[188] = 0;
   out_1848154903834159695[189] = 0;
   out_1848154903834159695[190] = 1;
   out_1848154903834159695[191] = 0;
   out_1848154903834159695[192] = 0;
   out_1848154903834159695[193] = 0;
   out_1848154903834159695[194] = 0;
   out_1848154903834159695[195] = 0;
   out_1848154903834159695[196] = 0;
   out_1848154903834159695[197] = 0;
   out_1848154903834159695[198] = 0;
   out_1848154903834159695[199] = 0;
   out_1848154903834159695[200] = 0;
   out_1848154903834159695[201] = 0;
   out_1848154903834159695[202] = 0;
   out_1848154903834159695[203] = 0;
   out_1848154903834159695[204] = 0;
   out_1848154903834159695[205] = 0;
   out_1848154903834159695[206] = 0;
   out_1848154903834159695[207] = 0;
   out_1848154903834159695[208] = 0;
   out_1848154903834159695[209] = 1;
   out_1848154903834159695[210] = 0;
   out_1848154903834159695[211] = 0;
   out_1848154903834159695[212] = 0;
   out_1848154903834159695[213] = 0;
   out_1848154903834159695[214] = 0;
   out_1848154903834159695[215] = 0;
   out_1848154903834159695[216] = 0;
   out_1848154903834159695[217] = 0;
   out_1848154903834159695[218] = 0;
   out_1848154903834159695[219] = 0;
   out_1848154903834159695[220] = 0;
   out_1848154903834159695[221] = 0;
   out_1848154903834159695[222] = 0;
   out_1848154903834159695[223] = 0;
   out_1848154903834159695[224] = 0;
   out_1848154903834159695[225] = 0;
   out_1848154903834159695[226] = 0;
   out_1848154903834159695[227] = 0;
   out_1848154903834159695[228] = 1;
   out_1848154903834159695[229] = 0;
   out_1848154903834159695[230] = 0;
   out_1848154903834159695[231] = 0;
   out_1848154903834159695[232] = 0;
   out_1848154903834159695[233] = 0;
   out_1848154903834159695[234] = 0;
   out_1848154903834159695[235] = 0;
   out_1848154903834159695[236] = 0;
   out_1848154903834159695[237] = 0;
   out_1848154903834159695[238] = 0;
   out_1848154903834159695[239] = 0;
   out_1848154903834159695[240] = 0;
   out_1848154903834159695[241] = 0;
   out_1848154903834159695[242] = 0;
   out_1848154903834159695[243] = 0;
   out_1848154903834159695[244] = 0;
   out_1848154903834159695[245] = 0;
   out_1848154903834159695[246] = 0;
   out_1848154903834159695[247] = 1;
   out_1848154903834159695[248] = 0;
   out_1848154903834159695[249] = 0;
   out_1848154903834159695[250] = 0;
   out_1848154903834159695[251] = 0;
   out_1848154903834159695[252] = 0;
   out_1848154903834159695[253] = 0;
   out_1848154903834159695[254] = 0;
   out_1848154903834159695[255] = 0;
   out_1848154903834159695[256] = 0;
   out_1848154903834159695[257] = 0;
   out_1848154903834159695[258] = 0;
   out_1848154903834159695[259] = 0;
   out_1848154903834159695[260] = 0;
   out_1848154903834159695[261] = 0;
   out_1848154903834159695[262] = 0;
   out_1848154903834159695[263] = 0;
   out_1848154903834159695[264] = 0;
   out_1848154903834159695[265] = 0;
   out_1848154903834159695[266] = 1;
   out_1848154903834159695[267] = 0;
   out_1848154903834159695[268] = 0;
   out_1848154903834159695[269] = 0;
   out_1848154903834159695[270] = 0;
   out_1848154903834159695[271] = 0;
   out_1848154903834159695[272] = 0;
   out_1848154903834159695[273] = 0;
   out_1848154903834159695[274] = 0;
   out_1848154903834159695[275] = 0;
   out_1848154903834159695[276] = 0;
   out_1848154903834159695[277] = 0;
   out_1848154903834159695[278] = 0;
   out_1848154903834159695[279] = 0;
   out_1848154903834159695[280] = 0;
   out_1848154903834159695[281] = 0;
   out_1848154903834159695[282] = 0;
   out_1848154903834159695[283] = 0;
   out_1848154903834159695[284] = 0;
   out_1848154903834159695[285] = 1;
   out_1848154903834159695[286] = 0;
   out_1848154903834159695[287] = 0;
   out_1848154903834159695[288] = 0;
   out_1848154903834159695[289] = 0;
   out_1848154903834159695[290] = 0;
   out_1848154903834159695[291] = 0;
   out_1848154903834159695[292] = 0;
   out_1848154903834159695[293] = 0;
   out_1848154903834159695[294] = 0;
   out_1848154903834159695[295] = 0;
   out_1848154903834159695[296] = 0;
   out_1848154903834159695[297] = 0;
   out_1848154903834159695[298] = 0;
   out_1848154903834159695[299] = 0;
   out_1848154903834159695[300] = 0;
   out_1848154903834159695[301] = 0;
   out_1848154903834159695[302] = 0;
   out_1848154903834159695[303] = 0;
   out_1848154903834159695[304] = 1;
   out_1848154903834159695[305] = 0;
   out_1848154903834159695[306] = 0;
   out_1848154903834159695[307] = 0;
   out_1848154903834159695[308] = 0;
   out_1848154903834159695[309] = 0;
   out_1848154903834159695[310] = 0;
   out_1848154903834159695[311] = 0;
   out_1848154903834159695[312] = 0;
   out_1848154903834159695[313] = 0;
   out_1848154903834159695[314] = 0;
   out_1848154903834159695[315] = 0;
   out_1848154903834159695[316] = 0;
   out_1848154903834159695[317] = 0;
   out_1848154903834159695[318] = 0;
   out_1848154903834159695[319] = 0;
   out_1848154903834159695[320] = 0;
   out_1848154903834159695[321] = 0;
   out_1848154903834159695[322] = 0;
   out_1848154903834159695[323] = 1;
}
void h_4(double *state, double *unused, double *out_3938051956761627657) {
   out_3938051956761627657[0] = state[6] + state[9];
   out_3938051956761627657[1] = state[7] + state[10];
   out_3938051956761627657[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_92837036171442255) {
   out_92837036171442255[0] = 0;
   out_92837036171442255[1] = 0;
   out_92837036171442255[2] = 0;
   out_92837036171442255[3] = 0;
   out_92837036171442255[4] = 0;
   out_92837036171442255[5] = 0;
   out_92837036171442255[6] = 1;
   out_92837036171442255[7] = 0;
   out_92837036171442255[8] = 0;
   out_92837036171442255[9] = 1;
   out_92837036171442255[10] = 0;
   out_92837036171442255[11] = 0;
   out_92837036171442255[12] = 0;
   out_92837036171442255[13] = 0;
   out_92837036171442255[14] = 0;
   out_92837036171442255[15] = 0;
   out_92837036171442255[16] = 0;
   out_92837036171442255[17] = 0;
   out_92837036171442255[18] = 0;
   out_92837036171442255[19] = 0;
   out_92837036171442255[20] = 0;
   out_92837036171442255[21] = 0;
   out_92837036171442255[22] = 0;
   out_92837036171442255[23] = 0;
   out_92837036171442255[24] = 0;
   out_92837036171442255[25] = 1;
   out_92837036171442255[26] = 0;
   out_92837036171442255[27] = 0;
   out_92837036171442255[28] = 1;
   out_92837036171442255[29] = 0;
   out_92837036171442255[30] = 0;
   out_92837036171442255[31] = 0;
   out_92837036171442255[32] = 0;
   out_92837036171442255[33] = 0;
   out_92837036171442255[34] = 0;
   out_92837036171442255[35] = 0;
   out_92837036171442255[36] = 0;
   out_92837036171442255[37] = 0;
   out_92837036171442255[38] = 0;
   out_92837036171442255[39] = 0;
   out_92837036171442255[40] = 0;
   out_92837036171442255[41] = 0;
   out_92837036171442255[42] = 0;
   out_92837036171442255[43] = 0;
   out_92837036171442255[44] = 1;
   out_92837036171442255[45] = 0;
   out_92837036171442255[46] = 0;
   out_92837036171442255[47] = 1;
   out_92837036171442255[48] = 0;
   out_92837036171442255[49] = 0;
   out_92837036171442255[50] = 0;
   out_92837036171442255[51] = 0;
   out_92837036171442255[52] = 0;
   out_92837036171442255[53] = 0;
}
void h_10(double *state, double *unused, double *out_1332736732351532351) {
   out_1332736732351532351[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_1332736732351532351[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_1332736732351532351[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_8776981312520129519) {
   out_8776981312520129519[0] = 0;
   out_8776981312520129519[1] = 9.8100000000000005*cos(state[1]);
   out_8776981312520129519[2] = 0;
   out_8776981312520129519[3] = 0;
   out_8776981312520129519[4] = -state[8];
   out_8776981312520129519[5] = state[7];
   out_8776981312520129519[6] = 0;
   out_8776981312520129519[7] = state[5];
   out_8776981312520129519[8] = -state[4];
   out_8776981312520129519[9] = 0;
   out_8776981312520129519[10] = 0;
   out_8776981312520129519[11] = 0;
   out_8776981312520129519[12] = 1;
   out_8776981312520129519[13] = 0;
   out_8776981312520129519[14] = 0;
   out_8776981312520129519[15] = 1;
   out_8776981312520129519[16] = 0;
   out_8776981312520129519[17] = 0;
   out_8776981312520129519[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_8776981312520129519[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_8776981312520129519[20] = 0;
   out_8776981312520129519[21] = state[8];
   out_8776981312520129519[22] = 0;
   out_8776981312520129519[23] = -state[6];
   out_8776981312520129519[24] = -state[5];
   out_8776981312520129519[25] = 0;
   out_8776981312520129519[26] = state[3];
   out_8776981312520129519[27] = 0;
   out_8776981312520129519[28] = 0;
   out_8776981312520129519[29] = 0;
   out_8776981312520129519[30] = 0;
   out_8776981312520129519[31] = 1;
   out_8776981312520129519[32] = 0;
   out_8776981312520129519[33] = 0;
   out_8776981312520129519[34] = 1;
   out_8776981312520129519[35] = 0;
   out_8776981312520129519[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_8776981312520129519[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_8776981312520129519[38] = 0;
   out_8776981312520129519[39] = -state[7];
   out_8776981312520129519[40] = state[6];
   out_8776981312520129519[41] = 0;
   out_8776981312520129519[42] = state[4];
   out_8776981312520129519[43] = -state[3];
   out_8776981312520129519[44] = 0;
   out_8776981312520129519[45] = 0;
   out_8776981312520129519[46] = 0;
   out_8776981312520129519[47] = 0;
   out_8776981312520129519[48] = 0;
   out_8776981312520129519[49] = 0;
   out_8776981312520129519[50] = 1;
   out_8776981312520129519[51] = 0;
   out_8776981312520129519[52] = 0;
   out_8776981312520129519[53] = 1;
}
void h_13(double *state, double *unused, double *out_6677041446263562296) {
   out_6677041446263562296[0] = state[3];
   out_6677041446263562296[1] = state[4];
   out_6677041446263562296[2] = state[5];
}
void H_13(double *state, double *unused, double *out_3305110861503775056) {
   out_3305110861503775056[0] = 0;
   out_3305110861503775056[1] = 0;
   out_3305110861503775056[2] = 0;
   out_3305110861503775056[3] = 1;
   out_3305110861503775056[4] = 0;
   out_3305110861503775056[5] = 0;
   out_3305110861503775056[6] = 0;
   out_3305110861503775056[7] = 0;
   out_3305110861503775056[8] = 0;
   out_3305110861503775056[9] = 0;
   out_3305110861503775056[10] = 0;
   out_3305110861503775056[11] = 0;
   out_3305110861503775056[12] = 0;
   out_3305110861503775056[13] = 0;
   out_3305110861503775056[14] = 0;
   out_3305110861503775056[15] = 0;
   out_3305110861503775056[16] = 0;
   out_3305110861503775056[17] = 0;
   out_3305110861503775056[18] = 0;
   out_3305110861503775056[19] = 0;
   out_3305110861503775056[20] = 0;
   out_3305110861503775056[21] = 0;
   out_3305110861503775056[22] = 1;
   out_3305110861503775056[23] = 0;
   out_3305110861503775056[24] = 0;
   out_3305110861503775056[25] = 0;
   out_3305110861503775056[26] = 0;
   out_3305110861503775056[27] = 0;
   out_3305110861503775056[28] = 0;
   out_3305110861503775056[29] = 0;
   out_3305110861503775056[30] = 0;
   out_3305110861503775056[31] = 0;
   out_3305110861503775056[32] = 0;
   out_3305110861503775056[33] = 0;
   out_3305110861503775056[34] = 0;
   out_3305110861503775056[35] = 0;
   out_3305110861503775056[36] = 0;
   out_3305110861503775056[37] = 0;
   out_3305110861503775056[38] = 0;
   out_3305110861503775056[39] = 0;
   out_3305110861503775056[40] = 0;
   out_3305110861503775056[41] = 1;
   out_3305110861503775056[42] = 0;
   out_3305110861503775056[43] = 0;
   out_3305110861503775056[44] = 0;
   out_3305110861503775056[45] = 0;
   out_3305110861503775056[46] = 0;
   out_3305110861503775056[47] = 0;
   out_3305110861503775056[48] = 0;
   out_3305110861503775056[49] = 0;
   out_3305110861503775056[50] = 0;
   out_3305110861503775056[51] = 0;
   out_3305110861503775056[52] = 0;
   out_3305110861503775056[53] = 0;
}
void h_14(double *state, double *unused, double *out_6699636769910654615) {
   out_6699636769910654615[0] = state[6];
   out_6699636769910654615[1] = state[7];
   out_6699636769910654615[2] = state[8];
}
void H_14(double *state, double *unused, double *out_342279490473441344) {
   out_342279490473441344[0] = 0;
   out_342279490473441344[1] = 0;
   out_342279490473441344[2] = 0;
   out_342279490473441344[3] = 0;
   out_342279490473441344[4] = 0;
   out_342279490473441344[5] = 0;
   out_342279490473441344[6] = 1;
   out_342279490473441344[7] = 0;
   out_342279490473441344[8] = 0;
   out_342279490473441344[9] = 0;
   out_342279490473441344[10] = 0;
   out_342279490473441344[11] = 0;
   out_342279490473441344[12] = 0;
   out_342279490473441344[13] = 0;
   out_342279490473441344[14] = 0;
   out_342279490473441344[15] = 0;
   out_342279490473441344[16] = 0;
   out_342279490473441344[17] = 0;
   out_342279490473441344[18] = 0;
   out_342279490473441344[19] = 0;
   out_342279490473441344[20] = 0;
   out_342279490473441344[21] = 0;
   out_342279490473441344[22] = 0;
   out_342279490473441344[23] = 0;
   out_342279490473441344[24] = 0;
   out_342279490473441344[25] = 1;
   out_342279490473441344[26] = 0;
   out_342279490473441344[27] = 0;
   out_342279490473441344[28] = 0;
   out_342279490473441344[29] = 0;
   out_342279490473441344[30] = 0;
   out_342279490473441344[31] = 0;
   out_342279490473441344[32] = 0;
   out_342279490473441344[33] = 0;
   out_342279490473441344[34] = 0;
   out_342279490473441344[35] = 0;
   out_342279490473441344[36] = 0;
   out_342279490473441344[37] = 0;
   out_342279490473441344[38] = 0;
   out_342279490473441344[39] = 0;
   out_342279490473441344[40] = 0;
   out_342279490473441344[41] = 0;
   out_342279490473441344[42] = 0;
   out_342279490473441344[43] = 0;
   out_342279490473441344[44] = 1;
   out_342279490473441344[45] = 0;
   out_342279490473441344[46] = 0;
   out_342279490473441344[47] = 0;
   out_342279490473441344[48] = 0;
   out_342279490473441344[49] = 0;
   out_342279490473441344[50] = 0;
   out_342279490473441344[51] = 0;
   out_342279490473441344[52] = 0;
   out_342279490473441344[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_5782186265648731279) {
  err_fun(nom_x, delta_x, out_5782186265648731279);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_7193052209322201941) {
  inv_err_fun(nom_x, true_x, out_7193052209322201941);
}
void pose_H_mod_fun(double *state, double *out_8077327556656833445) {
  H_mod_fun(state, out_8077327556656833445);
}
void pose_f_fun(double *state, double dt, double *out_6245206989908436510) {
  f_fun(state,  dt, out_6245206989908436510);
}
void pose_F_fun(double *state, double dt, double *out_1848154903834159695) {
  F_fun(state,  dt, out_1848154903834159695);
}
void pose_h_4(double *state, double *unused, double *out_3938051956761627657) {
  h_4(state, unused, out_3938051956761627657);
}
void pose_H_4(double *state, double *unused, double *out_92837036171442255) {
  H_4(state, unused, out_92837036171442255);
}
void pose_h_10(double *state, double *unused, double *out_1332736732351532351) {
  h_10(state, unused, out_1332736732351532351);
}
void pose_H_10(double *state, double *unused, double *out_8776981312520129519) {
  H_10(state, unused, out_8776981312520129519);
}
void pose_h_13(double *state, double *unused, double *out_6677041446263562296) {
  h_13(state, unused, out_6677041446263562296);
}
void pose_H_13(double *state, double *unused, double *out_3305110861503775056) {
  H_13(state, unused, out_3305110861503775056);
}
void pose_h_14(double *state, double *unused, double *out_6699636769910654615) {
  h_14(state, unused, out_6699636769910654615);
}
void pose_H_14(double *state, double *unused, double *out_342279490473441344) {
  H_14(state, unused, out_342279490473441344);
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
