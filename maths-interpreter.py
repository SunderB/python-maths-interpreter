#!/usr/bin/python3
from typing import NamedTuple
import re
import uuid

class Token(NamedTuple):
    type: str
    value: str # can be any type
    position: int

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

calc_input = input("calc: ")

operators = ["+", "-", "/", "*", "^"]
numeric_characters = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

test_input="((1 + 2) * (( 3 / 4) + 5)) - 6"
expected_output = [
    [
        ["1", "+", "2"],
        "*",
        [
            ["3", "/", "4"],
            "+",
            "5"
        ]
    ],
    "-",
    "6"
]

##def evaluate_simple_expression(expression):
##    value = None
##    
##    number = False
##    for i in range(0, len(expression)):
##        char = expression[i]
##        if (char == "("):
##            level += 1
##        elif (char == ")"):
##            level -= 1
##        elif any(o in char for o in operators):
##            tokens
##        elif any(n in char for n in numeric_characters):
##            pass
##        elif (char != " "):
##            raise(InputError("Invalid char: " + char))
##
##    return value
##
##def parse_maths(calc_input):
##    tokens = []
##
##    number = False
##    level = 0
##    current_level = []
##    for i in range(0, len(calc_input)):
##        char = calc_input[i]
##        if (char == "("):
##            level += 1
##        elif (char == ")"):
##            level -= 1
##        elif any(o in char for o in operators):
##            tokens
##        elif any(n in char for n in numeric_characters):
##            pass
##        elif (char != " "):
##            raise(InputError("Invalid char: " + char))


def tokenize(calc_input):
    token_specification = [
        ("LEVEL_START",         r'[\(]{1}'), # Matches '('
        ("LEVEL_END",           r'[\)]{1}'), # Matches ')'
        ("OPERATOR_INDICES",    r'[\^]{1}'), # Matches '^'
        ("OPERATOR_DIV_MUL",    r'[\/\*]{1}'), # Matches '/' or '*'
        ("OPERATOR_ADD_SUB",    r'[\+-]{1}'), # Matches '+' or '-'
        ("NUMBER",              r'\d+(\.\d*)?'), # Matches any integer or decimal number (e.g. 0, 123, 3.14, 0.123)
        ("WHITESPACE",          r'[ \t]+'),
        ("MISMATCH",            r'.'),
    ]
    # Join together all the regex statements, and assign the type names to each capture group
    token_regex = "|".join('(?P<%s>%s)' % pair for pair in token_specification)

    # Variables to keep track of current state
    current_section_id = "0"
    parent_sections = []
    position = 0
    #level_pos = 0

    sections = {"0": [] }
    
    for mo in re.finditer(token_regex, calc_input):
        kind = mo.lastgroup
        value = mo.group()
        position = mo.start()

        if kind == "LEVEL_START":
            # Add current section to parent list
            parent_sections.append(current_section_id)

            # Create new section id and append a reference to it in the current section
            new_section_id = uuid.uuid4().hex
            sections[current_section_id].append(Token("SECTION_REF", new_section_id, position))

            # Create the new section and switch to it
            sections[new_section_id] = []
            current_section_id = new_section_id
            continue
        
        elif kind == "LEVEL_END":
            # Switch to the previous section and remove it from the parent list
            current_section_id = parent_sections.pop()
            continue
        
        elif kind == "NUMBER":
            if "." in value:
                value = float(value)
            else:
                value = int(value)

        elif kind == "WHITESPACE":
            continue
        
        elif kind == "MISMATCH":
            raise(RuntimeError("Invalid char: " + value))

        sections[current_section_id].append(Token(kind, value, position))

    return sections

def search_tokens(tokens, properties):
    results = []
    for t in tokens:
        if ("value" in properties):
            if (t.value != properties["value"]): continue
        
        if ("type" in properties):
            if (t.type != properties["type"]): continue

        if ("level" in properties):
            if (t.level != properties["level"]): continue

        results.append(t)

    return results

def print_tokens(tokens):
    #for token in tokens:
    #    print(token)
    print(tokens)

def parse_section(sections, section_id) -> Token: 
    tokens = sections[section_id].copy()

    type_list = [
        "SECTION_REF"
        "OPERATOR_INDICES",
        "OPERATOR_DIV_MUL",
        "OPERATOR_ADD_SUB",
    ]

    parsed_tokens = tokens
    
    for i in range(0, len(tokens)):
        if (tokens[i].type == "SECTION_REF"):
            parsed_tokens[i] = parse_section(sections, tokens[i].value)

    tokens = parsed_tokens
    print_tokens(tokens)
    parsed_tokens = []

    i = 0
    while i < len(tokens):
        if (tokens[i].type == "OPERATOR_INDICES"):
            base = parsed_tokens.pop().value
            power = tokens[i+1].value
            
            parsed_tokens.append(Token("NUMBER", pow(base, power), None))
            i += 2

        else:
            parsed_tokens.append(tokens[i])
            i += 1

    tokens = parsed_tokens
    print_tokens(tokens)
    parsed_tokens = []

    i = 0
    while i < len(tokens):
        print(i)
        if (tokens[i].type == "OPERATOR_DIV_MUL"):
            num1 = parsed_tokens.pop().value
            num2 = tokens[i+1].value
            
            if (tokens[i].value == "*"):
                print(str(num1) + " * " + str(num2))
                parsed_tokens.append(Token("NUMBER", num1 * num2, None))
            elif (tokens[i].value == "/"):
                print(str(num1) + " / " + str(num2))
                parsed_tokens.append(Token("NUMBER", num1 / num2, None))
                
            i += 2
        else:
            parsed_tokens.append(tokens[i])
            i += 1

    tokens = parsed_tokens
    print_tokens(tokens)
    parsed_tokens = []

    i = 0
    while i < len(tokens):
        if (tokens[i].type == "OPERATOR_ADD_SUB"):
            num1 = parsed_tokens.pop().value
            num2 = tokens[i+1].value
            if (tokens[i].value == "+"):
                parsed_tokens.append(Token("NUMBER", num1 + num2, None))
            elif (tokens[i].value == "-"):
                parsed_tokens.append(Token("NUMBER", num1 - num2, None))
                
            i += 2
        else:
            parsed_tokens.append(tokens[i])
            i += 1

    return parsed_tokens[0]
    

tokens = tokenize(calc_input)
answer = parse_section(tokens, "0")
print("----")
print("Answer: " + str(answer.value))
#print(tokens)

#print(parse_maths(test_input))
