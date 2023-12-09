# ユーザーグループ関連性可視化ツール (User Group Relationship Visualization Tool)

## 概要 (Overview)
このツールは、ユーザーグループ間の関連性を可視化します。関連性データに基づき、有向グラフを生成し分析を容易にします。  
This tool visualizes the relevance between user groups. Based on the relevance data, a directed graph is generated to facilitate analysis.
  
## 依存関係 (Dependencies)
- **Python 3.9.7**
- **NetworkX**
- **Matplotlib**
  
## 使い方 (How to use)
次のようなcsvを用意してください。  
Prepare a csv with the following structure

Parent, Child  
Parent-1, Child-1  
Parent-1, Child-2  
Child-2, GrandChild-1  
...  

set_node_colors 関数でノードの色を設定しているので、設定を変更してください。開発時の設定がそのまま残っています。  
The set_node_colors function sets the color of each node. The settings are still the same as when I was developing.  

プログラムを実行したらcsvファイルを読み込んでください。他に大事なことを言い忘れていなければたぶんグラフが描画されるはずです。  
After you run the program, read the csv file. Unless I forgot to tell you otherwise, the graph will be drawn.# draw_relationships
