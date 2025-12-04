#!/usr/bin/env python3
"""Test script to inspect the MCP tool schemas generated"""

import json
from typing import Annotated
from pydantic import Field, BaseModel

class TestModel(BaseModel):
    limit_float: Annotated[float, Field(default=5.0, ge=1, le=100)] = 5.0
    offset_float: Annotated[float, Field(default=0.0, ge=0)] = 0.0
    object_id_float: float

# Print the JSON schema
schema = TestModel.model_json_schema()
print(json.dumps(schema, indent=2))
