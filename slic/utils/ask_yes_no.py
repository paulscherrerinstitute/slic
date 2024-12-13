
try:
    read_input = input # py3
except NameError:
    read_input = raw_input # py2



ANSWERS = {
    "y":   True,
    "n":   False,
    "yes": True,
    "no":  False
}

OPTION_PROMPTS = {
    None: "y/n",
    "y":  "Y/n",
    "n":  "y/N"
}



def ask_Yes_no(question, **kwargs):
    """
    See ask_yes_no() with default="y".
    """
    return ask_yes_no(question, default="y", **kwargs)


def ask_yes_No(question, **kwargs):
    """
    See ask_yes_no() with default="n".
    """
    return ask_yes_no(question, default="n", **kwargs)


def ask_yes_no(question, default=None, ctrl_c="n", ctrl_d=None):
    """
    Asks "question? [y/n]" and returns the answer as boolean.

    Valid answers are: y/n/yes/no (match is not case sensitive).
    For invalid answers the question is repeated.

    default (defaults to None) is used if the user input is empty, i.e., only Enter was pressed.
    ctrl_c (defaults to "n") is used if the user presses Ctrl-C.
    ctrl_d (defaults to default) is used if the user presses Ctrl-D.

    The default is capitalized in the prompt.
    """

    ctrl_d = default if ctrl_d is None else ctrl_d

    option_prompt = OPTION_PROMPTS[default]
    prompt = question + f"? [{option_prompt}] "

    ans = None
    while ans not in ANSWERS:
        try:
            ans = read_input(prompt).lower()
            if not ans:  # response was an empty string
                ans = default
        except KeyboardInterrupt:
            print()
            ans = ctrl_c
        except EOFError:
            print()
            ans = ctrl_d

    return ANSWERS[ans]



