import pytest

from src.animation.lms_scene import Narration
from src.animation.timing import NarrationTimingStore, Word, estimate_duration
from src.subtitles.srt_generator import srt_time, write_srt
from src.subtitles.subtitle_config import SubtitleSettings, build_cues
from src.subtitles.vtt_generator import write_vtt
from src.subtitles.whisper_alignment import estimated_alignment, fill_missing_times, sentences_from_words

TEXT = "Natural numbers never include zero. They count things!"
WORDS = [
    {"word": w, "start": s, "end": e}
    for w, s, e in [("Natural", 0.1, 0.5), ("numbers", 0.55, 0.9), ("never", 1.0, 1.2), ("include", 1.25, 1.6),
                    ("zero.", 1.7, 2.0), ("They", 2.4, 2.55), ("count", 2.6, 2.9), ("things!", 2.95, 3.3)]
]
TIMING = {"n1": {"duration": 3.4, "words": WORDS, "sentences": sentences_from_words(TEXT, WORDS)}}


def test_sentence_timestamps_from_words():
    sentences = TIMING["n1"]["sentences"]
    assert [s["text"] for s in sentences] == ["Natural numbers never include zero.", "They count things!"]
    assert (sentences[0]["start"], sentences[0]["end"]) == (0.1, 2.0)
    assert (sentences[1]["start"], sentences[1]["end"]) == (2.4, 3.3)


def test_word_timestamps_are_filled_when_missing():
    words = fill_missing_times([{"word": "a", "start": 0.0, "end": 0.2}, {"word": "1,", "start": None, "end": None},
                                {"word": "b", "start": 0.6, "end": 0.9}], 1.0)
    assert (words[1]["start"], words[1]["end"]) == (0.2, 0.6)


def test_sentence_mode_cues_are_offset_by_timeline():
    cues = build_cues([{"id": "n1", "start": 10.0}], TIMING, {"n1": {"subtitle": True}}, SubtitleSettings())
    assert [(c.start, c.end, c.text) for c in cues] == [
        (10.1, 12.0, "Natural numbers never include zero."),
        (12.4, 13.3, "They count things!"),
    ]


def test_word_mode_cues():
    cues = build_cues([{"id": "n1", "start": 0.0}], TIMING, {"n1": {"subtitle": True}}, SubtitleSettings(mode="word"))
    assert len(cues) == 8 and cues[4].text == "zero." and cues[4].start == 1.7


def test_subtitle_flag_and_long_sentence_split():
    assert build_cues([{"id": "n1", "start": 0}], TIMING, {"n1": {"subtitle": False}}, SubtitleSettings()) == []
    cues = build_cues([{"id": "n1", "start": 0}], TIMING, {"n1": {"subtitle": True}}, SubtitleSettings(max_chars=20))
    assert all(len(c.text) <= 20 for c in cues) and len(cues) > 2


def test_srt_and_vtt_output(tmp_path):
    cues = build_cues([{"id": "n1", "start": 61.5}], TIMING, {"n1": {"subtitle": True}}, SubtitleSettings())
    srt = write_srt(cues, tmp_path / "x.srt").read_text(encoding="utf-8")
    vtt = write_vtt(cues, tmp_path / "x.vtt").read_text(encoding="utf-8")
    assert srt.startswith("1\n00:01:01,600 --> 00:01:03,500\nNatural numbers never include zero.\n")
    assert "\n2\n00:01:03,900 --> 00:01:04,800\nThey count things!" in srt
    assert vtt.startswith("WEBVTT\n\n00:01:01.600 --> 00:01:03.500\nNatural numbers never include zero.\n")
    assert srt_time(3725.0421) == "01:02:05,042"


def test_settings_validation():
    assert SubtitleSettings.from_dict({"format": "srt"}).formats == ["srt"]
    with pytest.raises(ValueError):
        SubtitleSettings.from_dict({"mode": "karaoke"})
    with pytest.raises(ValueError):
        SubtitleSettings.from_dict({"formats": ["ass"]})


def test_word_offset_for_animation_sync():
    n = Narration("n1", TEXT, "teacher_a", None, True, 0.25, start=5.0, duration=3.4,
                  words=[Word(w["word"], w["start"], w["end"]) for w in WORDS])
    assert n.word_offset("zero") == 1.7
    assert n.word_offset("count things") == 2.6
    assert n.end == 8.4
    with pytest.raises(ValueError, match="not in narration"):
        n.word_offset("fractions")


def test_timing_store_uses_real_audio_or_estimates():
    store = NarrationTimingStore("render", {"n1": TIMING["n1"]})
    duration, words, estimated = store.lookup("n1", TEXT)
    assert (duration, len(words), estimated) == (3.4, 8, False)
    standalone = NarrationTimingStore()
    duration, words, estimated = standalone.lookup("other", "One two three four five")
    assert estimated and duration == estimate_duration("One two three four five")
    with pytest.raises(RuntimeError, match="has no generated audio"):
        store.lookup("missing", "text")


def test_estimated_alignment_fallback():
    data = estimated_alignment(TEXT, 4.0)
    assert data["method"] == "estimated" and len(data["words"]) == 8 and len(data["sentences"]) == 2
