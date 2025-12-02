"""
日本の物価指標分析・可視化スクリプト

各物価指標の推移を可視化し、系列間の違いを分析します。
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import numpy as np
import os
from pathlib import Path

# 日本語フォント設定
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

class PriceIndexAnalyzer:
    def __init__(self, data_path):
        """
        物価指標分析クラス

        Parameters:
        -----------
        data_path : str
            データファイルのパス
        """
        self.data = pd.read_csv(data_path)
        self.data['date'] = pd.to_datetime(self.data['date'])
        self.data = self.data.set_index('date')

        # 出力ディレクトリ
        self.output_dir = Path(__file__).parent.parent / 'output'
        self.output_dir.mkdir(exist_ok=True)

    def calculate_yoy_changes(self):
        """前年比変化率を計算"""
        yoy_changes = pd.DataFrame(index=self.data.index)

        for col in self.data.columns:
            yoy_changes[f'{col}_YoY'] = self.data[col].pct_change(12) * 100

        return yoy_changes

    def plot_all_indices_level(self):
        """全物価指標の水準を一つのグラフにプロット"""
        fig, ax = plt.subplots(figsize=(14, 8))

        # カラーパレット
        colors = sns.color_palette('husl', len(self.data.columns))

        for i, col in enumerate(self.data.columns):
            ax.plot(self.data.index, self.data[col],
                   label=col, linewidth=2, color=colors[i])

        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Index (2020=100)', fontsize=12)
        ax.set_title('Japan Price Indices Comparison (1990-2024)', fontsize=14, fontweight='bold')
        ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=100, color='red', linestyle='--', alpha=0.5, label='Base Year 2020')

        plt.tight_layout()
        plt.savefig(self.output_dir / 'all_indices_level.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Saved: {self.output_dir / 'all_indices_level.png'}")

    def plot_cpi_comparison(self):
        """CPI系列の比較"""
        fig, ax = plt.subplots(figsize=(14, 8))

        cpi_cols = [col for col in self.data.columns if 'CPI' in col]

        for col in cpi_cols:
            ax.plot(self.data.index, self.data[col],
                   label=col, linewidth=2)

        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Index (2020=100)', fontsize=12)
        ax.set_title('CPI Series Comparison', fontsize=14, fontweight='bold')
        ax.legend(loc='upper left', fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=100, color='red', linestyle='--', alpha=0.5)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'cpi_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Saved: {self.output_dir / 'cpi_comparison.png'}")

    def plot_cgpi_comparison(self):
        """企業物価指数の比較（国内、輸出、輸入）"""
        fig, ax = plt.subplots(figsize=(14, 8))

        cgpi_cols = [col for col in self.data.columns if 'CGPI' in col]

        for col in cgpi_cols:
            ax.plot(self.data.index, self.data[col],
                   label=col, linewidth=2)

        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Index (2020=100)', fontsize=12)
        ax.set_title('Corporate Goods Price Index Comparison', fontsize=14, fontweight='bold')
        ax.legend(loc='upper left', fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=100, color='red', linestyle='--', alpha=0.5)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'cgpi_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Saved: {self.output_dir / 'cgpi_comparison.png'}")

    def plot_yoy_changes(self):
        """前年比変化率のプロット"""
        yoy_changes = self.calculate_yoy_changes()

        fig, ax = plt.subplots(figsize=(14, 8))

        colors = sns.color_palette('husl', len(self.data.columns))

        for i, col in enumerate(self.data.columns):
            ax.plot(yoy_changes.index, yoy_changes[f'{col}_YoY'],
                   label=col, linewidth=1.5, alpha=0.8, color=colors[i])

        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Year-on-Year Change (%)', fontsize=12)
        ax.set_title('Price Indices: Year-on-Year Changes', fontsize=14, fontweight='bold')
        ax.legend(loc='upper left', fontsize=9, framealpha=0.9)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.7)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'yoy_changes.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Saved: {self.output_dir / 'yoy_changes.png'}")

    def plot_key_comparisons(self):
        """主要指標の比較（CPI総合、GDPデフレータ、CGPI国内）"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))

        # 水準の比較
        key_indices = ['CPI_総合', 'GDP_デフレータ', 'CGPI_国内', 'CSPI']
        for col in key_indices:
            if col in self.data.columns:
                ax1.plot(self.data.index, self.data[col],
                        label=col, linewidth=2.5)

        ax1.set_ylabel('Index (2020=100)', fontsize=12)
        ax1.set_title('Key Price Indices Comparison (Level)', fontsize=14, fontweight='bold')
        ax1.legend(loc='upper left', fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=100, color='red', linestyle='--', alpha=0.5)

        # 前年比変化率の比較
        yoy_changes = self.calculate_yoy_changes()
        for col in key_indices:
            if col in self.data.columns:
                ax2.plot(yoy_changes.index, yoy_changes[f'{col}_YoY'],
                        label=col, linewidth=2.5)

        ax2.set_xlabel('Year', fontsize=12)
        ax2.set_ylabel('Year-on-Year Change (%)', fontsize=12)
        ax2.set_title('Key Price Indices Comparison (YoY Change)', fontsize=14, fontweight='bold')
        ax2.legend(loc='upper left', fontsize=11)
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.7)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'key_indices_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Saved: {self.output_dir / 'key_indices_comparison.png'}")

    def plot_correlation_heatmap(self):
        """物価指標間の相関ヒートマップ"""
        # 前年比変化率の相関を計算
        yoy_changes = self.calculate_yoy_changes()
        correlation = yoy_changes.corr()

        # 列名を短縮
        short_names = {col: col.replace('_YoY', '') for col in correlation.columns}
        correlation = correlation.rename(columns=short_names, index=short_names)

        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(correlation, annot=True, fmt='.2f', cmap='coolwarm',
                   center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                   ax=ax, vmin=-1, vmax=1)

        ax.set_title('Correlation Matrix of Price Indices (YoY Changes)',
                    fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Saved: {self.output_dir / 'correlation_heatmap.png'}")

        return correlation

    def analyze_volatility(self):
        """各指標のボラティリティ分析"""
        yoy_changes = self.calculate_yoy_changes()

        volatility = pd.DataFrame({
            'Indicator': [col.replace('_YoY', '') for col in yoy_changes.columns],
            'Std Dev': yoy_changes.std().values,
            'Mean': yoy_changes.mean().values,
            'Max': yoy_changes.max().values,
            'Min': yoy_changes.min().values
        })

        volatility = volatility.sort_values('Std Dev', ascending=False)

        print("\n=== Volatility Analysis (Standard Deviation of YoY Changes) ===")
        print(volatility.to_string(index=False))
        print()

        # ボラティリティの可視化
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(volatility['Indicator'], volatility['Std Dev'],
                      color=sns.color_palette('viridis', len(volatility)))

        ax.set_xlabel('Standard Deviation (%)', fontsize=12)
        ax.set_title('Price Index Volatility Comparison', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        plt.savefig(self.output_dir / 'volatility_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Saved: {self.output_dir / 'volatility_comparison.png'}")

        return volatility

    def generate_summary_statistics(self):
        """各指標の要約統計量を生成"""
        yoy_changes = self.calculate_yoy_changes()

        summary = pd.DataFrame()

        for col in self.data.columns:
            stats = {
                'Indicator': col,
                'Latest Level (2024)': self.data[col].iloc[-1],
                'Avg YoY Change': yoy_changes[f'{col}_YoY'].mean(),
                'Std Dev YoY': yoy_changes[f'{col}_YoY'].std(),
                'Max YoY': yoy_changes[f'{col}_YoY'].max(),
                'Min YoY': yoy_changes[f'{col}_YoY'].min(),
                'Current YoY (Latest)': yoy_changes[f'{col}_YoY'].iloc[-1]
            }
            summary = pd.concat([summary, pd.DataFrame([stats])], ignore_index=True)

        print("\n=== Summary Statistics ===")
        print(summary.to_string(index=False))
        print()

        # CSV保存
        summary.to_csv(self.output_dir / 'summary_statistics.csv', index=False)
        print(f"Saved: {self.output_dir / 'summary_statistics.csv'}")

        return summary

    def run_full_analysis(self):
        """全分析を実行"""
        print("Starting comprehensive analysis...")
        print("="*60)

        # 可視化
        self.plot_all_indices_level()
        self.plot_cpi_comparison()
        self.plot_cgpi_comparison()
        self.plot_yoy_changes()
        self.plot_key_comparisons()

        # 相関分析
        correlation = self.plot_correlation_heatmap()

        # ボラティリティ分析
        volatility = self.analyze_volatility()

        # 要約統計
        summary = self.generate_summary_statistics()

        print("="*60)
        print("Analysis complete! All results saved to:", self.output_dir)

        return {
            'correlation': correlation,
            'volatility': volatility,
            'summary': summary
        }

if __name__ == '__main__':
    # データ読み込みと分析実行
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'japan_price_indices.csv')

    analyzer = PriceIndexAnalyzer(data_path)
    results = analyzer.run_full_analysis()
