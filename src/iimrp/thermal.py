import time
import numpy as np

# Heat Management Constants
HEAT_INCREASE = 1/90 # Heat increase per unit time
HARMONICS_SCALAR = 1 # Scalar dependent on harmonics_score
HEAT_DISSIPATION = HEAT_INCREASE/2  # Heat dissipation per unit time
OVERHEATING_RISK = 90 # Estimated high risk of overheating
COOLING_PERIOD = 90 # Time for a note to cool down after being turned off

class MRPNoteHeatMonitor:
    """
    A class to estimate the thermal state of an MRP note.
    This is an 'unverified' prototype of a 'heat monitor' for the MRP.
    It is simulation-based, i.e. it does not use any real temperature data.

    Attributes
    ----------
    midi_number : int
        The MIDI number of the note.
    heat_score : float
        The heat score of the note.
    last_played : float
        The timestamp of the last time the note was played.
    """

    def __init__(self, midi_number):
        """
        Constructs all the necessary attributes for the note object.

        Parameters
        ----------
        midi_number : int
            The MIDI number of the note.
        """
        self.start_time = time.time()
        self.midi_number = midi_number
        self.heat_score = 0
        self.last_played = self.start_time
        self.is_eligible = True

    def calculate_harmonics_score(self, harmonics_array):
        """
        Calculate the harmonics score based on the given array of harmonics.

        Parameters
        ----------
        harmonics_array : numpy.array
            The array of harmonics being played.

        Returns
        -------
        float
            The calculated harmonics score.
        """
        return np.dot((len(harmonics_array) - np.arange(len(harmonics_array))), harmonics_array)

    def update_heat_score_on(self, harmonics_array, current_time=None):
        """
        Update the heat score for the note when it is being played.

        Parameters
        ----------
        harmonics_array : numpy.array
            The array of harmonics being played.
        """
        if current_time is None:
            current_time = time.time()
        time_diff = current_time - self.last_played
        heat_increase_amount = HEAT_INCREASE * time_diff
        harmonics_scaling = HARMONICS_SCALAR * self.calculate_harmonics_score(harmonics_array)
        # heat_score_prev = self.heat_score
        self.heat_score += heat_increase_amount * harmonics_scaling
        # heat_score_diff = self.heat_score - heat_score_prev
        # print(f"increase {heat_increase_amount:.4f} * harmonics {harmonics_scaling:.4f} = heat_score: {self.heat_score:.4f}, time_diff: {time_diff:.4f}")
        self.last_played = current_time

    def update_heat_score_off(self, current_time=None):
        """
        Update the heat score for the note when it is not being played.
        """
        if current_time is None:
            current_time = time.time()
        if self.heat_score > 0:
            time_diff = current_time - self.last_played
            heat_score_prev = self.heat_score
            self.heat_score -= HEAT_DISSIPATION * time_diff
            heat_score_diff = self.heat_score - heat_score_prev
            # print(f"heat_score: {self.heat_score:.1f} heat_score_diff: {heat_score_diff:.1f} time_diff: {time_diff:.1f}")
            if self.heat_score < 0:
                self.heat_score = 0
        # self.last_played = current_time

    def check_eligibility(self, current_time=None):
        """
        Check if the note is eligible to be played.

        Returns
        -------
        bool
            True if the note is eligible to be played, False otherwise.
        """
        if current_time is None:
            current_time = time.time()
        time_diff = current_time - self.last_played
        # print(f"heat_score: {self.heat_score:.1f}, time_diff: {time_diff:.1f}")
        if self.heat_score > OVERHEATING_RISK:
            self.last_played = current_time + COOLING_PERIOD
            self.is_eligible = False
            # print(f"RESULT self.heat_score > OVERHEATING_RISK: {self.heat_score} > {OVERHEATING_RISK}")
        elif time_diff > COOLING_PERIOD:
            self.is_eligible = False
            # print(f"RESULT time_diff > COOLING_PERIOD: {time_diff} < {COOLING_PERIOD}")
        else:
            self.is_eligible = True
            # print(f"RESULT heat_score is less than OVERHEATING_RISK and time_diff is less than COOLING_PERIOD")
        return self.is_eligible

