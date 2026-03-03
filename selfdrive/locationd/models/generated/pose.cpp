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
void err_fun(double *nom_x, double *delta_x, double *out_4430854607241578209) {
   out_4430854607241578209[0] = delta_x[0] + nom_x[0];
   out_4430854607241578209[1] = delta_x[1] + nom_x[1];
   out_4430854607241578209[2] = delta_x[2] + nom_x[2];
   out_4430854607241578209[3] = delta_x[3] + nom_x[3];
   out_4430854607241578209[4] = delta_x[4] + nom_x[4];
   out_4430854607241578209[5] = delta_x[5] + nom_x[5];
   out_4430854607241578209[6] = delta_x[6] + nom_x[6];
   out_4430854607241578209[7] = delta_x[7] + nom_x[7];
   out_4430854607241578209[8] = delta_x[8] + nom_x[8];
   out_4430854607241578209[9] = delta_x[9] + nom_x[9];
   out_4430854607241578209[10] = delta_x[10] + nom_x[10];
   out_4430854607241578209[11] = delta_x[11] + nom_x[11];
   out_4430854607241578209[12] = delta_x[12] + nom_x[12];
   out_4430854607241578209[13] = delta_x[13] + nom_x[13];
   out_4430854607241578209[14] = delta_x[14] + nom_x[14];
   out_4430854607241578209[15] = delta_x[15] + nom_x[15];
   out_4430854607241578209[16] = delta_x[16] + nom_x[16];
   out_4430854607241578209[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_8029849703839127827) {
   out_8029849703839127827[0] = -nom_x[0] + true_x[0];
   out_8029849703839127827[1] = -nom_x[1] + true_x[1];
   out_8029849703839127827[2] = -nom_x[2] + true_x[2];
   out_8029849703839127827[3] = -nom_x[3] + true_x[3];
   out_8029849703839127827[4] = -nom_x[4] + true_x[4];
   out_8029849703839127827[5] = -nom_x[5] + true_x[5];
   out_8029849703839127827[6] = -nom_x[6] + true_x[6];
   out_8029849703839127827[7] = -nom_x[7] + true_x[7];
   out_8029849703839127827[8] = -nom_x[8] + true_x[8];
   out_8029849703839127827[9] = -nom_x[9] + true_x[9];
   out_8029849703839127827[10] = -nom_x[10] + true_x[10];
   out_8029849703839127827[11] = -nom_x[11] + true_x[11];
   out_8029849703839127827[12] = -nom_x[12] + true_x[12];
   out_8029849703839127827[13] = -nom_x[13] + true_x[13];
   out_8029849703839127827[14] = -nom_x[14] + true_x[14];
   out_8029849703839127827[15] = -nom_x[15] + true_x[15];
   out_8029849703839127827[16] = -nom_x[16] + true_x[16];
   out_8029849703839127827[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_4301683494632340000) {
   out_4301683494632340000[0] = 1.0;
   out_4301683494632340000[1] = 0.0;
   out_4301683494632340000[2] = 0.0;
   out_4301683494632340000[3] = 0.0;
   out_4301683494632340000[4] = 0.0;
   out_4301683494632340000[5] = 0.0;
   out_4301683494632340000[6] = 0.0;
   out_4301683494632340000[7] = 0.0;
   out_4301683494632340000[8] = 0.0;
   out_4301683494632340000[9] = 0.0;
   out_4301683494632340000[10] = 0.0;
   out_4301683494632340000[11] = 0.0;
   out_4301683494632340000[12] = 0.0;
   out_4301683494632340000[13] = 0.0;
   out_4301683494632340000[14] = 0.0;
   out_4301683494632340000[15] = 0.0;
   out_4301683494632340000[16] = 0.0;
   out_4301683494632340000[17] = 0.0;
   out_4301683494632340000[18] = 0.0;
   out_4301683494632340000[19] = 1.0;
   out_4301683494632340000[20] = 0.0;
   out_4301683494632340000[21] = 0.0;
   out_4301683494632340000[22] = 0.0;
   out_4301683494632340000[23] = 0.0;
   out_4301683494632340000[24] = 0.0;
   out_4301683494632340000[25] = 0.0;
   out_4301683494632340000[26] = 0.0;
   out_4301683494632340000[27] = 0.0;
   out_4301683494632340000[28] = 0.0;
   out_4301683494632340000[29] = 0.0;
   out_4301683494632340000[30] = 0.0;
   out_4301683494632340000[31] = 0.0;
   out_4301683494632340000[32] = 0.0;
   out_4301683494632340000[33] = 0.0;
   out_4301683494632340000[34] = 0.0;
   out_4301683494632340000[35] = 0.0;
   out_4301683494632340000[36] = 0.0;
   out_4301683494632340000[37] = 0.0;
   out_4301683494632340000[38] = 1.0;
   out_4301683494632340000[39] = 0.0;
   out_4301683494632340000[40] = 0.0;
   out_4301683494632340000[41] = 0.0;
   out_4301683494632340000[42] = 0.0;
   out_4301683494632340000[43] = 0.0;
   out_4301683494632340000[44] = 0.0;
   out_4301683494632340000[45] = 0.0;
   out_4301683494632340000[46] = 0.0;
   out_4301683494632340000[47] = 0.0;
   out_4301683494632340000[48] = 0.0;
   out_4301683494632340000[49] = 0.0;
   out_4301683494632340000[50] = 0.0;
   out_4301683494632340000[51] = 0.0;
   out_4301683494632340000[52] = 0.0;
   out_4301683494632340000[53] = 0.0;
   out_4301683494632340000[54] = 0.0;
   out_4301683494632340000[55] = 0.0;
   out_4301683494632340000[56] = 0.0;
   out_4301683494632340000[57] = 1.0;
   out_4301683494632340000[58] = 0.0;
   out_4301683494632340000[59] = 0.0;
   out_4301683494632340000[60] = 0.0;
   out_4301683494632340000[61] = 0.0;
   out_4301683494632340000[62] = 0.0;
   out_4301683494632340000[63] = 0.0;
   out_4301683494632340000[64] = 0.0;
   out_4301683494632340000[65] = 0.0;
   out_4301683494632340000[66] = 0.0;
   out_4301683494632340000[67] = 0.0;
   out_4301683494632340000[68] = 0.0;
   out_4301683494632340000[69] = 0.0;
   out_4301683494632340000[70] = 0.0;
   out_4301683494632340000[71] = 0.0;
   out_4301683494632340000[72] = 0.0;
   out_4301683494632340000[73] = 0.0;
   out_4301683494632340000[74] = 0.0;
   out_4301683494632340000[75] = 0.0;
   out_4301683494632340000[76] = 1.0;
   out_4301683494632340000[77] = 0.0;
   out_4301683494632340000[78] = 0.0;
   out_4301683494632340000[79] = 0.0;
   out_4301683494632340000[80] = 0.0;
   out_4301683494632340000[81] = 0.0;
   out_4301683494632340000[82] = 0.0;
   out_4301683494632340000[83] = 0.0;
   out_4301683494632340000[84] = 0.0;
   out_4301683494632340000[85] = 0.0;
   out_4301683494632340000[86] = 0.0;
   out_4301683494632340000[87] = 0.0;
   out_4301683494632340000[88] = 0.0;
   out_4301683494632340000[89] = 0.0;
   out_4301683494632340000[90] = 0.0;
   out_4301683494632340000[91] = 0.0;
   out_4301683494632340000[92] = 0.0;
   out_4301683494632340000[93] = 0.0;
   out_4301683494632340000[94] = 0.0;
   out_4301683494632340000[95] = 1.0;
   out_4301683494632340000[96] = 0.0;
   out_4301683494632340000[97] = 0.0;
   out_4301683494632340000[98] = 0.0;
   out_4301683494632340000[99] = 0.0;
   out_4301683494632340000[100] = 0.0;
   out_4301683494632340000[101] = 0.0;
   out_4301683494632340000[102] = 0.0;
   out_4301683494632340000[103] = 0.0;
   out_4301683494632340000[104] = 0.0;
   out_4301683494632340000[105] = 0.0;
   out_4301683494632340000[106] = 0.0;
   out_4301683494632340000[107] = 0.0;
   out_4301683494632340000[108] = 0.0;
   out_4301683494632340000[109] = 0.0;
   out_4301683494632340000[110] = 0.0;
   out_4301683494632340000[111] = 0.0;
   out_4301683494632340000[112] = 0.0;
   out_4301683494632340000[113] = 0.0;
   out_4301683494632340000[114] = 1.0;
   out_4301683494632340000[115] = 0.0;
   out_4301683494632340000[116] = 0.0;
   out_4301683494632340000[117] = 0.0;
   out_4301683494632340000[118] = 0.0;
   out_4301683494632340000[119] = 0.0;
   out_4301683494632340000[120] = 0.0;
   out_4301683494632340000[121] = 0.0;
   out_4301683494632340000[122] = 0.0;
   out_4301683494632340000[123] = 0.0;
   out_4301683494632340000[124] = 0.0;
   out_4301683494632340000[125] = 0.0;
   out_4301683494632340000[126] = 0.0;
   out_4301683494632340000[127] = 0.0;
   out_4301683494632340000[128] = 0.0;
   out_4301683494632340000[129] = 0.0;
   out_4301683494632340000[130] = 0.0;
   out_4301683494632340000[131] = 0.0;
   out_4301683494632340000[132] = 0.0;
   out_4301683494632340000[133] = 1.0;
   out_4301683494632340000[134] = 0.0;
   out_4301683494632340000[135] = 0.0;
   out_4301683494632340000[136] = 0.0;
   out_4301683494632340000[137] = 0.0;
   out_4301683494632340000[138] = 0.0;
   out_4301683494632340000[139] = 0.0;
   out_4301683494632340000[140] = 0.0;
   out_4301683494632340000[141] = 0.0;
   out_4301683494632340000[142] = 0.0;
   out_4301683494632340000[143] = 0.0;
   out_4301683494632340000[144] = 0.0;
   out_4301683494632340000[145] = 0.0;
   out_4301683494632340000[146] = 0.0;
   out_4301683494632340000[147] = 0.0;
   out_4301683494632340000[148] = 0.0;
   out_4301683494632340000[149] = 0.0;
   out_4301683494632340000[150] = 0.0;
   out_4301683494632340000[151] = 0.0;
   out_4301683494632340000[152] = 1.0;
   out_4301683494632340000[153] = 0.0;
   out_4301683494632340000[154] = 0.0;
   out_4301683494632340000[155] = 0.0;
   out_4301683494632340000[156] = 0.0;
   out_4301683494632340000[157] = 0.0;
   out_4301683494632340000[158] = 0.0;
   out_4301683494632340000[159] = 0.0;
   out_4301683494632340000[160] = 0.0;
   out_4301683494632340000[161] = 0.0;
   out_4301683494632340000[162] = 0.0;
   out_4301683494632340000[163] = 0.0;
   out_4301683494632340000[164] = 0.0;
   out_4301683494632340000[165] = 0.0;
   out_4301683494632340000[166] = 0.0;
   out_4301683494632340000[167] = 0.0;
   out_4301683494632340000[168] = 0.0;
   out_4301683494632340000[169] = 0.0;
   out_4301683494632340000[170] = 0.0;
   out_4301683494632340000[171] = 1.0;
   out_4301683494632340000[172] = 0.0;
   out_4301683494632340000[173] = 0.0;
   out_4301683494632340000[174] = 0.0;
   out_4301683494632340000[175] = 0.0;
   out_4301683494632340000[176] = 0.0;
   out_4301683494632340000[177] = 0.0;
   out_4301683494632340000[178] = 0.0;
   out_4301683494632340000[179] = 0.0;
   out_4301683494632340000[180] = 0.0;
   out_4301683494632340000[181] = 0.0;
   out_4301683494632340000[182] = 0.0;
   out_4301683494632340000[183] = 0.0;
   out_4301683494632340000[184] = 0.0;
   out_4301683494632340000[185] = 0.0;
   out_4301683494632340000[186] = 0.0;
   out_4301683494632340000[187] = 0.0;
   out_4301683494632340000[188] = 0.0;
   out_4301683494632340000[189] = 0.0;
   out_4301683494632340000[190] = 1.0;
   out_4301683494632340000[191] = 0.0;
   out_4301683494632340000[192] = 0.0;
   out_4301683494632340000[193] = 0.0;
   out_4301683494632340000[194] = 0.0;
   out_4301683494632340000[195] = 0.0;
   out_4301683494632340000[196] = 0.0;
   out_4301683494632340000[197] = 0.0;
   out_4301683494632340000[198] = 0.0;
   out_4301683494632340000[199] = 0.0;
   out_4301683494632340000[200] = 0.0;
   out_4301683494632340000[201] = 0.0;
   out_4301683494632340000[202] = 0.0;
   out_4301683494632340000[203] = 0.0;
   out_4301683494632340000[204] = 0.0;
   out_4301683494632340000[205] = 0.0;
   out_4301683494632340000[206] = 0.0;
   out_4301683494632340000[207] = 0.0;
   out_4301683494632340000[208] = 0.0;
   out_4301683494632340000[209] = 1.0;
   out_4301683494632340000[210] = 0.0;
   out_4301683494632340000[211] = 0.0;
   out_4301683494632340000[212] = 0.0;
   out_4301683494632340000[213] = 0.0;
   out_4301683494632340000[214] = 0.0;
   out_4301683494632340000[215] = 0.0;
   out_4301683494632340000[216] = 0.0;
   out_4301683494632340000[217] = 0.0;
   out_4301683494632340000[218] = 0.0;
   out_4301683494632340000[219] = 0.0;
   out_4301683494632340000[220] = 0.0;
   out_4301683494632340000[221] = 0.0;
   out_4301683494632340000[222] = 0.0;
   out_4301683494632340000[223] = 0.0;
   out_4301683494632340000[224] = 0.0;
   out_4301683494632340000[225] = 0.0;
   out_4301683494632340000[226] = 0.0;
   out_4301683494632340000[227] = 0.0;
   out_4301683494632340000[228] = 1.0;
   out_4301683494632340000[229] = 0.0;
   out_4301683494632340000[230] = 0.0;
   out_4301683494632340000[231] = 0.0;
   out_4301683494632340000[232] = 0.0;
   out_4301683494632340000[233] = 0.0;
   out_4301683494632340000[234] = 0.0;
   out_4301683494632340000[235] = 0.0;
   out_4301683494632340000[236] = 0.0;
   out_4301683494632340000[237] = 0.0;
   out_4301683494632340000[238] = 0.0;
   out_4301683494632340000[239] = 0.0;
   out_4301683494632340000[240] = 0.0;
   out_4301683494632340000[241] = 0.0;
   out_4301683494632340000[242] = 0.0;
   out_4301683494632340000[243] = 0.0;
   out_4301683494632340000[244] = 0.0;
   out_4301683494632340000[245] = 0.0;
   out_4301683494632340000[246] = 0.0;
   out_4301683494632340000[247] = 1.0;
   out_4301683494632340000[248] = 0.0;
   out_4301683494632340000[249] = 0.0;
   out_4301683494632340000[250] = 0.0;
   out_4301683494632340000[251] = 0.0;
   out_4301683494632340000[252] = 0.0;
   out_4301683494632340000[253] = 0.0;
   out_4301683494632340000[254] = 0.0;
   out_4301683494632340000[255] = 0.0;
   out_4301683494632340000[256] = 0.0;
   out_4301683494632340000[257] = 0.0;
   out_4301683494632340000[258] = 0.0;
   out_4301683494632340000[259] = 0.0;
   out_4301683494632340000[260] = 0.0;
   out_4301683494632340000[261] = 0.0;
   out_4301683494632340000[262] = 0.0;
   out_4301683494632340000[263] = 0.0;
   out_4301683494632340000[264] = 0.0;
   out_4301683494632340000[265] = 0.0;
   out_4301683494632340000[266] = 1.0;
   out_4301683494632340000[267] = 0.0;
   out_4301683494632340000[268] = 0.0;
   out_4301683494632340000[269] = 0.0;
   out_4301683494632340000[270] = 0.0;
   out_4301683494632340000[271] = 0.0;
   out_4301683494632340000[272] = 0.0;
   out_4301683494632340000[273] = 0.0;
   out_4301683494632340000[274] = 0.0;
   out_4301683494632340000[275] = 0.0;
   out_4301683494632340000[276] = 0.0;
   out_4301683494632340000[277] = 0.0;
   out_4301683494632340000[278] = 0.0;
   out_4301683494632340000[279] = 0.0;
   out_4301683494632340000[280] = 0.0;
   out_4301683494632340000[281] = 0.0;
   out_4301683494632340000[282] = 0.0;
   out_4301683494632340000[283] = 0.0;
   out_4301683494632340000[284] = 0.0;
   out_4301683494632340000[285] = 1.0;
   out_4301683494632340000[286] = 0.0;
   out_4301683494632340000[287] = 0.0;
   out_4301683494632340000[288] = 0.0;
   out_4301683494632340000[289] = 0.0;
   out_4301683494632340000[290] = 0.0;
   out_4301683494632340000[291] = 0.0;
   out_4301683494632340000[292] = 0.0;
   out_4301683494632340000[293] = 0.0;
   out_4301683494632340000[294] = 0.0;
   out_4301683494632340000[295] = 0.0;
   out_4301683494632340000[296] = 0.0;
   out_4301683494632340000[297] = 0.0;
   out_4301683494632340000[298] = 0.0;
   out_4301683494632340000[299] = 0.0;
   out_4301683494632340000[300] = 0.0;
   out_4301683494632340000[301] = 0.0;
   out_4301683494632340000[302] = 0.0;
   out_4301683494632340000[303] = 0.0;
   out_4301683494632340000[304] = 1.0;
   out_4301683494632340000[305] = 0.0;
   out_4301683494632340000[306] = 0.0;
   out_4301683494632340000[307] = 0.0;
   out_4301683494632340000[308] = 0.0;
   out_4301683494632340000[309] = 0.0;
   out_4301683494632340000[310] = 0.0;
   out_4301683494632340000[311] = 0.0;
   out_4301683494632340000[312] = 0.0;
   out_4301683494632340000[313] = 0.0;
   out_4301683494632340000[314] = 0.0;
   out_4301683494632340000[315] = 0.0;
   out_4301683494632340000[316] = 0.0;
   out_4301683494632340000[317] = 0.0;
   out_4301683494632340000[318] = 0.0;
   out_4301683494632340000[319] = 0.0;
   out_4301683494632340000[320] = 0.0;
   out_4301683494632340000[321] = 0.0;
   out_4301683494632340000[322] = 0.0;
   out_4301683494632340000[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_4902648027499170863) {
   out_4902648027499170863[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_4902648027499170863[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_4902648027499170863[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_4902648027499170863[3] = dt*state[12] + state[3];
   out_4902648027499170863[4] = dt*state[13] + state[4];
   out_4902648027499170863[5] = dt*state[14] + state[5];
   out_4902648027499170863[6] = state[6];
   out_4902648027499170863[7] = state[7];
   out_4902648027499170863[8] = state[8];
   out_4902648027499170863[9] = state[9];
   out_4902648027499170863[10] = state[10];
   out_4902648027499170863[11] = state[11];
   out_4902648027499170863[12] = state[12];
   out_4902648027499170863[13] = state[13];
   out_4902648027499170863[14] = state[14];
   out_4902648027499170863[15] = state[15];
   out_4902648027499170863[16] = state[16];
   out_4902648027499170863[17] = state[17];
}
void F_fun(double *state, double dt, double *out_6172052704526337973) {
   out_6172052704526337973[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6172052704526337973[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6172052704526337973[2] = 0;
   out_6172052704526337973[3] = 0;
   out_6172052704526337973[4] = 0;
   out_6172052704526337973[5] = 0;
   out_6172052704526337973[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6172052704526337973[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6172052704526337973[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6172052704526337973[9] = 0;
   out_6172052704526337973[10] = 0;
   out_6172052704526337973[11] = 0;
   out_6172052704526337973[12] = 0;
   out_6172052704526337973[13] = 0;
   out_6172052704526337973[14] = 0;
   out_6172052704526337973[15] = 0;
   out_6172052704526337973[16] = 0;
   out_6172052704526337973[17] = 0;
   out_6172052704526337973[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6172052704526337973[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6172052704526337973[20] = 0;
   out_6172052704526337973[21] = 0;
   out_6172052704526337973[22] = 0;
   out_6172052704526337973[23] = 0;
   out_6172052704526337973[24] = 0;
   out_6172052704526337973[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6172052704526337973[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6172052704526337973[27] = 0;
   out_6172052704526337973[28] = 0;
   out_6172052704526337973[29] = 0;
   out_6172052704526337973[30] = 0;
   out_6172052704526337973[31] = 0;
   out_6172052704526337973[32] = 0;
   out_6172052704526337973[33] = 0;
   out_6172052704526337973[34] = 0;
   out_6172052704526337973[35] = 0;
   out_6172052704526337973[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6172052704526337973[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6172052704526337973[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6172052704526337973[39] = 0;
   out_6172052704526337973[40] = 0;
   out_6172052704526337973[41] = 0;
   out_6172052704526337973[42] = 0;
   out_6172052704526337973[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6172052704526337973[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6172052704526337973[45] = 0;
   out_6172052704526337973[46] = 0;
   out_6172052704526337973[47] = 0;
   out_6172052704526337973[48] = 0;
   out_6172052704526337973[49] = 0;
   out_6172052704526337973[50] = 0;
   out_6172052704526337973[51] = 0;
   out_6172052704526337973[52] = 0;
   out_6172052704526337973[53] = 0;
   out_6172052704526337973[54] = 0;
   out_6172052704526337973[55] = 0;
   out_6172052704526337973[56] = 0;
   out_6172052704526337973[57] = 1;
   out_6172052704526337973[58] = 0;
   out_6172052704526337973[59] = 0;
   out_6172052704526337973[60] = 0;
   out_6172052704526337973[61] = 0;
   out_6172052704526337973[62] = 0;
   out_6172052704526337973[63] = 0;
   out_6172052704526337973[64] = 0;
   out_6172052704526337973[65] = 0;
   out_6172052704526337973[66] = dt;
   out_6172052704526337973[67] = 0;
   out_6172052704526337973[68] = 0;
   out_6172052704526337973[69] = 0;
   out_6172052704526337973[70] = 0;
   out_6172052704526337973[71] = 0;
   out_6172052704526337973[72] = 0;
   out_6172052704526337973[73] = 0;
   out_6172052704526337973[74] = 0;
   out_6172052704526337973[75] = 0;
   out_6172052704526337973[76] = 1;
   out_6172052704526337973[77] = 0;
   out_6172052704526337973[78] = 0;
   out_6172052704526337973[79] = 0;
   out_6172052704526337973[80] = 0;
   out_6172052704526337973[81] = 0;
   out_6172052704526337973[82] = 0;
   out_6172052704526337973[83] = 0;
   out_6172052704526337973[84] = 0;
   out_6172052704526337973[85] = dt;
   out_6172052704526337973[86] = 0;
   out_6172052704526337973[87] = 0;
   out_6172052704526337973[88] = 0;
   out_6172052704526337973[89] = 0;
   out_6172052704526337973[90] = 0;
   out_6172052704526337973[91] = 0;
   out_6172052704526337973[92] = 0;
   out_6172052704526337973[93] = 0;
   out_6172052704526337973[94] = 0;
   out_6172052704526337973[95] = 1;
   out_6172052704526337973[96] = 0;
   out_6172052704526337973[97] = 0;
   out_6172052704526337973[98] = 0;
   out_6172052704526337973[99] = 0;
   out_6172052704526337973[100] = 0;
   out_6172052704526337973[101] = 0;
   out_6172052704526337973[102] = 0;
   out_6172052704526337973[103] = 0;
   out_6172052704526337973[104] = dt;
   out_6172052704526337973[105] = 0;
   out_6172052704526337973[106] = 0;
   out_6172052704526337973[107] = 0;
   out_6172052704526337973[108] = 0;
   out_6172052704526337973[109] = 0;
   out_6172052704526337973[110] = 0;
   out_6172052704526337973[111] = 0;
   out_6172052704526337973[112] = 0;
   out_6172052704526337973[113] = 0;
   out_6172052704526337973[114] = 1;
   out_6172052704526337973[115] = 0;
   out_6172052704526337973[116] = 0;
   out_6172052704526337973[117] = 0;
   out_6172052704526337973[118] = 0;
   out_6172052704526337973[119] = 0;
   out_6172052704526337973[120] = 0;
   out_6172052704526337973[121] = 0;
   out_6172052704526337973[122] = 0;
   out_6172052704526337973[123] = 0;
   out_6172052704526337973[124] = 0;
   out_6172052704526337973[125] = 0;
   out_6172052704526337973[126] = 0;
   out_6172052704526337973[127] = 0;
   out_6172052704526337973[128] = 0;
   out_6172052704526337973[129] = 0;
   out_6172052704526337973[130] = 0;
   out_6172052704526337973[131] = 0;
   out_6172052704526337973[132] = 0;
   out_6172052704526337973[133] = 1;
   out_6172052704526337973[134] = 0;
   out_6172052704526337973[135] = 0;
   out_6172052704526337973[136] = 0;
   out_6172052704526337973[137] = 0;
   out_6172052704526337973[138] = 0;
   out_6172052704526337973[139] = 0;
   out_6172052704526337973[140] = 0;
   out_6172052704526337973[141] = 0;
   out_6172052704526337973[142] = 0;
   out_6172052704526337973[143] = 0;
   out_6172052704526337973[144] = 0;
   out_6172052704526337973[145] = 0;
   out_6172052704526337973[146] = 0;
   out_6172052704526337973[147] = 0;
   out_6172052704526337973[148] = 0;
   out_6172052704526337973[149] = 0;
   out_6172052704526337973[150] = 0;
   out_6172052704526337973[151] = 0;
   out_6172052704526337973[152] = 1;
   out_6172052704526337973[153] = 0;
   out_6172052704526337973[154] = 0;
   out_6172052704526337973[155] = 0;
   out_6172052704526337973[156] = 0;
   out_6172052704526337973[157] = 0;
   out_6172052704526337973[158] = 0;
   out_6172052704526337973[159] = 0;
   out_6172052704526337973[160] = 0;
   out_6172052704526337973[161] = 0;
   out_6172052704526337973[162] = 0;
   out_6172052704526337973[163] = 0;
   out_6172052704526337973[164] = 0;
   out_6172052704526337973[165] = 0;
   out_6172052704526337973[166] = 0;
   out_6172052704526337973[167] = 0;
   out_6172052704526337973[168] = 0;
   out_6172052704526337973[169] = 0;
   out_6172052704526337973[170] = 0;
   out_6172052704526337973[171] = 1;
   out_6172052704526337973[172] = 0;
   out_6172052704526337973[173] = 0;
   out_6172052704526337973[174] = 0;
   out_6172052704526337973[175] = 0;
   out_6172052704526337973[176] = 0;
   out_6172052704526337973[177] = 0;
   out_6172052704526337973[178] = 0;
   out_6172052704526337973[179] = 0;
   out_6172052704526337973[180] = 0;
   out_6172052704526337973[181] = 0;
   out_6172052704526337973[182] = 0;
   out_6172052704526337973[183] = 0;
   out_6172052704526337973[184] = 0;
   out_6172052704526337973[185] = 0;
   out_6172052704526337973[186] = 0;
   out_6172052704526337973[187] = 0;
   out_6172052704526337973[188] = 0;
   out_6172052704526337973[189] = 0;
   out_6172052704526337973[190] = 1;
   out_6172052704526337973[191] = 0;
   out_6172052704526337973[192] = 0;
   out_6172052704526337973[193] = 0;
   out_6172052704526337973[194] = 0;
   out_6172052704526337973[195] = 0;
   out_6172052704526337973[196] = 0;
   out_6172052704526337973[197] = 0;
   out_6172052704526337973[198] = 0;
   out_6172052704526337973[199] = 0;
   out_6172052704526337973[200] = 0;
   out_6172052704526337973[201] = 0;
   out_6172052704526337973[202] = 0;
   out_6172052704526337973[203] = 0;
   out_6172052704526337973[204] = 0;
   out_6172052704526337973[205] = 0;
   out_6172052704526337973[206] = 0;
   out_6172052704526337973[207] = 0;
   out_6172052704526337973[208] = 0;
   out_6172052704526337973[209] = 1;
   out_6172052704526337973[210] = 0;
   out_6172052704526337973[211] = 0;
   out_6172052704526337973[212] = 0;
   out_6172052704526337973[213] = 0;
   out_6172052704526337973[214] = 0;
   out_6172052704526337973[215] = 0;
   out_6172052704526337973[216] = 0;
   out_6172052704526337973[217] = 0;
   out_6172052704526337973[218] = 0;
   out_6172052704526337973[219] = 0;
   out_6172052704526337973[220] = 0;
   out_6172052704526337973[221] = 0;
   out_6172052704526337973[222] = 0;
   out_6172052704526337973[223] = 0;
   out_6172052704526337973[224] = 0;
   out_6172052704526337973[225] = 0;
   out_6172052704526337973[226] = 0;
   out_6172052704526337973[227] = 0;
   out_6172052704526337973[228] = 1;
   out_6172052704526337973[229] = 0;
   out_6172052704526337973[230] = 0;
   out_6172052704526337973[231] = 0;
   out_6172052704526337973[232] = 0;
   out_6172052704526337973[233] = 0;
   out_6172052704526337973[234] = 0;
   out_6172052704526337973[235] = 0;
   out_6172052704526337973[236] = 0;
   out_6172052704526337973[237] = 0;
   out_6172052704526337973[238] = 0;
   out_6172052704526337973[239] = 0;
   out_6172052704526337973[240] = 0;
   out_6172052704526337973[241] = 0;
   out_6172052704526337973[242] = 0;
   out_6172052704526337973[243] = 0;
   out_6172052704526337973[244] = 0;
   out_6172052704526337973[245] = 0;
   out_6172052704526337973[246] = 0;
   out_6172052704526337973[247] = 1;
   out_6172052704526337973[248] = 0;
   out_6172052704526337973[249] = 0;
   out_6172052704526337973[250] = 0;
   out_6172052704526337973[251] = 0;
   out_6172052704526337973[252] = 0;
   out_6172052704526337973[253] = 0;
   out_6172052704526337973[254] = 0;
   out_6172052704526337973[255] = 0;
   out_6172052704526337973[256] = 0;
   out_6172052704526337973[257] = 0;
   out_6172052704526337973[258] = 0;
   out_6172052704526337973[259] = 0;
   out_6172052704526337973[260] = 0;
   out_6172052704526337973[261] = 0;
   out_6172052704526337973[262] = 0;
   out_6172052704526337973[263] = 0;
   out_6172052704526337973[264] = 0;
   out_6172052704526337973[265] = 0;
   out_6172052704526337973[266] = 1;
   out_6172052704526337973[267] = 0;
   out_6172052704526337973[268] = 0;
   out_6172052704526337973[269] = 0;
   out_6172052704526337973[270] = 0;
   out_6172052704526337973[271] = 0;
   out_6172052704526337973[272] = 0;
   out_6172052704526337973[273] = 0;
   out_6172052704526337973[274] = 0;
   out_6172052704526337973[275] = 0;
   out_6172052704526337973[276] = 0;
   out_6172052704526337973[277] = 0;
   out_6172052704526337973[278] = 0;
   out_6172052704526337973[279] = 0;
   out_6172052704526337973[280] = 0;
   out_6172052704526337973[281] = 0;
   out_6172052704526337973[282] = 0;
   out_6172052704526337973[283] = 0;
   out_6172052704526337973[284] = 0;
   out_6172052704526337973[285] = 1;
   out_6172052704526337973[286] = 0;
   out_6172052704526337973[287] = 0;
   out_6172052704526337973[288] = 0;
   out_6172052704526337973[289] = 0;
   out_6172052704526337973[290] = 0;
   out_6172052704526337973[291] = 0;
   out_6172052704526337973[292] = 0;
   out_6172052704526337973[293] = 0;
   out_6172052704526337973[294] = 0;
   out_6172052704526337973[295] = 0;
   out_6172052704526337973[296] = 0;
   out_6172052704526337973[297] = 0;
   out_6172052704526337973[298] = 0;
   out_6172052704526337973[299] = 0;
   out_6172052704526337973[300] = 0;
   out_6172052704526337973[301] = 0;
   out_6172052704526337973[302] = 0;
   out_6172052704526337973[303] = 0;
   out_6172052704526337973[304] = 1;
   out_6172052704526337973[305] = 0;
   out_6172052704526337973[306] = 0;
   out_6172052704526337973[307] = 0;
   out_6172052704526337973[308] = 0;
   out_6172052704526337973[309] = 0;
   out_6172052704526337973[310] = 0;
   out_6172052704526337973[311] = 0;
   out_6172052704526337973[312] = 0;
   out_6172052704526337973[313] = 0;
   out_6172052704526337973[314] = 0;
   out_6172052704526337973[315] = 0;
   out_6172052704526337973[316] = 0;
   out_6172052704526337973[317] = 0;
   out_6172052704526337973[318] = 0;
   out_6172052704526337973[319] = 0;
   out_6172052704526337973[320] = 0;
   out_6172052704526337973[321] = 0;
   out_6172052704526337973[322] = 0;
   out_6172052704526337973[323] = 1;
}
void h_4(double *state, double *unused, double *out_5496881137641670048) {
   out_5496881137641670048[0] = state[6] + state[9];
   out_5496881137641670048[1] = state[7] + state[10];
   out_5496881137641670048[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_8296978772325252895) {
   out_8296978772325252895[0] = 0;
   out_8296978772325252895[1] = 0;
   out_8296978772325252895[2] = 0;
   out_8296978772325252895[3] = 0;
   out_8296978772325252895[4] = 0;
   out_8296978772325252895[5] = 0;
   out_8296978772325252895[6] = 1;
   out_8296978772325252895[7] = 0;
   out_8296978772325252895[8] = 0;
   out_8296978772325252895[9] = 1;
   out_8296978772325252895[10] = 0;
   out_8296978772325252895[11] = 0;
   out_8296978772325252895[12] = 0;
   out_8296978772325252895[13] = 0;
   out_8296978772325252895[14] = 0;
   out_8296978772325252895[15] = 0;
   out_8296978772325252895[16] = 0;
   out_8296978772325252895[17] = 0;
   out_8296978772325252895[18] = 0;
   out_8296978772325252895[19] = 0;
   out_8296978772325252895[20] = 0;
   out_8296978772325252895[21] = 0;
   out_8296978772325252895[22] = 0;
   out_8296978772325252895[23] = 0;
   out_8296978772325252895[24] = 0;
   out_8296978772325252895[25] = 1;
   out_8296978772325252895[26] = 0;
   out_8296978772325252895[27] = 0;
   out_8296978772325252895[28] = 1;
   out_8296978772325252895[29] = 0;
   out_8296978772325252895[30] = 0;
   out_8296978772325252895[31] = 0;
   out_8296978772325252895[32] = 0;
   out_8296978772325252895[33] = 0;
   out_8296978772325252895[34] = 0;
   out_8296978772325252895[35] = 0;
   out_8296978772325252895[36] = 0;
   out_8296978772325252895[37] = 0;
   out_8296978772325252895[38] = 0;
   out_8296978772325252895[39] = 0;
   out_8296978772325252895[40] = 0;
   out_8296978772325252895[41] = 0;
   out_8296978772325252895[42] = 0;
   out_8296978772325252895[43] = 0;
   out_8296978772325252895[44] = 1;
   out_8296978772325252895[45] = 0;
   out_8296978772325252895[46] = 0;
   out_8296978772325252895[47] = 1;
   out_8296978772325252895[48] = 0;
   out_8296978772325252895[49] = 0;
   out_8296978772325252895[50] = 0;
   out_8296978772325252895[51] = 0;
   out_8296978772325252895[52] = 0;
   out_8296978772325252895[53] = 0;
}
void h_10(double *state, double *unused, double *out_4392166538936845360) {
   out_4392166538936845360[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_4392166538936845360[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_4392166538936845360[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_3969889714076716852) {
   out_3969889714076716852[0] = 0;
   out_3969889714076716852[1] = 9.8100000000000005*cos(state[1]);
   out_3969889714076716852[2] = 0;
   out_3969889714076716852[3] = 0;
   out_3969889714076716852[4] = -state[8];
   out_3969889714076716852[5] = state[7];
   out_3969889714076716852[6] = 0;
   out_3969889714076716852[7] = state[5];
   out_3969889714076716852[8] = -state[4];
   out_3969889714076716852[9] = 0;
   out_3969889714076716852[10] = 0;
   out_3969889714076716852[11] = 0;
   out_3969889714076716852[12] = 1;
   out_3969889714076716852[13] = 0;
   out_3969889714076716852[14] = 0;
   out_3969889714076716852[15] = 1;
   out_3969889714076716852[16] = 0;
   out_3969889714076716852[17] = 0;
   out_3969889714076716852[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_3969889714076716852[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_3969889714076716852[20] = 0;
   out_3969889714076716852[21] = state[8];
   out_3969889714076716852[22] = 0;
   out_3969889714076716852[23] = -state[6];
   out_3969889714076716852[24] = -state[5];
   out_3969889714076716852[25] = 0;
   out_3969889714076716852[26] = state[3];
   out_3969889714076716852[27] = 0;
   out_3969889714076716852[28] = 0;
   out_3969889714076716852[29] = 0;
   out_3969889714076716852[30] = 0;
   out_3969889714076716852[31] = 1;
   out_3969889714076716852[32] = 0;
   out_3969889714076716852[33] = 0;
   out_3969889714076716852[34] = 1;
   out_3969889714076716852[35] = 0;
   out_3969889714076716852[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_3969889714076716852[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_3969889714076716852[38] = 0;
   out_3969889714076716852[39] = -state[7];
   out_3969889714076716852[40] = state[6];
   out_3969889714076716852[41] = 0;
   out_3969889714076716852[42] = state[4];
   out_3969889714076716852[43] = -state[3];
   out_3969889714076716852[44] = 0;
   out_3969889714076716852[45] = 0;
   out_3969889714076716852[46] = 0;
   out_3969889714076716852[47] = 0;
   out_3969889714076716852[48] = 0;
   out_3969889714076716852[49] = 0;
   out_3969889714076716852[50] = 1;
   out_3969889714076716852[51] = 0;
   out_3969889714076716852[52] = 0;
   out_3969889714076716852[53] = 1;
}
void h_13(double *state, double *unused, double *out_7956955057143480558) {
   out_7956955057143480558[0] = state[3];
   out_7956955057143480558[1] = state[4];
   out_7956955057143480558[2] = state[5];
}
void H_13(double *state, double *unused, double *out_6937491476051965920) {
   out_6937491476051965920[0] = 0;
   out_6937491476051965920[1] = 0;
   out_6937491476051965920[2] = 0;
   out_6937491476051965920[3] = 1;
   out_6937491476051965920[4] = 0;
   out_6937491476051965920[5] = 0;
   out_6937491476051965920[6] = 0;
   out_6937491476051965920[7] = 0;
   out_6937491476051965920[8] = 0;
   out_6937491476051965920[9] = 0;
   out_6937491476051965920[10] = 0;
   out_6937491476051965920[11] = 0;
   out_6937491476051965920[12] = 0;
   out_6937491476051965920[13] = 0;
   out_6937491476051965920[14] = 0;
   out_6937491476051965920[15] = 0;
   out_6937491476051965920[16] = 0;
   out_6937491476051965920[17] = 0;
   out_6937491476051965920[18] = 0;
   out_6937491476051965920[19] = 0;
   out_6937491476051965920[20] = 0;
   out_6937491476051965920[21] = 0;
   out_6937491476051965920[22] = 1;
   out_6937491476051965920[23] = 0;
   out_6937491476051965920[24] = 0;
   out_6937491476051965920[25] = 0;
   out_6937491476051965920[26] = 0;
   out_6937491476051965920[27] = 0;
   out_6937491476051965920[28] = 0;
   out_6937491476051965920[29] = 0;
   out_6937491476051965920[30] = 0;
   out_6937491476051965920[31] = 0;
   out_6937491476051965920[32] = 0;
   out_6937491476051965920[33] = 0;
   out_6937491476051965920[34] = 0;
   out_6937491476051965920[35] = 0;
   out_6937491476051965920[36] = 0;
   out_6937491476051965920[37] = 0;
   out_6937491476051965920[38] = 0;
   out_6937491476051965920[39] = 0;
   out_6937491476051965920[40] = 0;
   out_6937491476051965920[41] = 1;
   out_6937491476051965920[42] = 0;
   out_6937491476051965920[43] = 0;
   out_6937491476051965920[44] = 0;
   out_6937491476051965920[45] = 0;
   out_6937491476051965920[46] = 0;
   out_6937491476051965920[47] = 0;
   out_6937491476051965920[48] = 0;
   out_6937491476051965920[49] = 0;
   out_6937491476051965920[50] = 0;
   out_6937491476051965920[51] = 0;
   out_6937491476051965920[52] = 0;
   out_6937491476051965920[53] = 0;
}
void h_14(double *state, double *unused, double *out_4392676402397196917) {
   out_4392676402397196917[0] = state[6];
   out_4392676402397196917[1] = state[7];
   out_4392676402397196917[2] = state[8];
}
void H_14(double *state, double *unused, double *out_6186524445044814192) {
   out_6186524445044814192[0] = 0;
   out_6186524445044814192[1] = 0;
   out_6186524445044814192[2] = 0;
   out_6186524445044814192[3] = 0;
   out_6186524445044814192[4] = 0;
   out_6186524445044814192[5] = 0;
   out_6186524445044814192[6] = 1;
   out_6186524445044814192[7] = 0;
   out_6186524445044814192[8] = 0;
   out_6186524445044814192[9] = 0;
   out_6186524445044814192[10] = 0;
   out_6186524445044814192[11] = 0;
   out_6186524445044814192[12] = 0;
   out_6186524445044814192[13] = 0;
   out_6186524445044814192[14] = 0;
   out_6186524445044814192[15] = 0;
   out_6186524445044814192[16] = 0;
   out_6186524445044814192[17] = 0;
   out_6186524445044814192[18] = 0;
   out_6186524445044814192[19] = 0;
   out_6186524445044814192[20] = 0;
   out_6186524445044814192[21] = 0;
   out_6186524445044814192[22] = 0;
   out_6186524445044814192[23] = 0;
   out_6186524445044814192[24] = 0;
   out_6186524445044814192[25] = 1;
   out_6186524445044814192[26] = 0;
   out_6186524445044814192[27] = 0;
   out_6186524445044814192[28] = 0;
   out_6186524445044814192[29] = 0;
   out_6186524445044814192[30] = 0;
   out_6186524445044814192[31] = 0;
   out_6186524445044814192[32] = 0;
   out_6186524445044814192[33] = 0;
   out_6186524445044814192[34] = 0;
   out_6186524445044814192[35] = 0;
   out_6186524445044814192[36] = 0;
   out_6186524445044814192[37] = 0;
   out_6186524445044814192[38] = 0;
   out_6186524445044814192[39] = 0;
   out_6186524445044814192[40] = 0;
   out_6186524445044814192[41] = 0;
   out_6186524445044814192[42] = 0;
   out_6186524445044814192[43] = 0;
   out_6186524445044814192[44] = 1;
   out_6186524445044814192[45] = 0;
   out_6186524445044814192[46] = 0;
   out_6186524445044814192[47] = 0;
   out_6186524445044814192[48] = 0;
   out_6186524445044814192[49] = 0;
   out_6186524445044814192[50] = 0;
   out_6186524445044814192[51] = 0;
   out_6186524445044814192[52] = 0;
   out_6186524445044814192[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_4430854607241578209) {
  err_fun(nom_x, delta_x, out_4430854607241578209);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_8029849703839127827) {
  inv_err_fun(nom_x, true_x, out_8029849703839127827);
}
void pose_H_mod_fun(double *state, double *out_4301683494632340000) {
  H_mod_fun(state, out_4301683494632340000);
}
void pose_f_fun(double *state, double dt, double *out_4902648027499170863) {
  f_fun(state,  dt, out_4902648027499170863);
}
void pose_F_fun(double *state, double dt, double *out_6172052704526337973) {
  F_fun(state,  dt, out_6172052704526337973);
}
void pose_h_4(double *state, double *unused, double *out_5496881137641670048) {
  h_4(state, unused, out_5496881137641670048);
}
void pose_H_4(double *state, double *unused, double *out_8296978772325252895) {
  H_4(state, unused, out_8296978772325252895);
}
void pose_h_10(double *state, double *unused, double *out_4392166538936845360) {
  h_10(state, unused, out_4392166538936845360);
}
void pose_H_10(double *state, double *unused, double *out_3969889714076716852) {
  H_10(state, unused, out_3969889714076716852);
}
void pose_h_13(double *state, double *unused, double *out_7956955057143480558) {
  h_13(state, unused, out_7956955057143480558);
}
void pose_H_13(double *state, double *unused, double *out_6937491476051965920) {
  H_13(state, unused, out_6937491476051965920);
}
void pose_h_14(double *state, double *unused, double *out_4392676402397196917) {
  h_14(state, unused, out_4392676402397196917);
}
void pose_H_14(double *state, double *unused, double *out_6186524445044814192) {
  H_14(state, unused, out_6186524445044814192);
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
