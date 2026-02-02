from typing import List, Dict, Tuple
import json

def parse_ranking(js: str) -> List[List[str]]:
    data = json.loads(js)
    return data

def build_pos_maps(ranking: List[List[str]]) -> Tuple[Dict[str, int], Dict[str, int]]:
    cluster_pos: Dict[str, int] = {}
    inner_pos: Dict[str, int] = {}
    for ci, cluster in enumerate(ranking):
        for pi, obj in enumerate(cluster):
            cluster_pos[obj] = ci
            inner_pos[obj] = pi
    return cluster_pos, inner_pos

def find_contradictions(rank1: List[List[str]], rank2: List[List[str]]) -> List[Tuple[str, str]]:
    c1, _ = build_pos_maps(rank1)
    c2, _ = build_pos_maps(rank2)
    objs = list(c1.keys())
    res: List[Tuple[str, str]] = []
    for i in range(len(objs)):
        for j in range(i + 1, len(objs)):
            a, b = objs[i], objs[j]
            d1 = c1[a] - c1[b]
            d2 = c2[a] - c2[b]
            if d1 * d2 < 0:
                res.append((a, b))
    return res

def build_clusters_from_contradictions(objs: List[str],
                                       contradictions: List[Tuple[str, str]]) -> List[List[str]]:
    g: Dict[str, set] = {o: set() for o in objs}
    for a, b in contradictions:
        g[a].add(b)
        g[b].add(a)

    visited = set()
    clusters: List[List[str]] = []

    for o in objs:
        if o in visited:
            continue
        stack = [o]
        visited.add(o)
        comp: List[str] = []
        while stack:
            v = stack.pop()
            comp.append(v)
            for u in g[v]:
                if u not in visited:
                    visited.add(u)
                    stack.append(u)
        clusters.append(sorted(comp))
    return clusters

def order_clusters(clusters: List[List[str]], base_rank: List[List[str]]) -> List[List[str]]:
    cpos, _ = build_pos_maps(base_rank)

    def avg_pos(cluster: List[str]) -> float:
        return sum(cpos[o] for o in cluster) / len(cluster)

    return sorted(clusters, key=avg_pos)

def main(json_a: str, json_b: str) -> str:
    rank_a = parse_ranking(json_a)
    rank_b = parse_ranking(json_b)

    contradictions = find_contradictions(rank_a, rank_b)
    objs = sorted({o for cl in rank_a for o in cl})

    clusters = build_clusters_from_contradictions(objs, contradictions)
    ordered = order_clusters(clusters, rank_a)

    return json.dumps(ordered, ensure_ascii=False)


if __name__ == "__main__":
    r1 = json.dumps([["A", "B"], ["C"], ["D"]], ensure_ascii=False)
    r2 = json.dumps([["B"], ["A", "C"], ["D"]], ensure_ascii=False)
    print(main(r1, r2))
