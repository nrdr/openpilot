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
void err_fun(double *nom_x, double *delta_x, double *out_6269171790765846050) {
   out_6269171790765846050[0] = delta_x[0] + nom_x[0];
   out_6269171790765846050[1] = delta_x[1] + nom_x[1];
   out_6269171790765846050[2] = delta_x[2] + nom_x[2];
   out_6269171790765846050[3] = delta_x[3] + nom_x[3];
   out_6269171790765846050[4] = delta_x[4] + nom_x[4];
   out_6269171790765846050[5] = delta_x[5] + nom_x[5];
   out_6269171790765846050[6] = delta_x[6] + nom_x[6];
   out_6269171790765846050[7] = delta_x[7] + nom_x[7];
   out_6269171790765846050[8] = delta_x[8] + nom_x[8];
   out_6269171790765846050[9] = delta_x[9] + nom_x[9];
   out_6269171790765846050[10] = delta_x[10] + nom_x[10];
   out_6269171790765846050[11] = delta_x[11] + nom_x[11];
   out_6269171790765846050[12] = delta_x[12] + nom_x[12];
   out_6269171790765846050[13] = delta_x[13] + nom_x[13];
   out_6269171790765846050[14] = delta_x[14] + nom_x[14];
   out_6269171790765846050[15] = delta_x[15] + nom_x[15];
   out_6269171790765846050[16] = delta_x[16] + nom_x[16];
   out_6269171790765846050[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1497934558633100347) {
   out_1497934558633100347[0] = -nom_x[0] + true_x[0];
   out_1497934558633100347[1] = -nom_x[1] + true_x[1];
   out_1497934558633100347[2] = -nom_x[2] + true_x[2];
   out_1497934558633100347[3] = -nom_x[3] + true_x[3];
   out_1497934558633100347[4] = -nom_x[4] + true_x[4];
   out_1497934558633100347[5] = -nom_x[5] + true_x[5];
   out_1497934558633100347[6] = -nom_x[6] + true_x[6];
   out_1497934558633100347[7] = -nom_x[7] + true_x[7];
   out_1497934558633100347[8] = -nom_x[8] + true_x[8];
   out_1497934558633100347[9] = -nom_x[9] + true_x[9];
   out_1497934558633100347[10] = -nom_x[10] + true_x[10];
   out_1497934558633100347[11] = -nom_x[11] + true_x[11];
   out_1497934558633100347[12] = -nom_x[12] + true_x[12];
   out_1497934558633100347[13] = -nom_x[13] + true_x[13];
   out_1497934558633100347[14] = -nom_x[14] + true_x[14];
   out_1497934558633100347[15] = -nom_x[15] + true_x[15];
   out_1497934558633100347[16] = -nom_x[16] + true_x[16];
   out_1497934558633100347[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_7862392065184069712) {
   out_7862392065184069712[0] = 1.0;
   out_7862392065184069712[1] = 0.0;
   out_7862392065184069712[2] = 0.0;
   out_7862392065184069712[3] = 0.0;
   out_7862392065184069712[4] = 0.0;
   out_7862392065184069712[5] = 0.0;
   out_7862392065184069712[6] = 0.0;
   out_7862392065184069712[7] = 0.0;
   out_7862392065184069712[8] = 0.0;
   out_7862392065184069712[9] = 0.0;
   out_7862392065184069712[10] = 0.0;
   out_7862392065184069712[11] = 0.0;
   out_7862392065184069712[12] = 0.0;
   out_7862392065184069712[13] = 0.0;
   out_7862392065184069712[14] = 0.0;
   out_7862392065184069712[15] = 0.0;
   out_7862392065184069712[16] = 0.0;
   out_7862392065184069712[17] = 0.0;
   out_7862392065184069712[18] = 0.0;
   out_7862392065184069712[19] = 1.0;
   out_7862392065184069712[20] = 0.0;
   out_7862392065184069712[21] = 0.0;
   out_7862392065184069712[22] = 0.0;
   out_7862392065184069712[23] = 0.0;
   out_7862392065184069712[24] = 0.0;
   out_7862392065184069712[25] = 0.0;
   out_7862392065184069712[26] = 0.0;
   out_7862392065184069712[27] = 0.0;
   out_7862392065184069712[28] = 0.0;
   out_7862392065184069712[29] = 0.0;
   out_7862392065184069712[30] = 0.0;
   out_7862392065184069712[31] = 0.0;
   out_7862392065184069712[32] = 0.0;
   out_7862392065184069712[33] = 0.0;
   out_7862392065184069712[34] = 0.0;
   out_7862392065184069712[35] = 0.0;
   out_7862392065184069712[36] = 0.0;
   out_7862392065184069712[37] = 0.0;
   out_7862392065184069712[38] = 1.0;
   out_7862392065184069712[39] = 0.0;
   out_7862392065184069712[40] = 0.0;
   out_7862392065184069712[41] = 0.0;
   out_7862392065184069712[42] = 0.0;
   out_7862392065184069712[43] = 0.0;
   out_7862392065184069712[44] = 0.0;
   out_7862392065184069712[45] = 0.0;
   out_7862392065184069712[46] = 0.0;
   out_7862392065184069712[47] = 0.0;
   out_7862392065184069712[48] = 0.0;
   out_7862392065184069712[49] = 0.0;
   out_7862392065184069712[50] = 0.0;
   out_7862392065184069712[51] = 0.0;
   out_7862392065184069712[52] = 0.0;
   out_7862392065184069712[53] = 0.0;
   out_7862392065184069712[54] = 0.0;
   out_7862392065184069712[55] = 0.0;
   out_7862392065184069712[56] = 0.0;
   out_7862392065184069712[57] = 1.0;
   out_7862392065184069712[58] = 0.0;
   out_7862392065184069712[59] = 0.0;
   out_7862392065184069712[60] = 0.0;
   out_7862392065184069712[61] = 0.0;
   out_7862392065184069712[62] = 0.0;
   out_7862392065184069712[63] = 0.0;
   out_7862392065184069712[64] = 0.0;
   out_7862392065184069712[65] = 0.0;
   out_7862392065184069712[66] = 0.0;
   out_7862392065184069712[67] = 0.0;
   out_7862392065184069712[68] = 0.0;
   out_7862392065184069712[69] = 0.0;
   out_7862392065184069712[70] = 0.0;
   out_7862392065184069712[71] = 0.0;
   out_7862392065184069712[72] = 0.0;
   out_7862392065184069712[73] = 0.0;
   out_7862392065184069712[74] = 0.0;
   out_7862392065184069712[75] = 0.0;
   out_7862392065184069712[76] = 1.0;
   out_7862392065184069712[77] = 0.0;
   out_7862392065184069712[78] = 0.0;
   out_7862392065184069712[79] = 0.0;
   out_7862392065184069712[80] = 0.0;
   out_7862392065184069712[81] = 0.0;
   out_7862392065184069712[82] = 0.0;
   out_7862392065184069712[83] = 0.0;
   out_7862392065184069712[84] = 0.0;
   out_7862392065184069712[85] = 0.0;
   out_7862392065184069712[86] = 0.0;
   out_7862392065184069712[87] = 0.0;
   out_7862392065184069712[88] = 0.0;
   out_7862392065184069712[89] = 0.0;
   out_7862392065184069712[90] = 0.0;
   out_7862392065184069712[91] = 0.0;
   out_7862392065184069712[92] = 0.0;
   out_7862392065184069712[93] = 0.0;
   out_7862392065184069712[94] = 0.0;
   out_7862392065184069712[95] = 1.0;
   out_7862392065184069712[96] = 0.0;
   out_7862392065184069712[97] = 0.0;
   out_7862392065184069712[98] = 0.0;
   out_7862392065184069712[99] = 0.0;
   out_7862392065184069712[100] = 0.0;
   out_7862392065184069712[101] = 0.0;
   out_7862392065184069712[102] = 0.0;
   out_7862392065184069712[103] = 0.0;
   out_7862392065184069712[104] = 0.0;
   out_7862392065184069712[105] = 0.0;
   out_7862392065184069712[106] = 0.0;
   out_7862392065184069712[107] = 0.0;
   out_7862392065184069712[108] = 0.0;
   out_7862392065184069712[109] = 0.0;
   out_7862392065184069712[110] = 0.0;
   out_7862392065184069712[111] = 0.0;
   out_7862392065184069712[112] = 0.0;
   out_7862392065184069712[113] = 0.0;
   out_7862392065184069712[114] = 1.0;
   out_7862392065184069712[115] = 0.0;
   out_7862392065184069712[116] = 0.0;
   out_7862392065184069712[117] = 0.0;
   out_7862392065184069712[118] = 0.0;
   out_7862392065184069712[119] = 0.0;
   out_7862392065184069712[120] = 0.0;
   out_7862392065184069712[121] = 0.0;
   out_7862392065184069712[122] = 0.0;
   out_7862392065184069712[123] = 0.0;
   out_7862392065184069712[124] = 0.0;
   out_7862392065184069712[125] = 0.0;
   out_7862392065184069712[126] = 0.0;
   out_7862392065184069712[127] = 0.0;
   out_7862392065184069712[128] = 0.0;
   out_7862392065184069712[129] = 0.0;
   out_7862392065184069712[130] = 0.0;
   out_7862392065184069712[131] = 0.0;
   out_7862392065184069712[132] = 0.0;
   out_7862392065184069712[133] = 1.0;
   out_7862392065184069712[134] = 0.0;
   out_7862392065184069712[135] = 0.0;
   out_7862392065184069712[136] = 0.0;
   out_7862392065184069712[137] = 0.0;
   out_7862392065184069712[138] = 0.0;
   out_7862392065184069712[139] = 0.0;
   out_7862392065184069712[140] = 0.0;
   out_7862392065184069712[141] = 0.0;
   out_7862392065184069712[142] = 0.0;
   out_7862392065184069712[143] = 0.0;
   out_7862392065184069712[144] = 0.0;
   out_7862392065184069712[145] = 0.0;
   out_7862392065184069712[146] = 0.0;
   out_7862392065184069712[147] = 0.0;
   out_7862392065184069712[148] = 0.0;
   out_7862392065184069712[149] = 0.0;
   out_7862392065184069712[150] = 0.0;
   out_7862392065184069712[151] = 0.0;
   out_7862392065184069712[152] = 1.0;
   out_7862392065184069712[153] = 0.0;
   out_7862392065184069712[154] = 0.0;
   out_7862392065184069712[155] = 0.0;
   out_7862392065184069712[156] = 0.0;
   out_7862392065184069712[157] = 0.0;
   out_7862392065184069712[158] = 0.0;
   out_7862392065184069712[159] = 0.0;
   out_7862392065184069712[160] = 0.0;
   out_7862392065184069712[161] = 0.0;
   out_7862392065184069712[162] = 0.0;
   out_7862392065184069712[163] = 0.0;
   out_7862392065184069712[164] = 0.0;
   out_7862392065184069712[165] = 0.0;
   out_7862392065184069712[166] = 0.0;
   out_7862392065184069712[167] = 0.0;
   out_7862392065184069712[168] = 0.0;
   out_7862392065184069712[169] = 0.0;
   out_7862392065184069712[170] = 0.0;
   out_7862392065184069712[171] = 1.0;
   out_7862392065184069712[172] = 0.0;
   out_7862392065184069712[173] = 0.0;
   out_7862392065184069712[174] = 0.0;
   out_7862392065184069712[175] = 0.0;
   out_7862392065184069712[176] = 0.0;
   out_7862392065184069712[177] = 0.0;
   out_7862392065184069712[178] = 0.0;
   out_7862392065184069712[179] = 0.0;
   out_7862392065184069712[180] = 0.0;
   out_7862392065184069712[181] = 0.0;
   out_7862392065184069712[182] = 0.0;
   out_7862392065184069712[183] = 0.0;
   out_7862392065184069712[184] = 0.0;
   out_7862392065184069712[185] = 0.0;
   out_7862392065184069712[186] = 0.0;
   out_7862392065184069712[187] = 0.0;
   out_7862392065184069712[188] = 0.0;
   out_7862392065184069712[189] = 0.0;
   out_7862392065184069712[190] = 1.0;
   out_7862392065184069712[191] = 0.0;
   out_7862392065184069712[192] = 0.0;
   out_7862392065184069712[193] = 0.0;
   out_7862392065184069712[194] = 0.0;
   out_7862392065184069712[195] = 0.0;
   out_7862392065184069712[196] = 0.0;
   out_7862392065184069712[197] = 0.0;
   out_7862392065184069712[198] = 0.0;
   out_7862392065184069712[199] = 0.0;
   out_7862392065184069712[200] = 0.0;
   out_7862392065184069712[201] = 0.0;
   out_7862392065184069712[202] = 0.0;
   out_7862392065184069712[203] = 0.0;
   out_7862392065184069712[204] = 0.0;
   out_7862392065184069712[205] = 0.0;
   out_7862392065184069712[206] = 0.0;
   out_7862392065184069712[207] = 0.0;
   out_7862392065184069712[208] = 0.0;
   out_7862392065184069712[209] = 1.0;
   out_7862392065184069712[210] = 0.0;
   out_7862392065184069712[211] = 0.0;
   out_7862392065184069712[212] = 0.0;
   out_7862392065184069712[213] = 0.0;
   out_7862392065184069712[214] = 0.0;
   out_7862392065184069712[215] = 0.0;
   out_7862392065184069712[216] = 0.0;
   out_7862392065184069712[217] = 0.0;
   out_7862392065184069712[218] = 0.0;
   out_7862392065184069712[219] = 0.0;
   out_7862392065184069712[220] = 0.0;
   out_7862392065184069712[221] = 0.0;
   out_7862392065184069712[222] = 0.0;
   out_7862392065184069712[223] = 0.0;
   out_7862392065184069712[224] = 0.0;
   out_7862392065184069712[225] = 0.0;
   out_7862392065184069712[226] = 0.0;
   out_7862392065184069712[227] = 0.0;
   out_7862392065184069712[228] = 1.0;
   out_7862392065184069712[229] = 0.0;
   out_7862392065184069712[230] = 0.0;
   out_7862392065184069712[231] = 0.0;
   out_7862392065184069712[232] = 0.0;
   out_7862392065184069712[233] = 0.0;
   out_7862392065184069712[234] = 0.0;
   out_7862392065184069712[235] = 0.0;
   out_7862392065184069712[236] = 0.0;
   out_7862392065184069712[237] = 0.0;
   out_7862392065184069712[238] = 0.0;
   out_7862392065184069712[239] = 0.0;
   out_7862392065184069712[240] = 0.0;
   out_7862392065184069712[241] = 0.0;
   out_7862392065184069712[242] = 0.0;
   out_7862392065184069712[243] = 0.0;
   out_7862392065184069712[244] = 0.0;
   out_7862392065184069712[245] = 0.0;
   out_7862392065184069712[246] = 0.0;
   out_7862392065184069712[247] = 1.0;
   out_7862392065184069712[248] = 0.0;
   out_7862392065184069712[249] = 0.0;
   out_7862392065184069712[250] = 0.0;
   out_7862392065184069712[251] = 0.0;
   out_7862392065184069712[252] = 0.0;
   out_7862392065184069712[253] = 0.0;
   out_7862392065184069712[254] = 0.0;
   out_7862392065184069712[255] = 0.0;
   out_7862392065184069712[256] = 0.0;
   out_7862392065184069712[257] = 0.0;
   out_7862392065184069712[258] = 0.0;
   out_7862392065184069712[259] = 0.0;
   out_7862392065184069712[260] = 0.0;
   out_7862392065184069712[261] = 0.0;
   out_7862392065184069712[262] = 0.0;
   out_7862392065184069712[263] = 0.0;
   out_7862392065184069712[264] = 0.0;
   out_7862392065184069712[265] = 0.0;
   out_7862392065184069712[266] = 1.0;
   out_7862392065184069712[267] = 0.0;
   out_7862392065184069712[268] = 0.0;
   out_7862392065184069712[269] = 0.0;
   out_7862392065184069712[270] = 0.0;
   out_7862392065184069712[271] = 0.0;
   out_7862392065184069712[272] = 0.0;
   out_7862392065184069712[273] = 0.0;
   out_7862392065184069712[274] = 0.0;
   out_7862392065184069712[275] = 0.0;
   out_7862392065184069712[276] = 0.0;
   out_7862392065184069712[277] = 0.0;
   out_7862392065184069712[278] = 0.0;
   out_7862392065184069712[279] = 0.0;
   out_7862392065184069712[280] = 0.0;
   out_7862392065184069712[281] = 0.0;
   out_7862392065184069712[282] = 0.0;
   out_7862392065184069712[283] = 0.0;
   out_7862392065184069712[284] = 0.0;
   out_7862392065184069712[285] = 1.0;
   out_7862392065184069712[286] = 0.0;
   out_7862392065184069712[287] = 0.0;
   out_7862392065184069712[288] = 0.0;
   out_7862392065184069712[289] = 0.0;
   out_7862392065184069712[290] = 0.0;
   out_7862392065184069712[291] = 0.0;
   out_7862392065184069712[292] = 0.0;
   out_7862392065184069712[293] = 0.0;
   out_7862392065184069712[294] = 0.0;
   out_7862392065184069712[295] = 0.0;
   out_7862392065184069712[296] = 0.0;
   out_7862392065184069712[297] = 0.0;
   out_7862392065184069712[298] = 0.0;
   out_7862392065184069712[299] = 0.0;
   out_7862392065184069712[300] = 0.0;
   out_7862392065184069712[301] = 0.0;
   out_7862392065184069712[302] = 0.0;
   out_7862392065184069712[303] = 0.0;
   out_7862392065184069712[304] = 1.0;
   out_7862392065184069712[305] = 0.0;
   out_7862392065184069712[306] = 0.0;
   out_7862392065184069712[307] = 0.0;
   out_7862392065184069712[308] = 0.0;
   out_7862392065184069712[309] = 0.0;
   out_7862392065184069712[310] = 0.0;
   out_7862392065184069712[311] = 0.0;
   out_7862392065184069712[312] = 0.0;
   out_7862392065184069712[313] = 0.0;
   out_7862392065184069712[314] = 0.0;
   out_7862392065184069712[315] = 0.0;
   out_7862392065184069712[316] = 0.0;
   out_7862392065184069712[317] = 0.0;
   out_7862392065184069712[318] = 0.0;
   out_7862392065184069712[319] = 0.0;
   out_7862392065184069712[320] = 0.0;
   out_7862392065184069712[321] = 0.0;
   out_7862392065184069712[322] = 0.0;
   out_7862392065184069712[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_4855847476055627778) {
   out_4855847476055627778[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_4855847476055627778[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_4855847476055627778[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_4855847476055627778[3] = dt*state[12] + state[3];
   out_4855847476055627778[4] = dt*state[13] + state[4];
   out_4855847476055627778[5] = dt*state[14] + state[5];
   out_4855847476055627778[6] = state[6];
   out_4855847476055627778[7] = state[7];
   out_4855847476055627778[8] = state[8];
   out_4855847476055627778[9] = state[9];
   out_4855847476055627778[10] = state[10];
   out_4855847476055627778[11] = state[11];
   out_4855847476055627778[12] = state[12];
   out_4855847476055627778[13] = state[13];
   out_4855847476055627778[14] = state[14];
   out_4855847476055627778[15] = state[15];
   out_4855847476055627778[16] = state[16];
   out_4855847476055627778[17] = state[17];
}
void F_fun(double *state, double dt, double *out_1703318423524786966) {
   out_1703318423524786966[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1703318423524786966[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1703318423524786966[2] = 0;
   out_1703318423524786966[3] = 0;
   out_1703318423524786966[4] = 0;
   out_1703318423524786966[5] = 0;
   out_1703318423524786966[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1703318423524786966[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1703318423524786966[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_1703318423524786966[9] = 0;
   out_1703318423524786966[10] = 0;
   out_1703318423524786966[11] = 0;
   out_1703318423524786966[12] = 0;
   out_1703318423524786966[13] = 0;
   out_1703318423524786966[14] = 0;
   out_1703318423524786966[15] = 0;
   out_1703318423524786966[16] = 0;
   out_1703318423524786966[17] = 0;
   out_1703318423524786966[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_1703318423524786966[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_1703318423524786966[20] = 0;
   out_1703318423524786966[21] = 0;
   out_1703318423524786966[22] = 0;
   out_1703318423524786966[23] = 0;
   out_1703318423524786966[24] = 0;
   out_1703318423524786966[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_1703318423524786966[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_1703318423524786966[27] = 0;
   out_1703318423524786966[28] = 0;
   out_1703318423524786966[29] = 0;
   out_1703318423524786966[30] = 0;
   out_1703318423524786966[31] = 0;
   out_1703318423524786966[32] = 0;
   out_1703318423524786966[33] = 0;
   out_1703318423524786966[34] = 0;
   out_1703318423524786966[35] = 0;
   out_1703318423524786966[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1703318423524786966[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1703318423524786966[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1703318423524786966[39] = 0;
   out_1703318423524786966[40] = 0;
   out_1703318423524786966[41] = 0;
   out_1703318423524786966[42] = 0;
   out_1703318423524786966[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1703318423524786966[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_1703318423524786966[45] = 0;
   out_1703318423524786966[46] = 0;
   out_1703318423524786966[47] = 0;
   out_1703318423524786966[48] = 0;
   out_1703318423524786966[49] = 0;
   out_1703318423524786966[50] = 0;
   out_1703318423524786966[51] = 0;
   out_1703318423524786966[52] = 0;
   out_1703318423524786966[53] = 0;
   out_1703318423524786966[54] = 0;
   out_1703318423524786966[55] = 0;
   out_1703318423524786966[56] = 0;
   out_1703318423524786966[57] = 1;
   out_1703318423524786966[58] = 0;
   out_1703318423524786966[59] = 0;
   out_1703318423524786966[60] = 0;
   out_1703318423524786966[61] = 0;
   out_1703318423524786966[62] = 0;
   out_1703318423524786966[63] = 0;
   out_1703318423524786966[64] = 0;
   out_1703318423524786966[65] = 0;
   out_1703318423524786966[66] = dt;
   out_1703318423524786966[67] = 0;
   out_1703318423524786966[68] = 0;
   out_1703318423524786966[69] = 0;
   out_1703318423524786966[70] = 0;
   out_1703318423524786966[71] = 0;
   out_1703318423524786966[72] = 0;
   out_1703318423524786966[73] = 0;
   out_1703318423524786966[74] = 0;
   out_1703318423524786966[75] = 0;
   out_1703318423524786966[76] = 1;
   out_1703318423524786966[77] = 0;
   out_1703318423524786966[78] = 0;
   out_1703318423524786966[79] = 0;
   out_1703318423524786966[80] = 0;
   out_1703318423524786966[81] = 0;
   out_1703318423524786966[82] = 0;
   out_1703318423524786966[83] = 0;
   out_1703318423524786966[84] = 0;
   out_1703318423524786966[85] = dt;
   out_1703318423524786966[86] = 0;
   out_1703318423524786966[87] = 0;
   out_1703318423524786966[88] = 0;
   out_1703318423524786966[89] = 0;
   out_1703318423524786966[90] = 0;
   out_1703318423524786966[91] = 0;
   out_1703318423524786966[92] = 0;
   out_1703318423524786966[93] = 0;
   out_1703318423524786966[94] = 0;
   out_1703318423524786966[95] = 1;
   out_1703318423524786966[96] = 0;
   out_1703318423524786966[97] = 0;
   out_1703318423524786966[98] = 0;
   out_1703318423524786966[99] = 0;
   out_1703318423524786966[100] = 0;
   out_1703318423524786966[101] = 0;
   out_1703318423524786966[102] = 0;
   out_1703318423524786966[103] = 0;
   out_1703318423524786966[104] = dt;
   out_1703318423524786966[105] = 0;
   out_1703318423524786966[106] = 0;
   out_1703318423524786966[107] = 0;
   out_1703318423524786966[108] = 0;
   out_1703318423524786966[109] = 0;
   out_1703318423524786966[110] = 0;
   out_1703318423524786966[111] = 0;
   out_1703318423524786966[112] = 0;
   out_1703318423524786966[113] = 0;
   out_1703318423524786966[114] = 1;
   out_1703318423524786966[115] = 0;
   out_1703318423524786966[116] = 0;
   out_1703318423524786966[117] = 0;
   out_1703318423524786966[118] = 0;
   out_1703318423524786966[119] = 0;
   out_1703318423524786966[120] = 0;
   out_1703318423524786966[121] = 0;
   out_1703318423524786966[122] = 0;
   out_1703318423524786966[123] = 0;
   out_1703318423524786966[124] = 0;
   out_1703318423524786966[125] = 0;
   out_1703318423524786966[126] = 0;
   out_1703318423524786966[127] = 0;
   out_1703318423524786966[128] = 0;
   out_1703318423524786966[129] = 0;
   out_1703318423524786966[130] = 0;
   out_1703318423524786966[131] = 0;
   out_1703318423524786966[132] = 0;
   out_1703318423524786966[133] = 1;
   out_1703318423524786966[134] = 0;
   out_1703318423524786966[135] = 0;
   out_1703318423524786966[136] = 0;
   out_1703318423524786966[137] = 0;
   out_1703318423524786966[138] = 0;
   out_1703318423524786966[139] = 0;
   out_1703318423524786966[140] = 0;
   out_1703318423524786966[141] = 0;
   out_1703318423524786966[142] = 0;
   out_1703318423524786966[143] = 0;
   out_1703318423524786966[144] = 0;
   out_1703318423524786966[145] = 0;
   out_1703318423524786966[146] = 0;
   out_1703318423524786966[147] = 0;
   out_1703318423524786966[148] = 0;
   out_1703318423524786966[149] = 0;
   out_1703318423524786966[150] = 0;
   out_1703318423524786966[151] = 0;
   out_1703318423524786966[152] = 1;
   out_1703318423524786966[153] = 0;
   out_1703318423524786966[154] = 0;
   out_1703318423524786966[155] = 0;
   out_1703318423524786966[156] = 0;
   out_1703318423524786966[157] = 0;
   out_1703318423524786966[158] = 0;
   out_1703318423524786966[159] = 0;
   out_1703318423524786966[160] = 0;
   out_1703318423524786966[161] = 0;
   out_1703318423524786966[162] = 0;
   out_1703318423524786966[163] = 0;
   out_1703318423524786966[164] = 0;
   out_1703318423524786966[165] = 0;
   out_1703318423524786966[166] = 0;
   out_1703318423524786966[167] = 0;
   out_1703318423524786966[168] = 0;
   out_1703318423524786966[169] = 0;
   out_1703318423524786966[170] = 0;
   out_1703318423524786966[171] = 1;
   out_1703318423524786966[172] = 0;
   out_1703318423524786966[173] = 0;
   out_1703318423524786966[174] = 0;
   out_1703318423524786966[175] = 0;
   out_1703318423524786966[176] = 0;
   out_1703318423524786966[177] = 0;
   out_1703318423524786966[178] = 0;
   out_1703318423524786966[179] = 0;
   out_1703318423524786966[180] = 0;
   out_1703318423524786966[181] = 0;
   out_1703318423524786966[182] = 0;
   out_1703318423524786966[183] = 0;
   out_1703318423524786966[184] = 0;
   out_1703318423524786966[185] = 0;
   out_1703318423524786966[186] = 0;
   out_1703318423524786966[187] = 0;
   out_1703318423524786966[188] = 0;
   out_1703318423524786966[189] = 0;
   out_1703318423524786966[190] = 1;
   out_1703318423524786966[191] = 0;
   out_1703318423524786966[192] = 0;
   out_1703318423524786966[193] = 0;
   out_1703318423524786966[194] = 0;
   out_1703318423524786966[195] = 0;
   out_1703318423524786966[196] = 0;
   out_1703318423524786966[197] = 0;
   out_1703318423524786966[198] = 0;
   out_1703318423524786966[199] = 0;
   out_1703318423524786966[200] = 0;
   out_1703318423524786966[201] = 0;
   out_1703318423524786966[202] = 0;
   out_1703318423524786966[203] = 0;
   out_1703318423524786966[204] = 0;
   out_1703318423524786966[205] = 0;
   out_1703318423524786966[206] = 0;
   out_1703318423524786966[207] = 0;
   out_1703318423524786966[208] = 0;
   out_1703318423524786966[209] = 1;
   out_1703318423524786966[210] = 0;
   out_1703318423524786966[211] = 0;
   out_1703318423524786966[212] = 0;
   out_1703318423524786966[213] = 0;
   out_1703318423524786966[214] = 0;
   out_1703318423524786966[215] = 0;
   out_1703318423524786966[216] = 0;
   out_1703318423524786966[217] = 0;
   out_1703318423524786966[218] = 0;
   out_1703318423524786966[219] = 0;
   out_1703318423524786966[220] = 0;
   out_1703318423524786966[221] = 0;
   out_1703318423524786966[222] = 0;
   out_1703318423524786966[223] = 0;
   out_1703318423524786966[224] = 0;
   out_1703318423524786966[225] = 0;
   out_1703318423524786966[226] = 0;
   out_1703318423524786966[227] = 0;
   out_1703318423524786966[228] = 1;
   out_1703318423524786966[229] = 0;
   out_1703318423524786966[230] = 0;
   out_1703318423524786966[231] = 0;
   out_1703318423524786966[232] = 0;
   out_1703318423524786966[233] = 0;
   out_1703318423524786966[234] = 0;
   out_1703318423524786966[235] = 0;
   out_1703318423524786966[236] = 0;
   out_1703318423524786966[237] = 0;
   out_1703318423524786966[238] = 0;
   out_1703318423524786966[239] = 0;
   out_1703318423524786966[240] = 0;
   out_1703318423524786966[241] = 0;
   out_1703318423524786966[242] = 0;
   out_1703318423524786966[243] = 0;
   out_1703318423524786966[244] = 0;
   out_1703318423524786966[245] = 0;
   out_1703318423524786966[246] = 0;
   out_1703318423524786966[247] = 1;
   out_1703318423524786966[248] = 0;
   out_1703318423524786966[249] = 0;
   out_1703318423524786966[250] = 0;
   out_1703318423524786966[251] = 0;
   out_1703318423524786966[252] = 0;
   out_1703318423524786966[253] = 0;
   out_1703318423524786966[254] = 0;
   out_1703318423524786966[255] = 0;
   out_1703318423524786966[256] = 0;
   out_1703318423524786966[257] = 0;
   out_1703318423524786966[258] = 0;
   out_1703318423524786966[259] = 0;
   out_1703318423524786966[260] = 0;
   out_1703318423524786966[261] = 0;
   out_1703318423524786966[262] = 0;
   out_1703318423524786966[263] = 0;
   out_1703318423524786966[264] = 0;
   out_1703318423524786966[265] = 0;
   out_1703318423524786966[266] = 1;
   out_1703318423524786966[267] = 0;
   out_1703318423524786966[268] = 0;
   out_1703318423524786966[269] = 0;
   out_1703318423524786966[270] = 0;
   out_1703318423524786966[271] = 0;
   out_1703318423524786966[272] = 0;
   out_1703318423524786966[273] = 0;
   out_1703318423524786966[274] = 0;
   out_1703318423524786966[275] = 0;
   out_1703318423524786966[276] = 0;
   out_1703318423524786966[277] = 0;
   out_1703318423524786966[278] = 0;
   out_1703318423524786966[279] = 0;
   out_1703318423524786966[280] = 0;
   out_1703318423524786966[281] = 0;
   out_1703318423524786966[282] = 0;
   out_1703318423524786966[283] = 0;
   out_1703318423524786966[284] = 0;
   out_1703318423524786966[285] = 1;
   out_1703318423524786966[286] = 0;
   out_1703318423524786966[287] = 0;
   out_1703318423524786966[288] = 0;
   out_1703318423524786966[289] = 0;
   out_1703318423524786966[290] = 0;
   out_1703318423524786966[291] = 0;
   out_1703318423524786966[292] = 0;
   out_1703318423524786966[293] = 0;
   out_1703318423524786966[294] = 0;
   out_1703318423524786966[295] = 0;
   out_1703318423524786966[296] = 0;
   out_1703318423524786966[297] = 0;
   out_1703318423524786966[298] = 0;
   out_1703318423524786966[299] = 0;
   out_1703318423524786966[300] = 0;
   out_1703318423524786966[301] = 0;
   out_1703318423524786966[302] = 0;
   out_1703318423524786966[303] = 0;
   out_1703318423524786966[304] = 1;
   out_1703318423524786966[305] = 0;
   out_1703318423524786966[306] = 0;
   out_1703318423524786966[307] = 0;
   out_1703318423524786966[308] = 0;
   out_1703318423524786966[309] = 0;
   out_1703318423524786966[310] = 0;
   out_1703318423524786966[311] = 0;
   out_1703318423524786966[312] = 0;
   out_1703318423524786966[313] = 0;
   out_1703318423524786966[314] = 0;
   out_1703318423524786966[315] = 0;
   out_1703318423524786966[316] = 0;
   out_1703318423524786966[317] = 0;
   out_1703318423524786966[318] = 0;
   out_1703318423524786966[319] = 0;
   out_1703318423524786966[320] = 0;
   out_1703318423524786966[321] = 0;
   out_1703318423524786966[322] = 0;
   out_1703318423524786966[323] = 1;
}
void h_4(double *state, double *unused, double *out_7821603690376207235) {
   out_7821603690376207235[0] = state[6] + state[9];
   out_7821603690376207235[1] = state[7] + state[10];
   out_7821603690376207235[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_1639990342467660562) {
   out_1639990342467660562[0] = 0;
   out_1639990342467660562[1] = 0;
   out_1639990342467660562[2] = 0;
   out_1639990342467660562[3] = 0;
   out_1639990342467660562[4] = 0;
   out_1639990342467660562[5] = 0;
   out_1639990342467660562[6] = 1;
   out_1639990342467660562[7] = 0;
   out_1639990342467660562[8] = 0;
   out_1639990342467660562[9] = 1;
   out_1639990342467660562[10] = 0;
   out_1639990342467660562[11] = 0;
   out_1639990342467660562[12] = 0;
   out_1639990342467660562[13] = 0;
   out_1639990342467660562[14] = 0;
   out_1639990342467660562[15] = 0;
   out_1639990342467660562[16] = 0;
   out_1639990342467660562[17] = 0;
   out_1639990342467660562[18] = 0;
   out_1639990342467660562[19] = 0;
   out_1639990342467660562[20] = 0;
   out_1639990342467660562[21] = 0;
   out_1639990342467660562[22] = 0;
   out_1639990342467660562[23] = 0;
   out_1639990342467660562[24] = 0;
   out_1639990342467660562[25] = 1;
   out_1639990342467660562[26] = 0;
   out_1639990342467660562[27] = 0;
   out_1639990342467660562[28] = 1;
   out_1639990342467660562[29] = 0;
   out_1639990342467660562[30] = 0;
   out_1639990342467660562[31] = 0;
   out_1639990342467660562[32] = 0;
   out_1639990342467660562[33] = 0;
   out_1639990342467660562[34] = 0;
   out_1639990342467660562[35] = 0;
   out_1639990342467660562[36] = 0;
   out_1639990342467660562[37] = 0;
   out_1639990342467660562[38] = 0;
   out_1639990342467660562[39] = 0;
   out_1639990342467660562[40] = 0;
   out_1639990342467660562[41] = 0;
   out_1639990342467660562[42] = 0;
   out_1639990342467660562[43] = 0;
   out_1639990342467660562[44] = 1;
   out_1639990342467660562[45] = 0;
   out_1639990342467660562[46] = 0;
   out_1639990342467660562[47] = 1;
   out_1639990342467660562[48] = 0;
   out_1639990342467660562[49] = 0;
   out_1639990342467660562[50] = 0;
   out_1639990342467660562[51] = 0;
   out_1639990342467660562[52] = 0;
   out_1639990342467660562[53] = 0;
}
void h_10(double *state, double *unused, double *out_4627608962100745909) {
   out_4627608962100745909[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_4627608962100745909[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_4627608962100745909[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_5548344007433806154) {
   out_5548344007433806154[0] = 0;
   out_5548344007433806154[1] = 9.8100000000000005*cos(state[1]);
   out_5548344007433806154[2] = 0;
   out_5548344007433806154[3] = 0;
   out_5548344007433806154[4] = -state[8];
   out_5548344007433806154[5] = state[7];
   out_5548344007433806154[6] = 0;
   out_5548344007433806154[7] = state[5];
   out_5548344007433806154[8] = -state[4];
   out_5548344007433806154[9] = 0;
   out_5548344007433806154[10] = 0;
   out_5548344007433806154[11] = 0;
   out_5548344007433806154[12] = 1;
   out_5548344007433806154[13] = 0;
   out_5548344007433806154[14] = 0;
   out_5548344007433806154[15] = 1;
   out_5548344007433806154[16] = 0;
   out_5548344007433806154[17] = 0;
   out_5548344007433806154[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_5548344007433806154[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_5548344007433806154[20] = 0;
   out_5548344007433806154[21] = state[8];
   out_5548344007433806154[22] = 0;
   out_5548344007433806154[23] = -state[6];
   out_5548344007433806154[24] = -state[5];
   out_5548344007433806154[25] = 0;
   out_5548344007433806154[26] = state[3];
   out_5548344007433806154[27] = 0;
   out_5548344007433806154[28] = 0;
   out_5548344007433806154[29] = 0;
   out_5548344007433806154[30] = 0;
   out_5548344007433806154[31] = 1;
   out_5548344007433806154[32] = 0;
   out_5548344007433806154[33] = 0;
   out_5548344007433806154[34] = 1;
   out_5548344007433806154[35] = 0;
   out_5548344007433806154[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_5548344007433806154[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_5548344007433806154[38] = 0;
   out_5548344007433806154[39] = -state[7];
   out_5548344007433806154[40] = state[6];
   out_5548344007433806154[41] = 0;
   out_5548344007433806154[42] = state[4];
   out_5548344007433806154[43] = -state[3];
   out_5548344007433806154[44] = 0;
   out_5548344007433806154[45] = 0;
   out_5548344007433806154[46] = 0;
   out_5548344007433806154[47] = 0;
   out_5548344007433806154[48] = 0;
   out_5548344007433806154[49] = 0;
   out_5548344007433806154[50] = 1;
   out_5548344007433806154[51] = 0;
   out_5548344007433806154[52] = 0;
   out_5548344007433806154[53] = 1;
}
void h_13(double *state, double *unused, double *out_5105456950148742445) {
   out_5105456950148742445[0] = state[3];
   out_5105456950148742445[1] = state[4];
   out_5105456950148742445[2] = state[5];
}
void H_13(double *state, double *unused, double *out_4852264167799993363) {
   out_4852264167799993363[0] = 0;
   out_4852264167799993363[1] = 0;
   out_4852264167799993363[2] = 0;
   out_4852264167799993363[3] = 1;
   out_4852264167799993363[4] = 0;
   out_4852264167799993363[5] = 0;
   out_4852264167799993363[6] = 0;
   out_4852264167799993363[7] = 0;
   out_4852264167799993363[8] = 0;
   out_4852264167799993363[9] = 0;
   out_4852264167799993363[10] = 0;
   out_4852264167799993363[11] = 0;
   out_4852264167799993363[12] = 0;
   out_4852264167799993363[13] = 0;
   out_4852264167799993363[14] = 0;
   out_4852264167799993363[15] = 0;
   out_4852264167799993363[16] = 0;
   out_4852264167799993363[17] = 0;
   out_4852264167799993363[18] = 0;
   out_4852264167799993363[19] = 0;
   out_4852264167799993363[20] = 0;
   out_4852264167799993363[21] = 0;
   out_4852264167799993363[22] = 1;
   out_4852264167799993363[23] = 0;
   out_4852264167799993363[24] = 0;
   out_4852264167799993363[25] = 0;
   out_4852264167799993363[26] = 0;
   out_4852264167799993363[27] = 0;
   out_4852264167799993363[28] = 0;
   out_4852264167799993363[29] = 0;
   out_4852264167799993363[30] = 0;
   out_4852264167799993363[31] = 0;
   out_4852264167799993363[32] = 0;
   out_4852264167799993363[33] = 0;
   out_4852264167799993363[34] = 0;
   out_4852264167799993363[35] = 0;
   out_4852264167799993363[36] = 0;
   out_4852264167799993363[37] = 0;
   out_4852264167799993363[38] = 0;
   out_4852264167799993363[39] = 0;
   out_4852264167799993363[40] = 0;
   out_4852264167799993363[41] = 1;
   out_4852264167799993363[42] = 0;
   out_4852264167799993363[43] = 0;
   out_4852264167799993363[44] = 0;
   out_4852264167799993363[45] = 0;
   out_4852264167799993363[46] = 0;
   out_4852264167799993363[47] = 0;
   out_4852264167799993363[48] = 0;
   out_4852264167799993363[49] = 0;
   out_4852264167799993363[50] = 0;
   out_4852264167799993363[51] = 0;
   out_4852264167799993363[52] = 0;
   out_4852264167799993363[53] = 0;
}
void h_14(double *state, double *unused, double *out_7814084012328434224) {
   out_7814084012328434224[0] = state[6];
   out_7814084012328434224[1] = state[7];
   out_7814084012328434224[2] = state[8];
}
void H_14(double *state, double *unused, double *out_5603231198807145091) {
   out_5603231198807145091[0] = 0;
   out_5603231198807145091[1] = 0;
   out_5603231198807145091[2] = 0;
   out_5603231198807145091[3] = 0;
   out_5603231198807145091[4] = 0;
   out_5603231198807145091[5] = 0;
   out_5603231198807145091[6] = 1;
   out_5603231198807145091[7] = 0;
   out_5603231198807145091[8] = 0;
   out_5603231198807145091[9] = 0;
   out_5603231198807145091[10] = 0;
   out_5603231198807145091[11] = 0;
   out_5603231198807145091[12] = 0;
   out_5603231198807145091[13] = 0;
   out_5603231198807145091[14] = 0;
   out_5603231198807145091[15] = 0;
   out_5603231198807145091[16] = 0;
   out_5603231198807145091[17] = 0;
   out_5603231198807145091[18] = 0;
   out_5603231198807145091[19] = 0;
   out_5603231198807145091[20] = 0;
   out_5603231198807145091[21] = 0;
   out_5603231198807145091[22] = 0;
   out_5603231198807145091[23] = 0;
   out_5603231198807145091[24] = 0;
   out_5603231198807145091[25] = 1;
   out_5603231198807145091[26] = 0;
   out_5603231198807145091[27] = 0;
   out_5603231198807145091[28] = 0;
   out_5603231198807145091[29] = 0;
   out_5603231198807145091[30] = 0;
   out_5603231198807145091[31] = 0;
   out_5603231198807145091[32] = 0;
   out_5603231198807145091[33] = 0;
   out_5603231198807145091[34] = 0;
   out_5603231198807145091[35] = 0;
   out_5603231198807145091[36] = 0;
   out_5603231198807145091[37] = 0;
   out_5603231198807145091[38] = 0;
   out_5603231198807145091[39] = 0;
   out_5603231198807145091[40] = 0;
   out_5603231198807145091[41] = 0;
   out_5603231198807145091[42] = 0;
   out_5603231198807145091[43] = 0;
   out_5603231198807145091[44] = 1;
   out_5603231198807145091[45] = 0;
   out_5603231198807145091[46] = 0;
   out_5603231198807145091[47] = 0;
   out_5603231198807145091[48] = 0;
   out_5603231198807145091[49] = 0;
   out_5603231198807145091[50] = 0;
   out_5603231198807145091[51] = 0;
   out_5603231198807145091[52] = 0;
   out_5603231198807145091[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_6269171790765846050) {
  err_fun(nom_x, delta_x, out_6269171790765846050);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1497934558633100347) {
  inv_err_fun(nom_x, true_x, out_1497934558633100347);
}
void pose_H_mod_fun(double *state, double *out_7862392065184069712) {
  H_mod_fun(state, out_7862392065184069712);
}
void pose_f_fun(double *state, double dt, double *out_4855847476055627778) {
  f_fun(state,  dt, out_4855847476055627778);
}
void pose_F_fun(double *state, double dt, double *out_1703318423524786966) {
  F_fun(state,  dt, out_1703318423524786966);
}
void pose_h_4(double *state, double *unused, double *out_7821603690376207235) {
  h_4(state, unused, out_7821603690376207235);
}
void pose_H_4(double *state, double *unused, double *out_1639990342467660562) {
  H_4(state, unused, out_1639990342467660562);
}
void pose_h_10(double *state, double *unused, double *out_4627608962100745909) {
  h_10(state, unused, out_4627608962100745909);
}
void pose_H_10(double *state, double *unused, double *out_5548344007433806154) {
  H_10(state, unused, out_5548344007433806154);
}
void pose_h_13(double *state, double *unused, double *out_5105456950148742445) {
  h_13(state, unused, out_5105456950148742445);
}
void pose_H_13(double *state, double *unused, double *out_4852264167799993363) {
  H_13(state, unused, out_4852264167799993363);
}
void pose_h_14(double *state, double *unused, double *out_7814084012328434224) {
  h_14(state, unused, out_7814084012328434224);
}
void pose_H_14(double *state, double *unused, double *out_5603231198807145091) {
  H_14(state, unused, out_5603231198807145091);
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
