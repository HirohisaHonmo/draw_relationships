import csv
import tkinter
from tkinter import filedialog

import matplotlib.font_manager as font_manager
import matplotlib.pyplot as pyplot
import networkx

CUSTOM_BLUE = "#6c9cd4"
CUSTOM_GREEN = "#008803"

COLOR_FOR_SUSPICIOUS_NODE = "red"
COLOR_FOR_UG = "lightblue"
COLOR_FOR_NT_CC = "lightgreen"
COLOR_FOR_OTHERS = "lightpink"

FONT_PATH = "C:\\Windows\\Fonts\\YuGothM.ttc"
font_prop = font_manager.FontProperties(fname=FONT_PATH)
pyplot.rcParams["font.family"] = font_prop.get_name()


def read_relationships_from_csv(file_path):
    """
    指定されたCSVファイルから関係性を読み込む。

    CSVファイルは次のようなフォーマットであると仮定します。
    - 最初の行はヘッダーであり、読み飛ばされます。
    - それ以降の各行は、"親ノード, 子ノード"の形式で関係性を表しています。

    例：
    usergroup, subgroup
    UG-1, SG-1
    UG-1, SG-2
    UG-2, SG-3
    ...

    Parameters:
        file_path (str): CSVファイルのパス

    Returns:
        dict: 読み込んだ関係性を格納した辞書。
              キーは「親ノード」、値は「子ノード」のリストです。
    """
    relationships = {}

    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)

        for row in reader:
            user_group, sub_group = row
            relationships.setdefault(user_group, []).append(sub_group)

    return relationships


def add_edges_to_graph_from_relationships(user_groups_graph, relationships):
    """
    与えられた関係性の辞書からグラフにエッジ(辺)を追加します。

    この関数は既存の有向グラフ(DiGraph)オブジェクトに対して、
    関係性の辞書に基づいてエッジを追加します。
    関係性の辞書は、親ノードをキーとし、子ノードのリストを値として持っています。

    例：
    relationships = {
        'UG-1': ['SG-1', 'SG-2'],
        'UG-2': ['SG-3'],
        ...
    }

    Parameters:
        user_groups_graph (networkx.DiGraph): エッジを追加する対象の有向グラフ
        relationships (dict): 親ノードをキー、子ノードのリストを値とした関係性の辞書

    Returns:
        None: user_groups_graph は関数内で直接更新されます。
    """
    for user_group, sub_groups in relationships.items():
        for sub_group in sub_groups:
            user_groups_graph.add_edge(user_group, sub_group)


def get_root_nodes(user_groups_graph):
    """
    有向グラフ(user_groups_graph)からルートノード(入次数が0のノード)を探し、そのリストを返します。

    この関数では、有向グラフ(user_groups_graph)の各ノードに対して、入次数(他のノードからの入力エッジの数)を調べます。
    入次数が0であるノードはルートノードとして扱われ、そのリストが結果として返されます。

    Parameters:
        user_groups_graph (networkx.DiGraph): ルートノードを検索する対象の有向グラフ

    Returns:
        list: ルートノードのリスト
    """
    root_nodes = []

    ZERO_INDEGREE = 0
    for node, indegree in user_groups_graph.in_degree():
        if indegree == ZERO_INDEGREE:
            root_nodes.append(node)

    return root_nodes


def set_x_axis_recursively_from_roots(user_groups_graph, root_nodes):
    """
    与えられた有向グラフ(user_groups_graph)とルートノード(root_nodes)に基づいて、
    各ノードの x 座標を再帰的に設定します。

    この関数では、ルートノードから始まり、その子ノード、孫ノードと続く各ノードに対して、
    x座標を再帰的に割り当てます。座標は辞書形式で格納されます。

    Parameters:
        user_groups_graph (networkx.DiGraph): 座標を設定する対象の有向グラフ
        root_nodes (list): グラフのルートノードのリスト

    Returns:
        dict: 各ノードのx座標を格納した辞書
    """

    def _set_x_axis(graph, node, coordinates, x=0):
        """指定されたノードとその子ノードに再帰的に x 座標を設定します。"""
        coordinates[node] = (x, None)

        for sub_group in graph.successors(node):
            _set_x_axis(graph, sub_group, coordinates, x + 1)

    coordinates = {}

    for root_node in root_nodes:
        _set_x_axis(user_groups_graph, root_node, coordinates)

    return coordinates


def build_layer_info_recursively_from_roots(user_groups_graph, root_nodes):
    """
    与えられた有向グラフ(user_groups_graph)とルートノード(root_nodes)に基づいて、
    各ノードがどの「層(レイヤー)」に属するかの情報を再帰的に生成します。

    Parameters:
    - user_groups_graph: networkx.DiGraph
      ユーザーグループとサブグループの関係を表す有向グラフ
    - root_nodes: list
      有向グラフのルートノード(親がないノード)のリスト

    Returns:
    - layer_nodes: dict
      キーが「層(レイヤー)」のインデックス(0, 1, 2, ...)、
      値がその「層」に属するノードのリストとなる辞書
    """

    def _build_layers(graph, node, layer_nodes, x=0):
        if x not in layer_nodes:
            layer_nodes[x] = set()

        layer_nodes[x].add(node)

        for sub_group in graph.successors(node):
            _build_layers(graph, sub_group, layer_nodes, x + 1)

    layer_nodes = {}

    for root_node in root_nodes:
        _build_layers(user_groups_graph, root_node, layer_nodes)

    for x, nodes in layer_nodes.items():
        layer_nodes[x] = list(nodes)

    return layer_nodes


def set_y_axis(nodes_per_layer, coordinates):
    """
    各ノードのy座標を設定します。各「層(レイヤー)」に属するノードが等間隔で配置されるようにy座標を計算します。

    Parameters:
    - nodes_per_layer: dict
      キーが「層(レイヤー)」のインデックス(0, 1, 2, ...)、
      値がその「層」に属するノードのリストとなる辞書。

    - coordinates: dict
      キーがノード名、値が (x座標, y座標) の形式の座標となる辞書。
      この関数では、この辞書にy座標が設定されます。

    Returns:
    None(引数のcoordinatesが更新されます)
    """
    OFFSET = 0.5
    for x, nodes in nodes_per_layer.items():
        total_nodes = len(nodes)

        for i, node in enumerate(nodes):
            y = i - total_nodes * OFFSET
            coordinates[node] = (x, y)


def set_node_colors(user_groups_graph):
    """
    各ノードに適切な色を割り当てます。具体的には以下の条件に基づいてノードの色を設定します：

    1. ノード名に "UG-" が含まれていないが、その親ノードに "UG-" が含まれる場合: "怪しいノード" として赤色を割り当てます。
    2. ノード名に "UG-" が含まれる場合: "集約UG" として青色を割り当てます。
    3. ノード名に "NT" または "CC" が含まれる場合: 緑色を割り当てます。
    4. 上記のいずれにも該当しない場合: ピンク色を割り当てます。

    各ノードに割り当てられた色は、リスト形式で返されます。
    """
    node_colors = []

    for node in user_groups_graph.nodes():
        if "UG-" not in node and any(
            "UG-" in super_group for super_group in user_groups_graph.predecessors(node)
        ):
            node_colors.append(COLOR_FOR_SUSPICIOUS_NODE)
        elif "UG-" in node:
            node_colors.append(COLOR_FOR_UG)
        elif "NT" in node or "CC" in node:
            node_colors.append(COLOR_FOR_NT_CC)
        else:
            node_colors.append(COLOR_FOR_OTHERS)

    return node_colors


def draw_graph(user_groups_graph, coordinates, node_colors):
    """ユーザーグループの関連性を表す有向グラフを描画します。"""

    def draw_graph_elements(user_groups_graph, coordinates, node_colors):
        """グラフの主要な要素を描画する"""
        networkx.draw(
            user_groups_graph,
            coordinates,
            with_labels=True,
            font_family=font_prop.get_name(),
            node_color=node_colors,
            edge_color="lightgray",
            arrows=True,
            node_shape="o",
        )

    def set_legend():
        """凡例を設定する"""
        pyplot.scatter([], [], c=COLOR_FOR_UG, label="集約UG")
        pyplot.scatter([], [], c=COLOR_FOR_NT_CC, label="NT, CC")
        pyplot.scatter([], [], c=COLOR_FOR_OTHERS, label="その他")
        pyplot.scatter(
            [], [], c=COLOR_FOR_SUSPICIOUS_NODE, label="怪しいノード（集約 UG から接続された「その他」のノード）"
        )
        pyplot.legend()

    def set_caption():
        """補足説明を設定する"""
        x_limit = pyplot.xlim()
        y_limit = pyplot.ylim()
        MARGIN = 0.01
        x_axis_for_text = x_limit[0] + (x_limit[1] - x_limit[0]) * MARGIN
        y_axis_for_text = y_limit[1] - (y_limit[1] - y_limit[0]) * MARGIN

        pyplot.text(
            x_axis_for_text,
            y_axis_for_text,
            "各ノードから見て左側にいるやつが親で、右側がサブグループ",
            fontsize=12,
            ha="left",
            va="top",
        )

    draw_graph_elements(user_groups_graph, coordinates, node_colors)
    set_legend()
    set_caption()
    pyplot.show()


def main():
    """
    主処理を行う関数。
    1. ユーザーが選択したCSVファイルから関連性データを読み込む。
    2. 有向グラフを生成し、エッジを追加する。
    3. グラフの座標を設定する。
    4. ノードの色を設定する。
    5. グラフを描画する。

    処理の流れ:
    - ファイルダイアログでCSVファイルを選択。
    - CSVから関連性データを読み込む。
    - 有向グラフ(user_groups_graph)を作成し、エッジを追加。
    - 根ノード(ルートノード)を取得。
    - x軸、y軸の座標を設定。
    - ノードの色を設定。
    - グラフを描画。
    """
    file_path = filedialog.askopenfilename(
        title="CSV を選んでください。", filetypes=[("CSV files", "*.csv")]
    )

    if not file_path:
        return

    relationships = read_relationships_from_csv(file_path)

    user_groups_graph = networkx.DiGraph()
    add_edges_to_graph_from_relationships(user_groups_graph, relationships)

    root_nodes = get_root_nodes(user_groups_graph)

    coordinates = set_x_axis_recursively_from_roots(user_groups_graph, root_nodes)
    nodes_per_layer = build_layer_info_recursively_from_roots(
        user_groups_graph, root_nodes
    )
    set_y_axis(nodes_per_layer, coordinates)

    node_colors = set_node_colors(user_groups_graph)

    draw_graph(user_groups_graph, coordinates, node_colors)


# GUI の設定
root = tkinter.Tk()
root.title("関連図を描画します。")
button = tkinter.Button(
    root,
    text="CSV を選んで関連図を描画します。",
    width=50,
    height=10,
    command=main,
    fg="white",
    bg=CUSTOM_BLUE,
    activeforeground="white",
    activebackground=CUSTOM_GREEN,
)
button.pack(padx=100, pady=100)

root.mainloop()
