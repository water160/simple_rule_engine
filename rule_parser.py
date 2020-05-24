import json
from collections import OrderedDict


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

    def rule_var_to_value(self, arg):
        ans = None
        if isinstance(arg, str):
            ans = globals()[arg]
        elif isinstance(arg, (int, float, list)):
            ans = arg
        else:
            raise RuntimeError("arg is not `str`/`int`/`float`/`list`")
        return ans

    def eq(self, *args):
        return self.rule_var_to_value(args[0]) == self.rule_var_to_value(args[1])

    def neq(self, *args):
        return self.rule_var_to_value(args[0]) != self.rule_var_to_value(args[1])

    def gt(self, *args):
        return self.rule_var_to_value(args[0]) > self.rule_var_to_value(args[1])

    def gte(self, *args):
        return self.rule_var_to_value(args[0]) >= self.rule_var_to_value(args[1])

    def lt(self, *args):
        return self.rule_var_to_value(args[0]) < self.rule_var_to_value(args[1])

    def lte(self, *args):
        return self.rule_var_to_value(args[0]) <= self.rule_var_to_value(args[1])

    def in_(self, *args):
        return self.rule_var_to_value(args[0]) in self.rule_var_to_value(args[1:])

    def not_(self, *args):
        return not self.rule_var_to_value(args[0])

    def or_(self, *args):
        return any(args)

    def and_(self, *args):
        return all(args)

    def int_(self, *args):
        return int(self.rule_var_to_value(args[0]))

    def str_(self, *args):
        return str(self.rule_var_to_value(args[0]))

    def plus(self, *args):
        sum_plus = 0
        for arg in args:
            sum_plus += self.rule_var_to_value(arg)
        return sum_plus

    def minus(self, *args):
        return self.rule_var_to_value(args[0]) - self.rule_var_to_value(args[1])

    def multiply(self, *args):
        sum_multiply = 1
        for arg in args:
            sum_multiply *= self.rule_var_to_value(arg)
        return sum_multiply

    def divide(self, *args):
        return self.rule_var_to_value(args[0]) / self.rule_var_to_value(args[1])

    def abs(self, *args):
        return abs(self.rule_var_to_value(args[0]))

    def upper(self, *args):
        return self.rule_var_to_value(args[0]).upper()

    def lower(self, *args):
        return self.rule_var_to_value(args[0]).lower()


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


def dynamic_loop(loop_dict, cur_loop, loop_tmp, loop_result):
    """ dynamic loop of `loop_dict`
    dynamic_loop(loop_dict, 0, [], [])
    """
    max_loop_num = len(loop_dict) - 1
    for num in list(loop_dict.values())[cur_loop]:
        loop_tmp.append(num)
        if cur_loop == max_loop_num:
            loop_result.append([*loop_tmp])
        else:
            dynamic_loop(loop_dict, cur_loop+1, loop_tmp, loop_result)
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
    ans_vars.sort(key=loop_vars.index)
    return ans_vars


def tiling_loop_with_rules(loop_dict, rule_dict):

    loop_result = dynamic_loop(loop_dict, 0, [], [])
    for loop_var, loop_range in loop_dict.items():
        print("%-6s=>%s" % (loop_var, loop_range))
    print("\n")
    for rule_id, rule in rule_dict.items():
        print("%-6s=>%s" % (rule_id, rule))
    print("\n")
    for one_loop_ans in loop_result:
        for idx in range(len(one_loop_ans)):
            register_var(list(loop_dict.keys())[idx], one_loop_ans[idx])
        ret = True
        for rule_id, rule in rule_dict.items():
            ret = ret and RuleParser(rule).evaluate()
        if ret:
            print("%s" % (one_loop_ans))




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


def test_dynamic_loop_with_rules(rule_dict):
    loop_dict = OrderedDict()
    loop_dict['Ho'] = [1,2,3,4,5]
    loop_dict['Wo'] = [1,2,3,4,5]
    loop_dict['Xo'] = [1,2,3,4,5]
    tiling_loop_with_rules(loop_dict, rule_dict)


if __name__ == "__main__":
    with open("rule_tiling.json", 'r') as json_fp:
        rule_dict = json.load(json_fp)

    # test_rule_with_str_desc(rule_dict)
    test_dynamic_loop_with_rules(rule_dict)