# Copyright (c) 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
class ProductNode:
    def __init__(self, attrs):
        self.title        = attrs.get("title", "")
        self.asin         = attrs.get("asin", "")
        self.depth        = attrs.get("depth", -1)
        self.child        = {k: [ProductNode(i) for i in v] for k, v in attrs.get("child", {}).items()}
        self.description  = attrs.get("description", "")
        self.sections     = attrs.get("sections", "")      # section name -> list of citation papers
        self.source       = attrs.get("source", "Root")    # Root, Search, Expand
        self.select_score = attrs.get("select_score", 0.0) # the result of the selected model
        self.extra        = attrs.get("extra", {})

    def todic(self):
        return {
            "title":        self.title,
            "asin":         self.asin,
            "depth":        self.depth,
            "child":        {k: [i.todic() for i in v] for k, v in self.child.items()},
            "description":  self.description,
            "sections":     self.sections,
            "source":       self.source,
            "select_score": self.select_score,
            "extra":        self.extra,
        }

    @staticmethod
    def sort_paper(item):
        return item.select_score