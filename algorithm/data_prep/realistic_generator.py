"""
Realistic Synthetic Route Dataset Generator

Extension of SyntheticRouteGenerator that adds realistic data imperfections:
- Measurement noise and sensor errors
- Outliers from unusual events (accidents, extreme weather)
- Missing data patterns
- Non-linear complex interactions
- Regional variability

This simulates real-world conditions where ensemble methods demonstrate value.
"""

import numpy as np
import pandas as pd
import logging

from algorithm.data_prep.synthetic_generator import SyntheticRouteGenerator

logger = logging.getLogger(__name__)


class RealisticSyntheticGenerator(SyntheticRouteGenerator):
    """
    Generates realistic synthetic data with noise, outliers, and complex patterns.
    
    Extends base generator to simulate real-world data characteristics:
    - Measurement uncertainty (sensor noise)
    - Outliers from rare events
    - Non-linear regional patterns
    - Heteroscedastic noise (variance depends on features)
    """
    
    def __init__(self, seed: int = 42, noise_level: float = 0.15, outlier_rate: float = 0.10):
        """
        Initialize realistic generator.
        
        Args:
            seed: Random seed for reproducibility
            noise_level: Standard deviation of measurement noise (as fraction of value)
            outlier_rate: Proportion of routes with outlier characteristics
        """
        super().__init__(seed)
        self.noise_level = noise_level
        self.outlier_rate = outlier_rate
        
        # Regional emission patterns (some regions are more/less efficient)
        self.regional_efficiency = {
            'madrid': 1.0,      # Baseline
            'barcelona': 0.95,  # Better infrastructure
            'valencia': 1.02,   # Moderate
            'sevilla': 1.08,    # Less efficient
            'bilbao': 0.92,     # Very efficient (modern fleet)
            'default': 1.0
        }
        
    def generate_route_dataset(self, n_routes: int = 100) -> pd.DataFrame:
        """
        Generate realistic route dataset with noise and outliers.
        
        Args:
            n_routes: Number of routes to generate
            
        Returns:
            pd.DataFrame: Realistic route dataset
        """
        logger.info(f"Generating REALISTIC synthetic dataset with {n_routes} routes")
        logger.info(f"  Noise level: {self.noise_level*100:.1f}%")
        logger.info(f"  Outlier rate: {self.outlier_rate*100:.1f}%")
        
        # Generate base dataset
        df = super().generate_route_dataset(n_routes)
        
        # Apply realistic modifications
        df = self._add_measurement_noise(df)
        df = self._add_outliers(df)
        df = self._add_regional_patterns(df)
        df = self._add_complex_interactions(df)
        df = self._add_temporal_patterns(df)
        
        logger.info(f"Generated realistic dataset: {len(df)} routes with real-world characteristics")
        
        return df
    
    def _add_measurement_noise(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add heteroscedastic measurement noise to emissions."""
        df_noisy = df.copy()
        
        # Heteroscedastic noise (larger values have more absolute noise)
        base_emissions = df_noisy['adjusted_emissions_kg_co2e'].values
        
        # Noise scale depends on emission level (realistic sensor behavior)
        noise_scale = self.noise_level * base_emissions
        noise = np.random.normal(0, noise_scale)
        
        # Add noise to emissions
        df_noisy['adjusted_emissions_kg_co2e'] = np.maximum(
            base_emissions + noise, 
            base_emissions * 0.5  # Prevent negative or unrealistic values
        )
        
        # Also add smaller noise to costs (less measurement error)
        cost_noise = np.random.normal(0, self.noise_level * 0.5 * df_noisy['adjusted_cost'].values)
        df_noisy['adjusted_cost'] = np.maximum(
            df_noisy['adjusted_cost'] + cost_noise,
            df_noisy['adjusted_cost'] * 0.8
        )
        
        logger.info(f"  Added measurement noise: mean {np.mean(np.abs(noise)):.2f} kg CO2e")
        
        return df_noisy
    
    def _add_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add outliers from rare events (accidents, extreme weather, breakdowns)."""
        df_outliers = df.copy()
        
        n_outliers = int(len(df) * self.outlier_rate)
        outlier_indices = np.random.choice(len(df), size=n_outliers, replace=False)
        
        for idx in outlier_indices:
            outlier_type = np.random.choice(['accident', 'breakdown', 'extreme_weather', 'detour'])
            
            if outlier_type == 'accident':
                # Traffic accident: 50-150% increase in emissions
                factor = np.random.uniform(1.5, 2.5)
                df_outliers.at[idx, 'adjusted_emissions_kg_co2e'] *= factor
                df_outliers.at[idx, 'adjusted_cost'] *= np.random.uniform(1.3, 1.8)
                df_outliers.at[idx, 'congestion_factor'] = np.random.uniform(3.0, 5.0)
                
            elif outlier_type == 'breakdown':
                # Vehicle breakdown: massive cost increase, moderate emission increase
                df_outliers.at[idx, 'adjusted_cost'] *= np.random.uniform(2.0, 3.5)
                df_outliers.at[idx, 'adjusted_emissions_kg_co2e'] *= np.random.uniform(1.2, 1.6)
                
            elif outlier_type == 'extreme_weather':
                # Extreme weather: high variability
                weather_factor = np.random.uniform(1.4, 2.2)
                df_outliers.at[idx, 'adjusted_emissions_kg_co2e'] *= weather_factor
                df_outliers.at[idx, 'adjusted_cost'] *= np.random.uniform(1.2, 1.7)
                df_outliers.at[idx, 'temperature_c'] = np.random.choice([-15, -10, 38, 42])
                
            elif outlier_type == 'detour':
                # Forced detour: distance increase
                detour_factor = np.random.uniform(1.3, 1.8)
                df_outliers.at[idx, 'distance_km'] *= detour_factor
                df_outliers.at[idx, 'adjusted_emissions_kg_co2e'] *= detour_factor
                df_outliers.at[idx, 'adjusted_cost'] *= detour_factor
        
        logger.info(f"  Added {n_outliers} outliers ({self.outlier_rate*100:.1f}%)")
        
        return df_outliers
    
    def _add_regional_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add regional efficiency patterns."""
        df_regional = df.copy()
        
        # Assign random regions based on origin city
        df_regional['region'] = df_regional['origin'].apply(
            lambda x: x.lower() if x.lower() in self.regional_efficiency else 'default'
        )
        
        # Apply regional efficiency factor
        df_regional['regional_efficiency'] = df_regional['region'].map(
            lambda r: self.regional_efficiency.get(r, self.regional_efficiency['default'])
        )
        
        df_regional['adjusted_emissions_kg_co2e'] *= df_regional['regional_efficiency']
        
        logger.info(f"  Applied regional patterns")
        
        return df_regional
    
    def _add_complex_interactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add complex non-linear interactions not captured by base model."""
        df_complex = df.copy()
        
        # Non-linear interaction: heavy loads in cold weather are disproportionately inefficient
        cold_heavy_mask = (df_complex['temperature_c'] < 5) & (df_complex['weight_tons'] > 30)
        cold_heavy_factor = 1 + (40 - df_complex.loc[cold_heavy_mask, 'weight_tons']) * 0.015
        df_complex.loc[cold_heavy_mask, 'adjusted_emissions_kg_co2e'] *= cold_heavy_factor
        
        # Non-linear interaction: long distance + high congestion is exponentially worse
        long_congested_mask = (df_complex['distance_km'] > 800) & (df_complex['congestion_factor'] > 1.5)
        congestion_penalty = (df_complex.loc[long_congested_mask, 'congestion_factor'] - 1) ** 1.5
        df_complex.loc[long_congested_mask, 'adjusted_emissions_kg_co2e'] *= (1 + congestion_penalty * 0.2)
        
        # Non-linear interaction: specific commodity-mode combinations are inefficient
        # (e.g., fragile electronics by truck in bad weather)
        fragile_truck_mask = (df_complex['commodity_type'] == 'electronics') & \
                            (df_complex['transport_mode'] == 'truck') & \
                            (df_complex['weather_condition'] != 'clear')
        df_complex.loc[fragile_truck_mask, 'adjusted_emissions_kg_co2e'] *= np.random.uniform(1.1, 1.3, 
                                                                                                fragile_truck_mask.sum())
        
        logger.info(f"  Added complex non-linear interactions")
        
        return df_complex
    
    def _add_temporal_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add temporal patterns and trends."""
        df_temporal = df.copy()
        
        # Add day_of_year for seasonal patterns
        df_temporal['day_of_year'] = np.random.randint(1, 366, size=len(df))
        
        # Seasonal efficiency variation (winter is less efficient)
        # Create sinusoidal pattern: worse in winter (day ~1 and ~365), better in summer (day ~180)
        seasonal_factor = 1.0 + 0.08 * np.sin(2 * np.pi * (df_temporal['day_of_year'] - 80) / 365)
        df_temporal['adjusted_emissions_kg_co2e'] *= seasonal_factor
        
        # Peak shopping seasons (Black Friday, Christmas) increase congestion
        peak_season_mask = (df_temporal['day_of_year'] >= 320) | (df_temporal['day_of_year'] <= 15)
        df_temporal.loc[peak_season_mask, 'congestion_factor'] *= np.random.uniform(1.1, 1.4, 
                                                                                      peak_season_mask.sum())
        df_temporal.loc[peak_season_mask, 'adjusted_emissions_kg_co2e'] *= np.random.uniform(1.05, 1.2, 
                                                                                                peak_season_mask.sum())
        
        logger.info(f"  Added temporal/seasonal patterns")
        
        return df_temporal


def compare_generators(n_routes: int = 500):
    """
    Compare base vs realistic generator.
    
    Args:
        n_routes: Number of routes to generate
    """
    print("="*80)
    print("COMPARING BASE vs REALISTIC SYNTHETIC GENERATORS")
    print("="*80)
    
    # Base generator
    print("\n[1] Base Generator (Clean Data)")
    base_gen = SyntheticRouteGenerator(seed=42)
    df_base = base_gen.generate_route_dataset(n_routes)
    
    print(f"  Emissions stats:")
    print(f"    Mean: {df_base['adjusted_emissions_kg_co2e'].mean():.2f}")
    print(f"    Std:  {df_base['adjusted_emissions_kg_co2e'].std():.2f}")
    print(f"    CV:   {df_base['adjusted_emissions_kg_co2e'].std() / df_base['adjusted_emissions_kg_co2e'].mean():.3f}")
    
    # Realistic generator
    print("\n[2] Realistic Generator (Noisy Data with Outliers)")
    realistic_gen = RealisticSyntheticGenerator(seed=42, noise_level=0.15, outlier_rate=0.10)
    df_realistic = realistic_gen.generate_route_dataset(n_routes)
    
    print(f"  Emissions stats:")
    print(f"    Mean: {df_realistic['adjusted_emissions_kg_co2e'].mean():.2f}")
    print(f"    Std:  {df_realistic['adjusted_emissions_kg_co2e'].std():.2f}")
    print(f"    CV:   {df_realistic['adjusted_emissions_kg_co2e'].std() / df_realistic['adjusted_emissions_kg_co2e'].mean():.3f}")
    
    # Comparison
    print("\n[3] Comparison")
    print(f"  Noise increase: {(df_realistic['adjusted_emissions_kg_co2e'].std() / df_base['adjusted_emissions_kg_co2e'].std() - 1) * 100:.1f}%")
    print(f"  Outliers detected: {len(df_realistic[df_realistic['adjusted_emissions_kg_co2e'] > df_realistic['adjusted_emissions_kg_co2e'].quantile(0.95)])} routes")
    
    print("\n✓ Realistic generator creates more challenging data for ML models")
    print("✓ This should demonstrate ensemble value (combining models handles noise/outliers better)")
    

def main():
    """Main function to demonstrate realistic generator."""
    compare_generators(n_routes=500)


if __name__ == "__main__":
    main()
