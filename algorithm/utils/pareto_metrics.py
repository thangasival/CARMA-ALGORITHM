"""
Multi-Objective Pareto Quality Metrics
=======================================
Standard MOEA evaluation metrics for 4-objective optimization.

Implements:
  - Hypervolume (HV)          — dominated space volume, higher is better
  - Inverted Generational Distance (IGD) — front closeness to reference, lower is better
  - Generational Distance (GD) — convergence to reference, lower is better
  - Spread (Δ)                — diversity / uniformity of solutions, lower is better

These metrics are standard in the MOEA literature (Zitzler et al. 2003,
Deb et al. 2002) and required for comparison against NSGA-III, MOEA/D, RVEA.

Monte Carlo HV is used for n_obj >= 3 (exact WFG is O(n^(M-2) log n), too
complex to implement here; MC with 500k samples gives <1% error for ≤4 obj).

References
----------
- Zitzler, E., Thiele, L., Laumanns, M., Fonseca, C.M. & da Fonseca, V.G.
  (2003). Performance assessment of multiobjective optimizers. IEEE TEVC.
- While, L., Hingston, P., Barone, L. & Huband, S. (2006). A faster algorithm
  for calculating hypervolume. IEEE TEVC, 10(1), 29-38.
- Coello, C.A. & Sierra, M.R. (2004). A study of the parallelization of a
  coevolutionary multi-objective evolutionary algorithm. MICAI 2004.
"""
from __future__ import annotations

import numpy as np
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Core metric functions
# ---------------------------------------------------------------------------

def hypervolume(
    pareto_front: np.ndarray,
    ref_point: np.ndarray,
    n_samples: int = 500_000,
    seed: int = 42,
) -> float:
    """
    Hypervolume indicator (dominated hypervolume).

    For 2 objectives: exact sweep algorithm O(n log n).
    For 3-4 objectives: Monte Carlo estimator with 500k samples.

    Parameters
    ----------
    pareto_front : (n, M) array — objective values of approximated Pareto front
    ref_point    : (M,) array  — reference (nadir) point, must dominate all solutions
    n_samples    : MC sample count (only for M >= 3)
    seed         : random seed for reproducibility

    Returns
    -------
    float : hypervolume (higher is better; 0 if no solutions dominate ref_point)
    """
    if pareto_front is None or len(pareto_front) == 0:
        return 0.0

    pf = np.asarray(pareto_front, dtype=float)
    ref = np.asarray(ref_point, dtype=float)

    # Keep only non-dominated points that strictly dominate the reference
    pf = _filter_nondominated(pf)
    valid = np.all(pf < ref, axis=1)
    pf = pf[valid]
    if len(pf) == 0:
        return 0.0

    n_obj = pf.shape[1]
    if n_obj == 2:
        return _hv_2d_exact(pf, ref)
    else:
        return _hv_monte_carlo(pf, ref, n_samples=n_samples, seed=seed)


def _hv_2d_exact(pf: np.ndarray, ref: np.ndarray) -> float:
    """Exact 2D hypervolume via sweep line. O(n log n)."""
    # Sort by first objective ascending
    pf = pf[np.argsort(pf[:, 0])]
    hv = 0.0
    prev_y = ref[1]
    for i in range(len(pf) - 1, -1, -1):
        if pf[i, 1] < prev_y:
            hv += (ref[0] - pf[i, 0]) * (prev_y - pf[i, 1])
            prev_y = pf[i, 1]
    return float(hv)


def _hv_monte_carlo(
    pf: np.ndarray,
    ref: np.ndarray,
    n_samples: int = 500_000,
    seed: int = 42,
) -> float:
    """
    Monte Carlo hypervolume estimator.

    Sample n_samples points uniformly in [ideal(pf), ref].
    Fraction dominated by at least one PF point × total box volume = HV.

    Error bound: ~1/sqrt(n_samples) relative, so 500k → ~0.14% error.
    """
    rng = np.random.default_rng(seed)
    ideal = pf.min(axis=0)
    box_vol = float(np.prod(ref - ideal))
    if box_vol <= 0:
        return 0.0

    # Batch sampling to limit memory: 100k at a time
    batch = min(n_samples, 100_000)
    n_batches = (n_samples + batch - 1) // batch
    dominated_count = 0

    for _ in range(n_batches):
        samples = rng.uniform(ideal, ref, size=(batch, pf.shape[1]))
        # A sample s is dominated if ∃ p ∈ PF: p ≤ s componentwise
        dominated = np.any(
            np.all(pf[:, np.newaxis, :] <= samples[np.newaxis, :, :], axis=2),
            axis=0,
        )
        dominated_count += dominated.sum()

    return float(box_vol * dominated_count / (n_batches * batch))


def igd(
    pareto_approx: np.ndarray,
    reference_front: np.ndarray,
    normalize: bool = True,
) -> float:
    """
    Inverted Generational Distance.

    IGD = (1/|P*|) * Σ_{p ∈ P*}  min_{q ∈ PF} ||p − q||₂

    Lower is better (0 = perfect match to reference front).

    Parameters
    ----------
    pareto_approx   : (n, M) approximated Pareto front
    reference_front : (m, M) reference (true) Pareto front
    normalize       : if True, normalize both fronts to [0,1] per objective
                      using the union ideal/nadir before computing distances

    Returns
    -------
    float : IGD value (lower is better)
    """
    if len(pareto_approx) == 0 or len(reference_front) == 0:
        return np.inf

    pa = np.asarray(pareto_approx, dtype=float)
    rf = np.asarray(reference_front, dtype=float)

    if normalize:
        combined = np.vstack([pa, rf])
        ideal = combined.min(axis=0)
        nadir = combined.max(axis=0)
        denom = nadir - ideal
        denom[denom < 1e-10] = 1.0
        pa = (pa - ideal) / denom
        rf = (rf - ideal) / denom

    # For each reference point, find distance to nearest approximation point
    dists = np.array([
        np.linalg.norm(pa - ref_pt, axis=1).min()
        for ref_pt in rf
    ])
    return float(dists.mean())


def generational_distance(
    pareto_approx: np.ndarray,
    reference_front: np.ndarray,
    normalize: bool = True,
) -> float:
    """
    Generational Distance (GD).

    GD = (1/|PF|) * Σ_{q ∈ PF}  min_{p ∈ P*} ||q − p||₂

    Measures how well the approximation converges to the reference front.
    Lower is better.
    """
    if len(pareto_approx) == 0 or len(reference_front) == 0:
        return np.inf

    pa = np.asarray(pareto_approx, dtype=float)
    rf = np.asarray(reference_front, dtype=float)

    if normalize:
        combined = np.vstack([pa, rf])
        ideal = combined.min(axis=0)
        nadir = combined.max(axis=0)
        denom = nadir - ideal
        denom[denom < 1e-10] = 1.0
        pa = (pa - ideal) / denom
        rf = (rf - ideal) / denom

    dists = np.array([
        np.linalg.norm(rf - approx_pt, axis=1).min()
        for approx_pt in pa
    ])
    return float(dists.mean())


def spread(pareto_front: np.ndarray) -> float:
    """
    Spread (Δ) — solution diversity metric.

    Extended for M objectives using mean nearest-neighbor distance.
    Δ = Σ|d_i − d̄| / (n × d̄)

    where d_i = distance to nearest neighbour for solution i,
    d̄ = mean of d_i.

    Interpretation: 0 = perfectly uniform distribution, higher = more clustered.
    The metric is normalized so it is scale-independent.

    Returns
    -------
    float : spread value ∈ [0, ∞), lower is better
    """
    if len(pareto_front) < 3:
        return 0.0

    pf = np.asarray(pareto_front, dtype=float)

    # Normalize to [0, 1] per objective
    mn, mx = pf.min(axis=0), pf.max(axis=0)
    rng = mx - mn
    rng[rng < 1e-10] = 1.0
    pf_norm = (pf - mn) / rng

    # Compute nearest-neighbour distance for each point
    nn_dists = np.array([
        np.linalg.norm(
            np.delete(pf_norm, i, axis=0) - pf_norm[i], axis=1
        ).min()
        for i in range(len(pf_norm))
    ])

    d_mean = nn_dists.mean()
    if d_mean < 1e-12:
        return 0.0

    return float(np.sum(np.abs(nn_dists - d_mean)) / (len(nn_dists) * d_mean))


# ---------------------------------------------------------------------------
# Composite evaluation
# ---------------------------------------------------------------------------

def compute_all_metrics(
    pareto_approx: np.ndarray,
    reference_front: Optional[np.ndarray] = None,
    ref_point: Optional[np.ndarray] = None,
    hv_samples: int = 200_000,
) -> Dict[str, float]:
    """
    Compute all standard Pareto quality metrics for a given approximation.

    Parameters
    ----------
    pareto_approx   : (n, M) approximated Pareto front (objective values)
    reference_front : (m, M) reference front for IGD/GD. If None, skipped.
    ref_point       : (M,) nadir point for HV. If None, auto-computed as
                      1.1 × column-wise max of pareto_approx.
    hv_samples      : MC sample count for HV (lower = faster, less precise)

    Returns
    -------
    dict with keys: hv, spread, n_solutions, [igd, gd if reference given]
    """
    if pareto_approx is None or len(pareto_approx) == 0:
        result = {"hv": 0.0, "spread": 0.0, "n_solutions": 0}
        if reference_front is not None:
            result.update({"igd": np.inf, "gd": np.inf})
        return result

    pf = np.asarray(pareto_approx, dtype=float)

    if ref_point is None:
        ref_point = pf.max(axis=0) * 1.1

    result = {
        "hv":          hypervolume(pf, ref_point, n_samples=hv_samples),
        "spread":      spread(pf),
        "n_solutions": int(len(pf)),
    }

    if reference_front is not None and len(reference_front) > 0:
        rf = np.asarray(reference_front, dtype=float)
        result["igd"] = igd(pf, rf)
        result["gd"]  = generational_distance(pf, rf)

    return result


# ---------------------------------------------------------------------------
# Reference front utilities
# ---------------------------------------------------------------------------

def build_reference_front(
    all_fronts: List[np.ndarray],
) -> np.ndarray:
    """
    Build a combined reference front from multiple approximated fronts.

    Pools all solutions from all runs/algorithms, then extracts the
    overall non-dominated set. Used as a shared reference P* when
    a true Pareto front is unavailable.

    Parameters
    ----------
    all_fronts : list of (n_i, M) arrays from different runs/algorithms

    Returns
    -------
    np.ndarray : (k, M) non-dominated reference front
    """
    if not all_fronts:
        return np.empty((0,))
    combined = np.vstack([np.asarray(f, dtype=float) for f in all_fronts if len(f) > 0])
    return _filter_nondominated(combined)


def normalise_front(
    front: np.ndarray,
    ideal: Optional[np.ndarray] = None,
    nadir: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Normalize a Pareto front to [0, 1] per objective."""
    pf = np.asarray(front, dtype=float)
    if ideal is None:
        ideal = pf.min(axis=0)
    if nadir is None:
        nadir = pf.max(axis=0)
    denom = nadir - ideal
    denom[denom < 1e-10] = 1.0
    return (pf - ideal) / denom


# ---------------------------------------------------------------------------
# Non-dominated filter
# ---------------------------------------------------------------------------

def _filter_nondominated(points: np.ndarray) -> np.ndarray:
    """
    Return only non-dominated points from a set.

    A point p is dominated if ∃ q ≠ p: q ≤ p componentwise AND q < p somewhere.
    O(n²M) — adequate for fronts with ≤ 500 solutions.
    """
    pts = np.asarray(points, dtype=float)
    n = len(pts)
    is_dominated = np.zeros(n, dtype=bool)
    for i in range(n):
        if is_dominated[i]:
            continue
        for j in range(n):
            if i == j or is_dominated[j]:
                continue
            if np.all(pts[j] <= pts[i]) and np.any(pts[j] < pts[i]):
                is_dominated[i] = True
                break
    return pts[~is_dominated]


# ---------------------------------------------------------------------------
# Convenience: extract fitness matrix from DEAP population
# ---------------------------------------------------------------------------

def pareto_fitnesses(pareto_front_individuals: list) -> np.ndarray:
    """
    Extract (n, M) objective matrix from a list of DEAP individuals.

    Parameters
    ----------
    pareto_front_individuals : list of DEAP Individual objects with .fitness.values

    Returns
    -------
    np.ndarray : (n, M) float array of objective values
    """
    if not pareto_front_individuals:
        return np.empty((0, 4))
    return np.array([ind.fitness.values for ind in pareto_front_individuals])
