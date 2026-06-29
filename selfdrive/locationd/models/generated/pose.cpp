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
void err_fun(double *nom_x, double *delta_x, double *out_8253506042582469219) {
   out_8253506042582469219[0] = delta_x[0] + nom_x[0];
   out_8253506042582469219[1] = delta_x[1] + nom_x[1];
   out_8253506042582469219[2] = delta_x[2] + nom_x[2];
   out_8253506042582469219[3] = delta_x[3] + nom_x[3];
   out_8253506042582469219[4] = delta_x[4] + nom_x[4];
   out_8253506042582469219[5] = delta_x[5] + nom_x[5];
   out_8253506042582469219[6] = delta_x[6] + nom_x[6];
   out_8253506042582469219[7] = delta_x[7] + nom_x[7];
   out_8253506042582469219[8] = delta_x[8] + nom_x[8];
   out_8253506042582469219[9] = delta_x[9] + nom_x[9];
   out_8253506042582469219[10] = delta_x[10] + nom_x[10];
   out_8253506042582469219[11] = delta_x[11] + nom_x[11];
   out_8253506042582469219[12] = delta_x[12] + nom_x[12];
   out_8253506042582469219[13] = delta_x[13] + nom_x[13];
   out_8253506042582469219[14] = delta_x[14] + nom_x[14];
   out_8253506042582469219[15] = delta_x[15] + nom_x[15];
   out_8253506042582469219[16] = delta_x[16] + nom_x[16];
   out_8253506042582469219[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_2344330990237256254) {
   out_2344330990237256254[0] = -nom_x[0] + true_x[0];
   out_2344330990237256254[1] = -nom_x[1] + true_x[1];
   out_2344330990237256254[2] = -nom_x[2] + true_x[2];
   out_2344330990237256254[3] = -nom_x[3] + true_x[3];
   out_2344330990237256254[4] = -nom_x[4] + true_x[4];
   out_2344330990237256254[5] = -nom_x[5] + true_x[5];
   out_2344330990237256254[6] = -nom_x[6] + true_x[6];
   out_2344330990237256254[7] = -nom_x[7] + true_x[7];
   out_2344330990237256254[8] = -nom_x[8] + true_x[8];
   out_2344330990237256254[9] = -nom_x[9] + true_x[9];
   out_2344330990237256254[10] = -nom_x[10] + true_x[10];
   out_2344330990237256254[11] = -nom_x[11] + true_x[11];
   out_2344330990237256254[12] = -nom_x[12] + true_x[12];
   out_2344330990237256254[13] = -nom_x[13] + true_x[13];
   out_2344330990237256254[14] = -nom_x[14] + true_x[14];
   out_2344330990237256254[15] = -nom_x[15] + true_x[15];
   out_2344330990237256254[16] = -nom_x[16] + true_x[16];
   out_2344330990237256254[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_1157215523194220986) {
   out_1157215523194220986[0] = 1.0;
   out_1157215523194220986[1] = 0.0;
   out_1157215523194220986[2] = 0.0;
   out_1157215523194220986[3] = 0.0;
   out_1157215523194220986[4] = 0.0;
   out_1157215523194220986[5] = 0.0;
   out_1157215523194220986[6] = 0.0;
   out_1157215523194220986[7] = 0.0;
   out_1157215523194220986[8] = 0.0;
   out_1157215523194220986[9] = 0.0;
   out_1157215523194220986[10] = 0.0;
   out_1157215523194220986[11] = 0.0;
   out_1157215523194220986[12] = 0.0;
   out_1157215523194220986[13] = 0.0;
   out_1157215523194220986[14] = 0.0;
   out_1157215523194220986[15] = 0.0;
   out_1157215523194220986[16] = 0.0;
   out_1157215523194220986[17] = 0.0;
   out_1157215523194220986[18] = 0.0;
   out_1157215523194220986[19] = 1.0;
   out_1157215523194220986[20] = 0.0;
   out_1157215523194220986[21] = 0.0;
   out_1157215523194220986[22] = 0.0;
   out_1157215523194220986[23] = 0.0;
   out_1157215523194220986[24] = 0.0;
   out_1157215523194220986[25] = 0.0;
   out_1157215523194220986[26] = 0.0;
   out_1157215523194220986[27] = 0.0;
   out_1157215523194220986[28] = 0.0;
   out_1157215523194220986[29] = 0.0;
   out_1157215523194220986[30] = 0.0;
   out_1157215523194220986[31] = 0.0;
   out_1157215523194220986[32] = 0.0;
   out_1157215523194220986[33] = 0.0;
   out_1157215523194220986[34] = 0.0;
   out_1157215523194220986[35] = 0.0;
   out_1157215523194220986[36] = 0.0;
   out_1157215523194220986[37] = 0.0;
   out_1157215523194220986[38] = 1.0;
   out_1157215523194220986[39] = 0.0;
   out_1157215523194220986[40] = 0.0;
   out_1157215523194220986[41] = 0.0;
   out_1157215523194220986[42] = 0.0;
   out_1157215523194220986[43] = 0.0;
   out_1157215523194220986[44] = 0.0;
   out_1157215523194220986[45] = 0.0;
   out_1157215523194220986[46] = 0.0;
   out_1157215523194220986[47] = 0.0;
   out_1157215523194220986[48] = 0.0;
   out_1157215523194220986[49] = 0.0;
   out_1157215523194220986[50] = 0.0;
   out_1157215523194220986[51] = 0.0;
   out_1157215523194220986[52] = 0.0;
   out_1157215523194220986[53] = 0.0;
   out_1157215523194220986[54] = 0.0;
   out_1157215523194220986[55] = 0.0;
   out_1157215523194220986[56] = 0.0;
   out_1157215523194220986[57] = 1.0;
   out_1157215523194220986[58] = 0.0;
   out_1157215523194220986[59] = 0.0;
   out_1157215523194220986[60] = 0.0;
   out_1157215523194220986[61] = 0.0;
   out_1157215523194220986[62] = 0.0;
   out_1157215523194220986[63] = 0.0;
   out_1157215523194220986[64] = 0.0;
   out_1157215523194220986[65] = 0.0;
   out_1157215523194220986[66] = 0.0;
   out_1157215523194220986[67] = 0.0;
   out_1157215523194220986[68] = 0.0;
   out_1157215523194220986[69] = 0.0;
   out_1157215523194220986[70] = 0.0;
   out_1157215523194220986[71] = 0.0;
   out_1157215523194220986[72] = 0.0;
   out_1157215523194220986[73] = 0.0;
   out_1157215523194220986[74] = 0.0;
   out_1157215523194220986[75] = 0.0;
   out_1157215523194220986[76] = 1.0;
   out_1157215523194220986[77] = 0.0;
   out_1157215523194220986[78] = 0.0;
   out_1157215523194220986[79] = 0.0;
   out_1157215523194220986[80] = 0.0;
   out_1157215523194220986[81] = 0.0;
   out_1157215523194220986[82] = 0.0;
   out_1157215523194220986[83] = 0.0;
   out_1157215523194220986[84] = 0.0;
   out_1157215523194220986[85] = 0.0;
   out_1157215523194220986[86] = 0.0;
   out_1157215523194220986[87] = 0.0;
   out_1157215523194220986[88] = 0.0;
   out_1157215523194220986[89] = 0.0;
   out_1157215523194220986[90] = 0.0;
   out_1157215523194220986[91] = 0.0;
   out_1157215523194220986[92] = 0.0;
   out_1157215523194220986[93] = 0.0;
   out_1157215523194220986[94] = 0.0;
   out_1157215523194220986[95] = 1.0;
   out_1157215523194220986[96] = 0.0;
   out_1157215523194220986[97] = 0.0;
   out_1157215523194220986[98] = 0.0;
   out_1157215523194220986[99] = 0.0;
   out_1157215523194220986[100] = 0.0;
   out_1157215523194220986[101] = 0.0;
   out_1157215523194220986[102] = 0.0;
   out_1157215523194220986[103] = 0.0;
   out_1157215523194220986[104] = 0.0;
   out_1157215523194220986[105] = 0.0;
   out_1157215523194220986[106] = 0.0;
   out_1157215523194220986[107] = 0.0;
   out_1157215523194220986[108] = 0.0;
   out_1157215523194220986[109] = 0.0;
   out_1157215523194220986[110] = 0.0;
   out_1157215523194220986[111] = 0.0;
   out_1157215523194220986[112] = 0.0;
   out_1157215523194220986[113] = 0.0;
   out_1157215523194220986[114] = 1.0;
   out_1157215523194220986[115] = 0.0;
   out_1157215523194220986[116] = 0.0;
   out_1157215523194220986[117] = 0.0;
   out_1157215523194220986[118] = 0.0;
   out_1157215523194220986[119] = 0.0;
   out_1157215523194220986[120] = 0.0;
   out_1157215523194220986[121] = 0.0;
   out_1157215523194220986[122] = 0.0;
   out_1157215523194220986[123] = 0.0;
   out_1157215523194220986[124] = 0.0;
   out_1157215523194220986[125] = 0.0;
   out_1157215523194220986[126] = 0.0;
   out_1157215523194220986[127] = 0.0;
   out_1157215523194220986[128] = 0.0;
   out_1157215523194220986[129] = 0.0;
   out_1157215523194220986[130] = 0.0;
   out_1157215523194220986[131] = 0.0;
   out_1157215523194220986[132] = 0.0;
   out_1157215523194220986[133] = 1.0;
   out_1157215523194220986[134] = 0.0;
   out_1157215523194220986[135] = 0.0;
   out_1157215523194220986[136] = 0.0;
   out_1157215523194220986[137] = 0.0;
   out_1157215523194220986[138] = 0.0;
   out_1157215523194220986[139] = 0.0;
   out_1157215523194220986[140] = 0.0;
   out_1157215523194220986[141] = 0.0;
   out_1157215523194220986[142] = 0.0;
   out_1157215523194220986[143] = 0.0;
   out_1157215523194220986[144] = 0.0;
   out_1157215523194220986[145] = 0.0;
   out_1157215523194220986[146] = 0.0;
   out_1157215523194220986[147] = 0.0;
   out_1157215523194220986[148] = 0.0;
   out_1157215523194220986[149] = 0.0;
   out_1157215523194220986[150] = 0.0;
   out_1157215523194220986[151] = 0.0;
   out_1157215523194220986[152] = 1.0;
   out_1157215523194220986[153] = 0.0;
   out_1157215523194220986[154] = 0.0;
   out_1157215523194220986[155] = 0.0;
   out_1157215523194220986[156] = 0.0;
   out_1157215523194220986[157] = 0.0;
   out_1157215523194220986[158] = 0.0;
   out_1157215523194220986[159] = 0.0;
   out_1157215523194220986[160] = 0.0;
   out_1157215523194220986[161] = 0.0;
   out_1157215523194220986[162] = 0.0;
   out_1157215523194220986[163] = 0.0;
   out_1157215523194220986[164] = 0.0;
   out_1157215523194220986[165] = 0.0;
   out_1157215523194220986[166] = 0.0;
   out_1157215523194220986[167] = 0.0;
   out_1157215523194220986[168] = 0.0;
   out_1157215523194220986[169] = 0.0;
   out_1157215523194220986[170] = 0.0;
   out_1157215523194220986[171] = 1.0;
   out_1157215523194220986[172] = 0.0;
   out_1157215523194220986[173] = 0.0;
   out_1157215523194220986[174] = 0.0;
   out_1157215523194220986[175] = 0.0;
   out_1157215523194220986[176] = 0.0;
   out_1157215523194220986[177] = 0.0;
   out_1157215523194220986[178] = 0.0;
   out_1157215523194220986[179] = 0.0;
   out_1157215523194220986[180] = 0.0;
   out_1157215523194220986[181] = 0.0;
   out_1157215523194220986[182] = 0.0;
   out_1157215523194220986[183] = 0.0;
   out_1157215523194220986[184] = 0.0;
   out_1157215523194220986[185] = 0.0;
   out_1157215523194220986[186] = 0.0;
   out_1157215523194220986[187] = 0.0;
   out_1157215523194220986[188] = 0.0;
   out_1157215523194220986[189] = 0.0;
   out_1157215523194220986[190] = 1.0;
   out_1157215523194220986[191] = 0.0;
   out_1157215523194220986[192] = 0.0;
   out_1157215523194220986[193] = 0.0;
   out_1157215523194220986[194] = 0.0;
   out_1157215523194220986[195] = 0.0;
   out_1157215523194220986[196] = 0.0;
   out_1157215523194220986[197] = 0.0;
   out_1157215523194220986[198] = 0.0;
   out_1157215523194220986[199] = 0.0;
   out_1157215523194220986[200] = 0.0;
   out_1157215523194220986[201] = 0.0;
   out_1157215523194220986[202] = 0.0;
   out_1157215523194220986[203] = 0.0;
   out_1157215523194220986[204] = 0.0;
   out_1157215523194220986[205] = 0.0;
   out_1157215523194220986[206] = 0.0;
   out_1157215523194220986[207] = 0.0;
   out_1157215523194220986[208] = 0.0;
   out_1157215523194220986[209] = 1.0;
   out_1157215523194220986[210] = 0.0;
   out_1157215523194220986[211] = 0.0;
   out_1157215523194220986[212] = 0.0;
   out_1157215523194220986[213] = 0.0;
   out_1157215523194220986[214] = 0.0;
   out_1157215523194220986[215] = 0.0;
   out_1157215523194220986[216] = 0.0;
   out_1157215523194220986[217] = 0.0;
   out_1157215523194220986[218] = 0.0;
   out_1157215523194220986[219] = 0.0;
   out_1157215523194220986[220] = 0.0;
   out_1157215523194220986[221] = 0.0;
   out_1157215523194220986[222] = 0.0;
   out_1157215523194220986[223] = 0.0;
   out_1157215523194220986[224] = 0.0;
   out_1157215523194220986[225] = 0.0;
   out_1157215523194220986[226] = 0.0;
   out_1157215523194220986[227] = 0.0;
   out_1157215523194220986[228] = 1.0;
   out_1157215523194220986[229] = 0.0;
   out_1157215523194220986[230] = 0.0;
   out_1157215523194220986[231] = 0.0;
   out_1157215523194220986[232] = 0.0;
   out_1157215523194220986[233] = 0.0;
   out_1157215523194220986[234] = 0.0;
   out_1157215523194220986[235] = 0.0;
   out_1157215523194220986[236] = 0.0;
   out_1157215523194220986[237] = 0.0;
   out_1157215523194220986[238] = 0.0;
   out_1157215523194220986[239] = 0.0;
   out_1157215523194220986[240] = 0.0;
   out_1157215523194220986[241] = 0.0;
   out_1157215523194220986[242] = 0.0;
   out_1157215523194220986[243] = 0.0;
   out_1157215523194220986[244] = 0.0;
   out_1157215523194220986[245] = 0.0;
   out_1157215523194220986[246] = 0.0;
   out_1157215523194220986[247] = 1.0;
   out_1157215523194220986[248] = 0.0;
   out_1157215523194220986[249] = 0.0;
   out_1157215523194220986[250] = 0.0;
   out_1157215523194220986[251] = 0.0;
   out_1157215523194220986[252] = 0.0;
   out_1157215523194220986[253] = 0.0;
   out_1157215523194220986[254] = 0.0;
   out_1157215523194220986[255] = 0.0;
   out_1157215523194220986[256] = 0.0;
   out_1157215523194220986[257] = 0.0;
   out_1157215523194220986[258] = 0.0;
   out_1157215523194220986[259] = 0.0;
   out_1157215523194220986[260] = 0.0;
   out_1157215523194220986[261] = 0.0;
   out_1157215523194220986[262] = 0.0;
   out_1157215523194220986[263] = 0.0;
   out_1157215523194220986[264] = 0.0;
   out_1157215523194220986[265] = 0.0;
   out_1157215523194220986[266] = 1.0;
   out_1157215523194220986[267] = 0.0;
   out_1157215523194220986[268] = 0.0;
   out_1157215523194220986[269] = 0.0;
   out_1157215523194220986[270] = 0.0;
   out_1157215523194220986[271] = 0.0;
   out_1157215523194220986[272] = 0.0;
   out_1157215523194220986[273] = 0.0;
   out_1157215523194220986[274] = 0.0;
   out_1157215523194220986[275] = 0.0;
   out_1157215523194220986[276] = 0.0;
   out_1157215523194220986[277] = 0.0;
   out_1157215523194220986[278] = 0.0;
   out_1157215523194220986[279] = 0.0;
   out_1157215523194220986[280] = 0.0;
   out_1157215523194220986[281] = 0.0;
   out_1157215523194220986[282] = 0.0;
   out_1157215523194220986[283] = 0.0;
   out_1157215523194220986[284] = 0.0;
   out_1157215523194220986[285] = 1.0;
   out_1157215523194220986[286] = 0.0;
   out_1157215523194220986[287] = 0.0;
   out_1157215523194220986[288] = 0.0;
   out_1157215523194220986[289] = 0.0;
   out_1157215523194220986[290] = 0.0;
   out_1157215523194220986[291] = 0.0;
   out_1157215523194220986[292] = 0.0;
   out_1157215523194220986[293] = 0.0;
   out_1157215523194220986[294] = 0.0;
   out_1157215523194220986[295] = 0.0;
   out_1157215523194220986[296] = 0.0;
   out_1157215523194220986[297] = 0.0;
   out_1157215523194220986[298] = 0.0;
   out_1157215523194220986[299] = 0.0;
   out_1157215523194220986[300] = 0.0;
   out_1157215523194220986[301] = 0.0;
   out_1157215523194220986[302] = 0.0;
   out_1157215523194220986[303] = 0.0;
   out_1157215523194220986[304] = 1.0;
   out_1157215523194220986[305] = 0.0;
   out_1157215523194220986[306] = 0.0;
   out_1157215523194220986[307] = 0.0;
   out_1157215523194220986[308] = 0.0;
   out_1157215523194220986[309] = 0.0;
   out_1157215523194220986[310] = 0.0;
   out_1157215523194220986[311] = 0.0;
   out_1157215523194220986[312] = 0.0;
   out_1157215523194220986[313] = 0.0;
   out_1157215523194220986[314] = 0.0;
   out_1157215523194220986[315] = 0.0;
   out_1157215523194220986[316] = 0.0;
   out_1157215523194220986[317] = 0.0;
   out_1157215523194220986[318] = 0.0;
   out_1157215523194220986[319] = 0.0;
   out_1157215523194220986[320] = 0.0;
   out_1157215523194220986[321] = 0.0;
   out_1157215523194220986[322] = 0.0;
   out_1157215523194220986[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_6204252535340020659) {
   out_6204252535340020659[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_6204252535340020659[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_6204252535340020659[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_6204252535340020659[3] = dt*state[12] + state[3];
   out_6204252535340020659[4] = dt*state[13] + state[4];
   out_6204252535340020659[5] = dt*state[14] + state[5];
   out_6204252535340020659[6] = state[6];
   out_6204252535340020659[7] = state[7];
   out_6204252535340020659[8] = state[8];
   out_6204252535340020659[9] = state[9];
   out_6204252535340020659[10] = state[10];
   out_6204252535340020659[11] = state[11];
   out_6204252535340020659[12] = state[12];
   out_6204252535340020659[13] = state[13];
   out_6204252535340020659[14] = state[14];
   out_6204252535340020659[15] = state[15];
   out_6204252535340020659[16] = state[16];
   out_6204252535340020659[17] = state[17];
}
void F_fun(double *state, double dt, double *out_3422125367295010588) {
   out_3422125367295010588[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3422125367295010588[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3422125367295010588[2] = 0;
   out_3422125367295010588[3] = 0;
   out_3422125367295010588[4] = 0;
   out_3422125367295010588[5] = 0;
   out_3422125367295010588[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3422125367295010588[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3422125367295010588[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3422125367295010588[9] = 0;
   out_3422125367295010588[10] = 0;
   out_3422125367295010588[11] = 0;
   out_3422125367295010588[12] = 0;
   out_3422125367295010588[13] = 0;
   out_3422125367295010588[14] = 0;
   out_3422125367295010588[15] = 0;
   out_3422125367295010588[16] = 0;
   out_3422125367295010588[17] = 0;
   out_3422125367295010588[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3422125367295010588[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3422125367295010588[20] = 0;
   out_3422125367295010588[21] = 0;
   out_3422125367295010588[22] = 0;
   out_3422125367295010588[23] = 0;
   out_3422125367295010588[24] = 0;
   out_3422125367295010588[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3422125367295010588[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3422125367295010588[27] = 0;
   out_3422125367295010588[28] = 0;
   out_3422125367295010588[29] = 0;
   out_3422125367295010588[30] = 0;
   out_3422125367295010588[31] = 0;
   out_3422125367295010588[32] = 0;
   out_3422125367295010588[33] = 0;
   out_3422125367295010588[34] = 0;
   out_3422125367295010588[35] = 0;
   out_3422125367295010588[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3422125367295010588[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3422125367295010588[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3422125367295010588[39] = 0;
   out_3422125367295010588[40] = 0;
   out_3422125367295010588[41] = 0;
   out_3422125367295010588[42] = 0;
   out_3422125367295010588[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3422125367295010588[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3422125367295010588[45] = 0;
   out_3422125367295010588[46] = 0;
   out_3422125367295010588[47] = 0;
   out_3422125367295010588[48] = 0;
   out_3422125367295010588[49] = 0;
   out_3422125367295010588[50] = 0;
   out_3422125367295010588[51] = 0;
   out_3422125367295010588[52] = 0;
   out_3422125367295010588[53] = 0;
   out_3422125367295010588[54] = 0;
   out_3422125367295010588[55] = 0;
   out_3422125367295010588[56] = 0;
   out_3422125367295010588[57] = 1;
   out_3422125367295010588[58] = 0;
   out_3422125367295010588[59] = 0;
   out_3422125367295010588[60] = 0;
   out_3422125367295010588[61] = 0;
   out_3422125367295010588[62] = 0;
   out_3422125367295010588[63] = 0;
   out_3422125367295010588[64] = 0;
   out_3422125367295010588[65] = 0;
   out_3422125367295010588[66] = dt;
   out_3422125367295010588[67] = 0;
   out_3422125367295010588[68] = 0;
   out_3422125367295010588[69] = 0;
   out_3422125367295010588[70] = 0;
   out_3422125367295010588[71] = 0;
   out_3422125367295010588[72] = 0;
   out_3422125367295010588[73] = 0;
   out_3422125367295010588[74] = 0;
   out_3422125367295010588[75] = 0;
   out_3422125367295010588[76] = 1;
   out_3422125367295010588[77] = 0;
   out_3422125367295010588[78] = 0;
   out_3422125367295010588[79] = 0;
   out_3422125367295010588[80] = 0;
   out_3422125367295010588[81] = 0;
   out_3422125367295010588[82] = 0;
   out_3422125367295010588[83] = 0;
   out_3422125367295010588[84] = 0;
   out_3422125367295010588[85] = dt;
   out_3422125367295010588[86] = 0;
   out_3422125367295010588[87] = 0;
   out_3422125367295010588[88] = 0;
   out_3422125367295010588[89] = 0;
   out_3422125367295010588[90] = 0;
   out_3422125367295010588[91] = 0;
   out_3422125367295010588[92] = 0;
   out_3422125367295010588[93] = 0;
   out_3422125367295010588[94] = 0;
   out_3422125367295010588[95] = 1;
   out_3422125367295010588[96] = 0;
   out_3422125367295010588[97] = 0;
   out_3422125367295010588[98] = 0;
   out_3422125367295010588[99] = 0;
   out_3422125367295010588[100] = 0;
   out_3422125367295010588[101] = 0;
   out_3422125367295010588[102] = 0;
   out_3422125367295010588[103] = 0;
   out_3422125367295010588[104] = dt;
   out_3422125367295010588[105] = 0;
   out_3422125367295010588[106] = 0;
   out_3422125367295010588[107] = 0;
   out_3422125367295010588[108] = 0;
   out_3422125367295010588[109] = 0;
   out_3422125367295010588[110] = 0;
   out_3422125367295010588[111] = 0;
   out_3422125367295010588[112] = 0;
   out_3422125367295010588[113] = 0;
   out_3422125367295010588[114] = 1;
   out_3422125367295010588[115] = 0;
   out_3422125367295010588[116] = 0;
   out_3422125367295010588[117] = 0;
   out_3422125367295010588[118] = 0;
   out_3422125367295010588[119] = 0;
   out_3422125367295010588[120] = 0;
   out_3422125367295010588[121] = 0;
   out_3422125367295010588[122] = 0;
   out_3422125367295010588[123] = 0;
   out_3422125367295010588[124] = 0;
   out_3422125367295010588[125] = 0;
   out_3422125367295010588[126] = 0;
   out_3422125367295010588[127] = 0;
   out_3422125367295010588[128] = 0;
   out_3422125367295010588[129] = 0;
   out_3422125367295010588[130] = 0;
   out_3422125367295010588[131] = 0;
   out_3422125367295010588[132] = 0;
   out_3422125367295010588[133] = 1;
   out_3422125367295010588[134] = 0;
   out_3422125367295010588[135] = 0;
   out_3422125367295010588[136] = 0;
   out_3422125367295010588[137] = 0;
   out_3422125367295010588[138] = 0;
   out_3422125367295010588[139] = 0;
   out_3422125367295010588[140] = 0;
   out_3422125367295010588[141] = 0;
   out_3422125367295010588[142] = 0;
   out_3422125367295010588[143] = 0;
   out_3422125367295010588[144] = 0;
   out_3422125367295010588[145] = 0;
   out_3422125367295010588[146] = 0;
   out_3422125367295010588[147] = 0;
   out_3422125367295010588[148] = 0;
   out_3422125367295010588[149] = 0;
   out_3422125367295010588[150] = 0;
   out_3422125367295010588[151] = 0;
   out_3422125367295010588[152] = 1;
   out_3422125367295010588[153] = 0;
   out_3422125367295010588[154] = 0;
   out_3422125367295010588[155] = 0;
   out_3422125367295010588[156] = 0;
   out_3422125367295010588[157] = 0;
   out_3422125367295010588[158] = 0;
   out_3422125367295010588[159] = 0;
   out_3422125367295010588[160] = 0;
   out_3422125367295010588[161] = 0;
   out_3422125367295010588[162] = 0;
   out_3422125367295010588[163] = 0;
   out_3422125367295010588[164] = 0;
   out_3422125367295010588[165] = 0;
   out_3422125367295010588[166] = 0;
   out_3422125367295010588[167] = 0;
   out_3422125367295010588[168] = 0;
   out_3422125367295010588[169] = 0;
   out_3422125367295010588[170] = 0;
   out_3422125367295010588[171] = 1;
   out_3422125367295010588[172] = 0;
   out_3422125367295010588[173] = 0;
   out_3422125367295010588[174] = 0;
   out_3422125367295010588[175] = 0;
   out_3422125367295010588[176] = 0;
   out_3422125367295010588[177] = 0;
   out_3422125367295010588[178] = 0;
   out_3422125367295010588[179] = 0;
   out_3422125367295010588[180] = 0;
   out_3422125367295010588[181] = 0;
   out_3422125367295010588[182] = 0;
   out_3422125367295010588[183] = 0;
   out_3422125367295010588[184] = 0;
   out_3422125367295010588[185] = 0;
   out_3422125367295010588[186] = 0;
   out_3422125367295010588[187] = 0;
   out_3422125367295010588[188] = 0;
   out_3422125367295010588[189] = 0;
   out_3422125367295010588[190] = 1;
   out_3422125367295010588[191] = 0;
   out_3422125367295010588[192] = 0;
   out_3422125367295010588[193] = 0;
   out_3422125367295010588[194] = 0;
   out_3422125367295010588[195] = 0;
   out_3422125367295010588[196] = 0;
   out_3422125367295010588[197] = 0;
   out_3422125367295010588[198] = 0;
   out_3422125367295010588[199] = 0;
   out_3422125367295010588[200] = 0;
   out_3422125367295010588[201] = 0;
   out_3422125367295010588[202] = 0;
   out_3422125367295010588[203] = 0;
   out_3422125367295010588[204] = 0;
   out_3422125367295010588[205] = 0;
   out_3422125367295010588[206] = 0;
   out_3422125367295010588[207] = 0;
   out_3422125367295010588[208] = 0;
   out_3422125367295010588[209] = 1;
   out_3422125367295010588[210] = 0;
   out_3422125367295010588[211] = 0;
   out_3422125367295010588[212] = 0;
   out_3422125367295010588[213] = 0;
   out_3422125367295010588[214] = 0;
   out_3422125367295010588[215] = 0;
   out_3422125367295010588[216] = 0;
   out_3422125367295010588[217] = 0;
   out_3422125367295010588[218] = 0;
   out_3422125367295010588[219] = 0;
   out_3422125367295010588[220] = 0;
   out_3422125367295010588[221] = 0;
   out_3422125367295010588[222] = 0;
   out_3422125367295010588[223] = 0;
   out_3422125367295010588[224] = 0;
   out_3422125367295010588[225] = 0;
   out_3422125367295010588[226] = 0;
   out_3422125367295010588[227] = 0;
   out_3422125367295010588[228] = 1;
   out_3422125367295010588[229] = 0;
   out_3422125367295010588[230] = 0;
   out_3422125367295010588[231] = 0;
   out_3422125367295010588[232] = 0;
   out_3422125367295010588[233] = 0;
   out_3422125367295010588[234] = 0;
   out_3422125367295010588[235] = 0;
   out_3422125367295010588[236] = 0;
   out_3422125367295010588[237] = 0;
   out_3422125367295010588[238] = 0;
   out_3422125367295010588[239] = 0;
   out_3422125367295010588[240] = 0;
   out_3422125367295010588[241] = 0;
   out_3422125367295010588[242] = 0;
   out_3422125367295010588[243] = 0;
   out_3422125367295010588[244] = 0;
   out_3422125367295010588[245] = 0;
   out_3422125367295010588[246] = 0;
   out_3422125367295010588[247] = 1;
   out_3422125367295010588[248] = 0;
   out_3422125367295010588[249] = 0;
   out_3422125367295010588[250] = 0;
   out_3422125367295010588[251] = 0;
   out_3422125367295010588[252] = 0;
   out_3422125367295010588[253] = 0;
   out_3422125367295010588[254] = 0;
   out_3422125367295010588[255] = 0;
   out_3422125367295010588[256] = 0;
   out_3422125367295010588[257] = 0;
   out_3422125367295010588[258] = 0;
   out_3422125367295010588[259] = 0;
   out_3422125367295010588[260] = 0;
   out_3422125367295010588[261] = 0;
   out_3422125367295010588[262] = 0;
   out_3422125367295010588[263] = 0;
   out_3422125367295010588[264] = 0;
   out_3422125367295010588[265] = 0;
   out_3422125367295010588[266] = 1;
   out_3422125367295010588[267] = 0;
   out_3422125367295010588[268] = 0;
   out_3422125367295010588[269] = 0;
   out_3422125367295010588[270] = 0;
   out_3422125367295010588[271] = 0;
   out_3422125367295010588[272] = 0;
   out_3422125367295010588[273] = 0;
   out_3422125367295010588[274] = 0;
   out_3422125367295010588[275] = 0;
   out_3422125367295010588[276] = 0;
   out_3422125367295010588[277] = 0;
   out_3422125367295010588[278] = 0;
   out_3422125367295010588[279] = 0;
   out_3422125367295010588[280] = 0;
   out_3422125367295010588[281] = 0;
   out_3422125367295010588[282] = 0;
   out_3422125367295010588[283] = 0;
   out_3422125367295010588[284] = 0;
   out_3422125367295010588[285] = 1;
   out_3422125367295010588[286] = 0;
   out_3422125367295010588[287] = 0;
   out_3422125367295010588[288] = 0;
   out_3422125367295010588[289] = 0;
   out_3422125367295010588[290] = 0;
   out_3422125367295010588[291] = 0;
   out_3422125367295010588[292] = 0;
   out_3422125367295010588[293] = 0;
   out_3422125367295010588[294] = 0;
   out_3422125367295010588[295] = 0;
   out_3422125367295010588[296] = 0;
   out_3422125367295010588[297] = 0;
   out_3422125367295010588[298] = 0;
   out_3422125367295010588[299] = 0;
   out_3422125367295010588[300] = 0;
   out_3422125367295010588[301] = 0;
   out_3422125367295010588[302] = 0;
   out_3422125367295010588[303] = 0;
   out_3422125367295010588[304] = 1;
   out_3422125367295010588[305] = 0;
   out_3422125367295010588[306] = 0;
   out_3422125367295010588[307] = 0;
   out_3422125367295010588[308] = 0;
   out_3422125367295010588[309] = 0;
   out_3422125367295010588[310] = 0;
   out_3422125367295010588[311] = 0;
   out_3422125367295010588[312] = 0;
   out_3422125367295010588[313] = 0;
   out_3422125367295010588[314] = 0;
   out_3422125367295010588[315] = 0;
   out_3422125367295010588[316] = 0;
   out_3422125367295010588[317] = 0;
   out_3422125367295010588[318] = 0;
   out_3422125367295010588[319] = 0;
   out_3422125367295010588[320] = 0;
   out_3422125367295010588[321] = 0;
   out_3422125367295010588[322] = 0;
   out_3422125367295010588[323] = 1;
}
void h_4(double *state, double *unused, double *out_2817870145355419988) {
   out_2817870145355419988[0] = state[6] + state[9];
   out_2817870145355419988[1] = state[7] + state[10];
   out_2817870145355419988[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_7043089360779003781) {
   out_7043089360779003781[0] = 0;
   out_7043089360779003781[1] = 0;
   out_7043089360779003781[2] = 0;
   out_7043089360779003781[3] = 0;
   out_7043089360779003781[4] = 0;
   out_7043089360779003781[5] = 0;
   out_7043089360779003781[6] = 1;
   out_7043089360779003781[7] = 0;
   out_7043089360779003781[8] = 0;
   out_7043089360779003781[9] = 1;
   out_7043089360779003781[10] = 0;
   out_7043089360779003781[11] = 0;
   out_7043089360779003781[12] = 0;
   out_7043089360779003781[13] = 0;
   out_7043089360779003781[14] = 0;
   out_7043089360779003781[15] = 0;
   out_7043089360779003781[16] = 0;
   out_7043089360779003781[17] = 0;
   out_7043089360779003781[18] = 0;
   out_7043089360779003781[19] = 0;
   out_7043089360779003781[20] = 0;
   out_7043089360779003781[21] = 0;
   out_7043089360779003781[22] = 0;
   out_7043089360779003781[23] = 0;
   out_7043089360779003781[24] = 0;
   out_7043089360779003781[25] = 1;
   out_7043089360779003781[26] = 0;
   out_7043089360779003781[27] = 0;
   out_7043089360779003781[28] = 1;
   out_7043089360779003781[29] = 0;
   out_7043089360779003781[30] = 0;
   out_7043089360779003781[31] = 0;
   out_7043089360779003781[32] = 0;
   out_7043089360779003781[33] = 0;
   out_7043089360779003781[34] = 0;
   out_7043089360779003781[35] = 0;
   out_7043089360779003781[36] = 0;
   out_7043089360779003781[37] = 0;
   out_7043089360779003781[38] = 0;
   out_7043089360779003781[39] = 0;
   out_7043089360779003781[40] = 0;
   out_7043089360779003781[41] = 0;
   out_7043089360779003781[42] = 0;
   out_7043089360779003781[43] = 0;
   out_7043089360779003781[44] = 1;
   out_7043089360779003781[45] = 0;
   out_7043089360779003781[46] = 0;
   out_7043089360779003781[47] = 1;
   out_7043089360779003781[48] = 0;
   out_7043089360779003781[49] = 0;
   out_7043089360779003781[50] = 0;
   out_7043089360779003781[51] = 0;
   out_7043089360779003781[52] = 0;
   out_7043089360779003781[53] = 0;
}
void h_10(double *state, double *unused, double *out_3205891474748426047) {
   out_3205891474748426047[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_3205891474748426047[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_3205891474748426047[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_7912524881714638743) {
   out_7912524881714638743[0] = 0;
   out_7912524881714638743[1] = 9.8100000000000005*cos(state[1]);
   out_7912524881714638743[2] = 0;
   out_7912524881714638743[3] = 0;
   out_7912524881714638743[4] = -state[8];
   out_7912524881714638743[5] = state[7];
   out_7912524881714638743[6] = 0;
   out_7912524881714638743[7] = state[5];
   out_7912524881714638743[8] = -state[4];
   out_7912524881714638743[9] = 0;
   out_7912524881714638743[10] = 0;
   out_7912524881714638743[11] = 0;
   out_7912524881714638743[12] = 1;
   out_7912524881714638743[13] = 0;
   out_7912524881714638743[14] = 0;
   out_7912524881714638743[15] = 1;
   out_7912524881714638743[16] = 0;
   out_7912524881714638743[17] = 0;
   out_7912524881714638743[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_7912524881714638743[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_7912524881714638743[20] = 0;
   out_7912524881714638743[21] = state[8];
   out_7912524881714638743[22] = 0;
   out_7912524881714638743[23] = -state[6];
   out_7912524881714638743[24] = -state[5];
   out_7912524881714638743[25] = 0;
   out_7912524881714638743[26] = state[3];
   out_7912524881714638743[27] = 0;
   out_7912524881714638743[28] = 0;
   out_7912524881714638743[29] = 0;
   out_7912524881714638743[30] = 0;
   out_7912524881714638743[31] = 1;
   out_7912524881714638743[32] = 0;
   out_7912524881714638743[33] = 0;
   out_7912524881714638743[34] = 1;
   out_7912524881714638743[35] = 0;
   out_7912524881714638743[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_7912524881714638743[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_7912524881714638743[38] = 0;
   out_7912524881714638743[39] = -state[7];
   out_7912524881714638743[40] = state[6];
   out_7912524881714638743[41] = 0;
   out_7912524881714638743[42] = state[4];
   out_7912524881714638743[43] = -state[3];
   out_7912524881714638743[44] = 0;
   out_7912524881714638743[45] = 0;
   out_7912524881714638743[46] = 0;
   out_7912524881714638743[47] = 0;
   out_7912524881714638743[48] = 0;
   out_7912524881714638743[49] = 0;
   out_7912524881714638743[50] = 1;
   out_7912524881714638743[51] = 0;
   out_7912524881714638743[52] = 0;
   out_7912524881714638743[53] = 1;
}
void h_13(double *state, double *unused, double *out_4580396760279803780) {
   out_4580396760279803780[0] = state[3];
   out_4580396760279803780[1] = state[4];
   out_4580396760279803780[2] = state[5];
}
void H_13(double *state, double *unused, double *out_3793023504613846906) {
   out_3793023504613846906[0] = 0;
   out_3793023504613846906[1] = 0;
   out_3793023504613846906[2] = 0;
   out_3793023504613846906[3] = 1;
   out_3793023504613846906[4] = 0;
   out_3793023504613846906[5] = 0;
   out_3793023504613846906[6] = 0;
   out_3793023504613846906[7] = 0;
   out_3793023504613846906[8] = 0;
   out_3793023504613846906[9] = 0;
   out_3793023504613846906[10] = 0;
   out_3793023504613846906[11] = 0;
   out_3793023504613846906[12] = 0;
   out_3793023504613846906[13] = 0;
   out_3793023504613846906[14] = 0;
   out_3793023504613846906[15] = 0;
   out_3793023504613846906[16] = 0;
   out_3793023504613846906[17] = 0;
   out_3793023504613846906[18] = 0;
   out_3793023504613846906[19] = 0;
   out_3793023504613846906[20] = 0;
   out_3793023504613846906[21] = 0;
   out_3793023504613846906[22] = 1;
   out_3793023504613846906[23] = 0;
   out_3793023504613846906[24] = 0;
   out_3793023504613846906[25] = 0;
   out_3793023504613846906[26] = 0;
   out_3793023504613846906[27] = 0;
   out_3793023504613846906[28] = 0;
   out_3793023504613846906[29] = 0;
   out_3793023504613846906[30] = 0;
   out_3793023504613846906[31] = 0;
   out_3793023504613846906[32] = 0;
   out_3793023504613846906[33] = 0;
   out_3793023504613846906[34] = 0;
   out_3793023504613846906[35] = 0;
   out_3793023504613846906[36] = 0;
   out_3793023504613846906[37] = 0;
   out_3793023504613846906[38] = 0;
   out_3793023504613846906[39] = 0;
   out_3793023504613846906[40] = 0;
   out_3793023504613846906[41] = 1;
   out_3793023504613846906[42] = 0;
   out_3793023504613846906[43] = 0;
   out_3793023504613846906[44] = 0;
   out_3793023504613846906[45] = 0;
   out_3793023504613846906[46] = 0;
   out_3793023504613846906[47] = 0;
   out_3793023504613846906[48] = 0;
   out_3793023504613846906[49] = 0;
   out_3793023504613846906[50] = 0;
   out_3793023504613846906[51] = 0;
   out_3793023504613846906[52] = 0;
   out_3793023504613846906[53] = 0;
}
void h_14(double *state, double *unused, double *out_4584687085492276109) {
   out_4584687085492276109[0] = state[6];
   out_4584687085492276109[1] = state[7];
   out_4584687085492276109[2] = state[8];
}
void H_14(double *state, double *unused, double *out_7440413856591063306) {
   out_7440413856591063306[0] = 0;
   out_7440413856591063306[1] = 0;
   out_7440413856591063306[2] = 0;
   out_7440413856591063306[3] = 0;
   out_7440413856591063306[4] = 0;
   out_7440413856591063306[5] = 0;
   out_7440413856591063306[6] = 1;
   out_7440413856591063306[7] = 0;
   out_7440413856591063306[8] = 0;
   out_7440413856591063306[9] = 0;
   out_7440413856591063306[10] = 0;
   out_7440413856591063306[11] = 0;
   out_7440413856591063306[12] = 0;
   out_7440413856591063306[13] = 0;
   out_7440413856591063306[14] = 0;
   out_7440413856591063306[15] = 0;
   out_7440413856591063306[16] = 0;
   out_7440413856591063306[17] = 0;
   out_7440413856591063306[18] = 0;
   out_7440413856591063306[19] = 0;
   out_7440413856591063306[20] = 0;
   out_7440413856591063306[21] = 0;
   out_7440413856591063306[22] = 0;
   out_7440413856591063306[23] = 0;
   out_7440413856591063306[24] = 0;
   out_7440413856591063306[25] = 1;
   out_7440413856591063306[26] = 0;
   out_7440413856591063306[27] = 0;
   out_7440413856591063306[28] = 0;
   out_7440413856591063306[29] = 0;
   out_7440413856591063306[30] = 0;
   out_7440413856591063306[31] = 0;
   out_7440413856591063306[32] = 0;
   out_7440413856591063306[33] = 0;
   out_7440413856591063306[34] = 0;
   out_7440413856591063306[35] = 0;
   out_7440413856591063306[36] = 0;
   out_7440413856591063306[37] = 0;
   out_7440413856591063306[38] = 0;
   out_7440413856591063306[39] = 0;
   out_7440413856591063306[40] = 0;
   out_7440413856591063306[41] = 0;
   out_7440413856591063306[42] = 0;
   out_7440413856591063306[43] = 0;
   out_7440413856591063306[44] = 1;
   out_7440413856591063306[45] = 0;
   out_7440413856591063306[46] = 0;
   out_7440413856591063306[47] = 0;
   out_7440413856591063306[48] = 0;
   out_7440413856591063306[49] = 0;
   out_7440413856591063306[50] = 0;
   out_7440413856591063306[51] = 0;
   out_7440413856591063306[52] = 0;
   out_7440413856591063306[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_8253506042582469219) {
  err_fun(nom_x, delta_x, out_8253506042582469219);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_2344330990237256254) {
  inv_err_fun(nom_x, true_x, out_2344330990237256254);
}
void pose_H_mod_fun(double *state, double *out_1157215523194220986) {
  H_mod_fun(state, out_1157215523194220986);
}
void pose_f_fun(double *state, double dt, double *out_6204252535340020659) {
  f_fun(state,  dt, out_6204252535340020659);
}
void pose_F_fun(double *state, double dt, double *out_3422125367295010588) {
  F_fun(state,  dt, out_3422125367295010588);
}
void pose_h_4(double *state, double *unused, double *out_2817870145355419988) {
  h_4(state, unused, out_2817870145355419988);
}
void pose_H_4(double *state, double *unused, double *out_7043089360779003781) {
  H_4(state, unused, out_7043089360779003781);
}
void pose_h_10(double *state, double *unused, double *out_3205891474748426047) {
  h_10(state, unused, out_3205891474748426047);
}
void pose_H_10(double *state, double *unused, double *out_7912524881714638743) {
  H_10(state, unused, out_7912524881714638743);
}
void pose_h_13(double *state, double *unused, double *out_4580396760279803780) {
  h_13(state, unused, out_4580396760279803780);
}
void pose_H_13(double *state, double *unused, double *out_3793023504613846906) {
  H_13(state, unused, out_3793023504613846906);
}
void pose_h_14(double *state, double *unused, double *out_4584687085492276109) {
  h_14(state, unused, out_4584687085492276109);
}
void pose_H_14(double *state, double *unused, double *out_7440413856591063306) {
  H_14(state, unused, out_7440413856591063306);
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
