"""
Unmet-Demand-Index (UDI) calculation module.

This module computes the baseline Unmet-Demand-Index to identify ZIP codes
where patients travel >30 minutes for cardiology care.
"""

from .udi_calculator import UDICalculator

__all__ = ['UDICalculator'] 
