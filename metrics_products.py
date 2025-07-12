#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import glob
import argparse
from utils import cal_micro

def load_product_gt(gt_path):
    gt = {}
    with open(gt_path, 'r', encoding='utf-8') as f:
        for line in f:
            ex = json.loads(line)
            gt[ex['qid']] = set(ex.get('answer_asin', []))
    return gt

def extract_asins_from_tree(tree):
    asins = []
    queue = [tree]
    while queue:
        node = queue.pop(0)
        if 'asin' in node:
            asins.append(node['asin'])
        for child_list in node.get('child', {}).values():
            queue.extend(child_list)
    return asins

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Precisión and recall in product searches with PaSa"
    )
    parser.add_argument(
        '--pred_folder', type=str, default='product_results',
        help='Folder containing PaSa prediction JSON files for products'
    )
    parser.add_argument(
        '--gt_file', type=str, default='products_ground_truth.jsonl',
        help='JSONL file with ground truth ASINs per query'
    )
    args = parser.parse_args()
    gt = load_product_gt(args.gt_file)
    precisions, recalls = [], []
    recalls_20, recalls_50, recalls_100 = [], [], []
    pred_files = glob.glob(os.path.join(args.pred_folder, '*.json'))
    for pred_file in pred_files:
        qid = os.path.splitext(os.path.basename(pred_file))[0]
        tree = json.load(open(pred_file, encoding='utf-8'))
        pred_asins = extract_asins_from_tree(tree)
        set_all   = set(pred_asins)
        set_20    = set(pred_asins[:20])
        set_50    = set(pred_asins[:50])
        set_100   = set(pred_asins[:100])
        gt_set = gt.get(qid, set())

        tp, fp, fn = cal_micro(set_all, gt_set)
        precision  = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall     = tp / (tp + fn) if (tp + fn) > 0 else 0

        tp20, fp20, fn20 = cal_micro(set_20, gt_set)
        tp50, fp50, fn50 = cal_micro(set_50, gt_set)
        tp100, fp100, fn100 = cal_micro(set_100, gt_set)

        recall20  = tp20  / (tp20  + fn20)  if (tp20  + fn20)  > 0 else 0
        recall50  = tp50  / (tp50  + fn50)  if (tp50  + fn50)  > 0 else 0
        recall100 = tp100 / (tp100 + fn100) if (tp100 + fn100) > 0 else 0

        precisions.append(precision)
        recalls.append(recall)
        recalls_20.append(recall20)
        recalls_50.append(recall50)
        recalls_100.append(recall100)

    print("Precision avg   : {:.4f}".format(sum(precisions)   / len(precisions)))
    print("Recall avg      : {:.4f}".format(sum(recalls)      / len(recalls)))
    print("Recall@20 avg   : {:.4f}".format(sum(recalls_20)   / len(recalls_20)))
    print("Recall@50 avg   : {:.4f}".format(sum(recalls_50)   / len(recalls_50)))
    print("Recall@100 avg  : {:.4f}".format(sum(recalls_100)  / len(recalls_100)))

