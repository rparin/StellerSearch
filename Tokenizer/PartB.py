import PartA
import sys


# Time Complexity: O(1); a constant number of operations -- checking whether the inputted argument is valid -- always occurs regardless of the size.
def validateArgv(sysArgvList: list) -> str:
    """validateArgv is the first helper function that runs in partA. It does simple validation of the argument written in the console by checking that
       (1) A file path was provided or (2) two arguments were provided. If two arguments were provided, it will return both file paths.
       The string file paths are located in the first and second index of the argument list [PathB.py, textFilePath1, textFilePath2]

    Args:
        sysArgvList (list): The sys.argv list, which consists of [python, fileName, argument(s)].

    Returns:
        str: The file path.
    """
    if len(sysArgvList) == 1:  # Checks the length of the argument list is 1.
        print("File path was not provided.")
        return
    # Checks if the length of the argument list is 2.
    elif len(sysArgvList) == 2:
        print(
            f"Two arguments are accepted. 1 ({sysArgvList[1]}) was provided.")
    # Checks whether the length of the argument is not equal to 3 (doesn't contain [PathB.py, textFilePath1, textFilePath2]).
    elif len(sysArgvList) != 3:
        multFilesList = sysArgvList[1:]
        print(
            f"Two arguments are accepted. {len(multFilesList)} ({multFilesList}) were provided.")
        return
    # Returns both file paths in a tuple.
    return sysArgvList[1], sysArgvList[2]


if __name__ == "__main__":
    # Executes validateArgv which checks if only two files were inputted.
    sysArgv = validateArgv(sys.argv)
    # Checks if the system argv does not return None (which would occur if an error was found).
    if sysArgv is not None:
        # The tuple containing path1 and path2 are separated.
        path1, path2 = sysArgv
        # Executes tokenize function imported from Part A with path 1 and returns a list of tokens.
        path1TokList = PartA.tokenize(path1)
        # Executes tokenize function imported from Part A with path 2 and returns a list of tokens.
        path2TokList = PartA.tokenize(path2)
        # Checks to see whether there wasn't an error raised when trying to running tokenize. It would return None if there was.
        if path1TokList is not None and path2TokList is not None:
            # Executes the computeWordFrequencies from Part A with path 1 which returns a dictionary of tokens (key) and their frequency (value).
            path1TokDict = PartA.computeWordFrequencies(path1TokList)
            # Executes the computeWordFrequencies from Part A with path 2 which returns a dictionary of tokens (key) and their frequency (value).
            path2TokDict = PartA.computeWordFrequencies(path2TokList)
            # Combines path 1's dictionary and path 2's dictionary into one set, which gets ride of repeated keys from the intersected set of both. We then print the length of the combined set of keys.
            print(len(set(path1TokDict.keys()).intersection(set(path2TokDict.keys()))))
