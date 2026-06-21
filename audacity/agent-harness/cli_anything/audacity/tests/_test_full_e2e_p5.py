# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import tmp_dir  # noqa: F401,E501


class TestSoXAudioE2E:
    """True E2E tests using SoX."""

    def test_generate_sine_tone_wav(self):
        """Generate a sine tone WAV using SoX."""
        from cli_anything.audacity.utils.sox_backend import generate_tone

        with tempfile.TemporaryDirectory() as tmp_dir:
            output = os.path.join(tmp_dir, "tone.wav")
            result = generate_tone(output, frequency=440.0, duration=1.0)

            assert os.path.exists(result["output"])
            assert result["file_size"] > 0
            assert result["method"] == "sox"
            print(f"\n  SoX tone WAV: {result['output']} ({result['file_size']:,} bytes)")

    def test_apply_reverb_effect(self):
        """Generate tone then apply reverb effect using SoX."""
        from cli_anything.audacity.utils.sox_backend import generate_tone, apply_effect

        with tempfile.TemporaryDirectory() as tmp_dir:
            # Generate source tone
            src = os.path.join(tmp_dir, "source.wav")
            generate_tone(src, frequency=440.0, duration=1.0)

            # Apply reverb
            output = os.path.join(tmp_dir, "reverb.wav")
            result = apply_effect(src, output, ["reverb", "50", "50", "100"])

            assert os.path.exists(result["output"])
            assert result["file_size"] > 0
            print(f"\n  SoX reverb: {result['output']} ({result['file_size']:,} bytes)")

    def test_apply_fade_effect(self):
        """Apply fade in/out using SoX."""
        from cli_anything.audacity.utils.sox_backend import generate_tone, apply_effect

        with tempfile.TemporaryDirectory() as tmp_dir:
            src = os.path.join(tmp_dir, "source.wav")
            generate_tone(src, frequency=880.0, duration=2.0)

            output = os.path.join(tmp_dir, "faded.wav")
            result = apply_effect(src, output, ["fade", "t", "0.5", "2.0", "0.5"])

            assert os.path.exists(result["output"])
            assert result["file_size"] > 0
            print(f"\n  SoX fade: {result['output']} ({result['file_size']:,} bytes)")

    def test_generate_different_frequencies(self):
        """Generate tones at different frequencies."""
        from cli_anything.audacity.utils.sox_backend import generate_tone

        with tempfile.TemporaryDirectory() as tmp_dir:
            for freq in [220, 440, 880]:
                output = os.path.join(tmp_dir, f"tone_{freq}hz.wav")
                result = generate_tone(output, frequency=freq, duration=0.5)
                assert os.path.exists(result["output"])
                assert result["file_size"] > 0
                print(f"\n  SoX {freq}Hz tone: {result['output']} ({result['file_size']:,} bytes)")

    def test_convert_sample_rate(self):
        """Convert sample rate using SoX."""
        from cli_anything.audacity.utils.sox_backend import generate_tone, convert_format

        with tempfile.TemporaryDirectory() as tmp_dir:
            src = os.path.join(tmp_dir, "source_44100.wav")
            generate_tone(src, frequency=440.0, duration=1.0, sample_rate=44100)

            output = os.path.join(tmp_dir, "converted_22050.wav")
            result = convert_format(src, output, sample_rate=22050)

            assert os.path.exists(result["output"])
            assert result["file_size"] > 0
            print(f"\n  SoX 44100→22050: {result['output']} ({result['file_size']:,} bytes)")
