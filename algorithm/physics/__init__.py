"""
Physics-Informed Emission Models
=================================
Module for physics-based carbon emission calculations with improved
accuracy over simple multiplicative factor models.
"""

from .emission_model import EmissionModelV2, RouteEmissionInput, EmissionResult

__all__ = ["EmissionModelV2", "RouteEmissionInput", "EmissionResult"]
