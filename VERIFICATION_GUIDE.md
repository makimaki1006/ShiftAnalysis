# 統一分析管理システム 検証ガイド

## 🎯 検証の目的
1. 不足時間計算の正確性確認
2. 動的スロット設定の動作確認
3. JSON出力の品質確認
4. シナリオ別集計の正確性確認

## 📋 検証前の準備

### 1. テストデータの準備
- 実際に使用しているExcelファイル（できれば小規模なもの）
- または付属のテストデータ（`シート_テスト用データ.xlsx`など）

### 2. 現在の設定確認
```bash
# Gitでの変更状況確認
git status

# 統一システムファイルの存在確認
ls -la shift_suite/tasks/unified_analysis_manager.py
```

---

## 🔬 検証手順

### 検証1: 基本動作確認

#### Step 1: アプリケーション起動
```bash
streamlit run app.py
```

#### Step 2: 初期設定確認
1. ブラウザでアプリケーションを開く
2. サイドバーの「スロット間隔」設定を確認（デフォルト: 30分）
3. 値を変更してみる（例: 15分、60分）

#### 期待される結果:
- スロット間隔が5〜1440分の範囲で設定可能
- 設定値が保持される

---

### 検証2: 実データによる計算精度検証

#### Step 1: 小規模データでのテスト実行
1. テスト用Excelファイルをアップロード
2. 必要人数の計算方法を「統計的推定」に設定
3. 以下の分析を有効化:
   - ✅ 不足分析
   - ✅ 疲労分析
   - ✅ 公平性分析
4. 「分析を実行」をクリック

#### Step 2: 不足時間の確認
1. 分析完了後、「不足分析」タブを開く
2. 表示される数値を記録:
   - 総不足時間
   - 役職別不足時間
   - proportional分析の結果

#### Step 3: 計算の妥当性確認
```python
# 簡易検証スクリプトを作成
cat > verify_shortage_calculation.py << 'EOF'
import pandas as pd
from pathlib import Path

# 結果ファイルの読み込み
result_dir = Path("out/YOUR_FILE_NAME/scenario_default")
if result_dir.exists():
    # 不足分析結果の確認
    shortage_files = list(result_dir.glob("*shortage*.xlsx"))
    for file in shortage_files:
        print(f"\n=== {file.name} ===")
        df = pd.read_excel(file)
        print(df.head())
        if 'lack_h' in df.columns:
            total = df['lack_h'].sum()
            print(f"総不足時間: {total:.2f}時間")
            print(f"最大不足: {df['lack_h'].max():.2f}時間")
            print(f"平均不足: {df['lack_h'].mean():.2f}時間")
EOF

python3 verify_shortage_calculation.py
```

#### 期待される結果:
- 不足時間が現実的な範囲内（例: 月間で0〜500時間程度）
- 役職別の不足時間が妥当
- スロット間隔を変更しても、時間換算が正しい

---

### 検証3: JSON出力内容の実態確認

#### Step 1: AI包括レポートの生成確認
1. 分析実行後、結果画面を確認
2. 「AI向け分析結果（JSON）」セクションを探す

#### Step 2: JSON内容の検証
```python
# JSON出力確認スクリプト
cat > verify_json_output.py << 'EOF'
import json
from pathlib import Path

# 結果ディレクトリの確認
result_dirs = list(Path("out").glob("*/scenario_*"))
for result_dir in result_dirs:
    json_files = list(result_dir.glob("*comprehensive*.json"))
    for json_file in json_files:
        print(f"\n=== {json_file} ===")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # デフォルト値のチェック
        def check_defaults(obj, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if v == 0 or v == 0.0 or v == "N/A" or v == "default":
                        print(f"⚠️ デフォルト値検出: {path}.{k} = {v}")
                    elif isinstance(v, (dict, list)):
                        check_defaults(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_defaults(item, f"{path}[{i}]")
        
        check_defaults(data)
        
        # 主要メトリクスの確認
        if 'shortage_analysis' in data:
            shortage = data['shortage_analysis']
            print(f"不足時間: {shortage.get('total_shortage_hours', 'なし')}")
            print(f"データ整合性: {shortage.get('data_integrity', 'なし')}")
EOF

python3 verify_json_output.py
```

#### 期待される結果:
- JSON内に実際の分析結果が含まれている
- デフォルト値（0, "N/A", "default"）が最小限
- data_integrityが"valid"になっている

---

### 検証4: シナリオ別集計の確認

#### Step 1: 複数シナリオでのテスト
1. 異なるパラメータで2回以上分析を実行
2. 各実行で異なるスロット間隔を設定（例: 30分、60分）

#### Step 2: 結果の比較
```bash
# 結果ディレクトリの構造確認
ls -la out/*/scenario_*/

# 各シナリオの結果確認
find out -name "*shortage*.xlsx" -exec echo "=== {} ===" \; -exec head -5 {} \;
```

#### 期待される結果:
- 各シナリオの結果が独立して保存されている
- proportional分析が各シナリオ内で完結している
- シナリオ間で結果が混同されていない

---

### 検証5: 動的スロット設定の伝播確認

#### Step 1: ログ確認による動的設定の追跡
```bash
# アプリケーション実行時のログを確認
streamlit run app.py 2>&1 | grep -E "slot|スロット"
```

#### Step 2: 各モジュールでの設定確認
```python
# 動的スロット確認スクリプト
cat > verify_slot_propagation.py << 'EOF'
import re
from pathlib import Path

# 各分析モジュールでのスロット処理確認
modules = [
    "shift_suite/tasks/shortage.py",
    "shift_suite/tasks/fatigue.py",
    "shift_suite/tasks/heatmap.py"
]

for module_path in modules:
    if Path(module_path).exists():
        print(f"\n=== {module_path} ===")
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # スロット関連の処理を検索
        slot_patterns = [
            r'slot_minutes.*=.*(\d+)',
            r'slot_hours.*=.*slot.*60',
            r'SLOT_HOURS',  # 固定値の残存チェック
        ]
        
        for pattern in slot_patterns:
            matches = re.findall(pattern, content)
            if matches:
                print(f"  {pattern}: {len(matches)}箇所")
EOF

python3 verify_slot_propagation.py
```

#### 期待される結果:
- SLOT_HOURS（固定値）の使用が0箇所
- slot_minutes/slot_hoursの動的計算が実装されている

---

## 📊 検証結果の記録

### 検証チェックリスト

| 検証項目 | 結果 | 備考 |
|---------|------|------|
| アプリ起動 | □ OK / □ NG | |
| スロット設定変更 | □ OK / □ NG | |
| 不足時間計算 | □ OK / □ NG | 計算値: ___時間 |
| JSON出力品質 | □ OK / □ NG | デフォルト値: ___個 |
| シナリオ独立性 | □ OK / □ NG | |
| 動的設定伝播 | □ OK / □ NG | |

### 問題発見時の記録
```
発見日時: 
問題の内容:
再現手順:
期待される動作:
実際の動作:
エラーメッセージ（あれば）:
```

---

## 🚨 トラブルシューティング

### よくある問題と対処法

#### 1. アプリが起動しない
```bash
# 依存関係の確認
pip list | grep -E "streamlit|pandas|numpy"

# 必要に応じて再インストール
pip install -r requirements.txt
```

#### 2. 分析が途中で止まる
- ブラウザのコンソールログを確認（F12）
- `shift_suite.log`ファイルを確認
- メモリ使用量を確認

#### 3. 結果が表示されない
- `out`ディレクトリの権限を確認
- セッションステートをクリア（アプリ再起動）

---

## 📝 検証後のアクション

### 問題が見つかった場合
1. 上記の「問題発見時の記録」フォーマットで詳細を記録
2. 可能であればスクリーンショットを撮影
3. `shift_suite.log`の該当部分をコピー

### 問題がなかった場合
1. 検証チェックリストをすべて「OK」で埋める
2. 使用したテストデータの概要を記録
3. パフォーマンス（処理時間）を記録

---

## 💡 追加の検証アイデア

### 高度な検証（オプション）
1. **大規模データテスト**: 1ヶ月以上のデータで検証
2. **境界値テスト**: スロット間隔を極端な値（5分、1440分）で検証
3. **並行実行テスト**: 複数のブラウザタブで同時実行
4. **メモリリークテスト**: 連続10回の分析実行

### 定量的検証
```python
# 処理時間の計測
import time
start = time.time()
# 分析実行
end = time.time()
print(f"処理時間: {end - start:.2f}秒")
```

---

このガイドに従って検証を実施し、結果を記録してください。
問題が見つかった場合は、具体的な再現手順と共に報告してください。