# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p0 import PlainTextExtractionTests, HtmlConversionTests, NodeIdGenerationTests, NodePathConversionTests, NodeIterationTests, ResolveNodeAtPathTests, SerializeNodeTests  # noqa: F401,E501
from ._test_core_p1 import FolderIndexTests, DailyTitleTests, NormalizationHelperTests, TimestampConversionTests, DefaultPathDiscoveryTests, DedupeLatestRecordsTests, AmbiguousErrorMessageTests, EnrichDocumentMetaTests  # noqa: F401,E501


if __name__ == "__main__":
    unittest.main()
