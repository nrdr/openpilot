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
void err_fun(double *nom_x, double *delta_x, double *out_7113141565155944071) {
   out_7113141565155944071[0] = delta_x[0] + nom_x[0];
   out_7113141565155944071[1] = delta_x[1] + nom_x[1];
   out_7113141565155944071[2] = delta_x[2] + nom_x[2];
   out_7113141565155944071[3] = delta_x[3] + nom_x[3];
   out_7113141565155944071[4] = delta_x[4] + nom_x[4];
   out_7113141565155944071[5] = delta_x[5] + nom_x[5];
   out_7113141565155944071[6] = delta_x[6] + nom_x[6];
   out_7113141565155944071[7] = delta_x[7] + nom_x[7];
   out_7113141565155944071[8] = delta_x[8] + nom_x[8];
   out_7113141565155944071[9] = delta_x[9] + nom_x[9];
   out_7113141565155944071[10] = delta_x[10] + nom_x[10];
   out_7113141565155944071[11] = delta_x[11] + nom_x[11];
   out_7113141565155944071[12] = delta_x[12] + nom_x[12];
   out_7113141565155944071[13] = delta_x[13] + nom_x[13];
   out_7113141565155944071[14] = delta_x[14] + nom_x[14];
   out_7113141565155944071[15] = delta_x[15] + nom_x[15];
   out_7113141565155944071[16] = delta_x[16] + nom_x[16];
   out_7113141565155944071[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4273806753012627861) {
   out_4273806753012627861[0] = -nom_x[0] + true_x[0];
   out_4273806753012627861[1] = -nom_x[1] + true_x[1];
   out_4273806753012627861[2] = -nom_x[2] + true_x[2];
   out_4273806753012627861[3] = -nom_x[3] + true_x[3];
   out_4273806753012627861[4] = -nom_x[4] + true_x[4];
   out_4273806753012627861[5] = -nom_x[5] + true_x[5];
   out_4273806753012627861[6] = -nom_x[6] + true_x[6];
   out_4273806753012627861[7] = -nom_x[7] + true_x[7];
   out_4273806753012627861[8] = -nom_x[8] + true_x[8];
   out_4273806753012627861[9] = -nom_x[9] + true_x[9];
   out_4273806753012627861[10] = -nom_x[10] + true_x[10];
   out_4273806753012627861[11] = -nom_x[11] + true_x[11];
   out_4273806753012627861[12] = -nom_x[12] + true_x[12];
   out_4273806753012627861[13] = -nom_x[13] + true_x[13];
   out_4273806753012627861[14] = -nom_x[14] + true_x[14];
   out_4273806753012627861[15] = -nom_x[15] + true_x[15];
   out_4273806753012627861[16] = -nom_x[16] + true_x[16];
   out_4273806753012627861[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_4327706851715669235) {
   out_4327706851715669235[0] = 1.0;
   out_4327706851715669235[1] = 0.0;
   out_4327706851715669235[2] = 0.0;
   out_4327706851715669235[3] = 0.0;
   out_4327706851715669235[4] = 0.0;
   out_4327706851715669235[5] = 0.0;
   out_4327706851715669235[6] = 0.0;
   out_4327706851715669235[7] = 0.0;
   out_4327706851715669235[8] = 0.0;
   out_4327706851715669235[9] = 0.0;
   out_4327706851715669235[10] = 0.0;
   out_4327706851715669235[11] = 0.0;
   out_4327706851715669235[12] = 0.0;
   out_4327706851715669235[13] = 0.0;
   out_4327706851715669235[14] = 0.0;
   out_4327706851715669235[15] = 0.0;
   out_4327706851715669235[16] = 0.0;
   out_4327706851715669235[17] = 0.0;
   out_4327706851715669235[18] = 0.0;
   out_4327706851715669235[19] = 1.0;
   out_4327706851715669235[20] = 0.0;
   out_4327706851715669235[21] = 0.0;
   out_4327706851715669235[22] = 0.0;
   out_4327706851715669235[23] = 0.0;
   out_4327706851715669235[24] = 0.0;
   out_4327706851715669235[25] = 0.0;
   out_4327706851715669235[26] = 0.0;
   out_4327706851715669235[27] = 0.0;
   out_4327706851715669235[28] = 0.0;
   out_4327706851715669235[29] = 0.0;
   out_4327706851715669235[30] = 0.0;
   out_4327706851715669235[31] = 0.0;
   out_4327706851715669235[32] = 0.0;
   out_4327706851715669235[33] = 0.0;
   out_4327706851715669235[34] = 0.0;
   out_4327706851715669235[35] = 0.0;
   out_4327706851715669235[36] = 0.0;
   out_4327706851715669235[37] = 0.0;
   out_4327706851715669235[38] = 1.0;
   out_4327706851715669235[39] = 0.0;
   out_4327706851715669235[40] = 0.0;
   out_4327706851715669235[41] = 0.0;
   out_4327706851715669235[42] = 0.0;
   out_4327706851715669235[43] = 0.0;
   out_4327706851715669235[44] = 0.0;
   out_4327706851715669235[45] = 0.0;
   out_4327706851715669235[46] = 0.0;
   out_4327706851715669235[47] = 0.0;
   out_4327706851715669235[48] = 0.0;
   out_4327706851715669235[49] = 0.0;
   out_4327706851715669235[50] = 0.0;
   out_4327706851715669235[51] = 0.0;
   out_4327706851715669235[52] = 0.0;
   out_4327706851715669235[53] = 0.0;
   out_4327706851715669235[54] = 0.0;
   out_4327706851715669235[55] = 0.0;
   out_4327706851715669235[56] = 0.0;
   out_4327706851715669235[57] = 1.0;
   out_4327706851715669235[58] = 0.0;
   out_4327706851715669235[59] = 0.0;
   out_4327706851715669235[60] = 0.0;
   out_4327706851715669235[61] = 0.0;
   out_4327706851715669235[62] = 0.0;
   out_4327706851715669235[63] = 0.0;
   out_4327706851715669235[64] = 0.0;
   out_4327706851715669235[65] = 0.0;
   out_4327706851715669235[66] = 0.0;
   out_4327706851715669235[67] = 0.0;
   out_4327706851715669235[68] = 0.0;
   out_4327706851715669235[69] = 0.0;
   out_4327706851715669235[70] = 0.0;
   out_4327706851715669235[71] = 0.0;
   out_4327706851715669235[72] = 0.0;
   out_4327706851715669235[73] = 0.0;
   out_4327706851715669235[74] = 0.0;
   out_4327706851715669235[75] = 0.0;
   out_4327706851715669235[76] = 1.0;
   out_4327706851715669235[77] = 0.0;
   out_4327706851715669235[78] = 0.0;
   out_4327706851715669235[79] = 0.0;
   out_4327706851715669235[80] = 0.0;
   out_4327706851715669235[81] = 0.0;
   out_4327706851715669235[82] = 0.0;
   out_4327706851715669235[83] = 0.0;
   out_4327706851715669235[84] = 0.0;
   out_4327706851715669235[85] = 0.0;
   out_4327706851715669235[86] = 0.0;
   out_4327706851715669235[87] = 0.0;
   out_4327706851715669235[88] = 0.0;
   out_4327706851715669235[89] = 0.0;
   out_4327706851715669235[90] = 0.0;
   out_4327706851715669235[91] = 0.0;
   out_4327706851715669235[92] = 0.0;
   out_4327706851715669235[93] = 0.0;
   out_4327706851715669235[94] = 0.0;
   out_4327706851715669235[95] = 1.0;
   out_4327706851715669235[96] = 0.0;
   out_4327706851715669235[97] = 0.0;
   out_4327706851715669235[98] = 0.0;
   out_4327706851715669235[99] = 0.0;
   out_4327706851715669235[100] = 0.0;
   out_4327706851715669235[101] = 0.0;
   out_4327706851715669235[102] = 0.0;
   out_4327706851715669235[103] = 0.0;
   out_4327706851715669235[104] = 0.0;
   out_4327706851715669235[105] = 0.0;
   out_4327706851715669235[106] = 0.0;
   out_4327706851715669235[107] = 0.0;
   out_4327706851715669235[108] = 0.0;
   out_4327706851715669235[109] = 0.0;
   out_4327706851715669235[110] = 0.0;
   out_4327706851715669235[111] = 0.0;
   out_4327706851715669235[112] = 0.0;
   out_4327706851715669235[113] = 0.0;
   out_4327706851715669235[114] = 1.0;
   out_4327706851715669235[115] = 0.0;
   out_4327706851715669235[116] = 0.0;
   out_4327706851715669235[117] = 0.0;
   out_4327706851715669235[118] = 0.0;
   out_4327706851715669235[119] = 0.0;
   out_4327706851715669235[120] = 0.0;
   out_4327706851715669235[121] = 0.0;
   out_4327706851715669235[122] = 0.0;
   out_4327706851715669235[123] = 0.0;
   out_4327706851715669235[124] = 0.0;
   out_4327706851715669235[125] = 0.0;
   out_4327706851715669235[126] = 0.0;
   out_4327706851715669235[127] = 0.0;
   out_4327706851715669235[128] = 0.0;
   out_4327706851715669235[129] = 0.0;
   out_4327706851715669235[130] = 0.0;
   out_4327706851715669235[131] = 0.0;
   out_4327706851715669235[132] = 0.0;
   out_4327706851715669235[133] = 1.0;
   out_4327706851715669235[134] = 0.0;
   out_4327706851715669235[135] = 0.0;
   out_4327706851715669235[136] = 0.0;
   out_4327706851715669235[137] = 0.0;
   out_4327706851715669235[138] = 0.0;
   out_4327706851715669235[139] = 0.0;
   out_4327706851715669235[140] = 0.0;
   out_4327706851715669235[141] = 0.0;
   out_4327706851715669235[142] = 0.0;
   out_4327706851715669235[143] = 0.0;
   out_4327706851715669235[144] = 0.0;
   out_4327706851715669235[145] = 0.0;
   out_4327706851715669235[146] = 0.0;
   out_4327706851715669235[147] = 0.0;
   out_4327706851715669235[148] = 0.0;
   out_4327706851715669235[149] = 0.0;
   out_4327706851715669235[150] = 0.0;
   out_4327706851715669235[151] = 0.0;
   out_4327706851715669235[152] = 1.0;
   out_4327706851715669235[153] = 0.0;
   out_4327706851715669235[154] = 0.0;
   out_4327706851715669235[155] = 0.0;
   out_4327706851715669235[156] = 0.0;
   out_4327706851715669235[157] = 0.0;
   out_4327706851715669235[158] = 0.0;
   out_4327706851715669235[159] = 0.0;
   out_4327706851715669235[160] = 0.0;
   out_4327706851715669235[161] = 0.0;
   out_4327706851715669235[162] = 0.0;
   out_4327706851715669235[163] = 0.0;
   out_4327706851715669235[164] = 0.0;
   out_4327706851715669235[165] = 0.0;
   out_4327706851715669235[166] = 0.0;
   out_4327706851715669235[167] = 0.0;
   out_4327706851715669235[168] = 0.0;
   out_4327706851715669235[169] = 0.0;
   out_4327706851715669235[170] = 0.0;
   out_4327706851715669235[171] = 1.0;
   out_4327706851715669235[172] = 0.0;
   out_4327706851715669235[173] = 0.0;
   out_4327706851715669235[174] = 0.0;
   out_4327706851715669235[175] = 0.0;
   out_4327706851715669235[176] = 0.0;
   out_4327706851715669235[177] = 0.0;
   out_4327706851715669235[178] = 0.0;
   out_4327706851715669235[179] = 0.0;
   out_4327706851715669235[180] = 0.0;
   out_4327706851715669235[181] = 0.0;
   out_4327706851715669235[182] = 0.0;
   out_4327706851715669235[183] = 0.0;
   out_4327706851715669235[184] = 0.0;
   out_4327706851715669235[185] = 0.0;
   out_4327706851715669235[186] = 0.0;
   out_4327706851715669235[187] = 0.0;
   out_4327706851715669235[188] = 0.0;
   out_4327706851715669235[189] = 0.0;
   out_4327706851715669235[190] = 1.0;
   out_4327706851715669235[191] = 0.0;
   out_4327706851715669235[192] = 0.0;
   out_4327706851715669235[193] = 0.0;
   out_4327706851715669235[194] = 0.0;
   out_4327706851715669235[195] = 0.0;
   out_4327706851715669235[196] = 0.0;
   out_4327706851715669235[197] = 0.0;
   out_4327706851715669235[198] = 0.0;
   out_4327706851715669235[199] = 0.0;
   out_4327706851715669235[200] = 0.0;
   out_4327706851715669235[201] = 0.0;
   out_4327706851715669235[202] = 0.0;
   out_4327706851715669235[203] = 0.0;
   out_4327706851715669235[204] = 0.0;
   out_4327706851715669235[205] = 0.0;
   out_4327706851715669235[206] = 0.0;
   out_4327706851715669235[207] = 0.0;
   out_4327706851715669235[208] = 0.0;
   out_4327706851715669235[209] = 1.0;
   out_4327706851715669235[210] = 0.0;
   out_4327706851715669235[211] = 0.0;
   out_4327706851715669235[212] = 0.0;
   out_4327706851715669235[213] = 0.0;
   out_4327706851715669235[214] = 0.0;
   out_4327706851715669235[215] = 0.0;
   out_4327706851715669235[216] = 0.0;
   out_4327706851715669235[217] = 0.0;
   out_4327706851715669235[218] = 0.0;
   out_4327706851715669235[219] = 0.0;
   out_4327706851715669235[220] = 0.0;
   out_4327706851715669235[221] = 0.0;
   out_4327706851715669235[222] = 0.0;
   out_4327706851715669235[223] = 0.0;
   out_4327706851715669235[224] = 0.0;
   out_4327706851715669235[225] = 0.0;
   out_4327706851715669235[226] = 0.0;
   out_4327706851715669235[227] = 0.0;
   out_4327706851715669235[228] = 1.0;
   out_4327706851715669235[229] = 0.0;
   out_4327706851715669235[230] = 0.0;
   out_4327706851715669235[231] = 0.0;
   out_4327706851715669235[232] = 0.0;
   out_4327706851715669235[233] = 0.0;
   out_4327706851715669235[234] = 0.0;
   out_4327706851715669235[235] = 0.0;
   out_4327706851715669235[236] = 0.0;
   out_4327706851715669235[237] = 0.0;
   out_4327706851715669235[238] = 0.0;
   out_4327706851715669235[239] = 0.0;
   out_4327706851715669235[240] = 0.0;
   out_4327706851715669235[241] = 0.0;
   out_4327706851715669235[242] = 0.0;
   out_4327706851715669235[243] = 0.0;
   out_4327706851715669235[244] = 0.0;
   out_4327706851715669235[245] = 0.0;
   out_4327706851715669235[246] = 0.0;
   out_4327706851715669235[247] = 1.0;
   out_4327706851715669235[248] = 0.0;
   out_4327706851715669235[249] = 0.0;
   out_4327706851715669235[250] = 0.0;
   out_4327706851715669235[251] = 0.0;
   out_4327706851715669235[252] = 0.0;
   out_4327706851715669235[253] = 0.0;
   out_4327706851715669235[254] = 0.0;
   out_4327706851715669235[255] = 0.0;
   out_4327706851715669235[256] = 0.0;
   out_4327706851715669235[257] = 0.0;
   out_4327706851715669235[258] = 0.0;
   out_4327706851715669235[259] = 0.0;
   out_4327706851715669235[260] = 0.0;
   out_4327706851715669235[261] = 0.0;
   out_4327706851715669235[262] = 0.0;
   out_4327706851715669235[263] = 0.0;
   out_4327706851715669235[264] = 0.0;
   out_4327706851715669235[265] = 0.0;
   out_4327706851715669235[266] = 1.0;
   out_4327706851715669235[267] = 0.0;
   out_4327706851715669235[268] = 0.0;
   out_4327706851715669235[269] = 0.0;
   out_4327706851715669235[270] = 0.0;
   out_4327706851715669235[271] = 0.0;
   out_4327706851715669235[272] = 0.0;
   out_4327706851715669235[273] = 0.0;
   out_4327706851715669235[274] = 0.0;
   out_4327706851715669235[275] = 0.0;
   out_4327706851715669235[276] = 0.0;
   out_4327706851715669235[277] = 0.0;
   out_4327706851715669235[278] = 0.0;
   out_4327706851715669235[279] = 0.0;
   out_4327706851715669235[280] = 0.0;
   out_4327706851715669235[281] = 0.0;
   out_4327706851715669235[282] = 0.0;
   out_4327706851715669235[283] = 0.0;
   out_4327706851715669235[284] = 0.0;
   out_4327706851715669235[285] = 1.0;
   out_4327706851715669235[286] = 0.0;
   out_4327706851715669235[287] = 0.0;
   out_4327706851715669235[288] = 0.0;
   out_4327706851715669235[289] = 0.0;
   out_4327706851715669235[290] = 0.0;
   out_4327706851715669235[291] = 0.0;
   out_4327706851715669235[292] = 0.0;
   out_4327706851715669235[293] = 0.0;
   out_4327706851715669235[294] = 0.0;
   out_4327706851715669235[295] = 0.0;
   out_4327706851715669235[296] = 0.0;
   out_4327706851715669235[297] = 0.0;
   out_4327706851715669235[298] = 0.0;
   out_4327706851715669235[299] = 0.0;
   out_4327706851715669235[300] = 0.0;
   out_4327706851715669235[301] = 0.0;
   out_4327706851715669235[302] = 0.0;
   out_4327706851715669235[303] = 0.0;
   out_4327706851715669235[304] = 1.0;
   out_4327706851715669235[305] = 0.0;
   out_4327706851715669235[306] = 0.0;
   out_4327706851715669235[307] = 0.0;
   out_4327706851715669235[308] = 0.0;
   out_4327706851715669235[309] = 0.0;
   out_4327706851715669235[310] = 0.0;
   out_4327706851715669235[311] = 0.0;
   out_4327706851715669235[312] = 0.0;
   out_4327706851715669235[313] = 0.0;
   out_4327706851715669235[314] = 0.0;
   out_4327706851715669235[315] = 0.0;
   out_4327706851715669235[316] = 0.0;
   out_4327706851715669235[317] = 0.0;
   out_4327706851715669235[318] = 0.0;
   out_4327706851715669235[319] = 0.0;
   out_4327706851715669235[320] = 0.0;
   out_4327706851715669235[321] = 0.0;
   out_4327706851715669235[322] = 0.0;
   out_4327706851715669235[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_497730658810754078) {
   out_497730658810754078[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_497730658810754078[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_497730658810754078[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_497730658810754078[3] = dt*state[12] + state[3];
   out_497730658810754078[4] = dt*state[13] + state[4];
   out_497730658810754078[5] = dt*state[14] + state[5];
   out_497730658810754078[6] = state[6];
   out_497730658810754078[7] = state[7];
   out_497730658810754078[8] = state[8];
   out_497730658810754078[9] = state[9];
   out_497730658810754078[10] = state[10];
   out_497730658810754078[11] = state[11];
   out_497730658810754078[12] = state[12];
   out_497730658810754078[13] = state[13];
   out_497730658810754078[14] = state[14];
   out_497730658810754078[15] = state[15];
   out_497730658810754078[16] = state[16];
   out_497730658810754078[17] = state[17];
}
void F_fun(double *state, double dt, double *out_6088738551748760158) {
   out_6088738551748760158[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6088738551748760158[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6088738551748760158[2] = 0;
   out_6088738551748760158[3] = 0;
   out_6088738551748760158[4] = 0;
   out_6088738551748760158[5] = 0;
   out_6088738551748760158[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6088738551748760158[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6088738551748760158[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6088738551748760158[9] = 0;
   out_6088738551748760158[10] = 0;
   out_6088738551748760158[11] = 0;
   out_6088738551748760158[12] = 0;
   out_6088738551748760158[13] = 0;
   out_6088738551748760158[14] = 0;
   out_6088738551748760158[15] = 0;
   out_6088738551748760158[16] = 0;
   out_6088738551748760158[17] = 0;
   out_6088738551748760158[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6088738551748760158[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6088738551748760158[20] = 0;
   out_6088738551748760158[21] = 0;
   out_6088738551748760158[22] = 0;
   out_6088738551748760158[23] = 0;
   out_6088738551748760158[24] = 0;
   out_6088738551748760158[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6088738551748760158[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6088738551748760158[27] = 0;
   out_6088738551748760158[28] = 0;
   out_6088738551748760158[29] = 0;
   out_6088738551748760158[30] = 0;
   out_6088738551748760158[31] = 0;
   out_6088738551748760158[32] = 0;
   out_6088738551748760158[33] = 0;
   out_6088738551748760158[34] = 0;
   out_6088738551748760158[35] = 0;
   out_6088738551748760158[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6088738551748760158[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6088738551748760158[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6088738551748760158[39] = 0;
   out_6088738551748760158[40] = 0;
   out_6088738551748760158[41] = 0;
   out_6088738551748760158[42] = 0;
   out_6088738551748760158[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6088738551748760158[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6088738551748760158[45] = 0;
   out_6088738551748760158[46] = 0;
   out_6088738551748760158[47] = 0;
   out_6088738551748760158[48] = 0;
   out_6088738551748760158[49] = 0;
   out_6088738551748760158[50] = 0;
   out_6088738551748760158[51] = 0;
   out_6088738551748760158[52] = 0;
   out_6088738551748760158[53] = 0;
   out_6088738551748760158[54] = 0;
   out_6088738551748760158[55] = 0;
   out_6088738551748760158[56] = 0;
   out_6088738551748760158[57] = 1;
   out_6088738551748760158[58] = 0;
   out_6088738551748760158[59] = 0;
   out_6088738551748760158[60] = 0;
   out_6088738551748760158[61] = 0;
   out_6088738551748760158[62] = 0;
   out_6088738551748760158[63] = 0;
   out_6088738551748760158[64] = 0;
   out_6088738551748760158[65] = 0;
   out_6088738551748760158[66] = dt;
   out_6088738551748760158[67] = 0;
   out_6088738551748760158[68] = 0;
   out_6088738551748760158[69] = 0;
   out_6088738551748760158[70] = 0;
   out_6088738551748760158[71] = 0;
   out_6088738551748760158[72] = 0;
   out_6088738551748760158[73] = 0;
   out_6088738551748760158[74] = 0;
   out_6088738551748760158[75] = 0;
   out_6088738551748760158[76] = 1;
   out_6088738551748760158[77] = 0;
   out_6088738551748760158[78] = 0;
   out_6088738551748760158[79] = 0;
   out_6088738551748760158[80] = 0;
   out_6088738551748760158[81] = 0;
   out_6088738551748760158[82] = 0;
   out_6088738551748760158[83] = 0;
   out_6088738551748760158[84] = 0;
   out_6088738551748760158[85] = dt;
   out_6088738551748760158[86] = 0;
   out_6088738551748760158[87] = 0;
   out_6088738551748760158[88] = 0;
   out_6088738551748760158[89] = 0;
   out_6088738551748760158[90] = 0;
   out_6088738551748760158[91] = 0;
   out_6088738551748760158[92] = 0;
   out_6088738551748760158[93] = 0;
   out_6088738551748760158[94] = 0;
   out_6088738551748760158[95] = 1;
   out_6088738551748760158[96] = 0;
   out_6088738551748760158[97] = 0;
   out_6088738551748760158[98] = 0;
   out_6088738551748760158[99] = 0;
   out_6088738551748760158[100] = 0;
   out_6088738551748760158[101] = 0;
   out_6088738551748760158[102] = 0;
   out_6088738551748760158[103] = 0;
   out_6088738551748760158[104] = dt;
   out_6088738551748760158[105] = 0;
   out_6088738551748760158[106] = 0;
   out_6088738551748760158[107] = 0;
   out_6088738551748760158[108] = 0;
   out_6088738551748760158[109] = 0;
   out_6088738551748760158[110] = 0;
   out_6088738551748760158[111] = 0;
   out_6088738551748760158[112] = 0;
   out_6088738551748760158[113] = 0;
   out_6088738551748760158[114] = 1;
   out_6088738551748760158[115] = 0;
   out_6088738551748760158[116] = 0;
   out_6088738551748760158[117] = 0;
   out_6088738551748760158[118] = 0;
   out_6088738551748760158[119] = 0;
   out_6088738551748760158[120] = 0;
   out_6088738551748760158[121] = 0;
   out_6088738551748760158[122] = 0;
   out_6088738551748760158[123] = 0;
   out_6088738551748760158[124] = 0;
   out_6088738551748760158[125] = 0;
   out_6088738551748760158[126] = 0;
   out_6088738551748760158[127] = 0;
   out_6088738551748760158[128] = 0;
   out_6088738551748760158[129] = 0;
   out_6088738551748760158[130] = 0;
   out_6088738551748760158[131] = 0;
   out_6088738551748760158[132] = 0;
   out_6088738551748760158[133] = 1;
   out_6088738551748760158[134] = 0;
   out_6088738551748760158[135] = 0;
   out_6088738551748760158[136] = 0;
   out_6088738551748760158[137] = 0;
   out_6088738551748760158[138] = 0;
   out_6088738551748760158[139] = 0;
   out_6088738551748760158[140] = 0;
   out_6088738551748760158[141] = 0;
   out_6088738551748760158[142] = 0;
   out_6088738551748760158[143] = 0;
   out_6088738551748760158[144] = 0;
   out_6088738551748760158[145] = 0;
   out_6088738551748760158[146] = 0;
   out_6088738551748760158[147] = 0;
   out_6088738551748760158[148] = 0;
   out_6088738551748760158[149] = 0;
   out_6088738551748760158[150] = 0;
   out_6088738551748760158[151] = 0;
   out_6088738551748760158[152] = 1;
   out_6088738551748760158[153] = 0;
   out_6088738551748760158[154] = 0;
   out_6088738551748760158[155] = 0;
   out_6088738551748760158[156] = 0;
   out_6088738551748760158[157] = 0;
   out_6088738551748760158[158] = 0;
   out_6088738551748760158[159] = 0;
   out_6088738551748760158[160] = 0;
   out_6088738551748760158[161] = 0;
   out_6088738551748760158[162] = 0;
   out_6088738551748760158[163] = 0;
   out_6088738551748760158[164] = 0;
   out_6088738551748760158[165] = 0;
   out_6088738551748760158[166] = 0;
   out_6088738551748760158[167] = 0;
   out_6088738551748760158[168] = 0;
   out_6088738551748760158[169] = 0;
   out_6088738551748760158[170] = 0;
   out_6088738551748760158[171] = 1;
   out_6088738551748760158[172] = 0;
   out_6088738551748760158[173] = 0;
   out_6088738551748760158[174] = 0;
   out_6088738551748760158[175] = 0;
   out_6088738551748760158[176] = 0;
   out_6088738551748760158[177] = 0;
   out_6088738551748760158[178] = 0;
   out_6088738551748760158[179] = 0;
   out_6088738551748760158[180] = 0;
   out_6088738551748760158[181] = 0;
   out_6088738551748760158[182] = 0;
   out_6088738551748760158[183] = 0;
   out_6088738551748760158[184] = 0;
   out_6088738551748760158[185] = 0;
   out_6088738551748760158[186] = 0;
   out_6088738551748760158[187] = 0;
   out_6088738551748760158[188] = 0;
   out_6088738551748760158[189] = 0;
   out_6088738551748760158[190] = 1;
   out_6088738551748760158[191] = 0;
   out_6088738551748760158[192] = 0;
   out_6088738551748760158[193] = 0;
   out_6088738551748760158[194] = 0;
   out_6088738551748760158[195] = 0;
   out_6088738551748760158[196] = 0;
   out_6088738551748760158[197] = 0;
   out_6088738551748760158[198] = 0;
   out_6088738551748760158[199] = 0;
   out_6088738551748760158[200] = 0;
   out_6088738551748760158[201] = 0;
   out_6088738551748760158[202] = 0;
   out_6088738551748760158[203] = 0;
   out_6088738551748760158[204] = 0;
   out_6088738551748760158[205] = 0;
   out_6088738551748760158[206] = 0;
   out_6088738551748760158[207] = 0;
   out_6088738551748760158[208] = 0;
   out_6088738551748760158[209] = 1;
   out_6088738551748760158[210] = 0;
   out_6088738551748760158[211] = 0;
   out_6088738551748760158[212] = 0;
   out_6088738551748760158[213] = 0;
   out_6088738551748760158[214] = 0;
   out_6088738551748760158[215] = 0;
   out_6088738551748760158[216] = 0;
   out_6088738551748760158[217] = 0;
   out_6088738551748760158[218] = 0;
   out_6088738551748760158[219] = 0;
   out_6088738551748760158[220] = 0;
   out_6088738551748760158[221] = 0;
   out_6088738551748760158[222] = 0;
   out_6088738551748760158[223] = 0;
   out_6088738551748760158[224] = 0;
   out_6088738551748760158[225] = 0;
   out_6088738551748760158[226] = 0;
   out_6088738551748760158[227] = 0;
   out_6088738551748760158[228] = 1;
   out_6088738551748760158[229] = 0;
   out_6088738551748760158[230] = 0;
   out_6088738551748760158[231] = 0;
   out_6088738551748760158[232] = 0;
   out_6088738551748760158[233] = 0;
   out_6088738551748760158[234] = 0;
   out_6088738551748760158[235] = 0;
   out_6088738551748760158[236] = 0;
   out_6088738551748760158[237] = 0;
   out_6088738551748760158[238] = 0;
   out_6088738551748760158[239] = 0;
   out_6088738551748760158[240] = 0;
   out_6088738551748760158[241] = 0;
   out_6088738551748760158[242] = 0;
   out_6088738551748760158[243] = 0;
   out_6088738551748760158[244] = 0;
   out_6088738551748760158[245] = 0;
   out_6088738551748760158[246] = 0;
   out_6088738551748760158[247] = 1;
   out_6088738551748760158[248] = 0;
   out_6088738551748760158[249] = 0;
   out_6088738551748760158[250] = 0;
   out_6088738551748760158[251] = 0;
   out_6088738551748760158[252] = 0;
   out_6088738551748760158[253] = 0;
   out_6088738551748760158[254] = 0;
   out_6088738551748760158[255] = 0;
   out_6088738551748760158[256] = 0;
   out_6088738551748760158[257] = 0;
   out_6088738551748760158[258] = 0;
   out_6088738551748760158[259] = 0;
   out_6088738551748760158[260] = 0;
   out_6088738551748760158[261] = 0;
   out_6088738551748760158[262] = 0;
   out_6088738551748760158[263] = 0;
   out_6088738551748760158[264] = 0;
   out_6088738551748760158[265] = 0;
   out_6088738551748760158[266] = 1;
   out_6088738551748760158[267] = 0;
   out_6088738551748760158[268] = 0;
   out_6088738551748760158[269] = 0;
   out_6088738551748760158[270] = 0;
   out_6088738551748760158[271] = 0;
   out_6088738551748760158[272] = 0;
   out_6088738551748760158[273] = 0;
   out_6088738551748760158[274] = 0;
   out_6088738551748760158[275] = 0;
   out_6088738551748760158[276] = 0;
   out_6088738551748760158[277] = 0;
   out_6088738551748760158[278] = 0;
   out_6088738551748760158[279] = 0;
   out_6088738551748760158[280] = 0;
   out_6088738551748760158[281] = 0;
   out_6088738551748760158[282] = 0;
   out_6088738551748760158[283] = 0;
   out_6088738551748760158[284] = 0;
   out_6088738551748760158[285] = 1;
   out_6088738551748760158[286] = 0;
   out_6088738551748760158[287] = 0;
   out_6088738551748760158[288] = 0;
   out_6088738551748760158[289] = 0;
   out_6088738551748760158[290] = 0;
   out_6088738551748760158[291] = 0;
   out_6088738551748760158[292] = 0;
   out_6088738551748760158[293] = 0;
   out_6088738551748760158[294] = 0;
   out_6088738551748760158[295] = 0;
   out_6088738551748760158[296] = 0;
   out_6088738551748760158[297] = 0;
   out_6088738551748760158[298] = 0;
   out_6088738551748760158[299] = 0;
   out_6088738551748760158[300] = 0;
   out_6088738551748760158[301] = 0;
   out_6088738551748760158[302] = 0;
   out_6088738551748760158[303] = 0;
   out_6088738551748760158[304] = 1;
   out_6088738551748760158[305] = 0;
   out_6088738551748760158[306] = 0;
   out_6088738551748760158[307] = 0;
   out_6088738551748760158[308] = 0;
   out_6088738551748760158[309] = 0;
   out_6088738551748760158[310] = 0;
   out_6088738551748760158[311] = 0;
   out_6088738551748760158[312] = 0;
   out_6088738551748760158[313] = 0;
   out_6088738551748760158[314] = 0;
   out_6088738551748760158[315] = 0;
   out_6088738551748760158[316] = 0;
   out_6088738551748760158[317] = 0;
   out_6088738551748760158[318] = 0;
   out_6088738551748760158[319] = 0;
   out_6088738551748760158[320] = 0;
   out_6088738551748760158[321] = 0;
   out_6088738551748760158[322] = 0;
   out_6088738551748760158[323] = 1;
}
void h_4(double *state, double *unused, double *out_2742355909746826294) {
   out_2742355909746826294[0] = state[6] + state[9];
   out_2742355909746826294[1] = state[7] + state[10];
   out_2742355909746826294[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_3203571547522250360) {
   out_3203571547522250360[0] = 0;
   out_3203571547522250360[1] = 0;
   out_3203571547522250360[2] = 0;
   out_3203571547522250360[3] = 0;
   out_3203571547522250360[4] = 0;
   out_3203571547522250360[5] = 0;
   out_3203571547522250360[6] = 1;
   out_3203571547522250360[7] = 0;
   out_3203571547522250360[8] = 0;
   out_3203571547522250360[9] = 1;
   out_3203571547522250360[10] = 0;
   out_3203571547522250360[11] = 0;
   out_3203571547522250360[12] = 0;
   out_3203571547522250360[13] = 0;
   out_3203571547522250360[14] = 0;
   out_3203571547522250360[15] = 0;
   out_3203571547522250360[16] = 0;
   out_3203571547522250360[17] = 0;
   out_3203571547522250360[18] = 0;
   out_3203571547522250360[19] = 0;
   out_3203571547522250360[20] = 0;
   out_3203571547522250360[21] = 0;
   out_3203571547522250360[22] = 0;
   out_3203571547522250360[23] = 0;
   out_3203571547522250360[24] = 0;
   out_3203571547522250360[25] = 1;
   out_3203571547522250360[26] = 0;
   out_3203571547522250360[27] = 0;
   out_3203571547522250360[28] = 1;
   out_3203571547522250360[29] = 0;
   out_3203571547522250360[30] = 0;
   out_3203571547522250360[31] = 0;
   out_3203571547522250360[32] = 0;
   out_3203571547522250360[33] = 0;
   out_3203571547522250360[34] = 0;
   out_3203571547522250360[35] = 0;
   out_3203571547522250360[36] = 0;
   out_3203571547522250360[37] = 0;
   out_3203571547522250360[38] = 0;
   out_3203571547522250360[39] = 0;
   out_3203571547522250360[40] = 0;
   out_3203571547522250360[41] = 0;
   out_3203571547522250360[42] = 0;
   out_3203571547522250360[43] = 0;
   out_3203571547522250360[44] = 1;
   out_3203571547522250360[45] = 0;
   out_3203571547522250360[46] = 0;
   out_3203571547522250360[47] = 1;
   out_3203571547522250360[48] = 0;
   out_3203571547522250360[49] = 0;
   out_3203571547522250360[50] = 0;
   out_3203571547522250360[51] = 0;
   out_3203571547522250360[52] = 0;
   out_3203571547522250360[53] = 0;
}
void h_10(double *state, double *unused, double *out_5392750946095808839) {
   out_5392750946095808839[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_5392750946095808839[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_5392750946095808839[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_6832887606116687430) {
   out_6832887606116687430[0] = 0;
   out_6832887606116687430[1] = 9.8100000000000005*cos(state[1]);
   out_6832887606116687430[2] = 0;
   out_6832887606116687430[3] = 0;
   out_6832887606116687430[4] = -state[8];
   out_6832887606116687430[5] = state[7];
   out_6832887606116687430[6] = 0;
   out_6832887606116687430[7] = state[5];
   out_6832887606116687430[8] = -state[4];
   out_6832887606116687430[9] = 0;
   out_6832887606116687430[10] = 0;
   out_6832887606116687430[11] = 0;
   out_6832887606116687430[12] = 1;
   out_6832887606116687430[13] = 0;
   out_6832887606116687430[14] = 0;
   out_6832887606116687430[15] = 1;
   out_6832887606116687430[16] = 0;
   out_6832887606116687430[17] = 0;
   out_6832887606116687430[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_6832887606116687430[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_6832887606116687430[20] = 0;
   out_6832887606116687430[21] = state[8];
   out_6832887606116687430[22] = 0;
   out_6832887606116687430[23] = -state[6];
   out_6832887606116687430[24] = -state[5];
   out_6832887606116687430[25] = 0;
   out_6832887606116687430[26] = state[3];
   out_6832887606116687430[27] = 0;
   out_6832887606116687430[28] = 0;
   out_6832887606116687430[29] = 0;
   out_6832887606116687430[30] = 0;
   out_6832887606116687430[31] = 1;
   out_6832887606116687430[32] = 0;
   out_6832887606116687430[33] = 0;
   out_6832887606116687430[34] = 1;
   out_6832887606116687430[35] = 0;
   out_6832887606116687430[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_6832887606116687430[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_6832887606116687430[38] = 0;
   out_6832887606116687430[39] = -state[7];
   out_6832887606116687430[40] = state[6];
   out_6832887606116687430[41] = 0;
   out_6832887606116687430[42] = state[4];
   out_6832887606116687430[43] = -state[3];
   out_6832887606116687430[44] = 0;
   out_6832887606116687430[45] = 0;
   out_6832887606116687430[46] = 0;
   out_6832887606116687430[47] = 0;
   out_6832887606116687430[48] = 0;
   out_6832887606116687430[49] = 0;
   out_6832887606116687430[50] = 1;
   out_6832887606116687430[51] = 0;
   out_6832887606116687430[52] = 0;
   out_6832887606116687430[53] = 1;
}
void h_13(double *state, double *unused, double *out_7827281880185644605) {
   out_7827281880185644605[0] = state[3];
   out_7827281880185644605[1] = state[4];
   out_7827281880185644605[2] = state[5];
}
void H_13(double *state, double *unused, double *out_8702277810082441) {
   out_8702277810082441[0] = 0;
   out_8702277810082441[1] = 0;
   out_8702277810082441[2] = 0;
   out_8702277810082441[3] = 1;
   out_8702277810082441[4] = 0;
   out_8702277810082441[5] = 0;
   out_8702277810082441[6] = 0;
   out_8702277810082441[7] = 0;
   out_8702277810082441[8] = 0;
   out_8702277810082441[9] = 0;
   out_8702277810082441[10] = 0;
   out_8702277810082441[11] = 0;
   out_8702277810082441[12] = 0;
   out_8702277810082441[13] = 0;
   out_8702277810082441[14] = 0;
   out_8702277810082441[15] = 0;
   out_8702277810082441[16] = 0;
   out_8702277810082441[17] = 0;
   out_8702277810082441[18] = 0;
   out_8702277810082441[19] = 0;
   out_8702277810082441[20] = 0;
   out_8702277810082441[21] = 0;
   out_8702277810082441[22] = 1;
   out_8702277810082441[23] = 0;
   out_8702277810082441[24] = 0;
   out_8702277810082441[25] = 0;
   out_8702277810082441[26] = 0;
   out_8702277810082441[27] = 0;
   out_8702277810082441[28] = 0;
   out_8702277810082441[29] = 0;
   out_8702277810082441[30] = 0;
   out_8702277810082441[31] = 0;
   out_8702277810082441[32] = 0;
   out_8702277810082441[33] = 0;
   out_8702277810082441[34] = 0;
   out_8702277810082441[35] = 0;
   out_8702277810082441[36] = 0;
   out_8702277810082441[37] = 0;
   out_8702277810082441[38] = 0;
   out_8702277810082441[39] = 0;
   out_8702277810082441[40] = 0;
   out_8702277810082441[41] = 1;
   out_8702277810082441[42] = 0;
   out_8702277810082441[43] = 0;
   out_8702277810082441[44] = 0;
   out_8702277810082441[45] = 0;
   out_8702277810082441[46] = 0;
   out_8702277810082441[47] = 0;
   out_8702277810082441[48] = 0;
   out_8702277810082441[49] = 0;
   out_8702277810082441[50] = 0;
   out_8702277810082441[51] = 0;
   out_8702277810082441[52] = 0;
   out_8702277810082441[53] = 0;
}
void h_14(double *state, double *unused, double *out_3917682265727873259) {
   out_3917682265727873259[0] = state[6];
   out_3917682265727873259[1] = state[7];
   out_3917682265727873259[2] = state[8];
}
void H_14(double *state, double *unused, double *out_759669308817234169) {
   out_759669308817234169[0] = 0;
   out_759669308817234169[1] = 0;
   out_759669308817234169[2] = 0;
   out_759669308817234169[3] = 0;
   out_759669308817234169[4] = 0;
   out_759669308817234169[5] = 0;
   out_759669308817234169[6] = 1;
   out_759669308817234169[7] = 0;
   out_759669308817234169[8] = 0;
   out_759669308817234169[9] = 0;
   out_759669308817234169[10] = 0;
   out_759669308817234169[11] = 0;
   out_759669308817234169[12] = 0;
   out_759669308817234169[13] = 0;
   out_759669308817234169[14] = 0;
   out_759669308817234169[15] = 0;
   out_759669308817234169[16] = 0;
   out_759669308817234169[17] = 0;
   out_759669308817234169[18] = 0;
   out_759669308817234169[19] = 0;
   out_759669308817234169[20] = 0;
   out_759669308817234169[21] = 0;
   out_759669308817234169[22] = 0;
   out_759669308817234169[23] = 0;
   out_759669308817234169[24] = 0;
   out_759669308817234169[25] = 1;
   out_759669308817234169[26] = 0;
   out_759669308817234169[27] = 0;
   out_759669308817234169[28] = 0;
   out_759669308817234169[29] = 0;
   out_759669308817234169[30] = 0;
   out_759669308817234169[31] = 0;
   out_759669308817234169[32] = 0;
   out_759669308817234169[33] = 0;
   out_759669308817234169[34] = 0;
   out_759669308817234169[35] = 0;
   out_759669308817234169[36] = 0;
   out_759669308817234169[37] = 0;
   out_759669308817234169[38] = 0;
   out_759669308817234169[39] = 0;
   out_759669308817234169[40] = 0;
   out_759669308817234169[41] = 0;
   out_759669308817234169[42] = 0;
   out_759669308817234169[43] = 0;
   out_759669308817234169[44] = 1;
   out_759669308817234169[45] = 0;
   out_759669308817234169[46] = 0;
   out_759669308817234169[47] = 0;
   out_759669308817234169[48] = 0;
   out_759669308817234169[49] = 0;
   out_759669308817234169[50] = 0;
   out_759669308817234169[51] = 0;
   out_759669308817234169[52] = 0;
   out_759669308817234169[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_7113141565155944071) {
  err_fun(nom_x, delta_x, out_7113141565155944071);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_4273806753012627861) {
  inv_err_fun(nom_x, true_x, out_4273806753012627861);
}
void pose_H_mod_fun(double *state, double *out_4327706851715669235) {
  H_mod_fun(state, out_4327706851715669235);
}
void pose_f_fun(double *state, double dt, double *out_497730658810754078) {
  f_fun(state,  dt, out_497730658810754078);
}
void pose_F_fun(double *state, double dt, double *out_6088738551748760158) {
  F_fun(state,  dt, out_6088738551748760158);
}
void pose_h_4(double *state, double *unused, double *out_2742355909746826294) {
  h_4(state, unused, out_2742355909746826294);
}
void pose_H_4(double *state, double *unused, double *out_3203571547522250360) {
  H_4(state, unused, out_3203571547522250360);
}
void pose_h_10(double *state, double *unused, double *out_5392750946095808839) {
  h_10(state, unused, out_5392750946095808839);
}
void pose_H_10(double *state, double *unused, double *out_6832887606116687430) {
  H_10(state, unused, out_6832887606116687430);
}
void pose_h_13(double *state, double *unused, double *out_7827281880185644605) {
  h_13(state, unused, out_7827281880185644605);
}
void pose_H_13(double *state, double *unused, double *out_8702277810082441) {
  H_13(state, unused, out_8702277810082441);
}
void pose_h_14(double *state, double *unused, double *out_3917682265727873259) {
  h_14(state, unused, out_3917682265727873259);
}
void pose_H_14(double *state, double *unused, double *out_759669308817234169) {
  H_14(state, unused, out_759669308817234169);
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
