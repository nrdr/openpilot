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
void err_fun(double *nom_x, double *delta_x, double *out_4192685534810622048) {
   out_4192685534810622048[0] = delta_x[0] + nom_x[0];
   out_4192685534810622048[1] = delta_x[1] + nom_x[1];
   out_4192685534810622048[2] = delta_x[2] + nom_x[2];
   out_4192685534810622048[3] = delta_x[3] + nom_x[3];
   out_4192685534810622048[4] = delta_x[4] + nom_x[4];
   out_4192685534810622048[5] = delta_x[5] + nom_x[5];
   out_4192685534810622048[6] = delta_x[6] + nom_x[6];
   out_4192685534810622048[7] = delta_x[7] + nom_x[7];
   out_4192685534810622048[8] = delta_x[8] + nom_x[8];
   out_4192685534810622048[9] = delta_x[9] + nom_x[9];
   out_4192685534810622048[10] = delta_x[10] + nom_x[10];
   out_4192685534810622048[11] = delta_x[11] + nom_x[11];
   out_4192685534810622048[12] = delta_x[12] + nom_x[12];
   out_4192685534810622048[13] = delta_x[13] + nom_x[13];
   out_4192685534810622048[14] = delta_x[14] + nom_x[14];
   out_4192685534810622048[15] = delta_x[15] + nom_x[15];
   out_4192685534810622048[16] = delta_x[16] + nom_x[16];
   out_4192685534810622048[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5779284205001834883) {
   out_5779284205001834883[0] = -nom_x[0] + true_x[0];
   out_5779284205001834883[1] = -nom_x[1] + true_x[1];
   out_5779284205001834883[2] = -nom_x[2] + true_x[2];
   out_5779284205001834883[3] = -nom_x[3] + true_x[3];
   out_5779284205001834883[4] = -nom_x[4] + true_x[4];
   out_5779284205001834883[5] = -nom_x[5] + true_x[5];
   out_5779284205001834883[6] = -nom_x[6] + true_x[6];
   out_5779284205001834883[7] = -nom_x[7] + true_x[7];
   out_5779284205001834883[8] = -nom_x[8] + true_x[8];
   out_5779284205001834883[9] = -nom_x[9] + true_x[9];
   out_5779284205001834883[10] = -nom_x[10] + true_x[10];
   out_5779284205001834883[11] = -nom_x[11] + true_x[11];
   out_5779284205001834883[12] = -nom_x[12] + true_x[12];
   out_5779284205001834883[13] = -nom_x[13] + true_x[13];
   out_5779284205001834883[14] = -nom_x[14] + true_x[14];
   out_5779284205001834883[15] = -nom_x[15] + true_x[15];
   out_5779284205001834883[16] = -nom_x[16] + true_x[16];
   out_5779284205001834883[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_7935155873385146551) {
   out_7935155873385146551[0] = 1.0;
   out_7935155873385146551[1] = 0.0;
   out_7935155873385146551[2] = 0.0;
   out_7935155873385146551[3] = 0.0;
   out_7935155873385146551[4] = 0.0;
   out_7935155873385146551[5] = 0.0;
   out_7935155873385146551[6] = 0.0;
   out_7935155873385146551[7] = 0.0;
   out_7935155873385146551[8] = 0.0;
   out_7935155873385146551[9] = 0.0;
   out_7935155873385146551[10] = 0.0;
   out_7935155873385146551[11] = 0.0;
   out_7935155873385146551[12] = 0.0;
   out_7935155873385146551[13] = 0.0;
   out_7935155873385146551[14] = 0.0;
   out_7935155873385146551[15] = 0.0;
   out_7935155873385146551[16] = 0.0;
   out_7935155873385146551[17] = 0.0;
   out_7935155873385146551[18] = 0.0;
   out_7935155873385146551[19] = 1.0;
   out_7935155873385146551[20] = 0.0;
   out_7935155873385146551[21] = 0.0;
   out_7935155873385146551[22] = 0.0;
   out_7935155873385146551[23] = 0.0;
   out_7935155873385146551[24] = 0.0;
   out_7935155873385146551[25] = 0.0;
   out_7935155873385146551[26] = 0.0;
   out_7935155873385146551[27] = 0.0;
   out_7935155873385146551[28] = 0.0;
   out_7935155873385146551[29] = 0.0;
   out_7935155873385146551[30] = 0.0;
   out_7935155873385146551[31] = 0.0;
   out_7935155873385146551[32] = 0.0;
   out_7935155873385146551[33] = 0.0;
   out_7935155873385146551[34] = 0.0;
   out_7935155873385146551[35] = 0.0;
   out_7935155873385146551[36] = 0.0;
   out_7935155873385146551[37] = 0.0;
   out_7935155873385146551[38] = 1.0;
   out_7935155873385146551[39] = 0.0;
   out_7935155873385146551[40] = 0.0;
   out_7935155873385146551[41] = 0.0;
   out_7935155873385146551[42] = 0.0;
   out_7935155873385146551[43] = 0.0;
   out_7935155873385146551[44] = 0.0;
   out_7935155873385146551[45] = 0.0;
   out_7935155873385146551[46] = 0.0;
   out_7935155873385146551[47] = 0.0;
   out_7935155873385146551[48] = 0.0;
   out_7935155873385146551[49] = 0.0;
   out_7935155873385146551[50] = 0.0;
   out_7935155873385146551[51] = 0.0;
   out_7935155873385146551[52] = 0.0;
   out_7935155873385146551[53] = 0.0;
   out_7935155873385146551[54] = 0.0;
   out_7935155873385146551[55] = 0.0;
   out_7935155873385146551[56] = 0.0;
   out_7935155873385146551[57] = 1.0;
   out_7935155873385146551[58] = 0.0;
   out_7935155873385146551[59] = 0.0;
   out_7935155873385146551[60] = 0.0;
   out_7935155873385146551[61] = 0.0;
   out_7935155873385146551[62] = 0.0;
   out_7935155873385146551[63] = 0.0;
   out_7935155873385146551[64] = 0.0;
   out_7935155873385146551[65] = 0.0;
   out_7935155873385146551[66] = 0.0;
   out_7935155873385146551[67] = 0.0;
   out_7935155873385146551[68] = 0.0;
   out_7935155873385146551[69] = 0.0;
   out_7935155873385146551[70] = 0.0;
   out_7935155873385146551[71] = 0.0;
   out_7935155873385146551[72] = 0.0;
   out_7935155873385146551[73] = 0.0;
   out_7935155873385146551[74] = 0.0;
   out_7935155873385146551[75] = 0.0;
   out_7935155873385146551[76] = 1.0;
   out_7935155873385146551[77] = 0.0;
   out_7935155873385146551[78] = 0.0;
   out_7935155873385146551[79] = 0.0;
   out_7935155873385146551[80] = 0.0;
   out_7935155873385146551[81] = 0.0;
   out_7935155873385146551[82] = 0.0;
   out_7935155873385146551[83] = 0.0;
   out_7935155873385146551[84] = 0.0;
   out_7935155873385146551[85] = 0.0;
   out_7935155873385146551[86] = 0.0;
   out_7935155873385146551[87] = 0.0;
   out_7935155873385146551[88] = 0.0;
   out_7935155873385146551[89] = 0.0;
   out_7935155873385146551[90] = 0.0;
   out_7935155873385146551[91] = 0.0;
   out_7935155873385146551[92] = 0.0;
   out_7935155873385146551[93] = 0.0;
   out_7935155873385146551[94] = 0.0;
   out_7935155873385146551[95] = 1.0;
   out_7935155873385146551[96] = 0.0;
   out_7935155873385146551[97] = 0.0;
   out_7935155873385146551[98] = 0.0;
   out_7935155873385146551[99] = 0.0;
   out_7935155873385146551[100] = 0.0;
   out_7935155873385146551[101] = 0.0;
   out_7935155873385146551[102] = 0.0;
   out_7935155873385146551[103] = 0.0;
   out_7935155873385146551[104] = 0.0;
   out_7935155873385146551[105] = 0.0;
   out_7935155873385146551[106] = 0.0;
   out_7935155873385146551[107] = 0.0;
   out_7935155873385146551[108] = 0.0;
   out_7935155873385146551[109] = 0.0;
   out_7935155873385146551[110] = 0.0;
   out_7935155873385146551[111] = 0.0;
   out_7935155873385146551[112] = 0.0;
   out_7935155873385146551[113] = 0.0;
   out_7935155873385146551[114] = 1.0;
   out_7935155873385146551[115] = 0.0;
   out_7935155873385146551[116] = 0.0;
   out_7935155873385146551[117] = 0.0;
   out_7935155873385146551[118] = 0.0;
   out_7935155873385146551[119] = 0.0;
   out_7935155873385146551[120] = 0.0;
   out_7935155873385146551[121] = 0.0;
   out_7935155873385146551[122] = 0.0;
   out_7935155873385146551[123] = 0.0;
   out_7935155873385146551[124] = 0.0;
   out_7935155873385146551[125] = 0.0;
   out_7935155873385146551[126] = 0.0;
   out_7935155873385146551[127] = 0.0;
   out_7935155873385146551[128] = 0.0;
   out_7935155873385146551[129] = 0.0;
   out_7935155873385146551[130] = 0.0;
   out_7935155873385146551[131] = 0.0;
   out_7935155873385146551[132] = 0.0;
   out_7935155873385146551[133] = 1.0;
   out_7935155873385146551[134] = 0.0;
   out_7935155873385146551[135] = 0.0;
   out_7935155873385146551[136] = 0.0;
   out_7935155873385146551[137] = 0.0;
   out_7935155873385146551[138] = 0.0;
   out_7935155873385146551[139] = 0.0;
   out_7935155873385146551[140] = 0.0;
   out_7935155873385146551[141] = 0.0;
   out_7935155873385146551[142] = 0.0;
   out_7935155873385146551[143] = 0.0;
   out_7935155873385146551[144] = 0.0;
   out_7935155873385146551[145] = 0.0;
   out_7935155873385146551[146] = 0.0;
   out_7935155873385146551[147] = 0.0;
   out_7935155873385146551[148] = 0.0;
   out_7935155873385146551[149] = 0.0;
   out_7935155873385146551[150] = 0.0;
   out_7935155873385146551[151] = 0.0;
   out_7935155873385146551[152] = 1.0;
   out_7935155873385146551[153] = 0.0;
   out_7935155873385146551[154] = 0.0;
   out_7935155873385146551[155] = 0.0;
   out_7935155873385146551[156] = 0.0;
   out_7935155873385146551[157] = 0.0;
   out_7935155873385146551[158] = 0.0;
   out_7935155873385146551[159] = 0.0;
   out_7935155873385146551[160] = 0.0;
   out_7935155873385146551[161] = 0.0;
   out_7935155873385146551[162] = 0.0;
   out_7935155873385146551[163] = 0.0;
   out_7935155873385146551[164] = 0.0;
   out_7935155873385146551[165] = 0.0;
   out_7935155873385146551[166] = 0.0;
   out_7935155873385146551[167] = 0.0;
   out_7935155873385146551[168] = 0.0;
   out_7935155873385146551[169] = 0.0;
   out_7935155873385146551[170] = 0.0;
   out_7935155873385146551[171] = 1.0;
   out_7935155873385146551[172] = 0.0;
   out_7935155873385146551[173] = 0.0;
   out_7935155873385146551[174] = 0.0;
   out_7935155873385146551[175] = 0.0;
   out_7935155873385146551[176] = 0.0;
   out_7935155873385146551[177] = 0.0;
   out_7935155873385146551[178] = 0.0;
   out_7935155873385146551[179] = 0.0;
   out_7935155873385146551[180] = 0.0;
   out_7935155873385146551[181] = 0.0;
   out_7935155873385146551[182] = 0.0;
   out_7935155873385146551[183] = 0.0;
   out_7935155873385146551[184] = 0.0;
   out_7935155873385146551[185] = 0.0;
   out_7935155873385146551[186] = 0.0;
   out_7935155873385146551[187] = 0.0;
   out_7935155873385146551[188] = 0.0;
   out_7935155873385146551[189] = 0.0;
   out_7935155873385146551[190] = 1.0;
   out_7935155873385146551[191] = 0.0;
   out_7935155873385146551[192] = 0.0;
   out_7935155873385146551[193] = 0.0;
   out_7935155873385146551[194] = 0.0;
   out_7935155873385146551[195] = 0.0;
   out_7935155873385146551[196] = 0.0;
   out_7935155873385146551[197] = 0.0;
   out_7935155873385146551[198] = 0.0;
   out_7935155873385146551[199] = 0.0;
   out_7935155873385146551[200] = 0.0;
   out_7935155873385146551[201] = 0.0;
   out_7935155873385146551[202] = 0.0;
   out_7935155873385146551[203] = 0.0;
   out_7935155873385146551[204] = 0.0;
   out_7935155873385146551[205] = 0.0;
   out_7935155873385146551[206] = 0.0;
   out_7935155873385146551[207] = 0.0;
   out_7935155873385146551[208] = 0.0;
   out_7935155873385146551[209] = 1.0;
   out_7935155873385146551[210] = 0.0;
   out_7935155873385146551[211] = 0.0;
   out_7935155873385146551[212] = 0.0;
   out_7935155873385146551[213] = 0.0;
   out_7935155873385146551[214] = 0.0;
   out_7935155873385146551[215] = 0.0;
   out_7935155873385146551[216] = 0.0;
   out_7935155873385146551[217] = 0.0;
   out_7935155873385146551[218] = 0.0;
   out_7935155873385146551[219] = 0.0;
   out_7935155873385146551[220] = 0.0;
   out_7935155873385146551[221] = 0.0;
   out_7935155873385146551[222] = 0.0;
   out_7935155873385146551[223] = 0.0;
   out_7935155873385146551[224] = 0.0;
   out_7935155873385146551[225] = 0.0;
   out_7935155873385146551[226] = 0.0;
   out_7935155873385146551[227] = 0.0;
   out_7935155873385146551[228] = 1.0;
   out_7935155873385146551[229] = 0.0;
   out_7935155873385146551[230] = 0.0;
   out_7935155873385146551[231] = 0.0;
   out_7935155873385146551[232] = 0.0;
   out_7935155873385146551[233] = 0.0;
   out_7935155873385146551[234] = 0.0;
   out_7935155873385146551[235] = 0.0;
   out_7935155873385146551[236] = 0.0;
   out_7935155873385146551[237] = 0.0;
   out_7935155873385146551[238] = 0.0;
   out_7935155873385146551[239] = 0.0;
   out_7935155873385146551[240] = 0.0;
   out_7935155873385146551[241] = 0.0;
   out_7935155873385146551[242] = 0.0;
   out_7935155873385146551[243] = 0.0;
   out_7935155873385146551[244] = 0.0;
   out_7935155873385146551[245] = 0.0;
   out_7935155873385146551[246] = 0.0;
   out_7935155873385146551[247] = 1.0;
   out_7935155873385146551[248] = 0.0;
   out_7935155873385146551[249] = 0.0;
   out_7935155873385146551[250] = 0.0;
   out_7935155873385146551[251] = 0.0;
   out_7935155873385146551[252] = 0.0;
   out_7935155873385146551[253] = 0.0;
   out_7935155873385146551[254] = 0.0;
   out_7935155873385146551[255] = 0.0;
   out_7935155873385146551[256] = 0.0;
   out_7935155873385146551[257] = 0.0;
   out_7935155873385146551[258] = 0.0;
   out_7935155873385146551[259] = 0.0;
   out_7935155873385146551[260] = 0.0;
   out_7935155873385146551[261] = 0.0;
   out_7935155873385146551[262] = 0.0;
   out_7935155873385146551[263] = 0.0;
   out_7935155873385146551[264] = 0.0;
   out_7935155873385146551[265] = 0.0;
   out_7935155873385146551[266] = 1.0;
   out_7935155873385146551[267] = 0.0;
   out_7935155873385146551[268] = 0.0;
   out_7935155873385146551[269] = 0.0;
   out_7935155873385146551[270] = 0.0;
   out_7935155873385146551[271] = 0.0;
   out_7935155873385146551[272] = 0.0;
   out_7935155873385146551[273] = 0.0;
   out_7935155873385146551[274] = 0.0;
   out_7935155873385146551[275] = 0.0;
   out_7935155873385146551[276] = 0.0;
   out_7935155873385146551[277] = 0.0;
   out_7935155873385146551[278] = 0.0;
   out_7935155873385146551[279] = 0.0;
   out_7935155873385146551[280] = 0.0;
   out_7935155873385146551[281] = 0.0;
   out_7935155873385146551[282] = 0.0;
   out_7935155873385146551[283] = 0.0;
   out_7935155873385146551[284] = 0.0;
   out_7935155873385146551[285] = 1.0;
   out_7935155873385146551[286] = 0.0;
   out_7935155873385146551[287] = 0.0;
   out_7935155873385146551[288] = 0.0;
   out_7935155873385146551[289] = 0.0;
   out_7935155873385146551[290] = 0.0;
   out_7935155873385146551[291] = 0.0;
   out_7935155873385146551[292] = 0.0;
   out_7935155873385146551[293] = 0.0;
   out_7935155873385146551[294] = 0.0;
   out_7935155873385146551[295] = 0.0;
   out_7935155873385146551[296] = 0.0;
   out_7935155873385146551[297] = 0.0;
   out_7935155873385146551[298] = 0.0;
   out_7935155873385146551[299] = 0.0;
   out_7935155873385146551[300] = 0.0;
   out_7935155873385146551[301] = 0.0;
   out_7935155873385146551[302] = 0.0;
   out_7935155873385146551[303] = 0.0;
   out_7935155873385146551[304] = 1.0;
   out_7935155873385146551[305] = 0.0;
   out_7935155873385146551[306] = 0.0;
   out_7935155873385146551[307] = 0.0;
   out_7935155873385146551[308] = 0.0;
   out_7935155873385146551[309] = 0.0;
   out_7935155873385146551[310] = 0.0;
   out_7935155873385146551[311] = 0.0;
   out_7935155873385146551[312] = 0.0;
   out_7935155873385146551[313] = 0.0;
   out_7935155873385146551[314] = 0.0;
   out_7935155873385146551[315] = 0.0;
   out_7935155873385146551[316] = 0.0;
   out_7935155873385146551[317] = 0.0;
   out_7935155873385146551[318] = 0.0;
   out_7935155873385146551[319] = 0.0;
   out_7935155873385146551[320] = 0.0;
   out_7935155873385146551[321] = 0.0;
   out_7935155873385146551[322] = 0.0;
   out_7935155873385146551[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_1369858821784309025) {
   out_1369858821784309025[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_1369858821784309025[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_1369858821784309025[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_1369858821784309025[3] = dt*state[12] + state[3];
   out_1369858821784309025[4] = dt*state[13] + state[4];
   out_1369858821784309025[5] = dt*state[14] + state[5];
   out_1369858821784309025[6] = state[6];
   out_1369858821784309025[7] = state[7];
   out_1369858821784309025[8] = state[8];
   out_1369858821784309025[9] = state[9];
   out_1369858821784309025[10] = state[10];
   out_1369858821784309025[11] = state[11];
   out_1369858821784309025[12] = state[12];
   out_1369858821784309025[13] = state[13];
   out_1369858821784309025[14] = state[14];
   out_1369858821784309025[15] = state[15];
   out_1369858821784309025[16] = state[16];
   out_1369858821784309025[17] = state[17];
}
void F_fun(double *state, double dt, double *out_7622300413093662135) {
   out_7622300413093662135[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7622300413093662135[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7622300413093662135[2] = 0;
   out_7622300413093662135[3] = 0;
   out_7622300413093662135[4] = 0;
   out_7622300413093662135[5] = 0;
   out_7622300413093662135[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7622300413093662135[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7622300413093662135[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_7622300413093662135[9] = 0;
   out_7622300413093662135[10] = 0;
   out_7622300413093662135[11] = 0;
   out_7622300413093662135[12] = 0;
   out_7622300413093662135[13] = 0;
   out_7622300413093662135[14] = 0;
   out_7622300413093662135[15] = 0;
   out_7622300413093662135[16] = 0;
   out_7622300413093662135[17] = 0;
   out_7622300413093662135[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7622300413093662135[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7622300413093662135[20] = 0;
   out_7622300413093662135[21] = 0;
   out_7622300413093662135[22] = 0;
   out_7622300413093662135[23] = 0;
   out_7622300413093662135[24] = 0;
   out_7622300413093662135[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7622300413093662135[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_7622300413093662135[27] = 0;
   out_7622300413093662135[28] = 0;
   out_7622300413093662135[29] = 0;
   out_7622300413093662135[30] = 0;
   out_7622300413093662135[31] = 0;
   out_7622300413093662135[32] = 0;
   out_7622300413093662135[33] = 0;
   out_7622300413093662135[34] = 0;
   out_7622300413093662135[35] = 0;
   out_7622300413093662135[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7622300413093662135[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7622300413093662135[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7622300413093662135[39] = 0;
   out_7622300413093662135[40] = 0;
   out_7622300413093662135[41] = 0;
   out_7622300413093662135[42] = 0;
   out_7622300413093662135[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7622300413093662135[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_7622300413093662135[45] = 0;
   out_7622300413093662135[46] = 0;
   out_7622300413093662135[47] = 0;
   out_7622300413093662135[48] = 0;
   out_7622300413093662135[49] = 0;
   out_7622300413093662135[50] = 0;
   out_7622300413093662135[51] = 0;
   out_7622300413093662135[52] = 0;
   out_7622300413093662135[53] = 0;
   out_7622300413093662135[54] = 0;
   out_7622300413093662135[55] = 0;
   out_7622300413093662135[56] = 0;
   out_7622300413093662135[57] = 1;
   out_7622300413093662135[58] = 0;
   out_7622300413093662135[59] = 0;
   out_7622300413093662135[60] = 0;
   out_7622300413093662135[61] = 0;
   out_7622300413093662135[62] = 0;
   out_7622300413093662135[63] = 0;
   out_7622300413093662135[64] = 0;
   out_7622300413093662135[65] = 0;
   out_7622300413093662135[66] = dt;
   out_7622300413093662135[67] = 0;
   out_7622300413093662135[68] = 0;
   out_7622300413093662135[69] = 0;
   out_7622300413093662135[70] = 0;
   out_7622300413093662135[71] = 0;
   out_7622300413093662135[72] = 0;
   out_7622300413093662135[73] = 0;
   out_7622300413093662135[74] = 0;
   out_7622300413093662135[75] = 0;
   out_7622300413093662135[76] = 1;
   out_7622300413093662135[77] = 0;
   out_7622300413093662135[78] = 0;
   out_7622300413093662135[79] = 0;
   out_7622300413093662135[80] = 0;
   out_7622300413093662135[81] = 0;
   out_7622300413093662135[82] = 0;
   out_7622300413093662135[83] = 0;
   out_7622300413093662135[84] = 0;
   out_7622300413093662135[85] = dt;
   out_7622300413093662135[86] = 0;
   out_7622300413093662135[87] = 0;
   out_7622300413093662135[88] = 0;
   out_7622300413093662135[89] = 0;
   out_7622300413093662135[90] = 0;
   out_7622300413093662135[91] = 0;
   out_7622300413093662135[92] = 0;
   out_7622300413093662135[93] = 0;
   out_7622300413093662135[94] = 0;
   out_7622300413093662135[95] = 1;
   out_7622300413093662135[96] = 0;
   out_7622300413093662135[97] = 0;
   out_7622300413093662135[98] = 0;
   out_7622300413093662135[99] = 0;
   out_7622300413093662135[100] = 0;
   out_7622300413093662135[101] = 0;
   out_7622300413093662135[102] = 0;
   out_7622300413093662135[103] = 0;
   out_7622300413093662135[104] = dt;
   out_7622300413093662135[105] = 0;
   out_7622300413093662135[106] = 0;
   out_7622300413093662135[107] = 0;
   out_7622300413093662135[108] = 0;
   out_7622300413093662135[109] = 0;
   out_7622300413093662135[110] = 0;
   out_7622300413093662135[111] = 0;
   out_7622300413093662135[112] = 0;
   out_7622300413093662135[113] = 0;
   out_7622300413093662135[114] = 1;
   out_7622300413093662135[115] = 0;
   out_7622300413093662135[116] = 0;
   out_7622300413093662135[117] = 0;
   out_7622300413093662135[118] = 0;
   out_7622300413093662135[119] = 0;
   out_7622300413093662135[120] = 0;
   out_7622300413093662135[121] = 0;
   out_7622300413093662135[122] = 0;
   out_7622300413093662135[123] = 0;
   out_7622300413093662135[124] = 0;
   out_7622300413093662135[125] = 0;
   out_7622300413093662135[126] = 0;
   out_7622300413093662135[127] = 0;
   out_7622300413093662135[128] = 0;
   out_7622300413093662135[129] = 0;
   out_7622300413093662135[130] = 0;
   out_7622300413093662135[131] = 0;
   out_7622300413093662135[132] = 0;
   out_7622300413093662135[133] = 1;
   out_7622300413093662135[134] = 0;
   out_7622300413093662135[135] = 0;
   out_7622300413093662135[136] = 0;
   out_7622300413093662135[137] = 0;
   out_7622300413093662135[138] = 0;
   out_7622300413093662135[139] = 0;
   out_7622300413093662135[140] = 0;
   out_7622300413093662135[141] = 0;
   out_7622300413093662135[142] = 0;
   out_7622300413093662135[143] = 0;
   out_7622300413093662135[144] = 0;
   out_7622300413093662135[145] = 0;
   out_7622300413093662135[146] = 0;
   out_7622300413093662135[147] = 0;
   out_7622300413093662135[148] = 0;
   out_7622300413093662135[149] = 0;
   out_7622300413093662135[150] = 0;
   out_7622300413093662135[151] = 0;
   out_7622300413093662135[152] = 1;
   out_7622300413093662135[153] = 0;
   out_7622300413093662135[154] = 0;
   out_7622300413093662135[155] = 0;
   out_7622300413093662135[156] = 0;
   out_7622300413093662135[157] = 0;
   out_7622300413093662135[158] = 0;
   out_7622300413093662135[159] = 0;
   out_7622300413093662135[160] = 0;
   out_7622300413093662135[161] = 0;
   out_7622300413093662135[162] = 0;
   out_7622300413093662135[163] = 0;
   out_7622300413093662135[164] = 0;
   out_7622300413093662135[165] = 0;
   out_7622300413093662135[166] = 0;
   out_7622300413093662135[167] = 0;
   out_7622300413093662135[168] = 0;
   out_7622300413093662135[169] = 0;
   out_7622300413093662135[170] = 0;
   out_7622300413093662135[171] = 1;
   out_7622300413093662135[172] = 0;
   out_7622300413093662135[173] = 0;
   out_7622300413093662135[174] = 0;
   out_7622300413093662135[175] = 0;
   out_7622300413093662135[176] = 0;
   out_7622300413093662135[177] = 0;
   out_7622300413093662135[178] = 0;
   out_7622300413093662135[179] = 0;
   out_7622300413093662135[180] = 0;
   out_7622300413093662135[181] = 0;
   out_7622300413093662135[182] = 0;
   out_7622300413093662135[183] = 0;
   out_7622300413093662135[184] = 0;
   out_7622300413093662135[185] = 0;
   out_7622300413093662135[186] = 0;
   out_7622300413093662135[187] = 0;
   out_7622300413093662135[188] = 0;
   out_7622300413093662135[189] = 0;
   out_7622300413093662135[190] = 1;
   out_7622300413093662135[191] = 0;
   out_7622300413093662135[192] = 0;
   out_7622300413093662135[193] = 0;
   out_7622300413093662135[194] = 0;
   out_7622300413093662135[195] = 0;
   out_7622300413093662135[196] = 0;
   out_7622300413093662135[197] = 0;
   out_7622300413093662135[198] = 0;
   out_7622300413093662135[199] = 0;
   out_7622300413093662135[200] = 0;
   out_7622300413093662135[201] = 0;
   out_7622300413093662135[202] = 0;
   out_7622300413093662135[203] = 0;
   out_7622300413093662135[204] = 0;
   out_7622300413093662135[205] = 0;
   out_7622300413093662135[206] = 0;
   out_7622300413093662135[207] = 0;
   out_7622300413093662135[208] = 0;
   out_7622300413093662135[209] = 1;
   out_7622300413093662135[210] = 0;
   out_7622300413093662135[211] = 0;
   out_7622300413093662135[212] = 0;
   out_7622300413093662135[213] = 0;
   out_7622300413093662135[214] = 0;
   out_7622300413093662135[215] = 0;
   out_7622300413093662135[216] = 0;
   out_7622300413093662135[217] = 0;
   out_7622300413093662135[218] = 0;
   out_7622300413093662135[219] = 0;
   out_7622300413093662135[220] = 0;
   out_7622300413093662135[221] = 0;
   out_7622300413093662135[222] = 0;
   out_7622300413093662135[223] = 0;
   out_7622300413093662135[224] = 0;
   out_7622300413093662135[225] = 0;
   out_7622300413093662135[226] = 0;
   out_7622300413093662135[227] = 0;
   out_7622300413093662135[228] = 1;
   out_7622300413093662135[229] = 0;
   out_7622300413093662135[230] = 0;
   out_7622300413093662135[231] = 0;
   out_7622300413093662135[232] = 0;
   out_7622300413093662135[233] = 0;
   out_7622300413093662135[234] = 0;
   out_7622300413093662135[235] = 0;
   out_7622300413093662135[236] = 0;
   out_7622300413093662135[237] = 0;
   out_7622300413093662135[238] = 0;
   out_7622300413093662135[239] = 0;
   out_7622300413093662135[240] = 0;
   out_7622300413093662135[241] = 0;
   out_7622300413093662135[242] = 0;
   out_7622300413093662135[243] = 0;
   out_7622300413093662135[244] = 0;
   out_7622300413093662135[245] = 0;
   out_7622300413093662135[246] = 0;
   out_7622300413093662135[247] = 1;
   out_7622300413093662135[248] = 0;
   out_7622300413093662135[249] = 0;
   out_7622300413093662135[250] = 0;
   out_7622300413093662135[251] = 0;
   out_7622300413093662135[252] = 0;
   out_7622300413093662135[253] = 0;
   out_7622300413093662135[254] = 0;
   out_7622300413093662135[255] = 0;
   out_7622300413093662135[256] = 0;
   out_7622300413093662135[257] = 0;
   out_7622300413093662135[258] = 0;
   out_7622300413093662135[259] = 0;
   out_7622300413093662135[260] = 0;
   out_7622300413093662135[261] = 0;
   out_7622300413093662135[262] = 0;
   out_7622300413093662135[263] = 0;
   out_7622300413093662135[264] = 0;
   out_7622300413093662135[265] = 0;
   out_7622300413093662135[266] = 1;
   out_7622300413093662135[267] = 0;
   out_7622300413093662135[268] = 0;
   out_7622300413093662135[269] = 0;
   out_7622300413093662135[270] = 0;
   out_7622300413093662135[271] = 0;
   out_7622300413093662135[272] = 0;
   out_7622300413093662135[273] = 0;
   out_7622300413093662135[274] = 0;
   out_7622300413093662135[275] = 0;
   out_7622300413093662135[276] = 0;
   out_7622300413093662135[277] = 0;
   out_7622300413093662135[278] = 0;
   out_7622300413093662135[279] = 0;
   out_7622300413093662135[280] = 0;
   out_7622300413093662135[281] = 0;
   out_7622300413093662135[282] = 0;
   out_7622300413093662135[283] = 0;
   out_7622300413093662135[284] = 0;
   out_7622300413093662135[285] = 1;
   out_7622300413093662135[286] = 0;
   out_7622300413093662135[287] = 0;
   out_7622300413093662135[288] = 0;
   out_7622300413093662135[289] = 0;
   out_7622300413093662135[290] = 0;
   out_7622300413093662135[291] = 0;
   out_7622300413093662135[292] = 0;
   out_7622300413093662135[293] = 0;
   out_7622300413093662135[294] = 0;
   out_7622300413093662135[295] = 0;
   out_7622300413093662135[296] = 0;
   out_7622300413093662135[297] = 0;
   out_7622300413093662135[298] = 0;
   out_7622300413093662135[299] = 0;
   out_7622300413093662135[300] = 0;
   out_7622300413093662135[301] = 0;
   out_7622300413093662135[302] = 0;
   out_7622300413093662135[303] = 0;
   out_7622300413093662135[304] = 1;
   out_7622300413093662135[305] = 0;
   out_7622300413093662135[306] = 0;
   out_7622300413093662135[307] = 0;
   out_7622300413093662135[308] = 0;
   out_7622300413093662135[309] = 0;
   out_7622300413093662135[310] = 0;
   out_7622300413093662135[311] = 0;
   out_7622300413093662135[312] = 0;
   out_7622300413093662135[313] = 0;
   out_7622300413093662135[314] = 0;
   out_7622300413093662135[315] = 0;
   out_7622300413093662135[316] = 0;
   out_7622300413093662135[317] = 0;
   out_7622300413093662135[318] = 0;
   out_7622300413093662135[319] = 0;
   out_7622300413093662135[320] = 0;
   out_7622300413093662135[321] = 0;
   out_7622300413093662135[322] = 0;
   out_7622300413093662135[323] = 1;
}
void h_4(double *state, double *unused, double *out_3773389396917783373) {
   out_3773389396917783373[0] = state[6] + state[9];
   out_3773389396917783373[1] = state[7] + state[10];
   out_3773389396917783373[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_6737208391502248447) {
   out_6737208391502248447[0] = 0;
   out_6737208391502248447[1] = 0;
   out_6737208391502248447[2] = 0;
   out_6737208391502248447[3] = 0;
   out_6737208391502248447[4] = 0;
   out_6737208391502248447[5] = 0;
   out_6737208391502248447[6] = 1;
   out_6737208391502248447[7] = 0;
   out_6737208391502248447[8] = 0;
   out_6737208391502248447[9] = 1;
   out_6737208391502248447[10] = 0;
   out_6737208391502248447[11] = 0;
   out_6737208391502248447[12] = 0;
   out_6737208391502248447[13] = 0;
   out_6737208391502248447[14] = 0;
   out_6737208391502248447[15] = 0;
   out_6737208391502248447[16] = 0;
   out_6737208391502248447[17] = 0;
   out_6737208391502248447[18] = 0;
   out_6737208391502248447[19] = 0;
   out_6737208391502248447[20] = 0;
   out_6737208391502248447[21] = 0;
   out_6737208391502248447[22] = 0;
   out_6737208391502248447[23] = 0;
   out_6737208391502248447[24] = 0;
   out_6737208391502248447[25] = 1;
   out_6737208391502248447[26] = 0;
   out_6737208391502248447[27] = 0;
   out_6737208391502248447[28] = 1;
   out_6737208391502248447[29] = 0;
   out_6737208391502248447[30] = 0;
   out_6737208391502248447[31] = 0;
   out_6737208391502248447[32] = 0;
   out_6737208391502248447[33] = 0;
   out_6737208391502248447[34] = 0;
   out_6737208391502248447[35] = 0;
   out_6737208391502248447[36] = 0;
   out_6737208391502248447[37] = 0;
   out_6737208391502248447[38] = 0;
   out_6737208391502248447[39] = 0;
   out_6737208391502248447[40] = 0;
   out_6737208391502248447[41] = 0;
   out_6737208391502248447[42] = 0;
   out_6737208391502248447[43] = 0;
   out_6737208391502248447[44] = 1;
   out_6737208391502248447[45] = 0;
   out_6737208391502248447[46] = 0;
   out_6737208391502248447[47] = 1;
   out_6737208391502248447[48] = 0;
   out_6737208391502248447[49] = 0;
   out_6737208391502248447[50] = 0;
   out_6737208391502248447[51] = 0;
   out_6737208391502248447[52] = 0;
   out_6737208391502248447[53] = 0;
}
void h_10(double *state, double *unused, double *out_1400728838140262320) {
   out_1400728838140262320[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_1400728838140262320[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_1400728838140262320[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_8006133557618840022) {
   out_8006133557618840022[0] = 0;
   out_8006133557618840022[1] = 9.8100000000000005*cos(state[1]);
   out_8006133557618840022[2] = 0;
   out_8006133557618840022[3] = 0;
   out_8006133557618840022[4] = -state[8];
   out_8006133557618840022[5] = state[7];
   out_8006133557618840022[6] = 0;
   out_8006133557618840022[7] = state[5];
   out_8006133557618840022[8] = -state[4];
   out_8006133557618840022[9] = 0;
   out_8006133557618840022[10] = 0;
   out_8006133557618840022[11] = 0;
   out_8006133557618840022[12] = 1;
   out_8006133557618840022[13] = 0;
   out_8006133557618840022[14] = 0;
   out_8006133557618840022[15] = 1;
   out_8006133557618840022[16] = 0;
   out_8006133557618840022[17] = 0;
   out_8006133557618840022[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_8006133557618840022[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_8006133557618840022[20] = 0;
   out_8006133557618840022[21] = state[8];
   out_8006133557618840022[22] = 0;
   out_8006133557618840022[23] = -state[6];
   out_8006133557618840022[24] = -state[5];
   out_8006133557618840022[25] = 0;
   out_8006133557618840022[26] = state[3];
   out_8006133557618840022[27] = 0;
   out_8006133557618840022[28] = 0;
   out_8006133557618840022[29] = 0;
   out_8006133557618840022[30] = 0;
   out_8006133557618840022[31] = 1;
   out_8006133557618840022[32] = 0;
   out_8006133557618840022[33] = 0;
   out_8006133557618840022[34] = 1;
   out_8006133557618840022[35] = 0;
   out_8006133557618840022[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_8006133557618840022[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_8006133557618840022[38] = 0;
   out_8006133557618840022[39] = -state[7];
   out_8006133557618840022[40] = state[6];
   out_8006133557618840022[41] = 0;
   out_8006133557618840022[42] = state[4];
   out_8006133557618840022[43] = -state[3];
   out_8006133557618840022[44] = 0;
   out_8006133557618840022[45] = 0;
   out_8006133557618840022[46] = 0;
   out_8006133557618840022[47] = 0;
   out_8006133557618840022[48] = 0;
   out_8006133557618840022[49] = 0;
   out_8006133557618840022[50] = 1;
   out_8006133557618840022[51] = 0;
   out_8006133557618840022[52] = 0;
   out_8006133557618840022[53] = 1;
}
void h_13(double *state, double *unused, double *out_6743657915002124092) {
   out_6743657915002124092[0] = state[3];
   out_6743657915002124092[1] = state[4];
   out_6743657915002124092[2] = state[5];
}
void H_13(double *state, double *unused, double *out_7875780218904779145) {
   out_7875780218904779145[0] = 0;
   out_7875780218904779145[1] = 0;
   out_7875780218904779145[2] = 0;
   out_7875780218904779145[3] = 1;
   out_7875780218904779145[4] = 0;
   out_7875780218904779145[5] = 0;
   out_7875780218904779145[6] = 0;
   out_7875780218904779145[7] = 0;
   out_7875780218904779145[8] = 0;
   out_7875780218904779145[9] = 0;
   out_7875780218904779145[10] = 0;
   out_7875780218904779145[11] = 0;
   out_7875780218904779145[12] = 0;
   out_7875780218904779145[13] = 0;
   out_7875780218904779145[14] = 0;
   out_7875780218904779145[15] = 0;
   out_7875780218904779145[16] = 0;
   out_7875780218904779145[17] = 0;
   out_7875780218904779145[18] = 0;
   out_7875780218904779145[19] = 0;
   out_7875780218904779145[20] = 0;
   out_7875780218904779145[21] = 0;
   out_7875780218904779145[22] = 1;
   out_7875780218904779145[23] = 0;
   out_7875780218904779145[24] = 0;
   out_7875780218904779145[25] = 0;
   out_7875780218904779145[26] = 0;
   out_7875780218904779145[27] = 0;
   out_7875780218904779145[28] = 0;
   out_7875780218904779145[29] = 0;
   out_7875780218904779145[30] = 0;
   out_7875780218904779145[31] = 0;
   out_7875780218904779145[32] = 0;
   out_7875780218904779145[33] = 0;
   out_7875780218904779145[34] = 0;
   out_7875780218904779145[35] = 0;
   out_7875780218904779145[36] = 0;
   out_7875780218904779145[37] = 0;
   out_7875780218904779145[38] = 0;
   out_7875780218904779145[39] = 0;
   out_7875780218904779145[40] = 0;
   out_7875780218904779145[41] = 1;
   out_7875780218904779145[42] = 0;
   out_7875780218904779145[43] = 0;
   out_7875780218904779145[44] = 0;
   out_7875780218904779145[45] = 0;
   out_7875780218904779145[46] = 0;
   out_7875780218904779145[47] = 0;
   out_7875780218904779145[48] = 0;
   out_7875780218904779145[49] = 0;
   out_7875780218904779145[50] = 0;
   out_7875780218904779145[51] = 0;
   out_7875780218904779145[52] = 0;
   out_7875780218904779145[53] = 0;
}
void h_14(double *state, double *unused, double *out_72437106472348557) {
   out_72437106472348557[0] = state[6];
   out_72437106472348557[1] = state[7];
   out_72437106472348557[2] = state[8];
}
void H_14(double *state, double *unused, double *out_8626747249911930873) {
   out_8626747249911930873[0] = 0;
   out_8626747249911930873[1] = 0;
   out_8626747249911930873[2] = 0;
   out_8626747249911930873[3] = 0;
   out_8626747249911930873[4] = 0;
   out_8626747249911930873[5] = 0;
   out_8626747249911930873[6] = 1;
   out_8626747249911930873[7] = 0;
   out_8626747249911930873[8] = 0;
   out_8626747249911930873[9] = 0;
   out_8626747249911930873[10] = 0;
   out_8626747249911930873[11] = 0;
   out_8626747249911930873[12] = 0;
   out_8626747249911930873[13] = 0;
   out_8626747249911930873[14] = 0;
   out_8626747249911930873[15] = 0;
   out_8626747249911930873[16] = 0;
   out_8626747249911930873[17] = 0;
   out_8626747249911930873[18] = 0;
   out_8626747249911930873[19] = 0;
   out_8626747249911930873[20] = 0;
   out_8626747249911930873[21] = 0;
   out_8626747249911930873[22] = 0;
   out_8626747249911930873[23] = 0;
   out_8626747249911930873[24] = 0;
   out_8626747249911930873[25] = 1;
   out_8626747249911930873[26] = 0;
   out_8626747249911930873[27] = 0;
   out_8626747249911930873[28] = 0;
   out_8626747249911930873[29] = 0;
   out_8626747249911930873[30] = 0;
   out_8626747249911930873[31] = 0;
   out_8626747249911930873[32] = 0;
   out_8626747249911930873[33] = 0;
   out_8626747249911930873[34] = 0;
   out_8626747249911930873[35] = 0;
   out_8626747249911930873[36] = 0;
   out_8626747249911930873[37] = 0;
   out_8626747249911930873[38] = 0;
   out_8626747249911930873[39] = 0;
   out_8626747249911930873[40] = 0;
   out_8626747249911930873[41] = 0;
   out_8626747249911930873[42] = 0;
   out_8626747249911930873[43] = 0;
   out_8626747249911930873[44] = 1;
   out_8626747249911930873[45] = 0;
   out_8626747249911930873[46] = 0;
   out_8626747249911930873[47] = 0;
   out_8626747249911930873[48] = 0;
   out_8626747249911930873[49] = 0;
   out_8626747249911930873[50] = 0;
   out_8626747249911930873[51] = 0;
   out_8626747249911930873[52] = 0;
   out_8626747249911930873[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_4192685534810622048) {
  err_fun(nom_x, delta_x, out_4192685534810622048);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5779284205001834883) {
  inv_err_fun(nom_x, true_x, out_5779284205001834883);
}
void pose_H_mod_fun(double *state, double *out_7935155873385146551) {
  H_mod_fun(state, out_7935155873385146551);
}
void pose_f_fun(double *state, double dt, double *out_1369858821784309025) {
  f_fun(state,  dt, out_1369858821784309025);
}
void pose_F_fun(double *state, double dt, double *out_7622300413093662135) {
  F_fun(state,  dt, out_7622300413093662135);
}
void pose_h_4(double *state, double *unused, double *out_3773389396917783373) {
  h_4(state, unused, out_3773389396917783373);
}
void pose_H_4(double *state, double *unused, double *out_6737208391502248447) {
  H_4(state, unused, out_6737208391502248447);
}
void pose_h_10(double *state, double *unused, double *out_1400728838140262320) {
  h_10(state, unused, out_1400728838140262320);
}
void pose_H_10(double *state, double *unused, double *out_8006133557618840022) {
  H_10(state, unused, out_8006133557618840022);
}
void pose_h_13(double *state, double *unused, double *out_6743657915002124092) {
  h_13(state, unused, out_6743657915002124092);
}
void pose_H_13(double *state, double *unused, double *out_7875780218904779145) {
  H_13(state, unused, out_7875780218904779145);
}
void pose_h_14(double *state, double *unused, double *out_72437106472348557) {
  h_14(state, unused, out_72437106472348557);
}
void pose_H_14(double *state, double *unused, double *out_8626747249911930873) {
  H_14(state, unused, out_8626747249911930873);
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
