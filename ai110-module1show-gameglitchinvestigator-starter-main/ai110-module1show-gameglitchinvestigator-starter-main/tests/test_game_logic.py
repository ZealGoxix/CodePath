from logic_utils import check_guess

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"

def test_high_low_not_reversed():
    # This targets the bug I fixed: the high/low hints used to be backwards.
    # A guess way above the secret must be "Too High", and a guess way below
    # must be "Too Low". If these are swapped, the old bug is back.
    assert check_guess(99, 1) == "Too High"
    assert check_guess(1, 99) == "Too Low"
