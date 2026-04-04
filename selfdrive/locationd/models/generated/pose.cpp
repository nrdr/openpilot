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
void err_fun(double *nom_x, double *delta_x, double *out_6954349063036595351) {
   out_6954349063036595351[0] = delta_x[0] + nom_x[0];
   out_6954349063036595351[1] = delta_x[1] + nom_x[1];
   out_6954349063036595351[2] = delta_x[2] + nom_x[2];
   out_6954349063036595351[3] = delta_x[3] + nom_x[3];
   out_6954349063036595351[4] = delta_x[4] + nom_x[4];
   out_6954349063036595351[5] = delta_x[5] + nom_x[5];
   out_6954349063036595351[6] = delta_x[6] + nom_x[6];
   out_6954349063036595351[7] = delta_x[7] + nom_x[7];
   out_6954349063036595351[8] = delta_x[8] + nom_x[8];
   out_6954349063036595351[9] = delta_x[9] + nom_x[9];
   out_6954349063036595351[10] = delta_x[10] + nom_x[10];
   out_6954349063036595351[11] = delta_x[11] + nom_x[11];
   out_6954349063036595351[12] = delta_x[12] + nom_x[12];
   out_6954349063036595351[13] = delta_x[13] + nom_x[13];
   out_6954349063036595351[14] = delta_x[14] + nom_x[14];
   out_6954349063036595351[15] = delta_x[15] + nom_x[15];
   out_6954349063036595351[16] = delta_x[16] + nom_x[16];
   out_6954349063036595351[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_682628527898263653) {
   out_682628527898263653[0] = -nom_x[0] + true_x[0];
   out_682628527898263653[1] = -nom_x[1] + true_x[1];
   out_682628527898263653[2] = -nom_x[2] + true_x[2];
   out_682628527898263653[3] = -nom_x[3] + true_x[3];
   out_682628527898263653[4] = -nom_x[4] + true_x[4];
   out_682628527898263653[5] = -nom_x[5] + true_x[5];
   out_682628527898263653[6] = -nom_x[6] + true_x[6];
   out_682628527898263653[7] = -nom_x[7] + true_x[7];
   out_682628527898263653[8] = -nom_x[8] + true_x[8];
   out_682628527898263653[9] = -nom_x[9] + true_x[9];
   out_682628527898263653[10] = -nom_x[10] + true_x[10];
   out_682628527898263653[11] = -nom_x[11] + true_x[11];
   out_682628527898263653[12] = -nom_x[12] + true_x[12];
   out_682628527898263653[13] = -nom_x[13] + true_x[13];
   out_682628527898263653[14] = -nom_x[14] + true_x[14];
   out_682628527898263653[15] = -nom_x[15] + true_x[15];
   out_682628527898263653[16] = -nom_x[16] + true_x[16];
   out_682628527898263653[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_1843936589147875527) {
   out_1843936589147875527[0] = 1.0;
   out_1843936589147875527[1] = 0.0;
   out_1843936589147875527[2] = 0.0;
   out_1843936589147875527[3] = 0.0;
   out_1843936589147875527[4] = 0.0;
   out_1843936589147875527[5] = 0.0;
   out_1843936589147875527[6] = 0.0;
   out_1843936589147875527[7] = 0.0;
   out_1843936589147875527[8] = 0.0;
   out_1843936589147875527[9] = 0.0;
   out_1843936589147875527[10] = 0.0;
   out_1843936589147875527[11] = 0.0;
   out_1843936589147875527[12] = 0.0;
   out_1843936589147875527[13] = 0.0;
   out_1843936589147875527[14] = 0.0;
   out_1843936589147875527[15] = 0.0;
   out_1843936589147875527[16] = 0.0;
   out_1843936589147875527[17] = 0.0;
   out_1843936589147875527[18] = 0.0;
   out_1843936589147875527[19] = 1.0;
   out_1843936589147875527[20] = 0.0;
   out_1843936589147875527[21] = 0.0;
   out_1843936589147875527[22] = 0.0;
   out_1843936589147875527[23] = 0.0;
   out_1843936589147875527[24] = 0.0;
   out_1843936589147875527[25] = 0.0;
   out_1843936589147875527[26] = 0.0;
   out_1843936589147875527[27] = 0.0;
   out_1843936589147875527[28] = 0.0;
   out_1843936589147875527[29] = 0.0;
   out_1843936589147875527[30] = 0.0;
   out_1843936589147875527[31] = 0.0;
   out_1843936589147875527[32] = 0.0;
   out_1843936589147875527[33] = 0.0;
   out_1843936589147875527[34] = 0.0;
   out_1843936589147875527[35] = 0.0;
   out_1843936589147875527[36] = 0.0;
   out_1843936589147875527[37] = 0.0;
   out_1843936589147875527[38] = 1.0;
   out_1843936589147875527[39] = 0.0;
   out_1843936589147875527[40] = 0.0;
   out_1843936589147875527[41] = 0.0;
   out_1843936589147875527[42] = 0.0;
   out_1843936589147875527[43] = 0.0;
   out_1843936589147875527[44] = 0.0;
   out_1843936589147875527[45] = 0.0;
   out_1843936589147875527[46] = 0.0;
   out_1843936589147875527[47] = 0.0;
   out_1843936589147875527[48] = 0.0;
   out_1843936589147875527[49] = 0.0;
   out_1843936589147875527[50] = 0.0;
   out_1843936589147875527[51] = 0.0;
   out_1843936589147875527[52] = 0.0;
   out_1843936589147875527[53] = 0.0;
   out_1843936589147875527[54] = 0.0;
   out_1843936589147875527[55] = 0.0;
   out_1843936589147875527[56] = 0.0;
   out_1843936589147875527[57] = 1.0;
   out_1843936589147875527[58] = 0.0;
   out_1843936589147875527[59] = 0.0;
   out_1843936589147875527[60] = 0.0;
   out_1843936589147875527[61] = 0.0;
   out_1843936589147875527[62] = 0.0;
   out_1843936589147875527[63] = 0.0;
   out_1843936589147875527[64] = 0.0;
   out_1843936589147875527[65] = 0.0;
   out_1843936589147875527[66] = 0.0;
   out_1843936589147875527[67] = 0.0;
   out_1843936589147875527[68] = 0.0;
   out_1843936589147875527[69] = 0.0;
   out_1843936589147875527[70] = 0.0;
   out_1843936589147875527[71] = 0.0;
   out_1843936589147875527[72] = 0.0;
   out_1843936589147875527[73] = 0.0;
   out_1843936589147875527[74] = 0.0;
   out_1843936589147875527[75] = 0.0;
   out_1843936589147875527[76] = 1.0;
   out_1843936589147875527[77] = 0.0;
   out_1843936589147875527[78] = 0.0;
   out_1843936589147875527[79] = 0.0;
   out_1843936589147875527[80] = 0.0;
   out_1843936589147875527[81] = 0.0;
   out_1843936589147875527[82] = 0.0;
   out_1843936589147875527[83] = 0.0;
   out_1843936589147875527[84] = 0.0;
   out_1843936589147875527[85] = 0.0;
   out_1843936589147875527[86] = 0.0;
   out_1843936589147875527[87] = 0.0;
   out_1843936589147875527[88] = 0.0;
   out_1843936589147875527[89] = 0.0;
   out_1843936589147875527[90] = 0.0;
   out_1843936589147875527[91] = 0.0;
   out_1843936589147875527[92] = 0.0;
   out_1843936589147875527[93] = 0.0;
   out_1843936589147875527[94] = 0.0;
   out_1843936589147875527[95] = 1.0;
   out_1843936589147875527[96] = 0.0;
   out_1843936589147875527[97] = 0.0;
   out_1843936589147875527[98] = 0.0;
   out_1843936589147875527[99] = 0.0;
   out_1843936589147875527[100] = 0.0;
   out_1843936589147875527[101] = 0.0;
   out_1843936589147875527[102] = 0.0;
   out_1843936589147875527[103] = 0.0;
   out_1843936589147875527[104] = 0.0;
   out_1843936589147875527[105] = 0.0;
   out_1843936589147875527[106] = 0.0;
   out_1843936589147875527[107] = 0.0;
   out_1843936589147875527[108] = 0.0;
   out_1843936589147875527[109] = 0.0;
   out_1843936589147875527[110] = 0.0;
   out_1843936589147875527[111] = 0.0;
   out_1843936589147875527[112] = 0.0;
   out_1843936589147875527[113] = 0.0;
   out_1843936589147875527[114] = 1.0;
   out_1843936589147875527[115] = 0.0;
   out_1843936589147875527[116] = 0.0;
   out_1843936589147875527[117] = 0.0;
   out_1843936589147875527[118] = 0.0;
   out_1843936589147875527[119] = 0.0;
   out_1843936589147875527[120] = 0.0;
   out_1843936589147875527[121] = 0.0;
   out_1843936589147875527[122] = 0.0;
   out_1843936589147875527[123] = 0.0;
   out_1843936589147875527[124] = 0.0;
   out_1843936589147875527[125] = 0.0;
   out_1843936589147875527[126] = 0.0;
   out_1843936589147875527[127] = 0.0;
   out_1843936589147875527[128] = 0.0;
   out_1843936589147875527[129] = 0.0;
   out_1843936589147875527[130] = 0.0;
   out_1843936589147875527[131] = 0.0;
   out_1843936589147875527[132] = 0.0;
   out_1843936589147875527[133] = 1.0;
   out_1843936589147875527[134] = 0.0;
   out_1843936589147875527[135] = 0.0;
   out_1843936589147875527[136] = 0.0;
   out_1843936589147875527[137] = 0.0;
   out_1843936589147875527[138] = 0.0;
   out_1843936589147875527[139] = 0.0;
   out_1843936589147875527[140] = 0.0;
   out_1843936589147875527[141] = 0.0;
   out_1843936589147875527[142] = 0.0;
   out_1843936589147875527[143] = 0.0;
   out_1843936589147875527[144] = 0.0;
   out_1843936589147875527[145] = 0.0;
   out_1843936589147875527[146] = 0.0;
   out_1843936589147875527[147] = 0.0;
   out_1843936589147875527[148] = 0.0;
   out_1843936589147875527[149] = 0.0;
   out_1843936589147875527[150] = 0.0;
   out_1843936589147875527[151] = 0.0;
   out_1843936589147875527[152] = 1.0;
   out_1843936589147875527[153] = 0.0;
   out_1843936589147875527[154] = 0.0;
   out_1843936589147875527[155] = 0.0;
   out_1843936589147875527[156] = 0.0;
   out_1843936589147875527[157] = 0.0;
   out_1843936589147875527[158] = 0.0;
   out_1843936589147875527[159] = 0.0;
   out_1843936589147875527[160] = 0.0;
   out_1843936589147875527[161] = 0.0;
   out_1843936589147875527[162] = 0.0;
   out_1843936589147875527[163] = 0.0;
   out_1843936589147875527[164] = 0.0;
   out_1843936589147875527[165] = 0.0;
   out_1843936589147875527[166] = 0.0;
   out_1843936589147875527[167] = 0.0;
   out_1843936589147875527[168] = 0.0;
   out_1843936589147875527[169] = 0.0;
   out_1843936589147875527[170] = 0.0;
   out_1843936589147875527[171] = 1.0;
   out_1843936589147875527[172] = 0.0;
   out_1843936589147875527[173] = 0.0;
   out_1843936589147875527[174] = 0.0;
   out_1843936589147875527[175] = 0.0;
   out_1843936589147875527[176] = 0.0;
   out_1843936589147875527[177] = 0.0;
   out_1843936589147875527[178] = 0.0;
   out_1843936589147875527[179] = 0.0;
   out_1843936589147875527[180] = 0.0;
   out_1843936589147875527[181] = 0.0;
   out_1843936589147875527[182] = 0.0;
   out_1843936589147875527[183] = 0.0;
   out_1843936589147875527[184] = 0.0;
   out_1843936589147875527[185] = 0.0;
   out_1843936589147875527[186] = 0.0;
   out_1843936589147875527[187] = 0.0;
   out_1843936589147875527[188] = 0.0;
   out_1843936589147875527[189] = 0.0;
   out_1843936589147875527[190] = 1.0;
   out_1843936589147875527[191] = 0.0;
   out_1843936589147875527[192] = 0.0;
   out_1843936589147875527[193] = 0.0;
   out_1843936589147875527[194] = 0.0;
   out_1843936589147875527[195] = 0.0;
   out_1843936589147875527[196] = 0.0;
   out_1843936589147875527[197] = 0.0;
   out_1843936589147875527[198] = 0.0;
   out_1843936589147875527[199] = 0.0;
   out_1843936589147875527[200] = 0.0;
   out_1843936589147875527[201] = 0.0;
   out_1843936589147875527[202] = 0.0;
   out_1843936589147875527[203] = 0.0;
   out_1843936589147875527[204] = 0.0;
   out_1843936589147875527[205] = 0.0;
   out_1843936589147875527[206] = 0.0;
   out_1843936589147875527[207] = 0.0;
   out_1843936589147875527[208] = 0.0;
   out_1843936589147875527[209] = 1.0;
   out_1843936589147875527[210] = 0.0;
   out_1843936589147875527[211] = 0.0;
   out_1843936589147875527[212] = 0.0;
   out_1843936589147875527[213] = 0.0;
   out_1843936589147875527[214] = 0.0;
   out_1843936589147875527[215] = 0.0;
   out_1843936589147875527[216] = 0.0;
   out_1843936589147875527[217] = 0.0;
   out_1843936589147875527[218] = 0.0;
   out_1843936589147875527[219] = 0.0;
   out_1843936589147875527[220] = 0.0;
   out_1843936589147875527[221] = 0.0;
   out_1843936589147875527[222] = 0.0;
   out_1843936589147875527[223] = 0.0;
   out_1843936589147875527[224] = 0.0;
   out_1843936589147875527[225] = 0.0;
   out_1843936589147875527[226] = 0.0;
   out_1843936589147875527[227] = 0.0;
   out_1843936589147875527[228] = 1.0;
   out_1843936589147875527[229] = 0.0;
   out_1843936589147875527[230] = 0.0;
   out_1843936589147875527[231] = 0.0;
   out_1843936589147875527[232] = 0.0;
   out_1843936589147875527[233] = 0.0;
   out_1843936589147875527[234] = 0.0;
   out_1843936589147875527[235] = 0.0;
   out_1843936589147875527[236] = 0.0;
   out_1843936589147875527[237] = 0.0;
   out_1843936589147875527[238] = 0.0;
   out_1843936589147875527[239] = 0.0;
   out_1843936589147875527[240] = 0.0;
   out_1843936589147875527[241] = 0.0;
   out_1843936589147875527[242] = 0.0;
   out_1843936589147875527[243] = 0.0;
   out_1843936589147875527[244] = 0.0;
   out_1843936589147875527[245] = 0.0;
   out_1843936589147875527[246] = 0.0;
   out_1843936589147875527[247] = 1.0;
   out_1843936589147875527[248] = 0.0;
   out_1843936589147875527[249] = 0.0;
   out_1843936589147875527[250] = 0.0;
   out_1843936589147875527[251] = 0.0;
   out_1843936589147875527[252] = 0.0;
   out_1843936589147875527[253] = 0.0;
   out_1843936589147875527[254] = 0.0;
   out_1843936589147875527[255] = 0.0;
   out_1843936589147875527[256] = 0.0;
   out_1843936589147875527[257] = 0.0;
   out_1843936589147875527[258] = 0.0;
   out_1843936589147875527[259] = 0.0;
   out_1843936589147875527[260] = 0.0;
   out_1843936589147875527[261] = 0.0;
   out_1843936589147875527[262] = 0.0;
   out_1843936589147875527[263] = 0.0;
   out_1843936589147875527[264] = 0.0;
   out_1843936589147875527[265] = 0.0;
   out_1843936589147875527[266] = 1.0;
   out_1843936589147875527[267] = 0.0;
   out_1843936589147875527[268] = 0.0;
   out_1843936589147875527[269] = 0.0;
   out_1843936589147875527[270] = 0.0;
   out_1843936589147875527[271] = 0.0;
   out_1843936589147875527[272] = 0.0;
   out_1843936589147875527[273] = 0.0;
   out_1843936589147875527[274] = 0.0;
   out_1843936589147875527[275] = 0.0;
   out_1843936589147875527[276] = 0.0;
   out_1843936589147875527[277] = 0.0;
   out_1843936589147875527[278] = 0.0;
   out_1843936589147875527[279] = 0.0;
   out_1843936589147875527[280] = 0.0;
   out_1843936589147875527[281] = 0.0;
   out_1843936589147875527[282] = 0.0;
   out_1843936589147875527[283] = 0.0;
   out_1843936589147875527[284] = 0.0;
   out_1843936589147875527[285] = 1.0;
   out_1843936589147875527[286] = 0.0;
   out_1843936589147875527[287] = 0.0;
   out_1843936589147875527[288] = 0.0;
   out_1843936589147875527[289] = 0.0;
   out_1843936589147875527[290] = 0.0;
   out_1843936589147875527[291] = 0.0;
   out_1843936589147875527[292] = 0.0;
   out_1843936589147875527[293] = 0.0;
   out_1843936589147875527[294] = 0.0;
   out_1843936589147875527[295] = 0.0;
   out_1843936589147875527[296] = 0.0;
   out_1843936589147875527[297] = 0.0;
   out_1843936589147875527[298] = 0.0;
   out_1843936589147875527[299] = 0.0;
   out_1843936589147875527[300] = 0.0;
   out_1843936589147875527[301] = 0.0;
   out_1843936589147875527[302] = 0.0;
   out_1843936589147875527[303] = 0.0;
   out_1843936589147875527[304] = 1.0;
   out_1843936589147875527[305] = 0.0;
   out_1843936589147875527[306] = 0.0;
   out_1843936589147875527[307] = 0.0;
   out_1843936589147875527[308] = 0.0;
   out_1843936589147875527[309] = 0.0;
   out_1843936589147875527[310] = 0.0;
   out_1843936589147875527[311] = 0.0;
   out_1843936589147875527[312] = 0.0;
   out_1843936589147875527[313] = 0.0;
   out_1843936589147875527[314] = 0.0;
   out_1843936589147875527[315] = 0.0;
   out_1843936589147875527[316] = 0.0;
   out_1843936589147875527[317] = 0.0;
   out_1843936589147875527[318] = 0.0;
   out_1843936589147875527[319] = 0.0;
   out_1843936589147875527[320] = 0.0;
   out_1843936589147875527[321] = 0.0;
   out_1843936589147875527[322] = 0.0;
   out_1843936589147875527[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_4568297489233837757) {
   out_4568297489233837757[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_4568297489233837757[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_4568297489233837757[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_4568297489233837757[3] = dt*state[12] + state[3];
   out_4568297489233837757[4] = dt*state[13] + state[4];
   out_4568297489233837757[5] = dt*state[14] + state[5];
   out_4568297489233837757[6] = state[6];
   out_4568297489233837757[7] = state[7];
   out_4568297489233837757[8] = state[8];
   out_4568297489233837757[9] = state[9];
   out_4568297489233837757[10] = state[10];
   out_4568297489233837757[11] = state[11];
   out_4568297489233837757[12] = state[12];
   out_4568297489233837757[13] = state[13];
   out_4568297489233837757[14] = state[14];
   out_4568297489233837757[15] = state[15];
   out_4568297489233837757[16] = state[16];
   out_4568297489233837757[17] = state[17];
}
void F_fun(double *state, double dt, double *out_8898375213134066991) {
   out_8898375213134066991[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8898375213134066991[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8898375213134066991[2] = 0;
   out_8898375213134066991[3] = 0;
   out_8898375213134066991[4] = 0;
   out_8898375213134066991[5] = 0;
   out_8898375213134066991[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8898375213134066991[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8898375213134066991[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8898375213134066991[9] = 0;
   out_8898375213134066991[10] = 0;
   out_8898375213134066991[11] = 0;
   out_8898375213134066991[12] = 0;
   out_8898375213134066991[13] = 0;
   out_8898375213134066991[14] = 0;
   out_8898375213134066991[15] = 0;
   out_8898375213134066991[16] = 0;
   out_8898375213134066991[17] = 0;
   out_8898375213134066991[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8898375213134066991[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8898375213134066991[20] = 0;
   out_8898375213134066991[21] = 0;
   out_8898375213134066991[22] = 0;
   out_8898375213134066991[23] = 0;
   out_8898375213134066991[24] = 0;
   out_8898375213134066991[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8898375213134066991[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8898375213134066991[27] = 0;
   out_8898375213134066991[28] = 0;
   out_8898375213134066991[29] = 0;
   out_8898375213134066991[30] = 0;
   out_8898375213134066991[31] = 0;
   out_8898375213134066991[32] = 0;
   out_8898375213134066991[33] = 0;
   out_8898375213134066991[34] = 0;
   out_8898375213134066991[35] = 0;
   out_8898375213134066991[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8898375213134066991[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8898375213134066991[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8898375213134066991[39] = 0;
   out_8898375213134066991[40] = 0;
   out_8898375213134066991[41] = 0;
   out_8898375213134066991[42] = 0;
   out_8898375213134066991[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8898375213134066991[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8898375213134066991[45] = 0;
   out_8898375213134066991[46] = 0;
   out_8898375213134066991[47] = 0;
   out_8898375213134066991[48] = 0;
   out_8898375213134066991[49] = 0;
   out_8898375213134066991[50] = 0;
   out_8898375213134066991[51] = 0;
   out_8898375213134066991[52] = 0;
   out_8898375213134066991[53] = 0;
   out_8898375213134066991[54] = 0;
   out_8898375213134066991[55] = 0;
   out_8898375213134066991[56] = 0;
   out_8898375213134066991[57] = 1;
   out_8898375213134066991[58] = 0;
   out_8898375213134066991[59] = 0;
   out_8898375213134066991[60] = 0;
   out_8898375213134066991[61] = 0;
   out_8898375213134066991[62] = 0;
   out_8898375213134066991[63] = 0;
   out_8898375213134066991[64] = 0;
   out_8898375213134066991[65] = 0;
   out_8898375213134066991[66] = dt;
   out_8898375213134066991[67] = 0;
   out_8898375213134066991[68] = 0;
   out_8898375213134066991[69] = 0;
   out_8898375213134066991[70] = 0;
   out_8898375213134066991[71] = 0;
   out_8898375213134066991[72] = 0;
   out_8898375213134066991[73] = 0;
   out_8898375213134066991[74] = 0;
   out_8898375213134066991[75] = 0;
   out_8898375213134066991[76] = 1;
   out_8898375213134066991[77] = 0;
   out_8898375213134066991[78] = 0;
   out_8898375213134066991[79] = 0;
   out_8898375213134066991[80] = 0;
   out_8898375213134066991[81] = 0;
   out_8898375213134066991[82] = 0;
   out_8898375213134066991[83] = 0;
   out_8898375213134066991[84] = 0;
   out_8898375213134066991[85] = dt;
   out_8898375213134066991[86] = 0;
   out_8898375213134066991[87] = 0;
   out_8898375213134066991[88] = 0;
   out_8898375213134066991[89] = 0;
   out_8898375213134066991[90] = 0;
   out_8898375213134066991[91] = 0;
   out_8898375213134066991[92] = 0;
   out_8898375213134066991[93] = 0;
   out_8898375213134066991[94] = 0;
   out_8898375213134066991[95] = 1;
   out_8898375213134066991[96] = 0;
   out_8898375213134066991[97] = 0;
   out_8898375213134066991[98] = 0;
   out_8898375213134066991[99] = 0;
   out_8898375213134066991[100] = 0;
   out_8898375213134066991[101] = 0;
   out_8898375213134066991[102] = 0;
   out_8898375213134066991[103] = 0;
   out_8898375213134066991[104] = dt;
   out_8898375213134066991[105] = 0;
   out_8898375213134066991[106] = 0;
   out_8898375213134066991[107] = 0;
   out_8898375213134066991[108] = 0;
   out_8898375213134066991[109] = 0;
   out_8898375213134066991[110] = 0;
   out_8898375213134066991[111] = 0;
   out_8898375213134066991[112] = 0;
   out_8898375213134066991[113] = 0;
   out_8898375213134066991[114] = 1;
   out_8898375213134066991[115] = 0;
   out_8898375213134066991[116] = 0;
   out_8898375213134066991[117] = 0;
   out_8898375213134066991[118] = 0;
   out_8898375213134066991[119] = 0;
   out_8898375213134066991[120] = 0;
   out_8898375213134066991[121] = 0;
   out_8898375213134066991[122] = 0;
   out_8898375213134066991[123] = 0;
   out_8898375213134066991[124] = 0;
   out_8898375213134066991[125] = 0;
   out_8898375213134066991[126] = 0;
   out_8898375213134066991[127] = 0;
   out_8898375213134066991[128] = 0;
   out_8898375213134066991[129] = 0;
   out_8898375213134066991[130] = 0;
   out_8898375213134066991[131] = 0;
   out_8898375213134066991[132] = 0;
   out_8898375213134066991[133] = 1;
   out_8898375213134066991[134] = 0;
   out_8898375213134066991[135] = 0;
   out_8898375213134066991[136] = 0;
   out_8898375213134066991[137] = 0;
   out_8898375213134066991[138] = 0;
   out_8898375213134066991[139] = 0;
   out_8898375213134066991[140] = 0;
   out_8898375213134066991[141] = 0;
   out_8898375213134066991[142] = 0;
   out_8898375213134066991[143] = 0;
   out_8898375213134066991[144] = 0;
   out_8898375213134066991[145] = 0;
   out_8898375213134066991[146] = 0;
   out_8898375213134066991[147] = 0;
   out_8898375213134066991[148] = 0;
   out_8898375213134066991[149] = 0;
   out_8898375213134066991[150] = 0;
   out_8898375213134066991[151] = 0;
   out_8898375213134066991[152] = 1;
   out_8898375213134066991[153] = 0;
   out_8898375213134066991[154] = 0;
   out_8898375213134066991[155] = 0;
   out_8898375213134066991[156] = 0;
   out_8898375213134066991[157] = 0;
   out_8898375213134066991[158] = 0;
   out_8898375213134066991[159] = 0;
   out_8898375213134066991[160] = 0;
   out_8898375213134066991[161] = 0;
   out_8898375213134066991[162] = 0;
   out_8898375213134066991[163] = 0;
   out_8898375213134066991[164] = 0;
   out_8898375213134066991[165] = 0;
   out_8898375213134066991[166] = 0;
   out_8898375213134066991[167] = 0;
   out_8898375213134066991[168] = 0;
   out_8898375213134066991[169] = 0;
   out_8898375213134066991[170] = 0;
   out_8898375213134066991[171] = 1;
   out_8898375213134066991[172] = 0;
   out_8898375213134066991[173] = 0;
   out_8898375213134066991[174] = 0;
   out_8898375213134066991[175] = 0;
   out_8898375213134066991[176] = 0;
   out_8898375213134066991[177] = 0;
   out_8898375213134066991[178] = 0;
   out_8898375213134066991[179] = 0;
   out_8898375213134066991[180] = 0;
   out_8898375213134066991[181] = 0;
   out_8898375213134066991[182] = 0;
   out_8898375213134066991[183] = 0;
   out_8898375213134066991[184] = 0;
   out_8898375213134066991[185] = 0;
   out_8898375213134066991[186] = 0;
   out_8898375213134066991[187] = 0;
   out_8898375213134066991[188] = 0;
   out_8898375213134066991[189] = 0;
   out_8898375213134066991[190] = 1;
   out_8898375213134066991[191] = 0;
   out_8898375213134066991[192] = 0;
   out_8898375213134066991[193] = 0;
   out_8898375213134066991[194] = 0;
   out_8898375213134066991[195] = 0;
   out_8898375213134066991[196] = 0;
   out_8898375213134066991[197] = 0;
   out_8898375213134066991[198] = 0;
   out_8898375213134066991[199] = 0;
   out_8898375213134066991[200] = 0;
   out_8898375213134066991[201] = 0;
   out_8898375213134066991[202] = 0;
   out_8898375213134066991[203] = 0;
   out_8898375213134066991[204] = 0;
   out_8898375213134066991[205] = 0;
   out_8898375213134066991[206] = 0;
   out_8898375213134066991[207] = 0;
   out_8898375213134066991[208] = 0;
   out_8898375213134066991[209] = 1;
   out_8898375213134066991[210] = 0;
   out_8898375213134066991[211] = 0;
   out_8898375213134066991[212] = 0;
   out_8898375213134066991[213] = 0;
   out_8898375213134066991[214] = 0;
   out_8898375213134066991[215] = 0;
   out_8898375213134066991[216] = 0;
   out_8898375213134066991[217] = 0;
   out_8898375213134066991[218] = 0;
   out_8898375213134066991[219] = 0;
   out_8898375213134066991[220] = 0;
   out_8898375213134066991[221] = 0;
   out_8898375213134066991[222] = 0;
   out_8898375213134066991[223] = 0;
   out_8898375213134066991[224] = 0;
   out_8898375213134066991[225] = 0;
   out_8898375213134066991[226] = 0;
   out_8898375213134066991[227] = 0;
   out_8898375213134066991[228] = 1;
   out_8898375213134066991[229] = 0;
   out_8898375213134066991[230] = 0;
   out_8898375213134066991[231] = 0;
   out_8898375213134066991[232] = 0;
   out_8898375213134066991[233] = 0;
   out_8898375213134066991[234] = 0;
   out_8898375213134066991[235] = 0;
   out_8898375213134066991[236] = 0;
   out_8898375213134066991[237] = 0;
   out_8898375213134066991[238] = 0;
   out_8898375213134066991[239] = 0;
   out_8898375213134066991[240] = 0;
   out_8898375213134066991[241] = 0;
   out_8898375213134066991[242] = 0;
   out_8898375213134066991[243] = 0;
   out_8898375213134066991[244] = 0;
   out_8898375213134066991[245] = 0;
   out_8898375213134066991[246] = 0;
   out_8898375213134066991[247] = 1;
   out_8898375213134066991[248] = 0;
   out_8898375213134066991[249] = 0;
   out_8898375213134066991[250] = 0;
   out_8898375213134066991[251] = 0;
   out_8898375213134066991[252] = 0;
   out_8898375213134066991[253] = 0;
   out_8898375213134066991[254] = 0;
   out_8898375213134066991[255] = 0;
   out_8898375213134066991[256] = 0;
   out_8898375213134066991[257] = 0;
   out_8898375213134066991[258] = 0;
   out_8898375213134066991[259] = 0;
   out_8898375213134066991[260] = 0;
   out_8898375213134066991[261] = 0;
   out_8898375213134066991[262] = 0;
   out_8898375213134066991[263] = 0;
   out_8898375213134066991[264] = 0;
   out_8898375213134066991[265] = 0;
   out_8898375213134066991[266] = 1;
   out_8898375213134066991[267] = 0;
   out_8898375213134066991[268] = 0;
   out_8898375213134066991[269] = 0;
   out_8898375213134066991[270] = 0;
   out_8898375213134066991[271] = 0;
   out_8898375213134066991[272] = 0;
   out_8898375213134066991[273] = 0;
   out_8898375213134066991[274] = 0;
   out_8898375213134066991[275] = 0;
   out_8898375213134066991[276] = 0;
   out_8898375213134066991[277] = 0;
   out_8898375213134066991[278] = 0;
   out_8898375213134066991[279] = 0;
   out_8898375213134066991[280] = 0;
   out_8898375213134066991[281] = 0;
   out_8898375213134066991[282] = 0;
   out_8898375213134066991[283] = 0;
   out_8898375213134066991[284] = 0;
   out_8898375213134066991[285] = 1;
   out_8898375213134066991[286] = 0;
   out_8898375213134066991[287] = 0;
   out_8898375213134066991[288] = 0;
   out_8898375213134066991[289] = 0;
   out_8898375213134066991[290] = 0;
   out_8898375213134066991[291] = 0;
   out_8898375213134066991[292] = 0;
   out_8898375213134066991[293] = 0;
   out_8898375213134066991[294] = 0;
   out_8898375213134066991[295] = 0;
   out_8898375213134066991[296] = 0;
   out_8898375213134066991[297] = 0;
   out_8898375213134066991[298] = 0;
   out_8898375213134066991[299] = 0;
   out_8898375213134066991[300] = 0;
   out_8898375213134066991[301] = 0;
   out_8898375213134066991[302] = 0;
   out_8898375213134066991[303] = 0;
   out_8898375213134066991[304] = 1;
   out_8898375213134066991[305] = 0;
   out_8898375213134066991[306] = 0;
   out_8898375213134066991[307] = 0;
   out_8898375213134066991[308] = 0;
   out_8898375213134066991[309] = 0;
   out_8898375213134066991[310] = 0;
   out_8898375213134066991[311] = 0;
   out_8898375213134066991[312] = 0;
   out_8898375213134066991[313] = 0;
   out_8898375213134066991[314] = 0;
   out_8898375213134066991[315] = 0;
   out_8898375213134066991[316] = 0;
   out_8898375213134066991[317] = 0;
   out_8898375213134066991[318] = 0;
   out_8898375213134066991[319] = 0;
   out_8898375213134066991[320] = 0;
   out_8898375213134066991[321] = 0;
   out_8898375213134066991[322] = 0;
   out_8898375213134066991[323] = 1;
}
void h_4(double *state, double *unused, double *out_7637245117322563109) {
   out_7637245117322563109[0] = state[6] + state[9];
   out_7637245117322563109[1] = state[7] + state[10];
   out_7637245117322563109[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_7021791425393278159) {
   out_7021791425393278159[0] = 0;
   out_7021791425393278159[1] = 0;
   out_7021791425393278159[2] = 0;
   out_7021791425393278159[3] = 0;
   out_7021791425393278159[4] = 0;
   out_7021791425393278159[5] = 0;
   out_7021791425393278159[6] = 1;
   out_7021791425393278159[7] = 0;
   out_7021791425393278159[8] = 0;
   out_7021791425393278159[9] = 1;
   out_7021791425393278159[10] = 0;
   out_7021791425393278159[11] = 0;
   out_7021791425393278159[12] = 0;
   out_7021791425393278159[13] = 0;
   out_7021791425393278159[14] = 0;
   out_7021791425393278159[15] = 0;
   out_7021791425393278159[16] = 0;
   out_7021791425393278159[17] = 0;
   out_7021791425393278159[18] = 0;
   out_7021791425393278159[19] = 0;
   out_7021791425393278159[20] = 0;
   out_7021791425393278159[21] = 0;
   out_7021791425393278159[22] = 0;
   out_7021791425393278159[23] = 0;
   out_7021791425393278159[24] = 0;
   out_7021791425393278159[25] = 1;
   out_7021791425393278159[26] = 0;
   out_7021791425393278159[27] = 0;
   out_7021791425393278159[28] = 1;
   out_7021791425393278159[29] = 0;
   out_7021791425393278159[30] = 0;
   out_7021791425393278159[31] = 0;
   out_7021791425393278159[32] = 0;
   out_7021791425393278159[33] = 0;
   out_7021791425393278159[34] = 0;
   out_7021791425393278159[35] = 0;
   out_7021791425393278159[36] = 0;
   out_7021791425393278159[37] = 0;
   out_7021791425393278159[38] = 0;
   out_7021791425393278159[39] = 0;
   out_7021791425393278159[40] = 0;
   out_7021791425393278159[41] = 0;
   out_7021791425393278159[42] = 0;
   out_7021791425393278159[43] = 0;
   out_7021791425393278159[44] = 1;
   out_7021791425393278159[45] = 0;
   out_7021791425393278159[46] = 0;
   out_7021791425393278159[47] = 1;
   out_7021791425393278159[48] = 0;
   out_7021791425393278159[49] = 0;
   out_7021791425393278159[50] = 0;
   out_7021791425393278159[51] = 0;
   out_7021791425393278159[52] = 0;
   out_7021791425393278159[53] = 0;
}
void h_10(double *state, double *unused, double *out_5758875815588475648) {
   out_5758875815588475648[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_5758875815588475648[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_5758875815588475648[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_967659597114898975) {
   out_967659597114898975[0] = 0;
   out_967659597114898975[1] = 9.8100000000000005*cos(state[1]);
   out_967659597114898975[2] = 0;
   out_967659597114898975[3] = 0;
   out_967659597114898975[4] = -state[8];
   out_967659597114898975[5] = state[7];
   out_967659597114898975[6] = 0;
   out_967659597114898975[7] = state[5];
   out_967659597114898975[8] = -state[4];
   out_967659597114898975[9] = 0;
   out_967659597114898975[10] = 0;
   out_967659597114898975[11] = 0;
   out_967659597114898975[12] = 1;
   out_967659597114898975[13] = 0;
   out_967659597114898975[14] = 0;
   out_967659597114898975[15] = 1;
   out_967659597114898975[16] = 0;
   out_967659597114898975[17] = 0;
   out_967659597114898975[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_967659597114898975[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_967659597114898975[20] = 0;
   out_967659597114898975[21] = state[8];
   out_967659597114898975[22] = 0;
   out_967659597114898975[23] = -state[6];
   out_967659597114898975[24] = -state[5];
   out_967659597114898975[25] = 0;
   out_967659597114898975[26] = state[3];
   out_967659597114898975[27] = 0;
   out_967659597114898975[28] = 0;
   out_967659597114898975[29] = 0;
   out_967659597114898975[30] = 0;
   out_967659597114898975[31] = 1;
   out_967659597114898975[32] = 0;
   out_967659597114898975[33] = 0;
   out_967659597114898975[34] = 1;
   out_967659597114898975[35] = 0;
   out_967659597114898975[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_967659597114898975[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_967659597114898975[38] = 0;
   out_967659597114898975[39] = -state[7];
   out_967659597114898975[40] = state[6];
   out_967659597114898975[41] = 0;
   out_967659597114898975[42] = state[4];
   out_967659597114898975[43] = -state[3];
   out_967659597114898975[44] = 0;
   out_967659597114898975[45] = 0;
   out_967659597114898975[46] = 0;
   out_967659597114898975[47] = 0;
   out_967659597114898975[48] = 0;
   out_967659597114898975[49] = 0;
   out_967659597114898975[50] = 1;
   out_967659597114898975[51] = 0;
   out_967659597114898975[52] = 0;
   out_967659597114898975[53] = 1;
}
void h_13(double *state, double *unused, double *out_1246309401103887941) {
   out_1246309401103887941[0] = state[3];
   out_1246309401103887941[1] = state[4];
   out_1246309401103887941[2] = state[5];
}
void H_13(double *state, double *unused, double *out_3809517600060945358) {
   out_3809517600060945358[0] = 0;
   out_3809517600060945358[1] = 0;
   out_3809517600060945358[2] = 0;
   out_3809517600060945358[3] = 1;
   out_3809517600060945358[4] = 0;
   out_3809517600060945358[5] = 0;
   out_3809517600060945358[6] = 0;
   out_3809517600060945358[7] = 0;
   out_3809517600060945358[8] = 0;
   out_3809517600060945358[9] = 0;
   out_3809517600060945358[10] = 0;
   out_3809517600060945358[11] = 0;
   out_3809517600060945358[12] = 0;
   out_3809517600060945358[13] = 0;
   out_3809517600060945358[14] = 0;
   out_3809517600060945358[15] = 0;
   out_3809517600060945358[16] = 0;
   out_3809517600060945358[17] = 0;
   out_3809517600060945358[18] = 0;
   out_3809517600060945358[19] = 0;
   out_3809517600060945358[20] = 0;
   out_3809517600060945358[21] = 0;
   out_3809517600060945358[22] = 1;
   out_3809517600060945358[23] = 0;
   out_3809517600060945358[24] = 0;
   out_3809517600060945358[25] = 0;
   out_3809517600060945358[26] = 0;
   out_3809517600060945358[27] = 0;
   out_3809517600060945358[28] = 0;
   out_3809517600060945358[29] = 0;
   out_3809517600060945358[30] = 0;
   out_3809517600060945358[31] = 0;
   out_3809517600060945358[32] = 0;
   out_3809517600060945358[33] = 0;
   out_3809517600060945358[34] = 0;
   out_3809517600060945358[35] = 0;
   out_3809517600060945358[36] = 0;
   out_3809517600060945358[37] = 0;
   out_3809517600060945358[38] = 0;
   out_3809517600060945358[39] = 0;
   out_3809517600060945358[40] = 0;
   out_3809517600060945358[41] = 1;
   out_3809517600060945358[42] = 0;
   out_3809517600060945358[43] = 0;
   out_3809517600060945358[44] = 0;
   out_3809517600060945358[45] = 0;
   out_3809517600060945358[46] = 0;
   out_3809517600060945358[47] = 0;
   out_3809517600060945358[48] = 0;
   out_3809517600060945358[49] = 0;
   out_3809517600060945358[50] = 0;
   out_3809517600060945358[51] = 0;
   out_3809517600060945358[52] = 0;
   out_3809517600060945358[53] = 0;
}
void h_14(double *state, double *unused, double *out_8756863864319304456) {
   out_8756863864319304456[0] = state[6];
   out_8756863864319304456[1] = state[7];
   out_8756863864319304456[2] = state[8];
}
void H_14(double *state, double *unused, double *out_3058550569053793630) {
   out_3058550569053793630[0] = 0;
   out_3058550569053793630[1] = 0;
   out_3058550569053793630[2] = 0;
   out_3058550569053793630[3] = 0;
   out_3058550569053793630[4] = 0;
   out_3058550569053793630[5] = 0;
   out_3058550569053793630[6] = 1;
   out_3058550569053793630[7] = 0;
   out_3058550569053793630[8] = 0;
   out_3058550569053793630[9] = 0;
   out_3058550569053793630[10] = 0;
   out_3058550569053793630[11] = 0;
   out_3058550569053793630[12] = 0;
   out_3058550569053793630[13] = 0;
   out_3058550569053793630[14] = 0;
   out_3058550569053793630[15] = 0;
   out_3058550569053793630[16] = 0;
   out_3058550569053793630[17] = 0;
   out_3058550569053793630[18] = 0;
   out_3058550569053793630[19] = 0;
   out_3058550569053793630[20] = 0;
   out_3058550569053793630[21] = 0;
   out_3058550569053793630[22] = 0;
   out_3058550569053793630[23] = 0;
   out_3058550569053793630[24] = 0;
   out_3058550569053793630[25] = 1;
   out_3058550569053793630[26] = 0;
   out_3058550569053793630[27] = 0;
   out_3058550569053793630[28] = 0;
   out_3058550569053793630[29] = 0;
   out_3058550569053793630[30] = 0;
   out_3058550569053793630[31] = 0;
   out_3058550569053793630[32] = 0;
   out_3058550569053793630[33] = 0;
   out_3058550569053793630[34] = 0;
   out_3058550569053793630[35] = 0;
   out_3058550569053793630[36] = 0;
   out_3058550569053793630[37] = 0;
   out_3058550569053793630[38] = 0;
   out_3058550569053793630[39] = 0;
   out_3058550569053793630[40] = 0;
   out_3058550569053793630[41] = 0;
   out_3058550569053793630[42] = 0;
   out_3058550569053793630[43] = 0;
   out_3058550569053793630[44] = 1;
   out_3058550569053793630[45] = 0;
   out_3058550569053793630[46] = 0;
   out_3058550569053793630[47] = 0;
   out_3058550569053793630[48] = 0;
   out_3058550569053793630[49] = 0;
   out_3058550569053793630[50] = 0;
   out_3058550569053793630[51] = 0;
   out_3058550569053793630[52] = 0;
   out_3058550569053793630[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_6954349063036595351) {
  err_fun(nom_x, delta_x, out_6954349063036595351);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_682628527898263653) {
  inv_err_fun(nom_x, true_x, out_682628527898263653);
}
void pose_H_mod_fun(double *state, double *out_1843936589147875527) {
  H_mod_fun(state, out_1843936589147875527);
}
void pose_f_fun(double *state, double dt, double *out_4568297489233837757) {
  f_fun(state,  dt, out_4568297489233837757);
}
void pose_F_fun(double *state, double dt, double *out_8898375213134066991) {
  F_fun(state,  dt, out_8898375213134066991);
}
void pose_h_4(double *state, double *unused, double *out_7637245117322563109) {
  h_4(state, unused, out_7637245117322563109);
}
void pose_H_4(double *state, double *unused, double *out_7021791425393278159) {
  H_4(state, unused, out_7021791425393278159);
}
void pose_h_10(double *state, double *unused, double *out_5758875815588475648) {
  h_10(state, unused, out_5758875815588475648);
}
void pose_H_10(double *state, double *unused, double *out_967659597114898975) {
  H_10(state, unused, out_967659597114898975);
}
void pose_h_13(double *state, double *unused, double *out_1246309401103887941) {
  h_13(state, unused, out_1246309401103887941);
}
void pose_H_13(double *state, double *unused, double *out_3809517600060945358) {
  H_13(state, unused, out_3809517600060945358);
}
void pose_h_14(double *state, double *unused, double *out_8756863864319304456) {
  h_14(state, unused, out_8756863864319304456);
}
void pose_H_14(double *state, double *unused, double *out_3058550569053793630) {
  H_14(state, unused, out_3058550569053793630);
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
