#! /usr/bin/python3

from library_traverser import traverse_module, MemberVisitor, MemberInfoExtractor
import re
import inspect
import pymongo
import pandas as pd


# From tensorflow source
do_not_descend_map = {
    "pd": ["roll_kurt"]
}

prefix_black_list = {
    ".".join([prefix, name])
    for prefix in do_not_descend_map
    for name in do_not_descend_map[prefix]
}


class PandasMemberInfoExtractor(MemberInfoExtractor):
    _args_doc_regex = re.compile(
        r"(Parameters\n-{10})((\n\w+ : [\S ]+(\n {4}[\S ]+|\n$)*)+)")
    _arg_item_doc_regex = re.compile(
        r"\n(\w+) : ([\S ]+(\n {4}[\S ]+|\n$)*)")
    _returns_doc_regex = re.compile(
        r"(Returns\n-{7})((\n\w+ : [\S ]+(\n {4}[\S ]+|\n$)*)+)")
    # _raises_doc_regex = re.compile(r"(Raises:\n)((\ {2}[\S\ ]+\n)+)")

    def extract_args_doc(self, doc):
        arg_doc_match = next(self._args_doc_regex.finditer(doc or ""), None)
        if not arg_doc_match:
            return {}
        arg_doc = arg_doc_match.group(2)
        return {
            match.group(1):  match.group(2)
            for match in self._arg_item_doc_regex.finditer(arg_doc)
        }

    def extract_returns_doc(self, doc):
        match = next(self._returns_doc_regex.finditer(doc or ""), None)
        return match.group(2) if match else None

    def extract_raise_doc(self, doc):
        return None
        # match = next(self._raises_doc_regex.finditer(doc or ""), None)
        # return match.group(2) if match else None

    def is_deprecated(self, name, member):
        doc = inspect.getdoc(member)
        return False if not doc else "DEPRECATED" in doc


mongn_client = pymongo.MongoClient(host="172.17.0.2")
db = mongn_client.get_database("DeepLearningAPIEvoluation")
collection = db.get_collection("Pandas_APIs_%s" % pd.__version__)
collection.drop()


def insert_db(data):
    collection.insert(data,check_keys=False)


extractor = PandasMemberInfoExtractor()
visitor = MemberVisitor(insert_db, inspect, extractor)

traverse_module(("pd", pd), visitor, "pandas", prefix_black_list)

mongn_client.close()
