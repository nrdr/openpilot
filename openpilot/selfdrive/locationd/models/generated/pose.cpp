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
void err_fun(double *nom_x, double *delta_x, double *out_4907159739794112728) {
   out_4907159739794112728[0] = delta_x[0] + nom_x[0];
   out_4907159739794112728[1] = delta_x[1] + nom_x[1];
   out_4907159739794112728[2] = delta_x[2] + nom_x[2];
   out_4907159739794112728[3] = delta_x[3] + nom_x[3];
   out_4907159739794112728[4] = delta_x[4] + nom_x[4];
   out_4907159739794112728[5] = delta_x[5] + nom_x[5];
   out_4907159739794112728[6] = delta_x[6] + nom_x[6];
   out_4907159739794112728[7] = delta_x[7] + nom_x[7];
   out_4907159739794112728[8] = delta_x[8] + nom_x[8];
   out_4907159739794112728[9] = delta_x[9] + nom_x[9];
   out_4907159739794112728[10] = delta_x[10] + nom_x[10];
   out_4907159739794112728[11] = delta_x[11] + nom_x[11];
   out_4907159739794112728[12] = delta_x[12] + nom_x[12];
   out_4907159739794112728[13] = delta_x[13] + nom_x[13];
   out_4907159739794112728[14] = delta_x[14] + nom_x[14];
   out_4907159739794112728[15] = delta_x[15] + nom_x[15];
   out_4907159739794112728[16] = delta_x[16] + nom_x[16];
   out_4907159739794112728[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_9092805515226665715) {
   out_9092805515226665715[0] = -nom_x[0] + true_x[0];
   out_9092805515226665715[1] = -nom_x[1] + true_x[1];
   out_9092805515226665715[2] = -nom_x[2] + true_x[2];
   out_9092805515226665715[3] = -nom_x[3] + true_x[3];
   out_9092805515226665715[4] = -nom_x[4] + true_x[4];
   out_9092805515226665715[5] = -nom_x[5] + true_x[5];
   out_9092805515226665715[6] = -nom_x[6] + true_x[6];
   out_9092805515226665715[7] = -nom_x[7] + true_x[7];
   out_9092805515226665715[8] = -nom_x[8] + true_x[8];
   out_9092805515226665715[9] = -nom_x[9] + true_x[9];
   out_9092805515226665715[10] = -nom_x[10] + true_x[10];
   out_9092805515226665715[11] = -nom_x[11] + true_x[11];
   out_9092805515226665715[12] = -nom_x[12] + true_x[12];
   out_9092805515226665715[13] = -nom_x[13] + true_x[13];
   out_9092805515226665715[14] = -nom_x[14] + true_x[14];
   out_9092805515226665715[15] = -nom_x[15] + true_x[15];
   out_9092805515226665715[16] = -nom_x[16] + true_x[16];
   out_9092805515226665715[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_8838383476203492205) {
   out_8838383476203492205[0] = 1.0;
   out_8838383476203492205[1] = 0.0;
   out_8838383476203492205[2] = 0.0;
   out_8838383476203492205[3] = 0.0;
   out_8838383476203492205[4] = 0.0;
   out_8838383476203492205[5] = 0.0;
   out_8838383476203492205[6] = 0.0;
   out_8838383476203492205[7] = 0.0;
   out_8838383476203492205[8] = 0.0;
   out_8838383476203492205[9] = 0.0;
   out_8838383476203492205[10] = 0.0;
   out_8838383476203492205[11] = 0.0;
   out_8838383476203492205[12] = 0.0;
   out_8838383476203492205[13] = 0.0;
   out_8838383476203492205[14] = 0.0;
   out_8838383476203492205[15] = 0.0;
   out_8838383476203492205[16] = 0.0;
   out_8838383476203492205[17] = 0.0;
   out_8838383476203492205[18] = 0.0;
   out_8838383476203492205[19] = 1.0;
   out_8838383476203492205[20] = 0.0;
   out_8838383476203492205[21] = 0.0;
   out_8838383476203492205[22] = 0.0;
   out_8838383476203492205[23] = 0.0;
   out_8838383476203492205[24] = 0.0;
   out_8838383476203492205[25] = 0.0;
   out_8838383476203492205[26] = 0.0;
   out_8838383476203492205[27] = 0.0;
   out_8838383476203492205[28] = 0.0;
   out_8838383476203492205[29] = 0.0;
   out_8838383476203492205[30] = 0.0;
   out_8838383476203492205[31] = 0.0;
   out_8838383476203492205[32] = 0.0;
   out_8838383476203492205[33] = 0.0;
   out_8838383476203492205[34] = 0.0;
   out_8838383476203492205[35] = 0.0;
   out_8838383476203492205[36] = 0.0;
   out_8838383476203492205[37] = 0.0;
   out_8838383476203492205[38] = 1.0;
   out_8838383476203492205[39] = 0.0;
   out_8838383476203492205[40] = 0.0;
   out_8838383476203492205[41] = 0.0;
   out_8838383476203492205[42] = 0.0;
   out_8838383476203492205[43] = 0.0;
   out_8838383476203492205[44] = 0.0;
   out_8838383476203492205[45] = 0.0;
   out_8838383476203492205[46] = 0.0;
   out_8838383476203492205[47] = 0.0;
   out_8838383476203492205[48] = 0.0;
   out_8838383476203492205[49] = 0.0;
   out_8838383476203492205[50] = 0.0;
   out_8838383476203492205[51] = 0.0;
   out_8838383476203492205[52] = 0.0;
   out_8838383476203492205[53] = 0.0;
   out_8838383476203492205[54] = 0.0;
   out_8838383476203492205[55] = 0.0;
   out_8838383476203492205[56] = 0.0;
   out_8838383476203492205[57] = 1.0;
   out_8838383476203492205[58] = 0.0;
   out_8838383476203492205[59] = 0.0;
   out_8838383476203492205[60] = 0.0;
   out_8838383476203492205[61] = 0.0;
   out_8838383476203492205[62] = 0.0;
   out_8838383476203492205[63] = 0.0;
   out_8838383476203492205[64] = 0.0;
   out_8838383476203492205[65] = 0.0;
   out_8838383476203492205[66] = 0.0;
   out_8838383476203492205[67] = 0.0;
   out_8838383476203492205[68] = 0.0;
   out_8838383476203492205[69] = 0.0;
   out_8838383476203492205[70] = 0.0;
   out_8838383476203492205[71] = 0.0;
   out_8838383476203492205[72] = 0.0;
   out_8838383476203492205[73] = 0.0;
   out_8838383476203492205[74] = 0.0;
   out_8838383476203492205[75] = 0.0;
   out_8838383476203492205[76] = 1.0;
   out_8838383476203492205[77] = 0.0;
   out_8838383476203492205[78] = 0.0;
   out_8838383476203492205[79] = 0.0;
   out_8838383476203492205[80] = 0.0;
   out_8838383476203492205[81] = 0.0;
   out_8838383476203492205[82] = 0.0;
   out_8838383476203492205[83] = 0.0;
   out_8838383476203492205[84] = 0.0;
   out_8838383476203492205[85] = 0.0;
   out_8838383476203492205[86] = 0.0;
   out_8838383476203492205[87] = 0.0;
   out_8838383476203492205[88] = 0.0;
   out_8838383476203492205[89] = 0.0;
   out_8838383476203492205[90] = 0.0;
   out_8838383476203492205[91] = 0.0;
   out_8838383476203492205[92] = 0.0;
   out_8838383476203492205[93] = 0.0;
   out_8838383476203492205[94] = 0.0;
   out_8838383476203492205[95] = 1.0;
   out_8838383476203492205[96] = 0.0;
   out_8838383476203492205[97] = 0.0;
   out_8838383476203492205[98] = 0.0;
   out_8838383476203492205[99] = 0.0;
   out_8838383476203492205[100] = 0.0;
   out_8838383476203492205[101] = 0.0;
   out_8838383476203492205[102] = 0.0;
   out_8838383476203492205[103] = 0.0;
   out_8838383476203492205[104] = 0.0;
   out_8838383476203492205[105] = 0.0;
   out_8838383476203492205[106] = 0.0;
   out_8838383476203492205[107] = 0.0;
   out_8838383476203492205[108] = 0.0;
   out_8838383476203492205[109] = 0.0;
   out_8838383476203492205[110] = 0.0;
   out_8838383476203492205[111] = 0.0;
   out_8838383476203492205[112] = 0.0;
   out_8838383476203492205[113] = 0.0;
   out_8838383476203492205[114] = 1.0;
   out_8838383476203492205[115] = 0.0;
   out_8838383476203492205[116] = 0.0;
   out_8838383476203492205[117] = 0.0;
   out_8838383476203492205[118] = 0.0;
   out_8838383476203492205[119] = 0.0;
   out_8838383476203492205[120] = 0.0;
   out_8838383476203492205[121] = 0.0;
   out_8838383476203492205[122] = 0.0;
   out_8838383476203492205[123] = 0.0;
   out_8838383476203492205[124] = 0.0;
   out_8838383476203492205[125] = 0.0;
   out_8838383476203492205[126] = 0.0;
   out_8838383476203492205[127] = 0.0;
   out_8838383476203492205[128] = 0.0;
   out_8838383476203492205[129] = 0.0;
   out_8838383476203492205[130] = 0.0;
   out_8838383476203492205[131] = 0.0;
   out_8838383476203492205[132] = 0.0;
   out_8838383476203492205[133] = 1.0;
   out_8838383476203492205[134] = 0.0;
   out_8838383476203492205[135] = 0.0;
   out_8838383476203492205[136] = 0.0;
   out_8838383476203492205[137] = 0.0;
   out_8838383476203492205[138] = 0.0;
   out_8838383476203492205[139] = 0.0;
   out_8838383476203492205[140] = 0.0;
   out_8838383476203492205[141] = 0.0;
   out_8838383476203492205[142] = 0.0;
   out_8838383476203492205[143] = 0.0;
   out_8838383476203492205[144] = 0.0;
   out_8838383476203492205[145] = 0.0;
   out_8838383476203492205[146] = 0.0;
   out_8838383476203492205[147] = 0.0;
   out_8838383476203492205[148] = 0.0;
   out_8838383476203492205[149] = 0.0;
   out_8838383476203492205[150] = 0.0;
   out_8838383476203492205[151] = 0.0;
   out_8838383476203492205[152] = 1.0;
   out_8838383476203492205[153] = 0.0;
   out_8838383476203492205[154] = 0.0;
   out_8838383476203492205[155] = 0.0;
   out_8838383476203492205[156] = 0.0;
   out_8838383476203492205[157] = 0.0;
   out_8838383476203492205[158] = 0.0;
   out_8838383476203492205[159] = 0.0;
   out_8838383476203492205[160] = 0.0;
   out_8838383476203492205[161] = 0.0;
   out_8838383476203492205[162] = 0.0;
   out_8838383476203492205[163] = 0.0;
   out_8838383476203492205[164] = 0.0;
   out_8838383476203492205[165] = 0.0;
   out_8838383476203492205[166] = 0.0;
   out_8838383476203492205[167] = 0.0;
   out_8838383476203492205[168] = 0.0;
   out_8838383476203492205[169] = 0.0;
   out_8838383476203492205[170] = 0.0;
   out_8838383476203492205[171] = 1.0;
   out_8838383476203492205[172] = 0.0;
   out_8838383476203492205[173] = 0.0;
   out_8838383476203492205[174] = 0.0;
   out_8838383476203492205[175] = 0.0;
   out_8838383476203492205[176] = 0.0;
   out_8838383476203492205[177] = 0.0;
   out_8838383476203492205[178] = 0.0;
   out_8838383476203492205[179] = 0.0;
   out_8838383476203492205[180] = 0.0;
   out_8838383476203492205[181] = 0.0;
   out_8838383476203492205[182] = 0.0;
   out_8838383476203492205[183] = 0.0;
   out_8838383476203492205[184] = 0.0;
   out_8838383476203492205[185] = 0.0;
   out_8838383476203492205[186] = 0.0;
   out_8838383476203492205[187] = 0.0;
   out_8838383476203492205[188] = 0.0;
   out_8838383476203492205[189] = 0.0;
   out_8838383476203492205[190] = 1.0;
   out_8838383476203492205[191] = 0.0;
   out_8838383476203492205[192] = 0.0;
   out_8838383476203492205[193] = 0.0;
   out_8838383476203492205[194] = 0.0;
   out_8838383476203492205[195] = 0.0;
   out_8838383476203492205[196] = 0.0;
   out_8838383476203492205[197] = 0.0;
   out_8838383476203492205[198] = 0.0;
   out_8838383476203492205[199] = 0.0;
   out_8838383476203492205[200] = 0.0;
   out_8838383476203492205[201] = 0.0;
   out_8838383476203492205[202] = 0.0;
   out_8838383476203492205[203] = 0.0;
   out_8838383476203492205[204] = 0.0;
   out_8838383476203492205[205] = 0.0;
   out_8838383476203492205[206] = 0.0;
   out_8838383476203492205[207] = 0.0;
   out_8838383476203492205[208] = 0.0;
   out_8838383476203492205[209] = 1.0;
   out_8838383476203492205[210] = 0.0;
   out_8838383476203492205[211] = 0.0;
   out_8838383476203492205[212] = 0.0;
   out_8838383476203492205[213] = 0.0;
   out_8838383476203492205[214] = 0.0;
   out_8838383476203492205[215] = 0.0;
   out_8838383476203492205[216] = 0.0;
   out_8838383476203492205[217] = 0.0;
   out_8838383476203492205[218] = 0.0;
   out_8838383476203492205[219] = 0.0;
   out_8838383476203492205[220] = 0.0;
   out_8838383476203492205[221] = 0.0;
   out_8838383476203492205[222] = 0.0;
   out_8838383476203492205[223] = 0.0;
   out_8838383476203492205[224] = 0.0;
   out_8838383476203492205[225] = 0.0;
   out_8838383476203492205[226] = 0.0;
   out_8838383476203492205[227] = 0.0;
   out_8838383476203492205[228] = 1.0;
   out_8838383476203492205[229] = 0.0;
   out_8838383476203492205[230] = 0.0;
   out_8838383476203492205[231] = 0.0;
   out_8838383476203492205[232] = 0.0;
   out_8838383476203492205[233] = 0.0;
   out_8838383476203492205[234] = 0.0;
   out_8838383476203492205[235] = 0.0;
   out_8838383476203492205[236] = 0.0;
   out_8838383476203492205[237] = 0.0;
   out_8838383476203492205[238] = 0.0;
   out_8838383476203492205[239] = 0.0;
   out_8838383476203492205[240] = 0.0;
   out_8838383476203492205[241] = 0.0;
   out_8838383476203492205[242] = 0.0;
   out_8838383476203492205[243] = 0.0;
   out_8838383476203492205[244] = 0.0;
   out_8838383476203492205[245] = 0.0;
   out_8838383476203492205[246] = 0.0;
   out_8838383476203492205[247] = 1.0;
   out_8838383476203492205[248] = 0.0;
   out_8838383476203492205[249] = 0.0;
   out_8838383476203492205[250] = 0.0;
   out_8838383476203492205[251] = 0.0;
   out_8838383476203492205[252] = 0.0;
   out_8838383476203492205[253] = 0.0;
   out_8838383476203492205[254] = 0.0;
   out_8838383476203492205[255] = 0.0;
   out_8838383476203492205[256] = 0.0;
   out_8838383476203492205[257] = 0.0;
   out_8838383476203492205[258] = 0.0;
   out_8838383476203492205[259] = 0.0;
   out_8838383476203492205[260] = 0.0;
   out_8838383476203492205[261] = 0.0;
   out_8838383476203492205[262] = 0.0;
   out_8838383476203492205[263] = 0.0;
   out_8838383476203492205[264] = 0.0;
   out_8838383476203492205[265] = 0.0;
   out_8838383476203492205[266] = 1.0;
   out_8838383476203492205[267] = 0.0;
   out_8838383476203492205[268] = 0.0;
   out_8838383476203492205[269] = 0.0;
   out_8838383476203492205[270] = 0.0;
   out_8838383476203492205[271] = 0.0;
   out_8838383476203492205[272] = 0.0;
   out_8838383476203492205[273] = 0.0;
   out_8838383476203492205[274] = 0.0;
   out_8838383476203492205[275] = 0.0;
   out_8838383476203492205[276] = 0.0;
   out_8838383476203492205[277] = 0.0;
   out_8838383476203492205[278] = 0.0;
   out_8838383476203492205[279] = 0.0;
   out_8838383476203492205[280] = 0.0;
   out_8838383476203492205[281] = 0.0;
   out_8838383476203492205[282] = 0.0;
   out_8838383476203492205[283] = 0.0;
   out_8838383476203492205[284] = 0.0;
   out_8838383476203492205[285] = 1.0;
   out_8838383476203492205[286] = 0.0;
   out_8838383476203492205[287] = 0.0;
   out_8838383476203492205[288] = 0.0;
   out_8838383476203492205[289] = 0.0;
   out_8838383476203492205[290] = 0.0;
   out_8838383476203492205[291] = 0.0;
   out_8838383476203492205[292] = 0.0;
   out_8838383476203492205[293] = 0.0;
   out_8838383476203492205[294] = 0.0;
   out_8838383476203492205[295] = 0.0;
   out_8838383476203492205[296] = 0.0;
   out_8838383476203492205[297] = 0.0;
   out_8838383476203492205[298] = 0.0;
   out_8838383476203492205[299] = 0.0;
   out_8838383476203492205[300] = 0.0;
   out_8838383476203492205[301] = 0.0;
   out_8838383476203492205[302] = 0.0;
   out_8838383476203492205[303] = 0.0;
   out_8838383476203492205[304] = 1.0;
   out_8838383476203492205[305] = 0.0;
   out_8838383476203492205[306] = 0.0;
   out_8838383476203492205[307] = 0.0;
   out_8838383476203492205[308] = 0.0;
   out_8838383476203492205[309] = 0.0;
   out_8838383476203492205[310] = 0.0;
   out_8838383476203492205[311] = 0.0;
   out_8838383476203492205[312] = 0.0;
   out_8838383476203492205[313] = 0.0;
   out_8838383476203492205[314] = 0.0;
   out_8838383476203492205[315] = 0.0;
   out_8838383476203492205[316] = 0.0;
   out_8838383476203492205[317] = 0.0;
   out_8838383476203492205[318] = 0.0;
   out_8838383476203492205[319] = 0.0;
   out_8838383476203492205[320] = 0.0;
   out_8838383476203492205[321] = 0.0;
   out_8838383476203492205[322] = 0.0;
   out_8838383476203492205[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_1879607716571020306) {
   out_1879607716571020306[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_1879607716571020306[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_1879607716571020306[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_1879607716571020306[3] = dt*state[12] + state[3];
   out_1879607716571020306[4] = dt*state[13] + state[4];
   out_1879607716571020306[5] = dt*state[14] + state[5];
   out_1879607716571020306[6] = state[6];
   out_1879607716571020306[7] = state[7];
   out_1879607716571020306[8] = state[8];
   out_1879607716571020306[9] = state[9];
   out_1879607716571020306[10] = state[10];
   out_1879607716571020306[11] = state[11];
   out_1879607716571020306[12] = state[12];
   out_1879607716571020306[13] = state[13];
   out_1879607716571020306[14] = state[14];
   out_1879607716571020306[15] = state[15];
   out_1879607716571020306[16] = state[16];
   out_1879607716571020306[17] = state[17];
}
void F_fun(double *state, double dt, double *out_5462626924138888369) {
   out_5462626924138888369[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5462626924138888369[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5462626924138888369[2] = 0;
   out_5462626924138888369[3] = 0;
   out_5462626924138888369[4] = 0;
   out_5462626924138888369[5] = 0;
   out_5462626924138888369[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5462626924138888369[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5462626924138888369[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_5462626924138888369[9] = 0;
   out_5462626924138888369[10] = 0;
   out_5462626924138888369[11] = 0;
   out_5462626924138888369[12] = 0;
   out_5462626924138888369[13] = 0;
   out_5462626924138888369[14] = 0;
   out_5462626924138888369[15] = 0;
   out_5462626924138888369[16] = 0;
   out_5462626924138888369[17] = 0;
   out_5462626924138888369[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5462626924138888369[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5462626924138888369[20] = 0;
   out_5462626924138888369[21] = 0;
   out_5462626924138888369[22] = 0;
   out_5462626924138888369[23] = 0;
   out_5462626924138888369[24] = 0;
   out_5462626924138888369[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5462626924138888369[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_5462626924138888369[27] = 0;
   out_5462626924138888369[28] = 0;
   out_5462626924138888369[29] = 0;
   out_5462626924138888369[30] = 0;
   out_5462626924138888369[31] = 0;
   out_5462626924138888369[32] = 0;
   out_5462626924138888369[33] = 0;
   out_5462626924138888369[34] = 0;
   out_5462626924138888369[35] = 0;
   out_5462626924138888369[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5462626924138888369[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5462626924138888369[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5462626924138888369[39] = 0;
   out_5462626924138888369[40] = 0;
   out_5462626924138888369[41] = 0;
   out_5462626924138888369[42] = 0;
   out_5462626924138888369[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5462626924138888369[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_5462626924138888369[45] = 0;
   out_5462626924138888369[46] = 0;
   out_5462626924138888369[47] = 0;
   out_5462626924138888369[48] = 0;
   out_5462626924138888369[49] = 0;
   out_5462626924138888369[50] = 0;
   out_5462626924138888369[51] = 0;
   out_5462626924138888369[52] = 0;
   out_5462626924138888369[53] = 0;
   out_5462626924138888369[54] = 0;
   out_5462626924138888369[55] = 0;
   out_5462626924138888369[56] = 0;
   out_5462626924138888369[57] = 1;
   out_5462626924138888369[58] = 0;
   out_5462626924138888369[59] = 0;
   out_5462626924138888369[60] = 0;
   out_5462626924138888369[61] = 0;
   out_5462626924138888369[62] = 0;
   out_5462626924138888369[63] = 0;
   out_5462626924138888369[64] = 0;
   out_5462626924138888369[65] = 0;
   out_5462626924138888369[66] = dt;
   out_5462626924138888369[67] = 0;
   out_5462626924138888369[68] = 0;
   out_5462626924138888369[69] = 0;
   out_5462626924138888369[70] = 0;
   out_5462626924138888369[71] = 0;
   out_5462626924138888369[72] = 0;
   out_5462626924138888369[73] = 0;
   out_5462626924138888369[74] = 0;
   out_5462626924138888369[75] = 0;
   out_5462626924138888369[76] = 1;
   out_5462626924138888369[77] = 0;
   out_5462626924138888369[78] = 0;
   out_5462626924138888369[79] = 0;
   out_5462626924138888369[80] = 0;
   out_5462626924138888369[81] = 0;
   out_5462626924138888369[82] = 0;
   out_5462626924138888369[83] = 0;
   out_5462626924138888369[84] = 0;
   out_5462626924138888369[85] = dt;
   out_5462626924138888369[86] = 0;
   out_5462626924138888369[87] = 0;
   out_5462626924138888369[88] = 0;
   out_5462626924138888369[89] = 0;
   out_5462626924138888369[90] = 0;
   out_5462626924138888369[91] = 0;
   out_5462626924138888369[92] = 0;
   out_5462626924138888369[93] = 0;
   out_5462626924138888369[94] = 0;
   out_5462626924138888369[95] = 1;
   out_5462626924138888369[96] = 0;
   out_5462626924138888369[97] = 0;
   out_5462626924138888369[98] = 0;
   out_5462626924138888369[99] = 0;
   out_5462626924138888369[100] = 0;
   out_5462626924138888369[101] = 0;
   out_5462626924138888369[102] = 0;
   out_5462626924138888369[103] = 0;
   out_5462626924138888369[104] = dt;
   out_5462626924138888369[105] = 0;
   out_5462626924138888369[106] = 0;
   out_5462626924138888369[107] = 0;
   out_5462626924138888369[108] = 0;
   out_5462626924138888369[109] = 0;
   out_5462626924138888369[110] = 0;
   out_5462626924138888369[111] = 0;
   out_5462626924138888369[112] = 0;
   out_5462626924138888369[113] = 0;
   out_5462626924138888369[114] = 1;
   out_5462626924138888369[115] = 0;
   out_5462626924138888369[116] = 0;
   out_5462626924138888369[117] = 0;
   out_5462626924138888369[118] = 0;
   out_5462626924138888369[119] = 0;
   out_5462626924138888369[120] = 0;
   out_5462626924138888369[121] = 0;
   out_5462626924138888369[122] = 0;
   out_5462626924138888369[123] = 0;
   out_5462626924138888369[124] = 0;
   out_5462626924138888369[125] = 0;
   out_5462626924138888369[126] = 0;
   out_5462626924138888369[127] = 0;
   out_5462626924138888369[128] = 0;
   out_5462626924138888369[129] = 0;
   out_5462626924138888369[130] = 0;
   out_5462626924138888369[131] = 0;
   out_5462626924138888369[132] = 0;
   out_5462626924138888369[133] = 1;
   out_5462626924138888369[134] = 0;
   out_5462626924138888369[135] = 0;
   out_5462626924138888369[136] = 0;
   out_5462626924138888369[137] = 0;
   out_5462626924138888369[138] = 0;
   out_5462626924138888369[139] = 0;
   out_5462626924138888369[140] = 0;
   out_5462626924138888369[141] = 0;
   out_5462626924138888369[142] = 0;
   out_5462626924138888369[143] = 0;
   out_5462626924138888369[144] = 0;
   out_5462626924138888369[145] = 0;
   out_5462626924138888369[146] = 0;
   out_5462626924138888369[147] = 0;
   out_5462626924138888369[148] = 0;
   out_5462626924138888369[149] = 0;
   out_5462626924138888369[150] = 0;
   out_5462626924138888369[151] = 0;
   out_5462626924138888369[152] = 1;
   out_5462626924138888369[153] = 0;
   out_5462626924138888369[154] = 0;
   out_5462626924138888369[155] = 0;
   out_5462626924138888369[156] = 0;
   out_5462626924138888369[157] = 0;
   out_5462626924138888369[158] = 0;
   out_5462626924138888369[159] = 0;
   out_5462626924138888369[160] = 0;
   out_5462626924138888369[161] = 0;
   out_5462626924138888369[162] = 0;
   out_5462626924138888369[163] = 0;
   out_5462626924138888369[164] = 0;
   out_5462626924138888369[165] = 0;
   out_5462626924138888369[166] = 0;
   out_5462626924138888369[167] = 0;
   out_5462626924138888369[168] = 0;
   out_5462626924138888369[169] = 0;
   out_5462626924138888369[170] = 0;
   out_5462626924138888369[171] = 1;
   out_5462626924138888369[172] = 0;
   out_5462626924138888369[173] = 0;
   out_5462626924138888369[174] = 0;
   out_5462626924138888369[175] = 0;
   out_5462626924138888369[176] = 0;
   out_5462626924138888369[177] = 0;
   out_5462626924138888369[178] = 0;
   out_5462626924138888369[179] = 0;
   out_5462626924138888369[180] = 0;
   out_5462626924138888369[181] = 0;
   out_5462626924138888369[182] = 0;
   out_5462626924138888369[183] = 0;
   out_5462626924138888369[184] = 0;
   out_5462626924138888369[185] = 0;
   out_5462626924138888369[186] = 0;
   out_5462626924138888369[187] = 0;
   out_5462626924138888369[188] = 0;
   out_5462626924138888369[189] = 0;
   out_5462626924138888369[190] = 1;
   out_5462626924138888369[191] = 0;
   out_5462626924138888369[192] = 0;
   out_5462626924138888369[193] = 0;
   out_5462626924138888369[194] = 0;
   out_5462626924138888369[195] = 0;
   out_5462626924138888369[196] = 0;
   out_5462626924138888369[197] = 0;
   out_5462626924138888369[198] = 0;
   out_5462626924138888369[199] = 0;
   out_5462626924138888369[200] = 0;
   out_5462626924138888369[201] = 0;
   out_5462626924138888369[202] = 0;
   out_5462626924138888369[203] = 0;
   out_5462626924138888369[204] = 0;
   out_5462626924138888369[205] = 0;
   out_5462626924138888369[206] = 0;
   out_5462626924138888369[207] = 0;
   out_5462626924138888369[208] = 0;
   out_5462626924138888369[209] = 1;
   out_5462626924138888369[210] = 0;
   out_5462626924138888369[211] = 0;
   out_5462626924138888369[212] = 0;
   out_5462626924138888369[213] = 0;
   out_5462626924138888369[214] = 0;
   out_5462626924138888369[215] = 0;
   out_5462626924138888369[216] = 0;
   out_5462626924138888369[217] = 0;
   out_5462626924138888369[218] = 0;
   out_5462626924138888369[219] = 0;
   out_5462626924138888369[220] = 0;
   out_5462626924138888369[221] = 0;
   out_5462626924138888369[222] = 0;
   out_5462626924138888369[223] = 0;
   out_5462626924138888369[224] = 0;
   out_5462626924138888369[225] = 0;
   out_5462626924138888369[226] = 0;
   out_5462626924138888369[227] = 0;
   out_5462626924138888369[228] = 1;
   out_5462626924138888369[229] = 0;
   out_5462626924138888369[230] = 0;
   out_5462626924138888369[231] = 0;
   out_5462626924138888369[232] = 0;
   out_5462626924138888369[233] = 0;
   out_5462626924138888369[234] = 0;
   out_5462626924138888369[235] = 0;
   out_5462626924138888369[236] = 0;
   out_5462626924138888369[237] = 0;
   out_5462626924138888369[238] = 0;
   out_5462626924138888369[239] = 0;
   out_5462626924138888369[240] = 0;
   out_5462626924138888369[241] = 0;
   out_5462626924138888369[242] = 0;
   out_5462626924138888369[243] = 0;
   out_5462626924138888369[244] = 0;
   out_5462626924138888369[245] = 0;
   out_5462626924138888369[246] = 0;
   out_5462626924138888369[247] = 1;
   out_5462626924138888369[248] = 0;
   out_5462626924138888369[249] = 0;
   out_5462626924138888369[250] = 0;
   out_5462626924138888369[251] = 0;
   out_5462626924138888369[252] = 0;
   out_5462626924138888369[253] = 0;
   out_5462626924138888369[254] = 0;
   out_5462626924138888369[255] = 0;
   out_5462626924138888369[256] = 0;
   out_5462626924138888369[257] = 0;
   out_5462626924138888369[258] = 0;
   out_5462626924138888369[259] = 0;
   out_5462626924138888369[260] = 0;
   out_5462626924138888369[261] = 0;
   out_5462626924138888369[262] = 0;
   out_5462626924138888369[263] = 0;
   out_5462626924138888369[264] = 0;
   out_5462626924138888369[265] = 0;
   out_5462626924138888369[266] = 1;
   out_5462626924138888369[267] = 0;
   out_5462626924138888369[268] = 0;
   out_5462626924138888369[269] = 0;
   out_5462626924138888369[270] = 0;
   out_5462626924138888369[271] = 0;
   out_5462626924138888369[272] = 0;
   out_5462626924138888369[273] = 0;
   out_5462626924138888369[274] = 0;
   out_5462626924138888369[275] = 0;
   out_5462626924138888369[276] = 0;
   out_5462626924138888369[277] = 0;
   out_5462626924138888369[278] = 0;
   out_5462626924138888369[279] = 0;
   out_5462626924138888369[280] = 0;
   out_5462626924138888369[281] = 0;
   out_5462626924138888369[282] = 0;
   out_5462626924138888369[283] = 0;
   out_5462626924138888369[284] = 0;
   out_5462626924138888369[285] = 1;
   out_5462626924138888369[286] = 0;
   out_5462626924138888369[287] = 0;
   out_5462626924138888369[288] = 0;
   out_5462626924138888369[289] = 0;
   out_5462626924138888369[290] = 0;
   out_5462626924138888369[291] = 0;
   out_5462626924138888369[292] = 0;
   out_5462626924138888369[293] = 0;
   out_5462626924138888369[294] = 0;
   out_5462626924138888369[295] = 0;
   out_5462626924138888369[296] = 0;
   out_5462626924138888369[297] = 0;
   out_5462626924138888369[298] = 0;
   out_5462626924138888369[299] = 0;
   out_5462626924138888369[300] = 0;
   out_5462626924138888369[301] = 0;
   out_5462626924138888369[302] = 0;
   out_5462626924138888369[303] = 0;
   out_5462626924138888369[304] = 1;
   out_5462626924138888369[305] = 0;
   out_5462626924138888369[306] = 0;
   out_5462626924138888369[307] = 0;
   out_5462626924138888369[308] = 0;
   out_5462626924138888369[309] = 0;
   out_5462626924138888369[310] = 0;
   out_5462626924138888369[311] = 0;
   out_5462626924138888369[312] = 0;
   out_5462626924138888369[313] = 0;
   out_5462626924138888369[314] = 0;
   out_5462626924138888369[315] = 0;
   out_5462626924138888369[316] = 0;
   out_5462626924138888369[317] = 0;
   out_5462626924138888369[318] = 0;
   out_5462626924138888369[319] = 0;
   out_5462626924138888369[320] = 0;
   out_5462626924138888369[321] = 0;
   out_5462626924138888369[322] = 0;
   out_5462626924138888369[323] = 1;
}
void h_4(double *state, double *unused, double *out_1348371912510502215) {
   out_1348371912510502215[0] = state[6] + state[9];
   out_1348371912510502215[1] = state[7] + state[10];
   out_1348371912510502215[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_5836553387662151839) {
   out_5836553387662151839[0] = 0;
   out_5836553387662151839[1] = 0;
   out_5836553387662151839[2] = 0;
   out_5836553387662151839[3] = 0;
   out_5836553387662151839[4] = 0;
   out_5836553387662151839[5] = 0;
   out_5836553387662151839[6] = 1;
   out_5836553387662151839[7] = 0;
   out_5836553387662151839[8] = 0;
   out_5836553387662151839[9] = 1;
   out_5836553387662151839[10] = 0;
   out_5836553387662151839[11] = 0;
   out_5836553387662151839[12] = 0;
   out_5836553387662151839[13] = 0;
   out_5836553387662151839[14] = 0;
   out_5836553387662151839[15] = 0;
   out_5836553387662151839[16] = 0;
   out_5836553387662151839[17] = 0;
   out_5836553387662151839[18] = 0;
   out_5836553387662151839[19] = 0;
   out_5836553387662151839[20] = 0;
   out_5836553387662151839[21] = 0;
   out_5836553387662151839[22] = 0;
   out_5836553387662151839[23] = 0;
   out_5836553387662151839[24] = 0;
   out_5836553387662151839[25] = 1;
   out_5836553387662151839[26] = 0;
   out_5836553387662151839[27] = 0;
   out_5836553387662151839[28] = 1;
   out_5836553387662151839[29] = 0;
   out_5836553387662151839[30] = 0;
   out_5836553387662151839[31] = 0;
   out_5836553387662151839[32] = 0;
   out_5836553387662151839[33] = 0;
   out_5836553387662151839[34] = 0;
   out_5836553387662151839[35] = 0;
   out_5836553387662151839[36] = 0;
   out_5836553387662151839[37] = 0;
   out_5836553387662151839[38] = 0;
   out_5836553387662151839[39] = 0;
   out_5836553387662151839[40] = 0;
   out_5836553387662151839[41] = 0;
   out_5836553387662151839[42] = 0;
   out_5836553387662151839[43] = 0;
   out_5836553387662151839[44] = 1;
   out_5836553387662151839[45] = 0;
   out_5836553387662151839[46] = 0;
   out_5836553387662151839[47] = 1;
   out_5836553387662151839[48] = 0;
   out_5836553387662151839[49] = 0;
   out_5836553387662151839[50] = 0;
   out_5836553387662151839[51] = 0;
   out_5836553387662151839[52] = 0;
   out_5836553387662151839[53] = 0;
}
void h_10(double *state, double *unused, double *out_9044662776552187559) {
   out_9044662776552187559[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_9044662776552187559[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_9044662776552187559[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_4253353556758477164) {
   out_4253353556758477164[0] = 0;
   out_4253353556758477164[1] = 9.8100000000000005*cos(state[1]);
   out_4253353556758477164[2] = 0;
   out_4253353556758477164[3] = 0;
   out_4253353556758477164[4] = -state[8];
   out_4253353556758477164[5] = state[7];
   out_4253353556758477164[6] = 0;
   out_4253353556758477164[7] = state[5];
   out_4253353556758477164[8] = -state[4];
   out_4253353556758477164[9] = 0;
   out_4253353556758477164[10] = 0;
   out_4253353556758477164[11] = 0;
   out_4253353556758477164[12] = 1;
   out_4253353556758477164[13] = 0;
   out_4253353556758477164[14] = 0;
   out_4253353556758477164[15] = 1;
   out_4253353556758477164[16] = 0;
   out_4253353556758477164[17] = 0;
   out_4253353556758477164[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_4253353556758477164[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_4253353556758477164[20] = 0;
   out_4253353556758477164[21] = state[8];
   out_4253353556758477164[22] = 0;
   out_4253353556758477164[23] = -state[6];
   out_4253353556758477164[24] = -state[5];
   out_4253353556758477164[25] = 0;
   out_4253353556758477164[26] = state[3];
   out_4253353556758477164[27] = 0;
   out_4253353556758477164[28] = 0;
   out_4253353556758477164[29] = 0;
   out_4253353556758477164[30] = 0;
   out_4253353556758477164[31] = 1;
   out_4253353556758477164[32] = 0;
   out_4253353556758477164[33] = 0;
   out_4253353556758477164[34] = 1;
   out_4253353556758477164[35] = 0;
   out_4253353556758477164[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_4253353556758477164[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_4253353556758477164[38] = 0;
   out_4253353556758477164[39] = -state[7];
   out_4253353556758477164[40] = state[6];
   out_4253353556758477164[41] = 0;
   out_4253353556758477164[42] = state[4];
   out_4253353556758477164[43] = -state[3];
   out_4253353556758477164[44] = 0;
   out_4253353556758477164[45] = 0;
   out_4253353556758477164[46] = 0;
   out_4253353556758477164[47] = 0;
   out_4253353556758477164[48] = 0;
   out_4253353556758477164[49] = 0;
   out_4253353556758477164[50] = 1;
   out_4253353556758477164[51] = 0;
   out_4253353556758477164[52] = 0;
   out_4253353556758477164[53] = 1;
}
void h_13(double *state, double *unused, double *out_4638407917494187653) {
   out_4638407917494187653[0] = state[3];
   out_4638407917494187653[1] = state[4];
   out_4638407917494187653[2] = state[5];
}
void H_13(double *state, double *unused, double *out_2624279562329819038) {
   out_2624279562329819038[0] = 0;
   out_2624279562329819038[1] = 0;
   out_2624279562329819038[2] = 0;
   out_2624279562329819038[3] = 1;
   out_2624279562329819038[4] = 0;
   out_2624279562329819038[5] = 0;
   out_2624279562329819038[6] = 0;
   out_2624279562329819038[7] = 0;
   out_2624279562329819038[8] = 0;
   out_2624279562329819038[9] = 0;
   out_2624279562329819038[10] = 0;
   out_2624279562329819038[11] = 0;
   out_2624279562329819038[12] = 0;
   out_2624279562329819038[13] = 0;
   out_2624279562329819038[14] = 0;
   out_2624279562329819038[15] = 0;
   out_2624279562329819038[16] = 0;
   out_2624279562329819038[17] = 0;
   out_2624279562329819038[18] = 0;
   out_2624279562329819038[19] = 0;
   out_2624279562329819038[20] = 0;
   out_2624279562329819038[21] = 0;
   out_2624279562329819038[22] = 1;
   out_2624279562329819038[23] = 0;
   out_2624279562329819038[24] = 0;
   out_2624279562329819038[25] = 0;
   out_2624279562329819038[26] = 0;
   out_2624279562329819038[27] = 0;
   out_2624279562329819038[28] = 0;
   out_2624279562329819038[29] = 0;
   out_2624279562329819038[30] = 0;
   out_2624279562329819038[31] = 0;
   out_2624279562329819038[32] = 0;
   out_2624279562329819038[33] = 0;
   out_2624279562329819038[34] = 0;
   out_2624279562329819038[35] = 0;
   out_2624279562329819038[36] = 0;
   out_2624279562329819038[37] = 0;
   out_2624279562329819038[38] = 0;
   out_2624279562329819038[39] = 0;
   out_2624279562329819038[40] = 0;
   out_2624279562329819038[41] = 1;
   out_2624279562329819038[42] = 0;
   out_2624279562329819038[43] = 0;
   out_2624279562329819038[44] = 0;
   out_2624279562329819038[45] = 0;
   out_2624279562329819038[46] = 0;
   out_2624279562329819038[47] = 0;
   out_2624279562329819038[48] = 0;
   out_2624279562329819038[49] = 0;
   out_2624279562329819038[50] = 0;
   out_2624279562329819038[51] = 0;
   out_2624279562329819038[52] = 0;
   out_2624279562329819038[53] = 0;
}
void h_14(double *state, double *unused, double *out_6781244107497221472) {
   out_6781244107497221472[0] = state[6];
   out_6781244107497221472[1] = state[7];
   out_6781244107497221472[2] = state[8];
}
void H_14(double *state, double *unused, double *out_8919341819957524135) {
   out_8919341819957524135[0] = 0;
   out_8919341819957524135[1] = 0;
   out_8919341819957524135[2] = 0;
   out_8919341819957524135[3] = 0;
   out_8919341819957524135[4] = 0;
   out_8919341819957524135[5] = 0;
   out_8919341819957524135[6] = 1;
   out_8919341819957524135[7] = 0;
   out_8919341819957524135[8] = 0;
   out_8919341819957524135[9] = 0;
   out_8919341819957524135[10] = 0;
   out_8919341819957524135[11] = 0;
   out_8919341819957524135[12] = 0;
   out_8919341819957524135[13] = 0;
   out_8919341819957524135[14] = 0;
   out_8919341819957524135[15] = 0;
   out_8919341819957524135[16] = 0;
   out_8919341819957524135[17] = 0;
   out_8919341819957524135[18] = 0;
   out_8919341819957524135[19] = 0;
   out_8919341819957524135[20] = 0;
   out_8919341819957524135[21] = 0;
   out_8919341819957524135[22] = 0;
   out_8919341819957524135[23] = 0;
   out_8919341819957524135[24] = 0;
   out_8919341819957524135[25] = 1;
   out_8919341819957524135[26] = 0;
   out_8919341819957524135[27] = 0;
   out_8919341819957524135[28] = 0;
   out_8919341819957524135[29] = 0;
   out_8919341819957524135[30] = 0;
   out_8919341819957524135[31] = 0;
   out_8919341819957524135[32] = 0;
   out_8919341819957524135[33] = 0;
   out_8919341819957524135[34] = 0;
   out_8919341819957524135[35] = 0;
   out_8919341819957524135[36] = 0;
   out_8919341819957524135[37] = 0;
   out_8919341819957524135[38] = 0;
   out_8919341819957524135[39] = 0;
   out_8919341819957524135[40] = 0;
   out_8919341819957524135[41] = 0;
   out_8919341819957524135[42] = 0;
   out_8919341819957524135[43] = 0;
   out_8919341819957524135[44] = 1;
   out_8919341819957524135[45] = 0;
   out_8919341819957524135[46] = 0;
   out_8919341819957524135[47] = 0;
   out_8919341819957524135[48] = 0;
   out_8919341819957524135[49] = 0;
   out_8919341819957524135[50] = 0;
   out_8919341819957524135[51] = 0;
   out_8919341819957524135[52] = 0;
   out_8919341819957524135[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_4907159739794112728) {
  err_fun(nom_x, delta_x, out_4907159739794112728);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_9092805515226665715) {
  inv_err_fun(nom_x, true_x, out_9092805515226665715);
}
void pose_H_mod_fun(double *state, double *out_8838383476203492205) {
  H_mod_fun(state, out_8838383476203492205);
}
void pose_f_fun(double *state, double dt, double *out_1879607716571020306) {
  f_fun(state,  dt, out_1879607716571020306);
}
void pose_F_fun(double *state, double dt, double *out_5462626924138888369) {
  F_fun(state,  dt, out_5462626924138888369);
}
void pose_h_4(double *state, double *unused, double *out_1348371912510502215) {
  h_4(state, unused, out_1348371912510502215);
}
void pose_H_4(double *state, double *unused, double *out_5836553387662151839) {
  H_4(state, unused, out_5836553387662151839);
}
void pose_h_10(double *state, double *unused, double *out_9044662776552187559) {
  h_10(state, unused, out_9044662776552187559);
}
void pose_H_10(double *state, double *unused, double *out_4253353556758477164) {
  H_10(state, unused, out_4253353556758477164);
}
void pose_h_13(double *state, double *unused, double *out_4638407917494187653) {
  h_13(state, unused, out_4638407917494187653);
}
void pose_H_13(double *state, double *unused, double *out_2624279562329819038) {
  H_13(state, unused, out_2624279562329819038);
}
void pose_h_14(double *state, double *unused, double *out_6781244107497221472) {
  h_14(state, unused, out_6781244107497221472);
}
void pose_H_14(double *state, double *unused, double *out_8919341819957524135) {
  H_14(state, unused, out_8919341819957524135);
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
