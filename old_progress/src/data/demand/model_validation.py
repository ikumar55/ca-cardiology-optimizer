"""
Model validation and calibration for the Cardiology Care Optimization System.

This module validates the ensemble demand model against known health trends,
performs sensitivity analysis, and calibrates parameters for optimal performance.
"""

import logging
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

warnings.filterwarnings("ignore")

try:
    from ...utils.logging import get_logger
except ImportError:
    # Fallback for standalone testing
    def get_logger(name):
        return logging.getLogger(name)


logger = get_logger(__name__)


class EnsembleModelValidator:
    """Validate and calibrate the ensemble demand model."""

    def __init__(
        self, ensemble_model_path: str = "data/processed/ensemble_demand_model.csv"
    ):
        """Initialize the model validator."""
        self.ensemble_model_path = ensemble_model_path
        self.ensemble_data = None
        self.validation_results = {}
        self.calibration_results = {}

        # Known California health trends for validation
        self.ca_health_benchmarks = {
            "avg_heart_disease_prevalence": 0.065,  # 6.5% average CHD prevalence
            "avg_stroke_prevalence": 0.032,  # 3.2% average stroke prevalence
            "avg_high_bp_prevalence": 0.285,  # 28.5% average high BP prevalence
            "rural_healthcare_access_ratio": 0.7,  # Rural areas have 70% of urban access
            "poverty_health_correlation": 0.4,  # Moderate positive correlation
            "elderly_utilization_ratio": 2.5,  # Elderly use 2.5x more cardiology services
        }

        # Validation thresholds
        self.validation_thresholds = {
            "demand_score_range": (0.0, 1.0),
            "component_correlation_max": 0.8,
            "geographic_consistency_threshold": 0.7,
            "sensitivity_threshold": 0.1,
        }

    def load_ensemble_data(self) -> pd.DataFrame:
        """Load the ensemble model data for validation."""
        logger.info("Loading ensemble model data for validation...")

        if not Path(self.ensemble_model_path).exists():
            raise FileNotFoundError(
                f"Ensemble model file not found: {self.ensemble_model_path}"
            )

        self.ensemble_data = pd.read_csv(self.ensemble_model_path)
        logger.info(f"Loaded ensemble data: {self.ensemble_data.shape}")

        return self.ensemble_data

    def validate_demand_score_distribution(self) -> dict:
        """Validate the distribution of ensemble demand scores."""
        logger.info("Validating demand score distribution...")

        if self.ensemble_data is None:
            self.load_ensemble_data()

        if (
            self.ensemble_data is None
            or "ensemble_demand_score" not in self.ensemble_data.columns
        ):
            raise ValueError(
                "Ensemble data not loaded or missing ensemble_demand_score column"
            )

        demand_scores = self.ensemble_data["ensemble_demand_score"]

        # Basic distribution validation
        distribution_stats = {
            "mean": demand_scores.mean(),
            "std": demand_scores.std(),
            "min": demand_scores.min(),
            "max": demand_scores.max(),
            "median": demand_scores.median(),
            "skewness": stats.skew(demand_scores),
            "kurtosis": stats.kurtosis(demand_scores),
        }

        # Validate range
        min_score = float(distribution_stats["min"])
        max_score = float(distribution_stats["max"])
        range_valid = (
            min_score >= self.validation_thresholds["demand_score_range"][0]
            and max_score <= self.validation_thresholds["demand_score_range"][1]
        )

        # Validate realistic distribution
        mean_score = float(distribution_stats["mean"])
        std_score = float(distribution_stats["std"])
        realistic_distribution = (
            mean_score > 0.2  # Should have meaningful demand
            and mean_score < 0.8  # Shouldn't be universally high
            and std_score > 0.1  # Should have meaningful variation
        )

        validation_result = {
            "distribution_stats": distribution_stats,
            "range_valid": range_valid,
            "realistic_distribution": realistic_distribution,
            "overall_valid": range_valid and realistic_distribution,
        }

        self.validation_results["demand_distribution"] = validation_result
        logger.info(
            f"Demand distribution validation: {'PASS' if validation_result['overall_valid'] else 'FAIL'}"
        )

        return validation_result

    def validate_component_correlations(self) -> dict:
        """Validate correlations between demand components."""
        logger.info("Validating component correlations...")

        if self.ensemble_data is None:
            self.load_ensemble_data()

        # Calculate correlations between components
        components = [
            "health_demand_component",
            "unmet_need_component",
            "demographic_demand_component",
        ]
        correlation_matrix = self.ensemble_data[components].corr()

        # Check for multicollinearity (high correlations)
        high_correlations = []
        for i in range(len(components)):
            for j in range(i + 1, len(components)):
                corr_value = correlation_matrix.iloc[i, j]
                if (
                    abs(corr_value)
                    > self.validation_thresholds["component_correlation_max"]
                ):
                    high_correlations.append(
                        {
                            "component1": components[i],
                            "component2": components[j],
                            "correlation": corr_value,
                        }
                    )

        # Validate independence
        components_independent = len(high_correlations) == 0

        validation_result = {
            "correlation_matrix": correlation_matrix.to_dict(),
            "high_correlations": high_correlations,
            "components_independent": components_independent,
            "overall_valid": components_independent,
        }

        self.validation_results["component_correlations"] = validation_result
        logger.info(
            f"Component correlation validation: {'PASS' if validation_result['overall_valid'] else 'FAIL'}"
        )

        return validation_result

    def validate_geographic_consistency(self) -> dict:
        """Validate geographic consistency of demand patterns."""
        logger.info("Validating geographic consistency...")

        if self.ensemble_data is None:
            self.load_ensemble_data()

        # Check for geographic clustering of high/low demand areas
        zctas = self.ensemble_data["zcta"].astype(str)
        demand_scores = self.ensemble_data["ensemble_demand_score"]

        # Analyze first 3 digits (approximate region)
        regions = zctas.str[:3].astype(int)
        region_demand = pd.DataFrame({"region": regions, "demand_score": demand_scores})

        # Calculate regional consistency
        regional_stats = (
            region_demand.groupby("region")
            .agg({"demand_score": ["mean", "std", "count"]})
            .round(3)
        )

        # Check for geographic anomalies (regions with extreme demand)
        regional_means = regional_stats[("demand_score", "mean")]
        regional_std = regional_stats[("demand_score", "std")]

        # Identify anomalous regions
        anomalous_regions = []
        for region in regional_means.index:
            mean_demand = regional_means[region]
            std_demand = regional_std[region]

            # Flag regions with extreme demand patterns
            if mean_demand > 0.8 or mean_demand < 0.2:
                anomalous_regions.append(
                    {
                        "region": region,
                        "mean_demand": mean_demand,
                        "std_demand": std_demand,
                        "reason": "extreme_demand",
                    }
                )

        # Calculate geographic consistency score
        consistency_score = 1 - (len(anomalous_regions) / len(regional_means))
        geographic_consistent = (
            consistency_score
            >= self.validation_thresholds["geographic_consistency_threshold"]
        )

        validation_result = {
            "regional_stats": regional_stats.to_dict(),
            "anomalous_regions": anomalous_regions,
            "consistency_score": consistency_score,
            "geographic_consistent": geographic_consistent,
            "overall_valid": geographic_consistent,
        }

        self.validation_results["geographic_consistency"] = validation_result
        logger.info(
            f"Geographic consistency validation: {'PASS' if validation_result['overall_valid'] else 'FAIL'}"
        )

        return validation_result

    def validate_against_known_trends(self) -> dict:
        """Validate model outputs against known California health trends."""
        logger.info("Validating against known California health trends...")

        if self.ensemble_data is None:
            self.load_ensemble_data()

        validation_results = {}

        # 1. Validate heart disease prevalence patterns
        if "CHD" in self.ensemble_data.columns:
            chd_prevalence = self.ensemble_data["CHD"].mean()
            chd_deviation = abs(
                chd_prevalence
                - self.ca_health_benchmarks["avg_heart_disease_prevalence"]
            )
            chd_valid = chd_deviation < 0.02  # Within 2% of benchmark

            validation_results["heart_disease_prevalence"] = {
                "model_mean": chd_prevalence,
                "benchmark": self.ca_health_benchmarks["avg_heart_disease_prevalence"],
                "deviation": chd_deviation,
                "valid": chd_valid,
            }

        # 2. Validate poverty-health correlation
        if (
            "poverty_pct" in self.ensemble_data.columns
            and "ensemble_demand_score" in self.ensemble_data.columns
        ):
            poverty_correlation = self.ensemble_data["poverty_pct"].corr(
                self.ensemble_data["ensemble_demand_score"]
            )
            poverty_correlation_valid = poverty_correlation > 0.2  # Should be positive

            validation_results["poverty_health_correlation"] = {
                "model_correlation": poverty_correlation,
                "benchmark": self.ca_health_benchmarks["poverty_health_correlation"],
                "valid": poverty_correlation_valid,
            }

        # 3. Validate elderly utilization patterns
        if (
            "age_65_plus_pct" in self.ensemble_data.columns
            and "unmet_need_component" in self.ensemble_data.columns
        ):
            elderly_correlation = self.ensemble_data["age_65_plus_pct"].corr(
                self.ensemble_data["unmet_need_component"]
            )
            elderly_correlation_valid = (
                elderly_correlation > 0.1
            )  # Elderly should have higher unmet need

            validation_results["elderly_utilization"] = {
                "model_correlation": elderly_correlation,
                "expected_positive": True,
                "valid": elderly_correlation_valid,
            }

        # Overall validation
        overall_valid = all(result["valid"] for result in validation_results.values())

        validation_result = {
            "trend_validations": validation_results,
            "overall_valid": overall_valid,
        }

        self.validation_results["known_trends"] = validation_result
        logger.info(
            f"Known trends validation: {'PASS' if validation_result['overall_valid'] else 'FAIL'}"
        )

        return validation_result

    def perform_sensitivity_analysis(self) -> dict:
        """Perform sensitivity analysis on model parameters."""
        logger.info("Performing sensitivity analysis...")

        if self.ensemble_data is None:
            self.load_ensemble_data()

        # Test different weight combinations
        base_weights = {"health": 0.4, "unmet_need": 0.35, "demographic": 0.25}
        weight_variations = [
            {"health": 0.5, "unmet_need": 0.3, "demographic": 0.2},
            {"health": 0.3, "unmet_need": 0.5, "demographic": 0.2},
            {"health": 0.3, "unmet_need": 0.3, "demographic": 0.4},
            {"health": 0.33, "unmet_need": 0.33, "demographic": 0.34},
        ]

        sensitivity_results = {}

        # Calculate base demand scores
        base_scores = (
            base_weights["health"] * self.ensemble_data["health_demand_component"]
            + base_weights["unmet_need"] * self.ensemble_data["unmet_need_component"]
            + base_weights["demographic"]
            * self.ensemble_data["demographic_demand_component"]
        )

        # Test each weight variation
        for i, weights in enumerate(weight_variations):
            variation_scores = (
                weights["health"] * self.ensemble_data["health_demand_component"]
                + weights["unmet_need"] * self.ensemble_data["unmet_need_component"]
                + weights["demographic"]
                * self.ensemble_data["demographic_demand_component"]
            )

            # Calculate correlation with base scores
            correlation = base_scores.corr(variation_scores)

            # Calculate ranking stability
            base_rankings = base_scores.rank()
            variation_rankings = variation_scores.rank()
            ranking_correlation = base_rankings.corr(variation_rankings)

            sensitivity_results[f"variation_{i+1}"] = {
                "weights": weights,
                "score_correlation": correlation,
                "ranking_correlation": ranking_correlation,
                "stable": ranking_correlation > 0.8,  # Rankings should be stable
            }

        # Overall sensitivity assessment
        stable_variations = sum(
            1 for result in sensitivity_results.values() if result["stable"]
        )
        overall_stable = (
            stable_variations >= len(weight_variations) * 0.75
        )  # 75% should be stable

        sensitivity_result = {
            "base_weights": base_weights,
            "variations_tested": len(weight_variations),
            "sensitivity_results": sensitivity_results,
            "stable_variations": stable_variations,
            "overall_stable": overall_stable,
        }

        self.validation_results["sensitivity_analysis"] = sensitivity_result
        logger.info(
            f"Sensitivity analysis: {'STABLE' if sensitivity_result['overall_stable'] else 'UNSTABLE'}"
        )

        return sensitivity_result

    def calibrate_model_parameters(self) -> dict:
        """Calibrate model parameters based on validation results."""
        logger.info("Calibrating model parameters...")

        if not self.validation_results:
            raise ValueError("Must run validation before calibration")

        calibration_recommendations = []

        # Check demand distribution calibration
        if "demand_distribution" in self.validation_results:
            dist_result = self.validation_results["demand_distribution"]
            if not dist_result["realistic_distribution"]:
                calibration_recommendations.append(
                    {
                        "parameter": "demand_score_normalization",
                        "issue": "Unrealistic demand distribution",
                        "recommendation": "Adjust normalization method or component weights",
                    }
                )

        # Check component correlation calibration
        if "component_correlations" in self.validation_results:
            corr_result = self.validation_results["component_correlations"]
            if not corr_result["components_independent"]:
                calibration_recommendations.append(
                    {
                        "parameter": "component_weights",
                        "issue": "High component correlations detected",
                        "recommendation": "Reduce weight of highly correlated components",
                    }
                )

        # Check geographic consistency calibration
        if "geographic_consistency" in self.validation_results:
            geo_result = self.validation_results["geographic_consistency"]
            if not geo_result["geographic_consistent"]:
                calibration_recommendations.append(
                    {
                        "parameter": "geographic_alignment",
                        "issue": "Geographic inconsistencies detected",
                        "recommendation": "Improve ZCTA-to-ZIP mapping or add geographic smoothing",
                    }
                )

        # Generate optimal weight recommendations
        optimal_weights = self._calculate_optimal_weights()

        calibration_result = {
            "recommendations": calibration_recommendations,
            "optimal_weights": optimal_weights,
            "calibration_needed": len(calibration_recommendations) > 0,
        }

        self.calibration_results = calibration_result
        logger.info(
            f"Calibration complete: {len(calibration_recommendations)} recommendations"
        )

        return calibration_result

    def _calculate_optimal_weights(self) -> dict:
        """Calculate optimal component weights based on validation results."""
        # Start with current weights
        current_weights = {"health": 0.4, "unmet_need": 0.35, "demographic": 0.25}

        # Adjust based on validation results
        if "known_trends" in self.validation_results:
            trends = self.validation_results["known_trends"]["trend_validations"]

            # If poverty correlation is weak, increase demographic weight
            if (
                "poverty_health_correlation" in trends
                and not trends["poverty_health_correlation"]["valid"]
            ):
                current_weights["demographic"] = min(
                    0.35, current_weights["demographic"] + 0.05
                )
                current_weights["health"] = max(0.35, current_weights["health"] - 0.025)
                current_weights["unmet_need"] = max(
                    0.30, current_weights["unmet_need"] - 0.025
                )

        # Normalize weights to sum to 1.0
        total_weight = sum(current_weights.values())
        optimal_weights = {k: v / total_weight for k, v in current_weights.items()}

        return optimal_weights

    def create_validation_visualizations(
        self, output_dir: str = "data/processed/validation_plots"
    ):
        """Create validation visualizations."""
        logger.info("Creating validation visualizations...")

        if self.ensemble_data is None:
            self.load_ensemble_data()

        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Set up plotting style
        plt.style.use("default")
        sns.set_palette("husl")

        # 1. Demand Score Distribution
        plt.figure(figsize=(12, 8))

        plt.subplot(2, 3, 1)
        plt.hist(
            self.ensemble_data["ensemble_demand_score"],
            bins=20,
            alpha=0.7,
            color="skyblue",
        )
        plt.title("Ensemble Demand Score Distribution")
        plt.xlabel("Demand Score")
        plt.ylabel("Frequency")

        # 2. Component Distributions
        plt.subplot(2, 3, 2)
        components = [
            "health_demand_component",
            "unmet_need_component",
            "demographic_demand_component",
        ]
        component_data = [self.ensemble_data[comp] for comp in components]
        plt.boxplot(component_data, labels=["Health", "Unmet Need", "Demographic"])
        plt.title("Component Score Distributions")
        plt.ylabel("Score")

        # 3. Component Correlations
        plt.subplot(2, 3, 3)
        correlation_matrix = self.ensemble_data[components].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", center=0)
        plt.title("Component Correlations")

        # 4. Geographic Demand Pattern
        plt.subplot(2, 3, 4)
        regions = self.ensemble_data["zcta"].astype(str).str[:3].astype(int)
        region_demand = self.ensemble_data.groupby(regions)[
            "ensemble_demand_score"
        ].mean()
        plt.bar(range(len(region_demand)), region_demand.values, alpha=0.7)
        plt.title("Regional Demand Patterns")
        plt.xlabel("Region (First 3 ZCTA digits)")
        plt.ylabel("Average Demand Score")

        # 5. Poverty vs Demand
        plt.subplot(2, 3, 5)
        if "poverty_pct" in self.ensemble_data.columns:
            plt.scatter(
                self.ensemble_data["poverty_pct"],
                self.ensemble_data["ensemble_demand_score"],
                alpha=0.6,
            )
            plt.xlabel("Poverty Percentage")
            plt.ylabel("Demand Score")
            plt.title("Poverty vs Demand Score")

        # 6. Elderly vs Unmet Need
        plt.subplot(2, 3, 6)
        if "age_65_plus_pct" in self.ensemble_data.columns:
            plt.scatter(
                self.ensemble_data["age_65_plus_pct"],
                self.ensemble_data["unmet_need_component"],
                alpha=0.6,
            )
            plt.xlabel("Elderly Percentage (65+)")
            plt.ylabel("Unmet Need Score")
            plt.title("Elderly Population vs Unmet Need")

        plt.tight_layout()
        plt.savefig(
            f"{output_dir}/validation_analysis.png", dpi=300, bbox_inches="tight"
        )
        plt.close()

        logger.info(f"Validation visualizations saved to {output_dir}")

    def generate_validation_report(self) -> dict:
        """Generate comprehensive validation report."""
        logger.info("Generating validation report...")

        # Run all validations if not already done
        if not self.validation_results:
            self.validate_demand_score_distribution()
            self.validate_component_correlations()
            self.validate_geographic_consistency()
            self.validate_against_known_trends()
            self.perform_sensitivity_analysis()

        # Run calibration
        calibration_result = self.calibrate_model_parameters()

        # Compile comprehensive report
        report = {
            "validation_timestamp": datetime.now().isoformat(),
            "model_file": self.ensemble_model_path,
            "validation_results": self.validation_results,
            "calibration_results": calibration_result,
            "overall_validation_status": self._calculate_overall_status(),
            "recommendations": self._generate_recommendations(),
        }

        # Save report
        report_path = "data/processed/model_validation_report.json"
        import json

        # Convert tuple keys to strings for JSON serialization
        def convert_tuples(obj):
            if isinstance(obj, dict):
                return {
                    str(k) if isinstance(k, tuple) else k: convert_tuples(v)
                    for k, v in obj.items()
                }
            elif isinstance(obj, list):
                return [convert_tuples(item) for item in obj]
            else:
                return obj

        report_serializable = convert_tuples(report)

        with open(report_path, "w") as f:
            json.dump(report_serializable, f, indent=2, default=str)

        logger.info(f"Validation report saved to {report_path}")
        return report

    def _calculate_overall_status(self) -> str:
        """Calculate overall validation status."""
        if not self.validation_results:
            return "NOT_VALIDATED"

        # Count passing validations
        passing_validations = 0
        total_validations = 0

        for validation_name, result in self.validation_results.items():
            if "overall_valid" in result:
                total_validations += 1
                if result["overall_valid"]:
                    passing_validations += 1
            elif "overall_stable" in result:
                total_validations += 1
                if result["overall_stable"]:
                    passing_validations += 1

        if total_validations == 0:
            return "UNKNOWN"

        pass_rate = passing_validations / total_validations

        if pass_rate >= 0.8:
            return "EXCELLENT"
        elif pass_rate >= 0.6:
            return "GOOD"
        elif pass_rate >= 0.4:
            return "FAIR"
        else:
            return "POOR"

    def _generate_recommendations(self) -> list[str]:
        """Generate actionable recommendations based on validation results."""
        recommendations = []

        if not self.validation_results:
            return ["Run validation before generating recommendations"]

        # Check each validation result
        for validation_name, result in self.validation_results.items():
            if not result.get("overall_valid", True):
                if validation_name == "demand_distribution":
                    recommendations.append(
                        "Adjust demand score normalization to achieve more realistic distribution"
                    )
                elif validation_name == "component_correlations":
                    recommendations.append(
                        "Reduce component weights to minimize multicollinearity"
                    )
                elif validation_name == "geographic_consistency":
                    recommendations.append(
                        "Improve geographic alignment or add regional smoothing"
                    )
                elif validation_name == "known_trends":
                    recommendations.append(
                        "Calibrate model against known California health trends"
                    )

        # Add calibration recommendations
        if self.calibration_results.get("calibration_needed", False):
            for rec in self.calibration_results["recommendations"]:
                recommendations.append(f"{rec['issue']}: {rec['recommendation']}")

        if not recommendations:
            recommendations.append(
                "Model validation passed - no immediate action required"
            )

        return recommendations


def main():
    """Run comprehensive model validation and calibration."""
    # Initialize validator
    validator = EnsembleModelValidator()

    # Load ensemble data
    validator.load_ensemble_data()

    # Run all validations
    print("Running comprehensive model validation...")
    validator.validate_demand_score_distribution()
    validator.validate_component_correlations()
    validator.validate_geographic_consistency()
    validator.validate_against_known_trends()
    validator.perform_sensitivity_analysis()

    # Run calibration
    print("Running model calibration...")
    calibration_result = validator.calibrate_model_parameters()

    # Create visualizations
    print("Creating validation visualizations...")
    validator.create_validation_visualizations()

    # Generate report
    print("Generating validation report...")
    report = validator.generate_validation_report()

    # Print summary
    print(f"\n=== MODEL VALIDATION SUMMARY ===")
    print(f"Overall Status: {report['overall_validation_status']}")
    print(
        f"Validation Results: {len(validator.validation_results)} validations completed"
    )
    print(f"Calibration Needed: {calibration_result['calibration_needed']}")

    if calibration_result["optimal_weights"]:
        print(f"Optimal Weights: {calibration_result['optimal_weights']}")

    print(f"\nRecommendations:")
    for rec in report["recommendations"]:
        print(f"  - {rec}")

    print(f"\nValidation report saved to: data/processed/model_validation_report.json")
    print(f"Visualizations saved to: data/processed/validation_plots/")


if __name__ == "__main__":
    main()
