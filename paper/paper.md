---
title: 'ERAD: A Graph-Based Tool for Energy Resilience Analysis of Electric Distribution Systems'
tags:
  - python
  - neo4j
  - power distribution systems
  - energy resilience
  - disaster modeling
authors:
  - name: Kapil Duwadi
    orcid: 0000-0002-0589-5187
    affiliation: 1
  - name: Bryan Palmintier
    orcid: 0000-0002-1452-0715
    affiliation: 1
  - name: Aadil Latif
    affiliation: 1
  - name: Kwami Senam Sedzro
    orcid: 0000-0002-2107-8662
    affiliation: 1
  - name: Sherin Ann Abraham
    orcid: 0000-0002-4214-3267
    affiliation: 1
  
affiliations:
 - name: National Renewable Energy Laboratory (NREL), Golden, CO, USA
   index: 1
date: 1 February 2024
bibliography: paper.bib
---

# Summary

Understanding the impact of extreme events on people's ability to access energy is crucial for designing resilient energy systems. In the event of a disaster, damage to the electric system and related infrastructure (e.g., downed power lines, flooded equipment, hacked communication systems, damaged roads, etc.) can impact people's access to critical services, including not just electricity but also shelter, food, healthcare, and more. There is a key need to understand such impacts better and evaluate options to improve energy resilience. The Energy Resilience Analysis for Electric Distribution Systems (ERAD) tool is a free and open-source software package designed to help researchers and decision-makers analyze and improve energy system resilience.

# Statement of Need

Much of the past work in evaluating energy resilience has looked at historical data. For instance, @alper2021heat used historical power outage complaint calls in New York City to understand heat vulnerability, @flores20232021 used satellite images to understand the impact of winter storms in Texas. In another example, @brockway_inequitable_2021 showed how existing grid infrastructure constraints may hinder the ability of communities to charge electric vehicles and their access to distributed energy resources by looking at the geospatial intersection of demographics and grid hosting capacity data. ERAD instead provides a way to look ahead at possible future outages and service access challenges. ERAD also offers the unique feature of assessing access to multiple services under multiple disaster event scenarios.

Many of the software tools developed for a forward-looking understanding of grid resilience have been focused on the bulk power system. For example, @panteli2016power used fragility curves to assess the impact of extreme events in transmission system components, @8286183 developed resilience assessment indices to understand the impact of multiple transmission line outages, @8752426 proposed a resilience-constrained economic dispatch model for bulk system. These studies miss geospatial granularity to enable understanding of extreme events on critical service access or outage impacts at the neighborhood scale, let alone the individual customer scale. Unlike existing resilience-focused tools that focus on transmission resilience, ERAD enables capturing these local effects at the neighborhood level or even down to the customer level.

There have been some recent efforts that consider resilience at the distribution system. For instance, the REPAIR tool [@repair-paper] optimizes distribution system expansion planning considering both routine operations reliability and resilience to extreme events. However, it requires users to supply outage rate information and does not consider any energy metrics or look across critical services. The ReNCAT tool [@osti_1880920] does consider multi-service-based equity using the social burden metric introduced in  @osti_1846088, however it only considers microgrids as a resilience strategy and its optimization-based approach may struggle to scale to the very large regions ERAD can evaluate. ReNCAT also currently requires the .Net framework (nominally under the Windows operating system) and though open source, does not currently maintain a publicly accessible code repository to enable outside contributions or issue reporting. Both REPAIR and ReNCAT also require exogenous equipment damage risk data and patterns. In contrast, ERAD endogenously models damage patterns; computes a range of energy metrics, and enables open engagement in development through github.com.

# Implementation Overview

ERAD is a free, open-source Python toolkit for computing energy resilience measures in the face of hazards like earthquakes and flooding for distribution systems. It uses graph-based analysis to perform computation down to the individual households. Users start by defining hazard models either manually or using historic extreme events. Next, they define all distribution system assets of interest. Outage scenarios in ERAD are generated based on Monte Carlo samples across the individual equipment survival probabilities. Finally, ERAD computes a range of energy metrics, including outage probability, outage duration, and outage impact on critical services.

ERAD is now part of the [Grid-Data-Models](https://nrel-distribution-suites.github.io/grid-data-models/intro.html) (GDM) ecosystem! This integration enables ERAD to run resilience analyses directly on GDM-based distribution systems, improving interoperability with other distribution-focused tools and streamlining the development of automated workflows. 

For outage simulations, ERAD uses asset fragility curves [@Jessica; @kongar_seismic_2017; @kongar_seismic_2014; @en10071037; @Jeddi; @BAGHMISHEH2021106909; @williams_tsunami_2020; @bennett_extending_2021] which are functions that relate hazard severity to survival probability for power system assets including cables, transformers, substations, roof-mounted solar panels, etc. [@rajabzadeh_improving_2022; @fema_hazus_2020; @farahani_earthquake_2020; @cirone_valutazione_2013; @su12041527]. Outage scenarios are then generated based on Monte Carlo samples across these individual equipment survival probabilities.

# Example Usage

ERAD has been used as part of multiple high-impact research efforts. Specifically, it was used to analyze energy access to critical services for 8 neighborhoods in the city of Los Angeles as it transitions to a 100% renewable energy future as part of the LA100 Equity Strategies project [@la100-es-report]. For transmission distribution cosimulation after a flooding disaster, ERAD has also been used to generate distribution system outage scenarios as a part of North American Energy Resilience Model [@narem] studies.

# Next Steps

Future development will focus on expanding the tool's capabilities to simulate additional threats such as storms, heat waves, and cold spells, while also enhancing the efficiency of result visualization.

# Acknowledgements

This work was authored by the National Renewable Energy Laboratory (NREL), operated by Alliance for Sustainable Energy, LLC, for the U.S. Department of Energy (DOE) under Contract No. DE-AC36-08GO28308. Funding provided by NREL license revenue under the provisions of the Bayh-Dole Act. The views expressed in the article do not necessarily represent the views of the DOE or the U.S. Government. The U.S. Government retains and the publisher, by accepting the article for publication, acknowledges that the U.S. Government retains a nonexclusive, paid-up, irrevocable, worldwide license to publish or reproduce the published form of this work, or allow others to do so, for U.S. Government purposes.

# References
