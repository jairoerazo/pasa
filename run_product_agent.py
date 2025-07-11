import os
import json
import argparse
from models      import Agent
from product_agent import ProductAgent

parser = argparse.ArgumentParser()
parser.add_argument('--input_file',        type=str, default="data/RealProductQuery/test.jsonl")
parser.add_argument('--crawler_path',      type=str, default="checkpoints/pasa-7b-crawler")
parser.add_argument('--selector_path',     type=str, default="checkpoints/pasa-7b-selector")
parser.add_argument('--output_folder',     type=str, default="results_products")
parser.add_argument('--search_queries',    type=int, default=5)
parser.add_argument('--search_products',   type=int, default=10, help="number of products per query")
parser.add_argument('--threads_num',       type=int, default=20)
args = parser.parse_args()

crawler = Agent(args.crawler_path)
selector = Agent(args.selector_path)

if args.output_folder:
    os.makedirs(args.output_folder, exist_ok=True)

with open(args.input_file) as f:
    for idx, line in enumerate(f):
        data = json.loads(line)
        product_agent = ProductAgent(
            user_query     = data.get('query', data.get('question', '')),
            crawler        = crawler,
            selector       = selector,
            expand_layers  = 0,
            search_queries = args.search_queries,
            search_papers  = args.search_products,
            threads_num    = args.threads_num
        )
        product_agent.run()
        output_path = os.path.join(args.output_folder, f"{idx}.json")
        with open(output_path, 'w') as out_f:
            json.dump(product_agent.root.todic(), out_f, indent=2)