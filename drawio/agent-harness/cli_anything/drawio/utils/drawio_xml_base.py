# ruff: noqa: E501
"""Draw.io XML manipulation utilities.

Draw.io files (.drawio) are XML-based, using the mxGraph format.
We manipulate them directly by parsing and modifying the XML tree.

Structure:
    <mxfile>
      <diagram id="..." name="Page-1">
        <mxGraphModel dx="..." dy="..." ...>
          <root>
            <mxCell id="0"/>                     ← root container
            <mxCell id="1" parent="0"/>          ← default layer
            <mxCell id="2" value="Hello"         ← shapes/edges
                    style="rounded=1;..."
                    vertex="1" parent="1">
              <mxGeometry x="10" y="20"
                          width="120" height="60"
                          as="geometry"/>
            </mxCell>
          </root>
        </mxGraphModel>
      </diagram>
    </mxfile>
"""

import os
import time
from xml.etree import ElementTree as ET
from typing import Optional


# ============================================================================
# File I/O
# ============================================================================

__all__ = ["ET", "Optional", "os", "time"]
