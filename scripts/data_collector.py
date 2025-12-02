"""
日本の物価指標データ収集スクリプト

このスクリプトは、以下の物価指標のサンプルデータを生成します：
1. CPI（消費者物価指数）- 総合、コア、コアコア
2. GDPデフレータ
3. 企業物価指数（CGPI）- 国内、輸出、輸入
4. 企業向けサービス価格指数（CSPI）

実際のデータソース：
- CPI: e-Stat (https://www.e-stat.go.jp/) - 統計コード: 00200571
- GDPデフレータ: 内閣府 (https://www.esri.cao.go.jp/jp/sna/data/data.html)
- CGPI, CSPI: 日本銀行時系列統計 (https://www.stat-search.boj.or.jp/)

注意：このスクリプトはサンプルデータを生成します。
実際のデータを取得するには：
1. e-Stat APIキーを取得 (https://www.e-stat.go.jp/api/)
2. 日本銀行の時系列データサイトからCSVダウンロード
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class JapanPriceIndexCollector:
    def __init__(self, start_year=1990, end_year=2024):
        """
        日本の物価指標データコレクター

        Parameters:
        -----------
        start_year : int
            データ開始年
        end_year : int
            データ終了年
        """
        self.start_year = start_year
        self.end_year = end_year
        self.base_year = 2020  # 基準年

    def generate_sample_data(self):
        """
        実際の日本の物価動向に基づいたサンプルデータを生成

        主要な歴史的イベント：
        - 1990年代: バブル崩壊後のデフレ期
        - 1998-2012: 長期デフレ期
        - 2013-: アベノミクスによる物価上昇
        - 2020: COVID-19パンデミック
        - 2022-2024: エネルギー価格高騰、円安による輸入物価上昇
        """
        # 月次データの日付を生成
        dates = pd.date_range(
            start=f'{self.start_year}-01-01',
            end=f'{self.end_year}-12-01',
            freq='MS'
        )

        n_periods = len(dates)

        # 基本トレンドの生成
        # 1990年代後半からデフレ、2013年以降緩やかな上昇、2022年以降急上昇
        base_trend = self._create_base_trend(dates)

        # 各指標の生成
        data = pd.DataFrame({'date': dates})

        # 1. CPI - 消費者物価指数
        # 総合CPI: エネルギーと食品を含む
        data['CPI_総合'] = self._generate_cpi_general(base_trend, dates)

        # コアCPI: 生鮮食品を除く
        data['CPI_生鮮食品除く'] = self._generate_cpi_core(base_trend, dates)

        # コアコアCPI: 食料とエネルギーを除く
        data['CPI_食料エネルギー除く'] = self._generate_cpi_corecore(base_trend, dates)

        # 2. GDPデフレータ（四半期データを月次に補間）
        data['GDP_デフレータ'] = self._generate_gdp_deflator(base_trend, dates)

        # 3. 企業物価指数（CGPI）
        # 国内企業物価指数
        data['CGPI_国内'] = self._generate_cgpi_domestic(base_trend, dates)

        # 輸出物価指数
        data['CGPI_輸出'] = self._generate_cgpi_export(base_trend, dates)

        # 輸入物価指数
        data['CGPI_輸入'] = self._generate_cgpi_import(base_trend, dates)

        # 4. 企業向けサービス価格指数（CSPI）
        data['CSPI'] = self._generate_cspi(base_trend, dates)

        # 基準年を100として正規化
        base_year_idx = data[data['date'].dt.year == self.base_year].index[0]
        for col in data.columns:
            if col != 'date':
                data[col] = (data[col] / data.loc[base_year_idx, col]) * 100

        return data

    def _create_base_trend(self, dates):
        """基本トレンドを作成"""
        n = len(dates)
        trend = np.zeros(n)

        for i, date in enumerate(dates):
            year = date.year
            month = date.month

            # 期間ごとのトレンド
            if year < 1997:
                # バブル崩壊直後、緩やかな下落
                trend[i] = 100 - (year - 1990) * 0.3
            elif year < 2013:
                # デフレ期: 緩やかな下落
                trend[i] = 95 - (year - 1997) * 0.2
            elif year < 2020:
                # アベノミクス期: 緩やかな上昇
                trend[i] = 92 + (year - 2013) * 0.5
            elif year < 2022:
                # COVID-19期: 停滞
                trend[i] = 95 + (year - 2020) * 0.2
            else:
                # エネルギー価格高騰期: 急上昇
                months_since_2022 = (year - 2022) * 12 + month
                trend[i] = 96 + months_since_2022 * 0.3

        return trend

    def _generate_cpi_general(self, base_trend, dates):
        """CPI総合指数を生成（エネルギー価格の影響大）"""
        cpi = base_trend.copy()

        # エネルギー価格の変動を追加
        for i, date in enumerate(dates):
            year = date.year

            # 2008年: 原油価格高騰
            if 2007 <= year <= 2008:
                cpi[i] += 2.0
            # 2014-2015: 原油価格下落
            elif 2014 <= year <= 2015:
                cpi[i] -= 1.5
            # 2022-2024: エネルギー価格急騰
            elif year >= 2022:
                cpi[i] += (year - 2021) * 1.5

        # 月次変動を追加
        noise = np.random.normal(0, 0.1, len(cpi))
        cpi += noise

        return cpi

    def _generate_cpi_core(self, base_trend, dates):
        """コアCPI（生鮮食品除く）を生成"""
        cpi_core = base_trend.copy()

        # 生鮮食品の変動を除外するため、総合CPIより安定
        for i, date in enumerate(dates):
            year = date.year

            # エネルギー価格の影響（総合CPIより小さい）
            if 2007 <= year <= 2008:
                cpi_core[i] += 1.5
            elif 2014 <= year <= 2015:
                cpi_core[i] -= 1.0
            elif year >= 2022:
                cpi_core[i] += (year - 2021) * 1.2

        noise = np.random.normal(0, 0.08, len(cpi_core))
        cpi_core += noise

        return cpi_core

    def _generate_cpi_corecore(self, base_trend, dates):
        """コアコアCPI（食料・エネルギー除く）を生成"""
        cpi_corecore = base_trend.copy()

        # 最も安定した指標
        for i, date in enumerate(dates):
            year = date.year

            # 賃金上昇などの構造的要因のみ反映
            if year >= 2013:
                cpi_corecore[i] += (year - 2013) * 0.3

        noise = np.random.normal(0, 0.05, len(cpi_corecore))
        cpi_corecore += noise

        return cpi_corecore

    def _generate_gdp_deflator(self, base_trend, dates):
        """GDPデフレータを生成（国内生産品の価格）"""
        gdp_def = base_trend.copy()

        # 輸入価格の影響を受けにくい
        # 輸出価格の影響を受ける
        for i, date in enumerate(dates):
            year = date.year

            # 円安時は輸出価格上昇でプラス
            if year >= 2013:
                gdp_def[i] += (year - 2013) * 0.4

            # COVID-19の影響
            if year == 2020:
                gdp_def[i] -= 1.0

        noise = np.random.normal(0, 0.1, len(gdp_def))
        gdp_def += noise

        return gdp_def

    def _generate_cgpi_domestic(self, base_trend, dates):
        """国内企業物価指数を生成"""
        cgpi = base_trend.copy()

        # 原材料価格の影響を受けやすい
        for i, date in enumerate(dates):
            year = date.year

            if 2007 <= year <= 2008:
                cgpi[i] += 3.0
            elif 2014 <= year <= 2015:
                cgpi[i] -= 2.0
            elif year >= 2022:
                cgpi[i] += (year - 2021) * 2.5

        noise = np.random.normal(0, 0.15, len(cgpi))
        cgpi += noise

        return cgpi

    def _generate_cgpi_export(self, base_trend, dates):
        """輸出物価指数を生成（円建て）"""
        export = base_trend.copy()

        # 円安で上昇
        for i, date in enumerate(dates):
            year = date.year

            # 2013年以降の円安
            if year >= 2013:
                export[i] += (year - 2013) * 1.0

            # 2022年以降の急激な円安
            if year >= 2022:
                export[i] += (year - 2021) * 3.0

        noise = np.random.normal(0, 0.2, len(export))
        export += noise

        return export

    def _generate_cgpi_import(self, base_trend, dates):
        """輸入物価指数を生成（円建て）"""
        import_price = base_trend.copy()

        # 原油価格と為替の影響を強く受ける
        for i, date in enumerate(dates):
            year = date.year

            # 2008年: 原油価格高騰
            if 2007 <= year <= 2008:
                import_price[i] += 5.0
            # 2014-2015: 原油価格下落
            elif 2014 <= year <= 2015:
                import_price[i] -= 3.0
            # 2022-2024: エネルギー価格高騰と円安
            elif year >= 2022:
                import_price[i] += (year - 2021) * 5.0

        noise = np.random.normal(0, 0.3, len(import_price))
        import_price += noise

        return import_price

    def _generate_cspi(self, base_trend, dates):
        """企業向けサービス価格指数を生成"""
        cspi = base_trend.copy()

        # サービス価格は物価より硬直的
        for i, date in enumerate(dates):
            year = date.year

            # 賃金上昇の影響
            if year >= 2013:
                cspi[i] += (year - 2013) * 0.2

            # COVID-19の影響（サービス需要減少）
            if year == 2020:
                cspi[i] -= 2.0
            elif year == 2021:
                cspi[i] -= 1.0

        noise = np.random.normal(0, 0.05, len(cspi))
        cspi += noise

        return cspi

    def save_data(self, data, filename='japan_price_indices.csv'):
        """データをCSVファイルとして保存"""
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(output_dir, exist_ok=True)

        filepath = os.path.join(output_dir, filename)
        data.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"データを保存しました: {filepath}")

        return filepath

if __name__ == '__main__':
    # データ収集実行
    collector = JapanPriceIndexCollector(start_year=1990, end_year=2024)
    data = collector.generate_sample_data()

    print("生成されたデータの概要:")
    print(data.head())
    print("\nデータ統計:")
    print(data.describe())

    # データ保存
    collector.save_data(data)
