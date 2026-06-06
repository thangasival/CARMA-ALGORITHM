#!/usr/bin/env python3
"""
Train Paper Models - Carbon-Aware Route Optimization

This script trains the exact ML models described in the paper with their
documented hyperparameters and evaluates performance to verify reproducibility.

Models trained:
- Linear Regression (baseline)
- Random Forest (n_estimators=200, max_depth=15, min_samples_split=5)
- XGBoost (lr=0.1, max_depth=8, reg_alpha=0.1, reg_lambda=0.2)
- SVR (kernel='rbf', gamma='scale', C=100)
- Ensemble (weighted: RF=0.35, XGBoost=0.45, SVR=0.20)

Expected Performance (from paper):
- Ensemble MAPE: 10.26%
- Ensemble R²: 0.967

Author: Sivalingam Thangavel <th.sivalingam@gmail.com>
Date: 2026
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from algorithm.ml_models.emission_predictors import EmissionPredictionModels
from algorithm.data_prep.synthetic_generator import SyntheticRouteGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_training_data(n_samples: int = 3500, random_state: int = 42) -> pd.DataFrame:
    """
    Generate synthetic dataset matching paper specifications.
    
    Paper uses n=3,500 routes across three network sizes:
    - 500 routes (small network)
    - 1,000 routes (medium network)
    - 2,000 routes (large network)
    
    Args:
        n_samples: Total number of routes to generate
        random_state: Random seed for reproducibility
        
    Returns:
        pd.DataFrame: Complete training dataset
    """
    logger.info(f"Generating {n_samples} synthetic routes for training...")
    
    generator = SyntheticRouteGenerator(seed=random_state)
    
    # Generate datasets matching paper structure
    df_small = generator.generate_route_dataset(500)
    df_medium = generator.generate_route_dataset(1000)
    df_large = generator.generate_route_dataset(2000)
    
    # Combine all datasets
    df_combined = pd.concat([df_small, df_medium, df_large], ignore_index=True)
    
    logger.info(f"Generated {len(df_combined)} total routes")
    logger.info(f"  - Small network: {len(df_small)} routes")
    logger.info(f"  - Medium network: {len(df_medium)} routes")
    logger.info(f"  - Large network: {len(df_large)} routes")
    
    return df_combined


def train_and_evaluate_models(df: pd.DataFrame) -> dict:
    """
    Train all models with paper hyperparameters and evaluate performance.
    
    Args:
        df: Training dataset
        
    Returns:
        dict: Results for all models including ensemble
    """
    logger.info("="*80)
    logger.info("TRAINING PAPER MODELS")
    logger.info("="*80)
    
    # Initialize model collection with paper hyperparameters
    models = EmissionPredictionModels(random_state=42)
    
    # Train all models (includes ensemble training)
    results = models.train_models(df, test_size=0.2)
    
    logger.info("\n" + "="*80)
    logger.info("RESULTS SUMMARY")
    logger.info("="*80)
    
    # Display results in paper format
    print("\n| Model | MAPE (%) | R² | RMSE | CV RMSE |")
    print("|-------|----------|-----|------|---------|")
    
    for model_name, metrics in results.items():
        print(f"| {model_name:20s} | {metrics['mape']:7.2f} | {metrics['r2']:.3f} | "
              f"{metrics['rmse']:6.1f} | {metrics['cv_rmse_mean']:6.1f} ± {metrics['cv_rmse_std']:4.1f} |")
    
    print("\n" + "="*80)
    
    # Check if results match paper expectations
    ensemble_metrics = results.get('ensemble', {})
    expected_mape = 10.26
    expected_r2 = 0.967
    
    mape_diff = abs(ensemble_metrics.get('mape', 0) - expected_mape)
    r2_diff = abs(ensemble_metrics.get('r2', 0) - expected_r2)
    
    logger.info("\nPAPER VALIDATION:")
    logger.info(f"  Expected Ensemble MAPE: {expected_mape:.2f}%")
    logger.info(f"  Achieved Ensemble MAPE: {ensemble_metrics.get('mape', 0):.2f}%")
    logger.info(f"  Difference: {mape_diff:.2f}% {'✓' if mape_diff < 2.0 else '⚠️'}")
    logger.info(f"")
    logger.info(f"  Expected Ensemble R²: {expected_r2:.3f}")
    logger.info(f"  Achieved Ensemble R²: {ensemble_metrics.get('r2', 0):.3f}")
    logger.info(f"  Difference: {r2_diff:.3f} {'✓' if r2_diff < 0.02 else '⚠️'}")
    
    if mape_diff < 2.0 and r2_diff < 0.02:
        logger.info("\nSUCCESS: Results match paper within acceptable tolerance!")
    else:
        logger.warning("\nWARNING: Results deviate from paper expectations.")
        logger.warning("   This may be due to random data generation variations.")
        logger.warning("   Try running with different random seeds or more data.")
    
    return results, models


def save_results(results: dict, output_dir: str = "results/paper_models"):
    """
    Save training results to JSON for reproducibility verification.
    
    Args:
        results: Model evaluation results
        output_dir: Directory to save results
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert numpy types to Python types for JSON serialization
    results_serializable = {}
    for model_name, metrics in results.items():
        results_serializable[model_name] = {
            k: float(v) for k, v in metrics.items()
        }
    
    output_path = os.path.join(output_dir, "paper_model_results.json")
    with open(output_path, 'w') as f:
        json.dump(results_serializable, f, indent=2)
    
    logger.info(f"\nResults saved to: {output_path}")
    
    # Also save as CSV for easy viewing
    df_results = pd.DataFrame(results).T
    csv_path = os.path.join(output_dir, "paper_model_results.csv")
    df_results.to_csv(csv_path)
    logger.info(f"Results also saved as CSV: {csv_path}")


def main():
    """Main execution function."""
    try:
        logger.info("Starting Paper Model Training Script")
        logger.info("="*80)
        
        # Generate training data matching paper specifications
        df = generate_training_data(n_samples=3500, random_state=42)
        
        # Train and evaluate all models
        results, models = train_and_evaluate_models(df)
        
        # Save results for verification
        save_results(results)
        
        # Save trained models
        logger.info("\nSaving trained models...")
        models.save_models(output_dir="models/paper_models")
        logger.info("Models saved to: models/paper_models/")
        
        logger.info("\n" + "="*80)
        logger.info("TRAINING COMPLETE")
        logger.info("="*80)
        logger.info("\nNext steps:")
        logger.info("1. Review results in: results/paper_models/paper_model_results.json")
        logger.info("2. Verify models in: models/paper_models/")
        logger.info("3. Run validation script: python validate_paper_reproducibility.py")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during training: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())
