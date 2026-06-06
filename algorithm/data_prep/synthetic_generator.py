"""
Synthetic Route Dataset Generator

Generates realistic transportation route datasets for testing and validation
of ML models and optimization algorithms for carbon-aware route optimization.

Features:
- Configurable route generation with realistic characteristics
- Environmental factors (temperature, congestion, terrain)
- Physics-based cost and emission calculations
- Support for multiple transportation modes and commodities
"""

import numpy as np
import pandas as pd
import random
from typing import List, Dict, Tuple, Optional
import logging
import os
import sys

# Physics-informed emission model v2
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from algorithm.physics.emission_model import EmissionModelV2, RouteEmissionInput

# Configure logging
logger = logging.getLogger(__name__)

_emission_model = EmissionModelV2()


class SyntheticRouteGenerator:
    """
    Generator for synthetic transportation route datasets.
    
    Creates realistic route data for supply chain optimization research
    with controlled parameters for reproducible experiments.
    """
    
    def __init__(self, seed: int = 42):
        """
        Initialize the synthetic route generator.
        
        Args:
            seed: Random seed for reproducible results
        """
        np.random.seed(seed)
        random.seed(seed)
        self.seed = seed
        
        # Define realistic parameter ranges
        self.distance_range = (50, 2000)      # km
        self.weight_range = (1, 50)           # tons
        self.temperature_range = (-10, 35)    # Celsius
        self.congestion_range = (0.8, 2.5)    # multiplier (1.0 = normal)
        self.slope_range = (0, 15)            # degrees
        
        # Commodity types and their characteristics
        self.commodities = {
            'electronics': {'density': 0.3, 'value_per_kg': 150, 'fragility': 0.9},
            'textiles': {'density': 0.4, 'value_per_kg': 25, 'fragility': 0.3},
            'food': {'density': 0.6, 'value_per_kg': 8, 'fragility': 0.7},
            'machinery': {'density': 0.8, 'value_per_kg': 45, 'fragility': 0.4},
            'chemicals': {'density': 0.9, 'value_per_kg': 12, 'fragility': 0.8},
            'raw_materials': {'density': 1.2, 'value_per_kg': 3, 'fragility': 0.1}
        }
        
        # Transport modes and their characteristics
        self.transport_modes = {
            'truck': {'speed_kmh': 80, 'cost_per_km': 1.5, 'emission_factor': 0.161},
            'rail': {'speed_kmh': 60, 'cost_per_km': 0.8, 'emission_factor': 0.041},
            'ship': {'speed_kmh': 25, 'cost_per_km': 0.3, 'emission_factor': 0.015},
            'air': {'speed_kmh': 800, 'cost_per_km': 12.0, 'emission_factor': 0.602}
        }
        
        # Spanish cities for realistic route generation
        self.spanish_cities = [
            'Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Zaragoza',
            'Málaga', 'Murcia', 'Palma', 'Las Palmas', 'Bilbao',
            'Alicante', 'Córdoba', 'Valladolid', 'Vigo', 'Gijón',
            'Hospitalet', 'Vitoria', 'Coruña', 'Granada', 'Oviedo'
        ]
        
    def generate_route_dataset(self, n_routes: int = 100) -> pd.DataFrame:
        """
        Generate a synthetic route dataset.
        
        Args:
            n_routes: Number of routes to generate
            
        Returns:
            pd.DataFrame: Generated route dataset
        """
        logger.info(f"Generating synthetic dataset with {n_routes} routes")
        
        routes = []
        
        for i in range(n_routes):
            route = self._generate_single_route(route_id=i+1)
            routes.append(route)
            
        df = pd.DataFrame(routes)
        
        # Add calculated fields
        df = self._calculate_derived_features(df)
        
        logger.info(f"Generated dataset: {len(df)} routes, {len(df.columns)} features")
        return df
        
    def _generate_single_route(self, route_id: int) -> Dict:
        """
        Generate a single synthetic route.
        
        Args:
            route_id: Unique route identifier
            
        Returns:
            Dict: Route characteristics
        """
        # Basic route characteristics
        origin = random.choice(self.spanish_cities)
        destination = random.choice([city for city in self.spanish_cities if city != origin])
        
        distance_km = np.random.uniform(*self.distance_range)
        weight_tons = np.random.uniform(*self.weight_range)
        
        # Commodity and transport mode
        commodity_type = random.choice(list(self.commodities.keys()))
        transport_mode = self._select_transport_mode(distance_km, commodity_type)
        
        # Environmental and operational factors
        temperature_c = np.random.uniform(*self.temperature_range)
        congestion_factor = np.random.uniform(*self.congestion_range)
        slope_degrees = np.random.uniform(*self.slope_range)
        
        # Time-based factors
        is_peak_hour = random.choice([True, False])
        is_weekend = random.choice([True, False])
        weather_condition = random.choice(['clear', 'rain', 'snow', 'fog'])
        # Terrain direction (uphill vs downhill net gradient)
        is_uphill = random.choice([True, False])

        route = {
            'route_id': route_id,
            'origin': origin,
            'destination': destination,
            'distance_km': round(distance_km, 1),
            'weight_tons': round(weight_tons, 1),
            'commodity_type': commodity_type,
            'transport_mode': transport_mode,
            'temperature_c': round(temperature_c, 1),
            'congestion_factor': round(congestion_factor, 2),
            'slope_degrees': round(slope_degrees, 1),
            'is_uphill': is_uphill,
            'is_peak_hour': is_peak_hour,
            'is_weekend': is_weekend,
            'weather_condition': weather_condition
        }
        
        return route
        
    def _select_transport_mode(self, distance_km: float, commodity_type: str) -> str:
        """
        Select appropriate transport mode based on distance and commodity.
        
        Args:
            distance_km: Route distance
            commodity_type: Type of commodity
            
        Returns:
            str: Selected transport mode
        """
        # Transport mode selection logic
        if distance_km < 100:
            return 'truck'
        elif distance_km < 500:
            # Prefer truck for short-medium distances
            return random.choices(['truck', 'rail'], weights=[0.7, 0.3])[0]
        elif distance_km < 1000:
            # Mixed options for medium distances
            if commodity_type in ['electronics', 'food']:
                return random.choices(['truck', 'rail', 'air'], weights=[0.4, 0.5, 0.1])[0]
            else:
                return random.choices(['truck', 'rail'], weights=[0.3, 0.7])[0]
        else:
            # Long distances favor rail and ship
            if commodity_type in ['electronics']:
                return random.choices(['rail', 'air', 'ship'], weights=[0.5, 0.3, 0.2])[0]
            else:
                return random.choices(['rail', 'ship'], weights=[0.6, 0.4])[0]
                
    def _calculate_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate derived features like cost and emissions.
        
        Args:
            df: DataFrame with basic route features
            
        Returns:
            pd.DataFrame: DataFrame with calculated features
        """
        df = df.copy()
        
        # Calculate base cost and emissions
        df['base_cost'] = df.apply(self._calculate_base_cost, axis=1)
        df['base_emissions_kg_co2e'] = df.apply(self._calculate_base_emissions, axis=1)
        
        # Apply environmental and operational factors
        df['adjusted_cost'] = df.apply(self._apply_cost_adjustments, axis=1)
        df['adjusted_emissions_kg_co2e'] = df.apply(self._apply_emission_adjustments, axis=1)
        
        # Calculate efficiency metrics
        df['cost_per_km'] = df['adjusted_cost'] / df['distance_km']
        df['emissions_per_tonkm'] = df['adjusted_emissions_kg_co2e'] / (df['distance_km'] * df['weight_tons'])
        df['cost_per_ton'] = df['adjusted_cost'] / df['weight_tons']

        # Inject PIEM feature columns for ML enrichment
        df = self._add_piem_features(df)
        
        # Add categorical features for ML models
        df['distance_category'] = pd.cut(df['distance_km'], 
                                       bins=[0, 200, 500, 1000, float('inf')],
                                       labels=['short', 'medium', 'long', 'very_long'])
        df['weight_category'] = pd.cut(df['weight_tons'],
                                     bins=[0, 10, 25, float('inf')],
                                     labels=['light', 'medium', 'heavy'])
        
        return df
        
    def _calculate_base_cost(self, row: pd.Series) -> float:
        """Calculate base transportation cost."""
        mode_data = self.transport_modes[row['transport_mode']]
        return row['distance_km'] * mode_data['cost_per_km']
        
    def _calculate_base_emissions(self, row: pd.Series) -> float:
        """Calculate base emissions with realistic physics-based model."""
        mode_data = self.transport_modes[row['transport_mode']]
        
        # Base emission calculation: distance × weight × emission_factor
        base_emissions = row['distance_km'] * row['weight_tons'] * mode_data['emission_factor']
        
        # Add commodity-specific factors
        commodity_data = self.commodities[row['commodity_type']]
        commodity_factor = 1.0 + (commodity_data['fragility'] * 0.1)  # More fragile = more careful = more emissions
        
        return base_emissions * commodity_factor
        
    def _apply_cost_adjustments(self, row: pd.Series) -> float:
        """Apply environmental and operational adjustments to cost."""
        adjusted_cost = row['base_cost']
        
        # Congestion factor
        adjusted_cost *= row['congestion_factor']
        
        # Peak hour surcharge
        if row['is_peak_hour']:
            adjusted_cost *= 1.15
            
        # Weather conditions
        weather_multipliers = {'clear': 1.0, 'rain': 1.05, 'snow': 1.2, 'fog': 1.1}
        adjusted_cost *= weather_multipliers[row['weather_condition']]
        
        # Slope adjustment (affects fuel consumption)
        slope_factor = 1 + (row['slope_degrees'] * 0.02)
        adjusted_cost *= slope_factor
        
        return round(adjusted_cost, 2)
        
    def _apply_emission_adjustments(self, row: pd.Series) -> float:
        """
        Compute route emissions using Physics-Informed Model v2.

        Replaces the naive multiplicative v1 formula with:
          - Grubb payload efficiency (partial loads emit more per ton-km)
          - COPERT speed-curve correction (V-shaped, optimal ~82 km/h trucks)
          - Quadratic temperature penalty (cold-start asymmetry)
          - Non-linear congestion stop-and-go (HBEFA 4.2)
          - Bidirectional slope with regenerative braking for rail
          - Weather × congestion coupling (no double-counting)
          - Peak-hour as speed function (not fixed +20%)
        """
        inp = RouteEmissionInput(
            distance_km=float(row['distance_km']),
            weight_tons=float(row['weight_tons']),
            transport_mode=row['transport_mode'],
            temperature_c=float(row['temperature_c']),
            congestion_factor=float(row['congestion_factor']),
            slope_degrees=float(row['slope_degrees']),
            is_uphill=bool(row.get('is_uphill', True)),
            weather_condition=row['weather_condition'],
            is_peak_hour=bool(row['is_peak_hour']),
            is_weekend=bool(row['is_weekend']),
        )
        return round(_emission_model.compute(inp).total_emission_kg, 2)
        
    def _add_piem_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute and attach all PIEM feature columns.

        These features are consumed by the ML predictor's feature engineering
        pipeline (emission_predictors.py) to give tree models richer physics
        signal beyond raw route parameters.
        """
        feature_rows = []
        for _, row in df.iterrows():
            inp = RouteEmissionInput(
                distance_km=float(row['distance_km']),
                weight_tons=float(row['weight_tons']),
                transport_mode=row['transport_mode'],
                temperature_c=float(row['temperature_c']),
                congestion_factor=float(row['congestion_factor']),
                slope_degrees=float(row['slope_degrees']),
                is_uphill=bool(row.get('is_uphill', True)),
                weather_condition=row['weather_condition'],
                is_peak_hour=bool(row['is_peak_hour']),
                is_weekend=bool(row['is_weekend']),
            )
            feature_rows.append(_emission_model.get_physics_features(inp))

        phys_df = pd.DataFrame(feature_rows, index=df.index)
        # Rename to avoid collision with existing columns
        phys_df = phys_df.rename(columns={
            'ton_km': 'piem_ton_km',
            'emission_per_tonkm': 'piem_emission_per_tonkm',
            'emission_intensity': 'piem_emission_intensity',
        })
        return pd.concat([df, phys_df], axis=1)

    def generate_multi_scale_datasets(self, output_dir: str = "../data/processed") -> Dict[str, str]:
        """
        Generate datasets of different sizes for multi-scale evaluation.
        
        Args:
            output_dir: Directory to save generated datasets
            
        Returns:
            Dict[str, str]: Mapping of dataset size to file path
        """
        os.makedirs(output_dir, exist_ok=True)
        
        dataset_sizes = {'small': 50, 'medium': 200, 'large': 500}
        file_paths = {}
        
        for size_name, n_routes in dataset_sizes.items():
            df = self.generate_route_dataset(n_routes)
            
            filename = f"synthetic_routes_{size_name}_{n_routes}.csv"
            file_path = os.path.join(output_dir, filename)
            
            df.to_csv(file_path, index=False)
            file_paths[size_name] = file_path
            
            logger.info(f"Saved {size_name} dataset: {file_path} ({len(df)} routes)")
            
        return file_paths
        
    def get_dataset_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate descriptive statistics for the dataset.
        
        Args:
            df: Route dataset DataFrame
            
        Returns:
            Dict: Dataset statistics
        """
        stats = {
            'n_routes': len(df),
            'avg_distance_km': df['distance_km'].mean(),
            'avg_weight_tons': df['weight_tons'].mean(),
            'avg_cost': df['adjusted_cost'].mean(),
            'avg_emissions_kg_co2e': df['adjusted_emissions_kg_co2e'].mean(),
            'transport_mode_distribution': df['transport_mode'].value_counts().to_dict(),
            'commodity_distribution': df['commodity_type'].value_counts().to_dict(),
            'cost_range': (df['adjusted_cost'].min(), df['adjusted_cost'].max()),
            'emissions_range': (df['adjusted_emissions_kg_co2e'].min(), 
                              df['adjusted_emissions_kg_co2e'].max())
        }
        
        return stats


def main():
    """
    Main function to demonstrate synthetic dataset generation.
    """
    generator = SyntheticRouteGenerator(seed=42)
    
    # Generate sample dataset
    df = generator.generate_route_dataset(n_routes=100)
    
    # Display sample data
    print("Sample Generated Routes:")
    print(df.head())
    
    # Calculate and display statistics
    stats = generator.get_dataset_statistics(df)
    print(f"\nDataset Statistics:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
    
    # Generate multi-scale datasets
    file_paths = generator.generate_multi_scale_datasets()
    print(f"\nGenerated datasets: {file_paths}")


if __name__ == "__main__":
    main()
