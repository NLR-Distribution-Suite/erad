from collections import defaultdict
from unittest.mock import Mock

from infrasys import Component

from gdm.distribution import DistributionSystem
from gdm.systems.substation.components import PowerTransformer
import pytest

from erad.systems.asset_system import AssetSystem
from erad.constants import ASSET_TYPES
from erad.enums import AssetTypes
from erad.gdm_mapping import asset_to_gdm_mapping
from gdm.distribution.components import DistributionReactor


def test_component_addition():
    h = AssetSystem(auto_add_composed_components=True)
    for m in ASSET_TYPES:
        h.add_component(m.example())


def test_component_failure():
    class Testing(Component):
        ...

    test = Testing(name="asdf")

    h = AssetSystem(auto_add_composed_components=True)
    with pytest.raises(AssertionError):
        h.add_component(test)


def test_from_gdm(gdm_system: DistributionSystem):
    asset_system = AssetSystem.from_gdm(gdm_system)
    asset_system.info()


def test_gdm_24_reactor_mapping():
    assert AssetTypes.series_reactor.value == 14
    assert asset_to_gdm_mapping[AssetTypes.series_reactor][0].component_type is DistributionReactor


def test_power_transformer_maps_to_substation():
    transformer = PowerTransformer.model_construct(buses=[])
    dist_system = Mock()
    dist_system.get_components.return_value = [transformer]
    asset_map = defaultdict(list)

    AssetSystem._map_transformers(asset_map, dist_system)

    assert asset_map[AssetTypes.substation] == [transformer]


def test_serialization_deserialization(tmp_path):
    h = AssetSystem(auto_add_composed_components=True)
    for m in ASSET_TYPES:
        h.add_component(m.example())
    h.to_json(tmp_path / "asset_system.json")
    AssetSystem.from_json(tmp_path / "asset_system.json")


def test_plot(gdm_system_2: DistributionSystem):
    asset_system = AssetSystem.from_gdm(gdm_system_2)
    asset_system.plot()
