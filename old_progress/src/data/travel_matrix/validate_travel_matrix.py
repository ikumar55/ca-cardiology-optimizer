#!/usr/bin/env python3
"""
Validate Geographic Realism of California Travel Times

This script performs quality checks to ensure that computed travel times
are geographically plausible within California.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TravelMatrixValidator:
    """Validate the geographic realism of California travel times."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.travel_matrix = None
        self.provider_data = None
        self.demand_data = None
        
        # Known California city pairs with approximate travel times
        self.known_city_pairs = {
            # LA Metro Area
            ('90001', '90210'): (25, 35),  # Downtown LA to Beverly Hills
            ('90001', '90211'): (20, 30),  # Downtown LA to West Hollywood
            ('90001', '90212'): (30, 40),  # Downtown LA to Brentwood
            
            # SF Bay Area
            ('94102', '94105'): (10, 15),  # SF Civic Center to Financial District
            ('94102', '94108'): (8, 12),   # SF Civic Center to Chinatown
            ('94102', '94109'): (12, 18),  # SF Civic Center to North Beach
            
            # San Diego Area
            ('92101', '92102'): (8, 12),   # Downtown SD to Little Italy
            ('92101', '92103'): (10, 15),  # Downtown SD to Hillcrest
            ('92101', '92104'): (12, 18),  # Downtown SD to North Park
            
            # Cross-region (should be longer)
            ('90001', '94102'): (360, 420),  # LA to SF (6-7 hours)
            ('90001', '92101'): (120, 150),  # LA to San Diego (2-2.5 hours)
            ('94102', '92101'): (480, 540),  # SF to San Diego (8-9 hours)
        }
    
    def load_data(self):
        """Load travel matrix and supporting data."""
        logger.info("Loading travel matrix and supporting data...")
        
        # Load travel matrix
        travel_matrix_file = self.data_dir / "processed" / "travel_matrix.parquet"
        if not travel_matrix_file.exists():
            raise FileNotFoundError(f"Travel matrix not found: {travel_matrix_file}")
        
        self.travel_matrix = pd.read_parquet(travel_matrix_file)
        logger.info(f"Loaded travel matrix with {len(self.travel_matrix)} pairs")
        
        # Load provider data
        provider_file = self.data_dir / "processed" / "ca_providers_filtered.csv"
        if provider_file.exists():
            self.provider_data = pd.read_csv(provider_file)
            logger.info(f"Loaded {len(self.provider_data)} providers")
        
        # Load demand data
        demand_file = self.data_dir / "processed" / "ca_demand_filtered.csv"
        if demand_file.exists():
            self.demand_data = pd.read_csv(demand_file)
            logger.info(f"Loaded {len(self.demand_data)} demand areas")
    
    def validate_known_city_pairs(self) -> Dict:
        """Validate travel times for known city pairs."""
        logger.info("Validating known city pairs...")
        
        results = {}
        
        for (zip1, zip2), (expected_min, expected_max) in self.known_city_pairs.items():
            # Find travel times for this pair
            mask = (
                (self.travel_matrix['zip_code'] == zip1) & 
                (self.travel_matrix['provider_npi'].isin(
                    self.provider_data[self.provider_data['zip_code'] == zip2]['provider_npi']
                ))
            ) | (
                (self.travel_matrix['zip_code'] == zip2) & 
                (self.travel_matrix['provider_npi'].isin(
                    self.provider_data[self.provider_data['zip_code'] == zip1]['provider_npi']
                ))
            )
            
            if mask.any():
                actual_times = self.travel_matrix[mask]['drive_minutes']
                mean_time = actual_times.mean()
                median_time = actual_times.median()
                
                # Check if within expected range
                is_realistic = expected_min <= mean_time <= expected_max
                
                results[f"{zip1}-{zip2}"] = {
                    'expected_range': (expected_min, expected_max),
                    'actual_mean': mean_time,
                    'actual_median': median_time,
                    'actual_count': len(actual_times),
                    'is_realistic': is_realistic,
                    'actual_values': actual_times.tolist()
                }
                
                logger.info(f"{zip1}-{zip2}: Expected {expected_min}-{expected_max} min, "
                          f"Actual mean: {mean_time:.1f} min, Realistic: {is_realistic}")
            else:
                logger.warning(f"No data found for city pair {zip1}-{zip2}")
        
        return results
    
    def analyze_travel_time_distribution(self) -> Dict:
        """Analyze the distribution of travel times for anomalies."""
        logger.info("Analyzing travel time distribution...")
        
        travel_times = self.travel_matrix['drive_minutes']
        
        # Basic statistics
        stats = {
            'count': len(travel_times),
            'mean': travel_times.mean(),
            'median': travel_times.median(),
            'std': travel_times.std(),
            'min': travel_times.min(),
            'max': travel_times.max(),
            'q25': travel_times.quantile(0.25),
            'q75': travel_times.quantile(0.75),
            'iqr': travel_times.quantile(0.75) - travel_times.quantile(0.25)
        }
        
        # Identify anomalies
        q1 = travel_times.quantile(0.25)
        q3 = travel_times.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = travel_times[(travel_times < lower_bound) | (travel_times > upper_bound)]
        
        # Check for unrealistic values
        too_short = travel_times[travel_times < 1]  # Less than 1 minute
        too_long = travel_times[travel_times > 300]  # More than 5 hours
        exactly_180 = travel_times[travel_times == 180.0]  # Fallback value
        
        analysis = {
            'basic_stats': stats,
            'outliers_count': len(outliers),
            'outliers_percentage': len(outliers) / len(travel_times) * 100,
            'too_short_count': len(too_short),
            'too_long_count': len(too_long),
            'exactly_180_count': len(exactly_180),
            'exactly_180_percentage': len(exactly_180) / len(travel_times) * 100,
            'realistic_range': (lower_bound, upper_bound)
        }
        
        logger.info(f"Travel time analysis:")
        logger.info(f"  Mean: {stats['mean']:.1f} minutes")
        logger.info(f"  Median: {stats['median']:.1f} minutes")
        logger.info(f"  Outliers: {len(outliers)} ({len(outliers)/len(travel_times)*100:.1f}%)")
        logger.info(f"  Exactly 180 min: {len(exactly_180)} ({len(exactly_180)/len(travel_times)*100:.1f}%)")
        
        return analysis
    
    def check_missing_zip_codes(self) -> Dict:
        """Check for providers with missing ZIP codes in the database."""
        logger.info("Checking for missing ZIP codes...")
        
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
        from src.data.travel_matrix.zip_coordinates_db import ZipCoordinatesDB
        
        db = ZipCoordinatesDB()
        provider_zips = self.provider_data['zip_code'].unique()
        
        found_zips = [zip_code for zip_code in provider_zips if str(zip_code) in db.coordinates]
        missing_zips = [zip_code for zip_code in provider_zips if str(zip_code) not in db.coordinates]
        
        # Check impact of missing ZIP codes
        missing_providers = self.provider_data[
            self.provider_data['zip_code'].isin(missing_zips)
        ]['provider_npi'].unique()
        
        missing_pairs = self.travel_matrix[
            self.travel_matrix['provider_npi'].isin(missing_providers)
        ]
        
        analysis = {
            'total_provider_zips': len(provider_zips),
            'found_zips': len(found_zips),
            'missing_zips': len(missing_zips),
            'missing_zip_codes': missing_zips,
            'missing_providers': len(missing_providers),
            'missing_pairs': len(missing_pairs),
            'missing_pairs_percentage': len(missing_pairs) / len(self.travel_matrix) * 100
        }
        
        logger.info(f"ZIP code analysis:")
        logger.info(f"  Found: {len(found_zips)}/{len(provider_zips)} provider ZIP codes")
        logger.info(f"  Missing: {len(missing_zips)} ZIP codes")
        logger.info(f"  Impact: {len(missing_pairs)} pairs ({len(missing_pairs)/len(self.travel_matrix)*100:.1f}%)")
        
        return analysis
    
    def generate_validation_report(self) -> Dict:
        """Generate a comprehensive validation report."""
        logger.info("Generating validation report...")
        
        report = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'matrix_info': {
                'total_pairs': len(self.travel_matrix),
                'unique_providers': self.travel_matrix['provider_npi'].nunique(),
                'unique_demand_areas': self.travel_matrix['zip_code'].nunique(),
                'coverage': 1 - self.travel_matrix['drive_minutes'].isna().mean()
            },
            'known_city_pairs': self.validate_known_city_pairs(),
            'travel_time_analysis': self.analyze_travel_time_distribution(),
            'missing_zip_analysis': self.check_missing_zip_codes(),
            'recommendations': []
        }
        
        # Generate recommendations
        if report['travel_time_analysis']['exactly_180_percentage'] > 50:
            report['recommendations'].append(
                "High percentage of 180-minute travel times indicates fallback method overuse. "
                "Consider adding missing ZIP codes to database or improving fallback estimation."
            )
        
        if report['travel_time_analysis']['too_short_count'] > 0:
            report['recommendations'].append(
                f"Found {report['travel_time_analysis']['too_short_count']} travel times < 1 minute. "
                "These may be unrealistic and should be investigated."
            )
        
        if report['travel_time_analysis']['too_long_count'] > 0:
            report['recommendations'].append(
                f"Found {report['travel_time_analysis']['too_long_count']} travel times > 5 hours. "
                "These may be unrealistic for California travel."
            )
        
        if report['missing_zip_analysis']['missing_pairs_percentage'] > 10:
            report['recommendations'].append(
                f"Missing ZIP codes affect {report['missing_zip_analysis']['missing_pairs_percentage']:.1f}% of pairs. "
                "Consider adding missing ZIP codes to improve accuracy."
            )
        
        return report
    
    def save_validation_report(self, report: Dict):
        """Save validation report to file."""
        output_file = self.data_dir / "processed" / "travel_matrix_validation_report.json"
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Validation report saved to {output_file}")
    
    def create_visualizations(self):
        """Create visualizations of travel time distribution."""
        logger.info("Creating visualizations...")
        
        # Create output directory
        output_dir = self.data_dir / "processed" / "validation_plots"
        output_dir.mkdir(exist_ok=True)
        
        # Travel time distribution histogram
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        plt.hist(self.travel_matrix['drive_minutes'], bins=50, alpha=0.7, edgecolor='black')
        plt.title('Travel Time Distribution')
        plt.xlabel('Drive Minutes')
        plt.ylabel('Frequency')
        plt.axvline(self.travel_matrix['drive_minutes'].median(), color='red', linestyle='--', label='Median')
        plt.legend()
        
        # Box plot
        plt.subplot(2, 2, 2)
        plt.boxplot(self.travel_matrix['drive_minutes'])
        plt.title('Travel Time Box Plot')
        plt.ylabel('Drive Minutes')
        
        # Log scale histogram (to see distribution better)
        plt.subplot(2, 2, 3)
        plt.hist(self.travel_matrix['drive_minutes'], bins=50, alpha=0.7, edgecolor='black')
        plt.title('Travel Time Distribution (Log Scale)')
        plt.xlabel('Drive Minutes')
        plt.ylabel('Frequency')
        plt.yscale('log')
        
        # Travel time vs distance (if we had distance data)
        plt.subplot(2, 2, 4)
        # For now, just show the distribution of unique values
        unique_times = self.travel_matrix['drive_minutes'].value_counts().sort_index()
        plt.plot(unique_times.index, unique_times.values, 'o-')
        plt.title('Unique Travel Time Values')
        plt.xlabel('Drive Minutes')
        plt.ylabel('Count')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'travel_time_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Visualizations saved to {output_dir}")

def main():
    """Main validation function."""
    logger.info("Starting travel matrix validation...")
    
    validator = TravelMatrixValidator()
    
    try:
        # Load data
        validator.load_data()
        
        # Generate validation report
        report = validator.generate_validation_report()
        
        # Save report
        validator.save_validation_report(report)
        
        # Create visualizations
        validator.create_visualizations()
        
        # Print summary
        print("\n" + "="*60)
        print("TRAVEL MATRIX VALIDATION SUMMARY")
        print("="*60)
        print(f"Total pairs: {report['matrix_info']['total_pairs']:,}")
        print(f"Coverage: {report['matrix_info']['coverage']:.1%}")
        print(f"Mean travel time: {report['travel_time_analysis']['basic_stats']['mean']:.1f} minutes")
        print(f"Median travel time: {report['travel_time_analysis']['basic_stats']['median']:.1f} minutes")
        print(f"Exactly 180 min: {report['travel_time_analysis']['exactly_180_percentage']:.1f}%")
        print(f"Missing ZIP impact: {report['missing_zip_analysis']['missing_pairs_percentage']:.1f}%")
        
        print("\nRECOMMENDATIONS:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
        
        print("\nValidation completed successfully!")
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise

if __name__ == "__main__":
    main() 