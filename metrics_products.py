#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import glob
import argparse

def load_product_gt(gt_path):
    """
    Carga el ground-truth desde un JSONL con campos 'qid' y 'answer_asin'.
    Devuelve un dict qid -> set(asin).
    """
    gt = {}
    with open(gt_path, 'r', encoding='utf-8') as f:
        for line in f:
            ex = json.loads(line)
            gt[ex['qid']] = set(ex.get('answer_asin', []))
    return gt

def traverse_tree(tree, threshold=0.5):
    """
    Recorre recursivamente el árbol de PaSa extrayendo:
      - crawled_set: todos los ASINs vistos
      - crawled_list: lista de (asin, select_score)
      - selected_set: ASINs con select_score > threshold
    """
    crawled_set   = set()
    crawled_list  = []
    selected_set  = set()

    def _rec(node):
        asin  = node.get('asin')
        score = node.get('select_score', 0.0)
        # Si tiene ASIN, lo contamos
        if asin:
            if asin not in crawled_set:
                crawled_set.add(asin)
                crawled_list.append((asin, score))
            if score > threshold:
                selected_set.add(asin)
        # Recorremos hijos
        for child_list in node.get('child', {}).values():
            for ch in child_list:
                _rec(ch)

    _rec(tree)
    return crawled_set, crawled_list, selected_set

def precision_recall(tp, fp, fn):
    p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    return p, r

if __name__ == '__main__':
    p = argparse.ArgumentParser(
        description="Evalúa métricas de PaSa en búsquedas de productos"
    )
    p.add_argument('--pred_folder', type=str,
                   default='results/results_products_3',
                   help='Carpeta con JSON de predicción')
    p.add_argument('--gt_file', type=str,
                   default='data/RealProductQuery/test.jsonl',
                   help='JSONL con ground-truth de ASINs')
    args = p.parse_args()

    # 1) Cargar ground-truth
    gt = load_product_gt(args.gt_file)

    # 2) Inicializar acumuladores
    crawler_recalls = []
    precisions      = []
    recalls         = []
    recall20_list   = []
    recall50_list   = []
    recall100_list  = []

    # 3) Para cada archivo de predicción...
    pred_files = glob.glob(os.path.join(args.pred_folder, '*.json'))
    for path in pred_files:
        qid = os.path.splitext(os.path.basename(path))[0]
        tree = json.load(open(path, encoding='utf-8'))

        # Extraer sets y lista ordenada
        crawled_set, crawled_list, selected_set = traverse_tree(tree, threshold=0.5)

        # Sort by score descending
        crawled_list.sort(key=lambda x: x[1], reverse=True)
        top20  = set([asin for asin,_ in crawled_list[:20]])
        top50  = set([asin for asin,_ in crawled_list[:50]])
        top100 = set([asin for asin,_ in crawled_list[:100]])

        # Ground-truth para este QID
        truth = gt.get(qid, set())

        # -- Crawler Recall (recall de todo lo crawleado)
        tp_c = len(crawled_set & truth)
        fn_c = len(truth - crawled_set)
        _, r_c = precision_recall(tp_c, 0, fn_c)
        crawler_recalls.append(r_c)

        # -- Selected Precision & Recall
        tp_s = len(selected_set & truth)
        fp_s = len(selected_set - truth)
        fn_s = len(truth - selected_set)
        p_s, r_s = precision_recall(tp_s, fp_s, fn_s)
        precisions.append(p_s)
        recalls.append(r_s)

        # -- Recall@K
        for (container, lst) in [(recall20_list, top20),
                                 (recall50_list, top50),
                                 (recall100_list, top100)]:
            tp_k = len(lst & truth)
            fn_k = len(truth - lst)
            _, r_k = precision_recall(tp_k, 0, fn_k)
            container.append(r_k)

    # 4) Imprimir promedios
    N = len(crawler_recalls)
    print(f"Crawler Recall avg : {sum(crawler_recalls)/N:.4f}")
    print(f"Precision avg      : {sum(precisions)     /N:.4f}")
    print(f"Recall avg         : {sum(recalls)        /N:.4f}")
    print(f"Recall@20 avg      : {sum(recall20_list)  /N:.4f}")
    print(f"Recall@50 avg      : {sum(recall50_list)  /N:.4f}")
    print(f"Recall@100 avg     : {sum(recall100_list) /N:.4f}")
