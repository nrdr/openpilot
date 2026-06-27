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
void err_fun(double *nom_x, double *delta_x, double *out_691514128797402705) {
   out_691514128797402705[0] = delta_x[0] + nom_x[0];
   out_691514128797402705[1] = delta_x[1] + nom_x[1];
   out_691514128797402705[2] = delta_x[2] + nom_x[2];
   out_691514128797402705[3] = delta_x[3] + nom_x[3];
   out_691514128797402705[4] = delta_x[4] + nom_x[4];
   out_691514128797402705[5] = delta_x[5] + nom_x[5];
   out_691514128797402705[6] = delta_x[6] + nom_x[6];
   out_691514128797402705[7] = delta_x[7] + nom_x[7];
   out_691514128797402705[8] = delta_x[8] + nom_x[8];
   out_691514128797402705[9] = delta_x[9] + nom_x[9];
   out_691514128797402705[10] = delta_x[10] + nom_x[10];
   out_691514128797402705[11] = delta_x[11] + nom_x[11];
   out_691514128797402705[12] = delta_x[12] + nom_x[12];
   out_691514128797402705[13] = delta_x[13] + nom_x[13];
   out_691514128797402705[14] = delta_x[14] + nom_x[14];
   out_691514128797402705[15] = delta_x[15] + nom_x[15];
   out_691514128797402705[16] = delta_x[16] + nom_x[16];
   out_691514128797402705[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_2118645859809610286) {
   out_2118645859809610286[0] = -nom_x[0] + true_x[0];
   out_2118645859809610286[1] = -nom_x[1] + true_x[1];
   out_2118645859809610286[2] = -nom_x[2] + true_x[2];
   out_2118645859809610286[3] = -nom_x[3] + true_x[3];
   out_2118645859809610286[4] = -nom_x[4] + true_x[4];
   out_2118645859809610286[5] = -nom_x[5] + true_x[5];
   out_2118645859809610286[6] = -nom_x[6] + true_x[6];
   out_2118645859809610286[7] = -nom_x[7] + true_x[7];
   out_2118645859809610286[8] = -nom_x[8] + true_x[8];
   out_2118645859809610286[9] = -nom_x[9] + true_x[9];
   out_2118645859809610286[10] = -nom_x[10] + true_x[10];
   out_2118645859809610286[11] = -nom_x[11] + true_x[11];
   out_2118645859809610286[12] = -nom_x[12] + true_x[12];
   out_2118645859809610286[13] = -nom_x[13] + true_x[13];
   out_2118645859809610286[14] = -nom_x[14] + true_x[14];
   out_2118645859809610286[15] = -nom_x[15] + true_x[15];
   out_2118645859809610286[16] = -nom_x[16] + true_x[16];
   out_2118645859809610286[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_6073294327909702994) {
   out_6073294327909702994[0] = 1.0;
   out_6073294327909702994[1] = 0.0;
   out_6073294327909702994[2] = 0.0;
   out_6073294327909702994[3] = 0.0;
   out_6073294327909702994[4] = 0.0;
   out_6073294327909702994[5] = 0.0;
   out_6073294327909702994[6] = 0.0;
   out_6073294327909702994[7] = 0.0;
   out_6073294327909702994[8] = 0.0;
   out_6073294327909702994[9] = 0.0;
   out_6073294327909702994[10] = 0.0;
   out_6073294327909702994[11] = 0.0;
   out_6073294327909702994[12] = 0.0;
   out_6073294327909702994[13] = 0.0;
   out_6073294327909702994[14] = 0.0;
   out_6073294327909702994[15] = 0.0;
   out_6073294327909702994[16] = 0.0;
   out_6073294327909702994[17] = 0.0;
   out_6073294327909702994[18] = 0.0;
   out_6073294327909702994[19] = 1.0;
   out_6073294327909702994[20] = 0.0;
   out_6073294327909702994[21] = 0.0;
   out_6073294327909702994[22] = 0.0;
   out_6073294327909702994[23] = 0.0;
   out_6073294327909702994[24] = 0.0;
   out_6073294327909702994[25] = 0.0;
   out_6073294327909702994[26] = 0.0;
   out_6073294327909702994[27] = 0.0;
   out_6073294327909702994[28] = 0.0;
   out_6073294327909702994[29] = 0.0;
   out_6073294327909702994[30] = 0.0;
   out_6073294327909702994[31] = 0.0;
   out_6073294327909702994[32] = 0.0;
   out_6073294327909702994[33] = 0.0;
   out_6073294327909702994[34] = 0.0;
   out_6073294327909702994[35] = 0.0;
   out_6073294327909702994[36] = 0.0;
   out_6073294327909702994[37] = 0.0;
   out_6073294327909702994[38] = 1.0;
   out_6073294327909702994[39] = 0.0;
   out_6073294327909702994[40] = 0.0;
   out_6073294327909702994[41] = 0.0;
   out_6073294327909702994[42] = 0.0;
   out_6073294327909702994[43] = 0.0;
   out_6073294327909702994[44] = 0.0;
   out_6073294327909702994[45] = 0.0;
   out_6073294327909702994[46] = 0.0;
   out_6073294327909702994[47] = 0.0;
   out_6073294327909702994[48] = 0.0;
   out_6073294327909702994[49] = 0.0;
   out_6073294327909702994[50] = 0.0;
   out_6073294327909702994[51] = 0.0;
   out_6073294327909702994[52] = 0.0;
   out_6073294327909702994[53] = 0.0;
   out_6073294327909702994[54] = 0.0;
   out_6073294327909702994[55] = 0.0;
   out_6073294327909702994[56] = 0.0;
   out_6073294327909702994[57] = 1.0;
   out_6073294327909702994[58] = 0.0;
   out_6073294327909702994[59] = 0.0;
   out_6073294327909702994[60] = 0.0;
   out_6073294327909702994[61] = 0.0;
   out_6073294327909702994[62] = 0.0;
   out_6073294327909702994[63] = 0.0;
   out_6073294327909702994[64] = 0.0;
   out_6073294327909702994[65] = 0.0;
   out_6073294327909702994[66] = 0.0;
   out_6073294327909702994[67] = 0.0;
   out_6073294327909702994[68] = 0.0;
   out_6073294327909702994[69] = 0.0;
   out_6073294327909702994[70] = 0.0;
   out_6073294327909702994[71] = 0.0;
   out_6073294327909702994[72] = 0.0;
   out_6073294327909702994[73] = 0.0;
   out_6073294327909702994[74] = 0.0;
   out_6073294327909702994[75] = 0.0;
   out_6073294327909702994[76] = 1.0;
   out_6073294327909702994[77] = 0.0;
   out_6073294327909702994[78] = 0.0;
   out_6073294327909702994[79] = 0.0;
   out_6073294327909702994[80] = 0.0;
   out_6073294327909702994[81] = 0.0;
   out_6073294327909702994[82] = 0.0;
   out_6073294327909702994[83] = 0.0;
   out_6073294327909702994[84] = 0.0;
   out_6073294327909702994[85] = 0.0;
   out_6073294327909702994[86] = 0.0;
   out_6073294327909702994[87] = 0.0;
   out_6073294327909702994[88] = 0.0;
   out_6073294327909702994[89] = 0.0;
   out_6073294327909702994[90] = 0.0;
   out_6073294327909702994[91] = 0.0;
   out_6073294327909702994[92] = 0.0;
   out_6073294327909702994[93] = 0.0;
   out_6073294327909702994[94] = 0.0;
   out_6073294327909702994[95] = 1.0;
   out_6073294327909702994[96] = 0.0;
   out_6073294327909702994[97] = 0.0;
   out_6073294327909702994[98] = 0.0;
   out_6073294327909702994[99] = 0.0;
   out_6073294327909702994[100] = 0.0;
   out_6073294327909702994[101] = 0.0;
   out_6073294327909702994[102] = 0.0;
   out_6073294327909702994[103] = 0.0;
   out_6073294327909702994[104] = 0.0;
   out_6073294327909702994[105] = 0.0;
   out_6073294327909702994[106] = 0.0;
   out_6073294327909702994[107] = 0.0;
   out_6073294327909702994[108] = 0.0;
   out_6073294327909702994[109] = 0.0;
   out_6073294327909702994[110] = 0.0;
   out_6073294327909702994[111] = 0.0;
   out_6073294327909702994[112] = 0.0;
   out_6073294327909702994[113] = 0.0;
   out_6073294327909702994[114] = 1.0;
   out_6073294327909702994[115] = 0.0;
   out_6073294327909702994[116] = 0.0;
   out_6073294327909702994[117] = 0.0;
   out_6073294327909702994[118] = 0.0;
   out_6073294327909702994[119] = 0.0;
   out_6073294327909702994[120] = 0.0;
   out_6073294327909702994[121] = 0.0;
   out_6073294327909702994[122] = 0.0;
   out_6073294327909702994[123] = 0.0;
   out_6073294327909702994[124] = 0.0;
   out_6073294327909702994[125] = 0.0;
   out_6073294327909702994[126] = 0.0;
   out_6073294327909702994[127] = 0.0;
   out_6073294327909702994[128] = 0.0;
   out_6073294327909702994[129] = 0.0;
   out_6073294327909702994[130] = 0.0;
   out_6073294327909702994[131] = 0.0;
   out_6073294327909702994[132] = 0.0;
   out_6073294327909702994[133] = 1.0;
   out_6073294327909702994[134] = 0.0;
   out_6073294327909702994[135] = 0.0;
   out_6073294327909702994[136] = 0.0;
   out_6073294327909702994[137] = 0.0;
   out_6073294327909702994[138] = 0.0;
   out_6073294327909702994[139] = 0.0;
   out_6073294327909702994[140] = 0.0;
   out_6073294327909702994[141] = 0.0;
   out_6073294327909702994[142] = 0.0;
   out_6073294327909702994[143] = 0.0;
   out_6073294327909702994[144] = 0.0;
   out_6073294327909702994[145] = 0.0;
   out_6073294327909702994[146] = 0.0;
   out_6073294327909702994[147] = 0.0;
   out_6073294327909702994[148] = 0.0;
   out_6073294327909702994[149] = 0.0;
   out_6073294327909702994[150] = 0.0;
   out_6073294327909702994[151] = 0.0;
   out_6073294327909702994[152] = 1.0;
   out_6073294327909702994[153] = 0.0;
   out_6073294327909702994[154] = 0.0;
   out_6073294327909702994[155] = 0.0;
   out_6073294327909702994[156] = 0.0;
   out_6073294327909702994[157] = 0.0;
   out_6073294327909702994[158] = 0.0;
   out_6073294327909702994[159] = 0.0;
   out_6073294327909702994[160] = 0.0;
   out_6073294327909702994[161] = 0.0;
   out_6073294327909702994[162] = 0.0;
   out_6073294327909702994[163] = 0.0;
   out_6073294327909702994[164] = 0.0;
   out_6073294327909702994[165] = 0.0;
   out_6073294327909702994[166] = 0.0;
   out_6073294327909702994[167] = 0.0;
   out_6073294327909702994[168] = 0.0;
   out_6073294327909702994[169] = 0.0;
   out_6073294327909702994[170] = 0.0;
   out_6073294327909702994[171] = 1.0;
   out_6073294327909702994[172] = 0.0;
   out_6073294327909702994[173] = 0.0;
   out_6073294327909702994[174] = 0.0;
   out_6073294327909702994[175] = 0.0;
   out_6073294327909702994[176] = 0.0;
   out_6073294327909702994[177] = 0.0;
   out_6073294327909702994[178] = 0.0;
   out_6073294327909702994[179] = 0.0;
   out_6073294327909702994[180] = 0.0;
   out_6073294327909702994[181] = 0.0;
   out_6073294327909702994[182] = 0.0;
   out_6073294327909702994[183] = 0.0;
   out_6073294327909702994[184] = 0.0;
   out_6073294327909702994[185] = 0.0;
   out_6073294327909702994[186] = 0.0;
   out_6073294327909702994[187] = 0.0;
   out_6073294327909702994[188] = 0.0;
   out_6073294327909702994[189] = 0.0;
   out_6073294327909702994[190] = 1.0;
   out_6073294327909702994[191] = 0.0;
   out_6073294327909702994[192] = 0.0;
   out_6073294327909702994[193] = 0.0;
   out_6073294327909702994[194] = 0.0;
   out_6073294327909702994[195] = 0.0;
   out_6073294327909702994[196] = 0.0;
   out_6073294327909702994[197] = 0.0;
   out_6073294327909702994[198] = 0.0;
   out_6073294327909702994[199] = 0.0;
   out_6073294327909702994[200] = 0.0;
   out_6073294327909702994[201] = 0.0;
   out_6073294327909702994[202] = 0.0;
   out_6073294327909702994[203] = 0.0;
   out_6073294327909702994[204] = 0.0;
   out_6073294327909702994[205] = 0.0;
   out_6073294327909702994[206] = 0.0;
   out_6073294327909702994[207] = 0.0;
   out_6073294327909702994[208] = 0.0;
   out_6073294327909702994[209] = 1.0;
   out_6073294327909702994[210] = 0.0;
   out_6073294327909702994[211] = 0.0;
   out_6073294327909702994[212] = 0.0;
   out_6073294327909702994[213] = 0.0;
   out_6073294327909702994[214] = 0.0;
   out_6073294327909702994[215] = 0.0;
   out_6073294327909702994[216] = 0.0;
   out_6073294327909702994[217] = 0.0;
   out_6073294327909702994[218] = 0.0;
   out_6073294327909702994[219] = 0.0;
   out_6073294327909702994[220] = 0.0;
   out_6073294327909702994[221] = 0.0;
   out_6073294327909702994[222] = 0.0;
   out_6073294327909702994[223] = 0.0;
   out_6073294327909702994[224] = 0.0;
   out_6073294327909702994[225] = 0.0;
   out_6073294327909702994[226] = 0.0;
   out_6073294327909702994[227] = 0.0;
   out_6073294327909702994[228] = 1.0;
   out_6073294327909702994[229] = 0.0;
   out_6073294327909702994[230] = 0.0;
   out_6073294327909702994[231] = 0.0;
   out_6073294327909702994[232] = 0.0;
   out_6073294327909702994[233] = 0.0;
   out_6073294327909702994[234] = 0.0;
   out_6073294327909702994[235] = 0.0;
   out_6073294327909702994[236] = 0.0;
   out_6073294327909702994[237] = 0.0;
   out_6073294327909702994[238] = 0.0;
   out_6073294327909702994[239] = 0.0;
   out_6073294327909702994[240] = 0.0;
   out_6073294327909702994[241] = 0.0;
   out_6073294327909702994[242] = 0.0;
   out_6073294327909702994[243] = 0.0;
   out_6073294327909702994[244] = 0.0;
   out_6073294327909702994[245] = 0.0;
   out_6073294327909702994[246] = 0.0;
   out_6073294327909702994[247] = 1.0;
   out_6073294327909702994[248] = 0.0;
   out_6073294327909702994[249] = 0.0;
   out_6073294327909702994[250] = 0.0;
   out_6073294327909702994[251] = 0.0;
   out_6073294327909702994[252] = 0.0;
   out_6073294327909702994[253] = 0.0;
   out_6073294327909702994[254] = 0.0;
   out_6073294327909702994[255] = 0.0;
   out_6073294327909702994[256] = 0.0;
   out_6073294327909702994[257] = 0.0;
   out_6073294327909702994[258] = 0.0;
   out_6073294327909702994[259] = 0.0;
   out_6073294327909702994[260] = 0.0;
   out_6073294327909702994[261] = 0.0;
   out_6073294327909702994[262] = 0.0;
   out_6073294327909702994[263] = 0.0;
   out_6073294327909702994[264] = 0.0;
   out_6073294327909702994[265] = 0.0;
   out_6073294327909702994[266] = 1.0;
   out_6073294327909702994[267] = 0.0;
   out_6073294327909702994[268] = 0.0;
   out_6073294327909702994[269] = 0.0;
   out_6073294327909702994[270] = 0.0;
   out_6073294327909702994[271] = 0.0;
   out_6073294327909702994[272] = 0.0;
   out_6073294327909702994[273] = 0.0;
   out_6073294327909702994[274] = 0.0;
   out_6073294327909702994[275] = 0.0;
   out_6073294327909702994[276] = 0.0;
   out_6073294327909702994[277] = 0.0;
   out_6073294327909702994[278] = 0.0;
   out_6073294327909702994[279] = 0.0;
   out_6073294327909702994[280] = 0.0;
   out_6073294327909702994[281] = 0.0;
   out_6073294327909702994[282] = 0.0;
   out_6073294327909702994[283] = 0.0;
   out_6073294327909702994[284] = 0.0;
   out_6073294327909702994[285] = 1.0;
   out_6073294327909702994[286] = 0.0;
   out_6073294327909702994[287] = 0.0;
   out_6073294327909702994[288] = 0.0;
   out_6073294327909702994[289] = 0.0;
   out_6073294327909702994[290] = 0.0;
   out_6073294327909702994[291] = 0.0;
   out_6073294327909702994[292] = 0.0;
   out_6073294327909702994[293] = 0.0;
   out_6073294327909702994[294] = 0.0;
   out_6073294327909702994[295] = 0.0;
   out_6073294327909702994[296] = 0.0;
   out_6073294327909702994[297] = 0.0;
   out_6073294327909702994[298] = 0.0;
   out_6073294327909702994[299] = 0.0;
   out_6073294327909702994[300] = 0.0;
   out_6073294327909702994[301] = 0.0;
   out_6073294327909702994[302] = 0.0;
   out_6073294327909702994[303] = 0.0;
   out_6073294327909702994[304] = 1.0;
   out_6073294327909702994[305] = 0.0;
   out_6073294327909702994[306] = 0.0;
   out_6073294327909702994[307] = 0.0;
   out_6073294327909702994[308] = 0.0;
   out_6073294327909702994[309] = 0.0;
   out_6073294327909702994[310] = 0.0;
   out_6073294327909702994[311] = 0.0;
   out_6073294327909702994[312] = 0.0;
   out_6073294327909702994[313] = 0.0;
   out_6073294327909702994[314] = 0.0;
   out_6073294327909702994[315] = 0.0;
   out_6073294327909702994[316] = 0.0;
   out_6073294327909702994[317] = 0.0;
   out_6073294327909702994[318] = 0.0;
   out_6073294327909702994[319] = 0.0;
   out_6073294327909702994[320] = 0.0;
   out_6073294327909702994[321] = 0.0;
   out_6073294327909702994[322] = 0.0;
   out_6073294327909702994[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_395315253084136488) {
   out_395315253084136488[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_395315253084136488[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_395315253084136488[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_395315253084136488[3] = dt*state[12] + state[3];
   out_395315253084136488[4] = dt*state[13] + state[4];
   out_395315253084136488[5] = dt*state[14] + state[5];
   out_395315253084136488[6] = state[6];
   out_395315253084136488[7] = state[7];
   out_395315253084136488[8] = state[8];
   out_395315253084136488[9] = state[9];
   out_395315253084136488[10] = state[10];
   out_395315253084136488[11] = state[11];
   out_395315253084136488[12] = state[12];
   out_395315253084136488[13] = state[13];
   out_395315253084136488[14] = state[14];
   out_395315253084136488[15] = state[15];
   out_395315253084136488[16] = state[16];
   out_395315253084136488[17] = state[17];
}
void F_fun(double *state, double dt, double *out_3144799740001374156) {
   out_3144799740001374156[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3144799740001374156[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3144799740001374156[2] = 0;
   out_3144799740001374156[3] = 0;
   out_3144799740001374156[4] = 0;
   out_3144799740001374156[5] = 0;
   out_3144799740001374156[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3144799740001374156[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3144799740001374156[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_3144799740001374156[9] = 0;
   out_3144799740001374156[10] = 0;
   out_3144799740001374156[11] = 0;
   out_3144799740001374156[12] = 0;
   out_3144799740001374156[13] = 0;
   out_3144799740001374156[14] = 0;
   out_3144799740001374156[15] = 0;
   out_3144799740001374156[16] = 0;
   out_3144799740001374156[17] = 0;
   out_3144799740001374156[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3144799740001374156[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3144799740001374156[20] = 0;
   out_3144799740001374156[21] = 0;
   out_3144799740001374156[22] = 0;
   out_3144799740001374156[23] = 0;
   out_3144799740001374156[24] = 0;
   out_3144799740001374156[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3144799740001374156[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_3144799740001374156[27] = 0;
   out_3144799740001374156[28] = 0;
   out_3144799740001374156[29] = 0;
   out_3144799740001374156[30] = 0;
   out_3144799740001374156[31] = 0;
   out_3144799740001374156[32] = 0;
   out_3144799740001374156[33] = 0;
   out_3144799740001374156[34] = 0;
   out_3144799740001374156[35] = 0;
   out_3144799740001374156[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3144799740001374156[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3144799740001374156[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3144799740001374156[39] = 0;
   out_3144799740001374156[40] = 0;
   out_3144799740001374156[41] = 0;
   out_3144799740001374156[42] = 0;
   out_3144799740001374156[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3144799740001374156[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_3144799740001374156[45] = 0;
   out_3144799740001374156[46] = 0;
   out_3144799740001374156[47] = 0;
   out_3144799740001374156[48] = 0;
   out_3144799740001374156[49] = 0;
   out_3144799740001374156[50] = 0;
   out_3144799740001374156[51] = 0;
   out_3144799740001374156[52] = 0;
   out_3144799740001374156[53] = 0;
   out_3144799740001374156[54] = 0;
   out_3144799740001374156[55] = 0;
   out_3144799740001374156[56] = 0;
   out_3144799740001374156[57] = 1;
   out_3144799740001374156[58] = 0;
   out_3144799740001374156[59] = 0;
   out_3144799740001374156[60] = 0;
   out_3144799740001374156[61] = 0;
   out_3144799740001374156[62] = 0;
   out_3144799740001374156[63] = 0;
   out_3144799740001374156[64] = 0;
   out_3144799740001374156[65] = 0;
   out_3144799740001374156[66] = dt;
   out_3144799740001374156[67] = 0;
   out_3144799740001374156[68] = 0;
   out_3144799740001374156[69] = 0;
   out_3144799740001374156[70] = 0;
   out_3144799740001374156[71] = 0;
   out_3144799740001374156[72] = 0;
   out_3144799740001374156[73] = 0;
   out_3144799740001374156[74] = 0;
   out_3144799740001374156[75] = 0;
   out_3144799740001374156[76] = 1;
   out_3144799740001374156[77] = 0;
   out_3144799740001374156[78] = 0;
   out_3144799740001374156[79] = 0;
   out_3144799740001374156[80] = 0;
   out_3144799740001374156[81] = 0;
   out_3144799740001374156[82] = 0;
   out_3144799740001374156[83] = 0;
   out_3144799740001374156[84] = 0;
   out_3144799740001374156[85] = dt;
   out_3144799740001374156[86] = 0;
   out_3144799740001374156[87] = 0;
   out_3144799740001374156[88] = 0;
   out_3144799740001374156[89] = 0;
   out_3144799740001374156[90] = 0;
   out_3144799740001374156[91] = 0;
   out_3144799740001374156[92] = 0;
   out_3144799740001374156[93] = 0;
   out_3144799740001374156[94] = 0;
   out_3144799740001374156[95] = 1;
   out_3144799740001374156[96] = 0;
   out_3144799740001374156[97] = 0;
   out_3144799740001374156[98] = 0;
   out_3144799740001374156[99] = 0;
   out_3144799740001374156[100] = 0;
   out_3144799740001374156[101] = 0;
   out_3144799740001374156[102] = 0;
   out_3144799740001374156[103] = 0;
   out_3144799740001374156[104] = dt;
   out_3144799740001374156[105] = 0;
   out_3144799740001374156[106] = 0;
   out_3144799740001374156[107] = 0;
   out_3144799740001374156[108] = 0;
   out_3144799740001374156[109] = 0;
   out_3144799740001374156[110] = 0;
   out_3144799740001374156[111] = 0;
   out_3144799740001374156[112] = 0;
   out_3144799740001374156[113] = 0;
   out_3144799740001374156[114] = 1;
   out_3144799740001374156[115] = 0;
   out_3144799740001374156[116] = 0;
   out_3144799740001374156[117] = 0;
   out_3144799740001374156[118] = 0;
   out_3144799740001374156[119] = 0;
   out_3144799740001374156[120] = 0;
   out_3144799740001374156[121] = 0;
   out_3144799740001374156[122] = 0;
   out_3144799740001374156[123] = 0;
   out_3144799740001374156[124] = 0;
   out_3144799740001374156[125] = 0;
   out_3144799740001374156[126] = 0;
   out_3144799740001374156[127] = 0;
   out_3144799740001374156[128] = 0;
   out_3144799740001374156[129] = 0;
   out_3144799740001374156[130] = 0;
   out_3144799740001374156[131] = 0;
   out_3144799740001374156[132] = 0;
   out_3144799740001374156[133] = 1;
   out_3144799740001374156[134] = 0;
   out_3144799740001374156[135] = 0;
   out_3144799740001374156[136] = 0;
   out_3144799740001374156[137] = 0;
   out_3144799740001374156[138] = 0;
   out_3144799740001374156[139] = 0;
   out_3144799740001374156[140] = 0;
   out_3144799740001374156[141] = 0;
   out_3144799740001374156[142] = 0;
   out_3144799740001374156[143] = 0;
   out_3144799740001374156[144] = 0;
   out_3144799740001374156[145] = 0;
   out_3144799740001374156[146] = 0;
   out_3144799740001374156[147] = 0;
   out_3144799740001374156[148] = 0;
   out_3144799740001374156[149] = 0;
   out_3144799740001374156[150] = 0;
   out_3144799740001374156[151] = 0;
   out_3144799740001374156[152] = 1;
   out_3144799740001374156[153] = 0;
   out_3144799740001374156[154] = 0;
   out_3144799740001374156[155] = 0;
   out_3144799740001374156[156] = 0;
   out_3144799740001374156[157] = 0;
   out_3144799740001374156[158] = 0;
   out_3144799740001374156[159] = 0;
   out_3144799740001374156[160] = 0;
   out_3144799740001374156[161] = 0;
   out_3144799740001374156[162] = 0;
   out_3144799740001374156[163] = 0;
   out_3144799740001374156[164] = 0;
   out_3144799740001374156[165] = 0;
   out_3144799740001374156[166] = 0;
   out_3144799740001374156[167] = 0;
   out_3144799740001374156[168] = 0;
   out_3144799740001374156[169] = 0;
   out_3144799740001374156[170] = 0;
   out_3144799740001374156[171] = 1;
   out_3144799740001374156[172] = 0;
   out_3144799740001374156[173] = 0;
   out_3144799740001374156[174] = 0;
   out_3144799740001374156[175] = 0;
   out_3144799740001374156[176] = 0;
   out_3144799740001374156[177] = 0;
   out_3144799740001374156[178] = 0;
   out_3144799740001374156[179] = 0;
   out_3144799740001374156[180] = 0;
   out_3144799740001374156[181] = 0;
   out_3144799740001374156[182] = 0;
   out_3144799740001374156[183] = 0;
   out_3144799740001374156[184] = 0;
   out_3144799740001374156[185] = 0;
   out_3144799740001374156[186] = 0;
   out_3144799740001374156[187] = 0;
   out_3144799740001374156[188] = 0;
   out_3144799740001374156[189] = 0;
   out_3144799740001374156[190] = 1;
   out_3144799740001374156[191] = 0;
   out_3144799740001374156[192] = 0;
   out_3144799740001374156[193] = 0;
   out_3144799740001374156[194] = 0;
   out_3144799740001374156[195] = 0;
   out_3144799740001374156[196] = 0;
   out_3144799740001374156[197] = 0;
   out_3144799740001374156[198] = 0;
   out_3144799740001374156[199] = 0;
   out_3144799740001374156[200] = 0;
   out_3144799740001374156[201] = 0;
   out_3144799740001374156[202] = 0;
   out_3144799740001374156[203] = 0;
   out_3144799740001374156[204] = 0;
   out_3144799740001374156[205] = 0;
   out_3144799740001374156[206] = 0;
   out_3144799740001374156[207] = 0;
   out_3144799740001374156[208] = 0;
   out_3144799740001374156[209] = 1;
   out_3144799740001374156[210] = 0;
   out_3144799740001374156[211] = 0;
   out_3144799740001374156[212] = 0;
   out_3144799740001374156[213] = 0;
   out_3144799740001374156[214] = 0;
   out_3144799740001374156[215] = 0;
   out_3144799740001374156[216] = 0;
   out_3144799740001374156[217] = 0;
   out_3144799740001374156[218] = 0;
   out_3144799740001374156[219] = 0;
   out_3144799740001374156[220] = 0;
   out_3144799740001374156[221] = 0;
   out_3144799740001374156[222] = 0;
   out_3144799740001374156[223] = 0;
   out_3144799740001374156[224] = 0;
   out_3144799740001374156[225] = 0;
   out_3144799740001374156[226] = 0;
   out_3144799740001374156[227] = 0;
   out_3144799740001374156[228] = 1;
   out_3144799740001374156[229] = 0;
   out_3144799740001374156[230] = 0;
   out_3144799740001374156[231] = 0;
   out_3144799740001374156[232] = 0;
   out_3144799740001374156[233] = 0;
   out_3144799740001374156[234] = 0;
   out_3144799740001374156[235] = 0;
   out_3144799740001374156[236] = 0;
   out_3144799740001374156[237] = 0;
   out_3144799740001374156[238] = 0;
   out_3144799740001374156[239] = 0;
   out_3144799740001374156[240] = 0;
   out_3144799740001374156[241] = 0;
   out_3144799740001374156[242] = 0;
   out_3144799740001374156[243] = 0;
   out_3144799740001374156[244] = 0;
   out_3144799740001374156[245] = 0;
   out_3144799740001374156[246] = 0;
   out_3144799740001374156[247] = 1;
   out_3144799740001374156[248] = 0;
   out_3144799740001374156[249] = 0;
   out_3144799740001374156[250] = 0;
   out_3144799740001374156[251] = 0;
   out_3144799740001374156[252] = 0;
   out_3144799740001374156[253] = 0;
   out_3144799740001374156[254] = 0;
   out_3144799740001374156[255] = 0;
   out_3144799740001374156[256] = 0;
   out_3144799740001374156[257] = 0;
   out_3144799740001374156[258] = 0;
   out_3144799740001374156[259] = 0;
   out_3144799740001374156[260] = 0;
   out_3144799740001374156[261] = 0;
   out_3144799740001374156[262] = 0;
   out_3144799740001374156[263] = 0;
   out_3144799740001374156[264] = 0;
   out_3144799740001374156[265] = 0;
   out_3144799740001374156[266] = 1;
   out_3144799740001374156[267] = 0;
   out_3144799740001374156[268] = 0;
   out_3144799740001374156[269] = 0;
   out_3144799740001374156[270] = 0;
   out_3144799740001374156[271] = 0;
   out_3144799740001374156[272] = 0;
   out_3144799740001374156[273] = 0;
   out_3144799740001374156[274] = 0;
   out_3144799740001374156[275] = 0;
   out_3144799740001374156[276] = 0;
   out_3144799740001374156[277] = 0;
   out_3144799740001374156[278] = 0;
   out_3144799740001374156[279] = 0;
   out_3144799740001374156[280] = 0;
   out_3144799740001374156[281] = 0;
   out_3144799740001374156[282] = 0;
   out_3144799740001374156[283] = 0;
   out_3144799740001374156[284] = 0;
   out_3144799740001374156[285] = 1;
   out_3144799740001374156[286] = 0;
   out_3144799740001374156[287] = 0;
   out_3144799740001374156[288] = 0;
   out_3144799740001374156[289] = 0;
   out_3144799740001374156[290] = 0;
   out_3144799740001374156[291] = 0;
   out_3144799740001374156[292] = 0;
   out_3144799740001374156[293] = 0;
   out_3144799740001374156[294] = 0;
   out_3144799740001374156[295] = 0;
   out_3144799740001374156[296] = 0;
   out_3144799740001374156[297] = 0;
   out_3144799740001374156[298] = 0;
   out_3144799740001374156[299] = 0;
   out_3144799740001374156[300] = 0;
   out_3144799740001374156[301] = 0;
   out_3144799740001374156[302] = 0;
   out_3144799740001374156[303] = 0;
   out_3144799740001374156[304] = 1;
   out_3144799740001374156[305] = 0;
   out_3144799740001374156[306] = 0;
   out_3144799740001374156[307] = 0;
   out_3144799740001374156[308] = 0;
   out_3144799740001374156[309] = 0;
   out_3144799740001374156[310] = 0;
   out_3144799740001374156[311] = 0;
   out_3144799740001374156[312] = 0;
   out_3144799740001374156[313] = 0;
   out_3144799740001374156[314] = 0;
   out_3144799740001374156[315] = 0;
   out_3144799740001374156[316] = 0;
   out_3144799740001374156[317] = 0;
   out_3144799740001374156[318] = 0;
   out_3144799740001374156[319] = 0;
   out_3144799740001374156[320] = 0;
   out_3144799740001374156[321] = 0;
   out_3144799740001374156[322] = 0;
   out_3144799740001374156[323] = 1;
}
void h_4(double *state, double *unused, double *out_7170570279272954882) {
   out_7170570279272954882[0] = state[6] + state[9];
   out_7170570279272954882[1] = state[7] + state[10];
   out_7170570279272954882[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_2301487118065795422) {
   out_2301487118065795422[0] = 0;
   out_2301487118065795422[1] = 0;
   out_2301487118065795422[2] = 0;
   out_2301487118065795422[3] = 0;
   out_2301487118065795422[4] = 0;
   out_2301487118065795422[5] = 0;
   out_2301487118065795422[6] = 1;
   out_2301487118065795422[7] = 0;
   out_2301487118065795422[8] = 0;
   out_2301487118065795422[9] = 1;
   out_2301487118065795422[10] = 0;
   out_2301487118065795422[11] = 0;
   out_2301487118065795422[12] = 0;
   out_2301487118065795422[13] = 0;
   out_2301487118065795422[14] = 0;
   out_2301487118065795422[15] = 0;
   out_2301487118065795422[16] = 0;
   out_2301487118065795422[17] = 0;
   out_2301487118065795422[18] = 0;
   out_2301487118065795422[19] = 0;
   out_2301487118065795422[20] = 0;
   out_2301487118065795422[21] = 0;
   out_2301487118065795422[22] = 0;
   out_2301487118065795422[23] = 0;
   out_2301487118065795422[24] = 0;
   out_2301487118065795422[25] = 1;
   out_2301487118065795422[26] = 0;
   out_2301487118065795422[27] = 0;
   out_2301487118065795422[28] = 1;
   out_2301487118065795422[29] = 0;
   out_2301487118065795422[30] = 0;
   out_2301487118065795422[31] = 0;
   out_2301487118065795422[32] = 0;
   out_2301487118065795422[33] = 0;
   out_2301487118065795422[34] = 0;
   out_2301487118065795422[35] = 0;
   out_2301487118065795422[36] = 0;
   out_2301487118065795422[37] = 0;
   out_2301487118065795422[38] = 0;
   out_2301487118065795422[39] = 0;
   out_2301487118065795422[40] = 0;
   out_2301487118065795422[41] = 0;
   out_2301487118065795422[42] = 0;
   out_2301487118065795422[43] = 0;
   out_2301487118065795422[44] = 1;
   out_2301487118065795422[45] = 0;
   out_2301487118065795422[46] = 0;
   out_2301487118065795422[47] = 1;
   out_2301487118065795422[48] = 0;
   out_2301487118065795422[49] = 0;
   out_2301487118065795422[50] = 0;
   out_2301487118065795422[51] = 0;
   out_2301487118065795422[52] = 0;
   out_2301487118065795422[53] = 0;
}
void h_10(double *state, double *unused, double *out_2811610427292929098) {
   out_2811610427292929098[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_2811610427292929098[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_2811610427292929098[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_4485692655108419471) {
   out_4485692655108419471[0] = 0;
   out_4485692655108419471[1] = 9.8100000000000005*cos(state[1]);
   out_4485692655108419471[2] = 0;
   out_4485692655108419471[3] = 0;
   out_4485692655108419471[4] = -state[8];
   out_4485692655108419471[5] = state[7];
   out_4485692655108419471[6] = 0;
   out_4485692655108419471[7] = state[5];
   out_4485692655108419471[8] = -state[4];
   out_4485692655108419471[9] = 0;
   out_4485692655108419471[10] = 0;
   out_4485692655108419471[11] = 0;
   out_4485692655108419471[12] = 1;
   out_4485692655108419471[13] = 0;
   out_4485692655108419471[14] = 0;
   out_4485692655108419471[15] = 1;
   out_4485692655108419471[16] = 0;
   out_4485692655108419471[17] = 0;
   out_4485692655108419471[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_4485692655108419471[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_4485692655108419471[20] = 0;
   out_4485692655108419471[21] = state[8];
   out_4485692655108419471[22] = 0;
   out_4485692655108419471[23] = -state[6];
   out_4485692655108419471[24] = -state[5];
   out_4485692655108419471[25] = 0;
   out_4485692655108419471[26] = state[3];
   out_4485692655108419471[27] = 0;
   out_4485692655108419471[28] = 0;
   out_4485692655108419471[29] = 0;
   out_4485692655108419471[30] = 0;
   out_4485692655108419471[31] = 1;
   out_4485692655108419471[32] = 0;
   out_4485692655108419471[33] = 0;
   out_4485692655108419471[34] = 1;
   out_4485692655108419471[35] = 0;
   out_4485692655108419471[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_4485692655108419471[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_4485692655108419471[38] = 0;
   out_4485692655108419471[39] = -state[7];
   out_4485692655108419471[40] = state[6];
   out_4485692655108419471[41] = 0;
   out_4485692655108419471[42] = state[4];
   out_4485692655108419471[43] = -state[3];
   out_4485692655108419471[44] = 0;
   out_4485692655108419471[45] = 0;
   out_4485692655108419471[46] = 0;
   out_4485692655108419471[47] = 0;
   out_4485692655108419471[48] = 0;
   out_4485692655108419471[49] = 0;
   out_4485692655108419471[50] = 1;
   out_4485692655108419471[51] = 0;
   out_4485692655108419471[52] = 0;
   out_4485692655108419471[53] = 1;
}
void h_13(double *state, double *unused, double *out_5723609330334209216) {
   out_5723609330334209216[0] = state[3];
   out_5723609330334209216[1] = state[4];
   out_5723609330334209216[2] = state[5];
}
void H_13(double *state, double *unused, double *out_910786707266537379) {
   out_910786707266537379[0] = 0;
   out_910786707266537379[1] = 0;
   out_910786707266537379[2] = 0;
   out_910786707266537379[3] = 1;
   out_910786707266537379[4] = 0;
   out_910786707266537379[5] = 0;
   out_910786707266537379[6] = 0;
   out_910786707266537379[7] = 0;
   out_910786707266537379[8] = 0;
   out_910786707266537379[9] = 0;
   out_910786707266537379[10] = 0;
   out_910786707266537379[11] = 0;
   out_910786707266537379[12] = 0;
   out_910786707266537379[13] = 0;
   out_910786707266537379[14] = 0;
   out_910786707266537379[15] = 0;
   out_910786707266537379[16] = 0;
   out_910786707266537379[17] = 0;
   out_910786707266537379[18] = 0;
   out_910786707266537379[19] = 0;
   out_910786707266537379[20] = 0;
   out_910786707266537379[21] = 0;
   out_910786707266537379[22] = 1;
   out_910786707266537379[23] = 0;
   out_910786707266537379[24] = 0;
   out_910786707266537379[25] = 0;
   out_910786707266537379[26] = 0;
   out_910786707266537379[27] = 0;
   out_910786707266537379[28] = 0;
   out_910786707266537379[29] = 0;
   out_910786707266537379[30] = 0;
   out_910786707266537379[31] = 0;
   out_910786707266537379[32] = 0;
   out_910786707266537379[33] = 0;
   out_910786707266537379[34] = 0;
   out_910786707266537379[35] = 0;
   out_910786707266537379[36] = 0;
   out_910786707266537379[37] = 0;
   out_910786707266537379[38] = 0;
   out_910786707266537379[39] = 0;
   out_910786707266537379[40] = 0;
   out_910786707266537379[41] = 1;
   out_910786707266537379[42] = 0;
   out_910786707266537379[43] = 0;
   out_910786707266537379[44] = 0;
   out_910786707266537379[45] = 0;
   out_910786707266537379[46] = 0;
   out_910786707266537379[47] = 0;
   out_910786707266537379[48] = 0;
   out_910786707266537379[49] = 0;
   out_910786707266537379[50] = 0;
   out_910786707266537379[51] = 0;
   out_910786707266537379[52] = 0;
   out_910786707266537379[53] = 0;
}
void h_14(double *state, double *unused, double *out_1904023991098828728) {
   out_1904023991098828728[0] = state[6];
   out_1904023991098828728[1] = state[7];
   out_1904023991098828728[2] = state[8];
}
void H_14(double *state, double *unused, double *out_5384275550361167718) {
   out_5384275550361167718[0] = 0;
   out_5384275550361167718[1] = 0;
   out_5384275550361167718[2] = 0;
   out_5384275550361167718[3] = 0;
   out_5384275550361167718[4] = 0;
   out_5384275550361167718[5] = 0;
   out_5384275550361167718[6] = 1;
   out_5384275550361167718[7] = 0;
   out_5384275550361167718[8] = 0;
   out_5384275550361167718[9] = 0;
   out_5384275550361167718[10] = 0;
   out_5384275550361167718[11] = 0;
   out_5384275550361167718[12] = 0;
   out_5384275550361167718[13] = 0;
   out_5384275550361167718[14] = 0;
   out_5384275550361167718[15] = 0;
   out_5384275550361167718[16] = 0;
   out_5384275550361167718[17] = 0;
   out_5384275550361167718[18] = 0;
   out_5384275550361167718[19] = 0;
   out_5384275550361167718[20] = 0;
   out_5384275550361167718[21] = 0;
   out_5384275550361167718[22] = 0;
   out_5384275550361167718[23] = 0;
   out_5384275550361167718[24] = 0;
   out_5384275550361167718[25] = 1;
   out_5384275550361167718[26] = 0;
   out_5384275550361167718[27] = 0;
   out_5384275550361167718[28] = 0;
   out_5384275550361167718[29] = 0;
   out_5384275550361167718[30] = 0;
   out_5384275550361167718[31] = 0;
   out_5384275550361167718[32] = 0;
   out_5384275550361167718[33] = 0;
   out_5384275550361167718[34] = 0;
   out_5384275550361167718[35] = 0;
   out_5384275550361167718[36] = 0;
   out_5384275550361167718[37] = 0;
   out_5384275550361167718[38] = 0;
   out_5384275550361167718[39] = 0;
   out_5384275550361167718[40] = 0;
   out_5384275550361167718[41] = 0;
   out_5384275550361167718[42] = 0;
   out_5384275550361167718[43] = 0;
   out_5384275550361167718[44] = 1;
   out_5384275550361167718[45] = 0;
   out_5384275550361167718[46] = 0;
   out_5384275550361167718[47] = 0;
   out_5384275550361167718[48] = 0;
   out_5384275550361167718[49] = 0;
   out_5384275550361167718[50] = 0;
   out_5384275550361167718[51] = 0;
   out_5384275550361167718[52] = 0;
   out_5384275550361167718[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_691514128797402705) {
  err_fun(nom_x, delta_x, out_691514128797402705);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_2118645859809610286) {
  inv_err_fun(nom_x, true_x, out_2118645859809610286);
}
void pose_H_mod_fun(double *state, double *out_6073294327909702994) {
  H_mod_fun(state, out_6073294327909702994);
}
void pose_f_fun(double *state, double dt, double *out_395315253084136488) {
  f_fun(state,  dt, out_395315253084136488);
}
void pose_F_fun(double *state, double dt, double *out_3144799740001374156) {
  F_fun(state,  dt, out_3144799740001374156);
}
void pose_h_4(double *state, double *unused, double *out_7170570279272954882) {
  h_4(state, unused, out_7170570279272954882);
}
void pose_H_4(double *state, double *unused, double *out_2301487118065795422) {
  H_4(state, unused, out_2301487118065795422);
}
void pose_h_10(double *state, double *unused, double *out_2811610427292929098) {
  h_10(state, unused, out_2811610427292929098);
}
void pose_H_10(double *state, double *unused, double *out_4485692655108419471) {
  H_10(state, unused, out_4485692655108419471);
}
void pose_h_13(double *state, double *unused, double *out_5723609330334209216) {
  h_13(state, unused, out_5723609330334209216);
}
void pose_H_13(double *state, double *unused, double *out_910786707266537379) {
  H_13(state, unused, out_910786707266537379);
}
void pose_h_14(double *state, double *unused, double *out_1904023991098828728) {
  h_14(state, unused, out_1904023991098828728);
}
void pose_H_14(double *state, double *unused, double *out_5384275550361167718) {
  H_14(state, unused, out_5384275550361167718);
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
