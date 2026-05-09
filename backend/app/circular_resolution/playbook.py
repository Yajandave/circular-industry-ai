"""Material-specific circular economy playbooks.

These playbooks are deliberately practical rather than exhaustive. They turn the
rules-engine route into a more circular-economy-specific intervention pattern:
prevention, value retention, supplier loops, industrial symbiosis, evidence and
claim controls.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MaterialPlaybook:
    family: str
    focus: str
    best_routes: list[str]
    routes_to_avoid: list[str]
    evidence_required: list[str]
    supplier_questions: list[str]
    process_questions: list[str]
    pilot_kpis: list[str]
    fallback_route: str
    value_retention_logic: str
    circular_economy_reason: str


PLAYBOOKS: dict[str, MaterialPlaybook] = {
    "metals": MaterialPlaybook(
        family="metals",
        focus="segregation, grade retention and closed-loop metal recovery",
        best_routes=[
            "prevent machining or cutting losses where practical",
            "segregate by alloy or grade at source",
            "keep clean offcuts separate from contaminated swarf",
            "test supplier take-back or closed-loop remelt",
            "use mixed scrap only as lower-value fallback",
        ],
        routes_to_avoid=[
            "mixing clean alloy offcuts with low-grade mixed scrap",
            "claiming closed-loop recycling without alloy, collection and processor evidence",
        ],
        evidence_required=[
            "alloy or grade records",
            "contamination controls",
            "segregated collection records",
            "supplier or recycler acceptance criteria",
            "current mixed-scrap value or disposal cost baseline",
        ],
        supplier_questions=[
            "Can the supplier or recycler accept segregated metal by alloy or grade?",
            "What contamination limits and rejection criteria apply?",
            "Can documentation confirm whether the material returns to a comparable application?",
        ],
        process_questions=[
            "Which product/job types generate the largest avoidable metal losses?",
            "Can nesting, cutting plans, tolerance settings or batch planning reduce offcuts?",
            "Can collection points be labelled by alloy or job family?",
        ],
        pilot_kpis=[
            "kg segregated by alloy per month",
            "rejection rate from recycler/supplier",
            "difference between mixed-scrap value and closed-loop route value",
            "number of jobs with grade/source recorded",
        ],
        fallback_route="documented metal recycling or mixed scrap sale, with segregation maintained where feasible",
        value_retention_logic="Keeping metals separated by alloy/grade preserves material quality and usually retains more value than mixed scrap handling.",
        circular_economy_reason="The intervention keeps technical material in circulation at a higher quality level instead of treating it as a generic waste output.",
    ),
    "plastics": MaterialPlaybook(
        family="plastics",
        focus="polymer identification, source reduction, regrind quality and supplier loops",
        best_routes=[
            "prevent purge and setup losses before recycling",
            "segregate by polymer and colour where relevant",
            "test regrind or closed-loop use where quality allows",
            "use supplier take-back for packaging and recurring resin streams",
            "use open-loop recycling only when closed-loop quality is not feasible",
        ],
        routes_to_avoid=[
            "mixing polymers before checking grade and additive compatibility",
            "claiming circularity where the route is downcycling without evidence",
        ],
        evidence_required=[
            "polymer type and grade",
            "additives, colour or filler information",
            "contamination rate",
            "regrind quality limits",
            "supplier/recycler acceptance criteria",
        ],
        supplier_questions=[
            "Can the supplier accept clean segregated polymer returns or provide take-back?",
            "Can recycled-content or regrind limits be documented?",
            "Would packaging prevention or reusable pallet containment be feasible?",
        ],
        process_questions=[
            "Can line purge, setup scrap or reject rates be reduced?",
            "Can polymer streams be separated at the point of generation?",
            "Can rejected material be trialled in non-critical parts?",
        ],
        pilot_kpis=[
            "kg segregated by polymer grade",
            "contamination rate",
            "regrind acceptance/rejection rate",
            "kg virgin input displaced in trial batches",
        ],
        fallback_route="segregated open-loop recycling with documented acceptance criteria",
        value_retention_logic="Polymer purity and grade control increase the chance of reuse or closed-loop recycling before lower-value recycling.",
        circular_economy_reason="The intervention prioritises preventing process losses and preserving polymer quality rather than treating all plastic as mixed waste.",
    ),
    "cardboard/packaging": MaterialPlaybook(
        family="cardboard/packaging",
        focus="packaging prevention, returnable transit packaging and supplier redesign",
        best_routes=[
            "reduce unnecessary secondary packaging",
            "pilot returnable transit packaging",
            "use supplier-owned totes/crates where delivery frequency supports it",
            "segregate clean cardboard recycling as fallback",
        ],
        routes_to_avoid=[
            "treating recycling as the first option when repeat supplier packaging could be prevented",
            "introducing return loops without checking storage, damage and transport burden",
        ],
        evidence_required=[
            "packaging weight by supplier or lane",
            "delivery frequency",
            "damage rate",
            "return logistics requirements",
            "storage space and handling constraints",
        ],
        supplier_questions=[
            "Can the supplier reduce one-way packaging or use returnable transit packaging?",
            "Can packaging specifications be changed without increasing damage risk?",
            "What return logistics, deposit or collection terms would apply?",
        ],
        process_questions=[
            "Which suppliers generate the highest packaging volume?",
            "Can packaging be separated by material and supplier route?",
            "Are there recurring lanes suitable for reusable totes or pallet systems?",
        ],
        pilot_kpis=[
            "kg packaging avoided per delivery cycle",
            "returnable packaging cycle count",
            "damage rate compared with baseline",
            "storage and handling incidents",
        ],
        fallback_route="clean segregated recycling for packaging not suitable for prevention or reuse",
        value_retention_logic="Avoiding or reusing packaging retains more value than recycling single-use packaging after each delivery.",
        circular_economy_reason="The intervention shifts the system from one-way packaging disposal to prevention, reuse and supplier-loop design.",
    ),
    "wood/pallets": MaterialPlaybook(
        family="wood/pallets",
        focus="repair, pooling, supplier return and contamination separation",
        best_routes=[
            "separate repairable pallets from damaged or contaminated wood",
            "use pallet pooling or repair contracts",
            "return supplier-owned pallets/crates",
            "reuse untreated timber internally where safe",
            "use energy recovery only as a lower-value fallback",
        ],
        routes_to_avoid=[
            "sending repairable pallets directly to energy recovery",
            "mixing painted/treated contaminated wood with clean timber routes",
        ],
        evidence_required=[
            "treatment or contamination status",
            "repairability assessment",
            "ownership and supplier return terms",
            "quantity and frequency",
            "acceptance criteria for pallet repair or reuse",
        ],
        supplier_questions=[
            "Can pallets or crates be returned, pooled or repaired under contract?",
            "Who owns the pallets and what rejection criteria apply?",
            "Can the supplier move to standardised returnable units?",
        ],
        process_questions=[
            "What proportion is repairable rather than broken beyond use?",
            "Can storage and handling reduce pallet breakage?",
            "Can clean untreated wood be separated from treated/painted material?",
        ],
        pilot_kpis=[
            "pallets repaired or returned per month",
            "kg timber avoided from disposal/recovery",
            "breakage rate",
            "cost per reuse cycle",
        ],
        fallback_route="documented recycling or recovery route separated by contamination/treatment status",
        value_retention_logic="Repair and reuse keep pallets and timber in a higher-value loop than shredding, disposal or energy recovery.",
        circular_economy_reason="The intervention keeps packaging assets in circulation and prevents avoidable timber waste.",
    ),
    "chemicals/solvents": MaterialPlaybook(
        family="chemicals/solvents",
        focus="source reduction, substitution, authorised recovery and strict classification",
        best_routes=[
            "reduce chemical use at source",
            "substitute lower-risk material where technically feasible",
            "use closed-loop solvent recovery only where classification and contamination allow",
            "use authorised specialist recovery/disposal for controlled or hazardous streams",
        ],
        routes_to_avoid=[
            "proposing reuse or recovery without SDS, classification and contractor acceptance",
            "mixing solvent streams before checking recovery specification",
        ],
        evidence_required=[
            "SDS or product safety information",
            "hazard classification",
            "contamination profile",
            "storage and container requirements",
            "authorised contractor acceptance criteria",
        ],
        supplier_questions=[
            "Can the supplier provide return, recovery or substitution options?",
            "What safety, container and contamination limits apply?",
            "What evidence confirms the contractor is authorised for this stream?",
        ],
        process_questions=[
            "Can chemical use be reduced by dosing, cleaning frequency or process control?",
            "Can streams be kept separate for recovery?",
            "Can a lower-risk formulation meet the same specification?",
        ],
        pilot_kpis=[
            "litres/kg chemical use reduced",
            "hazardous waste volume trend",
            "recovery acceptance rate where authorised",
            "incidents/rejections/non-conformances",
        ],
        fallback_route="compliant authorised hazardous or specialist waste route with full documentation",
        value_retention_logic="For chemicals, safe source reduction and authorised recovery matter more than forcing a circular route where risk is unresolved.",
        circular_economy_reason="The intervention prioritises prevention and safe recovery while respecting legal and safety boundaries.",
    ),
    "textiles": MaterialPlaybook(
        family="textiles",
        focus="reuse where safe, fibre recovery and controlled review for PPE/filter media",
        best_routes=[
            "reuse or laundry contracts where hygiene and contamination allow",
            "segregate clean offcuts for fibre recovery",
            "use supplier take-back where available",
            "controlled disposal for contaminated PPE or filter media",
        ],
        routes_to_avoid=[
            "treating contaminated PPE/filter media as ordinary textile recycling",
            "claiming reuse where hygiene or contamination controls are unknown",
        ],
        evidence_required=[
            "textile composition",
            "contamination type",
            "hygiene/safety requirements",
            "reuse/laundry limits",
            "specialist recycler acceptance criteria",
        ],
        supplier_questions=[
            "Can the supplier provide take-back or recycled-content evidence?",
            "Can clean offcuts be accepted separately from contaminated textiles?",
            "What hygiene or contamination restrictions apply?",
        ],
        process_questions=[
            "Can offcuts be reduced through cutting optimisation?",
            "Can clean offcuts be segregated at source?",
            "Are any streams PPE, filter media or potentially contaminated?",
        ],
        pilot_kpis=[
            "kg clean textiles segregated",
            "kg reused/laundered safely",
            "kg sent to specialist fibre recovery",
            "contamination rejection rate",
        ],
        fallback_route="specialist recovery or compliant disposal depending on contamination and safety review",
        value_retention_logic="Clean textiles can retain value through reuse or fibre recovery, but controlled streams require safety review first.",
        circular_economy_reason="The intervention separates clean value-retention routes from safety-controlled textile waste.",
    ),
    "glass": MaterialPlaybook(
        family="glass",
        focus="glass type separation and specialist routes for laminated/contaminated glass",
        best_routes=[
            "segregate clear cullet separately",
            "use specialist processing for laminated/safety glass",
            "confirm contamination and interlayer constraints",
            "screen supplier return where recurring rejects exist",
        ],
        routes_to_avoid=[
            "treating laminated safety glass like clear cullet",
            "mixing contaminated lab glass with ordinary glass recycling",
        ],
        evidence_required=[
            "glass type",
            "lamination or interlayer detail",
            "contamination status",
            "processor acceptance criteria",
            "segregation records",
        ],
        supplier_questions=[
            "Can the supplier or processor accept this glass type separately?",
            "Do laminated/interlayer materials require specialist separation?",
            "What quality or contamination limits apply?",
        ],
        process_questions=[
            "Can clear, laminated and contaminated glass be separated at source?",
            "Which processes generate repeat rejects?",
            "Can quality defects be reduced upstream?",
        ],
        pilot_kpis=[
            "kg glass segregated by type",
            "processor acceptance rate",
            "reject rate from quality control",
            "kg diverted from specialist disposal where safe",
        ],
        fallback_route="specialist disposal/recovery route matched to glass type and contamination status",
        value_retention_logic="Separating glass by type maintains route quality and avoids contaminating higher-value cullet streams.",
        circular_economy_reason="The intervention preserves material quality and prevents avoidable downcycling or route rejection.",
    ),
    "rubber": MaterialPlaybook(
        family="rubber",
        focus="trimming reduction, quality segregation and specialist rubber recovery",
        best_routes=[
            "reduce trimming and rejection at source",
            "segregate clean rubber by type",
            "screen crumb/reprocessing routes",
            "use supplier recovery where available",
            "controlled review for oil-contaminated rubber",
        ],
        routes_to_avoid=[
            "sending clean repetitive trimming waste to general waste",
            "mixing oil-contaminated rubber with clean recovery streams",
        ],
        evidence_required=[
            "rubber type and formulation",
            "oil/chemical contamination status",
            "quality rejection cause",
            "supplier/recycler acceptance criteria",
            "process scrap rate",
        ],
        supplier_questions=[
            "Can the supplier accept clean rubber rejects or advise on recovery routes?",
            "What contamination and formulation limits apply?",
            "Can specification changes reduce rejection or trimming loss?",
        ],
        process_questions=[
            "Can die/cutting tolerances or nesting reduce trim waste?",
            "What quality issue causes rejected seals or gaskets?",
            "Can clean rubber be segregated from contaminated mats?",
        ],
        pilot_kpis=[
            "kg trim waste per production batch",
            "quality reject rate",
            "kg accepted by specialist recovery",
            "contamination rejection rate",
        ],
        fallback_route="specialist rubber recovery or compliant controlled disposal based on contamination status",
        value_retention_logic="Reducing process scrap and segregating clean rubber retains more value than general waste handling.",
        circular_economy_reason="The intervention addresses upstream scrap causes before selecting a recovery route.",
    ),
    "electronic components": MaterialPlaybook(
        family="electronic components",
        focus="repair/refurbishment screening, authorised WEEE/battery handling and component recovery",
        best_routes=[
            "repair or refurbish where safe and technically viable",
            "harvest components where quality and data/security controls allow",
            "use authorised WEEE treatment routes",
            "use specialist battery routes for damaged lithium packs",
            "supplier take-back for recurring component rejects",
        ],
        routes_to_avoid=[
            "treating batteries or hazardous electronics as quick-win circular streams",
            "claiming recovery without authorised treatment evidence",
        ],
        evidence_required=[
            "WEEE or battery classification",
            "battery chemistry or hazardous content where relevant",
            "data/security requirements",
            "authorised treatment route evidence",
            "repair/refurbishment quality criteria",
        ],
        supplier_questions=[
            "Can the supplier provide take-back or warranty return routes?",
            "What authorised WEEE or battery treatment evidence is available?",
            "Can components be repaired, refurbished or harvested safely?",
        ],
        process_questions=[
            "What defect type creates the reject?",
            "Can testing or handling reduce rejects?",
            "Are any batteries damaged, swollen or requiring specialist isolation?",
        ],
        pilot_kpis=[
            "units repaired/refurbished",
            "kg routed through authorised WEEE/battery route",
            "component harvest acceptance rate",
            "reject cause reduction rate",
        ],
        fallback_route="authorised WEEE or battery specialist treatment with documented transfer/consignment evidence",
        value_retention_logic="Repair and component recovery retain more value than raw material recovery, but safety and authorisation come first.",
        circular_economy_reason="The intervention prioritises product/component value retention while blocking unsafe routes for hazardous electronics.",
    ),
    "organic/process residue": MaterialPlaybook(
        family="organic/process residue",
        focus="source prevention, food/biogenic residue separation and authorised biological recovery",
        best_routes=[
            "prevent avoidable residues at source",
            "segregate clean food-grade or biogenic residues",
            "screen anaerobic digestion or composting where suitable",
            "screen specialist FOG recovery for grease-type streams only after classification",
            "use authorised disposal where contamination or classification blocks recovery",
        ],
        routes_to_avoid=[
            "proposing biological recovery without contamination and acceptance evidence",
            "treating grease trap waste as a normal food residue stream",
        ],
        evidence_required=[
            "composition and contamination profile",
            "contractor acceptance criteria",
            "volume trends and collection frequency",
            "classification and handling documentation",
            "food/animal by-product or FOG-specific constraints where relevant",
        ],
        supplier_questions=[
            "Can the contractor confirm authorised recovery or disposal options?",
            "What contamination and composition limits apply?",
            "What transfer, treatment or acceptance evidence can be provided?",
        ],
        process_questions=[
            "Can the residue be prevented through upstream process or kitchen practice changes?",
            "Can clean organic residues be separated from contaminated streams?",
            "Are maintenance schedules or operating practices driving avoidable volume?",
        ],
        pilot_kpis=[
            "kg residue reduced at source",
            "kg accepted by authorised biological/recovery route",
            "contamination rejection rate",
            "collection frequency and volume trend",
        ],
        fallback_route="authorised specialist treatment or disposal until classification and acceptance evidence supports recovery",
        value_retention_logic="Clean biogenic residues may be recovered, but prevention and contamination control protect higher-value and safer routes.",
        circular_economy_reason="The intervention prioritises upstream prevention and controlled recovery rather than treating organic residues as generic waste.",
    ),
    "process water": MaterialPlaybook(
        family="process water",
        focus="water efficiency, reuse loops and permit-aware treatment controls",
        best_routes=[
            "reduce water use at source",
            "optimise rinsing and flow controls",
            "screen filtration or closed-loop reuse",
            "confirm discharge/treatment limits before reuse or release",
        ],
        routes_to_avoid=[
            "framing process water as waste diversion without water quality and permit evidence",
            "proposing reuse before contaminant profile is known",
        ],
        evidence_required=[
            "flow rate and operating hours",
            "water quality and contaminant profile",
            "treatment requirements",
            "permit/discharge constraints",
            "reuse quality requirements",
        ],
        supplier_questions=[
            "Can the water treatment supplier specify reuse or filtration options?",
            "What contaminant thresholds and monitoring evidence are required?",
            "What permitted discharge or treatment route applies?",
        ],
        process_questions=[
            "Can rinsing be counter-flow, timed or sensor-controlled?",
            "Can water be reused in a lower-grade process step?",
            "What contamination prevents closed-loop reuse?",
        ],
        pilot_kpis=[
            "m3 water reduced or reused per month",
            "contaminant concentration before/after treatment",
            "reuse acceptance rate",
            "discharge non-conformance count",
        ],
        fallback_route="documented treatment/discharge route while reuse feasibility is assessed",
        value_retention_logic="Water reuse and reduction reduce resource demand and treatment burden, but must be controlled by quality and permit evidence.",
        circular_economy_reason="The intervention treats water as a resource loop, not simply as a waste stream to move off site.",
    ),
    "energy/resource stream": MaterialPlaybook(
        family="energy/resource stream",
        focus="heat mapping, internal reuse and industrial symbiosis for excess energy",
        best_routes=[
            "measure temperature, duration and operating pattern",
            "screen internal heat recovery first",
            "evaluate heat exchange or pre-heating opportunities",
            "screen nearby heat users only after quantity and distance are known",
        ],
        routes_to_avoid=[
            "claiming waste heat recovery without temperature and energy data",
            "treating zero-kg energy streams as waste-diversion opportunities",
        ],
        evidence_required=[
            "temperature profile",
            "operating hours and frequency",
            "estimated recoverable energy",
            "distance to potential user",
            "technical feasibility and heat quality requirements",
        ],
        supplier_questions=[
            "Can the equipment supplier provide heat recovery specifications?",
            "What temperature and flow data are needed for feasibility?",
            "Can heat be recovered internally before external symbiosis is considered?",
        ],
        process_questions=[
            "Which operations need heat at compatible times and temperatures?",
            "Can curing/pre-heating/drying loads use recovered heat?",
            "What monitoring is needed to quantify recoverable energy?",
        ],
        pilot_kpis=[
            "kWh recoverable heat estimated",
            "hours of compatible operation",
            "temperature profile captured",
            "internal heat demand matched",
        ],
        fallback_route="documented energy efficiency review without diversion or carbon claims until data is measured",
        value_retention_logic="Recovered heat retains energy value within the system before considering external users.",
        circular_economy_reason="The intervention treats lost energy as a resource-efficiency and symbiosis opportunity rather than a material waste stream.",
    ),
    "process mineral residue": MaterialPlaybook(
        family="process mineral residue",
        focus="classification, contamination control and specialist mineral recovery screening",
        best_routes=[
            "reduce sludge or grinding residue at source",
            "confirm mineral composition and contamination",
            "screen specialist mineral recovery or construction-material use only if lawful and accepted",
            "use compliant disposal while evidence is unresolved",
        ],
        routes_to_avoid=[
            "proposing construction or fill uses without waste/by-product status and contamination evidence",
            "mixing mineral residues with hazardous or oil-contaminated streams",
        ],
        evidence_required=[
            "mineral composition",
            "hazardous status",
            "contamination profile",
            "moisture/handling characteristics",
            "authorised acceptance criteria",
        ],
        supplier_questions=[
            "Can a specialist processor accept this residue and under what specification?",
            "What analysis is required to confirm safe recovery?",
            "What legal status and documentation would be needed?",
        ],
        process_questions=[
            "Can grinding/cooling/fluid management reduce sludge generation?",
            "Can solids be separated before contamination increases?",
            "Can process settings reduce residue formation?",
        ],
        pilot_kpis=[
            "kg residue reduced",
            "contamination analysis results",
            "acceptance/rejection from specialist processor",
            "disposal cost trend",
        ],
        fallback_route="compliant disposal or specialist treatment until composition and legal acceptance are confirmed",
        value_retention_logic="Mineral residues may have secondary value only where composition, contamination and legal acceptance are evidenced.",
        circular_economy_reason="The intervention avoids unsafe reuse and focuses on evidence-controlled material recovery.",
    ),
}


def normalise_material(material: str | None) -> str:
    value = (material or "").strip().lower()
    if value in PLAYBOOKS:
        return value
    if "metal" in value or "aluminium" in value or "steel" in value or "copper" in value:
        return "metals"
    if "plastic" in value or "poly" in value or "pet" in value or "ldpe" in value:
        return "plastics"
    if "pack" in value or "cardboard" in value or "label" in value:
        return "cardboard/packaging"
    if "wood" in value or "pallet" in value or "timber" in value:
        return "wood/pallets"
    if "chemical" in value or "solvent" in value or "oil" in value:
        return "chemicals/solvents"
    if "textile" in value or "ppe" in value or "fabric" in value:
        return "textiles"
    if "glass" in value:
        return "glass"
    if "rubber" in value:
        return "rubber"
    if "electronic" in value or "battery" in value or "pcb" in value:
        return "electronic components"
    if "water" in value:
        return "process water"
    if "energy" in value or "heat" in value:
        return "energy/resource stream"
    if "mineral" in value or "sludge" in value:
        return "process mineral residue"
    if "organic" in value or "grease" in value or "food" in value or "biomass" in value:
        return "organic/process residue"
    return "organic/process residue"


def get_playbook(material: str | None) -> MaterialPlaybook:
    return PLAYBOOKS[normalise_material(material)]
