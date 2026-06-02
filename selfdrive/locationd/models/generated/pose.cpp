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
void err_fun(double *nom_x, double *delta_x, double *out_2192517159883214491) {
   out_2192517159883214491[0] = delta_x[0] + nom_x[0];
   out_2192517159883214491[1] = delta_x[1] + nom_x[1];
   out_2192517159883214491[2] = delta_x[2] + nom_x[2];
   out_2192517159883214491[3] = delta_x[3] + nom_x[3];
   out_2192517159883214491[4] = delta_x[4] + nom_x[4];
   out_2192517159883214491[5] = delta_x[5] + nom_x[5];
   out_2192517159883214491[6] = delta_x[6] + nom_x[6];
   out_2192517159883214491[7] = delta_x[7] + nom_x[7];
   out_2192517159883214491[8] = delta_x[8] + nom_x[8];
   out_2192517159883214491[9] = delta_x[9] + nom_x[9];
   out_2192517159883214491[10] = delta_x[10] + nom_x[10];
   out_2192517159883214491[11] = delta_x[11] + nom_x[11];
   out_2192517159883214491[12] = delta_x[12] + nom_x[12];
   out_2192517159883214491[13] = delta_x[13] + nom_x[13];
   out_2192517159883214491[14] = delta_x[14] + nom_x[14];
   out_2192517159883214491[15] = delta_x[15] + nom_x[15];
   out_2192517159883214491[16] = delta_x[16] + nom_x[16];
   out_2192517159883214491[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7620744679476459470) {
   out_7620744679476459470[0] = -nom_x[0] + true_x[0];
   out_7620744679476459470[1] = -nom_x[1] + true_x[1];
   out_7620744679476459470[2] = -nom_x[2] + true_x[2];
   out_7620744679476459470[3] = -nom_x[3] + true_x[3];
   out_7620744679476459470[4] = -nom_x[4] + true_x[4];
   out_7620744679476459470[5] = -nom_x[5] + true_x[5];
   out_7620744679476459470[6] = -nom_x[6] + true_x[6];
   out_7620744679476459470[7] = -nom_x[7] + true_x[7];
   out_7620744679476459470[8] = -nom_x[8] + true_x[8];
   out_7620744679476459470[9] = -nom_x[9] + true_x[9];
   out_7620744679476459470[10] = -nom_x[10] + true_x[10];
   out_7620744679476459470[11] = -nom_x[11] + true_x[11];
   out_7620744679476459470[12] = -nom_x[12] + true_x[12];
   out_7620744679476459470[13] = -nom_x[13] + true_x[13];
   out_7620744679476459470[14] = -nom_x[14] + true_x[14];
   out_7620744679476459470[15] = -nom_x[15] + true_x[15];
   out_7620744679476459470[16] = -nom_x[16] + true_x[16];
   out_7620744679476459470[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_7476444296888154553) {
   out_7476444296888154553[0] = 1.0;
   out_7476444296888154553[1] = 0.0;
   out_7476444296888154553[2] = 0.0;
   out_7476444296888154553[3] = 0.0;
   out_7476444296888154553[4] = 0.0;
   out_7476444296888154553[5] = 0.0;
   out_7476444296888154553[6] = 0.0;
   out_7476444296888154553[7] = 0.0;
   out_7476444296888154553[8] = 0.0;
   out_7476444296888154553[9] = 0.0;
   out_7476444296888154553[10] = 0.0;
   out_7476444296888154553[11] = 0.0;
   out_7476444296888154553[12] = 0.0;
   out_7476444296888154553[13] = 0.0;
   out_7476444296888154553[14] = 0.0;
   out_7476444296888154553[15] = 0.0;
   out_7476444296888154553[16] = 0.0;
   out_7476444296888154553[17] = 0.0;
   out_7476444296888154553[18] = 0.0;
   out_7476444296888154553[19] = 1.0;
   out_7476444296888154553[20] = 0.0;
   out_7476444296888154553[21] = 0.0;
   out_7476444296888154553[22] = 0.0;
   out_7476444296888154553[23] = 0.0;
   out_7476444296888154553[24] = 0.0;
   out_7476444296888154553[25] = 0.0;
   out_7476444296888154553[26] = 0.0;
   out_7476444296888154553[27] = 0.0;
   out_7476444296888154553[28] = 0.0;
   out_7476444296888154553[29] = 0.0;
   out_7476444296888154553[30] = 0.0;
   out_7476444296888154553[31] = 0.0;
   out_7476444296888154553[32] = 0.0;
   out_7476444296888154553[33] = 0.0;
   out_7476444296888154553[34] = 0.0;
   out_7476444296888154553[35] = 0.0;
   out_7476444296888154553[36] = 0.0;
   out_7476444296888154553[37] = 0.0;
   out_7476444296888154553[38] = 1.0;
   out_7476444296888154553[39] = 0.0;
   out_7476444296888154553[40] = 0.0;
   out_7476444296888154553[41] = 0.0;
   out_7476444296888154553[42] = 0.0;
   out_7476444296888154553[43] = 0.0;
   out_7476444296888154553[44] = 0.0;
   out_7476444296888154553[45] = 0.0;
   out_7476444296888154553[46] = 0.0;
   out_7476444296888154553[47] = 0.0;
   out_7476444296888154553[48] = 0.0;
   out_7476444296888154553[49] = 0.0;
   out_7476444296888154553[50] = 0.0;
   out_7476444296888154553[51] = 0.0;
   out_7476444296888154553[52] = 0.0;
   out_7476444296888154553[53] = 0.0;
   out_7476444296888154553[54] = 0.0;
   out_7476444296888154553[55] = 0.0;
   out_7476444296888154553[56] = 0.0;
   out_7476444296888154553[57] = 1.0;
   out_7476444296888154553[58] = 0.0;
   out_7476444296888154553[59] = 0.0;
   out_7476444296888154553[60] = 0.0;
   out_7476444296888154553[61] = 0.0;
   out_7476444296888154553[62] = 0.0;
   out_7476444296888154553[63] = 0.0;
   out_7476444296888154553[64] = 0.0;
   out_7476444296888154553[65] = 0.0;
   out_7476444296888154553[66] = 0.0;
   out_7476444296888154553[67] = 0.0;
   out_7476444296888154553[68] = 0.0;
   out_7476444296888154553[69] = 0.0;
   out_7476444296888154553[70] = 0.0;
   out_7476444296888154553[71] = 0.0;
   out_7476444296888154553[72] = 0.0;
   out_7476444296888154553[73] = 0.0;
   out_7476444296888154553[74] = 0.0;
   out_7476444296888154553[75] = 0.0;
   out_7476444296888154553[76] = 1.0;
   out_7476444296888154553[77] = 0.0;
   out_7476444296888154553[78] = 0.0;
   out_7476444296888154553[79] = 0.0;
   out_7476444296888154553[80] = 0.0;
   out_7476444296888154553[81] = 0.0;
   out_7476444296888154553[82] = 0.0;
   out_7476444296888154553[83] = 0.0;
   out_7476444296888154553[84] = 0.0;
   out_7476444296888154553[85] = 0.0;
   out_7476444296888154553[86] = 0.0;
   out_7476444296888154553[87] = 0.0;
   out_7476444296888154553[88] = 0.0;
   out_7476444296888154553[89] = 0.0;
   out_7476444296888154553[90] = 0.0;
   out_7476444296888154553[91] = 0.0;
   out_7476444296888154553[92] = 0.0;
   out_7476444296888154553[93] = 0.0;
   out_7476444296888154553[94] = 0.0;
   out_7476444296888154553[95] = 1.0;
   out_7476444296888154553[96] = 0.0;
   out_7476444296888154553[97] = 0.0;
   out_7476444296888154553[98] = 0.0;
   out_7476444296888154553[99] = 0.0;
   out_7476444296888154553[100] = 0.0;
   out_7476444296888154553[101] = 0.0;
   out_7476444296888154553[102] = 0.0;
   out_7476444296888154553[103] = 0.0;
   out_7476444296888154553[104] = 0.0;
   out_7476444296888154553[105] = 0.0;
   out_7476444296888154553[106] = 0.0;
   out_7476444296888154553[107] = 0.0;
   out_7476444296888154553[108] = 0.0;
   out_7476444296888154553[109] = 0.0;
   out_7476444296888154553[110] = 0.0;
   out_7476444296888154553[111] = 0.0;
   out_7476444296888154553[112] = 0.0;
   out_7476444296888154553[113] = 0.0;
   out_7476444296888154553[114] = 1.0;
   out_7476444296888154553[115] = 0.0;
   out_7476444296888154553[116] = 0.0;
   out_7476444296888154553[117] = 0.0;
   out_7476444296888154553[118] = 0.0;
   out_7476444296888154553[119] = 0.0;
   out_7476444296888154553[120] = 0.0;
   out_7476444296888154553[121] = 0.0;
   out_7476444296888154553[122] = 0.0;
   out_7476444296888154553[123] = 0.0;
   out_7476444296888154553[124] = 0.0;
   out_7476444296888154553[125] = 0.0;
   out_7476444296888154553[126] = 0.0;
   out_7476444296888154553[127] = 0.0;
   out_7476444296888154553[128] = 0.0;
   out_7476444296888154553[129] = 0.0;
   out_7476444296888154553[130] = 0.0;
   out_7476444296888154553[131] = 0.0;
   out_7476444296888154553[132] = 0.0;
   out_7476444296888154553[133] = 1.0;
   out_7476444296888154553[134] = 0.0;
   out_7476444296888154553[135] = 0.0;
   out_7476444296888154553[136] = 0.0;
   out_7476444296888154553[137] = 0.0;
   out_7476444296888154553[138] = 0.0;
   out_7476444296888154553[139] = 0.0;
   out_7476444296888154553[140] = 0.0;
   out_7476444296888154553[141] = 0.0;
   out_7476444296888154553[142] = 0.0;
   out_7476444296888154553[143] = 0.0;
   out_7476444296888154553[144] = 0.0;
   out_7476444296888154553[145] = 0.0;
   out_7476444296888154553[146] = 0.0;
   out_7476444296888154553[147] = 0.0;
   out_7476444296888154553[148] = 0.0;
   out_7476444296888154553[149] = 0.0;
   out_7476444296888154553[150] = 0.0;
   out_7476444296888154553[151] = 0.0;
   out_7476444296888154553[152] = 1.0;
   out_7476444296888154553[153] = 0.0;
   out_7476444296888154553[154] = 0.0;
   out_7476444296888154553[155] = 0.0;
   out_7476444296888154553[156] = 0.0;
   out_7476444296888154553[157] = 0.0;
   out_7476444296888154553[158] = 0.0;
   out_7476444296888154553[159] = 0.0;
   out_7476444296888154553[160] = 0.0;
   out_7476444296888154553[161] = 0.0;
   out_7476444296888154553[162] = 0.0;
   out_7476444296888154553[163] = 0.0;
   out_7476444296888154553[164] = 0.0;
   out_7476444296888154553[165] = 0.0;
   out_7476444296888154553[166] = 0.0;
   out_7476444296888154553[167] = 0.0;
   out_7476444296888154553[168] = 0.0;
   out_7476444296888154553[169] = 0.0;
   out_7476444296888154553[170] = 0.0;
   out_7476444296888154553[171] = 1.0;
   out_7476444296888154553[172] = 0.0;
   out_7476444296888154553[173] = 0.0;
   out_7476444296888154553[174] = 0.0;
   out_7476444296888154553[175] = 0.0;
   out_7476444296888154553[176] = 0.0;
   out_7476444296888154553[177] = 0.0;
   out_7476444296888154553[178] = 0.0;
   out_7476444296888154553[179] = 0.0;
   out_7476444296888154553[180] = 0.0;
   out_7476444296888154553[181] = 0.0;
   out_7476444296888154553[182] = 0.0;
   out_7476444296888154553[183] = 0.0;
   out_7476444296888154553[184] = 0.0;
   out_7476444296888154553[185] = 0.0;
   out_7476444296888154553[186] = 0.0;
   out_7476444296888154553[187] = 0.0;
   out_7476444296888154553[188] = 0.0;
   out_7476444296888154553[189] = 0.0;
   out_7476444296888154553[190] = 1.0;
   out_7476444296888154553[191] = 0.0;
   out_7476444296888154553[192] = 0.0;
   out_7476444296888154553[193] = 0.0;
   out_7476444296888154553[194] = 0.0;
   out_7476444296888154553[195] = 0.0;
   out_7476444296888154553[196] = 0.0;
   out_7476444296888154553[197] = 0.0;
   out_7476444296888154553[198] = 0.0;
   out_7476444296888154553[199] = 0.0;
   out_7476444296888154553[200] = 0.0;
   out_7476444296888154553[201] = 0.0;
   out_7476444296888154553[202] = 0.0;
   out_7476444296888154553[203] = 0.0;
   out_7476444296888154553[204] = 0.0;
   out_7476444296888154553[205] = 0.0;
   out_7476444296888154553[206] = 0.0;
   out_7476444296888154553[207] = 0.0;
   out_7476444296888154553[208] = 0.0;
   out_7476444296888154553[209] = 1.0;
   out_7476444296888154553[210] = 0.0;
   out_7476444296888154553[211] = 0.0;
   out_7476444296888154553[212] = 0.0;
   out_7476444296888154553[213] = 0.0;
   out_7476444296888154553[214] = 0.0;
   out_7476444296888154553[215] = 0.0;
   out_7476444296888154553[216] = 0.0;
   out_7476444296888154553[217] = 0.0;
   out_7476444296888154553[218] = 0.0;
   out_7476444296888154553[219] = 0.0;
   out_7476444296888154553[220] = 0.0;
   out_7476444296888154553[221] = 0.0;
   out_7476444296888154553[222] = 0.0;
   out_7476444296888154553[223] = 0.0;
   out_7476444296888154553[224] = 0.0;
   out_7476444296888154553[225] = 0.0;
   out_7476444296888154553[226] = 0.0;
   out_7476444296888154553[227] = 0.0;
   out_7476444296888154553[228] = 1.0;
   out_7476444296888154553[229] = 0.0;
   out_7476444296888154553[230] = 0.0;
   out_7476444296888154553[231] = 0.0;
   out_7476444296888154553[232] = 0.0;
   out_7476444296888154553[233] = 0.0;
   out_7476444296888154553[234] = 0.0;
   out_7476444296888154553[235] = 0.0;
   out_7476444296888154553[236] = 0.0;
   out_7476444296888154553[237] = 0.0;
   out_7476444296888154553[238] = 0.0;
   out_7476444296888154553[239] = 0.0;
   out_7476444296888154553[240] = 0.0;
   out_7476444296888154553[241] = 0.0;
   out_7476444296888154553[242] = 0.0;
   out_7476444296888154553[243] = 0.0;
   out_7476444296888154553[244] = 0.0;
   out_7476444296888154553[245] = 0.0;
   out_7476444296888154553[246] = 0.0;
   out_7476444296888154553[247] = 1.0;
   out_7476444296888154553[248] = 0.0;
   out_7476444296888154553[249] = 0.0;
   out_7476444296888154553[250] = 0.0;
   out_7476444296888154553[251] = 0.0;
   out_7476444296888154553[252] = 0.0;
   out_7476444296888154553[253] = 0.0;
   out_7476444296888154553[254] = 0.0;
   out_7476444296888154553[255] = 0.0;
   out_7476444296888154553[256] = 0.0;
   out_7476444296888154553[257] = 0.0;
   out_7476444296888154553[258] = 0.0;
   out_7476444296888154553[259] = 0.0;
   out_7476444296888154553[260] = 0.0;
   out_7476444296888154553[261] = 0.0;
   out_7476444296888154553[262] = 0.0;
   out_7476444296888154553[263] = 0.0;
   out_7476444296888154553[264] = 0.0;
   out_7476444296888154553[265] = 0.0;
   out_7476444296888154553[266] = 1.0;
   out_7476444296888154553[267] = 0.0;
   out_7476444296888154553[268] = 0.0;
   out_7476444296888154553[269] = 0.0;
   out_7476444296888154553[270] = 0.0;
   out_7476444296888154553[271] = 0.0;
   out_7476444296888154553[272] = 0.0;
   out_7476444296888154553[273] = 0.0;
   out_7476444296888154553[274] = 0.0;
   out_7476444296888154553[275] = 0.0;
   out_7476444296888154553[276] = 0.0;
   out_7476444296888154553[277] = 0.0;
   out_7476444296888154553[278] = 0.0;
   out_7476444296888154553[279] = 0.0;
   out_7476444296888154553[280] = 0.0;
   out_7476444296888154553[281] = 0.0;
   out_7476444296888154553[282] = 0.0;
   out_7476444296888154553[283] = 0.0;
   out_7476444296888154553[284] = 0.0;
   out_7476444296888154553[285] = 1.0;
   out_7476444296888154553[286] = 0.0;
   out_7476444296888154553[287] = 0.0;
   out_7476444296888154553[288] = 0.0;
   out_7476444296888154553[289] = 0.0;
   out_7476444296888154553[290] = 0.0;
   out_7476444296888154553[291] = 0.0;
   out_7476444296888154553[292] = 0.0;
   out_7476444296888154553[293] = 0.0;
   out_7476444296888154553[294] = 0.0;
   out_7476444296888154553[295] = 0.0;
   out_7476444296888154553[296] = 0.0;
   out_7476444296888154553[297] = 0.0;
   out_7476444296888154553[298] = 0.0;
   out_7476444296888154553[299] = 0.0;
   out_7476444296888154553[300] = 0.0;
   out_7476444296888154553[301] = 0.0;
   out_7476444296888154553[302] = 0.0;
   out_7476444296888154553[303] = 0.0;
   out_7476444296888154553[304] = 1.0;
   out_7476444296888154553[305] = 0.0;
   out_7476444296888154553[306] = 0.0;
   out_7476444296888154553[307] = 0.0;
   out_7476444296888154553[308] = 0.0;
   out_7476444296888154553[309] = 0.0;
   out_7476444296888154553[310] = 0.0;
   out_7476444296888154553[311] = 0.0;
   out_7476444296888154553[312] = 0.0;
   out_7476444296888154553[313] = 0.0;
   out_7476444296888154553[314] = 0.0;
   out_7476444296888154553[315] = 0.0;
   out_7476444296888154553[316] = 0.0;
   out_7476444296888154553[317] = 0.0;
   out_7476444296888154553[318] = 0.0;
   out_7476444296888154553[319] = 0.0;
   out_7476444296888154553[320] = 0.0;
   out_7476444296888154553[321] = 0.0;
   out_7476444296888154553[322] = 0.0;
   out_7476444296888154553[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_5554352162049920971) {
   out_5554352162049920971[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_5554352162049920971[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_5554352162049920971[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_5554352162049920971[3] = dt*state[12] + state[3];
   out_5554352162049920971[4] = dt*state[13] + state[4];
   out_5554352162049920971[5] = dt*state[14] + state[5];
   out_5554352162049920971[6] = state[6];
   out_5554352162049920971[7] = state[7];
   out_5554352162049920971[8] = state[8];
   out_5554352162049920971[9] = state[9];
   out_5554352162049920971[10] = state[10];
   out_5554352162049920971[11] = state[11];
   out_5554352162049920971[12] = state[12];
   out_5554352162049920971[13] = state[13];
   out_5554352162049920971[14] = state[14];
   out_5554352162049920971[15] = state[15];
   out_5554352162049920971[16] = state[16];
   out_5554352162049920971[17] = state[17];
}
void F_fun(double *state, double dt, double *out_6614407721487933261) {
   out_6614407721487933261[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6614407721487933261[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6614407721487933261[2] = 0;
   out_6614407721487933261[3] = 0;
   out_6614407721487933261[4] = 0;
   out_6614407721487933261[5] = 0;
   out_6614407721487933261[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6614407721487933261[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6614407721487933261[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6614407721487933261[9] = 0;
   out_6614407721487933261[10] = 0;
   out_6614407721487933261[11] = 0;
   out_6614407721487933261[12] = 0;
   out_6614407721487933261[13] = 0;
   out_6614407721487933261[14] = 0;
   out_6614407721487933261[15] = 0;
   out_6614407721487933261[16] = 0;
   out_6614407721487933261[17] = 0;
   out_6614407721487933261[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6614407721487933261[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6614407721487933261[20] = 0;
   out_6614407721487933261[21] = 0;
   out_6614407721487933261[22] = 0;
   out_6614407721487933261[23] = 0;
   out_6614407721487933261[24] = 0;
   out_6614407721487933261[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6614407721487933261[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6614407721487933261[27] = 0;
   out_6614407721487933261[28] = 0;
   out_6614407721487933261[29] = 0;
   out_6614407721487933261[30] = 0;
   out_6614407721487933261[31] = 0;
   out_6614407721487933261[32] = 0;
   out_6614407721487933261[33] = 0;
   out_6614407721487933261[34] = 0;
   out_6614407721487933261[35] = 0;
   out_6614407721487933261[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6614407721487933261[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6614407721487933261[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6614407721487933261[39] = 0;
   out_6614407721487933261[40] = 0;
   out_6614407721487933261[41] = 0;
   out_6614407721487933261[42] = 0;
   out_6614407721487933261[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6614407721487933261[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6614407721487933261[45] = 0;
   out_6614407721487933261[46] = 0;
   out_6614407721487933261[47] = 0;
   out_6614407721487933261[48] = 0;
   out_6614407721487933261[49] = 0;
   out_6614407721487933261[50] = 0;
   out_6614407721487933261[51] = 0;
   out_6614407721487933261[52] = 0;
   out_6614407721487933261[53] = 0;
   out_6614407721487933261[54] = 0;
   out_6614407721487933261[55] = 0;
   out_6614407721487933261[56] = 0;
   out_6614407721487933261[57] = 1;
   out_6614407721487933261[58] = 0;
   out_6614407721487933261[59] = 0;
   out_6614407721487933261[60] = 0;
   out_6614407721487933261[61] = 0;
   out_6614407721487933261[62] = 0;
   out_6614407721487933261[63] = 0;
   out_6614407721487933261[64] = 0;
   out_6614407721487933261[65] = 0;
   out_6614407721487933261[66] = dt;
   out_6614407721487933261[67] = 0;
   out_6614407721487933261[68] = 0;
   out_6614407721487933261[69] = 0;
   out_6614407721487933261[70] = 0;
   out_6614407721487933261[71] = 0;
   out_6614407721487933261[72] = 0;
   out_6614407721487933261[73] = 0;
   out_6614407721487933261[74] = 0;
   out_6614407721487933261[75] = 0;
   out_6614407721487933261[76] = 1;
   out_6614407721487933261[77] = 0;
   out_6614407721487933261[78] = 0;
   out_6614407721487933261[79] = 0;
   out_6614407721487933261[80] = 0;
   out_6614407721487933261[81] = 0;
   out_6614407721487933261[82] = 0;
   out_6614407721487933261[83] = 0;
   out_6614407721487933261[84] = 0;
   out_6614407721487933261[85] = dt;
   out_6614407721487933261[86] = 0;
   out_6614407721487933261[87] = 0;
   out_6614407721487933261[88] = 0;
   out_6614407721487933261[89] = 0;
   out_6614407721487933261[90] = 0;
   out_6614407721487933261[91] = 0;
   out_6614407721487933261[92] = 0;
   out_6614407721487933261[93] = 0;
   out_6614407721487933261[94] = 0;
   out_6614407721487933261[95] = 1;
   out_6614407721487933261[96] = 0;
   out_6614407721487933261[97] = 0;
   out_6614407721487933261[98] = 0;
   out_6614407721487933261[99] = 0;
   out_6614407721487933261[100] = 0;
   out_6614407721487933261[101] = 0;
   out_6614407721487933261[102] = 0;
   out_6614407721487933261[103] = 0;
   out_6614407721487933261[104] = dt;
   out_6614407721487933261[105] = 0;
   out_6614407721487933261[106] = 0;
   out_6614407721487933261[107] = 0;
   out_6614407721487933261[108] = 0;
   out_6614407721487933261[109] = 0;
   out_6614407721487933261[110] = 0;
   out_6614407721487933261[111] = 0;
   out_6614407721487933261[112] = 0;
   out_6614407721487933261[113] = 0;
   out_6614407721487933261[114] = 1;
   out_6614407721487933261[115] = 0;
   out_6614407721487933261[116] = 0;
   out_6614407721487933261[117] = 0;
   out_6614407721487933261[118] = 0;
   out_6614407721487933261[119] = 0;
   out_6614407721487933261[120] = 0;
   out_6614407721487933261[121] = 0;
   out_6614407721487933261[122] = 0;
   out_6614407721487933261[123] = 0;
   out_6614407721487933261[124] = 0;
   out_6614407721487933261[125] = 0;
   out_6614407721487933261[126] = 0;
   out_6614407721487933261[127] = 0;
   out_6614407721487933261[128] = 0;
   out_6614407721487933261[129] = 0;
   out_6614407721487933261[130] = 0;
   out_6614407721487933261[131] = 0;
   out_6614407721487933261[132] = 0;
   out_6614407721487933261[133] = 1;
   out_6614407721487933261[134] = 0;
   out_6614407721487933261[135] = 0;
   out_6614407721487933261[136] = 0;
   out_6614407721487933261[137] = 0;
   out_6614407721487933261[138] = 0;
   out_6614407721487933261[139] = 0;
   out_6614407721487933261[140] = 0;
   out_6614407721487933261[141] = 0;
   out_6614407721487933261[142] = 0;
   out_6614407721487933261[143] = 0;
   out_6614407721487933261[144] = 0;
   out_6614407721487933261[145] = 0;
   out_6614407721487933261[146] = 0;
   out_6614407721487933261[147] = 0;
   out_6614407721487933261[148] = 0;
   out_6614407721487933261[149] = 0;
   out_6614407721487933261[150] = 0;
   out_6614407721487933261[151] = 0;
   out_6614407721487933261[152] = 1;
   out_6614407721487933261[153] = 0;
   out_6614407721487933261[154] = 0;
   out_6614407721487933261[155] = 0;
   out_6614407721487933261[156] = 0;
   out_6614407721487933261[157] = 0;
   out_6614407721487933261[158] = 0;
   out_6614407721487933261[159] = 0;
   out_6614407721487933261[160] = 0;
   out_6614407721487933261[161] = 0;
   out_6614407721487933261[162] = 0;
   out_6614407721487933261[163] = 0;
   out_6614407721487933261[164] = 0;
   out_6614407721487933261[165] = 0;
   out_6614407721487933261[166] = 0;
   out_6614407721487933261[167] = 0;
   out_6614407721487933261[168] = 0;
   out_6614407721487933261[169] = 0;
   out_6614407721487933261[170] = 0;
   out_6614407721487933261[171] = 1;
   out_6614407721487933261[172] = 0;
   out_6614407721487933261[173] = 0;
   out_6614407721487933261[174] = 0;
   out_6614407721487933261[175] = 0;
   out_6614407721487933261[176] = 0;
   out_6614407721487933261[177] = 0;
   out_6614407721487933261[178] = 0;
   out_6614407721487933261[179] = 0;
   out_6614407721487933261[180] = 0;
   out_6614407721487933261[181] = 0;
   out_6614407721487933261[182] = 0;
   out_6614407721487933261[183] = 0;
   out_6614407721487933261[184] = 0;
   out_6614407721487933261[185] = 0;
   out_6614407721487933261[186] = 0;
   out_6614407721487933261[187] = 0;
   out_6614407721487933261[188] = 0;
   out_6614407721487933261[189] = 0;
   out_6614407721487933261[190] = 1;
   out_6614407721487933261[191] = 0;
   out_6614407721487933261[192] = 0;
   out_6614407721487933261[193] = 0;
   out_6614407721487933261[194] = 0;
   out_6614407721487933261[195] = 0;
   out_6614407721487933261[196] = 0;
   out_6614407721487933261[197] = 0;
   out_6614407721487933261[198] = 0;
   out_6614407721487933261[199] = 0;
   out_6614407721487933261[200] = 0;
   out_6614407721487933261[201] = 0;
   out_6614407721487933261[202] = 0;
   out_6614407721487933261[203] = 0;
   out_6614407721487933261[204] = 0;
   out_6614407721487933261[205] = 0;
   out_6614407721487933261[206] = 0;
   out_6614407721487933261[207] = 0;
   out_6614407721487933261[208] = 0;
   out_6614407721487933261[209] = 1;
   out_6614407721487933261[210] = 0;
   out_6614407721487933261[211] = 0;
   out_6614407721487933261[212] = 0;
   out_6614407721487933261[213] = 0;
   out_6614407721487933261[214] = 0;
   out_6614407721487933261[215] = 0;
   out_6614407721487933261[216] = 0;
   out_6614407721487933261[217] = 0;
   out_6614407721487933261[218] = 0;
   out_6614407721487933261[219] = 0;
   out_6614407721487933261[220] = 0;
   out_6614407721487933261[221] = 0;
   out_6614407721487933261[222] = 0;
   out_6614407721487933261[223] = 0;
   out_6614407721487933261[224] = 0;
   out_6614407721487933261[225] = 0;
   out_6614407721487933261[226] = 0;
   out_6614407721487933261[227] = 0;
   out_6614407721487933261[228] = 1;
   out_6614407721487933261[229] = 0;
   out_6614407721487933261[230] = 0;
   out_6614407721487933261[231] = 0;
   out_6614407721487933261[232] = 0;
   out_6614407721487933261[233] = 0;
   out_6614407721487933261[234] = 0;
   out_6614407721487933261[235] = 0;
   out_6614407721487933261[236] = 0;
   out_6614407721487933261[237] = 0;
   out_6614407721487933261[238] = 0;
   out_6614407721487933261[239] = 0;
   out_6614407721487933261[240] = 0;
   out_6614407721487933261[241] = 0;
   out_6614407721487933261[242] = 0;
   out_6614407721487933261[243] = 0;
   out_6614407721487933261[244] = 0;
   out_6614407721487933261[245] = 0;
   out_6614407721487933261[246] = 0;
   out_6614407721487933261[247] = 1;
   out_6614407721487933261[248] = 0;
   out_6614407721487933261[249] = 0;
   out_6614407721487933261[250] = 0;
   out_6614407721487933261[251] = 0;
   out_6614407721487933261[252] = 0;
   out_6614407721487933261[253] = 0;
   out_6614407721487933261[254] = 0;
   out_6614407721487933261[255] = 0;
   out_6614407721487933261[256] = 0;
   out_6614407721487933261[257] = 0;
   out_6614407721487933261[258] = 0;
   out_6614407721487933261[259] = 0;
   out_6614407721487933261[260] = 0;
   out_6614407721487933261[261] = 0;
   out_6614407721487933261[262] = 0;
   out_6614407721487933261[263] = 0;
   out_6614407721487933261[264] = 0;
   out_6614407721487933261[265] = 0;
   out_6614407721487933261[266] = 1;
   out_6614407721487933261[267] = 0;
   out_6614407721487933261[268] = 0;
   out_6614407721487933261[269] = 0;
   out_6614407721487933261[270] = 0;
   out_6614407721487933261[271] = 0;
   out_6614407721487933261[272] = 0;
   out_6614407721487933261[273] = 0;
   out_6614407721487933261[274] = 0;
   out_6614407721487933261[275] = 0;
   out_6614407721487933261[276] = 0;
   out_6614407721487933261[277] = 0;
   out_6614407721487933261[278] = 0;
   out_6614407721487933261[279] = 0;
   out_6614407721487933261[280] = 0;
   out_6614407721487933261[281] = 0;
   out_6614407721487933261[282] = 0;
   out_6614407721487933261[283] = 0;
   out_6614407721487933261[284] = 0;
   out_6614407721487933261[285] = 1;
   out_6614407721487933261[286] = 0;
   out_6614407721487933261[287] = 0;
   out_6614407721487933261[288] = 0;
   out_6614407721487933261[289] = 0;
   out_6614407721487933261[290] = 0;
   out_6614407721487933261[291] = 0;
   out_6614407721487933261[292] = 0;
   out_6614407721487933261[293] = 0;
   out_6614407721487933261[294] = 0;
   out_6614407721487933261[295] = 0;
   out_6614407721487933261[296] = 0;
   out_6614407721487933261[297] = 0;
   out_6614407721487933261[298] = 0;
   out_6614407721487933261[299] = 0;
   out_6614407721487933261[300] = 0;
   out_6614407721487933261[301] = 0;
   out_6614407721487933261[302] = 0;
   out_6614407721487933261[303] = 0;
   out_6614407721487933261[304] = 1;
   out_6614407721487933261[305] = 0;
   out_6614407721487933261[306] = 0;
   out_6614407721487933261[307] = 0;
   out_6614407721487933261[308] = 0;
   out_6614407721487933261[309] = 0;
   out_6614407721487933261[310] = 0;
   out_6614407721487933261[311] = 0;
   out_6614407721487933261[312] = 0;
   out_6614407721487933261[313] = 0;
   out_6614407721487933261[314] = 0;
   out_6614407721487933261[315] = 0;
   out_6614407721487933261[316] = 0;
   out_6614407721487933261[317] = 0;
   out_6614407721487933261[318] = 0;
   out_6614407721487933261[319] = 0;
   out_6614407721487933261[320] = 0;
   out_6614407721487933261[321] = 0;
   out_6614407721487933261[322] = 0;
   out_6614407721487933261[323] = 1;
}
void h_4(double *state, double *unused, double *out_5876735221666534963) {
   out_5876735221666534963[0] = state[6] + state[9];
   out_5876735221666534963[1] = state[7] + state[10];
   out_5876735221666534963[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_5817781391782316328) {
   out_5817781391782316328[0] = 0;
   out_5817781391782316328[1] = 0;
   out_5817781391782316328[2] = 0;
   out_5817781391782316328[3] = 0;
   out_5817781391782316328[4] = 0;
   out_5817781391782316328[5] = 0;
   out_5817781391782316328[6] = 1;
   out_5817781391782316328[7] = 0;
   out_5817781391782316328[8] = 0;
   out_5817781391782316328[9] = 1;
   out_5817781391782316328[10] = 0;
   out_5817781391782316328[11] = 0;
   out_5817781391782316328[12] = 0;
   out_5817781391782316328[13] = 0;
   out_5817781391782316328[14] = 0;
   out_5817781391782316328[15] = 0;
   out_5817781391782316328[16] = 0;
   out_5817781391782316328[17] = 0;
   out_5817781391782316328[18] = 0;
   out_5817781391782316328[19] = 0;
   out_5817781391782316328[20] = 0;
   out_5817781391782316328[21] = 0;
   out_5817781391782316328[22] = 0;
   out_5817781391782316328[23] = 0;
   out_5817781391782316328[24] = 0;
   out_5817781391782316328[25] = 1;
   out_5817781391782316328[26] = 0;
   out_5817781391782316328[27] = 0;
   out_5817781391782316328[28] = 1;
   out_5817781391782316328[29] = 0;
   out_5817781391782316328[30] = 0;
   out_5817781391782316328[31] = 0;
   out_5817781391782316328[32] = 0;
   out_5817781391782316328[33] = 0;
   out_5817781391782316328[34] = 0;
   out_5817781391782316328[35] = 0;
   out_5817781391782316328[36] = 0;
   out_5817781391782316328[37] = 0;
   out_5817781391782316328[38] = 0;
   out_5817781391782316328[39] = 0;
   out_5817781391782316328[40] = 0;
   out_5817781391782316328[41] = 0;
   out_5817781391782316328[42] = 0;
   out_5817781391782316328[43] = 0;
   out_5817781391782316328[44] = 1;
   out_5817781391782316328[45] = 0;
   out_5817781391782316328[46] = 0;
   out_5817781391782316328[47] = 1;
   out_5817781391782316328[48] = 0;
   out_5817781391782316328[49] = 0;
   out_5817781391782316328[50] = 0;
   out_5817781391782316328[51] = 0;
   out_5817781391782316328[52] = 0;
   out_5817781391782316328[53] = 0;
}
void h_10(double *state, double *unused, double *out_7879293322521614101) {
   out_7879293322521614101[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_7879293322521614101[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_7879293322521614101[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_6097031029555240174) {
   out_6097031029555240174[0] = 0;
   out_6097031029555240174[1] = 9.8100000000000005*cos(state[1]);
   out_6097031029555240174[2] = 0;
   out_6097031029555240174[3] = 0;
   out_6097031029555240174[4] = -state[8];
   out_6097031029555240174[5] = state[7];
   out_6097031029555240174[6] = 0;
   out_6097031029555240174[7] = state[5];
   out_6097031029555240174[8] = -state[4];
   out_6097031029555240174[9] = 0;
   out_6097031029555240174[10] = 0;
   out_6097031029555240174[11] = 0;
   out_6097031029555240174[12] = 1;
   out_6097031029555240174[13] = 0;
   out_6097031029555240174[14] = 0;
   out_6097031029555240174[15] = 1;
   out_6097031029555240174[16] = 0;
   out_6097031029555240174[17] = 0;
   out_6097031029555240174[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_6097031029555240174[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_6097031029555240174[20] = 0;
   out_6097031029555240174[21] = state[8];
   out_6097031029555240174[22] = 0;
   out_6097031029555240174[23] = -state[6];
   out_6097031029555240174[24] = -state[5];
   out_6097031029555240174[25] = 0;
   out_6097031029555240174[26] = state[3];
   out_6097031029555240174[27] = 0;
   out_6097031029555240174[28] = 0;
   out_6097031029555240174[29] = 0;
   out_6097031029555240174[30] = 0;
   out_6097031029555240174[31] = 1;
   out_6097031029555240174[32] = 0;
   out_6097031029555240174[33] = 0;
   out_6097031029555240174[34] = 1;
   out_6097031029555240174[35] = 0;
   out_6097031029555240174[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_6097031029555240174[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_6097031029555240174[38] = 0;
   out_6097031029555240174[39] = -state[7];
   out_6097031029555240174[40] = state[6];
   out_6097031029555240174[41] = 0;
   out_6097031029555240174[42] = state[4];
   out_6097031029555240174[43] = -state[3];
   out_6097031029555240174[44] = 0;
   out_6097031029555240174[45] = 0;
   out_6097031029555240174[46] = 0;
   out_6097031029555240174[47] = 0;
   out_6097031029555240174[48] = 0;
   out_6097031029555240174[49] = 0;
   out_6097031029555240174[50] = 1;
   out_6097031029555240174[51] = 0;
   out_6097031029555240174[52] = 0;
   out_6097031029555240174[53] = 1;
}
void h_13(double *state, double *unused, double *out_3226875223116851983) {
   out_3226875223116851983[0] = state[3];
   out_3226875223116851983[1] = state[4];
   out_3226875223116851983[2] = state[5];
}
void H_13(double *state, double *unused, double *out_2605507566449983527) {
   out_2605507566449983527[0] = 0;
   out_2605507566449983527[1] = 0;
   out_2605507566449983527[2] = 0;
   out_2605507566449983527[3] = 1;
   out_2605507566449983527[4] = 0;
   out_2605507566449983527[5] = 0;
   out_2605507566449983527[6] = 0;
   out_2605507566449983527[7] = 0;
   out_2605507566449983527[8] = 0;
   out_2605507566449983527[9] = 0;
   out_2605507566449983527[10] = 0;
   out_2605507566449983527[11] = 0;
   out_2605507566449983527[12] = 0;
   out_2605507566449983527[13] = 0;
   out_2605507566449983527[14] = 0;
   out_2605507566449983527[15] = 0;
   out_2605507566449983527[16] = 0;
   out_2605507566449983527[17] = 0;
   out_2605507566449983527[18] = 0;
   out_2605507566449983527[19] = 0;
   out_2605507566449983527[20] = 0;
   out_2605507566449983527[21] = 0;
   out_2605507566449983527[22] = 1;
   out_2605507566449983527[23] = 0;
   out_2605507566449983527[24] = 0;
   out_2605507566449983527[25] = 0;
   out_2605507566449983527[26] = 0;
   out_2605507566449983527[27] = 0;
   out_2605507566449983527[28] = 0;
   out_2605507566449983527[29] = 0;
   out_2605507566449983527[30] = 0;
   out_2605507566449983527[31] = 0;
   out_2605507566449983527[32] = 0;
   out_2605507566449983527[33] = 0;
   out_2605507566449983527[34] = 0;
   out_2605507566449983527[35] = 0;
   out_2605507566449983527[36] = 0;
   out_2605507566449983527[37] = 0;
   out_2605507566449983527[38] = 0;
   out_2605507566449983527[39] = 0;
   out_2605507566449983527[40] = 0;
   out_2605507566449983527[41] = 1;
   out_2605507566449983527[42] = 0;
   out_2605507566449983527[43] = 0;
   out_2605507566449983527[44] = 0;
   out_2605507566449983527[45] = 0;
   out_2605507566449983527[46] = 0;
   out_2605507566449983527[47] = 0;
   out_2605507566449983527[48] = 0;
   out_2605507566449983527[49] = 0;
   out_2605507566449983527[50] = 0;
   out_2605507566449983527[51] = 0;
   out_2605507566449983527[52] = 0;
   out_2605507566449983527[53] = 0;
}
void h_14(double *state, double *unused, double *out_4838960397532814427) {
   out_4838960397532814427[0] = state[6];
   out_4838960397532814427[1] = state[7];
   out_4838960397532814427[2] = state[8];
}
void H_14(double *state, double *unused, double *out_1854540535442831799) {
   out_1854540535442831799[0] = 0;
   out_1854540535442831799[1] = 0;
   out_1854540535442831799[2] = 0;
   out_1854540535442831799[3] = 0;
   out_1854540535442831799[4] = 0;
   out_1854540535442831799[5] = 0;
   out_1854540535442831799[6] = 1;
   out_1854540535442831799[7] = 0;
   out_1854540535442831799[8] = 0;
   out_1854540535442831799[9] = 0;
   out_1854540535442831799[10] = 0;
   out_1854540535442831799[11] = 0;
   out_1854540535442831799[12] = 0;
   out_1854540535442831799[13] = 0;
   out_1854540535442831799[14] = 0;
   out_1854540535442831799[15] = 0;
   out_1854540535442831799[16] = 0;
   out_1854540535442831799[17] = 0;
   out_1854540535442831799[18] = 0;
   out_1854540535442831799[19] = 0;
   out_1854540535442831799[20] = 0;
   out_1854540535442831799[21] = 0;
   out_1854540535442831799[22] = 0;
   out_1854540535442831799[23] = 0;
   out_1854540535442831799[24] = 0;
   out_1854540535442831799[25] = 1;
   out_1854540535442831799[26] = 0;
   out_1854540535442831799[27] = 0;
   out_1854540535442831799[28] = 0;
   out_1854540535442831799[29] = 0;
   out_1854540535442831799[30] = 0;
   out_1854540535442831799[31] = 0;
   out_1854540535442831799[32] = 0;
   out_1854540535442831799[33] = 0;
   out_1854540535442831799[34] = 0;
   out_1854540535442831799[35] = 0;
   out_1854540535442831799[36] = 0;
   out_1854540535442831799[37] = 0;
   out_1854540535442831799[38] = 0;
   out_1854540535442831799[39] = 0;
   out_1854540535442831799[40] = 0;
   out_1854540535442831799[41] = 0;
   out_1854540535442831799[42] = 0;
   out_1854540535442831799[43] = 0;
   out_1854540535442831799[44] = 1;
   out_1854540535442831799[45] = 0;
   out_1854540535442831799[46] = 0;
   out_1854540535442831799[47] = 0;
   out_1854540535442831799[48] = 0;
   out_1854540535442831799[49] = 0;
   out_1854540535442831799[50] = 0;
   out_1854540535442831799[51] = 0;
   out_1854540535442831799[52] = 0;
   out_1854540535442831799[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_2192517159883214491) {
  err_fun(nom_x, delta_x, out_2192517159883214491);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_7620744679476459470) {
  inv_err_fun(nom_x, true_x, out_7620744679476459470);
}
void pose_H_mod_fun(double *state, double *out_7476444296888154553) {
  H_mod_fun(state, out_7476444296888154553);
}
void pose_f_fun(double *state, double dt, double *out_5554352162049920971) {
  f_fun(state,  dt, out_5554352162049920971);
}
void pose_F_fun(double *state, double dt, double *out_6614407721487933261) {
  F_fun(state,  dt, out_6614407721487933261);
}
void pose_h_4(double *state, double *unused, double *out_5876735221666534963) {
  h_4(state, unused, out_5876735221666534963);
}
void pose_H_4(double *state, double *unused, double *out_5817781391782316328) {
  H_4(state, unused, out_5817781391782316328);
}
void pose_h_10(double *state, double *unused, double *out_7879293322521614101) {
  h_10(state, unused, out_7879293322521614101);
}
void pose_H_10(double *state, double *unused, double *out_6097031029555240174) {
  H_10(state, unused, out_6097031029555240174);
}
void pose_h_13(double *state, double *unused, double *out_3226875223116851983) {
  h_13(state, unused, out_3226875223116851983);
}
void pose_H_13(double *state, double *unused, double *out_2605507566449983527) {
  H_13(state, unused, out_2605507566449983527);
}
void pose_h_14(double *state, double *unused, double *out_4838960397532814427) {
  h_14(state, unused, out_4838960397532814427);
}
void pose_H_14(double *state, double *unused, double *out_1854540535442831799) {
  H_14(state, unused, out_1854540535442831799);
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
