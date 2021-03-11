#! /usr/bin/python3

from library_traverser import traverse_module, MemberVisitor, MemberInfoExtractor
import re
import inspect
import pymongo
import tensorflow as tf
import json

# Make the lazy loader load bafore TF 1.2.0
try:
    import tensorflow.contrib
except:
    pass

# From tensorflow source
do_not_descend_map = {
    'tf': [
        'compiler',
        'core',
        'examples',
        'flags',  # Don't add flags
        # TODO(drpng): This can be removed once sealed off.
        'platform',
        # TODO(drpng): This can be removed once sealed.
        'pywrap_tensorflow',
        # TODO(drpng): This can be removed once sealed.
        'user_ops',
        'python',
        'tools',
        'tensorboard'
    ],
    # Everything below here is legitimate.
    # It'll stay, but it's not officially part of the API.
    'tf.app': ['flags'],
    # Imported for compatibility between py2/3.
    'tf.test': ['mock'],
    # Externalized modules of the Keras API.
    'tf.keras': ['applications', 'preprocessing']
}

prefix_black_list = {
    ".".join([prefix, name])
    for prefix in do_not_descend_map
    for name in do_not_descend_map[prefix]
}


class TensorFlowMemberInfoExtractor(MemberInfoExtractor):
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

mongn_client = pymongo.MongoClient("172.17.0.2")
db = mongn_client.get_database("DeepLearningAPIEvoluation")
collection = db.get_collection("TensorFlow_APIs_%s" % tf.__version__)
collection.drop()

def insert_db(data):
    collection.insert(data,check_keys=False)
extractor = TensorFlowMemberInfoExtractor()
visitor = MemberVisitor(insert_db, inspect, extractor)

traverse_module(("tf", tf), visitor, "tensorflow", prefix_black_list)

mongn_client.close()

