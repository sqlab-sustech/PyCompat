import argparse, logging, os, json
from api_extractor import API_Extractor
from fixing_finder import detect_fixing_ifs, detect_fixing_tries
import json
from os.path import join


def loading_db(db_path):
    logger.debug("Loading resource from {}".format(os.path.abspath(db_path)))
    with open(db_path, "r") as f:
        db_data = json.load(f)
    return db_data


def get_rules(rule_path):
    # Rule1: (api_name = new_api) ; (change_type = api_rename)
    # Rule2: (api_name = new_api) and (keyword_t = old_api_name or new_api_name); (old_api_name != new_api_name)
    pass


def check_PRN(api_usage, api_trans):
    return api_trans['change_type'] == 'parameter rename'


def check_ARR(api_usage, api_trans):
    return (api_usage[''] == (api_trans['old_api'] or api_trans['new_api']) and (
            api_trans['change_type'] == "api_rename"))


def check_api_usage(api_usage, api_db, rules):
    for api_trans in api_db:
        # TODO: change to DSL
        if check_ARR(api_usage, api_trans):
            return True
        if check_PRN(api_usage, api_trans):
            return True
    return False


def check_fixing(danger_api_usage: dict):
    fixing_ifs = detect_fixing_ifs(danger_api_usage['file_name'])
    fixing_tries = detect_fixing_tries(danger_api_usage['file_name'])
    if len(fixing_ifs) > 0 or len(fixing_tries) > 0:
        return True
    else:
        return False


def generate_report(unfixed_danger_api, output_dir):
    json.dump(unfixed_danger_api, join(output_dir, "pycompat_report.json"))


def start_pycompat(args):
    # Get all APIs
    api_extractor = API_Extractor(args.framework, args.input, "none")
    all_apis = api_extractor.get_api()

    # Get all api evolution ground truth
    api_db = loading_db(args.dataset)

    # Get all Rules
    rules = get_rules(args.rule_path)

    # Filter detrimental APIs
    danger_api_usage = list(filter(lambda api_usage: check_api_usage(api_usage, api_db), all_apis))

    # Checking fixing strategies
    unfixed_danger_api = list(filter(lambda x: not check_fixing(x), danger_api_usage))

    # Generating report
    generate_report(unfixed_danger_api, args.output)


def set_logger(level):
    FORMAT = '[%(levelname)s][%(filename)s][line:%(lineno)d]%(message)s'
    logging.basicConfig(format=FORMAT, level=level)
    return logging.getLogger("pycompat")


if __name__ == "__main__":
    logger = set_logger(logging.DEBUG)

    parser = argparse.ArgumentParser(description='PyCompat')
    parser.add_argument("input",
                        help='Path for input file')
    parser.add_argument("framework",
                        help='framework name')
    parser.add_argument("rule_path",
                        help='Path for rule set')
    parser.add_argument("dataset",
                        help='Path for dataset')
    parser.add_argument("output",
                        help='Path for output')
    args = parser.parse_args()

    start_pycompat(args)
