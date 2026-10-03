
#include <math.h>
#include <limits.h>
/* events sorted by (group, t); A_i = sum_{j<i, same group} e^{-beta(t_i-t_j)}, B_i = sum (t_i-t_j) e^{...} */
void exp_sums(long n, const double* t, const long* g, double beta, double* A, double* B) {
  double a = 0.0, b = 0.0;
  for (long i = 0; i < n; i++) {
    if (i == 0 || g[i] != g[i-1]) { a = 0.0; b = 0.0; }
    else {
      double dt = t[i] - t[i-1];
      double e = exp(-beta * dt);
      b = e * (b + dt * (1.0 + a));
      a = e * (a + 1.0);
    }
    A[i] = a;
    if (B) B[i] = b;
  }
}
/* X_i = sum_{x in same group, x < t_i} e^{-delta (t_i - x)}; events and exo both sorted by (group, time) */
void exo_sums(long n, const double* t, const long* g, long m, const double* x, const long* gx,
              double delta, double* X) {
  long j = 0; double s = 0.0, tref = 0.0; int have = 0; long gcur = LONG_MIN;
  for (long i = 0; i < n; i++) {
    if (g[i] != gcur) { gcur = g[i]; s = 0.0; have = 0; while (j < m && gx[j] < gcur) j++; }
    while (j < m && gx[j] == gcur && x[j] < t[i]) {
      if (have) s *= exp(-delta * (x[j] - tref));
      s += 1.0; tref = x[j]; have = 1; j++;
    }
    X[i] = have ? s * exp(-delta * (t[i] - tref)) : 0.0;
  }
}
/* For events with u[i] >= 0 pick a parent j < i in the same group with prob ∝ e^{-beta (t_i - t_j)}. */
void sample_parents(long n, const double* t, const long* g, double beta, const double* A,
                    const double* u, long* parent) {
  for (long i = 0; i < n; i++) {
    parent[i] = -1;
    if (u[i] < 0.0) continue;
    double target = u[i] * A[i], cum = 0.0; long j = i - 1, last = -1;
    while (j >= 0 && g[j] == g[i]) {
      cum += exp(-beta * (t[i] - t[j])); last = j;
      if (cum >= target) { parent[i] = j; break; }
      j--;
    }
    if (parent[i] < 0) parent[i] = last;
  }
}
