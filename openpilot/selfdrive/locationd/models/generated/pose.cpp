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
void err_fun(double *nom_x, double *delta_x, double *out_4541492771646069759) {
   out_4541492771646069759[0] = delta_x[0] + nom_x[0];
   out_4541492771646069759[1] = delta_x[1] + nom_x[1];
   out_4541492771646069759[2] = delta_x[2] + nom_x[2];
   out_4541492771646069759[3] = delta_x[3] + nom_x[3];
   out_4541492771646069759[4] = delta_x[4] + nom_x[4];
   out_4541492771646069759[5] = delta_x[5] + nom_x[5];
   out_4541492771646069759[6] = delta_x[6] + nom_x[6];
   out_4541492771646069759[7] = delta_x[7] + nom_x[7];
   out_4541492771646069759[8] = delta_x[8] + nom_x[8];
   out_4541492771646069759[9] = delta_x[9] + nom_x[9];
   out_4541492771646069759[10] = delta_x[10] + nom_x[10];
   out_4541492771646069759[11] = delta_x[11] + nom_x[11];
   out_4541492771646069759[12] = delta_x[12] + nom_x[12];
   out_4541492771646069759[13] = delta_x[13] + nom_x[13];
   out_4541492771646069759[14] = delta_x[14] + nom_x[14];
   out_4541492771646069759[15] = delta_x[15] + nom_x[15];
   out_4541492771646069759[16] = delta_x[16] + nom_x[16];
   out_4541492771646069759[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_3364276346708699962) {
   out_3364276346708699962[0] = -nom_x[0] + true_x[0];
   out_3364276346708699962[1] = -nom_x[1] + true_x[1];
   out_3364276346708699962[2] = -nom_x[2] + true_x[2];
   out_3364276346708699962[3] = -nom_x[3] + true_x[3];
   out_3364276346708699962[4] = -nom_x[4] + true_x[4];
   out_3364276346708699962[5] = -nom_x[5] + true_x[5];
   out_3364276346708699962[6] = -nom_x[6] + true_x[6];
   out_3364276346708699962[7] = -nom_x[7] + true_x[7];
   out_3364276346708699962[8] = -nom_x[8] + true_x[8];
   out_3364276346708699962[9] = -nom_x[9] + true_x[9];
   out_3364276346708699962[10] = -nom_x[10] + true_x[10];
   out_3364276346708699962[11] = -nom_x[11] + true_x[11];
   out_3364276346708699962[12] = -nom_x[12] + true_x[12];
   out_3364276346708699962[13] = -nom_x[13] + true_x[13];
   out_3364276346708699962[14] = -nom_x[14] + true_x[14];
   out_3364276346708699962[15] = -nom_x[15] + true_x[15];
   out_3364276346708699962[16] = -nom_x[16] + true_x[16];
   out_3364276346708699962[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_7182100953115386674) {
   out_7182100953115386674[0] = 1.0;
   out_7182100953115386674[1] = 0.0;
   out_7182100953115386674[2] = 0.0;
   out_7182100953115386674[3] = 0.0;
   out_7182100953115386674[4] = 0.0;
   out_7182100953115386674[5] = 0.0;
   out_7182100953115386674[6] = 0.0;
   out_7182100953115386674[7] = 0.0;
   out_7182100953115386674[8] = 0.0;
   out_7182100953115386674[9] = 0.0;
   out_7182100953115386674[10] = 0.0;
   out_7182100953115386674[11] = 0.0;
   out_7182100953115386674[12] = 0.0;
   out_7182100953115386674[13] = 0.0;
   out_7182100953115386674[14] = 0.0;
   out_7182100953115386674[15] = 0.0;
   out_7182100953115386674[16] = 0.0;
   out_7182100953115386674[17] = 0.0;
   out_7182100953115386674[18] = 0.0;
   out_7182100953115386674[19] = 1.0;
   out_7182100953115386674[20] = 0.0;
   out_7182100953115386674[21] = 0.0;
   out_7182100953115386674[22] = 0.0;
   out_7182100953115386674[23] = 0.0;
   out_7182100953115386674[24] = 0.0;
   out_7182100953115386674[25] = 0.0;
   out_7182100953115386674[26] = 0.0;
   out_7182100953115386674[27] = 0.0;
   out_7182100953115386674[28] = 0.0;
   out_7182100953115386674[29] = 0.0;
   out_7182100953115386674[30] = 0.0;
   out_7182100953115386674[31] = 0.0;
   out_7182100953115386674[32] = 0.0;
   out_7182100953115386674[33] = 0.0;
   out_7182100953115386674[34] = 0.0;
   out_7182100953115386674[35] = 0.0;
   out_7182100953115386674[36] = 0.0;
   out_7182100953115386674[37] = 0.0;
   out_7182100953115386674[38] = 1.0;
   out_7182100953115386674[39] = 0.0;
   out_7182100953115386674[40] = 0.0;
   out_7182100953115386674[41] = 0.0;
   out_7182100953115386674[42] = 0.0;
   out_7182100953115386674[43] = 0.0;
   out_7182100953115386674[44] = 0.0;
   out_7182100953115386674[45] = 0.0;
   out_7182100953115386674[46] = 0.0;
   out_7182100953115386674[47] = 0.0;
   out_7182100953115386674[48] = 0.0;
   out_7182100953115386674[49] = 0.0;
   out_7182100953115386674[50] = 0.0;
   out_7182100953115386674[51] = 0.0;
   out_7182100953115386674[52] = 0.0;
   out_7182100953115386674[53] = 0.0;
   out_7182100953115386674[54] = 0.0;
   out_7182100953115386674[55] = 0.0;
   out_7182100953115386674[56] = 0.0;
   out_7182100953115386674[57] = 1.0;
   out_7182100953115386674[58] = 0.0;
   out_7182100953115386674[59] = 0.0;
   out_7182100953115386674[60] = 0.0;
   out_7182100953115386674[61] = 0.0;
   out_7182100953115386674[62] = 0.0;
   out_7182100953115386674[63] = 0.0;
   out_7182100953115386674[64] = 0.0;
   out_7182100953115386674[65] = 0.0;
   out_7182100953115386674[66] = 0.0;
   out_7182100953115386674[67] = 0.0;
   out_7182100953115386674[68] = 0.0;
   out_7182100953115386674[69] = 0.0;
   out_7182100953115386674[70] = 0.0;
   out_7182100953115386674[71] = 0.0;
   out_7182100953115386674[72] = 0.0;
   out_7182100953115386674[73] = 0.0;
   out_7182100953115386674[74] = 0.0;
   out_7182100953115386674[75] = 0.0;
   out_7182100953115386674[76] = 1.0;
   out_7182100953115386674[77] = 0.0;
   out_7182100953115386674[78] = 0.0;
   out_7182100953115386674[79] = 0.0;
   out_7182100953115386674[80] = 0.0;
   out_7182100953115386674[81] = 0.0;
   out_7182100953115386674[82] = 0.0;
   out_7182100953115386674[83] = 0.0;
   out_7182100953115386674[84] = 0.0;
   out_7182100953115386674[85] = 0.0;
   out_7182100953115386674[86] = 0.0;
   out_7182100953115386674[87] = 0.0;
   out_7182100953115386674[88] = 0.0;
   out_7182100953115386674[89] = 0.0;
   out_7182100953115386674[90] = 0.0;
   out_7182100953115386674[91] = 0.0;
   out_7182100953115386674[92] = 0.0;
   out_7182100953115386674[93] = 0.0;
   out_7182100953115386674[94] = 0.0;
   out_7182100953115386674[95] = 1.0;
   out_7182100953115386674[96] = 0.0;
   out_7182100953115386674[97] = 0.0;
   out_7182100953115386674[98] = 0.0;
   out_7182100953115386674[99] = 0.0;
   out_7182100953115386674[100] = 0.0;
   out_7182100953115386674[101] = 0.0;
   out_7182100953115386674[102] = 0.0;
   out_7182100953115386674[103] = 0.0;
   out_7182100953115386674[104] = 0.0;
   out_7182100953115386674[105] = 0.0;
   out_7182100953115386674[106] = 0.0;
   out_7182100953115386674[107] = 0.0;
   out_7182100953115386674[108] = 0.0;
   out_7182100953115386674[109] = 0.0;
   out_7182100953115386674[110] = 0.0;
   out_7182100953115386674[111] = 0.0;
   out_7182100953115386674[112] = 0.0;
   out_7182100953115386674[113] = 0.0;
   out_7182100953115386674[114] = 1.0;
   out_7182100953115386674[115] = 0.0;
   out_7182100953115386674[116] = 0.0;
   out_7182100953115386674[117] = 0.0;
   out_7182100953115386674[118] = 0.0;
   out_7182100953115386674[119] = 0.0;
   out_7182100953115386674[120] = 0.0;
   out_7182100953115386674[121] = 0.0;
   out_7182100953115386674[122] = 0.0;
   out_7182100953115386674[123] = 0.0;
   out_7182100953115386674[124] = 0.0;
   out_7182100953115386674[125] = 0.0;
   out_7182100953115386674[126] = 0.0;
   out_7182100953115386674[127] = 0.0;
   out_7182100953115386674[128] = 0.0;
   out_7182100953115386674[129] = 0.0;
   out_7182100953115386674[130] = 0.0;
   out_7182100953115386674[131] = 0.0;
   out_7182100953115386674[132] = 0.0;
   out_7182100953115386674[133] = 1.0;
   out_7182100953115386674[134] = 0.0;
   out_7182100953115386674[135] = 0.0;
   out_7182100953115386674[136] = 0.0;
   out_7182100953115386674[137] = 0.0;
   out_7182100953115386674[138] = 0.0;
   out_7182100953115386674[139] = 0.0;
   out_7182100953115386674[140] = 0.0;
   out_7182100953115386674[141] = 0.0;
   out_7182100953115386674[142] = 0.0;
   out_7182100953115386674[143] = 0.0;
   out_7182100953115386674[144] = 0.0;
   out_7182100953115386674[145] = 0.0;
   out_7182100953115386674[146] = 0.0;
   out_7182100953115386674[147] = 0.0;
   out_7182100953115386674[148] = 0.0;
   out_7182100953115386674[149] = 0.0;
   out_7182100953115386674[150] = 0.0;
   out_7182100953115386674[151] = 0.0;
   out_7182100953115386674[152] = 1.0;
   out_7182100953115386674[153] = 0.0;
   out_7182100953115386674[154] = 0.0;
   out_7182100953115386674[155] = 0.0;
   out_7182100953115386674[156] = 0.0;
   out_7182100953115386674[157] = 0.0;
   out_7182100953115386674[158] = 0.0;
   out_7182100953115386674[159] = 0.0;
   out_7182100953115386674[160] = 0.0;
   out_7182100953115386674[161] = 0.0;
   out_7182100953115386674[162] = 0.0;
   out_7182100953115386674[163] = 0.0;
   out_7182100953115386674[164] = 0.0;
   out_7182100953115386674[165] = 0.0;
   out_7182100953115386674[166] = 0.0;
   out_7182100953115386674[167] = 0.0;
   out_7182100953115386674[168] = 0.0;
   out_7182100953115386674[169] = 0.0;
   out_7182100953115386674[170] = 0.0;
   out_7182100953115386674[171] = 1.0;
   out_7182100953115386674[172] = 0.0;
   out_7182100953115386674[173] = 0.0;
   out_7182100953115386674[174] = 0.0;
   out_7182100953115386674[175] = 0.0;
   out_7182100953115386674[176] = 0.0;
   out_7182100953115386674[177] = 0.0;
   out_7182100953115386674[178] = 0.0;
   out_7182100953115386674[179] = 0.0;
   out_7182100953115386674[180] = 0.0;
   out_7182100953115386674[181] = 0.0;
   out_7182100953115386674[182] = 0.0;
   out_7182100953115386674[183] = 0.0;
   out_7182100953115386674[184] = 0.0;
   out_7182100953115386674[185] = 0.0;
   out_7182100953115386674[186] = 0.0;
   out_7182100953115386674[187] = 0.0;
   out_7182100953115386674[188] = 0.0;
   out_7182100953115386674[189] = 0.0;
   out_7182100953115386674[190] = 1.0;
   out_7182100953115386674[191] = 0.0;
   out_7182100953115386674[192] = 0.0;
   out_7182100953115386674[193] = 0.0;
   out_7182100953115386674[194] = 0.0;
   out_7182100953115386674[195] = 0.0;
   out_7182100953115386674[196] = 0.0;
   out_7182100953115386674[197] = 0.0;
   out_7182100953115386674[198] = 0.0;
   out_7182100953115386674[199] = 0.0;
   out_7182100953115386674[200] = 0.0;
   out_7182100953115386674[201] = 0.0;
   out_7182100953115386674[202] = 0.0;
   out_7182100953115386674[203] = 0.0;
   out_7182100953115386674[204] = 0.0;
   out_7182100953115386674[205] = 0.0;
   out_7182100953115386674[206] = 0.0;
   out_7182100953115386674[207] = 0.0;
   out_7182100953115386674[208] = 0.0;
   out_7182100953115386674[209] = 1.0;
   out_7182100953115386674[210] = 0.0;
   out_7182100953115386674[211] = 0.0;
   out_7182100953115386674[212] = 0.0;
   out_7182100953115386674[213] = 0.0;
   out_7182100953115386674[214] = 0.0;
   out_7182100953115386674[215] = 0.0;
   out_7182100953115386674[216] = 0.0;
   out_7182100953115386674[217] = 0.0;
   out_7182100953115386674[218] = 0.0;
   out_7182100953115386674[219] = 0.0;
   out_7182100953115386674[220] = 0.0;
   out_7182100953115386674[221] = 0.0;
   out_7182100953115386674[222] = 0.0;
   out_7182100953115386674[223] = 0.0;
   out_7182100953115386674[224] = 0.0;
   out_7182100953115386674[225] = 0.0;
   out_7182100953115386674[226] = 0.0;
   out_7182100953115386674[227] = 0.0;
   out_7182100953115386674[228] = 1.0;
   out_7182100953115386674[229] = 0.0;
   out_7182100953115386674[230] = 0.0;
   out_7182100953115386674[231] = 0.0;
   out_7182100953115386674[232] = 0.0;
   out_7182100953115386674[233] = 0.0;
   out_7182100953115386674[234] = 0.0;
   out_7182100953115386674[235] = 0.0;
   out_7182100953115386674[236] = 0.0;
   out_7182100953115386674[237] = 0.0;
   out_7182100953115386674[238] = 0.0;
   out_7182100953115386674[239] = 0.0;
   out_7182100953115386674[240] = 0.0;
   out_7182100953115386674[241] = 0.0;
   out_7182100953115386674[242] = 0.0;
   out_7182100953115386674[243] = 0.0;
   out_7182100953115386674[244] = 0.0;
   out_7182100953115386674[245] = 0.0;
   out_7182100953115386674[246] = 0.0;
   out_7182100953115386674[247] = 1.0;
   out_7182100953115386674[248] = 0.0;
   out_7182100953115386674[249] = 0.0;
   out_7182100953115386674[250] = 0.0;
   out_7182100953115386674[251] = 0.0;
   out_7182100953115386674[252] = 0.0;
   out_7182100953115386674[253] = 0.0;
   out_7182100953115386674[254] = 0.0;
   out_7182100953115386674[255] = 0.0;
   out_7182100953115386674[256] = 0.0;
   out_7182100953115386674[257] = 0.0;
   out_7182100953115386674[258] = 0.0;
   out_7182100953115386674[259] = 0.0;
   out_7182100953115386674[260] = 0.0;
   out_7182100953115386674[261] = 0.0;
   out_7182100953115386674[262] = 0.0;
   out_7182100953115386674[263] = 0.0;
   out_7182100953115386674[264] = 0.0;
   out_7182100953115386674[265] = 0.0;
   out_7182100953115386674[266] = 1.0;
   out_7182100953115386674[267] = 0.0;
   out_7182100953115386674[268] = 0.0;
   out_7182100953115386674[269] = 0.0;
   out_7182100953115386674[270] = 0.0;
   out_7182100953115386674[271] = 0.0;
   out_7182100953115386674[272] = 0.0;
   out_7182100953115386674[273] = 0.0;
   out_7182100953115386674[274] = 0.0;
   out_7182100953115386674[275] = 0.0;
   out_7182100953115386674[276] = 0.0;
   out_7182100953115386674[277] = 0.0;
   out_7182100953115386674[278] = 0.0;
   out_7182100953115386674[279] = 0.0;
   out_7182100953115386674[280] = 0.0;
   out_7182100953115386674[281] = 0.0;
   out_7182100953115386674[282] = 0.0;
   out_7182100953115386674[283] = 0.0;
   out_7182100953115386674[284] = 0.0;
   out_7182100953115386674[285] = 1.0;
   out_7182100953115386674[286] = 0.0;
   out_7182100953115386674[287] = 0.0;
   out_7182100953115386674[288] = 0.0;
   out_7182100953115386674[289] = 0.0;
   out_7182100953115386674[290] = 0.0;
   out_7182100953115386674[291] = 0.0;
   out_7182100953115386674[292] = 0.0;
   out_7182100953115386674[293] = 0.0;
   out_7182100953115386674[294] = 0.0;
   out_7182100953115386674[295] = 0.0;
   out_7182100953115386674[296] = 0.0;
   out_7182100953115386674[297] = 0.0;
   out_7182100953115386674[298] = 0.0;
   out_7182100953115386674[299] = 0.0;
   out_7182100953115386674[300] = 0.0;
   out_7182100953115386674[301] = 0.0;
   out_7182100953115386674[302] = 0.0;
   out_7182100953115386674[303] = 0.0;
   out_7182100953115386674[304] = 1.0;
   out_7182100953115386674[305] = 0.0;
   out_7182100953115386674[306] = 0.0;
   out_7182100953115386674[307] = 0.0;
   out_7182100953115386674[308] = 0.0;
   out_7182100953115386674[309] = 0.0;
   out_7182100953115386674[310] = 0.0;
   out_7182100953115386674[311] = 0.0;
   out_7182100953115386674[312] = 0.0;
   out_7182100953115386674[313] = 0.0;
   out_7182100953115386674[314] = 0.0;
   out_7182100953115386674[315] = 0.0;
   out_7182100953115386674[316] = 0.0;
   out_7182100953115386674[317] = 0.0;
   out_7182100953115386674[318] = 0.0;
   out_7182100953115386674[319] = 0.0;
   out_7182100953115386674[320] = 0.0;
   out_7182100953115386674[321] = 0.0;
   out_7182100953115386674[322] = 0.0;
   out_7182100953115386674[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_6957551748977013851) {
   out_6957551748977013851[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_6957551748977013851[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_6957551748977013851[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_6957551748977013851[3] = dt*state[12] + state[3];
   out_6957551748977013851[4] = dt*state[13] + state[4];
   out_6957551748977013851[5] = dt*state[14] + state[5];
   out_6957551748977013851[6] = state[6];
   out_6957551748977013851[7] = state[7];
   out_6957551748977013851[8] = state[8];
   out_6957551748977013851[9] = state[9];
   out_6957551748977013851[10] = state[10];
   out_6957551748977013851[11] = state[11];
   out_6957551748977013851[12] = state[12];
   out_6957551748977013851[13] = state[13];
   out_6957551748977013851[14] = state[14];
   out_6957551748977013851[15] = state[15];
   out_6957551748977013851[16] = state[16];
   out_6957551748977013851[17] = state[17];
}
void F_fun(double *state, double dt, double *out_5301176885049343435) {
   out_5301176885049343435[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5301176885049343435[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5301176885049343435[2] = 0;
   out_5301176885049343435[3] = 0;
   out_5301176885049343435[4] = 0;
   out_5301176885049343435[5] = 0;
   out_5301176885049343435[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5301176885049343435[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5301176885049343435[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5301176885049343435[9] = 0;
   out_5301176885049343435[10] = 0;
   out_5301176885049343435[11] = 0;
   out_5301176885049343435[12] = 0;
   out_5301176885049343435[13] = 0;
   out_5301176885049343435[14] = 0;
   out_5301176885049343435[15] = 0;
   out_5301176885049343435[16] = 0;
   out_5301176885049343435[17] = 0;
   out_5301176885049343435[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5301176885049343435[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5301176885049343435[20] = 0;
   out_5301176885049343435[21] = 0;
   out_5301176885049343435[22] = 0;
   out_5301176885049343435[23] = 0;
   out_5301176885049343435[24] = 0;
   out_5301176885049343435[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5301176885049343435[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5301176885049343435[27] = 0;
   out_5301176885049343435[28] = 0;
   out_5301176885049343435[29] = 0;
   out_5301176885049343435[30] = 0;
   out_5301176885049343435[31] = 0;
   out_5301176885049343435[32] = 0;
   out_5301176885049343435[33] = 0;
   out_5301176885049343435[34] = 0;
   out_5301176885049343435[35] = 0;
   out_5301176885049343435[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5301176885049343435[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5301176885049343435[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5301176885049343435[39] = 0;
   out_5301176885049343435[40] = 0;
   out_5301176885049343435[41] = 0;
   out_5301176885049343435[42] = 0;
   out_5301176885049343435[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5301176885049343435[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5301176885049343435[45] = 0;
   out_5301176885049343435[46] = 0;
   out_5301176885049343435[47] = 0;
   out_5301176885049343435[48] = 0;
   out_5301176885049343435[49] = 0;
   out_5301176885049343435[50] = 0;
   out_5301176885049343435[51] = 0;
   out_5301176885049343435[52] = 0;
   out_5301176885049343435[53] = 0;
   out_5301176885049343435[54] = 0;
   out_5301176885049343435[55] = 0;
   out_5301176885049343435[56] = 0;
   out_5301176885049343435[57] = 1;
   out_5301176885049343435[58] = 0;
   out_5301176885049343435[59] = 0;
   out_5301176885049343435[60] = 0;
   out_5301176885049343435[61] = 0;
   out_5301176885049343435[62] = 0;
   out_5301176885049343435[63] = 0;
   out_5301176885049343435[64] = 0;
   out_5301176885049343435[65] = 0;
   out_5301176885049343435[66] = dt;
   out_5301176885049343435[67] = 0;
   out_5301176885049343435[68] = 0;
   out_5301176885049343435[69] = 0;
   out_5301176885049343435[70] = 0;
   out_5301176885049343435[71] = 0;
   out_5301176885049343435[72] = 0;
   out_5301176885049343435[73] = 0;
   out_5301176885049343435[74] = 0;
   out_5301176885049343435[75] = 0;
   out_5301176885049343435[76] = 1;
   out_5301176885049343435[77] = 0;
   out_5301176885049343435[78] = 0;
   out_5301176885049343435[79] = 0;
   out_5301176885049343435[80] = 0;
   out_5301176885049343435[81] = 0;
   out_5301176885049343435[82] = 0;
   out_5301176885049343435[83] = 0;
   out_5301176885049343435[84] = 0;
   out_5301176885049343435[85] = dt;
   out_5301176885049343435[86] = 0;
   out_5301176885049343435[87] = 0;
   out_5301176885049343435[88] = 0;
   out_5301176885049343435[89] = 0;
   out_5301176885049343435[90] = 0;
   out_5301176885049343435[91] = 0;
   out_5301176885049343435[92] = 0;
   out_5301176885049343435[93] = 0;
   out_5301176885049343435[94] = 0;
   out_5301176885049343435[95] = 1;
   out_5301176885049343435[96] = 0;
   out_5301176885049343435[97] = 0;
   out_5301176885049343435[98] = 0;
   out_5301176885049343435[99] = 0;
   out_5301176885049343435[100] = 0;
   out_5301176885049343435[101] = 0;
   out_5301176885049343435[102] = 0;
   out_5301176885049343435[103] = 0;
   out_5301176885049343435[104] = dt;
   out_5301176885049343435[105] = 0;
   out_5301176885049343435[106] = 0;
   out_5301176885049343435[107] = 0;
   out_5301176885049343435[108] = 0;
   out_5301176885049343435[109] = 0;
   out_5301176885049343435[110] = 0;
   out_5301176885049343435[111] = 0;
   out_5301176885049343435[112] = 0;
   out_5301176885049343435[113] = 0;
   out_5301176885049343435[114] = 1;
   out_5301176885049343435[115] = 0;
   out_5301176885049343435[116] = 0;
   out_5301176885049343435[117] = 0;
   out_5301176885049343435[118] = 0;
   out_5301176885049343435[119] = 0;
   out_5301176885049343435[120] = 0;
   out_5301176885049343435[121] = 0;
   out_5301176885049343435[122] = 0;
   out_5301176885049343435[123] = 0;
   out_5301176885049343435[124] = 0;
   out_5301176885049343435[125] = 0;
   out_5301176885049343435[126] = 0;
   out_5301176885049343435[127] = 0;
   out_5301176885049343435[128] = 0;
   out_5301176885049343435[129] = 0;
   out_5301176885049343435[130] = 0;
   out_5301176885049343435[131] = 0;
   out_5301176885049343435[132] = 0;
   out_5301176885049343435[133] = 1;
   out_5301176885049343435[134] = 0;
   out_5301176885049343435[135] = 0;
   out_5301176885049343435[136] = 0;
   out_5301176885049343435[137] = 0;
   out_5301176885049343435[138] = 0;
   out_5301176885049343435[139] = 0;
   out_5301176885049343435[140] = 0;
   out_5301176885049343435[141] = 0;
   out_5301176885049343435[142] = 0;
   out_5301176885049343435[143] = 0;
   out_5301176885049343435[144] = 0;
   out_5301176885049343435[145] = 0;
   out_5301176885049343435[146] = 0;
   out_5301176885049343435[147] = 0;
   out_5301176885049343435[148] = 0;
   out_5301176885049343435[149] = 0;
   out_5301176885049343435[150] = 0;
   out_5301176885049343435[151] = 0;
   out_5301176885049343435[152] = 1;
   out_5301176885049343435[153] = 0;
   out_5301176885049343435[154] = 0;
   out_5301176885049343435[155] = 0;
   out_5301176885049343435[156] = 0;
   out_5301176885049343435[157] = 0;
   out_5301176885049343435[158] = 0;
   out_5301176885049343435[159] = 0;
   out_5301176885049343435[160] = 0;
   out_5301176885049343435[161] = 0;
   out_5301176885049343435[162] = 0;
   out_5301176885049343435[163] = 0;
   out_5301176885049343435[164] = 0;
   out_5301176885049343435[165] = 0;
   out_5301176885049343435[166] = 0;
   out_5301176885049343435[167] = 0;
   out_5301176885049343435[168] = 0;
   out_5301176885049343435[169] = 0;
   out_5301176885049343435[170] = 0;
   out_5301176885049343435[171] = 1;
   out_5301176885049343435[172] = 0;
   out_5301176885049343435[173] = 0;
   out_5301176885049343435[174] = 0;
   out_5301176885049343435[175] = 0;
   out_5301176885049343435[176] = 0;
   out_5301176885049343435[177] = 0;
   out_5301176885049343435[178] = 0;
   out_5301176885049343435[179] = 0;
   out_5301176885049343435[180] = 0;
   out_5301176885049343435[181] = 0;
   out_5301176885049343435[182] = 0;
   out_5301176885049343435[183] = 0;
   out_5301176885049343435[184] = 0;
   out_5301176885049343435[185] = 0;
   out_5301176885049343435[186] = 0;
   out_5301176885049343435[187] = 0;
   out_5301176885049343435[188] = 0;
   out_5301176885049343435[189] = 0;
   out_5301176885049343435[190] = 1;
   out_5301176885049343435[191] = 0;
   out_5301176885049343435[192] = 0;
   out_5301176885049343435[193] = 0;
   out_5301176885049343435[194] = 0;
   out_5301176885049343435[195] = 0;
   out_5301176885049343435[196] = 0;
   out_5301176885049343435[197] = 0;
   out_5301176885049343435[198] = 0;
   out_5301176885049343435[199] = 0;
   out_5301176885049343435[200] = 0;
   out_5301176885049343435[201] = 0;
   out_5301176885049343435[202] = 0;
   out_5301176885049343435[203] = 0;
   out_5301176885049343435[204] = 0;
   out_5301176885049343435[205] = 0;
   out_5301176885049343435[206] = 0;
   out_5301176885049343435[207] = 0;
   out_5301176885049343435[208] = 0;
   out_5301176885049343435[209] = 1;
   out_5301176885049343435[210] = 0;
   out_5301176885049343435[211] = 0;
   out_5301176885049343435[212] = 0;
   out_5301176885049343435[213] = 0;
   out_5301176885049343435[214] = 0;
   out_5301176885049343435[215] = 0;
   out_5301176885049343435[216] = 0;
   out_5301176885049343435[217] = 0;
   out_5301176885049343435[218] = 0;
   out_5301176885049343435[219] = 0;
   out_5301176885049343435[220] = 0;
   out_5301176885049343435[221] = 0;
   out_5301176885049343435[222] = 0;
   out_5301176885049343435[223] = 0;
   out_5301176885049343435[224] = 0;
   out_5301176885049343435[225] = 0;
   out_5301176885049343435[226] = 0;
   out_5301176885049343435[227] = 0;
   out_5301176885049343435[228] = 1;
   out_5301176885049343435[229] = 0;
   out_5301176885049343435[230] = 0;
   out_5301176885049343435[231] = 0;
   out_5301176885049343435[232] = 0;
   out_5301176885049343435[233] = 0;
   out_5301176885049343435[234] = 0;
   out_5301176885049343435[235] = 0;
   out_5301176885049343435[236] = 0;
   out_5301176885049343435[237] = 0;
   out_5301176885049343435[238] = 0;
   out_5301176885049343435[239] = 0;
   out_5301176885049343435[240] = 0;
   out_5301176885049343435[241] = 0;
   out_5301176885049343435[242] = 0;
   out_5301176885049343435[243] = 0;
   out_5301176885049343435[244] = 0;
   out_5301176885049343435[245] = 0;
   out_5301176885049343435[246] = 0;
   out_5301176885049343435[247] = 1;
   out_5301176885049343435[248] = 0;
   out_5301176885049343435[249] = 0;
   out_5301176885049343435[250] = 0;
   out_5301176885049343435[251] = 0;
   out_5301176885049343435[252] = 0;
   out_5301176885049343435[253] = 0;
   out_5301176885049343435[254] = 0;
   out_5301176885049343435[255] = 0;
   out_5301176885049343435[256] = 0;
   out_5301176885049343435[257] = 0;
   out_5301176885049343435[258] = 0;
   out_5301176885049343435[259] = 0;
   out_5301176885049343435[260] = 0;
   out_5301176885049343435[261] = 0;
   out_5301176885049343435[262] = 0;
   out_5301176885049343435[263] = 0;
   out_5301176885049343435[264] = 0;
   out_5301176885049343435[265] = 0;
   out_5301176885049343435[266] = 1;
   out_5301176885049343435[267] = 0;
   out_5301176885049343435[268] = 0;
   out_5301176885049343435[269] = 0;
   out_5301176885049343435[270] = 0;
   out_5301176885049343435[271] = 0;
   out_5301176885049343435[272] = 0;
   out_5301176885049343435[273] = 0;
   out_5301176885049343435[274] = 0;
   out_5301176885049343435[275] = 0;
   out_5301176885049343435[276] = 0;
   out_5301176885049343435[277] = 0;
   out_5301176885049343435[278] = 0;
   out_5301176885049343435[279] = 0;
   out_5301176885049343435[280] = 0;
   out_5301176885049343435[281] = 0;
   out_5301176885049343435[282] = 0;
   out_5301176885049343435[283] = 0;
   out_5301176885049343435[284] = 0;
   out_5301176885049343435[285] = 1;
   out_5301176885049343435[286] = 0;
   out_5301176885049343435[287] = 0;
   out_5301176885049343435[288] = 0;
   out_5301176885049343435[289] = 0;
   out_5301176885049343435[290] = 0;
   out_5301176885049343435[291] = 0;
   out_5301176885049343435[292] = 0;
   out_5301176885049343435[293] = 0;
   out_5301176885049343435[294] = 0;
   out_5301176885049343435[295] = 0;
   out_5301176885049343435[296] = 0;
   out_5301176885049343435[297] = 0;
   out_5301176885049343435[298] = 0;
   out_5301176885049343435[299] = 0;
   out_5301176885049343435[300] = 0;
   out_5301176885049343435[301] = 0;
   out_5301176885049343435[302] = 0;
   out_5301176885049343435[303] = 0;
   out_5301176885049343435[304] = 1;
   out_5301176885049343435[305] = 0;
   out_5301176885049343435[306] = 0;
   out_5301176885049343435[307] = 0;
   out_5301176885049343435[308] = 0;
   out_5301176885049343435[309] = 0;
   out_5301176885049343435[310] = 0;
   out_5301176885049343435[311] = 0;
   out_5301176885049343435[312] = 0;
   out_5301176885049343435[313] = 0;
   out_5301176885049343435[314] = 0;
   out_5301176885049343435[315] = 0;
   out_5301176885049343435[316] = 0;
   out_5301176885049343435[317] = 0;
   out_5301176885049343435[318] = 0;
   out_5301176885049343435[319] = 0;
   out_5301176885049343435[320] = 0;
   out_5301176885049343435[321] = 0;
   out_5301176885049343435[322] = 0;
   out_5301176885049343435[323] = 1;
}
void h_4(double *state, double *unused, double *out_3098701076704019746) {
   out_3098701076704019746[0] = state[6] + state[9];
   out_3098701076704019746[1] = state[7] + state[10];
   out_3098701076704019746[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_368172970598732889) {
   out_368172970598732889[0] = 0;
   out_368172970598732889[1] = 0;
   out_368172970598732889[2] = 0;
   out_368172970598732889[3] = 0;
   out_368172970598732889[4] = 0;
   out_368172970598732889[5] = 0;
   out_368172970598732889[6] = 1;
   out_368172970598732889[7] = 0;
   out_368172970598732889[8] = 0;
   out_368172970598732889[9] = 1;
   out_368172970598732889[10] = 0;
   out_368172970598732889[11] = 0;
   out_368172970598732889[12] = 0;
   out_368172970598732889[13] = 0;
   out_368172970598732889[14] = 0;
   out_368172970598732889[15] = 0;
   out_368172970598732889[16] = 0;
   out_368172970598732889[17] = 0;
   out_368172970598732889[18] = 0;
   out_368172970598732889[19] = 0;
   out_368172970598732889[20] = 0;
   out_368172970598732889[21] = 0;
   out_368172970598732889[22] = 0;
   out_368172970598732889[23] = 0;
   out_368172970598732889[24] = 0;
   out_368172970598732889[25] = 1;
   out_368172970598732889[26] = 0;
   out_368172970598732889[27] = 0;
   out_368172970598732889[28] = 1;
   out_368172970598732889[29] = 0;
   out_368172970598732889[30] = 0;
   out_368172970598732889[31] = 0;
   out_368172970598732889[32] = 0;
   out_368172970598732889[33] = 0;
   out_368172970598732889[34] = 0;
   out_368172970598732889[35] = 0;
   out_368172970598732889[36] = 0;
   out_368172970598732889[37] = 0;
   out_368172970598732889[38] = 0;
   out_368172970598732889[39] = 0;
   out_368172970598732889[40] = 0;
   out_368172970598732889[41] = 0;
   out_368172970598732889[42] = 0;
   out_368172970598732889[43] = 0;
   out_368172970598732889[44] = 1;
   out_368172970598732889[45] = 0;
   out_368172970598732889[46] = 0;
   out_368172970598732889[47] = 1;
   out_368172970598732889[48] = 0;
   out_368172970598732889[49] = 0;
   out_368172970598732889[50] = 0;
   out_368172970598732889[51] = 0;
   out_368172970598732889[52] = 0;
   out_368172970598732889[53] = 0;
}
void h_10(double *state, double *unused, double *out_5402423064051119791) {
   out_5402423064051119791[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_5402423064051119791[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_5402423064051119791[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_3989863782830359753) {
   out_3989863782830359753[0] = 0;
   out_3989863782830359753[1] = 9.8100000000000005*cos(state[1]);
   out_3989863782830359753[2] = 0;
   out_3989863782830359753[3] = 0;
   out_3989863782830359753[4] = -state[8];
   out_3989863782830359753[5] = state[7];
   out_3989863782830359753[6] = 0;
   out_3989863782830359753[7] = state[5];
   out_3989863782830359753[8] = -state[4];
   out_3989863782830359753[9] = 0;
   out_3989863782830359753[10] = 0;
   out_3989863782830359753[11] = 0;
   out_3989863782830359753[12] = 1;
   out_3989863782830359753[13] = 0;
   out_3989863782830359753[14] = 0;
   out_3989863782830359753[15] = 1;
   out_3989863782830359753[16] = 0;
   out_3989863782830359753[17] = 0;
   out_3989863782830359753[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_3989863782830359753[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_3989863782830359753[20] = 0;
   out_3989863782830359753[21] = state[8];
   out_3989863782830359753[22] = 0;
   out_3989863782830359753[23] = -state[6];
   out_3989863782830359753[24] = -state[5];
   out_3989863782830359753[25] = 0;
   out_3989863782830359753[26] = state[3];
   out_3989863782830359753[27] = 0;
   out_3989863782830359753[28] = 0;
   out_3989863782830359753[29] = 0;
   out_3989863782830359753[30] = 0;
   out_3989863782830359753[31] = 1;
   out_3989863782830359753[32] = 0;
   out_3989863782830359753[33] = 0;
   out_3989863782830359753[34] = 1;
   out_3989863782830359753[35] = 0;
   out_3989863782830359753[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_3989863782830359753[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_3989863782830359753[38] = 0;
   out_3989863782830359753[39] = -state[7];
   out_3989863782830359753[40] = state[6];
   out_3989863782830359753[41] = 0;
   out_3989863782830359753[42] = state[4];
   out_3989863782830359753[43] = -state[3];
   out_3989863782830359753[44] = 0;
   out_3989863782830359753[45] = 0;
   out_3989863782830359753[46] = 0;
   out_3989863782830359753[47] = 0;
   out_3989863782830359753[48] = 0;
   out_3989863782830359753[49] = 0;
   out_3989863782830359753[50] = 1;
   out_3989863782830359753[51] = 0;
   out_3989863782830359753[52] = 0;
   out_3989863782830359753[53] = 1;
}
void h_13(double *state, double *unused, double *out_8642008707511601712) {
   out_8642008707511601712[0] = state[3];
   out_8642008707511601712[1] = state[4];
   out_8642008707511601712[2] = state[5];
}
void H_13(double *state, double *unused, double *out_7242458237717968040) {
   out_7242458237717968040[0] = 0;
   out_7242458237717968040[1] = 0;
   out_7242458237717968040[2] = 0;
   out_7242458237717968040[3] = 1;
   out_7242458237717968040[4] = 0;
   out_7242458237717968040[5] = 0;
   out_7242458237717968040[6] = 0;
   out_7242458237717968040[7] = 0;
   out_7242458237717968040[8] = 0;
   out_7242458237717968040[9] = 0;
   out_7242458237717968040[10] = 0;
   out_7242458237717968040[11] = 0;
   out_7242458237717968040[12] = 0;
   out_7242458237717968040[13] = 0;
   out_7242458237717968040[14] = 0;
   out_7242458237717968040[15] = 0;
   out_7242458237717968040[16] = 0;
   out_7242458237717968040[17] = 0;
   out_7242458237717968040[18] = 0;
   out_7242458237717968040[19] = 0;
   out_7242458237717968040[20] = 0;
   out_7242458237717968040[21] = 0;
   out_7242458237717968040[22] = 1;
   out_7242458237717968040[23] = 0;
   out_7242458237717968040[24] = 0;
   out_7242458237717968040[25] = 0;
   out_7242458237717968040[26] = 0;
   out_7242458237717968040[27] = 0;
   out_7242458237717968040[28] = 0;
   out_7242458237717968040[29] = 0;
   out_7242458237717968040[30] = 0;
   out_7242458237717968040[31] = 0;
   out_7242458237717968040[32] = 0;
   out_7242458237717968040[33] = 0;
   out_7242458237717968040[34] = 0;
   out_7242458237717968040[35] = 0;
   out_7242458237717968040[36] = 0;
   out_7242458237717968040[37] = 0;
   out_7242458237717968040[38] = 0;
   out_7242458237717968040[39] = 0;
   out_7242458237717968040[40] = 0;
   out_7242458237717968040[41] = 1;
   out_7242458237717968040[42] = 0;
   out_7242458237717968040[43] = 0;
   out_7242458237717968040[44] = 0;
   out_7242458237717968040[45] = 0;
   out_7242458237717968040[46] = 0;
   out_7242458237717968040[47] = 0;
   out_7242458237717968040[48] = 0;
   out_7242458237717968040[49] = 0;
   out_7242458237717968040[50] = 0;
   out_7242458237717968040[51] = 0;
   out_7242458237717968040[52] = 0;
   out_7242458237717968040[53] = 0;
}
void h_14(double *state, double *unused, double *out_1963635100147538950) {
   out_1963635100147538950[0] = state[6];
   out_1963635100147538950[1] = state[7];
   out_1963635100147538950[2] = state[8];
}
void H_14(double *state, double *unused, double *out_3450961402894105185) {
   out_3450961402894105185[0] = 0;
   out_3450961402894105185[1] = 0;
   out_3450961402894105185[2] = 0;
   out_3450961402894105185[3] = 0;
   out_3450961402894105185[4] = 0;
   out_3450961402894105185[5] = 0;
   out_3450961402894105185[6] = 1;
   out_3450961402894105185[7] = 0;
   out_3450961402894105185[8] = 0;
   out_3450961402894105185[9] = 0;
   out_3450961402894105185[10] = 0;
   out_3450961402894105185[11] = 0;
   out_3450961402894105185[12] = 0;
   out_3450961402894105185[13] = 0;
   out_3450961402894105185[14] = 0;
   out_3450961402894105185[15] = 0;
   out_3450961402894105185[16] = 0;
   out_3450961402894105185[17] = 0;
   out_3450961402894105185[18] = 0;
   out_3450961402894105185[19] = 0;
   out_3450961402894105185[20] = 0;
   out_3450961402894105185[21] = 0;
   out_3450961402894105185[22] = 0;
   out_3450961402894105185[23] = 0;
   out_3450961402894105185[24] = 0;
   out_3450961402894105185[25] = 1;
   out_3450961402894105185[26] = 0;
   out_3450961402894105185[27] = 0;
   out_3450961402894105185[28] = 0;
   out_3450961402894105185[29] = 0;
   out_3450961402894105185[30] = 0;
   out_3450961402894105185[31] = 0;
   out_3450961402894105185[32] = 0;
   out_3450961402894105185[33] = 0;
   out_3450961402894105185[34] = 0;
   out_3450961402894105185[35] = 0;
   out_3450961402894105185[36] = 0;
   out_3450961402894105185[37] = 0;
   out_3450961402894105185[38] = 0;
   out_3450961402894105185[39] = 0;
   out_3450961402894105185[40] = 0;
   out_3450961402894105185[41] = 0;
   out_3450961402894105185[42] = 0;
   out_3450961402894105185[43] = 0;
   out_3450961402894105185[44] = 1;
   out_3450961402894105185[45] = 0;
   out_3450961402894105185[46] = 0;
   out_3450961402894105185[47] = 0;
   out_3450961402894105185[48] = 0;
   out_3450961402894105185[49] = 0;
   out_3450961402894105185[50] = 0;
   out_3450961402894105185[51] = 0;
   out_3450961402894105185[52] = 0;
   out_3450961402894105185[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_4541492771646069759) {
  err_fun(nom_x, delta_x, out_4541492771646069759);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_3364276346708699962) {
  inv_err_fun(nom_x, true_x, out_3364276346708699962);
}
void pose_H_mod_fun(double *state, double *out_7182100953115386674) {
  H_mod_fun(state, out_7182100953115386674);
}
void pose_f_fun(double *state, double dt, double *out_6957551748977013851) {
  f_fun(state,  dt, out_6957551748977013851);
}
void pose_F_fun(double *state, double dt, double *out_5301176885049343435) {
  F_fun(state,  dt, out_5301176885049343435);
}
void pose_h_4(double *state, double *unused, double *out_3098701076704019746) {
  h_4(state, unused, out_3098701076704019746);
}
void pose_H_4(double *state, double *unused, double *out_368172970598732889) {
  H_4(state, unused, out_368172970598732889);
}
void pose_h_10(double *state, double *unused, double *out_5402423064051119791) {
  h_10(state, unused, out_5402423064051119791);
}
void pose_H_10(double *state, double *unused, double *out_3989863782830359753) {
  H_10(state, unused, out_3989863782830359753);
}
void pose_h_13(double *state, double *unused, double *out_8642008707511601712) {
  h_13(state, unused, out_8642008707511601712);
}
void pose_H_13(double *state, double *unused, double *out_7242458237717968040) {
  H_13(state, unused, out_7242458237717968040);
}
void pose_h_14(double *state, double *unused, double *out_1963635100147538950) {
  h_14(state, unused, out_1963635100147538950);
}
void pose_H_14(double *state, double *unused, double *out_3450961402894105185) {
  H_14(state, unused, out_3450961402894105185);
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
