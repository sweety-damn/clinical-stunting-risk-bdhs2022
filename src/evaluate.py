"""Calibration utilities for the BDHS-2022 stunting risk model.

All public functions accept 1-D arrays of predicted probabilities.
Hard labels are never accepted for AUROC or ECE.
"""
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve
from sklearn.metrics import brier_score_loss


def brier(y_true, y_prob):
    return brier_score_loss(np.asarray(y_true), np.asarray(y_prob))


def expected_calibration_error(y_true, y_prob, n_bins=10, strategy="quantile"):
    """Weighted mean |predicted - observed| across bins.

    strategy='quantile' is default because predicted probabilities from
    imbalanced classifiers are skewed; equal-width bins would place most
    predictions in the first bin and hide miscalibration.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_prob = np.asarray(y_prob, dtype=float)
    if strategy == "quantile":
        edges = np.quantile(y_prob, np.linspace(0, 1, n_bins + 1))
        edges[0], edges[-1] = -np.inf, np.inf
    else:
        edges = np.linspace(0, 1, n_bins + 1)
    bin_idx = np.digitize(y_prob, edges[1:-1])
    n = len(y_prob)
    ece = 0.0
    for b in range(n_bins):
        mask = bin_idx == b
        if not mask.any():
            continue
        ece += (mask.sum() / n) * abs(y_true[mask].mean() - y_prob[mask].mean())
    return float(ece)


def plot_reliability(y_true, y_prob, ax=None, label=None, n_bins=10, color=None):
    if ax is None:
        _, ax = plt.subplots(figsize=(4, 4))
    frac_pos, mean_pred = calibration_curve(
        np.asarray(y_true), np.asarray(y_prob), n_bins=n_bins, strategy="quantile"
    )
    ax.plot([0, 1], [0, 1], linestyle="--", color="grey", linewidth=1, label="Perfect calibration")
    ax.plot(mean_pred, frac_pos, marker="o", linewidth=1.5, label=label, color=color)
    ax.set_xlabel("Mean predicted probability")
    ax.set_ylabel("Observed prevalence")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    if label:
        ax.legend(fontsize=8, loc="upper left")
    return ax


def bootstrap_brier_ci(y_true, y_prob, n_boot=1000, alpha=0.05, seed=42):
    rng = np.random.default_rng(seed)
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    n = len(y_true)
    scores = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        scores[i] = brier_score_loss(y_true[idx], y_prob[idx])
    lo, hi = np.quantile(scores, [alpha / 2, 1 - alpha / 2])
    return float(scores.mean()), float(lo), float(hi)
