import os

from childespython.transcript import Transcript


class ChildesDataset:
    """
    A class to represent a dataset of CHILDES transcripts.

    Expects folder structure:
    <path>/<corpus_name>/<child_name>/<recording_name>.cha

    Attributes:
        path (str): The path to the directory containing the CHILDES transcripts.
    """

    def __init__(self, path: str):
        """
        Initializes the Dataset with the given parameters.

        Parameters:
            path (str): The path to the directory containing the CHILDES transcripts.
        """
        self.path = path
        self.dataset = dict()

    def load_dataset(self):
        """
        Loads the dataset from the specified path.
        """
        for dir in os.listdir(self.path):
            self.dataset[dir] = dict()
            corpus_path = os.path.join(self.path, dir)
            if os.path.isdir(corpus_path):
                for child in os.listdir(corpus_path):
                    self.dataset[dir][child] = dict()
                    child_path = os.path.join(corpus_path, child)
                    if os.path.isdir(child_path):
                        for recording in os.listdir(child_path):
                            self.dataset[dir][child][recording] = dict()
                            recording_path = os.path.join(child_path, recording)
                            if recording.endswith(".cha"):
                                transcript = Transcript(path=self.path, corpus=dir, child=child, recording=recording)
                                self.dataset[dir][child][recording] = transcript





