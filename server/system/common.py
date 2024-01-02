

def fprint(message):
    print(message, flush=True)


def ensure_set(input_arg):
    """
    Ensure the input argument is a set. If the argument is a string or a list, it's converted into a set.
    If the argument is of any other type, a TypeError is raised.

    :param input_arg: The input argument, can be a string or a list.
    :return: A set based on the input argument.
    :raises TypeError: If input_arg is not a string or a list.
    """
    if isinstance(input_arg, str):
        # Convert string to a set with the string as a single element
        return {input_arg}
    elif isinstance(input_arg, list):
        # Convert list to a set
        return set(input_arg)
    else:
        # Raise TypeError if input_arg is neither a string nor a list
        raise TypeError("Input argument must be a string or a list")

