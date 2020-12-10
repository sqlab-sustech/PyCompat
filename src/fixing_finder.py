#! /usr/bin/python3

from collections import deque
import os
import gc
import importlib

import parso
from parso.python.tree import TryStmt, IfStmt, Name, PythonNode

from utils import variables_out, find_nodes, extract_caluses_try, extract_caluses_if

import jedi

from jedi.api.classes import Definition


def search_files(repo_dir):
    result = []
    dir_queue = deque()
    dir_queue.appendleft(repo_dir)
    while dir_queue:
        working_dir = dir_queue.pop()
        names = os.listdir(working_dir)
        for name in names:
            full_path = os.path.join(working_dir, name)
            if os.path.isdir(full_path) and name != ".git":
                dir_queue.appendleft(full_path)
            elif os.path.isfile(full_path):
                result.append(full_path)
    return result


def is_fixing_try(stmt: TryStmt):
    caught_exception = list(stmt.get_except_clause_tests())
    caught_exception = caught_exception[0] if len(
        caught_exception) > 0 else None
    if caught_exception and isinstance(caught_exception, Name) and caught_exception.value in {"AttributeError", "ImportError", "TypeError"}:
        c1, c2 = extract_caluses_try(stmt)
        return is_symmetric(c1, c2)
    else:
        return False


def name_in_condition(name: Definition, condition: PythonNode):
    return condition.start_pos[0] <= name.line <= condition.end_pos[0] and condition.start_pos[1] <= name.column <= condition.end_pos[1]


def get_assignments(n: Definition):
    try:
        script = jedi.Script(path=n.module_path, line=n.line, column=n.column)
        result = script.goto_assignments(follow_imports=True)
        del script
        return [n for n in result if n.type == "statement"]
    except:
        return []


def is_depended_on_version(condition: PythonNode, code, file_name):
    # print("Test")
    try:
        names = jedi.names(path=file_name, definitions=False, references=True)
    except LookupError:
        return False
    names = [n for n in names if name_in_condition(n, condition)]
    if any(n for n in names if n.name == "__version__"):
        return True
    q = deque()
    visited = set()
    counter = 0
    for n in names:
        assignments = get_assignments(n)
        for a in assignments:
            q.appendleft(a)
    while q:
        if counter > 1000:
            return False
        d: Definition = q.pop()
        # print(d)
        if d.name == "__version__":
            return True
        right_side_vars_defs = jedi.names(
            path=d.module_path, definitions=False, references=True)
        right_side_vars = [v for v in right_side_vars_defs if v.line == d.line]
        del right_side_vars_defs
        for rs in right_side_vars:
            if rs.name == "__version__":
                return True
            assignments = get_assignments(rs)
            for a in assignments:
                if (a.column, a.line, a.module_path) not in visited:
                    q.appendleft(a)
                    visited.add((a.column, a.line, a.module_path))
                    counter += 1
    return False


def is_fixing_if(stmt: IfStmt, code, file_name):
    condition = next(stmt.get_test_nodes())
    cond_code = condition.get_code()
    c1, c2 = extract_caluses_if(stmt)
    if is_symmetric(c1, c2):
        return "__version__" in cond_code or is_depended_on_version(condition, code, file_name)
    else:
        return False


def is_symmetric(c1, c2):
    n1 = variables_out(c1)
    n2 = variables_out(c2)
    return len(n1) > 0 and n1 == n2


def detect_fixing_tries(file_name):
    with open(file_name) as code_file:
        code = code_file.read()

    mod = parso.parse(code)
    nodes = find_nodes(mod, lambda x: isinstance(x, TryStmt))

    fixing_tries = [
        n for n in nodes if is_fixing_try(n)
    ]
    return fixing_tries


def detect_fixing_ifs(file_name):
    try:
        with open(file_name) as code_file:
            code = code_file.read()
    except UnicodeDecodeError:
        return []
    mod = parso.parse(code)
    nodes = find_nodes(mod, lambda x: isinstance(x, IfStmt))

    fixing_ifs = [
        n for n in nodes if is_fixing_if(n, code, file_name)
    ]
    del mod
    del code
    del nodes
    return fixing_ifs


def main():
    import sys
    files = search_files(
        "../Repos-selection/repos/")
    py_files = list(filter(lambda fn: fn.endswith(".py"), files))
    # py_files = search_files("./test_code/if")
    count = 0
    n = 0
    total = len(py_files)
    for f in py_files:
        try:
            cf = len(detect_fixing_tries(f))
        except:
            cf = 0
        if cf > 0:
            print("[%d] %s" % (cf, f))
        else:
            sys.stderr.write("\033[K")
            print("[%d / %d] %s" % (n,total, f), end="\r", flush=True, file=sys.stderr)
        count += cf
        n += 1
        if n % 200 == 0:
            importlib.reload(jedi)
            gc.collect()

    print("Total", count)


if __name__ == "__main__":
    main()
