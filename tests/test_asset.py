from datetime import datetime

import pytest
from gdm.quantities import Angle
from shapely.geometry import Point, Polygon

from erad.models.asset import AssetState
from erad.models.hazard.wild_fire import FireModel, FireModelArea
from erad.quantities import Speed


def make_fire_model() -> FireModel:
    return FireModel(
        name="test fire",
        timestamp=datetime(2025, 1, 1),
        affected_areas=[
            FireModelArea(
                affected_area=Polygon([(1, -0.5), (2, -0.5), (2, 0.5), (1, 0.5)]),
                wind_speed=Speed(0, "miles/hour"),
                wind_direction=Angle(0, "degree"),
            )
        ],
    )


def test_fire_boundary_distance_is_zero_inside_perimeter():
    state = AssetState(timestamp=datetime(2025, 1, 1))

    state.calculate_fire_vectors(Point(1.5, 0), make_fire_model())

    assert state.fire_boundary_dist is not None
    assert state.fire_boundary_dist.distance.to("kilometer").magnitude == 0


def test_fire_boundary_distance_uses_geodesic_kilometers():
    state = AssetState(timestamp=datetime(2025, 1, 1))

    state.calculate_fire_vectors(Point(0, 0), make_fire_model())

    assert state.fire_boundary_dist is not None
    assert state.fire_boundary_dist.distance.to("kilometer").magnitude == pytest.approx(
        111.319,
        abs=0.01,
    )
