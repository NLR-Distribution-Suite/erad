import erad.models.fragility_curve as frag
from erad.quantities import Acceleration
from erad.enums import AssetTypes

DEFAULT_PEAK_GROUND_ACCELERATION_FRAGILITY_CURVES = frag.HazardFragilityCurves(
    asset_state_param="peak_ground_acceleration",
    curves=[
        frag.FragilityCurve(
            asset_type=AssetTypes.switch,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[
                    Acceleration(0.8, "m/s**2"),
                    Acceleration(0.40 * 9.81, "m/s**2"),
                    1 / 0.80,
                ],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.battery_storage,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[
                    Acceleration(0.8, "m/s**2"),
                    Acceleration(0.40 * 9.81, "m/s**2"),
                    1 / 0.80,
                ],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_junction_box,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[
                    Acceleration(0.5, "m/s**2"),
                    Acceleration(0.45 * 9.81, "m/s**2"),
                    1 / 0.50,
                ],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_overhead_lines,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[
                    Acceleration(0.55, "m/s**2"),
                    Acceleration(0.50 * 9.81, "m/s**2"),
                    1 / 0.55,
                ],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_poles,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[
                    Acceleration(0.6, "m/s**2"),
                    Acceleration(0.40 * 9.81, "m/s**2"),
                    1 / 0.6,
                ],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_underground_cables,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[
                    Acceleration(0.8, "m/s**2"),
                    Acceleration(1.0 * 9.81, "m/s**2"),
                    1 / 0.8,
                ],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.solar_panels,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[
                    Acceleration(0.45, "m/s**2"),
                    Acceleration(0.45 * 9.81, "m/s**2"),
                    1 / 0.45,
                ],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.substation,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[
                    Acceleration(0.5, "m/s**2"),
                    Acceleration(0.40 * 9.81, "m/s**2"),
                    1 / 0.5,
                ],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.series_reactor,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[
                    Acceleration(0.5, "m/s**2"),
                    Acceleration(0.40 * 9.81, "m/s**2"),
                    1 / 0.5,
                ],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transformer_mad_mount,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[
                    Acceleration(0.6, "m/s**2"),
                    Acceleration(0.40 * 9.81, "m/s**2"),
                    1 / 0.6,
                ],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transformer_pole_mount,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[
                    Acceleration(0.8, "m/s**2"),
                    Acceleration(0.50 * 9.81, "m/s**2"),
                    1 / 0.70,
                ],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_junction_box,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[
                    Acceleration(0.5, "m/s**2"),
                    Acceleration(0.50 * 9.81, "m/s**2"),
                    1 / 0.50,
                ],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_overhead_lines,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[
                    Acceleration(0.6, "m/s**2"),
                    Acceleration(0.60 * 9.81, "m/s**2"),
                    1 / 0.60,
                ],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_tower,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[
                    Acceleration(0.4, "m/s**2"),
                    Acceleration(0.35 * 9.81, "m/s**2"),
                    1 / 0.40,
                ],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_underground_cables,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[
                    Acceleration(0.55, "m/s**2"),
                    Acceleration(0.80 * 9.81, "m/s**2"),
                    1 / 0.55,
                ],
            ),
        ),
    ],
)
