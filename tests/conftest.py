from infrasys import Location
from gdm.distribution import DistributionSystem
from gdm.distribution.components import DistributionReactor, DistributionVoltageSource

import pytest


def _example_gdm_system():
    system = DistributionSystem(auto_add_composed_components=True)
    voltage_source = DistributionVoltageSource.example()
    reactor = DistributionReactor.example()
    reactor.buses[0] = voltage_source.bus
    reactor.buses[1].coordinate = Location(x=20.01, y=30.01)
    system.add_components(voltage_source, reactor)
    return system


@pytest.fixture(scope="session")
def gdm_system():
    return _example_gdm_system()


@pytest.fixture(scope="session")
def gdm_system_2():
    return _example_gdm_system()
