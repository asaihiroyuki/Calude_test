"""
中央銀行の当座預金付利金利データの収集と分析スクリプト

世界の主要中央銀行が市中銀行の中央銀行当座預金に付利している金利の推移を収集します。
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 日本語フォント設定
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Noto Sans CJK JP', 'IPAexGothic']
plt.rcParams['axes.unicode_minus'] = False

def fetch_fred_data(series_id, start_date='2000-01-01'):
    """
    FRED APIからデータを取得（pandas_datareaderを使用）

    Parameters:
    -----------
    series_id : str
        FREDのシリーズID
    start_date : str
        データ取得開始日

    Returns:
    --------
    pd.Series
        取得したデータ
    """
    try:
        from pandas_datareader import data as web
        df = web.DataReader(series_id, 'fred', start_date)
        return df[series_id]
    except Exception as e:
        print(f"Error fetching {series_id}: {e}")
        return None

def create_manual_data():
    """
    手動で中央銀行の金利データを作成（FRED APIが使えない場合のフォールバック）
    """
    # 2015年から現在までの主要な金利変更ポイントのサンプルデータ
    dates = pd.date_range(start='2015-01-01', end='2024-12-01', freq='ME')

    data = {
        'US_FRB': [],
        'ECB': [],
        'Japan_BOJ': [],
        'UK_BOE': [],
        'Canada_BoC': [],
        'Australia_RBA': [],
        'Switzerland_SNB': []
    }

    # 米国FRB - 2015年末から段階的利上げ、2020年ゼロ金利、2022年から急速利上げ
    for date in dates:
        if date < pd.Timestamp('2015-12-01'):
            data['US_FRB'].append(0.25)
        elif date < pd.Timestamp('2016-12-01'):
            data['US_FRB'].append(0.50)
        elif date < pd.Timestamp('2017-12-01'):
            data['US_FRB'].append(1.00)
        elif date < pd.Timestamp('2018-12-01'):
            data['US_FRB'].append(2.00)
        elif date < pd.Timestamp('2019-12-01'):
            data['US_FRB'].append(2.40)
        elif date < pd.Timestamp('2020-03-01'):
            data['US_FRB'].append(1.55)
        elif date < pd.Timestamp('2022-03-01'):
            data['US_FRB'].append(0.10)
        elif date < pd.Timestamp('2022-12-01'):
            data['US_FRB'].append(3.00)
        elif date < pd.Timestamp('2023-07-01'):
            data['US_FRB'].append(5.00)
        else:
            data['US_FRB'].append(5.40)

    # ECB - 長期マイナス金利、2022年から利上げ
    for date in dates:
        if date < pd.Timestamp('2019-09-01'):
            data['ECB'].append(-0.40)
        elif date < pd.Timestamp('2022-07-01'):
            data['ECB'].append(-0.50)
        elif date < pd.Timestamp('2022-12-01'):
            data['ECB'].append(0.75)
        elif date < pd.Timestamp('2023-09-01'):
            data['ECB'].append(3.50)
        else:
            data['ECB'].append(4.00)

    # 日本BOJ - マイナス金利政策継続、2024年解除
    for date in dates:
        if date < pd.Timestamp('2016-02-01'):
            data['Japan_BOJ'].append(0.10)
        elif date < pd.Timestamp('2024-03-01'):
            data['Japan_BOJ'].append(-0.10)
        else:
            data['Japan_BOJ'].append(0.10)

    # 英国BOE
    for date in dates:
        if date < pd.Timestamp('2020-03-01'):
            data['UK_BOE'].append(0.75)
        elif date < pd.Timestamp('2021-12-01'):
            data['UK_BOE'].append(0.10)
        elif date < pd.Timestamp('2023-08-01'):
            data['UK_BOE'].append(4.50)
        else:
            data['UK_BOE'].append(5.25)

    # カナダ
    for date in dates:
        if date < pd.Timestamp('2020-03-01'):
            data['Canada_BoC'].append(1.75)
        elif date < pd.Timestamp('2022-03-01'):
            data['Canada_BoC'].append(0.25)
        elif date < pd.Timestamp('2023-07-01'):
            data['Canada_BoC'].append(4.50)
        else:
            data['Canada_BoC'].append(5.00)

    # オーストラリア
    for date in dates:
        if date < pd.Timestamp('2020-03-01'):
            data['Australia_RBA'].append(0.75)
        elif date < pd.Timestamp('2022-05-01'):
            data['Australia_RBA'].append(0.10)
        elif date < pd.Timestamp('2023-11-01'):
            data['Australia_RBA'].append(4.10)
        else:
            data['Australia_RBA'].append(4.35)

    # スイス
    for date in dates:
        if date < pd.Timestamp('2022-06-01'):
            data['Switzerland_SNB'].append(-0.75)
        elif date < pd.Timestamp('2023-06-01'):
            data['Switzerland_SNB'].append(1.00)
        else:
            data['Switzerland_SNB'].append(1.75)

    df = pd.DataFrame(data, index=dates)
    return df

def collect_central_bank_rates():
    """
    主要中央銀行の当座預金付利金利データを収集
    """
    print("中央銀行の付利金利データを収集中...")

    # FREDのシリーズID（主要な中央銀行の金利）
    series_ids = {
        'US_FRB': 'IORB',           # 米国: Interest on Reserve Balances
        'ECB': 'ECBDFR',            # 欧州: Deposit Facility Rate
        'Japan_BOJ': 'INTDSRJPM193N',  # 日本: Interest Rate on Excess Reserves
        'UK_BOE': 'IUDSOIA',        # 英国: Bank Rate
        'Canada_BoC': 'IONCBCR',    # カナダ: Deposit Rate
        'Australia_RBA': 'IRATCBA', # オーストラリア: Cash Rate Target
        'Switzerland_SNB': 'CHSNBPOL'  # スイス: Policy Rate
    }

    start_date = '2010-01-01'
    all_data = {}

    # データ取得を試みる
    success_count = 0
    for name, series_id in series_ids.items():
        print(f"  {name} ({series_id}) のデータを取得中...")
        data = fetch_fred_data(series_id, start_date)
        if data is not None and len(data) > 0:
            all_data[name] = data
            success_count += 1

    # データ取得に失敗した場合は手動データを使用
    if success_count < 3:
        print("\nFRED APIからの取得に失敗しました。サンプルデータを使用します。")
        df = create_manual_data()
    else:
        # 取得したデータをDataFrameに結合
        df = pd.DataFrame(all_data)

    # NaN値を前方補完
    df = df.ffill()

    return df

def analyze_rates(df):
    """
    金利データの統計分析
    """
    print("\n=== 中央銀行付利金利の統計サマリー ===\n")

    # 最新の金利
    print("【最新の金利水準（%）】")
    latest = df.iloc[-1]
    for bank, rate in latest.items():
        print(f"  {bank}: {rate:.2f}%")

    # 期間中の最高値・最低値
    print("\n【期間中の最高値・最低値（%）】")
    for col in df.columns:
        print(f"\n  {col}:")
        print(f"    最高値: {df[col].max():.2f}% ({df[col].idxmax().strftime('%Y-%m')})")
        print(f"    最低値: {df[col].min():.2f}% ({df[col].idxmin().strftime('%Y-%m')})")

    # 変動幅
    print("\n【変動幅（最高値 - 最低値）】")
    for col in df.columns:
        volatility = df[col].max() - df[col].min()
        print(f"  {col}: {volatility:.2f}%")

    return latest

def visualize_rates(df, output_dir='output'):
    """
    金利データの可視化
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    # 1. 全中央銀行の金利推移（時系列）
    plt.figure(figsize=(16, 10))

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']

    for i, col in enumerate(df.columns):
        plt.plot(df.index, df[col], label=col, linewidth=2, color=colors[i % len(colors)])

    plt.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    plt.title('Major Central Banks - Interest Rates on Reserve Deposits\n主要中央銀行の当座預金付利金利の推移',
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Year / 年', fontsize=12, fontweight='bold')
    plt.ylabel('Interest Rate (%) / 金利（%）', fontsize=12, fontweight='bold')
    plt.legend(loc='upper left', fontsize=10, framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/central_bank_rates_all.png', dpi=300, bbox_inches='tight')
    print(f"\n図表を保存しました: {output_dir}/central_bank_rates_all.png")

    # 2. 地域別比較（先進国 vs 欧州 vs アジア太平洋）
    plt.figure(figsize=(16, 10))

    # 先進国（米国、英国、カナダ）
    plt.subplot(3, 1, 1)
    for bank in ['US_FRB', 'UK_BOE', 'Canada_BoC']:
        if bank in df.columns:
            plt.plot(df.index, df[bank], label=bank, linewidth=2.5)
    plt.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    plt.title('Advanced Economies (US, UK, Canada) / 先進国（米国、英国、カナダ）',
              fontsize=12, fontweight='bold')
    plt.ylabel('Rate (%)', fontsize=10)
    plt.legend(loc='upper left', fontsize=9)
    plt.grid(True, alpha=0.3)

    # 欧州（ECB、スイス）
    plt.subplot(3, 1, 2)
    for bank in ['ECB', 'Switzerland_SNB']:
        if bank in df.columns:
            plt.plot(df.index, df[bank], label=bank, linewidth=2.5)
    plt.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    plt.title('Europe (ECB, Switzerland) / 欧州（ECB、スイス）',
              fontsize=12, fontweight='bold')
    plt.ylabel('Rate (%)', fontsize=10)
    plt.legend(loc='upper left', fontsize=9)
    plt.grid(True, alpha=0.3)

    # アジア太平洋（日本、オーストラリア）
    plt.subplot(3, 1, 3)
    for bank in ['Japan_BOJ', 'Australia_RBA']:
        if bank in df.columns:
            plt.plot(df.index, df[bank], label=bank, linewidth=2.5)
    plt.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    plt.title('Asia-Pacific (Japan, Australia) / アジア太平洋（日本、オーストラリア）',
              fontsize=12, fontweight='bold')
    plt.xlabel('Year / 年', fontsize=10)
    plt.ylabel('Rate (%)', fontsize=10)
    plt.legend(loc='upper left', fontsize=9)
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/central_bank_rates_by_region.png', dpi=300, bbox_inches='tight')
    print(f"図表を保存しました: {output_dir}/central_bank_rates_by_region.png")

    # 3. 最近5年間の詳細推移
    plt.figure(figsize=(16, 10))

    # 最近5年間のデータ
    five_years_ago = datetime.now() - timedelta(days=5*365)
    recent_df = df[df.index >= five_years_ago]

    for i, col in enumerate(recent_df.columns):
        plt.plot(recent_df.index, recent_df[col], label=col, linewidth=2.5,
                marker='o', markersize=3, color=colors[i % len(colors)])

    plt.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    plt.title('Recent 5 Years - Central Bank Rates\n直近5年間の中央銀行金利推移',
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Year / 年', fontsize=12, fontweight='bold')
    plt.ylabel('Interest Rate (%) / 金利（%）', fontsize=12, fontweight='bold')
    plt.legend(loc='upper left', fontsize=10, framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/central_bank_rates_recent5years.png', dpi=300, bbox_inches='tight')
    print(f"図表を保存しました: {output_dir}/central_bank_rates_recent5years.png")

    # 4. ヒートマップ（年次平均）
    plt.figure(figsize=(14, 8))

    # 年次平均を計算
    yearly_avg = df.resample('YE').mean()
    yearly_avg.index = yearly_avg.index.year

    # ヒートマップを作成
    sns.heatmap(yearly_avg.T, annot=True, fmt='.2f', cmap='RdYlGn_r',
                center=0, cbar_kws={'label': 'Interest Rate (%)'})
    plt.title('Annual Average Interest Rates - Heatmap\n年次平均金利ヒートマップ',
              fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('Year / 年', fontsize=11, fontweight='bold')
    plt.ylabel('Central Bank / 中央銀行', fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/central_bank_rates_heatmap.png', dpi=300, bbox_inches='tight')
    print(f"図表を保存しました: {output_dir}/central_bank_rates_heatmap.png")

    plt.close('all')

def save_data(df, output_dir='data'):
    """
    データをCSVファイルとして保存
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    filepath = f'{output_dir}/central_bank_rates.csv'
    df.to_csv(filepath)
    print(f"\nデータを保存しました: {filepath}")

def main():
    """
    メイン実行関数
    """
    print("=" * 80)
    print("世界の中央銀行 当座預金付利金利 分析プログラム")
    print("Central Bank Interest Rates on Reserve Deposits Analysis")
    print("=" * 80)

    # データ収集
    df = collect_central_bank_rates()

    # データ保存
    save_data(df)

    # 統計分析
    latest_rates = analyze_rates(df)

    # 可視化
    print("\n図表を作成中...")
    visualize_rates(df)

    print("\n" + "=" * 80)
    print("分析が完了しました！")
    print("=" * 80)

    return df

if __name__ == '__main__':
    df = main()
