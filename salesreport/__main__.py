"""Allows:  python -m salesreport [orders.csv]"""
import sys

from .cli import main

sys.exit(main())
