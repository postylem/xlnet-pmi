"""
Gets dependency information from CONLL data
ParseDistanceTask closely based on structural-probes/task.py by John Hewitt
"""

import torch


class Task:
    """Abstract class representing a linguistic task
    mapping texts to labels."""

    @staticmethod
    def labels(observation):
        """Maps an observation to a matrix of labels.
        Should be overriden in implementing classes.
        """
        raise NotImplementedError


class LinearBaselineTask(Task):
    """
    Ignores everything but observation length,
    and maps observations to simple string-distance matrix as baseline
    """

    @staticmethod
    def labels(observation):
        """Maps observation to a torch tensor of distance labels
        corresponding to linear distance L to R in the string.

        Args:
            observation: a single Observation class for a sentence:
        Returns:
            A torch tensor of shape (sentence_length, sentence_length)
            of distances in the parse tree which simply increase with
            position in the string.
        """
        # All observation fields must be of same length
        sentence_length = len(observation[0])
        distances = torch.zeros((sentence_length, sentence_length))
        for i in range(sentence_length):
            for j in range(i, sentence_length):
                i_j_distance = abs(i-j)  # = distance in the string
                distances[i][j] = i_j_distance
                distances[j][i] = i_j_distance
        return distances


class RandomBaselineTask(Task):
    """
    Ignores everything, creates random matrix as baseline
    """

    @staticmethod
    def labels(observation):
        """Maps observation to a torch random tensor of distance labels.

        Args:
            observation: a single Observation class for a sentence:
        Returns:
            A torch tensor of shape (sentence_length, sentence_length)
            of distances in the parse tree which simply increase with
            position in the string.
        """
        # All observation fields must be of same length
        sentence_length = len(observation[0])
        distances = torch.rand((sentence_length, sentence_length))
        return distances


class ParseDistanceTask(Task):
    """Maps observations to dependency parse distances between words."""

    @staticmethod
    def labels(observation):
        """Computes the distances between all pairs of words;
        returns them as a torch tensor.

        Args:
            observation: a single Observation class for a sentence:
        Returns:
            A torch tensor of shape (sentence_length, sentence_length)
            of distances in the parse tree as specified by the
            observation annotation.
        """
        # All observation fields must be of same length
        sentence_length = len(observation[0])
        distances = torch.zeros((sentence_length, sentence_length))
        for i in range(sentence_length):
            for j in range(i, sentence_length):
                i_j_distance = ParseDistanceTask.distance_between_pairs(
                    observation, i, j)
                distances[i][j] = i_j_distance
                distances[j][i] = i_j_distance
        return distances

    @staticmethod
    def distance_between_pairs(observation, i, j, head_indices=None):
        '''Computes path distance between a pair of words

        Args:
            observation: an Observation namedtuple, with a head_indices field.
                    or None, if head_indices != None
            i: one of the two words to compute the distance between.
            j: one of the two words to compute the distance between.
            head_indices: the head indices (according to a dependency parse)
                of all words, or None, if observation != None.

        Returns:
            The integer distance d_path(i,j)
        '''
        if i == j:
            return 0
        if observation:
            head_indices = []
            number_of_underscores = 0
            for elt in observation.head_indices:
                if elt == '_':
                    head_indices.append(0)
                    number_of_underscores += 1
                else:
                    head_indices.append(int(elt) + number_of_underscores)
        i_path = [i+1]
        j_path = [j+1]
        i_head = i+1
        j_head = j+1
        while True:
            if not (i_head == 0 and (i_path == [i+1] or i_path[-1] == 0)):
                i_head = head_indices[i_head - 1]
                i_path.append(i_head)
            if not (j_head == 0 and (j_path == [j+1] or j_path[-1] == 0)):
                j_head = head_indices[j_head - 1]
                j_path.append(j_head)
            if i_head in j_path:
                j_path_length = j_path.index(i_head)
                i_path_length = len(i_path) - 1
                break
            elif j_head in i_path:
                i_path_length = i_path.index(j_head)
                j_path_length = len(j_path) - 1
                break
            elif i_head == j_head:
                i_path_length = len(i_path) - 1
                j_path_length = len(j_path) - 1
                break
        total_length = j_path_length + i_path_length
        return total_length
