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
void err_fun(double *nom_x, double *delta_x, double *out_2591816007629674382) {
   out_2591816007629674382[0] = delta_x[0] + nom_x[0];
   out_2591816007629674382[1] = delta_x[1] + nom_x[1];
   out_2591816007629674382[2] = delta_x[2] + nom_x[2];
   out_2591816007629674382[3] = delta_x[3] + nom_x[3];
   out_2591816007629674382[4] = delta_x[4] + nom_x[4];
   out_2591816007629674382[5] = delta_x[5] + nom_x[5];
   out_2591816007629674382[6] = delta_x[6] + nom_x[6];
   out_2591816007629674382[7] = delta_x[7] + nom_x[7];
   out_2591816007629674382[8] = delta_x[8] + nom_x[8];
   out_2591816007629674382[9] = delta_x[9] + nom_x[9];
   out_2591816007629674382[10] = delta_x[10] + nom_x[10];
   out_2591816007629674382[11] = delta_x[11] + nom_x[11];
   out_2591816007629674382[12] = delta_x[12] + nom_x[12];
   out_2591816007629674382[13] = delta_x[13] + nom_x[13];
   out_2591816007629674382[14] = delta_x[14] + nom_x[14];
   out_2591816007629674382[15] = delta_x[15] + nom_x[15];
   out_2591816007629674382[16] = delta_x[16] + nom_x[16];
   out_2591816007629674382[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5111003568722884551) {
   out_5111003568722884551[0] = -nom_x[0] + true_x[0];
   out_5111003568722884551[1] = -nom_x[1] + true_x[1];
   out_5111003568722884551[2] = -nom_x[2] + true_x[2];
   out_5111003568722884551[3] = -nom_x[3] + true_x[3];
   out_5111003568722884551[4] = -nom_x[4] + true_x[4];
   out_5111003568722884551[5] = -nom_x[5] + true_x[5];
   out_5111003568722884551[6] = -nom_x[6] + true_x[6];
   out_5111003568722884551[7] = -nom_x[7] + true_x[7];
   out_5111003568722884551[8] = -nom_x[8] + true_x[8];
   out_5111003568722884551[9] = -nom_x[9] + true_x[9];
   out_5111003568722884551[10] = -nom_x[10] + true_x[10];
   out_5111003568722884551[11] = -nom_x[11] + true_x[11];
   out_5111003568722884551[12] = -nom_x[12] + true_x[12];
   out_5111003568722884551[13] = -nom_x[13] + true_x[13];
   out_5111003568722884551[14] = -nom_x[14] + true_x[14];
   out_5111003568722884551[15] = -nom_x[15] + true_x[15];
   out_5111003568722884551[16] = -nom_x[16] + true_x[16];
   out_5111003568722884551[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_5953397541332519964) {
   out_5953397541332519964[0] = 1.0;
   out_5953397541332519964[1] = 0.0;
   out_5953397541332519964[2] = 0.0;
   out_5953397541332519964[3] = 0.0;
   out_5953397541332519964[4] = 0.0;
   out_5953397541332519964[5] = 0.0;
   out_5953397541332519964[6] = 0.0;
   out_5953397541332519964[7] = 0.0;
   out_5953397541332519964[8] = 0.0;
   out_5953397541332519964[9] = 0.0;
   out_5953397541332519964[10] = 0.0;
   out_5953397541332519964[11] = 0.0;
   out_5953397541332519964[12] = 0.0;
   out_5953397541332519964[13] = 0.0;
   out_5953397541332519964[14] = 0.0;
   out_5953397541332519964[15] = 0.0;
   out_5953397541332519964[16] = 0.0;
   out_5953397541332519964[17] = 0.0;
   out_5953397541332519964[18] = 0.0;
   out_5953397541332519964[19] = 1.0;
   out_5953397541332519964[20] = 0.0;
   out_5953397541332519964[21] = 0.0;
   out_5953397541332519964[22] = 0.0;
   out_5953397541332519964[23] = 0.0;
   out_5953397541332519964[24] = 0.0;
   out_5953397541332519964[25] = 0.0;
   out_5953397541332519964[26] = 0.0;
   out_5953397541332519964[27] = 0.0;
   out_5953397541332519964[28] = 0.0;
   out_5953397541332519964[29] = 0.0;
   out_5953397541332519964[30] = 0.0;
   out_5953397541332519964[31] = 0.0;
   out_5953397541332519964[32] = 0.0;
   out_5953397541332519964[33] = 0.0;
   out_5953397541332519964[34] = 0.0;
   out_5953397541332519964[35] = 0.0;
   out_5953397541332519964[36] = 0.0;
   out_5953397541332519964[37] = 0.0;
   out_5953397541332519964[38] = 1.0;
   out_5953397541332519964[39] = 0.0;
   out_5953397541332519964[40] = 0.0;
   out_5953397541332519964[41] = 0.0;
   out_5953397541332519964[42] = 0.0;
   out_5953397541332519964[43] = 0.0;
   out_5953397541332519964[44] = 0.0;
   out_5953397541332519964[45] = 0.0;
   out_5953397541332519964[46] = 0.0;
   out_5953397541332519964[47] = 0.0;
   out_5953397541332519964[48] = 0.0;
   out_5953397541332519964[49] = 0.0;
   out_5953397541332519964[50] = 0.0;
   out_5953397541332519964[51] = 0.0;
   out_5953397541332519964[52] = 0.0;
   out_5953397541332519964[53] = 0.0;
   out_5953397541332519964[54] = 0.0;
   out_5953397541332519964[55] = 0.0;
   out_5953397541332519964[56] = 0.0;
   out_5953397541332519964[57] = 1.0;
   out_5953397541332519964[58] = 0.0;
   out_5953397541332519964[59] = 0.0;
   out_5953397541332519964[60] = 0.0;
   out_5953397541332519964[61] = 0.0;
   out_5953397541332519964[62] = 0.0;
   out_5953397541332519964[63] = 0.0;
   out_5953397541332519964[64] = 0.0;
   out_5953397541332519964[65] = 0.0;
   out_5953397541332519964[66] = 0.0;
   out_5953397541332519964[67] = 0.0;
   out_5953397541332519964[68] = 0.0;
   out_5953397541332519964[69] = 0.0;
   out_5953397541332519964[70] = 0.0;
   out_5953397541332519964[71] = 0.0;
   out_5953397541332519964[72] = 0.0;
   out_5953397541332519964[73] = 0.0;
   out_5953397541332519964[74] = 0.0;
   out_5953397541332519964[75] = 0.0;
   out_5953397541332519964[76] = 1.0;
   out_5953397541332519964[77] = 0.0;
   out_5953397541332519964[78] = 0.0;
   out_5953397541332519964[79] = 0.0;
   out_5953397541332519964[80] = 0.0;
   out_5953397541332519964[81] = 0.0;
   out_5953397541332519964[82] = 0.0;
   out_5953397541332519964[83] = 0.0;
   out_5953397541332519964[84] = 0.0;
   out_5953397541332519964[85] = 0.0;
   out_5953397541332519964[86] = 0.0;
   out_5953397541332519964[87] = 0.0;
   out_5953397541332519964[88] = 0.0;
   out_5953397541332519964[89] = 0.0;
   out_5953397541332519964[90] = 0.0;
   out_5953397541332519964[91] = 0.0;
   out_5953397541332519964[92] = 0.0;
   out_5953397541332519964[93] = 0.0;
   out_5953397541332519964[94] = 0.0;
   out_5953397541332519964[95] = 1.0;
   out_5953397541332519964[96] = 0.0;
   out_5953397541332519964[97] = 0.0;
   out_5953397541332519964[98] = 0.0;
   out_5953397541332519964[99] = 0.0;
   out_5953397541332519964[100] = 0.0;
   out_5953397541332519964[101] = 0.0;
   out_5953397541332519964[102] = 0.0;
   out_5953397541332519964[103] = 0.0;
   out_5953397541332519964[104] = 0.0;
   out_5953397541332519964[105] = 0.0;
   out_5953397541332519964[106] = 0.0;
   out_5953397541332519964[107] = 0.0;
   out_5953397541332519964[108] = 0.0;
   out_5953397541332519964[109] = 0.0;
   out_5953397541332519964[110] = 0.0;
   out_5953397541332519964[111] = 0.0;
   out_5953397541332519964[112] = 0.0;
   out_5953397541332519964[113] = 0.0;
   out_5953397541332519964[114] = 1.0;
   out_5953397541332519964[115] = 0.0;
   out_5953397541332519964[116] = 0.0;
   out_5953397541332519964[117] = 0.0;
   out_5953397541332519964[118] = 0.0;
   out_5953397541332519964[119] = 0.0;
   out_5953397541332519964[120] = 0.0;
   out_5953397541332519964[121] = 0.0;
   out_5953397541332519964[122] = 0.0;
   out_5953397541332519964[123] = 0.0;
   out_5953397541332519964[124] = 0.0;
   out_5953397541332519964[125] = 0.0;
   out_5953397541332519964[126] = 0.0;
   out_5953397541332519964[127] = 0.0;
   out_5953397541332519964[128] = 0.0;
   out_5953397541332519964[129] = 0.0;
   out_5953397541332519964[130] = 0.0;
   out_5953397541332519964[131] = 0.0;
   out_5953397541332519964[132] = 0.0;
   out_5953397541332519964[133] = 1.0;
   out_5953397541332519964[134] = 0.0;
   out_5953397541332519964[135] = 0.0;
   out_5953397541332519964[136] = 0.0;
   out_5953397541332519964[137] = 0.0;
   out_5953397541332519964[138] = 0.0;
   out_5953397541332519964[139] = 0.0;
   out_5953397541332519964[140] = 0.0;
   out_5953397541332519964[141] = 0.0;
   out_5953397541332519964[142] = 0.0;
   out_5953397541332519964[143] = 0.0;
   out_5953397541332519964[144] = 0.0;
   out_5953397541332519964[145] = 0.0;
   out_5953397541332519964[146] = 0.0;
   out_5953397541332519964[147] = 0.0;
   out_5953397541332519964[148] = 0.0;
   out_5953397541332519964[149] = 0.0;
   out_5953397541332519964[150] = 0.0;
   out_5953397541332519964[151] = 0.0;
   out_5953397541332519964[152] = 1.0;
   out_5953397541332519964[153] = 0.0;
   out_5953397541332519964[154] = 0.0;
   out_5953397541332519964[155] = 0.0;
   out_5953397541332519964[156] = 0.0;
   out_5953397541332519964[157] = 0.0;
   out_5953397541332519964[158] = 0.0;
   out_5953397541332519964[159] = 0.0;
   out_5953397541332519964[160] = 0.0;
   out_5953397541332519964[161] = 0.0;
   out_5953397541332519964[162] = 0.0;
   out_5953397541332519964[163] = 0.0;
   out_5953397541332519964[164] = 0.0;
   out_5953397541332519964[165] = 0.0;
   out_5953397541332519964[166] = 0.0;
   out_5953397541332519964[167] = 0.0;
   out_5953397541332519964[168] = 0.0;
   out_5953397541332519964[169] = 0.0;
   out_5953397541332519964[170] = 0.0;
   out_5953397541332519964[171] = 1.0;
   out_5953397541332519964[172] = 0.0;
   out_5953397541332519964[173] = 0.0;
   out_5953397541332519964[174] = 0.0;
   out_5953397541332519964[175] = 0.0;
   out_5953397541332519964[176] = 0.0;
   out_5953397541332519964[177] = 0.0;
   out_5953397541332519964[178] = 0.0;
   out_5953397541332519964[179] = 0.0;
   out_5953397541332519964[180] = 0.0;
   out_5953397541332519964[181] = 0.0;
   out_5953397541332519964[182] = 0.0;
   out_5953397541332519964[183] = 0.0;
   out_5953397541332519964[184] = 0.0;
   out_5953397541332519964[185] = 0.0;
   out_5953397541332519964[186] = 0.0;
   out_5953397541332519964[187] = 0.0;
   out_5953397541332519964[188] = 0.0;
   out_5953397541332519964[189] = 0.0;
   out_5953397541332519964[190] = 1.0;
   out_5953397541332519964[191] = 0.0;
   out_5953397541332519964[192] = 0.0;
   out_5953397541332519964[193] = 0.0;
   out_5953397541332519964[194] = 0.0;
   out_5953397541332519964[195] = 0.0;
   out_5953397541332519964[196] = 0.0;
   out_5953397541332519964[197] = 0.0;
   out_5953397541332519964[198] = 0.0;
   out_5953397541332519964[199] = 0.0;
   out_5953397541332519964[200] = 0.0;
   out_5953397541332519964[201] = 0.0;
   out_5953397541332519964[202] = 0.0;
   out_5953397541332519964[203] = 0.0;
   out_5953397541332519964[204] = 0.0;
   out_5953397541332519964[205] = 0.0;
   out_5953397541332519964[206] = 0.0;
   out_5953397541332519964[207] = 0.0;
   out_5953397541332519964[208] = 0.0;
   out_5953397541332519964[209] = 1.0;
   out_5953397541332519964[210] = 0.0;
   out_5953397541332519964[211] = 0.0;
   out_5953397541332519964[212] = 0.0;
   out_5953397541332519964[213] = 0.0;
   out_5953397541332519964[214] = 0.0;
   out_5953397541332519964[215] = 0.0;
   out_5953397541332519964[216] = 0.0;
   out_5953397541332519964[217] = 0.0;
   out_5953397541332519964[218] = 0.0;
   out_5953397541332519964[219] = 0.0;
   out_5953397541332519964[220] = 0.0;
   out_5953397541332519964[221] = 0.0;
   out_5953397541332519964[222] = 0.0;
   out_5953397541332519964[223] = 0.0;
   out_5953397541332519964[224] = 0.0;
   out_5953397541332519964[225] = 0.0;
   out_5953397541332519964[226] = 0.0;
   out_5953397541332519964[227] = 0.0;
   out_5953397541332519964[228] = 1.0;
   out_5953397541332519964[229] = 0.0;
   out_5953397541332519964[230] = 0.0;
   out_5953397541332519964[231] = 0.0;
   out_5953397541332519964[232] = 0.0;
   out_5953397541332519964[233] = 0.0;
   out_5953397541332519964[234] = 0.0;
   out_5953397541332519964[235] = 0.0;
   out_5953397541332519964[236] = 0.0;
   out_5953397541332519964[237] = 0.0;
   out_5953397541332519964[238] = 0.0;
   out_5953397541332519964[239] = 0.0;
   out_5953397541332519964[240] = 0.0;
   out_5953397541332519964[241] = 0.0;
   out_5953397541332519964[242] = 0.0;
   out_5953397541332519964[243] = 0.0;
   out_5953397541332519964[244] = 0.0;
   out_5953397541332519964[245] = 0.0;
   out_5953397541332519964[246] = 0.0;
   out_5953397541332519964[247] = 1.0;
   out_5953397541332519964[248] = 0.0;
   out_5953397541332519964[249] = 0.0;
   out_5953397541332519964[250] = 0.0;
   out_5953397541332519964[251] = 0.0;
   out_5953397541332519964[252] = 0.0;
   out_5953397541332519964[253] = 0.0;
   out_5953397541332519964[254] = 0.0;
   out_5953397541332519964[255] = 0.0;
   out_5953397541332519964[256] = 0.0;
   out_5953397541332519964[257] = 0.0;
   out_5953397541332519964[258] = 0.0;
   out_5953397541332519964[259] = 0.0;
   out_5953397541332519964[260] = 0.0;
   out_5953397541332519964[261] = 0.0;
   out_5953397541332519964[262] = 0.0;
   out_5953397541332519964[263] = 0.0;
   out_5953397541332519964[264] = 0.0;
   out_5953397541332519964[265] = 0.0;
   out_5953397541332519964[266] = 1.0;
   out_5953397541332519964[267] = 0.0;
   out_5953397541332519964[268] = 0.0;
   out_5953397541332519964[269] = 0.0;
   out_5953397541332519964[270] = 0.0;
   out_5953397541332519964[271] = 0.0;
   out_5953397541332519964[272] = 0.0;
   out_5953397541332519964[273] = 0.0;
   out_5953397541332519964[274] = 0.0;
   out_5953397541332519964[275] = 0.0;
   out_5953397541332519964[276] = 0.0;
   out_5953397541332519964[277] = 0.0;
   out_5953397541332519964[278] = 0.0;
   out_5953397541332519964[279] = 0.0;
   out_5953397541332519964[280] = 0.0;
   out_5953397541332519964[281] = 0.0;
   out_5953397541332519964[282] = 0.0;
   out_5953397541332519964[283] = 0.0;
   out_5953397541332519964[284] = 0.0;
   out_5953397541332519964[285] = 1.0;
   out_5953397541332519964[286] = 0.0;
   out_5953397541332519964[287] = 0.0;
   out_5953397541332519964[288] = 0.0;
   out_5953397541332519964[289] = 0.0;
   out_5953397541332519964[290] = 0.0;
   out_5953397541332519964[291] = 0.0;
   out_5953397541332519964[292] = 0.0;
   out_5953397541332519964[293] = 0.0;
   out_5953397541332519964[294] = 0.0;
   out_5953397541332519964[295] = 0.0;
   out_5953397541332519964[296] = 0.0;
   out_5953397541332519964[297] = 0.0;
   out_5953397541332519964[298] = 0.0;
   out_5953397541332519964[299] = 0.0;
   out_5953397541332519964[300] = 0.0;
   out_5953397541332519964[301] = 0.0;
   out_5953397541332519964[302] = 0.0;
   out_5953397541332519964[303] = 0.0;
   out_5953397541332519964[304] = 1.0;
   out_5953397541332519964[305] = 0.0;
   out_5953397541332519964[306] = 0.0;
   out_5953397541332519964[307] = 0.0;
   out_5953397541332519964[308] = 0.0;
   out_5953397541332519964[309] = 0.0;
   out_5953397541332519964[310] = 0.0;
   out_5953397541332519964[311] = 0.0;
   out_5953397541332519964[312] = 0.0;
   out_5953397541332519964[313] = 0.0;
   out_5953397541332519964[314] = 0.0;
   out_5953397541332519964[315] = 0.0;
   out_5953397541332519964[316] = 0.0;
   out_5953397541332519964[317] = 0.0;
   out_5953397541332519964[318] = 0.0;
   out_5953397541332519964[319] = 0.0;
   out_5953397541332519964[320] = 0.0;
   out_5953397541332519964[321] = 0.0;
   out_5953397541332519964[322] = 0.0;
   out_5953397541332519964[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_754329157820044725) {
   out_754329157820044725[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_754329157820044725[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_754329157820044725[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_754329157820044725[3] = dt*state[12] + state[3];
   out_754329157820044725[4] = dt*state[13] + state[4];
   out_754329157820044725[5] = dt*state[14] + state[5];
   out_754329157820044725[6] = state[6];
   out_754329157820044725[7] = state[7];
   out_754329157820044725[8] = state[8];
   out_754329157820044725[9] = state[9];
   out_754329157820044725[10] = state[10];
   out_754329157820044725[11] = state[11];
   out_754329157820044725[12] = state[12];
   out_754329157820044725[13] = state[13];
   out_754329157820044725[14] = state[14];
   out_754329157820044725[15] = state[15];
   out_754329157820044725[16] = state[16];
   out_754329157820044725[17] = state[17];
}
void F_fun(double *state, double dt, double *out_6133369954690992745) {
   out_6133369954690992745[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6133369954690992745[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6133369954690992745[2] = 0;
   out_6133369954690992745[3] = 0;
   out_6133369954690992745[4] = 0;
   out_6133369954690992745[5] = 0;
   out_6133369954690992745[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6133369954690992745[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6133369954690992745[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6133369954690992745[9] = 0;
   out_6133369954690992745[10] = 0;
   out_6133369954690992745[11] = 0;
   out_6133369954690992745[12] = 0;
   out_6133369954690992745[13] = 0;
   out_6133369954690992745[14] = 0;
   out_6133369954690992745[15] = 0;
   out_6133369954690992745[16] = 0;
   out_6133369954690992745[17] = 0;
   out_6133369954690992745[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6133369954690992745[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6133369954690992745[20] = 0;
   out_6133369954690992745[21] = 0;
   out_6133369954690992745[22] = 0;
   out_6133369954690992745[23] = 0;
   out_6133369954690992745[24] = 0;
   out_6133369954690992745[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6133369954690992745[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6133369954690992745[27] = 0;
   out_6133369954690992745[28] = 0;
   out_6133369954690992745[29] = 0;
   out_6133369954690992745[30] = 0;
   out_6133369954690992745[31] = 0;
   out_6133369954690992745[32] = 0;
   out_6133369954690992745[33] = 0;
   out_6133369954690992745[34] = 0;
   out_6133369954690992745[35] = 0;
   out_6133369954690992745[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6133369954690992745[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6133369954690992745[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6133369954690992745[39] = 0;
   out_6133369954690992745[40] = 0;
   out_6133369954690992745[41] = 0;
   out_6133369954690992745[42] = 0;
   out_6133369954690992745[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6133369954690992745[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6133369954690992745[45] = 0;
   out_6133369954690992745[46] = 0;
   out_6133369954690992745[47] = 0;
   out_6133369954690992745[48] = 0;
   out_6133369954690992745[49] = 0;
   out_6133369954690992745[50] = 0;
   out_6133369954690992745[51] = 0;
   out_6133369954690992745[52] = 0;
   out_6133369954690992745[53] = 0;
   out_6133369954690992745[54] = 0;
   out_6133369954690992745[55] = 0;
   out_6133369954690992745[56] = 0;
   out_6133369954690992745[57] = 1;
   out_6133369954690992745[58] = 0;
   out_6133369954690992745[59] = 0;
   out_6133369954690992745[60] = 0;
   out_6133369954690992745[61] = 0;
   out_6133369954690992745[62] = 0;
   out_6133369954690992745[63] = 0;
   out_6133369954690992745[64] = 0;
   out_6133369954690992745[65] = 0;
   out_6133369954690992745[66] = dt;
   out_6133369954690992745[67] = 0;
   out_6133369954690992745[68] = 0;
   out_6133369954690992745[69] = 0;
   out_6133369954690992745[70] = 0;
   out_6133369954690992745[71] = 0;
   out_6133369954690992745[72] = 0;
   out_6133369954690992745[73] = 0;
   out_6133369954690992745[74] = 0;
   out_6133369954690992745[75] = 0;
   out_6133369954690992745[76] = 1;
   out_6133369954690992745[77] = 0;
   out_6133369954690992745[78] = 0;
   out_6133369954690992745[79] = 0;
   out_6133369954690992745[80] = 0;
   out_6133369954690992745[81] = 0;
   out_6133369954690992745[82] = 0;
   out_6133369954690992745[83] = 0;
   out_6133369954690992745[84] = 0;
   out_6133369954690992745[85] = dt;
   out_6133369954690992745[86] = 0;
   out_6133369954690992745[87] = 0;
   out_6133369954690992745[88] = 0;
   out_6133369954690992745[89] = 0;
   out_6133369954690992745[90] = 0;
   out_6133369954690992745[91] = 0;
   out_6133369954690992745[92] = 0;
   out_6133369954690992745[93] = 0;
   out_6133369954690992745[94] = 0;
   out_6133369954690992745[95] = 1;
   out_6133369954690992745[96] = 0;
   out_6133369954690992745[97] = 0;
   out_6133369954690992745[98] = 0;
   out_6133369954690992745[99] = 0;
   out_6133369954690992745[100] = 0;
   out_6133369954690992745[101] = 0;
   out_6133369954690992745[102] = 0;
   out_6133369954690992745[103] = 0;
   out_6133369954690992745[104] = dt;
   out_6133369954690992745[105] = 0;
   out_6133369954690992745[106] = 0;
   out_6133369954690992745[107] = 0;
   out_6133369954690992745[108] = 0;
   out_6133369954690992745[109] = 0;
   out_6133369954690992745[110] = 0;
   out_6133369954690992745[111] = 0;
   out_6133369954690992745[112] = 0;
   out_6133369954690992745[113] = 0;
   out_6133369954690992745[114] = 1;
   out_6133369954690992745[115] = 0;
   out_6133369954690992745[116] = 0;
   out_6133369954690992745[117] = 0;
   out_6133369954690992745[118] = 0;
   out_6133369954690992745[119] = 0;
   out_6133369954690992745[120] = 0;
   out_6133369954690992745[121] = 0;
   out_6133369954690992745[122] = 0;
   out_6133369954690992745[123] = 0;
   out_6133369954690992745[124] = 0;
   out_6133369954690992745[125] = 0;
   out_6133369954690992745[126] = 0;
   out_6133369954690992745[127] = 0;
   out_6133369954690992745[128] = 0;
   out_6133369954690992745[129] = 0;
   out_6133369954690992745[130] = 0;
   out_6133369954690992745[131] = 0;
   out_6133369954690992745[132] = 0;
   out_6133369954690992745[133] = 1;
   out_6133369954690992745[134] = 0;
   out_6133369954690992745[135] = 0;
   out_6133369954690992745[136] = 0;
   out_6133369954690992745[137] = 0;
   out_6133369954690992745[138] = 0;
   out_6133369954690992745[139] = 0;
   out_6133369954690992745[140] = 0;
   out_6133369954690992745[141] = 0;
   out_6133369954690992745[142] = 0;
   out_6133369954690992745[143] = 0;
   out_6133369954690992745[144] = 0;
   out_6133369954690992745[145] = 0;
   out_6133369954690992745[146] = 0;
   out_6133369954690992745[147] = 0;
   out_6133369954690992745[148] = 0;
   out_6133369954690992745[149] = 0;
   out_6133369954690992745[150] = 0;
   out_6133369954690992745[151] = 0;
   out_6133369954690992745[152] = 1;
   out_6133369954690992745[153] = 0;
   out_6133369954690992745[154] = 0;
   out_6133369954690992745[155] = 0;
   out_6133369954690992745[156] = 0;
   out_6133369954690992745[157] = 0;
   out_6133369954690992745[158] = 0;
   out_6133369954690992745[159] = 0;
   out_6133369954690992745[160] = 0;
   out_6133369954690992745[161] = 0;
   out_6133369954690992745[162] = 0;
   out_6133369954690992745[163] = 0;
   out_6133369954690992745[164] = 0;
   out_6133369954690992745[165] = 0;
   out_6133369954690992745[166] = 0;
   out_6133369954690992745[167] = 0;
   out_6133369954690992745[168] = 0;
   out_6133369954690992745[169] = 0;
   out_6133369954690992745[170] = 0;
   out_6133369954690992745[171] = 1;
   out_6133369954690992745[172] = 0;
   out_6133369954690992745[173] = 0;
   out_6133369954690992745[174] = 0;
   out_6133369954690992745[175] = 0;
   out_6133369954690992745[176] = 0;
   out_6133369954690992745[177] = 0;
   out_6133369954690992745[178] = 0;
   out_6133369954690992745[179] = 0;
   out_6133369954690992745[180] = 0;
   out_6133369954690992745[181] = 0;
   out_6133369954690992745[182] = 0;
   out_6133369954690992745[183] = 0;
   out_6133369954690992745[184] = 0;
   out_6133369954690992745[185] = 0;
   out_6133369954690992745[186] = 0;
   out_6133369954690992745[187] = 0;
   out_6133369954690992745[188] = 0;
   out_6133369954690992745[189] = 0;
   out_6133369954690992745[190] = 1;
   out_6133369954690992745[191] = 0;
   out_6133369954690992745[192] = 0;
   out_6133369954690992745[193] = 0;
   out_6133369954690992745[194] = 0;
   out_6133369954690992745[195] = 0;
   out_6133369954690992745[196] = 0;
   out_6133369954690992745[197] = 0;
   out_6133369954690992745[198] = 0;
   out_6133369954690992745[199] = 0;
   out_6133369954690992745[200] = 0;
   out_6133369954690992745[201] = 0;
   out_6133369954690992745[202] = 0;
   out_6133369954690992745[203] = 0;
   out_6133369954690992745[204] = 0;
   out_6133369954690992745[205] = 0;
   out_6133369954690992745[206] = 0;
   out_6133369954690992745[207] = 0;
   out_6133369954690992745[208] = 0;
   out_6133369954690992745[209] = 1;
   out_6133369954690992745[210] = 0;
   out_6133369954690992745[211] = 0;
   out_6133369954690992745[212] = 0;
   out_6133369954690992745[213] = 0;
   out_6133369954690992745[214] = 0;
   out_6133369954690992745[215] = 0;
   out_6133369954690992745[216] = 0;
   out_6133369954690992745[217] = 0;
   out_6133369954690992745[218] = 0;
   out_6133369954690992745[219] = 0;
   out_6133369954690992745[220] = 0;
   out_6133369954690992745[221] = 0;
   out_6133369954690992745[222] = 0;
   out_6133369954690992745[223] = 0;
   out_6133369954690992745[224] = 0;
   out_6133369954690992745[225] = 0;
   out_6133369954690992745[226] = 0;
   out_6133369954690992745[227] = 0;
   out_6133369954690992745[228] = 1;
   out_6133369954690992745[229] = 0;
   out_6133369954690992745[230] = 0;
   out_6133369954690992745[231] = 0;
   out_6133369954690992745[232] = 0;
   out_6133369954690992745[233] = 0;
   out_6133369954690992745[234] = 0;
   out_6133369954690992745[235] = 0;
   out_6133369954690992745[236] = 0;
   out_6133369954690992745[237] = 0;
   out_6133369954690992745[238] = 0;
   out_6133369954690992745[239] = 0;
   out_6133369954690992745[240] = 0;
   out_6133369954690992745[241] = 0;
   out_6133369954690992745[242] = 0;
   out_6133369954690992745[243] = 0;
   out_6133369954690992745[244] = 0;
   out_6133369954690992745[245] = 0;
   out_6133369954690992745[246] = 0;
   out_6133369954690992745[247] = 1;
   out_6133369954690992745[248] = 0;
   out_6133369954690992745[249] = 0;
   out_6133369954690992745[250] = 0;
   out_6133369954690992745[251] = 0;
   out_6133369954690992745[252] = 0;
   out_6133369954690992745[253] = 0;
   out_6133369954690992745[254] = 0;
   out_6133369954690992745[255] = 0;
   out_6133369954690992745[256] = 0;
   out_6133369954690992745[257] = 0;
   out_6133369954690992745[258] = 0;
   out_6133369954690992745[259] = 0;
   out_6133369954690992745[260] = 0;
   out_6133369954690992745[261] = 0;
   out_6133369954690992745[262] = 0;
   out_6133369954690992745[263] = 0;
   out_6133369954690992745[264] = 0;
   out_6133369954690992745[265] = 0;
   out_6133369954690992745[266] = 1;
   out_6133369954690992745[267] = 0;
   out_6133369954690992745[268] = 0;
   out_6133369954690992745[269] = 0;
   out_6133369954690992745[270] = 0;
   out_6133369954690992745[271] = 0;
   out_6133369954690992745[272] = 0;
   out_6133369954690992745[273] = 0;
   out_6133369954690992745[274] = 0;
   out_6133369954690992745[275] = 0;
   out_6133369954690992745[276] = 0;
   out_6133369954690992745[277] = 0;
   out_6133369954690992745[278] = 0;
   out_6133369954690992745[279] = 0;
   out_6133369954690992745[280] = 0;
   out_6133369954690992745[281] = 0;
   out_6133369954690992745[282] = 0;
   out_6133369954690992745[283] = 0;
   out_6133369954690992745[284] = 0;
   out_6133369954690992745[285] = 1;
   out_6133369954690992745[286] = 0;
   out_6133369954690992745[287] = 0;
   out_6133369954690992745[288] = 0;
   out_6133369954690992745[289] = 0;
   out_6133369954690992745[290] = 0;
   out_6133369954690992745[291] = 0;
   out_6133369954690992745[292] = 0;
   out_6133369954690992745[293] = 0;
   out_6133369954690992745[294] = 0;
   out_6133369954690992745[295] = 0;
   out_6133369954690992745[296] = 0;
   out_6133369954690992745[297] = 0;
   out_6133369954690992745[298] = 0;
   out_6133369954690992745[299] = 0;
   out_6133369954690992745[300] = 0;
   out_6133369954690992745[301] = 0;
   out_6133369954690992745[302] = 0;
   out_6133369954690992745[303] = 0;
   out_6133369954690992745[304] = 1;
   out_6133369954690992745[305] = 0;
   out_6133369954690992745[306] = 0;
   out_6133369954690992745[307] = 0;
   out_6133369954690992745[308] = 0;
   out_6133369954690992745[309] = 0;
   out_6133369954690992745[310] = 0;
   out_6133369954690992745[311] = 0;
   out_6133369954690992745[312] = 0;
   out_6133369954690992745[313] = 0;
   out_6133369954690992745[314] = 0;
   out_6133369954690992745[315] = 0;
   out_6133369954690992745[316] = 0;
   out_6133369954690992745[317] = 0;
   out_6133369954690992745[318] = 0;
   out_6133369954690992745[319] = 0;
   out_6133369954690992745[320] = 0;
   out_6133369954690992745[321] = 0;
   out_6133369954690992745[322] = 0;
   out_6133369954690992745[323] = 1;
}
void h_4(double *state, double *unused, double *out_516041222348960560) {
   out_516041222348960560[0] = state[6] + state[9];
   out_516041222348960560[1] = state[7] + state[10];
   out_516041222348960560[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_1338770504403203600) {
   out_1338770504403203600[0] = 0;
   out_1338770504403203600[1] = 0;
   out_1338770504403203600[2] = 0;
   out_1338770504403203600[3] = 0;
   out_1338770504403203600[4] = 0;
   out_1338770504403203600[5] = 0;
   out_1338770504403203600[6] = 1;
   out_1338770504403203600[7] = 0;
   out_1338770504403203600[8] = 0;
   out_1338770504403203600[9] = 1;
   out_1338770504403203600[10] = 0;
   out_1338770504403203600[11] = 0;
   out_1338770504403203600[12] = 0;
   out_1338770504403203600[13] = 0;
   out_1338770504403203600[14] = 0;
   out_1338770504403203600[15] = 0;
   out_1338770504403203600[16] = 0;
   out_1338770504403203600[17] = 0;
   out_1338770504403203600[18] = 0;
   out_1338770504403203600[19] = 0;
   out_1338770504403203600[20] = 0;
   out_1338770504403203600[21] = 0;
   out_1338770504403203600[22] = 0;
   out_1338770504403203600[23] = 0;
   out_1338770504403203600[24] = 0;
   out_1338770504403203600[25] = 1;
   out_1338770504403203600[26] = 0;
   out_1338770504403203600[27] = 0;
   out_1338770504403203600[28] = 1;
   out_1338770504403203600[29] = 0;
   out_1338770504403203600[30] = 0;
   out_1338770504403203600[31] = 0;
   out_1338770504403203600[32] = 0;
   out_1338770504403203600[33] = 0;
   out_1338770504403203600[34] = 0;
   out_1338770504403203600[35] = 0;
   out_1338770504403203600[36] = 0;
   out_1338770504403203600[37] = 0;
   out_1338770504403203600[38] = 0;
   out_1338770504403203600[39] = 0;
   out_1338770504403203600[40] = 0;
   out_1338770504403203600[41] = 0;
   out_1338770504403203600[42] = 0;
   out_1338770504403203600[43] = 0;
   out_1338770504403203600[44] = 1;
   out_1338770504403203600[45] = 0;
   out_1338770504403203600[46] = 0;
   out_1338770504403203600[47] = 1;
   out_1338770504403203600[48] = 0;
   out_1338770504403203600[49] = 0;
   out_1338770504403203600[50] = 0;
   out_1338770504403203600[51] = 0;
   out_1338770504403203600[52] = 0;
   out_1338770504403203600[53] = 0;
}
void h_10(double *state, double *unused, double *out_2447986843515870103) {
   out_2447986843515870103[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_2447986843515870103[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_2447986843515870103[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_7155285139208376669) {
   out_7155285139208376669[0] = 0;
   out_7155285139208376669[1] = 9.8100000000000005*cos(state[1]);
   out_7155285139208376669[2] = 0;
   out_7155285139208376669[3] = 0;
   out_7155285139208376669[4] = -state[8];
   out_7155285139208376669[5] = state[7];
   out_7155285139208376669[6] = 0;
   out_7155285139208376669[7] = state[5];
   out_7155285139208376669[8] = -state[4];
   out_7155285139208376669[9] = 0;
   out_7155285139208376669[10] = 0;
   out_7155285139208376669[11] = 0;
   out_7155285139208376669[12] = 1;
   out_7155285139208376669[13] = 0;
   out_7155285139208376669[14] = 0;
   out_7155285139208376669[15] = 1;
   out_7155285139208376669[16] = 0;
   out_7155285139208376669[17] = 0;
   out_7155285139208376669[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_7155285139208376669[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_7155285139208376669[20] = 0;
   out_7155285139208376669[21] = state[8];
   out_7155285139208376669[22] = 0;
   out_7155285139208376669[23] = -state[6];
   out_7155285139208376669[24] = -state[5];
   out_7155285139208376669[25] = 0;
   out_7155285139208376669[26] = state[3];
   out_7155285139208376669[27] = 0;
   out_7155285139208376669[28] = 0;
   out_7155285139208376669[29] = 0;
   out_7155285139208376669[30] = 0;
   out_7155285139208376669[31] = 1;
   out_7155285139208376669[32] = 0;
   out_7155285139208376669[33] = 0;
   out_7155285139208376669[34] = 1;
   out_7155285139208376669[35] = 0;
   out_7155285139208376669[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_7155285139208376669[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_7155285139208376669[38] = 0;
   out_7155285139208376669[39] = -state[7];
   out_7155285139208376669[40] = state[6];
   out_7155285139208376669[41] = 0;
   out_7155285139208376669[42] = state[4];
   out_7155285139208376669[43] = -state[3];
   out_7155285139208376669[44] = 0;
   out_7155285139208376669[45] = 0;
   out_7155285139208376669[46] = 0;
   out_7155285139208376669[47] = 0;
   out_7155285139208376669[48] = 0;
   out_7155285139208376669[49] = 0;
   out_7155285139208376669[50] = 1;
   out_7155285139208376669[51] = 0;
   out_7155285139208376669[52] = 0;
   out_7155285139208376669[53] = 1;
}
void h_13(double *state, double *unused, double *out_4078955435366114031) {
   out_4078955435366114031[0] = state[3];
   out_4078955435366114031[1] = state[4];
   out_4078955435366114031[2] = state[5];
}
void H_13(double *state, double *unused, double *out_1873503320929129201) {
   out_1873503320929129201[0] = 0;
   out_1873503320929129201[1] = 0;
   out_1873503320929129201[2] = 0;
   out_1873503320929129201[3] = 1;
   out_1873503320929129201[4] = 0;
   out_1873503320929129201[5] = 0;
   out_1873503320929129201[6] = 0;
   out_1873503320929129201[7] = 0;
   out_1873503320929129201[8] = 0;
   out_1873503320929129201[9] = 0;
   out_1873503320929129201[10] = 0;
   out_1873503320929129201[11] = 0;
   out_1873503320929129201[12] = 0;
   out_1873503320929129201[13] = 0;
   out_1873503320929129201[14] = 0;
   out_1873503320929129201[15] = 0;
   out_1873503320929129201[16] = 0;
   out_1873503320929129201[17] = 0;
   out_1873503320929129201[18] = 0;
   out_1873503320929129201[19] = 0;
   out_1873503320929129201[20] = 0;
   out_1873503320929129201[21] = 0;
   out_1873503320929129201[22] = 1;
   out_1873503320929129201[23] = 0;
   out_1873503320929129201[24] = 0;
   out_1873503320929129201[25] = 0;
   out_1873503320929129201[26] = 0;
   out_1873503320929129201[27] = 0;
   out_1873503320929129201[28] = 0;
   out_1873503320929129201[29] = 0;
   out_1873503320929129201[30] = 0;
   out_1873503320929129201[31] = 0;
   out_1873503320929129201[32] = 0;
   out_1873503320929129201[33] = 0;
   out_1873503320929129201[34] = 0;
   out_1873503320929129201[35] = 0;
   out_1873503320929129201[36] = 0;
   out_1873503320929129201[37] = 0;
   out_1873503320929129201[38] = 0;
   out_1873503320929129201[39] = 0;
   out_1873503320929129201[40] = 0;
   out_1873503320929129201[41] = 1;
   out_1873503320929129201[42] = 0;
   out_1873503320929129201[43] = 0;
   out_1873503320929129201[44] = 0;
   out_1873503320929129201[45] = 0;
   out_1873503320929129201[46] = 0;
   out_1873503320929129201[47] = 0;
   out_1873503320929129201[48] = 0;
   out_1873503320929129201[49] = 0;
   out_1873503320929129201[50] = 0;
   out_1873503320929129201[51] = 0;
   out_1873503320929129201[52] = 0;
   out_1873503320929129201[53] = 0;
}
void h_14(double *state, double *unused, double *out_8824687956191096942) {
   out_8824687956191096942[0] = state[6];
   out_8824687956191096942[1] = state[7];
   out_8824687956191096942[2] = state[8];
}
void H_14(double *state, double *unused, double *out_2624470351936280929) {
   out_2624470351936280929[0] = 0;
   out_2624470351936280929[1] = 0;
   out_2624470351936280929[2] = 0;
   out_2624470351936280929[3] = 0;
   out_2624470351936280929[4] = 0;
   out_2624470351936280929[5] = 0;
   out_2624470351936280929[6] = 1;
   out_2624470351936280929[7] = 0;
   out_2624470351936280929[8] = 0;
   out_2624470351936280929[9] = 0;
   out_2624470351936280929[10] = 0;
   out_2624470351936280929[11] = 0;
   out_2624470351936280929[12] = 0;
   out_2624470351936280929[13] = 0;
   out_2624470351936280929[14] = 0;
   out_2624470351936280929[15] = 0;
   out_2624470351936280929[16] = 0;
   out_2624470351936280929[17] = 0;
   out_2624470351936280929[18] = 0;
   out_2624470351936280929[19] = 0;
   out_2624470351936280929[20] = 0;
   out_2624470351936280929[21] = 0;
   out_2624470351936280929[22] = 0;
   out_2624470351936280929[23] = 0;
   out_2624470351936280929[24] = 0;
   out_2624470351936280929[25] = 1;
   out_2624470351936280929[26] = 0;
   out_2624470351936280929[27] = 0;
   out_2624470351936280929[28] = 0;
   out_2624470351936280929[29] = 0;
   out_2624470351936280929[30] = 0;
   out_2624470351936280929[31] = 0;
   out_2624470351936280929[32] = 0;
   out_2624470351936280929[33] = 0;
   out_2624470351936280929[34] = 0;
   out_2624470351936280929[35] = 0;
   out_2624470351936280929[36] = 0;
   out_2624470351936280929[37] = 0;
   out_2624470351936280929[38] = 0;
   out_2624470351936280929[39] = 0;
   out_2624470351936280929[40] = 0;
   out_2624470351936280929[41] = 0;
   out_2624470351936280929[42] = 0;
   out_2624470351936280929[43] = 0;
   out_2624470351936280929[44] = 1;
   out_2624470351936280929[45] = 0;
   out_2624470351936280929[46] = 0;
   out_2624470351936280929[47] = 0;
   out_2624470351936280929[48] = 0;
   out_2624470351936280929[49] = 0;
   out_2624470351936280929[50] = 0;
   out_2624470351936280929[51] = 0;
   out_2624470351936280929[52] = 0;
   out_2624470351936280929[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_2591816007629674382) {
  err_fun(nom_x, delta_x, out_2591816007629674382);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5111003568722884551) {
  inv_err_fun(nom_x, true_x, out_5111003568722884551);
}
void pose_H_mod_fun(double *state, double *out_5953397541332519964) {
  H_mod_fun(state, out_5953397541332519964);
}
void pose_f_fun(double *state, double dt, double *out_754329157820044725) {
  f_fun(state,  dt, out_754329157820044725);
}
void pose_F_fun(double *state, double dt, double *out_6133369954690992745) {
  F_fun(state,  dt, out_6133369954690992745);
}
void pose_h_4(double *state, double *unused, double *out_516041222348960560) {
  h_4(state, unused, out_516041222348960560);
}
void pose_H_4(double *state, double *unused, double *out_1338770504403203600) {
  H_4(state, unused, out_1338770504403203600);
}
void pose_h_10(double *state, double *unused, double *out_2447986843515870103) {
  h_10(state, unused, out_2447986843515870103);
}
void pose_H_10(double *state, double *unused, double *out_7155285139208376669) {
  H_10(state, unused, out_7155285139208376669);
}
void pose_h_13(double *state, double *unused, double *out_4078955435366114031) {
  h_13(state, unused, out_4078955435366114031);
}
void pose_H_13(double *state, double *unused, double *out_1873503320929129201) {
  H_13(state, unused, out_1873503320929129201);
}
void pose_h_14(double *state, double *unused, double *out_8824687956191096942) {
  h_14(state, unused, out_8824687956191096942);
}
void pose_H_14(double *state, double *unused, double *out_2624470351936280929) {
  H_14(state, unused, out_2624470351936280929);
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
