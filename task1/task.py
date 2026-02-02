from typing import List, Tuple

def main(s: str, e: str) -> Tuple[
    List[List[bool]],
    List[List[bool]],
    List[List[bool]],
    List[List[bool]],
    List[List[bool]]
]:
    edges = [tuple(map(int, line.split(','))) for line in s.strip().split('\n') if line.strip()]
    nodes = sorted({x for uv in edges for x in uv})
    node_idx = {node: i for i, node in enumerate(nodes)}
    n = len(nodes)

    children = [[] for _ in range(n)]
    for u, v in edges:
        children[node_idx[u]].append(node_idx[v])

    r1 = [[False] * n for _ in range(n)]
    for u, v in edges:
        r1[node_idx[u]][node_idx[v]] = True

    r3 = [[False] * n for _ in range(n)]
    def dfs_desc(u: int, orig: int):
        for v in children[u]:
            r3[orig][v] = True
            dfs_desc(v, orig)
    for i in range(n):
        dfs_desc(i, i)

    r4 = [[False] * n for _ in range(n)]
    parents = [[] for _ in range(n)]
    for u, v in edges:
        parents[node_idx[v]].append(node_idx[u])

    def dfs_anc(u: int, orig: int):
        for p in parents[u]:
            r4[orig][p] = True
            dfs_anc(p, orig)
    for i in range(n):
        dfs_anc(i, i)

    r2 = [[False] * n for _ in range(n)]
    for u, v in edges:
        r2[node_idx[v]][node_idx[u]] = True

    r5 = [[i == j for j in range(n)] for i in range(n)]

    return r1, r2, r3, r4, r5


if __name__ == "__main__":
    csv_str = "1,2\n1,3\n3,4\n3,5\n5,6\n6,7"
    root = "1"
    mats = main(csv_str, root)

    for k, m in enumerate(mats, 1):
        print(f"Matrix {k}:")
        for row in m:
            print(row)
        print("---------------\n")
