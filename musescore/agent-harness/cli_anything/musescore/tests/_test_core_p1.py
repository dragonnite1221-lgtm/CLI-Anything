# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestKeySignature:
    def test_major_keys(self):
        assert key_name_to_int("C") == 0
        assert key_name_to_int("C major") == 0
        assert key_name_to_int("G") == 1
        assert key_name_to_int("Db") == -5
        assert key_name_to_int("Db major") == -5
        assert key_name_to_int("F#") == 6

    def test_minor_keys(self):
        assert key_name_to_int("A minor") == 0
        assert key_name_to_int("Am") == 0
        assert key_name_to_int("D minor") == -1
        assert key_name_to_int("F# minor") == 3

    def test_case_insensitive(self):
        assert key_name_to_int("c major") == 0
        assert key_name_to_int("DB MAJOR") == -5
        assert key_name_to_int("am") == 0

    def test_invalid_key(self):
        with pytest.raises(ValueError, match="Unrecognized key"):
            key_name_to_int("X major")

    def test_int_to_name(self):
        assert key_int_to_name(0) == "C major"
        assert key_int_to_name(-5) == "Db major"
        assert key_int_to_name(0, minor=True) == "A minor"

    def test_all_major_keys_roundtrip(self):
        for i, name in KEY_INT_TO_MAJOR.items():
            assert key_name_to_int(name) == i
            assert key_name_to_int(f"{name} major") == i


class TestTranspose:
    def test_semitones_to_interval_unison(self):
        assert semitones_to_interval_index(0) == 0  # Perfect Unison

    def test_semitones_to_interval_minor_second(self):
        assert semitones_to_interval_index(1) == 1  # Minor Second

    def test_semitones_to_interval_octave(self):
        assert semitones_to_interval_index(12) == 12  # Perfect Octave

    def test_semitones_to_interval_fifth(self):
        assert semitones_to_interval_index(7) == 7  # Perfect Fifth

    def test_interval_enum_count(self):
        assert len(INTERVAL_ENUM) == 26
