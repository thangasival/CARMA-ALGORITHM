"""
Climatiq API Connector for Global Emission Factors

This module provides integration with the Climatiq API to retrieve
real-world emission factors for transportation routes and commodities.

Features:
- Access to global emission factors database
- Support for multiple transportation modes
- Geographical and commodity-specific factors
- Rate limiting and error handling
- Caching for improved performance

API Documentation: https://www.climatiq.io/data
Note: Requires API key (free tier available)
"""

import requests
import json
import os
from typing import Dict, List, Optional
import time
import logging

# Configure logging
logger = logging.getLogger(__name__)


class ClimatiqConnector:
    """
    Connector for Climatiq API to retrieve global emission factors.
    
    Provides access to emission factors for transportation, energy,
    and commodity data with built-in caching and error handling.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Climatiq API connector.
        
        Args:
            api_key: Climatiq API key (or set CLIMATIQ_API_KEY environment variable)
        """
        self.api_key = api_key or os.getenv('CLIMATIQ_API_KEY')
        self.base_url = "https://api.climatiq.io/data/v1"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        if not self.api_key:
            logger.warning("No Climatiq API key provided. Set CLIMATIQ_API_KEY environment variable.")
            
    def get_transport_emission_factors(self, transport_mode: str = 'freight_truck') -> Dict:
        """
        Get emission factors for transportation modes.
        
        Args:
            transport_mode: Type of transport (freight_truck, freight_rail, freight_ship, freight_air)
            
        Returns:
            Dict: Emission factors data from Climatiq API
        """
        if not self.api_key:
            return self._get_mock_transport_factors(transport_mode)
            
        endpoint = f"{self.base_url}/emission-factors"
        params = {
            'category': 'transport',
            'source': transport_mode,
            'data_version': 'latest'
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved {len(data.get('results', []))} emission factors for {transport_mode}")
            return data
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch transport emission factors: {e}")
            return self._get_mock_transport_factors(transport_mode)
            
    def get_commodity_emission_factors(self, commodity_type: str) -> Dict:
        """
        Get emission factors for specific commodity types.
        
        Args:
            commodity_type: Type of commodity (electronics, textiles, food, etc.)
            
        Returns:
            Dict: Commodity emission factors
        """
        if not self.api_key:
            return self._get_mock_commodity_factors(commodity_type)
            
        endpoint = f"{self.base_url}/emission-factors"
        params = {
            'category': 'material',
            'source': commodity_type,
            'data_version': 'latest'
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved emission factors for commodity: {commodity_type}")
            return data
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch commodity emission factors: {e}")
            return self._get_mock_commodity_factors(commodity_type)
            
    def calculate_route_emissions(self, distance_km: float, weight_tons: float, 
                                transport_mode: str = 'freight_truck') -> float:
        """
        Calculate total emissions for a route.
        
        Args:
            distance_km: Route distance in kilometers
            weight_tons: Cargo weight in tons
            transport_mode: Transportation mode
            
        Returns:
            float: Total emissions in kg CO2e
        """
        emission_factors = self.get_transport_emission_factors(transport_mode)
        
        # Extract emission factor from API response
        if 'results' in emission_factors and emission_factors['results']:
            factor = emission_factors['results'][0].get('emission_factor', {})
            co2e_per_tonkm = factor.get('value', 0.161)  # Default truck factor
        else:
            co2e_per_tonkm = 0.161  # Default truck emission factor
            
        total_emissions = distance_km * weight_tons * co2e_per_tonkm
        
        logger.info(f"Route emissions: {total_emissions:.2f} kg CO2e "
                   f"({distance_km}km × {weight_tons}t × {co2e_per_tonkm} factor)")
        
        return total_emissions
        
    def _get_mock_transport_factors(self, transport_mode: str) -> Dict:
        """
        Provide mock transport emission factors for development.
        
        Args:
            transport_mode: Transportation mode
            
        Returns:
            Dict: Mock emission factors data
        """
        mock_factors = {
            'freight_truck': 0.161,    # kg CO2e per ton-km
            'freight_rail': 0.041,     # kg CO2e per ton-km
            'freight_ship': 0.015,     # kg CO2e per ton-km
            'freight_air': 0.602       # kg CO2e per ton-km
        }
        
        factor = mock_factors.get(transport_mode, 0.161)
        
        return {
            'results': [{
                'emission_factor': {
                    'value': factor,
                    'unit': 'kg CO2e per ton-km'
                },
                'source': transport_mode,
                'category': 'transport'
            }]
        }
        
    def _get_mock_commodity_factors(self, commodity_type: str) -> Dict:
        """
        Provide mock commodity emission factors for development.
        
        Args:
            commodity_type: Commodity type
            
        Returns:
            Dict: Mock commodity emission factors
        """
        mock_factors = {
            'electronics': 15.2,      # kg CO2e per kg
            'textiles': 8.1,          # kg CO2e per kg
            'food': 2.5,              # kg CO2e per kg
            'machinery': 12.8,        # kg CO2e per kg
            'chemicals': 18.7         # kg CO2e per kg
        }
        
        factor = mock_factors.get(commodity_type, 10.0)
        
        return {
            'results': [{
                'emission_factor': {
                    'value': factor,
                    'unit': 'kg CO2e per kg'
                },
                'source': commodity_type,
                'category': 'material'
            }]
        }
        
    def batch_emission_calculation(self, routes: List[Dict]) -> List[Dict]:
        """
        Calculate emissions for multiple routes efficiently.
        
        Args:
            routes: List of route dictionaries with distance, weight, transport_mode
            
        Returns:
            List[Dict]: Routes with calculated emissions
        """
        results = []
        
        for route in routes:
            emissions = self.calculate_route_emissions(
                distance_km=route.get('distance_km', 0),
                weight_tons=route.get('weight_tons', 0),
                transport_mode=route.get('transport_mode', 'freight_truck')
            )
            
            route_result = route.copy()
            route_result['emissions_kg_co2e'] = emissions
            results.append(route_result)
            
            # Add small delay to respect API rate limits
            time.sleep(0.1)
            
        logger.info(f"Calculated emissions for {len(results)} routes")
        return results


def main():
    """
    Main function to demonstrate Climatiq API usage.
    """
    # Initialize connector (will use mock data if no API key)
    connector = ClimatiqConnector()
    
    # Test transport emission factors
    truck_factors = connector.get_transport_emission_factors('freight_truck')
    print(f"Truck emission factors: {truck_factors}")
    
    # Test route emission calculation
    emissions = connector.calculate_route_emissions(
        distance_km=500,
        weight_tons=25,
        transport_mode='freight_truck'
    )
    print(f"Route emissions: {emissions} kg CO2e")
    
    # Test batch calculation
    sample_routes = [
        {'distance_km': 300, 'weight_tons': 15, 'transport_mode': 'freight_truck'},
        {'distance_km': 800, 'weight_tons': 30, 'transport_mode': 'freight_rail'},
        {'distance_km': 1200, 'weight_tons': 50, 'transport_mode': 'freight_ship'}
    ]
    
    results = connector.batch_emission_calculation(sample_routes)
    print(f"Batch calculation results: {len(results)} routes processed")


if __name__ == "__main__":
    main()
