#!/bin/env python3
from __future__ import annotations
import pandas as pd
import html
import pathlib
from typing import Set, Dict, TextIO
import json
from pypinyin import pinyin, lazy_pinyin, Style


# Sample DataFrame with HTML entities
df = pd.concat(map(pd.read_excel, pathlib.Path("input").glob("*.xls")))
cols_to_unescape = ["题目类型", "题干", "选项", "答案"]
df[cols_to_unescape] = df[cols_to_unescape].map(html.unescape, "ignore")


df.reset_index(drop=True, inplace=True)


class TrieNode:
    count: int
    is_end_of_word: bool
    children: Dict[str, TrieNode]
    content: dict
    prob_index: int
    node_id: int

    def __init__(self, node_id):
        self.children = {}
        self.count = 0
        self.is_end_of_word = False
        self.content = {}
        self.prob_index = -1
        self.node_id = node_id


class Trie:

    def __init__(self):
        self.root = TrieNode(0)
        self.node_count = 1

    def insert(self, word, prob_index):
        node = self.root
        node.count += 1
        for char in word:
            # If the character is not already a child, add it
            if char not in node.children:
                node.children[char] = TrieNode(self.node_count)
                self.node_count += 1
            node = node.children[char]
            node.count += 1
        # Mark the end of a word
        node.is_end_of_word = True
        node.prob_index = prob_index

    def search(self, word):
        node = self.root
        for char in word:
            # If the character isn't found, the word doesn't exist
            if char not in node.children:
                return False
            node = node.children[char]
        # Return True only if it's the end of a valid word
        return node.is_end_of_word

    def starts_with(self, prefix):
        node = self.root
        for char in prefix:
            # If the character isn't found, the prefix doesn't exist
            if char not in node.children:
                return False
            node = node.children[char]
        return True


probs = df["题干"].to_dict()
h = Trie()
for u, v in probs.items():
    h.insert("".join(filter(str.isalnum, v)), u)


def format_prob(index: int):
    s = {}
    s["题干"] = df.loc[index, "题干"]
    if pd.notna(df.loc[index, "选项"]):
        s["选项"] = df.loc[index, "选项"]
    if pd.notna(df.loc[index, "答案"]):
        s["答案"] = df.loc[index, "答案"]
    return s


def Dfs(prefix: str, x: TrieNode) -> int:
    if x.is_end_of_word:
        x.content["prob"] = format_prob(x.prob_index)
    elif len(x.children) == 1:  # 由儿子全权代表
        for u, v in x.children.items():
            return Dfs(prefix + u, v)
    sons = []
    for u, v in x.children.items():
        sons += [Dfs(prefix + u, v)]
    x.content["prefix"] = f"{prefix if prefix else "起始索引"}: \n"
    if sons:
        x.content["sons"] = sons
    x.content["node_id"] = x.node_id
    return prefix, x.node_id


Dfs("", h.root)


def Dfs2(x: TrieNode) -> dict:
    if x.content:
        entries.append(x.content)
    for v in x.children.values():
        Dfs2(v)


entries = []
Dfs2(h.root)


e0s = []
for son in sorted(
    entries[0]["sons"],
    key=lambda y: (lambda x: x if x.isascii() else pinyin(x, style=Style.TONE3)[0][0])(
        y[0][0]
    ),
):
    son = list(son)
    if not son[0][0].isascii():
        son[0] = f"{pinyin(son[0][0])[0][0]}-{son[0]}"
    e0s.append(son)
entries[0]["sons"] = e0s
with open("data.json", "w") as f:
    json.dump(
        entries,
        f,
        ensure_ascii=False,
        indent=4,
    )
