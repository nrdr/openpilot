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
void err_fun(double *nom_x, double *delta_x, double *out_3288415244471962854) {
   out_3288415244471962854[0] = delta_x[0] + nom_x[0];
   out_3288415244471962854[1] = delta_x[1] + nom_x[1];
   out_3288415244471962854[2] = delta_x[2] + nom_x[2];
   out_3288415244471962854[3] = delta_x[3] + nom_x[3];
   out_3288415244471962854[4] = delta_x[4] + nom_x[4];
   out_3288415244471962854[5] = delta_x[5] + nom_x[5];
   out_3288415244471962854[6] = delta_x[6] + nom_x[6];
   out_3288415244471962854[7] = delta_x[7] + nom_x[7];
   out_3288415244471962854[8] = delta_x[8] + nom_x[8];
   out_3288415244471962854[9] = delta_x[9] + nom_x[9];
   out_3288415244471962854[10] = delta_x[10] + nom_x[10];
   out_3288415244471962854[11] = delta_x[11] + nom_x[11];
   out_3288415244471962854[12] = delta_x[12] + nom_x[12];
   out_3288415244471962854[13] = delta_x[13] + nom_x[13];
   out_3288415244471962854[14] = delta_x[14] + nom_x[14];
   out_3288415244471962854[15] = delta_x[15] + nom_x[15];
   out_3288415244471962854[16] = delta_x[16] + nom_x[16];
   out_3288415244471962854[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_2706393179994234815) {
   out_2706393179994234815[0] = -nom_x[0] + true_x[0];
   out_2706393179994234815[1] = -nom_x[1] + true_x[1];
   out_2706393179994234815[2] = -nom_x[2] + true_x[2];
   out_2706393179994234815[3] = -nom_x[3] + true_x[3];
   out_2706393179994234815[4] = -nom_x[4] + true_x[4];
   out_2706393179994234815[5] = -nom_x[5] + true_x[5];
   out_2706393179994234815[6] = -nom_x[6] + true_x[6];
   out_2706393179994234815[7] = -nom_x[7] + true_x[7];
   out_2706393179994234815[8] = -nom_x[8] + true_x[8];
   out_2706393179994234815[9] = -nom_x[9] + true_x[9];
   out_2706393179994234815[10] = -nom_x[10] + true_x[10];
   out_2706393179994234815[11] = -nom_x[11] + true_x[11];
   out_2706393179994234815[12] = -nom_x[12] + true_x[12];
   out_2706393179994234815[13] = -nom_x[13] + true_x[13];
   out_2706393179994234815[14] = -nom_x[14] + true_x[14];
   out_2706393179994234815[15] = -nom_x[15] + true_x[15];
   out_2706393179994234815[16] = -nom_x[16] + true_x[16];
   out_2706393179994234815[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_298691080821975752) {
   out_298691080821975752[0] = 1.0;
   out_298691080821975752[1] = 0.0;
   out_298691080821975752[2] = 0.0;
   out_298691080821975752[3] = 0.0;
   out_298691080821975752[4] = 0.0;
   out_298691080821975752[5] = 0.0;
   out_298691080821975752[6] = 0.0;
   out_298691080821975752[7] = 0.0;
   out_298691080821975752[8] = 0.0;
   out_298691080821975752[9] = 0.0;
   out_298691080821975752[10] = 0.0;
   out_298691080821975752[11] = 0.0;
   out_298691080821975752[12] = 0.0;
   out_298691080821975752[13] = 0.0;
   out_298691080821975752[14] = 0.0;
   out_298691080821975752[15] = 0.0;
   out_298691080821975752[16] = 0.0;
   out_298691080821975752[17] = 0.0;
   out_298691080821975752[18] = 0.0;
   out_298691080821975752[19] = 1.0;
   out_298691080821975752[20] = 0.0;
   out_298691080821975752[21] = 0.0;
   out_298691080821975752[22] = 0.0;
   out_298691080821975752[23] = 0.0;
   out_298691080821975752[24] = 0.0;
   out_298691080821975752[25] = 0.0;
   out_298691080821975752[26] = 0.0;
   out_298691080821975752[27] = 0.0;
   out_298691080821975752[28] = 0.0;
   out_298691080821975752[29] = 0.0;
   out_298691080821975752[30] = 0.0;
   out_298691080821975752[31] = 0.0;
   out_298691080821975752[32] = 0.0;
   out_298691080821975752[33] = 0.0;
   out_298691080821975752[34] = 0.0;
   out_298691080821975752[35] = 0.0;
   out_298691080821975752[36] = 0.0;
   out_298691080821975752[37] = 0.0;
   out_298691080821975752[38] = 1.0;
   out_298691080821975752[39] = 0.0;
   out_298691080821975752[40] = 0.0;
   out_298691080821975752[41] = 0.0;
   out_298691080821975752[42] = 0.0;
   out_298691080821975752[43] = 0.0;
   out_298691080821975752[44] = 0.0;
   out_298691080821975752[45] = 0.0;
   out_298691080821975752[46] = 0.0;
   out_298691080821975752[47] = 0.0;
   out_298691080821975752[48] = 0.0;
   out_298691080821975752[49] = 0.0;
   out_298691080821975752[50] = 0.0;
   out_298691080821975752[51] = 0.0;
   out_298691080821975752[52] = 0.0;
   out_298691080821975752[53] = 0.0;
   out_298691080821975752[54] = 0.0;
   out_298691080821975752[55] = 0.0;
   out_298691080821975752[56] = 0.0;
   out_298691080821975752[57] = 1.0;
   out_298691080821975752[58] = 0.0;
   out_298691080821975752[59] = 0.0;
   out_298691080821975752[60] = 0.0;
   out_298691080821975752[61] = 0.0;
   out_298691080821975752[62] = 0.0;
   out_298691080821975752[63] = 0.0;
   out_298691080821975752[64] = 0.0;
   out_298691080821975752[65] = 0.0;
   out_298691080821975752[66] = 0.0;
   out_298691080821975752[67] = 0.0;
   out_298691080821975752[68] = 0.0;
   out_298691080821975752[69] = 0.0;
   out_298691080821975752[70] = 0.0;
   out_298691080821975752[71] = 0.0;
   out_298691080821975752[72] = 0.0;
   out_298691080821975752[73] = 0.0;
   out_298691080821975752[74] = 0.0;
   out_298691080821975752[75] = 0.0;
   out_298691080821975752[76] = 1.0;
   out_298691080821975752[77] = 0.0;
   out_298691080821975752[78] = 0.0;
   out_298691080821975752[79] = 0.0;
   out_298691080821975752[80] = 0.0;
   out_298691080821975752[81] = 0.0;
   out_298691080821975752[82] = 0.0;
   out_298691080821975752[83] = 0.0;
   out_298691080821975752[84] = 0.0;
   out_298691080821975752[85] = 0.0;
   out_298691080821975752[86] = 0.0;
   out_298691080821975752[87] = 0.0;
   out_298691080821975752[88] = 0.0;
   out_298691080821975752[89] = 0.0;
   out_298691080821975752[90] = 0.0;
   out_298691080821975752[91] = 0.0;
   out_298691080821975752[92] = 0.0;
   out_298691080821975752[93] = 0.0;
   out_298691080821975752[94] = 0.0;
   out_298691080821975752[95] = 1.0;
   out_298691080821975752[96] = 0.0;
   out_298691080821975752[97] = 0.0;
   out_298691080821975752[98] = 0.0;
   out_298691080821975752[99] = 0.0;
   out_298691080821975752[100] = 0.0;
   out_298691080821975752[101] = 0.0;
   out_298691080821975752[102] = 0.0;
   out_298691080821975752[103] = 0.0;
   out_298691080821975752[104] = 0.0;
   out_298691080821975752[105] = 0.0;
   out_298691080821975752[106] = 0.0;
   out_298691080821975752[107] = 0.0;
   out_298691080821975752[108] = 0.0;
   out_298691080821975752[109] = 0.0;
   out_298691080821975752[110] = 0.0;
   out_298691080821975752[111] = 0.0;
   out_298691080821975752[112] = 0.0;
   out_298691080821975752[113] = 0.0;
   out_298691080821975752[114] = 1.0;
   out_298691080821975752[115] = 0.0;
   out_298691080821975752[116] = 0.0;
   out_298691080821975752[117] = 0.0;
   out_298691080821975752[118] = 0.0;
   out_298691080821975752[119] = 0.0;
   out_298691080821975752[120] = 0.0;
   out_298691080821975752[121] = 0.0;
   out_298691080821975752[122] = 0.0;
   out_298691080821975752[123] = 0.0;
   out_298691080821975752[124] = 0.0;
   out_298691080821975752[125] = 0.0;
   out_298691080821975752[126] = 0.0;
   out_298691080821975752[127] = 0.0;
   out_298691080821975752[128] = 0.0;
   out_298691080821975752[129] = 0.0;
   out_298691080821975752[130] = 0.0;
   out_298691080821975752[131] = 0.0;
   out_298691080821975752[132] = 0.0;
   out_298691080821975752[133] = 1.0;
   out_298691080821975752[134] = 0.0;
   out_298691080821975752[135] = 0.0;
   out_298691080821975752[136] = 0.0;
   out_298691080821975752[137] = 0.0;
   out_298691080821975752[138] = 0.0;
   out_298691080821975752[139] = 0.0;
   out_298691080821975752[140] = 0.0;
   out_298691080821975752[141] = 0.0;
   out_298691080821975752[142] = 0.0;
   out_298691080821975752[143] = 0.0;
   out_298691080821975752[144] = 0.0;
   out_298691080821975752[145] = 0.0;
   out_298691080821975752[146] = 0.0;
   out_298691080821975752[147] = 0.0;
   out_298691080821975752[148] = 0.0;
   out_298691080821975752[149] = 0.0;
   out_298691080821975752[150] = 0.0;
   out_298691080821975752[151] = 0.0;
   out_298691080821975752[152] = 1.0;
   out_298691080821975752[153] = 0.0;
   out_298691080821975752[154] = 0.0;
   out_298691080821975752[155] = 0.0;
   out_298691080821975752[156] = 0.0;
   out_298691080821975752[157] = 0.0;
   out_298691080821975752[158] = 0.0;
   out_298691080821975752[159] = 0.0;
   out_298691080821975752[160] = 0.0;
   out_298691080821975752[161] = 0.0;
   out_298691080821975752[162] = 0.0;
   out_298691080821975752[163] = 0.0;
   out_298691080821975752[164] = 0.0;
   out_298691080821975752[165] = 0.0;
   out_298691080821975752[166] = 0.0;
   out_298691080821975752[167] = 0.0;
   out_298691080821975752[168] = 0.0;
   out_298691080821975752[169] = 0.0;
   out_298691080821975752[170] = 0.0;
   out_298691080821975752[171] = 1.0;
   out_298691080821975752[172] = 0.0;
   out_298691080821975752[173] = 0.0;
   out_298691080821975752[174] = 0.0;
   out_298691080821975752[175] = 0.0;
   out_298691080821975752[176] = 0.0;
   out_298691080821975752[177] = 0.0;
   out_298691080821975752[178] = 0.0;
   out_298691080821975752[179] = 0.0;
   out_298691080821975752[180] = 0.0;
   out_298691080821975752[181] = 0.0;
   out_298691080821975752[182] = 0.0;
   out_298691080821975752[183] = 0.0;
   out_298691080821975752[184] = 0.0;
   out_298691080821975752[185] = 0.0;
   out_298691080821975752[186] = 0.0;
   out_298691080821975752[187] = 0.0;
   out_298691080821975752[188] = 0.0;
   out_298691080821975752[189] = 0.0;
   out_298691080821975752[190] = 1.0;
   out_298691080821975752[191] = 0.0;
   out_298691080821975752[192] = 0.0;
   out_298691080821975752[193] = 0.0;
   out_298691080821975752[194] = 0.0;
   out_298691080821975752[195] = 0.0;
   out_298691080821975752[196] = 0.0;
   out_298691080821975752[197] = 0.0;
   out_298691080821975752[198] = 0.0;
   out_298691080821975752[199] = 0.0;
   out_298691080821975752[200] = 0.0;
   out_298691080821975752[201] = 0.0;
   out_298691080821975752[202] = 0.0;
   out_298691080821975752[203] = 0.0;
   out_298691080821975752[204] = 0.0;
   out_298691080821975752[205] = 0.0;
   out_298691080821975752[206] = 0.0;
   out_298691080821975752[207] = 0.0;
   out_298691080821975752[208] = 0.0;
   out_298691080821975752[209] = 1.0;
   out_298691080821975752[210] = 0.0;
   out_298691080821975752[211] = 0.0;
   out_298691080821975752[212] = 0.0;
   out_298691080821975752[213] = 0.0;
   out_298691080821975752[214] = 0.0;
   out_298691080821975752[215] = 0.0;
   out_298691080821975752[216] = 0.0;
   out_298691080821975752[217] = 0.0;
   out_298691080821975752[218] = 0.0;
   out_298691080821975752[219] = 0.0;
   out_298691080821975752[220] = 0.0;
   out_298691080821975752[221] = 0.0;
   out_298691080821975752[222] = 0.0;
   out_298691080821975752[223] = 0.0;
   out_298691080821975752[224] = 0.0;
   out_298691080821975752[225] = 0.0;
   out_298691080821975752[226] = 0.0;
   out_298691080821975752[227] = 0.0;
   out_298691080821975752[228] = 1.0;
   out_298691080821975752[229] = 0.0;
   out_298691080821975752[230] = 0.0;
   out_298691080821975752[231] = 0.0;
   out_298691080821975752[232] = 0.0;
   out_298691080821975752[233] = 0.0;
   out_298691080821975752[234] = 0.0;
   out_298691080821975752[235] = 0.0;
   out_298691080821975752[236] = 0.0;
   out_298691080821975752[237] = 0.0;
   out_298691080821975752[238] = 0.0;
   out_298691080821975752[239] = 0.0;
   out_298691080821975752[240] = 0.0;
   out_298691080821975752[241] = 0.0;
   out_298691080821975752[242] = 0.0;
   out_298691080821975752[243] = 0.0;
   out_298691080821975752[244] = 0.0;
   out_298691080821975752[245] = 0.0;
   out_298691080821975752[246] = 0.0;
   out_298691080821975752[247] = 1.0;
   out_298691080821975752[248] = 0.0;
   out_298691080821975752[249] = 0.0;
   out_298691080821975752[250] = 0.0;
   out_298691080821975752[251] = 0.0;
   out_298691080821975752[252] = 0.0;
   out_298691080821975752[253] = 0.0;
   out_298691080821975752[254] = 0.0;
   out_298691080821975752[255] = 0.0;
   out_298691080821975752[256] = 0.0;
   out_298691080821975752[257] = 0.0;
   out_298691080821975752[258] = 0.0;
   out_298691080821975752[259] = 0.0;
   out_298691080821975752[260] = 0.0;
   out_298691080821975752[261] = 0.0;
   out_298691080821975752[262] = 0.0;
   out_298691080821975752[263] = 0.0;
   out_298691080821975752[264] = 0.0;
   out_298691080821975752[265] = 0.0;
   out_298691080821975752[266] = 1.0;
   out_298691080821975752[267] = 0.0;
   out_298691080821975752[268] = 0.0;
   out_298691080821975752[269] = 0.0;
   out_298691080821975752[270] = 0.0;
   out_298691080821975752[271] = 0.0;
   out_298691080821975752[272] = 0.0;
   out_298691080821975752[273] = 0.0;
   out_298691080821975752[274] = 0.0;
   out_298691080821975752[275] = 0.0;
   out_298691080821975752[276] = 0.0;
   out_298691080821975752[277] = 0.0;
   out_298691080821975752[278] = 0.0;
   out_298691080821975752[279] = 0.0;
   out_298691080821975752[280] = 0.0;
   out_298691080821975752[281] = 0.0;
   out_298691080821975752[282] = 0.0;
   out_298691080821975752[283] = 0.0;
   out_298691080821975752[284] = 0.0;
   out_298691080821975752[285] = 1.0;
   out_298691080821975752[286] = 0.0;
   out_298691080821975752[287] = 0.0;
   out_298691080821975752[288] = 0.0;
   out_298691080821975752[289] = 0.0;
   out_298691080821975752[290] = 0.0;
   out_298691080821975752[291] = 0.0;
   out_298691080821975752[292] = 0.0;
   out_298691080821975752[293] = 0.0;
   out_298691080821975752[294] = 0.0;
   out_298691080821975752[295] = 0.0;
   out_298691080821975752[296] = 0.0;
   out_298691080821975752[297] = 0.0;
   out_298691080821975752[298] = 0.0;
   out_298691080821975752[299] = 0.0;
   out_298691080821975752[300] = 0.0;
   out_298691080821975752[301] = 0.0;
   out_298691080821975752[302] = 0.0;
   out_298691080821975752[303] = 0.0;
   out_298691080821975752[304] = 1.0;
   out_298691080821975752[305] = 0.0;
   out_298691080821975752[306] = 0.0;
   out_298691080821975752[307] = 0.0;
   out_298691080821975752[308] = 0.0;
   out_298691080821975752[309] = 0.0;
   out_298691080821975752[310] = 0.0;
   out_298691080821975752[311] = 0.0;
   out_298691080821975752[312] = 0.0;
   out_298691080821975752[313] = 0.0;
   out_298691080821975752[314] = 0.0;
   out_298691080821975752[315] = 0.0;
   out_298691080821975752[316] = 0.0;
   out_298691080821975752[317] = 0.0;
   out_298691080821975752[318] = 0.0;
   out_298691080821975752[319] = 0.0;
   out_298691080821975752[320] = 0.0;
   out_298691080821975752[321] = 0.0;
   out_298691080821975752[322] = 0.0;
   out_298691080821975752[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_3084202619553510425) {
   out_3084202619553510425[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_3084202619553510425[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_3084202619553510425[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_3084202619553510425[3] = dt*state[12] + state[3];
   out_3084202619553510425[4] = dt*state[13] + state[4];
   out_3084202619553510425[5] = dt*state[14] + state[5];
   out_3084202619553510425[6] = state[6];
   out_3084202619553510425[7] = state[7];
   out_3084202619553510425[8] = state[8];
   out_3084202619553510425[9] = state[9];
   out_3084202619553510425[10] = state[10];
   out_3084202619553510425[11] = state[11];
   out_3084202619553510425[12] = state[12];
   out_3084202619553510425[13] = state[13];
   out_3084202619553510425[14] = state[14];
   out_3084202619553510425[15] = state[15];
   out_3084202619553510425[16] = state[16];
   out_3084202619553510425[17] = state[17];
}
void F_fun(double *state, double dt, double *out_6041342056914775001) {
   out_6041342056914775001[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6041342056914775001[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6041342056914775001[2] = 0;
   out_6041342056914775001[3] = 0;
   out_6041342056914775001[4] = 0;
   out_6041342056914775001[5] = 0;
   out_6041342056914775001[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6041342056914775001[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6041342056914775001[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_6041342056914775001[9] = 0;
   out_6041342056914775001[10] = 0;
   out_6041342056914775001[11] = 0;
   out_6041342056914775001[12] = 0;
   out_6041342056914775001[13] = 0;
   out_6041342056914775001[14] = 0;
   out_6041342056914775001[15] = 0;
   out_6041342056914775001[16] = 0;
   out_6041342056914775001[17] = 0;
   out_6041342056914775001[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6041342056914775001[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6041342056914775001[20] = 0;
   out_6041342056914775001[21] = 0;
   out_6041342056914775001[22] = 0;
   out_6041342056914775001[23] = 0;
   out_6041342056914775001[24] = 0;
   out_6041342056914775001[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6041342056914775001[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_6041342056914775001[27] = 0;
   out_6041342056914775001[28] = 0;
   out_6041342056914775001[29] = 0;
   out_6041342056914775001[30] = 0;
   out_6041342056914775001[31] = 0;
   out_6041342056914775001[32] = 0;
   out_6041342056914775001[33] = 0;
   out_6041342056914775001[34] = 0;
   out_6041342056914775001[35] = 0;
   out_6041342056914775001[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6041342056914775001[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6041342056914775001[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6041342056914775001[39] = 0;
   out_6041342056914775001[40] = 0;
   out_6041342056914775001[41] = 0;
   out_6041342056914775001[42] = 0;
   out_6041342056914775001[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6041342056914775001[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_6041342056914775001[45] = 0;
   out_6041342056914775001[46] = 0;
   out_6041342056914775001[47] = 0;
   out_6041342056914775001[48] = 0;
   out_6041342056914775001[49] = 0;
   out_6041342056914775001[50] = 0;
   out_6041342056914775001[51] = 0;
   out_6041342056914775001[52] = 0;
   out_6041342056914775001[53] = 0;
   out_6041342056914775001[54] = 0;
   out_6041342056914775001[55] = 0;
   out_6041342056914775001[56] = 0;
   out_6041342056914775001[57] = 1;
   out_6041342056914775001[58] = 0;
   out_6041342056914775001[59] = 0;
   out_6041342056914775001[60] = 0;
   out_6041342056914775001[61] = 0;
   out_6041342056914775001[62] = 0;
   out_6041342056914775001[63] = 0;
   out_6041342056914775001[64] = 0;
   out_6041342056914775001[65] = 0;
   out_6041342056914775001[66] = dt;
   out_6041342056914775001[67] = 0;
   out_6041342056914775001[68] = 0;
   out_6041342056914775001[69] = 0;
   out_6041342056914775001[70] = 0;
   out_6041342056914775001[71] = 0;
   out_6041342056914775001[72] = 0;
   out_6041342056914775001[73] = 0;
   out_6041342056914775001[74] = 0;
   out_6041342056914775001[75] = 0;
   out_6041342056914775001[76] = 1;
   out_6041342056914775001[77] = 0;
   out_6041342056914775001[78] = 0;
   out_6041342056914775001[79] = 0;
   out_6041342056914775001[80] = 0;
   out_6041342056914775001[81] = 0;
   out_6041342056914775001[82] = 0;
   out_6041342056914775001[83] = 0;
   out_6041342056914775001[84] = 0;
   out_6041342056914775001[85] = dt;
   out_6041342056914775001[86] = 0;
   out_6041342056914775001[87] = 0;
   out_6041342056914775001[88] = 0;
   out_6041342056914775001[89] = 0;
   out_6041342056914775001[90] = 0;
   out_6041342056914775001[91] = 0;
   out_6041342056914775001[92] = 0;
   out_6041342056914775001[93] = 0;
   out_6041342056914775001[94] = 0;
   out_6041342056914775001[95] = 1;
   out_6041342056914775001[96] = 0;
   out_6041342056914775001[97] = 0;
   out_6041342056914775001[98] = 0;
   out_6041342056914775001[99] = 0;
   out_6041342056914775001[100] = 0;
   out_6041342056914775001[101] = 0;
   out_6041342056914775001[102] = 0;
   out_6041342056914775001[103] = 0;
   out_6041342056914775001[104] = dt;
   out_6041342056914775001[105] = 0;
   out_6041342056914775001[106] = 0;
   out_6041342056914775001[107] = 0;
   out_6041342056914775001[108] = 0;
   out_6041342056914775001[109] = 0;
   out_6041342056914775001[110] = 0;
   out_6041342056914775001[111] = 0;
   out_6041342056914775001[112] = 0;
   out_6041342056914775001[113] = 0;
   out_6041342056914775001[114] = 1;
   out_6041342056914775001[115] = 0;
   out_6041342056914775001[116] = 0;
   out_6041342056914775001[117] = 0;
   out_6041342056914775001[118] = 0;
   out_6041342056914775001[119] = 0;
   out_6041342056914775001[120] = 0;
   out_6041342056914775001[121] = 0;
   out_6041342056914775001[122] = 0;
   out_6041342056914775001[123] = 0;
   out_6041342056914775001[124] = 0;
   out_6041342056914775001[125] = 0;
   out_6041342056914775001[126] = 0;
   out_6041342056914775001[127] = 0;
   out_6041342056914775001[128] = 0;
   out_6041342056914775001[129] = 0;
   out_6041342056914775001[130] = 0;
   out_6041342056914775001[131] = 0;
   out_6041342056914775001[132] = 0;
   out_6041342056914775001[133] = 1;
   out_6041342056914775001[134] = 0;
   out_6041342056914775001[135] = 0;
   out_6041342056914775001[136] = 0;
   out_6041342056914775001[137] = 0;
   out_6041342056914775001[138] = 0;
   out_6041342056914775001[139] = 0;
   out_6041342056914775001[140] = 0;
   out_6041342056914775001[141] = 0;
   out_6041342056914775001[142] = 0;
   out_6041342056914775001[143] = 0;
   out_6041342056914775001[144] = 0;
   out_6041342056914775001[145] = 0;
   out_6041342056914775001[146] = 0;
   out_6041342056914775001[147] = 0;
   out_6041342056914775001[148] = 0;
   out_6041342056914775001[149] = 0;
   out_6041342056914775001[150] = 0;
   out_6041342056914775001[151] = 0;
   out_6041342056914775001[152] = 1;
   out_6041342056914775001[153] = 0;
   out_6041342056914775001[154] = 0;
   out_6041342056914775001[155] = 0;
   out_6041342056914775001[156] = 0;
   out_6041342056914775001[157] = 0;
   out_6041342056914775001[158] = 0;
   out_6041342056914775001[159] = 0;
   out_6041342056914775001[160] = 0;
   out_6041342056914775001[161] = 0;
   out_6041342056914775001[162] = 0;
   out_6041342056914775001[163] = 0;
   out_6041342056914775001[164] = 0;
   out_6041342056914775001[165] = 0;
   out_6041342056914775001[166] = 0;
   out_6041342056914775001[167] = 0;
   out_6041342056914775001[168] = 0;
   out_6041342056914775001[169] = 0;
   out_6041342056914775001[170] = 0;
   out_6041342056914775001[171] = 1;
   out_6041342056914775001[172] = 0;
   out_6041342056914775001[173] = 0;
   out_6041342056914775001[174] = 0;
   out_6041342056914775001[175] = 0;
   out_6041342056914775001[176] = 0;
   out_6041342056914775001[177] = 0;
   out_6041342056914775001[178] = 0;
   out_6041342056914775001[179] = 0;
   out_6041342056914775001[180] = 0;
   out_6041342056914775001[181] = 0;
   out_6041342056914775001[182] = 0;
   out_6041342056914775001[183] = 0;
   out_6041342056914775001[184] = 0;
   out_6041342056914775001[185] = 0;
   out_6041342056914775001[186] = 0;
   out_6041342056914775001[187] = 0;
   out_6041342056914775001[188] = 0;
   out_6041342056914775001[189] = 0;
   out_6041342056914775001[190] = 1;
   out_6041342056914775001[191] = 0;
   out_6041342056914775001[192] = 0;
   out_6041342056914775001[193] = 0;
   out_6041342056914775001[194] = 0;
   out_6041342056914775001[195] = 0;
   out_6041342056914775001[196] = 0;
   out_6041342056914775001[197] = 0;
   out_6041342056914775001[198] = 0;
   out_6041342056914775001[199] = 0;
   out_6041342056914775001[200] = 0;
   out_6041342056914775001[201] = 0;
   out_6041342056914775001[202] = 0;
   out_6041342056914775001[203] = 0;
   out_6041342056914775001[204] = 0;
   out_6041342056914775001[205] = 0;
   out_6041342056914775001[206] = 0;
   out_6041342056914775001[207] = 0;
   out_6041342056914775001[208] = 0;
   out_6041342056914775001[209] = 1;
   out_6041342056914775001[210] = 0;
   out_6041342056914775001[211] = 0;
   out_6041342056914775001[212] = 0;
   out_6041342056914775001[213] = 0;
   out_6041342056914775001[214] = 0;
   out_6041342056914775001[215] = 0;
   out_6041342056914775001[216] = 0;
   out_6041342056914775001[217] = 0;
   out_6041342056914775001[218] = 0;
   out_6041342056914775001[219] = 0;
   out_6041342056914775001[220] = 0;
   out_6041342056914775001[221] = 0;
   out_6041342056914775001[222] = 0;
   out_6041342056914775001[223] = 0;
   out_6041342056914775001[224] = 0;
   out_6041342056914775001[225] = 0;
   out_6041342056914775001[226] = 0;
   out_6041342056914775001[227] = 0;
   out_6041342056914775001[228] = 1;
   out_6041342056914775001[229] = 0;
   out_6041342056914775001[230] = 0;
   out_6041342056914775001[231] = 0;
   out_6041342056914775001[232] = 0;
   out_6041342056914775001[233] = 0;
   out_6041342056914775001[234] = 0;
   out_6041342056914775001[235] = 0;
   out_6041342056914775001[236] = 0;
   out_6041342056914775001[237] = 0;
   out_6041342056914775001[238] = 0;
   out_6041342056914775001[239] = 0;
   out_6041342056914775001[240] = 0;
   out_6041342056914775001[241] = 0;
   out_6041342056914775001[242] = 0;
   out_6041342056914775001[243] = 0;
   out_6041342056914775001[244] = 0;
   out_6041342056914775001[245] = 0;
   out_6041342056914775001[246] = 0;
   out_6041342056914775001[247] = 1;
   out_6041342056914775001[248] = 0;
   out_6041342056914775001[249] = 0;
   out_6041342056914775001[250] = 0;
   out_6041342056914775001[251] = 0;
   out_6041342056914775001[252] = 0;
   out_6041342056914775001[253] = 0;
   out_6041342056914775001[254] = 0;
   out_6041342056914775001[255] = 0;
   out_6041342056914775001[256] = 0;
   out_6041342056914775001[257] = 0;
   out_6041342056914775001[258] = 0;
   out_6041342056914775001[259] = 0;
   out_6041342056914775001[260] = 0;
   out_6041342056914775001[261] = 0;
   out_6041342056914775001[262] = 0;
   out_6041342056914775001[263] = 0;
   out_6041342056914775001[264] = 0;
   out_6041342056914775001[265] = 0;
   out_6041342056914775001[266] = 1;
   out_6041342056914775001[267] = 0;
   out_6041342056914775001[268] = 0;
   out_6041342056914775001[269] = 0;
   out_6041342056914775001[270] = 0;
   out_6041342056914775001[271] = 0;
   out_6041342056914775001[272] = 0;
   out_6041342056914775001[273] = 0;
   out_6041342056914775001[274] = 0;
   out_6041342056914775001[275] = 0;
   out_6041342056914775001[276] = 0;
   out_6041342056914775001[277] = 0;
   out_6041342056914775001[278] = 0;
   out_6041342056914775001[279] = 0;
   out_6041342056914775001[280] = 0;
   out_6041342056914775001[281] = 0;
   out_6041342056914775001[282] = 0;
   out_6041342056914775001[283] = 0;
   out_6041342056914775001[284] = 0;
   out_6041342056914775001[285] = 1;
   out_6041342056914775001[286] = 0;
   out_6041342056914775001[287] = 0;
   out_6041342056914775001[288] = 0;
   out_6041342056914775001[289] = 0;
   out_6041342056914775001[290] = 0;
   out_6041342056914775001[291] = 0;
   out_6041342056914775001[292] = 0;
   out_6041342056914775001[293] = 0;
   out_6041342056914775001[294] = 0;
   out_6041342056914775001[295] = 0;
   out_6041342056914775001[296] = 0;
   out_6041342056914775001[297] = 0;
   out_6041342056914775001[298] = 0;
   out_6041342056914775001[299] = 0;
   out_6041342056914775001[300] = 0;
   out_6041342056914775001[301] = 0;
   out_6041342056914775001[302] = 0;
   out_6041342056914775001[303] = 0;
   out_6041342056914775001[304] = 1;
   out_6041342056914775001[305] = 0;
   out_6041342056914775001[306] = 0;
   out_6041342056914775001[307] = 0;
   out_6041342056914775001[308] = 0;
   out_6041342056914775001[309] = 0;
   out_6041342056914775001[310] = 0;
   out_6041342056914775001[311] = 0;
   out_6041342056914775001[312] = 0;
   out_6041342056914775001[313] = 0;
   out_6041342056914775001[314] = 0;
   out_6041342056914775001[315] = 0;
   out_6041342056914775001[316] = 0;
   out_6041342056914775001[317] = 0;
   out_6041342056914775001[318] = 0;
   out_6041342056914775001[319] = 0;
   out_6041342056914775001[320] = 0;
   out_6041342056914775001[321] = 0;
   out_6041342056914775001[322] = 0;
   out_6041342056914775001[323] = 1;
}
void h_4(double *state, double *unused, double *out_3042131446626966500) {
   out_3042131446626966500[0] = state[6] + state[9];
   out_3042131446626966500[1] = state[7] + state[10];
   out_3042131446626966500[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_1496638562704873856) {
   out_1496638562704873856[0] = 0;
   out_1496638562704873856[1] = 0;
   out_1496638562704873856[2] = 0;
   out_1496638562704873856[3] = 0;
   out_1496638562704873856[4] = 0;
   out_1496638562704873856[5] = 0;
   out_1496638562704873856[6] = 1;
   out_1496638562704873856[7] = 0;
   out_1496638562704873856[8] = 0;
   out_1496638562704873856[9] = 1;
   out_1496638562704873856[10] = 0;
   out_1496638562704873856[11] = 0;
   out_1496638562704873856[12] = 0;
   out_1496638562704873856[13] = 0;
   out_1496638562704873856[14] = 0;
   out_1496638562704873856[15] = 0;
   out_1496638562704873856[16] = 0;
   out_1496638562704873856[17] = 0;
   out_1496638562704873856[18] = 0;
   out_1496638562704873856[19] = 0;
   out_1496638562704873856[20] = 0;
   out_1496638562704873856[21] = 0;
   out_1496638562704873856[22] = 0;
   out_1496638562704873856[23] = 0;
   out_1496638562704873856[24] = 0;
   out_1496638562704873856[25] = 1;
   out_1496638562704873856[26] = 0;
   out_1496638562704873856[27] = 0;
   out_1496638562704873856[28] = 1;
   out_1496638562704873856[29] = 0;
   out_1496638562704873856[30] = 0;
   out_1496638562704873856[31] = 0;
   out_1496638562704873856[32] = 0;
   out_1496638562704873856[33] = 0;
   out_1496638562704873856[34] = 0;
   out_1496638562704873856[35] = 0;
   out_1496638562704873856[36] = 0;
   out_1496638562704873856[37] = 0;
   out_1496638562704873856[38] = 0;
   out_1496638562704873856[39] = 0;
   out_1496638562704873856[40] = 0;
   out_1496638562704873856[41] = 0;
   out_1496638562704873856[42] = 0;
   out_1496638562704873856[43] = 0;
   out_1496638562704873856[44] = 1;
   out_1496638562704873856[45] = 0;
   out_1496638562704873856[46] = 0;
   out_1496638562704873856[47] = 1;
   out_1496638562704873856[48] = 0;
   out_1496638562704873856[49] = 0;
   out_1496638562704873856[50] = 0;
   out_1496638562704873856[51] = 0;
   out_1496638562704873856[52] = 0;
   out_1496638562704873856[53] = 0;
}
void h_10(double *state, double *unused, double *out_2775567503613228806) {
   out_2775567503613228806[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_2775567503613228806[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_2775567503613228806[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_2780045028419684985) {
   out_2780045028419684985[0] = 0;
   out_2780045028419684985[1] = 9.8100000000000005*cos(state[1]);
   out_2780045028419684985[2] = 0;
   out_2780045028419684985[3] = 0;
   out_2780045028419684985[4] = -state[8];
   out_2780045028419684985[5] = state[7];
   out_2780045028419684985[6] = 0;
   out_2780045028419684985[7] = state[5];
   out_2780045028419684985[8] = -state[4];
   out_2780045028419684985[9] = 0;
   out_2780045028419684985[10] = 0;
   out_2780045028419684985[11] = 0;
   out_2780045028419684985[12] = 1;
   out_2780045028419684985[13] = 0;
   out_2780045028419684985[14] = 0;
   out_2780045028419684985[15] = 1;
   out_2780045028419684985[16] = 0;
   out_2780045028419684985[17] = 0;
   out_2780045028419684985[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_2780045028419684985[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_2780045028419684985[20] = 0;
   out_2780045028419684985[21] = state[8];
   out_2780045028419684985[22] = 0;
   out_2780045028419684985[23] = -state[6];
   out_2780045028419684985[24] = -state[5];
   out_2780045028419684985[25] = 0;
   out_2780045028419684985[26] = state[3];
   out_2780045028419684985[27] = 0;
   out_2780045028419684985[28] = 0;
   out_2780045028419684985[29] = 0;
   out_2780045028419684985[30] = 0;
   out_2780045028419684985[31] = 1;
   out_2780045028419684985[32] = 0;
   out_2780045028419684985[33] = 0;
   out_2780045028419684985[34] = 1;
   out_2780045028419684985[35] = 0;
   out_2780045028419684985[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_2780045028419684985[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_2780045028419684985[38] = 0;
   out_2780045028419684985[39] = -state[7];
   out_2780045028419684985[40] = state[6];
   out_2780045028419684985[41] = 0;
   out_2780045028419684985[42] = state[4];
   out_2780045028419684985[43] = -state[3];
   out_2780045028419684985[44] = 0;
   out_2780045028419684985[45] = 0;
   out_2780045028419684985[46] = 0;
   out_2780045028419684985[47] = 0;
   out_2780045028419684985[48] = 0;
   out_2780045028419684985[49] = 0;
   out_2780045028419684985[50] = 1;
   out_2780045028419684985[51] = 0;
   out_2780045028419684985[52] = 0;
   out_2780045028419684985[53] = 1;
}
void h_13(double *state, double *unused, double *out_8486620153364892703) {
   out_8486620153364892703[0] = state[3];
   out_8486620153364892703[1] = state[4];
   out_8486620153364892703[2] = state[5];
}
void H_13(double *state, double *unused, double *out_4708912388037206657) {
   out_4708912388037206657[0] = 0;
   out_4708912388037206657[1] = 0;
   out_4708912388037206657[2] = 0;
   out_4708912388037206657[3] = 1;
   out_4708912388037206657[4] = 0;
   out_4708912388037206657[5] = 0;
   out_4708912388037206657[6] = 0;
   out_4708912388037206657[7] = 0;
   out_4708912388037206657[8] = 0;
   out_4708912388037206657[9] = 0;
   out_4708912388037206657[10] = 0;
   out_4708912388037206657[11] = 0;
   out_4708912388037206657[12] = 0;
   out_4708912388037206657[13] = 0;
   out_4708912388037206657[14] = 0;
   out_4708912388037206657[15] = 0;
   out_4708912388037206657[16] = 0;
   out_4708912388037206657[17] = 0;
   out_4708912388037206657[18] = 0;
   out_4708912388037206657[19] = 0;
   out_4708912388037206657[20] = 0;
   out_4708912388037206657[21] = 0;
   out_4708912388037206657[22] = 1;
   out_4708912388037206657[23] = 0;
   out_4708912388037206657[24] = 0;
   out_4708912388037206657[25] = 0;
   out_4708912388037206657[26] = 0;
   out_4708912388037206657[27] = 0;
   out_4708912388037206657[28] = 0;
   out_4708912388037206657[29] = 0;
   out_4708912388037206657[30] = 0;
   out_4708912388037206657[31] = 0;
   out_4708912388037206657[32] = 0;
   out_4708912388037206657[33] = 0;
   out_4708912388037206657[34] = 0;
   out_4708912388037206657[35] = 0;
   out_4708912388037206657[36] = 0;
   out_4708912388037206657[37] = 0;
   out_4708912388037206657[38] = 0;
   out_4708912388037206657[39] = 0;
   out_4708912388037206657[40] = 0;
   out_4708912388037206657[41] = 1;
   out_4708912388037206657[42] = 0;
   out_4708912388037206657[43] = 0;
   out_4708912388037206657[44] = 0;
   out_4708912388037206657[45] = 0;
   out_4708912388037206657[46] = 0;
   out_4708912388037206657[47] = 0;
   out_4708912388037206657[48] = 0;
   out_4708912388037206657[49] = 0;
   out_4708912388037206657[50] = 0;
   out_4708912388037206657[51] = 0;
   out_4708912388037206657[52] = 0;
   out_4708912388037206657[53] = 0;
}
void h_14(double *state, double *unused, double *out_3864446336470039484) {
   out_3864446336470039484[0] = state[6];
   out_3864446336470039484[1] = state[7];
   out_3864446336470039484[2] = state[8];
}
void H_14(double *state, double *unused, double *out_1061522036059990257) {
   out_1061522036059990257[0] = 0;
   out_1061522036059990257[1] = 0;
   out_1061522036059990257[2] = 0;
   out_1061522036059990257[3] = 0;
   out_1061522036059990257[4] = 0;
   out_1061522036059990257[5] = 0;
   out_1061522036059990257[6] = 1;
   out_1061522036059990257[7] = 0;
   out_1061522036059990257[8] = 0;
   out_1061522036059990257[9] = 0;
   out_1061522036059990257[10] = 0;
   out_1061522036059990257[11] = 0;
   out_1061522036059990257[12] = 0;
   out_1061522036059990257[13] = 0;
   out_1061522036059990257[14] = 0;
   out_1061522036059990257[15] = 0;
   out_1061522036059990257[16] = 0;
   out_1061522036059990257[17] = 0;
   out_1061522036059990257[18] = 0;
   out_1061522036059990257[19] = 0;
   out_1061522036059990257[20] = 0;
   out_1061522036059990257[21] = 0;
   out_1061522036059990257[22] = 0;
   out_1061522036059990257[23] = 0;
   out_1061522036059990257[24] = 0;
   out_1061522036059990257[25] = 1;
   out_1061522036059990257[26] = 0;
   out_1061522036059990257[27] = 0;
   out_1061522036059990257[28] = 0;
   out_1061522036059990257[29] = 0;
   out_1061522036059990257[30] = 0;
   out_1061522036059990257[31] = 0;
   out_1061522036059990257[32] = 0;
   out_1061522036059990257[33] = 0;
   out_1061522036059990257[34] = 0;
   out_1061522036059990257[35] = 0;
   out_1061522036059990257[36] = 0;
   out_1061522036059990257[37] = 0;
   out_1061522036059990257[38] = 0;
   out_1061522036059990257[39] = 0;
   out_1061522036059990257[40] = 0;
   out_1061522036059990257[41] = 0;
   out_1061522036059990257[42] = 0;
   out_1061522036059990257[43] = 0;
   out_1061522036059990257[44] = 1;
   out_1061522036059990257[45] = 0;
   out_1061522036059990257[46] = 0;
   out_1061522036059990257[47] = 0;
   out_1061522036059990257[48] = 0;
   out_1061522036059990257[49] = 0;
   out_1061522036059990257[50] = 0;
   out_1061522036059990257[51] = 0;
   out_1061522036059990257[52] = 0;
   out_1061522036059990257[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_3288415244471962854) {
  err_fun(nom_x, delta_x, out_3288415244471962854);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_2706393179994234815) {
  inv_err_fun(nom_x, true_x, out_2706393179994234815);
}
void pose_H_mod_fun(double *state, double *out_298691080821975752) {
  H_mod_fun(state, out_298691080821975752);
}
void pose_f_fun(double *state, double dt, double *out_3084202619553510425) {
  f_fun(state,  dt, out_3084202619553510425);
}
void pose_F_fun(double *state, double dt, double *out_6041342056914775001) {
  F_fun(state,  dt, out_6041342056914775001);
}
void pose_h_4(double *state, double *unused, double *out_3042131446626966500) {
  h_4(state, unused, out_3042131446626966500);
}
void pose_H_4(double *state, double *unused, double *out_1496638562704873856) {
  H_4(state, unused, out_1496638562704873856);
}
void pose_h_10(double *state, double *unused, double *out_2775567503613228806) {
  h_10(state, unused, out_2775567503613228806);
}
void pose_H_10(double *state, double *unused, double *out_2780045028419684985) {
  H_10(state, unused, out_2780045028419684985);
}
void pose_h_13(double *state, double *unused, double *out_8486620153364892703) {
  h_13(state, unused, out_8486620153364892703);
}
void pose_H_13(double *state, double *unused, double *out_4708912388037206657) {
  H_13(state, unused, out_4708912388037206657);
}
void pose_h_14(double *state, double *unused, double *out_3864446336470039484) {
  h_14(state, unused, out_3864446336470039484);
}
void pose_H_14(double *state, double *unused, double *out_1061522036059990257) {
  H_14(state, unused, out_1061522036059990257);
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
