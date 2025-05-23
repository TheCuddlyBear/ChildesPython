import math

from childespython.util import get_recording_by_recording_name, tokenize


class Transcript:
    """
    A class to represent a CHILDES transcript.
    This class provides methods to read and process a CHILDES transcript file,
    extracting relevant information such as participants, age, and structured utterances.
    Attributes:
        path (str): The base path where the corpus is located.
        corpus (str): The name of the CHILDES corpus (e.g., "Schaerlaekens").
        child (str): The identifier for the child participant (e.g., "Gijs").
        recording (list of str): The lines of the transcript file.
    Methods:
        get_cleaned_transcript(): Returns a list of cleaned lines from the transcript file.
        get_participants_and_age(): Returns a dictionary with participant information and child's age.
        get_age_in_days(): Returns the child's age in days.
        get_participant_tiers_markers(): Returns a list of participant tiers markers.
        get_structured_transcript(): Returns a structured representation of the transcript.
    """
    def __init__(self, path: str, corpus: str, child: str, recording: str):
        """
        Initializes the Transcript object with the path to the transcript file.

        Parameters:
            path (str): The base path where the corpus is located.
            corpus (str): The name of the CHILDES corpus (e.g., "Schaerlaekens").
            child (str): The identifier for the child participant (e.g., "Gijs").
            recording (str): The filename of the transcript (e.g., "021023.cha").
        """
        self.path: str = path
        self.corpus: str = corpus
        self.child: str = child
        self.recording: str = get_recording_by_recording_name(path=path, corpus_name=corpus, child_name=child, recording_name=recording)

    def get_cleaned_transcript(self) -> list:
        """
        Retrieves the cleaned transcript lines from the specified CHILDES transcript file.

        Returns:
            list of str: A list of cleaned lines from the transcript file.
        """
        cleaned_up_transcript = []
        for line in self.recording:
            line = line.strip()
            if line.startswith("@") or line.startswith("*") or line.startswith("%"):
                cleaned_up_transcript.append(line)
            else:
                if cleaned_up_transcript:
                    cleaned_up_transcript[-1] += " " + line
                else:
                    cleaned_up_transcript.append(line)
        return cleaned_up_transcript

    def get_participants_and_age(self) -> dict:
        """
            Extracts participant information and the child's age from the transcript header.
            Returns:
                dict: A dictionary with keys "participants" and "age" containing corresponding information.
            """
        cleaned_up_transcript = self.get_cleaned_transcript()

        participants_line = [line for line in cleaned_up_transcript if line.startswith("@Participants")]
        participants = participants_line[0].split('\t', 1)[1]  # Split at the first tab only and take the second element

        age_line = [line for line in cleaned_up_transcript if line.startswith("@ID") and ";" in line]
        age = [bit for bit in age_line[0].split("|") if ";" in bit][0]

        return {"participants": participants, "age": age}

    def get_age_in_days(self) -> int:
        """
        Extracts the child's age in days from the transcript header.

        Returns:
            int: The child's age in days.
        """
        age_in_childes_format = self.get_participants_and_age()["age"]
        return int(age_in_childes_format.split(";")[0]) * 12 * 30 + int(
            age_in_childes_format.split(";")[1].split(".")[0]) * 30 + int(
            age_in_childes_format.split(";")[1].split(".")[1])

    def get_participant_tiers_markers(self) -> list:
        """
        Extracts the participant tiers markers from the transcript header.

        Returns:
            list: A list of participant tiers markers.
        """
        list_of_participants = self.get_participants_and_age()["participants"]
        participant_tiers = ["*" + bit for bit in list_of_participants.split(" ") if len(bit) == 3]
        return participant_tiers

    def get_structured_transcript(self) -> list:
        """
        Processes each line of the transcript to extract the speaker tiers and the dependent tiers.
        Each entry in the returned structured transcript contains a speaker's tier, dependent tiers,
        and a unique utterance ID as an integer.

        Returns:
            list of dict: A list of dictionaries, each containing:
                - "id": an integer starting from 1
                - "speaker's tier": dict with the speaker tier
                - "dependent tiers": dict with dependent tiers
        """
        cleaned_up_transcript = self.get_cleaned_transcript()
        structured_transcript = []
        current_entry = {
            "id": None,
            "speaker's tier": {},
            "dependent tiers": {}
        }

        body_of_transcript = [bit for bit in cleaned_up_transcript if bit.startswith(("*", "%"))]
        id_counter = 1

        for line in body_of_transcript:
            line_parts = line.split('\t', 1)  # Split at the first tab only

            if "*" in line_parts[0]:
                # Save current utterance before starting new one
                if current_entry["speaker's tier"]:
                    structured_transcript.append(current_entry)
                    id_counter += 1
                    current_entry = {
                        "id": id_counter,
                        "speaker's tier": {},
                        "dependent tiers": {}
                    }
                current_entry["speaker's tier"] = {line_parts[0].strip(":"): line_parts[1]}

            elif "%" in line_parts[0]:
                current_entry["dependent tiers"].update(
                    {line_parts[0].strip(":"): line_parts[1]}
                )

        # Append the final utterance
        if current_entry["speaker's tier"] or current_entry["dependent tiers"]:
            structured_transcript.append(current_entry)

        return structured_transcript

    def get_word_mlu(self, speaker, list_of_strings_to_be_ignored=[",", ".", "?", "!", "(.)", "[?]"]):
        """
       Returns a dictionary containing the word MLU and the standard deviation of the word MLU.

        Parameters:
            speaker (str): The speaker whose utterances and morphemes are being processed.
            list_of_strings_to_be_ignored (list, optional): List of strings to ignore in both word and morpheme counts.

        Returns:
            dict: A dictionary containing the word MLU and the standard deviation of the word MLU.
        """
        # Filter the structured transcript to get only the entries for the given speaker
        structured_transcript = self.get_structured_transcript()
        structured_transcript_filtered_by_speaker = [element for element in structured_transcript if
                                                     speaker in element["speaker's tier"]]

        total_words = 0
        total_utterances = 0
        word_mlus = []  # List to store MLU values for each utterance

        for element in structured_transcript_filtered_by_speaker:
            # Get the utterance from the speaker's tier
            utterance = element["speaker's tier"][speaker]

            # Clean up the utterance by removing unwanted strings
            utterance = utterance.replace("[: ", "[:")  # Replaces [: x] with [;x]
            list_of_words = utterance.split()  # Split by whitespace to get words

            # Exclude words in the ignore list
            list_of_words = [word for word in list_of_words if word not in list_of_strings_to_be_ignored]

            # Exclude experimenter markings like [: or [*] without removing them
            list_of_words = [word for word in list_of_words if not word.startswith(("[:", "[*"))]

            # Count words
            total_words += len(list_of_words)

            # Increment utterance count
            total_utterances += 1

            # Store the MLU for this utterance
            word_mlus.append(len(list_of_words))

        # Calculate word MLU (Mean Length of Utterance)
        word_mlu = round(total_words / total_utterances, 2) if total_utterances > 0 else 0

        # Calculate the standard deviation
        if len(word_mlus) > 1:
            mean_mlu = sum(word_mlus) / len(word_mlus)
            variance = sum((x - mean_mlu) ** 2 for x in word_mlus) / len(word_mlus)
            std_dev = round(math.sqrt(variance), 2)
        else:
            std_dev = 0  # If there's only one utterance, no variability exists

        # Return the dictionary with word MLU and standard deviation
        return {
            "word mlu": word_mlu,
            "word mlu standard deviation": std_dev
        }

    def get_frequencies(self, speaker="*CHI", tier="utterance", pattern=None, match_type="contains"):
        """
        Returns a dictionary with the frequency of each token in the specified tier for the given speaker.
        The tokens are filtered based on the specified pattern and match type.
        :param speaker: The speaker whose utterances are being processed.
        :param tier: The tier to analyze (e.g., "utterance", "dependent tiers").
        :param pattern: The pattern to filter tokens (e.g., a specific word or phrase).
        :param match_type: The type of match to perform (e.g., "startswith", "contains", "endswith", "equals").
        :return: A dictionary with tokens as keys and their frequencies as values.
        """
        structured_transcript = self.get_structured_transcript()
        word_counts = {}

        if pattern and match_type not in {"startswith", "contains", "endswith", "equals"}:
            raise ValueError("match_type must be one of: 'startswith', 'contains', 'endswith', 'equals'")

        filtered_segments = []
        for el in structured_transcript:
            if "speaker's tier" in el and speaker in el["speaker's tier"]:
                filtered_segments.append(el)

        for el in filtered_segments:
            if tier == "utterance":
                text = el["speaker's tier"][speaker]
            else:
                if "dependent tiers" in el and tier in el["dependent tiers"]:
                    text = el["dependent tiers"][tier]
                else:
                    text = ""

            for token in tokenize(text):
                if pattern:
                    if match_type == "startswith" and not token.startswith(pattern):
                        continue
                    elif match_type == "contains" and pattern not in token:
                        continue
                    elif match_type == "endswith" and not token.endswith(pattern):
                        continue
                    elif match_type == "equals" and token != pattern:
                        continue

                if token in word_counts:
                    word_counts[token] += 1
                else:
                    word_counts[token] = 1

        return dict(sorted(word_counts.items(), key=lambda item: item[1], reverse=True))

    def compute_ttr_from_frequencies(frequency_dictionary):
        """
        Compute the Type-Token Ratio (TTR) from a frequency dictionary.

        The TTR is calculated as the number of unique items (types) divided by the total number of items (tokens). This function
        can be applied to frequency counts of any linguistic units (e.g., words, morphological tags, POS tags).

        Parameters:
            frequency_dictionary (dict): A dictionary where keys are unique items and values are their respective frequencies.

        Returns:
            float: The Type-Token Ratio (TTR), a value between 0 and 1. Returns 0 if the frequency dictionary is empty.
        """
        num_types = len(frequency_dictionary)
        num_tokens = sum(frequency_dictionary.values())

        return round(num_types / num_tokens, 2) if num_tokens > 0 else 0