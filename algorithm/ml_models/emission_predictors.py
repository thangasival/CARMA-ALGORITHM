"""
Machine Learning Models for Carbon Emission Prediction

Implements and compares ML algorithms for predicting transportation
route carbon emissions in supply chain optimization contexts.

Supported Models (Paper Implementation):
- Linear Regression (baseline comparison)
- Random Forest Regressor (ensemble component)
- XGBoost Regressor (ensemble component)
- Optimized Ensemble (RF: 0.25, XGBoost: 0.75)

Features:
- Automated feature preprocessing and scaling
- Cross-validation for robust evaluation
- Performance metrics (MAPE, R², RMSE)
- Model persistence and loading capabilities
- Exact hyperparameters from published paper

Note: SVR was evaluated but excluded from the final ensemble due to poor
performance with categorical features (MAPE > 70%) and extreme sensitivity
to outliers in real-world emission measurements.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_percentage_error, r2_score, mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from typing import Dict, List, Tuple, Any, Optional
import joblib
import os

# Configure logging
logger = logging.getLogger(__name__)


class EmissionPredictionModels:
    """
    Collection of ML models for carbon emission prediction in transportation routes.
    
    Provides a unified interface for training, evaluating, and comparing
    different ML algorithms for emission prediction.
    """
    
    def __init__(self, random_state: int = 42):
        """
        Initialize the ML models collection.
        
        Args:
            random_state: Random seed for reproducible results
        """
        self.random_state = random_state
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_names = []
        self.target_name = 'adjusted_emissions_kg_co2e'
        
        # Ensemble weights (optimized through cross-validation on synthetic data)
        # Validated: 9.48% MAPE, 0.928 R² (see validate_ml_performance.py)
        self.ensemble_weights = {
            'random_forest': 0.25,
            'xgboost': 0.75
        }
        
        # Initialize models
        self._initialize_models()
        
    def _initialize_models(self):
        """
        Initialize all ML models with exact hyperparameters from paper.
        
        Models and hyperparameters match those documented in:
        "Carbon-Aware Route Optimization in Supply Chain Networks" (Section 3.2.2)
        
        Note: SVR was evaluated but excluded due to poor performance with
        categorical features common in transportation data (MAPE > 70%).
        """
        
        # 1. Baseline Linear Model (comparison baseline only)
        self.models['linear_baseline'] = LinearRegression()
        
        # 2. Random Forest (Paper: 200 trees, depth 15, min_samples_split 5)
        self.models['random_forest'] = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=1,
            max_features='sqrt',
            random_state=self.random_state,
            n_jobs=-1
        )
        
        # 3. XGBoost (Paper: lr=0.1, depth=8, L1=0.1, L2=0.2)
        self.models['xgboost'] = XGBRegressor(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=8,
            reg_alpha=0.1,  # L1 regularization
            reg_lambda=0.2,  # L2 regularization
            random_state=self.random_state,
            n_jobs=-1,
            verbosity=0
        )
        
        logger.info(f"Initialized {len(self.models)} ML models with paper hyperparameters")
        logger.info(f"Ensemble weights: RF={self.ensemble_weights['random_forest']}, "
                   f"XGB={self.ensemble_weights['xgboost']}")
        
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features and target for ML training with enhanced feature engineering.
        
        Args:
            df: DataFrame with route data
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: Features (X) and target (y)
        """
        # Create enhanced features
        df_enhanced = df.copy()
        
        # ----------------------------------------------------------------
        # Core physics features — simple flat-EF baseline
        # (retained alongside PIEM features for ML calibration signal)
        # ----------------------------------------------------------------
        df_enhanced['ton_km'] = df_enhanced['distance_km'] * df_enhanced['weight_tons']
        df_enhanced['load_intensity'] = df_enhanced['weight_tons'] / np.maximum(df_enhanced['distance_km'], 1)

        transport_emission_map = {'truck': 0.161, 'rail': 0.041, 'ship': 0.015, 'air': 0.602}
        df_enhanced['transport_emission_factor'] = df_enhanced['transport_mode'].map(transport_emission_map)

        # simple environmental efficiency (flat-EF proxy, kept as ML feature alongside PIEM)
        df_enhanced['env_efficiency_simple'] = (
            df_enhanced['congestion_factor'] *
            (1 + df_enhanced['slope_degrees'] * 0.01) *
            (1 + np.abs(df_enhanced['temperature_c'] - 20) * 0.005)
        )
        df_enhanced['physics_emission_simple'] = (
            df_enhanced['ton_km'] *
            df_enhanced['transport_emission_factor'] *
            df_enhanced['env_efficiency_simple']
        )

        # ----------------------------------------------------------------
        # PIEM features — use pre-computed columns when available
        # (added by SyntheticRouteGenerator._add_piem_features),
        # otherwise compute on-the-fly via EmissionModelV2
        # ----------------------------------------------------------------
        v2_cols = ['load_factor', 'payload_efficiency', 'speed_ratio',
                   'f_temp', 'f_congestion', 'f_slope', 'f_weather', 'f_peak',
                   'piem_emission', 'piem_emission_per_tonkm',
                   'actual_speed_kmh', 'optimal_speed_kmh']

        has_v2 = all(c in df_enhanced.columns for c in
                     ['load_factor', 'piem_emission'])

        if not has_v2:
            # Compute v2 features on-the-fly (inference / new data path)
            try:
                import sys, os as _os
                sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), '..', '..'))
                from algorithm.physics.emission_model import EmissionModelV2, RouteEmissionInput
                _model_v2 = EmissionModelV2()
                v2_rows = []
                for _, row in df_enhanced.iterrows():
                    inp = RouteEmissionInput(
                        distance_km=float(row['distance_km']),
                        weight_tons=float(row['weight_tons']),
                        transport_mode=row['transport_mode'],
                        temperature_c=float(row.get('temperature_c', 20.0)),
                        congestion_factor=float(row.get('congestion_factor', 1.0)),
                        slope_degrees=float(row.get('slope_degrees', 0.0)),
                        is_uphill=bool(row.get('is_uphill', True)),
                        weather_condition=row.get('weather_condition', 'clear'),
                        is_peak_hour=bool(row.get('is_peak_hour', False)),
                        is_weekend=bool(row.get('is_weekend', False)),
                    )
                    v2_rows.append(_model_v2.get_physics_features(inp))
                import pandas as _pd
                v2_df = _pd.DataFrame(v2_rows, index=df_enhanced.index)
                # merge v2 columns that don't already exist
                for col in v2_df.columns:
                    if col not in df_enhanced.columns:
                        df_enhanced[col] = v2_df[col]
                logger.info("PIEM features computed on-the-fly")
            except Exception as exc:
                logger.warning(f"PIEM feature computation failed ({exc}); "
                               "falling back to v1-only features")

        # ----------------------------------------------------------------
        # Define final feature sets
        # ----------------------------------------------------------------
        numerical_features = [
            # v1 core
            'distance_km', 'weight_tons', 'ton_km', 'load_intensity',
            'transport_emission_factor', 'temperature_c', 'congestion_factor',
            'slope_degrees', 'env_efficiency_simple', 'physics_emission_simple',
        ]

        # Append v2 features when available
        v2_numerical = [
            'load_factor', 'payload_efficiency', 'actual_speed_kmh',
            'optimal_speed_kmh', 'speed_ratio',
            'f_temp', 'f_congestion', 'f_slope', 'f_weather', 'f_peak',
            'piem_emission', 'piem_emission_per_tonkm',
        ]
        for col in v2_numerical:
            if col in df_enhanced.columns:
                numerical_features.append(col)

        categorical_features = ['commodity_type', 'weather_condition']
        boolean_features = ['is_peak_hour', 'is_weekend']
        
        # Process numerical features
        X_numerical = df_enhanced[numerical_features].values
        
        # Process categorical features
        X_categorical = []
        for feature in categorical_features:
            if feature not in self.encoders:
                self.encoders[feature] = LabelEncoder()
                encoded = self.encoders[feature].fit_transform(df_enhanced[feature])
            else:
                encoded = self.encoders[feature].transform(df_enhanced[feature])
            X_categorical.append(encoded.reshape(-1, 1))
        
        X_categorical = np.hstack(X_categorical) if X_categorical else np.empty((len(df_enhanced), 0))
        
        # Process boolean features
        X_boolean = df_enhanced[boolean_features].astype(int).values
        
        # Combine all features
        X = np.hstack([X_numerical, X_categorical, X_boolean])
        
        # Store feature names for interpretation
        self.feature_names = numerical_features + categorical_features + boolean_features
        
        # Extract target
        y = df_enhanced[self.target_name].values
        
        logger.info(f"Enhanced features prepared: {X.shape[1]} features, {X.shape[0]} samples")
        phys_col = 'piem_emission' if 'piem_emission' in df_enhanced.columns else 'physics_emission_simple'
        logger.info(f"Physics feature ({phys_col}) correlation with target: "
                    f"{np.corrcoef(df_enhanced[phys_col], y)[0,1]:.3f}")
        
        return X, y
        
    def train_models(self, df: pd.DataFrame, test_size: float = 0.2) -> Dict[str, Dict]:
        """
        Train all ML models and evaluate their performance.
        
        Args:
            df: Training dataset
            test_size: Proportion of data for testing
            
        Returns:
            Dict[str, Dict]: Performance metrics for each model
        """
        X, y = self.prepare_features(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state
        )
        
        # Scale features (important for neural networks)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers['standard'] = scaler
        
        results = {}
        
        # Train individual models
        for model_name, model in self.models.items():
            logger.info(f"Training {model_name}...")
            
            # SVR requires scaled features
            if model_name == 'svr':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            
            # Calculate metrics
            metrics = self._calculate_metrics(y_test, y_pred)
            
            # Add cross-validation score
            if model_name == 'svr':
                cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, 
                                          scoring='neg_mean_squared_error')
            else:
                cv_scores = cross_val_score(model, X_train, y_train, cv=5, 
                                          scoring='neg_mean_squared_error')
            
            metrics['cv_rmse_mean'] = np.sqrt(-cv_scores.mean())
            metrics['cv_rmse_std'] = np.sqrt(cv_scores.std())
            
            results[model_name] = metrics
            
            logger.info(f"{model_name} - MAPE: {metrics['mape']:.2f}%, R²: {metrics['r2']:.3f}")
        
        # Train ensemble (weighted combination of RF, XGBoost, SVR)
        logger.info("Evaluating ensemble model...")
        ensemble_pred = self.ensemble_predict(X_test, X_test_scaled)
        ensemble_metrics = self._calculate_metrics(y_test, ensemble_pred)
        
        # Ensemble cross-validation (using weighted combination)
        cv_ensemble_scores = []
        from sklearn.model_selection import KFold
        kf = KFold(n_splits=5, shuffle=True, random_state=self.random_state)
        for train_idx, val_idx in kf.split(X_train):
            X_cv_train, X_cv_val = X_train[train_idx], X_train[val_idx]
            y_cv_train, y_cv_val = y_train[train_idx], y_train[val_idx]
            
            # Scale for SVR
            scaler_cv = StandardScaler()
            X_cv_train_scaled = scaler_cv.fit_transform(X_cv_train)
            X_cv_val_scaled = scaler_cv.transform(X_cv_val)
            
            # Retrain ensemble components
            self.models['random_forest'].fit(X_cv_train, y_cv_train)
            self.models['xgboost'].fit(X_cv_train, y_cv_train)
            self.models['svr'].fit(X_cv_train_scaled, y_cv_train)
            
            # Ensemble prediction
            y_cv_pred = self.ensemble_predict(X_cv_val, X_cv_val_scaled)
            mse = mean_squared_error(y_cv_val, y_cv_pred)
            cv_ensemble_scores.append(mse)
        
        ensemble_metrics['cv_rmse_mean'] = np.sqrt(np.mean(cv_ensemble_scores))
        ensemble_metrics['cv_rmse_std'] = np.sqrt(np.std(cv_ensemble_scores))
        
        results['ensemble'] = ensemble_metrics
        logger.info(f"ensemble - MAPE: {ensemble_metrics['mape']:.2f}%, R²: {ensemble_metrics['r2']:.3f}")
        
        # Store scaled test data for future ensemble predictions
        self.X_test_scaled = X_test_scaled
        
        return results
    
    def ensemble_predict(self, X: np.ndarray, X_scaled: np.ndarray) -> np.ndarray:
        """
        Generate ensemble prediction using weighted combination of RF and XGBoost.
        
        Implements optimized ensemble equation:
        prediction_ensemble = w_RF × prediction_RF + w_XGB × prediction_XGB
        
        Weights (optimized through grid search cross-validation):
        - Random Forest: 0.25
        - XGBoost: 0.75
        
        Validated performance on synthetic clean data (n=3,500):
        - MAPE: 9.48%
        - R²: 0.928
        - RMSE: 4286.02 kg CO2e
        
        Args:
            X: Feature matrix for RF and XGBoost (unscaled)
            X_scaled: Scaled feature matrix (not used in current implementation,
                      kept for API compatibility)
            
        Returns:
            np.ndarray: Ensemble predictions
        """
        rf_pred = self.models['random_forest'].predict(X)
        xgb_pred = self.models['xgboost'].predict(X)
        
        ensemble_pred = (
            self.ensemble_weights['random_forest'] * rf_pred +
            self.ensemble_weights['xgboost'] * xgb_pred
        )
        
        return ensemble_pred
        
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculate comprehensive performance metrics.
        
        Args:
            y_true: True emission values
            y_pred: Predicted emission values
            
        Returns:
            Dict[str, float]: Performance metrics
        """
        mape = mean_absolute_percentage_error(y_true, y_pred) * 100
        r2 = r2_score(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = np.mean(np.abs(y_true - y_pred))
        
        # Relative error (target < 12%)
        relative_error = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        
        return {
            'mape': mape,
            'r2': r2,
            'rmse': rmse,
            'mae': mae,
            'relative_error': relative_error
        }
        
    def compare_models(self, results: Dict[str, Dict]) -> pd.DataFrame:
        """
        Create comparison table of model performance.
        
        Args:
            results: Model performance results
            
        Returns:
            pd.DataFrame: Comparison table
        """
        comparison_df = pd.DataFrame(results).T
        
        # Sort by R² score (descending)
        comparison_df = comparison_df.sort_values('r2', ascending=False)
        
        # Add ranking
        comparison_df['rank'] = range(1, len(comparison_df) + 1)
        
        # Highlight best performers
        comparison_df['meets_mape_target'] = comparison_df['mape'] <= 12.0
        comparison_df['meets_r2_target'] = comparison_df['r2'] >= 0.85
        comparison_df['meets_relative_error_target'] = comparison_df['relative_error'] <= 12.0
        
        return comparison_df
        
    def plot_model_comparison(self, results: Dict[str, Dict], save_path: str = None):
        """
        Create visualization comparing model performance.
        
        Args:
            results: Model performance results
            save_path: Path to save the plot
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('ML Models Performance Comparison', fontsize=16, y=0.98)
        
        models = list(results.keys())
        
        # MAPE comparison
        mape_values = [results[model]['mape'] for model in models]
        axes[0, 0].bar(models, mape_values, color='skyblue', alpha=0.7)
        axes[0, 0].axhline(y=12, color='red', linestyle='--', label='Target < 12%')
        axes[0, 0].set_title('Mean Absolute Percentage Error (MAPE)')
        axes[0, 0].set_ylabel('MAPE (%)')
        axes[0, 0].legend()
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # R² comparison
        r2_values = [results[model]['r2'] for model in models]
        axes[0, 1].bar(models, r2_values, color='lightgreen', alpha=0.7)
        axes[0, 1].axhline(y=0.85, color='red', linestyle='--', label='Target > 0.85')
        axes[0, 1].set_title('R² Score')
        axes[0, 1].set_ylabel('R²')
        axes[0, 1].legend()
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # RMSE comparison
        rmse_values = [results[model]['rmse'] for model in models]
        axes[1, 0].bar(models, rmse_values, color='orange', alpha=0.7)
        axes[1, 0].set_title('Root Mean Square Error (RMSE)')
        axes[1, 0].set_ylabel('RMSE')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Relative Error comparison
        rel_error_values = [results[model]['relative_error'] for model in models]
        axes[1, 1].bar(models, rel_error_values, color='pink', alpha=0.7)
        axes[1, 1].axhline(y=12, color='red', linestyle='--', label='Target < 12%')
        axes[1, 1].set_title('Relative Error')
        axes[1, 1].set_ylabel('Relative Error (%)')
        axes[1, 1].legend()
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Model comparison plot saved to {save_path}")
            
        plt.show()
        
    def get_feature_importance(self, model_name: str) -> pd.DataFrame:
        """
        Get feature importance for tree-based models.
        
        Args:
            model_name: Name of the model
            
        Returns:
            pd.DataFrame: Feature importance ranking
        """
        if model_name not in ['random_forest', 'adaboost']:
            logger.warning(f"Feature importance not available for {model_name}")
            return None
            
        model = self.models[model_name]
        
        if hasattr(model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            return importance_df
        else:
            return None
            
    def save_models(self, output_dir: str = "../models"):
        """
        Save trained models to disk.
        
        Args:
            output_dir: Directory to save models
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for model_name, model in self.models.items():
            model_path = os.path.join(output_dir, f"{model_name}.joblib")
            joblib.dump(model, model_path)
            logger.info(f"Saved {model_name} to {model_path}")
            
        # Save scalers and encoders
        if self.scalers:
            scaler_path = os.path.join(output_dir, "scalers.joblib")
            joblib.dump(self.scalers, scaler_path)
            
        if self.encoders:
            encoder_path = os.path.join(output_dir, "encoders.joblib")
            joblib.dump(self.encoders, encoder_path)
            
    def predict_emissions(self, route_data: Dict, model_name: str = 'adaboost') -> float:
        """
        Predict emissions for a single route.
        
        Args:
            route_data: Dictionary with route characteristics
            model_name: Name of the model to use for prediction
            
        Returns:
            float: Predicted emissions in kg CO2e
        """
        # Convert route data to DataFrame for processing
        df = pd.DataFrame([route_data])
        X, _ = self.prepare_features(df)
        
        model = self.models[model_name]
        
        if model_name == 'neural_network':
            X = self.scalers['standard'].transform(X)
            
        prediction = model.predict(X)[0]
        return max(0, prediction)  # Ensure non-negative emissions


def main():
    """
    Main function to demonstrate ML models training and comparison.
    """
    # This would typically load data from the synthetic generator
    logger.info("ML Models module initialized")
    
    # Example usage (uncomment when data is available):
    # from algorithm.data_prep.synthetic_generator import SyntheticRouteGenerator
    # 
    # generator = SyntheticRouteGenerator()
    # df = generator.generate_route_dataset(200)
    # 
    # models = EmissionPredictionModels()
    # results = models.train_models(df)
    # 
    # comparison = models.compare_models(results)
    # print(comparison)
    # 
    # models.plot_model_comparison(results)


if __name__ == "__main__":
    main()
