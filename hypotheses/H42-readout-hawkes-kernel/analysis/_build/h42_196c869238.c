
#include <math.h>
#include <limits.h>
/* X_i = sum_{j: gx_j == g_i, x_j < t_i} w_j exp(-beta (t_i - x_j)); events sorted by (g,t), sources by (gx,x) */
void wexp_sums(long n, const double* t, const long* g, long m, const double* x, const long* gx, const double* w,
               double beta, double* X) {
  long j = 0; double s = 0.0, tref = 0.0; int have = 0; long gcur = LONG_MIN;
  for (long i = 0; i < n; i++) {
    if (g[i] != gcur) { gcur = g[i]; s = 0.0; have = 0; while (j < m && gx[j] < gcur) j++; }
    while (j < m && gx[j] == gcur && x[j] < t[i]) {
      if (have) s *= exp(-beta * (x[j] - tref));
      s += w[j]; tref = x[j]; have = 1; j++;
    }
    X[i] = have ? s * exp(-beta * (t[i] - tref)) : 0.0;
  }
}
