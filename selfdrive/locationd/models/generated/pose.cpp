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
void err_fun(double *nom_x, double *delta_x, double *out_3891534798634327778) {
   out_3891534798634327778[0] = delta_x[0] + nom_x[0];
   out_3891534798634327778[1] = delta_x[1] + nom_x[1];
   out_3891534798634327778[2] = delta_x[2] + nom_x[2];
   out_3891534798634327778[3] = delta_x[3] + nom_x[3];
   out_3891534798634327778[4] = delta_x[4] + nom_x[4];
   out_3891534798634327778[5] = delta_x[5] + nom_x[5];
   out_3891534798634327778[6] = delta_x[6] + nom_x[6];
   out_3891534798634327778[7] = delta_x[7] + nom_x[7];
   out_3891534798634327778[8] = delta_x[8] + nom_x[8];
   out_3891534798634327778[9] = delta_x[9] + nom_x[9];
   out_3891534798634327778[10] = delta_x[10] + nom_x[10];
   out_3891534798634327778[11] = delta_x[11] + nom_x[11];
   out_3891534798634327778[12] = delta_x[12] + nom_x[12];
   out_3891534798634327778[13] = delta_x[13] + nom_x[13];
   out_3891534798634327778[14] = delta_x[14] + nom_x[14];
   out_3891534798634327778[15] = delta_x[15] + nom_x[15];
   out_3891534798634327778[16] = delta_x[16] + nom_x[16];
   out_3891534798634327778[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5649509494944615681) {
   out_5649509494944615681[0] = -nom_x[0] + true_x[0];
   out_5649509494944615681[1] = -nom_x[1] + true_x[1];
   out_5649509494944615681[2] = -nom_x[2] + true_x[2];
   out_5649509494944615681[3] = -nom_x[3] + true_x[3];
   out_5649509494944615681[4] = -nom_x[4] + true_x[4];
   out_5649509494944615681[5] = -nom_x[5] + true_x[5];
   out_5649509494944615681[6] = -nom_x[6] + true_x[6];
   out_5649509494944615681[7] = -nom_x[7] + true_x[7];
   out_5649509494944615681[8] = -nom_x[8] + true_x[8];
   out_5649509494944615681[9] = -nom_x[9] + true_x[9];
   out_5649509494944615681[10] = -nom_x[10] + true_x[10];
   out_5649509494944615681[11] = -nom_x[11] + true_x[11];
   out_5649509494944615681[12] = -nom_x[12] + true_x[12];
   out_5649509494944615681[13] = -nom_x[13] + true_x[13];
   out_5649509494944615681[14] = -nom_x[14] + true_x[14];
   out_5649509494944615681[15] = -nom_x[15] + true_x[15];
   out_5649509494944615681[16] = -nom_x[16] + true_x[16];
   out_5649509494944615681[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_7794314942061694640) {
   out_7794314942061694640[0] = 1.0;
   out_7794314942061694640[1] = 0.0;
   out_7794314942061694640[2] = 0.0;
   out_7794314942061694640[3] = 0.0;
   out_7794314942061694640[4] = 0.0;
   out_7794314942061694640[5] = 0.0;
   out_7794314942061694640[6] = 0.0;
   out_7794314942061694640[7] = 0.0;
   out_7794314942061694640[8] = 0.0;
   out_7794314942061694640[9] = 0.0;
   out_7794314942061694640[10] = 0.0;
   out_7794314942061694640[11] = 0.0;
   out_7794314942061694640[12] = 0.0;
   out_7794314942061694640[13] = 0.0;
   out_7794314942061694640[14] = 0.0;
   out_7794314942061694640[15] = 0.0;
   out_7794314942061694640[16] = 0.0;
   out_7794314942061694640[17] = 0.0;
   out_7794314942061694640[18] = 0.0;
   out_7794314942061694640[19] = 1.0;
   out_7794314942061694640[20] = 0.0;
   out_7794314942061694640[21] = 0.0;
   out_7794314942061694640[22] = 0.0;
   out_7794314942061694640[23] = 0.0;
   out_7794314942061694640[24] = 0.0;
   out_7794314942061694640[25] = 0.0;
   out_7794314942061694640[26] = 0.0;
   out_7794314942061694640[27] = 0.0;
   out_7794314942061694640[28] = 0.0;
   out_7794314942061694640[29] = 0.0;
   out_7794314942061694640[30] = 0.0;
   out_7794314942061694640[31] = 0.0;
   out_7794314942061694640[32] = 0.0;
   out_7794314942061694640[33] = 0.0;
   out_7794314942061694640[34] = 0.0;
   out_7794314942061694640[35] = 0.0;
   out_7794314942061694640[36] = 0.0;
   out_7794314942061694640[37] = 0.0;
   out_7794314942061694640[38] = 1.0;
   out_7794314942061694640[39] = 0.0;
   out_7794314942061694640[40] = 0.0;
   out_7794314942061694640[41] = 0.0;
   out_7794314942061694640[42] = 0.0;
   out_7794314942061694640[43] = 0.0;
   out_7794314942061694640[44] = 0.0;
   out_7794314942061694640[45] = 0.0;
   out_7794314942061694640[46] = 0.0;
   out_7794314942061694640[47] = 0.0;
   out_7794314942061694640[48] = 0.0;
   out_7794314942061694640[49] = 0.0;
   out_7794314942061694640[50] = 0.0;
   out_7794314942061694640[51] = 0.0;
   out_7794314942061694640[52] = 0.0;
   out_7794314942061694640[53] = 0.0;
   out_7794314942061694640[54] = 0.0;
   out_7794314942061694640[55] = 0.0;
   out_7794314942061694640[56] = 0.0;
   out_7794314942061694640[57] = 1.0;
   out_7794314942061694640[58] = 0.0;
   out_7794314942061694640[59] = 0.0;
   out_7794314942061694640[60] = 0.0;
   out_7794314942061694640[61] = 0.0;
   out_7794314942061694640[62] = 0.0;
   out_7794314942061694640[63] = 0.0;
   out_7794314942061694640[64] = 0.0;
   out_7794314942061694640[65] = 0.0;
   out_7794314942061694640[66] = 0.0;
   out_7794314942061694640[67] = 0.0;
   out_7794314942061694640[68] = 0.0;
   out_7794314942061694640[69] = 0.0;
   out_7794314942061694640[70] = 0.0;
   out_7794314942061694640[71] = 0.0;
   out_7794314942061694640[72] = 0.0;
   out_7794314942061694640[73] = 0.0;
   out_7794314942061694640[74] = 0.0;
   out_7794314942061694640[75] = 0.0;
   out_7794314942061694640[76] = 1.0;
   out_7794314942061694640[77] = 0.0;
   out_7794314942061694640[78] = 0.0;
   out_7794314942061694640[79] = 0.0;
   out_7794314942061694640[80] = 0.0;
   out_7794314942061694640[81] = 0.0;
   out_7794314942061694640[82] = 0.0;
   out_7794314942061694640[83] = 0.0;
   out_7794314942061694640[84] = 0.0;
   out_7794314942061694640[85] = 0.0;
   out_7794314942061694640[86] = 0.0;
   out_7794314942061694640[87] = 0.0;
   out_7794314942061694640[88] = 0.0;
   out_7794314942061694640[89] = 0.0;
   out_7794314942061694640[90] = 0.0;
   out_7794314942061694640[91] = 0.0;
   out_7794314942061694640[92] = 0.0;
   out_7794314942061694640[93] = 0.0;
   out_7794314942061694640[94] = 0.0;
   out_7794314942061694640[95] = 1.0;
   out_7794314942061694640[96] = 0.0;
   out_7794314942061694640[97] = 0.0;
   out_7794314942061694640[98] = 0.0;
   out_7794314942061694640[99] = 0.0;
   out_7794314942061694640[100] = 0.0;
   out_7794314942061694640[101] = 0.0;
   out_7794314942061694640[102] = 0.0;
   out_7794314942061694640[103] = 0.0;
   out_7794314942061694640[104] = 0.0;
   out_7794314942061694640[105] = 0.0;
   out_7794314942061694640[106] = 0.0;
   out_7794314942061694640[107] = 0.0;
   out_7794314942061694640[108] = 0.0;
   out_7794314942061694640[109] = 0.0;
   out_7794314942061694640[110] = 0.0;
   out_7794314942061694640[111] = 0.0;
   out_7794314942061694640[112] = 0.0;
   out_7794314942061694640[113] = 0.0;
   out_7794314942061694640[114] = 1.0;
   out_7794314942061694640[115] = 0.0;
   out_7794314942061694640[116] = 0.0;
   out_7794314942061694640[117] = 0.0;
   out_7794314942061694640[118] = 0.0;
   out_7794314942061694640[119] = 0.0;
   out_7794314942061694640[120] = 0.0;
   out_7794314942061694640[121] = 0.0;
   out_7794314942061694640[122] = 0.0;
   out_7794314942061694640[123] = 0.0;
   out_7794314942061694640[124] = 0.0;
   out_7794314942061694640[125] = 0.0;
   out_7794314942061694640[126] = 0.0;
   out_7794314942061694640[127] = 0.0;
   out_7794314942061694640[128] = 0.0;
   out_7794314942061694640[129] = 0.0;
   out_7794314942061694640[130] = 0.0;
   out_7794314942061694640[131] = 0.0;
   out_7794314942061694640[132] = 0.0;
   out_7794314942061694640[133] = 1.0;
   out_7794314942061694640[134] = 0.0;
   out_7794314942061694640[135] = 0.0;
   out_7794314942061694640[136] = 0.0;
   out_7794314942061694640[137] = 0.0;
   out_7794314942061694640[138] = 0.0;
   out_7794314942061694640[139] = 0.0;
   out_7794314942061694640[140] = 0.0;
   out_7794314942061694640[141] = 0.0;
   out_7794314942061694640[142] = 0.0;
   out_7794314942061694640[143] = 0.0;
   out_7794314942061694640[144] = 0.0;
   out_7794314942061694640[145] = 0.0;
   out_7794314942061694640[146] = 0.0;
   out_7794314942061694640[147] = 0.0;
   out_7794314942061694640[148] = 0.0;
   out_7794314942061694640[149] = 0.0;
   out_7794314942061694640[150] = 0.0;
   out_7794314942061694640[151] = 0.0;
   out_7794314942061694640[152] = 1.0;
   out_7794314942061694640[153] = 0.0;
   out_7794314942061694640[154] = 0.0;
   out_7794314942061694640[155] = 0.0;
   out_7794314942061694640[156] = 0.0;
   out_7794314942061694640[157] = 0.0;
   out_7794314942061694640[158] = 0.0;
   out_7794314942061694640[159] = 0.0;
   out_7794314942061694640[160] = 0.0;
   out_7794314942061694640[161] = 0.0;
   out_7794314942061694640[162] = 0.0;
   out_7794314942061694640[163] = 0.0;
   out_7794314942061694640[164] = 0.0;
   out_7794314942061694640[165] = 0.0;
   out_7794314942061694640[166] = 0.0;
   out_7794314942061694640[167] = 0.0;
   out_7794314942061694640[168] = 0.0;
   out_7794314942061694640[169] = 0.0;
   out_7794314942061694640[170] = 0.0;
   out_7794314942061694640[171] = 1.0;
   out_7794314942061694640[172] = 0.0;
   out_7794314942061694640[173] = 0.0;
   out_7794314942061694640[174] = 0.0;
   out_7794314942061694640[175] = 0.0;
   out_7794314942061694640[176] = 0.0;
   out_7794314942061694640[177] = 0.0;
   out_7794314942061694640[178] = 0.0;
   out_7794314942061694640[179] = 0.0;
   out_7794314942061694640[180] = 0.0;
   out_7794314942061694640[181] = 0.0;
   out_7794314942061694640[182] = 0.0;
   out_7794314942061694640[183] = 0.0;
   out_7794314942061694640[184] = 0.0;
   out_7794314942061694640[185] = 0.0;
   out_7794314942061694640[186] = 0.0;
   out_7794314942061694640[187] = 0.0;
   out_7794314942061694640[188] = 0.0;
   out_7794314942061694640[189] = 0.0;
   out_7794314942061694640[190] = 1.0;
   out_7794314942061694640[191] = 0.0;
   out_7794314942061694640[192] = 0.0;
   out_7794314942061694640[193] = 0.0;
   out_7794314942061694640[194] = 0.0;
   out_7794314942061694640[195] = 0.0;
   out_7794314942061694640[196] = 0.0;
   out_7794314942061694640[197] = 0.0;
   out_7794314942061694640[198] = 0.0;
   out_7794314942061694640[199] = 0.0;
   out_7794314942061694640[200] = 0.0;
   out_7794314942061694640[201] = 0.0;
   out_7794314942061694640[202] = 0.0;
   out_7794314942061694640[203] = 0.0;
   out_7794314942061694640[204] = 0.0;
   out_7794314942061694640[205] = 0.0;
   out_7794314942061694640[206] = 0.0;
   out_7794314942061694640[207] = 0.0;
   out_7794314942061694640[208] = 0.0;
   out_7794314942061694640[209] = 1.0;
   out_7794314942061694640[210] = 0.0;
   out_7794314942061694640[211] = 0.0;
   out_7794314942061694640[212] = 0.0;
   out_7794314942061694640[213] = 0.0;
   out_7794314942061694640[214] = 0.0;
   out_7794314942061694640[215] = 0.0;
   out_7794314942061694640[216] = 0.0;
   out_7794314942061694640[217] = 0.0;
   out_7794314942061694640[218] = 0.0;
   out_7794314942061694640[219] = 0.0;
   out_7794314942061694640[220] = 0.0;
   out_7794314942061694640[221] = 0.0;
   out_7794314942061694640[222] = 0.0;
   out_7794314942061694640[223] = 0.0;
   out_7794314942061694640[224] = 0.0;
   out_7794314942061694640[225] = 0.0;
   out_7794314942061694640[226] = 0.0;
   out_7794314942061694640[227] = 0.0;
   out_7794314942061694640[228] = 1.0;
   out_7794314942061694640[229] = 0.0;
   out_7794314942061694640[230] = 0.0;
   out_7794314942061694640[231] = 0.0;
   out_7794314942061694640[232] = 0.0;
   out_7794314942061694640[233] = 0.0;
   out_7794314942061694640[234] = 0.0;
   out_7794314942061694640[235] = 0.0;
   out_7794314942061694640[236] = 0.0;
   out_7794314942061694640[237] = 0.0;
   out_7794314942061694640[238] = 0.0;
   out_7794314942061694640[239] = 0.0;
   out_7794314942061694640[240] = 0.0;
   out_7794314942061694640[241] = 0.0;
   out_7794314942061694640[242] = 0.0;
   out_7794314942061694640[243] = 0.0;
   out_7794314942061694640[244] = 0.0;
   out_7794314942061694640[245] = 0.0;
   out_7794314942061694640[246] = 0.0;
   out_7794314942061694640[247] = 1.0;
   out_7794314942061694640[248] = 0.0;
   out_7794314942061694640[249] = 0.0;
   out_7794314942061694640[250] = 0.0;
   out_7794314942061694640[251] = 0.0;
   out_7794314942061694640[252] = 0.0;
   out_7794314942061694640[253] = 0.0;
   out_7794314942061694640[254] = 0.0;
   out_7794314942061694640[255] = 0.0;
   out_7794314942061694640[256] = 0.0;
   out_7794314942061694640[257] = 0.0;
   out_7794314942061694640[258] = 0.0;
   out_7794314942061694640[259] = 0.0;
   out_7794314942061694640[260] = 0.0;
   out_7794314942061694640[261] = 0.0;
   out_7794314942061694640[262] = 0.0;
   out_7794314942061694640[263] = 0.0;
   out_7794314942061694640[264] = 0.0;
   out_7794314942061694640[265] = 0.0;
   out_7794314942061694640[266] = 1.0;
   out_7794314942061694640[267] = 0.0;
   out_7794314942061694640[268] = 0.0;
   out_7794314942061694640[269] = 0.0;
   out_7794314942061694640[270] = 0.0;
   out_7794314942061694640[271] = 0.0;
   out_7794314942061694640[272] = 0.0;
   out_7794314942061694640[273] = 0.0;
   out_7794314942061694640[274] = 0.0;
   out_7794314942061694640[275] = 0.0;
   out_7794314942061694640[276] = 0.0;
   out_7794314942061694640[277] = 0.0;
   out_7794314942061694640[278] = 0.0;
   out_7794314942061694640[279] = 0.0;
   out_7794314942061694640[280] = 0.0;
   out_7794314942061694640[281] = 0.0;
   out_7794314942061694640[282] = 0.0;
   out_7794314942061694640[283] = 0.0;
   out_7794314942061694640[284] = 0.0;
   out_7794314942061694640[285] = 1.0;
   out_7794314942061694640[286] = 0.0;
   out_7794314942061694640[287] = 0.0;
   out_7794314942061694640[288] = 0.0;
   out_7794314942061694640[289] = 0.0;
   out_7794314942061694640[290] = 0.0;
   out_7794314942061694640[291] = 0.0;
   out_7794314942061694640[292] = 0.0;
   out_7794314942061694640[293] = 0.0;
   out_7794314942061694640[294] = 0.0;
   out_7794314942061694640[295] = 0.0;
   out_7794314942061694640[296] = 0.0;
   out_7794314942061694640[297] = 0.0;
   out_7794314942061694640[298] = 0.0;
   out_7794314942061694640[299] = 0.0;
   out_7794314942061694640[300] = 0.0;
   out_7794314942061694640[301] = 0.0;
   out_7794314942061694640[302] = 0.0;
   out_7794314942061694640[303] = 0.0;
   out_7794314942061694640[304] = 1.0;
   out_7794314942061694640[305] = 0.0;
   out_7794314942061694640[306] = 0.0;
   out_7794314942061694640[307] = 0.0;
   out_7794314942061694640[308] = 0.0;
   out_7794314942061694640[309] = 0.0;
   out_7794314942061694640[310] = 0.0;
   out_7794314942061694640[311] = 0.0;
   out_7794314942061694640[312] = 0.0;
   out_7794314942061694640[313] = 0.0;
   out_7794314942061694640[314] = 0.0;
   out_7794314942061694640[315] = 0.0;
   out_7794314942061694640[316] = 0.0;
   out_7794314942061694640[317] = 0.0;
   out_7794314942061694640[318] = 0.0;
   out_7794314942061694640[319] = 0.0;
   out_7794314942061694640[320] = 0.0;
   out_7794314942061694640[321] = 0.0;
   out_7794314942061694640[322] = 0.0;
   out_7794314942061694640[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_8869893727485620911) {
   out_8869893727485620911[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_8869893727485620911[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_8869893727485620911[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_8869893727485620911[3] = dt*state[12] + state[3];
   out_8869893727485620911[4] = dt*state[13] + state[4];
   out_8869893727485620911[5] = dt*state[14] + state[5];
   out_8869893727485620911[6] = state[6];
   out_8869893727485620911[7] = state[7];
   out_8869893727485620911[8] = state[8];
   out_8869893727485620911[9] = state[9];
   out_8869893727485620911[10] = state[10];
   out_8869893727485620911[11] = state[11];
   out_8869893727485620911[12] = state[12];
   out_8869893727485620911[13] = state[13];
   out_8869893727485620911[14] = state[14];
   out_8869893727485620911[15] = state[15];
   out_8869893727485620911[16] = state[16];
   out_8869893727485620911[17] = state[17];
}
void F_fun(double *state, double dt, double *out_8161571396865937044) {
   out_8161571396865937044[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8161571396865937044[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8161571396865937044[2] = 0;
   out_8161571396865937044[3] = 0;
   out_8161571396865937044[4] = 0;
   out_8161571396865937044[5] = 0;
   out_8161571396865937044[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8161571396865937044[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8161571396865937044[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8161571396865937044[9] = 0;
   out_8161571396865937044[10] = 0;
   out_8161571396865937044[11] = 0;
   out_8161571396865937044[12] = 0;
   out_8161571396865937044[13] = 0;
   out_8161571396865937044[14] = 0;
   out_8161571396865937044[15] = 0;
   out_8161571396865937044[16] = 0;
   out_8161571396865937044[17] = 0;
   out_8161571396865937044[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8161571396865937044[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8161571396865937044[20] = 0;
   out_8161571396865937044[21] = 0;
   out_8161571396865937044[22] = 0;
   out_8161571396865937044[23] = 0;
   out_8161571396865937044[24] = 0;
   out_8161571396865937044[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8161571396865937044[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8161571396865937044[27] = 0;
   out_8161571396865937044[28] = 0;
   out_8161571396865937044[29] = 0;
   out_8161571396865937044[30] = 0;
   out_8161571396865937044[31] = 0;
   out_8161571396865937044[32] = 0;
   out_8161571396865937044[33] = 0;
   out_8161571396865937044[34] = 0;
   out_8161571396865937044[35] = 0;
   out_8161571396865937044[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8161571396865937044[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8161571396865937044[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8161571396865937044[39] = 0;
   out_8161571396865937044[40] = 0;
   out_8161571396865937044[41] = 0;
   out_8161571396865937044[42] = 0;
   out_8161571396865937044[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8161571396865937044[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8161571396865937044[45] = 0;
   out_8161571396865937044[46] = 0;
   out_8161571396865937044[47] = 0;
   out_8161571396865937044[48] = 0;
   out_8161571396865937044[49] = 0;
   out_8161571396865937044[50] = 0;
   out_8161571396865937044[51] = 0;
   out_8161571396865937044[52] = 0;
   out_8161571396865937044[53] = 0;
   out_8161571396865937044[54] = 0;
   out_8161571396865937044[55] = 0;
   out_8161571396865937044[56] = 0;
   out_8161571396865937044[57] = 1;
   out_8161571396865937044[58] = 0;
   out_8161571396865937044[59] = 0;
   out_8161571396865937044[60] = 0;
   out_8161571396865937044[61] = 0;
   out_8161571396865937044[62] = 0;
   out_8161571396865937044[63] = 0;
   out_8161571396865937044[64] = 0;
   out_8161571396865937044[65] = 0;
   out_8161571396865937044[66] = dt;
   out_8161571396865937044[67] = 0;
   out_8161571396865937044[68] = 0;
   out_8161571396865937044[69] = 0;
   out_8161571396865937044[70] = 0;
   out_8161571396865937044[71] = 0;
   out_8161571396865937044[72] = 0;
   out_8161571396865937044[73] = 0;
   out_8161571396865937044[74] = 0;
   out_8161571396865937044[75] = 0;
   out_8161571396865937044[76] = 1;
   out_8161571396865937044[77] = 0;
   out_8161571396865937044[78] = 0;
   out_8161571396865937044[79] = 0;
   out_8161571396865937044[80] = 0;
   out_8161571396865937044[81] = 0;
   out_8161571396865937044[82] = 0;
   out_8161571396865937044[83] = 0;
   out_8161571396865937044[84] = 0;
   out_8161571396865937044[85] = dt;
   out_8161571396865937044[86] = 0;
   out_8161571396865937044[87] = 0;
   out_8161571396865937044[88] = 0;
   out_8161571396865937044[89] = 0;
   out_8161571396865937044[90] = 0;
   out_8161571396865937044[91] = 0;
   out_8161571396865937044[92] = 0;
   out_8161571396865937044[93] = 0;
   out_8161571396865937044[94] = 0;
   out_8161571396865937044[95] = 1;
   out_8161571396865937044[96] = 0;
   out_8161571396865937044[97] = 0;
   out_8161571396865937044[98] = 0;
   out_8161571396865937044[99] = 0;
   out_8161571396865937044[100] = 0;
   out_8161571396865937044[101] = 0;
   out_8161571396865937044[102] = 0;
   out_8161571396865937044[103] = 0;
   out_8161571396865937044[104] = dt;
   out_8161571396865937044[105] = 0;
   out_8161571396865937044[106] = 0;
   out_8161571396865937044[107] = 0;
   out_8161571396865937044[108] = 0;
   out_8161571396865937044[109] = 0;
   out_8161571396865937044[110] = 0;
   out_8161571396865937044[111] = 0;
   out_8161571396865937044[112] = 0;
   out_8161571396865937044[113] = 0;
   out_8161571396865937044[114] = 1;
   out_8161571396865937044[115] = 0;
   out_8161571396865937044[116] = 0;
   out_8161571396865937044[117] = 0;
   out_8161571396865937044[118] = 0;
   out_8161571396865937044[119] = 0;
   out_8161571396865937044[120] = 0;
   out_8161571396865937044[121] = 0;
   out_8161571396865937044[122] = 0;
   out_8161571396865937044[123] = 0;
   out_8161571396865937044[124] = 0;
   out_8161571396865937044[125] = 0;
   out_8161571396865937044[126] = 0;
   out_8161571396865937044[127] = 0;
   out_8161571396865937044[128] = 0;
   out_8161571396865937044[129] = 0;
   out_8161571396865937044[130] = 0;
   out_8161571396865937044[131] = 0;
   out_8161571396865937044[132] = 0;
   out_8161571396865937044[133] = 1;
   out_8161571396865937044[134] = 0;
   out_8161571396865937044[135] = 0;
   out_8161571396865937044[136] = 0;
   out_8161571396865937044[137] = 0;
   out_8161571396865937044[138] = 0;
   out_8161571396865937044[139] = 0;
   out_8161571396865937044[140] = 0;
   out_8161571396865937044[141] = 0;
   out_8161571396865937044[142] = 0;
   out_8161571396865937044[143] = 0;
   out_8161571396865937044[144] = 0;
   out_8161571396865937044[145] = 0;
   out_8161571396865937044[146] = 0;
   out_8161571396865937044[147] = 0;
   out_8161571396865937044[148] = 0;
   out_8161571396865937044[149] = 0;
   out_8161571396865937044[150] = 0;
   out_8161571396865937044[151] = 0;
   out_8161571396865937044[152] = 1;
   out_8161571396865937044[153] = 0;
   out_8161571396865937044[154] = 0;
   out_8161571396865937044[155] = 0;
   out_8161571396865937044[156] = 0;
   out_8161571396865937044[157] = 0;
   out_8161571396865937044[158] = 0;
   out_8161571396865937044[159] = 0;
   out_8161571396865937044[160] = 0;
   out_8161571396865937044[161] = 0;
   out_8161571396865937044[162] = 0;
   out_8161571396865937044[163] = 0;
   out_8161571396865937044[164] = 0;
   out_8161571396865937044[165] = 0;
   out_8161571396865937044[166] = 0;
   out_8161571396865937044[167] = 0;
   out_8161571396865937044[168] = 0;
   out_8161571396865937044[169] = 0;
   out_8161571396865937044[170] = 0;
   out_8161571396865937044[171] = 1;
   out_8161571396865937044[172] = 0;
   out_8161571396865937044[173] = 0;
   out_8161571396865937044[174] = 0;
   out_8161571396865937044[175] = 0;
   out_8161571396865937044[176] = 0;
   out_8161571396865937044[177] = 0;
   out_8161571396865937044[178] = 0;
   out_8161571396865937044[179] = 0;
   out_8161571396865937044[180] = 0;
   out_8161571396865937044[181] = 0;
   out_8161571396865937044[182] = 0;
   out_8161571396865937044[183] = 0;
   out_8161571396865937044[184] = 0;
   out_8161571396865937044[185] = 0;
   out_8161571396865937044[186] = 0;
   out_8161571396865937044[187] = 0;
   out_8161571396865937044[188] = 0;
   out_8161571396865937044[189] = 0;
   out_8161571396865937044[190] = 1;
   out_8161571396865937044[191] = 0;
   out_8161571396865937044[192] = 0;
   out_8161571396865937044[193] = 0;
   out_8161571396865937044[194] = 0;
   out_8161571396865937044[195] = 0;
   out_8161571396865937044[196] = 0;
   out_8161571396865937044[197] = 0;
   out_8161571396865937044[198] = 0;
   out_8161571396865937044[199] = 0;
   out_8161571396865937044[200] = 0;
   out_8161571396865937044[201] = 0;
   out_8161571396865937044[202] = 0;
   out_8161571396865937044[203] = 0;
   out_8161571396865937044[204] = 0;
   out_8161571396865937044[205] = 0;
   out_8161571396865937044[206] = 0;
   out_8161571396865937044[207] = 0;
   out_8161571396865937044[208] = 0;
   out_8161571396865937044[209] = 1;
   out_8161571396865937044[210] = 0;
   out_8161571396865937044[211] = 0;
   out_8161571396865937044[212] = 0;
   out_8161571396865937044[213] = 0;
   out_8161571396865937044[214] = 0;
   out_8161571396865937044[215] = 0;
   out_8161571396865937044[216] = 0;
   out_8161571396865937044[217] = 0;
   out_8161571396865937044[218] = 0;
   out_8161571396865937044[219] = 0;
   out_8161571396865937044[220] = 0;
   out_8161571396865937044[221] = 0;
   out_8161571396865937044[222] = 0;
   out_8161571396865937044[223] = 0;
   out_8161571396865937044[224] = 0;
   out_8161571396865937044[225] = 0;
   out_8161571396865937044[226] = 0;
   out_8161571396865937044[227] = 0;
   out_8161571396865937044[228] = 1;
   out_8161571396865937044[229] = 0;
   out_8161571396865937044[230] = 0;
   out_8161571396865937044[231] = 0;
   out_8161571396865937044[232] = 0;
   out_8161571396865937044[233] = 0;
   out_8161571396865937044[234] = 0;
   out_8161571396865937044[235] = 0;
   out_8161571396865937044[236] = 0;
   out_8161571396865937044[237] = 0;
   out_8161571396865937044[238] = 0;
   out_8161571396865937044[239] = 0;
   out_8161571396865937044[240] = 0;
   out_8161571396865937044[241] = 0;
   out_8161571396865937044[242] = 0;
   out_8161571396865937044[243] = 0;
   out_8161571396865937044[244] = 0;
   out_8161571396865937044[245] = 0;
   out_8161571396865937044[246] = 0;
   out_8161571396865937044[247] = 1;
   out_8161571396865937044[248] = 0;
   out_8161571396865937044[249] = 0;
   out_8161571396865937044[250] = 0;
   out_8161571396865937044[251] = 0;
   out_8161571396865937044[252] = 0;
   out_8161571396865937044[253] = 0;
   out_8161571396865937044[254] = 0;
   out_8161571396865937044[255] = 0;
   out_8161571396865937044[256] = 0;
   out_8161571396865937044[257] = 0;
   out_8161571396865937044[258] = 0;
   out_8161571396865937044[259] = 0;
   out_8161571396865937044[260] = 0;
   out_8161571396865937044[261] = 0;
   out_8161571396865937044[262] = 0;
   out_8161571396865937044[263] = 0;
   out_8161571396865937044[264] = 0;
   out_8161571396865937044[265] = 0;
   out_8161571396865937044[266] = 1;
   out_8161571396865937044[267] = 0;
   out_8161571396865937044[268] = 0;
   out_8161571396865937044[269] = 0;
   out_8161571396865937044[270] = 0;
   out_8161571396865937044[271] = 0;
   out_8161571396865937044[272] = 0;
   out_8161571396865937044[273] = 0;
   out_8161571396865937044[274] = 0;
   out_8161571396865937044[275] = 0;
   out_8161571396865937044[276] = 0;
   out_8161571396865937044[277] = 0;
   out_8161571396865937044[278] = 0;
   out_8161571396865937044[279] = 0;
   out_8161571396865937044[280] = 0;
   out_8161571396865937044[281] = 0;
   out_8161571396865937044[282] = 0;
   out_8161571396865937044[283] = 0;
   out_8161571396865937044[284] = 0;
   out_8161571396865937044[285] = 1;
   out_8161571396865937044[286] = 0;
   out_8161571396865937044[287] = 0;
   out_8161571396865937044[288] = 0;
   out_8161571396865937044[289] = 0;
   out_8161571396865937044[290] = 0;
   out_8161571396865937044[291] = 0;
   out_8161571396865937044[292] = 0;
   out_8161571396865937044[293] = 0;
   out_8161571396865937044[294] = 0;
   out_8161571396865937044[295] = 0;
   out_8161571396865937044[296] = 0;
   out_8161571396865937044[297] = 0;
   out_8161571396865937044[298] = 0;
   out_8161571396865937044[299] = 0;
   out_8161571396865937044[300] = 0;
   out_8161571396865937044[301] = 0;
   out_8161571396865937044[302] = 0;
   out_8161571396865937044[303] = 0;
   out_8161571396865937044[304] = 1;
   out_8161571396865937044[305] = 0;
   out_8161571396865937044[306] = 0;
   out_8161571396865937044[307] = 0;
   out_8161571396865937044[308] = 0;
   out_8161571396865937044[309] = 0;
   out_8161571396865937044[310] = 0;
   out_8161571396865937044[311] = 0;
   out_8161571396865937044[312] = 0;
   out_8161571396865937044[313] = 0;
   out_8161571396865937044[314] = 0;
   out_8161571396865937044[315] = 0;
   out_8161571396865937044[316] = 0;
   out_8161571396865937044[317] = 0;
   out_8161571396865937044[318] = 0;
   out_8161571396865937044[319] = 0;
   out_8161571396865937044[320] = 0;
   out_8161571396865937044[321] = 0;
   out_8161571396865937044[322] = 0;
   out_8161571396865937044[323] = 1;
}
void h_4(double *state, double *unused, double *out_246670649264504437) {
   out_246670649264504437[0] = state[6] + state[9];
   out_246670649264504437[1] = state[7] + state[10];
   out_246670649264504437[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_6037802094718540612) {
   out_6037802094718540612[0] = 0;
   out_6037802094718540612[1] = 0;
   out_6037802094718540612[2] = 0;
   out_6037802094718540612[3] = 0;
   out_6037802094718540612[4] = 0;
   out_6037802094718540612[5] = 0;
   out_6037802094718540612[6] = 1;
   out_6037802094718540612[7] = 0;
   out_6037802094718540612[8] = 0;
   out_6037802094718540612[9] = 1;
   out_6037802094718540612[10] = 0;
   out_6037802094718540612[11] = 0;
   out_6037802094718540612[12] = 0;
   out_6037802094718540612[13] = 0;
   out_6037802094718540612[14] = 0;
   out_6037802094718540612[15] = 0;
   out_6037802094718540612[16] = 0;
   out_6037802094718540612[17] = 0;
   out_6037802094718540612[18] = 0;
   out_6037802094718540612[19] = 0;
   out_6037802094718540612[20] = 0;
   out_6037802094718540612[21] = 0;
   out_6037802094718540612[22] = 0;
   out_6037802094718540612[23] = 0;
   out_6037802094718540612[24] = 0;
   out_6037802094718540612[25] = 1;
   out_6037802094718540612[26] = 0;
   out_6037802094718540612[27] = 0;
   out_6037802094718540612[28] = 1;
   out_6037802094718540612[29] = 0;
   out_6037802094718540612[30] = 0;
   out_6037802094718540612[31] = 0;
   out_6037802094718540612[32] = 0;
   out_6037802094718540612[33] = 0;
   out_6037802094718540612[34] = 0;
   out_6037802094718540612[35] = 0;
   out_6037802094718540612[36] = 0;
   out_6037802094718540612[37] = 0;
   out_6037802094718540612[38] = 0;
   out_6037802094718540612[39] = 0;
   out_6037802094718540612[40] = 0;
   out_6037802094718540612[41] = 0;
   out_6037802094718540612[42] = 0;
   out_6037802094718540612[43] = 0;
   out_6037802094718540612[44] = 1;
   out_6037802094718540612[45] = 0;
   out_6037802094718540612[46] = 0;
   out_6037802094718540612[47] = 1;
   out_6037802094718540612[48] = 0;
   out_6037802094718540612[49] = 0;
   out_6037802094718540612[50] = 0;
   out_6037802094718540612[51] = 0;
   out_6037802094718540612[52] = 0;
   out_6037802094718540612[53] = 0;
}
void h_10(double *state, double *unused, double *out_3326189525576215270) {
   out_3326189525576215270[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_3326189525576215270[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_3326189525576215270[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_5195608496361205355) {
   out_5195608496361205355[0] = 0;
   out_5195608496361205355[1] = 9.8100000000000005*cos(state[1]);
   out_5195608496361205355[2] = 0;
   out_5195608496361205355[3] = 0;
   out_5195608496361205355[4] = -state[8];
   out_5195608496361205355[5] = state[7];
   out_5195608496361205355[6] = 0;
   out_5195608496361205355[7] = state[5];
   out_5195608496361205355[8] = -state[4];
   out_5195608496361205355[9] = 0;
   out_5195608496361205355[10] = 0;
   out_5195608496361205355[11] = 0;
   out_5195608496361205355[12] = 1;
   out_5195608496361205355[13] = 0;
   out_5195608496361205355[14] = 0;
   out_5195608496361205355[15] = 1;
   out_5195608496361205355[16] = 0;
   out_5195608496361205355[17] = 0;
   out_5195608496361205355[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_5195608496361205355[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_5195608496361205355[20] = 0;
   out_5195608496361205355[21] = state[8];
   out_5195608496361205355[22] = 0;
   out_5195608496361205355[23] = -state[6];
   out_5195608496361205355[24] = -state[5];
   out_5195608496361205355[25] = 0;
   out_5195608496361205355[26] = state[3];
   out_5195608496361205355[27] = 0;
   out_5195608496361205355[28] = 0;
   out_5195608496361205355[29] = 0;
   out_5195608496361205355[30] = 0;
   out_5195608496361205355[31] = 1;
   out_5195608496361205355[32] = 0;
   out_5195608496361205355[33] = 0;
   out_5195608496361205355[34] = 1;
   out_5195608496361205355[35] = 0;
   out_5195608496361205355[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_5195608496361205355[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_5195608496361205355[38] = 0;
   out_5195608496361205355[39] = -state[7];
   out_5195608496361205355[40] = state[6];
   out_5195608496361205355[41] = 0;
   out_5195608496361205355[42] = state[4];
   out_5195608496361205355[43] = -state[3];
   out_5195608496361205355[44] = 0;
   out_5195608496361205355[45] = 0;
   out_5195608496361205355[46] = 0;
   out_5195608496361205355[47] = 0;
   out_5195608496361205355[48] = 0;
   out_5195608496361205355[49] = 0;
   out_5195608496361205355[50] = 1;
   out_5195608496361205355[51] = 0;
   out_5195608496361205355[52] = 0;
   out_5195608496361205355[53] = 1;
}
void h_13(double *state, double *unused, double *out_5017380501583283993) {
   out_5017380501583283993[0] = state[3];
   out_5017380501583283993[1] = state[4];
   out_5017380501583283993[2] = state[5];
}
void H_13(double *state, double *unused, double *out_2825528269386207811) {
   out_2825528269386207811[0] = 0;
   out_2825528269386207811[1] = 0;
   out_2825528269386207811[2] = 0;
   out_2825528269386207811[3] = 1;
   out_2825528269386207811[4] = 0;
   out_2825528269386207811[5] = 0;
   out_2825528269386207811[6] = 0;
   out_2825528269386207811[7] = 0;
   out_2825528269386207811[8] = 0;
   out_2825528269386207811[9] = 0;
   out_2825528269386207811[10] = 0;
   out_2825528269386207811[11] = 0;
   out_2825528269386207811[12] = 0;
   out_2825528269386207811[13] = 0;
   out_2825528269386207811[14] = 0;
   out_2825528269386207811[15] = 0;
   out_2825528269386207811[16] = 0;
   out_2825528269386207811[17] = 0;
   out_2825528269386207811[18] = 0;
   out_2825528269386207811[19] = 0;
   out_2825528269386207811[20] = 0;
   out_2825528269386207811[21] = 0;
   out_2825528269386207811[22] = 1;
   out_2825528269386207811[23] = 0;
   out_2825528269386207811[24] = 0;
   out_2825528269386207811[25] = 0;
   out_2825528269386207811[26] = 0;
   out_2825528269386207811[27] = 0;
   out_2825528269386207811[28] = 0;
   out_2825528269386207811[29] = 0;
   out_2825528269386207811[30] = 0;
   out_2825528269386207811[31] = 0;
   out_2825528269386207811[32] = 0;
   out_2825528269386207811[33] = 0;
   out_2825528269386207811[34] = 0;
   out_2825528269386207811[35] = 0;
   out_2825528269386207811[36] = 0;
   out_2825528269386207811[37] = 0;
   out_2825528269386207811[38] = 0;
   out_2825528269386207811[39] = 0;
   out_2825528269386207811[40] = 0;
   out_2825528269386207811[41] = 1;
   out_2825528269386207811[42] = 0;
   out_2825528269386207811[43] = 0;
   out_2825528269386207811[44] = 0;
   out_2825528269386207811[45] = 0;
   out_2825528269386207811[46] = 0;
   out_2825528269386207811[47] = 0;
   out_2825528269386207811[48] = 0;
   out_2825528269386207811[49] = 0;
   out_2825528269386207811[50] = 0;
   out_2825528269386207811[51] = 0;
   out_2825528269386207811[52] = 0;
   out_2825528269386207811[53] = 0;
}
void h_14(double *state, double *unused, double *out_5006204601247985119) {
   out_5006204601247985119[0] = state[6];
   out_5006204601247985119[1] = state[7];
   out_5006204601247985119[2] = state[8];
}
void H_14(double *state, double *unused, double *out_2074561238379056083) {
   out_2074561238379056083[0] = 0;
   out_2074561238379056083[1] = 0;
   out_2074561238379056083[2] = 0;
   out_2074561238379056083[3] = 0;
   out_2074561238379056083[4] = 0;
   out_2074561238379056083[5] = 0;
   out_2074561238379056083[6] = 1;
   out_2074561238379056083[7] = 0;
   out_2074561238379056083[8] = 0;
   out_2074561238379056083[9] = 0;
   out_2074561238379056083[10] = 0;
   out_2074561238379056083[11] = 0;
   out_2074561238379056083[12] = 0;
   out_2074561238379056083[13] = 0;
   out_2074561238379056083[14] = 0;
   out_2074561238379056083[15] = 0;
   out_2074561238379056083[16] = 0;
   out_2074561238379056083[17] = 0;
   out_2074561238379056083[18] = 0;
   out_2074561238379056083[19] = 0;
   out_2074561238379056083[20] = 0;
   out_2074561238379056083[21] = 0;
   out_2074561238379056083[22] = 0;
   out_2074561238379056083[23] = 0;
   out_2074561238379056083[24] = 0;
   out_2074561238379056083[25] = 1;
   out_2074561238379056083[26] = 0;
   out_2074561238379056083[27] = 0;
   out_2074561238379056083[28] = 0;
   out_2074561238379056083[29] = 0;
   out_2074561238379056083[30] = 0;
   out_2074561238379056083[31] = 0;
   out_2074561238379056083[32] = 0;
   out_2074561238379056083[33] = 0;
   out_2074561238379056083[34] = 0;
   out_2074561238379056083[35] = 0;
   out_2074561238379056083[36] = 0;
   out_2074561238379056083[37] = 0;
   out_2074561238379056083[38] = 0;
   out_2074561238379056083[39] = 0;
   out_2074561238379056083[40] = 0;
   out_2074561238379056083[41] = 0;
   out_2074561238379056083[42] = 0;
   out_2074561238379056083[43] = 0;
   out_2074561238379056083[44] = 1;
   out_2074561238379056083[45] = 0;
   out_2074561238379056083[46] = 0;
   out_2074561238379056083[47] = 0;
   out_2074561238379056083[48] = 0;
   out_2074561238379056083[49] = 0;
   out_2074561238379056083[50] = 0;
   out_2074561238379056083[51] = 0;
   out_2074561238379056083[52] = 0;
   out_2074561238379056083[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_3891534798634327778) {
  err_fun(nom_x, delta_x, out_3891534798634327778);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5649509494944615681) {
  inv_err_fun(nom_x, true_x, out_5649509494944615681);
}
void pose_H_mod_fun(double *state, double *out_7794314942061694640) {
  H_mod_fun(state, out_7794314942061694640);
}
void pose_f_fun(double *state, double dt, double *out_8869893727485620911) {
  f_fun(state,  dt, out_8869893727485620911);
}
void pose_F_fun(double *state, double dt, double *out_8161571396865937044) {
  F_fun(state,  dt, out_8161571396865937044);
}
void pose_h_4(double *state, double *unused, double *out_246670649264504437) {
  h_4(state, unused, out_246670649264504437);
}
void pose_H_4(double *state, double *unused, double *out_6037802094718540612) {
  H_4(state, unused, out_6037802094718540612);
}
void pose_h_10(double *state, double *unused, double *out_3326189525576215270) {
  h_10(state, unused, out_3326189525576215270);
}
void pose_H_10(double *state, double *unused, double *out_5195608496361205355) {
  H_10(state, unused, out_5195608496361205355);
}
void pose_h_13(double *state, double *unused, double *out_5017380501583283993) {
  h_13(state, unused, out_5017380501583283993);
}
void pose_H_13(double *state, double *unused, double *out_2825528269386207811) {
  H_13(state, unused, out_2825528269386207811);
}
void pose_h_14(double *state, double *unused, double *out_5006204601247985119) {
  h_14(state, unused, out_5006204601247985119);
}
void pose_H_14(double *state, double *unused, double *out_2074561238379056083) {
  H_14(state, unused, out_2074561238379056083);
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
