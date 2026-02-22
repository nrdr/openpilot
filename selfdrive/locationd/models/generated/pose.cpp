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
void err_fun(double *nom_x, double *delta_x, double *out_3540814927069874749) {
   out_3540814927069874749[0] = delta_x[0] + nom_x[0];
   out_3540814927069874749[1] = delta_x[1] + nom_x[1];
   out_3540814927069874749[2] = delta_x[2] + nom_x[2];
   out_3540814927069874749[3] = delta_x[3] + nom_x[3];
   out_3540814927069874749[4] = delta_x[4] + nom_x[4];
   out_3540814927069874749[5] = delta_x[5] + nom_x[5];
   out_3540814927069874749[6] = delta_x[6] + nom_x[6];
   out_3540814927069874749[7] = delta_x[7] + nom_x[7];
   out_3540814927069874749[8] = delta_x[8] + nom_x[8];
   out_3540814927069874749[9] = delta_x[9] + nom_x[9];
   out_3540814927069874749[10] = delta_x[10] + nom_x[10];
   out_3540814927069874749[11] = delta_x[11] + nom_x[11];
   out_3540814927069874749[12] = delta_x[12] + nom_x[12];
   out_3540814927069874749[13] = delta_x[13] + nom_x[13];
   out_3540814927069874749[14] = delta_x[14] + nom_x[14];
   out_3540814927069874749[15] = delta_x[15] + nom_x[15];
   out_3540814927069874749[16] = delta_x[16] + nom_x[16];
   out_3540814927069874749[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6824921044159080785) {
   out_6824921044159080785[0] = -nom_x[0] + true_x[0];
   out_6824921044159080785[1] = -nom_x[1] + true_x[1];
   out_6824921044159080785[2] = -nom_x[2] + true_x[2];
   out_6824921044159080785[3] = -nom_x[3] + true_x[3];
   out_6824921044159080785[4] = -nom_x[4] + true_x[4];
   out_6824921044159080785[5] = -nom_x[5] + true_x[5];
   out_6824921044159080785[6] = -nom_x[6] + true_x[6];
   out_6824921044159080785[7] = -nom_x[7] + true_x[7];
   out_6824921044159080785[8] = -nom_x[8] + true_x[8];
   out_6824921044159080785[9] = -nom_x[9] + true_x[9];
   out_6824921044159080785[10] = -nom_x[10] + true_x[10];
   out_6824921044159080785[11] = -nom_x[11] + true_x[11];
   out_6824921044159080785[12] = -nom_x[12] + true_x[12];
   out_6824921044159080785[13] = -nom_x[13] + true_x[13];
   out_6824921044159080785[14] = -nom_x[14] + true_x[14];
   out_6824921044159080785[15] = -nom_x[15] + true_x[15];
   out_6824921044159080785[16] = -nom_x[16] + true_x[16];
   out_6824921044159080785[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_1646016674355801401) {
   out_1646016674355801401[0] = 1.0;
   out_1646016674355801401[1] = 0.0;
   out_1646016674355801401[2] = 0.0;
   out_1646016674355801401[3] = 0.0;
   out_1646016674355801401[4] = 0.0;
   out_1646016674355801401[5] = 0.0;
   out_1646016674355801401[6] = 0.0;
   out_1646016674355801401[7] = 0.0;
   out_1646016674355801401[8] = 0.0;
   out_1646016674355801401[9] = 0.0;
   out_1646016674355801401[10] = 0.0;
   out_1646016674355801401[11] = 0.0;
   out_1646016674355801401[12] = 0.0;
   out_1646016674355801401[13] = 0.0;
   out_1646016674355801401[14] = 0.0;
   out_1646016674355801401[15] = 0.0;
   out_1646016674355801401[16] = 0.0;
   out_1646016674355801401[17] = 0.0;
   out_1646016674355801401[18] = 0.0;
   out_1646016674355801401[19] = 1.0;
   out_1646016674355801401[20] = 0.0;
   out_1646016674355801401[21] = 0.0;
   out_1646016674355801401[22] = 0.0;
   out_1646016674355801401[23] = 0.0;
   out_1646016674355801401[24] = 0.0;
   out_1646016674355801401[25] = 0.0;
   out_1646016674355801401[26] = 0.0;
   out_1646016674355801401[27] = 0.0;
   out_1646016674355801401[28] = 0.0;
   out_1646016674355801401[29] = 0.0;
   out_1646016674355801401[30] = 0.0;
   out_1646016674355801401[31] = 0.0;
   out_1646016674355801401[32] = 0.0;
   out_1646016674355801401[33] = 0.0;
   out_1646016674355801401[34] = 0.0;
   out_1646016674355801401[35] = 0.0;
   out_1646016674355801401[36] = 0.0;
   out_1646016674355801401[37] = 0.0;
   out_1646016674355801401[38] = 1.0;
   out_1646016674355801401[39] = 0.0;
   out_1646016674355801401[40] = 0.0;
   out_1646016674355801401[41] = 0.0;
   out_1646016674355801401[42] = 0.0;
   out_1646016674355801401[43] = 0.0;
   out_1646016674355801401[44] = 0.0;
   out_1646016674355801401[45] = 0.0;
   out_1646016674355801401[46] = 0.0;
   out_1646016674355801401[47] = 0.0;
   out_1646016674355801401[48] = 0.0;
   out_1646016674355801401[49] = 0.0;
   out_1646016674355801401[50] = 0.0;
   out_1646016674355801401[51] = 0.0;
   out_1646016674355801401[52] = 0.0;
   out_1646016674355801401[53] = 0.0;
   out_1646016674355801401[54] = 0.0;
   out_1646016674355801401[55] = 0.0;
   out_1646016674355801401[56] = 0.0;
   out_1646016674355801401[57] = 1.0;
   out_1646016674355801401[58] = 0.0;
   out_1646016674355801401[59] = 0.0;
   out_1646016674355801401[60] = 0.0;
   out_1646016674355801401[61] = 0.0;
   out_1646016674355801401[62] = 0.0;
   out_1646016674355801401[63] = 0.0;
   out_1646016674355801401[64] = 0.0;
   out_1646016674355801401[65] = 0.0;
   out_1646016674355801401[66] = 0.0;
   out_1646016674355801401[67] = 0.0;
   out_1646016674355801401[68] = 0.0;
   out_1646016674355801401[69] = 0.0;
   out_1646016674355801401[70] = 0.0;
   out_1646016674355801401[71] = 0.0;
   out_1646016674355801401[72] = 0.0;
   out_1646016674355801401[73] = 0.0;
   out_1646016674355801401[74] = 0.0;
   out_1646016674355801401[75] = 0.0;
   out_1646016674355801401[76] = 1.0;
   out_1646016674355801401[77] = 0.0;
   out_1646016674355801401[78] = 0.0;
   out_1646016674355801401[79] = 0.0;
   out_1646016674355801401[80] = 0.0;
   out_1646016674355801401[81] = 0.0;
   out_1646016674355801401[82] = 0.0;
   out_1646016674355801401[83] = 0.0;
   out_1646016674355801401[84] = 0.0;
   out_1646016674355801401[85] = 0.0;
   out_1646016674355801401[86] = 0.0;
   out_1646016674355801401[87] = 0.0;
   out_1646016674355801401[88] = 0.0;
   out_1646016674355801401[89] = 0.0;
   out_1646016674355801401[90] = 0.0;
   out_1646016674355801401[91] = 0.0;
   out_1646016674355801401[92] = 0.0;
   out_1646016674355801401[93] = 0.0;
   out_1646016674355801401[94] = 0.0;
   out_1646016674355801401[95] = 1.0;
   out_1646016674355801401[96] = 0.0;
   out_1646016674355801401[97] = 0.0;
   out_1646016674355801401[98] = 0.0;
   out_1646016674355801401[99] = 0.0;
   out_1646016674355801401[100] = 0.0;
   out_1646016674355801401[101] = 0.0;
   out_1646016674355801401[102] = 0.0;
   out_1646016674355801401[103] = 0.0;
   out_1646016674355801401[104] = 0.0;
   out_1646016674355801401[105] = 0.0;
   out_1646016674355801401[106] = 0.0;
   out_1646016674355801401[107] = 0.0;
   out_1646016674355801401[108] = 0.0;
   out_1646016674355801401[109] = 0.0;
   out_1646016674355801401[110] = 0.0;
   out_1646016674355801401[111] = 0.0;
   out_1646016674355801401[112] = 0.0;
   out_1646016674355801401[113] = 0.0;
   out_1646016674355801401[114] = 1.0;
   out_1646016674355801401[115] = 0.0;
   out_1646016674355801401[116] = 0.0;
   out_1646016674355801401[117] = 0.0;
   out_1646016674355801401[118] = 0.0;
   out_1646016674355801401[119] = 0.0;
   out_1646016674355801401[120] = 0.0;
   out_1646016674355801401[121] = 0.0;
   out_1646016674355801401[122] = 0.0;
   out_1646016674355801401[123] = 0.0;
   out_1646016674355801401[124] = 0.0;
   out_1646016674355801401[125] = 0.0;
   out_1646016674355801401[126] = 0.0;
   out_1646016674355801401[127] = 0.0;
   out_1646016674355801401[128] = 0.0;
   out_1646016674355801401[129] = 0.0;
   out_1646016674355801401[130] = 0.0;
   out_1646016674355801401[131] = 0.0;
   out_1646016674355801401[132] = 0.0;
   out_1646016674355801401[133] = 1.0;
   out_1646016674355801401[134] = 0.0;
   out_1646016674355801401[135] = 0.0;
   out_1646016674355801401[136] = 0.0;
   out_1646016674355801401[137] = 0.0;
   out_1646016674355801401[138] = 0.0;
   out_1646016674355801401[139] = 0.0;
   out_1646016674355801401[140] = 0.0;
   out_1646016674355801401[141] = 0.0;
   out_1646016674355801401[142] = 0.0;
   out_1646016674355801401[143] = 0.0;
   out_1646016674355801401[144] = 0.0;
   out_1646016674355801401[145] = 0.0;
   out_1646016674355801401[146] = 0.0;
   out_1646016674355801401[147] = 0.0;
   out_1646016674355801401[148] = 0.0;
   out_1646016674355801401[149] = 0.0;
   out_1646016674355801401[150] = 0.0;
   out_1646016674355801401[151] = 0.0;
   out_1646016674355801401[152] = 1.0;
   out_1646016674355801401[153] = 0.0;
   out_1646016674355801401[154] = 0.0;
   out_1646016674355801401[155] = 0.0;
   out_1646016674355801401[156] = 0.0;
   out_1646016674355801401[157] = 0.0;
   out_1646016674355801401[158] = 0.0;
   out_1646016674355801401[159] = 0.0;
   out_1646016674355801401[160] = 0.0;
   out_1646016674355801401[161] = 0.0;
   out_1646016674355801401[162] = 0.0;
   out_1646016674355801401[163] = 0.0;
   out_1646016674355801401[164] = 0.0;
   out_1646016674355801401[165] = 0.0;
   out_1646016674355801401[166] = 0.0;
   out_1646016674355801401[167] = 0.0;
   out_1646016674355801401[168] = 0.0;
   out_1646016674355801401[169] = 0.0;
   out_1646016674355801401[170] = 0.0;
   out_1646016674355801401[171] = 1.0;
   out_1646016674355801401[172] = 0.0;
   out_1646016674355801401[173] = 0.0;
   out_1646016674355801401[174] = 0.0;
   out_1646016674355801401[175] = 0.0;
   out_1646016674355801401[176] = 0.0;
   out_1646016674355801401[177] = 0.0;
   out_1646016674355801401[178] = 0.0;
   out_1646016674355801401[179] = 0.0;
   out_1646016674355801401[180] = 0.0;
   out_1646016674355801401[181] = 0.0;
   out_1646016674355801401[182] = 0.0;
   out_1646016674355801401[183] = 0.0;
   out_1646016674355801401[184] = 0.0;
   out_1646016674355801401[185] = 0.0;
   out_1646016674355801401[186] = 0.0;
   out_1646016674355801401[187] = 0.0;
   out_1646016674355801401[188] = 0.0;
   out_1646016674355801401[189] = 0.0;
   out_1646016674355801401[190] = 1.0;
   out_1646016674355801401[191] = 0.0;
   out_1646016674355801401[192] = 0.0;
   out_1646016674355801401[193] = 0.0;
   out_1646016674355801401[194] = 0.0;
   out_1646016674355801401[195] = 0.0;
   out_1646016674355801401[196] = 0.0;
   out_1646016674355801401[197] = 0.0;
   out_1646016674355801401[198] = 0.0;
   out_1646016674355801401[199] = 0.0;
   out_1646016674355801401[200] = 0.0;
   out_1646016674355801401[201] = 0.0;
   out_1646016674355801401[202] = 0.0;
   out_1646016674355801401[203] = 0.0;
   out_1646016674355801401[204] = 0.0;
   out_1646016674355801401[205] = 0.0;
   out_1646016674355801401[206] = 0.0;
   out_1646016674355801401[207] = 0.0;
   out_1646016674355801401[208] = 0.0;
   out_1646016674355801401[209] = 1.0;
   out_1646016674355801401[210] = 0.0;
   out_1646016674355801401[211] = 0.0;
   out_1646016674355801401[212] = 0.0;
   out_1646016674355801401[213] = 0.0;
   out_1646016674355801401[214] = 0.0;
   out_1646016674355801401[215] = 0.0;
   out_1646016674355801401[216] = 0.0;
   out_1646016674355801401[217] = 0.0;
   out_1646016674355801401[218] = 0.0;
   out_1646016674355801401[219] = 0.0;
   out_1646016674355801401[220] = 0.0;
   out_1646016674355801401[221] = 0.0;
   out_1646016674355801401[222] = 0.0;
   out_1646016674355801401[223] = 0.0;
   out_1646016674355801401[224] = 0.0;
   out_1646016674355801401[225] = 0.0;
   out_1646016674355801401[226] = 0.0;
   out_1646016674355801401[227] = 0.0;
   out_1646016674355801401[228] = 1.0;
   out_1646016674355801401[229] = 0.0;
   out_1646016674355801401[230] = 0.0;
   out_1646016674355801401[231] = 0.0;
   out_1646016674355801401[232] = 0.0;
   out_1646016674355801401[233] = 0.0;
   out_1646016674355801401[234] = 0.0;
   out_1646016674355801401[235] = 0.0;
   out_1646016674355801401[236] = 0.0;
   out_1646016674355801401[237] = 0.0;
   out_1646016674355801401[238] = 0.0;
   out_1646016674355801401[239] = 0.0;
   out_1646016674355801401[240] = 0.0;
   out_1646016674355801401[241] = 0.0;
   out_1646016674355801401[242] = 0.0;
   out_1646016674355801401[243] = 0.0;
   out_1646016674355801401[244] = 0.0;
   out_1646016674355801401[245] = 0.0;
   out_1646016674355801401[246] = 0.0;
   out_1646016674355801401[247] = 1.0;
   out_1646016674355801401[248] = 0.0;
   out_1646016674355801401[249] = 0.0;
   out_1646016674355801401[250] = 0.0;
   out_1646016674355801401[251] = 0.0;
   out_1646016674355801401[252] = 0.0;
   out_1646016674355801401[253] = 0.0;
   out_1646016674355801401[254] = 0.0;
   out_1646016674355801401[255] = 0.0;
   out_1646016674355801401[256] = 0.0;
   out_1646016674355801401[257] = 0.0;
   out_1646016674355801401[258] = 0.0;
   out_1646016674355801401[259] = 0.0;
   out_1646016674355801401[260] = 0.0;
   out_1646016674355801401[261] = 0.0;
   out_1646016674355801401[262] = 0.0;
   out_1646016674355801401[263] = 0.0;
   out_1646016674355801401[264] = 0.0;
   out_1646016674355801401[265] = 0.0;
   out_1646016674355801401[266] = 1.0;
   out_1646016674355801401[267] = 0.0;
   out_1646016674355801401[268] = 0.0;
   out_1646016674355801401[269] = 0.0;
   out_1646016674355801401[270] = 0.0;
   out_1646016674355801401[271] = 0.0;
   out_1646016674355801401[272] = 0.0;
   out_1646016674355801401[273] = 0.0;
   out_1646016674355801401[274] = 0.0;
   out_1646016674355801401[275] = 0.0;
   out_1646016674355801401[276] = 0.0;
   out_1646016674355801401[277] = 0.0;
   out_1646016674355801401[278] = 0.0;
   out_1646016674355801401[279] = 0.0;
   out_1646016674355801401[280] = 0.0;
   out_1646016674355801401[281] = 0.0;
   out_1646016674355801401[282] = 0.0;
   out_1646016674355801401[283] = 0.0;
   out_1646016674355801401[284] = 0.0;
   out_1646016674355801401[285] = 1.0;
   out_1646016674355801401[286] = 0.0;
   out_1646016674355801401[287] = 0.0;
   out_1646016674355801401[288] = 0.0;
   out_1646016674355801401[289] = 0.0;
   out_1646016674355801401[290] = 0.0;
   out_1646016674355801401[291] = 0.0;
   out_1646016674355801401[292] = 0.0;
   out_1646016674355801401[293] = 0.0;
   out_1646016674355801401[294] = 0.0;
   out_1646016674355801401[295] = 0.0;
   out_1646016674355801401[296] = 0.0;
   out_1646016674355801401[297] = 0.0;
   out_1646016674355801401[298] = 0.0;
   out_1646016674355801401[299] = 0.0;
   out_1646016674355801401[300] = 0.0;
   out_1646016674355801401[301] = 0.0;
   out_1646016674355801401[302] = 0.0;
   out_1646016674355801401[303] = 0.0;
   out_1646016674355801401[304] = 1.0;
   out_1646016674355801401[305] = 0.0;
   out_1646016674355801401[306] = 0.0;
   out_1646016674355801401[307] = 0.0;
   out_1646016674355801401[308] = 0.0;
   out_1646016674355801401[309] = 0.0;
   out_1646016674355801401[310] = 0.0;
   out_1646016674355801401[311] = 0.0;
   out_1646016674355801401[312] = 0.0;
   out_1646016674355801401[313] = 0.0;
   out_1646016674355801401[314] = 0.0;
   out_1646016674355801401[315] = 0.0;
   out_1646016674355801401[316] = 0.0;
   out_1646016674355801401[317] = 0.0;
   out_1646016674355801401[318] = 0.0;
   out_1646016674355801401[319] = 0.0;
   out_1646016674355801401[320] = 0.0;
   out_1646016674355801401[321] = 0.0;
   out_1646016674355801401[322] = 0.0;
   out_1646016674355801401[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_1812064668052849173) {
   out_1812064668052849173[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_1812064668052849173[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_1812064668052849173[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_1812064668052849173[3] = dt*state[12] + state[3];
   out_1812064668052849173[4] = dt*state[13] + state[4];
   out_1812064668052849173[5] = dt*state[14] + state[5];
   out_1812064668052849173[6] = state[6];
   out_1812064668052849173[7] = state[7];
   out_1812064668052849173[8] = state[8];
   out_1812064668052849173[9] = state[9];
   out_1812064668052849173[10] = state[10];
   out_1812064668052849173[11] = state[11];
   out_1812064668052849173[12] = state[12];
   out_1812064668052849173[13] = state[13];
   out_1812064668052849173[14] = state[14];
   out_1812064668052849173[15] = state[15];
   out_1812064668052849173[16] = state[16];
   out_1812064668052849173[17] = state[17];
}
void F_fun(double *state, double dt, double *out_8063307411811769324) {
   out_8063307411811769324[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8063307411811769324[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8063307411811769324[2] = 0;
   out_8063307411811769324[3] = 0;
   out_8063307411811769324[4] = 0;
   out_8063307411811769324[5] = 0;
   out_8063307411811769324[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8063307411811769324[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8063307411811769324[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8063307411811769324[9] = 0;
   out_8063307411811769324[10] = 0;
   out_8063307411811769324[11] = 0;
   out_8063307411811769324[12] = 0;
   out_8063307411811769324[13] = 0;
   out_8063307411811769324[14] = 0;
   out_8063307411811769324[15] = 0;
   out_8063307411811769324[16] = 0;
   out_8063307411811769324[17] = 0;
   out_8063307411811769324[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8063307411811769324[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8063307411811769324[20] = 0;
   out_8063307411811769324[21] = 0;
   out_8063307411811769324[22] = 0;
   out_8063307411811769324[23] = 0;
   out_8063307411811769324[24] = 0;
   out_8063307411811769324[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8063307411811769324[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8063307411811769324[27] = 0;
   out_8063307411811769324[28] = 0;
   out_8063307411811769324[29] = 0;
   out_8063307411811769324[30] = 0;
   out_8063307411811769324[31] = 0;
   out_8063307411811769324[32] = 0;
   out_8063307411811769324[33] = 0;
   out_8063307411811769324[34] = 0;
   out_8063307411811769324[35] = 0;
   out_8063307411811769324[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8063307411811769324[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8063307411811769324[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8063307411811769324[39] = 0;
   out_8063307411811769324[40] = 0;
   out_8063307411811769324[41] = 0;
   out_8063307411811769324[42] = 0;
   out_8063307411811769324[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8063307411811769324[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8063307411811769324[45] = 0;
   out_8063307411811769324[46] = 0;
   out_8063307411811769324[47] = 0;
   out_8063307411811769324[48] = 0;
   out_8063307411811769324[49] = 0;
   out_8063307411811769324[50] = 0;
   out_8063307411811769324[51] = 0;
   out_8063307411811769324[52] = 0;
   out_8063307411811769324[53] = 0;
   out_8063307411811769324[54] = 0;
   out_8063307411811769324[55] = 0;
   out_8063307411811769324[56] = 0;
   out_8063307411811769324[57] = 1;
   out_8063307411811769324[58] = 0;
   out_8063307411811769324[59] = 0;
   out_8063307411811769324[60] = 0;
   out_8063307411811769324[61] = 0;
   out_8063307411811769324[62] = 0;
   out_8063307411811769324[63] = 0;
   out_8063307411811769324[64] = 0;
   out_8063307411811769324[65] = 0;
   out_8063307411811769324[66] = dt;
   out_8063307411811769324[67] = 0;
   out_8063307411811769324[68] = 0;
   out_8063307411811769324[69] = 0;
   out_8063307411811769324[70] = 0;
   out_8063307411811769324[71] = 0;
   out_8063307411811769324[72] = 0;
   out_8063307411811769324[73] = 0;
   out_8063307411811769324[74] = 0;
   out_8063307411811769324[75] = 0;
   out_8063307411811769324[76] = 1;
   out_8063307411811769324[77] = 0;
   out_8063307411811769324[78] = 0;
   out_8063307411811769324[79] = 0;
   out_8063307411811769324[80] = 0;
   out_8063307411811769324[81] = 0;
   out_8063307411811769324[82] = 0;
   out_8063307411811769324[83] = 0;
   out_8063307411811769324[84] = 0;
   out_8063307411811769324[85] = dt;
   out_8063307411811769324[86] = 0;
   out_8063307411811769324[87] = 0;
   out_8063307411811769324[88] = 0;
   out_8063307411811769324[89] = 0;
   out_8063307411811769324[90] = 0;
   out_8063307411811769324[91] = 0;
   out_8063307411811769324[92] = 0;
   out_8063307411811769324[93] = 0;
   out_8063307411811769324[94] = 0;
   out_8063307411811769324[95] = 1;
   out_8063307411811769324[96] = 0;
   out_8063307411811769324[97] = 0;
   out_8063307411811769324[98] = 0;
   out_8063307411811769324[99] = 0;
   out_8063307411811769324[100] = 0;
   out_8063307411811769324[101] = 0;
   out_8063307411811769324[102] = 0;
   out_8063307411811769324[103] = 0;
   out_8063307411811769324[104] = dt;
   out_8063307411811769324[105] = 0;
   out_8063307411811769324[106] = 0;
   out_8063307411811769324[107] = 0;
   out_8063307411811769324[108] = 0;
   out_8063307411811769324[109] = 0;
   out_8063307411811769324[110] = 0;
   out_8063307411811769324[111] = 0;
   out_8063307411811769324[112] = 0;
   out_8063307411811769324[113] = 0;
   out_8063307411811769324[114] = 1;
   out_8063307411811769324[115] = 0;
   out_8063307411811769324[116] = 0;
   out_8063307411811769324[117] = 0;
   out_8063307411811769324[118] = 0;
   out_8063307411811769324[119] = 0;
   out_8063307411811769324[120] = 0;
   out_8063307411811769324[121] = 0;
   out_8063307411811769324[122] = 0;
   out_8063307411811769324[123] = 0;
   out_8063307411811769324[124] = 0;
   out_8063307411811769324[125] = 0;
   out_8063307411811769324[126] = 0;
   out_8063307411811769324[127] = 0;
   out_8063307411811769324[128] = 0;
   out_8063307411811769324[129] = 0;
   out_8063307411811769324[130] = 0;
   out_8063307411811769324[131] = 0;
   out_8063307411811769324[132] = 0;
   out_8063307411811769324[133] = 1;
   out_8063307411811769324[134] = 0;
   out_8063307411811769324[135] = 0;
   out_8063307411811769324[136] = 0;
   out_8063307411811769324[137] = 0;
   out_8063307411811769324[138] = 0;
   out_8063307411811769324[139] = 0;
   out_8063307411811769324[140] = 0;
   out_8063307411811769324[141] = 0;
   out_8063307411811769324[142] = 0;
   out_8063307411811769324[143] = 0;
   out_8063307411811769324[144] = 0;
   out_8063307411811769324[145] = 0;
   out_8063307411811769324[146] = 0;
   out_8063307411811769324[147] = 0;
   out_8063307411811769324[148] = 0;
   out_8063307411811769324[149] = 0;
   out_8063307411811769324[150] = 0;
   out_8063307411811769324[151] = 0;
   out_8063307411811769324[152] = 1;
   out_8063307411811769324[153] = 0;
   out_8063307411811769324[154] = 0;
   out_8063307411811769324[155] = 0;
   out_8063307411811769324[156] = 0;
   out_8063307411811769324[157] = 0;
   out_8063307411811769324[158] = 0;
   out_8063307411811769324[159] = 0;
   out_8063307411811769324[160] = 0;
   out_8063307411811769324[161] = 0;
   out_8063307411811769324[162] = 0;
   out_8063307411811769324[163] = 0;
   out_8063307411811769324[164] = 0;
   out_8063307411811769324[165] = 0;
   out_8063307411811769324[166] = 0;
   out_8063307411811769324[167] = 0;
   out_8063307411811769324[168] = 0;
   out_8063307411811769324[169] = 0;
   out_8063307411811769324[170] = 0;
   out_8063307411811769324[171] = 1;
   out_8063307411811769324[172] = 0;
   out_8063307411811769324[173] = 0;
   out_8063307411811769324[174] = 0;
   out_8063307411811769324[175] = 0;
   out_8063307411811769324[176] = 0;
   out_8063307411811769324[177] = 0;
   out_8063307411811769324[178] = 0;
   out_8063307411811769324[179] = 0;
   out_8063307411811769324[180] = 0;
   out_8063307411811769324[181] = 0;
   out_8063307411811769324[182] = 0;
   out_8063307411811769324[183] = 0;
   out_8063307411811769324[184] = 0;
   out_8063307411811769324[185] = 0;
   out_8063307411811769324[186] = 0;
   out_8063307411811769324[187] = 0;
   out_8063307411811769324[188] = 0;
   out_8063307411811769324[189] = 0;
   out_8063307411811769324[190] = 1;
   out_8063307411811769324[191] = 0;
   out_8063307411811769324[192] = 0;
   out_8063307411811769324[193] = 0;
   out_8063307411811769324[194] = 0;
   out_8063307411811769324[195] = 0;
   out_8063307411811769324[196] = 0;
   out_8063307411811769324[197] = 0;
   out_8063307411811769324[198] = 0;
   out_8063307411811769324[199] = 0;
   out_8063307411811769324[200] = 0;
   out_8063307411811769324[201] = 0;
   out_8063307411811769324[202] = 0;
   out_8063307411811769324[203] = 0;
   out_8063307411811769324[204] = 0;
   out_8063307411811769324[205] = 0;
   out_8063307411811769324[206] = 0;
   out_8063307411811769324[207] = 0;
   out_8063307411811769324[208] = 0;
   out_8063307411811769324[209] = 1;
   out_8063307411811769324[210] = 0;
   out_8063307411811769324[211] = 0;
   out_8063307411811769324[212] = 0;
   out_8063307411811769324[213] = 0;
   out_8063307411811769324[214] = 0;
   out_8063307411811769324[215] = 0;
   out_8063307411811769324[216] = 0;
   out_8063307411811769324[217] = 0;
   out_8063307411811769324[218] = 0;
   out_8063307411811769324[219] = 0;
   out_8063307411811769324[220] = 0;
   out_8063307411811769324[221] = 0;
   out_8063307411811769324[222] = 0;
   out_8063307411811769324[223] = 0;
   out_8063307411811769324[224] = 0;
   out_8063307411811769324[225] = 0;
   out_8063307411811769324[226] = 0;
   out_8063307411811769324[227] = 0;
   out_8063307411811769324[228] = 1;
   out_8063307411811769324[229] = 0;
   out_8063307411811769324[230] = 0;
   out_8063307411811769324[231] = 0;
   out_8063307411811769324[232] = 0;
   out_8063307411811769324[233] = 0;
   out_8063307411811769324[234] = 0;
   out_8063307411811769324[235] = 0;
   out_8063307411811769324[236] = 0;
   out_8063307411811769324[237] = 0;
   out_8063307411811769324[238] = 0;
   out_8063307411811769324[239] = 0;
   out_8063307411811769324[240] = 0;
   out_8063307411811769324[241] = 0;
   out_8063307411811769324[242] = 0;
   out_8063307411811769324[243] = 0;
   out_8063307411811769324[244] = 0;
   out_8063307411811769324[245] = 0;
   out_8063307411811769324[246] = 0;
   out_8063307411811769324[247] = 1;
   out_8063307411811769324[248] = 0;
   out_8063307411811769324[249] = 0;
   out_8063307411811769324[250] = 0;
   out_8063307411811769324[251] = 0;
   out_8063307411811769324[252] = 0;
   out_8063307411811769324[253] = 0;
   out_8063307411811769324[254] = 0;
   out_8063307411811769324[255] = 0;
   out_8063307411811769324[256] = 0;
   out_8063307411811769324[257] = 0;
   out_8063307411811769324[258] = 0;
   out_8063307411811769324[259] = 0;
   out_8063307411811769324[260] = 0;
   out_8063307411811769324[261] = 0;
   out_8063307411811769324[262] = 0;
   out_8063307411811769324[263] = 0;
   out_8063307411811769324[264] = 0;
   out_8063307411811769324[265] = 0;
   out_8063307411811769324[266] = 1;
   out_8063307411811769324[267] = 0;
   out_8063307411811769324[268] = 0;
   out_8063307411811769324[269] = 0;
   out_8063307411811769324[270] = 0;
   out_8063307411811769324[271] = 0;
   out_8063307411811769324[272] = 0;
   out_8063307411811769324[273] = 0;
   out_8063307411811769324[274] = 0;
   out_8063307411811769324[275] = 0;
   out_8063307411811769324[276] = 0;
   out_8063307411811769324[277] = 0;
   out_8063307411811769324[278] = 0;
   out_8063307411811769324[279] = 0;
   out_8063307411811769324[280] = 0;
   out_8063307411811769324[281] = 0;
   out_8063307411811769324[282] = 0;
   out_8063307411811769324[283] = 0;
   out_8063307411811769324[284] = 0;
   out_8063307411811769324[285] = 1;
   out_8063307411811769324[286] = 0;
   out_8063307411811769324[287] = 0;
   out_8063307411811769324[288] = 0;
   out_8063307411811769324[289] = 0;
   out_8063307411811769324[290] = 0;
   out_8063307411811769324[291] = 0;
   out_8063307411811769324[292] = 0;
   out_8063307411811769324[293] = 0;
   out_8063307411811769324[294] = 0;
   out_8063307411811769324[295] = 0;
   out_8063307411811769324[296] = 0;
   out_8063307411811769324[297] = 0;
   out_8063307411811769324[298] = 0;
   out_8063307411811769324[299] = 0;
   out_8063307411811769324[300] = 0;
   out_8063307411811769324[301] = 0;
   out_8063307411811769324[302] = 0;
   out_8063307411811769324[303] = 0;
   out_8063307411811769324[304] = 1;
   out_8063307411811769324[305] = 0;
   out_8063307411811769324[306] = 0;
   out_8063307411811769324[307] = 0;
   out_8063307411811769324[308] = 0;
   out_8063307411811769324[309] = 0;
   out_8063307411811769324[310] = 0;
   out_8063307411811769324[311] = 0;
   out_8063307411811769324[312] = 0;
   out_8063307411811769324[313] = 0;
   out_8063307411811769324[314] = 0;
   out_8063307411811769324[315] = 0;
   out_8063307411811769324[316] = 0;
   out_8063307411811769324[317] = 0;
   out_8063307411811769324[318] = 0;
   out_8063307411811769324[319] = 0;
   out_8063307411811769324[320] = 0;
   out_8063307411811769324[321] = 0;
   out_8063307411811769324[322] = 0;
   out_8063307411811769324[323] = 1;
}
void h_4(double *state, double *unused, double *out_2303598358625783284) {
   out_2303598358625783284[0] = state[6] + state[9];
   out_2303598358625783284[1] = state[7] + state[10];
   out_2303598358625783284[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_4202065132396157320) {
   out_4202065132396157320[0] = 0;
   out_4202065132396157320[1] = 0;
   out_4202065132396157320[2] = 0;
   out_4202065132396157320[3] = 0;
   out_4202065132396157320[4] = 0;
   out_4202065132396157320[5] = 0;
   out_4202065132396157320[6] = 1;
   out_4202065132396157320[7] = 0;
   out_4202065132396157320[8] = 0;
   out_4202065132396157320[9] = 1;
   out_4202065132396157320[10] = 0;
   out_4202065132396157320[11] = 0;
   out_4202065132396157320[12] = 0;
   out_4202065132396157320[13] = 0;
   out_4202065132396157320[14] = 0;
   out_4202065132396157320[15] = 0;
   out_4202065132396157320[16] = 0;
   out_4202065132396157320[17] = 0;
   out_4202065132396157320[18] = 0;
   out_4202065132396157320[19] = 0;
   out_4202065132396157320[20] = 0;
   out_4202065132396157320[21] = 0;
   out_4202065132396157320[22] = 0;
   out_4202065132396157320[23] = 0;
   out_4202065132396157320[24] = 0;
   out_4202065132396157320[25] = 1;
   out_4202065132396157320[26] = 0;
   out_4202065132396157320[27] = 0;
   out_4202065132396157320[28] = 1;
   out_4202065132396157320[29] = 0;
   out_4202065132396157320[30] = 0;
   out_4202065132396157320[31] = 0;
   out_4202065132396157320[32] = 0;
   out_4202065132396157320[33] = 0;
   out_4202065132396157320[34] = 0;
   out_4202065132396157320[35] = 0;
   out_4202065132396157320[36] = 0;
   out_4202065132396157320[37] = 0;
   out_4202065132396157320[38] = 0;
   out_4202065132396157320[39] = 0;
   out_4202065132396157320[40] = 0;
   out_4202065132396157320[41] = 0;
   out_4202065132396157320[42] = 0;
   out_4202065132396157320[43] = 0;
   out_4202065132396157320[44] = 1;
   out_4202065132396157320[45] = 0;
   out_4202065132396157320[46] = 0;
   out_4202065132396157320[47] = 1;
   out_4202065132396157320[48] = 0;
   out_4202065132396157320[49] = 0;
   out_4202065132396157320[50] = 0;
   out_4202065132396157320[51] = 0;
   out_4202065132396157320[52] = 0;
   out_4202065132396157320[53] = 0;
}
void h_10(double *state, double *unused, double *out_8093621696167248788) {
   out_8093621696167248788[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_8093621696167248788[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_8093621696167248788[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_17303435982620736) {
   out_17303435982620736[0] = 0;
   out_17303435982620736[1] = 9.8100000000000005*cos(state[1]);
   out_17303435982620736[2] = 0;
   out_17303435982620736[3] = 0;
   out_17303435982620736[4] = -state[8];
   out_17303435982620736[5] = state[7];
   out_17303435982620736[6] = 0;
   out_17303435982620736[7] = state[5];
   out_17303435982620736[8] = -state[4];
   out_17303435982620736[9] = 0;
   out_17303435982620736[10] = 0;
   out_17303435982620736[11] = 0;
   out_17303435982620736[12] = 1;
   out_17303435982620736[13] = 0;
   out_17303435982620736[14] = 0;
   out_17303435982620736[15] = 1;
   out_17303435982620736[16] = 0;
   out_17303435982620736[17] = 0;
   out_17303435982620736[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_17303435982620736[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_17303435982620736[20] = 0;
   out_17303435982620736[21] = state[8];
   out_17303435982620736[22] = 0;
   out_17303435982620736[23] = -state[6];
   out_17303435982620736[24] = -state[5];
   out_17303435982620736[25] = 0;
   out_17303435982620736[26] = state[3];
   out_17303435982620736[27] = 0;
   out_17303435982620736[28] = 0;
   out_17303435982620736[29] = 0;
   out_17303435982620736[30] = 0;
   out_17303435982620736[31] = 1;
   out_17303435982620736[32] = 0;
   out_17303435982620736[33] = 0;
   out_17303435982620736[34] = 1;
   out_17303435982620736[35] = 0;
   out_17303435982620736[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_17303435982620736[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_17303435982620736[38] = 0;
   out_17303435982620736[39] = -state[7];
   out_17303435982620736[40] = state[6];
   out_17303435982620736[41] = 0;
   out_17303435982620736[42] = state[4];
   out_17303435982620736[43] = -state[3];
   out_17303435982620736[44] = 0;
   out_17303435982620736[45] = 0;
   out_17303435982620736[46] = 0;
   out_17303435982620736[47] = 0;
   out_17303435982620736[48] = 0;
   out_17303435982620736[49] = 0;
   out_17303435982620736[50] = 1;
   out_17303435982620736[51] = 0;
   out_17303435982620736[52] = 0;
   out_17303435982620736[53] = 1;
}
void h_13(double *state, double *unused, double *out_5450973548134688447) {
   out_5450973548134688447[0] = state[3];
   out_5450973548134688447[1] = state[4];
   out_5450973548134688447[2] = state[5];
}
void H_13(double *state, double *unused, double *out_989791307063824519) {
   out_989791307063824519[0] = 0;
   out_989791307063824519[1] = 0;
   out_989791307063824519[2] = 0;
   out_989791307063824519[3] = 1;
   out_989791307063824519[4] = 0;
   out_989791307063824519[5] = 0;
   out_989791307063824519[6] = 0;
   out_989791307063824519[7] = 0;
   out_989791307063824519[8] = 0;
   out_989791307063824519[9] = 0;
   out_989791307063824519[10] = 0;
   out_989791307063824519[11] = 0;
   out_989791307063824519[12] = 0;
   out_989791307063824519[13] = 0;
   out_989791307063824519[14] = 0;
   out_989791307063824519[15] = 0;
   out_989791307063824519[16] = 0;
   out_989791307063824519[17] = 0;
   out_989791307063824519[18] = 0;
   out_989791307063824519[19] = 0;
   out_989791307063824519[20] = 0;
   out_989791307063824519[21] = 0;
   out_989791307063824519[22] = 1;
   out_989791307063824519[23] = 0;
   out_989791307063824519[24] = 0;
   out_989791307063824519[25] = 0;
   out_989791307063824519[26] = 0;
   out_989791307063824519[27] = 0;
   out_989791307063824519[28] = 0;
   out_989791307063824519[29] = 0;
   out_989791307063824519[30] = 0;
   out_989791307063824519[31] = 0;
   out_989791307063824519[32] = 0;
   out_989791307063824519[33] = 0;
   out_989791307063824519[34] = 0;
   out_989791307063824519[35] = 0;
   out_989791307063824519[36] = 0;
   out_989791307063824519[37] = 0;
   out_989791307063824519[38] = 0;
   out_989791307063824519[39] = 0;
   out_989791307063824519[40] = 0;
   out_989791307063824519[41] = 1;
   out_989791307063824519[42] = 0;
   out_989791307063824519[43] = 0;
   out_989791307063824519[44] = 0;
   out_989791307063824519[45] = 0;
   out_989791307063824519[46] = 0;
   out_989791307063824519[47] = 0;
   out_989791307063824519[48] = 0;
   out_989791307063824519[49] = 0;
   out_989791307063824519[50] = 0;
   out_989791307063824519[51] = 0;
   out_989791307063824519[52] = 0;
   out_989791307063824519[53] = 0;
}
void h_14(double *state, double *unused, double *out_6736526479382297115) {
   out_6736526479382297115[0] = state[6];
   out_6736526479382297115[1] = state[7];
   out_6736526479382297115[2] = state[8];
}
void H_14(double *state, double *unused, double *out_238824276056672791) {
   out_238824276056672791[0] = 0;
   out_238824276056672791[1] = 0;
   out_238824276056672791[2] = 0;
   out_238824276056672791[3] = 0;
   out_238824276056672791[4] = 0;
   out_238824276056672791[5] = 0;
   out_238824276056672791[6] = 1;
   out_238824276056672791[7] = 0;
   out_238824276056672791[8] = 0;
   out_238824276056672791[9] = 0;
   out_238824276056672791[10] = 0;
   out_238824276056672791[11] = 0;
   out_238824276056672791[12] = 0;
   out_238824276056672791[13] = 0;
   out_238824276056672791[14] = 0;
   out_238824276056672791[15] = 0;
   out_238824276056672791[16] = 0;
   out_238824276056672791[17] = 0;
   out_238824276056672791[18] = 0;
   out_238824276056672791[19] = 0;
   out_238824276056672791[20] = 0;
   out_238824276056672791[21] = 0;
   out_238824276056672791[22] = 0;
   out_238824276056672791[23] = 0;
   out_238824276056672791[24] = 0;
   out_238824276056672791[25] = 1;
   out_238824276056672791[26] = 0;
   out_238824276056672791[27] = 0;
   out_238824276056672791[28] = 0;
   out_238824276056672791[29] = 0;
   out_238824276056672791[30] = 0;
   out_238824276056672791[31] = 0;
   out_238824276056672791[32] = 0;
   out_238824276056672791[33] = 0;
   out_238824276056672791[34] = 0;
   out_238824276056672791[35] = 0;
   out_238824276056672791[36] = 0;
   out_238824276056672791[37] = 0;
   out_238824276056672791[38] = 0;
   out_238824276056672791[39] = 0;
   out_238824276056672791[40] = 0;
   out_238824276056672791[41] = 0;
   out_238824276056672791[42] = 0;
   out_238824276056672791[43] = 0;
   out_238824276056672791[44] = 1;
   out_238824276056672791[45] = 0;
   out_238824276056672791[46] = 0;
   out_238824276056672791[47] = 0;
   out_238824276056672791[48] = 0;
   out_238824276056672791[49] = 0;
   out_238824276056672791[50] = 0;
   out_238824276056672791[51] = 0;
   out_238824276056672791[52] = 0;
   out_238824276056672791[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_3540814927069874749) {
  err_fun(nom_x, delta_x, out_3540814927069874749);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_6824921044159080785) {
  inv_err_fun(nom_x, true_x, out_6824921044159080785);
}
void pose_H_mod_fun(double *state, double *out_1646016674355801401) {
  H_mod_fun(state, out_1646016674355801401);
}
void pose_f_fun(double *state, double dt, double *out_1812064668052849173) {
  f_fun(state,  dt, out_1812064668052849173);
}
void pose_F_fun(double *state, double dt, double *out_8063307411811769324) {
  F_fun(state,  dt, out_8063307411811769324);
}
void pose_h_4(double *state, double *unused, double *out_2303598358625783284) {
  h_4(state, unused, out_2303598358625783284);
}
void pose_H_4(double *state, double *unused, double *out_4202065132396157320) {
  H_4(state, unused, out_4202065132396157320);
}
void pose_h_10(double *state, double *unused, double *out_8093621696167248788) {
  h_10(state, unused, out_8093621696167248788);
}
void pose_H_10(double *state, double *unused, double *out_17303435982620736) {
  H_10(state, unused, out_17303435982620736);
}
void pose_h_13(double *state, double *unused, double *out_5450973548134688447) {
  h_13(state, unused, out_5450973548134688447);
}
void pose_H_13(double *state, double *unused, double *out_989791307063824519) {
  H_13(state, unused, out_989791307063824519);
}
void pose_h_14(double *state, double *unused, double *out_6736526479382297115) {
  h_14(state, unused, out_6736526479382297115);
}
void pose_H_14(double *state, double *unused, double *out_238824276056672791) {
  H_14(state, unused, out_238824276056672791);
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
