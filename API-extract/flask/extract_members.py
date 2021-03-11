#! /usr/bin/python3

from library_traverser import traverse_module, MemberVisitor, MemberInfoExtractor
import re
import inspect
import pymongo
import flask
import pkgutil
import importlib


sub_modules = [m for m in pkgutil.iter_modules(flask.__path__) if m[2]]

for m in sub_modules:
    importlib.import_module("flask.%s" % m[1], m)
# From tensorflow source
do_not_descend_map = {

}

prefix_black_list = {
    ".".join([prefix, name])
    for prefix in do_not_descend_map
    for name in do_not_descend_map[prefix]
}


class FlaskMemberInfoExtractor(MemberInfoExtractor):
    _args_doc_regex = re.compile(
        r"((\n:param (\w+): ([\S ]+(\n\ {16}[\S ]+)*))+)")
    _arg_item_doc_regex = re.compile(
        r":param (\w+): ([\S ]+(\n\ {16}[\S ]+)*)")
    # _returns_doc_regex = re.compile(r"(Returns:\n)((\ {2}[\S\ ]+\n)+)")
    # _raises_doc_regex = re.compile(r"(Raises:\n)((\ {2}[\S\ ]+\n)+)")

    def extract_args_doc(self, doc):
        arg_doc_match = next(self._args_doc_regex.finditer(doc or ""), None)
        if not arg_doc_match:
            return {}
        arg_doc = arg_doc_match.group(1)
        return {
            match.group(1):  match.group(2)
            for match in self._arg_item_doc_regex.finditer(arg_doc)
        }

    def extract_returns_doc(self, doc):
        return None
        # match = next(self._returns_doc_regex.finditer(doc or ""), None)
        # return match.group(2) if match else None

    def extract_raise_doc(self, doc):
        return None
        # match = next(self._raises_doc_regex.finditer(doc or ""), None)
        # return match.group(2) if match else None

    def is_deprecated(self, name, member):
        doc = inspect.getdoc(member)
        return False if not doc else "DEPRECATED" in doc

mongn_client = pymongo.MongoClient(host="172.17.0.2")
db = mongn_client.get_database("DeepLearningAPIEvoluation")
collection = db.get_collection("Flask_APIs_%s" % flask.__version__)
collection.drop()


def insert_db(data):
    collection.insert(data,check_keys=False)


extractor = FlaskMemberInfoExtractor()
visitor = MemberVisitor(insert_db, inspect, extractor)

traverse_module(("flask", flask), visitor, "flask", prefix_black_list)

mongn_client.close()
