import interpreter as interp


def check_string(input_string, stripped_string):
    assert (interp.strip_parens(input_string) == stripped_string)


def test_strip_basic():
    check_string("this is a test (and I hope it works).",
                 "this is a test .")


def test_strip_nested():
    check_string("(i am (nested))",
                 "")


def test_strip_very_nested():
    check_string("x (i am (super (duper (nested))) lol)",
                 "x ")


def test_strip_left_unbalanced():
    check_string("(x ((i am (super (duper (nested))) lol)",
                 "(x (")


def test_strip_right_unbalanced():
    check_string("x (i am (super (duper (nested))) lol))",
                 "x )")
