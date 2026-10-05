import sumgui;
import sumui;


def test_sumgui_uses_backend_neutral_help_model():
    assert sumgui.HelpCorpus is sumui.HelpCorpus;
    assert sumgui.HelpTopic is sumui.HelpTopic;


def test_help_order_is_identical_for_gui_consumers():
    topics = [
        sumgui.HelpTopic("SUM", "Math", "sum", ("SUM(...)" ,), "SUM(1, 2)"),
        sumgui.HelpTopic("ABS", "Math", "abs", ("ABS(n)",), "ABS(-1)"),
    ];
    assert sumgui.HelpCorpus("Help", topics).topic_names() == ["ABS", "SUM"];
