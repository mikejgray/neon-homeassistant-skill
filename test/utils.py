from padacioso.bracket_expansion import expand_parentheses


def construct_test_yaml(intent: str, entity: str) -> None:
    [
        print(f"    - {x.replace('{entity}', entity)}:\n        - entity: {entity}")
        for x in expand_parentheses(intent)
    ]
