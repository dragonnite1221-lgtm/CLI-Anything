# ruff: noqa: F403, F405, E501
from ._test_mubu_probe_base import *  # noqa: F403
from ._test_mubu_probe_p0 import BackupLoadingTests, ClientSyncParsingTests, ExtractPlainTextTests, FolderNormalizationTests, SearchTests  # noqa: F401,E501
from ._test_mubu_probe_p1 import DocumentMetaNormalizationTests, LinkExtractionTests  # noqa: F401,E501
from ._test_mubu_probe_p2 import PathResolutionTests  # noqa: F401,E501
from ._test_mubu_probe_p3 import DocumentMetadataOverlayTests  # noqa: F401,E501
from ._test_mubu_probe_p4 import DailySelectionTests, DocumentNodeListingTests  # noqa: F401,E501
from ._test_mubu_probe_c0 import _WritePathTestsMixin0  # noqa: F401
from ._test_mubu_probe_c1 import _WritePathTestsMixin1  # noqa: F401
from ._test_mubu_probe_c2 import _WritePathTestsMixin2  # noqa: F401


class WritePathTests(_WritePathTestsMixin0, _WritePathTestsMixin1, _WritePathTestsMixin2, unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
