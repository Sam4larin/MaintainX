from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import confusion_matrix


def save_confusion_matrix(y_true, y_pred, output_dir: Path):
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(4, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
    ax.set_title('Confusion Matrix')
    fig.tight_layout()
    fig.savefig(output_dir / 'confusion_matrix.png')
    plt.close(fig)


def save_regression_plot(y_true, y_pred, output_dir: Path):
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.scatter(y_true, y_pred, alpha=0.7)
    ax.plot([min(y_true), max(y_true)], [min(y_true), max(y_true)], 'r--')
    ax.set_title('Predicted vs Actual')
    fig.tight_layout()
    fig.savefig(output_dir / 'regression_scatter.png')
    plt.close(fig)


def save_anomaly_plot(scores, labels, output_dir: Path):
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.hist(scores[labels == 0], alpha=0.5, label='Normal')
    ax.hist(scores[labels == 1], alpha=0.5, label='Failure')
    ax.set_title('Anomaly Score Distribution')
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / 'anomaly_distribution.png')
    plt.close(fig)
