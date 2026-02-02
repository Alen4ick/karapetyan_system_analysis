# -*- coding: utf-8 -*-
import ast
import json


def load_data(raw):
    if isinstance(raw, (dict, list)):
        return raw
    text = str(raw).strip()
    try:
        return json.loads(text)
    except Exception:
        return ast.literal_eval(text)


def canon_term(x):
    if x is None:
        return x
    token = str(x).strip().lower()
    mapping = {
        "нормально": "комфортно",
        "комф": "комфортно",
        "слабо": "слабый",
        "слаб": "слабый",
        "умеренно": "умеренный",
        "умерен": "умеренный",
        "интенсивно": "интенсивный",
        "интенс": "интенсивный",
    }
    return mapping.get(token, token)


def clip01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def interp_membership(x, points):
    if not points:
        return 0.0

    pts = [(float(a), float(b)) for a, b in points]
    pts.sort(key=lambda p: p[0])

    x0, y0 = pts[0]
    xn, yn = pts[-1]

    if x <= x0:
        return clip01(y0)
    if x >= xn:
        return clip01(yn)

    same_x = [y for px, y in pts if px == x]
    if same_x:
        return clip01(max(same_x))

    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if x1 <= x <= x2:
            if x2 == x1:
                return clip01(max(y1, y2))
            frac = (x - x1) / (x2 - x1)
            return clip01(y1 + frac * (y2 - y1))

    return 0.0


def pick_key(d: dict, candidates):
    for k in candidates:
        if k in d:
            return k
    return None


def index_terms(container: dict, var_key: str) -> dict:
    if var_key not in container:
        raise KeyError(f"Нет ключа {var_key!r}. Доступные: {list(container.keys())}")
    res = {}
    for row in container[var_key]:
        term = canon_term(row.get("id"))
        res[term] = row.get("points")
    return res


def main(temp_json, heat_json, rules_json, t_current) -> float:
    temp_obj = load_data(temp_json)
    heat_obj = load_data(heat_json)
    rules = load_data(rules_json)

    temp_key = pick_key(temp_obj, ["температура", "temperature"])
    heat_key = pick_key(heat_obj, ["уровень нагрева", "heat level", "heating level", "heat_level"])

    if temp_key is None:
        raise KeyError(f"Не найден ключ температуры. Доступные: {list(temp_obj.keys())}")
    if heat_key is None:
        raise KeyError(f"Не найден ключ нагрева. Доступные: {list(heat_obj.keys())}")

    temp_terms = index_terms(temp_obj, temp_key)
    heat_terms = index_terms(heat_obj, heat_key)

    t = float(t_current)
    mu_temp = {name: interp_membership(t, pts) for name, pts in temp_terms.items()}

    grid_xs = [float(px) for pts in heat_terms.values() for px, _ in pts]
    if not grid_xs:
        raise ValueError(f"В '{heat_key}' нет points.")

    s_min, s_max = min(grid_xs), max(grid_xs)
    span = s_max - s_min
    if span == 0:
        return float(s_min)

    n = 10000
    step = span / n
    agg = [0.0] * (n + 1)

    for rule in rules:
        ant = canon_term(rule[0])
        cons = canon_term(rule[1])
        alpha = float(mu_temp.get(ant, 0.0))
        if alpha <= 0.0:
            continue

        if cons not in heat_terms:
            raise KeyError(f"Нет терма {cons!r} в '{heat_key}'. Доступно: {list(heat_terms.keys())}")

        cons_pts = heat_terms[cons]
        for i in range(n + 1):
            s = s_min + step * i
            mu_cons = interp_membership(s, cons_pts)
            mu_rule = alpha if alpha < mu_cons else mu_cons
            if mu_rule > agg[i]:
                agg[i] = mu_rule

    max_mu = max(agg) if agg else 0.0
    eps = 1e-12
    for i, v in enumerate(agg):
        if v >= max_mu - eps:
            return float(s_min + step * i)

    return float(s_min)


if __name__ == "__main__":
    TEMP = {
        "температура": [
            {"id": "холодно", "points": [[0, 1], [18, 1], [22, 0], [50, 0]]},
            {"id": "комфортно", "points": [[18, 0], [22, 1], [24, 1], [26, 0]]},
            {"id": "жарко", "points": [[0, 0], [24, 0], [26, 1], [50, 1]]},
        ]
    }

    HEAT = {
        "heat level": [
            {"id": "слабый", "points": [[0, 0], [0, 1], [5, 1], [8, 0]]},
            {"id": "умеренный", "points": [[5, 0], [8, 1], [13, 1], [16, 0]]},
            {"id": "интенсивный", "points": [[13, 0], [18, 1], [23, 1], [26, 0]]},
        ]
    }

    rules = "[['холодно','интенсивно'],['нормально','умеренно'],['жарко','слабо']]"
    print(main(TEMP, HEAT, rules, 19.0))
