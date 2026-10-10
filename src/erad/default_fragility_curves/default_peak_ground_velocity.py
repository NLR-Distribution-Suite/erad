import erad.models.fragility_curve as frag
from erad.enums import AssetTypes
from erad.quantities import Speed

DEFAULT_PEAK_GROUND_VELOCITY_FRAGILITY_CURVES = frag.HazardFragilityCurves(
    asset_state_param="peak_ground_velocity",
    curves=[
        frag.FragilityCurve(
            asset_type=AssetTypes.switch,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.5, "cm/s"), Speed(35, "cm/s"), 2]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.battery_storage,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.5, "cm/s"), Speed(35, "cm/s"), 2]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_junction_box,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.5, "cm/s"), Speed(35, "cm/s"), 2]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_overhead_lines,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.5, "cm/s"), Speed(40, "cm/s"), 2]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_poles,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.5, "cm/s"), Speed(40, "cm/s"), 2]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_underground_cables,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.5, "cm/s"), Speed(60, "cm/s"), 2]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.solar_panels,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.5, "cm/s"), Speed(35, "cm/s"), 2]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.substation,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.5, "cm/s"), Speed(50, "cm/s"), 2]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.series_reactor,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.5, "cm/s"), Speed(50, "cm/s"), 2]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transformer_mad_mount,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.5, "cm/s"), Speed(35, "cm/s"), 2]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transformer_pole_mount,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.5, "cm/s"), Speed(40, "cm/s"), 2]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_junction_box,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.5, "cm/s"), Speed(50, "cm/s"), 2]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_overhead_lines,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.5, "cm/s"), Speed(45, "cm/s"), 2]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_tower,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm", parameters=[Speed(0.5, "cm/s"), Speed(35, "cm/s"), 2]
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_underground_cables,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Speed(0.55, "cm/s"), Speed(65, "cm/s"), 1 / 0.55],
            ),
        ),
    ],
)
