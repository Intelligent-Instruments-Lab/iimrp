import time
import pytest
import numpy as np

from ..thermal import *

@pytest.fixture
def setup():
    note = MRPNoteHeatMonitor(60)
    return note

def test_calculate_harmonics_score(setup):
    note = setup
    harmonics_array = np.array([1, 0.5, 0.33, 0.25])
    assert note.calculate_harmonics_score(harmonics_array) == 6.41, f"harmonics_score: {note.calculate_harmonics_score(harmonics_array)}"

def test_update_heat_score_on(setup):
    note = setup
    harmonics_array = np.array([1, 0.5, 0.33, 0.25])
    note.last_played += 1 # Simulate time passing
    note.update_heat_score_on(harmonics_array)
    assert note.heat_score > 0, f"heat_score: {note.heat_score}"

def test_check_eligibility_overheating_risk(setup):
    note = setup
    note.heat_score = OVERHEATING_RISK + 1
    assert note.check_eligibility() == False, f"is_eligible: {note.is_eligible}, should be False"

def test_check_eligibility_cooling_period(setup):
    note = setup
    assert note.check_eligibility() == True, f"is_eligible: {note.is_eligible}, should be True (1/3)"
    note.heat_score = OVERHEATING_RISK + 1
    assert note.check_eligibility() == False, f"is_eligible: {note.is_eligible}, should be False (2/3)"
    time_elapsed = time.time()+COOLING_PERIOD*4+1
    note.update_heat_score_off(current_time=time_elapsed)
    time_diff = time_elapsed - note.last_played
    # print(f"elapsed: {time_elapsed} last_played: {note.last_played} time_diff: {time_diff} heat_score: {note.heat_score}")
    assert note.check_eligibility() == True, f"is_eligible: {note.is_eligible}, should be True (3/3)"

def test_check_eligibility_no_time_passed_with_overheating_risk(setup):
    note = setup
    note.heat_score = OVERHEATING_RISK + 1
    assert note.check_eligibility() == False, f"is_eligible: {note.is_eligible}, should be False"
    assert note.check_eligibility() == False, f"is_eligible: {note.is_eligible}, should be False"

def test_check_eligibility_no_time_passed_without_overheating_risk(setup):
    note = setup
    assert note.check_eligibility() == True, f"is_eligible: {note.is_eligible}, should be True"
    assert note.check_eligibility() == True, f"is_eligible: {note.is_eligible}, should be True"

def test_update_heat_score_off(setup):
    note = setup
    harmonics_array = np.array([1, 0.5, 0.33, 0.25])
    note.update_heat_score_on(harmonics_array)
    time_elapsed = time.time()+COOLING_PERIOD+1
    note.update_heat_score_off(current_time=time_elapsed)
    assert note.heat_score >= 0, f"heat_score: {note.heat_score}"

def test_check_eligibility(setup):
    note = setup
    assert note.check_eligibility() == True, f"is_eligible: {note.is_eligible}"
    note.heat_score = OVERHEATING_RISK + 1
    assert note.check_eligibility() == False, f"is_eligible: {note.is_eligible}"

def test_calculate_harmonics_score_zero(setup):
    note = setup
    harmonics_array = np.array([0, 0, 0, 0])
    assert note.calculate_harmonics_score(harmonics_array) == 0, f"harmonics_score: {note.calculate_harmonics_score(harmonics_array)}"

def test_update_heat_score_on_no_time_passed(setup):
    note = setup
    harmonics_array = np.array([1, 0.5, 0.33, 0.25])
    note.update_heat_score_on(harmonics_array, current_time=note.last_played)
    assert note.heat_score == 6.41, f"heat_score: {note.heat_score}"

def test_update_heat_score_off_no_heat(setup):
    note = setup
    assert note.heat_score == 0, f"heat_score: {note.heat_score}"
    note.update_heat_score_off()
    assert note.heat_score == 0, f"heat_score: {note.heat_score}"
