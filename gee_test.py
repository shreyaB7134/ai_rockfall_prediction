"""
Earth Engine API Test Script
=============================

This script tests the Google Earth Engine API initialization and authentication.
Run this after completing the earthengine authenticate step.

Usage:
    1. First run: earthengine authenticate
    2. Then run: python gee_test.py
"""

import ee

print("Initializing Earth Engine...")
ee.Initialize(project='rockfall-project-492810')
print("Earth Engine initialized successfully!")
