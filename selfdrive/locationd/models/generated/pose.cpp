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
void err_fun(double *nom_x, double *delta_x, double *out_5289520161060537688) {
   out_5289520161060537688[0] = delta_x[0] + nom_x[0];
   out_5289520161060537688[1] = delta_x[1] + nom_x[1];
   out_5289520161060537688[2] = delta_x[2] + nom_x[2];
   out_5289520161060537688[3] = delta_x[3] + nom_x[3];
   out_5289520161060537688[4] = delta_x[4] + nom_x[4];
   out_5289520161060537688[5] = delta_x[5] + nom_x[5];
   out_5289520161060537688[6] = delta_x[6] + nom_x[6];
   out_5289520161060537688[7] = delta_x[7] + nom_x[7];
   out_5289520161060537688[8] = delta_x[8] + nom_x[8];
   out_5289520161060537688[9] = delta_x[9] + nom_x[9];
   out_5289520161060537688[10] = delta_x[10] + nom_x[10];
   out_5289520161060537688[11] = delta_x[11] + nom_x[11];
   out_5289520161060537688[12] = delta_x[12] + nom_x[12];
   out_5289520161060537688[13] = delta_x[13] + nom_x[13];
   out_5289520161060537688[14] = delta_x[14] + nom_x[14];
   out_5289520161060537688[15] = delta_x[15] + nom_x[15];
   out_5289520161060537688[16] = delta_x[16] + nom_x[16];
   out_5289520161060537688[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_8611651352423676881) {
   out_8611651352423676881[0] = -nom_x[0] + true_x[0];
   out_8611651352423676881[1] = -nom_x[1] + true_x[1];
   out_8611651352423676881[2] = -nom_x[2] + true_x[2];
   out_8611651352423676881[3] = -nom_x[3] + true_x[3];
   out_8611651352423676881[4] = -nom_x[4] + true_x[4];
   out_8611651352423676881[5] = -nom_x[5] + true_x[5];
   out_8611651352423676881[6] = -nom_x[6] + true_x[6];
   out_8611651352423676881[7] = -nom_x[7] + true_x[7];
   out_8611651352423676881[8] = -nom_x[8] + true_x[8];
   out_8611651352423676881[9] = -nom_x[9] + true_x[9];
   out_8611651352423676881[10] = -nom_x[10] + true_x[10];
   out_8611651352423676881[11] = -nom_x[11] + true_x[11];
   out_8611651352423676881[12] = -nom_x[12] + true_x[12];
   out_8611651352423676881[13] = -nom_x[13] + true_x[13];
   out_8611651352423676881[14] = -nom_x[14] + true_x[14];
   out_8611651352423676881[15] = -nom_x[15] + true_x[15];
   out_8611651352423676881[16] = -nom_x[16] + true_x[16];
   out_8611651352423676881[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_2960483098895628084) {
   out_2960483098895628084[0] = 1.0;
   out_2960483098895628084[1] = 0.0;
   out_2960483098895628084[2] = 0.0;
   out_2960483098895628084[3] = 0.0;
   out_2960483098895628084[4] = 0.0;
   out_2960483098895628084[5] = 0.0;
   out_2960483098895628084[6] = 0.0;
   out_2960483098895628084[7] = 0.0;
   out_2960483098895628084[8] = 0.0;
   out_2960483098895628084[9] = 0.0;
   out_2960483098895628084[10] = 0.0;
   out_2960483098895628084[11] = 0.0;
   out_2960483098895628084[12] = 0.0;
   out_2960483098895628084[13] = 0.0;
   out_2960483098895628084[14] = 0.0;
   out_2960483098895628084[15] = 0.0;
   out_2960483098895628084[16] = 0.0;
   out_2960483098895628084[17] = 0.0;
   out_2960483098895628084[18] = 0.0;
   out_2960483098895628084[19] = 1.0;
   out_2960483098895628084[20] = 0.0;
   out_2960483098895628084[21] = 0.0;
   out_2960483098895628084[22] = 0.0;
   out_2960483098895628084[23] = 0.0;
   out_2960483098895628084[24] = 0.0;
   out_2960483098895628084[25] = 0.0;
   out_2960483098895628084[26] = 0.0;
   out_2960483098895628084[27] = 0.0;
   out_2960483098895628084[28] = 0.0;
   out_2960483098895628084[29] = 0.0;
   out_2960483098895628084[30] = 0.0;
   out_2960483098895628084[31] = 0.0;
   out_2960483098895628084[32] = 0.0;
   out_2960483098895628084[33] = 0.0;
   out_2960483098895628084[34] = 0.0;
   out_2960483098895628084[35] = 0.0;
   out_2960483098895628084[36] = 0.0;
   out_2960483098895628084[37] = 0.0;
   out_2960483098895628084[38] = 1.0;
   out_2960483098895628084[39] = 0.0;
   out_2960483098895628084[40] = 0.0;
   out_2960483098895628084[41] = 0.0;
   out_2960483098895628084[42] = 0.0;
   out_2960483098895628084[43] = 0.0;
   out_2960483098895628084[44] = 0.0;
   out_2960483098895628084[45] = 0.0;
   out_2960483098895628084[46] = 0.0;
   out_2960483098895628084[47] = 0.0;
   out_2960483098895628084[48] = 0.0;
   out_2960483098895628084[49] = 0.0;
   out_2960483098895628084[50] = 0.0;
   out_2960483098895628084[51] = 0.0;
   out_2960483098895628084[52] = 0.0;
   out_2960483098895628084[53] = 0.0;
   out_2960483098895628084[54] = 0.0;
   out_2960483098895628084[55] = 0.0;
   out_2960483098895628084[56] = 0.0;
   out_2960483098895628084[57] = 1.0;
   out_2960483098895628084[58] = 0.0;
   out_2960483098895628084[59] = 0.0;
   out_2960483098895628084[60] = 0.0;
   out_2960483098895628084[61] = 0.0;
   out_2960483098895628084[62] = 0.0;
   out_2960483098895628084[63] = 0.0;
   out_2960483098895628084[64] = 0.0;
   out_2960483098895628084[65] = 0.0;
   out_2960483098895628084[66] = 0.0;
   out_2960483098895628084[67] = 0.0;
   out_2960483098895628084[68] = 0.0;
   out_2960483098895628084[69] = 0.0;
   out_2960483098895628084[70] = 0.0;
   out_2960483098895628084[71] = 0.0;
   out_2960483098895628084[72] = 0.0;
   out_2960483098895628084[73] = 0.0;
   out_2960483098895628084[74] = 0.0;
   out_2960483098895628084[75] = 0.0;
   out_2960483098895628084[76] = 1.0;
   out_2960483098895628084[77] = 0.0;
   out_2960483098895628084[78] = 0.0;
   out_2960483098895628084[79] = 0.0;
   out_2960483098895628084[80] = 0.0;
   out_2960483098895628084[81] = 0.0;
   out_2960483098895628084[82] = 0.0;
   out_2960483098895628084[83] = 0.0;
   out_2960483098895628084[84] = 0.0;
   out_2960483098895628084[85] = 0.0;
   out_2960483098895628084[86] = 0.0;
   out_2960483098895628084[87] = 0.0;
   out_2960483098895628084[88] = 0.0;
   out_2960483098895628084[89] = 0.0;
   out_2960483098895628084[90] = 0.0;
   out_2960483098895628084[91] = 0.0;
   out_2960483098895628084[92] = 0.0;
   out_2960483098895628084[93] = 0.0;
   out_2960483098895628084[94] = 0.0;
   out_2960483098895628084[95] = 1.0;
   out_2960483098895628084[96] = 0.0;
   out_2960483098895628084[97] = 0.0;
   out_2960483098895628084[98] = 0.0;
   out_2960483098895628084[99] = 0.0;
   out_2960483098895628084[100] = 0.0;
   out_2960483098895628084[101] = 0.0;
   out_2960483098895628084[102] = 0.0;
   out_2960483098895628084[103] = 0.0;
   out_2960483098895628084[104] = 0.0;
   out_2960483098895628084[105] = 0.0;
   out_2960483098895628084[106] = 0.0;
   out_2960483098895628084[107] = 0.0;
   out_2960483098895628084[108] = 0.0;
   out_2960483098895628084[109] = 0.0;
   out_2960483098895628084[110] = 0.0;
   out_2960483098895628084[111] = 0.0;
   out_2960483098895628084[112] = 0.0;
   out_2960483098895628084[113] = 0.0;
   out_2960483098895628084[114] = 1.0;
   out_2960483098895628084[115] = 0.0;
   out_2960483098895628084[116] = 0.0;
   out_2960483098895628084[117] = 0.0;
   out_2960483098895628084[118] = 0.0;
   out_2960483098895628084[119] = 0.0;
   out_2960483098895628084[120] = 0.0;
   out_2960483098895628084[121] = 0.0;
   out_2960483098895628084[122] = 0.0;
   out_2960483098895628084[123] = 0.0;
   out_2960483098895628084[124] = 0.0;
   out_2960483098895628084[125] = 0.0;
   out_2960483098895628084[126] = 0.0;
   out_2960483098895628084[127] = 0.0;
   out_2960483098895628084[128] = 0.0;
   out_2960483098895628084[129] = 0.0;
   out_2960483098895628084[130] = 0.0;
   out_2960483098895628084[131] = 0.0;
   out_2960483098895628084[132] = 0.0;
   out_2960483098895628084[133] = 1.0;
   out_2960483098895628084[134] = 0.0;
   out_2960483098895628084[135] = 0.0;
   out_2960483098895628084[136] = 0.0;
   out_2960483098895628084[137] = 0.0;
   out_2960483098895628084[138] = 0.0;
   out_2960483098895628084[139] = 0.0;
   out_2960483098895628084[140] = 0.0;
   out_2960483098895628084[141] = 0.0;
   out_2960483098895628084[142] = 0.0;
   out_2960483098895628084[143] = 0.0;
   out_2960483098895628084[144] = 0.0;
   out_2960483098895628084[145] = 0.0;
   out_2960483098895628084[146] = 0.0;
   out_2960483098895628084[147] = 0.0;
   out_2960483098895628084[148] = 0.0;
   out_2960483098895628084[149] = 0.0;
   out_2960483098895628084[150] = 0.0;
   out_2960483098895628084[151] = 0.0;
   out_2960483098895628084[152] = 1.0;
   out_2960483098895628084[153] = 0.0;
   out_2960483098895628084[154] = 0.0;
   out_2960483098895628084[155] = 0.0;
   out_2960483098895628084[156] = 0.0;
   out_2960483098895628084[157] = 0.0;
   out_2960483098895628084[158] = 0.0;
   out_2960483098895628084[159] = 0.0;
   out_2960483098895628084[160] = 0.0;
   out_2960483098895628084[161] = 0.0;
   out_2960483098895628084[162] = 0.0;
   out_2960483098895628084[163] = 0.0;
   out_2960483098895628084[164] = 0.0;
   out_2960483098895628084[165] = 0.0;
   out_2960483098895628084[166] = 0.0;
   out_2960483098895628084[167] = 0.0;
   out_2960483098895628084[168] = 0.0;
   out_2960483098895628084[169] = 0.0;
   out_2960483098895628084[170] = 0.0;
   out_2960483098895628084[171] = 1.0;
   out_2960483098895628084[172] = 0.0;
   out_2960483098895628084[173] = 0.0;
   out_2960483098895628084[174] = 0.0;
   out_2960483098895628084[175] = 0.0;
   out_2960483098895628084[176] = 0.0;
   out_2960483098895628084[177] = 0.0;
   out_2960483098895628084[178] = 0.0;
   out_2960483098895628084[179] = 0.0;
   out_2960483098895628084[180] = 0.0;
   out_2960483098895628084[181] = 0.0;
   out_2960483098895628084[182] = 0.0;
   out_2960483098895628084[183] = 0.0;
   out_2960483098895628084[184] = 0.0;
   out_2960483098895628084[185] = 0.0;
   out_2960483098895628084[186] = 0.0;
   out_2960483098895628084[187] = 0.0;
   out_2960483098895628084[188] = 0.0;
   out_2960483098895628084[189] = 0.0;
   out_2960483098895628084[190] = 1.0;
   out_2960483098895628084[191] = 0.0;
   out_2960483098895628084[192] = 0.0;
   out_2960483098895628084[193] = 0.0;
   out_2960483098895628084[194] = 0.0;
   out_2960483098895628084[195] = 0.0;
   out_2960483098895628084[196] = 0.0;
   out_2960483098895628084[197] = 0.0;
   out_2960483098895628084[198] = 0.0;
   out_2960483098895628084[199] = 0.0;
   out_2960483098895628084[200] = 0.0;
   out_2960483098895628084[201] = 0.0;
   out_2960483098895628084[202] = 0.0;
   out_2960483098895628084[203] = 0.0;
   out_2960483098895628084[204] = 0.0;
   out_2960483098895628084[205] = 0.0;
   out_2960483098895628084[206] = 0.0;
   out_2960483098895628084[207] = 0.0;
   out_2960483098895628084[208] = 0.0;
   out_2960483098895628084[209] = 1.0;
   out_2960483098895628084[210] = 0.0;
   out_2960483098895628084[211] = 0.0;
   out_2960483098895628084[212] = 0.0;
   out_2960483098895628084[213] = 0.0;
   out_2960483098895628084[214] = 0.0;
   out_2960483098895628084[215] = 0.0;
   out_2960483098895628084[216] = 0.0;
   out_2960483098895628084[217] = 0.0;
   out_2960483098895628084[218] = 0.0;
   out_2960483098895628084[219] = 0.0;
   out_2960483098895628084[220] = 0.0;
   out_2960483098895628084[221] = 0.0;
   out_2960483098895628084[222] = 0.0;
   out_2960483098895628084[223] = 0.0;
   out_2960483098895628084[224] = 0.0;
   out_2960483098895628084[225] = 0.0;
   out_2960483098895628084[226] = 0.0;
   out_2960483098895628084[227] = 0.0;
   out_2960483098895628084[228] = 1.0;
   out_2960483098895628084[229] = 0.0;
   out_2960483098895628084[230] = 0.0;
   out_2960483098895628084[231] = 0.0;
   out_2960483098895628084[232] = 0.0;
   out_2960483098895628084[233] = 0.0;
   out_2960483098895628084[234] = 0.0;
   out_2960483098895628084[235] = 0.0;
   out_2960483098895628084[236] = 0.0;
   out_2960483098895628084[237] = 0.0;
   out_2960483098895628084[238] = 0.0;
   out_2960483098895628084[239] = 0.0;
   out_2960483098895628084[240] = 0.0;
   out_2960483098895628084[241] = 0.0;
   out_2960483098895628084[242] = 0.0;
   out_2960483098895628084[243] = 0.0;
   out_2960483098895628084[244] = 0.0;
   out_2960483098895628084[245] = 0.0;
   out_2960483098895628084[246] = 0.0;
   out_2960483098895628084[247] = 1.0;
   out_2960483098895628084[248] = 0.0;
   out_2960483098895628084[249] = 0.0;
   out_2960483098895628084[250] = 0.0;
   out_2960483098895628084[251] = 0.0;
   out_2960483098895628084[252] = 0.0;
   out_2960483098895628084[253] = 0.0;
   out_2960483098895628084[254] = 0.0;
   out_2960483098895628084[255] = 0.0;
   out_2960483098895628084[256] = 0.0;
   out_2960483098895628084[257] = 0.0;
   out_2960483098895628084[258] = 0.0;
   out_2960483098895628084[259] = 0.0;
   out_2960483098895628084[260] = 0.0;
   out_2960483098895628084[261] = 0.0;
   out_2960483098895628084[262] = 0.0;
   out_2960483098895628084[263] = 0.0;
   out_2960483098895628084[264] = 0.0;
   out_2960483098895628084[265] = 0.0;
   out_2960483098895628084[266] = 1.0;
   out_2960483098895628084[267] = 0.0;
   out_2960483098895628084[268] = 0.0;
   out_2960483098895628084[269] = 0.0;
   out_2960483098895628084[270] = 0.0;
   out_2960483098895628084[271] = 0.0;
   out_2960483098895628084[272] = 0.0;
   out_2960483098895628084[273] = 0.0;
   out_2960483098895628084[274] = 0.0;
   out_2960483098895628084[275] = 0.0;
   out_2960483098895628084[276] = 0.0;
   out_2960483098895628084[277] = 0.0;
   out_2960483098895628084[278] = 0.0;
   out_2960483098895628084[279] = 0.0;
   out_2960483098895628084[280] = 0.0;
   out_2960483098895628084[281] = 0.0;
   out_2960483098895628084[282] = 0.0;
   out_2960483098895628084[283] = 0.0;
   out_2960483098895628084[284] = 0.0;
   out_2960483098895628084[285] = 1.0;
   out_2960483098895628084[286] = 0.0;
   out_2960483098895628084[287] = 0.0;
   out_2960483098895628084[288] = 0.0;
   out_2960483098895628084[289] = 0.0;
   out_2960483098895628084[290] = 0.0;
   out_2960483098895628084[291] = 0.0;
   out_2960483098895628084[292] = 0.0;
   out_2960483098895628084[293] = 0.0;
   out_2960483098895628084[294] = 0.0;
   out_2960483098895628084[295] = 0.0;
   out_2960483098895628084[296] = 0.0;
   out_2960483098895628084[297] = 0.0;
   out_2960483098895628084[298] = 0.0;
   out_2960483098895628084[299] = 0.0;
   out_2960483098895628084[300] = 0.0;
   out_2960483098895628084[301] = 0.0;
   out_2960483098895628084[302] = 0.0;
   out_2960483098895628084[303] = 0.0;
   out_2960483098895628084[304] = 1.0;
   out_2960483098895628084[305] = 0.0;
   out_2960483098895628084[306] = 0.0;
   out_2960483098895628084[307] = 0.0;
   out_2960483098895628084[308] = 0.0;
   out_2960483098895628084[309] = 0.0;
   out_2960483098895628084[310] = 0.0;
   out_2960483098895628084[311] = 0.0;
   out_2960483098895628084[312] = 0.0;
   out_2960483098895628084[313] = 0.0;
   out_2960483098895628084[314] = 0.0;
   out_2960483098895628084[315] = 0.0;
   out_2960483098895628084[316] = 0.0;
   out_2960483098895628084[317] = 0.0;
   out_2960483098895628084[318] = 0.0;
   out_2960483098895628084[319] = 0.0;
   out_2960483098895628084[320] = 0.0;
   out_2960483098895628084[321] = 0.0;
   out_2960483098895628084[322] = 0.0;
   out_2960483098895628084[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_6109586615606219235) {
   out_6109586615606219235[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_6109586615606219235[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_6109586615606219235[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_6109586615606219235[3] = dt*state[12] + state[3];
   out_6109586615606219235[4] = dt*state[13] + state[4];
   out_6109586615606219235[5] = dt*state[14] + state[5];
   out_6109586615606219235[6] = state[6];
   out_6109586615606219235[7] = state[7];
   out_6109586615606219235[8] = state[8];
   out_6109586615606219235[9] = state[9];
   out_6109586615606219235[10] = state[10];
   out_6109586615606219235[11] = state[11];
   out_6109586615606219235[12] = state[12];
   out_6109586615606219235[13] = state[13];
   out_6109586615606219235[14] = state[14];
   out_6109586615606219235[15] = state[15];
   out_6109586615606219235[16] = state[16];
   out_6109586615606219235[17] = state[17];
}
void F_fun(double *state, double dt, double *out_3005971387171110242) {
   out_3005971387171110242[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3005971387171110242[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3005971387171110242[2] = 0;
   out_3005971387171110242[3] = 0;
   out_3005971387171110242[4] = 0;
   out_3005971387171110242[5] = 0;
   out_3005971387171110242[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3005971387171110242[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3005971387171110242[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3005971387171110242[9] = 0;
   out_3005971387171110242[10] = 0;
   out_3005971387171110242[11] = 0;
   out_3005971387171110242[12] = 0;
   out_3005971387171110242[13] = 0;
   out_3005971387171110242[14] = 0;
   out_3005971387171110242[15] = 0;
   out_3005971387171110242[16] = 0;
   out_3005971387171110242[17] = 0;
   out_3005971387171110242[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3005971387171110242[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3005971387171110242[20] = 0;
   out_3005971387171110242[21] = 0;
   out_3005971387171110242[22] = 0;
   out_3005971387171110242[23] = 0;
   out_3005971387171110242[24] = 0;
   out_3005971387171110242[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3005971387171110242[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3005971387171110242[27] = 0;
   out_3005971387171110242[28] = 0;
   out_3005971387171110242[29] = 0;
   out_3005971387171110242[30] = 0;
   out_3005971387171110242[31] = 0;
   out_3005971387171110242[32] = 0;
   out_3005971387171110242[33] = 0;
   out_3005971387171110242[34] = 0;
   out_3005971387171110242[35] = 0;
   out_3005971387171110242[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3005971387171110242[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3005971387171110242[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3005971387171110242[39] = 0;
   out_3005971387171110242[40] = 0;
   out_3005971387171110242[41] = 0;
   out_3005971387171110242[42] = 0;
   out_3005971387171110242[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3005971387171110242[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3005971387171110242[45] = 0;
   out_3005971387171110242[46] = 0;
   out_3005971387171110242[47] = 0;
   out_3005971387171110242[48] = 0;
   out_3005971387171110242[49] = 0;
   out_3005971387171110242[50] = 0;
   out_3005971387171110242[51] = 0;
   out_3005971387171110242[52] = 0;
   out_3005971387171110242[53] = 0;
   out_3005971387171110242[54] = 0;
   out_3005971387171110242[55] = 0;
   out_3005971387171110242[56] = 0;
   out_3005971387171110242[57] = 1;
   out_3005971387171110242[58] = 0;
   out_3005971387171110242[59] = 0;
   out_3005971387171110242[60] = 0;
   out_3005971387171110242[61] = 0;
   out_3005971387171110242[62] = 0;
   out_3005971387171110242[63] = 0;
   out_3005971387171110242[64] = 0;
   out_3005971387171110242[65] = 0;
   out_3005971387171110242[66] = dt;
   out_3005971387171110242[67] = 0;
   out_3005971387171110242[68] = 0;
   out_3005971387171110242[69] = 0;
   out_3005971387171110242[70] = 0;
   out_3005971387171110242[71] = 0;
   out_3005971387171110242[72] = 0;
   out_3005971387171110242[73] = 0;
   out_3005971387171110242[74] = 0;
   out_3005971387171110242[75] = 0;
   out_3005971387171110242[76] = 1;
   out_3005971387171110242[77] = 0;
   out_3005971387171110242[78] = 0;
   out_3005971387171110242[79] = 0;
   out_3005971387171110242[80] = 0;
   out_3005971387171110242[81] = 0;
   out_3005971387171110242[82] = 0;
   out_3005971387171110242[83] = 0;
   out_3005971387171110242[84] = 0;
   out_3005971387171110242[85] = dt;
   out_3005971387171110242[86] = 0;
   out_3005971387171110242[87] = 0;
   out_3005971387171110242[88] = 0;
   out_3005971387171110242[89] = 0;
   out_3005971387171110242[90] = 0;
   out_3005971387171110242[91] = 0;
   out_3005971387171110242[92] = 0;
   out_3005971387171110242[93] = 0;
   out_3005971387171110242[94] = 0;
   out_3005971387171110242[95] = 1;
   out_3005971387171110242[96] = 0;
   out_3005971387171110242[97] = 0;
   out_3005971387171110242[98] = 0;
   out_3005971387171110242[99] = 0;
   out_3005971387171110242[100] = 0;
   out_3005971387171110242[101] = 0;
   out_3005971387171110242[102] = 0;
   out_3005971387171110242[103] = 0;
   out_3005971387171110242[104] = dt;
   out_3005971387171110242[105] = 0;
   out_3005971387171110242[106] = 0;
   out_3005971387171110242[107] = 0;
   out_3005971387171110242[108] = 0;
   out_3005971387171110242[109] = 0;
   out_3005971387171110242[110] = 0;
   out_3005971387171110242[111] = 0;
   out_3005971387171110242[112] = 0;
   out_3005971387171110242[113] = 0;
   out_3005971387171110242[114] = 1;
   out_3005971387171110242[115] = 0;
   out_3005971387171110242[116] = 0;
   out_3005971387171110242[117] = 0;
   out_3005971387171110242[118] = 0;
   out_3005971387171110242[119] = 0;
   out_3005971387171110242[120] = 0;
   out_3005971387171110242[121] = 0;
   out_3005971387171110242[122] = 0;
   out_3005971387171110242[123] = 0;
   out_3005971387171110242[124] = 0;
   out_3005971387171110242[125] = 0;
   out_3005971387171110242[126] = 0;
   out_3005971387171110242[127] = 0;
   out_3005971387171110242[128] = 0;
   out_3005971387171110242[129] = 0;
   out_3005971387171110242[130] = 0;
   out_3005971387171110242[131] = 0;
   out_3005971387171110242[132] = 0;
   out_3005971387171110242[133] = 1;
   out_3005971387171110242[134] = 0;
   out_3005971387171110242[135] = 0;
   out_3005971387171110242[136] = 0;
   out_3005971387171110242[137] = 0;
   out_3005971387171110242[138] = 0;
   out_3005971387171110242[139] = 0;
   out_3005971387171110242[140] = 0;
   out_3005971387171110242[141] = 0;
   out_3005971387171110242[142] = 0;
   out_3005971387171110242[143] = 0;
   out_3005971387171110242[144] = 0;
   out_3005971387171110242[145] = 0;
   out_3005971387171110242[146] = 0;
   out_3005971387171110242[147] = 0;
   out_3005971387171110242[148] = 0;
   out_3005971387171110242[149] = 0;
   out_3005971387171110242[150] = 0;
   out_3005971387171110242[151] = 0;
   out_3005971387171110242[152] = 1;
   out_3005971387171110242[153] = 0;
   out_3005971387171110242[154] = 0;
   out_3005971387171110242[155] = 0;
   out_3005971387171110242[156] = 0;
   out_3005971387171110242[157] = 0;
   out_3005971387171110242[158] = 0;
   out_3005971387171110242[159] = 0;
   out_3005971387171110242[160] = 0;
   out_3005971387171110242[161] = 0;
   out_3005971387171110242[162] = 0;
   out_3005971387171110242[163] = 0;
   out_3005971387171110242[164] = 0;
   out_3005971387171110242[165] = 0;
   out_3005971387171110242[166] = 0;
   out_3005971387171110242[167] = 0;
   out_3005971387171110242[168] = 0;
   out_3005971387171110242[169] = 0;
   out_3005971387171110242[170] = 0;
   out_3005971387171110242[171] = 1;
   out_3005971387171110242[172] = 0;
   out_3005971387171110242[173] = 0;
   out_3005971387171110242[174] = 0;
   out_3005971387171110242[175] = 0;
   out_3005971387171110242[176] = 0;
   out_3005971387171110242[177] = 0;
   out_3005971387171110242[178] = 0;
   out_3005971387171110242[179] = 0;
   out_3005971387171110242[180] = 0;
   out_3005971387171110242[181] = 0;
   out_3005971387171110242[182] = 0;
   out_3005971387171110242[183] = 0;
   out_3005971387171110242[184] = 0;
   out_3005971387171110242[185] = 0;
   out_3005971387171110242[186] = 0;
   out_3005971387171110242[187] = 0;
   out_3005971387171110242[188] = 0;
   out_3005971387171110242[189] = 0;
   out_3005971387171110242[190] = 1;
   out_3005971387171110242[191] = 0;
   out_3005971387171110242[192] = 0;
   out_3005971387171110242[193] = 0;
   out_3005971387171110242[194] = 0;
   out_3005971387171110242[195] = 0;
   out_3005971387171110242[196] = 0;
   out_3005971387171110242[197] = 0;
   out_3005971387171110242[198] = 0;
   out_3005971387171110242[199] = 0;
   out_3005971387171110242[200] = 0;
   out_3005971387171110242[201] = 0;
   out_3005971387171110242[202] = 0;
   out_3005971387171110242[203] = 0;
   out_3005971387171110242[204] = 0;
   out_3005971387171110242[205] = 0;
   out_3005971387171110242[206] = 0;
   out_3005971387171110242[207] = 0;
   out_3005971387171110242[208] = 0;
   out_3005971387171110242[209] = 1;
   out_3005971387171110242[210] = 0;
   out_3005971387171110242[211] = 0;
   out_3005971387171110242[212] = 0;
   out_3005971387171110242[213] = 0;
   out_3005971387171110242[214] = 0;
   out_3005971387171110242[215] = 0;
   out_3005971387171110242[216] = 0;
   out_3005971387171110242[217] = 0;
   out_3005971387171110242[218] = 0;
   out_3005971387171110242[219] = 0;
   out_3005971387171110242[220] = 0;
   out_3005971387171110242[221] = 0;
   out_3005971387171110242[222] = 0;
   out_3005971387171110242[223] = 0;
   out_3005971387171110242[224] = 0;
   out_3005971387171110242[225] = 0;
   out_3005971387171110242[226] = 0;
   out_3005971387171110242[227] = 0;
   out_3005971387171110242[228] = 1;
   out_3005971387171110242[229] = 0;
   out_3005971387171110242[230] = 0;
   out_3005971387171110242[231] = 0;
   out_3005971387171110242[232] = 0;
   out_3005971387171110242[233] = 0;
   out_3005971387171110242[234] = 0;
   out_3005971387171110242[235] = 0;
   out_3005971387171110242[236] = 0;
   out_3005971387171110242[237] = 0;
   out_3005971387171110242[238] = 0;
   out_3005971387171110242[239] = 0;
   out_3005971387171110242[240] = 0;
   out_3005971387171110242[241] = 0;
   out_3005971387171110242[242] = 0;
   out_3005971387171110242[243] = 0;
   out_3005971387171110242[244] = 0;
   out_3005971387171110242[245] = 0;
   out_3005971387171110242[246] = 0;
   out_3005971387171110242[247] = 1;
   out_3005971387171110242[248] = 0;
   out_3005971387171110242[249] = 0;
   out_3005971387171110242[250] = 0;
   out_3005971387171110242[251] = 0;
   out_3005971387171110242[252] = 0;
   out_3005971387171110242[253] = 0;
   out_3005971387171110242[254] = 0;
   out_3005971387171110242[255] = 0;
   out_3005971387171110242[256] = 0;
   out_3005971387171110242[257] = 0;
   out_3005971387171110242[258] = 0;
   out_3005971387171110242[259] = 0;
   out_3005971387171110242[260] = 0;
   out_3005971387171110242[261] = 0;
   out_3005971387171110242[262] = 0;
   out_3005971387171110242[263] = 0;
   out_3005971387171110242[264] = 0;
   out_3005971387171110242[265] = 0;
   out_3005971387171110242[266] = 1;
   out_3005971387171110242[267] = 0;
   out_3005971387171110242[268] = 0;
   out_3005971387171110242[269] = 0;
   out_3005971387171110242[270] = 0;
   out_3005971387171110242[271] = 0;
   out_3005971387171110242[272] = 0;
   out_3005971387171110242[273] = 0;
   out_3005971387171110242[274] = 0;
   out_3005971387171110242[275] = 0;
   out_3005971387171110242[276] = 0;
   out_3005971387171110242[277] = 0;
   out_3005971387171110242[278] = 0;
   out_3005971387171110242[279] = 0;
   out_3005971387171110242[280] = 0;
   out_3005971387171110242[281] = 0;
   out_3005971387171110242[282] = 0;
   out_3005971387171110242[283] = 0;
   out_3005971387171110242[284] = 0;
   out_3005971387171110242[285] = 1;
   out_3005971387171110242[286] = 0;
   out_3005971387171110242[287] = 0;
   out_3005971387171110242[288] = 0;
   out_3005971387171110242[289] = 0;
   out_3005971387171110242[290] = 0;
   out_3005971387171110242[291] = 0;
   out_3005971387171110242[292] = 0;
   out_3005971387171110242[293] = 0;
   out_3005971387171110242[294] = 0;
   out_3005971387171110242[295] = 0;
   out_3005971387171110242[296] = 0;
   out_3005971387171110242[297] = 0;
   out_3005971387171110242[298] = 0;
   out_3005971387171110242[299] = 0;
   out_3005971387171110242[300] = 0;
   out_3005971387171110242[301] = 0;
   out_3005971387171110242[302] = 0;
   out_3005971387171110242[303] = 0;
   out_3005971387171110242[304] = 1;
   out_3005971387171110242[305] = 0;
   out_3005971387171110242[306] = 0;
   out_3005971387171110242[307] = 0;
   out_3005971387171110242[308] = 0;
   out_3005971387171110242[309] = 0;
   out_3005971387171110242[310] = 0;
   out_3005971387171110242[311] = 0;
   out_3005971387171110242[312] = 0;
   out_3005971387171110242[313] = 0;
   out_3005971387171110242[314] = 0;
   out_3005971387171110242[315] = 0;
   out_3005971387171110242[316] = 0;
   out_3005971387171110242[317] = 0;
   out_3005971387171110242[318] = 0;
   out_3005971387171110242[319] = 0;
   out_3005971387171110242[320] = 0;
   out_3005971387171110242[321] = 0;
   out_3005971387171110242[322] = 0;
   out_3005971387171110242[323] = 1;
}
void h_4(double *state, double *unused, double *out_8555068318404903596) {
   out_8555068318404903596[0] = state[6] + state[9];
   out_8555068318404903596[1] = state[7] + state[10];
   out_8555068318404903596[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_2206322096840915477) {
   out_2206322096840915477[0] = 0;
   out_2206322096840915477[1] = 0;
   out_2206322096840915477[2] = 0;
   out_2206322096840915477[3] = 0;
   out_2206322096840915477[4] = 0;
   out_2206322096840915477[5] = 0;
   out_2206322096840915477[6] = 1;
   out_2206322096840915477[7] = 0;
   out_2206322096840915477[8] = 0;
   out_2206322096840915477[9] = 1;
   out_2206322096840915477[10] = 0;
   out_2206322096840915477[11] = 0;
   out_2206322096840915477[12] = 0;
   out_2206322096840915477[13] = 0;
   out_2206322096840915477[14] = 0;
   out_2206322096840915477[15] = 0;
   out_2206322096840915477[16] = 0;
   out_2206322096840915477[17] = 0;
   out_2206322096840915477[18] = 0;
   out_2206322096840915477[19] = 0;
   out_2206322096840915477[20] = 0;
   out_2206322096840915477[21] = 0;
   out_2206322096840915477[22] = 0;
   out_2206322096840915477[23] = 0;
   out_2206322096840915477[24] = 0;
   out_2206322096840915477[25] = 1;
   out_2206322096840915477[26] = 0;
   out_2206322096840915477[27] = 0;
   out_2206322096840915477[28] = 1;
   out_2206322096840915477[29] = 0;
   out_2206322096840915477[30] = 0;
   out_2206322096840915477[31] = 0;
   out_2206322096840915477[32] = 0;
   out_2206322096840915477[33] = 0;
   out_2206322096840915477[34] = 0;
   out_2206322096840915477[35] = 0;
   out_2206322096840915477[36] = 0;
   out_2206322096840915477[37] = 0;
   out_2206322096840915477[38] = 0;
   out_2206322096840915477[39] = 0;
   out_2206322096840915477[40] = 0;
   out_2206322096840915477[41] = 0;
   out_2206322096840915477[42] = 0;
   out_2206322096840915477[43] = 0;
   out_2206322096840915477[44] = 1;
   out_2206322096840915477[45] = 0;
   out_2206322096840915477[46] = 0;
   out_2206322096840915477[47] = 1;
   out_2206322096840915477[48] = 0;
   out_2206322096840915477[49] = 0;
   out_2206322096840915477[50] = 0;
   out_2206322096840915477[51] = 0;
   out_2206322096840915477[52] = 0;
   out_2206322096840915477[53] = 0;
}
void h_10(double *state, double *unused, double *out_3926024267674485452) {
   out_3926024267674485452[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_3926024267674485452[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_3926024267674485452[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_3320228119013668997) {
   out_3320228119013668997[0] = 0;
   out_3320228119013668997[1] = 9.8100000000000005*cos(state[1]);
   out_3320228119013668997[2] = 0;
   out_3320228119013668997[3] = 0;
   out_3320228119013668997[4] = -state[8];
   out_3320228119013668997[5] = state[7];
   out_3320228119013668997[6] = 0;
   out_3320228119013668997[7] = state[5];
   out_3320228119013668997[8] = -state[4];
   out_3320228119013668997[9] = 0;
   out_3320228119013668997[10] = 0;
   out_3320228119013668997[11] = 0;
   out_3320228119013668997[12] = 1;
   out_3320228119013668997[13] = 0;
   out_3320228119013668997[14] = 0;
   out_3320228119013668997[15] = 1;
   out_3320228119013668997[16] = 0;
   out_3320228119013668997[17] = 0;
   out_3320228119013668997[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_3320228119013668997[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_3320228119013668997[20] = 0;
   out_3320228119013668997[21] = state[8];
   out_3320228119013668997[22] = 0;
   out_3320228119013668997[23] = -state[6];
   out_3320228119013668997[24] = -state[5];
   out_3320228119013668997[25] = 0;
   out_3320228119013668997[26] = state[3];
   out_3320228119013668997[27] = 0;
   out_3320228119013668997[28] = 0;
   out_3320228119013668997[29] = 0;
   out_3320228119013668997[30] = 0;
   out_3320228119013668997[31] = 1;
   out_3320228119013668997[32] = 0;
   out_3320228119013668997[33] = 0;
   out_3320228119013668997[34] = 1;
   out_3320228119013668997[35] = 0;
   out_3320228119013668997[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_3320228119013668997[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_3320228119013668997[38] = 0;
   out_3320228119013668997[39] = -state[7];
   out_3320228119013668997[40] = state[6];
   out_3320228119013668997[41] = 0;
   out_3320228119013668997[42] = state[4];
   out_3320228119013668997[43] = -state[3];
   out_3320228119013668997[44] = 0;
   out_3320228119013668997[45] = 0;
   out_3320228119013668997[46] = 0;
   out_3320228119013668997[47] = 0;
   out_3320228119013668997[48] = 0;
   out_3320228119013668997[49] = 0;
   out_3320228119013668997[50] = 1;
   out_3320228119013668997[51] = 0;
   out_3320228119013668997[52] = 0;
   out_3320228119013668997[53] = 1;
}
void h_13(double *state, double *unused, double *out_7226674194180226055) {
   out_7226674194180226055[0] = state[3];
   out_7226674194180226055[1] = state[4];
   out_7226674194180226055[2] = state[5];
}
void H_13(double *state, double *unused, double *out_6040077560143439501) {
   out_6040077560143439501[0] = 0;
   out_6040077560143439501[1] = 0;
   out_6040077560143439501[2] = 0;
   out_6040077560143439501[3] = 1;
   out_6040077560143439501[4] = 0;
   out_6040077560143439501[5] = 0;
   out_6040077560143439501[6] = 0;
   out_6040077560143439501[7] = 0;
   out_6040077560143439501[8] = 0;
   out_6040077560143439501[9] = 0;
   out_6040077560143439501[10] = 0;
   out_6040077560143439501[11] = 0;
   out_6040077560143439501[12] = 0;
   out_6040077560143439501[13] = 0;
   out_6040077560143439501[14] = 0;
   out_6040077560143439501[15] = 0;
   out_6040077560143439501[16] = 0;
   out_6040077560143439501[17] = 0;
   out_6040077560143439501[18] = 0;
   out_6040077560143439501[19] = 0;
   out_6040077560143439501[20] = 0;
   out_6040077560143439501[21] = 0;
   out_6040077560143439501[22] = 1;
   out_6040077560143439501[23] = 0;
   out_6040077560143439501[24] = 0;
   out_6040077560143439501[25] = 0;
   out_6040077560143439501[26] = 0;
   out_6040077560143439501[27] = 0;
   out_6040077560143439501[28] = 0;
   out_6040077560143439501[29] = 0;
   out_6040077560143439501[30] = 0;
   out_6040077560143439501[31] = 0;
   out_6040077560143439501[32] = 0;
   out_6040077560143439501[33] = 0;
   out_6040077560143439501[34] = 0;
   out_6040077560143439501[35] = 0;
   out_6040077560143439501[36] = 0;
   out_6040077560143439501[37] = 0;
   out_6040077560143439501[38] = 0;
   out_6040077560143439501[39] = 0;
   out_6040077560143439501[40] = 0;
   out_6040077560143439501[41] = 1;
   out_6040077560143439501[42] = 0;
   out_6040077560143439501[43] = 0;
   out_6040077560143439501[44] = 0;
   out_6040077560143439501[45] = 0;
   out_6040077560143439501[46] = 0;
   out_6040077560143439501[47] = 0;
   out_6040077560143439501[48] = 0;
   out_6040077560143439501[49] = 0;
   out_6040077560143439501[50] = 0;
   out_6040077560143439501[51] = 0;
   out_6040077560143439501[52] = 0;
   out_6040077560143439501[53] = 0;
}
void h_14(double *state, double *unused, double *out_6511557007088322924) {
   out_6511557007088322924[0] = state[6];
   out_6511557007088322924[1] = state[7];
   out_6511557007088322924[2] = state[8];
}
void H_14(double *state, double *unused, double *out_5289110529136287773) {
   out_5289110529136287773[0] = 0;
   out_5289110529136287773[1] = 0;
   out_5289110529136287773[2] = 0;
   out_5289110529136287773[3] = 0;
   out_5289110529136287773[4] = 0;
   out_5289110529136287773[5] = 0;
   out_5289110529136287773[6] = 1;
   out_5289110529136287773[7] = 0;
   out_5289110529136287773[8] = 0;
   out_5289110529136287773[9] = 0;
   out_5289110529136287773[10] = 0;
   out_5289110529136287773[11] = 0;
   out_5289110529136287773[12] = 0;
   out_5289110529136287773[13] = 0;
   out_5289110529136287773[14] = 0;
   out_5289110529136287773[15] = 0;
   out_5289110529136287773[16] = 0;
   out_5289110529136287773[17] = 0;
   out_5289110529136287773[18] = 0;
   out_5289110529136287773[19] = 0;
   out_5289110529136287773[20] = 0;
   out_5289110529136287773[21] = 0;
   out_5289110529136287773[22] = 0;
   out_5289110529136287773[23] = 0;
   out_5289110529136287773[24] = 0;
   out_5289110529136287773[25] = 1;
   out_5289110529136287773[26] = 0;
   out_5289110529136287773[27] = 0;
   out_5289110529136287773[28] = 0;
   out_5289110529136287773[29] = 0;
   out_5289110529136287773[30] = 0;
   out_5289110529136287773[31] = 0;
   out_5289110529136287773[32] = 0;
   out_5289110529136287773[33] = 0;
   out_5289110529136287773[34] = 0;
   out_5289110529136287773[35] = 0;
   out_5289110529136287773[36] = 0;
   out_5289110529136287773[37] = 0;
   out_5289110529136287773[38] = 0;
   out_5289110529136287773[39] = 0;
   out_5289110529136287773[40] = 0;
   out_5289110529136287773[41] = 0;
   out_5289110529136287773[42] = 0;
   out_5289110529136287773[43] = 0;
   out_5289110529136287773[44] = 1;
   out_5289110529136287773[45] = 0;
   out_5289110529136287773[46] = 0;
   out_5289110529136287773[47] = 0;
   out_5289110529136287773[48] = 0;
   out_5289110529136287773[49] = 0;
   out_5289110529136287773[50] = 0;
   out_5289110529136287773[51] = 0;
   out_5289110529136287773[52] = 0;
   out_5289110529136287773[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_5289520161060537688) {
  err_fun(nom_x, delta_x, out_5289520161060537688);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_8611651352423676881) {
  inv_err_fun(nom_x, true_x, out_8611651352423676881);
}
void pose_H_mod_fun(double *state, double *out_2960483098895628084) {
  H_mod_fun(state, out_2960483098895628084);
}
void pose_f_fun(double *state, double dt, double *out_6109586615606219235) {
  f_fun(state,  dt, out_6109586615606219235);
}
void pose_F_fun(double *state, double dt, double *out_3005971387171110242) {
  F_fun(state,  dt, out_3005971387171110242);
}
void pose_h_4(double *state, double *unused, double *out_8555068318404903596) {
  h_4(state, unused, out_8555068318404903596);
}
void pose_H_4(double *state, double *unused, double *out_2206322096840915477) {
  H_4(state, unused, out_2206322096840915477);
}
void pose_h_10(double *state, double *unused, double *out_3926024267674485452) {
  h_10(state, unused, out_3926024267674485452);
}
void pose_H_10(double *state, double *unused, double *out_3320228119013668997) {
  H_10(state, unused, out_3320228119013668997);
}
void pose_h_13(double *state, double *unused, double *out_7226674194180226055) {
  h_13(state, unused, out_7226674194180226055);
}
void pose_H_13(double *state, double *unused, double *out_6040077560143439501) {
  H_13(state, unused, out_6040077560143439501);
}
void pose_h_14(double *state, double *unused, double *out_6511557007088322924) {
  h_14(state, unused, out_6511557007088322924);
}
void pose_H_14(double *state, double *unused, double *out_5289110529136287773) {
  H_14(state, unused, out_5289110529136287773);
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
