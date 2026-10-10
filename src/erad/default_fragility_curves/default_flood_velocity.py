import erad.models.fragility_curve as frag
from erad.quantities import Speed
from erad.enums import AssetTypes

DEFAULT_FLOOD_VELOCITY_FRAGILITY_CURVES = frag.HazardFragilityCurves(
    asset_state_param="flood_velocity",
    curves=[
        frag.FragilityCurve(
            asset_type=AssetTypes.switch,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Speed(0.35, "m/s"), Speed(1.5, "m/s"), 1 / 0.35],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.battery_storage,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Speed(0.35, "m/s"), Speed(1.5, "m/s"), 1 / 0.35],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_junction_box,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.4, "m/s"), Speed(2.0, "m/s"), 1 / 0.40]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_overhead_lines,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Speed(0.35, "m/s"), Speed(3.5, "m/s"), 1 / 0.35],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_poles,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Speed(0.35, "m/s"), Speed(3.0, "m/s"), 1 / 0.35],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_underground_cables,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.4, "m/s"), Speed(2.0, "m/s"), 1 / 0.4]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.solar_panels,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Speed(0.35, "m/s"), Speed(2.0, "m/s"), 1 / 0.35],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.substation,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.4, "m/s"), Speed(2.0, "m/s"), 1 / 0.4]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.series_reactor,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.4, "m/s"), Speed(2.0, "m/s"), 1 / 0.4]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transformer_mad_mount,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Speed(0.35, "m/s"), Speed(1.5, "m/s"), 1 / 0.35],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transformer_pole_mount,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.3, "m/s"), Speed(2.5, "m/s"), 1 / 0.30]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_junction_box,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.4, "m/s"), Speed(1.5, "m/s"), 1 / 0.4]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_overhead_lines,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Speed(0.35, "m/s"), Speed(3.5, "m/s"), 1 / 0.35],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_tower,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Speed(0.40, "m/s"), Speed(3.0, "m/s"), 1 / 0.40],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_underground_cables,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.40, "m/s"), Speed(2.0, "m/s"), 1 / 0.4]
            ),
        ),
    ],
)
