#!/usr/bin/env python3
"""
dash_app.py側への按分廃止タブ追加
Step 2: 按分廃止・職種別分析タブの実装
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import re

def generate_proportional_abolition_tab_code():
    """按分廃止タブのコード生成"""
    
    print('=' * 80)
    print('Step 2: dash_app.py按分廃止タブ追加')
    print('按分廃止・職種別分析タブの実装コード生成')
    print('=' * 80)
    
    # 1. create_proportional_abolition_tab関数
    tab_function_code = '''
def create_proportional_abolition_tab(selected_scenario: str = None) -> html.Div:
    """按分廃止・職種別分析タブを作成"""
    try:
        log.info("===== 按分廃止・職種別分析タブ作成開始 =====")
        log.info(f"scenario: {selected_scenario}")
        
        content = []
        
        # 🎯 分析タイトルとコンセプト説明
        content.append(html.Div([
            html.H2("🎯 按分廃止・職種別分析", style=UNIFIED_STYLES['header']),
            html.P([
                "従来の按分方式を廃止し、各職種の真の過不足を分析します。",
                html.Br(),
                "按分による「真実の隠蔽」を排除し、現場の実態に即した分析を提供します。"
            ], style={
                'backgroundColor': '#e8f4fd', 
                'padding': '15px', 
                'border-left': '4px solid #2196F3',
                'marginBottom': '30px'
            })
        ]))
        
        # 按分廃止データ読み込み
        log.info("按分廃止データ読み込み開始")
        df_proportional_role = data_get('proportional_abolition_role_summary', pd.DataFrame())
        df_proportional_org = data_get('proportional_abolition_organization_summary', pd.DataFrame())
        
        if df_proportional_role.empty:
            log.warning("按分廃止分析結果が見つかりません")
            content.append(html.Div([
                html.H4("⚠️ データ不足", style={'color': '#ff9800'}),
                html.P([
                    "按分廃止分析結果が見つかりません。",
                    html.Br(),
                    "app.pyで按分廃止分析を実行し、結果をZIPファイルでアップロードしてください。"
                ], style={'color': '#666', 'fontSize': '16px'}),
                html.Div([
                    html.H5("実行手順:"),
                    html.Ol([
                        html.Li("app.pyで分析を実行"),
                        html.Li("按分廃止分析結果を含むZIPファイルをダウンロード"),
                        html.Li("このダッシュボードにZIPファイルをアップロード"),
                        html.Li("按分廃止分析タブで結果確認")
                    ])
                ], style={'marginTop': '20px'})
            ], style={
                'backgroundColor': '#fff3e0',
                'padding': '20px',
                'borderRadius': '8px',
                'border': '2px solid #ff9800'
            }))
            return html.Div(content)
        
        log.info(f"按分廃止データ読み込み完了: 職種{len(df_proportional_role)}個")
        
        # 📊 組織全体サマリー
        if not df_proportional_org.empty:
            org_data = df_proportional_org.iloc[0]
            log.info(f"組織全体データ: {org_data['status']}")
            
            content.append(html.H3("📊 組織全体の真の過不足状況"))
            
            # 状態に応じた色設定
            shortage_color = '#f44336' if org_data['total_shortage'] > 0 else '#4caf50' if org_data['total_shortage'] < 0 else '#ff9800'
            status_colors = {
                'SHORTAGE': '#f44336',
                'SURPLUS': '#4caf50', 
                'BALANCED': '#ff9800'
            }
            status_color = status_colors.get(org_data['status'], '#666')
            
            status_text = {
                'SHORTAGE': '🔴 人手不足',
                'SURPLUS': '🟢 人手余剰',
                'BALANCED': '🟡 適正配置'
            }.get(org_data['status'], org_data['status'])
            
            metrics_row = html.Div([
                html.Div([
                    create_metric_card("Need時間/日", f"{org_data['total_need']:.1f}h")
                ], style={'width': '23%', 'display': 'inline-block', 'padding': '5px'}),
                
                html.Div([
                    create_metric_card("実配置時間/日", f"{org_data['total_actual']:.1f}h")  
                ], style={'width': '23%', 'display': 'inline-block', 'padding': '5px'}),
                
                html.Div([
                    create_metric_card("過不足時間/日", 
                                     f"{org_data['total_shortage']:+.1f}h",
                                     color=shortage_color)
                ], style={'width': '23%', 'display': 'inline-block', 'padding': '5px'}),
                
                html.Div([
                    create_metric_card("組織状態", status_text, color=status_color)
                ], style={'width': '23%', 'display': 'inline-block', 'padding': '5px'}),
                
                html.Div([
                    create_metric_card("総スタッフ数", f"{org_data['total_staff_count']}名")
                ], style={'width': '8%', 'display': 'inline-block', 'padding': '5px'})
            ], style={'marginBottom': '30px', 'display': 'flex', 'flexWrap': 'wrap'})
            
            content.append(metrics_row)
        
        # 🎯 職種別真の過不足分析
        content.append(html.H3("🎯 職種別真の過不足分析 (按分廃止)", 
                              style={'marginTop': '30px'}))
        
        # 職種別メトリクス表示
        if not df_proportional_role.empty:
            
            # 不足職種と余剰職種の分離
            shortage_roles = df_proportional_role[df_proportional_role['過不足時間/日'] > 0].sort_values('過不足時間/日', ascending=False)
            surplus_roles = df_proportional_role[df_proportional_role['過不足時間/日'] < 0].sort_values('過不足時間/日', ascending=True)
            balanced_roles = df_proportional_role[df_proportional_role['過不足時間/日'] == 0]
            
            # 重要な発見の表示
            if len(shortage_roles) > 0:
                severe_shortage = shortage_roles[shortage_roles['過不足時間/日'] > 2.0]
                zero_allocation = shortage_roles[shortage_roles['現在スタッフ数'] == 0]
                
                if len(severe_shortage) > 0 or len(zero_allocation) > 0:
                    content.append(html.Div([
                        html.H4("⚠️ 按分廃止により発見された重要な問題", style={'color': '#f44336'}),
                        html.Ul([
                            html.Li(f"深刻な不足職種: {len(severe_shortage)}職種 (2時間/日以上の不足)") if len(severe_shortage) > 0 else None,
                            html.Li(f"完全未配置職種: {len(zero_allocation)}職種 (スタッフ0名だがNeed有り)") if len(zero_allocation) > 0 else None
                        ])
                    ], style={
                        'backgroundColor': '#ffebee',
                        'padding': '15px',
                        'border-left': '4px solid #f44336',
                        'marginBottom': '20px'
                    }))
            
            # データテーブル表示
            content.append(dash_table.DataTable(
                id='proportional-abolition-table',
                data=df_proportional_role.to_dict('records'),
                columns=[
                    {'name': '職種', 'id': '職種', 'type': 'text'},
                    {'name': 'Need時間/日', 'id': 'Need時間/日', 'type': 'numeric', 'format': {'specifier': '.1f'}},
                    {'name': '実配置時間/日', 'id': '実配置時間/日', 'type': 'numeric', 'format': {'specifier': '.1f'}},
                    {'name': '過不足時間/日', 'id': '過不足時間/日', 'type': 'numeric', 'format': {'specifier': '+.1f'}},
                    {'name': '現在スタッフ数', 'id': '現在スタッフ数', 'type': 'numeric'},
                    {'name': '状態', 'id': '状態', 'type': 'text'}
                ],
                style_cell={
                    'textAlign': 'center',
                    'padding': '12px',
                    'fontFamily': 'Arial, sans-serif'
                },
                style_header={
                    'backgroundColor': '#1976d2',
                    'color': 'white',
                    'fontWeight': 'bold'
                },
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{状態} = SHORTAGE'},
                        'backgroundColor': '#ffebee',
                        'color': 'black'
                    },
                    {
                        'if': {'filter_query': '{状態} = SURPLUS'}, 
                        'backgroundColor': '#e8f5e8',
                        'color': 'black'
                    },
                    {
                        'if': {'filter_query': '{現在スタッフ数} = 0 && {過不足時間/日} > 0'},
                        'backgroundColor': '#ffcdd2',
                        'color': '#d32f2f',
                        'fontWeight': 'bold'
                    }
                ],
                sort_action="native",
                style_table={'marginBottom': '30px'}
            ))
            
            # 📈 按分廃止の効果説明
            content.append(html.Div([
                html.H4("📈 按分廃止分析の効果"),
                html.Div([
                    html.Div([
                        html.H5("🔴 按分廃止方式の結果:", style={'color': '#f44336'}),
                        html.P("各職種の真の過不足を露呈し、隠れていた問題を可視化")
                    ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px', 'verticalAlign': 'top'}),
                    
                    html.Div([
                        html.H5("⚪ 従来の按分方式の問題:", style={'color': '#666'}),
                        html.P("組織全体では均衡に見えるが、個別職種の深刻な不均衡が隠蔽される")
                    ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px', 'verticalAlign': 'top'})
                ])
            ], style={
                'backgroundColor': '#f8f9fa',
                'padding': '20px',
                'border-left': '4px solid #007bff',
                'marginBottom': '30px'
            }))
            
            # 改善アクションプラン
            if len(shortage_roles) > 0:
                content.append(html.H4("🎯 改善アクションプラン"))
                
                action_items = []
                for _, role_row in shortage_roles.head(5).iterrows():  # 上位5職種
                    if role_row['現在スタッフ数'] == 0:
                        priority = "緊急"
                        action = f"【{priority}】{role_row['職種']}の専門スタッフを至急採用"
                        color = "#f44336"
                    elif role_row['過不足時間/日'] > 5.0:
                        priority = "高"
                        needed_staff = role_row['過不足時間/日'] / 4.0  # 1人4時間/日と仮定
                        action = f"【{priority}】{role_row['職種']}を約{needed_staff:.1f}名増員"
                        color = "#ff9800"
                    elif role_row['過不足時間/日'] > 2.0:
                        priority = "中"
                        action = f"【{priority}】{role_row['職種']}の勤務時間を{role_row['過不足時間/日']:.1f}時間/日増加"
                        color = "#ffc107"
                    else:
                        priority = "低"
                        action = f"【{priority}】{role_row['職種']}の配置微調整 (+{role_row['過不足時間/日']:.1f}時間/日)"
                        color = "#4caf50"
                    
                    action_items.append(html.Li(action, style={'color': color, 'marginBottom': '8px'}))
                
                content.append(html.Ol(action_items, style={'fontSize': '16px'}))
        
        else:
            content.append(html.P("職種別データが読み込まれていません。", style={'color': '#f44336'}))
        
        return html.Div(content)
        
    except Exception as e:
        log.error(f"按分廃止タブ作成エラー: {e}")
        import traceback
        log.error(f"詳細エラー: {traceback.format_exc()}")
        return html.Div([
            html.H3("🎯 按分廃止・職種別分析"),
            html.P(f"エラーが発生しました: {str(e)}", style={'color': 'red'}),
            html.P("データが正しく読み込まれているか確認してください。", style={'color': '#666'})
        ])
'''
    
    # 2. タブ定義への追加
    tab_definition_code = '''
# create_main_ui_tabs()関数内のタブ定義に以下を追加:

dcc.Tab(label='🎯 按分廃止分析', value='proportional_abolition'),
'''
    
    # 3. タブコンテナ追加
    tab_container_code = '''
# create_main_ui_tabs()関数内のタブコンテナ部分に以下を追加:

html.Div(id='proportional-abolition-tab-container',
         style={'display': 'none'},
         children=[
             dcc.Loading(
                 id="loading-proportional-abolition",
                 type="circle", 
                 children=html.Div(id='proportional-abolition-content')
             )
         ]),
'''
    
    # 4. コールバック更新
    callback_update_code = '''
# update_tab_visibility関数のOutput部分に以下を追加:
Output('proportional-abolition-tab-container', 'style'),

# update_tab_visibility関数の戻り値に以下を追加:
{'display': 'block'} if active_tab == 'proportional_abolition' and selected_scenario and data_status else {'display': 'none'},
'''
    
    # 5. 按分廃止コンテンツ初期化コールバック
    content_callback_code = '''
# 按分廃止タブ用の新しいコールバック関数を追加:

@app.callback(
    Output('proportional-abolition-content', 'children'),
    [Input('proportional-abolition-tab-container', 'style'),
     Input('scenario-dropdown', 'value')],
    State('data-loaded', 'data'),
)
@safe_callback
def initialize_proportional_abolition_content(style, selected_scenario, data_status):
    """按分廃止分析タブの内容を初期化"""
    log.info(f"[proportional_abolition_tab] 初期化開始 - scenario: {selected_scenario}, data_status: {data_status}, style: {style}")
    
    if not selected_scenario or not data_status or style.get('display') == 'none':
        log.info("[proportional_abolition_tab] PreventUpdate - 条件不満足")
        raise PreventUpdate
    try:
        log.info("[proportional_abolition_tab] create_proportional_abolition_tab呼び出し開始")
        result = create_proportional_abolition_tab(selected_scenario)
        log.info("[proportional_abolition_tab] create_proportional_abolition_tab完了")
        return result
    except Exception as e:
        log.error(f"按分廃止分析タブの初期化エラー: {str(e)}")
        import traceback
        log.error(f"按分廃止分析タブ詳細エラー: {traceback.format_exc()}")
        return html.Div(f"エラーが発生しました: {str(e)}", style={'color': 'red'})
'''
    
    return {
        'tab_function': tab_function_code,
        'tab_definition': tab_definition_code,
        'tab_container': tab_container_code,
        'callback_update': callback_update_code,
        'content_callback': content_callback_code
    }

def create_dash_app_integration_patch():
    """dash_app.py統合パッチファイル作成"""
    
    print('\n【Phase 1: 按分廃止タブコード生成】')
    code_components = generate_proportional_abolition_tab_code()
    
    print('\n【Phase 2: 統合パッチファイル作成】')
    
    patch_content = f'''#!/usr/bin/env python3
"""
dash_app.py 按分廃止タブ統合パッチ
Step 2: 按分廃止・職種別分析タブの追加

使用方法:
1. このファイルの内容を確認
2. dash_app.pyに手動で追加、または
3. 自動パッチスクリプトを実行
"""

# ================================================================================
# 1. create_proportional_abolition_tab関数をdash_app.pyに追加
# ================================================================================
{code_components['tab_function']}

# ================================================================================
# 2. create_main_ui_tabs()のタブ定義に追加
# ================================================================================
{code_components['tab_definition']}

# ================================================================================
# 3. create_main_ui_tabs()のタブコンテナに追加  
# ================================================================================
{code_components['tab_container']}

# ================================================================================
# 4. update_tab_visibility関数の更新
# ================================================================================
{code_components['callback_update']}

# ================================================================================
# 5. 按分廃止コンテンツ初期化コールバック追加
# ================================================================================
{code_components['content_callback']}

# ================================================================================
# 実装手順
# ================================================================================
"""
Step 1: dash_app.pyを開く

Step 2: create_shortage_tab関数の後に、create_proportional_abolition_tab関数を追加

Step 3: create_main_ui_tabs()関数内で:
   - タブ定義部分（dcc.Tabs children）に按分廃止タブを追加
   - タブコンテナ部分に按分廃止コンテナを追加

Step 4: update_tab_visibility関数を更新:
   - Output部分に按分廃止タブのstyleを追加
   - 戻り値に按分廃止タブの表示制御を追加

Step 5: 按分廃止コンテンツ初期化コールバックを追加

Step 6: dash_app.pyの動作確認
"""
'''
    
    # パッチファイル保存
    patch_file = f'dash_app_proportional_abolition_patch_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
    with open(patch_file, 'w', encoding='utf-8') as f:
        f.write(patch_content)
    
    print(f'統合パッチファイル作成: {patch_file}')
    
    return {
        'patch_file': patch_file,
        'code_components': code_components
    }

def analyze_dash_app_integration_points():
    """dash_app.pyの統合ポイント分析"""
    
    print('\n【Phase 3: dash_app.py統合ポイント分析】')
    
    try:
        # dash_app.pyの構造確認
        dash_app_path = Path('dash_app.py')
        if not dash_app_path.exists():
            print(f'[WARNING] dash_app.py が見つかりません: {dash_app_path}')
            return {'analysis_success': False, 'error': 'dash_app.py not found'}
        
        with open(dash_app_path, 'r', encoding='utf-8') as f:
            dash_app_content = f.read()
        
        # 主要な統合ポイントの確認
        integration_points = {
            'create_shortage_tab_function': 'def create_shortage_tab(' in dash_app_content,
            'create_main_ui_tabs_function': 'def create_main_ui_tabs(' in dash_app_content,
            'update_tab_visibility_function': 'def update_tab_visibility(' in dash_app_content,
            'shortage_tab_definition': "value='shortage'" in dash_app_content,
            'tab_container_pattern': "html.Div(id='shortage-tab-container'" in dash_app_content,
            'data_get_function': 'def data_get(' in dash_app_content or 'data_get(' in dash_app_content
        }
        
        print('統合ポイント分析結果:')
        for point, found in integration_points.items():
            status = '[OK]' if found else '[MISSING]'
            print(f'  {status} {point}: {found}')
        
        # 既存のタブ数計算
        tab_count = dash_app_content.count("dcc.Tab(label=")
        container_count = dash_app_content.count("-tab-container")
        
        print(f'\n既存構造分析:')
        print(f'  既存タブ数: {tab_count}個')
        print(f'  既存コンテナ数: {container_count}個')
        
        # 推奨挿入位置の特定
        insertion_points = {}
        
        # create_shortage_tab関数の後の位置
        shortage_tab_match = re.search(r'def create_shortage_tab.*?(?=\ndef|\nclass|\n@app\.callback|\Z)', 
                                     dash_app_content, re.DOTALL)
        if shortage_tab_match:
            insertion_points['function_insertion'] = shortage_tab_match.end()
        
        # タブ定義部分
        tab_definition_match = re.search(r"dcc\.Tab\(label='⚠️ 不足分析', value='shortage'\)", dash_app_content)
        if tab_definition_match:
            insertion_points['tab_definition_insertion'] = tab_definition_match.end()
        
        success_rate = sum(integration_points.values()) / len(integration_points) * 100
        
        return {
            'analysis_success': True,
            'integration_points': integration_points,
            'success_rate': success_rate,
            'existing_tabs': tab_count,
            'existing_containers': container_count,
            'insertion_points': insertion_points,
            'file_size': len(dash_app_content)
        }
        
    except Exception as e:
        print(f'[ERROR] dash_app.py分析失敗: {e}')
        return {'analysis_success': False, 'error': str(e)}

def execute_step2_dash_app_integration():
    """Step 2: dash_app.py按分廃止タブ統合実行"""
    
    print('=' * 80)
    print('Step 2: dash_app.py按分廃止タブ統合実行')
    print('按分廃止・職種別分析タブをdash_app.pyに追加')
    print('=' * 80)
    
    try:
        # 1. 按分廃止タブコード生成
        code_result = generate_proportional_abolition_tab_code()
        
        # 2. 統合パッチファイル作成
        patch_result = create_dash_app_integration_patch()
        
        # 3. dash_app.py統合ポイント分析
        analysis_result = analyze_dash_app_integration_points()
        
        # 4. 結果統合
        step2_results = {
            'step2_success': True,
            'code_generation': {
                'success': True,
                'components_generated': len(code_result),
                'tab_function_ready': True,
                'callbacks_ready': True
            },
            'patch_creation': {
                'success': True,
                'patch_file': patch_result['patch_file'],
                'ready_for_integration': True
            },
            'dash_app_analysis': analysis_result,
            'execution_timestamp': datetime.now().isoformat()
        }
        
        # 5. 成功判定
        if analysis_result.get('success_rate', 0) >= 80:
            print('\n' + '=' * 80)
            print('[SUCCESS] Step 2: dash_app.py按分廃止タブ統合準備完了!')
            print('按分廃止タブのコード生成とパッチファイル作成が完了しました')
            print('=' * 80)
            
            print(f'\n📊 統合準備状況:')
            print(f'   dash_app.py統合成功率: {analysis_result.get("success_rate", 0):.1f}%')
            print(f'   既存タブ数: {analysis_result.get("existing_tabs", 0)}個')
            print(f'   コード生成: 完了 ({len(code_result)}コンポーネント)')
            
            print(f'\n📁 生成ファイル:')
            print(f'   統合パッチファイル: {patch_result["patch_file"]}')
            
            print(f'\n🎯 次のステップ (手動統合):')
            print('1. 生成されたパッチファイルを確認')
            print('2. dash_app.pyに按分廃止タブ機能を追加')
            print('3. 動作確認 (ZIPアップロード → 按分廃止タブ確認)')
            
            return step2_results
        else:
            print(f'\n[WARNING] dash_app.py統合準備に問題があります')
            print(f'統合成功率: {analysis_result.get("success_rate", 0):.1f}%')
            return step2_results
            
    except Exception as e:
        print(f'[ERROR] Step 2実行失敗: {e}')
        import traceback
        traceback.print_exc()
        return {'step2_success': False, 'error': str(e)}

if __name__ == "__main__":
    result = execute_step2_dash_app_integration()
    
    if result and result.get('step2_success', False):
        print('\n🚀 Step 2完了 - Step 3の動作確認に進むことができます')
    else:
        print('\nStep 2でエラーが発生しました。問題を解決してから次のステップに進んでください。')