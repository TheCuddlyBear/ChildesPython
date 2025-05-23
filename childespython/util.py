import os

def tokenize(text, list_of_strings_to_be_ignored = [",", ".", "?", "!", "(.)", "[?]"]):
    """
    Split text into tokens, stripping any trailing or leading ignore_list items.
    Preserves original case of tokens and skips empty tokens.

    Parameters:
        text (str): input string to tokenize
        list_of_strings_to_be_ignored (list of str): list of substrings to strip from tokens edges

    Returns:
        cleaned token (str)
    """

    for raw in text.split():
        cleaned = raw
        # Strip repeatedly from start and end if any ignore_list item matches
        stripping = True
        while stripping and cleaned:
            stripping = False
            for ign in list_of_strings_to_be_ignored:
                if cleaned.startswith(ign):
                    cleaned = cleaned[len(ign):]
                    stripping = True
                if cleaned.endswith(ign):
                    cleaned = cleaned[:-len(ign)]
                    stripping = True

        # Skip empty tokens or those without alphanumerics
        if cleaned and any(c.isalnum() for c in cleaned):
            yield cleaned

def get_recording_by_recording_name(path, corpus_name: str, child_name: str, recording_name: str):
    """
    Retrieves the raw lines of a CHILDES transcript file given its corpus, child, and recording names.

    Parameters:
        corpus_name (str): The name of the CHILDES corpus (e.g., "Schaerlaekens").
        child_name (str): The identifier for the child participant (e.g., "Gijs").
        recording_name (str): The filename of the transcript (e.g., "021023.cha").

    Returns:
        list of str or None
        If successful, returns a list of lines (strings) from the transcript file.
        Returns None if the file is not found or an error occurs while reading.

    """
    # Build the file path
    file_path = os.path.join(path, corpus_name, child_name, recording_name)

    # Open the file and read its contents
    try:
        with open(file_path, "r") as my_file:
            return my_file.readlines()  # Returns a list of lines in the file
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None