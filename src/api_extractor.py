# coding: utf-8

# ## API_Extractor
# #### this is used for extract all api use of all files under a directory


import re
import parso
import os
import json
import collections
import logging


class API_Extractor:
    def __init__(self, framework, fileName, repo_url):
        self.framework = framework
        self.module = self.parse_module(fileName)
        self.iR = self.get_import_name()
        self.fileName = fileName
        self.repo_url = repo_url

    # Check if the API call belongs to our framework
    def check(self, value, iR):
        if value in list(iR.keys()):
            return iR[value]
        return None

    # Get parameters
    def __handle_param__(self, param):
        p = []
        if param.children[1].type == 'name':
            p = [param.children[1].value]
        ##处理多个参数
        else:
            if param.children[1].type == 'atom_expr':
                ###处理xxx
                p = [param.children[1].get_code().replace(' ', '').replace('\n', '')]
            elif param.children[1].type == 'arglist':
                ###处理(XX,DD,DD.(sdf))
                for child in param.children[1].children:
                    if child.type != 'operator':
                        ###TO-DO 处理XX=CC的情况###
                        p.append(child.get_code().replace(' ', '').replace('\n', ''))
            elif len(param.children) == 2:
                ###处理()
                p = []
        return p

    # Extract call_chain and param_chain
    def __extract_call_param__(self, expr):
        allChildren = expr.children
        callChain = [allChildren[0].value]
        paramChain = [None]
        for i, leaf in enumerate(allChildren):
            if leaf.get_first_leaf() == '.':
                callChain.append(leaf.get_last_leaf().value)
                paramChain.append(None)
            elif leaf.get_first_leaf() == '(':
                param = self.__handle_param__(leaf)
                if paramChain[-1] is None:
                    paramChain[-1] = param
                else:
                    logging.error("Wrong!\n" + expr)
        return callChain, paramChain

    # Find each atom expression for API call
    def find_atom_expr(self, module, iR):
        allapi = []
        temp_iR = iR.copy()
        for node in module.children:
            if node.type == 'funcdef':
                if hasattr(node, 'children'):
                    allapi += self.find_atom_expr(node, temp_iR)
            else:
                if type(node) == parso.python.tree.PythonNode and node.type == 'atom_expr':
                    checkResult = self.check(node.get_first_leaf().value, iR)
                    if checkResult is not None:
                        allapi.append({node: checkResult})
                    #     if(node.parent is not None and node.parent.type == 'expr_stmt'):
                    #         try:
                    #             iR[node.parent.get_defined_names()[0].value] = self.__extract_call_param__(node)
                    #         except IndexError:
                    #             pass
                if hasattr(node, 'children'):
                    allapi += self.find_atom_expr(node, iR)
        return allapi

    # Transform api
    def transform_api(self, aE):
        call_0 = {
            "tensorflow": "tf",
            "pandas": "pd",
            "keras": "keras",
            "scikit-learn": "sklearn",
            "parso": "parso",
            "collections": "collections"
        }
        atomExpr = list(aE.keys())[0]

        lineNum, colNum = atomExpr.start_pos
        path = aE[atomExpr]

        call_chain, param_chain = self.__extract_call_param__(atomExpr)
        call_chain = path + call_chain[1:]  ###所有调用链
        call_chain[0] = call_0[self.framework]

        param_chain = param_chain

        api_name = ".".join(call_chain)

        return dict([
            ("framework", self.framework),
            ("repo_url", self.repo_url),
            ("api_name", api_name),
            ("line_num", lineNum),
            ("file_name", self.fileName),
            ('call_chain', call_chain),
            ('param_chain', param_chain)
        ])

    # Parse module
    def parse_module(self, fileName: str):
        return parso.parse(open(fileName, "r").read())

        # Get all import

    def get_import_name(self):
        import_results = {}  ###[{dfNameA:pathA...}]
        for imports in self.module.iter_imports():
            paths = imports.get_paths()  ###[[a,b,c][a,b,d]]
            names = imports.get_defined_names()  ###[c,d]
            for t, p in enumerate(paths):
                if len(p) > 0 and p[0].value == (self.framework):
                    call_path = list(map(lambda x: x.value, p))
                    # param_path = list(None for i in range(len(call_path)))
                    try:
                        import_results[names[t].value] = call_path
                    except IndexError:
                        pass

        return import_results

        # Get all API callsites

    def get_api(self):
        exprs = self.find_atom_expr(self.module, self.iR)
        transformedApi = list(map(self.transform_api, exprs))
        return transformedApi


def extract_files(path):
    allFile = []
    for i in os.listdir(path):
        if os.path.isdir(path + '/' + i):
            allFile += extract_files(path + '/' + i)
        else:
            if i.endswith('.py'):
                allFile.append(path + '/' + i)
    return allFile
