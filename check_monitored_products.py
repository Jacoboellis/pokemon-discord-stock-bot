#!/usr/bin/env python3
"""
Simple script to check monitored products - replacement for check_products.py
"""
from utils.product_checker import ProductChecker

if __name__ == "__main__":
    checker = ProductChecker()
    checker.print_monitored_products()
    checker.print_summary()