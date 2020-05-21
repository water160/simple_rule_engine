import json
import math
import inspect
# from rule_parser import RuleParser


class Functions(object):

    ALIAS = {
        '=': 'eq',
        '!=': 'neq',
        '>': 'gt',
        '>=': 'gte',
        '<': 'lt',
        '<=': 'lte',
        'and': 'and_',
        'in': 'in_',
        'or': 'or_',
        'not': 'not_',
        'str': 'str_',
        'int': 'int_',
        '+': 'plus',
        '-': 'minus',
        '*': 'multiply',
        '/': 'divide'
    }

    def eq(self, *args):
        if isinstance(args[0], str) and isinstance(args[1], str):
            return globals()[args[0]] == globals()[args[1]]
        elif isinstance(args[0], str) and isinstance(args[1], (int, float)):
            return globals()[args[0]] == args[1]
        elif isinstance(args[0], (int, float)) and isinstance(args[1], str):
            return args[0] == globals()[args[1]]
        elif isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
            return args[0] == args[1]
        else:
            raise RuntimeError("%s and %s have wrong type, not `int`/`float`/`str`"\
                % (args[0], args[1]))

    def neq(self, *args):
        if isinstance(args[0], str) and isinstance(args[1], str):
            return globals()[args[0]] != globals()[args[1]]
        elif isinstance(args[0], str) and isinstance(args[1], (int, float)):
            return globals()[args[0]] != args[1]
        elif isinstance(args[0], (int, float)) and isinstance(args[1], str):
            return args[0] != globals()[args[1]]
        elif isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
            return args[0] != args[1]
        else:
            raise RuntimeError("%s and %s have wrong type, not `int`/`float`/`str`"\
                % (args[0], args[1]))

    def gt(self, *args):
        if isinstance(args[0], str) and isinstance(args[1], str):
            return globals()[args[0]] > globals()[args[1]]
        elif isinstance(args[0], str) and isinstance(args[1], (int, float)):
            return globals()[args[0]] > args[1]
        elif isinstance(args[0], (int, float)) and isinstance(args[1], str):
            return args[0] > globals()[args[1]]
        elif isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
            return args[0] > args[1]
        else:
            raise RuntimeError("%s and %s have wrong type, not `int`/`float`/`str`"\
                % (args[0], args[1]))

    def gte(self, *args):
        if isinstance(args[0], str) and isinstance(args[1], str):
            return globals()[args[0]] >= globals()[args[1]]
        elif isinstance(args[0], str) and isinstance(args[1], (int, float)):
            return globals()[args[0]] >= args[1]
        elif isinstance(args[0], (int, float)) and isinstance(args[1], str):
            return args[0] >= globals()[args[1]]
        elif isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
            return args[0] >= args[1]
        else:
            raise RuntimeError("%s and %s have wrong type, not `int`/`float`/`str`"\
                % (args[0], args[1]))

    def lt(self, *args):
        if isinstance(args[0], str) and isinstance(args[1], str):
            return globals()[args[0]] < globals()[args[1]]
        elif isinstance(args[0], str) and isinstance(args[1], (int, float)):
            return globals()[args[0]] < args[1]
        elif isinstance(args[0], (int, float)) and isinstance(args[1], str):
            return args[0] < globals()[args[1]]
        elif isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
            return args[0] < args[1]
        else:
            raise RuntimeError("%s and %s have wrong type, not `int`/`float`/`str`"\
                % (args[0], args[1]))

    def lte(self, *args):
        if isinstance(args[0], str) and isinstance(args[1], str):
            return globals()[args[0]] <= globals()[args[1]]
        elif isinstance(args[0], str) and isinstance(args[1], (int, float)):
            return globals()[args[0]] <= args[1]
        elif isinstance(args[0], (int, float)) and isinstance(args[1], str):
            return args[0] <= globals()[args[1]]
        elif isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
            return args[0] <= args[1]
        else:
            raise RuntimeError("%s and %s have wrong type, not `int`/`float`/`str`"\
                % (args[0], args[1]))

    def in_(self, *args):
        return args[0] in args[1:]

    def not_(self, *args):
        return not args[0]

    def or_(self, *args):
        return any(args)

    def and_(self, *args):
        return all(args)

    def int_(self, *args):
        return int(args[0])

    def str_(self, *args):
        return unicode(args[0])

    def upper(self, *args):
        return args[0].upper()

    def lower(self, *args):
        return args[0].lower()

    def plus(self, *args):
        return sum(args)

    def minus(self, *args):
        return args[0] - args[1]

    def multiply(self, *args):
        return args[0] * args[1]

    def divide(self, *args):
        return float(args[0]) / float(args[1])

    def abs(self, *args):
        return abs(args[0])


class RuleParser(object):
    def __init__(self, rule):
        if isinstance(rule, str):
            self.rule = json.loads(rule)
        else:
            self.rule = rule
        self.validate(self.rule)

    @staticmethod
    def validate(rule):
        if not isinstance(rule, list):
            raise RuleEvaluationError('Rule must be a list, got {}'.format(type(rule)))
        if len(rule) < 2:
            raise RuleEvaluationError('Must have at least one argument.')

    def _evaluate(self, rule, fns):
        """ 递归执行list内容
        """
        def _recurse_eval(arg):
            if isinstance(arg, list):
                return self._evaluate(arg, fns)
            else:
                return arg

        r = list(map(_recurse_eval, rule))
        r[0] = Functions.ALIAS.get(r[0]) or r[0]
        func = getattr(fns, r[0])
        return func(*r[1:])

    def evaluate(self):
        fns = Functions()
        ret = self._evaluate(self.rule, fns)
        if not isinstance(ret, bool):
            raise RuntimeError('In common usage, a rule must return a bool value,'
                        'but get {}, please check the rule to ensure it is true' )
        return ret


def register_var(tiling_var, val):
    """ set vars to globals(), only effective in one file
    """
    globals()[tiling_var] = val


def get_variable_name(variable):
    """ get variable dynamicly
    call: get_variable_name(list['list_0']).pop()
    output: list_0
    """
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    ans = [var_name for var_name, var_val in callers_local_vars if var_val is variable]
    return ans


def dynamic_loop(loop_list, cur_loop, loop_tmp, loop_result):
    """ dynamic loop of `loop_list`
    dynamic_loop(loop_list, 0, [], [])
    """
    max_loop_num = len(loop_list) - 1
    for num in loop_list[cur_loop]:
        loop_tmp.append(num)
        if cur_loop == max_loop_num:
            loop_result.append([*loop_tmp])
        else:
            dynamic_loop(loop_list, cur_loop+1, loop_tmp, loop_result)
        loop_tmp.pop()
    return loop_result


def get_loop_vars(rule):
    """ get loop_vars from rule
    """
    traverse_list = [rule]
    loop_vars = []
    while(traverse_list):
        one_rule = traverse_list.pop()
        operator = one_rule[0]
        operate_nums = one_rule[1:]
        # print("operate_nums: %s" % operate_nums)
        for operate_num in operate_nums:
            if isinstance(operate_num, str):
                loop_vars.append(operate_num)
            elif isinstance(operate_num, list):
                traverse_list.append(operate_num)
            else:
                continue
    # remove redundant vars, and keep the order
    ans_vars = list(set(loop_vars))
    ans_vars.sort(key = loop_vars.index)
    return ans_vars


def tiling_loop_with_rule(loop_list, rule):
    loop_vars = get_loop_vars(rule)
    loop_result = dynamic_loop(loop_list, 0, [], [])
    print("loop_vars: %s" % loop_vars)
    print("loop_result: %s" % loop_result)
    # if rule is add to loop_list





"""
Test Functions
"""
def test_rule_with_str_desc(rule_dict):
    rule = rule_dict['rule_0']
    for x in range(1, 5):
        for y in range(1, 5):
            for z in range(1, 5):
                register_var('Ho', x)
                register_var('Wo', y)
                register_var('Xo', z)
                # print(globals())
                # exit()
                ret = True
                for rule_id, rule in rule_dict.items():
                    ret = ret and RuleParser(rule).evaluate()
                if ret:
                    print("======")
                    print("Ho = %s, Wo = %s, Xo = %s, ret = %s" % (x, y, z, ret))


def test_dynamic_loop_with_rule(rule_dict):
    rule = rule_dict['rule_0']
    loop_list = [
        [1,2,3,4,5],
        [1,2,3,4,5]
    ]
    tiling_loop_with_rule(loop_list, rule)


if __name__ == "__main__":
    with open("rules.json", 'r') as json_fp:
        rule_dict = json.load(json_fp)

    # test_rule_with_str_desc(rule_dict)
    test_dynamic_loop_with_rule(rule_dict)