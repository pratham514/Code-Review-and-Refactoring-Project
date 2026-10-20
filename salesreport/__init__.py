"""salesreport - read an orders CSV and produce sales reports.

Layers (each depends only on the ones above it):
    models      data classes shared by all layers
    pricing     discount rules and order pricing
    loader      CSV reading and row validation
    reports     calculations (pure functions, no printing)
    formatting  turns report results into text
    cli         command-line entry point
"""

__version__ = "2.0.0"
