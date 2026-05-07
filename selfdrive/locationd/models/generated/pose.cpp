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
void err_fun(double *nom_x, double *delta_x, double *out_6395110133292861521) {
   out_6395110133292861521[0] = delta_x[0] + nom_x[0];
   out_6395110133292861521[1] = delta_x[1] + nom_x[1];
   out_6395110133292861521[2] = delta_x[2] + nom_x[2];
   out_6395110133292861521[3] = delta_x[3] + nom_x[3];
   out_6395110133292861521[4] = delta_x[4] + nom_x[4];
   out_6395110133292861521[5] = delta_x[5] + nom_x[5];
   out_6395110133292861521[6] = delta_x[6] + nom_x[6];
   out_6395110133292861521[7] = delta_x[7] + nom_x[7];
   out_6395110133292861521[8] = delta_x[8] + nom_x[8];
   out_6395110133292861521[9] = delta_x[9] + nom_x[9];
   out_6395110133292861521[10] = delta_x[10] + nom_x[10];
   out_6395110133292861521[11] = delta_x[11] + nom_x[11];
   out_6395110133292861521[12] = delta_x[12] + nom_x[12];
   out_6395110133292861521[13] = delta_x[13] + nom_x[13];
   out_6395110133292861521[14] = delta_x[14] + nom_x[14];
   out_6395110133292861521[15] = delta_x[15] + nom_x[15];
   out_6395110133292861521[16] = delta_x[16] + nom_x[16];
   out_6395110133292861521[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5574902989131587335) {
   out_5574902989131587335[0] = -nom_x[0] + true_x[0];
   out_5574902989131587335[1] = -nom_x[1] + true_x[1];
   out_5574902989131587335[2] = -nom_x[2] + true_x[2];
   out_5574902989131587335[3] = -nom_x[3] + true_x[3];
   out_5574902989131587335[4] = -nom_x[4] + true_x[4];
   out_5574902989131587335[5] = -nom_x[5] + true_x[5];
   out_5574902989131587335[6] = -nom_x[6] + true_x[6];
   out_5574902989131587335[7] = -nom_x[7] + true_x[7];
   out_5574902989131587335[8] = -nom_x[8] + true_x[8];
   out_5574902989131587335[9] = -nom_x[9] + true_x[9];
   out_5574902989131587335[10] = -nom_x[10] + true_x[10];
   out_5574902989131587335[11] = -nom_x[11] + true_x[11];
   out_5574902989131587335[12] = -nom_x[12] + true_x[12];
   out_5574902989131587335[13] = -nom_x[13] + true_x[13];
   out_5574902989131587335[14] = -nom_x[14] + true_x[14];
   out_5574902989131587335[15] = -nom_x[15] + true_x[15];
   out_5574902989131587335[16] = -nom_x[16] + true_x[16];
   out_5574902989131587335[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_6860086072787592800) {
   out_6860086072787592800[0] = 1.0;
   out_6860086072787592800[1] = 0.0;
   out_6860086072787592800[2] = 0.0;
   out_6860086072787592800[3] = 0.0;
   out_6860086072787592800[4] = 0.0;
   out_6860086072787592800[5] = 0.0;
   out_6860086072787592800[6] = 0.0;
   out_6860086072787592800[7] = 0.0;
   out_6860086072787592800[8] = 0.0;
   out_6860086072787592800[9] = 0.0;
   out_6860086072787592800[10] = 0.0;
   out_6860086072787592800[11] = 0.0;
   out_6860086072787592800[12] = 0.0;
   out_6860086072787592800[13] = 0.0;
   out_6860086072787592800[14] = 0.0;
   out_6860086072787592800[15] = 0.0;
   out_6860086072787592800[16] = 0.0;
   out_6860086072787592800[17] = 0.0;
   out_6860086072787592800[18] = 0.0;
   out_6860086072787592800[19] = 1.0;
   out_6860086072787592800[20] = 0.0;
   out_6860086072787592800[21] = 0.0;
   out_6860086072787592800[22] = 0.0;
   out_6860086072787592800[23] = 0.0;
   out_6860086072787592800[24] = 0.0;
   out_6860086072787592800[25] = 0.0;
   out_6860086072787592800[26] = 0.0;
   out_6860086072787592800[27] = 0.0;
   out_6860086072787592800[28] = 0.0;
   out_6860086072787592800[29] = 0.0;
   out_6860086072787592800[30] = 0.0;
   out_6860086072787592800[31] = 0.0;
   out_6860086072787592800[32] = 0.0;
   out_6860086072787592800[33] = 0.0;
   out_6860086072787592800[34] = 0.0;
   out_6860086072787592800[35] = 0.0;
   out_6860086072787592800[36] = 0.0;
   out_6860086072787592800[37] = 0.0;
   out_6860086072787592800[38] = 1.0;
   out_6860086072787592800[39] = 0.0;
   out_6860086072787592800[40] = 0.0;
   out_6860086072787592800[41] = 0.0;
   out_6860086072787592800[42] = 0.0;
   out_6860086072787592800[43] = 0.0;
   out_6860086072787592800[44] = 0.0;
   out_6860086072787592800[45] = 0.0;
   out_6860086072787592800[46] = 0.0;
   out_6860086072787592800[47] = 0.0;
   out_6860086072787592800[48] = 0.0;
   out_6860086072787592800[49] = 0.0;
   out_6860086072787592800[50] = 0.0;
   out_6860086072787592800[51] = 0.0;
   out_6860086072787592800[52] = 0.0;
   out_6860086072787592800[53] = 0.0;
   out_6860086072787592800[54] = 0.0;
   out_6860086072787592800[55] = 0.0;
   out_6860086072787592800[56] = 0.0;
   out_6860086072787592800[57] = 1.0;
   out_6860086072787592800[58] = 0.0;
   out_6860086072787592800[59] = 0.0;
   out_6860086072787592800[60] = 0.0;
   out_6860086072787592800[61] = 0.0;
   out_6860086072787592800[62] = 0.0;
   out_6860086072787592800[63] = 0.0;
   out_6860086072787592800[64] = 0.0;
   out_6860086072787592800[65] = 0.0;
   out_6860086072787592800[66] = 0.0;
   out_6860086072787592800[67] = 0.0;
   out_6860086072787592800[68] = 0.0;
   out_6860086072787592800[69] = 0.0;
   out_6860086072787592800[70] = 0.0;
   out_6860086072787592800[71] = 0.0;
   out_6860086072787592800[72] = 0.0;
   out_6860086072787592800[73] = 0.0;
   out_6860086072787592800[74] = 0.0;
   out_6860086072787592800[75] = 0.0;
   out_6860086072787592800[76] = 1.0;
   out_6860086072787592800[77] = 0.0;
   out_6860086072787592800[78] = 0.0;
   out_6860086072787592800[79] = 0.0;
   out_6860086072787592800[80] = 0.0;
   out_6860086072787592800[81] = 0.0;
   out_6860086072787592800[82] = 0.0;
   out_6860086072787592800[83] = 0.0;
   out_6860086072787592800[84] = 0.0;
   out_6860086072787592800[85] = 0.0;
   out_6860086072787592800[86] = 0.0;
   out_6860086072787592800[87] = 0.0;
   out_6860086072787592800[88] = 0.0;
   out_6860086072787592800[89] = 0.0;
   out_6860086072787592800[90] = 0.0;
   out_6860086072787592800[91] = 0.0;
   out_6860086072787592800[92] = 0.0;
   out_6860086072787592800[93] = 0.0;
   out_6860086072787592800[94] = 0.0;
   out_6860086072787592800[95] = 1.0;
   out_6860086072787592800[96] = 0.0;
   out_6860086072787592800[97] = 0.0;
   out_6860086072787592800[98] = 0.0;
   out_6860086072787592800[99] = 0.0;
   out_6860086072787592800[100] = 0.0;
   out_6860086072787592800[101] = 0.0;
   out_6860086072787592800[102] = 0.0;
   out_6860086072787592800[103] = 0.0;
   out_6860086072787592800[104] = 0.0;
   out_6860086072787592800[105] = 0.0;
   out_6860086072787592800[106] = 0.0;
   out_6860086072787592800[107] = 0.0;
   out_6860086072787592800[108] = 0.0;
   out_6860086072787592800[109] = 0.0;
   out_6860086072787592800[110] = 0.0;
   out_6860086072787592800[111] = 0.0;
   out_6860086072787592800[112] = 0.0;
   out_6860086072787592800[113] = 0.0;
   out_6860086072787592800[114] = 1.0;
   out_6860086072787592800[115] = 0.0;
   out_6860086072787592800[116] = 0.0;
   out_6860086072787592800[117] = 0.0;
   out_6860086072787592800[118] = 0.0;
   out_6860086072787592800[119] = 0.0;
   out_6860086072787592800[120] = 0.0;
   out_6860086072787592800[121] = 0.0;
   out_6860086072787592800[122] = 0.0;
   out_6860086072787592800[123] = 0.0;
   out_6860086072787592800[124] = 0.0;
   out_6860086072787592800[125] = 0.0;
   out_6860086072787592800[126] = 0.0;
   out_6860086072787592800[127] = 0.0;
   out_6860086072787592800[128] = 0.0;
   out_6860086072787592800[129] = 0.0;
   out_6860086072787592800[130] = 0.0;
   out_6860086072787592800[131] = 0.0;
   out_6860086072787592800[132] = 0.0;
   out_6860086072787592800[133] = 1.0;
   out_6860086072787592800[134] = 0.0;
   out_6860086072787592800[135] = 0.0;
   out_6860086072787592800[136] = 0.0;
   out_6860086072787592800[137] = 0.0;
   out_6860086072787592800[138] = 0.0;
   out_6860086072787592800[139] = 0.0;
   out_6860086072787592800[140] = 0.0;
   out_6860086072787592800[141] = 0.0;
   out_6860086072787592800[142] = 0.0;
   out_6860086072787592800[143] = 0.0;
   out_6860086072787592800[144] = 0.0;
   out_6860086072787592800[145] = 0.0;
   out_6860086072787592800[146] = 0.0;
   out_6860086072787592800[147] = 0.0;
   out_6860086072787592800[148] = 0.0;
   out_6860086072787592800[149] = 0.0;
   out_6860086072787592800[150] = 0.0;
   out_6860086072787592800[151] = 0.0;
   out_6860086072787592800[152] = 1.0;
   out_6860086072787592800[153] = 0.0;
   out_6860086072787592800[154] = 0.0;
   out_6860086072787592800[155] = 0.0;
   out_6860086072787592800[156] = 0.0;
   out_6860086072787592800[157] = 0.0;
   out_6860086072787592800[158] = 0.0;
   out_6860086072787592800[159] = 0.0;
   out_6860086072787592800[160] = 0.0;
   out_6860086072787592800[161] = 0.0;
   out_6860086072787592800[162] = 0.0;
   out_6860086072787592800[163] = 0.0;
   out_6860086072787592800[164] = 0.0;
   out_6860086072787592800[165] = 0.0;
   out_6860086072787592800[166] = 0.0;
   out_6860086072787592800[167] = 0.0;
   out_6860086072787592800[168] = 0.0;
   out_6860086072787592800[169] = 0.0;
   out_6860086072787592800[170] = 0.0;
   out_6860086072787592800[171] = 1.0;
   out_6860086072787592800[172] = 0.0;
   out_6860086072787592800[173] = 0.0;
   out_6860086072787592800[174] = 0.0;
   out_6860086072787592800[175] = 0.0;
   out_6860086072787592800[176] = 0.0;
   out_6860086072787592800[177] = 0.0;
   out_6860086072787592800[178] = 0.0;
   out_6860086072787592800[179] = 0.0;
   out_6860086072787592800[180] = 0.0;
   out_6860086072787592800[181] = 0.0;
   out_6860086072787592800[182] = 0.0;
   out_6860086072787592800[183] = 0.0;
   out_6860086072787592800[184] = 0.0;
   out_6860086072787592800[185] = 0.0;
   out_6860086072787592800[186] = 0.0;
   out_6860086072787592800[187] = 0.0;
   out_6860086072787592800[188] = 0.0;
   out_6860086072787592800[189] = 0.0;
   out_6860086072787592800[190] = 1.0;
   out_6860086072787592800[191] = 0.0;
   out_6860086072787592800[192] = 0.0;
   out_6860086072787592800[193] = 0.0;
   out_6860086072787592800[194] = 0.0;
   out_6860086072787592800[195] = 0.0;
   out_6860086072787592800[196] = 0.0;
   out_6860086072787592800[197] = 0.0;
   out_6860086072787592800[198] = 0.0;
   out_6860086072787592800[199] = 0.0;
   out_6860086072787592800[200] = 0.0;
   out_6860086072787592800[201] = 0.0;
   out_6860086072787592800[202] = 0.0;
   out_6860086072787592800[203] = 0.0;
   out_6860086072787592800[204] = 0.0;
   out_6860086072787592800[205] = 0.0;
   out_6860086072787592800[206] = 0.0;
   out_6860086072787592800[207] = 0.0;
   out_6860086072787592800[208] = 0.0;
   out_6860086072787592800[209] = 1.0;
   out_6860086072787592800[210] = 0.0;
   out_6860086072787592800[211] = 0.0;
   out_6860086072787592800[212] = 0.0;
   out_6860086072787592800[213] = 0.0;
   out_6860086072787592800[214] = 0.0;
   out_6860086072787592800[215] = 0.0;
   out_6860086072787592800[216] = 0.0;
   out_6860086072787592800[217] = 0.0;
   out_6860086072787592800[218] = 0.0;
   out_6860086072787592800[219] = 0.0;
   out_6860086072787592800[220] = 0.0;
   out_6860086072787592800[221] = 0.0;
   out_6860086072787592800[222] = 0.0;
   out_6860086072787592800[223] = 0.0;
   out_6860086072787592800[224] = 0.0;
   out_6860086072787592800[225] = 0.0;
   out_6860086072787592800[226] = 0.0;
   out_6860086072787592800[227] = 0.0;
   out_6860086072787592800[228] = 1.0;
   out_6860086072787592800[229] = 0.0;
   out_6860086072787592800[230] = 0.0;
   out_6860086072787592800[231] = 0.0;
   out_6860086072787592800[232] = 0.0;
   out_6860086072787592800[233] = 0.0;
   out_6860086072787592800[234] = 0.0;
   out_6860086072787592800[235] = 0.0;
   out_6860086072787592800[236] = 0.0;
   out_6860086072787592800[237] = 0.0;
   out_6860086072787592800[238] = 0.0;
   out_6860086072787592800[239] = 0.0;
   out_6860086072787592800[240] = 0.0;
   out_6860086072787592800[241] = 0.0;
   out_6860086072787592800[242] = 0.0;
   out_6860086072787592800[243] = 0.0;
   out_6860086072787592800[244] = 0.0;
   out_6860086072787592800[245] = 0.0;
   out_6860086072787592800[246] = 0.0;
   out_6860086072787592800[247] = 1.0;
   out_6860086072787592800[248] = 0.0;
   out_6860086072787592800[249] = 0.0;
   out_6860086072787592800[250] = 0.0;
   out_6860086072787592800[251] = 0.0;
   out_6860086072787592800[252] = 0.0;
   out_6860086072787592800[253] = 0.0;
   out_6860086072787592800[254] = 0.0;
   out_6860086072787592800[255] = 0.0;
   out_6860086072787592800[256] = 0.0;
   out_6860086072787592800[257] = 0.0;
   out_6860086072787592800[258] = 0.0;
   out_6860086072787592800[259] = 0.0;
   out_6860086072787592800[260] = 0.0;
   out_6860086072787592800[261] = 0.0;
   out_6860086072787592800[262] = 0.0;
   out_6860086072787592800[263] = 0.0;
   out_6860086072787592800[264] = 0.0;
   out_6860086072787592800[265] = 0.0;
   out_6860086072787592800[266] = 1.0;
   out_6860086072787592800[267] = 0.0;
   out_6860086072787592800[268] = 0.0;
   out_6860086072787592800[269] = 0.0;
   out_6860086072787592800[270] = 0.0;
   out_6860086072787592800[271] = 0.0;
   out_6860086072787592800[272] = 0.0;
   out_6860086072787592800[273] = 0.0;
   out_6860086072787592800[274] = 0.0;
   out_6860086072787592800[275] = 0.0;
   out_6860086072787592800[276] = 0.0;
   out_6860086072787592800[277] = 0.0;
   out_6860086072787592800[278] = 0.0;
   out_6860086072787592800[279] = 0.0;
   out_6860086072787592800[280] = 0.0;
   out_6860086072787592800[281] = 0.0;
   out_6860086072787592800[282] = 0.0;
   out_6860086072787592800[283] = 0.0;
   out_6860086072787592800[284] = 0.0;
   out_6860086072787592800[285] = 1.0;
   out_6860086072787592800[286] = 0.0;
   out_6860086072787592800[287] = 0.0;
   out_6860086072787592800[288] = 0.0;
   out_6860086072787592800[289] = 0.0;
   out_6860086072787592800[290] = 0.0;
   out_6860086072787592800[291] = 0.0;
   out_6860086072787592800[292] = 0.0;
   out_6860086072787592800[293] = 0.0;
   out_6860086072787592800[294] = 0.0;
   out_6860086072787592800[295] = 0.0;
   out_6860086072787592800[296] = 0.0;
   out_6860086072787592800[297] = 0.0;
   out_6860086072787592800[298] = 0.0;
   out_6860086072787592800[299] = 0.0;
   out_6860086072787592800[300] = 0.0;
   out_6860086072787592800[301] = 0.0;
   out_6860086072787592800[302] = 0.0;
   out_6860086072787592800[303] = 0.0;
   out_6860086072787592800[304] = 1.0;
   out_6860086072787592800[305] = 0.0;
   out_6860086072787592800[306] = 0.0;
   out_6860086072787592800[307] = 0.0;
   out_6860086072787592800[308] = 0.0;
   out_6860086072787592800[309] = 0.0;
   out_6860086072787592800[310] = 0.0;
   out_6860086072787592800[311] = 0.0;
   out_6860086072787592800[312] = 0.0;
   out_6860086072787592800[313] = 0.0;
   out_6860086072787592800[314] = 0.0;
   out_6860086072787592800[315] = 0.0;
   out_6860086072787592800[316] = 0.0;
   out_6860086072787592800[317] = 0.0;
   out_6860086072787592800[318] = 0.0;
   out_6860086072787592800[319] = 0.0;
   out_6860086072787592800[320] = 0.0;
   out_6860086072787592800[321] = 0.0;
   out_6860086072787592800[322] = 0.0;
   out_6860086072787592800[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_6157473931416548839) {
   out_6157473931416548839[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_6157473931416548839[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_6157473931416548839[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_6157473931416548839[3] = dt*state[12] + state[3];
   out_6157473931416548839[4] = dt*state[13] + state[4];
   out_6157473931416548839[5] = dt*state[14] + state[5];
   out_6157473931416548839[6] = state[6];
   out_6157473931416548839[7] = state[7];
   out_6157473931416548839[8] = state[8];
   out_6157473931416548839[9] = state[9];
   out_6157473931416548839[10] = state[10];
   out_6157473931416548839[11] = state[11];
   out_6157473931416548839[12] = state[12];
   out_6157473931416548839[13] = state[13];
   out_6157473931416548839[14] = state[14];
   out_6157473931416548839[15] = state[15];
   out_6157473931416548839[16] = state[16];
   out_6157473931416548839[17] = state[17];
}
void F_fun(double *state, double dt, double *out_2563232569638129684) {
   out_2563232569638129684[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2563232569638129684[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2563232569638129684[2] = 0;
   out_2563232569638129684[3] = 0;
   out_2563232569638129684[4] = 0;
   out_2563232569638129684[5] = 0;
   out_2563232569638129684[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2563232569638129684[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2563232569638129684[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2563232569638129684[9] = 0;
   out_2563232569638129684[10] = 0;
   out_2563232569638129684[11] = 0;
   out_2563232569638129684[12] = 0;
   out_2563232569638129684[13] = 0;
   out_2563232569638129684[14] = 0;
   out_2563232569638129684[15] = 0;
   out_2563232569638129684[16] = 0;
   out_2563232569638129684[17] = 0;
   out_2563232569638129684[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2563232569638129684[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2563232569638129684[20] = 0;
   out_2563232569638129684[21] = 0;
   out_2563232569638129684[22] = 0;
   out_2563232569638129684[23] = 0;
   out_2563232569638129684[24] = 0;
   out_2563232569638129684[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2563232569638129684[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2563232569638129684[27] = 0;
   out_2563232569638129684[28] = 0;
   out_2563232569638129684[29] = 0;
   out_2563232569638129684[30] = 0;
   out_2563232569638129684[31] = 0;
   out_2563232569638129684[32] = 0;
   out_2563232569638129684[33] = 0;
   out_2563232569638129684[34] = 0;
   out_2563232569638129684[35] = 0;
   out_2563232569638129684[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2563232569638129684[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2563232569638129684[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2563232569638129684[39] = 0;
   out_2563232569638129684[40] = 0;
   out_2563232569638129684[41] = 0;
   out_2563232569638129684[42] = 0;
   out_2563232569638129684[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2563232569638129684[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2563232569638129684[45] = 0;
   out_2563232569638129684[46] = 0;
   out_2563232569638129684[47] = 0;
   out_2563232569638129684[48] = 0;
   out_2563232569638129684[49] = 0;
   out_2563232569638129684[50] = 0;
   out_2563232569638129684[51] = 0;
   out_2563232569638129684[52] = 0;
   out_2563232569638129684[53] = 0;
   out_2563232569638129684[54] = 0;
   out_2563232569638129684[55] = 0;
   out_2563232569638129684[56] = 0;
   out_2563232569638129684[57] = 1;
   out_2563232569638129684[58] = 0;
   out_2563232569638129684[59] = 0;
   out_2563232569638129684[60] = 0;
   out_2563232569638129684[61] = 0;
   out_2563232569638129684[62] = 0;
   out_2563232569638129684[63] = 0;
   out_2563232569638129684[64] = 0;
   out_2563232569638129684[65] = 0;
   out_2563232569638129684[66] = dt;
   out_2563232569638129684[67] = 0;
   out_2563232569638129684[68] = 0;
   out_2563232569638129684[69] = 0;
   out_2563232569638129684[70] = 0;
   out_2563232569638129684[71] = 0;
   out_2563232569638129684[72] = 0;
   out_2563232569638129684[73] = 0;
   out_2563232569638129684[74] = 0;
   out_2563232569638129684[75] = 0;
   out_2563232569638129684[76] = 1;
   out_2563232569638129684[77] = 0;
   out_2563232569638129684[78] = 0;
   out_2563232569638129684[79] = 0;
   out_2563232569638129684[80] = 0;
   out_2563232569638129684[81] = 0;
   out_2563232569638129684[82] = 0;
   out_2563232569638129684[83] = 0;
   out_2563232569638129684[84] = 0;
   out_2563232569638129684[85] = dt;
   out_2563232569638129684[86] = 0;
   out_2563232569638129684[87] = 0;
   out_2563232569638129684[88] = 0;
   out_2563232569638129684[89] = 0;
   out_2563232569638129684[90] = 0;
   out_2563232569638129684[91] = 0;
   out_2563232569638129684[92] = 0;
   out_2563232569638129684[93] = 0;
   out_2563232569638129684[94] = 0;
   out_2563232569638129684[95] = 1;
   out_2563232569638129684[96] = 0;
   out_2563232569638129684[97] = 0;
   out_2563232569638129684[98] = 0;
   out_2563232569638129684[99] = 0;
   out_2563232569638129684[100] = 0;
   out_2563232569638129684[101] = 0;
   out_2563232569638129684[102] = 0;
   out_2563232569638129684[103] = 0;
   out_2563232569638129684[104] = dt;
   out_2563232569638129684[105] = 0;
   out_2563232569638129684[106] = 0;
   out_2563232569638129684[107] = 0;
   out_2563232569638129684[108] = 0;
   out_2563232569638129684[109] = 0;
   out_2563232569638129684[110] = 0;
   out_2563232569638129684[111] = 0;
   out_2563232569638129684[112] = 0;
   out_2563232569638129684[113] = 0;
   out_2563232569638129684[114] = 1;
   out_2563232569638129684[115] = 0;
   out_2563232569638129684[116] = 0;
   out_2563232569638129684[117] = 0;
   out_2563232569638129684[118] = 0;
   out_2563232569638129684[119] = 0;
   out_2563232569638129684[120] = 0;
   out_2563232569638129684[121] = 0;
   out_2563232569638129684[122] = 0;
   out_2563232569638129684[123] = 0;
   out_2563232569638129684[124] = 0;
   out_2563232569638129684[125] = 0;
   out_2563232569638129684[126] = 0;
   out_2563232569638129684[127] = 0;
   out_2563232569638129684[128] = 0;
   out_2563232569638129684[129] = 0;
   out_2563232569638129684[130] = 0;
   out_2563232569638129684[131] = 0;
   out_2563232569638129684[132] = 0;
   out_2563232569638129684[133] = 1;
   out_2563232569638129684[134] = 0;
   out_2563232569638129684[135] = 0;
   out_2563232569638129684[136] = 0;
   out_2563232569638129684[137] = 0;
   out_2563232569638129684[138] = 0;
   out_2563232569638129684[139] = 0;
   out_2563232569638129684[140] = 0;
   out_2563232569638129684[141] = 0;
   out_2563232569638129684[142] = 0;
   out_2563232569638129684[143] = 0;
   out_2563232569638129684[144] = 0;
   out_2563232569638129684[145] = 0;
   out_2563232569638129684[146] = 0;
   out_2563232569638129684[147] = 0;
   out_2563232569638129684[148] = 0;
   out_2563232569638129684[149] = 0;
   out_2563232569638129684[150] = 0;
   out_2563232569638129684[151] = 0;
   out_2563232569638129684[152] = 1;
   out_2563232569638129684[153] = 0;
   out_2563232569638129684[154] = 0;
   out_2563232569638129684[155] = 0;
   out_2563232569638129684[156] = 0;
   out_2563232569638129684[157] = 0;
   out_2563232569638129684[158] = 0;
   out_2563232569638129684[159] = 0;
   out_2563232569638129684[160] = 0;
   out_2563232569638129684[161] = 0;
   out_2563232569638129684[162] = 0;
   out_2563232569638129684[163] = 0;
   out_2563232569638129684[164] = 0;
   out_2563232569638129684[165] = 0;
   out_2563232569638129684[166] = 0;
   out_2563232569638129684[167] = 0;
   out_2563232569638129684[168] = 0;
   out_2563232569638129684[169] = 0;
   out_2563232569638129684[170] = 0;
   out_2563232569638129684[171] = 1;
   out_2563232569638129684[172] = 0;
   out_2563232569638129684[173] = 0;
   out_2563232569638129684[174] = 0;
   out_2563232569638129684[175] = 0;
   out_2563232569638129684[176] = 0;
   out_2563232569638129684[177] = 0;
   out_2563232569638129684[178] = 0;
   out_2563232569638129684[179] = 0;
   out_2563232569638129684[180] = 0;
   out_2563232569638129684[181] = 0;
   out_2563232569638129684[182] = 0;
   out_2563232569638129684[183] = 0;
   out_2563232569638129684[184] = 0;
   out_2563232569638129684[185] = 0;
   out_2563232569638129684[186] = 0;
   out_2563232569638129684[187] = 0;
   out_2563232569638129684[188] = 0;
   out_2563232569638129684[189] = 0;
   out_2563232569638129684[190] = 1;
   out_2563232569638129684[191] = 0;
   out_2563232569638129684[192] = 0;
   out_2563232569638129684[193] = 0;
   out_2563232569638129684[194] = 0;
   out_2563232569638129684[195] = 0;
   out_2563232569638129684[196] = 0;
   out_2563232569638129684[197] = 0;
   out_2563232569638129684[198] = 0;
   out_2563232569638129684[199] = 0;
   out_2563232569638129684[200] = 0;
   out_2563232569638129684[201] = 0;
   out_2563232569638129684[202] = 0;
   out_2563232569638129684[203] = 0;
   out_2563232569638129684[204] = 0;
   out_2563232569638129684[205] = 0;
   out_2563232569638129684[206] = 0;
   out_2563232569638129684[207] = 0;
   out_2563232569638129684[208] = 0;
   out_2563232569638129684[209] = 1;
   out_2563232569638129684[210] = 0;
   out_2563232569638129684[211] = 0;
   out_2563232569638129684[212] = 0;
   out_2563232569638129684[213] = 0;
   out_2563232569638129684[214] = 0;
   out_2563232569638129684[215] = 0;
   out_2563232569638129684[216] = 0;
   out_2563232569638129684[217] = 0;
   out_2563232569638129684[218] = 0;
   out_2563232569638129684[219] = 0;
   out_2563232569638129684[220] = 0;
   out_2563232569638129684[221] = 0;
   out_2563232569638129684[222] = 0;
   out_2563232569638129684[223] = 0;
   out_2563232569638129684[224] = 0;
   out_2563232569638129684[225] = 0;
   out_2563232569638129684[226] = 0;
   out_2563232569638129684[227] = 0;
   out_2563232569638129684[228] = 1;
   out_2563232569638129684[229] = 0;
   out_2563232569638129684[230] = 0;
   out_2563232569638129684[231] = 0;
   out_2563232569638129684[232] = 0;
   out_2563232569638129684[233] = 0;
   out_2563232569638129684[234] = 0;
   out_2563232569638129684[235] = 0;
   out_2563232569638129684[236] = 0;
   out_2563232569638129684[237] = 0;
   out_2563232569638129684[238] = 0;
   out_2563232569638129684[239] = 0;
   out_2563232569638129684[240] = 0;
   out_2563232569638129684[241] = 0;
   out_2563232569638129684[242] = 0;
   out_2563232569638129684[243] = 0;
   out_2563232569638129684[244] = 0;
   out_2563232569638129684[245] = 0;
   out_2563232569638129684[246] = 0;
   out_2563232569638129684[247] = 1;
   out_2563232569638129684[248] = 0;
   out_2563232569638129684[249] = 0;
   out_2563232569638129684[250] = 0;
   out_2563232569638129684[251] = 0;
   out_2563232569638129684[252] = 0;
   out_2563232569638129684[253] = 0;
   out_2563232569638129684[254] = 0;
   out_2563232569638129684[255] = 0;
   out_2563232569638129684[256] = 0;
   out_2563232569638129684[257] = 0;
   out_2563232569638129684[258] = 0;
   out_2563232569638129684[259] = 0;
   out_2563232569638129684[260] = 0;
   out_2563232569638129684[261] = 0;
   out_2563232569638129684[262] = 0;
   out_2563232569638129684[263] = 0;
   out_2563232569638129684[264] = 0;
   out_2563232569638129684[265] = 0;
   out_2563232569638129684[266] = 1;
   out_2563232569638129684[267] = 0;
   out_2563232569638129684[268] = 0;
   out_2563232569638129684[269] = 0;
   out_2563232569638129684[270] = 0;
   out_2563232569638129684[271] = 0;
   out_2563232569638129684[272] = 0;
   out_2563232569638129684[273] = 0;
   out_2563232569638129684[274] = 0;
   out_2563232569638129684[275] = 0;
   out_2563232569638129684[276] = 0;
   out_2563232569638129684[277] = 0;
   out_2563232569638129684[278] = 0;
   out_2563232569638129684[279] = 0;
   out_2563232569638129684[280] = 0;
   out_2563232569638129684[281] = 0;
   out_2563232569638129684[282] = 0;
   out_2563232569638129684[283] = 0;
   out_2563232569638129684[284] = 0;
   out_2563232569638129684[285] = 1;
   out_2563232569638129684[286] = 0;
   out_2563232569638129684[287] = 0;
   out_2563232569638129684[288] = 0;
   out_2563232569638129684[289] = 0;
   out_2563232569638129684[290] = 0;
   out_2563232569638129684[291] = 0;
   out_2563232569638129684[292] = 0;
   out_2563232569638129684[293] = 0;
   out_2563232569638129684[294] = 0;
   out_2563232569638129684[295] = 0;
   out_2563232569638129684[296] = 0;
   out_2563232569638129684[297] = 0;
   out_2563232569638129684[298] = 0;
   out_2563232569638129684[299] = 0;
   out_2563232569638129684[300] = 0;
   out_2563232569638129684[301] = 0;
   out_2563232569638129684[302] = 0;
   out_2563232569638129684[303] = 0;
   out_2563232569638129684[304] = 1;
   out_2563232569638129684[305] = 0;
   out_2563232569638129684[306] = 0;
   out_2563232569638129684[307] = 0;
   out_2563232569638129684[308] = 0;
   out_2563232569638129684[309] = 0;
   out_2563232569638129684[310] = 0;
   out_2563232569638129684[311] = 0;
   out_2563232569638129684[312] = 0;
   out_2563232569638129684[313] = 0;
   out_2563232569638129684[314] = 0;
   out_2563232569638129684[315] = 0;
   out_2563232569638129684[316] = 0;
   out_2563232569638129684[317] = 0;
   out_2563232569638129684[318] = 0;
   out_2563232569638129684[319] = 0;
   out_2563232569638129684[320] = 0;
   out_2563232569638129684[321] = 0;
   out_2563232569638129684[322] = 0;
   out_2563232569638129684[323] = 1;
}
void h_4(double *state, double *unused, double *out_9057789463521636950) {
   out_9057789463521636950[0] = state[6] + state[9];
   out_9057789463521636950[1] = state[7] + state[10];
   out_9057789463521636950[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_6434139615882878081) {
   out_6434139615882878081[0] = 0;
   out_6434139615882878081[1] = 0;
   out_6434139615882878081[2] = 0;
   out_6434139615882878081[3] = 0;
   out_6434139615882878081[4] = 0;
   out_6434139615882878081[5] = 0;
   out_6434139615882878081[6] = 1;
   out_6434139615882878081[7] = 0;
   out_6434139615882878081[8] = 0;
   out_6434139615882878081[9] = 1;
   out_6434139615882878081[10] = 0;
   out_6434139615882878081[11] = 0;
   out_6434139615882878081[12] = 0;
   out_6434139615882878081[13] = 0;
   out_6434139615882878081[14] = 0;
   out_6434139615882878081[15] = 0;
   out_6434139615882878081[16] = 0;
   out_6434139615882878081[17] = 0;
   out_6434139615882878081[18] = 0;
   out_6434139615882878081[19] = 0;
   out_6434139615882878081[20] = 0;
   out_6434139615882878081[21] = 0;
   out_6434139615882878081[22] = 0;
   out_6434139615882878081[23] = 0;
   out_6434139615882878081[24] = 0;
   out_6434139615882878081[25] = 1;
   out_6434139615882878081[26] = 0;
   out_6434139615882878081[27] = 0;
   out_6434139615882878081[28] = 1;
   out_6434139615882878081[29] = 0;
   out_6434139615882878081[30] = 0;
   out_6434139615882878081[31] = 0;
   out_6434139615882878081[32] = 0;
   out_6434139615882878081[33] = 0;
   out_6434139615882878081[34] = 0;
   out_6434139615882878081[35] = 0;
   out_6434139615882878081[36] = 0;
   out_6434139615882878081[37] = 0;
   out_6434139615882878081[38] = 0;
   out_6434139615882878081[39] = 0;
   out_6434139615882878081[40] = 0;
   out_6434139615882878081[41] = 0;
   out_6434139615882878081[42] = 0;
   out_6434139615882878081[43] = 0;
   out_6434139615882878081[44] = 1;
   out_6434139615882878081[45] = 0;
   out_6434139615882878081[46] = 0;
   out_6434139615882878081[47] = 1;
   out_6434139615882878081[48] = 0;
   out_6434139615882878081[49] = 0;
   out_6434139615882878081[50] = 0;
   out_6434139615882878081[51] = 0;
   out_6434139615882878081[52] = 0;
   out_6434139615882878081[53] = 0;
}
void h_10(double *state, double *unused, double *out_439040734435285181) {
   out_439040734435285181[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_439040734435285181[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_439040734435285181[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_1840785913394498883) {
   out_1840785913394498883[0] = 0;
   out_1840785913394498883[1] = 9.8100000000000005*cos(state[1]);
   out_1840785913394498883[2] = 0;
   out_1840785913394498883[3] = 0;
   out_1840785913394498883[4] = -state[8];
   out_1840785913394498883[5] = state[7];
   out_1840785913394498883[6] = 0;
   out_1840785913394498883[7] = state[5];
   out_1840785913394498883[8] = -state[4];
   out_1840785913394498883[9] = 0;
   out_1840785913394498883[10] = 0;
   out_1840785913394498883[11] = 0;
   out_1840785913394498883[12] = 1;
   out_1840785913394498883[13] = 0;
   out_1840785913394498883[14] = 0;
   out_1840785913394498883[15] = 1;
   out_1840785913394498883[16] = 0;
   out_1840785913394498883[17] = 0;
   out_1840785913394498883[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_1840785913394498883[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_1840785913394498883[20] = 0;
   out_1840785913394498883[21] = state[8];
   out_1840785913394498883[22] = 0;
   out_1840785913394498883[23] = -state[6];
   out_1840785913394498883[24] = -state[5];
   out_1840785913394498883[25] = 0;
   out_1840785913394498883[26] = state[3];
   out_1840785913394498883[27] = 0;
   out_1840785913394498883[28] = 0;
   out_1840785913394498883[29] = 0;
   out_1840785913394498883[30] = 0;
   out_1840785913394498883[31] = 1;
   out_1840785913394498883[32] = 0;
   out_1840785913394498883[33] = 0;
   out_1840785913394498883[34] = 1;
   out_1840785913394498883[35] = 0;
   out_1840785913394498883[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_1840785913394498883[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_1840785913394498883[38] = 0;
   out_1840785913394498883[39] = -state[7];
   out_1840785913394498883[40] = state[6];
   out_1840785913394498883[41] = 0;
   out_1840785913394498883[42] = state[4];
   out_1840785913394498883[43] = -state[3];
   out_1840785913394498883[44] = 0;
   out_1840785913394498883[45] = 0;
   out_1840785913394498883[46] = 0;
   out_1840785913394498883[47] = 0;
   out_1840785913394498883[48] = 0;
   out_1840785913394498883[49] = 0;
   out_1840785913394498883[50] = 1;
   out_1840785913394498883[51] = 0;
   out_1840785913394498883[52] = 0;
   out_1840785913394498883[53] = 1;
}
void h_13(double *state, double *unused, double *out_7181492765475252926) {
   out_7181492765475252926[0] = state[3];
   out_7181492765475252926[1] = state[4];
   out_7181492765475252926[2] = state[5];
}
void H_13(double *state, double *unused, double *out_3221865790550545280) {
   out_3221865790550545280[0] = 0;
   out_3221865790550545280[1] = 0;
   out_3221865790550545280[2] = 0;
   out_3221865790550545280[3] = 1;
   out_3221865790550545280[4] = 0;
   out_3221865790550545280[5] = 0;
   out_3221865790550545280[6] = 0;
   out_3221865790550545280[7] = 0;
   out_3221865790550545280[8] = 0;
   out_3221865790550545280[9] = 0;
   out_3221865790550545280[10] = 0;
   out_3221865790550545280[11] = 0;
   out_3221865790550545280[12] = 0;
   out_3221865790550545280[13] = 0;
   out_3221865790550545280[14] = 0;
   out_3221865790550545280[15] = 0;
   out_3221865790550545280[16] = 0;
   out_3221865790550545280[17] = 0;
   out_3221865790550545280[18] = 0;
   out_3221865790550545280[19] = 0;
   out_3221865790550545280[20] = 0;
   out_3221865790550545280[21] = 0;
   out_3221865790550545280[22] = 1;
   out_3221865790550545280[23] = 0;
   out_3221865790550545280[24] = 0;
   out_3221865790550545280[25] = 0;
   out_3221865790550545280[26] = 0;
   out_3221865790550545280[27] = 0;
   out_3221865790550545280[28] = 0;
   out_3221865790550545280[29] = 0;
   out_3221865790550545280[30] = 0;
   out_3221865790550545280[31] = 0;
   out_3221865790550545280[32] = 0;
   out_3221865790550545280[33] = 0;
   out_3221865790550545280[34] = 0;
   out_3221865790550545280[35] = 0;
   out_3221865790550545280[36] = 0;
   out_3221865790550545280[37] = 0;
   out_3221865790550545280[38] = 0;
   out_3221865790550545280[39] = 0;
   out_3221865790550545280[40] = 0;
   out_3221865790550545280[41] = 1;
   out_3221865790550545280[42] = 0;
   out_3221865790550545280[43] = 0;
   out_3221865790550545280[44] = 0;
   out_3221865790550545280[45] = 0;
   out_3221865790550545280[46] = 0;
   out_3221865790550545280[47] = 0;
   out_3221865790550545280[48] = 0;
   out_3221865790550545280[49] = 0;
   out_3221865790550545280[50] = 0;
   out_3221865790550545280[51] = 0;
   out_3221865790550545280[52] = 0;
   out_3221865790550545280[53] = 0;
}
void h_14(double *state, double *unused, double *out_1398557426791028034) {
   out_1398557426791028034[0] = state[6];
   out_1398557426791028034[1] = state[7];
   out_1398557426791028034[2] = state[8];
}
void H_14(double *state, double *unused, double *out_2470898759543393552) {
   out_2470898759543393552[0] = 0;
   out_2470898759543393552[1] = 0;
   out_2470898759543393552[2] = 0;
   out_2470898759543393552[3] = 0;
   out_2470898759543393552[4] = 0;
   out_2470898759543393552[5] = 0;
   out_2470898759543393552[6] = 1;
   out_2470898759543393552[7] = 0;
   out_2470898759543393552[8] = 0;
   out_2470898759543393552[9] = 0;
   out_2470898759543393552[10] = 0;
   out_2470898759543393552[11] = 0;
   out_2470898759543393552[12] = 0;
   out_2470898759543393552[13] = 0;
   out_2470898759543393552[14] = 0;
   out_2470898759543393552[15] = 0;
   out_2470898759543393552[16] = 0;
   out_2470898759543393552[17] = 0;
   out_2470898759543393552[18] = 0;
   out_2470898759543393552[19] = 0;
   out_2470898759543393552[20] = 0;
   out_2470898759543393552[21] = 0;
   out_2470898759543393552[22] = 0;
   out_2470898759543393552[23] = 0;
   out_2470898759543393552[24] = 0;
   out_2470898759543393552[25] = 1;
   out_2470898759543393552[26] = 0;
   out_2470898759543393552[27] = 0;
   out_2470898759543393552[28] = 0;
   out_2470898759543393552[29] = 0;
   out_2470898759543393552[30] = 0;
   out_2470898759543393552[31] = 0;
   out_2470898759543393552[32] = 0;
   out_2470898759543393552[33] = 0;
   out_2470898759543393552[34] = 0;
   out_2470898759543393552[35] = 0;
   out_2470898759543393552[36] = 0;
   out_2470898759543393552[37] = 0;
   out_2470898759543393552[38] = 0;
   out_2470898759543393552[39] = 0;
   out_2470898759543393552[40] = 0;
   out_2470898759543393552[41] = 0;
   out_2470898759543393552[42] = 0;
   out_2470898759543393552[43] = 0;
   out_2470898759543393552[44] = 1;
   out_2470898759543393552[45] = 0;
   out_2470898759543393552[46] = 0;
   out_2470898759543393552[47] = 0;
   out_2470898759543393552[48] = 0;
   out_2470898759543393552[49] = 0;
   out_2470898759543393552[50] = 0;
   out_2470898759543393552[51] = 0;
   out_2470898759543393552[52] = 0;
   out_2470898759543393552[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_6395110133292861521) {
  err_fun(nom_x, delta_x, out_6395110133292861521);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5574902989131587335) {
  inv_err_fun(nom_x, true_x, out_5574902989131587335);
}
void pose_H_mod_fun(double *state, double *out_6860086072787592800) {
  H_mod_fun(state, out_6860086072787592800);
}
void pose_f_fun(double *state, double dt, double *out_6157473931416548839) {
  f_fun(state,  dt, out_6157473931416548839);
}
void pose_F_fun(double *state, double dt, double *out_2563232569638129684) {
  F_fun(state,  dt, out_2563232569638129684);
}
void pose_h_4(double *state, double *unused, double *out_9057789463521636950) {
  h_4(state, unused, out_9057789463521636950);
}
void pose_H_4(double *state, double *unused, double *out_6434139615882878081) {
  H_4(state, unused, out_6434139615882878081);
}
void pose_h_10(double *state, double *unused, double *out_439040734435285181) {
  h_10(state, unused, out_439040734435285181);
}
void pose_H_10(double *state, double *unused, double *out_1840785913394498883) {
  H_10(state, unused, out_1840785913394498883);
}
void pose_h_13(double *state, double *unused, double *out_7181492765475252926) {
  h_13(state, unused, out_7181492765475252926);
}
void pose_H_13(double *state, double *unused, double *out_3221865790550545280) {
  H_13(state, unused, out_3221865790550545280);
}
void pose_h_14(double *state, double *unused, double *out_1398557426791028034) {
  h_14(state, unused, out_1398557426791028034);
}
void pose_H_14(double *state, double *unused, double *out_2470898759543393552) {
  H_14(state, unused, out_2470898759543393552);
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
