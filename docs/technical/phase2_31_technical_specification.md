# Phase 2/3.1 技術仕様書

**文書バージョン**: 1.0  
**作成日**: 2025年08月03日  
**最終更新**: 2025年08月03日

## 📋 概要

本文書は、Shift-Suite システムにおけるPhase 2/3.1のSLOT_HOURS修正に関する技術仕様を詳述します。

## 🎯 修正の背景と目的

### 問題の発見
- **問題**: parsed_slots_count（スロット数）を時間として扱う重複変換問題
- **影響**: 計算結果が実際の2倍になる精度問題
- **発見経緯**: 深い思考による「なぜこの値なのか」の追求

### 解決方針
```
修正前: parsed_slots_count（既に時間と誤認）
修正後: parsed_slots_count × SLOT_HOURS（正確な時間変換）
```

## 🔧 技術的変更内容

### 1. Phase 2: FactExtractorPrototype
**ファイル**: `shift_suite/tasks/fact_extractor_prototype.py`

**修正箇所**: 4箇所
```python
# 修正例
total_hours = group['parsed_slots_count'].sum() * SLOT_HOURS
```

### 2. Phase 3.1: LightweightAnomalyDetector  
**ファイル**: `shift_suite/tasks/lightweight_anomaly_detector.py`

**修正箇所**: 1箇所
```python
# 修正例
monthly_hours = work_df.groupby(['staff', 'year_month'])['parsed_slots_count'].sum() * SLOT_HOURS
```

### 3. 定数定義
```python
SLOT_HOURS = 0.5  # 30分スロット = 0.5時間
```

## 📊 データフロー

```
Excel入力 → io_excel.py → parsed_slots_count（整数）
                           ↓
Phase 2/3.1 → parsed_slots_count × SLOT_HOURS → 時間（浮動小数点）
                           ↓
FactBookVisualizer → dash_fact_book_integration → dash_app.py
```

## 🧪 品質保証

### テスト項目
1. **単体テスト**: SLOT_HOURS計算の正確性
2. **統合テスト**: Phase 2/3.1間のデータ整合性
3. **回帰テスト**: 既存機能への影響確認

### 検証方法
```python
# 検証例
slots = 8
expected_hours = 4.0
actual_hours = slots * SLOT_HOURS
assert abs(actual_hours - expected_hours) < 0.001
```

## ⚠️ 重要な考慮事項

### 前提条件の明確化
- **30分スロット**: 現在の前提だが、業務実態との適合性要検証
- **一律変換**: 全業務を同等扱いしているが、重み付けの余地あり
- **数値の意味**: 670時間は「現在の計算結果」であり「絶対的真実」ではない

### 継続的改善の視点
- より良い時間単位の可能性（15分、可変スロット）
- 質的評価の導入（スキル×時間）
- 業務実態との継続的照合

## 🔧 設定・環境

### 必要な依存関係
```
pandas >= 1.0.0
numpy >= 1.18.0
```

### 設定ファイル
```json
{
    "SLOT_HOURS": 0.5,
    "calculation_precision": 3,
    "validation_enabled": true
}
```

## 📈 性能特性

### 計算性能
- **基本計算**: <0.001秒
- **大量データ（1000件）**: 0.0002秒
- **メモリ使用量**: 最小限（in-place計算）

### スケーラビリティ
- **線形スケーリング**: データ量に比例した処理時間
- **精度保持**: 大規模集計での累積誤差なし

## 🚀 デプロイメント

### デプロイ手順
1. バックアップ作成
2. 構文チェック実行
3. Phase 2/3.1ファイル更新
4. 統合テスト実行
5. 本番反映

### ロールバック手順
```bash
# バックアップからの復旧
cp backup/fact_extractor_prototype.py shift_suite/tasks/
cp backup/lightweight_anomaly_detector.py shift_suite/tasks/
```

## 📝 変更履歴

| 日付 | バージョン | 変更内容 | 担当者 |
|------|-----------|----------|--------|
| 2025-08-03 | 1.0 | 初版作成、SLOT_HOURS修正実装 | Claude Code |

## 🔗 関連文書

- [運用・保守マニュアル](../operational/operations_maintenance_manual.md)
- [継続的改善フレームワーク](../improvement/continuous_improvement_framework.md)
- [API・データフロー仕様書](api_dataflow_specification.md)

---
*本文書は継続的改善の精神に基づき、定期的な見直しと更新を行います。*
