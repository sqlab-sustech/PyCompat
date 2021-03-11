#! /usr/bin/python3

from library_traverser import traverse_module, MemberVisitor, MemberInfoExtractor
import re
import inspect
import pymongo
import pkgutil
import importlib
import sklearn

sub_modules = [m for m in pkgutil.iter_modules(sklearn.__path__) if m[2]]

for m in sub_modules:
    try:
        importlib.import_module("sklearn.%s" % m[1], m)
    except:
        pass

# From tensorflow source
do_not_descend_map = {

}

prefix_black_list = {
    ".".join([prefix, name])
    for prefix in do_not_descend_map
    for name in do_not_descend_map[prefix]
}


class SklearnMemberInfoExtractor(MemberInfoExtractor):
    _args_doc_regex = re.compile(
        r"(Args:\n)((\ {2}\w+:\s[\S\ ]+(\n\ {4}[\S\ ]+)*\n*)+)")
    _arg_item_doc_regex = re.compile(
        r"\ {2}(\w+):\s([\S\ ]+(\n\ {4}[\S\ ]+)*)")
    _returns_doc_regex = re.compile(r"(Returns:\n)((\ {2}[\S\ ]+\n)+)")
    _raises_doc_regex = re.compile(r"(Raises:\n)((\ {2}[\S\ ]+\n)+)")

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
        match = next(self._raises_doc_regex.finditer(doc or ""), None)
        return match.group(2) if match else None

    def is_deprecated(self, name, member):
        doc = inspect.getdoc(member)
        return False if not doc else "DEPRECATED" in doc

mongn_client = pymongo.MongoClient(host="172.17.0.2")
db = mongn_client.get_database("DeepLearningAPIEvoluation")
collection = db.get_collection("Scikit-learn_APIs_%s" % sklearn.__version__)
collection.drop()


def insert_db(data):
    collection.insert(data,check_keys=False)


extractor = SklearnMemberInfoExtractor()
visitor = MemberVisitor(insert_db, inspect, extractor)

traverse_module(("sklearn", sklearn), visitor, "sklearn", prefix_black_list)

mongn_client.close()
