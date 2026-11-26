from tradutor_ao_vivo.live_translator import remove_repeated_prefix


def test_removes_matching_overlap_ignoring_punctuation():
    assert remove_repeated_prefix("we are ready.", "Ready, let's begin") == "let's begin"


def test_keeps_text_when_there_is_no_overlap():
    assert remove_repeated_prefix("first sentence", "different sentence") == "different sentence"


def test_removes_a_fully_repeated_window():
    assert remove_repeated_prefix("the meeting starts now", "the meeting starts now") == ""


def test_keeps_current_text_when_previous_window_is_empty():
    assert remove_repeated_prefix("", "A new meeting starts") == "A new meeting starts"
