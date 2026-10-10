from infrasys import Location
from gdm.distribution import DistributionSystem
from gdm.distribution.components import (
    DistributionBus,
    DistributionReactor,
    DistributionVoltageSource,
)

import pytest


def _example_gdm_system():
    system = DistributionSystem(auto_add_composed_components=True)
    voltage_source = DistributionVoltageSource.example()
    reactor = DistributionReactor.example()
    reactor.buses[0] = voltage_source.bus
    reactor.buses[1].voltage_type = voltage_source.bus.voltage_type
    reactor.buses[1].rated_voltage = voltage_source.bus.rated_voltage
    reactor.buses[1].coordinate = Location(x=20.01, y=30.01)
    system.add_components(voltage_source, reactor)
    connected_buses = {
        bus.uuid
        for component in (voltage_source, reactor)
        for bus in (component.buses if hasattr(component, "buses") else [component.bus])
    }
    for bus in system.get_components(DistributionBus):
        if bus.uuid not in connected_buses:
            system.remove_component(bus, cascade_down=False)
    return system


@pytest.fixture(scope="session")
def gdm_system():
    return _example_gdm_system()


@pytest.fixture(scope="session")
def gdm_system_2():
    return _example_gdm_system()
