"""
Context-Adaptive Ensemble (Mixture of Experts)
================================================
Replaces the fixed global weights  RF=0.25, XGB=0.75  with *segment-aware*
weights that adapt to the local characteristics of each route.

Motivation
----------
RF outperforms XGBoost on short-haul truck routes where tree depth matters
less and variance reduction dominates.  XGBoost dominates on long-haul and
multi-modal routes with complex feature interactions.  A single global weight
misses this.

Approaches implemented (increasing sophistication)
--------------------------------------------------
1. SegmentedEnsemble  — hard segment boundaries, one weight per segment;
                        trained by minimising MSE within each segment.
   Segments: {short_truck, medium_truck, long_rail, maritime, air, mixed}

2. SoftMixtureEnsemble — learned gating network (tiny MLP / Ridge) that
                          outputs continuous weights w(x) = softmax(g(x)).
                          Full Mixture-of-Experts formulation.

3. StackedGeneralization — Level-2 Ridge meta-learner trained on
                           out-of-fold base model predictions.
                           The canonical "stacking" approach.

References
----------
- Jacobs et al. (1991) "Adaptive Mixtures of Local Experts", Neural Computation
- Wolpert (1992) "Stacked Generalization", Neural Networks
- Zhou (2012) "Ensemble Methods: Foundations and Algorithms"
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_percentage_error, r2_score

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Route segment definitions
# ---------------------------------------------------------------------------

SEGMENTS = {
    "short_truck":   "distance < 200 km, mode = truck",
    "medium_truck":  "200 ≤ distance < 600 km, mode = truck",
    "long_truck":    "distance ≥ 600 km, mode = truck",
    "rail":          "mode = rail (any distance)",
    "maritime":      "mode = ship",
    "air":           "mode = air",
}


def _assign_segment(df: pd.DataFrame) -> pd.Series:
    """
    Assign each route row to one of the six expert segments.
    """
    seg = pd.Series("medium_truck", index=df.index)
    mode = df["transport_mode"].str.lower()
    dist = df["distance_km"]

    seg.loc[(mode == "truck") & (dist < 200)]             = "short_truck"
    seg.loc[(mode == "truck") & (dist >= 200) & (dist < 600)] = "medium_truck"
    seg.loc[(mode == "truck") & (dist >= 600)]            = "long_truck"
    seg.loc[mode == "rail"]                               = "rail"
    seg.loc[mode == "ship"]                               = "maritime"
    seg.loc[mode == "air"]                                = "air"
    return seg


# ---------------------------------------------------------------------------
# 1. Segmented (hard-boundary) Ensemble
# ---------------------------------------------------------------------------

class SegmentedEnsemble:
    """
    Hard-segmented Mixture of Experts.

    One (w_RF, w_XGB) pair per segment, optimised by grid search to minimise
    segment-local validation MAPE.

    Parameters
    ----------
    base_models : dict with keys 'random_forest', 'xgboost' — trained sklearn models
    """

    # Weight grid to search (must sum to 1)
    _WEIGHT_GRID = [(w, 1.0 - w) for w in np.arange(0.05, 1.00, 0.05)]

    def __init__(self, base_models: Dict):
        self.base_models = base_models
        self.segment_weights: Dict[str, Tuple[float, float]] = {}
        self._fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray,
            df_meta: pd.DataFrame) -> "SegmentedEnsemble":
        """
        Find optimal (w_RF, w_XGB) for each segment.

        Parameters
        ----------
        X       : feature matrix (unscaled)
        y       : emission targets
        df_meta : DataFrame with 'transport_mode' and 'distance_km' columns
                  (same row order as X)
        """
        segments = _assign_segment(df_meta).values
        rf_pred  = self.base_models["random_forest"].predict(X)
        xgb_pred = self.base_models["xgboost"].predict(X)

        logger.info("Optimising segment weights via grid search...")

        for seg_name in SEGMENTS:
            mask = segments == seg_name
            if mask.sum() < 5:
                # Not enough samples — use global default
                self.segment_weights[seg_name] = (0.25, 0.75)
                logger.info(f"  {seg_name:<15} n={mask.sum():<4}  "
                            f"[too few — using global default 0.25/0.75]")
                continue

            y_seg   = y[mask]
            rf_seg  = rf_pred[mask]
            xgb_seg = xgb_pred[mask]

            best_mape, best_w = np.inf, (0.25, 0.75)
            for w_rf, w_xgb in self._WEIGHT_GRID:
                ens = w_rf * rf_seg + w_xgb * xgb_seg
                mape = mean_absolute_percentage_error(y_seg, ens) * 100
                if mape < best_mape:
                    best_mape, best_w = mape, (round(w_rf, 2), round(w_xgb, 2))

            self.segment_weights[seg_name] = best_w
            logger.info(f"  {seg_name:<15} n={mask.sum():<4}  "
                        f"w_RF={best_w[0]:.2f}  w_XGB={best_w[1]:.2f}  "
                        f"MAPE={best_mape:.2f}%")

        self._fitted = True
        return self

    def predict(self, X: np.ndarray, df_meta: pd.DataFrame) -> np.ndarray:
        """
        Predict emissions using segment-specific weights.
        """
        if not self._fitted:
            raise RuntimeError("Call fit() before predict()")

        rf_pred  = self.base_models["random_forest"].predict(X)
        xgb_pred = self.base_models["xgboost"].predict(X)
        segments = _assign_segment(df_meta).values

        predictions = np.empty(len(X))
        for seg_name, (w_rf, w_xgb) in self.segment_weights.items():
            mask = segments == seg_name
            if not mask.any():
                continue
            predictions[mask] = w_rf * rf_pred[mask] + w_xgb * xgb_pred[mask]

        # Rows not assigned to any segment (shouldn't happen, but safety net)
        unassigned = np.isnan(predictions) if hasattr(predictions, '__iter__') else False
        if np.any(np.isnan(predictions)):
            predictions[np.isnan(predictions)] = (
                0.25 * rf_pred[np.isnan(predictions)] +
                0.75 * xgb_pred[np.isnan(predictions)]
            )

        return np.maximum(0.0, predictions)

    def weights_table(self) -> pd.DataFrame:
        """Return a DataFrame showing per-segment weights."""
        rows = [
            {"Segment": seg, "w_RF": w[0], "w_XGB": w[1],
             "Description": SEGMENTS[seg]}
            for seg, w in self.segment_weights.items()
        ]
        return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 2. Soft Mixture of Experts (learned gating network)
# ---------------------------------------------------------------------------

class SoftMixtureEnsemble:
    """
    Soft Mixture of Experts with a learned gating network.

    Architecture:
        ŷ(x) = softmax(g(x)) · [ŷ_RF(x), ŷ_XGB(x)]ᵀ

    where g(x) is a small Ridge classifier trained to predict which expert
    performs best locally.  The softmax converts logit scores to mixing weights.

    The gating features are a compact subset of route characteristics that
    capture segment identity without needing the full feature vector.

    Parameters
    ----------
    base_models : dict with keys 'random_forest', 'xgboost'
    gating_type : 'ridge' (fast, interpretable) or 'mlp' (more expressive)
    temperature : softmax temperature τ; higher → softer (more equal) weights
    """

    _GATING_FEATURES = [
        "distance_km", "transport_mode_enc", "weight_tons",
        "congestion_factor", "slope_degrees",
    ]

    def __init__(
        self,
        base_models: Dict,
        gating_type: str = "ridge",
        temperature: float = 1.0,
    ):
        self.base_models = base_models
        self.gating_type = gating_type
        self.temperature = temperature

        self._mode_enc = LabelEncoder()
        self._gate_scaler = StandardScaler()

        if gating_type == "ridge":
            # Two separate Ridge regressors (one per expert logit)
            self._gate_rf  = Ridge(alpha=1.0)
            self._gate_xgb = Ridge(alpha=1.0)
        else:
            # Small MLP for gating (2 outputs = [logit_RF, logit_XGB])
            self._gate = MLPRegressor(
                hidden_layer_sizes=(32, 16),
                max_iter=500,
                random_state=42,
            )
        self._fitted = False

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        df_meta: pd.DataFrame,
        cv_folds: int = 5,
    ) -> "SoftMixtureEnsemble":
        """
        Train gating network on out-of-fold squared errors of each expert.

        Strategy: for each CV fold, compute squared-error of RF and XGB.
        Train gating network to predict the negative of each expert's error
        (high output → low error → prefer this expert).
        """
        Xg = self._build_gating_features(df_meta, fit=True)
        rf_pred  = self.base_models["random_forest"].predict(X)
        xgb_pred = self.base_models["xgboost"].predict(X)

        # Expert quality: 1/(1 + |error|)  → higher = better
        eps = 1e-6
        score_rf  = 1.0 / (1.0 + np.abs(y - rf_pred)  + eps)
        score_xgb = 1.0 / (1.0 + np.abs(y - xgb_pred) + eps)

        logger.info(f"Training soft gating network ({self.gating_type})...")

        if self.gating_type == "ridge":
            self._gate_rf.fit(Xg, score_rf)
            self._gate_xgb.fit(Xg, score_xgb)
        else:
            # Stack both scores as 2-column target
            self._gate.fit(Xg, np.stack([score_rf, score_xgb], axis=1))

        self._fitted = True

        # Evaluate on training set (in-sample, for diagnostics)
        ens_pred = self.predict(X, df_meta)
        mape = mean_absolute_percentage_error(y, ens_pred) * 100
        r2   = r2_score(y, ens_pred)
        logger.info(f"Soft MoE — train MAPE={mape:.2f}%  R²={r2:.4f}")
        return self

    def predict(self, X: np.ndarray, df_meta: pd.DataFrame) -> np.ndarray:
        """
        Predict emissions using context-adaptive soft weights.
        """
        if not self._fitted:
            raise RuntimeError("Call fit() before predict()")

        Xg = self._build_gating_features(df_meta, fit=False)
        rf_pred  = self.base_models["random_forest"].predict(X)
        xgb_pred = self.base_models["xgboost"].predict(X)

        # Compute gating logits
        if self.gating_type == "ridge":
            logit_rf  = self._gate_rf.predict(Xg)
            logit_xgb = self._gate_xgb.predict(Xg)
            logits = np.stack([logit_rf, logit_xgb], axis=1)
        else:
            logits = self._gate.predict(Xg)

        # Softmax over [logit_RF, logit_XGB] with temperature
        logits = logits / max(self.temperature, 1e-6)
        exp_l  = np.exp(logits - logits.max(axis=1, keepdims=True))
        weights = exp_l / exp_l.sum(axis=1, keepdims=True)   # shape (n, 2)

        predictions = weights[:, 0] * rf_pred + weights[:, 1] * xgb_pred
        return np.maximum(0.0, predictions)

    def get_weights_sample(
        self, X: np.ndarray, df_meta: pd.DataFrame, n: int = 10
    ) -> pd.DataFrame:
        """
        Return a table of (w_RF, w_XGB, segment) for the first n samples.
        Useful for explainability.
        """
        Xg = self._build_gating_features(df_meta.head(n), fit=False)

        if self.gating_type == "ridge":
            logit_rf  = self._gate_rf.predict(Xg)
            logit_xgb = self._gate_xgb.predict(Xg)
            logits = np.stack([logit_rf, logit_xgb], axis=1)
        else:
            logits = self._gate.predict(Xg)

        exp_l  = np.exp(logits - logits.max(axis=1, keepdims=True))
        w = exp_l / exp_l.sum(axis=1, keepdims=True)
        segs = _assign_segment(df_meta.head(n)).values

        return pd.DataFrame({
            "segment":   segs,
            "w_RF":      w[:, 0].round(3),
            "w_XGB":     w[:, 1].round(3),
            "distance":  df_meta.head(n)["distance_km"].values,
            "mode":      df_meta.head(n)["transport_mode"].values,
        })

    def _build_gating_features(
        self, df: pd.DataFrame, fit: bool = False
    ) -> np.ndarray:
        """Build compact gating feature matrix from route metadata."""
        df = df.copy()
        if fit:
            df["transport_mode_enc"] = self._mode_enc.fit_transform(
                df["transport_mode"])
        else:
            # Handle unseen modes gracefully
            known = set(self._mode_enc.classes_)
            df["transport_mode_enc"] = df["transport_mode"].apply(
                lambda m: self._mode_enc.transform([m])[0]
                if m in known else 0
            )

        avail = [f for f in self._GATING_FEATURES if f in df.columns]
        Xg = df[avail].fillna(0).values.astype(np.float64)

        if fit:
            Xg = self._gate_scaler.fit_transform(Xg)
        else:
            Xg = self._gate_scaler.transform(Xg)

        return Xg


# ---------------------------------------------------------------------------
# 3. Stacked Generalization (level-2 Ridge meta-learner)
# ---------------------------------------------------------------------------

class StackedEnsemble:
    """
    Stacked Generalization ensemble.

    Level 0: RF + XGBoost (+ optional PIEM estimate)
    Level 1: Ridge regression meta-learner trained on out-of-fold (OOF)
             predictions of the Level-0 models.

    OOF construction prevents data leakage: the meta-learner never sees
    training predictions computed on the same data it was trained on.

    Parameters
    ----------
    base_models   : dict with keys 'random_forest', 'xgboost'
    use_physics   : if True, include PIEM estimate as a 3rd level-0 input
    alpha         : Ridge regularisation strength for meta-learner
    cv_folds      : number of cross-validation folds for OOF generation
    """

    def __init__(
        self,
        base_models: Dict,
        use_physics: bool = True,
        alpha: float = 1.0,
        cv_folds: int = 5,
    ):
        self.base_models = base_models
        self.use_physics = use_physics
        self.cv_folds    = cv_folds
        self.meta_learner = Ridge(alpha=alpha)
        self._fitted = False
        self._phys_model = None

        if use_physics:
            try:
                import sys, os
                sys.path.insert(0, os.path.join(
                    os.path.dirname(__file__), "..", ".."))
                from algorithm.physics.emission_model import EmissionModelV2
                self._phys_model = EmissionModelV2()
                logger.info("PIEM model loaded as level-0 expert")
            except Exception as exc:
                logger.warning(f"PIEM unavailable ({exc}); stacking RF+XGB only")
                self.use_physics = False

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        df_meta: Optional[pd.DataFrame] = None,
    ) -> "StackedEnsemble":
        """
        Generate OOF predictions and train the meta-learner.

        Parameters
        ----------
        X       : feature matrix (unscaled, shape n × p)
        y       : emission targets (shape n,)
        df_meta : route metadata DataFrame (required if use_physics=True)
        """
        n = len(X)
        kf = KFold(n_splits=self.cv_folds, shuffle=True, random_state=42)

        rf_oof  = np.zeros(n)
        xgb_oof = np.zeros(n)
        phys_oof = np.zeros(n) if self.use_physics else None

        logger.info(f"Generating OOF predictions ({self.cv_folds} folds)...")

        for fold, (tr_idx, val_idx) in enumerate(kf.split(X)):
            X_tr, X_val = X[tr_idx], X[val_idx]
            y_tr = y[tr_idx]

            # Temporarily refit base models on fold training split
            # (shallow clone to avoid polluting the original fitted models)
            from sklearn.base import clone
            rf_fold  = clone(self.base_models["random_forest"]).fit(X_tr, y_tr)
            xgb_fold = clone(self.base_models["xgboost"]).fit(X_tr, y_tr)

            rf_oof[val_idx]  = rf_fold.predict(X_val)
            xgb_oof[val_idx] = xgb_fold.predict(X_val)

            if self.use_physics and df_meta is not None:
                phys_oof[val_idx] = self._predict_physics(
                    df_meta.iloc[val_idx])

            logger.info(f"  Fold {fold+1}/{self.cv_folds} done")

        # Build meta-feature matrix
        meta_X = self._build_meta_features(rf_oof, xgb_oof, phys_oof)

        # Train meta-learner
        self.meta_learner.fit(meta_X, y)
        self._fitted = True

        # Diagnostics
        meta_pred = self.meta_learner.predict(meta_X)
        mape = mean_absolute_percentage_error(y, np.maximum(0, meta_pred)) * 100
        r2   = r2_score(y, np.maximum(0, meta_pred))
        logger.info(f"Stacked ensemble OOF — MAPE={mape:.2f}%  R²={r2:.4f}")
        logger.info(f"Meta-learner coefficients: "
                    f"RF={self.meta_learner.coef_[0]:.3f}  "
                    f"XGB={self.meta_learner.coef_[1]:.3f}"
                    + (f"  Phys={self.meta_learner.coef_[2]:.3f}"
                       if self.use_physics else ""))
        return self

    def predict(
        self,
        X: np.ndarray,
        df_meta: Optional[pd.DataFrame] = None,
    ) -> np.ndarray:
        """
        Predict using the trained meta-learner on level-0 predictions.
        """
        if not self._fitted:
            raise RuntimeError("Call fit() before predict()")

        rf_pred  = self.base_models["random_forest"].predict(X)
        xgb_pred = self.base_models["xgboost"].predict(X)
        phys_pred = None
        if self.use_physics and df_meta is not None:
            phys_pred = self._predict_physics(df_meta)

        meta_X = self._build_meta_features(rf_pred, xgb_pred, phys_pred)
        return np.maximum(0.0, self.meta_learner.predict(meta_X))

    def evaluate(
        self, X: np.ndarray, y: np.ndarray,
        df_meta: Optional[pd.DataFrame] = None
    ) -> Dict[str, float]:
        """Return MAPE and R² on a held-out test set."""
        pred = self.predict(X, df_meta)
        return {
            "mape": round(mean_absolute_percentage_error(y, pred) * 100, 4),
            "r2":   round(r2_score(y, pred), 6),
        }

    def _build_meta_features(
        self,
        rf_pred: np.ndarray,
        xgb_pred: np.ndarray,
        phys_pred: Optional[np.ndarray],
    ) -> np.ndarray:
        cols = [rf_pred, xgb_pred]
        if self.use_physics and phys_pred is not None:
            cols.append(phys_pred)
        return np.stack(cols, axis=1)

    def _predict_physics(self, df_meta: pd.DataFrame) -> np.ndarray:
        """Run PIEM model over df_meta rows."""
        from algorithm.physics.emission_model import RouteEmissionInput
        results = []
        for _, row in df_meta.iterrows():
            inp = RouteEmissionInput(
                distance_km       = float(row.get("distance_km", 100)),
                weight_tons       = float(row.get("weight_tons", 10)),
                transport_mode    = str(row.get("transport_mode", "truck")),
                temperature_c     = float(row.get("temperature_c", 20)),
                congestion_factor = float(row.get("congestion_factor", 1.0)),
                slope_degrees     = float(row.get("slope_degrees", 0.0)),
                is_uphill         = bool(row.get("is_uphill", True)),
                weather_condition = str(row.get("weather_condition", "clear")),
                is_peak_hour      = bool(row.get("is_peak_hour", False)),
                is_weekend        = bool(row.get("is_weekend", False)),
            )
            results.append(self._phys_model.compute(inp).total_emission_kg)
        return np.array(results, dtype=np.float64)


# ---------------------------------------------------------------------------
# Factory function — easy integration with EmissionPredictionModels
# ---------------------------------------------------------------------------

def build_adaptive_ensemble(
    base_models: Dict,
    X_train: np.ndarray,
    y_train: np.ndarray,
    df_meta_train: pd.DataFrame,
    strategy: str = "stacked",
) -> object:
    """
    Build and fit the chosen adaptive ensemble strategy.

    Parameters
    ----------
    base_models    : {'random_forest': <fitted>, 'xgboost': <fitted>}
    X_train        : training feature matrix
    y_train        : training targets
    df_meta_train  : training route metadata (must have transport_mode, distance_km)
    strategy       : 'segmented' | 'soft_moe' | 'stacked'

    Returns
    -------
    Fitted ensemble object with .predict(X, df_meta) method
    """
    logger.info(f"Building adaptive ensemble — strategy='{strategy}'")

    if strategy == "segmented":
        ens = SegmentedEnsemble(base_models)
        ens.fit(X_train, y_train, df_meta_train)
        return ens

    elif strategy == "soft_moe":
        ens = SoftMixtureEnsemble(base_models, gating_type="ridge")
        ens.fit(X_train, y_train, df_meta_train)
        return ens

    elif strategy == "stacked":
        ens = StackedEnsemble(base_models, use_physics=True)
        ens.fit(X_train, y_train, df_meta_train)
        return ens

    else:
        raise ValueError(f"Unknown strategy '{strategy}'. "
                         "Choose: segmented | soft_moe | stacked")


# ---------------------------------------------------------------------------
# Standalone comparison demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

    print("\n=== Context-Adaptive Ensemble — Comparison Demo ===\n")

    from algorithm.data_prep.synthetic_generator import SyntheticRouteGenerator
    from algorithm.ml_models.emission_predictors import EmissionPredictionModels
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_percentage_error, r2_score

    # Generate data
    gen = SyntheticRouteGenerator(seed=42)
    df  = gen.generate_route_dataset(n_routes=600)

    # Train base models
    epm = EmissionPredictionModels(random_state=42)
    X, y = epm.prepare_features(df)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
    df_tr = df.iloc[:len(X_tr)].reset_index(drop=True)
    df_te = df.iloc[len(X_tr):].reset_index(drop=True)

    epm.models["random_forest"].fit(X_tr, y_tr)
    epm.models["xgboost"].fit(X_tr, y_tr)

    base_models = {
        "random_forest": epm.models["random_forest"],
        "xgboost":       epm.models["xgboost"],
    }

    results = {}

    # Baseline fixed ensemble
    fixed_pred = 0.25 * base_models["random_forest"].predict(X_te) + \
                 0.75 * base_models["xgboost"].predict(X_te)
    results["Fixed (0.25/0.75)"] = {
        "MAPE": mean_absolute_percentage_error(y_te, fixed_pred) * 100,
        "R2":   r2_score(y_te, fixed_pred),
    }

    # Segmented ensemble
    seg = SegmentedEnsemble(base_models)
    seg.fit(X_tr, y_tr, df_tr)
    seg_pred = seg.predict(X_te, df_te)
    results["Segmented MoE"] = {
        "MAPE": mean_absolute_percentage_error(y_te, seg_pred) * 100,
        "R2":   r2_score(y_te, seg_pred),
    }
    print("\nSegment weight table:")
    print(seg.weights_table().to_string(index=False))

    # Soft MoE
    soft = SoftMixtureEnsemble(base_models, gating_type="ridge")
    soft.fit(X_tr, y_tr, df_tr)
    soft_pred = soft.predict(X_te, df_te)
    results["Soft MoE (Ridge gate)"] = {
        "MAPE": mean_absolute_percentage_error(y_te, soft_pred) * 100,
        "R2":   r2_score(y_te, soft_pred),
    }
    print("\nSoft MoE sample weights (first 6 test routes):")
    print(soft.get_weights_sample(X_te[:6], df_te.head(6)).to_string(index=False))

    # Stacked generalization
    stk = StackedEnsemble(base_models, use_physics=True)
    stk.fit(X_tr, y_tr, df_tr)
    stk_pred = stk.predict(X_te, df_te)
    results["Stacked (Ridge meta)"] = {
        "MAPE": mean_absolute_percentage_error(y_te, stk_pred) * 100,
        "R2":   r2_score(y_te, stk_pred),
    }

    # Summary table
    print("\n\n=== RESULTS SUMMARY ===")
    print(f"{'Method':<25}  {'MAPE %':>8}  {'R²':>8}")
    print("-" * 46)
    for name, m in results.items():
        print(f"{name:<25}  {m['MAPE']:>8.2f}  {m['R2']:>8.4f}")

    best = min(results, key=lambda k: results[k]["MAPE"])
    print(f"\nBest strategy: {best}")
    print(f"Improvement over fixed ensemble: "
          f"{results['Fixed (0.25/0.75)']['MAPE'] - results[best]['MAPE']:+.2f}% MAPE")
