import erad.models.fragility_curve as frag
from erad.enums import AssetTypes
from erad.quantities import Speed


DEFAULT_WIND_SPEED_FRAGILITY_CURVES = frag.HazardFragilityCurves(
    asset_state_param="wind_speed",
    curves=[
        frag.FragilityCurve(
            asset_type=AssetTypes.switch,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.45, "m/s"), Speed(50, "m/s"), 1 / 0.45]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.battery_storage,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.45, "m/s"), Speed(50, "m/s"), 1 / 0.45]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_junction_box,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.4, "m/s"), Speed(50, "m/s"), 1 / 0.4]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_overhead_lines,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.35, "m/s"), Speed(45, "m/s"), 1 / 0.35]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_poles,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.4, "m/s"), Speed(45, "m/s"), 1 / 0.4]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_underground_cables,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.4, "m/s"), Speed(55, "m/s"), 1 / 0.4]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.solar_panels,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.3, "m/s"), Speed(55, "m/s"), 1 / 0.3]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.substation,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.4, "m/s"), Speed(55, "m/s"), 1 / 0.40]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.series_reactor,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.4, "m/s"), Speed(55, "m/s"), 1 / 0.40]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transformer_mad_mount,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.35, "m/s"), Speed(50, "m/s"), 1 / 0.35]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transformer_pole_mount,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.3, "m/s"), Speed(45, "m/s"), 1 / 0.30]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_junction_box,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.54, "m/s"), Speed(55, "m/s"), 1 / 0.54]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_overhead_lines,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.35, "m/s"), Speed(50, "m/s"), 1 / 0.35]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_tower,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.4, "m/s"), Speed(55, "m/s"), 1 / 0.40]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_underground_cables,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.4, "m/s"), Speed(60, "m/s"), 1 / 0.40]
            ),
        ),
    ],
)
