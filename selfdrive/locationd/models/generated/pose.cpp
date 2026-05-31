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
void err_fun(double *nom_x, double *delta_x, double *out_5792096138533243612) {
   out_5792096138533243612[0] = delta_x[0] + nom_x[0];
   out_5792096138533243612[1] = delta_x[1] + nom_x[1];
   out_5792096138533243612[2] = delta_x[2] + nom_x[2];
   out_5792096138533243612[3] = delta_x[3] + nom_x[3];
   out_5792096138533243612[4] = delta_x[4] + nom_x[4];
   out_5792096138533243612[5] = delta_x[5] + nom_x[5];
   out_5792096138533243612[6] = delta_x[6] + nom_x[6];
   out_5792096138533243612[7] = delta_x[7] + nom_x[7];
   out_5792096138533243612[8] = delta_x[8] + nom_x[8];
   out_5792096138533243612[9] = delta_x[9] + nom_x[9];
   out_5792096138533243612[10] = delta_x[10] + nom_x[10];
   out_5792096138533243612[11] = delta_x[11] + nom_x[11];
   out_5792096138533243612[12] = delta_x[12] + nom_x[12];
   out_5792096138533243612[13] = delta_x[13] + nom_x[13];
   out_5792096138533243612[14] = delta_x[14] + nom_x[14];
   out_5792096138533243612[15] = delta_x[15] + nom_x[15];
   out_5792096138533243612[16] = delta_x[16] + nom_x[16];
   out_5792096138533243612[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7145879757653058560) {
   out_7145879757653058560[0] = -nom_x[0] + true_x[0];
   out_7145879757653058560[1] = -nom_x[1] + true_x[1];
   out_7145879757653058560[2] = -nom_x[2] + true_x[2];
   out_7145879757653058560[3] = -nom_x[3] + true_x[3];
   out_7145879757653058560[4] = -nom_x[4] + true_x[4];
   out_7145879757653058560[5] = -nom_x[5] + true_x[5];
   out_7145879757653058560[6] = -nom_x[6] + true_x[6];
   out_7145879757653058560[7] = -nom_x[7] + true_x[7];
   out_7145879757653058560[8] = -nom_x[8] + true_x[8];
   out_7145879757653058560[9] = -nom_x[9] + true_x[9];
   out_7145879757653058560[10] = -nom_x[10] + true_x[10];
   out_7145879757653058560[11] = -nom_x[11] + true_x[11];
   out_7145879757653058560[12] = -nom_x[12] + true_x[12];
   out_7145879757653058560[13] = -nom_x[13] + true_x[13];
   out_7145879757653058560[14] = -nom_x[14] + true_x[14];
   out_7145879757653058560[15] = -nom_x[15] + true_x[15];
   out_7145879757653058560[16] = -nom_x[16] + true_x[16];
   out_7145879757653058560[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_3034674074733119560) {
   out_3034674074733119560[0] = 1.0;
   out_3034674074733119560[1] = 0.0;
   out_3034674074733119560[2] = 0.0;
   out_3034674074733119560[3] = 0.0;
   out_3034674074733119560[4] = 0.0;
   out_3034674074733119560[5] = 0.0;
   out_3034674074733119560[6] = 0.0;
   out_3034674074733119560[7] = 0.0;
   out_3034674074733119560[8] = 0.0;
   out_3034674074733119560[9] = 0.0;
   out_3034674074733119560[10] = 0.0;
   out_3034674074733119560[11] = 0.0;
   out_3034674074733119560[12] = 0.0;
   out_3034674074733119560[13] = 0.0;
   out_3034674074733119560[14] = 0.0;
   out_3034674074733119560[15] = 0.0;
   out_3034674074733119560[16] = 0.0;
   out_3034674074733119560[17] = 0.0;
   out_3034674074733119560[18] = 0.0;
   out_3034674074733119560[19] = 1.0;
   out_3034674074733119560[20] = 0.0;
   out_3034674074733119560[21] = 0.0;
   out_3034674074733119560[22] = 0.0;
   out_3034674074733119560[23] = 0.0;
   out_3034674074733119560[24] = 0.0;
   out_3034674074733119560[25] = 0.0;
   out_3034674074733119560[26] = 0.0;
   out_3034674074733119560[27] = 0.0;
   out_3034674074733119560[28] = 0.0;
   out_3034674074733119560[29] = 0.0;
   out_3034674074733119560[30] = 0.0;
   out_3034674074733119560[31] = 0.0;
   out_3034674074733119560[32] = 0.0;
   out_3034674074733119560[33] = 0.0;
   out_3034674074733119560[34] = 0.0;
   out_3034674074733119560[35] = 0.0;
   out_3034674074733119560[36] = 0.0;
   out_3034674074733119560[37] = 0.0;
   out_3034674074733119560[38] = 1.0;
   out_3034674074733119560[39] = 0.0;
   out_3034674074733119560[40] = 0.0;
   out_3034674074733119560[41] = 0.0;
   out_3034674074733119560[42] = 0.0;
   out_3034674074733119560[43] = 0.0;
   out_3034674074733119560[44] = 0.0;
   out_3034674074733119560[45] = 0.0;
   out_3034674074733119560[46] = 0.0;
   out_3034674074733119560[47] = 0.0;
   out_3034674074733119560[48] = 0.0;
   out_3034674074733119560[49] = 0.0;
   out_3034674074733119560[50] = 0.0;
   out_3034674074733119560[51] = 0.0;
   out_3034674074733119560[52] = 0.0;
   out_3034674074733119560[53] = 0.0;
   out_3034674074733119560[54] = 0.0;
   out_3034674074733119560[55] = 0.0;
   out_3034674074733119560[56] = 0.0;
   out_3034674074733119560[57] = 1.0;
   out_3034674074733119560[58] = 0.0;
   out_3034674074733119560[59] = 0.0;
   out_3034674074733119560[60] = 0.0;
   out_3034674074733119560[61] = 0.0;
   out_3034674074733119560[62] = 0.0;
   out_3034674074733119560[63] = 0.0;
   out_3034674074733119560[64] = 0.0;
   out_3034674074733119560[65] = 0.0;
   out_3034674074733119560[66] = 0.0;
   out_3034674074733119560[67] = 0.0;
   out_3034674074733119560[68] = 0.0;
   out_3034674074733119560[69] = 0.0;
   out_3034674074733119560[70] = 0.0;
   out_3034674074733119560[71] = 0.0;
   out_3034674074733119560[72] = 0.0;
   out_3034674074733119560[73] = 0.0;
   out_3034674074733119560[74] = 0.0;
   out_3034674074733119560[75] = 0.0;
   out_3034674074733119560[76] = 1.0;
   out_3034674074733119560[77] = 0.0;
   out_3034674074733119560[78] = 0.0;
   out_3034674074733119560[79] = 0.0;
   out_3034674074733119560[80] = 0.0;
   out_3034674074733119560[81] = 0.0;
   out_3034674074733119560[82] = 0.0;
   out_3034674074733119560[83] = 0.0;
   out_3034674074733119560[84] = 0.0;
   out_3034674074733119560[85] = 0.0;
   out_3034674074733119560[86] = 0.0;
   out_3034674074733119560[87] = 0.0;
   out_3034674074733119560[88] = 0.0;
   out_3034674074733119560[89] = 0.0;
   out_3034674074733119560[90] = 0.0;
   out_3034674074733119560[91] = 0.0;
   out_3034674074733119560[92] = 0.0;
   out_3034674074733119560[93] = 0.0;
   out_3034674074733119560[94] = 0.0;
   out_3034674074733119560[95] = 1.0;
   out_3034674074733119560[96] = 0.0;
   out_3034674074733119560[97] = 0.0;
   out_3034674074733119560[98] = 0.0;
   out_3034674074733119560[99] = 0.0;
   out_3034674074733119560[100] = 0.0;
   out_3034674074733119560[101] = 0.0;
   out_3034674074733119560[102] = 0.0;
   out_3034674074733119560[103] = 0.0;
   out_3034674074733119560[104] = 0.0;
   out_3034674074733119560[105] = 0.0;
   out_3034674074733119560[106] = 0.0;
   out_3034674074733119560[107] = 0.0;
   out_3034674074733119560[108] = 0.0;
   out_3034674074733119560[109] = 0.0;
   out_3034674074733119560[110] = 0.0;
   out_3034674074733119560[111] = 0.0;
   out_3034674074733119560[112] = 0.0;
   out_3034674074733119560[113] = 0.0;
   out_3034674074733119560[114] = 1.0;
   out_3034674074733119560[115] = 0.0;
   out_3034674074733119560[116] = 0.0;
   out_3034674074733119560[117] = 0.0;
   out_3034674074733119560[118] = 0.0;
   out_3034674074733119560[119] = 0.0;
   out_3034674074733119560[120] = 0.0;
   out_3034674074733119560[121] = 0.0;
   out_3034674074733119560[122] = 0.0;
   out_3034674074733119560[123] = 0.0;
   out_3034674074733119560[124] = 0.0;
   out_3034674074733119560[125] = 0.0;
   out_3034674074733119560[126] = 0.0;
   out_3034674074733119560[127] = 0.0;
   out_3034674074733119560[128] = 0.0;
   out_3034674074733119560[129] = 0.0;
   out_3034674074733119560[130] = 0.0;
   out_3034674074733119560[131] = 0.0;
   out_3034674074733119560[132] = 0.0;
   out_3034674074733119560[133] = 1.0;
   out_3034674074733119560[134] = 0.0;
   out_3034674074733119560[135] = 0.0;
   out_3034674074733119560[136] = 0.0;
   out_3034674074733119560[137] = 0.0;
   out_3034674074733119560[138] = 0.0;
   out_3034674074733119560[139] = 0.0;
   out_3034674074733119560[140] = 0.0;
   out_3034674074733119560[141] = 0.0;
   out_3034674074733119560[142] = 0.0;
   out_3034674074733119560[143] = 0.0;
   out_3034674074733119560[144] = 0.0;
   out_3034674074733119560[145] = 0.0;
   out_3034674074733119560[146] = 0.0;
   out_3034674074733119560[147] = 0.0;
   out_3034674074733119560[148] = 0.0;
   out_3034674074733119560[149] = 0.0;
   out_3034674074733119560[150] = 0.0;
   out_3034674074733119560[151] = 0.0;
   out_3034674074733119560[152] = 1.0;
   out_3034674074733119560[153] = 0.0;
   out_3034674074733119560[154] = 0.0;
   out_3034674074733119560[155] = 0.0;
   out_3034674074733119560[156] = 0.0;
   out_3034674074733119560[157] = 0.0;
   out_3034674074733119560[158] = 0.0;
   out_3034674074733119560[159] = 0.0;
   out_3034674074733119560[160] = 0.0;
   out_3034674074733119560[161] = 0.0;
   out_3034674074733119560[162] = 0.0;
   out_3034674074733119560[163] = 0.0;
   out_3034674074733119560[164] = 0.0;
   out_3034674074733119560[165] = 0.0;
   out_3034674074733119560[166] = 0.0;
   out_3034674074733119560[167] = 0.0;
   out_3034674074733119560[168] = 0.0;
   out_3034674074733119560[169] = 0.0;
   out_3034674074733119560[170] = 0.0;
   out_3034674074733119560[171] = 1.0;
   out_3034674074733119560[172] = 0.0;
   out_3034674074733119560[173] = 0.0;
   out_3034674074733119560[174] = 0.0;
   out_3034674074733119560[175] = 0.0;
   out_3034674074733119560[176] = 0.0;
   out_3034674074733119560[177] = 0.0;
   out_3034674074733119560[178] = 0.0;
   out_3034674074733119560[179] = 0.0;
   out_3034674074733119560[180] = 0.0;
   out_3034674074733119560[181] = 0.0;
   out_3034674074733119560[182] = 0.0;
   out_3034674074733119560[183] = 0.0;
   out_3034674074733119560[184] = 0.0;
   out_3034674074733119560[185] = 0.0;
   out_3034674074733119560[186] = 0.0;
   out_3034674074733119560[187] = 0.0;
   out_3034674074733119560[188] = 0.0;
   out_3034674074733119560[189] = 0.0;
   out_3034674074733119560[190] = 1.0;
   out_3034674074733119560[191] = 0.0;
   out_3034674074733119560[192] = 0.0;
   out_3034674074733119560[193] = 0.0;
   out_3034674074733119560[194] = 0.0;
   out_3034674074733119560[195] = 0.0;
   out_3034674074733119560[196] = 0.0;
   out_3034674074733119560[197] = 0.0;
   out_3034674074733119560[198] = 0.0;
   out_3034674074733119560[199] = 0.0;
   out_3034674074733119560[200] = 0.0;
   out_3034674074733119560[201] = 0.0;
   out_3034674074733119560[202] = 0.0;
   out_3034674074733119560[203] = 0.0;
   out_3034674074733119560[204] = 0.0;
   out_3034674074733119560[205] = 0.0;
   out_3034674074733119560[206] = 0.0;
   out_3034674074733119560[207] = 0.0;
   out_3034674074733119560[208] = 0.0;
   out_3034674074733119560[209] = 1.0;
   out_3034674074733119560[210] = 0.0;
   out_3034674074733119560[211] = 0.0;
   out_3034674074733119560[212] = 0.0;
   out_3034674074733119560[213] = 0.0;
   out_3034674074733119560[214] = 0.0;
   out_3034674074733119560[215] = 0.0;
   out_3034674074733119560[216] = 0.0;
   out_3034674074733119560[217] = 0.0;
   out_3034674074733119560[218] = 0.0;
   out_3034674074733119560[219] = 0.0;
   out_3034674074733119560[220] = 0.0;
   out_3034674074733119560[221] = 0.0;
   out_3034674074733119560[222] = 0.0;
   out_3034674074733119560[223] = 0.0;
   out_3034674074733119560[224] = 0.0;
   out_3034674074733119560[225] = 0.0;
   out_3034674074733119560[226] = 0.0;
   out_3034674074733119560[227] = 0.0;
   out_3034674074733119560[228] = 1.0;
   out_3034674074733119560[229] = 0.0;
   out_3034674074733119560[230] = 0.0;
   out_3034674074733119560[231] = 0.0;
   out_3034674074733119560[232] = 0.0;
   out_3034674074733119560[233] = 0.0;
   out_3034674074733119560[234] = 0.0;
   out_3034674074733119560[235] = 0.0;
   out_3034674074733119560[236] = 0.0;
   out_3034674074733119560[237] = 0.0;
   out_3034674074733119560[238] = 0.0;
   out_3034674074733119560[239] = 0.0;
   out_3034674074733119560[240] = 0.0;
   out_3034674074733119560[241] = 0.0;
   out_3034674074733119560[242] = 0.0;
   out_3034674074733119560[243] = 0.0;
   out_3034674074733119560[244] = 0.0;
   out_3034674074733119560[245] = 0.0;
   out_3034674074733119560[246] = 0.0;
   out_3034674074733119560[247] = 1.0;
   out_3034674074733119560[248] = 0.0;
   out_3034674074733119560[249] = 0.0;
   out_3034674074733119560[250] = 0.0;
   out_3034674074733119560[251] = 0.0;
   out_3034674074733119560[252] = 0.0;
   out_3034674074733119560[253] = 0.0;
   out_3034674074733119560[254] = 0.0;
   out_3034674074733119560[255] = 0.0;
   out_3034674074733119560[256] = 0.0;
   out_3034674074733119560[257] = 0.0;
   out_3034674074733119560[258] = 0.0;
   out_3034674074733119560[259] = 0.0;
   out_3034674074733119560[260] = 0.0;
   out_3034674074733119560[261] = 0.0;
   out_3034674074733119560[262] = 0.0;
   out_3034674074733119560[263] = 0.0;
   out_3034674074733119560[264] = 0.0;
   out_3034674074733119560[265] = 0.0;
   out_3034674074733119560[266] = 1.0;
   out_3034674074733119560[267] = 0.0;
   out_3034674074733119560[268] = 0.0;
   out_3034674074733119560[269] = 0.0;
   out_3034674074733119560[270] = 0.0;
   out_3034674074733119560[271] = 0.0;
   out_3034674074733119560[272] = 0.0;
   out_3034674074733119560[273] = 0.0;
   out_3034674074733119560[274] = 0.0;
   out_3034674074733119560[275] = 0.0;
   out_3034674074733119560[276] = 0.0;
   out_3034674074733119560[277] = 0.0;
   out_3034674074733119560[278] = 0.0;
   out_3034674074733119560[279] = 0.0;
   out_3034674074733119560[280] = 0.0;
   out_3034674074733119560[281] = 0.0;
   out_3034674074733119560[282] = 0.0;
   out_3034674074733119560[283] = 0.0;
   out_3034674074733119560[284] = 0.0;
   out_3034674074733119560[285] = 1.0;
   out_3034674074733119560[286] = 0.0;
   out_3034674074733119560[287] = 0.0;
   out_3034674074733119560[288] = 0.0;
   out_3034674074733119560[289] = 0.0;
   out_3034674074733119560[290] = 0.0;
   out_3034674074733119560[291] = 0.0;
   out_3034674074733119560[292] = 0.0;
   out_3034674074733119560[293] = 0.0;
   out_3034674074733119560[294] = 0.0;
   out_3034674074733119560[295] = 0.0;
   out_3034674074733119560[296] = 0.0;
   out_3034674074733119560[297] = 0.0;
   out_3034674074733119560[298] = 0.0;
   out_3034674074733119560[299] = 0.0;
   out_3034674074733119560[300] = 0.0;
   out_3034674074733119560[301] = 0.0;
   out_3034674074733119560[302] = 0.0;
   out_3034674074733119560[303] = 0.0;
   out_3034674074733119560[304] = 1.0;
   out_3034674074733119560[305] = 0.0;
   out_3034674074733119560[306] = 0.0;
   out_3034674074733119560[307] = 0.0;
   out_3034674074733119560[308] = 0.0;
   out_3034674074733119560[309] = 0.0;
   out_3034674074733119560[310] = 0.0;
   out_3034674074733119560[311] = 0.0;
   out_3034674074733119560[312] = 0.0;
   out_3034674074733119560[313] = 0.0;
   out_3034674074733119560[314] = 0.0;
   out_3034674074733119560[315] = 0.0;
   out_3034674074733119560[316] = 0.0;
   out_3034674074733119560[317] = 0.0;
   out_3034674074733119560[318] = 0.0;
   out_3034674074733119560[319] = 0.0;
   out_3034674074733119560[320] = 0.0;
   out_3034674074733119560[321] = 0.0;
   out_3034674074733119560[322] = 0.0;
   out_3034674074733119560[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_5494423390909502238) {
   out_5494423390909502238[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_5494423390909502238[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_5494423390909502238[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_5494423390909502238[3] = dt*state[12] + state[3];
   out_5494423390909502238[4] = dt*state[13] + state[4];
   out_5494423390909502238[5] = dt*state[14] + state[5];
   out_5494423390909502238[6] = state[6];
   out_5494423390909502238[7] = state[7];
   out_5494423390909502238[8] = state[8];
   out_5494423390909502238[9] = state[9];
   out_5494423390909502238[10] = state[10];
   out_5494423390909502238[11] = state[11];
   out_5494423390909502238[12] = state[12];
   out_5494423390909502238[13] = state[13];
   out_5494423390909502238[14] = state[14];
   out_5494423390909502238[15] = state[15];
   out_5494423390909502238[16] = state[16];
   out_5494423390909502238[17] = state[17];
}
void F_fun(double *state, double dt, double *out_7397549611683591868) {
   out_7397549611683591868[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7397549611683591868[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7397549611683591868[2] = 0;
   out_7397549611683591868[3] = 0;
   out_7397549611683591868[4] = 0;
   out_7397549611683591868[5] = 0;
   out_7397549611683591868[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7397549611683591868[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7397549611683591868[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7397549611683591868[9] = 0;
   out_7397549611683591868[10] = 0;
   out_7397549611683591868[11] = 0;
   out_7397549611683591868[12] = 0;
   out_7397549611683591868[13] = 0;
   out_7397549611683591868[14] = 0;
   out_7397549611683591868[15] = 0;
   out_7397549611683591868[16] = 0;
   out_7397549611683591868[17] = 0;
   out_7397549611683591868[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7397549611683591868[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7397549611683591868[20] = 0;
   out_7397549611683591868[21] = 0;
   out_7397549611683591868[22] = 0;
   out_7397549611683591868[23] = 0;
   out_7397549611683591868[24] = 0;
   out_7397549611683591868[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7397549611683591868[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7397549611683591868[27] = 0;
   out_7397549611683591868[28] = 0;
   out_7397549611683591868[29] = 0;
   out_7397549611683591868[30] = 0;
   out_7397549611683591868[31] = 0;
   out_7397549611683591868[32] = 0;
   out_7397549611683591868[33] = 0;
   out_7397549611683591868[34] = 0;
   out_7397549611683591868[35] = 0;
   out_7397549611683591868[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7397549611683591868[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7397549611683591868[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7397549611683591868[39] = 0;
   out_7397549611683591868[40] = 0;
   out_7397549611683591868[41] = 0;
   out_7397549611683591868[42] = 0;
   out_7397549611683591868[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7397549611683591868[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7397549611683591868[45] = 0;
   out_7397549611683591868[46] = 0;
   out_7397549611683591868[47] = 0;
   out_7397549611683591868[48] = 0;
   out_7397549611683591868[49] = 0;
   out_7397549611683591868[50] = 0;
   out_7397549611683591868[51] = 0;
   out_7397549611683591868[52] = 0;
   out_7397549611683591868[53] = 0;
   out_7397549611683591868[54] = 0;
   out_7397549611683591868[55] = 0;
   out_7397549611683591868[56] = 0;
   out_7397549611683591868[57] = 1;
   out_7397549611683591868[58] = 0;
   out_7397549611683591868[59] = 0;
   out_7397549611683591868[60] = 0;
   out_7397549611683591868[61] = 0;
   out_7397549611683591868[62] = 0;
   out_7397549611683591868[63] = 0;
   out_7397549611683591868[64] = 0;
   out_7397549611683591868[65] = 0;
   out_7397549611683591868[66] = dt;
   out_7397549611683591868[67] = 0;
   out_7397549611683591868[68] = 0;
   out_7397549611683591868[69] = 0;
   out_7397549611683591868[70] = 0;
   out_7397549611683591868[71] = 0;
   out_7397549611683591868[72] = 0;
   out_7397549611683591868[73] = 0;
   out_7397549611683591868[74] = 0;
   out_7397549611683591868[75] = 0;
   out_7397549611683591868[76] = 1;
   out_7397549611683591868[77] = 0;
   out_7397549611683591868[78] = 0;
   out_7397549611683591868[79] = 0;
   out_7397549611683591868[80] = 0;
   out_7397549611683591868[81] = 0;
   out_7397549611683591868[82] = 0;
   out_7397549611683591868[83] = 0;
   out_7397549611683591868[84] = 0;
   out_7397549611683591868[85] = dt;
   out_7397549611683591868[86] = 0;
   out_7397549611683591868[87] = 0;
   out_7397549611683591868[88] = 0;
   out_7397549611683591868[89] = 0;
   out_7397549611683591868[90] = 0;
   out_7397549611683591868[91] = 0;
   out_7397549611683591868[92] = 0;
   out_7397549611683591868[93] = 0;
   out_7397549611683591868[94] = 0;
   out_7397549611683591868[95] = 1;
   out_7397549611683591868[96] = 0;
   out_7397549611683591868[97] = 0;
   out_7397549611683591868[98] = 0;
   out_7397549611683591868[99] = 0;
   out_7397549611683591868[100] = 0;
   out_7397549611683591868[101] = 0;
   out_7397549611683591868[102] = 0;
   out_7397549611683591868[103] = 0;
   out_7397549611683591868[104] = dt;
   out_7397549611683591868[105] = 0;
   out_7397549611683591868[106] = 0;
   out_7397549611683591868[107] = 0;
   out_7397549611683591868[108] = 0;
   out_7397549611683591868[109] = 0;
   out_7397549611683591868[110] = 0;
   out_7397549611683591868[111] = 0;
   out_7397549611683591868[112] = 0;
   out_7397549611683591868[113] = 0;
   out_7397549611683591868[114] = 1;
   out_7397549611683591868[115] = 0;
   out_7397549611683591868[116] = 0;
   out_7397549611683591868[117] = 0;
   out_7397549611683591868[118] = 0;
   out_7397549611683591868[119] = 0;
   out_7397549611683591868[120] = 0;
   out_7397549611683591868[121] = 0;
   out_7397549611683591868[122] = 0;
   out_7397549611683591868[123] = 0;
   out_7397549611683591868[124] = 0;
   out_7397549611683591868[125] = 0;
   out_7397549611683591868[126] = 0;
   out_7397549611683591868[127] = 0;
   out_7397549611683591868[128] = 0;
   out_7397549611683591868[129] = 0;
   out_7397549611683591868[130] = 0;
   out_7397549611683591868[131] = 0;
   out_7397549611683591868[132] = 0;
   out_7397549611683591868[133] = 1;
   out_7397549611683591868[134] = 0;
   out_7397549611683591868[135] = 0;
   out_7397549611683591868[136] = 0;
   out_7397549611683591868[137] = 0;
   out_7397549611683591868[138] = 0;
   out_7397549611683591868[139] = 0;
   out_7397549611683591868[140] = 0;
   out_7397549611683591868[141] = 0;
   out_7397549611683591868[142] = 0;
   out_7397549611683591868[143] = 0;
   out_7397549611683591868[144] = 0;
   out_7397549611683591868[145] = 0;
   out_7397549611683591868[146] = 0;
   out_7397549611683591868[147] = 0;
   out_7397549611683591868[148] = 0;
   out_7397549611683591868[149] = 0;
   out_7397549611683591868[150] = 0;
   out_7397549611683591868[151] = 0;
   out_7397549611683591868[152] = 1;
   out_7397549611683591868[153] = 0;
   out_7397549611683591868[154] = 0;
   out_7397549611683591868[155] = 0;
   out_7397549611683591868[156] = 0;
   out_7397549611683591868[157] = 0;
   out_7397549611683591868[158] = 0;
   out_7397549611683591868[159] = 0;
   out_7397549611683591868[160] = 0;
   out_7397549611683591868[161] = 0;
   out_7397549611683591868[162] = 0;
   out_7397549611683591868[163] = 0;
   out_7397549611683591868[164] = 0;
   out_7397549611683591868[165] = 0;
   out_7397549611683591868[166] = 0;
   out_7397549611683591868[167] = 0;
   out_7397549611683591868[168] = 0;
   out_7397549611683591868[169] = 0;
   out_7397549611683591868[170] = 0;
   out_7397549611683591868[171] = 1;
   out_7397549611683591868[172] = 0;
   out_7397549611683591868[173] = 0;
   out_7397549611683591868[174] = 0;
   out_7397549611683591868[175] = 0;
   out_7397549611683591868[176] = 0;
   out_7397549611683591868[177] = 0;
   out_7397549611683591868[178] = 0;
   out_7397549611683591868[179] = 0;
   out_7397549611683591868[180] = 0;
   out_7397549611683591868[181] = 0;
   out_7397549611683591868[182] = 0;
   out_7397549611683591868[183] = 0;
   out_7397549611683591868[184] = 0;
   out_7397549611683591868[185] = 0;
   out_7397549611683591868[186] = 0;
   out_7397549611683591868[187] = 0;
   out_7397549611683591868[188] = 0;
   out_7397549611683591868[189] = 0;
   out_7397549611683591868[190] = 1;
   out_7397549611683591868[191] = 0;
   out_7397549611683591868[192] = 0;
   out_7397549611683591868[193] = 0;
   out_7397549611683591868[194] = 0;
   out_7397549611683591868[195] = 0;
   out_7397549611683591868[196] = 0;
   out_7397549611683591868[197] = 0;
   out_7397549611683591868[198] = 0;
   out_7397549611683591868[199] = 0;
   out_7397549611683591868[200] = 0;
   out_7397549611683591868[201] = 0;
   out_7397549611683591868[202] = 0;
   out_7397549611683591868[203] = 0;
   out_7397549611683591868[204] = 0;
   out_7397549611683591868[205] = 0;
   out_7397549611683591868[206] = 0;
   out_7397549611683591868[207] = 0;
   out_7397549611683591868[208] = 0;
   out_7397549611683591868[209] = 1;
   out_7397549611683591868[210] = 0;
   out_7397549611683591868[211] = 0;
   out_7397549611683591868[212] = 0;
   out_7397549611683591868[213] = 0;
   out_7397549611683591868[214] = 0;
   out_7397549611683591868[215] = 0;
   out_7397549611683591868[216] = 0;
   out_7397549611683591868[217] = 0;
   out_7397549611683591868[218] = 0;
   out_7397549611683591868[219] = 0;
   out_7397549611683591868[220] = 0;
   out_7397549611683591868[221] = 0;
   out_7397549611683591868[222] = 0;
   out_7397549611683591868[223] = 0;
   out_7397549611683591868[224] = 0;
   out_7397549611683591868[225] = 0;
   out_7397549611683591868[226] = 0;
   out_7397549611683591868[227] = 0;
   out_7397549611683591868[228] = 1;
   out_7397549611683591868[229] = 0;
   out_7397549611683591868[230] = 0;
   out_7397549611683591868[231] = 0;
   out_7397549611683591868[232] = 0;
   out_7397549611683591868[233] = 0;
   out_7397549611683591868[234] = 0;
   out_7397549611683591868[235] = 0;
   out_7397549611683591868[236] = 0;
   out_7397549611683591868[237] = 0;
   out_7397549611683591868[238] = 0;
   out_7397549611683591868[239] = 0;
   out_7397549611683591868[240] = 0;
   out_7397549611683591868[241] = 0;
   out_7397549611683591868[242] = 0;
   out_7397549611683591868[243] = 0;
   out_7397549611683591868[244] = 0;
   out_7397549611683591868[245] = 0;
   out_7397549611683591868[246] = 0;
   out_7397549611683591868[247] = 1;
   out_7397549611683591868[248] = 0;
   out_7397549611683591868[249] = 0;
   out_7397549611683591868[250] = 0;
   out_7397549611683591868[251] = 0;
   out_7397549611683591868[252] = 0;
   out_7397549611683591868[253] = 0;
   out_7397549611683591868[254] = 0;
   out_7397549611683591868[255] = 0;
   out_7397549611683591868[256] = 0;
   out_7397549611683591868[257] = 0;
   out_7397549611683591868[258] = 0;
   out_7397549611683591868[259] = 0;
   out_7397549611683591868[260] = 0;
   out_7397549611683591868[261] = 0;
   out_7397549611683591868[262] = 0;
   out_7397549611683591868[263] = 0;
   out_7397549611683591868[264] = 0;
   out_7397549611683591868[265] = 0;
   out_7397549611683591868[266] = 1;
   out_7397549611683591868[267] = 0;
   out_7397549611683591868[268] = 0;
   out_7397549611683591868[269] = 0;
   out_7397549611683591868[270] = 0;
   out_7397549611683591868[271] = 0;
   out_7397549611683591868[272] = 0;
   out_7397549611683591868[273] = 0;
   out_7397549611683591868[274] = 0;
   out_7397549611683591868[275] = 0;
   out_7397549611683591868[276] = 0;
   out_7397549611683591868[277] = 0;
   out_7397549611683591868[278] = 0;
   out_7397549611683591868[279] = 0;
   out_7397549611683591868[280] = 0;
   out_7397549611683591868[281] = 0;
   out_7397549611683591868[282] = 0;
   out_7397549611683591868[283] = 0;
   out_7397549611683591868[284] = 0;
   out_7397549611683591868[285] = 1;
   out_7397549611683591868[286] = 0;
   out_7397549611683591868[287] = 0;
   out_7397549611683591868[288] = 0;
   out_7397549611683591868[289] = 0;
   out_7397549611683591868[290] = 0;
   out_7397549611683591868[291] = 0;
   out_7397549611683591868[292] = 0;
   out_7397549611683591868[293] = 0;
   out_7397549611683591868[294] = 0;
   out_7397549611683591868[295] = 0;
   out_7397549611683591868[296] = 0;
   out_7397549611683591868[297] = 0;
   out_7397549611683591868[298] = 0;
   out_7397549611683591868[299] = 0;
   out_7397549611683591868[300] = 0;
   out_7397549611683591868[301] = 0;
   out_7397549611683591868[302] = 0;
   out_7397549611683591868[303] = 0;
   out_7397549611683591868[304] = 1;
   out_7397549611683591868[305] = 0;
   out_7397549611683591868[306] = 0;
   out_7397549611683591868[307] = 0;
   out_7397549611683591868[308] = 0;
   out_7397549611683591868[309] = 0;
   out_7397549611683591868[310] = 0;
   out_7397549611683591868[311] = 0;
   out_7397549611683591868[312] = 0;
   out_7397549611683591868[313] = 0;
   out_7397549611683591868[314] = 0;
   out_7397549611683591868[315] = 0;
   out_7397549611683591868[316] = 0;
   out_7397549611683591868[317] = 0;
   out_7397549611683591868[318] = 0;
   out_7397549611683591868[319] = 0;
   out_7397549611683591868[320] = 0;
   out_7397549611683591868[321] = 0;
   out_7397549611683591868[322] = 0;
   out_7397549611683591868[323] = 1;
}
void h_4(double *state, double *unused, double *out_4176955461475617995) {
   out_4176955461475617995[0] = state[6] + state[9];
   out_4176955461475617995[1] = state[7] + state[10];
   out_4176955461475617995[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_737133135110788012) {
   out_737133135110788012[0] = 0;
   out_737133135110788012[1] = 0;
   out_737133135110788012[2] = 0;
   out_737133135110788012[3] = 0;
   out_737133135110788012[4] = 0;
   out_737133135110788012[5] = 0;
   out_737133135110788012[6] = 1;
   out_737133135110788012[7] = 0;
   out_737133135110788012[8] = 0;
   out_737133135110788012[9] = 1;
   out_737133135110788012[10] = 0;
   out_737133135110788012[11] = 0;
   out_737133135110788012[12] = 0;
   out_737133135110788012[13] = 0;
   out_737133135110788012[14] = 0;
   out_737133135110788012[15] = 0;
   out_737133135110788012[16] = 0;
   out_737133135110788012[17] = 0;
   out_737133135110788012[18] = 0;
   out_737133135110788012[19] = 0;
   out_737133135110788012[20] = 0;
   out_737133135110788012[21] = 0;
   out_737133135110788012[22] = 0;
   out_737133135110788012[23] = 0;
   out_737133135110788012[24] = 0;
   out_737133135110788012[25] = 1;
   out_737133135110788012[26] = 0;
   out_737133135110788012[27] = 0;
   out_737133135110788012[28] = 1;
   out_737133135110788012[29] = 0;
   out_737133135110788012[30] = 0;
   out_737133135110788012[31] = 0;
   out_737133135110788012[32] = 0;
   out_737133135110788012[33] = 0;
   out_737133135110788012[34] = 0;
   out_737133135110788012[35] = 0;
   out_737133135110788012[36] = 0;
   out_737133135110788012[37] = 0;
   out_737133135110788012[38] = 0;
   out_737133135110788012[39] = 0;
   out_737133135110788012[40] = 0;
   out_737133135110788012[41] = 0;
   out_737133135110788012[42] = 0;
   out_737133135110788012[43] = 0;
   out_737133135110788012[44] = 1;
   out_737133135110788012[45] = 0;
   out_737133135110788012[46] = 0;
   out_737133135110788012[47] = 1;
   out_737133135110788012[48] = 0;
   out_737133135110788012[49] = 0;
   out_737133135110788012[50] = 0;
   out_737133135110788012[51] = 0;
   out_737133135110788012[52] = 0;
   out_737133135110788012[53] = 0;
}
void h_10(double *state, double *unused, double *out_46181122683215881) {
   out_46181122683215881[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_46181122683215881[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_46181122683215881[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_1259791951393668272) {
   out_1259791951393668272[0] = 0;
   out_1259791951393668272[1] = 9.8100000000000005*cos(state[1]);
   out_1259791951393668272[2] = 0;
   out_1259791951393668272[3] = 0;
   out_1259791951393668272[4] = -state[8];
   out_1259791951393668272[5] = state[7];
   out_1259791951393668272[6] = 0;
   out_1259791951393668272[7] = state[5];
   out_1259791951393668272[8] = -state[4];
   out_1259791951393668272[9] = 0;
   out_1259791951393668272[10] = 0;
   out_1259791951393668272[11] = 0;
   out_1259791951393668272[12] = 1;
   out_1259791951393668272[13] = 0;
   out_1259791951393668272[14] = 0;
   out_1259791951393668272[15] = 1;
   out_1259791951393668272[16] = 0;
   out_1259791951393668272[17] = 0;
   out_1259791951393668272[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_1259791951393668272[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_1259791951393668272[20] = 0;
   out_1259791951393668272[21] = state[8];
   out_1259791951393668272[22] = 0;
   out_1259791951393668272[23] = -state[6];
   out_1259791951393668272[24] = -state[5];
   out_1259791951393668272[25] = 0;
   out_1259791951393668272[26] = state[3];
   out_1259791951393668272[27] = 0;
   out_1259791951393668272[28] = 0;
   out_1259791951393668272[29] = 0;
   out_1259791951393668272[30] = 0;
   out_1259791951393668272[31] = 1;
   out_1259791951393668272[32] = 0;
   out_1259791951393668272[33] = 0;
   out_1259791951393668272[34] = 1;
   out_1259791951393668272[35] = 0;
   out_1259791951393668272[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_1259791951393668272[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_1259791951393668272[38] = 0;
   out_1259791951393668272[39] = -state[7];
   out_1259791951393668272[40] = state[6];
   out_1259791951393668272[41] = 0;
   out_1259791951393668272[42] = state[4];
   out_1259791951393668272[43] = -state[3];
   out_1259791951393668272[44] = 0;
   out_1259791951393668272[45] = 0;
   out_1259791951393668272[46] = 0;
   out_1259791951393668272[47] = 0;
   out_1259791951393668272[48] = 0;
   out_1259791951393668272[49] = 0;
   out_1259791951393668272[50] = 1;
   out_1259791951393668272[51] = 0;
   out_1259791951393668272[52] = 0;
   out_1259791951393668272[53] = 1;
}
void h_13(double *state, double *unused, double *out_4952163822481543057) {
   out_4952163822481543057[0] = state[3];
   out_4952163822481543057[1] = state[4];
   out_4952163822481543057[2] = state[5];
}
void H_13(double *state, double *unused, double *out_3096622328191736012) {
   out_3096622328191736012[0] = 0;
   out_3096622328191736012[1] = 0;
   out_3096622328191736012[2] = 0;
   out_3096622328191736012[3] = 1;
   out_3096622328191736012[4] = 0;
   out_3096622328191736012[5] = 0;
   out_3096622328191736012[6] = 0;
   out_3096622328191736012[7] = 0;
   out_3096622328191736012[8] = 0;
   out_3096622328191736012[9] = 0;
   out_3096622328191736012[10] = 0;
   out_3096622328191736012[11] = 0;
   out_3096622328191736012[12] = 0;
   out_3096622328191736012[13] = 0;
   out_3096622328191736012[14] = 0;
   out_3096622328191736012[15] = 0;
   out_3096622328191736012[16] = 0;
   out_3096622328191736012[17] = 0;
   out_3096622328191736012[18] = 0;
   out_3096622328191736012[19] = 0;
   out_3096622328191736012[20] = 0;
   out_3096622328191736012[21] = 0;
   out_3096622328191736012[22] = 1;
   out_3096622328191736012[23] = 0;
   out_3096622328191736012[24] = 0;
   out_3096622328191736012[25] = 0;
   out_3096622328191736012[26] = 0;
   out_3096622328191736012[27] = 0;
   out_3096622328191736012[28] = 0;
   out_3096622328191736012[29] = 0;
   out_3096622328191736012[30] = 0;
   out_3096622328191736012[31] = 0;
   out_3096622328191736012[32] = 0;
   out_3096622328191736012[33] = 0;
   out_3096622328191736012[34] = 0;
   out_3096622328191736012[35] = 0;
   out_3096622328191736012[36] = 0;
   out_3096622328191736012[37] = 0;
   out_3096622328191736012[38] = 0;
   out_3096622328191736012[39] = 0;
   out_3096622328191736012[40] = 0;
   out_3096622328191736012[41] = 1;
   out_3096622328191736012[42] = 0;
   out_3096622328191736012[43] = 0;
   out_3096622328191736012[44] = 0;
   out_3096622328191736012[45] = 0;
   out_3096622328191736012[46] = 0;
   out_3096622328191736012[47] = 0;
   out_3096622328191736012[48] = 0;
   out_3096622328191736012[49] = 0;
   out_3096622328191736012[50] = 0;
   out_3096622328191736012[51] = 0;
   out_3096622328191736012[52] = 0;
   out_3096622328191736012[53] = 0;
}
void h_14(double *state, double *unused, double *out_4243659524338283765) {
   out_4243659524338283765[0] = state[6];
   out_4243659524338283765[1] = state[7];
   out_4243659524338283765[2] = state[8];
}
void H_14(double *state, double *unused, double *out_2345655297184584284) {
   out_2345655297184584284[0] = 0;
   out_2345655297184584284[1] = 0;
   out_2345655297184584284[2] = 0;
   out_2345655297184584284[3] = 0;
   out_2345655297184584284[4] = 0;
   out_2345655297184584284[5] = 0;
   out_2345655297184584284[6] = 1;
   out_2345655297184584284[7] = 0;
   out_2345655297184584284[8] = 0;
   out_2345655297184584284[9] = 0;
   out_2345655297184584284[10] = 0;
   out_2345655297184584284[11] = 0;
   out_2345655297184584284[12] = 0;
   out_2345655297184584284[13] = 0;
   out_2345655297184584284[14] = 0;
   out_2345655297184584284[15] = 0;
   out_2345655297184584284[16] = 0;
   out_2345655297184584284[17] = 0;
   out_2345655297184584284[18] = 0;
   out_2345655297184584284[19] = 0;
   out_2345655297184584284[20] = 0;
   out_2345655297184584284[21] = 0;
   out_2345655297184584284[22] = 0;
   out_2345655297184584284[23] = 0;
   out_2345655297184584284[24] = 0;
   out_2345655297184584284[25] = 1;
   out_2345655297184584284[26] = 0;
   out_2345655297184584284[27] = 0;
   out_2345655297184584284[28] = 0;
   out_2345655297184584284[29] = 0;
   out_2345655297184584284[30] = 0;
   out_2345655297184584284[31] = 0;
   out_2345655297184584284[32] = 0;
   out_2345655297184584284[33] = 0;
   out_2345655297184584284[34] = 0;
   out_2345655297184584284[35] = 0;
   out_2345655297184584284[36] = 0;
   out_2345655297184584284[37] = 0;
   out_2345655297184584284[38] = 0;
   out_2345655297184584284[39] = 0;
   out_2345655297184584284[40] = 0;
   out_2345655297184584284[41] = 0;
   out_2345655297184584284[42] = 0;
   out_2345655297184584284[43] = 0;
   out_2345655297184584284[44] = 1;
   out_2345655297184584284[45] = 0;
   out_2345655297184584284[46] = 0;
   out_2345655297184584284[47] = 0;
   out_2345655297184584284[48] = 0;
   out_2345655297184584284[49] = 0;
   out_2345655297184584284[50] = 0;
   out_2345655297184584284[51] = 0;
   out_2345655297184584284[52] = 0;
   out_2345655297184584284[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_5792096138533243612) {
  err_fun(nom_x, delta_x, out_5792096138533243612);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_7145879757653058560) {
  inv_err_fun(nom_x, true_x, out_7145879757653058560);
}
void pose_H_mod_fun(double *state, double *out_3034674074733119560) {
  H_mod_fun(state, out_3034674074733119560);
}
void pose_f_fun(double *state, double dt, double *out_5494423390909502238) {
  f_fun(state,  dt, out_5494423390909502238);
}
void pose_F_fun(double *state, double dt, double *out_7397549611683591868) {
  F_fun(state,  dt, out_7397549611683591868);
}
void pose_h_4(double *state, double *unused, double *out_4176955461475617995) {
  h_4(state, unused, out_4176955461475617995);
}
void pose_H_4(double *state, double *unused, double *out_737133135110788012) {
  H_4(state, unused, out_737133135110788012);
}
void pose_h_10(double *state, double *unused, double *out_46181122683215881) {
  h_10(state, unused, out_46181122683215881);
}
void pose_H_10(double *state, double *unused, double *out_1259791951393668272) {
  H_10(state, unused, out_1259791951393668272);
}
void pose_h_13(double *state, double *unused, double *out_4952163822481543057) {
  h_13(state, unused, out_4952163822481543057);
}
void pose_H_13(double *state, double *unused, double *out_3096622328191736012) {
  H_13(state, unused, out_3096622328191736012);
}
void pose_h_14(double *state, double *unused, double *out_4243659524338283765) {
  h_14(state, unused, out_4243659524338283765);
}
void pose_H_14(double *state, double *unused, double *out_2345655297184584284) {
  H_14(state, unused, out_2345655297184584284);
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
