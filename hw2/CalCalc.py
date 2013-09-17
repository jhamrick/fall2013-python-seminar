import argparse
import urllib2
import xml.etree.ElementTree as ET
import warnings
import re


def ask_wolframalpha(query):
    """Send a query to WolframAlpha, and return the plaintext result.

    Parameters
    ----------
    query : str
        The query to sent to WolframAlpha

    Returns
    -------
    str : the response from WolframAlpha

    """

    # quote the input (e.g., replacing spaces by %20)
    quoted = urllib2.quote(query)
    url = ("http://api.wolframalpha.com/v2/query?"
           "input=%s"
           "&appid=UAGAWR-3X6Y8W777Q"
           "&format=plaintext" % quoted)
    # send the query to wolfram alpha and get the response
    handler = urllib2.urlopen(url)
    response = handler.read()
    handler.close()

    # parse the response xml to find the result
    root = ET.fromstring(response)
    if root.get('success') != 'true':
        raise RuntimeError("WolframAlpha request failed")
    result = [x.find("subpod").find("plaintext").text
              for x in root if x.get('title') == "Result"]

    # make sure we got exactly one result
    if len(result) == 0:
        raise RuntimeError("no results returned")
    if len(result) > 1:
        raise RuntimeError(
            "got multiple results, but expected only one: %s" % result)

    # convert the string from unicode
    text = result[0].encode('utf-8')
    # replace multiplication unicode character
    text = re.sub(ur"\xc3\x97", "x", text)

    return text


def str2float(string):
    """Convert a string to a float.

    This function should work even if the string is in scientific
    notation and even if it includes units afterwards, e.g.:

    >>> str2float("1.2x10^-7 kg")
    1.2e-07

    Parameters
    ----------
    string : str
        The string to convert

    Result
    ------
    float

    """
    try:
        # just try to convert it, maybe it will work
        out = float(string)

    except ValueError:
        # match a number at the beginning of the string that uses
        # scientific notation of the form 1.2x10^4
        string = string.split(" ")[0]
        match_num = re.match(ur"((-?\d+(\.\d+)?)(x10\^-?\d+)?)$", string)
        if not match_num:
            raise ValueError(
                "could not convert string to float: %s" % string)

        # replace "x10^" with "e"
        fnum = re.sub(ur"x10\^", "e", match_num.group(1))

        # convert to a float
        out = float(fnum)

    return out


def calculate(string, return_float=False):
    """Evaluate a command in a (relatively) safe manner. If the command is
    something complicated, this function will attempt to ask
    WolframAlpha for an answer.

    Parameters
    ----------
    string : str
        Command to evaluate
    return_float : bool (default=False)
        Whether to return the result as a float

    Returns
    -------
    The result of the evaluation

    """
    # make sure we can't use special commands, like __import__
    if "__" in string:
        raise ValueError("invalid command: %s" % string)

    try:
        # evaluate the string but don't include any globals or
        # builtins, to help avoid code from being executed arbitrarily
        answer = eval(string, {'__builtins__': {}})

    except SyntaxError:
        warnings.warn("Python evaluation failed, asking Wolfram Alpha")
        answer = ask_wolframalpha(string)
        if return_float:
            answer = str2float(answer)

    return answer


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "string", help="string to evaluate")
    parser.add_argument(
        "-f", "--float", dest="return_float", action="store_true",
        default=False, help="whether result should be a float")
    args = parser.parse_args()

    # evaluate the command
    print calculate(args.string, return_float=args.return_float)
