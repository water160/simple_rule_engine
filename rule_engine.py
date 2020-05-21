import json
import math
import inspect
from rule_parser import RuleParser





'''
{
    "rule_0":[
        "and",
        [">", "Ho", "Wo"],
        [">=", "Ho", 2]
    ],
    "rule_1":[
        "and",
        ["<", "Xo", "Wo"],
        [">=", 3, 2]
    ]
}

for rule_id, rule in rule_dict.items():
    ret = RuleParser(rule).evaluate()
    print(rule_id, rule, ret)
{
    "rule_0":[
        "and",
        [">", 5, 3],
        [">=", 3, 4]
    ],
    "rule_1":[
        "and",
        ["<", 4, 10],
        [">=", 3, 2]
    ]
}
'''