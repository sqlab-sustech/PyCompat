from collections import deque

from parso.python.tree import TryStmt, ExprStmt, ImportFrom, Name, ImportName, IfStmt

import jedi


def find_nodes(node, pred=lambda x: True):
    que = deque()
    que.append(node)
    result = []
    if pred(node):
        result.append(node)
    while que:
        n = que.popleft()
        if not hasattr(n, "children"):
            continue
        for ch in n.children:
            if pred(ch):
                result.append(ch)
            que.append(ch)

    return result


def extract_caluses_try(stmt):
    assert isinstance(stmt, TryStmt)
    if len(stmt.children) == 6:
        return stmt.children[2], stmt.children[5]
    else:
        return stmt.children[2], None


def extract_caluses_if(stmt):
    assert isinstance(stmt, IfStmt)
    if len(stmt.children) < 7:
        return stmt.children[3], None
    else:
        return stmt.children[3], stmt.children[6]


def variables_out(suite):
    return {
        d.name
        for d in jedi.names(suite.get_code())
    } if suite else set()
