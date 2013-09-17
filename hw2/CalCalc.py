import argparse


def calculate(string):
    """Evaluate a command in a (relatively) safe manner.

    Parameters
    ----------
    string : str
        Command to evaluate

    Returns
    -------
    The result of the evaluation

    """
    # make sure we can't use special commands, like __import__
    if "__" in string:
        raise ValueError("invalid command: %s" % string)
    # evaluate the string but don't include any globals or builtins,
    # to help avoid code from being executed arbitrarily
    answer = eval(string, {'__builtins__': {}})
    return answer


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", dest="string", type=str,
        help="string to evaluate")
    args = parser.parse_args()

    # evaluate the command
    print calculate(args.string)
