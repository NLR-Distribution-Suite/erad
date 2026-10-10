from infrasys import Location
from gdm.distribution import DistributionSystem
from gdm.distribution.components import DistributionReactor, DistributionVoltageSource

import pytest


def _example_gdm_system():
    system = DistributionSystem(auto_add_composed_components=True)
    reactor = DistributionReactor.example()
    reactor.buses[0].coordinate = Location(x=20.0, y=30.0)
    reactor.buses[1].coordinate = Location(x=20.01, y=30.01)
    system.add_components(DistributionVoltageSource.example(), reactor)
    return system


@pytest.fixture(scope="session")
def gdm_system():
    return _example_gdm_system()


@pytest.fixture(scope="session")
def gdm_system_2():
    return _example_gdm_system()
