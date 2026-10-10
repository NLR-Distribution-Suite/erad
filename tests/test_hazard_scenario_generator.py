from datetime import datetime

from gdm.distribution.components import DistributionBus
from gdm.tracked_changes import filter_tracked_changes_by_name_and_date, apply_updates_to_system
from gdm.distribution import DistributionSystem
from gdm.quantities import Distance
from shapely.geometry import Point

from erad.runner import HazardScenarioGenerator
from erad.models.hazard import EarthQuakeModel
from erad.systems.asset_system import AssetSystem
from erad.systems.hazard_system import HazardSystem


def test_hazard_scenarios(gdm_system: DistributionSystem):
    number_of_samples = 5
    asset_system = AssetSystem.from_gdm(gdm_system)
    bus = next(gdm_system.get_components(DistributionBus))
    hazard = EarthQuakeModel(
        name="local_earthquake",
        timestamp=datetime.now(),
        origin=Point(bus.coordinate.x, bus.coordinate.y),
        depth=Distance(10, "kilometer"),
        magnitude=8.0,
    )
    hazard_system = HazardSystem(auto_add_composed_components=True)
    hazard_system.add_component(hazard)
    scenario_generator = HazardScenarioGenerator(
        asset_system=asset_system, hazard_system=hazard_system, engine="legacy"
    )
    scenarios = scenario_generator.samples(number_of_samples)
    assert scenarios

    scenario_names = {s.scenario_name for s in scenarios}
    assert len(scenario_names) == number_of_samples

    scenario_0 = filter_tracked_changes_by_name_and_date(
        tracked_changes=scenarios, scenario_name=list(scenario_names)[0]
    )
    n_asset_inservice_before = sum(
        [c.in_service for c in gdm_system.iter_all_components() if hasattr(c, "in_service")]
    )
    updated_gdm_system = apply_updates_to_system(scenario_0, gdm_system, None)
    n_asset_inservice_after = sum(
        [
            c.in_service
            for c in updated_gdm_system.iter_all_components()
            if hasattr(c, "in_service")
        ]
    )
    assert n_asset_inservice_before != n_asset_inservice_after
