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
void err_fun(double *nom_x, double *delta_x, double *out_8244834270034669277) {
   out_8244834270034669277[0] = delta_x[0] + nom_x[0];
   out_8244834270034669277[1] = delta_x[1] + nom_x[1];
   out_8244834270034669277[2] = delta_x[2] + nom_x[2];
   out_8244834270034669277[3] = delta_x[3] + nom_x[3];
   out_8244834270034669277[4] = delta_x[4] + nom_x[4];
   out_8244834270034669277[5] = delta_x[5] + nom_x[5];
   out_8244834270034669277[6] = delta_x[6] + nom_x[6];
   out_8244834270034669277[7] = delta_x[7] + nom_x[7];
   out_8244834270034669277[8] = delta_x[8] + nom_x[8];
   out_8244834270034669277[9] = delta_x[9] + nom_x[9];
   out_8244834270034669277[10] = delta_x[10] + nom_x[10];
   out_8244834270034669277[11] = delta_x[11] + nom_x[11];
   out_8244834270034669277[12] = delta_x[12] + nom_x[12];
   out_8244834270034669277[13] = delta_x[13] + nom_x[13];
   out_8244834270034669277[14] = delta_x[14] + nom_x[14];
   out_8244834270034669277[15] = delta_x[15] + nom_x[15];
   out_8244834270034669277[16] = delta_x[16] + nom_x[16];
   out_8244834270034669277[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5687769365300631080) {
   out_5687769365300631080[0] = -nom_x[0] + true_x[0];
   out_5687769365300631080[1] = -nom_x[1] + true_x[1];
   out_5687769365300631080[2] = -nom_x[2] + true_x[2];
   out_5687769365300631080[3] = -nom_x[3] + true_x[3];
   out_5687769365300631080[4] = -nom_x[4] + true_x[4];
   out_5687769365300631080[5] = -nom_x[5] + true_x[5];
   out_5687769365300631080[6] = -nom_x[6] + true_x[6];
   out_5687769365300631080[7] = -nom_x[7] + true_x[7];
   out_5687769365300631080[8] = -nom_x[8] + true_x[8];
   out_5687769365300631080[9] = -nom_x[9] + true_x[9];
   out_5687769365300631080[10] = -nom_x[10] + true_x[10];
   out_5687769365300631080[11] = -nom_x[11] + true_x[11];
   out_5687769365300631080[12] = -nom_x[12] + true_x[12];
   out_5687769365300631080[13] = -nom_x[13] + true_x[13];
   out_5687769365300631080[14] = -nom_x[14] + true_x[14];
   out_5687769365300631080[15] = -nom_x[15] + true_x[15];
   out_5687769365300631080[16] = -nom_x[16] + true_x[16];
   out_5687769365300631080[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_5729207129571741933) {
   out_5729207129571741933[0] = 1.0;
   out_5729207129571741933[1] = 0.0;
   out_5729207129571741933[2] = 0.0;
   out_5729207129571741933[3] = 0.0;
   out_5729207129571741933[4] = 0.0;
   out_5729207129571741933[5] = 0.0;
   out_5729207129571741933[6] = 0.0;
   out_5729207129571741933[7] = 0.0;
   out_5729207129571741933[8] = 0.0;
   out_5729207129571741933[9] = 0.0;
   out_5729207129571741933[10] = 0.0;
   out_5729207129571741933[11] = 0.0;
   out_5729207129571741933[12] = 0.0;
   out_5729207129571741933[13] = 0.0;
   out_5729207129571741933[14] = 0.0;
   out_5729207129571741933[15] = 0.0;
   out_5729207129571741933[16] = 0.0;
   out_5729207129571741933[17] = 0.0;
   out_5729207129571741933[18] = 0.0;
   out_5729207129571741933[19] = 1.0;
   out_5729207129571741933[20] = 0.0;
   out_5729207129571741933[21] = 0.0;
   out_5729207129571741933[22] = 0.0;
   out_5729207129571741933[23] = 0.0;
   out_5729207129571741933[24] = 0.0;
   out_5729207129571741933[25] = 0.0;
   out_5729207129571741933[26] = 0.0;
   out_5729207129571741933[27] = 0.0;
   out_5729207129571741933[28] = 0.0;
   out_5729207129571741933[29] = 0.0;
   out_5729207129571741933[30] = 0.0;
   out_5729207129571741933[31] = 0.0;
   out_5729207129571741933[32] = 0.0;
   out_5729207129571741933[33] = 0.0;
   out_5729207129571741933[34] = 0.0;
   out_5729207129571741933[35] = 0.0;
   out_5729207129571741933[36] = 0.0;
   out_5729207129571741933[37] = 0.0;
   out_5729207129571741933[38] = 1.0;
   out_5729207129571741933[39] = 0.0;
   out_5729207129571741933[40] = 0.0;
   out_5729207129571741933[41] = 0.0;
   out_5729207129571741933[42] = 0.0;
   out_5729207129571741933[43] = 0.0;
   out_5729207129571741933[44] = 0.0;
   out_5729207129571741933[45] = 0.0;
   out_5729207129571741933[46] = 0.0;
   out_5729207129571741933[47] = 0.0;
   out_5729207129571741933[48] = 0.0;
   out_5729207129571741933[49] = 0.0;
   out_5729207129571741933[50] = 0.0;
   out_5729207129571741933[51] = 0.0;
   out_5729207129571741933[52] = 0.0;
   out_5729207129571741933[53] = 0.0;
   out_5729207129571741933[54] = 0.0;
   out_5729207129571741933[55] = 0.0;
   out_5729207129571741933[56] = 0.0;
   out_5729207129571741933[57] = 1.0;
   out_5729207129571741933[58] = 0.0;
   out_5729207129571741933[59] = 0.0;
   out_5729207129571741933[60] = 0.0;
   out_5729207129571741933[61] = 0.0;
   out_5729207129571741933[62] = 0.0;
   out_5729207129571741933[63] = 0.0;
   out_5729207129571741933[64] = 0.0;
   out_5729207129571741933[65] = 0.0;
   out_5729207129571741933[66] = 0.0;
   out_5729207129571741933[67] = 0.0;
   out_5729207129571741933[68] = 0.0;
   out_5729207129571741933[69] = 0.0;
   out_5729207129571741933[70] = 0.0;
   out_5729207129571741933[71] = 0.0;
   out_5729207129571741933[72] = 0.0;
   out_5729207129571741933[73] = 0.0;
   out_5729207129571741933[74] = 0.0;
   out_5729207129571741933[75] = 0.0;
   out_5729207129571741933[76] = 1.0;
   out_5729207129571741933[77] = 0.0;
   out_5729207129571741933[78] = 0.0;
   out_5729207129571741933[79] = 0.0;
   out_5729207129571741933[80] = 0.0;
   out_5729207129571741933[81] = 0.0;
   out_5729207129571741933[82] = 0.0;
   out_5729207129571741933[83] = 0.0;
   out_5729207129571741933[84] = 0.0;
   out_5729207129571741933[85] = 0.0;
   out_5729207129571741933[86] = 0.0;
   out_5729207129571741933[87] = 0.0;
   out_5729207129571741933[88] = 0.0;
   out_5729207129571741933[89] = 0.0;
   out_5729207129571741933[90] = 0.0;
   out_5729207129571741933[91] = 0.0;
   out_5729207129571741933[92] = 0.0;
   out_5729207129571741933[93] = 0.0;
   out_5729207129571741933[94] = 0.0;
   out_5729207129571741933[95] = 1.0;
   out_5729207129571741933[96] = 0.0;
   out_5729207129571741933[97] = 0.0;
   out_5729207129571741933[98] = 0.0;
   out_5729207129571741933[99] = 0.0;
   out_5729207129571741933[100] = 0.0;
   out_5729207129571741933[101] = 0.0;
   out_5729207129571741933[102] = 0.0;
   out_5729207129571741933[103] = 0.0;
   out_5729207129571741933[104] = 0.0;
   out_5729207129571741933[105] = 0.0;
   out_5729207129571741933[106] = 0.0;
   out_5729207129571741933[107] = 0.0;
   out_5729207129571741933[108] = 0.0;
   out_5729207129571741933[109] = 0.0;
   out_5729207129571741933[110] = 0.0;
   out_5729207129571741933[111] = 0.0;
   out_5729207129571741933[112] = 0.0;
   out_5729207129571741933[113] = 0.0;
   out_5729207129571741933[114] = 1.0;
   out_5729207129571741933[115] = 0.0;
   out_5729207129571741933[116] = 0.0;
   out_5729207129571741933[117] = 0.0;
   out_5729207129571741933[118] = 0.0;
   out_5729207129571741933[119] = 0.0;
   out_5729207129571741933[120] = 0.0;
   out_5729207129571741933[121] = 0.0;
   out_5729207129571741933[122] = 0.0;
   out_5729207129571741933[123] = 0.0;
   out_5729207129571741933[124] = 0.0;
   out_5729207129571741933[125] = 0.0;
   out_5729207129571741933[126] = 0.0;
   out_5729207129571741933[127] = 0.0;
   out_5729207129571741933[128] = 0.0;
   out_5729207129571741933[129] = 0.0;
   out_5729207129571741933[130] = 0.0;
   out_5729207129571741933[131] = 0.0;
   out_5729207129571741933[132] = 0.0;
   out_5729207129571741933[133] = 1.0;
   out_5729207129571741933[134] = 0.0;
   out_5729207129571741933[135] = 0.0;
   out_5729207129571741933[136] = 0.0;
   out_5729207129571741933[137] = 0.0;
   out_5729207129571741933[138] = 0.0;
   out_5729207129571741933[139] = 0.0;
   out_5729207129571741933[140] = 0.0;
   out_5729207129571741933[141] = 0.0;
   out_5729207129571741933[142] = 0.0;
   out_5729207129571741933[143] = 0.0;
   out_5729207129571741933[144] = 0.0;
   out_5729207129571741933[145] = 0.0;
   out_5729207129571741933[146] = 0.0;
   out_5729207129571741933[147] = 0.0;
   out_5729207129571741933[148] = 0.0;
   out_5729207129571741933[149] = 0.0;
   out_5729207129571741933[150] = 0.0;
   out_5729207129571741933[151] = 0.0;
   out_5729207129571741933[152] = 1.0;
   out_5729207129571741933[153] = 0.0;
   out_5729207129571741933[154] = 0.0;
   out_5729207129571741933[155] = 0.0;
   out_5729207129571741933[156] = 0.0;
   out_5729207129571741933[157] = 0.0;
   out_5729207129571741933[158] = 0.0;
   out_5729207129571741933[159] = 0.0;
   out_5729207129571741933[160] = 0.0;
   out_5729207129571741933[161] = 0.0;
   out_5729207129571741933[162] = 0.0;
   out_5729207129571741933[163] = 0.0;
   out_5729207129571741933[164] = 0.0;
   out_5729207129571741933[165] = 0.0;
   out_5729207129571741933[166] = 0.0;
   out_5729207129571741933[167] = 0.0;
   out_5729207129571741933[168] = 0.0;
   out_5729207129571741933[169] = 0.0;
   out_5729207129571741933[170] = 0.0;
   out_5729207129571741933[171] = 1.0;
   out_5729207129571741933[172] = 0.0;
   out_5729207129571741933[173] = 0.0;
   out_5729207129571741933[174] = 0.0;
   out_5729207129571741933[175] = 0.0;
   out_5729207129571741933[176] = 0.0;
   out_5729207129571741933[177] = 0.0;
   out_5729207129571741933[178] = 0.0;
   out_5729207129571741933[179] = 0.0;
   out_5729207129571741933[180] = 0.0;
   out_5729207129571741933[181] = 0.0;
   out_5729207129571741933[182] = 0.0;
   out_5729207129571741933[183] = 0.0;
   out_5729207129571741933[184] = 0.0;
   out_5729207129571741933[185] = 0.0;
   out_5729207129571741933[186] = 0.0;
   out_5729207129571741933[187] = 0.0;
   out_5729207129571741933[188] = 0.0;
   out_5729207129571741933[189] = 0.0;
   out_5729207129571741933[190] = 1.0;
   out_5729207129571741933[191] = 0.0;
   out_5729207129571741933[192] = 0.0;
   out_5729207129571741933[193] = 0.0;
   out_5729207129571741933[194] = 0.0;
   out_5729207129571741933[195] = 0.0;
   out_5729207129571741933[196] = 0.0;
   out_5729207129571741933[197] = 0.0;
   out_5729207129571741933[198] = 0.0;
   out_5729207129571741933[199] = 0.0;
   out_5729207129571741933[200] = 0.0;
   out_5729207129571741933[201] = 0.0;
   out_5729207129571741933[202] = 0.0;
   out_5729207129571741933[203] = 0.0;
   out_5729207129571741933[204] = 0.0;
   out_5729207129571741933[205] = 0.0;
   out_5729207129571741933[206] = 0.0;
   out_5729207129571741933[207] = 0.0;
   out_5729207129571741933[208] = 0.0;
   out_5729207129571741933[209] = 1.0;
   out_5729207129571741933[210] = 0.0;
   out_5729207129571741933[211] = 0.0;
   out_5729207129571741933[212] = 0.0;
   out_5729207129571741933[213] = 0.0;
   out_5729207129571741933[214] = 0.0;
   out_5729207129571741933[215] = 0.0;
   out_5729207129571741933[216] = 0.0;
   out_5729207129571741933[217] = 0.0;
   out_5729207129571741933[218] = 0.0;
   out_5729207129571741933[219] = 0.0;
   out_5729207129571741933[220] = 0.0;
   out_5729207129571741933[221] = 0.0;
   out_5729207129571741933[222] = 0.0;
   out_5729207129571741933[223] = 0.0;
   out_5729207129571741933[224] = 0.0;
   out_5729207129571741933[225] = 0.0;
   out_5729207129571741933[226] = 0.0;
   out_5729207129571741933[227] = 0.0;
   out_5729207129571741933[228] = 1.0;
   out_5729207129571741933[229] = 0.0;
   out_5729207129571741933[230] = 0.0;
   out_5729207129571741933[231] = 0.0;
   out_5729207129571741933[232] = 0.0;
   out_5729207129571741933[233] = 0.0;
   out_5729207129571741933[234] = 0.0;
   out_5729207129571741933[235] = 0.0;
   out_5729207129571741933[236] = 0.0;
   out_5729207129571741933[237] = 0.0;
   out_5729207129571741933[238] = 0.0;
   out_5729207129571741933[239] = 0.0;
   out_5729207129571741933[240] = 0.0;
   out_5729207129571741933[241] = 0.0;
   out_5729207129571741933[242] = 0.0;
   out_5729207129571741933[243] = 0.0;
   out_5729207129571741933[244] = 0.0;
   out_5729207129571741933[245] = 0.0;
   out_5729207129571741933[246] = 0.0;
   out_5729207129571741933[247] = 1.0;
   out_5729207129571741933[248] = 0.0;
   out_5729207129571741933[249] = 0.0;
   out_5729207129571741933[250] = 0.0;
   out_5729207129571741933[251] = 0.0;
   out_5729207129571741933[252] = 0.0;
   out_5729207129571741933[253] = 0.0;
   out_5729207129571741933[254] = 0.0;
   out_5729207129571741933[255] = 0.0;
   out_5729207129571741933[256] = 0.0;
   out_5729207129571741933[257] = 0.0;
   out_5729207129571741933[258] = 0.0;
   out_5729207129571741933[259] = 0.0;
   out_5729207129571741933[260] = 0.0;
   out_5729207129571741933[261] = 0.0;
   out_5729207129571741933[262] = 0.0;
   out_5729207129571741933[263] = 0.0;
   out_5729207129571741933[264] = 0.0;
   out_5729207129571741933[265] = 0.0;
   out_5729207129571741933[266] = 1.0;
   out_5729207129571741933[267] = 0.0;
   out_5729207129571741933[268] = 0.0;
   out_5729207129571741933[269] = 0.0;
   out_5729207129571741933[270] = 0.0;
   out_5729207129571741933[271] = 0.0;
   out_5729207129571741933[272] = 0.0;
   out_5729207129571741933[273] = 0.0;
   out_5729207129571741933[274] = 0.0;
   out_5729207129571741933[275] = 0.0;
   out_5729207129571741933[276] = 0.0;
   out_5729207129571741933[277] = 0.0;
   out_5729207129571741933[278] = 0.0;
   out_5729207129571741933[279] = 0.0;
   out_5729207129571741933[280] = 0.0;
   out_5729207129571741933[281] = 0.0;
   out_5729207129571741933[282] = 0.0;
   out_5729207129571741933[283] = 0.0;
   out_5729207129571741933[284] = 0.0;
   out_5729207129571741933[285] = 1.0;
   out_5729207129571741933[286] = 0.0;
   out_5729207129571741933[287] = 0.0;
   out_5729207129571741933[288] = 0.0;
   out_5729207129571741933[289] = 0.0;
   out_5729207129571741933[290] = 0.0;
   out_5729207129571741933[291] = 0.0;
   out_5729207129571741933[292] = 0.0;
   out_5729207129571741933[293] = 0.0;
   out_5729207129571741933[294] = 0.0;
   out_5729207129571741933[295] = 0.0;
   out_5729207129571741933[296] = 0.0;
   out_5729207129571741933[297] = 0.0;
   out_5729207129571741933[298] = 0.0;
   out_5729207129571741933[299] = 0.0;
   out_5729207129571741933[300] = 0.0;
   out_5729207129571741933[301] = 0.0;
   out_5729207129571741933[302] = 0.0;
   out_5729207129571741933[303] = 0.0;
   out_5729207129571741933[304] = 1.0;
   out_5729207129571741933[305] = 0.0;
   out_5729207129571741933[306] = 0.0;
   out_5729207129571741933[307] = 0.0;
   out_5729207129571741933[308] = 0.0;
   out_5729207129571741933[309] = 0.0;
   out_5729207129571741933[310] = 0.0;
   out_5729207129571741933[311] = 0.0;
   out_5729207129571741933[312] = 0.0;
   out_5729207129571741933[313] = 0.0;
   out_5729207129571741933[314] = 0.0;
   out_5729207129571741933[315] = 0.0;
   out_5729207129571741933[316] = 0.0;
   out_5729207129571741933[317] = 0.0;
   out_5729207129571741933[318] = 0.0;
   out_5729207129571741933[319] = 0.0;
   out_5729207129571741933[320] = 0.0;
   out_5729207129571741933[321] = 0.0;
   out_5729207129571741933[322] = 0.0;
   out_5729207129571741933[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_5327017859701626059) {
   out_5327017859701626059[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_5327017859701626059[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_5327017859701626059[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_5327017859701626059[3] = dt*state[12] + state[3];
   out_5327017859701626059[4] = dt*state[13] + state[4];
   out_5327017859701626059[5] = dt*state[14] + state[5];
   out_5327017859701626059[6] = state[6];
   out_5327017859701626059[7] = state[7];
   out_5327017859701626059[8] = state[8];
   out_5327017859701626059[9] = state[9];
   out_5327017859701626059[10] = state[10];
   out_5327017859701626059[11] = state[11];
   out_5327017859701626059[12] = state[12];
   out_5327017859701626059[13] = state[13];
   out_5327017859701626059[14] = state[14];
   out_5327017859701626059[15] = state[15];
   out_5327017859701626059[16] = state[16];
   out_5327017859701626059[17] = state[17];
}
void F_fun(double *state, double dt, double *out_8075335770489140637) {
   out_8075335770489140637[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8075335770489140637[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8075335770489140637[2] = 0;
   out_8075335770489140637[3] = 0;
   out_8075335770489140637[4] = 0;
   out_8075335770489140637[5] = 0;
   out_8075335770489140637[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8075335770489140637[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8075335770489140637[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8075335770489140637[9] = 0;
   out_8075335770489140637[10] = 0;
   out_8075335770489140637[11] = 0;
   out_8075335770489140637[12] = 0;
   out_8075335770489140637[13] = 0;
   out_8075335770489140637[14] = 0;
   out_8075335770489140637[15] = 0;
   out_8075335770489140637[16] = 0;
   out_8075335770489140637[17] = 0;
   out_8075335770489140637[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8075335770489140637[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8075335770489140637[20] = 0;
   out_8075335770489140637[21] = 0;
   out_8075335770489140637[22] = 0;
   out_8075335770489140637[23] = 0;
   out_8075335770489140637[24] = 0;
   out_8075335770489140637[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8075335770489140637[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8075335770489140637[27] = 0;
   out_8075335770489140637[28] = 0;
   out_8075335770489140637[29] = 0;
   out_8075335770489140637[30] = 0;
   out_8075335770489140637[31] = 0;
   out_8075335770489140637[32] = 0;
   out_8075335770489140637[33] = 0;
   out_8075335770489140637[34] = 0;
   out_8075335770489140637[35] = 0;
   out_8075335770489140637[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8075335770489140637[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8075335770489140637[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8075335770489140637[39] = 0;
   out_8075335770489140637[40] = 0;
   out_8075335770489140637[41] = 0;
   out_8075335770489140637[42] = 0;
   out_8075335770489140637[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8075335770489140637[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8075335770489140637[45] = 0;
   out_8075335770489140637[46] = 0;
   out_8075335770489140637[47] = 0;
   out_8075335770489140637[48] = 0;
   out_8075335770489140637[49] = 0;
   out_8075335770489140637[50] = 0;
   out_8075335770489140637[51] = 0;
   out_8075335770489140637[52] = 0;
   out_8075335770489140637[53] = 0;
   out_8075335770489140637[54] = 0;
   out_8075335770489140637[55] = 0;
   out_8075335770489140637[56] = 0;
   out_8075335770489140637[57] = 1;
   out_8075335770489140637[58] = 0;
   out_8075335770489140637[59] = 0;
   out_8075335770489140637[60] = 0;
   out_8075335770489140637[61] = 0;
   out_8075335770489140637[62] = 0;
   out_8075335770489140637[63] = 0;
   out_8075335770489140637[64] = 0;
   out_8075335770489140637[65] = 0;
   out_8075335770489140637[66] = dt;
   out_8075335770489140637[67] = 0;
   out_8075335770489140637[68] = 0;
   out_8075335770489140637[69] = 0;
   out_8075335770489140637[70] = 0;
   out_8075335770489140637[71] = 0;
   out_8075335770489140637[72] = 0;
   out_8075335770489140637[73] = 0;
   out_8075335770489140637[74] = 0;
   out_8075335770489140637[75] = 0;
   out_8075335770489140637[76] = 1;
   out_8075335770489140637[77] = 0;
   out_8075335770489140637[78] = 0;
   out_8075335770489140637[79] = 0;
   out_8075335770489140637[80] = 0;
   out_8075335770489140637[81] = 0;
   out_8075335770489140637[82] = 0;
   out_8075335770489140637[83] = 0;
   out_8075335770489140637[84] = 0;
   out_8075335770489140637[85] = dt;
   out_8075335770489140637[86] = 0;
   out_8075335770489140637[87] = 0;
   out_8075335770489140637[88] = 0;
   out_8075335770489140637[89] = 0;
   out_8075335770489140637[90] = 0;
   out_8075335770489140637[91] = 0;
   out_8075335770489140637[92] = 0;
   out_8075335770489140637[93] = 0;
   out_8075335770489140637[94] = 0;
   out_8075335770489140637[95] = 1;
   out_8075335770489140637[96] = 0;
   out_8075335770489140637[97] = 0;
   out_8075335770489140637[98] = 0;
   out_8075335770489140637[99] = 0;
   out_8075335770489140637[100] = 0;
   out_8075335770489140637[101] = 0;
   out_8075335770489140637[102] = 0;
   out_8075335770489140637[103] = 0;
   out_8075335770489140637[104] = dt;
   out_8075335770489140637[105] = 0;
   out_8075335770489140637[106] = 0;
   out_8075335770489140637[107] = 0;
   out_8075335770489140637[108] = 0;
   out_8075335770489140637[109] = 0;
   out_8075335770489140637[110] = 0;
   out_8075335770489140637[111] = 0;
   out_8075335770489140637[112] = 0;
   out_8075335770489140637[113] = 0;
   out_8075335770489140637[114] = 1;
   out_8075335770489140637[115] = 0;
   out_8075335770489140637[116] = 0;
   out_8075335770489140637[117] = 0;
   out_8075335770489140637[118] = 0;
   out_8075335770489140637[119] = 0;
   out_8075335770489140637[120] = 0;
   out_8075335770489140637[121] = 0;
   out_8075335770489140637[122] = 0;
   out_8075335770489140637[123] = 0;
   out_8075335770489140637[124] = 0;
   out_8075335770489140637[125] = 0;
   out_8075335770489140637[126] = 0;
   out_8075335770489140637[127] = 0;
   out_8075335770489140637[128] = 0;
   out_8075335770489140637[129] = 0;
   out_8075335770489140637[130] = 0;
   out_8075335770489140637[131] = 0;
   out_8075335770489140637[132] = 0;
   out_8075335770489140637[133] = 1;
   out_8075335770489140637[134] = 0;
   out_8075335770489140637[135] = 0;
   out_8075335770489140637[136] = 0;
   out_8075335770489140637[137] = 0;
   out_8075335770489140637[138] = 0;
   out_8075335770489140637[139] = 0;
   out_8075335770489140637[140] = 0;
   out_8075335770489140637[141] = 0;
   out_8075335770489140637[142] = 0;
   out_8075335770489140637[143] = 0;
   out_8075335770489140637[144] = 0;
   out_8075335770489140637[145] = 0;
   out_8075335770489140637[146] = 0;
   out_8075335770489140637[147] = 0;
   out_8075335770489140637[148] = 0;
   out_8075335770489140637[149] = 0;
   out_8075335770489140637[150] = 0;
   out_8075335770489140637[151] = 0;
   out_8075335770489140637[152] = 1;
   out_8075335770489140637[153] = 0;
   out_8075335770489140637[154] = 0;
   out_8075335770489140637[155] = 0;
   out_8075335770489140637[156] = 0;
   out_8075335770489140637[157] = 0;
   out_8075335770489140637[158] = 0;
   out_8075335770489140637[159] = 0;
   out_8075335770489140637[160] = 0;
   out_8075335770489140637[161] = 0;
   out_8075335770489140637[162] = 0;
   out_8075335770489140637[163] = 0;
   out_8075335770489140637[164] = 0;
   out_8075335770489140637[165] = 0;
   out_8075335770489140637[166] = 0;
   out_8075335770489140637[167] = 0;
   out_8075335770489140637[168] = 0;
   out_8075335770489140637[169] = 0;
   out_8075335770489140637[170] = 0;
   out_8075335770489140637[171] = 1;
   out_8075335770489140637[172] = 0;
   out_8075335770489140637[173] = 0;
   out_8075335770489140637[174] = 0;
   out_8075335770489140637[175] = 0;
   out_8075335770489140637[176] = 0;
   out_8075335770489140637[177] = 0;
   out_8075335770489140637[178] = 0;
   out_8075335770489140637[179] = 0;
   out_8075335770489140637[180] = 0;
   out_8075335770489140637[181] = 0;
   out_8075335770489140637[182] = 0;
   out_8075335770489140637[183] = 0;
   out_8075335770489140637[184] = 0;
   out_8075335770489140637[185] = 0;
   out_8075335770489140637[186] = 0;
   out_8075335770489140637[187] = 0;
   out_8075335770489140637[188] = 0;
   out_8075335770489140637[189] = 0;
   out_8075335770489140637[190] = 1;
   out_8075335770489140637[191] = 0;
   out_8075335770489140637[192] = 0;
   out_8075335770489140637[193] = 0;
   out_8075335770489140637[194] = 0;
   out_8075335770489140637[195] = 0;
   out_8075335770489140637[196] = 0;
   out_8075335770489140637[197] = 0;
   out_8075335770489140637[198] = 0;
   out_8075335770489140637[199] = 0;
   out_8075335770489140637[200] = 0;
   out_8075335770489140637[201] = 0;
   out_8075335770489140637[202] = 0;
   out_8075335770489140637[203] = 0;
   out_8075335770489140637[204] = 0;
   out_8075335770489140637[205] = 0;
   out_8075335770489140637[206] = 0;
   out_8075335770489140637[207] = 0;
   out_8075335770489140637[208] = 0;
   out_8075335770489140637[209] = 1;
   out_8075335770489140637[210] = 0;
   out_8075335770489140637[211] = 0;
   out_8075335770489140637[212] = 0;
   out_8075335770489140637[213] = 0;
   out_8075335770489140637[214] = 0;
   out_8075335770489140637[215] = 0;
   out_8075335770489140637[216] = 0;
   out_8075335770489140637[217] = 0;
   out_8075335770489140637[218] = 0;
   out_8075335770489140637[219] = 0;
   out_8075335770489140637[220] = 0;
   out_8075335770489140637[221] = 0;
   out_8075335770489140637[222] = 0;
   out_8075335770489140637[223] = 0;
   out_8075335770489140637[224] = 0;
   out_8075335770489140637[225] = 0;
   out_8075335770489140637[226] = 0;
   out_8075335770489140637[227] = 0;
   out_8075335770489140637[228] = 1;
   out_8075335770489140637[229] = 0;
   out_8075335770489140637[230] = 0;
   out_8075335770489140637[231] = 0;
   out_8075335770489140637[232] = 0;
   out_8075335770489140637[233] = 0;
   out_8075335770489140637[234] = 0;
   out_8075335770489140637[235] = 0;
   out_8075335770489140637[236] = 0;
   out_8075335770489140637[237] = 0;
   out_8075335770489140637[238] = 0;
   out_8075335770489140637[239] = 0;
   out_8075335770489140637[240] = 0;
   out_8075335770489140637[241] = 0;
   out_8075335770489140637[242] = 0;
   out_8075335770489140637[243] = 0;
   out_8075335770489140637[244] = 0;
   out_8075335770489140637[245] = 0;
   out_8075335770489140637[246] = 0;
   out_8075335770489140637[247] = 1;
   out_8075335770489140637[248] = 0;
   out_8075335770489140637[249] = 0;
   out_8075335770489140637[250] = 0;
   out_8075335770489140637[251] = 0;
   out_8075335770489140637[252] = 0;
   out_8075335770489140637[253] = 0;
   out_8075335770489140637[254] = 0;
   out_8075335770489140637[255] = 0;
   out_8075335770489140637[256] = 0;
   out_8075335770489140637[257] = 0;
   out_8075335770489140637[258] = 0;
   out_8075335770489140637[259] = 0;
   out_8075335770489140637[260] = 0;
   out_8075335770489140637[261] = 0;
   out_8075335770489140637[262] = 0;
   out_8075335770489140637[263] = 0;
   out_8075335770489140637[264] = 0;
   out_8075335770489140637[265] = 0;
   out_8075335770489140637[266] = 1;
   out_8075335770489140637[267] = 0;
   out_8075335770489140637[268] = 0;
   out_8075335770489140637[269] = 0;
   out_8075335770489140637[270] = 0;
   out_8075335770489140637[271] = 0;
   out_8075335770489140637[272] = 0;
   out_8075335770489140637[273] = 0;
   out_8075335770489140637[274] = 0;
   out_8075335770489140637[275] = 0;
   out_8075335770489140637[276] = 0;
   out_8075335770489140637[277] = 0;
   out_8075335770489140637[278] = 0;
   out_8075335770489140637[279] = 0;
   out_8075335770489140637[280] = 0;
   out_8075335770489140637[281] = 0;
   out_8075335770489140637[282] = 0;
   out_8075335770489140637[283] = 0;
   out_8075335770489140637[284] = 0;
   out_8075335770489140637[285] = 1;
   out_8075335770489140637[286] = 0;
   out_8075335770489140637[287] = 0;
   out_8075335770489140637[288] = 0;
   out_8075335770489140637[289] = 0;
   out_8075335770489140637[290] = 0;
   out_8075335770489140637[291] = 0;
   out_8075335770489140637[292] = 0;
   out_8075335770489140637[293] = 0;
   out_8075335770489140637[294] = 0;
   out_8075335770489140637[295] = 0;
   out_8075335770489140637[296] = 0;
   out_8075335770489140637[297] = 0;
   out_8075335770489140637[298] = 0;
   out_8075335770489140637[299] = 0;
   out_8075335770489140637[300] = 0;
   out_8075335770489140637[301] = 0;
   out_8075335770489140637[302] = 0;
   out_8075335770489140637[303] = 0;
   out_8075335770489140637[304] = 1;
   out_8075335770489140637[305] = 0;
   out_8075335770489140637[306] = 0;
   out_8075335770489140637[307] = 0;
   out_8075335770489140637[308] = 0;
   out_8075335770489140637[309] = 0;
   out_8075335770489140637[310] = 0;
   out_8075335770489140637[311] = 0;
   out_8075335770489140637[312] = 0;
   out_8075335770489140637[313] = 0;
   out_8075335770489140637[314] = 0;
   out_8075335770489140637[315] = 0;
   out_8075335770489140637[316] = 0;
   out_8075335770489140637[317] = 0;
   out_8075335770489140637[318] = 0;
   out_8075335770489140637[319] = 0;
   out_8075335770489140637[320] = 0;
   out_8075335770489140637[321] = 0;
   out_8075335770489140637[322] = 0;
   out_8075335770489140637[323] = 1;
}
void h_4(double *state, double *unused, double *out_3181184218861517088) {
   out_3181184218861517088[0] = state[6] + state[9];
   out_3181184218861517088[1] = state[7] + state[10];
   out_3181184218861517088[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_6784719679909297658) {
   out_6784719679909297658[0] = 0;
   out_6784719679909297658[1] = 0;
   out_6784719679909297658[2] = 0;
   out_6784719679909297658[3] = 0;
   out_6784719679909297658[4] = 0;
   out_6784719679909297658[5] = 0;
   out_6784719679909297658[6] = 1;
   out_6784719679909297658[7] = 0;
   out_6784719679909297658[8] = 0;
   out_6784719679909297658[9] = 1;
   out_6784719679909297658[10] = 0;
   out_6784719679909297658[11] = 0;
   out_6784719679909297658[12] = 0;
   out_6784719679909297658[13] = 0;
   out_6784719679909297658[14] = 0;
   out_6784719679909297658[15] = 0;
   out_6784719679909297658[16] = 0;
   out_6784719679909297658[17] = 0;
   out_6784719679909297658[18] = 0;
   out_6784719679909297658[19] = 0;
   out_6784719679909297658[20] = 0;
   out_6784719679909297658[21] = 0;
   out_6784719679909297658[22] = 0;
   out_6784719679909297658[23] = 0;
   out_6784719679909297658[24] = 0;
   out_6784719679909297658[25] = 1;
   out_6784719679909297658[26] = 0;
   out_6784719679909297658[27] = 0;
   out_6784719679909297658[28] = 1;
   out_6784719679909297658[29] = 0;
   out_6784719679909297658[30] = 0;
   out_6784719679909297658[31] = 0;
   out_6784719679909297658[32] = 0;
   out_6784719679909297658[33] = 0;
   out_6784719679909297658[34] = 0;
   out_6784719679909297658[35] = 0;
   out_6784719679909297658[36] = 0;
   out_6784719679909297658[37] = 0;
   out_6784719679909297658[38] = 0;
   out_6784719679909297658[39] = 0;
   out_6784719679909297658[40] = 0;
   out_6784719679909297658[41] = 0;
   out_6784719679909297658[42] = 0;
   out_6784719679909297658[43] = 0;
   out_6784719679909297658[44] = 1;
   out_6784719679909297658[45] = 0;
   out_6784719679909297658[46] = 0;
   out_6784719679909297658[47] = 1;
   out_6784719679909297658[48] = 0;
   out_6784719679909297658[49] = 0;
   out_6784719679909297658[50] = 0;
   out_6784719679909297658[51] = 0;
   out_6784719679909297658[52] = 0;
   out_6784719679909297658[53] = 0;
}
void h_10(double *state, double *unused, double *out_2256141700394740444) {
   out_2256141700394740444[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_2256141700394740444[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_2256141700394740444[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_271565957382003015) {
   out_271565957382003015[0] = 0;
   out_271565957382003015[1] = 9.8100000000000005*cos(state[1]);
   out_271565957382003015[2] = 0;
   out_271565957382003015[3] = 0;
   out_271565957382003015[4] = -state[8];
   out_271565957382003015[5] = state[7];
   out_271565957382003015[6] = 0;
   out_271565957382003015[7] = state[5];
   out_271565957382003015[8] = -state[4];
   out_271565957382003015[9] = 0;
   out_271565957382003015[10] = 0;
   out_271565957382003015[11] = 0;
   out_271565957382003015[12] = 1;
   out_271565957382003015[13] = 0;
   out_271565957382003015[14] = 0;
   out_271565957382003015[15] = 1;
   out_271565957382003015[16] = 0;
   out_271565957382003015[17] = 0;
   out_271565957382003015[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_271565957382003015[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_271565957382003015[20] = 0;
   out_271565957382003015[21] = state[8];
   out_271565957382003015[22] = 0;
   out_271565957382003015[23] = -state[6];
   out_271565957382003015[24] = -state[5];
   out_271565957382003015[25] = 0;
   out_271565957382003015[26] = state[3];
   out_271565957382003015[27] = 0;
   out_271565957382003015[28] = 0;
   out_271565957382003015[29] = 0;
   out_271565957382003015[30] = 0;
   out_271565957382003015[31] = 1;
   out_271565957382003015[32] = 0;
   out_271565957382003015[33] = 0;
   out_271565957382003015[34] = 1;
   out_271565957382003015[35] = 0;
   out_271565957382003015[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_271565957382003015[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_271565957382003015[38] = 0;
   out_271565957382003015[39] = -state[7];
   out_271565957382003015[40] = state[6];
   out_271565957382003015[41] = 0;
   out_271565957382003015[42] = state[4];
   out_271565957382003015[43] = -state[3];
   out_271565957382003015[44] = 0;
   out_271565957382003015[45] = 0;
   out_271565957382003015[46] = 0;
   out_271565957382003015[47] = 0;
   out_271565957382003015[48] = 0;
   out_271565957382003015[49] = 0;
   out_271565957382003015[50] = 1;
   out_271565957382003015[51] = 0;
   out_271565957382003015[52] = 0;
   out_271565957382003015[53] = 1;
}
void h_13(double *state, double *unused, double *out_5753684260181993321) {
   out_5753684260181993321[0] = state[3];
   out_5753684260181993321[1] = state[4];
   out_5753684260181993321[2] = state[5];
}
void H_13(double *state, double *unused, double *out_3572445854576964857) {
   out_3572445854576964857[0] = 0;
   out_3572445854576964857[1] = 0;
   out_3572445854576964857[2] = 0;
   out_3572445854576964857[3] = 1;
   out_3572445854576964857[4] = 0;
   out_3572445854576964857[5] = 0;
   out_3572445854576964857[6] = 0;
   out_3572445854576964857[7] = 0;
   out_3572445854576964857[8] = 0;
   out_3572445854576964857[9] = 0;
   out_3572445854576964857[10] = 0;
   out_3572445854576964857[11] = 0;
   out_3572445854576964857[12] = 0;
   out_3572445854576964857[13] = 0;
   out_3572445854576964857[14] = 0;
   out_3572445854576964857[15] = 0;
   out_3572445854576964857[16] = 0;
   out_3572445854576964857[17] = 0;
   out_3572445854576964857[18] = 0;
   out_3572445854576964857[19] = 0;
   out_3572445854576964857[20] = 0;
   out_3572445854576964857[21] = 0;
   out_3572445854576964857[22] = 1;
   out_3572445854576964857[23] = 0;
   out_3572445854576964857[24] = 0;
   out_3572445854576964857[25] = 0;
   out_3572445854576964857[26] = 0;
   out_3572445854576964857[27] = 0;
   out_3572445854576964857[28] = 0;
   out_3572445854576964857[29] = 0;
   out_3572445854576964857[30] = 0;
   out_3572445854576964857[31] = 0;
   out_3572445854576964857[32] = 0;
   out_3572445854576964857[33] = 0;
   out_3572445854576964857[34] = 0;
   out_3572445854576964857[35] = 0;
   out_3572445854576964857[36] = 0;
   out_3572445854576964857[37] = 0;
   out_3572445854576964857[38] = 0;
   out_3572445854576964857[39] = 0;
   out_3572445854576964857[40] = 0;
   out_3572445854576964857[41] = 1;
   out_3572445854576964857[42] = 0;
   out_3572445854576964857[43] = 0;
   out_3572445854576964857[44] = 0;
   out_3572445854576964857[45] = 0;
   out_3572445854576964857[46] = 0;
   out_3572445854576964857[47] = 0;
   out_3572445854576964857[48] = 0;
   out_3572445854576964857[49] = 0;
   out_3572445854576964857[50] = 0;
   out_3572445854576964857[51] = 0;
   out_3572445854576964857[52] = 0;
   out_3572445854576964857[53] = 0;
}
void h_14(double *state, double *unused, double *out_4183173073051920193) {
   out_4183173073051920193[0] = state[6];
   out_4183173073051920193[1] = state[7];
   out_4183173073051920193[2] = state[8];
}
void H_14(double *state, double *unused, double *out_8579235961504881662) {
   out_8579235961504881662[0] = 0;
   out_8579235961504881662[1] = 0;
   out_8579235961504881662[2] = 0;
   out_8579235961504881662[3] = 0;
   out_8579235961504881662[4] = 0;
   out_8579235961504881662[5] = 0;
   out_8579235961504881662[6] = 1;
   out_8579235961504881662[7] = 0;
   out_8579235961504881662[8] = 0;
   out_8579235961504881662[9] = 0;
   out_8579235961504881662[10] = 0;
   out_8579235961504881662[11] = 0;
   out_8579235961504881662[12] = 0;
   out_8579235961504881662[13] = 0;
   out_8579235961504881662[14] = 0;
   out_8579235961504881662[15] = 0;
   out_8579235961504881662[16] = 0;
   out_8579235961504881662[17] = 0;
   out_8579235961504881662[18] = 0;
   out_8579235961504881662[19] = 0;
   out_8579235961504881662[20] = 0;
   out_8579235961504881662[21] = 0;
   out_8579235961504881662[22] = 0;
   out_8579235961504881662[23] = 0;
   out_8579235961504881662[24] = 0;
   out_8579235961504881662[25] = 1;
   out_8579235961504881662[26] = 0;
   out_8579235961504881662[27] = 0;
   out_8579235961504881662[28] = 0;
   out_8579235961504881662[29] = 0;
   out_8579235961504881662[30] = 0;
   out_8579235961504881662[31] = 0;
   out_8579235961504881662[32] = 0;
   out_8579235961504881662[33] = 0;
   out_8579235961504881662[34] = 0;
   out_8579235961504881662[35] = 0;
   out_8579235961504881662[36] = 0;
   out_8579235961504881662[37] = 0;
   out_8579235961504881662[38] = 0;
   out_8579235961504881662[39] = 0;
   out_8579235961504881662[40] = 0;
   out_8579235961504881662[41] = 0;
   out_8579235961504881662[42] = 0;
   out_8579235961504881662[43] = 0;
   out_8579235961504881662[44] = 1;
   out_8579235961504881662[45] = 0;
   out_8579235961504881662[46] = 0;
   out_8579235961504881662[47] = 0;
   out_8579235961504881662[48] = 0;
   out_8579235961504881662[49] = 0;
   out_8579235961504881662[50] = 0;
   out_8579235961504881662[51] = 0;
   out_8579235961504881662[52] = 0;
   out_8579235961504881662[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_8244834270034669277) {
  err_fun(nom_x, delta_x, out_8244834270034669277);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5687769365300631080) {
  inv_err_fun(nom_x, true_x, out_5687769365300631080);
}
void pose_H_mod_fun(double *state, double *out_5729207129571741933) {
  H_mod_fun(state, out_5729207129571741933);
}
void pose_f_fun(double *state, double dt, double *out_5327017859701626059) {
  f_fun(state,  dt, out_5327017859701626059);
}
void pose_F_fun(double *state, double dt, double *out_8075335770489140637) {
  F_fun(state,  dt, out_8075335770489140637);
}
void pose_h_4(double *state, double *unused, double *out_3181184218861517088) {
  h_4(state, unused, out_3181184218861517088);
}
void pose_H_4(double *state, double *unused, double *out_6784719679909297658) {
  H_4(state, unused, out_6784719679909297658);
}
void pose_h_10(double *state, double *unused, double *out_2256141700394740444) {
  h_10(state, unused, out_2256141700394740444);
}
void pose_H_10(double *state, double *unused, double *out_271565957382003015) {
  H_10(state, unused, out_271565957382003015);
}
void pose_h_13(double *state, double *unused, double *out_5753684260181993321) {
  h_13(state, unused, out_5753684260181993321);
}
void pose_H_13(double *state, double *unused, double *out_3572445854576964857) {
  H_13(state, unused, out_3572445854576964857);
}
void pose_h_14(double *state, double *unused, double *out_4183173073051920193) {
  h_14(state, unused, out_4183173073051920193);
}
void pose_H_14(double *state, double *unused, double *out_8579235961504881662) {
  H_14(state, unused, out_8579235961504881662);
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
