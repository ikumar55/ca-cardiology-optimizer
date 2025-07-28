#!/usr/bin/env python3
"""
Travel Matrix Construction Script

This script builds a comprehensive travel time matrix between healthcare providers
and demand areas using the hybrid interpolation approach.
"""

import logging
import sys
from pathlib import Path

import pandas as pd

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.travel_matrix.travel_matrix_builder import TravelMatrixBuilder
from src.utils.logging import setup_logging


def main():
    """Main function to build the travel matrix."""
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting travel matrix construction")
    
    try:
        # Initialize the travel matrix builder
        builder = TravelMatrixBuilder(
            data_dir="data",
            output_dir="data/processed",
            max_error_rate=0.15,
            min_coverage=0.95
        )
        
        # Build the travel matrix
        travel_matrix = builder.build_travel_matrix()
        
        # Get and display summary
        summary = builder.get_matrix_summary()
        
        logger.info("Travel matrix construction completed successfully!")
        logger.info(f"Matrix Summary:")
        logger.info(f"  Total pairs: {summary['total_pairs']:,}")
        logger.info(f"  Coverage: {summary['coverage']:.2%}")
        logger.info(f"  Mean travel time: {summary['mean_travel_time']:.1f} minutes")
        logger.info(f"  Median travel time: {summary['median_travel_time']:.1f} minutes")
        logger.info(f"  Providers: {summary['providers_count']}")
        logger.info(f"  Demand areas: {summary['demand_areas_count']}")
        
        # Display sample of the matrix
        logger.info("\nSample of travel matrix:")
        print(travel_matrix.head(10).to_string(index=False))
        
        return travel_matrix
        
    except Exception as e:
        logger.error(f"Error building travel matrix: {e}")
        raise

if __name__ == "__main__":
    main() 