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
void err_fun(double *nom_x, double *delta_x, double *out_1395186704351471913) {
   out_1395186704351471913[0] = delta_x[0] + nom_x[0];
   out_1395186704351471913[1] = delta_x[1] + nom_x[1];
   out_1395186704351471913[2] = delta_x[2] + nom_x[2];
   out_1395186704351471913[3] = delta_x[3] + nom_x[3];
   out_1395186704351471913[4] = delta_x[4] + nom_x[4];
   out_1395186704351471913[5] = delta_x[5] + nom_x[5];
   out_1395186704351471913[6] = delta_x[6] + nom_x[6];
   out_1395186704351471913[7] = delta_x[7] + nom_x[7];
   out_1395186704351471913[8] = delta_x[8] + nom_x[8];
   out_1395186704351471913[9] = delta_x[9] + nom_x[9];
   out_1395186704351471913[10] = delta_x[10] + nom_x[10];
   out_1395186704351471913[11] = delta_x[11] + nom_x[11];
   out_1395186704351471913[12] = delta_x[12] + nom_x[12];
   out_1395186704351471913[13] = delta_x[13] + nom_x[13];
   out_1395186704351471913[14] = delta_x[14] + nom_x[14];
   out_1395186704351471913[15] = delta_x[15] + nom_x[15];
   out_1395186704351471913[16] = delta_x[16] + nom_x[16];
   out_1395186704351471913[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_9198727305711896910) {
   out_9198727305711896910[0] = -nom_x[0] + true_x[0];
   out_9198727305711896910[1] = -nom_x[1] + true_x[1];
   out_9198727305711896910[2] = -nom_x[2] + true_x[2];
   out_9198727305711896910[3] = -nom_x[3] + true_x[3];
   out_9198727305711896910[4] = -nom_x[4] + true_x[4];
   out_9198727305711896910[5] = -nom_x[5] + true_x[5];
   out_9198727305711896910[6] = -nom_x[6] + true_x[6];
   out_9198727305711896910[7] = -nom_x[7] + true_x[7];
   out_9198727305711896910[8] = -nom_x[8] + true_x[8];
   out_9198727305711896910[9] = -nom_x[9] + true_x[9];
   out_9198727305711896910[10] = -nom_x[10] + true_x[10];
   out_9198727305711896910[11] = -nom_x[11] + true_x[11];
   out_9198727305711896910[12] = -nom_x[12] + true_x[12];
   out_9198727305711896910[13] = -nom_x[13] + true_x[13];
   out_9198727305711896910[14] = -nom_x[14] + true_x[14];
   out_9198727305711896910[15] = -nom_x[15] + true_x[15];
   out_9198727305711896910[16] = -nom_x[16] + true_x[16];
   out_9198727305711896910[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_3093613195444398718) {
   out_3093613195444398718[0] = 1.0;
   out_3093613195444398718[1] = 0.0;
   out_3093613195444398718[2] = 0.0;
   out_3093613195444398718[3] = 0.0;
   out_3093613195444398718[4] = 0.0;
   out_3093613195444398718[5] = 0.0;
   out_3093613195444398718[6] = 0.0;
   out_3093613195444398718[7] = 0.0;
   out_3093613195444398718[8] = 0.0;
   out_3093613195444398718[9] = 0.0;
   out_3093613195444398718[10] = 0.0;
   out_3093613195444398718[11] = 0.0;
   out_3093613195444398718[12] = 0.0;
   out_3093613195444398718[13] = 0.0;
   out_3093613195444398718[14] = 0.0;
   out_3093613195444398718[15] = 0.0;
   out_3093613195444398718[16] = 0.0;
   out_3093613195444398718[17] = 0.0;
   out_3093613195444398718[18] = 0.0;
   out_3093613195444398718[19] = 1.0;
   out_3093613195444398718[20] = 0.0;
   out_3093613195444398718[21] = 0.0;
   out_3093613195444398718[22] = 0.0;
   out_3093613195444398718[23] = 0.0;
   out_3093613195444398718[24] = 0.0;
   out_3093613195444398718[25] = 0.0;
   out_3093613195444398718[26] = 0.0;
   out_3093613195444398718[27] = 0.0;
   out_3093613195444398718[28] = 0.0;
   out_3093613195444398718[29] = 0.0;
   out_3093613195444398718[30] = 0.0;
   out_3093613195444398718[31] = 0.0;
   out_3093613195444398718[32] = 0.0;
   out_3093613195444398718[33] = 0.0;
   out_3093613195444398718[34] = 0.0;
   out_3093613195444398718[35] = 0.0;
   out_3093613195444398718[36] = 0.0;
   out_3093613195444398718[37] = 0.0;
   out_3093613195444398718[38] = 1.0;
   out_3093613195444398718[39] = 0.0;
   out_3093613195444398718[40] = 0.0;
   out_3093613195444398718[41] = 0.0;
   out_3093613195444398718[42] = 0.0;
   out_3093613195444398718[43] = 0.0;
   out_3093613195444398718[44] = 0.0;
   out_3093613195444398718[45] = 0.0;
   out_3093613195444398718[46] = 0.0;
   out_3093613195444398718[47] = 0.0;
   out_3093613195444398718[48] = 0.0;
   out_3093613195444398718[49] = 0.0;
   out_3093613195444398718[50] = 0.0;
   out_3093613195444398718[51] = 0.0;
   out_3093613195444398718[52] = 0.0;
   out_3093613195444398718[53] = 0.0;
   out_3093613195444398718[54] = 0.0;
   out_3093613195444398718[55] = 0.0;
   out_3093613195444398718[56] = 0.0;
   out_3093613195444398718[57] = 1.0;
   out_3093613195444398718[58] = 0.0;
   out_3093613195444398718[59] = 0.0;
   out_3093613195444398718[60] = 0.0;
   out_3093613195444398718[61] = 0.0;
   out_3093613195444398718[62] = 0.0;
   out_3093613195444398718[63] = 0.0;
   out_3093613195444398718[64] = 0.0;
   out_3093613195444398718[65] = 0.0;
   out_3093613195444398718[66] = 0.0;
   out_3093613195444398718[67] = 0.0;
   out_3093613195444398718[68] = 0.0;
   out_3093613195444398718[69] = 0.0;
   out_3093613195444398718[70] = 0.0;
   out_3093613195444398718[71] = 0.0;
   out_3093613195444398718[72] = 0.0;
   out_3093613195444398718[73] = 0.0;
   out_3093613195444398718[74] = 0.0;
   out_3093613195444398718[75] = 0.0;
   out_3093613195444398718[76] = 1.0;
   out_3093613195444398718[77] = 0.0;
   out_3093613195444398718[78] = 0.0;
   out_3093613195444398718[79] = 0.0;
   out_3093613195444398718[80] = 0.0;
   out_3093613195444398718[81] = 0.0;
   out_3093613195444398718[82] = 0.0;
   out_3093613195444398718[83] = 0.0;
   out_3093613195444398718[84] = 0.0;
   out_3093613195444398718[85] = 0.0;
   out_3093613195444398718[86] = 0.0;
   out_3093613195444398718[87] = 0.0;
   out_3093613195444398718[88] = 0.0;
   out_3093613195444398718[89] = 0.0;
   out_3093613195444398718[90] = 0.0;
   out_3093613195444398718[91] = 0.0;
   out_3093613195444398718[92] = 0.0;
   out_3093613195444398718[93] = 0.0;
   out_3093613195444398718[94] = 0.0;
   out_3093613195444398718[95] = 1.0;
   out_3093613195444398718[96] = 0.0;
   out_3093613195444398718[97] = 0.0;
   out_3093613195444398718[98] = 0.0;
   out_3093613195444398718[99] = 0.0;
   out_3093613195444398718[100] = 0.0;
   out_3093613195444398718[101] = 0.0;
   out_3093613195444398718[102] = 0.0;
   out_3093613195444398718[103] = 0.0;
   out_3093613195444398718[104] = 0.0;
   out_3093613195444398718[105] = 0.0;
   out_3093613195444398718[106] = 0.0;
   out_3093613195444398718[107] = 0.0;
   out_3093613195444398718[108] = 0.0;
   out_3093613195444398718[109] = 0.0;
   out_3093613195444398718[110] = 0.0;
   out_3093613195444398718[111] = 0.0;
   out_3093613195444398718[112] = 0.0;
   out_3093613195444398718[113] = 0.0;
   out_3093613195444398718[114] = 1.0;
   out_3093613195444398718[115] = 0.0;
   out_3093613195444398718[116] = 0.0;
   out_3093613195444398718[117] = 0.0;
   out_3093613195444398718[118] = 0.0;
   out_3093613195444398718[119] = 0.0;
   out_3093613195444398718[120] = 0.0;
   out_3093613195444398718[121] = 0.0;
   out_3093613195444398718[122] = 0.0;
   out_3093613195444398718[123] = 0.0;
   out_3093613195444398718[124] = 0.0;
   out_3093613195444398718[125] = 0.0;
   out_3093613195444398718[126] = 0.0;
   out_3093613195444398718[127] = 0.0;
   out_3093613195444398718[128] = 0.0;
   out_3093613195444398718[129] = 0.0;
   out_3093613195444398718[130] = 0.0;
   out_3093613195444398718[131] = 0.0;
   out_3093613195444398718[132] = 0.0;
   out_3093613195444398718[133] = 1.0;
   out_3093613195444398718[134] = 0.0;
   out_3093613195444398718[135] = 0.0;
   out_3093613195444398718[136] = 0.0;
   out_3093613195444398718[137] = 0.0;
   out_3093613195444398718[138] = 0.0;
   out_3093613195444398718[139] = 0.0;
   out_3093613195444398718[140] = 0.0;
   out_3093613195444398718[141] = 0.0;
   out_3093613195444398718[142] = 0.0;
   out_3093613195444398718[143] = 0.0;
   out_3093613195444398718[144] = 0.0;
   out_3093613195444398718[145] = 0.0;
   out_3093613195444398718[146] = 0.0;
   out_3093613195444398718[147] = 0.0;
   out_3093613195444398718[148] = 0.0;
   out_3093613195444398718[149] = 0.0;
   out_3093613195444398718[150] = 0.0;
   out_3093613195444398718[151] = 0.0;
   out_3093613195444398718[152] = 1.0;
   out_3093613195444398718[153] = 0.0;
   out_3093613195444398718[154] = 0.0;
   out_3093613195444398718[155] = 0.0;
   out_3093613195444398718[156] = 0.0;
   out_3093613195444398718[157] = 0.0;
   out_3093613195444398718[158] = 0.0;
   out_3093613195444398718[159] = 0.0;
   out_3093613195444398718[160] = 0.0;
   out_3093613195444398718[161] = 0.0;
   out_3093613195444398718[162] = 0.0;
   out_3093613195444398718[163] = 0.0;
   out_3093613195444398718[164] = 0.0;
   out_3093613195444398718[165] = 0.0;
   out_3093613195444398718[166] = 0.0;
   out_3093613195444398718[167] = 0.0;
   out_3093613195444398718[168] = 0.0;
   out_3093613195444398718[169] = 0.0;
   out_3093613195444398718[170] = 0.0;
   out_3093613195444398718[171] = 1.0;
   out_3093613195444398718[172] = 0.0;
   out_3093613195444398718[173] = 0.0;
   out_3093613195444398718[174] = 0.0;
   out_3093613195444398718[175] = 0.0;
   out_3093613195444398718[176] = 0.0;
   out_3093613195444398718[177] = 0.0;
   out_3093613195444398718[178] = 0.0;
   out_3093613195444398718[179] = 0.0;
   out_3093613195444398718[180] = 0.0;
   out_3093613195444398718[181] = 0.0;
   out_3093613195444398718[182] = 0.0;
   out_3093613195444398718[183] = 0.0;
   out_3093613195444398718[184] = 0.0;
   out_3093613195444398718[185] = 0.0;
   out_3093613195444398718[186] = 0.0;
   out_3093613195444398718[187] = 0.0;
   out_3093613195444398718[188] = 0.0;
   out_3093613195444398718[189] = 0.0;
   out_3093613195444398718[190] = 1.0;
   out_3093613195444398718[191] = 0.0;
   out_3093613195444398718[192] = 0.0;
   out_3093613195444398718[193] = 0.0;
   out_3093613195444398718[194] = 0.0;
   out_3093613195444398718[195] = 0.0;
   out_3093613195444398718[196] = 0.0;
   out_3093613195444398718[197] = 0.0;
   out_3093613195444398718[198] = 0.0;
   out_3093613195444398718[199] = 0.0;
   out_3093613195444398718[200] = 0.0;
   out_3093613195444398718[201] = 0.0;
   out_3093613195444398718[202] = 0.0;
   out_3093613195444398718[203] = 0.0;
   out_3093613195444398718[204] = 0.0;
   out_3093613195444398718[205] = 0.0;
   out_3093613195444398718[206] = 0.0;
   out_3093613195444398718[207] = 0.0;
   out_3093613195444398718[208] = 0.0;
   out_3093613195444398718[209] = 1.0;
   out_3093613195444398718[210] = 0.0;
   out_3093613195444398718[211] = 0.0;
   out_3093613195444398718[212] = 0.0;
   out_3093613195444398718[213] = 0.0;
   out_3093613195444398718[214] = 0.0;
   out_3093613195444398718[215] = 0.0;
   out_3093613195444398718[216] = 0.0;
   out_3093613195444398718[217] = 0.0;
   out_3093613195444398718[218] = 0.0;
   out_3093613195444398718[219] = 0.0;
   out_3093613195444398718[220] = 0.0;
   out_3093613195444398718[221] = 0.0;
   out_3093613195444398718[222] = 0.0;
   out_3093613195444398718[223] = 0.0;
   out_3093613195444398718[224] = 0.0;
   out_3093613195444398718[225] = 0.0;
   out_3093613195444398718[226] = 0.0;
   out_3093613195444398718[227] = 0.0;
   out_3093613195444398718[228] = 1.0;
   out_3093613195444398718[229] = 0.0;
   out_3093613195444398718[230] = 0.0;
   out_3093613195444398718[231] = 0.0;
   out_3093613195444398718[232] = 0.0;
   out_3093613195444398718[233] = 0.0;
   out_3093613195444398718[234] = 0.0;
   out_3093613195444398718[235] = 0.0;
   out_3093613195444398718[236] = 0.0;
   out_3093613195444398718[237] = 0.0;
   out_3093613195444398718[238] = 0.0;
   out_3093613195444398718[239] = 0.0;
   out_3093613195444398718[240] = 0.0;
   out_3093613195444398718[241] = 0.0;
   out_3093613195444398718[242] = 0.0;
   out_3093613195444398718[243] = 0.0;
   out_3093613195444398718[244] = 0.0;
   out_3093613195444398718[245] = 0.0;
   out_3093613195444398718[246] = 0.0;
   out_3093613195444398718[247] = 1.0;
   out_3093613195444398718[248] = 0.0;
   out_3093613195444398718[249] = 0.0;
   out_3093613195444398718[250] = 0.0;
   out_3093613195444398718[251] = 0.0;
   out_3093613195444398718[252] = 0.0;
   out_3093613195444398718[253] = 0.0;
   out_3093613195444398718[254] = 0.0;
   out_3093613195444398718[255] = 0.0;
   out_3093613195444398718[256] = 0.0;
   out_3093613195444398718[257] = 0.0;
   out_3093613195444398718[258] = 0.0;
   out_3093613195444398718[259] = 0.0;
   out_3093613195444398718[260] = 0.0;
   out_3093613195444398718[261] = 0.0;
   out_3093613195444398718[262] = 0.0;
   out_3093613195444398718[263] = 0.0;
   out_3093613195444398718[264] = 0.0;
   out_3093613195444398718[265] = 0.0;
   out_3093613195444398718[266] = 1.0;
   out_3093613195444398718[267] = 0.0;
   out_3093613195444398718[268] = 0.0;
   out_3093613195444398718[269] = 0.0;
   out_3093613195444398718[270] = 0.0;
   out_3093613195444398718[271] = 0.0;
   out_3093613195444398718[272] = 0.0;
   out_3093613195444398718[273] = 0.0;
   out_3093613195444398718[274] = 0.0;
   out_3093613195444398718[275] = 0.0;
   out_3093613195444398718[276] = 0.0;
   out_3093613195444398718[277] = 0.0;
   out_3093613195444398718[278] = 0.0;
   out_3093613195444398718[279] = 0.0;
   out_3093613195444398718[280] = 0.0;
   out_3093613195444398718[281] = 0.0;
   out_3093613195444398718[282] = 0.0;
   out_3093613195444398718[283] = 0.0;
   out_3093613195444398718[284] = 0.0;
   out_3093613195444398718[285] = 1.0;
   out_3093613195444398718[286] = 0.0;
   out_3093613195444398718[287] = 0.0;
   out_3093613195444398718[288] = 0.0;
   out_3093613195444398718[289] = 0.0;
   out_3093613195444398718[290] = 0.0;
   out_3093613195444398718[291] = 0.0;
   out_3093613195444398718[292] = 0.0;
   out_3093613195444398718[293] = 0.0;
   out_3093613195444398718[294] = 0.0;
   out_3093613195444398718[295] = 0.0;
   out_3093613195444398718[296] = 0.0;
   out_3093613195444398718[297] = 0.0;
   out_3093613195444398718[298] = 0.0;
   out_3093613195444398718[299] = 0.0;
   out_3093613195444398718[300] = 0.0;
   out_3093613195444398718[301] = 0.0;
   out_3093613195444398718[302] = 0.0;
   out_3093613195444398718[303] = 0.0;
   out_3093613195444398718[304] = 1.0;
   out_3093613195444398718[305] = 0.0;
   out_3093613195444398718[306] = 0.0;
   out_3093613195444398718[307] = 0.0;
   out_3093613195444398718[308] = 0.0;
   out_3093613195444398718[309] = 0.0;
   out_3093613195444398718[310] = 0.0;
   out_3093613195444398718[311] = 0.0;
   out_3093613195444398718[312] = 0.0;
   out_3093613195444398718[313] = 0.0;
   out_3093613195444398718[314] = 0.0;
   out_3093613195444398718[315] = 0.0;
   out_3093613195444398718[316] = 0.0;
   out_3093613195444398718[317] = 0.0;
   out_3093613195444398718[318] = 0.0;
   out_3093613195444398718[319] = 0.0;
   out_3093613195444398718[320] = 0.0;
   out_3093613195444398718[321] = 0.0;
   out_3093613195444398718[322] = 0.0;
   out_3093613195444398718[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_1996627188251084581) {
   out_1996627188251084581[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_1996627188251084581[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_1996627188251084581[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_1996627188251084581[3] = dt*state[12] + state[3];
   out_1996627188251084581[4] = dt*state[13] + state[4];
   out_1996627188251084581[5] = dt*state[14] + state[5];
   out_1996627188251084581[6] = state[6];
   out_1996627188251084581[7] = state[7];
   out_1996627188251084581[8] = state[8];
   out_1996627188251084581[9] = state[9];
   out_1996627188251084581[10] = state[10];
   out_1996627188251084581[11] = state[11];
   out_1996627188251084581[12] = state[12];
   out_1996627188251084581[13] = state[13];
   out_1996627188251084581[14] = state[14];
   out_1996627188251084581[15] = state[15];
   out_1996627188251084581[16] = state[16];
   out_1996627188251084581[17] = state[17];
}
void F_fun(double *state, double dt, double *out_7555202558844146792) {
   out_7555202558844146792[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7555202558844146792[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7555202558844146792[2] = 0;
   out_7555202558844146792[3] = 0;
   out_7555202558844146792[4] = 0;
   out_7555202558844146792[5] = 0;
   out_7555202558844146792[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7555202558844146792[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7555202558844146792[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7555202558844146792[9] = 0;
   out_7555202558844146792[10] = 0;
   out_7555202558844146792[11] = 0;
   out_7555202558844146792[12] = 0;
   out_7555202558844146792[13] = 0;
   out_7555202558844146792[14] = 0;
   out_7555202558844146792[15] = 0;
   out_7555202558844146792[16] = 0;
   out_7555202558844146792[17] = 0;
   out_7555202558844146792[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7555202558844146792[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7555202558844146792[20] = 0;
   out_7555202558844146792[21] = 0;
   out_7555202558844146792[22] = 0;
   out_7555202558844146792[23] = 0;
   out_7555202558844146792[24] = 0;
   out_7555202558844146792[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7555202558844146792[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7555202558844146792[27] = 0;
   out_7555202558844146792[28] = 0;
   out_7555202558844146792[29] = 0;
   out_7555202558844146792[30] = 0;
   out_7555202558844146792[31] = 0;
   out_7555202558844146792[32] = 0;
   out_7555202558844146792[33] = 0;
   out_7555202558844146792[34] = 0;
   out_7555202558844146792[35] = 0;
   out_7555202558844146792[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7555202558844146792[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7555202558844146792[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7555202558844146792[39] = 0;
   out_7555202558844146792[40] = 0;
   out_7555202558844146792[41] = 0;
   out_7555202558844146792[42] = 0;
   out_7555202558844146792[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7555202558844146792[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7555202558844146792[45] = 0;
   out_7555202558844146792[46] = 0;
   out_7555202558844146792[47] = 0;
   out_7555202558844146792[48] = 0;
   out_7555202558844146792[49] = 0;
   out_7555202558844146792[50] = 0;
   out_7555202558844146792[51] = 0;
   out_7555202558844146792[52] = 0;
   out_7555202558844146792[53] = 0;
   out_7555202558844146792[54] = 0;
   out_7555202558844146792[55] = 0;
   out_7555202558844146792[56] = 0;
   out_7555202558844146792[57] = 1;
   out_7555202558844146792[58] = 0;
   out_7555202558844146792[59] = 0;
   out_7555202558844146792[60] = 0;
   out_7555202558844146792[61] = 0;
   out_7555202558844146792[62] = 0;
   out_7555202558844146792[63] = 0;
   out_7555202558844146792[64] = 0;
   out_7555202558844146792[65] = 0;
   out_7555202558844146792[66] = dt;
   out_7555202558844146792[67] = 0;
   out_7555202558844146792[68] = 0;
   out_7555202558844146792[69] = 0;
   out_7555202558844146792[70] = 0;
   out_7555202558844146792[71] = 0;
   out_7555202558844146792[72] = 0;
   out_7555202558844146792[73] = 0;
   out_7555202558844146792[74] = 0;
   out_7555202558844146792[75] = 0;
   out_7555202558844146792[76] = 1;
   out_7555202558844146792[77] = 0;
   out_7555202558844146792[78] = 0;
   out_7555202558844146792[79] = 0;
   out_7555202558844146792[80] = 0;
   out_7555202558844146792[81] = 0;
   out_7555202558844146792[82] = 0;
   out_7555202558844146792[83] = 0;
   out_7555202558844146792[84] = 0;
   out_7555202558844146792[85] = dt;
   out_7555202558844146792[86] = 0;
   out_7555202558844146792[87] = 0;
   out_7555202558844146792[88] = 0;
   out_7555202558844146792[89] = 0;
   out_7555202558844146792[90] = 0;
   out_7555202558844146792[91] = 0;
   out_7555202558844146792[92] = 0;
   out_7555202558844146792[93] = 0;
   out_7555202558844146792[94] = 0;
   out_7555202558844146792[95] = 1;
   out_7555202558844146792[96] = 0;
   out_7555202558844146792[97] = 0;
   out_7555202558844146792[98] = 0;
   out_7555202558844146792[99] = 0;
   out_7555202558844146792[100] = 0;
   out_7555202558844146792[101] = 0;
   out_7555202558844146792[102] = 0;
   out_7555202558844146792[103] = 0;
   out_7555202558844146792[104] = dt;
   out_7555202558844146792[105] = 0;
   out_7555202558844146792[106] = 0;
   out_7555202558844146792[107] = 0;
   out_7555202558844146792[108] = 0;
   out_7555202558844146792[109] = 0;
   out_7555202558844146792[110] = 0;
   out_7555202558844146792[111] = 0;
   out_7555202558844146792[112] = 0;
   out_7555202558844146792[113] = 0;
   out_7555202558844146792[114] = 1;
   out_7555202558844146792[115] = 0;
   out_7555202558844146792[116] = 0;
   out_7555202558844146792[117] = 0;
   out_7555202558844146792[118] = 0;
   out_7555202558844146792[119] = 0;
   out_7555202558844146792[120] = 0;
   out_7555202558844146792[121] = 0;
   out_7555202558844146792[122] = 0;
   out_7555202558844146792[123] = 0;
   out_7555202558844146792[124] = 0;
   out_7555202558844146792[125] = 0;
   out_7555202558844146792[126] = 0;
   out_7555202558844146792[127] = 0;
   out_7555202558844146792[128] = 0;
   out_7555202558844146792[129] = 0;
   out_7555202558844146792[130] = 0;
   out_7555202558844146792[131] = 0;
   out_7555202558844146792[132] = 0;
   out_7555202558844146792[133] = 1;
   out_7555202558844146792[134] = 0;
   out_7555202558844146792[135] = 0;
   out_7555202558844146792[136] = 0;
   out_7555202558844146792[137] = 0;
   out_7555202558844146792[138] = 0;
   out_7555202558844146792[139] = 0;
   out_7555202558844146792[140] = 0;
   out_7555202558844146792[141] = 0;
   out_7555202558844146792[142] = 0;
   out_7555202558844146792[143] = 0;
   out_7555202558844146792[144] = 0;
   out_7555202558844146792[145] = 0;
   out_7555202558844146792[146] = 0;
   out_7555202558844146792[147] = 0;
   out_7555202558844146792[148] = 0;
   out_7555202558844146792[149] = 0;
   out_7555202558844146792[150] = 0;
   out_7555202558844146792[151] = 0;
   out_7555202558844146792[152] = 1;
   out_7555202558844146792[153] = 0;
   out_7555202558844146792[154] = 0;
   out_7555202558844146792[155] = 0;
   out_7555202558844146792[156] = 0;
   out_7555202558844146792[157] = 0;
   out_7555202558844146792[158] = 0;
   out_7555202558844146792[159] = 0;
   out_7555202558844146792[160] = 0;
   out_7555202558844146792[161] = 0;
   out_7555202558844146792[162] = 0;
   out_7555202558844146792[163] = 0;
   out_7555202558844146792[164] = 0;
   out_7555202558844146792[165] = 0;
   out_7555202558844146792[166] = 0;
   out_7555202558844146792[167] = 0;
   out_7555202558844146792[168] = 0;
   out_7555202558844146792[169] = 0;
   out_7555202558844146792[170] = 0;
   out_7555202558844146792[171] = 1;
   out_7555202558844146792[172] = 0;
   out_7555202558844146792[173] = 0;
   out_7555202558844146792[174] = 0;
   out_7555202558844146792[175] = 0;
   out_7555202558844146792[176] = 0;
   out_7555202558844146792[177] = 0;
   out_7555202558844146792[178] = 0;
   out_7555202558844146792[179] = 0;
   out_7555202558844146792[180] = 0;
   out_7555202558844146792[181] = 0;
   out_7555202558844146792[182] = 0;
   out_7555202558844146792[183] = 0;
   out_7555202558844146792[184] = 0;
   out_7555202558844146792[185] = 0;
   out_7555202558844146792[186] = 0;
   out_7555202558844146792[187] = 0;
   out_7555202558844146792[188] = 0;
   out_7555202558844146792[189] = 0;
   out_7555202558844146792[190] = 1;
   out_7555202558844146792[191] = 0;
   out_7555202558844146792[192] = 0;
   out_7555202558844146792[193] = 0;
   out_7555202558844146792[194] = 0;
   out_7555202558844146792[195] = 0;
   out_7555202558844146792[196] = 0;
   out_7555202558844146792[197] = 0;
   out_7555202558844146792[198] = 0;
   out_7555202558844146792[199] = 0;
   out_7555202558844146792[200] = 0;
   out_7555202558844146792[201] = 0;
   out_7555202558844146792[202] = 0;
   out_7555202558844146792[203] = 0;
   out_7555202558844146792[204] = 0;
   out_7555202558844146792[205] = 0;
   out_7555202558844146792[206] = 0;
   out_7555202558844146792[207] = 0;
   out_7555202558844146792[208] = 0;
   out_7555202558844146792[209] = 1;
   out_7555202558844146792[210] = 0;
   out_7555202558844146792[211] = 0;
   out_7555202558844146792[212] = 0;
   out_7555202558844146792[213] = 0;
   out_7555202558844146792[214] = 0;
   out_7555202558844146792[215] = 0;
   out_7555202558844146792[216] = 0;
   out_7555202558844146792[217] = 0;
   out_7555202558844146792[218] = 0;
   out_7555202558844146792[219] = 0;
   out_7555202558844146792[220] = 0;
   out_7555202558844146792[221] = 0;
   out_7555202558844146792[222] = 0;
   out_7555202558844146792[223] = 0;
   out_7555202558844146792[224] = 0;
   out_7555202558844146792[225] = 0;
   out_7555202558844146792[226] = 0;
   out_7555202558844146792[227] = 0;
   out_7555202558844146792[228] = 1;
   out_7555202558844146792[229] = 0;
   out_7555202558844146792[230] = 0;
   out_7555202558844146792[231] = 0;
   out_7555202558844146792[232] = 0;
   out_7555202558844146792[233] = 0;
   out_7555202558844146792[234] = 0;
   out_7555202558844146792[235] = 0;
   out_7555202558844146792[236] = 0;
   out_7555202558844146792[237] = 0;
   out_7555202558844146792[238] = 0;
   out_7555202558844146792[239] = 0;
   out_7555202558844146792[240] = 0;
   out_7555202558844146792[241] = 0;
   out_7555202558844146792[242] = 0;
   out_7555202558844146792[243] = 0;
   out_7555202558844146792[244] = 0;
   out_7555202558844146792[245] = 0;
   out_7555202558844146792[246] = 0;
   out_7555202558844146792[247] = 1;
   out_7555202558844146792[248] = 0;
   out_7555202558844146792[249] = 0;
   out_7555202558844146792[250] = 0;
   out_7555202558844146792[251] = 0;
   out_7555202558844146792[252] = 0;
   out_7555202558844146792[253] = 0;
   out_7555202558844146792[254] = 0;
   out_7555202558844146792[255] = 0;
   out_7555202558844146792[256] = 0;
   out_7555202558844146792[257] = 0;
   out_7555202558844146792[258] = 0;
   out_7555202558844146792[259] = 0;
   out_7555202558844146792[260] = 0;
   out_7555202558844146792[261] = 0;
   out_7555202558844146792[262] = 0;
   out_7555202558844146792[263] = 0;
   out_7555202558844146792[264] = 0;
   out_7555202558844146792[265] = 0;
   out_7555202558844146792[266] = 1;
   out_7555202558844146792[267] = 0;
   out_7555202558844146792[268] = 0;
   out_7555202558844146792[269] = 0;
   out_7555202558844146792[270] = 0;
   out_7555202558844146792[271] = 0;
   out_7555202558844146792[272] = 0;
   out_7555202558844146792[273] = 0;
   out_7555202558844146792[274] = 0;
   out_7555202558844146792[275] = 0;
   out_7555202558844146792[276] = 0;
   out_7555202558844146792[277] = 0;
   out_7555202558844146792[278] = 0;
   out_7555202558844146792[279] = 0;
   out_7555202558844146792[280] = 0;
   out_7555202558844146792[281] = 0;
   out_7555202558844146792[282] = 0;
   out_7555202558844146792[283] = 0;
   out_7555202558844146792[284] = 0;
   out_7555202558844146792[285] = 1;
   out_7555202558844146792[286] = 0;
   out_7555202558844146792[287] = 0;
   out_7555202558844146792[288] = 0;
   out_7555202558844146792[289] = 0;
   out_7555202558844146792[290] = 0;
   out_7555202558844146792[291] = 0;
   out_7555202558844146792[292] = 0;
   out_7555202558844146792[293] = 0;
   out_7555202558844146792[294] = 0;
   out_7555202558844146792[295] = 0;
   out_7555202558844146792[296] = 0;
   out_7555202558844146792[297] = 0;
   out_7555202558844146792[298] = 0;
   out_7555202558844146792[299] = 0;
   out_7555202558844146792[300] = 0;
   out_7555202558844146792[301] = 0;
   out_7555202558844146792[302] = 0;
   out_7555202558844146792[303] = 0;
   out_7555202558844146792[304] = 1;
   out_7555202558844146792[305] = 0;
   out_7555202558844146792[306] = 0;
   out_7555202558844146792[307] = 0;
   out_7555202558844146792[308] = 0;
   out_7555202558844146792[309] = 0;
   out_7555202558844146792[310] = 0;
   out_7555202558844146792[311] = 0;
   out_7555202558844146792[312] = 0;
   out_7555202558844146792[313] = 0;
   out_7555202558844146792[314] = 0;
   out_7555202558844146792[315] = 0;
   out_7555202558844146792[316] = 0;
   out_7555202558844146792[317] = 0;
   out_7555202558844146792[318] = 0;
   out_7555202558844146792[319] = 0;
   out_7555202558844146792[320] = 0;
   out_7555202558844146792[321] = 0;
   out_7555202558844146792[322] = 0;
   out_7555202558844146792[323] = 1;
}
void h_4(double *state, double *unused, double *out_5476937082898018351) {
   out_5476937082898018351[0] = state[6] + state[9];
   out_5476937082898018351[1] = state[7] + state[10];
   out_5476937082898018351[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_6294023096545868742) {
   out_6294023096545868742[0] = 0;
   out_6294023096545868742[1] = 0;
   out_6294023096545868742[2] = 0;
   out_6294023096545868742[3] = 0;
   out_6294023096545868742[4] = 0;
   out_6294023096545868742[5] = 0;
   out_6294023096545868742[6] = 1;
   out_6294023096545868742[7] = 0;
   out_6294023096545868742[8] = 0;
   out_6294023096545868742[9] = 1;
   out_6294023096545868742[10] = 0;
   out_6294023096545868742[11] = 0;
   out_6294023096545868742[12] = 0;
   out_6294023096545868742[13] = 0;
   out_6294023096545868742[14] = 0;
   out_6294023096545868742[15] = 0;
   out_6294023096545868742[16] = 0;
   out_6294023096545868742[17] = 0;
   out_6294023096545868742[18] = 0;
   out_6294023096545868742[19] = 0;
   out_6294023096545868742[20] = 0;
   out_6294023096545868742[21] = 0;
   out_6294023096545868742[22] = 0;
   out_6294023096545868742[23] = 0;
   out_6294023096545868742[24] = 0;
   out_6294023096545868742[25] = 1;
   out_6294023096545868742[26] = 0;
   out_6294023096545868742[27] = 0;
   out_6294023096545868742[28] = 1;
   out_6294023096545868742[29] = 0;
   out_6294023096545868742[30] = 0;
   out_6294023096545868742[31] = 0;
   out_6294023096545868742[32] = 0;
   out_6294023096545868742[33] = 0;
   out_6294023096545868742[34] = 0;
   out_6294023096545868742[35] = 0;
   out_6294023096545868742[36] = 0;
   out_6294023096545868742[37] = 0;
   out_6294023096545868742[38] = 0;
   out_6294023096545868742[39] = 0;
   out_6294023096545868742[40] = 0;
   out_6294023096545868742[41] = 0;
   out_6294023096545868742[42] = 0;
   out_6294023096545868742[43] = 0;
   out_6294023096545868742[44] = 1;
   out_6294023096545868742[45] = 0;
   out_6294023096545868742[46] = 0;
   out_6294023096545868742[47] = 1;
   out_6294023096545868742[48] = 0;
   out_6294023096545868742[49] = 0;
   out_6294023096545868742[50] = 0;
   out_6294023096545868742[51] = 0;
   out_6294023096545868742[52] = 0;
   out_6294023096545868742[53] = 0;
}
void h_10(double *state, double *unused, double *out_6657021705980566751) {
   out_6657021705980566751[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_6657021705980566751[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_6657021705980566751[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_6597046473621448693) {
   out_6597046473621448693[0] = 0;
   out_6597046473621448693[1] = 9.8100000000000005*cos(state[1]);
   out_6597046473621448693[2] = 0;
   out_6597046473621448693[3] = 0;
   out_6597046473621448693[4] = -state[8];
   out_6597046473621448693[5] = state[7];
   out_6597046473621448693[6] = 0;
   out_6597046473621448693[7] = state[5];
   out_6597046473621448693[8] = -state[4];
   out_6597046473621448693[9] = 0;
   out_6597046473621448693[10] = 0;
   out_6597046473621448693[11] = 0;
   out_6597046473621448693[12] = 1;
   out_6597046473621448693[13] = 0;
   out_6597046473621448693[14] = 0;
   out_6597046473621448693[15] = 1;
   out_6597046473621448693[16] = 0;
   out_6597046473621448693[17] = 0;
   out_6597046473621448693[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_6597046473621448693[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_6597046473621448693[20] = 0;
   out_6597046473621448693[21] = state[8];
   out_6597046473621448693[22] = 0;
   out_6597046473621448693[23] = -state[6];
   out_6597046473621448693[24] = -state[5];
   out_6597046473621448693[25] = 0;
   out_6597046473621448693[26] = state[3];
   out_6597046473621448693[27] = 0;
   out_6597046473621448693[28] = 0;
   out_6597046473621448693[29] = 0;
   out_6597046473621448693[30] = 0;
   out_6597046473621448693[31] = 1;
   out_6597046473621448693[32] = 0;
   out_6597046473621448693[33] = 0;
   out_6597046473621448693[34] = 1;
   out_6597046473621448693[35] = 0;
   out_6597046473621448693[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_6597046473621448693[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_6597046473621448693[38] = 0;
   out_6597046473621448693[39] = -state[7];
   out_6597046473621448693[40] = state[6];
   out_6597046473621448693[41] = 0;
   out_6597046473621448693[42] = state[4];
   out_6597046473621448693[43] = -state[3];
   out_6597046473621448693[44] = 0;
   out_6597046473621448693[45] = 0;
   out_6597046473621448693[46] = 0;
   out_6597046473621448693[47] = 0;
   out_6597046473621448693[48] = 0;
   out_6597046473621448693[49] = 0;
   out_6597046473621448693[50] = 1;
   out_6597046473621448693[51] = 0;
   out_6597046473621448693[52] = 0;
   out_6597046473621448693[53] = 1;
}
void h_13(double *state, double *unused, double *out_6585329472009713103) {
   out_6585329472009713103[0] = state[3];
   out_6585329472009713103[1] = state[4];
   out_6585329472009713103[2] = state[5];
}
void H_13(double *state, double *unused, double *out_5729421176864024638) {
   out_5729421176864024638[0] = 0;
   out_5729421176864024638[1] = 0;
   out_5729421176864024638[2] = 0;
   out_5729421176864024638[3] = 1;
   out_5729421176864024638[4] = 0;
   out_5729421176864024638[5] = 0;
   out_5729421176864024638[6] = 0;
   out_5729421176864024638[7] = 0;
   out_5729421176864024638[8] = 0;
   out_5729421176864024638[9] = 0;
   out_5729421176864024638[10] = 0;
   out_5729421176864024638[11] = 0;
   out_5729421176864024638[12] = 0;
   out_5729421176864024638[13] = 0;
   out_5729421176864024638[14] = 0;
   out_5729421176864024638[15] = 0;
   out_5729421176864024638[16] = 0;
   out_5729421176864024638[17] = 0;
   out_5729421176864024638[18] = 0;
   out_5729421176864024638[19] = 0;
   out_5729421176864024638[20] = 0;
   out_5729421176864024638[21] = 0;
   out_5729421176864024638[22] = 1;
   out_5729421176864024638[23] = 0;
   out_5729421176864024638[24] = 0;
   out_5729421176864024638[25] = 0;
   out_5729421176864024638[26] = 0;
   out_5729421176864024638[27] = 0;
   out_5729421176864024638[28] = 0;
   out_5729421176864024638[29] = 0;
   out_5729421176864024638[30] = 0;
   out_5729421176864024638[31] = 0;
   out_5729421176864024638[32] = 0;
   out_5729421176864024638[33] = 0;
   out_5729421176864024638[34] = 0;
   out_5729421176864024638[35] = 0;
   out_5729421176864024638[36] = 0;
   out_5729421176864024638[37] = 0;
   out_5729421176864024638[38] = 0;
   out_5729421176864024638[39] = 0;
   out_5729421176864024638[40] = 0;
   out_5729421176864024638[41] = 1;
   out_5729421176864024638[42] = 0;
   out_5729421176864024638[43] = 0;
   out_5729421176864024638[44] = 0;
   out_5729421176864024638[45] = 0;
   out_5729421176864024638[46] = 0;
   out_5729421176864024638[47] = 0;
   out_5729421176864024638[48] = 0;
   out_5729421176864024638[49] = 0;
   out_5729421176864024638[50] = 0;
   out_5729421176864024638[51] = 0;
   out_5729421176864024638[52] = 0;
   out_5729421176864024638[53] = 0;
}
void h_14(double *state, double *unused, double *out_8914797937571097614) {
   out_8914797937571097614[0] = state[6];
   out_8914797937571097614[1] = state[7];
   out_8914797937571097614[2] = state[8];
}
void H_14(double *state, double *unused, double *out_9069932544868310578) {
   out_9069932544868310578[0] = 0;
   out_9069932544868310578[1] = 0;
   out_9069932544868310578[2] = 0;
   out_9069932544868310578[3] = 0;
   out_9069932544868310578[4] = 0;
   out_9069932544868310578[5] = 0;
   out_9069932544868310578[6] = 1;
   out_9069932544868310578[7] = 0;
   out_9069932544868310578[8] = 0;
   out_9069932544868310578[9] = 0;
   out_9069932544868310578[10] = 0;
   out_9069932544868310578[11] = 0;
   out_9069932544868310578[12] = 0;
   out_9069932544868310578[13] = 0;
   out_9069932544868310578[14] = 0;
   out_9069932544868310578[15] = 0;
   out_9069932544868310578[16] = 0;
   out_9069932544868310578[17] = 0;
   out_9069932544868310578[18] = 0;
   out_9069932544868310578[19] = 0;
   out_9069932544868310578[20] = 0;
   out_9069932544868310578[21] = 0;
   out_9069932544868310578[22] = 0;
   out_9069932544868310578[23] = 0;
   out_9069932544868310578[24] = 0;
   out_9069932544868310578[25] = 1;
   out_9069932544868310578[26] = 0;
   out_9069932544868310578[27] = 0;
   out_9069932544868310578[28] = 0;
   out_9069932544868310578[29] = 0;
   out_9069932544868310578[30] = 0;
   out_9069932544868310578[31] = 0;
   out_9069932544868310578[32] = 0;
   out_9069932544868310578[33] = 0;
   out_9069932544868310578[34] = 0;
   out_9069932544868310578[35] = 0;
   out_9069932544868310578[36] = 0;
   out_9069932544868310578[37] = 0;
   out_9069932544868310578[38] = 0;
   out_9069932544868310578[39] = 0;
   out_9069932544868310578[40] = 0;
   out_9069932544868310578[41] = 0;
   out_9069932544868310578[42] = 0;
   out_9069932544868310578[43] = 0;
   out_9069932544868310578[44] = 1;
   out_9069932544868310578[45] = 0;
   out_9069932544868310578[46] = 0;
   out_9069932544868310578[47] = 0;
   out_9069932544868310578[48] = 0;
   out_9069932544868310578[49] = 0;
   out_9069932544868310578[50] = 0;
   out_9069932544868310578[51] = 0;
   out_9069932544868310578[52] = 0;
   out_9069932544868310578[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_1395186704351471913) {
  err_fun(nom_x, delta_x, out_1395186704351471913);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_9198727305711896910) {
  inv_err_fun(nom_x, true_x, out_9198727305711896910);
}
void pose_H_mod_fun(double *state, double *out_3093613195444398718) {
  H_mod_fun(state, out_3093613195444398718);
}
void pose_f_fun(double *state, double dt, double *out_1996627188251084581) {
  f_fun(state,  dt, out_1996627188251084581);
}
void pose_F_fun(double *state, double dt, double *out_7555202558844146792) {
  F_fun(state,  dt, out_7555202558844146792);
}
void pose_h_4(double *state, double *unused, double *out_5476937082898018351) {
  h_4(state, unused, out_5476937082898018351);
}
void pose_H_4(double *state, double *unused, double *out_6294023096545868742) {
  H_4(state, unused, out_6294023096545868742);
}
void pose_h_10(double *state, double *unused, double *out_6657021705980566751) {
  h_10(state, unused, out_6657021705980566751);
}
void pose_H_10(double *state, double *unused, double *out_6597046473621448693) {
  H_10(state, unused, out_6597046473621448693);
}
void pose_h_13(double *state, double *unused, double *out_6585329472009713103) {
  h_13(state, unused, out_6585329472009713103);
}
void pose_H_13(double *state, double *unused, double *out_5729421176864024638) {
  H_13(state, unused, out_5729421176864024638);
}
void pose_h_14(double *state, double *unused, double *out_8914797937571097614) {
  h_14(state, unused, out_8914797937571097614);
}
void pose_H_14(double *state, double *unused, double *out_9069932544868310578) {
  H_14(state, unused, out_9069932544868310578);
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
