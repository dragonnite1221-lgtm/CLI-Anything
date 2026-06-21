# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def sine_wav(tmp_dir):
    """Create a 1-second 440Hz sine wave WAV file (mono, 44100Hz, 16-bit)."""
    path = os.path.join(tmp_dir, "sine_440.wav")
    samples = generate_sine_wave(440, 1.0, 44100, 0.5, 1)
    write_wav(path, samples, 44100, 1, 16)
    return path


@pytest.fixture
def stereo_wav(tmp_dir):
    """Create a 2-second stereo WAV file with different tones L/R."""
    path = os.path.join(tmp_dir, "stereo.wav")
    # Left channel: 440Hz, Right channel: 880Hz
    duration = 2.0
    sr = 44100
    n = int(duration * sr)
    samples = []
    for i in range(n):
        t = i / sr
        left = 0.4 * math.sin(2 * math.pi * 440 * t)
        right = 0.4 * math.sin(2 * math.pi * 880 * t)
        samples.append(left)
        samples.append(right)
    write_wav(path, samples, sr, 2, 16)
    return path


@pytest.fixture
def silence_wav(tmp_dir):
    """Create a 3-second silence WAV file."""
    path = os.path.join(tmp_dir, "silence.wav")
    samples = generate_silence(3.0, 44100, 1)
    write_wav(path, samples, 44100, 1, 16)
    return path


@pytest.fixture
def short_wav(tmp_dir):
    """Create a 0.5-second 1kHz sine wave."""
    path = os.path.join(tmp_dir, "short_1k.wav")
    samples = generate_sine_wave(1000, 0.5, 44100, 0.7, 1)
    write_wav(path, samples, 44100, 1, 16)
    return path


def _read_wav_numpy(path):
    """Read a WAV file into a numpy array for analysis."""
    samples, sr, ch, bd = read_wav(path)
    return np.array(samples), sr, ch, bd


class TestWavIO:
    def test_write_read_roundtrip_16bit(self, tmp_dir):
        path = os.path.join(tmp_dir, "rt16.wav")
        original = generate_sine_wave(440, 0.1, 44100, 0.5, 1)
        write_wav(path, original, 44100, 1, 16)
        loaded, sr, ch, bd = read_wav(path)
        assert sr == 44100
        assert ch == 1
        assert bd == 16
        assert abs(len(loaded) - len(original)) <= 1
        # Check correlation (should be very high)
        min_len = min(len(original), len(loaded))
        corr = np.corrcoef(original[:min_len], loaded[:min_len])[0, 1]
        assert corr > 0.99

    def test_write_read_roundtrip_stereo(self, tmp_dir):
        path = os.path.join(tmp_dir, "rt_stereo.wav")
        samples = generate_sine_wave(440, 0.1, 44100, 0.5, 2)
        write_wav(path, samples, 44100, 2, 16)
        loaded, sr, ch, bd = read_wav(path)
        assert ch == 2
        assert abs(len(loaded) - len(samples)) <= 2

    def test_write_read_roundtrip_24bit(self, tmp_dir):
        path = os.path.join(tmp_dir, "rt24.wav")
        original = generate_sine_wave(440, 0.1, 44100, 0.5, 1)
        write_wav(path, original, 44100, 1, 24)
        loaded, sr, ch, bd = read_wav(path)
        assert bd == 24
        min_len = min(len(original), len(loaded))
        corr = np.corrcoef(original[:min_len], loaded[:min_len])[0, 1]
        assert corr > 0.99

    def test_wav_file_properties(self, sine_wav):
        with wave.open(sine_wav, "r") as wf:
            assert wf.getframerate() == 44100
            assert wf.getnchannels() == 1
            assert wf.getsampwidth() == 2
            duration = wf.getnframes() / wf.getframerate()
            assert abs(duration - 1.0) < 0.01

    def test_stereo_wav_properties(self, stereo_wav):
        with wave.open(stereo_wav, "r") as wf:
            assert wf.getnchannels() == 2
            duration = wf.getnframes() / wf.getframerate()
            assert abs(duration - 2.0) < 0.01
