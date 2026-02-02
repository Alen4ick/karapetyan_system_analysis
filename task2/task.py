from typing import Tuple
import math

def main(s: str, e: str) -> Tuple[float, float]:
    edges = [tuple(map(int, line.split(','))) for line in s.strip().split('\n') if line.strip()]
    nodes = sorted({x for uv in edges for x in uv})
    node_idx = {node: i for i, node in enumerate(nodes)}
    n = len(nodes)

    r1 = [[False] * n for _ in range(n)]
    for u, v in edges:
        r1[node_idx[u]][node_idx[v]] = True

    rel = 0
    for i in range(n):
        for j in range(n):
            if r1[i][j]:
                rel += 1

    if rel == 0 or n == 0:
        return 0.0, 0.0

    p = 1.0 / rel
    H = -rel * (p * math.log2(p))
    Hmax = math.log2(n * n) if n > 0 else 0.0
    K = H / Hmax if Hmax != 0 else 0.0

    return round(H, 1), round(K, 1)


if __name__ == "__main__":
    csv_str = "1,2\n1,3\n3,4\n3,5\n5,6\n6,7"
    root = "1"
    print("TEST\n")
    print(main(csv_str, root))
