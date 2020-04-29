#!/usr/bin/env python3

def get_best_phonem_combos(target, subtitles):
    """
    Returns the best phonem sequences in subtitles and returns its indexes

    Arguments:
    - target: array of phonems to match in subtitles
    - subtitles: array of phonems (should be longer than target)

    Returns:
    an array of array of tuples (x, y) where:
        - x is the starting position of a phonem sequence
        - y is the length of the phonem sequence

    Raises:
    Exception if a phonem in target is not found in the subtitles

    Example:
    (imagine that target and subtitles are arrays)
    target = SalutCaVa
    subtitles = WeshCamaradeSalutCommentVaSalutations
    The program returns [
                            [(12, 5), (26, 5)], -> References of Salut in subtiles
                            [(4, 2)], -> References of Ca in subtitles
                            [(24, 2)] -> References of Va in subtitles
                        ]
    """

    if target == []:
        return []

    # Finds the longest phonem sequence in subtitles matching with a seqeunce in target
    found, index_found = _longestSubstringFinder(target, subtitles)

    if index_found == -1:
        raise Exception("Error, phonems", target, "not found in given subtitles")

    # Recursively launches the function on remaining left and right phonems
    left_tab = get_best_phonem_combos(target[:index_found], subtitles)
    right_tab = get_best_phonem_combos(target[index_found+len(found):], subtitles)

    # Concatenates all the results in the proper order
    return_tab = []
    if left_tab:
        return_tab.append(left_tab)

    return_tab.append(_matchings(subtitles, found))

    if right_tab:
        return_tab.append(right_tab)

    return return_tab

def _longestSubstringFinder(target, subtitles):
    """
    This function finds the longest common substring between target and subtitles arrays

    Returns: tuple containing found sequence and index of first phonem
    """

    answer = []
    answer_start_index_target = -1

    for i in range(len(target)):
        for j in range(len(subtitles)):
            match = []
            # Find a common first phonem in the two arrays
            if target[i] == subtitles[j]:
                # Now iterates to find the longest common sequence from this first phonem
                match_index = i
                for k in range(min(len(subtitles)-j, len(target)-i)):
                    if target[i+k] == subtitles[j+k]:
                        match.append(target[i+k])
                    else:
                        break

                # If the sequence is the longest, updates variables
                if len(match) > len(answer):
                    answer = match
                    answer_start_index_target = match_index

    return answer, answer_start_index_target

def _matchings(subtitles, found):
    """
    This function finds in subtitles all the occurences of sequence "found"

    Returns:
    an array containing tuples of seuqence's first phonem index and phonem sequence length
    """

    found_tab = []
    for i in range(len(subtitles)):
        if subtitles[i] == found[0]:
            if subtitles[i:i+len(found)] == found:
                found_tab.append((i, len(found)))
    return found_tab
