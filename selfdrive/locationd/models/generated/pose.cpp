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
void err_fun(double *nom_x, double *delta_x, double *out_7345200414518154806) {
   out_7345200414518154806[0] = delta_x[0] + nom_x[0];
   out_7345200414518154806[1] = delta_x[1] + nom_x[1];
   out_7345200414518154806[2] = delta_x[2] + nom_x[2];
   out_7345200414518154806[3] = delta_x[3] + nom_x[3];
   out_7345200414518154806[4] = delta_x[4] + nom_x[4];
   out_7345200414518154806[5] = delta_x[5] + nom_x[5];
   out_7345200414518154806[6] = delta_x[6] + nom_x[6];
   out_7345200414518154806[7] = delta_x[7] + nom_x[7];
   out_7345200414518154806[8] = delta_x[8] + nom_x[8];
   out_7345200414518154806[9] = delta_x[9] + nom_x[9];
   out_7345200414518154806[10] = delta_x[10] + nom_x[10];
   out_7345200414518154806[11] = delta_x[11] + nom_x[11];
   out_7345200414518154806[12] = delta_x[12] + nom_x[12];
   out_7345200414518154806[13] = delta_x[13] + nom_x[13];
   out_7345200414518154806[14] = delta_x[14] + nom_x[14];
   out_7345200414518154806[15] = delta_x[15] + nom_x[15];
   out_7345200414518154806[16] = delta_x[16] + nom_x[16];
   out_7345200414518154806[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_283206327660277539) {
   out_283206327660277539[0] = -nom_x[0] + true_x[0];
   out_283206327660277539[1] = -nom_x[1] + true_x[1];
   out_283206327660277539[2] = -nom_x[2] + true_x[2];
   out_283206327660277539[3] = -nom_x[3] + true_x[3];
   out_283206327660277539[4] = -nom_x[4] + true_x[4];
   out_283206327660277539[5] = -nom_x[5] + true_x[5];
   out_283206327660277539[6] = -nom_x[6] + true_x[6];
   out_283206327660277539[7] = -nom_x[7] + true_x[7];
   out_283206327660277539[8] = -nom_x[8] + true_x[8];
   out_283206327660277539[9] = -nom_x[9] + true_x[9];
   out_283206327660277539[10] = -nom_x[10] + true_x[10];
   out_283206327660277539[11] = -nom_x[11] + true_x[11];
   out_283206327660277539[12] = -nom_x[12] + true_x[12];
   out_283206327660277539[13] = -nom_x[13] + true_x[13];
   out_283206327660277539[14] = -nom_x[14] + true_x[14];
   out_283206327660277539[15] = -nom_x[15] + true_x[15];
   out_283206327660277539[16] = -nom_x[16] + true_x[16];
   out_283206327660277539[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_2082368326476086218) {
   out_2082368326476086218[0] = 1.0;
   out_2082368326476086218[1] = 0.0;
   out_2082368326476086218[2] = 0.0;
   out_2082368326476086218[3] = 0.0;
   out_2082368326476086218[4] = 0.0;
   out_2082368326476086218[5] = 0.0;
   out_2082368326476086218[6] = 0.0;
   out_2082368326476086218[7] = 0.0;
   out_2082368326476086218[8] = 0.0;
   out_2082368326476086218[9] = 0.0;
   out_2082368326476086218[10] = 0.0;
   out_2082368326476086218[11] = 0.0;
   out_2082368326476086218[12] = 0.0;
   out_2082368326476086218[13] = 0.0;
   out_2082368326476086218[14] = 0.0;
   out_2082368326476086218[15] = 0.0;
   out_2082368326476086218[16] = 0.0;
   out_2082368326476086218[17] = 0.0;
   out_2082368326476086218[18] = 0.0;
   out_2082368326476086218[19] = 1.0;
   out_2082368326476086218[20] = 0.0;
   out_2082368326476086218[21] = 0.0;
   out_2082368326476086218[22] = 0.0;
   out_2082368326476086218[23] = 0.0;
   out_2082368326476086218[24] = 0.0;
   out_2082368326476086218[25] = 0.0;
   out_2082368326476086218[26] = 0.0;
   out_2082368326476086218[27] = 0.0;
   out_2082368326476086218[28] = 0.0;
   out_2082368326476086218[29] = 0.0;
   out_2082368326476086218[30] = 0.0;
   out_2082368326476086218[31] = 0.0;
   out_2082368326476086218[32] = 0.0;
   out_2082368326476086218[33] = 0.0;
   out_2082368326476086218[34] = 0.0;
   out_2082368326476086218[35] = 0.0;
   out_2082368326476086218[36] = 0.0;
   out_2082368326476086218[37] = 0.0;
   out_2082368326476086218[38] = 1.0;
   out_2082368326476086218[39] = 0.0;
   out_2082368326476086218[40] = 0.0;
   out_2082368326476086218[41] = 0.0;
   out_2082368326476086218[42] = 0.0;
   out_2082368326476086218[43] = 0.0;
   out_2082368326476086218[44] = 0.0;
   out_2082368326476086218[45] = 0.0;
   out_2082368326476086218[46] = 0.0;
   out_2082368326476086218[47] = 0.0;
   out_2082368326476086218[48] = 0.0;
   out_2082368326476086218[49] = 0.0;
   out_2082368326476086218[50] = 0.0;
   out_2082368326476086218[51] = 0.0;
   out_2082368326476086218[52] = 0.0;
   out_2082368326476086218[53] = 0.0;
   out_2082368326476086218[54] = 0.0;
   out_2082368326476086218[55] = 0.0;
   out_2082368326476086218[56] = 0.0;
   out_2082368326476086218[57] = 1.0;
   out_2082368326476086218[58] = 0.0;
   out_2082368326476086218[59] = 0.0;
   out_2082368326476086218[60] = 0.0;
   out_2082368326476086218[61] = 0.0;
   out_2082368326476086218[62] = 0.0;
   out_2082368326476086218[63] = 0.0;
   out_2082368326476086218[64] = 0.0;
   out_2082368326476086218[65] = 0.0;
   out_2082368326476086218[66] = 0.0;
   out_2082368326476086218[67] = 0.0;
   out_2082368326476086218[68] = 0.0;
   out_2082368326476086218[69] = 0.0;
   out_2082368326476086218[70] = 0.0;
   out_2082368326476086218[71] = 0.0;
   out_2082368326476086218[72] = 0.0;
   out_2082368326476086218[73] = 0.0;
   out_2082368326476086218[74] = 0.0;
   out_2082368326476086218[75] = 0.0;
   out_2082368326476086218[76] = 1.0;
   out_2082368326476086218[77] = 0.0;
   out_2082368326476086218[78] = 0.0;
   out_2082368326476086218[79] = 0.0;
   out_2082368326476086218[80] = 0.0;
   out_2082368326476086218[81] = 0.0;
   out_2082368326476086218[82] = 0.0;
   out_2082368326476086218[83] = 0.0;
   out_2082368326476086218[84] = 0.0;
   out_2082368326476086218[85] = 0.0;
   out_2082368326476086218[86] = 0.0;
   out_2082368326476086218[87] = 0.0;
   out_2082368326476086218[88] = 0.0;
   out_2082368326476086218[89] = 0.0;
   out_2082368326476086218[90] = 0.0;
   out_2082368326476086218[91] = 0.0;
   out_2082368326476086218[92] = 0.0;
   out_2082368326476086218[93] = 0.0;
   out_2082368326476086218[94] = 0.0;
   out_2082368326476086218[95] = 1.0;
   out_2082368326476086218[96] = 0.0;
   out_2082368326476086218[97] = 0.0;
   out_2082368326476086218[98] = 0.0;
   out_2082368326476086218[99] = 0.0;
   out_2082368326476086218[100] = 0.0;
   out_2082368326476086218[101] = 0.0;
   out_2082368326476086218[102] = 0.0;
   out_2082368326476086218[103] = 0.0;
   out_2082368326476086218[104] = 0.0;
   out_2082368326476086218[105] = 0.0;
   out_2082368326476086218[106] = 0.0;
   out_2082368326476086218[107] = 0.0;
   out_2082368326476086218[108] = 0.0;
   out_2082368326476086218[109] = 0.0;
   out_2082368326476086218[110] = 0.0;
   out_2082368326476086218[111] = 0.0;
   out_2082368326476086218[112] = 0.0;
   out_2082368326476086218[113] = 0.0;
   out_2082368326476086218[114] = 1.0;
   out_2082368326476086218[115] = 0.0;
   out_2082368326476086218[116] = 0.0;
   out_2082368326476086218[117] = 0.0;
   out_2082368326476086218[118] = 0.0;
   out_2082368326476086218[119] = 0.0;
   out_2082368326476086218[120] = 0.0;
   out_2082368326476086218[121] = 0.0;
   out_2082368326476086218[122] = 0.0;
   out_2082368326476086218[123] = 0.0;
   out_2082368326476086218[124] = 0.0;
   out_2082368326476086218[125] = 0.0;
   out_2082368326476086218[126] = 0.0;
   out_2082368326476086218[127] = 0.0;
   out_2082368326476086218[128] = 0.0;
   out_2082368326476086218[129] = 0.0;
   out_2082368326476086218[130] = 0.0;
   out_2082368326476086218[131] = 0.0;
   out_2082368326476086218[132] = 0.0;
   out_2082368326476086218[133] = 1.0;
   out_2082368326476086218[134] = 0.0;
   out_2082368326476086218[135] = 0.0;
   out_2082368326476086218[136] = 0.0;
   out_2082368326476086218[137] = 0.0;
   out_2082368326476086218[138] = 0.0;
   out_2082368326476086218[139] = 0.0;
   out_2082368326476086218[140] = 0.0;
   out_2082368326476086218[141] = 0.0;
   out_2082368326476086218[142] = 0.0;
   out_2082368326476086218[143] = 0.0;
   out_2082368326476086218[144] = 0.0;
   out_2082368326476086218[145] = 0.0;
   out_2082368326476086218[146] = 0.0;
   out_2082368326476086218[147] = 0.0;
   out_2082368326476086218[148] = 0.0;
   out_2082368326476086218[149] = 0.0;
   out_2082368326476086218[150] = 0.0;
   out_2082368326476086218[151] = 0.0;
   out_2082368326476086218[152] = 1.0;
   out_2082368326476086218[153] = 0.0;
   out_2082368326476086218[154] = 0.0;
   out_2082368326476086218[155] = 0.0;
   out_2082368326476086218[156] = 0.0;
   out_2082368326476086218[157] = 0.0;
   out_2082368326476086218[158] = 0.0;
   out_2082368326476086218[159] = 0.0;
   out_2082368326476086218[160] = 0.0;
   out_2082368326476086218[161] = 0.0;
   out_2082368326476086218[162] = 0.0;
   out_2082368326476086218[163] = 0.0;
   out_2082368326476086218[164] = 0.0;
   out_2082368326476086218[165] = 0.0;
   out_2082368326476086218[166] = 0.0;
   out_2082368326476086218[167] = 0.0;
   out_2082368326476086218[168] = 0.0;
   out_2082368326476086218[169] = 0.0;
   out_2082368326476086218[170] = 0.0;
   out_2082368326476086218[171] = 1.0;
   out_2082368326476086218[172] = 0.0;
   out_2082368326476086218[173] = 0.0;
   out_2082368326476086218[174] = 0.0;
   out_2082368326476086218[175] = 0.0;
   out_2082368326476086218[176] = 0.0;
   out_2082368326476086218[177] = 0.0;
   out_2082368326476086218[178] = 0.0;
   out_2082368326476086218[179] = 0.0;
   out_2082368326476086218[180] = 0.0;
   out_2082368326476086218[181] = 0.0;
   out_2082368326476086218[182] = 0.0;
   out_2082368326476086218[183] = 0.0;
   out_2082368326476086218[184] = 0.0;
   out_2082368326476086218[185] = 0.0;
   out_2082368326476086218[186] = 0.0;
   out_2082368326476086218[187] = 0.0;
   out_2082368326476086218[188] = 0.0;
   out_2082368326476086218[189] = 0.0;
   out_2082368326476086218[190] = 1.0;
   out_2082368326476086218[191] = 0.0;
   out_2082368326476086218[192] = 0.0;
   out_2082368326476086218[193] = 0.0;
   out_2082368326476086218[194] = 0.0;
   out_2082368326476086218[195] = 0.0;
   out_2082368326476086218[196] = 0.0;
   out_2082368326476086218[197] = 0.0;
   out_2082368326476086218[198] = 0.0;
   out_2082368326476086218[199] = 0.0;
   out_2082368326476086218[200] = 0.0;
   out_2082368326476086218[201] = 0.0;
   out_2082368326476086218[202] = 0.0;
   out_2082368326476086218[203] = 0.0;
   out_2082368326476086218[204] = 0.0;
   out_2082368326476086218[205] = 0.0;
   out_2082368326476086218[206] = 0.0;
   out_2082368326476086218[207] = 0.0;
   out_2082368326476086218[208] = 0.0;
   out_2082368326476086218[209] = 1.0;
   out_2082368326476086218[210] = 0.0;
   out_2082368326476086218[211] = 0.0;
   out_2082368326476086218[212] = 0.0;
   out_2082368326476086218[213] = 0.0;
   out_2082368326476086218[214] = 0.0;
   out_2082368326476086218[215] = 0.0;
   out_2082368326476086218[216] = 0.0;
   out_2082368326476086218[217] = 0.0;
   out_2082368326476086218[218] = 0.0;
   out_2082368326476086218[219] = 0.0;
   out_2082368326476086218[220] = 0.0;
   out_2082368326476086218[221] = 0.0;
   out_2082368326476086218[222] = 0.0;
   out_2082368326476086218[223] = 0.0;
   out_2082368326476086218[224] = 0.0;
   out_2082368326476086218[225] = 0.0;
   out_2082368326476086218[226] = 0.0;
   out_2082368326476086218[227] = 0.0;
   out_2082368326476086218[228] = 1.0;
   out_2082368326476086218[229] = 0.0;
   out_2082368326476086218[230] = 0.0;
   out_2082368326476086218[231] = 0.0;
   out_2082368326476086218[232] = 0.0;
   out_2082368326476086218[233] = 0.0;
   out_2082368326476086218[234] = 0.0;
   out_2082368326476086218[235] = 0.0;
   out_2082368326476086218[236] = 0.0;
   out_2082368326476086218[237] = 0.0;
   out_2082368326476086218[238] = 0.0;
   out_2082368326476086218[239] = 0.0;
   out_2082368326476086218[240] = 0.0;
   out_2082368326476086218[241] = 0.0;
   out_2082368326476086218[242] = 0.0;
   out_2082368326476086218[243] = 0.0;
   out_2082368326476086218[244] = 0.0;
   out_2082368326476086218[245] = 0.0;
   out_2082368326476086218[246] = 0.0;
   out_2082368326476086218[247] = 1.0;
   out_2082368326476086218[248] = 0.0;
   out_2082368326476086218[249] = 0.0;
   out_2082368326476086218[250] = 0.0;
   out_2082368326476086218[251] = 0.0;
   out_2082368326476086218[252] = 0.0;
   out_2082368326476086218[253] = 0.0;
   out_2082368326476086218[254] = 0.0;
   out_2082368326476086218[255] = 0.0;
   out_2082368326476086218[256] = 0.0;
   out_2082368326476086218[257] = 0.0;
   out_2082368326476086218[258] = 0.0;
   out_2082368326476086218[259] = 0.0;
   out_2082368326476086218[260] = 0.0;
   out_2082368326476086218[261] = 0.0;
   out_2082368326476086218[262] = 0.0;
   out_2082368326476086218[263] = 0.0;
   out_2082368326476086218[264] = 0.0;
   out_2082368326476086218[265] = 0.0;
   out_2082368326476086218[266] = 1.0;
   out_2082368326476086218[267] = 0.0;
   out_2082368326476086218[268] = 0.0;
   out_2082368326476086218[269] = 0.0;
   out_2082368326476086218[270] = 0.0;
   out_2082368326476086218[271] = 0.0;
   out_2082368326476086218[272] = 0.0;
   out_2082368326476086218[273] = 0.0;
   out_2082368326476086218[274] = 0.0;
   out_2082368326476086218[275] = 0.0;
   out_2082368326476086218[276] = 0.0;
   out_2082368326476086218[277] = 0.0;
   out_2082368326476086218[278] = 0.0;
   out_2082368326476086218[279] = 0.0;
   out_2082368326476086218[280] = 0.0;
   out_2082368326476086218[281] = 0.0;
   out_2082368326476086218[282] = 0.0;
   out_2082368326476086218[283] = 0.0;
   out_2082368326476086218[284] = 0.0;
   out_2082368326476086218[285] = 1.0;
   out_2082368326476086218[286] = 0.0;
   out_2082368326476086218[287] = 0.0;
   out_2082368326476086218[288] = 0.0;
   out_2082368326476086218[289] = 0.0;
   out_2082368326476086218[290] = 0.0;
   out_2082368326476086218[291] = 0.0;
   out_2082368326476086218[292] = 0.0;
   out_2082368326476086218[293] = 0.0;
   out_2082368326476086218[294] = 0.0;
   out_2082368326476086218[295] = 0.0;
   out_2082368326476086218[296] = 0.0;
   out_2082368326476086218[297] = 0.0;
   out_2082368326476086218[298] = 0.0;
   out_2082368326476086218[299] = 0.0;
   out_2082368326476086218[300] = 0.0;
   out_2082368326476086218[301] = 0.0;
   out_2082368326476086218[302] = 0.0;
   out_2082368326476086218[303] = 0.0;
   out_2082368326476086218[304] = 1.0;
   out_2082368326476086218[305] = 0.0;
   out_2082368326476086218[306] = 0.0;
   out_2082368326476086218[307] = 0.0;
   out_2082368326476086218[308] = 0.0;
   out_2082368326476086218[309] = 0.0;
   out_2082368326476086218[310] = 0.0;
   out_2082368326476086218[311] = 0.0;
   out_2082368326476086218[312] = 0.0;
   out_2082368326476086218[313] = 0.0;
   out_2082368326476086218[314] = 0.0;
   out_2082368326476086218[315] = 0.0;
   out_2082368326476086218[316] = 0.0;
   out_2082368326476086218[317] = 0.0;
   out_2082368326476086218[318] = 0.0;
   out_2082368326476086218[319] = 0.0;
   out_2082368326476086218[320] = 0.0;
   out_2082368326476086218[321] = 0.0;
   out_2082368326476086218[322] = 0.0;
   out_2082368326476086218[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_5163268778687305893) {
   out_5163268778687305893[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_5163268778687305893[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_5163268778687305893[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_5163268778687305893[3] = dt*state[12] + state[3];
   out_5163268778687305893[4] = dt*state[13] + state[4];
   out_5163268778687305893[5] = dt*state[14] + state[5];
   out_5163268778687305893[6] = state[6];
   out_5163268778687305893[7] = state[7];
   out_5163268778687305893[8] = state[8];
   out_5163268778687305893[9] = state[9];
   out_5163268778687305893[10] = state[10];
   out_5163268778687305893[11] = state[11];
   out_5163268778687305893[12] = state[12];
   out_5163268778687305893[13] = state[13];
   out_5163268778687305893[14] = state[14];
   out_5163268778687305893[15] = state[15];
   out_5163268778687305893[16] = state[16];
   out_5163268778687305893[17] = state[17];
}
void F_fun(double *state, double dt, double *out_2262566197447778253) {
   out_2262566197447778253[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2262566197447778253[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2262566197447778253[2] = 0;
   out_2262566197447778253[3] = 0;
   out_2262566197447778253[4] = 0;
   out_2262566197447778253[5] = 0;
   out_2262566197447778253[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2262566197447778253[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2262566197447778253[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_2262566197447778253[9] = 0;
   out_2262566197447778253[10] = 0;
   out_2262566197447778253[11] = 0;
   out_2262566197447778253[12] = 0;
   out_2262566197447778253[13] = 0;
   out_2262566197447778253[14] = 0;
   out_2262566197447778253[15] = 0;
   out_2262566197447778253[16] = 0;
   out_2262566197447778253[17] = 0;
   out_2262566197447778253[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2262566197447778253[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2262566197447778253[20] = 0;
   out_2262566197447778253[21] = 0;
   out_2262566197447778253[22] = 0;
   out_2262566197447778253[23] = 0;
   out_2262566197447778253[24] = 0;
   out_2262566197447778253[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2262566197447778253[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_2262566197447778253[27] = 0;
   out_2262566197447778253[28] = 0;
   out_2262566197447778253[29] = 0;
   out_2262566197447778253[30] = 0;
   out_2262566197447778253[31] = 0;
   out_2262566197447778253[32] = 0;
   out_2262566197447778253[33] = 0;
   out_2262566197447778253[34] = 0;
   out_2262566197447778253[35] = 0;
   out_2262566197447778253[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2262566197447778253[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2262566197447778253[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2262566197447778253[39] = 0;
   out_2262566197447778253[40] = 0;
   out_2262566197447778253[41] = 0;
   out_2262566197447778253[42] = 0;
   out_2262566197447778253[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2262566197447778253[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_2262566197447778253[45] = 0;
   out_2262566197447778253[46] = 0;
   out_2262566197447778253[47] = 0;
   out_2262566197447778253[48] = 0;
   out_2262566197447778253[49] = 0;
   out_2262566197447778253[50] = 0;
   out_2262566197447778253[51] = 0;
   out_2262566197447778253[52] = 0;
   out_2262566197447778253[53] = 0;
   out_2262566197447778253[54] = 0;
   out_2262566197447778253[55] = 0;
   out_2262566197447778253[56] = 0;
   out_2262566197447778253[57] = 1;
   out_2262566197447778253[58] = 0;
   out_2262566197447778253[59] = 0;
   out_2262566197447778253[60] = 0;
   out_2262566197447778253[61] = 0;
   out_2262566197447778253[62] = 0;
   out_2262566197447778253[63] = 0;
   out_2262566197447778253[64] = 0;
   out_2262566197447778253[65] = 0;
   out_2262566197447778253[66] = dt;
   out_2262566197447778253[67] = 0;
   out_2262566197447778253[68] = 0;
   out_2262566197447778253[69] = 0;
   out_2262566197447778253[70] = 0;
   out_2262566197447778253[71] = 0;
   out_2262566197447778253[72] = 0;
   out_2262566197447778253[73] = 0;
   out_2262566197447778253[74] = 0;
   out_2262566197447778253[75] = 0;
   out_2262566197447778253[76] = 1;
   out_2262566197447778253[77] = 0;
   out_2262566197447778253[78] = 0;
   out_2262566197447778253[79] = 0;
   out_2262566197447778253[80] = 0;
   out_2262566197447778253[81] = 0;
   out_2262566197447778253[82] = 0;
   out_2262566197447778253[83] = 0;
   out_2262566197447778253[84] = 0;
   out_2262566197447778253[85] = dt;
   out_2262566197447778253[86] = 0;
   out_2262566197447778253[87] = 0;
   out_2262566197447778253[88] = 0;
   out_2262566197447778253[89] = 0;
   out_2262566197447778253[90] = 0;
   out_2262566197447778253[91] = 0;
   out_2262566197447778253[92] = 0;
   out_2262566197447778253[93] = 0;
   out_2262566197447778253[94] = 0;
   out_2262566197447778253[95] = 1;
   out_2262566197447778253[96] = 0;
   out_2262566197447778253[97] = 0;
   out_2262566197447778253[98] = 0;
   out_2262566197447778253[99] = 0;
   out_2262566197447778253[100] = 0;
   out_2262566197447778253[101] = 0;
   out_2262566197447778253[102] = 0;
   out_2262566197447778253[103] = 0;
   out_2262566197447778253[104] = dt;
   out_2262566197447778253[105] = 0;
   out_2262566197447778253[106] = 0;
   out_2262566197447778253[107] = 0;
   out_2262566197447778253[108] = 0;
   out_2262566197447778253[109] = 0;
   out_2262566197447778253[110] = 0;
   out_2262566197447778253[111] = 0;
   out_2262566197447778253[112] = 0;
   out_2262566197447778253[113] = 0;
   out_2262566197447778253[114] = 1;
   out_2262566197447778253[115] = 0;
   out_2262566197447778253[116] = 0;
   out_2262566197447778253[117] = 0;
   out_2262566197447778253[118] = 0;
   out_2262566197447778253[119] = 0;
   out_2262566197447778253[120] = 0;
   out_2262566197447778253[121] = 0;
   out_2262566197447778253[122] = 0;
   out_2262566197447778253[123] = 0;
   out_2262566197447778253[124] = 0;
   out_2262566197447778253[125] = 0;
   out_2262566197447778253[126] = 0;
   out_2262566197447778253[127] = 0;
   out_2262566197447778253[128] = 0;
   out_2262566197447778253[129] = 0;
   out_2262566197447778253[130] = 0;
   out_2262566197447778253[131] = 0;
   out_2262566197447778253[132] = 0;
   out_2262566197447778253[133] = 1;
   out_2262566197447778253[134] = 0;
   out_2262566197447778253[135] = 0;
   out_2262566197447778253[136] = 0;
   out_2262566197447778253[137] = 0;
   out_2262566197447778253[138] = 0;
   out_2262566197447778253[139] = 0;
   out_2262566197447778253[140] = 0;
   out_2262566197447778253[141] = 0;
   out_2262566197447778253[142] = 0;
   out_2262566197447778253[143] = 0;
   out_2262566197447778253[144] = 0;
   out_2262566197447778253[145] = 0;
   out_2262566197447778253[146] = 0;
   out_2262566197447778253[147] = 0;
   out_2262566197447778253[148] = 0;
   out_2262566197447778253[149] = 0;
   out_2262566197447778253[150] = 0;
   out_2262566197447778253[151] = 0;
   out_2262566197447778253[152] = 1;
   out_2262566197447778253[153] = 0;
   out_2262566197447778253[154] = 0;
   out_2262566197447778253[155] = 0;
   out_2262566197447778253[156] = 0;
   out_2262566197447778253[157] = 0;
   out_2262566197447778253[158] = 0;
   out_2262566197447778253[159] = 0;
   out_2262566197447778253[160] = 0;
   out_2262566197447778253[161] = 0;
   out_2262566197447778253[162] = 0;
   out_2262566197447778253[163] = 0;
   out_2262566197447778253[164] = 0;
   out_2262566197447778253[165] = 0;
   out_2262566197447778253[166] = 0;
   out_2262566197447778253[167] = 0;
   out_2262566197447778253[168] = 0;
   out_2262566197447778253[169] = 0;
   out_2262566197447778253[170] = 0;
   out_2262566197447778253[171] = 1;
   out_2262566197447778253[172] = 0;
   out_2262566197447778253[173] = 0;
   out_2262566197447778253[174] = 0;
   out_2262566197447778253[175] = 0;
   out_2262566197447778253[176] = 0;
   out_2262566197447778253[177] = 0;
   out_2262566197447778253[178] = 0;
   out_2262566197447778253[179] = 0;
   out_2262566197447778253[180] = 0;
   out_2262566197447778253[181] = 0;
   out_2262566197447778253[182] = 0;
   out_2262566197447778253[183] = 0;
   out_2262566197447778253[184] = 0;
   out_2262566197447778253[185] = 0;
   out_2262566197447778253[186] = 0;
   out_2262566197447778253[187] = 0;
   out_2262566197447778253[188] = 0;
   out_2262566197447778253[189] = 0;
   out_2262566197447778253[190] = 1;
   out_2262566197447778253[191] = 0;
   out_2262566197447778253[192] = 0;
   out_2262566197447778253[193] = 0;
   out_2262566197447778253[194] = 0;
   out_2262566197447778253[195] = 0;
   out_2262566197447778253[196] = 0;
   out_2262566197447778253[197] = 0;
   out_2262566197447778253[198] = 0;
   out_2262566197447778253[199] = 0;
   out_2262566197447778253[200] = 0;
   out_2262566197447778253[201] = 0;
   out_2262566197447778253[202] = 0;
   out_2262566197447778253[203] = 0;
   out_2262566197447778253[204] = 0;
   out_2262566197447778253[205] = 0;
   out_2262566197447778253[206] = 0;
   out_2262566197447778253[207] = 0;
   out_2262566197447778253[208] = 0;
   out_2262566197447778253[209] = 1;
   out_2262566197447778253[210] = 0;
   out_2262566197447778253[211] = 0;
   out_2262566197447778253[212] = 0;
   out_2262566197447778253[213] = 0;
   out_2262566197447778253[214] = 0;
   out_2262566197447778253[215] = 0;
   out_2262566197447778253[216] = 0;
   out_2262566197447778253[217] = 0;
   out_2262566197447778253[218] = 0;
   out_2262566197447778253[219] = 0;
   out_2262566197447778253[220] = 0;
   out_2262566197447778253[221] = 0;
   out_2262566197447778253[222] = 0;
   out_2262566197447778253[223] = 0;
   out_2262566197447778253[224] = 0;
   out_2262566197447778253[225] = 0;
   out_2262566197447778253[226] = 0;
   out_2262566197447778253[227] = 0;
   out_2262566197447778253[228] = 1;
   out_2262566197447778253[229] = 0;
   out_2262566197447778253[230] = 0;
   out_2262566197447778253[231] = 0;
   out_2262566197447778253[232] = 0;
   out_2262566197447778253[233] = 0;
   out_2262566197447778253[234] = 0;
   out_2262566197447778253[235] = 0;
   out_2262566197447778253[236] = 0;
   out_2262566197447778253[237] = 0;
   out_2262566197447778253[238] = 0;
   out_2262566197447778253[239] = 0;
   out_2262566197447778253[240] = 0;
   out_2262566197447778253[241] = 0;
   out_2262566197447778253[242] = 0;
   out_2262566197447778253[243] = 0;
   out_2262566197447778253[244] = 0;
   out_2262566197447778253[245] = 0;
   out_2262566197447778253[246] = 0;
   out_2262566197447778253[247] = 1;
   out_2262566197447778253[248] = 0;
   out_2262566197447778253[249] = 0;
   out_2262566197447778253[250] = 0;
   out_2262566197447778253[251] = 0;
   out_2262566197447778253[252] = 0;
   out_2262566197447778253[253] = 0;
   out_2262566197447778253[254] = 0;
   out_2262566197447778253[255] = 0;
   out_2262566197447778253[256] = 0;
   out_2262566197447778253[257] = 0;
   out_2262566197447778253[258] = 0;
   out_2262566197447778253[259] = 0;
   out_2262566197447778253[260] = 0;
   out_2262566197447778253[261] = 0;
   out_2262566197447778253[262] = 0;
   out_2262566197447778253[263] = 0;
   out_2262566197447778253[264] = 0;
   out_2262566197447778253[265] = 0;
   out_2262566197447778253[266] = 1;
   out_2262566197447778253[267] = 0;
   out_2262566197447778253[268] = 0;
   out_2262566197447778253[269] = 0;
   out_2262566197447778253[270] = 0;
   out_2262566197447778253[271] = 0;
   out_2262566197447778253[272] = 0;
   out_2262566197447778253[273] = 0;
   out_2262566197447778253[274] = 0;
   out_2262566197447778253[275] = 0;
   out_2262566197447778253[276] = 0;
   out_2262566197447778253[277] = 0;
   out_2262566197447778253[278] = 0;
   out_2262566197447778253[279] = 0;
   out_2262566197447778253[280] = 0;
   out_2262566197447778253[281] = 0;
   out_2262566197447778253[282] = 0;
   out_2262566197447778253[283] = 0;
   out_2262566197447778253[284] = 0;
   out_2262566197447778253[285] = 1;
   out_2262566197447778253[286] = 0;
   out_2262566197447778253[287] = 0;
   out_2262566197447778253[288] = 0;
   out_2262566197447778253[289] = 0;
   out_2262566197447778253[290] = 0;
   out_2262566197447778253[291] = 0;
   out_2262566197447778253[292] = 0;
   out_2262566197447778253[293] = 0;
   out_2262566197447778253[294] = 0;
   out_2262566197447778253[295] = 0;
   out_2262566197447778253[296] = 0;
   out_2262566197447778253[297] = 0;
   out_2262566197447778253[298] = 0;
   out_2262566197447778253[299] = 0;
   out_2262566197447778253[300] = 0;
   out_2262566197447778253[301] = 0;
   out_2262566197447778253[302] = 0;
   out_2262566197447778253[303] = 0;
   out_2262566197447778253[304] = 1;
   out_2262566197447778253[305] = 0;
   out_2262566197447778253[306] = 0;
   out_2262566197447778253[307] = 0;
   out_2262566197447778253[308] = 0;
   out_2262566197447778253[309] = 0;
   out_2262566197447778253[310] = 0;
   out_2262566197447778253[311] = 0;
   out_2262566197447778253[312] = 0;
   out_2262566197447778253[313] = 0;
   out_2262566197447778253[314] = 0;
   out_2262566197447778253[315] = 0;
   out_2262566197447778253[316] = 0;
   out_2262566197447778253[317] = 0;
   out_2262566197447778253[318] = 0;
   out_2262566197447778253[319] = 0;
   out_2262566197447778253[320] = 0;
   out_2262566197447778253[321] = 0;
   out_2262566197447778253[322] = 0;
   out_2262566197447778253[323] = 1;
}
void h_4(double *state, double *unused, double *out_7434247557157613397) {
   out_7434247557157613397[0] = state[6] + state[9];
   out_7434247557157613397[1] = state[7] + state[10];
   out_7434247557157613397[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_5932809187836661446) {
   out_5932809187836661446[0] = 0;
   out_5932809187836661446[1] = 0;
   out_5932809187836661446[2] = 0;
   out_5932809187836661446[3] = 0;
   out_5932809187836661446[4] = 0;
   out_5932809187836661446[5] = 0;
   out_5932809187836661446[6] = 1;
   out_5932809187836661446[7] = 0;
   out_5932809187836661446[8] = 0;
   out_5932809187836661446[9] = 1;
   out_5932809187836661446[10] = 0;
   out_5932809187836661446[11] = 0;
   out_5932809187836661446[12] = 0;
   out_5932809187836661446[13] = 0;
   out_5932809187836661446[14] = 0;
   out_5932809187836661446[15] = 0;
   out_5932809187836661446[16] = 0;
   out_5932809187836661446[17] = 0;
   out_5932809187836661446[18] = 0;
   out_5932809187836661446[19] = 0;
   out_5932809187836661446[20] = 0;
   out_5932809187836661446[21] = 0;
   out_5932809187836661446[22] = 0;
   out_5932809187836661446[23] = 0;
   out_5932809187836661446[24] = 0;
   out_5932809187836661446[25] = 1;
   out_5932809187836661446[26] = 0;
   out_5932809187836661446[27] = 0;
   out_5932809187836661446[28] = 1;
   out_5932809187836661446[29] = 0;
   out_5932809187836661446[30] = 0;
   out_5932809187836661446[31] = 0;
   out_5932809187836661446[32] = 0;
   out_5932809187836661446[33] = 0;
   out_5932809187836661446[34] = 0;
   out_5932809187836661446[35] = 0;
   out_5932809187836661446[36] = 0;
   out_5932809187836661446[37] = 0;
   out_5932809187836661446[38] = 0;
   out_5932809187836661446[39] = 0;
   out_5932809187836661446[40] = 0;
   out_5932809187836661446[41] = 0;
   out_5932809187836661446[42] = 0;
   out_5932809187836661446[43] = 0;
   out_5932809187836661446[44] = 1;
   out_5932809187836661446[45] = 0;
   out_5932809187836661446[46] = 0;
   out_5932809187836661446[47] = 1;
   out_5932809187836661446[48] = 0;
   out_5932809187836661446[49] = 0;
   out_5932809187836661446[50] = 0;
   out_5932809187836661446[51] = 0;
   out_5932809187836661446[52] = 0;
   out_5932809187836661446[53] = 0;
}
void h_10(double *state, double *unused, double *out_7247789716920531684) {
   out_7247789716920531684[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_7247789716920531684[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_7247789716920531684[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_5259832045949180196) {
   out_5259832045949180196[0] = 0;
   out_5259832045949180196[1] = 9.8100000000000005*cos(state[1]);
   out_5259832045949180196[2] = 0;
   out_5259832045949180196[3] = 0;
   out_5259832045949180196[4] = -state[8];
   out_5259832045949180196[5] = state[7];
   out_5259832045949180196[6] = 0;
   out_5259832045949180196[7] = state[5];
   out_5259832045949180196[8] = -state[4];
   out_5259832045949180196[9] = 0;
   out_5259832045949180196[10] = 0;
   out_5259832045949180196[11] = 0;
   out_5259832045949180196[12] = 1;
   out_5259832045949180196[13] = 0;
   out_5259832045949180196[14] = 0;
   out_5259832045949180196[15] = 1;
   out_5259832045949180196[16] = 0;
   out_5259832045949180196[17] = 0;
   out_5259832045949180196[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_5259832045949180196[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_5259832045949180196[20] = 0;
   out_5259832045949180196[21] = state[8];
   out_5259832045949180196[22] = 0;
   out_5259832045949180196[23] = -state[6];
   out_5259832045949180196[24] = -state[5];
   out_5259832045949180196[25] = 0;
   out_5259832045949180196[26] = state[3];
   out_5259832045949180196[27] = 0;
   out_5259832045949180196[28] = 0;
   out_5259832045949180196[29] = 0;
   out_5259832045949180196[30] = 0;
   out_5259832045949180196[31] = 1;
   out_5259832045949180196[32] = 0;
   out_5259832045949180196[33] = 0;
   out_5259832045949180196[34] = 1;
   out_5259832045949180196[35] = 0;
   out_5259832045949180196[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_5259832045949180196[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_5259832045949180196[38] = 0;
   out_5259832045949180196[39] = -state[7];
   out_5259832045949180196[40] = state[6];
   out_5259832045949180196[41] = 0;
   out_5259832045949180196[42] = state[4];
   out_5259832045949180196[43] = -state[3];
   out_5259832045949180196[44] = 0;
   out_5259832045949180196[45] = 0;
   out_5259832045949180196[46] = 0;
   out_5259832045949180196[47] = 0;
   out_5259832045949180196[48] = 0;
   out_5259832045949180196[49] = 0;
   out_5259832045949180196[50] = 1;
   out_5259832045949180196[51] = 0;
   out_5259832045949180196[52] = 0;
   out_5259832045949180196[53] = 1;
}
void h_13(double *state, double *unused, double *out_7157875501104788200) {
   out_7157875501104788200[0] = state[3];
   out_7157875501104788200[1] = state[4];
   out_7157875501104788200[2] = state[5];
}
void H_13(double *state, double *unused, double *out_4903303677556189241) {
   out_4903303677556189241[0] = 0;
   out_4903303677556189241[1] = 0;
   out_4903303677556189241[2] = 0;
   out_4903303677556189241[3] = 1;
   out_4903303677556189241[4] = 0;
   out_4903303677556189241[5] = 0;
   out_4903303677556189241[6] = 0;
   out_4903303677556189241[7] = 0;
   out_4903303677556189241[8] = 0;
   out_4903303677556189241[9] = 0;
   out_4903303677556189241[10] = 0;
   out_4903303677556189241[11] = 0;
   out_4903303677556189241[12] = 0;
   out_4903303677556189241[13] = 0;
   out_4903303677556189241[14] = 0;
   out_4903303677556189241[15] = 0;
   out_4903303677556189241[16] = 0;
   out_4903303677556189241[17] = 0;
   out_4903303677556189241[18] = 0;
   out_4903303677556189241[19] = 0;
   out_4903303677556189241[20] = 0;
   out_4903303677556189241[21] = 0;
   out_4903303677556189241[22] = 1;
   out_4903303677556189241[23] = 0;
   out_4903303677556189241[24] = 0;
   out_4903303677556189241[25] = 0;
   out_4903303677556189241[26] = 0;
   out_4903303677556189241[27] = 0;
   out_4903303677556189241[28] = 0;
   out_4903303677556189241[29] = 0;
   out_4903303677556189241[30] = 0;
   out_4903303677556189241[31] = 0;
   out_4903303677556189241[32] = 0;
   out_4903303677556189241[33] = 0;
   out_4903303677556189241[34] = 0;
   out_4903303677556189241[35] = 0;
   out_4903303677556189241[36] = 0;
   out_4903303677556189241[37] = 0;
   out_4903303677556189241[38] = 0;
   out_4903303677556189241[39] = 0;
   out_4903303677556189241[40] = 0;
   out_4903303677556189241[41] = 1;
   out_4903303677556189241[42] = 0;
   out_4903303677556189241[43] = 0;
   out_4903303677556189241[44] = 0;
   out_4903303677556189241[45] = 0;
   out_4903303677556189241[46] = 0;
   out_4903303677556189241[47] = 0;
   out_4903303677556189241[48] = 0;
   out_4903303677556189241[49] = 0;
   out_4903303677556189241[50] = 0;
   out_4903303677556189241[51] = 0;
   out_4903303677556189241[52] = 0;
   out_4903303677556189241[53] = 0;
}
void h_14(double *state, double *unused, double *out_3063669227662560702) {
   out_3063669227662560702[0] = state[6];
   out_3063669227662560702[1] = state[7];
   out_3063669227662560702[2] = state[8];
}
void H_14(double *state, double *unused, double *out_8550694029533405641) {
   out_8550694029533405641[0] = 0;
   out_8550694029533405641[1] = 0;
   out_8550694029533405641[2] = 0;
   out_8550694029533405641[3] = 0;
   out_8550694029533405641[4] = 0;
   out_8550694029533405641[5] = 0;
   out_8550694029533405641[6] = 1;
   out_8550694029533405641[7] = 0;
   out_8550694029533405641[8] = 0;
   out_8550694029533405641[9] = 0;
   out_8550694029533405641[10] = 0;
   out_8550694029533405641[11] = 0;
   out_8550694029533405641[12] = 0;
   out_8550694029533405641[13] = 0;
   out_8550694029533405641[14] = 0;
   out_8550694029533405641[15] = 0;
   out_8550694029533405641[16] = 0;
   out_8550694029533405641[17] = 0;
   out_8550694029533405641[18] = 0;
   out_8550694029533405641[19] = 0;
   out_8550694029533405641[20] = 0;
   out_8550694029533405641[21] = 0;
   out_8550694029533405641[22] = 0;
   out_8550694029533405641[23] = 0;
   out_8550694029533405641[24] = 0;
   out_8550694029533405641[25] = 1;
   out_8550694029533405641[26] = 0;
   out_8550694029533405641[27] = 0;
   out_8550694029533405641[28] = 0;
   out_8550694029533405641[29] = 0;
   out_8550694029533405641[30] = 0;
   out_8550694029533405641[31] = 0;
   out_8550694029533405641[32] = 0;
   out_8550694029533405641[33] = 0;
   out_8550694029533405641[34] = 0;
   out_8550694029533405641[35] = 0;
   out_8550694029533405641[36] = 0;
   out_8550694029533405641[37] = 0;
   out_8550694029533405641[38] = 0;
   out_8550694029533405641[39] = 0;
   out_8550694029533405641[40] = 0;
   out_8550694029533405641[41] = 0;
   out_8550694029533405641[42] = 0;
   out_8550694029533405641[43] = 0;
   out_8550694029533405641[44] = 1;
   out_8550694029533405641[45] = 0;
   out_8550694029533405641[46] = 0;
   out_8550694029533405641[47] = 0;
   out_8550694029533405641[48] = 0;
   out_8550694029533405641[49] = 0;
   out_8550694029533405641[50] = 0;
   out_8550694029533405641[51] = 0;
   out_8550694029533405641[52] = 0;
   out_8550694029533405641[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_7345200414518154806) {
  err_fun(nom_x, delta_x, out_7345200414518154806);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_283206327660277539) {
  inv_err_fun(nom_x, true_x, out_283206327660277539);
}
void pose_H_mod_fun(double *state, double *out_2082368326476086218) {
  H_mod_fun(state, out_2082368326476086218);
}
void pose_f_fun(double *state, double dt, double *out_5163268778687305893) {
  f_fun(state,  dt, out_5163268778687305893);
}
void pose_F_fun(double *state, double dt, double *out_2262566197447778253) {
  F_fun(state,  dt, out_2262566197447778253);
}
void pose_h_4(double *state, double *unused, double *out_7434247557157613397) {
  h_4(state, unused, out_7434247557157613397);
}
void pose_H_4(double *state, double *unused, double *out_5932809187836661446) {
  H_4(state, unused, out_5932809187836661446);
}
void pose_h_10(double *state, double *unused, double *out_7247789716920531684) {
  h_10(state, unused, out_7247789716920531684);
}
void pose_H_10(double *state, double *unused, double *out_5259832045949180196) {
  H_10(state, unused, out_5259832045949180196);
}
void pose_h_13(double *state, double *unused, double *out_7157875501104788200) {
  h_13(state, unused, out_7157875501104788200);
}
void pose_H_13(double *state, double *unused, double *out_4903303677556189241) {
  H_13(state, unused, out_4903303677556189241);
}
void pose_h_14(double *state, double *unused, double *out_3063669227662560702) {
  h_14(state, unused, out_3063669227662560702);
}
void pose_H_14(double *state, double *unused, double *out_8550694029533405641) {
  H_14(state, unused, out_8550694029533405641);
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
