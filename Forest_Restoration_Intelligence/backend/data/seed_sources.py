"""Curated forest-restoration evidence corpus (seed data).

Each source is a real, citable publication (FAO / IPCC / peer-reviewed forest
ecology literature). Chunk text is a paraphrased summary of the source's
findings (not a verbatim excerpt), written for this project and tagged with
the causal-chain edge it supports. Tags must match `chain_template.py`.
"""

SOURCES = [
    {
        "source_id": "fao_sowf2020",
        "title": "The State of the World's Forests 2020: Forests, Biodiversity and People",
        "publisher": "FAO & UNEP",
        "year": "2020",
        "url": "https://www.fao.org/documents/card/en/c/ca8642en",
        "chunks": [
            (
                "Between 1990 and 2020 the world lost 420 million hectares of forest "
                "through conversion to other land uses, primarily agriculture. This "
                "loss of forest cover reduces canopy buffering and is strongly "
                "associated with declines in species richness and overall "
                "biodiversity in affected landscapes.",
                "trigger",
            ),
            (
                "Agricultural expansion is the leading direct driver of deforestation "
                "in the tropics, converting closed-canopy forest into fragmented "
                "mosaics of cropland, pasture and residual forest patches.",
                "deforestation_agri->fragmentation",
            ),
        ],
    },
    {
        "source_id": "ipcc_ar6_wg2_ch2",
        "title": "Climate Change 2022: Impacts, Adaptation and Vulnerability — Chapter 2: Terrestrial and Freshwater Ecosystems",
        "publisher": "IPCC (AR6, Working Group II)",
        "year": "2022",
        "url": "https://www.ipcc.ch/report/ar6/wg2/chapter/chapter-2/",
        "chunks": [
            (
                "Loss of forest cover reduces evapotranspiration and disrupts local "
                "and regional rainfall recycling, while rising regional temperatures "
                "increase atmospheric evaporative demand. Together these compound "
                "soil and plant water deficits in remaining forest fragments.",
                "deforestation_temp_rainfall->water_stress",
            ),
            (
                "Forest ecosystems exposed to combined warming and precipitation "
                "decline show increased tree mortality risk, reduced growth rates "
                "and shifts in species composition toward more drought-tolerant, "
                "often lower-biodiversity-value assemblages.",
                "water_stress->vegetation_stress",
            ),
        ],
    },
    {
        "source_id": "ellison2017",
        "title": "Trees, forests and water: Cool insights for a hot world",
        "publisher": "Global Environmental Change, 43, 51-61",
        "year": "2017",
        "url": "https://doi.org/10.1016/j.gloenvcha.2017.01.002",
        "chunks": [
            (
                "Forests actively cool their surroundings and help sustain rainfall "
                "through evapotranspiration and cloud formation. Removing forest "
                "cover interrupts this hydrological cycle, lowering local humidity "
                "and soil moisture and pushing remaining vegetation toward chronic "
                "water stress.",
                "deforestation_temp_rainfall->water_stress",
            ),
        ],
    },
    {
        "source_id": "bonan2008",
        "title": "Forests and Climate Change: Forcings, Feedbacks, and the Climate Benefits of Forests",
        "publisher": "Science, 320(5882), 1444-1449",
        "year": "2008",
        "url": "https://doi.org/10.1126/science.1155121",
        "chunks": [
            (
                "Forest canopies regulate surface energy balance and moisture flux. "
                "Canopy loss raises local surface temperatures and reduces moisture "
                "retention, amplifying water-stress signals already driven by "
                "regional warming and rainfall decline.",
                "deforestation_temp_rainfall->water_stress",
            ),
        ],
    },
    {
        "source_id": "brando2014",
        "title": "Abrupt increases in Amazonian tree mortality due to drought-fire interactions",
        "publisher": "PNAS, 111(17), 6347-6352",
        "year": "2014",
        "url": "https://doi.org/10.1073/pnas.1305499111",
        "chunks": [
            (
                "Drought-stressed tropical forests show abrupt increases in tree "
                "mortality when water deficit interacts with fire and heat stress, "
                "with mortality rates several times higher than under non-drought "
                "conditions, directly degrading canopy structure and vegetation "
                "condition.",
                "water_stress->vegetation_stress",
            ),
        ],
    },
    {
        "source_id": "allen2010",
        "title": "A global overview of drought and heat-induced tree mortality reveals emerging climate change risks for forests",
        "publisher": "Forest Ecology and Management, 259(4), 660-684",
        "year": "2010",
        "url": "https://doi.org/10.1016/j.foreco.2009.09.001",
        "chunks": [
            (
                "A global synthesis of case studies confirms that drought- and "
                "heat-induced tree mortality is an emerging risk across forest "
                "biomes, with water-stressed stands showing reduced productivity, "
                "canopy dieback and heightened vulnerability to secondary "
                "stressors such as pests and disease.",
                "water_stress->vegetation_stress",
            ),
        ],
    },
    {
        "source_id": "gibson2011",
        "title": "Primary forests are irreplaceable for sustaining tropical biodiversity",
        "publisher": "Nature, 478, 378-381",
        "year": "2011",
        "url": "https://doi.org/10.1038/nature10425",
        "chunks": [
            (
                "Primary forests retain substantially higher biodiversity value than "
                "degraded or secondary forests. As vegetation condition and "
                "structural complexity decline, habitat quality for forest-dependent "
                "species falls sharply, driving measurable biodiversity loss.",
                "vegetation_stress->habitat_degradation",
            ),
            (
                "Habitat degradation in tropical forests is consistently associated "
                "with declines in vertebrate and invertebrate species richness, with "
                "the steepest losses occurring in taxa most dependent on intact "
                "canopy structure.",
                "habitat_degradation->biodiversity_decline",
            ),
        ],
    },
    {
        "source_id": "sasaki_putz2009",
        "title": "Critical need for new definitions of 'forest' and 'forest degradation' in global climate change agreements",
        "publisher": "Conservation Letters, 2(5), 226-232",
        "year": "2009",
        "url": "https://doi.org/10.1111/j.1755-263X.2009.00067.x",
        "chunks": [
            (
                "Even where forest cover nominally persists, degradation of "
                "vegetation structure and carbon stocks undermines the ecological "
                "functions that support biodiversity, meaning canopy presence alone "
                "does not indicate habitat quality.",
                "vegetation_stress->habitat_degradation",
            ),
        ],
    },
    {
        "source_id": "laurance2014",
        "title": "Agricultural expansion and its impacts on tropical nature",
        "publisher": "Trends in Ecology & Evolution, 29(2), 107-116",
        "year": "2014",
        "url": "https://doi.org/10.1016/j.tree.2013.12.001",
        "chunks": [
            (
                "Agricultural expansion is the dominant proximate driver of tropical "
                "deforestation, converting contiguous forest into fragmented patches "
                "surrounded by cropland and pasture, with edge effects penetrating "
                "hundreds of meters into remaining forest fragments.",
                "deforestation_agri->fragmentation",
            ),
        ],
    },
    {
        "source_id": "haddad2015",
        "title": "Habitat fragmentation and its lasting impact on Earth's ecosystems",
        "publisher": "Science Advances, 1(2), e1500052",
        "year": "2015",
        "url": "https://doi.org/10.1126/sciadv.1500052",
        "chunks": [
            (
                "Habitat fragmentation reduces patch size and increases isolation, "
                "degrading the ecological integrity of remaining habitat through "
                "edge effects, altered microclimate and disrupted species movement, "
                "with effects compounding over decades.",
                "fragmentation->habitat_degradation",
            ),
            (
                "Across biomes, fragmented habitats show reduced biodiversity "
                "persistence over time, with smaller and more isolated fragments "
                "losing species at consistently higher rates than contiguous "
                "habitat of equivalent total area.",
                "habitat_degradation->biodiversity_decline",
            ),
        ],
    },
    {
        "source_id": "fahrig2003",
        "title": "Effects of Habitat Fragmentation on Biodiversity",
        "publisher": "Annual Review of Ecology, Evolution, and Systematics, 34, 487-515",
        "year": "2003",
        "url": "https://doi.org/10.1146/annurev.ecolsys.34.011802.132419",
        "chunks": [
            (
                "Habitat fragmentation independent of habitat amount has small but "
                "consistently negative effects on biodiversity, primarily through "
                "reduced patch size and increased isolation limiting population "
                "persistence and recolonization.",
                "habitat_degradation->biodiversity_decline",
            ),
        ],
    },
    {
        "source_id": "chazdon2008",
        "title": "Beyond Deforestation: Restoring Forests and Ecosystem Services on Degraded Lands",
        "publisher": "Science, 320(5882), 1458-1460",
        "year": "2008",
        "url": "https://doi.org/10.1126/science.1155365",
        "chunks": [
            (
                "Assisted natural regeneration leverages existing seed banks, root "
                "stocks and nearby seed sources to rebuild canopy cover and "
                "vegetation structure, often restoring a majority of aboveground "
                "biomass within two to three decades at substantially lower cost "
                "than active replanting.",
                "regeneration->vegetation_recovery",
            ),
        ],
    },
    {
        "source_id": "crouzeilles2017",
        "title": "A global meta-analysis on the ecological drivers of forest restoration success",
        "publisher": "Nature Communications, 8, 11666",
        "year": "2017",
        "url": "https://doi.org/10.1038/ncomms11666",
        "chunks": [
            (
                "A global meta-analysis of forest restoration outcomes found that "
                "natural regeneration recovers vegetation structure, species "
                "diversity and ecosystem services to 70-80% of reference forest "
                "values within the first two decades, with recovery rates strongly "
                "mediated by surrounding landscape forest cover.",
                "regeneration->vegetation_recovery",
            ),
        ],
    },
    {
        "source_id": "holl_aide2011",
        "title": "When and where to actively restore ecosystems?",
        "publisher": "Forest Ecology and Management, 261(10), 1558-1563",
        "year": "2011",
        "url": "https://doi.org/10.1016/j.foreco.2010.07.004",
        "chunks": [
            (
                "On severely degraded sites where seed sources and soil conditions "
                "limit natural regeneration, active planting with native pioneer "
                "species accelerates canopy closure and vegetation recovery "
                "relative to passive approaches.",
                "regeneration->vegetation_recovery",
            ),
        ],
    },
    {
        "source_id": "lamb2005",
        "title": "Restoration of Degraded Tropical Forest Landscapes",
        "publisher": "Science, 310(5754), 1628-1632",
        "year": "2005",
        "url": "https://doi.org/10.1126/science.1111773",
        "chunks": [
            (
                "Restoring degraded tropical forest landscapes through a mix of "
                "natural regeneration and targeted native species planting can "
                "substantially increase species richness relative to unassisted "
                "recovery, particularly when reintroduced species restore habitat "
                "structure and food resources for forest fauna.",
                "reintroduction->biodiversity_recovery",
            ),
            (
                "Reconnecting fragmented forest patches through corridor "
                "restoration and buffer planting reduces edge effects and "
                "isolation, allowing species movement and gene flow to resume "
                "between previously isolated habitat fragments.",
                "connectivity->habitat_recovery",
            ),
        ],
    },
    {
        "source_id": "tambosi2014",
        "title": "A framework to optimize biodiversity restoration efforts based on habitat amount and landscape connectivity",
        "publisher": "Restoration Ecology, 22(2), 169-177",
        "year": "2014",
        "url": "https://doi.org/10.1111/rec.12049",
        "chunks": [
            (
                "Prioritizing restoration to increase landscape connectivity, "
                "rather than only total habitat amount, more effectively counters "
                "the habitat-degradation effects of fragmentation and yields "
                "greater biodiversity return per unit area restored.",
                "fragmentation->habitat_degradation",
            ),
            (
                "Strategic corridor placement between fragments is among the most "
                "cost-effective interventions for restoring connectivity and "
                "supporting species persistence in fragmented forest landscapes.",
                "connectivity->habitat_recovery",
            ),
        ],
    },
]
