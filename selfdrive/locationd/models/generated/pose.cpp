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
void err_fun(double *nom_x, double *delta_x, double *out_4874754272255029803) {
   out_4874754272255029803[0] = delta_x[0] + nom_x[0];
   out_4874754272255029803[1] = delta_x[1] + nom_x[1];
   out_4874754272255029803[2] = delta_x[2] + nom_x[2];
   out_4874754272255029803[3] = delta_x[3] + nom_x[3];
   out_4874754272255029803[4] = delta_x[4] + nom_x[4];
   out_4874754272255029803[5] = delta_x[5] + nom_x[5];
   out_4874754272255029803[6] = delta_x[6] + nom_x[6];
   out_4874754272255029803[7] = delta_x[7] + nom_x[7];
   out_4874754272255029803[8] = delta_x[8] + nom_x[8];
   out_4874754272255029803[9] = delta_x[9] + nom_x[9];
   out_4874754272255029803[10] = delta_x[10] + nom_x[10];
   out_4874754272255029803[11] = delta_x[11] + nom_x[11];
   out_4874754272255029803[12] = delta_x[12] + nom_x[12];
   out_4874754272255029803[13] = delta_x[13] + nom_x[13];
   out_4874754272255029803[14] = delta_x[14] + nom_x[14];
   out_4874754272255029803[15] = delta_x[15] + nom_x[15];
   out_4874754272255029803[16] = delta_x[16] + nom_x[16];
   out_4874754272255029803[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_3314318466659131181) {
   out_3314318466659131181[0] = -nom_x[0] + true_x[0];
   out_3314318466659131181[1] = -nom_x[1] + true_x[1];
   out_3314318466659131181[2] = -nom_x[2] + true_x[2];
   out_3314318466659131181[3] = -nom_x[3] + true_x[3];
   out_3314318466659131181[4] = -nom_x[4] + true_x[4];
   out_3314318466659131181[5] = -nom_x[5] + true_x[5];
   out_3314318466659131181[6] = -nom_x[6] + true_x[6];
   out_3314318466659131181[7] = -nom_x[7] + true_x[7];
   out_3314318466659131181[8] = -nom_x[8] + true_x[8];
   out_3314318466659131181[9] = -nom_x[9] + true_x[9];
   out_3314318466659131181[10] = -nom_x[10] + true_x[10];
   out_3314318466659131181[11] = -nom_x[11] + true_x[11];
   out_3314318466659131181[12] = -nom_x[12] + true_x[12];
   out_3314318466659131181[13] = -nom_x[13] + true_x[13];
   out_3314318466659131181[14] = -nom_x[14] + true_x[14];
   out_3314318466659131181[15] = -nom_x[15] + true_x[15];
   out_3314318466659131181[16] = -nom_x[16] + true_x[16];
   out_3314318466659131181[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_8802356504304725397) {
   out_8802356504304725397[0] = 1.0;
   out_8802356504304725397[1] = 0.0;
   out_8802356504304725397[2] = 0.0;
   out_8802356504304725397[3] = 0.0;
   out_8802356504304725397[4] = 0.0;
   out_8802356504304725397[5] = 0.0;
   out_8802356504304725397[6] = 0.0;
   out_8802356504304725397[7] = 0.0;
   out_8802356504304725397[8] = 0.0;
   out_8802356504304725397[9] = 0.0;
   out_8802356504304725397[10] = 0.0;
   out_8802356504304725397[11] = 0.0;
   out_8802356504304725397[12] = 0.0;
   out_8802356504304725397[13] = 0.0;
   out_8802356504304725397[14] = 0.0;
   out_8802356504304725397[15] = 0.0;
   out_8802356504304725397[16] = 0.0;
   out_8802356504304725397[17] = 0.0;
   out_8802356504304725397[18] = 0.0;
   out_8802356504304725397[19] = 1.0;
   out_8802356504304725397[20] = 0.0;
   out_8802356504304725397[21] = 0.0;
   out_8802356504304725397[22] = 0.0;
   out_8802356504304725397[23] = 0.0;
   out_8802356504304725397[24] = 0.0;
   out_8802356504304725397[25] = 0.0;
   out_8802356504304725397[26] = 0.0;
   out_8802356504304725397[27] = 0.0;
   out_8802356504304725397[28] = 0.0;
   out_8802356504304725397[29] = 0.0;
   out_8802356504304725397[30] = 0.0;
   out_8802356504304725397[31] = 0.0;
   out_8802356504304725397[32] = 0.0;
   out_8802356504304725397[33] = 0.0;
   out_8802356504304725397[34] = 0.0;
   out_8802356504304725397[35] = 0.0;
   out_8802356504304725397[36] = 0.0;
   out_8802356504304725397[37] = 0.0;
   out_8802356504304725397[38] = 1.0;
   out_8802356504304725397[39] = 0.0;
   out_8802356504304725397[40] = 0.0;
   out_8802356504304725397[41] = 0.0;
   out_8802356504304725397[42] = 0.0;
   out_8802356504304725397[43] = 0.0;
   out_8802356504304725397[44] = 0.0;
   out_8802356504304725397[45] = 0.0;
   out_8802356504304725397[46] = 0.0;
   out_8802356504304725397[47] = 0.0;
   out_8802356504304725397[48] = 0.0;
   out_8802356504304725397[49] = 0.0;
   out_8802356504304725397[50] = 0.0;
   out_8802356504304725397[51] = 0.0;
   out_8802356504304725397[52] = 0.0;
   out_8802356504304725397[53] = 0.0;
   out_8802356504304725397[54] = 0.0;
   out_8802356504304725397[55] = 0.0;
   out_8802356504304725397[56] = 0.0;
   out_8802356504304725397[57] = 1.0;
   out_8802356504304725397[58] = 0.0;
   out_8802356504304725397[59] = 0.0;
   out_8802356504304725397[60] = 0.0;
   out_8802356504304725397[61] = 0.0;
   out_8802356504304725397[62] = 0.0;
   out_8802356504304725397[63] = 0.0;
   out_8802356504304725397[64] = 0.0;
   out_8802356504304725397[65] = 0.0;
   out_8802356504304725397[66] = 0.0;
   out_8802356504304725397[67] = 0.0;
   out_8802356504304725397[68] = 0.0;
   out_8802356504304725397[69] = 0.0;
   out_8802356504304725397[70] = 0.0;
   out_8802356504304725397[71] = 0.0;
   out_8802356504304725397[72] = 0.0;
   out_8802356504304725397[73] = 0.0;
   out_8802356504304725397[74] = 0.0;
   out_8802356504304725397[75] = 0.0;
   out_8802356504304725397[76] = 1.0;
   out_8802356504304725397[77] = 0.0;
   out_8802356504304725397[78] = 0.0;
   out_8802356504304725397[79] = 0.0;
   out_8802356504304725397[80] = 0.0;
   out_8802356504304725397[81] = 0.0;
   out_8802356504304725397[82] = 0.0;
   out_8802356504304725397[83] = 0.0;
   out_8802356504304725397[84] = 0.0;
   out_8802356504304725397[85] = 0.0;
   out_8802356504304725397[86] = 0.0;
   out_8802356504304725397[87] = 0.0;
   out_8802356504304725397[88] = 0.0;
   out_8802356504304725397[89] = 0.0;
   out_8802356504304725397[90] = 0.0;
   out_8802356504304725397[91] = 0.0;
   out_8802356504304725397[92] = 0.0;
   out_8802356504304725397[93] = 0.0;
   out_8802356504304725397[94] = 0.0;
   out_8802356504304725397[95] = 1.0;
   out_8802356504304725397[96] = 0.0;
   out_8802356504304725397[97] = 0.0;
   out_8802356504304725397[98] = 0.0;
   out_8802356504304725397[99] = 0.0;
   out_8802356504304725397[100] = 0.0;
   out_8802356504304725397[101] = 0.0;
   out_8802356504304725397[102] = 0.0;
   out_8802356504304725397[103] = 0.0;
   out_8802356504304725397[104] = 0.0;
   out_8802356504304725397[105] = 0.0;
   out_8802356504304725397[106] = 0.0;
   out_8802356504304725397[107] = 0.0;
   out_8802356504304725397[108] = 0.0;
   out_8802356504304725397[109] = 0.0;
   out_8802356504304725397[110] = 0.0;
   out_8802356504304725397[111] = 0.0;
   out_8802356504304725397[112] = 0.0;
   out_8802356504304725397[113] = 0.0;
   out_8802356504304725397[114] = 1.0;
   out_8802356504304725397[115] = 0.0;
   out_8802356504304725397[116] = 0.0;
   out_8802356504304725397[117] = 0.0;
   out_8802356504304725397[118] = 0.0;
   out_8802356504304725397[119] = 0.0;
   out_8802356504304725397[120] = 0.0;
   out_8802356504304725397[121] = 0.0;
   out_8802356504304725397[122] = 0.0;
   out_8802356504304725397[123] = 0.0;
   out_8802356504304725397[124] = 0.0;
   out_8802356504304725397[125] = 0.0;
   out_8802356504304725397[126] = 0.0;
   out_8802356504304725397[127] = 0.0;
   out_8802356504304725397[128] = 0.0;
   out_8802356504304725397[129] = 0.0;
   out_8802356504304725397[130] = 0.0;
   out_8802356504304725397[131] = 0.0;
   out_8802356504304725397[132] = 0.0;
   out_8802356504304725397[133] = 1.0;
   out_8802356504304725397[134] = 0.0;
   out_8802356504304725397[135] = 0.0;
   out_8802356504304725397[136] = 0.0;
   out_8802356504304725397[137] = 0.0;
   out_8802356504304725397[138] = 0.0;
   out_8802356504304725397[139] = 0.0;
   out_8802356504304725397[140] = 0.0;
   out_8802356504304725397[141] = 0.0;
   out_8802356504304725397[142] = 0.0;
   out_8802356504304725397[143] = 0.0;
   out_8802356504304725397[144] = 0.0;
   out_8802356504304725397[145] = 0.0;
   out_8802356504304725397[146] = 0.0;
   out_8802356504304725397[147] = 0.0;
   out_8802356504304725397[148] = 0.0;
   out_8802356504304725397[149] = 0.0;
   out_8802356504304725397[150] = 0.0;
   out_8802356504304725397[151] = 0.0;
   out_8802356504304725397[152] = 1.0;
   out_8802356504304725397[153] = 0.0;
   out_8802356504304725397[154] = 0.0;
   out_8802356504304725397[155] = 0.0;
   out_8802356504304725397[156] = 0.0;
   out_8802356504304725397[157] = 0.0;
   out_8802356504304725397[158] = 0.0;
   out_8802356504304725397[159] = 0.0;
   out_8802356504304725397[160] = 0.0;
   out_8802356504304725397[161] = 0.0;
   out_8802356504304725397[162] = 0.0;
   out_8802356504304725397[163] = 0.0;
   out_8802356504304725397[164] = 0.0;
   out_8802356504304725397[165] = 0.0;
   out_8802356504304725397[166] = 0.0;
   out_8802356504304725397[167] = 0.0;
   out_8802356504304725397[168] = 0.0;
   out_8802356504304725397[169] = 0.0;
   out_8802356504304725397[170] = 0.0;
   out_8802356504304725397[171] = 1.0;
   out_8802356504304725397[172] = 0.0;
   out_8802356504304725397[173] = 0.0;
   out_8802356504304725397[174] = 0.0;
   out_8802356504304725397[175] = 0.0;
   out_8802356504304725397[176] = 0.0;
   out_8802356504304725397[177] = 0.0;
   out_8802356504304725397[178] = 0.0;
   out_8802356504304725397[179] = 0.0;
   out_8802356504304725397[180] = 0.0;
   out_8802356504304725397[181] = 0.0;
   out_8802356504304725397[182] = 0.0;
   out_8802356504304725397[183] = 0.0;
   out_8802356504304725397[184] = 0.0;
   out_8802356504304725397[185] = 0.0;
   out_8802356504304725397[186] = 0.0;
   out_8802356504304725397[187] = 0.0;
   out_8802356504304725397[188] = 0.0;
   out_8802356504304725397[189] = 0.0;
   out_8802356504304725397[190] = 1.0;
   out_8802356504304725397[191] = 0.0;
   out_8802356504304725397[192] = 0.0;
   out_8802356504304725397[193] = 0.0;
   out_8802356504304725397[194] = 0.0;
   out_8802356504304725397[195] = 0.0;
   out_8802356504304725397[196] = 0.0;
   out_8802356504304725397[197] = 0.0;
   out_8802356504304725397[198] = 0.0;
   out_8802356504304725397[199] = 0.0;
   out_8802356504304725397[200] = 0.0;
   out_8802356504304725397[201] = 0.0;
   out_8802356504304725397[202] = 0.0;
   out_8802356504304725397[203] = 0.0;
   out_8802356504304725397[204] = 0.0;
   out_8802356504304725397[205] = 0.0;
   out_8802356504304725397[206] = 0.0;
   out_8802356504304725397[207] = 0.0;
   out_8802356504304725397[208] = 0.0;
   out_8802356504304725397[209] = 1.0;
   out_8802356504304725397[210] = 0.0;
   out_8802356504304725397[211] = 0.0;
   out_8802356504304725397[212] = 0.0;
   out_8802356504304725397[213] = 0.0;
   out_8802356504304725397[214] = 0.0;
   out_8802356504304725397[215] = 0.0;
   out_8802356504304725397[216] = 0.0;
   out_8802356504304725397[217] = 0.0;
   out_8802356504304725397[218] = 0.0;
   out_8802356504304725397[219] = 0.0;
   out_8802356504304725397[220] = 0.0;
   out_8802356504304725397[221] = 0.0;
   out_8802356504304725397[222] = 0.0;
   out_8802356504304725397[223] = 0.0;
   out_8802356504304725397[224] = 0.0;
   out_8802356504304725397[225] = 0.0;
   out_8802356504304725397[226] = 0.0;
   out_8802356504304725397[227] = 0.0;
   out_8802356504304725397[228] = 1.0;
   out_8802356504304725397[229] = 0.0;
   out_8802356504304725397[230] = 0.0;
   out_8802356504304725397[231] = 0.0;
   out_8802356504304725397[232] = 0.0;
   out_8802356504304725397[233] = 0.0;
   out_8802356504304725397[234] = 0.0;
   out_8802356504304725397[235] = 0.0;
   out_8802356504304725397[236] = 0.0;
   out_8802356504304725397[237] = 0.0;
   out_8802356504304725397[238] = 0.0;
   out_8802356504304725397[239] = 0.0;
   out_8802356504304725397[240] = 0.0;
   out_8802356504304725397[241] = 0.0;
   out_8802356504304725397[242] = 0.0;
   out_8802356504304725397[243] = 0.0;
   out_8802356504304725397[244] = 0.0;
   out_8802356504304725397[245] = 0.0;
   out_8802356504304725397[246] = 0.0;
   out_8802356504304725397[247] = 1.0;
   out_8802356504304725397[248] = 0.0;
   out_8802356504304725397[249] = 0.0;
   out_8802356504304725397[250] = 0.0;
   out_8802356504304725397[251] = 0.0;
   out_8802356504304725397[252] = 0.0;
   out_8802356504304725397[253] = 0.0;
   out_8802356504304725397[254] = 0.0;
   out_8802356504304725397[255] = 0.0;
   out_8802356504304725397[256] = 0.0;
   out_8802356504304725397[257] = 0.0;
   out_8802356504304725397[258] = 0.0;
   out_8802356504304725397[259] = 0.0;
   out_8802356504304725397[260] = 0.0;
   out_8802356504304725397[261] = 0.0;
   out_8802356504304725397[262] = 0.0;
   out_8802356504304725397[263] = 0.0;
   out_8802356504304725397[264] = 0.0;
   out_8802356504304725397[265] = 0.0;
   out_8802356504304725397[266] = 1.0;
   out_8802356504304725397[267] = 0.0;
   out_8802356504304725397[268] = 0.0;
   out_8802356504304725397[269] = 0.0;
   out_8802356504304725397[270] = 0.0;
   out_8802356504304725397[271] = 0.0;
   out_8802356504304725397[272] = 0.0;
   out_8802356504304725397[273] = 0.0;
   out_8802356504304725397[274] = 0.0;
   out_8802356504304725397[275] = 0.0;
   out_8802356504304725397[276] = 0.0;
   out_8802356504304725397[277] = 0.0;
   out_8802356504304725397[278] = 0.0;
   out_8802356504304725397[279] = 0.0;
   out_8802356504304725397[280] = 0.0;
   out_8802356504304725397[281] = 0.0;
   out_8802356504304725397[282] = 0.0;
   out_8802356504304725397[283] = 0.0;
   out_8802356504304725397[284] = 0.0;
   out_8802356504304725397[285] = 1.0;
   out_8802356504304725397[286] = 0.0;
   out_8802356504304725397[287] = 0.0;
   out_8802356504304725397[288] = 0.0;
   out_8802356504304725397[289] = 0.0;
   out_8802356504304725397[290] = 0.0;
   out_8802356504304725397[291] = 0.0;
   out_8802356504304725397[292] = 0.0;
   out_8802356504304725397[293] = 0.0;
   out_8802356504304725397[294] = 0.0;
   out_8802356504304725397[295] = 0.0;
   out_8802356504304725397[296] = 0.0;
   out_8802356504304725397[297] = 0.0;
   out_8802356504304725397[298] = 0.0;
   out_8802356504304725397[299] = 0.0;
   out_8802356504304725397[300] = 0.0;
   out_8802356504304725397[301] = 0.0;
   out_8802356504304725397[302] = 0.0;
   out_8802356504304725397[303] = 0.0;
   out_8802356504304725397[304] = 1.0;
   out_8802356504304725397[305] = 0.0;
   out_8802356504304725397[306] = 0.0;
   out_8802356504304725397[307] = 0.0;
   out_8802356504304725397[308] = 0.0;
   out_8802356504304725397[309] = 0.0;
   out_8802356504304725397[310] = 0.0;
   out_8802356504304725397[311] = 0.0;
   out_8802356504304725397[312] = 0.0;
   out_8802356504304725397[313] = 0.0;
   out_8802356504304725397[314] = 0.0;
   out_8802356504304725397[315] = 0.0;
   out_8802356504304725397[316] = 0.0;
   out_8802356504304725397[317] = 0.0;
   out_8802356504304725397[318] = 0.0;
   out_8802356504304725397[319] = 0.0;
   out_8802356504304725397[320] = 0.0;
   out_8802356504304725397[321] = 0.0;
   out_8802356504304725397[322] = 0.0;
   out_8802356504304725397[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_495287790681774033) {
   out_495287790681774033[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_495287790681774033[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_495287790681774033[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_495287790681774033[3] = dt*state[12] + state[3];
   out_495287790681774033[4] = dt*state[13] + state[4];
   out_495287790681774033[5] = dt*state[14] + state[5];
   out_495287790681774033[6] = state[6];
   out_495287790681774033[7] = state[7];
   out_495287790681774033[8] = state[8];
   out_495287790681774033[9] = state[9];
   out_495287790681774033[10] = state[10];
   out_495287790681774033[11] = state[11];
   out_495287790681774033[12] = state[12];
   out_495287790681774033[13] = state[13];
   out_495287790681774033[14] = state[14];
   out_495287790681774033[15] = state[15];
   out_495287790681774033[16] = state[16];
   out_495287790681774033[17] = state[17];
}
void F_fun(double *state, double dt, double *out_8548468874185098314) {
   out_8548468874185098314[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8548468874185098314[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8548468874185098314[2] = 0;
   out_8548468874185098314[3] = 0;
   out_8548468874185098314[4] = 0;
   out_8548468874185098314[5] = 0;
   out_8548468874185098314[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8548468874185098314[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8548468874185098314[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8548468874185098314[9] = 0;
   out_8548468874185098314[10] = 0;
   out_8548468874185098314[11] = 0;
   out_8548468874185098314[12] = 0;
   out_8548468874185098314[13] = 0;
   out_8548468874185098314[14] = 0;
   out_8548468874185098314[15] = 0;
   out_8548468874185098314[16] = 0;
   out_8548468874185098314[17] = 0;
   out_8548468874185098314[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8548468874185098314[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8548468874185098314[20] = 0;
   out_8548468874185098314[21] = 0;
   out_8548468874185098314[22] = 0;
   out_8548468874185098314[23] = 0;
   out_8548468874185098314[24] = 0;
   out_8548468874185098314[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8548468874185098314[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8548468874185098314[27] = 0;
   out_8548468874185098314[28] = 0;
   out_8548468874185098314[29] = 0;
   out_8548468874185098314[30] = 0;
   out_8548468874185098314[31] = 0;
   out_8548468874185098314[32] = 0;
   out_8548468874185098314[33] = 0;
   out_8548468874185098314[34] = 0;
   out_8548468874185098314[35] = 0;
   out_8548468874185098314[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8548468874185098314[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8548468874185098314[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8548468874185098314[39] = 0;
   out_8548468874185098314[40] = 0;
   out_8548468874185098314[41] = 0;
   out_8548468874185098314[42] = 0;
   out_8548468874185098314[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8548468874185098314[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8548468874185098314[45] = 0;
   out_8548468874185098314[46] = 0;
   out_8548468874185098314[47] = 0;
   out_8548468874185098314[48] = 0;
   out_8548468874185098314[49] = 0;
   out_8548468874185098314[50] = 0;
   out_8548468874185098314[51] = 0;
   out_8548468874185098314[52] = 0;
   out_8548468874185098314[53] = 0;
   out_8548468874185098314[54] = 0;
   out_8548468874185098314[55] = 0;
   out_8548468874185098314[56] = 0;
   out_8548468874185098314[57] = 1;
   out_8548468874185098314[58] = 0;
   out_8548468874185098314[59] = 0;
   out_8548468874185098314[60] = 0;
   out_8548468874185098314[61] = 0;
   out_8548468874185098314[62] = 0;
   out_8548468874185098314[63] = 0;
   out_8548468874185098314[64] = 0;
   out_8548468874185098314[65] = 0;
   out_8548468874185098314[66] = dt;
   out_8548468874185098314[67] = 0;
   out_8548468874185098314[68] = 0;
   out_8548468874185098314[69] = 0;
   out_8548468874185098314[70] = 0;
   out_8548468874185098314[71] = 0;
   out_8548468874185098314[72] = 0;
   out_8548468874185098314[73] = 0;
   out_8548468874185098314[74] = 0;
   out_8548468874185098314[75] = 0;
   out_8548468874185098314[76] = 1;
   out_8548468874185098314[77] = 0;
   out_8548468874185098314[78] = 0;
   out_8548468874185098314[79] = 0;
   out_8548468874185098314[80] = 0;
   out_8548468874185098314[81] = 0;
   out_8548468874185098314[82] = 0;
   out_8548468874185098314[83] = 0;
   out_8548468874185098314[84] = 0;
   out_8548468874185098314[85] = dt;
   out_8548468874185098314[86] = 0;
   out_8548468874185098314[87] = 0;
   out_8548468874185098314[88] = 0;
   out_8548468874185098314[89] = 0;
   out_8548468874185098314[90] = 0;
   out_8548468874185098314[91] = 0;
   out_8548468874185098314[92] = 0;
   out_8548468874185098314[93] = 0;
   out_8548468874185098314[94] = 0;
   out_8548468874185098314[95] = 1;
   out_8548468874185098314[96] = 0;
   out_8548468874185098314[97] = 0;
   out_8548468874185098314[98] = 0;
   out_8548468874185098314[99] = 0;
   out_8548468874185098314[100] = 0;
   out_8548468874185098314[101] = 0;
   out_8548468874185098314[102] = 0;
   out_8548468874185098314[103] = 0;
   out_8548468874185098314[104] = dt;
   out_8548468874185098314[105] = 0;
   out_8548468874185098314[106] = 0;
   out_8548468874185098314[107] = 0;
   out_8548468874185098314[108] = 0;
   out_8548468874185098314[109] = 0;
   out_8548468874185098314[110] = 0;
   out_8548468874185098314[111] = 0;
   out_8548468874185098314[112] = 0;
   out_8548468874185098314[113] = 0;
   out_8548468874185098314[114] = 1;
   out_8548468874185098314[115] = 0;
   out_8548468874185098314[116] = 0;
   out_8548468874185098314[117] = 0;
   out_8548468874185098314[118] = 0;
   out_8548468874185098314[119] = 0;
   out_8548468874185098314[120] = 0;
   out_8548468874185098314[121] = 0;
   out_8548468874185098314[122] = 0;
   out_8548468874185098314[123] = 0;
   out_8548468874185098314[124] = 0;
   out_8548468874185098314[125] = 0;
   out_8548468874185098314[126] = 0;
   out_8548468874185098314[127] = 0;
   out_8548468874185098314[128] = 0;
   out_8548468874185098314[129] = 0;
   out_8548468874185098314[130] = 0;
   out_8548468874185098314[131] = 0;
   out_8548468874185098314[132] = 0;
   out_8548468874185098314[133] = 1;
   out_8548468874185098314[134] = 0;
   out_8548468874185098314[135] = 0;
   out_8548468874185098314[136] = 0;
   out_8548468874185098314[137] = 0;
   out_8548468874185098314[138] = 0;
   out_8548468874185098314[139] = 0;
   out_8548468874185098314[140] = 0;
   out_8548468874185098314[141] = 0;
   out_8548468874185098314[142] = 0;
   out_8548468874185098314[143] = 0;
   out_8548468874185098314[144] = 0;
   out_8548468874185098314[145] = 0;
   out_8548468874185098314[146] = 0;
   out_8548468874185098314[147] = 0;
   out_8548468874185098314[148] = 0;
   out_8548468874185098314[149] = 0;
   out_8548468874185098314[150] = 0;
   out_8548468874185098314[151] = 0;
   out_8548468874185098314[152] = 1;
   out_8548468874185098314[153] = 0;
   out_8548468874185098314[154] = 0;
   out_8548468874185098314[155] = 0;
   out_8548468874185098314[156] = 0;
   out_8548468874185098314[157] = 0;
   out_8548468874185098314[158] = 0;
   out_8548468874185098314[159] = 0;
   out_8548468874185098314[160] = 0;
   out_8548468874185098314[161] = 0;
   out_8548468874185098314[162] = 0;
   out_8548468874185098314[163] = 0;
   out_8548468874185098314[164] = 0;
   out_8548468874185098314[165] = 0;
   out_8548468874185098314[166] = 0;
   out_8548468874185098314[167] = 0;
   out_8548468874185098314[168] = 0;
   out_8548468874185098314[169] = 0;
   out_8548468874185098314[170] = 0;
   out_8548468874185098314[171] = 1;
   out_8548468874185098314[172] = 0;
   out_8548468874185098314[173] = 0;
   out_8548468874185098314[174] = 0;
   out_8548468874185098314[175] = 0;
   out_8548468874185098314[176] = 0;
   out_8548468874185098314[177] = 0;
   out_8548468874185098314[178] = 0;
   out_8548468874185098314[179] = 0;
   out_8548468874185098314[180] = 0;
   out_8548468874185098314[181] = 0;
   out_8548468874185098314[182] = 0;
   out_8548468874185098314[183] = 0;
   out_8548468874185098314[184] = 0;
   out_8548468874185098314[185] = 0;
   out_8548468874185098314[186] = 0;
   out_8548468874185098314[187] = 0;
   out_8548468874185098314[188] = 0;
   out_8548468874185098314[189] = 0;
   out_8548468874185098314[190] = 1;
   out_8548468874185098314[191] = 0;
   out_8548468874185098314[192] = 0;
   out_8548468874185098314[193] = 0;
   out_8548468874185098314[194] = 0;
   out_8548468874185098314[195] = 0;
   out_8548468874185098314[196] = 0;
   out_8548468874185098314[197] = 0;
   out_8548468874185098314[198] = 0;
   out_8548468874185098314[199] = 0;
   out_8548468874185098314[200] = 0;
   out_8548468874185098314[201] = 0;
   out_8548468874185098314[202] = 0;
   out_8548468874185098314[203] = 0;
   out_8548468874185098314[204] = 0;
   out_8548468874185098314[205] = 0;
   out_8548468874185098314[206] = 0;
   out_8548468874185098314[207] = 0;
   out_8548468874185098314[208] = 0;
   out_8548468874185098314[209] = 1;
   out_8548468874185098314[210] = 0;
   out_8548468874185098314[211] = 0;
   out_8548468874185098314[212] = 0;
   out_8548468874185098314[213] = 0;
   out_8548468874185098314[214] = 0;
   out_8548468874185098314[215] = 0;
   out_8548468874185098314[216] = 0;
   out_8548468874185098314[217] = 0;
   out_8548468874185098314[218] = 0;
   out_8548468874185098314[219] = 0;
   out_8548468874185098314[220] = 0;
   out_8548468874185098314[221] = 0;
   out_8548468874185098314[222] = 0;
   out_8548468874185098314[223] = 0;
   out_8548468874185098314[224] = 0;
   out_8548468874185098314[225] = 0;
   out_8548468874185098314[226] = 0;
   out_8548468874185098314[227] = 0;
   out_8548468874185098314[228] = 1;
   out_8548468874185098314[229] = 0;
   out_8548468874185098314[230] = 0;
   out_8548468874185098314[231] = 0;
   out_8548468874185098314[232] = 0;
   out_8548468874185098314[233] = 0;
   out_8548468874185098314[234] = 0;
   out_8548468874185098314[235] = 0;
   out_8548468874185098314[236] = 0;
   out_8548468874185098314[237] = 0;
   out_8548468874185098314[238] = 0;
   out_8548468874185098314[239] = 0;
   out_8548468874185098314[240] = 0;
   out_8548468874185098314[241] = 0;
   out_8548468874185098314[242] = 0;
   out_8548468874185098314[243] = 0;
   out_8548468874185098314[244] = 0;
   out_8548468874185098314[245] = 0;
   out_8548468874185098314[246] = 0;
   out_8548468874185098314[247] = 1;
   out_8548468874185098314[248] = 0;
   out_8548468874185098314[249] = 0;
   out_8548468874185098314[250] = 0;
   out_8548468874185098314[251] = 0;
   out_8548468874185098314[252] = 0;
   out_8548468874185098314[253] = 0;
   out_8548468874185098314[254] = 0;
   out_8548468874185098314[255] = 0;
   out_8548468874185098314[256] = 0;
   out_8548468874185098314[257] = 0;
   out_8548468874185098314[258] = 0;
   out_8548468874185098314[259] = 0;
   out_8548468874185098314[260] = 0;
   out_8548468874185098314[261] = 0;
   out_8548468874185098314[262] = 0;
   out_8548468874185098314[263] = 0;
   out_8548468874185098314[264] = 0;
   out_8548468874185098314[265] = 0;
   out_8548468874185098314[266] = 1;
   out_8548468874185098314[267] = 0;
   out_8548468874185098314[268] = 0;
   out_8548468874185098314[269] = 0;
   out_8548468874185098314[270] = 0;
   out_8548468874185098314[271] = 0;
   out_8548468874185098314[272] = 0;
   out_8548468874185098314[273] = 0;
   out_8548468874185098314[274] = 0;
   out_8548468874185098314[275] = 0;
   out_8548468874185098314[276] = 0;
   out_8548468874185098314[277] = 0;
   out_8548468874185098314[278] = 0;
   out_8548468874185098314[279] = 0;
   out_8548468874185098314[280] = 0;
   out_8548468874185098314[281] = 0;
   out_8548468874185098314[282] = 0;
   out_8548468874185098314[283] = 0;
   out_8548468874185098314[284] = 0;
   out_8548468874185098314[285] = 1;
   out_8548468874185098314[286] = 0;
   out_8548468874185098314[287] = 0;
   out_8548468874185098314[288] = 0;
   out_8548468874185098314[289] = 0;
   out_8548468874185098314[290] = 0;
   out_8548468874185098314[291] = 0;
   out_8548468874185098314[292] = 0;
   out_8548468874185098314[293] = 0;
   out_8548468874185098314[294] = 0;
   out_8548468874185098314[295] = 0;
   out_8548468874185098314[296] = 0;
   out_8548468874185098314[297] = 0;
   out_8548468874185098314[298] = 0;
   out_8548468874185098314[299] = 0;
   out_8548468874185098314[300] = 0;
   out_8548468874185098314[301] = 0;
   out_8548468874185098314[302] = 0;
   out_8548468874185098314[303] = 0;
   out_8548468874185098314[304] = 1;
   out_8548468874185098314[305] = 0;
   out_8548468874185098314[306] = 0;
   out_8548468874185098314[307] = 0;
   out_8548468874185098314[308] = 0;
   out_8548468874185098314[309] = 0;
   out_8548468874185098314[310] = 0;
   out_8548468874185098314[311] = 0;
   out_8548468874185098314[312] = 0;
   out_8548468874185098314[313] = 0;
   out_8548468874185098314[314] = 0;
   out_8548468874185098314[315] = 0;
   out_8548468874185098314[316] = 0;
   out_8548468874185098314[317] = 0;
   out_8548468874185098314[318] = 0;
   out_8548468874185098314[319] = 0;
   out_8548468874185098314[320] = 0;
   out_8548468874185098314[321] = 0;
   out_8548468874185098314[322] = 0;
   out_8548468874185098314[323] = 1;
}
void h_4(double *state, double *unused, double *out_3252594159490457083) {
   out_3252594159490457083[0] = state[6] + state[9];
   out_3252594159490457083[1] = state[7] + state[10];
   out_3252594159490457083[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_3698331479637363251) {
   out_3698331479637363251[0] = 0;
   out_3698331479637363251[1] = 0;
   out_3698331479637363251[2] = 0;
   out_3698331479637363251[3] = 0;
   out_3698331479637363251[4] = 0;
   out_3698331479637363251[5] = 0;
   out_3698331479637363251[6] = 1;
   out_3698331479637363251[7] = 0;
   out_3698331479637363251[8] = 0;
   out_3698331479637363251[9] = 1;
   out_3698331479637363251[10] = 0;
   out_3698331479637363251[11] = 0;
   out_3698331479637363251[12] = 0;
   out_3698331479637363251[13] = 0;
   out_3698331479637363251[14] = 0;
   out_3698331479637363251[15] = 0;
   out_3698331479637363251[16] = 0;
   out_3698331479637363251[17] = 0;
   out_3698331479637363251[18] = 0;
   out_3698331479637363251[19] = 0;
   out_3698331479637363251[20] = 0;
   out_3698331479637363251[21] = 0;
   out_3698331479637363251[22] = 0;
   out_3698331479637363251[23] = 0;
   out_3698331479637363251[24] = 0;
   out_3698331479637363251[25] = 1;
   out_3698331479637363251[26] = 0;
   out_3698331479637363251[27] = 0;
   out_3698331479637363251[28] = 1;
   out_3698331479637363251[29] = 0;
   out_3698331479637363251[30] = 0;
   out_3698331479637363251[31] = 0;
   out_3698331479637363251[32] = 0;
   out_3698331479637363251[33] = 0;
   out_3698331479637363251[34] = 0;
   out_3698331479637363251[35] = 0;
   out_3698331479637363251[36] = 0;
   out_3698331479637363251[37] = 0;
   out_3698331479637363251[38] = 0;
   out_3698331479637363251[39] = 0;
   out_3698331479637363251[40] = 0;
   out_3698331479637363251[41] = 0;
   out_3698331479637363251[42] = 0;
   out_3698331479637363251[43] = 0;
   out_3698331479637363251[44] = 1;
   out_3698331479637363251[45] = 0;
   out_3698331479637363251[46] = 0;
   out_3698331479637363251[47] = 1;
   out_3698331479637363251[48] = 0;
   out_3698331479637363251[49] = 0;
   out_3698331479637363251[50] = 0;
   out_3698331479637363251[51] = 0;
   out_3698331479637363251[52] = 0;
   out_3698331479637363251[53] = 0;
}
void h_10(double *state, double *unused, double *out_3535286898244842348) {
   out_3535286898244842348[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_3535286898244842348[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_3535286898244842348[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_694831672492554201) {
   out_694831672492554201[0] = 0;
   out_694831672492554201[1] = 9.8100000000000005*cos(state[1]);
   out_694831672492554201[2] = 0;
   out_694831672492554201[3] = 0;
   out_694831672492554201[4] = -state[8];
   out_694831672492554201[5] = state[7];
   out_694831672492554201[6] = 0;
   out_694831672492554201[7] = state[5];
   out_694831672492554201[8] = -state[4];
   out_694831672492554201[9] = 0;
   out_694831672492554201[10] = 0;
   out_694831672492554201[11] = 0;
   out_694831672492554201[12] = 1;
   out_694831672492554201[13] = 0;
   out_694831672492554201[14] = 0;
   out_694831672492554201[15] = 1;
   out_694831672492554201[16] = 0;
   out_694831672492554201[17] = 0;
   out_694831672492554201[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_694831672492554201[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_694831672492554201[20] = 0;
   out_694831672492554201[21] = state[8];
   out_694831672492554201[22] = 0;
   out_694831672492554201[23] = -state[6];
   out_694831672492554201[24] = -state[5];
   out_694831672492554201[25] = 0;
   out_694831672492554201[26] = state[3];
   out_694831672492554201[27] = 0;
   out_694831672492554201[28] = 0;
   out_694831672492554201[29] = 0;
   out_694831672492554201[30] = 0;
   out_694831672492554201[31] = 1;
   out_694831672492554201[32] = 0;
   out_694831672492554201[33] = 0;
   out_694831672492554201[34] = 1;
   out_694831672492554201[35] = 0;
   out_694831672492554201[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_694831672492554201[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_694831672492554201[38] = 0;
   out_694831672492554201[39] = -state[7];
   out_694831672492554201[40] = state[6];
   out_694831672492554201[41] = 0;
   out_694831672492554201[42] = state[4];
   out_694831672492554201[43] = -state[3];
   out_694831672492554201[44] = 0;
   out_694831672492554201[45] = 0;
   out_694831672492554201[46] = 0;
   out_694831672492554201[47] = 0;
   out_694831672492554201[48] = 0;
   out_694831672492554201[49] = 0;
   out_694831672492554201[50] = 1;
   out_694831672492554201[51] = 0;
   out_694831672492554201[52] = 0;
   out_694831672492554201[53] = 1;
}
void h_13(double *state, double *unused, double *out_203621820230683097) {
   out_203621820230683097[0] = state[3];
   out_203621820230683097[1] = state[4];
   out_203621820230683097[2] = state[5];
}
void H_13(double *state, double *unused, double *out_3912299728679337678) {
   out_3912299728679337678[0] = 0;
   out_3912299728679337678[1] = 0;
   out_3912299728679337678[2] = 0;
   out_3912299728679337678[3] = 1;
   out_3912299728679337678[4] = 0;
   out_3912299728679337678[5] = 0;
   out_3912299728679337678[6] = 0;
   out_3912299728679337678[7] = 0;
   out_3912299728679337678[8] = 0;
   out_3912299728679337678[9] = 0;
   out_3912299728679337678[10] = 0;
   out_3912299728679337678[11] = 0;
   out_3912299728679337678[12] = 0;
   out_3912299728679337678[13] = 0;
   out_3912299728679337678[14] = 0;
   out_3912299728679337678[15] = 0;
   out_3912299728679337678[16] = 0;
   out_3912299728679337678[17] = 0;
   out_3912299728679337678[18] = 0;
   out_3912299728679337678[19] = 0;
   out_3912299728679337678[20] = 0;
   out_3912299728679337678[21] = 0;
   out_3912299728679337678[22] = 1;
   out_3912299728679337678[23] = 0;
   out_3912299728679337678[24] = 0;
   out_3912299728679337678[25] = 0;
   out_3912299728679337678[26] = 0;
   out_3912299728679337678[27] = 0;
   out_3912299728679337678[28] = 0;
   out_3912299728679337678[29] = 0;
   out_3912299728679337678[30] = 0;
   out_3912299728679337678[31] = 0;
   out_3912299728679337678[32] = 0;
   out_3912299728679337678[33] = 0;
   out_3912299728679337678[34] = 0;
   out_3912299728679337678[35] = 0;
   out_3912299728679337678[36] = 0;
   out_3912299728679337678[37] = 0;
   out_3912299728679337678[38] = 0;
   out_3912299728679337678[39] = 0;
   out_3912299728679337678[40] = 0;
   out_3912299728679337678[41] = 1;
   out_3912299728679337678[42] = 0;
   out_3912299728679337678[43] = 0;
   out_3912299728679337678[44] = 0;
   out_3912299728679337678[45] = 0;
   out_3912299728679337678[46] = 0;
   out_3912299728679337678[47] = 0;
   out_3912299728679337678[48] = 0;
   out_3912299728679337678[49] = 0;
   out_3912299728679337678[50] = 0;
   out_3912299728679337678[51] = 0;
   out_3912299728679337678[52] = 0;
   out_3912299728679337678[53] = 0;
}
void h_14(double *state, double *unused, double *out_4310404466280692584) {
   out_4310404466280692584[0] = state[6];
   out_4310404466280692584[1] = state[7];
   out_4310404466280692584[2] = state[8];
}
void H_14(double *state, double *unused, double *out_6781119911932735547) {
   out_6781119911932735547[0] = 0;
   out_6781119911932735547[1] = 0;
   out_6781119911932735547[2] = 0;
   out_6781119911932735547[3] = 0;
   out_6781119911932735547[4] = 0;
   out_6781119911932735547[5] = 0;
   out_6781119911932735547[6] = 1;
   out_6781119911932735547[7] = 0;
   out_6781119911932735547[8] = 0;
   out_6781119911932735547[9] = 0;
   out_6781119911932735547[10] = 0;
   out_6781119911932735547[11] = 0;
   out_6781119911932735547[12] = 0;
   out_6781119911932735547[13] = 0;
   out_6781119911932735547[14] = 0;
   out_6781119911932735547[15] = 0;
   out_6781119911932735547[16] = 0;
   out_6781119911932735547[17] = 0;
   out_6781119911932735547[18] = 0;
   out_6781119911932735547[19] = 0;
   out_6781119911932735547[20] = 0;
   out_6781119911932735547[21] = 0;
   out_6781119911932735547[22] = 0;
   out_6781119911932735547[23] = 0;
   out_6781119911932735547[24] = 0;
   out_6781119911932735547[25] = 1;
   out_6781119911932735547[26] = 0;
   out_6781119911932735547[27] = 0;
   out_6781119911932735547[28] = 0;
   out_6781119911932735547[29] = 0;
   out_6781119911932735547[30] = 0;
   out_6781119911932735547[31] = 0;
   out_6781119911932735547[32] = 0;
   out_6781119911932735547[33] = 0;
   out_6781119911932735547[34] = 0;
   out_6781119911932735547[35] = 0;
   out_6781119911932735547[36] = 0;
   out_6781119911932735547[37] = 0;
   out_6781119911932735547[38] = 0;
   out_6781119911932735547[39] = 0;
   out_6781119911932735547[40] = 0;
   out_6781119911932735547[41] = 0;
   out_6781119911932735547[42] = 0;
   out_6781119911932735547[43] = 0;
   out_6781119911932735547[44] = 1;
   out_6781119911932735547[45] = 0;
   out_6781119911932735547[46] = 0;
   out_6781119911932735547[47] = 0;
   out_6781119911932735547[48] = 0;
   out_6781119911932735547[49] = 0;
   out_6781119911932735547[50] = 0;
   out_6781119911932735547[51] = 0;
   out_6781119911932735547[52] = 0;
   out_6781119911932735547[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_4874754272255029803) {
  err_fun(nom_x, delta_x, out_4874754272255029803);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_3314318466659131181) {
  inv_err_fun(nom_x, true_x, out_3314318466659131181);
}
void pose_H_mod_fun(double *state, double *out_8802356504304725397) {
  H_mod_fun(state, out_8802356504304725397);
}
void pose_f_fun(double *state, double dt, double *out_495287790681774033) {
  f_fun(state,  dt, out_495287790681774033);
}
void pose_F_fun(double *state, double dt, double *out_8548468874185098314) {
  F_fun(state,  dt, out_8548468874185098314);
}
void pose_h_4(double *state, double *unused, double *out_3252594159490457083) {
  h_4(state, unused, out_3252594159490457083);
}
void pose_H_4(double *state, double *unused, double *out_3698331479637363251) {
  H_4(state, unused, out_3698331479637363251);
}
void pose_h_10(double *state, double *unused, double *out_3535286898244842348) {
  h_10(state, unused, out_3535286898244842348);
}
void pose_H_10(double *state, double *unused, double *out_694831672492554201) {
  H_10(state, unused, out_694831672492554201);
}
void pose_h_13(double *state, double *unused, double *out_203621820230683097) {
  h_13(state, unused, out_203621820230683097);
}
void pose_H_13(double *state, double *unused, double *out_3912299728679337678) {
  H_13(state, unused, out_3912299728679337678);
}
void pose_h_14(double *state, double *unused, double *out_4310404466280692584) {
  h_14(state, unused, out_4310404466280692584);
}
void pose_H_14(double *state, double *unused, double *out_6781119911932735547) {
  H_14(state, unused, out_6781119911932735547);
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
