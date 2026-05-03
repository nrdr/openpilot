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
void err_fun(double *nom_x, double *delta_x, double *out_6247163002975687744) {
   out_6247163002975687744[0] = delta_x[0] + nom_x[0];
   out_6247163002975687744[1] = delta_x[1] + nom_x[1];
   out_6247163002975687744[2] = delta_x[2] + nom_x[2];
   out_6247163002975687744[3] = delta_x[3] + nom_x[3];
   out_6247163002975687744[4] = delta_x[4] + nom_x[4];
   out_6247163002975687744[5] = delta_x[5] + nom_x[5];
   out_6247163002975687744[6] = delta_x[6] + nom_x[6];
   out_6247163002975687744[7] = delta_x[7] + nom_x[7];
   out_6247163002975687744[8] = delta_x[8] + nom_x[8];
   out_6247163002975687744[9] = delta_x[9] + nom_x[9];
   out_6247163002975687744[10] = delta_x[10] + nom_x[10];
   out_6247163002975687744[11] = delta_x[11] + nom_x[11];
   out_6247163002975687744[12] = delta_x[12] + nom_x[12];
   out_6247163002975687744[13] = delta_x[13] + nom_x[13];
   out_6247163002975687744[14] = delta_x[14] + nom_x[14];
   out_6247163002975687744[15] = delta_x[15] + nom_x[15];
   out_6247163002975687744[16] = delta_x[16] + nom_x[16];
   out_6247163002975687744[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_2784495282432373016) {
   out_2784495282432373016[0] = -nom_x[0] + true_x[0];
   out_2784495282432373016[1] = -nom_x[1] + true_x[1];
   out_2784495282432373016[2] = -nom_x[2] + true_x[2];
   out_2784495282432373016[3] = -nom_x[3] + true_x[3];
   out_2784495282432373016[4] = -nom_x[4] + true_x[4];
   out_2784495282432373016[5] = -nom_x[5] + true_x[5];
   out_2784495282432373016[6] = -nom_x[6] + true_x[6];
   out_2784495282432373016[7] = -nom_x[7] + true_x[7];
   out_2784495282432373016[8] = -nom_x[8] + true_x[8];
   out_2784495282432373016[9] = -nom_x[9] + true_x[9];
   out_2784495282432373016[10] = -nom_x[10] + true_x[10];
   out_2784495282432373016[11] = -nom_x[11] + true_x[11];
   out_2784495282432373016[12] = -nom_x[12] + true_x[12];
   out_2784495282432373016[13] = -nom_x[13] + true_x[13];
   out_2784495282432373016[14] = -nom_x[14] + true_x[14];
   out_2784495282432373016[15] = -nom_x[15] + true_x[15];
   out_2784495282432373016[16] = -nom_x[16] + true_x[16];
   out_2784495282432373016[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_662979392671356586) {
   out_662979392671356586[0] = 1.0;
   out_662979392671356586[1] = 0.0;
   out_662979392671356586[2] = 0.0;
   out_662979392671356586[3] = 0.0;
   out_662979392671356586[4] = 0.0;
   out_662979392671356586[5] = 0.0;
   out_662979392671356586[6] = 0.0;
   out_662979392671356586[7] = 0.0;
   out_662979392671356586[8] = 0.0;
   out_662979392671356586[9] = 0.0;
   out_662979392671356586[10] = 0.0;
   out_662979392671356586[11] = 0.0;
   out_662979392671356586[12] = 0.0;
   out_662979392671356586[13] = 0.0;
   out_662979392671356586[14] = 0.0;
   out_662979392671356586[15] = 0.0;
   out_662979392671356586[16] = 0.0;
   out_662979392671356586[17] = 0.0;
   out_662979392671356586[18] = 0.0;
   out_662979392671356586[19] = 1.0;
   out_662979392671356586[20] = 0.0;
   out_662979392671356586[21] = 0.0;
   out_662979392671356586[22] = 0.0;
   out_662979392671356586[23] = 0.0;
   out_662979392671356586[24] = 0.0;
   out_662979392671356586[25] = 0.0;
   out_662979392671356586[26] = 0.0;
   out_662979392671356586[27] = 0.0;
   out_662979392671356586[28] = 0.0;
   out_662979392671356586[29] = 0.0;
   out_662979392671356586[30] = 0.0;
   out_662979392671356586[31] = 0.0;
   out_662979392671356586[32] = 0.0;
   out_662979392671356586[33] = 0.0;
   out_662979392671356586[34] = 0.0;
   out_662979392671356586[35] = 0.0;
   out_662979392671356586[36] = 0.0;
   out_662979392671356586[37] = 0.0;
   out_662979392671356586[38] = 1.0;
   out_662979392671356586[39] = 0.0;
   out_662979392671356586[40] = 0.0;
   out_662979392671356586[41] = 0.0;
   out_662979392671356586[42] = 0.0;
   out_662979392671356586[43] = 0.0;
   out_662979392671356586[44] = 0.0;
   out_662979392671356586[45] = 0.0;
   out_662979392671356586[46] = 0.0;
   out_662979392671356586[47] = 0.0;
   out_662979392671356586[48] = 0.0;
   out_662979392671356586[49] = 0.0;
   out_662979392671356586[50] = 0.0;
   out_662979392671356586[51] = 0.0;
   out_662979392671356586[52] = 0.0;
   out_662979392671356586[53] = 0.0;
   out_662979392671356586[54] = 0.0;
   out_662979392671356586[55] = 0.0;
   out_662979392671356586[56] = 0.0;
   out_662979392671356586[57] = 1.0;
   out_662979392671356586[58] = 0.0;
   out_662979392671356586[59] = 0.0;
   out_662979392671356586[60] = 0.0;
   out_662979392671356586[61] = 0.0;
   out_662979392671356586[62] = 0.0;
   out_662979392671356586[63] = 0.0;
   out_662979392671356586[64] = 0.0;
   out_662979392671356586[65] = 0.0;
   out_662979392671356586[66] = 0.0;
   out_662979392671356586[67] = 0.0;
   out_662979392671356586[68] = 0.0;
   out_662979392671356586[69] = 0.0;
   out_662979392671356586[70] = 0.0;
   out_662979392671356586[71] = 0.0;
   out_662979392671356586[72] = 0.0;
   out_662979392671356586[73] = 0.0;
   out_662979392671356586[74] = 0.0;
   out_662979392671356586[75] = 0.0;
   out_662979392671356586[76] = 1.0;
   out_662979392671356586[77] = 0.0;
   out_662979392671356586[78] = 0.0;
   out_662979392671356586[79] = 0.0;
   out_662979392671356586[80] = 0.0;
   out_662979392671356586[81] = 0.0;
   out_662979392671356586[82] = 0.0;
   out_662979392671356586[83] = 0.0;
   out_662979392671356586[84] = 0.0;
   out_662979392671356586[85] = 0.0;
   out_662979392671356586[86] = 0.0;
   out_662979392671356586[87] = 0.0;
   out_662979392671356586[88] = 0.0;
   out_662979392671356586[89] = 0.0;
   out_662979392671356586[90] = 0.0;
   out_662979392671356586[91] = 0.0;
   out_662979392671356586[92] = 0.0;
   out_662979392671356586[93] = 0.0;
   out_662979392671356586[94] = 0.0;
   out_662979392671356586[95] = 1.0;
   out_662979392671356586[96] = 0.0;
   out_662979392671356586[97] = 0.0;
   out_662979392671356586[98] = 0.0;
   out_662979392671356586[99] = 0.0;
   out_662979392671356586[100] = 0.0;
   out_662979392671356586[101] = 0.0;
   out_662979392671356586[102] = 0.0;
   out_662979392671356586[103] = 0.0;
   out_662979392671356586[104] = 0.0;
   out_662979392671356586[105] = 0.0;
   out_662979392671356586[106] = 0.0;
   out_662979392671356586[107] = 0.0;
   out_662979392671356586[108] = 0.0;
   out_662979392671356586[109] = 0.0;
   out_662979392671356586[110] = 0.0;
   out_662979392671356586[111] = 0.0;
   out_662979392671356586[112] = 0.0;
   out_662979392671356586[113] = 0.0;
   out_662979392671356586[114] = 1.0;
   out_662979392671356586[115] = 0.0;
   out_662979392671356586[116] = 0.0;
   out_662979392671356586[117] = 0.0;
   out_662979392671356586[118] = 0.0;
   out_662979392671356586[119] = 0.0;
   out_662979392671356586[120] = 0.0;
   out_662979392671356586[121] = 0.0;
   out_662979392671356586[122] = 0.0;
   out_662979392671356586[123] = 0.0;
   out_662979392671356586[124] = 0.0;
   out_662979392671356586[125] = 0.0;
   out_662979392671356586[126] = 0.0;
   out_662979392671356586[127] = 0.0;
   out_662979392671356586[128] = 0.0;
   out_662979392671356586[129] = 0.0;
   out_662979392671356586[130] = 0.0;
   out_662979392671356586[131] = 0.0;
   out_662979392671356586[132] = 0.0;
   out_662979392671356586[133] = 1.0;
   out_662979392671356586[134] = 0.0;
   out_662979392671356586[135] = 0.0;
   out_662979392671356586[136] = 0.0;
   out_662979392671356586[137] = 0.0;
   out_662979392671356586[138] = 0.0;
   out_662979392671356586[139] = 0.0;
   out_662979392671356586[140] = 0.0;
   out_662979392671356586[141] = 0.0;
   out_662979392671356586[142] = 0.0;
   out_662979392671356586[143] = 0.0;
   out_662979392671356586[144] = 0.0;
   out_662979392671356586[145] = 0.0;
   out_662979392671356586[146] = 0.0;
   out_662979392671356586[147] = 0.0;
   out_662979392671356586[148] = 0.0;
   out_662979392671356586[149] = 0.0;
   out_662979392671356586[150] = 0.0;
   out_662979392671356586[151] = 0.0;
   out_662979392671356586[152] = 1.0;
   out_662979392671356586[153] = 0.0;
   out_662979392671356586[154] = 0.0;
   out_662979392671356586[155] = 0.0;
   out_662979392671356586[156] = 0.0;
   out_662979392671356586[157] = 0.0;
   out_662979392671356586[158] = 0.0;
   out_662979392671356586[159] = 0.0;
   out_662979392671356586[160] = 0.0;
   out_662979392671356586[161] = 0.0;
   out_662979392671356586[162] = 0.0;
   out_662979392671356586[163] = 0.0;
   out_662979392671356586[164] = 0.0;
   out_662979392671356586[165] = 0.0;
   out_662979392671356586[166] = 0.0;
   out_662979392671356586[167] = 0.0;
   out_662979392671356586[168] = 0.0;
   out_662979392671356586[169] = 0.0;
   out_662979392671356586[170] = 0.0;
   out_662979392671356586[171] = 1.0;
   out_662979392671356586[172] = 0.0;
   out_662979392671356586[173] = 0.0;
   out_662979392671356586[174] = 0.0;
   out_662979392671356586[175] = 0.0;
   out_662979392671356586[176] = 0.0;
   out_662979392671356586[177] = 0.0;
   out_662979392671356586[178] = 0.0;
   out_662979392671356586[179] = 0.0;
   out_662979392671356586[180] = 0.0;
   out_662979392671356586[181] = 0.0;
   out_662979392671356586[182] = 0.0;
   out_662979392671356586[183] = 0.0;
   out_662979392671356586[184] = 0.0;
   out_662979392671356586[185] = 0.0;
   out_662979392671356586[186] = 0.0;
   out_662979392671356586[187] = 0.0;
   out_662979392671356586[188] = 0.0;
   out_662979392671356586[189] = 0.0;
   out_662979392671356586[190] = 1.0;
   out_662979392671356586[191] = 0.0;
   out_662979392671356586[192] = 0.0;
   out_662979392671356586[193] = 0.0;
   out_662979392671356586[194] = 0.0;
   out_662979392671356586[195] = 0.0;
   out_662979392671356586[196] = 0.0;
   out_662979392671356586[197] = 0.0;
   out_662979392671356586[198] = 0.0;
   out_662979392671356586[199] = 0.0;
   out_662979392671356586[200] = 0.0;
   out_662979392671356586[201] = 0.0;
   out_662979392671356586[202] = 0.0;
   out_662979392671356586[203] = 0.0;
   out_662979392671356586[204] = 0.0;
   out_662979392671356586[205] = 0.0;
   out_662979392671356586[206] = 0.0;
   out_662979392671356586[207] = 0.0;
   out_662979392671356586[208] = 0.0;
   out_662979392671356586[209] = 1.0;
   out_662979392671356586[210] = 0.0;
   out_662979392671356586[211] = 0.0;
   out_662979392671356586[212] = 0.0;
   out_662979392671356586[213] = 0.0;
   out_662979392671356586[214] = 0.0;
   out_662979392671356586[215] = 0.0;
   out_662979392671356586[216] = 0.0;
   out_662979392671356586[217] = 0.0;
   out_662979392671356586[218] = 0.0;
   out_662979392671356586[219] = 0.0;
   out_662979392671356586[220] = 0.0;
   out_662979392671356586[221] = 0.0;
   out_662979392671356586[222] = 0.0;
   out_662979392671356586[223] = 0.0;
   out_662979392671356586[224] = 0.0;
   out_662979392671356586[225] = 0.0;
   out_662979392671356586[226] = 0.0;
   out_662979392671356586[227] = 0.0;
   out_662979392671356586[228] = 1.0;
   out_662979392671356586[229] = 0.0;
   out_662979392671356586[230] = 0.0;
   out_662979392671356586[231] = 0.0;
   out_662979392671356586[232] = 0.0;
   out_662979392671356586[233] = 0.0;
   out_662979392671356586[234] = 0.0;
   out_662979392671356586[235] = 0.0;
   out_662979392671356586[236] = 0.0;
   out_662979392671356586[237] = 0.0;
   out_662979392671356586[238] = 0.0;
   out_662979392671356586[239] = 0.0;
   out_662979392671356586[240] = 0.0;
   out_662979392671356586[241] = 0.0;
   out_662979392671356586[242] = 0.0;
   out_662979392671356586[243] = 0.0;
   out_662979392671356586[244] = 0.0;
   out_662979392671356586[245] = 0.0;
   out_662979392671356586[246] = 0.0;
   out_662979392671356586[247] = 1.0;
   out_662979392671356586[248] = 0.0;
   out_662979392671356586[249] = 0.0;
   out_662979392671356586[250] = 0.0;
   out_662979392671356586[251] = 0.0;
   out_662979392671356586[252] = 0.0;
   out_662979392671356586[253] = 0.0;
   out_662979392671356586[254] = 0.0;
   out_662979392671356586[255] = 0.0;
   out_662979392671356586[256] = 0.0;
   out_662979392671356586[257] = 0.0;
   out_662979392671356586[258] = 0.0;
   out_662979392671356586[259] = 0.0;
   out_662979392671356586[260] = 0.0;
   out_662979392671356586[261] = 0.0;
   out_662979392671356586[262] = 0.0;
   out_662979392671356586[263] = 0.0;
   out_662979392671356586[264] = 0.0;
   out_662979392671356586[265] = 0.0;
   out_662979392671356586[266] = 1.0;
   out_662979392671356586[267] = 0.0;
   out_662979392671356586[268] = 0.0;
   out_662979392671356586[269] = 0.0;
   out_662979392671356586[270] = 0.0;
   out_662979392671356586[271] = 0.0;
   out_662979392671356586[272] = 0.0;
   out_662979392671356586[273] = 0.0;
   out_662979392671356586[274] = 0.0;
   out_662979392671356586[275] = 0.0;
   out_662979392671356586[276] = 0.0;
   out_662979392671356586[277] = 0.0;
   out_662979392671356586[278] = 0.0;
   out_662979392671356586[279] = 0.0;
   out_662979392671356586[280] = 0.0;
   out_662979392671356586[281] = 0.0;
   out_662979392671356586[282] = 0.0;
   out_662979392671356586[283] = 0.0;
   out_662979392671356586[284] = 0.0;
   out_662979392671356586[285] = 1.0;
   out_662979392671356586[286] = 0.0;
   out_662979392671356586[287] = 0.0;
   out_662979392671356586[288] = 0.0;
   out_662979392671356586[289] = 0.0;
   out_662979392671356586[290] = 0.0;
   out_662979392671356586[291] = 0.0;
   out_662979392671356586[292] = 0.0;
   out_662979392671356586[293] = 0.0;
   out_662979392671356586[294] = 0.0;
   out_662979392671356586[295] = 0.0;
   out_662979392671356586[296] = 0.0;
   out_662979392671356586[297] = 0.0;
   out_662979392671356586[298] = 0.0;
   out_662979392671356586[299] = 0.0;
   out_662979392671356586[300] = 0.0;
   out_662979392671356586[301] = 0.0;
   out_662979392671356586[302] = 0.0;
   out_662979392671356586[303] = 0.0;
   out_662979392671356586[304] = 1.0;
   out_662979392671356586[305] = 0.0;
   out_662979392671356586[306] = 0.0;
   out_662979392671356586[307] = 0.0;
   out_662979392671356586[308] = 0.0;
   out_662979392671356586[309] = 0.0;
   out_662979392671356586[310] = 0.0;
   out_662979392671356586[311] = 0.0;
   out_662979392671356586[312] = 0.0;
   out_662979392671356586[313] = 0.0;
   out_662979392671356586[314] = 0.0;
   out_662979392671356586[315] = 0.0;
   out_662979392671356586[316] = 0.0;
   out_662979392671356586[317] = 0.0;
   out_662979392671356586[318] = 0.0;
   out_662979392671356586[319] = 0.0;
   out_662979392671356586[320] = 0.0;
   out_662979392671356586[321] = 0.0;
   out_662979392671356586[322] = 0.0;
   out_662979392671356586[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_5358842043988680887) {
   out_5358842043988680887[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_5358842043988680887[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_5358842043988680887[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_5358842043988680887[3] = dt*state[12] + state[3];
   out_5358842043988680887[4] = dt*state[13] + state[4];
   out_5358842043988680887[5] = dt*state[14] + state[5];
   out_5358842043988680887[6] = state[6];
   out_5358842043988680887[7] = state[7];
   out_5358842043988680887[8] = state[8];
   out_5358842043988680887[9] = state[9];
   out_5358842043988680887[10] = state[10];
   out_5358842043988680887[11] = state[11];
   out_5358842043988680887[12] = state[12];
   out_5358842043988680887[13] = state[13];
   out_5358842043988680887[14] = state[14];
   out_5358842043988680887[15] = state[15];
   out_5358842043988680887[16] = state[16];
   out_5358842043988680887[17] = state[17];
}
void F_fun(double *state, double dt, double *out_6970610951587922797) {
   out_6970610951587922797[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6970610951587922797[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6970610951587922797[2] = 0;
   out_6970610951587922797[3] = 0;
   out_6970610951587922797[4] = 0;
   out_6970610951587922797[5] = 0;
   out_6970610951587922797[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6970610951587922797[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6970610951587922797[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6970610951587922797[9] = 0;
   out_6970610951587922797[10] = 0;
   out_6970610951587922797[11] = 0;
   out_6970610951587922797[12] = 0;
   out_6970610951587922797[13] = 0;
   out_6970610951587922797[14] = 0;
   out_6970610951587922797[15] = 0;
   out_6970610951587922797[16] = 0;
   out_6970610951587922797[17] = 0;
   out_6970610951587922797[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6970610951587922797[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6970610951587922797[20] = 0;
   out_6970610951587922797[21] = 0;
   out_6970610951587922797[22] = 0;
   out_6970610951587922797[23] = 0;
   out_6970610951587922797[24] = 0;
   out_6970610951587922797[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6970610951587922797[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6970610951587922797[27] = 0;
   out_6970610951587922797[28] = 0;
   out_6970610951587922797[29] = 0;
   out_6970610951587922797[30] = 0;
   out_6970610951587922797[31] = 0;
   out_6970610951587922797[32] = 0;
   out_6970610951587922797[33] = 0;
   out_6970610951587922797[34] = 0;
   out_6970610951587922797[35] = 0;
   out_6970610951587922797[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6970610951587922797[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6970610951587922797[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6970610951587922797[39] = 0;
   out_6970610951587922797[40] = 0;
   out_6970610951587922797[41] = 0;
   out_6970610951587922797[42] = 0;
   out_6970610951587922797[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6970610951587922797[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6970610951587922797[45] = 0;
   out_6970610951587922797[46] = 0;
   out_6970610951587922797[47] = 0;
   out_6970610951587922797[48] = 0;
   out_6970610951587922797[49] = 0;
   out_6970610951587922797[50] = 0;
   out_6970610951587922797[51] = 0;
   out_6970610951587922797[52] = 0;
   out_6970610951587922797[53] = 0;
   out_6970610951587922797[54] = 0;
   out_6970610951587922797[55] = 0;
   out_6970610951587922797[56] = 0;
   out_6970610951587922797[57] = 1;
   out_6970610951587922797[58] = 0;
   out_6970610951587922797[59] = 0;
   out_6970610951587922797[60] = 0;
   out_6970610951587922797[61] = 0;
   out_6970610951587922797[62] = 0;
   out_6970610951587922797[63] = 0;
   out_6970610951587922797[64] = 0;
   out_6970610951587922797[65] = 0;
   out_6970610951587922797[66] = dt;
   out_6970610951587922797[67] = 0;
   out_6970610951587922797[68] = 0;
   out_6970610951587922797[69] = 0;
   out_6970610951587922797[70] = 0;
   out_6970610951587922797[71] = 0;
   out_6970610951587922797[72] = 0;
   out_6970610951587922797[73] = 0;
   out_6970610951587922797[74] = 0;
   out_6970610951587922797[75] = 0;
   out_6970610951587922797[76] = 1;
   out_6970610951587922797[77] = 0;
   out_6970610951587922797[78] = 0;
   out_6970610951587922797[79] = 0;
   out_6970610951587922797[80] = 0;
   out_6970610951587922797[81] = 0;
   out_6970610951587922797[82] = 0;
   out_6970610951587922797[83] = 0;
   out_6970610951587922797[84] = 0;
   out_6970610951587922797[85] = dt;
   out_6970610951587922797[86] = 0;
   out_6970610951587922797[87] = 0;
   out_6970610951587922797[88] = 0;
   out_6970610951587922797[89] = 0;
   out_6970610951587922797[90] = 0;
   out_6970610951587922797[91] = 0;
   out_6970610951587922797[92] = 0;
   out_6970610951587922797[93] = 0;
   out_6970610951587922797[94] = 0;
   out_6970610951587922797[95] = 1;
   out_6970610951587922797[96] = 0;
   out_6970610951587922797[97] = 0;
   out_6970610951587922797[98] = 0;
   out_6970610951587922797[99] = 0;
   out_6970610951587922797[100] = 0;
   out_6970610951587922797[101] = 0;
   out_6970610951587922797[102] = 0;
   out_6970610951587922797[103] = 0;
   out_6970610951587922797[104] = dt;
   out_6970610951587922797[105] = 0;
   out_6970610951587922797[106] = 0;
   out_6970610951587922797[107] = 0;
   out_6970610951587922797[108] = 0;
   out_6970610951587922797[109] = 0;
   out_6970610951587922797[110] = 0;
   out_6970610951587922797[111] = 0;
   out_6970610951587922797[112] = 0;
   out_6970610951587922797[113] = 0;
   out_6970610951587922797[114] = 1;
   out_6970610951587922797[115] = 0;
   out_6970610951587922797[116] = 0;
   out_6970610951587922797[117] = 0;
   out_6970610951587922797[118] = 0;
   out_6970610951587922797[119] = 0;
   out_6970610951587922797[120] = 0;
   out_6970610951587922797[121] = 0;
   out_6970610951587922797[122] = 0;
   out_6970610951587922797[123] = 0;
   out_6970610951587922797[124] = 0;
   out_6970610951587922797[125] = 0;
   out_6970610951587922797[126] = 0;
   out_6970610951587922797[127] = 0;
   out_6970610951587922797[128] = 0;
   out_6970610951587922797[129] = 0;
   out_6970610951587922797[130] = 0;
   out_6970610951587922797[131] = 0;
   out_6970610951587922797[132] = 0;
   out_6970610951587922797[133] = 1;
   out_6970610951587922797[134] = 0;
   out_6970610951587922797[135] = 0;
   out_6970610951587922797[136] = 0;
   out_6970610951587922797[137] = 0;
   out_6970610951587922797[138] = 0;
   out_6970610951587922797[139] = 0;
   out_6970610951587922797[140] = 0;
   out_6970610951587922797[141] = 0;
   out_6970610951587922797[142] = 0;
   out_6970610951587922797[143] = 0;
   out_6970610951587922797[144] = 0;
   out_6970610951587922797[145] = 0;
   out_6970610951587922797[146] = 0;
   out_6970610951587922797[147] = 0;
   out_6970610951587922797[148] = 0;
   out_6970610951587922797[149] = 0;
   out_6970610951587922797[150] = 0;
   out_6970610951587922797[151] = 0;
   out_6970610951587922797[152] = 1;
   out_6970610951587922797[153] = 0;
   out_6970610951587922797[154] = 0;
   out_6970610951587922797[155] = 0;
   out_6970610951587922797[156] = 0;
   out_6970610951587922797[157] = 0;
   out_6970610951587922797[158] = 0;
   out_6970610951587922797[159] = 0;
   out_6970610951587922797[160] = 0;
   out_6970610951587922797[161] = 0;
   out_6970610951587922797[162] = 0;
   out_6970610951587922797[163] = 0;
   out_6970610951587922797[164] = 0;
   out_6970610951587922797[165] = 0;
   out_6970610951587922797[166] = 0;
   out_6970610951587922797[167] = 0;
   out_6970610951587922797[168] = 0;
   out_6970610951587922797[169] = 0;
   out_6970610951587922797[170] = 0;
   out_6970610951587922797[171] = 1;
   out_6970610951587922797[172] = 0;
   out_6970610951587922797[173] = 0;
   out_6970610951587922797[174] = 0;
   out_6970610951587922797[175] = 0;
   out_6970610951587922797[176] = 0;
   out_6970610951587922797[177] = 0;
   out_6970610951587922797[178] = 0;
   out_6970610951587922797[179] = 0;
   out_6970610951587922797[180] = 0;
   out_6970610951587922797[181] = 0;
   out_6970610951587922797[182] = 0;
   out_6970610951587922797[183] = 0;
   out_6970610951587922797[184] = 0;
   out_6970610951587922797[185] = 0;
   out_6970610951587922797[186] = 0;
   out_6970610951587922797[187] = 0;
   out_6970610951587922797[188] = 0;
   out_6970610951587922797[189] = 0;
   out_6970610951587922797[190] = 1;
   out_6970610951587922797[191] = 0;
   out_6970610951587922797[192] = 0;
   out_6970610951587922797[193] = 0;
   out_6970610951587922797[194] = 0;
   out_6970610951587922797[195] = 0;
   out_6970610951587922797[196] = 0;
   out_6970610951587922797[197] = 0;
   out_6970610951587922797[198] = 0;
   out_6970610951587922797[199] = 0;
   out_6970610951587922797[200] = 0;
   out_6970610951587922797[201] = 0;
   out_6970610951587922797[202] = 0;
   out_6970610951587922797[203] = 0;
   out_6970610951587922797[204] = 0;
   out_6970610951587922797[205] = 0;
   out_6970610951587922797[206] = 0;
   out_6970610951587922797[207] = 0;
   out_6970610951587922797[208] = 0;
   out_6970610951587922797[209] = 1;
   out_6970610951587922797[210] = 0;
   out_6970610951587922797[211] = 0;
   out_6970610951587922797[212] = 0;
   out_6970610951587922797[213] = 0;
   out_6970610951587922797[214] = 0;
   out_6970610951587922797[215] = 0;
   out_6970610951587922797[216] = 0;
   out_6970610951587922797[217] = 0;
   out_6970610951587922797[218] = 0;
   out_6970610951587922797[219] = 0;
   out_6970610951587922797[220] = 0;
   out_6970610951587922797[221] = 0;
   out_6970610951587922797[222] = 0;
   out_6970610951587922797[223] = 0;
   out_6970610951587922797[224] = 0;
   out_6970610951587922797[225] = 0;
   out_6970610951587922797[226] = 0;
   out_6970610951587922797[227] = 0;
   out_6970610951587922797[228] = 1;
   out_6970610951587922797[229] = 0;
   out_6970610951587922797[230] = 0;
   out_6970610951587922797[231] = 0;
   out_6970610951587922797[232] = 0;
   out_6970610951587922797[233] = 0;
   out_6970610951587922797[234] = 0;
   out_6970610951587922797[235] = 0;
   out_6970610951587922797[236] = 0;
   out_6970610951587922797[237] = 0;
   out_6970610951587922797[238] = 0;
   out_6970610951587922797[239] = 0;
   out_6970610951587922797[240] = 0;
   out_6970610951587922797[241] = 0;
   out_6970610951587922797[242] = 0;
   out_6970610951587922797[243] = 0;
   out_6970610951587922797[244] = 0;
   out_6970610951587922797[245] = 0;
   out_6970610951587922797[246] = 0;
   out_6970610951587922797[247] = 1;
   out_6970610951587922797[248] = 0;
   out_6970610951587922797[249] = 0;
   out_6970610951587922797[250] = 0;
   out_6970610951587922797[251] = 0;
   out_6970610951587922797[252] = 0;
   out_6970610951587922797[253] = 0;
   out_6970610951587922797[254] = 0;
   out_6970610951587922797[255] = 0;
   out_6970610951587922797[256] = 0;
   out_6970610951587922797[257] = 0;
   out_6970610951587922797[258] = 0;
   out_6970610951587922797[259] = 0;
   out_6970610951587922797[260] = 0;
   out_6970610951587922797[261] = 0;
   out_6970610951587922797[262] = 0;
   out_6970610951587922797[263] = 0;
   out_6970610951587922797[264] = 0;
   out_6970610951587922797[265] = 0;
   out_6970610951587922797[266] = 1;
   out_6970610951587922797[267] = 0;
   out_6970610951587922797[268] = 0;
   out_6970610951587922797[269] = 0;
   out_6970610951587922797[270] = 0;
   out_6970610951587922797[271] = 0;
   out_6970610951587922797[272] = 0;
   out_6970610951587922797[273] = 0;
   out_6970610951587922797[274] = 0;
   out_6970610951587922797[275] = 0;
   out_6970610951587922797[276] = 0;
   out_6970610951587922797[277] = 0;
   out_6970610951587922797[278] = 0;
   out_6970610951587922797[279] = 0;
   out_6970610951587922797[280] = 0;
   out_6970610951587922797[281] = 0;
   out_6970610951587922797[282] = 0;
   out_6970610951587922797[283] = 0;
   out_6970610951587922797[284] = 0;
   out_6970610951587922797[285] = 1;
   out_6970610951587922797[286] = 0;
   out_6970610951587922797[287] = 0;
   out_6970610951587922797[288] = 0;
   out_6970610951587922797[289] = 0;
   out_6970610951587922797[290] = 0;
   out_6970610951587922797[291] = 0;
   out_6970610951587922797[292] = 0;
   out_6970610951587922797[293] = 0;
   out_6970610951587922797[294] = 0;
   out_6970610951587922797[295] = 0;
   out_6970610951587922797[296] = 0;
   out_6970610951587922797[297] = 0;
   out_6970610951587922797[298] = 0;
   out_6970610951587922797[299] = 0;
   out_6970610951587922797[300] = 0;
   out_6970610951587922797[301] = 0;
   out_6970610951587922797[302] = 0;
   out_6970610951587922797[303] = 0;
   out_6970610951587922797[304] = 1;
   out_6970610951587922797[305] = 0;
   out_6970610951587922797[306] = 0;
   out_6970610951587922797[307] = 0;
   out_6970610951587922797[308] = 0;
   out_6970610951587922797[309] = 0;
   out_6970610951587922797[310] = 0;
   out_6970610951587922797[311] = 0;
   out_6970610951587922797[312] = 0;
   out_6970610951587922797[313] = 0;
   out_6970610951587922797[314] = 0;
   out_6970610951587922797[315] = 0;
   out_6970610951587922797[316] = 0;
   out_6970610951587922797[317] = 0;
   out_6970610951587922797[318] = 0;
   out_6970610951587922797[319] = 0;
   out_6970610951587922797[320] = 0;
   out_6970610951587922797[321] = 0;
   out_6970610951587922797[322] = 0;
   out_6970610951587922797[323] = 1;
}
void h_4(double *state, double *unused, double *out_3613363558024225199) {
   out_3613363558024225199[0] = state[6] + state[9];
   out_3613363558024225199[1] = state[7] + state[10];
   out_3613363558024225199[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_8770780261124510538) {
   out_8770780261124510538[0] = 0;
   out_8770780261124510538[1] = 0;
   out_8770780261124510538[2] = 0;
   out_8770780261124510538[3] = 0;
   out_8770780261124510538[4] = 0;
   out_8770780261124510538[5] = 0;
   out_8770780261124510538[6] = 1;
   out_8770780261124510538[7] = 0;
   out_8770780261124510538[8] = 0;
   out_8770780261124510538[9] = 1;
   out_8770780261124510538[10] = 0;
   out_8770780261124510538[11] = 0;
   out_8770780261124510538[12] = 0;
   out_8770780261124510538[13] = 0;
   out_8770780261124510538[14] = 0;
   out_8770780261124510538[15] = 0;
   out_8770780261124510538[16] = 0;
   out_8770780261124510538[17] = 0;
   out_8770780261124510538[18] = 0;
   out_8770780261124510538[19] = 0;
   out_8770780261124510538[20] = 0;
   out_8770780261124510538[21] = 0;
   out_8770780261124510538[22] = 0;
   out_8770780261124510538[23] = 0;
   out_8770780261124510538[24] = 0;
   out_8770780261124510538[25] = 1;
   out_8770780261124510538[26] = 0;
   out_8770780261124510538[27] = 0;
   out_8770780261124510538[28] = 1;
   out_8770780261124510538[29] = 0;
   out_8770780261124510538[30] = 0;
   out_8770780261124510538[31] = 0;
   out_8770780261124510538[32] = 0;
   out_8770780261124510538[33] = 0;
   out_8770780261124510538[34] = 0;
   out_8770780261124510538[35] = 0;
   out_8770780261124510538[36] = 0;
   out_8770780261124510538[37] = 0;
   out_8770780261124510538[38] = 0;
   out_8770780261124510538[39] = 0;
   out_8770780261124510538[40] = 0;
   out_8770780261124510538[41] = 0;
   out_8770780261124510538[42] = 0;
   out_8770780261124510538[43] = 0;
   out_8770780261124510538[44] = 1;
   out_8770780261124510538[45] = 0;
   out_8770780261124510538[46] = 0;
   out_8770780261124510538[47] = 1;
   out_8770780261124510538[48] = 0;
   out_8770780261124510538[49] = 0;
   out_8770780261124510538[50] = 0;
   out_8770780261124510538[51] = 0;
   out_8770780261124510538[52] = 0;
   out_8770780261124510538[53] = 0;
}
void h_10(double *state, double *unused, double *out_7325246586980236980) {
   out_7325246586980236980[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_7325246586980236980[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_7325246586980236980[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_8143750738918534214) {
   out_8143750738918534214[0] = 0;
   out_8143750738918534214[1] = 9.8100000000000005*cos(state[1]);
   out_8143750738918534214[2] = 0;
   out_8143750738918534214[3] = 0;
   out_8143750738918534214[4] = -state[8];
   out_8143750738918534214[5] = state[7];
   out_8143750738918534214[6] = 0;
   out_8143750738918534214[7] = state[5];
   out_8143750738918534214[8] = -state[4];
   out_8143750738918534214[9] = 0;
   out_8143750738918534214[10] = 0;
   out_8143750738918534214[11] = 0;
   out_8143750738918534214[12] = 1;
   out_8143750738918534214[13] = 0;
   out_8143750738918534214[14] = 0;
   out_8143750738918534214[15] = 1;
   out_8143750738918534214[16] = 0;
   out_8143750738918534214[17] = 0;
   out_8143750738918534214[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_8143750738918534214[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_8143750738918534214[20] = 0;
   out_8143750738918534214[21] = state[8];
   out_8143750738918534214[22] = 0;
   out_8143750738918534214[23] = -state[6];
   out_8143750738918534214[24] = -state[5];
   out_8143750738918534214[25] = 0;
   out_8143750738918534214[26] = state[3];
   out_8143750738918534214[27] = 0;
   out_8143750738918534214[28] = 0;
   out_8143750738918534214[29] = 0;
   out_8143750738918534214[30] = 0;
   out_8143750738918534214[31] = 1;
   out_8143750738918534214[32] = 0;
   out_8143750738918534214[33] = 0;
   out_8143750738918534214[34] = 1;
   out_8143750738918534214[35] = 0;
   out_8143750738918534214[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_8143750738918534214[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_8143750738918534214[38] = 0;
   out_8143750738918534214[39] = -state[7];
   out_8143750738918534214[40] = state[6];
   out_8143750738918534214[41] = 0;
   out_8143750738918534214[42] = state[4];
   out_8143750738918534214[43] = -state[3];
   out_8143750738918534214[44] = 0;
   out_8143750738918534214[45] = 0;
   out_8143750738918534214[46] = 0;
   out_8143750738918534214[47] = 0;
   out_8143750738918534214[48] = 0;
   out_8143750738918534214[49] = 0;
   out_8143750738918534214[50] = 1;
   out_8143750738918534214[51] = 0;
   out_8143750738918534214[52] = 0;
   out_8143750738918534214[53] = 1;
}
void h_13(double *state, double *unused, double *out_4440237870440636920) {
   out_4440237870440636920[0] = state[3];
   out_4440237870440636920[1] = state[4];
   out_4440237870440636920[2] = state[5];
}
void H_13(double *state, double *unused, double *out_5558506435792177737) {
   out_5558506435792177737[0] = 0;
   out_5558506435792177737[1] = 0;
   out_5558506435792177737[2] = 0;
   out_5558506435792177737[3] = 1;
   out_5558506435792177737[4] = 0;
   out_5558506435792177737[5] = 0;
   out_5558506435792177737[6] = 0;
   out_5558506435792177737[7] = 0;
   out_5558506435792177737[8] = 0;
   out_5558506435792177737[9] = 0;
   out_5558506435792177737[10] = 0;
   out_5558506435792177737[11] = 0;
   out_5558506435792177737[12] = 0;
   out_5558506435792177737[13] = 0;
   out_5558506435792177737[14] = 0;
   out_5558506435792177737[15] = 0;
   out_5558506435792177737[16] = 0;
   out_5558506435792177737[17] = 0;
   out_5558506435792177737[18] = 0;
   out_5558506435792177737[19] = 0;
   out_5558506435792177737[20] = 0;
   out_5558506435792177737[21] = 0;
   out_5558506435792177737[22] = 1;
   out_5558506435792177737[23] = 0;
   out_5558506435792177737[24] = 0;
   out_5558506435792177737[25] = 0;
   out_5558506435792177737[26] = 0;
   out_5558506435792177737[27] = 0;
   out_5558506435792177737[28] = 0;
   out_5558506435792177737[29] = 0;
   out_5558506435792177737[30] = 0;
   out_5558506435792177737[31] = 0;
   out_5558506435792177737[32] = 0;
   out_5558506435792177737[33] = 0;
   out_5558506435792177737[34] = 0;
   out_5558506435792177737[35] = 0;
   out_5558506435792177737[36] = 0;
   out_5558506435792177737[37] = 0;
   out_5558506435792177737[38] = 0;
   out_5558506435792177737[39] = 0;
   out_5558506435792177737[40] = 0;
   out_5558506435792177737[41] = 1;
   out_5558506435792177737[42] = 0;
   out_5558506435792177737[43] = 0;
   out_5558506435792177737[44] = 0;
   out_5558506435792177737[45] = 0;
   out_5558506435792177737[46] = 0;
   out_5558506435792177737[47] = 0;
   out_5558506435792177737[48] = 0;
   out_5558506435792177737[49] = 0;
   out_5558506435792177737[50] = 0;
   out_5558506435792177737[51] = 0;
   out_5558506435792177737[52] = 0;
   out_5558506435792177737[53] = 0;
}
void h_14(double *state, double *unused, double *out_854572314087465107) {
   out_854572314087465107[0] = state[6];
   out_854572314087465107[1] = state[7];
   out_854572314087465107[2] = state[8];
}
void H_14(double *state, double *unused, double *out_4807539404785026009) {
   out_4807539404785026009[0] = 0;
   out_4807539404785026009[1] = 0;
   out_4807539404785026009[2] = 0;
   out_4807539404785026009[3] = 0;
   out_4807539404785026009[4] = 0;
   out_4807539404785026009[5] = 0;
   out_4807539404785026009[6] = 1;
   out_4807539404785026009[7] = 0;
   out_4807539404785026009[8] = 0;
   out_4807539404785026009[9] = 0;
   out_4807539404785026009[10] = 0;
   out_4807539404785026009[11] = 0;
   out_4807539404785026009[12] = 0;
   out_4807539404785026009[13] = 0;
   out_4807539404785026009[14] = 0;
   out_4807539404785026009[15] = 0;
   out_4807539404785026009[16] = 0;
   out_4807539404785026009[17] = 0;
   out_4807539404785026009[18] = 0;
   out_4807539404785026009[19] = 0;
   out_4807539404785026009[20] = 0;
   out_4807539404785026009[21] = 0;
   out_4807539404785026009[22] = 0;
   out_4807539404785026009[23] = 0;
   out_4807539404785026009[24] = 0;
   out_4807539404785026009[25] = 1;
   out_4807539404785026009[26] = 0;
   out_4807539404785026009[27] = 0;
   out_4807539404785026009[28] = 0;
   out_4807539404785026009[29] = 0;
   out_4807539404785026009[30] = 0;
   out_4807539404785026009[31] = 0;
   out_4807539404785026009[32] = 0;
   out_4807539404785026009[33] = 0;
   out_4807539404785026009[34] = 0;
   out_4807539404785026009[35] = 0;
   out_4807539404785026009[36] = 0;
   out_4807539404785026009[37] = 0;
   out_4807539404785026009[38] = 0;
   out_4807539404785026009[39] = 0;
   out_4807539404785026009[40] = 0;
   out_4807539404785026009[41] = 0;
   out_4807539404785026009[42] = 0;
   out_4807539404785026009[43] = 0;
   out_4807539404785026009[44] = 1;
   out_4807539404785026009[45] = 0;
   out_4807539404785026009[46] = 0;
   out_4807539404785026009[47] = 0;
   out_4807539404785026009[48] = 0;
   out_4807539404785026009[49] = 0;
   out_4807539404785026009[50] = 0;
   out_4807539404785026009[51] = 0;
   out_4807539404785026009[52] = 0;
   out_4807539404785026009[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_6247163002975687744) {
  err_fun(nom_x, delta_x, out_6247163002975687744);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_2784495282432373016) {
  inv_err_fun(nom_x, true_x, out_2784495282432373016);
}
void pose_H_mod_fun(double *state, double *out_662979392671356586) {
  H_mod_fun(state, out_662979392671356586);
}
void pose_f_fun(double *state, double dt, double *out_5358842043988680887) {
  f_fun(state,  dt, out_5358842043988680887);
}
void pose_F_fun(double *state, double dt, double *out_6970610951587922797) {
  F_fun(state,  dt, out_6970610951587922797);
}
void pose_h_4(double *state, double *unused, double *out_3613363558024225199) {
  h_4(state, unused, out_3613363558024225199);
}
void pose_H_4(double *state, double *unused, double *out_8770780261124510538) {
  H_4(state, unused, out_8770780261124510538);
}
void pose_h_10(double *state, double *unused, double *out_7325246586980236980) {
  h_10(state, unused, out_7325246586980236980);
}
void pose_H_10(double *state, double *unused, double *out_8143750738918534214) {
  H_10(state, unused, out_8143750738918534214);
}
void pose_h_13(double *state, double *unused, double *out_4440237870440636920) {
  h_13(state, unused, out_4440237870440636920);
}
void pose_H_13(double *state, double *unused, double *out_5558506435792177737) {
  H_13(state, unused, out_5558506435792177737);
}
void pose_h_14(double *state, double *unused, double *out_854572314087465107) {
  h_14(state, unused, out_854572314087465107);
}
void pose_H_14(double *state, double *unused, double *out_4807539404785026009) {
  H_14(state, unused, out_4807539404785026009);
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
