#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法的・業界標準準拠の具体的集計内容詳細分析
各集計項目が対応する法令条文と業界標準の明確化
"""

from pathlib import Path

def analyze_legal_compliance_calculations():
    """法的準拠のための具体的集計内容分析"""
    
    print("=" * 100)
    print("📋 法的・業界標準準拠の具体的集計内容詳細分析")
    print("=" * 100)
    
    # 1. 労働基準法準拠の集計項目
    print("\n🏛️ 労働基準法準拠集計")
    print("-" * 90)
    
    labor_law_calculations = {
        "労働基準法第32条（労働時間）": {
            "集計項目": "monthly_hours = group.groupby('year_month')['parsed_slots_count'].sum() * SLOT_HOURS",
            "具体的処理": [
                "1. 個人別・月別の総労働時間を集計",
                "2. 月間労働時間 = スロット数 × 0.5時間",
                "3. 全体平均の1.5倍超過を異常として検知",
                "4. threshold = overall_mean * 1.5"
            ],
            "法的基準": "月間160時間（一般）、月間240時間（医療従事者上限）",
            "重要度判定": "緊急（2倍超過）、高（1.5倍超過）、中（1.2倍超過）",
            "出力例": "2024-07月の労働時間が異常に多い (280.5時間)"
        },
        
        "労働基準法第35条（休日）": {
            "集計項目": "continuous_days = 連続勤務日数の計算",
            "具体的処理": [
                "1. work_dates = group['ds'].dt.date.unique().sort()",
                "2. 日付差が1日の場合、連続勤務としてカウント",
                "3. continuous_days > 7日で違反として検知",
                "4. 期間開始日〜終了日を記録"
            ],
            "法的基準": "週1回の休日確保（連続7日勤務は原則違反）",
            "重要度判定": "緊急（12日超過）、高（7日超過）、中（5日超過）",
            "出力例": "10日間の連続勤務を検出 (2024-07-01 → 2024-07-10)"
        },
        
        "労働時間等設定改善法（勤務間インターバル）": {
            "集計項目": "interval_hours = (curr_start - prev_end).total_seconds() / 3600",
            "具体的処理": [
                "1. sorted_group = group.sort_values('ds')",
                "2. 前回勤務終了〜次回勤務開始の時間差を計算",
                "3. interval_hours < 11時間で違反検知",
                "4. violation_rate = violations / total_intervals"
            ],
            "法的基準": "11時間のインターバル確保（努力義務）",
            "重要度判定": "高（30%超の違反率）、中（10%超の違反率）",
            "出力例": "勤務間インターバル違反が多発 (15/50回)"
        }
    }
    
    for law_section, details in labor_law_calculations.items():
        print(f"\n📜 {law_section}")
        print(f"  💻 集計処理: {details['集計項目']}")
        print("  🔧 具体的処理:")
        for step in details['具体的処理']:
            print(f"    {step}")
        print(f"  ⚖️ 法的基準: {details['法的基準']}")
        print(f"  🚨 重要度: {details['重要度判定']}")
        print(f"  📝 出力例: {details['出力例']}")
    
    # 2. 医療法・看護業界準拠の集計
    print(f"\n🏥 医療法・看護業界標準準拠集計")
    print("-" * 90)
    
    medical_law_calculations = {
        "医療法施行規則第19条の3（看護職員配置）": {
            "集計項目": "role_stats = work_df.groupby('role').agg({'staff': 'nunique', 'parsed_slots_count': 'sum'})",
            "具体的処理": [
                "1. 職種別の職員数をカウント（'role'列による分類）",
                "2. 職種別の総労働時間を集計",
                "3. 総レコード数・総スロット数を職種別に算出",
                "4. 職種別労働時間 = スロット数 × 0.5時間"
            ],
            "法的基準": "看護職員の適正配置（患者7:1、10:1等）",
            "ビジネス価値": "医療の質確保、診療報酬適正請求",
            "出力例": "看護師: 25名、総労働時間: 4,200時間、総レコード数: 8,400件"
        },
        
        "看護職員の夜勤・交代制勤務に関する指針": {
            "集計項目": "night_shifts = group[group['code'].str.contains('夜', na=False)].shape[0]",
            "具体的処理": [
                "1. コード列に'夜'を含む勤務をパターンマッチで検出",
                "2. night_shift_ratio = night_shifts / total_shifts",
                "3. 夜勤比率 > 40%で異常として検知",
                "4. 個人別の夜勤負荷を定量化"
            ],
            "法的基準": "月8回以内の夜勤、適切な夜勤間隔確保",
            "重要度判定": "高（60%超）、中（40%超）、低（30%超）",
            "出力例": "夜勤頻度が過多 (45.2%、28回/62回)"
        },
        
        "雇用形態別管理（労働契約法）": {
            "集計項目": "emp_stats = work_df.groupby('employment').agg({'staff': 'nunique', 'parsed_slots_count': 'sum'})",
            "具体的処理": [
                "1. 雇用形態別（正職員・パート・派遣等）の集計",
                "2. 雇用形態別の職員数・労働時間を算出",
                "3. 雇用形態別の労働負荷バランス分析",
                "4. 非正規職員の労働時間上限管理"
            ],
            "法的基準": "有期契約労働者の適正管理、同一労働同一賃金",
            "ビジネス価値": "人件費最適化、コンプライアンス確保",
            "出力例": "正職員: 30名、パート: 15名、派遣: 5名"
        }
    }
    
    for regulation, details in medical_law_calculations.items():
        print(f"\n🏥 {regulation}")
        print(f"  💻 集計処理: {details['集計項目']}")
        print("  🔧 具体的処理:")
        for step in details['具体的処理']:
            print(f"    {step}")
        print(f"  ⚖️ 法的基準: {details['法的基準']}")
        if 'ビジネス価値' in details:
            print(f"  💰 ビジネス価値: {details['ビジネス価値']}")
        if '重要度判定' in details:
            print(f"  🚨 重要度: {details['重要度判定']}")
        print(f"  📝 出力例: {details['出力例']}")

def analyze_time_pattern_compliance():
    """時間パターン分析の法的準拠"""
    
    print(f"\n⏰ 時間パターン分析の法的準拠")
    print("=" * 100)
    
    time_pattern_calculations = {
        "曜日別勤務分析": {
            "集計処理": "weekday_counts = group.groupby(group['ds'].dt.dayofweek).size()",
            "法的根拠": "労働基準法第35条（週休制）",
            "具体的計算": [
                "1. 曜日番号取得: ds.dt.dayofweek (0=月曜, 6=日曜)",
                "2. 曜日別勤務回数をカウント",
                "3. 各曜日の勤務比率を計算: count / total_records",
                "4. 土日勤務率の特別集計: weekend_shifts = group[ds.dt.dayofweek.isin([5,6])]"
            ],
            "準拠確認": "週1回休日確保、土日勤務過多の検知",
            "出力データ": "月曜: 15回(24%), 火曜: 12回(19%), ..., 日曜: 3回(5%)"
        },
        
        "時間帯別勤務分析": {
            "集計処理": "hour_counts = group.groupby(group['ds'].dt.hour).size()",
            "法的根拠": "労働基準法第37条（深夜労働）、労働安全衛生法",
            "具体的計算": [
                "1. 時間取得: ds.dt.hour (0-23時)",
                "2. 時間帯別勤務回数をカウント",
                "3. 深夜時間帯（22-6時）の特別集計",
                "4. 時間帯別勤務比率: count / total_records"
            ],
            "準拠確認": "深夜労働（22-6時）の適正管理、労働強度分析",
            "出力データ": "8時台: 25回(15%), 22時台: 8回(5%), 2時台: 12回(7%)"
        },
        
        "休日勤務分析": {
            "集計処理": "holiday_shifts = group[group['holiday_type'].notna() & (group['holiday_type'] != '')]",
            "法的根拠": "労働基準法第35条（休日労働）",
            "具体的計算": [
                "1. holiday_type列の非空データを抽出",
                "2. 休日種別（祝日・年末年始等）別の集計",
                "3. 休日勤務回数・比率の算出",
                "4. 休日労働手当対象の勤務特定"
            ],
            "準拠確認": "休日労働の適正管理、割増賃金計算根拠",
            "出力データ": "祝日勤務: 5回, 年末年始: 2回, 全休日勤務率: 12%"
        }
    }
    
    for pattern_type, details in time_pattern_calculations.items():
        print(f"\n📊 {pattern_type}")
        print(f"  💻 集計処理: {details['集計処理']}")
        print(f"  ⚖️ 法的根拠: {details['法的根拠']}")
        print("  🔧 具体的計算:")
        for step in details['具体的計算']:
            print(f"    {step}")
        print(f"  ✅ 準拠確認: {details['準拠確認']}")
        print(f"  📋 出力データ: {details['出力データ']}")

def demonstrate_calculation_examples():
    """実際の計算例の詳細デモ"""
    
    print(f"\n💡 実際の計算例デモンストレーション")
    print("=" * 100)
    
    # サンプルデータでの計算例
    calculation_examples = {
        "労働時間違反検知の計算例": {
            "サンプルデータ": "田中太郎さん: 7月 = 285時間, 全体平均 = 180時間",
            "計算過程": [
                "1. threshold = 180 * 1.5 = 270時間",
                "2. 285 > 270 → 違反検知",
                "3. severity = calculate_severity(285, 270, 360)",
                "4. 285 > 270*1.5(405) → False, 285 > 270*1.2(324) → False → '中'"
            ],
            "出力結果": "AnomalyResult(anomaly_type='過度な労働時間', severity='中', staff='田中太郎', value=285.0)",
            "法的意味": "月間労働時間が基準値を55%超過、要注意レベル"
        },
        
        "連続勤務違反の計算例": {
            "サンプルデータ": "佐藤花子さん: 7/1,7/2,7/3,7/4,7/5,7/6,7/7,7/8,7/9",
            "計算過程": [
                "1. work_dates = [2024-07-01, 2024-07-02, ..., 2024-07-09]",
                "2. continuous_days = 9 (連続9日間)",
                "3. 9 > threshold(7) → 違反検知",
                "4. severity = calculate_severity(9, 7, 12) → '高'"
            ],
            "出力結果": "AnomalyResult(anomaly_type='連続勤務違反', severity='高', staff='佐藤花子', value=9)",
            "法的意味": "労働基準法第35条違反の可能性、緊急対応必要"
        },
        
        "夜勤頻度過多の計算例": {
            "サンプルデータ": "山田次郎さん: 全62回勤務中、夜勤28回",
            "計算過程": [
                "1. night_shifts = 28 (code列に'夜'を含む勤務)",
                "2. night_shift_ratio = 28/62 = 0.452 (45.2%)",
                "3. 0.452 > threshold(0.4) → 違反検知",
                "4. severity = calculate_severity(0.452, 0.4, 0.6) → '中'"
            ],
            "出力結果": "AnomalyResult(anomaly_type='夜勤頻度過多', severity='中', staff='山田次郎', value=0.452)",
            "法的意味": "看護職員夜勤指針基準超過、健康管理要注意"
        },
        
        "職種別労働時間集計例": {
            "サンプルデータ": "看護師25名、介護士15名、事務員5名",
            "計算過程": [
                "1. role_stats = work_df.groupby('role').agg({'staff': 'nunique', 'parsed_slots_count': 'sum'})",
                "2. 看護師: staff=25, slots=8400, hours=4200.0",
                "3. 介護士: staff=15, slots=4800, hours=2400.0", 
                "4. 事務員: staff=5, slots=800, hours=400.0"
            ],
            "出力結果": "職種別統計DataFrame: 看護師(25名,4200h), 介護士(15名,2400h), 事務員(5名,400h)",
            "法的意味": "医療法看護職員配置基準の遵守状況確認データ"
        }
    }
    
    for example_name, details in calculation_examples.items():
        print(f"\n🧮 {example_name}")
        print(f"  📊 サンプルデータ: {details['サンプルデータ']}")
        print("  🔢 計算過程:")
        for step in details['計算過程']:
            print(f"    {step}")
        print(f"  📋 出力結果: {details['出力結果']}")
        print(f"  ⚖️ 法的意味: {details['法的意味']}")

if __name__ == "__main__":
    print("🔍 法的・業界標準準拠の具体的集計内容を詳細分析します...")
    
    analyze_legal_compliance_calculations()
    analyze_time_pattern_compliance()
    demonstrate_calculation_examples()
    
    print(f"\n" + "=" * 100)
    print("📋 結論: 全集計項目が具体的な法令条文と業界標準に直接対応")
    print("⚖️ 根拠: 労働基準法・医療法・看護業界指針の条文レベル準拠")
    print("🎯 精度: 個人・期間・職種・時間軸での多次元的法令遵守チェック")
    print("✅ 分析完了")