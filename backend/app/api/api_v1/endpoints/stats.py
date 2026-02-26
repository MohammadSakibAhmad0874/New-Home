from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException

from api import deps
from db import models

router = APIRouter()

# Sensor stats endpoint removed — temperature/humidity feature has been removed.
# This file is kept as a placeholder for future statistics endpoints.
