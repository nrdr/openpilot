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
void err_fun(double *nom_x, double *delta_x, double *out_1395619254280121889) {
   out_1395619254280121889[0] = delta_x[0] + nom_x[0];
   out_1395619254280121889[1] = delta_x[1] + nom_x[1];
   out_1395619254280121889[2] = delta_x[2] + nom_x[2];
   out_1395619254280121889[3] = delta_x[3] + nom_x[3];
   out_1395619254280121889[4] = delta_x[4] + nom_x[4];
   out_1395619254280121889[5] = delta_x[5] + nom_x[5];
   out_1395619254280121889[6] = delta_x[6] + nom_x[6];
   out_1395619254280121889[7] = delta_x[7] + nom_x[7];
   out_1395619254280121889[8] = delta_x[8] + nom_x[8];
   out_1395619254280121889[9] = delta_x[9] + nom_x[9];
   out_1395619254280121889[10] = delta_x[10] + nom_x[10];
   out_1395619254280121889[11] = delta_x[11] + nom_x[11];
   out_1395619254280121889[12] = delta_x[12] + nom_x[12];
   out_1395619254280121889[13] = delta_x[13] + nom_x[13];
   out_1395619254280121889[14] = delta_x[14] + nom_x[14];
   out_1395619254280121889[15] = delta_x[15] + nom_x[15];
   out_1395619254280121889[16] = delta_x[16] + nom_x[16];
   out_1395619254280121889[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_214512694638000517) {
   out_214512694638000517[0] = -nom_x[0] + true_x[0];
   out_214512694638000517[1] = -nom_x[1] + true_x[1];
   out_214512694638000517[2] = -nom_x[2] + true_x[2];
   out_214512694638000517[3] = -nom_x[3] + true_x[3];
   out_214512694638000517[4] = -nom_x[4] + true_x[4];
   out_214512694638000517[5] = -nom_x[5] + true_x[5];
   out_214512694638000517[6] = -nom_x[6] + true_x[6];
   out_214512694638000517[7] = -nom_x[7] + true_x[7];
   out_214512694638000517[8] = -nom_x[8] + true_x[8];
   out_214512694638000517[9] = -nom_x[9] + true_x[9];
   out_214512694638000517[10] = -nom_x[10] + true_x[10];
   out_214512694638000517[11] = -nom_x[11] + true_x[11];
   out_214512694638000517[12] = -nom_x[12] + true_x[12];
   out_214512694638000517[13] = -nom_x[13] + true_x[13];
   out_214512694638000517[14] = -nom_x[14] + true_x[14];
   out_214512694638000517[15] = -nom_x[15] + true_x[15];
   out_214512694638000517[16] = -nom_x[16] + true_x[16];
   out_214512694638000517[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_4178491048942550488) {
   out_4178491048942550488[0] = 1.0;
   out_4178491048942550488[1] = 0.0;
   out_4178491048942550488[2] = 0.0;
   out_4178491048942550488[3] = 0.0;
   out_4178491048942550488[4] = 0.0;
   out_4178491048942550488[5] = 0.0;
   out_4178491048942550488[6] = 0.0;
   out_4178491048942550488[7] = 0.0;
   out_4178491048942550488[8] = 0.0;
   out_4178491048942550488[9] = 0.0;
   out_4178491048942550488[10] = 0.0;
   out_4178491048942550488[11] = 0.0;
   out_4178491048942550488[12] = 0.0;
   out_4178491048942550488[13] = 0.0;
   out_4178491048942550488[14] = 0.0;
   out_4178491048942550488[15] = 0.0;
   out_4178491048942550488[16] = 0.0;
   out_4178491048942550488[17] = 0.0;
   out_4178491048942550488[18] = 0.0;
   out_4178491048942550488[19] = 1.0;
   out_4178491048942550488[20] = 0.0;
   out_4178491048942550488[21] = 0.0;
   out_4178491048942550488[22] = 0.0;
   out_4178491048942550488[23] = 0.0;
   out_4178491048942550488[24] = 0.0;
   out_4178491048942550488[25] = 0.0;
   out_4178491048942550488[26] = 0.0;
   out_4178491048942550488[27] = 0.0;
   out_4178491048942550488[28] = 0.0;
   out_4178491048942550488[29] = 0.0;
   out_4178491048942550488[30] = 0.0;
   out_4178491048942550488[31] = 0.0;
   out_4178491048942550488[32] = 0.0;
   out_4178491048942550488[33] = 0.0;
   out_4178491048942550488[34] = 0.0;
   out_4178491048942550488[35] = 0.0;
   out_4178491048942550488[36] = 0.0;
   out_4178491048942550488[37] = 0.0;
   out_4178491048942550488[38] = 1.0;
   out_4178491048942550488[39] = 0.0;
   out_4178491048942550488[40] = 0.0;
   out_4178491048942550488[41] = 0.0;
   out_4178491048942550488[42] = 0.0;
   out_4178491048942550488[43] = 0.0;
   out_4178491048942550488[44] = 0.0;
   out_4178491048942550488[45] = 0.0;
   out_4178491048942550488[46] = 0.0;
   out_4178491048942550488[47] = 0.0;
   out_4178491048942550488[48] = 0.0;
   out_4178491048942550488[49] = 0.0;
   out_4178491048942550488[50] = 0.0;
   out_4178491048942550488[51] = 0.0;
   out_4178491048942550488[52] = 0.0;
   out_4178491048942550488[53] = 0.0;
   out_4178491048942550488[54] = 0.0;
   out_4178491048942550488[55] = 0.0;
   out_4178491048942550488[56] = 0.0;
   out_4178491048942550488[57] = 1.0;
   out_4178491048942550488[58] = 0.0;
   out_4178491048942550488[59] = 0.0;
   out_4178491048942550488[60] = 0.0;
   out_4178491048942550488[61] = 0.0;
   out_4178491048942550488[62] = 0.0;
   out_4178491048942550488[63] = 0.0;
   out_4178491048942550488[64] = 0.0;
   out_4178491048942550488[65] = 0.0;
   out_4178491048942550488[66] = 0.0;
   out_4178491048942550488[67] = 0.0;
   out_4178491048942550488[68] = 0.0;
   out_4178491048942550488[69] = 0.0;
   out_4178491048942550488[70] = 0.0;
   out_4178491048942550488[71] = 0.0;
   out_4178491048942550488[72] = 0.0;
   out_4178491048942550488[73] = 0.0;
   out_4178491048942550488[74] = 0.0;
   out_4178491048942550488[75] = 0.0;
   out_4178491048942550488[76] = 1.0;
   out_4178491048942550488[77] = 0.0;
   out_4178491048942550488[78] = 0.0;
   out_4178491048942550488[79] = 0.0;
   out_4178491048942550488[80] = 0.0;
   out_4178491048942550488[81] = 0.0;
   out_4178491048942550488[82] = 0.0;
   out_4178491048942550488[83] = 0.0;
   out_4178491048942550488[84] = 0.0;
   out_4178491048942550488[85] = 0.0;
   out_4178491048942550488[86] = 0.0;
   out_4178491048942550488[87] = 0.0;
   out_4178491048942550488[88] = 0.0;
   out_4178491048942550488[89] = 0.0;
   out_4178491048942550488[90] = 0.0;
   out_4178491048942550488[91] = 0.0;
   out_4178491048942550488[92] = 0.0;
   out_4178491048942550488[93] = 0.0;
   out_4178491048942550488[94] = 0.0;
   out_4178491048942550488[95] = 1.0;
   out_4178491048942550488[96] = 0.0;
   out_4178491048942550488[97] = 0.0;
   out_4178491048942550488[98] = 0.0;
   out_4178491048942550488[99] = 0.0;
   out_4178491048942550488[100] = 0.0;
   out_4178491048942550488[101] = 0.0;
   out_4178491048942550488[102] = 0.0;
   out_4178491048942550488[103] = 0.0;
   out_4178491048942550488[104] = 0.0;
   out_4178491048942550488[105] = 0.0;
   out_4178491048942550488[106] = 0.0;
   out_4178491048942550488[107] = 0.0;
   out_4178491048942550488[108] = 0.0;
   out_4178491048942550488[109] = 0.0;
   out_4178491048942550488[110] = 0.0;
   out_4178491048942550488[111] = 0.0;
   out_4178491048942550488[112] = 0.0;
   out_4178491048942550488[113] = 0.0;
   out_4178491048942550488[114] = 1.0;
   out_4178491048942550488[115] = 0.0;
   out_4178491048942550488[116] = 0.0;
   out_4178491048942550488[117] = 0.0;
   out_4178491048942550488[118] = 0.0;
   out_4178491048942550488[119] = 0.0;
   out_4178491048942550488[120] = 0.0;
   out_4178491048942550488[121] = 0.0;
   out_4178491048942550488[122] = 0.0;
   out_4178491048942550488[123] = 0.0;
   out_4178491048942550488[124] = 0.0;
   out_4178491048942550488[125] = 0.0;
   out_4178491048942550488[126] = 0.0;
   out_4178491048942550488[127] = 0.0;
   out_4178491048942550488[128] = 0.0;
   out_4178491048942550488[129] = 0.0;
   out_4178491048942550488[130] = 0.0;
   out_4178491048942550488[131] = 0.0;
   out_4178491048942550488[132] = 0.0;
   out_4178491048942550488[133] = 1.0;
   out_4178491048942550488[134] = 0.0;
   out_4178491048942550488[135] = 0.0;
   out_4178491048942550488[136] = 0.0;
   out_4178491048942550488[137] = 0.0;
   out_4178491048942550488[138] = 0.0;
   out_4178491048942550488[139] = 0.0;
   out_4178491048942550488[140] = 0.0;
   out_4178491048942550488[141] = 0.0;
   out_4178491048942550488[142] = 0.0;
   out_4178491048942550488[143] = 0.0;
   out_4178491048942550488[144] = 0.0;
   out_4178491048942550488[145] = 0.0;
   out_4178491048942550488[146] = 0.0;
   out_4178491048942550488[147] = 0.0;
   out_4178491048942550488[148] = 0.0;
   out_4178491048942550488[149] = 0.0;
   out_4178491048942550488[150] = 0.0;
   out_4178491048942550488[151] = 0.0;
   out_4178491048942550488[152] = 1.0;
   out_4178491048942550488[153] = 0.0;
   out_4178491048942550488[154] = 0.0;
   out_4178491048942550488[155] = 0.0;
   out_4178491048942550488[156] = 0.0;
   out_4178491048942550488[157] = 0.0;
   out_4178491048942550488[158] = 0.0;
   out_4178491048942550488[159] = 0.0;
   out_4178491048942550488[160] = 0.0;
   out_4178491048942550488[161] = 0.0;
   out_4178491048942550488[162] = 0.0;
   out_4178491048942550488[163] = 0.0;
   out_4178491048942550488[164] = 0.0;
   out_4178491048942550488[165] = 0.0;
   out_4178491048942550488[166] = 0.0;
   out_4178491048942550488[167] = 0.0;
   out_4178491048942550488[168] = 0.0;
   out_4178491048942550488[169] = 0.0;
   out_4178491048942550488[170] = 0.0;
   out_4178491048942550488[171] = 1.0;
   out_4178491048942550488[172] = 0.0;
   out_4178491048942550488[173] = 0.0;
   out_4178491048942550488[174] = 0.0;
   out_4178491048942550488[175] = 0.0;
   out_4178491048942550488[176] = 0.0;
   out_4178491048942550488[177] = 0.0;
   out_4178491048942550488[178] = 0.0;
   out_4178491048942550488[179] = 0.0;
   out_4178491048942550488[180] = 0.0;
   out_4178491048942550488[181] = 0.0;
   out_4178491048942550488[182] = 0.0;
   out_4178491048942550488[183] = 0.0;
   out_4178491048942550488[184] = 0.0;
   out_4178491048942550488[185] = 0.0;
   out_4178491048942550488[186] = 0.0;
   out_4178491048942550488[187] = 0.0;
   out_4178491048942550488[188] = 0.0;
   out_4178491048942550488[189] = 0.0;
   out_4178491048942550488[190] = 1.0;
   out_4178491048942550488[191] = 0.0;
   out_4178491048942550488[192] = 0.0;
   out_4178491048942550488[193] = 0.0;
   out_4178491048942550488[194] = 0.0;
   out_4178491048942550488[195] = 0.0;
   out_4178491048942550488[196] = 0.0;
   out_4178491048942550488[197] = 0.0;
   out_4178491048942550488[198] = 0.0;
   out_4178491048942550488[199] = 0.0;
   out_4178491048942550488[200] = 0.0;
   out_4178491048942550488[201] = 0.0;
   out_4178491048942550488[202] = 0.0;
   out_4178491048942550488[203] = 0.0;
   out_4178491048942550488[204] = 0.0;
   out_4178491048942550488[205] = 0.0;
   out_4178491048942550488[206] = 0.0;
   out_4178491048942550488[207] = 0.0;
   out_4178491048942550488[208] = 0.0;
   out_4178491048942550488[209] = 1.0;
   out_4178491048942550488[210] = 0.0;
   out_4178491048942550488[211] = 0.0;
   out_4178491048942550488[212] = 0.0;
   out_4178491048942550488[213] = 0.0;
   out_4178491048942550488[214] = 0.0;
   out_4178491048942550488[215] = 0.0;
   out_4178491048942550488[216] = 0.0;
   out_4178491048942550488[217] = 0.0;
   out_4178491048942550488[218] = 0.0;
   out_4178491048942550488[219] = 0.0;
   out_4178491048942550488[220] = 0.0;
   out_4178491048942550488[221] = 0.0;
   out_4178491048942550488[222] = 0.0;
   out_4178491048942550488[223] = 0.0;
   out_4178491048942550488[224] = 0.0;
   out_4178491048942550488[225] = 0.0;
   out_4178491048942550488[226] = 0.0;
   out_4178491048942550488[227] = 0.0;
   out_4178491048942550488[228] = 1.0;
   out_4178491048942550488[229] = 0.0;
   out_4178491048942550488[230] = 0.0;
   out_4178491048942550488[231] = 0.0;
   out_4178491048942550488[232] = 0.0;
   out_4178491048942550488[233] = 0.0;
   out_4178491048942550488[234] = 0.0;
   out_4178491048942550488[235] = 0.0;
   out_4178491048942550488[236] = 0.0;
   out_4178491048942550488[237] = 0.0;
   out_4178491048942550488[238] = 0.0;
   out_4178491048942550488[239] = 0.0;
   out_4178491048942550488[240] = 0.0;
   out_4178491048942550488[241] = 0.0;
   out_4178491048942550488[242] = 0.0;
   out_4178491048942550488[243] = 0.0;
   out_4178491048942550488[244] = 0.0;
   out_4178491048942550488[245] = 0.0;
   out_4178491048942550488[246] = 0.0;
   out_4178491048942550488[247] = 1.0;
   out_4178491048942550488[248] = 0.0;
   out_4178491048942550488[249] = 0.0;
   out_4178491048942550488[250] = 0.0;
   out_4178491048942550488[251] = 0.0;
   out_4178491048942550488[252] = 0.0;
   out_4178491048942550488[253] = 0.0;
   out_4178491048942550488[254] = 0.0;
   out_4178491048942550488[255] = 0.0;
   out_4178491048942550488[256] = 0.0;
   out_4178491048942550488[257] = 0.0;
   out_4178491048942550488[258] = 0.0;
   out_4178491048942550488[259] = 0.0;
   out_4178491048942550488[260] = 0.0;
   out_4178491048942550488[261] = 0.0;
   out_4178491048942550488[262] = 0.0;
   out_4178491048942550488[263] = 0.0;
   out_4178491048942550488[264] = 0.0;
   out_4178491048942550488[265] = 0.0;
   out_4178491048942550488[266] = 1.0;
   out_4178491048942550488[267] = 0.0;
   out_4178491048942550488[268] = 0.0;
   out_4178491048942550488[269] = 0.0;
   out_4178491048942550488[270] = 0.0;
   out_4178491048942550488[271] = 0.0;
   out_4178491048942550488[272] = 0.0;
   out_4178491048942550488[273] = 0.0;
   out_4178491048942550488[274] = 0.0;
   out_4178491048942550488[275] = 0.0;
   out_4178491048942550488[276] = 0.0;
   out_4178491048942550488[277] = 0.0;
   out_4178491048942550488[278] = 0.0;
   out_4178491048942550488[279] = 0.0;
   out_4178491048942550488[280] = 0.0;
   out_4178491048942550488[281] = 0.0;
   out_4178491048942550488[282] = 0.0;
   out_4178491048942550488[283] = 0.0;
   out_4178491048942550488[284] = 0.0;
   out_4178491048942550488[285] = 1.0;
   out_4178491048942550488[286] = 0.0;
   out_4178491048942550488[287] = 0.0;
   out_4178491048942550488[288] = 0.0;
   out_4178491048942550488[289] = 0.0;
   out_4178491048942550488[290] = 0.0;
   out_4178491048942550488[291] = 0.0;
   out_4178491048942550488[292] = 0.0;
   out_4178491048942550488[293] = 0.0;
   out_4178491048942550488[294] = 0.0;
   out_4178491048942550488[295] = 0.0;
   out_4178491048942550488[296] = 0.0;
   out_4178491048942550488[297] = 0.0;
   out_4178491048942550488[298] = 0.0;
   out_4178491048942550488[299] = 0.0;
   out_4178491048942550488[300] = 0.0;
   out_4178491048942550488[301] = 0.0;
   out_4178491048942550488[302] = 0.0;
   out_4178491048942550488[303] = 0.0;
   out_4178491048942550488[304] = 1.0;
   out_4178491048942550488[305] = 0.0;
   out_4178491048942550488[306] = 0.0;
   out_4178491048942550488[307] = 0.0;
   out_4178491048942550488[308] = 0.0;
   out_4178491048942550488[309] = 0.0;
   out_4178491048942550488[310] = 0.0;
   out_4178491048942550488[311] = 0.0;
   out_4178491048942550488[312] = 0.0;
   out_4178491048942550488[313] = 0.0;
   out_4178491048942550488[314] = 0.0;
   out_4178491048942550488[315] = 0.0;
   out_4178491048942550488[316] = 0.0;
   out_4178491048942550488[317] = 0.0;
   out_4178491048942550488[318] = 0.0;
   out_4178491048942550488[319] = 0.0;
   out_4178491048942550488[320] = 0.0;
   out_4178491048942550488[321] = 0.0;
   out_4178491048942550488[322] = 0.0;
   out_4178491048942550488[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_6955059668244195066) {
   out_6955059668244195066[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_6955059668244195066[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_6955059668244195066[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_6955059668244195066[3] = dt*state[12] + state[3];
   out_6955059668244195066[4] = dt*state[13] + state[4];
   out_6955059668244195066[5] = dt*state[14] + state[5];
   out_6955059668244195066[6] = state[6];
   out_6955059668244195066[7] = state[7];
   out_6955059668244195066[8] = state[8];
   out_6955059668244195066[9] = state[9];
   out_6955059668244195066[10] = state[10];
   out_6955059668244195066[11] = state[11];
   out_6955059668244195066[12] = state[12];
   out_6955059668244195066[13] = state[13];
   out_6955059668244195066[14] = state[14];
   out_6955059668244195066[15] = state[15];
   out_6955059668244195066[16] = state[16];
   out_6955059668244195066[17] = state[17];
}
void F_fun(double *state, double dt, double *out_5780055978525304403) {
   out_5780055978525304403[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5780055978525304403[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5780055978525304403[2] = 0;
   out_5780055978525304403[3] = 0;
   out_5780055978525304403[4] = 0;
   out_5780055978525304403[5] = 0;
   out_5780055978525304403[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5780055978525304403[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5780055978525304403[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5780055978525304403[9] = 0;
   out_5780055978525304403[10] = 0;
   out_5780055978525304403[11] = 0;
   out_5780055978525304403[12] = 0;
   out_5780055978525304403[13] = 0;
   out_5780055978525304403[14] = 0;
   out_5780055978525304403[15] = 0;
   out_5780055978525304403[16] = 0;
   out_5780055978525304403[17] = 0;
   out_5780055978525304403[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5780055978525304403[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5780055978525304403[20] = 0;
   out_5780055978525304403[21] = 0;
   out_5780055978525304403[22] = 0;
   out_5780055978525304403[23] = 0;
   out_5780055978525304403[24] = 0;
   out_5780055978525304403[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5780055978525304403[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5780055978525304403[27] = 0;
   out_5780055978525304403[28] = 0;
   out_5780055978525304403[29] = 0;
   out_5780055978525304403[30] = 0;
   out_5780055978525304403[31] = 0;
   out_5780055978525304403[32] = 0;
   out_5780055978525304403[33] = 0;
   out_5780055978525304403[34] = 0;
   out_5780055978525304403[35] = 0;
   out_5780055978525304403[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5780055978525304403[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5780055978525304403[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5780055978525304403[39] = 0;
   out_5780055978525304403[40] = 0;
   out_5780055978525304403[41] = 0;
   out_5780055978525304403[42] = 0;
   out_5780055978525304403[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5780055978525304403[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5780055978525304403[45] = 0;
   out_5780055978525304403[46] = 0;
   out_5780055978525304403[47] = 0;
   out_5780055978525304403[48] = 0;
   out_5780055978525304403[49] = 0;
   out_5780055978525304403[50] = 0;
   out_5780055978525304403[51] = 0;
   out_5780055978525304403[52] = 0;
   out_5780055978525304403[53] = 0;
   out_5780055978525304403[54] = 0;
   out_5780055978525304403[55] = 0;
   out_5780055978525304403[56] = 0;
   out_5780055978525304403[57] = 1;
   out_5780055978525304403[58] = 0;
   out_5780055978525304403[59] = 0;
   out_5780055978525304403[60] = 0;
   out_5780055978525304403[61] = 0;
   out_5780055978525304403[62] = 0;
   out_5780055978525304403[63] = 0;
   out_5780055978525304403[64] = 0;
   out_5780055978525304403[65] = 0;
   out_5780055978525304403[66] = dt;
   out_5780055978525304403[67] = 0;
   out_5780055978525304403[68] = 0;
   out_5780055978525304403[69] = 0;
   out_5780055978525304403[70] = 0;
   out_5780055978525304403[71] = 0;
   out_5780055978525304403[72] = 0;
   out_5780055978525304403[73] = 0;
   out_5780055978525304403[74] = 0;
   out_5780055978525304403[75] = 0;
   out_5780055978525304403[76] = 1;
   out_5780055978525304403[77] = 0;
   out_5780055978525304403[78] = 0;
   out_5780055978525304403[79] = 0;
   out_5780055978525304403[80] = 0;
   out_5780055978525304403[81] = 0;
   out_5780055978525304403[82] = 0;
   out_5780055978525304403[83] = 0;
   out_5780055978525304403[84] = 0;
   out_5780055978525304403[85] = dt;
   out_5780055978525304403[86] = 0;
   out_5780055978525304403[87] = 0;
   out_5780055978525304403[88] = 0;
   out_5780055978525304403[89] = 0;
   out_5780055978525304403[90] = 0;
   out_5780055978525304403[91] = 0;
   out_5780055978525304403[92] = 0;
   out_5780055978525304403[93] = 0;
   out_5780055978525304403[94] = 0;
   out_5780055978525304403[95] = 1;
   out_5780055978525304403[96] = 0;
   out_5780055978525304403[97] = 0;
   out_5780055978525304403[98] = 0;
   out_5780055978525304403[99] = 0;
   out_5780055978525304403[100] = 0;
   out_5780055978525304403[101] = 0;
   out_5780055978525304403[102] = 0;
   out_5780055978525304403[103] = 0;
   out_5780055978525304403[104] = dt;
   out_5780055978525304403[105] = 0;
   out_5780055978525304403[106] = 0;
   out_5780055978525304403[107] = 0;
   out_5780055978525304403[108] = 0;
   out_5780055978525304403[109] = 0;
   out_5780055978525304403[110] = 0;
   out_5780055978525304403[111] = 0;
   out_5780055978525304403[112] = 0;
   out_5780055978525304403[113] = 0;
   out_5780055978525304403[114] = 1;
   out_5780055978525304403[115] = 0;
   out_5780055978525304403[116] = 0;
   out_5780055978525304403[117] = 0;
   out_5780055978525304403[118] = 0;
   out_5780055978525304403[119] = 0;
   out_5780055978525304403[120] = 0;
   out_5780055978525304403[121] = 0;
   out_5780055978525304403[122] = 0;
   out_5780055978525304403[123] = 0;
   out_5780055978525304403[124] = 0;
   out_5780055978525304403[125] = 0;
   out_5780055978525304403[126] = 0;
   out_5780055978525304403[127] = 0;
   out_5780055978525304403[128] = 0;
   out_5780055978525304403[129] = 0;
   out_5780055978525304403[130] = 0;
   out_5780055978525304403[131] = 0;
   out_5780055978525304403[132] = 0;
   out_5780055978525304403[133] = 1;
   out_5780055978525304403[134] = 0;
   out_5780055978525304403[135] = 0;
   out_5780055978525304403[136] = 0;
   out_5780055978525304403[137] = 0;
   out_5780055978525304403[138] = 0;
   out_5780055978525304403[139] = 0;
   out_5780055978525304403[140] = 0;
   out_5780055978525304403[141] = 0;
   out_5780055978525304403[142] = 0;
   out_5780055978525304403[143] = 0;
   out_5780055978525304403[144] = 0;
   out_5780055978525304403[145] = 0;
   out_5780055978525304403[146] = 0;
   out_5780055978525304403[147] = 0;
   out_5780055978525304403[148] = 0;
   out_5780055978525304403[149] = 0;
   out_5780055978525304403[150] = 0;
   out_5780055978525304403[151] = 0;
   out_5780055978525304403[152] = 1;
   out_5780055978525304403[153] = 0;
   out_5780055978525304403[154] = 0;
   out_5780055978525304403[155] = 0;
   out_5780055978525304403[156] = 0;
   out_5780055978525304403[157] = 0;
   out_5780055978525304403[158] = 0;
   out_5780055978525304403[159] = 0;
   out_5780055978525304403[160] = 0;
   out_5780055978525304403[161] = 0;
   out_5780055978525304403[162] = 0;
   out_5780055978525304403[163] = 0;
   out_5780055978525304403[164] = 0;
   out_5780055978525304403[165] = 0;
   out_5780055978525304403[166] = 0;
   out_5780055978525304403[167] = 0;
   out_5780055978525304403[168] = 0;
   out_5780055978525304403[169] = 0;
   out_5780055978525304403[170] = 0;
   out_5780055978525304403[171] = 1;
   out_5780055978525304403[172] = 0;
   out_5780055978525304403[173] = 0;
   out_5780055978525304403[174] = 0;
   out_5780055978525304403[175] = 0;
   out_5780055978525304403[176] = 0;
   out_5780055978525304403[177] = 0;
   out_5780055978525304403[178] = 0;
   out_5780055978525304403[179] = 0;
   out_5780055978525304403[180] = 0;
   out_5780055978525304403[181] = 0;
   out_5780055978525304403[182] = 0;
   out_5780055978525304403[183] = 0;
   out_5780055978525304403[184] = 0;
   out_5780055978525304403[185] = 0;
   out_5780055978525304403[186] = 0;
   out_5780055978525304403[187] = 0;
   out_5780055978525304403[188] = 0;
   out_5780055978525304403[189] = 0;
   out_5780055978525304403[190] = 1;
   out_5780055978525304403[191] = 0;
   out_5780055978525304403[192] = 0;
   out_5780055978525304403[193] = 0;
   out_5780055978525304403[194] = 0;
   out_5780055978525304403[195] = 0;
   out_5780055978525304403[196] = 0;
   out_5780055978525304403[197] = 0;
   out_5780055978525304403[198] = 0;
   out_5780055978525304403[199] = 0;
   out_5780055978525304403[200] = 0;
   out_5780055978525304403[201] = 0;
   out_5780055978525304403[202] = 0;
   out_5780055978525304403[203] = 0;
   out_5780055978525304403[204] = 0;
   out_5780055978525304403[205] = 0;
   out_5780055978525304403[206] = 0;
   out_5780055978525304403[207] = 0;
   out_5780055978525304403[208] = 0;
   out_5780055978525304403[209] = 1;
   out_5780055978525304403[210] = 0;
   out_5780055978525304403[211] = 0;
   out_5780055978525304403[212] = 0;
   out_5780055978525304403[213] = 0;
   out_5780055978525304403[214] = 0;
   out_5780055978525304403[215] = 0;
   out_5780055978525304403[216] = 0;
   out_5780055978525304403[217] = 0;
   out_5780055978525304403[218] = 0;
   out_5780055978525304403[219] = 0;
   out_5780055978525304403[220] = 0;
   out_5780055978525304403[221] = 0;
   out_5780055978525304403[222] = 0;
   out_5780055978525304403[223] = 0;
   out_5780055978525304403[224] = 0;
   out_5780055978525304403[225] = 0;
   out_5780055978525304403[226] = 0;
   out_5780055978525304403[227] = 0;
   out_5780055978525304403[228] = 1;
   out_5780055978525304403[229] = 0;
   out_5780055978525304403[230] = 0;
   out_5780055978525304403[231] = 0;
   out_5780055978525304403[232] = 0;
   out_5780055978525304403[233] = 0;
   out_5780055978525304403[234] = 0;
   out_5780055978525304403[235] = 0;
   out_5780055978525304403[236] = 0;
   out_5780055978525304403[237] = 0;
   out_5780055978525304403[238] = 0;
   out_5780055978525304403[239] = 0;
   out_5780055978525304403[240] = 0;
   out_5780055978525304403[241] = 0;
   out_5780055978525304403[242] = 0;
   out_5780055978525304403[243] = 0;
   out_5780055978525304403[244] = 0;
   out_5780055978525304403[245] = 0;
   out_5780055978525304403[246] = 0;
   out_5780055978525304403[247] = 1;
   out_5780055978525304403[248] = 0;
   out_5780055978525304403[249] = 0;
   out_5780055978525304403[250] = 0;
   out_5780055978525304403[251] = 0;
   out_5780055978525304403[252] = 0;
   out_5780055978525304403[253] = 0;
   out_5780055978525304403[254] = 0;
   out_5780055978525304403[255] = 0;
   out_5780055978525304403[256] = 0;
   out_5780055978525304403[257] = 0;
   out_5780055978525304403[258] = 0;
   out_5780055978525304403[259] = 0;
   out_5780055978525304403[260] = 0;
   out_5780055978525304403[261] = 0;
   out_5780055978525304403[262] = 0;
   out_5780055978525304403[263] = 0;
   out_5780055978525304403[264] = 0;
   out_5780055978525304403[265] = 0;
   out_5780055978525304403[266] = 1;
   out_5780055978525304403[267] = 0;
   out_5780055978525304403[268] = 0;
   out_5780055978525304403[269] = 0;
   out_5780055978525304403[270] = 0;
   out_5780055978525304403[271] = 0;
   out_5780055978525304403[272] = 0;
   out_5780055978525304403[273] = 0;
   out_5780055978525304403[274] = 0;
   out_5780055978525304403[275] = 0;
   out_5780055978525304403[276] = 0;
   out_5780055978525304403[277] = 0;
   out_5780055978525304403[278] = 0;
   out_5780055978525304403[279] = 0;
   out_5780055978525304403[280] = 0;
   out_5780055978525304403[281] = 0;
   out_5780055978525304403[282] = 0;
   out_5780055978525304403[283] = 0;
   out_5780055978525304403[284] = 0;
   out_5780055978525304403[285] = 1;
   out_5780055978525304403[286] = 0;
   out_5780055978525304403[287] = 0;
   out_5780055978525304403[288] = 0;
   out_5780055978525304403[289] = 0;
   out_5780055978525304403[290] = 0;
   out_5780055978525304403[291] = 0;
   out_5780055978525304403[292] = 0;
   out_5780055978525304403[293] = 0;
   out_5780055978525304403[294] = 0;
   out_5780055978525304403[295] = 0;
   out_5780055978525304403[296] = 0;
   out_5780055978525304403[297] = 0;
   out_5780055978525304403[298] = 0;
   out_5780055978525304403[299] = 0;
   out_5780055978525304403[300] = 0;
   out_5780055978525304403[301] = 0;
   out_5780055978525304403[302] = 0;
   out_5780055978525304403[303] = 0;
   out_5780055978525304403[304] = 1;
   out_5780055978525304403[305] = 0;
   out_5780055978525304403[306] = 0;
   out_5780055978525304403[307] = 0;
   out_5780055978525304403[308] = 0;
   out_5780055978525304403[309] = 0;
   out_5780055978525304403[310] = 0;
   out_5780055978525304403[311] = 0;
   out_5780055978525304403[312] = 0;
   out_5780055978525304403[313] = 0;
   out_5780055978525304403[314] = 0;
   out_5780055978525304403[315] = 0;
   out_5780055978525304403[316] = 0;
   out_5780055978525304403[317] = 0;
   out_5780055978525304403[318] = 0;
   out_5780055978525304403[319] = 0;
   out_5780055978525304403[320] = 0;
   out_5780055978525304403[321] = 0;
   out_5780055978525304403[322] = 0;
   out_5780055978525304403[323] = 1;
}
void h_4(double *state, double *unused, double *out_4735577956641194937) {
   out_4735577956641194937[0] = state[6] + state[9];
   out_4735577956641194937[1] = state[7] + state[10];
   out_4735577956641194937[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_2358792323036253627) {
   out_2358792323036253627[0] = 0;
   out_2358792323036253627[1] = 0;
   out_2358792323036253627[2] = 0;
   out_2358792323036253627[3] = 0;
   out_2358792323036253627[4] = 0;
   out_2358792323036253627[5] = 0;
   out_2358792323036253627[6] = 1;
   out_2358792323036253627[7] = 0;
   out_2358792323036253627[8] = 0;
   out_2358792323036253627[9] = 1;
   out_2358792323036253627[10] = 0;
   out_2358792323036253627[11] = 0;
   out_2358792323036253627[12] = 0;
   out_2358792323036253627[13] = 0;
   out_2358792323036253627[14] = 0;
   out_2358792323036253627[15] = 0;
   out_2358792323036253627[16] = 0;
   out_2358792323036253627[17] = 0;
   out_2358792323036253627[18] = 0;
   out_2358792323036253627[19] = 0;
   out_2358792323036253627[20] = 0;
   out_2358792323036253627[21] = 0;
   out_2358792323036253627[22] = 0;
   out_2358792323036253627[23] = 0;
   out_2358792323036253627[24] = 0;
   out_2358792323036253627[25] = 1;
   out_2358792323036253627[26] = 0;
   out_2358792323036253627[27] = 0;
   out_2358792323036253627[28] = 1;
   out_2358792323036253627[29] = 0;
   out_2358792323036253627[30] = 0;
   out_2358792323036253627[31] = 0;
   out_2358792323036253627[32] = 0;
   out_2358792323036253627[33] = 0;
   out_2358792323036253627[34] = 0;
   out_2358792323036253627[35] = 0;
   out_2358792323036253627[36] = 0;
   out_2358792323036253627[37] = 0;
   out_2358792323036253627[38] = 0;
   out_2358792323036253627[39] = 0;
   out_2358792323036253627[40] = 0;
   out_2358792323036253627[41] = 0;
   out_2358792323036253627[42] = 0;
   out_2358792323036253627[43] = 0;
   out_2358792323036253627[44] = 1;
   out_2358792323036253627[45] = 0;
   out_2358792323036253627[46] = 0;
   out_2358792323036253627[47] = 1;
   out_2358792323036253627[48] = 0;
   out_2358792323036253627[49] = 0;
   out_2358792323036253627[50] = 0;
   out_2358792323036253627[51] = 0;
   out_2358792323036253627[52] = 0;
   out_2358792323036253627[53] = 0;
}
void h_10(double *state, double *unused, double *out_791674336687732538) {
   out_791674336687732538[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_791674336687732538[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_791674336687732538[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_6454210329134681661) {
   out_6454210329134681661[0] = 0;
   out_6454210329134681661[1] = 9.8100000000000005*cos(state[1]);
   out_6454210329134681661[2] = 0;
   out_6454210329134681661[3] = 0;
   out_6454210329134681661[4] = -state[8];
   out_6454210329134681661[5] = state[7];
   out_6454210329134681661[6] = 0;
   out_6454210329134681661[7] = state[5];
   out_6454210329134681661[8] = -state[4];
   out_6454210329134681661[9] = 0;
   out_6454210329134681661[10] = 0;
   out_6454210329134681661[11] = 0;
   out_6454210329134681661[12] = 1;
   out_6454210329134681661[13] = 0;
   out_6454210329134681661[14] = 0;
   out_6454210329134681661[15] = 1;
   out_6454210329134681661[16] = 0;
   out_6454210329134681661[17] = 0;
   out_6454210329134681661[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_6454210329134681661[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_6454210329134681661[20] = 0;
   out_6454210329134681661[21] = state[8];
   out_6454210329134681661[22] = 0;
   out_6454210329134681661[23] = -state[6];
   out_6454210329134681661[24] = -state[5];
   out_6454210329134681661[25] = 0;
   out_6454210329134681661[26] = state[3];
   out_6454210329134681661[27] = 0;
   out_6454210329134681661[28] = 0;
   out_6454210329134681661[29] = 0;
   out_6454210329134681661[30] = 0;
   out_6454210329134681661[31] = 1;
   out_6454210329134681661[32] = 0;
   out_6454210329134681661[33] = 0;
   out_6454210329134681661[34] = 1;
   out_6454210329134681661[35] = 0;
   out_6454210329134681661[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_6454210329134681661[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_6454210329134681661[38] = 0;
   out_6454210329134681661[39] = -state[7];
   out_6454210329134681661[40] = state[6];
   out_6454210329134681661[41] = 0;
   out_6454210329134681661[42] = state[4];
   out_6454210329134681661[43] = -state[3];
   out_6454210329134681661[44] = 0;
   out_6454210329134681661[45] = 0;
   out_6454210329134681661[46] = 0;
   out_6454210329134681661[47] = 0;
   out_6454210329134681661[48] = 0;
   out_6454210329134681661[49] = 0;
   out_6454210329134681661[50] = 1;
   out_6454210329134681661[51] = 0;
   out_6454210329134681661[52] = 0;
   out_6454210329134681661[53] = 1;
}
void h_13(double *state, double *unused, double *out_1136153937435491358) {
   out_1136153937435491358[0] = state[3];
   out_1136153937435491358[1] = state[4];
   out_1136153937435491358[2] = state[5];
}
void H_13(double *state, double *unused, double *out_2923394242718097731) {
   out_2923394242718097731[0] = 0;
   out_2923394242718097731[1] = 0;
   out_2923394242718097731[2] = 0;
   out_2923394242718097731[3] = 1;
   out_2923394242718097731[4] = 0;
   out_2923394242718097731[5] = 0;
   out_2923394242718097731[6] = 0;
   out_2923394242718097731[7] = 0;
   out_2923394242718097731[8] = 0;
   out_2923394242718097731[9] = 0;
   out_2923394242718097731[10] = 0;
   out_2923394242718097731[11] = 0;
   out_2923394242718097731[12] = 0;
   out_2923394242718097731[13] = 0;
   out_2923394242718097731[14] = 0;
   out_2923394242718097731[15] = 0;
   out_2923394242718097731[16] = 0;
   out_2923394242718097731[17] = 0;
   out_2923394242718097731[18] = 0;
   out_2923394242718097731[19] = 0;
   out_2923394242718097731[20] = 0;
   out_2923394242718097731[21] = 0;
   out_2923394242718097731[22] = 1;
   out_2923394242718097731[23] = 0;
   out_2923394242718097731[24] = 0;
   out_2923394242718097731[25] = 0;
   out_2923394242718097731[26] = 0;
   out_2923394242718097731[27] = 0;
   out_2923394242718097731[28] = 0;
   out_2923394242718097731[29] = 0;
   out_2923394242718097731[30] = 0;
   out_2923394242718097731[31] = 0;
   out_2923394242718097731[32] = 0;
   out_2923394242718097731[33] = 0;
   out_2923394242718097731[34] = 0;
   out_2923394242718097731[35] = 0;
   out_2923394242718097731[36] = 0;
   out_2923394242718097731[37] = 0;
   out_2923394242718097731[38] = 0;
   out_2923394242718097731[39] = 0;
   out_2923394242718097731[40] = 0;
   out_2923394242718097731[41] = 1;
   out_2923394242718097731[42] = 0;
   out_2923394242718097731[43] = 0;
   out_2923394242718097731[44] = 0;
   out_2923394242718097731[45] = 0;
   out_2923394242718097731[46] = 0;
   out_2923394242718097731[47] = 0;
   out_2923394242718097731[48] = 0;
   out_2923394242718097731[49] = 0;
   out_2923394242718097731[50] = 0;
   out_2923394242718097731[51] = 0;
   out_2923394242718097731[52] = 0;
   out_2923394242718097731[53] = 0;
}
void h_14(double *state, double *unused, double *out_7535707900612158623) {
   out_7535707900612158623[0] = state[6];
   out_7535707900612158623[1] = state[7];
   out_7535707900612158623[2] = state[8];
}
void H_14(double *state, double *unused, double *out_723996109259118669) {
   out_723996109259118669[0] = 0;
   out_723996109259118669[1] = 0;
   out_723996109259118669[2] = 0;
   out_723996109259118669[3] = 0;
   out_723996109259118669[4] = 0;
   out_723996109259118669[5] = 0;
   out_723996109259118669[6] = 1;
   out_723996109259118669[7] = 0;
   out_723996109259118669[8] = 0;
   out_723996109259118669[9] = 0;
   out_723996109259118669[10] = 0;
   out_723996109259118669[11] = 0;
   out_723996109259118669[12] = 0;
   out_723996109259118669[13] = 0;
   out_723996109259118669[14] = 0;
   out_723996109259118669[15] = 0;
   out_723996109259118669[16] = 0;
   out_723996109259118669[17] = 0;
   out_723996109259118669[18] = 0;
   out_723996109259118669[19] = 0;
   out_723996109259118669[20] = 0;
   out_723996109259118669[21] = 0;
   out_723996109259118669[22] = 0;
   out_723996109259118669[23] = 0;
   out_723996109259118669[24] = 0;
   out_723996109259118669[25] = 1;
   out_723996109259118669[26] = 0;
   out_723996109259118669[27] = 0;
   out_723996109259118669[28] = 0;
   out_723996109259118669[29] = 0;
   out_723996109259118669[30] = 0;
   out_723996109259118669[31] = 0;
   out_723996109259118669[32] = 0;
   out_723996109259118669[33] = 0;
   out_723996109259118669[34] = 0;
   out_723996109259118669[35] = 0;
   out_723996109259118669[36] = 0;
   out_723996109259118669[37] = 0;
   out_723996109259118669[38] = 0;
   out_723996109259118669[39] = 0;
   out_723996109259118669[40] = 0;
   out_723996109259118669[41] = 0;
   out_723996109259118669[42] = 0;
   out_723996109259118669[43] = 0;
   out_723996109259118669[44] = 1;
   out_723996109259118669[45] = 0;
   out_723996109259118669[46] = 0;
   out_723996109259118669[47] = 0;
   out_723996109259118669[48] = 0;
   out_723996109259118669[49] = 0;
   out_723996109259118669[50] = 0;
   out_723996109259118669[51] = 0;
   out_723996109259118669[52] = 0;
   out_723996109259118669[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_1395619254280121889) {
  err_fun(nom_x, delta_x, out_1395619254280121889);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_214512694638000517) {
  inv_err_fun(nom_x, true_x, out_214512694638000517);
}
void pose_H_mod_fun(double *state, double *out_4178491048942550488) {
  H_mod_fun(state, out_4178491048942550488);
}
void pose_f_fun(double *state, double dt, double *out_6955059668244195066) {
  f_fun(state,  dt, out_6955059668244195066);
}
void pose_F_fun(double *state, double dt, double *out_5780055978525304403) {
  F_fun(state,  dt, out_5780055978525304403);
}
void pose_h_4(double *state, double *unused, double *out_4735577956641194937) {
  h_4(state, unused, out_4735577956641194937);
}
void pose_H_4(double *state, double *unused, double *out_2358792323036253627) {
  H_4(state, unused, out_2358792323036253627);
}
void pose_h_10(double *state, double *unused, double *out_791674336687732538) {
  h_10(state, unused, out_791674336687732538);
}
void pose_H_10(double *state, double *unused, double *out_6454210329134681661) {
  H_10(state, unused, out_6454210329134681661);
}
void pose_h_13(double *state, double *unused, double *out_1136153937435491358) {
  h_13(state, unused, out_1136153937435491358);
}
void pose_H_13(double *state, double *unused, double *out_2923394242718097731) {
  H_13(state, unused, out_2923394242718097731);
}
void pose_h_14(double *state, double *unused, double *out_7535707900612158623) {
  h_14(state, unused, out_7535707900612158623);
}
void pose_H_14(double *state, double *unused, double *out_723996109259118669) {
  H_14(state, unused, out_723996109259118669);
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
