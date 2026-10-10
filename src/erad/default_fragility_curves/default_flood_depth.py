from gdm.quantities import Distance

import erad.models.fragility_curve as frag
from erad.enums import AssetTypes


moderate_mu_meters = {
    "Class 1": 1.524,
    "Class 2": 1.463,
    "Class 3": 1.372,
    "Class 4": 1.280,
    "Class 5": 1.219,
    "Class 6": 1.128,
    "Class 7": 1.067,
    "Class 8": 0.975,
    "Class 9": 0.914,
    "Class 10": 0.853,
}

dispersion_values = {
    "Class 1": 0.45,
    "Class 2": 0.45,
    "Class 3": 0.50,
    "Class 4": 0.50,
    "Class 5": 0.50,
    "Class 6": 0.50,
    "Class 7": 0.55,
    "Class 8": 0.55,
    "Class 9": 0.60,
    "Class 10": 0.60,
}

DEFAULT_FLOOD_DEPTH_FRAGILITY_CURVES = frag.HazardFragilityCurves(
    asset_state_param="flood_depth",
    curves=[
        frag.FragilityCurve(
            asset_type=AssetTypes.switch,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.35, "m"), Distance(0.50, "m"), 1 / 0.35],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.battery_storage,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.4, "m"), Distance(0.01, "m"), 0.7],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_junction_box,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.8, "m"), Distance(2.0, "m"), 1 / 0.8],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_overhead_lines,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[
                    Distance(dispersion_values["Class 4"], "m"),
                    Distance(0.01, "m"),
                    moderate_mu_meters["Class 4"],
                ],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_poles,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[
                    Distance(dispersion_values["Class 4"], "m"),
                    Distance(0.01, "m"),
                    moderate_mu_meters["Class 4"],
                ],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_underground_cables,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.8, "m"), Distance(2.0, "m"), 1 / 0.8],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.solar_panels,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.4, "m"), Distance(0.01, "m"), 0.8],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.substation,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.01, "m"), Distance(0.01, "m"), 1],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.series_reactor,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.01, "m"), Distance(0.01, "m"), 1],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transformer_mad_mount,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.5, "m"), Distance(0.01, "m"), 0.9],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transformer_pole_mount,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.5, "m"), Distance(0.01, "m"), 1.2],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_junction_box,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.40, "m"), Distance(1.0, "m"), 1 / 0.40],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_overhead_lines,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.30, "m"), Distance(1.8, "m"), 1 / 0.3],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_tower,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.40, "m"), Distance(2.2, "m"), 1 / 0.40],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_underground_cables,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.25, "m"), Distance(0.8, "m"), 1 / 0.25],
            ),
        ),
    ],
)
