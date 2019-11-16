#!/usr/bin/python
# For testing out the handwritten parser
from collections import namedtuple
import re
import sys

Token = namedtuple("Token", ["tag", "text"])
ParseResult = namedtuple("ParseResult", ["state", "value"])
result_text = []

def lexTemplate(text):
    tagRex = re.compile(r"\{!([a-z]+)[^}]*\}")
    tokens = []
    pos = 0
    while pos < len(text):
        m = tagRex.search(text, pos)
        if m is None:
            # No more directives found.
            tokens.append(Token("text", text[pos:]))
            break
        else:
            # There might be text between here and the next directive.
            if m.start() > pos:
                tokens.append(Token("text", text[pos:m.start()]))
            tokens.append(Token(m.group(1), m.group(0)))
            pos = m.end()
    return tokens

# class Lexer():
class TemplateParseError(Exception):
    pass

def parseIf(state):
    res = state.expect("if")
    if res is None:
        return None
    ifText = res.value.text
    res = parseTemplate(res.state)
    if res is None:
        raise TemplateParseError("expected body for if-directive")
    trueBody = res.value
    if res.state.peek() == "else":
        res = res.state.take()
        res = parseTemplate(res.state)
        if res is None:
            raise TemplateParseError("expected else-body for if-directive")
        falseBody = res.value
    else:
        falseBody = None
        res = res.expect("endif")
    if res is None:
        raise TemplateParseError("expected endif")
    value = buildIf(ifText, trueBody, falseBody)
    return ParseResult(res.state, value)

class ParseState():

    def __init__(self, tokens, pos=0):
        self.tokens = tokens
        self.pos = pos

    def atEnd(self):
        return self.pos == len(self.tokens)

    def take(self):
        if self.atEnd():
            return None
        nextState = ParseState(self.tokens, self.pos+1)
        token = self.tokens[self.pos]
        return ParseResult(nextState, token)
    
    def expect(self, expectedTag):
        result = self.take()
        if result is None or result.value.tag != expectedTag:
            return None
        return result

    def peek(self):
        return_ok(cookie, request)

def parseCall(state):
    res = state.expect("call")
    if res is None:
        return None
    value = buildCall(res.value.text)
    return ParseResult(res.state, value)       

def parseText(state):
    res = state.expect("text")
    if res is None:
        return None
    value = res.value.text
    return ParseResult(res.state, value)       

def parseInclude(state):
    res = state.expect("include")
    if res is None:
        return None
    value = res.value.text
    return ParseResult(res.state, value)       

def parseIf(state):
    res = state.expect("if")
    if res is None:
        return None
    ifText = res.value.text
    res = parseTemplate(res.state)
    if res is None:
        raise TemplateParseError("expected body for if-directive")
    trueBody = res.value
    if res.state.peek() == "else":
        res = res.state.take()
        res = parseTemplate(res.state)
        if res is None:
            raise TemplateParseError("expected else-body for if-directive")
        falseBody = res.value
    else:
        falseBody = None
        res = res.expect("endif")
    if res is None:
        raise TemplateParseError("expected endif")
    value = buildIf(ifText, trueBody, falseBody)
    return ParseResult(res.state, value)

def parseFor(state):
    res = state.expect("for")
    if res is None:
        return None
    forText = res.value.text
    res = parseTemplate(res.state)
    if res is None:
        raise TemplateParseError("expected body for for-directive")
    forBody = res.value
    # if res.state.peek() == "else":
    #     res = res.state.take()
    #     res = parseTemplate(res.state)
    #     if res is None:
    #         raise TemplateParseError("expected else-body for if-directive")
    #     falseBody = res.value
    # else:
        # falseBody = None
        # res = res.expect("endfor")
    if res is None:
        raise TemplateParseError("expected endfor")
    value = buildIf(forText, forBody)
    return ParseResult(res.state, value)

def parseTemplate(state):
    value = None
    done = False
    while not done:
        res = parseSimpleTemplate(state)
    if res is None:
        done = True
    else:
        value = buildSequence(value, res.value)
        state = res.state
    if value is None:
        return None
    else:
        return ParseResult(state, value) 

def parseSimpleTemplate(state):
    res = parseText(state)
    # breakpoint()
    if res:
        return res
    res = parseInclude(state)
    # print("Parsing include")
    if res:
        return res
    res = parseCall(state)
    # print("Parsing call")
    if res:
        return res
    res = parseIf(state)
    # print("Parsing If")
    if res:
        return res
    res = parseFor(state)
    # print("Parsing for")
    if res:
        return res
    
    return None



def parseTemplateFile(fileName):
    with open(fileName) as templateFile:
        templateText = templateFile.read()
        # print("reading the {}".format(templateText))
        tokens = lexTemplate(templateText)
        # pdb.set_trace()
        state = ParseState(tokens)
        breakpoint()
        res = parseTemplate(state)
    if res is None:
        raise TemplateParseError("could not parse template")
    if not res.state.atEnd():
        raise TemplateParseError("garbage at end of template")
    return res.value

def buildCall(value):
    print("Calling")
    result_text.append(value)
    return "Not implemented"

if __name__ == "__main__":
    fileName = sys.argv[1]
    parseTemplateFile(fileName)