from enum import IntEnum


class ScenarioTypes(IntEnum):
    flood_m = 0
    wind_m_per_s = 1
    fire_m = 2
    earthquake_pga = 3


class NodeTypes(IntEnum):
    transmission_tower = 5
    distribution_poles = 6
    transmission_junction_box = 11
    distribution_junction_box = 12


class AssetTypes(IntEnum):
    substation = 0
    solar_panels = 1
    distribution_underground_cables = 2
    transmission_underground_cables = 3
    battery_storage = 4
    transmission_tower = 5
    distribution_poles = 6
    transmission_overhead_lines = 7
    distribution_overhead_lines = 8
    transformer_mad_mount = 9
    transformer_pole_mount = 10
    transmission_junction_box = 11
    distribution_junction_box = 12
    switch = 13
    series_reactor = 14

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def has_asset(cls, asset):
        return asset in cls.__members__
