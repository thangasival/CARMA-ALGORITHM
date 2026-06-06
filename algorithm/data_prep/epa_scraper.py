"""
EPA Supply Chain GHG Emission Factors Data Scraper

This module downloads and processes EPA Supply Chain GHG Emission Factors v1.3
containing emission factors for 1,016 US commodities.

Data Source: https://catalog.data.gov/dataset/supply-chain-greenhouse-gas-emission-factors-v1-3-by-naics-6

"""

import pandas as pd
import requests
import os
from typing import Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EPAEmissionFactorsScraper:
    """
    Scraper for EPA Supply Chain GHG Emission Factors data.
    
    Downloads and processes emission factors for US commodities to create
    a standardized dataset for carbon emission calculations.
    """
    
    def __init__(self, data_dir: str = "../data/raw"):
        """
        Initialize the EPA data scraper.
        
        Args:
            data_dir: Directory to save raw data files
        """
        self.data_dir = data_dir
        self.base_url = "https://www.epa.gov/system/files/documents/2024-01/"
        self.filename = "supply_chain_emission_factors_v1_3.csv"
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
    def download_epa_data(self) -> bool:
        """
        Download EPA emission factors dataset.
        
        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            # Note: This is a placeholder URL - actual EPA data URL needs to be verified
            url = f"{self.base_url}{self.filename}"
            
            logger.info(f"Downloading EPA emission factors from {url}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            file_path = os.path.join(self.data_dir, self.filename)
            with open(file_path, 'wb') as f:
                f.write(response.content)
                
            logger.info(f"EPA data downloaded successfully to {file_path}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to download EPA data: {e}")
            return False
            
    def load_epa_data(self) -> Optional[pd.DataFrame]:
        """
        Load EPA emission factors data from local file.
        
        Returns:
            pd.DataFrame: EPA emission factors data or None if file not found
        """
        file_path = os.path.join(self.data_dir, self.filename)
        
        if not os.path.exists(file_path):
            logger.warning(f"EPA data file not found at {file_path}")
            return None
            
        try:
            df = pd.read_csv(file_path)
            logger.info(f"EPA data loaded: {len(df)} records, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load EPA data: {e}")
            return None
            
    def process_emission_factors(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process and clean EPA emission factors data.
        
        Args:
            df: Raw EPA emission factors DataFrame
            
        Returns:
            pd.DataFrame: Processed emission factors
        """
        if df is None:
            return None
            
        # Basic data cleaning and standardization
        processed_df = df.copy()
        
        # Standardize column names
        processed_df.columns = processed_df.columns.str.lower().str.replace(' ', '_')
        
        # Remove rows with missing emission factors
        processed_df = processed_df.dropna(subset=['emission_factor'])
        
        # Convert emission factors to numeric
        processed_df['emission_factor'] = pd.to_numeric(
            processed_df['emission_factor'], errors='coerce'
        )
        
        # Add commodity categories for grouping
        if 'naics_code' in processed_df.columns:
            processed_df['commodity_category'] = processed_df['naics_code'].astype(str).str[:2]
            
        logger.info(f"Processed EPA data: {len(processed_df)} valid records")
        return processed_df
        
    def save_processed_data(self, df: pd.DataFrame) -> None:
        """
        Save processed emission factors data.
        
        Args:
            df: Processed emission factors DataFrame
        """
        if df is None:
            return
            
        output_path = os.path.join(self.data_dir.replace('raw', 'processed'), 
                                 'epa_emission_factors_processed.csv')
        
        # Ensure processed data directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        df.to_csv(output_path, index=False)
        logger.info(f"Processed EPA data saved to {output_path}")
        
    def get_emission_factor(self, commodity_code: str, transport_mode: str = 'truck') -> float:
        """
        Get emission factor for specific commodity and transport mode.
        
        Args:
            commodity_code: NAICS commodity code
            transport_mode: Transportation mode (truck, rail, ship, air)
            
        Returns:
            float: Emission factor in kg CO2e per unit
        """
        # Placeholder implementation - to be completed with actual EPA data structure
        emission_factors = {
            'truck': 0.161,  # kg CO2e per ton-km
            'rail': 0.041,   # kg CO2e per ton-km  
            'ship': 0.015,   # kg CO2e per ton-km
            'air': 0.602     # kg CO2e per ton-km
        }
        
        return emission_factors.get(transport_mode, emission_factors['truck'])


def main():
    """
    Main function to demonstrate EPA data scraping and processing.
    """
    scraper = EPAEmissionFactorsScraper()
    
    # Download EPA data (uncomment when actual URL is available)
    # scraper.download_epa_data()
    
    # For now, create sample data for development
    sample_data = pd.DataFrame({
        'naics_code': ['111000', '112000', '113000'],
        'commodity_description': ['Crop Production', 'Animal Production', 'Forestry'],
        'emission_factor': [0.125, 0.189, 0.067],
        'unit': ['kg CO2e/USD', 'kg CO2e/USD', 'kg CO2e/USD']
    })
    
    # Process the data
    processed_data = scraper.process_emission_factors(sample_data)
    
    # Save processed data
    scraper.save_processed_data(processed_data)
    
    logger.info("EPA data scraping and processing completed")


if __name__ == "__main__":
    main()
