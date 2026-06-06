#!/usr/bin/env python3
"""
Configuration Settings for CARMA-ALGORITHM

Centralized configuration management for the CARMA framework.
Supports environment variables and default values.

Author: Sivalingam Thangavel <th.sivalingam@gmail.com>

Usage:
    from config import Config
    config = Config()
    print(config.MODEL_RANDOM_STATE)
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    """Centralized configuration for CARMA-ALGORITHM."""
    
    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    RESULTS_DIR: Path = PROJECT_ROOT / "results"
    MODELS_DIR: Path = PROJECT_ROOT / "models"
    
    # API Configuration
    CLIMATIQ_API_KEY: str = os.getenv("CLIMATIQ_API_KEY", "")
    CLIMATIQ_BASE_URL: str = os.getenv("CLIMATIQ_BASE_URL", "https://beta3.api.climatiq.io")
    EPA_API_KEY: str = os.getenv("EPA_API_KEY", "")
    
    # Data Configuration
    DATA_SOURCE: str = os.getenv("DATA_SOURCE", "synthetic")  # synthetic, climatiq, epa
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "data/processed")
    
    # Model Configuration
    MODEL_RANDOM_STATE: int = int(os.getenv("MODEL_RANDOM_STATE", "42"))
    CROSS_VALIDATION_FOLDS: int = int(os.getenv("CROSS_VALIDATION_FOLDS", "5"))
    TEST_SIZE: float = float(os.getenv("TEST_SIZE", "0.2"))
    
    # Optimization Configuration
    GA_POPULATION_SIZE: int = int(os.getenv("GA_POPULATION_SIZE", "50"))
    GA_GENERATIONS: int = int(os.getenv("GA_GENERATIONS", "30"))
    GA_MUTATION_RATE: float = float(os.getenv("GA_MUTATION_RATE", "0.2"))
    GA_CROSSOVER_RATE: float = float(os.getenv("GA_CROSSOVER_RATE", "0.8"))
    
    # Performance Targets
    TARGET_MAPE_THRESHOLD: float = float(os.getenv("TARGET_MAPE_THRESHOLD", "12.0"))
    TARGET_R2_THRESHOLD: float = float(os.getenv("TARGET_R2_THRESHOLD", "0.85"))
    TARGET_EMISSION_REDUCTION: float = float(os.getenv("TARGET_EMISSION_REDUCTION", "15.0"))
    TARGET_COST_INCREASE: float = float(os.getenv("TARGET_COST_INCREASE", "5.0"))
    
    # Model Parameters
    AVAILABLE_MODELS: List[str] = None
    DEFAULT_MODELS: List[str] = None
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    def __post_init__(self):
        """Initialize derived configurations."""
        if self.AVAILABLE_MODELS is None:
            self.AVAILABLE_MODELS = [
                "linear_baseline",
                "adaboost", 
                "random_forest",
                "neural_network"
            ]
        
        if self.DEFAULT_MODELS is None:
            self.DEFAULT_MODELS = self.AVAILABLE_MODELS.copy()
        
        # Create directories if they don't exist
        self.DATA_DIR.mkdir(exist_ok=True)
        self.RESULTS_DIR.mkdir(exist_ok=True)
        self.MODELS_DIR.mkdir(exist_ok=True)
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get machine learning model configuration."""
        return {
            "random_state": self.MODEL_RANDOM_STATE,
            "cv_folds": self.CROSS_VALIDATION_FOLDS,
            "test_size": self.TEST_SIZE,
            "available_models": self.AVAILABLE_MODELS,
            "default_models": self.DEFAULT_MODELS
        }
    
    def get_optimization_config(self) -> Dict[str, Any]:
        """Get genetic algorithm optimization configuration."""
        return {
            "population_size": self.GA_POPULATION_SIZE,
            "generations": self.GA_GENERATIONS,
            "mutation_rate": self.GA_MUTATION_RATE,
            "crossover_rate": self.GA_CROSSOVER_RATE,
            "random_state": self.MODEL_RANDOM_STATE
        }
    
    def get_performance_targets(self) -> Dict[str, float]:
        """Get performance target thresholds."""
        return {
            "mape_threshold": self.TARGET_MAPE_THRESHOLD,
            "r2_threshold": self.TARGET_R2_THRESHOLD,
            "emission_reduction": self.TARGET_EMISSION_REDUCTION,
            "cost_increase": self.TARGET_COST_INCREASE
        }
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate API key availability."""
        return {
            "climatiq": bool(self.CLIMATIQ_API_KEY),
            "epa": bool(self.EPA_API_KEY)
        }
    
    def get_data_source_config(self) -> Dict[str, Any]:
        """Get data source configuration."""
        return {
            "source": self.DATA_SOURCE,
            "output_dir": self.OUTPUT_DIR,
            "api_keys": self.validate_api_keys()
        }

# Global configuration instance
config = Config()

# Convenience functions for common configurations
def get_model_config() -> Dict[str, Any]:
    """Get model configuration."""
    return config.get_model_config()

def get_optimization_config() -> Dict[str, Any]:
    """Get optimization configuration."""
    return config.get_optimization_config()

def get_performance_targets() -> Dict[str, float]:
    """Get performance targets."""
    return config.get_performance_targets()

def validate_environment() -> bool:
    """Validate that the environment is properly configured."""
    try:
        # Check if critical directories exist
        config.DATA_DIR.mkdir(exist_ok=True)
        config.RESULTS_DIR.mkdir(exist_ok=True)
        config.MODELS_DIR.mkdir(exist_ok=True)
        
        # Check if at least one data source is available
        if config.DATA_SOURCE == "synthetic":
            return True
        elif config.DATA_SOURCE == "climatiq":
            return bool(config.CLIMATIQ_API_KEY)
        elif config.DATA_SOURCE == "epa":
            return bool(config.EPA_API_KEY)
        else:
            return False
            
    except Exception as e:
        print(f"Environment validation failed: {e}")
        return False

if __name__ == "__main__":
    """Display current configuration."""
    print("CARMA-ALGORITHM — Configuration")
    print("=" * 50)
    print(f"Project Root: {config.PROJECT_ROOT}")
    print(f"Data Source: {config.DATA_SOURCE}")
    print(f"Model Random State: {config.MODEL_RANDOM_STATE}")
    print(f"Available Models: {', '.join(config.AVAILABLE_MODELS)}")
    print(f"GA Population Size: {config.GA_POPULATION_SIZE}")
    print(f"Performance Targets: MAPE<{config.TARGET_MAPE_THRESHOLD}%, R²>{config.TARGET_R2_THRESHOLD}")
    print("\nAPI Keys:")
    api_status = config.validate_api_keys()
    for api, available in api_status.items():
        status = "OK" if available else "ERROR"
        print(f"  {api.upper()}: {status}")
    print(f"\nEnvironment Valid: {'OK' if validate_environment() else 'ERROR'}")
