"""
Utility Functions for Metrics Calculation and Visualization

Provides common functions for performance metrics, statistical analysis,
and scientific visualization for the carbon route optimization project.

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any, Optional
from scipy import stats
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set publication-quality plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class PerformanceMetrics:
    """
    Collection of performance metrics for route optimization evaluation.
    
    Implements standard metrics for both predictive and prescriptive performance
    according to supply chain optimization literature.
    """
    
    @staticmethod
    def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calculate Mean Absolute Percentage Error.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            float: MAPE in percentage
        """
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        
    @staticmethod
    def calculate_relative_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calculate relative error (Harvard study benchmark).
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            float: Relative error in percentage
        """
        return np.mean(np.abs(y_true - y_pred) / np.abs(y_true)) * 100
        
    @staticmethod
    def calculate_improvement_metrics(baseline_values: np.ndarray, 
                                    optimized_values: np.ndarray) -> Dict[str, float]:
        """
        Calculate improvement metrics for optimization results.
        
        Args:
            baseline_values: Original values before optimization
            optimized_values: Values after optimization
            
        Returns:
            Dict[str, float]: Improvement metrics
        """
        mean_baseline = np.mean(baseline_values)
        mean_optimized = np.mean(optimized_values)
        
        absolute_improvement = mean_baseline - mean_optimized
        relative_improvement = (absolute_improvement / mean_baseline) * 100
        
        # Statistical significance test
        t_stat, p_value = stats.ttest_rel(baseline_values, optimized_values)
        
        return {
            'absolute_improvement': absolute_improvement,
            'relative_improvement_percent': relative_improvement,
            'baseline_mean': mean_baseline,
            'optimized_mean': mean_optimized,
            'baseline_std': np.std(baseline_values),
            'optimized_std': np.std(optimized_values),
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < 0.05
        }
        
    @staticmethod
    def calculate_pareto_metrics(costs: np.ndarray, emissions: np.ndarray) -> Dict[str, float]:
        """
        Calculate metrics for Pareto frontier analysis.
        
        Args:
            costs: Array of cost values
            emissions: Array of emission values
            
        Returns:
            Dict[str, float]: Pareto frontier metrics
        """
        # Hypervolume (simplified version)
        # Reference point is maximum cost and emission
        ref_cost = np.max(costs) * 1.1
        ref_emission = np.max(emissions) * 1.1
        
        # Sort points by cost
        sorted_indices = np.argsort(costs)
        sorted_costs = costs[sorted_indices]
        sorted_emissions = emissions[sorted_indices]
        
        # Calculate hypervolume
        hypervolume = 0
        for i in range(len(sorted_costs)):
            if i == 0:
                width = ref_cost - sorted_costs[i]
            else:
                width = sorted_costs[i-1] - sorted_costs[i]
            height = ref_emission - sorted_emissions[i]
            hypervolume += width * height
            
        # Spread metric (diversity of solutions)
        cost_spread = np.std(costs)
        emission_spread = np.std(emissions)
        
        return {
            'hypervolume': hypervolume,
            'cost_spread': cost_spread,
            'emission_spread': emission_spread,
            'n_solutions': len(costs),
            'cost_range': np.max(costs) - np.min(costs),
            'emission_range': np.max(emissions) - np.min(emissions)
        }


class ScientificVisualizer:
    """
    Scientific visualization tools for academic publication.
    
    Creates publication-quality figures with appropriate styling,
    statistics, and annotations for journal submission.
    """
    
    def __init__(self, figsize: Tuple[int, int] = (10, 6), dpi: int = 300):
        """
        Initialize scientific visualizer.
        
        Args:
            figsize: Default figure size
            dpi: Resolution for saved figures
        """
        self.figsize = figsize
        self.dpi = dpi
        
        # Set publication style
        plt.rcParams.update({
            'font.size': 12,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
            'figure.titlesize': 16
        })
        
    def plot_model_performance_comparison(self, results: Dict[str, Dict], 
                                        save_path: Optional[str] = None) -> None:
        """
        Create comprehensive ML model performance comparison.
        
        Args:
            results: Model performance results
            save_path: Path to save the figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Machine Learning Models Performance Comparison', 
                    fontsize=16, y=0.98)
        
        models = list(results.keys())
        model_labels = [model.replace('_', ' ').title() for model in models]
        
        # MAPE comparison
        mape_values = [results[model]['mape'] for model in models]
        bars1 = axes[0, 0].bar(model_labels, mape_values, 
                              color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'], alpha=0.8)
        axes[0, 0].axhline(y=12, color='red', linestyle='--', alpha=0.7, 
                          label='Target < 12%')
        axes[0, 0].set_title('Mean Absolute Percentage Error (MAPE)')
        axes[0, 0].set_ylabel('MAPE (%)')
        axes[0, 0].legend()
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars1, mape_values):
            height = bar.get_height()
            axes[0, 0].text(bar.get_x() + bar.get_width()/2., height + 0.1,
                           f'{value:.2f}%', ha='center', va='bottom')
        
        # R² comparison
        r2_values = [results[model]['r2'] for model in models]
        bars2 = axes[0, 1].bar(model_labels, r2_values, 
                              color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'], alpha=0.8)
        axes[0, 1].axhline(y=0.85, color='red', linestyle='--', alpha=0.7, 
                          label='Target > 0.85')
        axes[0, 1].set_title('Coefficient of Determination (R²)')
        axes[0, 1].set_ylabel('R²')
        axes[0, 1].set_ylim(0, 1)
        axes[0, 1].legend()
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar, value in zip(bars2, r2_values):
            height = bar.get_height()
            axes[0, 1].text(bar.get_x() + bar.get_width()/2., height + 0.01,
                           f'{value:.3f}', ha='center', va='bottom')
        
        # RMSE comparison
        rmse_values = [results[model]['rmse'] for model in models]
        bars3 = axes[1, 0].bar(model_labels, rmse_values, 
                              color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'], alpha=0.8)
        axes[1, 0].set_title('Root Mean Square Error (RMSE)')
        axes[1, 0].set_ylabel('RMSE (kg CO₂e)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Relative Error comparison
        rel_error_values = [results[model]['relative_error'] for model in models]
        bars4 = axes[1, 1].bar(model_labels, rel_error_values, 
                              color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'], alpha=0.8)
        axes[1, 1].axhline(y=12, color='red', linestyle='--', alpha=0.7, 
                          label='Target < 12%')
        axes[1, 1].set_title('Relative Error')
        axes[1, 1].set_ylabel('Relative Error (%)')
        axes[1, 1].legend()
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"Model performance comparison saved to {save_path}")
            
        plt.show()
        
    def plot_pareto_frontier(self, costs: np.ndarray, emissions: np.ndarray,
                           baseline_cost: float = None, baseline_emission: float = None,
                           save_path: Optional[str] = None) -> None:
        """
        Create publication-quality Pareto frontier plot.
        
        Args:
            costs: Array of cost values
            emissions: Array of emission values
            baseline_cost: Baseline cost for comparison
            baseline_emission: Baseline emission for comparison
            save_path: Path to save the figure
        """
        plt.figure(figsize=self.figsize)
        
        # Plot Pareto front
        plt.scatter(costs, emissions, alpha=0.7, s=60, c='#2ca02c', 
                   label='Pareto Optimal Solutions', edgecolors='black', linewidth=0.5)
        
        # Add baseline point if provided
        if baseline_cost is not None and baseline_emission is not None:
            plt.scatter([baseline_cost], [baseline_emission], s=150, c='#d62728', 
                       marker='*', label='Baseline Solution', edgecolors='black', linewidth=1)
        
        # Add trend line
        if len(costs) > 1:
            sorted_indices = np.argsort(costs)
            plt.plot(costs[sorted_indices], emissions[sorted_indices], 
                    '--', alpha=0.5, color='gray', linewidth=1)
        
        plt.xlabel('Total Cost (€)')
        plt.ylabel('Total Emissions (kg CO₂e)')
        plt.title('Pareto Frontier: Cost vs Emissions Trade-off')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Add improvement annotations
        if baseline_cost is not None and baseline_emission is not None:
            min_cost_idx = np.argmin(costs)
            min_emission_idx = np.argmin(emissions)
            
            cost_improvement = (baseline_cost - costs[min_cost_idx]) / baseline_cost * 100
            emission_improvement = (baseline_emission - emissions[min_emission_idx]) / baseline_emission * 100
            
            plt.text(0.02, 0.98, f'Max Cost Reduction: {cost_improvement:.1f}%\n'
                                 f'Max Emission Reduction: {emission_improvement:.1f}%',
                    transform=plt.gca().transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"Pareto frontier plot saved to {save_path}")
            
        plt.show()
        
    def plot_scalability_analysis(self, dataset_sizes: List[int], 
                                metrics: Dict[str, List[float]], 
                                save_path: Optional[str] = None) -> None:
        """
        Plot scalability analysis across different dataset sizes.
        
        Args:
            dataset_sizes: List of dataset sizes (e.g., [50, 200, 500])
            metrics: Dictionary with metric names and values for each size
            save_path: Path to save the figure
        """
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Performance metrics vs dataset size
        for metric_name, values in metrics.items():
            if 'time' not in metric_name.lower():
                axes[0].plot(dataset_sizes, values, marker='o', linewidth=2, 
                           markersize=8, label=metric_name)
        
        axes[0].set_xlabel('Dataset Size (Number of Routes)')
        axes[0].set_ylabel('Performance Metric Value')
        axes[0].set_title('Performance vs Dataset Size')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        axes[0].set_xscale('log')
        
        # Computational time analysis
        if any('time' in metric.lower() for metric in metrics.keys()):
            time_metrics = {k: v for k, v in metrics.items() if 'time' in k.lower()}
            
            for metric_name, values in time_metrics.items():
                axes[1].plot(dataset_sizes, values, marker='s', linewidth=2, 
                           markersize=8, label=metric_name)
            
            axes[1].set_xlabel('Dataset Size (Number of Routes)')
            axes[1].set_ylabel('Computation Time (seconds)')
            axes[1].set_title('Computational Scalability')
            axes[1].legend()
            axes[1].grid(True, alpha=0.3)
            axes[1].set_xscale('log')
            axes[1].set_yscale('log')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"Scalability analysis plot saved to {save_path}")
            
        plt.show()
        
    def create_summary_table(self, results: Dict[str, Dict], 
                           save_path: Optional[str] = None) -> pd.DataFrame:
        """
        Create formatted summary table for academic publication.
        
        Args:
            results: Results dictionary
            save_path: Path to save table as CSV
            
        Returns:
            pd.DataFrame: Formatted results table
        """
        # Create DataFrame from results
        df = pd.DataFrame(results).T
        
        # Round numerical values appropriately
        numerical_columns = df.select_dtypes(include=[np.number]).columns
        for col in numerical_columns:
            if 'mape' in col.lower() or 'error' in col.lower():
                df[col] = df[col].round(2)
            elif 'r2' in col.lower():
                df[col] = df[col].round(3)
            else:
                df[col] = df[col].round(2)
        
        # Add ranking
        if 'r2' in df.columns:
            df = df.sort_values('r2', ascending=False)
            df['Rank'] = range(1, len(df) + 1)
        
        # Add performance indicators
        if 'mape' in df.columns:
            df['MAPE_Target_Met'] = df['mape'] <= 12.0
        if 'r2' in df.columns:
            df['R2_Target_Met'] = df['r2'] >= 0.85
        
        if save_path:
            df.to_csv(save_path)
            logger.info(f"Summary table saved to {save_path}")
            
        return df


class StatisticalAnalysis:
    """
    Statistical analysis tools for scientific validation.
    
    Provides statistical tests and analysis methods for validating
    optimization results and model performance.
    """
    
    @staticmethod
    def perform_anova(groups: Dict[str, np.ndarray]) -> Dict[str, float]:
        """
        Perform ANOVA test across multiple groups.
        
        Args:
            groups: Dictionary with group names and values
            
        Returns:
            Dict[str, float]: ANOVA results
        """
        group_values = list(groups.values())
        f_stat, p_value = stats.f_oneway(*group_values)
        
        return {
            'f_statistic': f_stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'n_groups': len(groups),
            'total_samples': sum(len(group) for group in group_values)
        }
        
    @staticmethod
    def paired_t_test(before: np.ndarray, after: np.ndarray) -> Dict[str, float]:
        """
        Perform paired t-test for before/after comparison.
        
        Args:
            before: Values before optimization
            after: Values after optimization
            
        Returns:
            Dict[str, float]: T-test results
        """
        t_stat, p_value = stats.ttest_rel(before, after)
        
        effect_size = (np.mean(before) - np.mean(after)) / np.std(before - after)
        
        return {
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'effect_size': effect_size,
            'mean_difference': np.mean(before) - np.mean(after),
            'confidence_interval_95': stats.t.interval(0.95, len(before)-1, 
                                                      loc=np.mean(before-after),
                                                      scale=stats.sem(before-after))
        }
        
    @staticmethod
    def calculate_confidence_intervals(data: np.ndarray, confidence: float = 0.95) -> Tuple[float, float]:
        """
        Calculate confidence intervals for data.
        
        Args:
            data: Data array
            confidence: Confidence level (default 0.95)
            
        Returns:
            Tuple[float, float]: Lower and upper confidence bounds
        """
        alpha = 1 - confidence
        return stats.t.interval(confidence, len(data)-1, loc=np.mean(data), scale=stats.sem(data))


def main():
    """
    Main function to demonstrate utility functions.
    """
    logger.info("Utility functions module initialized")
    
    # Example usage would be demonstrated here
    # when integrated with actual data and results


if __name__ == "__main__":
    main()
