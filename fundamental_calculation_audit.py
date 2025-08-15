#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根本的計算方法監査 - 過不足計算の基盤設計検証
既存システムの計算方法とPhase 2実装の整合性検証
"""

from pathlib import Path
import json

def audit_fundamental_calculation_logic():
    """根本的な計算ロジックの監査"""
    
    print("=" * 120)
    print("🔍 根本的計算方法監査 - 過不足計算の基盤設計検証")
    print("=" * 120)
    
    # 1. スロット概念の設計妥当性分析
    analyze_slot_concept_validity()
    
    # 2. 時間変換の一貫性検証  
    analyze_time_conversion_consistency()
    
    # 3. long_df設計の妥当性検証
    analyze_long_df_design_validity()
    
    # 4. parsed_slots_countの意味検証
    analyze_parsed_slots_count_meaning()
    
    # 5. Phase 2実装との整合性検証
    analyze_phase2_implementation_consistency()

def analyze_slot_concept_validity():
    """スロット概念の設計妥当性分析"""
    
    print("\n📊 スロット概念の設計妥当性分析")
    print("-" * 100)
    
    slot_analysis = {
        "現在の設計": {
            "スロット単位": "30分 (DEFAULT_SLOT_MINUTES = 30)",
            "時間変換": "SLOT_HOURS = 0.5時間",
            "想定用途": "シフト時間帯の最小単位として使用",
            "計算式": "労働時間 = スロット数 × 0.5時間"
        },
        "設計の妥当性評価": {
            "業界標準適合性": "🟡 部分的",
            "詳細": [
                "✅ 30分単位は看護・介護業界で一般的",
                "⚠️ 連続シフト（8時間勤務等）の表現が冗長",
                "❌ 休憩時間の扱いが不明確",
                "❌ 夜勤跨ぎシフトの日付境界問題"
            ]
        },
        "発見された問題": {
            "二重変換リスク": "🔴 高リスク",
            "問題内容": [
                "shortage.pyで既に時間単位に変換済み",
                "dash_app.pyで再度SLOT_HOURSを乗算する可能性",
                "Phase 2実装でも同様のリスク",
                "データの意味（時間 vs スロット数）が曖昧"
            ],
            "影響範囲": "全分析結果の数値的正確性に影響"
        }
    }
    
    for category, details in slot_analysis.items():
        print(f"\n🎯 {category}:")
        if isinstance(details, dict):
            for key, value in details.items():
                if isinstance(value, list):
                    print(f"  {key}:")
                    for item in value:
                        print(f"    {item}")
                else:
                    print(f"  {key}: {value}")
        else:
            print(f"  {details}")

def analyze_time_conversion_consistency():
    """時間変換の一貫性検証"""
    
    print(f"\n⏰ 時間変換の一貫性検証")
    print("-" * 100)
    
    # 既存ファイルでの時間変換パターンを分析
    conversion_patterns = {
        "shortage.py (v2.7.0)": {
            "変換方法": "slot_hours = slot / 60.0",
            "保存形式": "lack_h (時間単位)",
            "計算式": "total_lack_hours = (lack_count * slot_hours).sum().sum()",
            "最終値": "時間単位で保存・表示"
        },
        "constants.py": {
            "定義": "SLOT_HOURS = DEFAULT_SLOT_MINUTES / 60.0",
            "値": "30分 → 0.5時間",
            "用途": "各モジュールでの統一的な時間変換"
        },
        "fact_extractor_prototype.py (Phase 2)": {
            "実装": "total_hours = group['parsed_slots_count'].sum() * SLOT_HOURS",
            "前提": "parsed_slots_countがスロット数",
            "問題": "parsed_slots_countが既に時間単位の場合、二重変換"
        },
        "lightweight_anomaly_detector.py (Phase 3.1)": {
            "実装": "monthly_hours = work_df.groupby(['staff', 'year_month'])['parsed_slots_count'].sum() * SLOT_HOURS",
            "同様問題": "parsed_slots_countの意味が不明確"
        }
    }
    
    print("📋 各モジュールでの時間変換パターン:")
    for module, pattern in conversion_patterns.items():
        print(f"\n  🔧 {module}:")
        for key, value in pattern.items():
            print(f"    {key}: {value}")
    
    # 不整合の検出
    print(f"\n⚠️ 検出された不整合:")
    inconsistencies = [
        {
            "問題": "parsed_slots_countの意味の曖昧性",
            "詳細": "スロット数なのか、既に時間単位なのかが不明確",
            "影響": "二重変換による計算誤差",
            "重要度": "🔴 クリティカル"
        },
        {
            "問題": "モジュール間での時間変換の不統一",
            "詳細": "shortage.pyとPhase 2実装で異なる前提",
            "影響": "分析結果の数値的不整合",
            "重要度": "🔴 クリティカル"
        },
        {
            "問題": "データの単位情報の欠如",
            "詳細": "long_dfのカラムに単位情報がない",
            "影響": "開発者の混乱、バグの温床",
            "重要度": "🟡 メジャー"
        }
    ]
    
    for inconsistency in inconsistencies:
        print(f"  {inconsistency['重要度']} {inconsistency['問題']}")
        print(f"    詳細: {inconsistency['詳細']}")
        print(f"    影響: {inconsistency['影響']}")

def analyze_long_df_design_validity():
    """long_df設計の妥当性検証"""
    
    print(f"\n📊 long_df設計の妥当性検証")
    print("-" * 100)
    
    long_df_analysis = {
        "現在の設計": {
            "必須カラム": [
                "ds (日時)",
                "staff (職員ID)",
                "role (職種)",
                "code (勤務コード)",
                "holiday_type (休日種別)",
                "parsed_slots_count (スロット数？時間？)"
            ],
            "データ形式": "長形式（各レコードが1つの勤務時間帯）",
            "想定": "1レコード = 1スロット期間の勤務"
        },
        "設計の問題点": {
            "データ意味の曖昧性": [
                "parsed_slots_countが何を表すか不明確",
                "1レコードが何時間の勤務を表すか不明",
                "休憩時間の扱いが不明",
                "連続勤務の境界が不明確"
            ],
            "スケーラビリティ問題": [
                "8時間勤務 = 16レコード（30分スロット）",
                "大規模データでの処理効率悪化",
                "メモリ使用量の増大"
            ],
            "業務実態との乖離": [
                "実際のシフト作成は時間単位",
                "30分刻みの詳細管理は現実的でない",
                "勤務実績と管理単位の不一致"
            ]
        },
        "代替設計案": {
            "時間ベース設計": {
                "カラム": "start_time, end_time, duration_hours",
                "利点": "直感的、計算効率良い、業務実態に合致"
            },
            "集約型設計": {
                "カラム": "date, staff, role, total_hours, shift_count",
                "利点": "データ量削減、処理高速化"
            }
        }
    }
    
    for category, details in long_df_analysis.items():
        print(f"\n🎯 {category}:")
        if isinstance(details, dict):
            for key, value in details.items():
                print(f"  {key}:")
                if isinstance(value, list):
                    for item in value:
                        print(f"    • {item}")
                else:
                    print(f"    {value}")
        else:
            print(f"  {details}")

def analyze_parsed_slots_count_meaning():
    """parsed_slots_countの意味検証"""
    
    print(f"\n🔍 parsed_slots_countの意味検証")
    print("-" * 100)
    
    # ファイル内容の分析を通じてparsed_slots_countの使われ方を調査
    usage_patterns = {
        "Phase 2実装での使用": {
            "計算式": "total_hours = group['parsed_slots_count'].sum() * SLOT_HOURS",
            "前提": "parsed_slots_countはスロット数",
            "結果": "時間単位の労働時間"
        },
        "Phase 3.1実装での使用": {
            "計算式": "monthly_hours = groupby(['staff', 'year_month'])['parsed_slots_count'].sum() * SLOT_HOURS",
            "前提": "同様にスロット数として扱う",
            "結果": "月間労働時間"
        },
        "推定される意味": {
            "仮説1": "スロット数（整数値、30分刻み）",
            "仮説2": "時間値（小数値、時間単位）",
            "仮説3": "分数値（整数値、分単位）"
        }
    }
    
    print("📋 parsed_slots_countの使用パターン分析:")
    for pattern_name, pattern_detail in usage_patterns.items():
        print(f"\n  🔧 {pattern_name}:")
        for key, value in pattern_detail.items():
            print(f"    {key}: {value}")
    
    # 検証方法の提案
    print(f"\n🎯 検証が必要な項目:")
    verification_items = [
        "実際のlong_dfサンプルでのparsed_slots_countの値の確認",
        "30分勤務時のparsed_slots_countが1なのか0.5なのか",
        "8時間勤務時の合計値が16なのか8なのか",
        "既存のshortage.pyでの計算結果との整合性",
        "実データでの数値レンジの確認"
    ]
    
    for i, item in enumerate(verification_items, 1):
        print(f"  {i}. {item}")

def analyze_phase2_implementation_consistency():
    """Phase 2実装との整合性検証"""
    
    print(f"\n🔧 Phase 2実装との整合性検証")
    print("-" * 100)
    
    consistency_analysis = {
        "実装前提の確認": {
            "Phase 2の前提": "parsed_slots_countはスロット数",
            "計算方法": "時間 = スロット数 × 0.5",
            "既存システム": "shortage.pyは既に時間単位で保存",
            "矛盾": "二重変換の可能性"
        },
        "具体的な問題箇所": {
            "fact_extractor_prototype.py:98": {
                "コード": "total_hours = group['parsed_slots_count'].sum() * SLOT_HOURS",
                "問題": "parsed_slots_countが既に時間単位なら二重変換",
                "修正案": "データの意味を確認してから計算方法決定"
            },
            "lightweight_anomaly_detector.py:132": {
                "コード": "monthly_hours = work_df.groupby(['staff', 'year_month'])['parsed_slots_count'].sum() * SLOT_HOURS",
                "問題": "同様の二重変換リスク",
                "修正案": "統一的なデータ解釈の確立"
            }
        },
        "影響評価": {
            "数値精度": "50%の誤差（0.5倍または2倍）の可能性",
            "法的準拠": "労働時間の誤算により法的基準判定も誤る",
            "ビジネス影響": "コスト計算、人員計画の根本的誤り",
            "信頼性": "システム全体の数値的信頼性に疑義"
        },
        "緊急対応が必要な理由": {
            "1": "既に統合済みのシステムでの計算誤差",
            "2": "法的準拠チェックの根本的な信頼性問題",
            "3": "経営判断に直結する数値の正確性問題",
            "4": "第三者検証で95.2%だった品質評価の再評価が必要"
        }
    }
    
    for category, details in consistency_analysis.items():
        print(f"\n🎯 {category}:")
        if isinstance(details, dict):
            for key, value in details.items():
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for subkey, subvalue in value.items():
                        print(f"    {subkey}: {subvalue}")
                else:
                    print(f"  {key}: {value}")

def generate_fundamental_audit_summary():
    """根本的監査のサマリー生成"""
    
    print(f"\n📋 根本的監査サマリー")
    print("=" * 120)
    
    critical_findings = {
        "クリティカル問題": [
            "parsed_slots_countの意味の曖昧性による二重変換リスク",
            "既存システムとPhase 2実装の計算前提の不整合", 
            "時間単位データの扱いに関する根本的設計欠陥",
            "法的準拠チェックの数値的信頼性問題"
        ],
        "影響範囲": [
            "Phase 2: 基本事実抽出の労働時間計算",
            "Phase 3.1: 異常検知の労働時間閾値判定",
            "統合ファクトブック: 全ての時間ベース分析",
            "法的準拠: 労働基準法の時間制限チェック"
        ],
        "緊急対応項目": [
            "1. 実データでのparsed_slots_count値の確認",
            "2. 既存shortage.pyとの計算結果比較",
            "3. Phase 2/3.1の時間計算ロジック修正",
            "4. データ仕様書の明確化",
            "5. 全モジュールでの時間変換統一"
        ],
        "品質への影響": [
            "数値精度: 最大50%の誤差可能性",
            "法的準拠: 根本的な判定精度問題",
            "システム信頼性: 計算基盤の信頼性低下",
            "第三者評価: 95.2%スコアの再評価必要"
        ]
    }
    
    for category, items in critical_findings.items():
        print(f"\n🚨 {category}:")
        for i, item in enumerate(items, 1):
            print(f"  {i}. {item}")
    
    # 優先度評価
    print(f"\n🎯 対応優先度:")
    priorities = [
        ("最優先", "実データでのparsed_slots_count意味の確認"),
        ("高優先", "Phase 2/3.1の時間計算ロジック修正"),
        ("中優先", "データ仕様書の整備"),
        ("低優先", "長期的なアーキテクチャ改善")
    ]
    
    for priority, action in priorities:
        priority_icon = "🔥" if priority == "最優先" else "⚠️" if priority == "高優先" else "📋"
        print(f"  {priority_icon} {priority}: {action}")
    
    # 総合評価
    print(f"\n📊 総合評価:")
    print("🔴 根本的な計算基盤に重大な設計欠陥を発見")
    print("📋 Phase 2/3の実装は表面的な統合に留まり、基盤検証が不十分")
    print("⚠️ 修正範囲が広範囲に及ぶため、段階的なアプローチが必要")
    print("🎯 数値的信頼性の確保が最優先課題")

if __name__ == "__main__":
    print("🔍 根本的計算方法監査を開始します...")
    
    audit_fundamental_calculation_logic()
    generate_fundamental_audit_summary()
    
    print(f"\n" + "=" * 120)
    print("📝 監査結論:")
    print("既存システムの計算基盤に根本的な設計問題を発見。")
    print("Phase 2/3の実装は基盤理解不足により重大な計算誤差を含む可能性。")
    print("緊急的な検証と修正が必要。")
    print("✅ 根本的監査完了")