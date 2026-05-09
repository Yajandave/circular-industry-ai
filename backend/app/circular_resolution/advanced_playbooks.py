"""Advanced material-specific circular economy playbooks.

Milestone 7D adds a stronger domain layer above the core resolution engine.
The goal is to make outputs less generic by adding material-family knowledge,
route-specific cautions, evidence tests, supplier questions, pilot patterns and
reporting links. These playbooks do not make legal, safety or carbon claims.
They provide structured prompts and controls for human review and the optional
LLM reasoning layer.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.circular_resolution.playbook import normalise_material


@dataclass(frozen=True)
class AdvancedMaterialPlaybook:
    material_family: str
    material_cycle: str
    core_circularity_question: str
    best_fit_streams: list[str]
    high_value_intervention_patterns: list[str]
    prevention_and_design_levers: list[str]
    value_retention_levers: list[str]
    supplier_and_procurement_levers: list[str]
    industrial_symbiosis_partner_types: list[str]
    evidence_tests: list[str]
    red_flags: list[str]
    routes_to_avoid: list[str]
    pilot_patterns: list[str]
    kpis: list[str]
    claim_controls: list[str]
    esrs_e5_mapping: list[str]
    cti_style_metrics: list[str]
    circular_design_questions: list[str]
    fallback_controls: list[str]
    example_resolution_prompt: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


ADVANCED_PLAYBOOKS: dict[str, AdvancedMaterialPlaybook] = {
    "metals": AdvancedMaterialPlaybook(
        material_family="metals",
        material_cycle="technical material cycle",
        core_circularity_question="Can metal value be retained through prevention, alloy segregation, closed-loop remelt or supplier return before mixed scrap handling?",
        best_fit_streams=["aluminium offcuts", "stainless steel offcuts", "copper cable", "ferrous swarf", "metal drums"],
        high_value_intervention_patterns=[
            "Create alloy or grade-specific collection points at the source process.",
            "Separate clean offcuts from oily swarf, painted rejects or mixed scrap.",
            "Use supplier or recycler acceptance criteria to validate closed-loop remelt potential.",
            "Compare mixed scrap value with segregated material value and collection cost.",
            "For recurring metal containers, test supplier-owned return loops rather than scrap routes.",
        ],
        prevention_and_design_levers=[
            "Review nesting, cutting plans, set-up losses and quality rejects before selecting an end route.",
            "Check whether tolerance, batch-size or ordering changes can reduce offcut generation.",
            "Record alloy/grade at source so the material can stay in a higher-value loop.",
        ],
        value_retention_levers=[
            "same-grade reuse or remelt",
            "supplier take-back with material identity preserved",
            "segregated recycling with documented acceptance criteria",
        ],
        supplier_and_procurement_levers=[
            "Ask for alloy-specific take-back terms and rejection thresholds.",
            "Add segregation and documentation duties to supplier or recycler agreements.",
            "Request evidence showing whether material returns to comparable metal applications.",
        ],
        industrial_symbiosis_partner_types=["secondary aluminium processor", "foundry", "metal recycler", "remanufacturer"],
        evidence_tests=["alloy/grade record", "contamination check", "segregated weight log", "acceptance/rejection record", "baseline scrap value"],
        red_flags=["mixed alloys", "oily swarf", "paint contamination", "unknown grade", "no chain-of-custody evidence"],
        routes_to_avoid=["claiming closed-loop recycling from generic mixed scrap sale", "mixing clean alloy offcuts with contaminated metal"],
        pilot_patterns=["8-week source-segregation pilot", "one CNC cell or product family", "weekly accepted/rejected material log"],
        kpis=["kg segregated by alloy", "rejection rate", "value retained versus mixed scrap", "jobs with grade recorded"],
        claim_controls=["Do not claim closed-loop impact without supplier/recycler acceptance evidence and collection records."],
        esrs_e5_mapping=["resource outflows", "waste diverted from disposal", "secondary material potential", "actions and resources"],
        cti_style_metrics=["% output routed to recovery", "% closed-loop eligible", "value-retention route strength"],
        circular_design_questions=["Can parts be nested better?", "Can tolerances reduce reject rates?", "Can alloy information travel with the material?"],
        fallback_controls=["documented segregated recycling", "mixed scrap only after higher-value loop is not feasible"],
        example_resolution_prompt="Design an alloy-segregation pilot before treating the stream as generic scrap.",
    ),
    "plastics": AdvancedMaterialPlaybook(
        material_family="plastics",
        material_cycle="technical material cycle",
        core_circularity_question="Can polymer losses be prevented or kept pure enough for regrind, supplier return or higher-value recycling?",
        best_fit_streams=["LDPE film", "PET trim", "HDPE purge", "ABS rejects", "mixed polymer rejects"],
        high_value_intervention_patterns=[
            "Identify polymer grade, colour, additives and contamination before route selection.",
            "Separate clean film/trim/rejects at source instead of creating mixed plastic waste.",
            "Test internal regrind or lower-risk part use where product quality allows.",
            "Use supplier take-back for recurring packaging or resin streams.",
            "Keep open-loop recycling as fallback where closed-loop quality is not possible.",
        ],
        prevention_and_design_levers=[
            "Reduce purge and setup scrap through process settings and changeover discipline.",
            "Review material specification, colour matching and reject root causes.",
            "Replace one-way pallet wrap with reusable bands or supplier-owned packaging where feasible.",
        ],
        value_retention_levers=["regrind trial", "polymer-specific segregation", "supplier film take-back", "reusable packaging replacement"],
        supplier_and_procurement_levers=[
            "Ask for recycled-content specifications and quality constraints.",
            "Ask whether supplier can collect segregated polymer or packaging streams.",
            "Build acceptance criteria into supply or recycling agreements.",
        ],
        industrial_symbiosis_partner_types=["plastic compounder", "film recycler", "moulder using lower-grade feedstock", "packaging recycler"],
        evidence_tests=["polymer ID", "additive/colour record", "contamination rate", "regrind specification", "food/contact restriction check"],
        red_flags=["mixed polymers", "unknown additives", "chemical contamination", "food/contact restrictions", "no polymer identification"],
        routes_to_avoid=["treating mixed polymer rejects as equivalent to clean single-polymer streams", "claiming circularity from downcycling without evidence"],
        pilot_patterns=["6-week segregated collection pilot", "regrind batch trial", "supplier film return test"],
        kpis=["kg by polymer grade", "contamination rate", "regrind acceptance", "virgin input displaced in test batches"],
        claim_controls=["Do not claim closed-loop plastic circularity unless polymer identity, quality acceptance and route evidence are documented."],
        esrs_e5_mapping=["resource inflows", "secondary recycled material", "resource outflows", "waste stream management"],
        cti_style_metrics=["% polymer output recovered", "% potentially closed-loop", "recycled-content evidence readiness"],
        circular_design_questions=["Can purge be reduced?", "Can design allow recycled-content input?", "Can polymer grades be standardised?"],
        fallback_controls=["segregated open-loop recycling", "specialist recovery where contamination limits are met"],
        example_resolution_prompt="Separate polymer grade at source, then validate regrind or supplier take-back before open-loop recycling.",
    ),
    "cardboard/packaging": AdvancedMaterialPlaybook(
        material_family="cardboard/packaging",
        material_cycle="technical material and packaging loop",
        core_circularity_question="Can one-way packaging be prevented, reduced, reused or returned before recycling is treated as the main route?",
        best_fit_streams=["cardboard cartons", "foam inserts", "plastic totes", "labels", "packaging cores"],
        high_value_intervention_patterns=[
            "Map packaging volumes by supplier lane rather than treating all packaging as one stream.",
            "Pilot returnable transit packaging on frequent supplier routes.",
            "Reduce secondary packaging specification before improving recycling routes.",
            "Use supplier-owned totes, crates or pallet systems where reverse logistics are viable.",
        ],
        prevention_and_design_levers=[
            "Review packaging specification, damage rate and over-packaging evidence.",
            "Identify repeat delivery lanes suitable for reusable transit packaging.",
            "Separate unavoidable packaging from packaging caused by supplier practice.",
        ],
        value_retention_levers=["returnable transit packaging", "supplier-owned packaging", "internal reuse", "clean fibre recycling fallback"],
        supplier_and_procurement_levers=[
            "Request packaging reduction options by supplier lane.",
            "Add returnable packaging trials to supplier review meetings.",
            "Define damage, cleaning, deposit, ownership and return logistics terms.",
        ],
        industrial_symbiosis_partner_types=["packaging supplier", "local reuse network", "fibre recycler", "pallet/pooling provider"],
        evidence_tests=["packaging weight by supplier", "delivery frequency", "damage rate", "return trip feasibility", "storage space"],
        red_flags=["return loop creates excessive transport", "lack of storage", "higher product damage", "mixed contaminated packaging"],
        routes_to_avoid=["calling recycling the first circular option on repeat supplier packaging", "introducing reusable packaging without damage and logistics evidence"],
        pilot_patterns=["one supplier lane returnable-packaging pilot", "six-week packaging reduction trial", "damage-rate comparison"],
        kpis=["kg packaging avoided", "return cycles", "damage rate", "storage incidents", "cost per delivery cycle"],
        claim_controls=["Do not claim avoided packaging until delivery counts, weight records and supplier acceptance are confirmed."],
        esrs_e5_mapping=["packaging resource inflows", "resource outflows", "waste reduction actions", "value-chain collaboration"],
        cti_style_metrics=["% packaging reused", "% packaging avoided", "% packaging recycled as fallback"],
        circular_design_questions=["Is the packaging necessary?", "Can it be reusable?", "Can product protection be kept while reducing material?"],
        fallback_controls=["clean segregated recycling", "documented general waste only for contaminated mixed packaging"],
        example_resolution_prompt="Prioritise supplier packaging prevention or returnable packaging before recycling cardboard or foam.",
    ),
    "wood/pallets": AdvancedMaterialPlaybook(
        material_family="wood/pallets",
        material_cycle="technical packaging asset loop and biological material route",
        core_circularity_question="Can pallets, crates and timber be repaired, pooled or returned before lower-value recycling or energy recovery?",
        best_fit_streams=["wooden pallets", "export crates", "timber offcuts", "painted timber"],
        high_value_intervention_patterns=[
            "Separate repairable pallets from contaminated or treated wood.",
            "Use pallet pooling or repair agreements for recurring inbound/outbound flows.",
            "Return supplier-owned crates and pallets where ownership is clear.",
            "Use untreated wood internally only where safety and quality allow.",
        ],
        prevention_and_design_levers=["Reduce pallet breakage through handling and storage changes.", "Standardise pallet types where suppliers allow.", "Design crates for repeated cycles."],
        value_retention_levers=["repair", "pooling", "supplier return", "internal reuse", "cascading untreated wood use"],
        supplier_and_procurement_levers=["Clarify pallet ownership.", "Add returnable pallet/crate terms.", "Request repair/reuse reporting from contractor."],
        industrial_symbiosis_partner_types=["pallet repair contractor", "crate manufacturer", "wood processor", "biomass route for unsuitable clean wood"],
        evidence_tests=["treatment status", "contamination status", "repairability count", "ownership terms", "reuse cycle count"],
        red_flags=["painted or treated wood", "unknown contamination", "broken beyond repair", "pest/handling controls"],
        routes_to_avoid=["sending repairable pallets to energy recovery", "mixing treated wood with clean timber"],
        pilot_patterns=["pallet sort-and-repair trial", "supplier return lane", "breakage root-cause review"],
        kpis=["pallets repaired", "reuse cycles", "kg wood avoided", "breakage rate"],
        claim_controls=["Do not call energy recovery circular; frame it as lower-value fallback."],
        esrs_e5_mapping=["resource outflows", "packaging waste", "reuse actions", "value-chain collaboration"],
        cti_style_metrics=["% pallet reuse", "% repairable assets", "% clean wood recovered"],
        circular_design_questions=["Can pallet design survive more cycles?", "Can supplier packaging ownership shift to pooling?"],
        fallback_controls=["documented recycling/recovery by treatment status", "controlled disposal for contaminated painted wood"],
        example_resolution_prompt="Sort by repairability and treatment status before considering recovery or disposal.",
    ),
    "chemicals/solvents": AdvancedMaterialPlaybook(
        material_family="chemicals/solvents",
        material_cycle="controlled technical material route",
        core_circularity_question="Can chemical use be reduced, substituted or recovered safely within authorised classification and contractor controls?",
        best_fit_streams=["solvents", "cleaning solutions", "adhesives", "lubricating oil", "powder coating overspray"],
        high_value_intervention_patterns=[
            "Reduce use through dosing, cleaning-frequency or process-control changes.",
            "Keep streams segregated where recovery specifications require purity.",
            "Assess lower-risk substitution before recovery claims.",
            "Use authorised recovery only where classification, SDS and contamination evidence allow.",
        ],
        prevention_and_design_levers=["cleaning process optimisation", "material substitution", "inventory control to avoid expiry", "spray/overspray reduction"],
        value_retention_levers=["solvent recovery", "oil recovery", "supplier return", "process substitution"],
        supplier_and_procurement_levers=["Request SDS, recovery acceptance criteria and authorised contractor evidence.", "Ask supplier for lower-risk or refillable formats.", "Include expired-stock minimisation in procurement controls."],
        industrial_symbiosis_partner_types=["authorised solvent recycler", "oil recovery contractor", "chemical supplier take-back programme"],
        evidence_tests=["SDS", "hazard classification", "contamination profile", "storage requirements", "contractor permit/acceptance"],
        red_flags=["hazardous classification", "mixed solvents", "unknown contamination", "expired chemicals", "unverified recovery contractor"],
        routes_to_avoid=["reuse without SDS/classification", "mixing streams before recovery assessment", "public claims for hazardous stream recovery without evidence"],
        pilot_patterns=["desk-based classification review", "segregation and sample analysis", "source-reduction trial before route change"],
        kpis=["kg/litre use reduced", "hazardous waste volume", "accepted recovery rate", "non-conformance count"],
        claim_controls=["Do not propose or claim circular recovery without classification, authorised acceptance and contractor documentation."],
        esrs_e5_mapping=["hazardous waste", "actions and resources", "resource outflows", "pollution-linked controls"],
        cti_style_metrics=["% source reduction", "% authorised recovery", "claim-readiness status"],
        circular_design_questions=["Can the process use less chemical?", "Can material be substituted?", "Can stock control prevent expiry?"],
        fallback_controls=["authorised hazardous/specialist disposal", "human review before any circular route"],
        example_resolution_prompt="Treat recovery as a controlled option after classification, not as a default circular route.",
    ),
    "textiles": AdvancedMaterialPlaybook(
        material_family="textiles",
        material_cycle="technical or biological material route depending on fibre and contamination",
        core_circularity_question="Can clean textile material be reused or recovered while keeping PPE/filter/contaminated streams under safety control?",
        best_fit_streams=["clean textile offcuts", "filter fabric", "PPE garments", "cleaning cloths"],
        high_value_intervention_patterns=["Separate clean offcuts from PPE/filter media.", "Use laundering or reuse only where contamination and hygiene controls are evidenced.", "Screen fibre recovery for clean, identifiable textiles."],
        prevention_and_design_levers=["cutting optimisation", "standardise reusable cloth systems", "specify reusable/launderable textiles where safe"],
        value_retention_levers=["reuse/laundry", "fibre recovery", "supplier take-back", "material substitution"],
        supplier_and_procurement_levers=["Ask suppliers for reusable or recycled-content textile options.", "Request acceptance criteria for take-back of clean offcuts.", "Clarify hygiene controls for reuse."],
        industrial_symbiosis_partner_types=["textile recycler", "industrial wiper/laundry provider", "fibre processor"],
        evidence_tests=["composition", "contamination type", "hygiene restriction", "laundry/reuse feasibility", "recycler acceptance"],
        red_flags=["PPE contamination", "filter media contamination", "unknown fibre blend", "hygiene or biohazard risk"],
        routes_to_avoid=["ordinary textile recycling for contaminated PPE/filter media", "reuse without hygiene evidence"],
        pilot_patterns=["clean offcut segregation pilot", "laundry reuse trial", "controlled PPE review"],
        kpis=["kg clean textiles segregated", "reuse cycles", "contamination rejection rate", "kg fibre recovered"],
        claim_controls=["Keep PPE/filter streams in human review until contamination and safety restrictions are resolved."],
        esrs_e5_mapping=["resource outflows", "waste streams", "reuse/recycling actions"],
        cti_style_metrics=["% clean textile recovered", "% reuse cycles", "% controlled disposal"],
        circular_design_questions=["Can cutting patterns reduce offcuts?", "Can reusable PPE/cloths be specified where safe?"],
        fallback_controls=["specialist recovery for clean streams", "compliant disposal for controlled contaminated streams"],
        example_resolution_prompt="Separate clean textile recovery from PPE/filter controlled-review logic.",
    ),
    "glass": AdvancedMaterialPlaybook(
        material_family="glass",
        material_cycle="technical mineral material cycle",
        core_circularity_question="Can glass be separated by type and contamination so clear cullet is preserved and specialist glass is correctly routed?",
        best_fit_streams=["clear glass cullet", "laminated glass", "lab glassware"],
        high_value_intervention_patterns=["Segregate clear glass from laminated and contaminated glass.", "Use specialist laminated glass processing where interlayers are present.", "Keep lab/contaminated glass under compliance review."],
        prevention_and_design_levers=["reduce quality defects", "review handling and inspection failures", "improve segregation at source"],
        value_retention_levers=["clear cullet recycling", "specialist laminated processing", "supplier return where recurring defects occur"],
        supplier_and_procurement_levers=["Ask supplier/processor for glass-type acceptance criteria.", "Clarify laminated interlayer requirements.", "Request route evidence for specialist glass."],
        industrial_symbiosis_partner_types=["glass processor", "laminated glass specialist", "construction material processor"],
        evidence_tests=["glass type", "interlayer/lamination", "contamination status", "processor acceptance", "segregation records"],
        red_flags=["lab contamination", "laminated interlayer", "mixed glass types", "unknown treatment/coating"],
        routes_to_avoid=["mixing laminated safety glass with clear cullet", "ordinary recycling for contaminated lab glass"],
        pilot_patterns=["glass-type segregation trial", "processor acceptance test", "reject root-cause review"],
        kpis=["kg by glass type", "processor rejection rate", "quality reject reduction", "kg accepted by specialist route"],
        claim_controls=["Claim only the glass type and route that is evidenced; do not generalise all glass as recyclable."],
        esrs_e5_mapping=["resource outflows", "waste by material type", "recycling/recovery actions"],
        cti_style_metrics=["% cullet accepted", "% specialist glass processed", "route rejection rate"],
        circular_design_questions=["Can breakage/defects be reduced?", "Can glass type be tagged at source?"],
        fallback_controls=["specialist disposal/recovery matched to type and contamination"],
        example_resolution_prompt="Treat laminated and lab glass differently from clear cullet.",
    ),
    "rubber": AdvancedMaterialPlaybook(
        material_family="rubber",
        material_cycle="technical polymer/elastomer material cycle",
        core_circularity_question="Can rubber scrap be prevented or kept clean enough for specialist recovery, while contaminated rubber remains controlled?",
        best_fit_streams=["rubber trimmings", "rejected seals", "oil-contaminated mats"],
        high_value_intervention_patterns=["Reduce trim scrap through process settings.", "Separate clean rubber by formulation.", "Screen crumbing or specialist reprocessing only where contamination is controlled."],
        prevention_and_design_levers=["die tolerance review", "nesting/cutting optimisation", "quality reject root-cause analysis"],
        value_retention_levers=["clean rubber recovery", "supplier recovery", "lower-grade reuse", "process scrap reduction"],
        supplier_and_procurement_levers=["Ask supplier for formulation limits and recovery routes.", "Request advice on specification changes to reduce reject rates."],
        industrial_symbiosis_partner_types=["rubber recycler", "crumb rubber processor", "secondary rubber product manufacturer"],
        evidence_tests=["rubber formulation", "contamination status", "quality defect cause", "recycler acceptance", "batch records"],
        red_flags=["oil contamination", "unknown formulation", "mixed elastomers", "hazardous residues"],
        routes_to_avoid=["general waste for clean repetitive rubber scrap", "mixing contaminated rubber with recovery streams"],
        pilot_patterns=["trim-reduction trial", "clean rubber segregation", "specialist acceptance sample"],
        kpis=["kg trim per batch", "quality reject rate", "kg accepted by specialist recovery", "contamination rejection rate"],
        claim_controls=["Do not claim recovery if oil or chemical contamination is unresolved."],
        esrs_e5_mapping=["resource outflows", "waste stream actions", "process efficiency actions"],
        cti_style_metrics=["% clean rubber recovered", "% scrap reduced", "specialist route acceptance"],
        circular_design_questions=["Can tooling reduce trim?", "Can product quality checks prevent rejected seals?"],
        fallback_controls=["specialist recovery or compliant disposal according to contamination"],
        example_resolution_prompt="Prioritise trim reduction and clean segregation before specialist rubber recovery.",
    ),
    "electronic components": AdvancedMaterialPlaybook(
        material_family="electronic components",
        material_cycle="technical product/component cycle with hazardous controls",
        core_circularity_question="Can component value be retained through repair, warranty return, harvesting or authorised WEEE treatment without bypassing hazardous controls?",
        best_fit_streams=["PCB rejects", "wiring harness rejects", "sensor modules", "lithium battery packs"],
        high_value_intervention_patterns=["Screen repair/refurbishment first where safe.", "Use supplier warranty or take-back routes.", "Separate batteries and hazardous WEEE.", "Use authorised WEEE treatment and evidence records."],
        prevention_and_design_levers=["test failure root cause", "handling damage reduction", "inventory obsolescence control", "design for disassembly/repair"],
        value_retention_levers=["repair", "refurbishment", "component harvesting", "authorised WEEE recovery", "battery specialist route"],
        supplier_and_procurement_levers=["Ask supplier for warranty return, take-back and repair options.", "Request authorised treatment evidence and battery handling requirements."],
        industrial_symbiosis_partner_types=["authorised WEEE operator", "electronics refurbisher", "component recovery specialist", "battery recycler"],
        evidence_tests=["WEEE classification", "battery chemistry/status", "POP/hazard assessment where relevant", "data/security controls", "authorised treatment evidence"],
        red_flags=["damaged lithium batteries", "PCB hazardous substances", "POPs risk", "data-bearing devices", "unknown treatment route"],
        routes_to_avoid=["ordinary scrap route for batteries or hazardous WEEE", "reuse/refurbishment without safety and data controls"],
        pilot_patterns=["defect-code review", "warranty-return pilot", "component harvesting feasibility", "battery isolation and authorised route check"],
        kpis=["units repaired", "warranty returns", "kg authorised WEEE", "defect-rate reduction", "battery incidents avoided"],
        claim_controls=["Never frame damaged batteries as quick-win circularity; authorised handling and human review come first."],
        esrs_e5_mapping=["resource outflows", "waste type hazardous/non-hazardous", "product/component recirculation"],
        cti_style_metrics=["% units repaired/refurbished", "% authorised treatment", "% component value retained"],
        circular_design_questions=["Can components be repaired?", "Can failures be prevented?", "Can product data support disassembly and recovery?"],
        fallback_controls=["authorised WEEE/battery treatment with classification evidence"],
        example_resolution_prompt="Prioritise repair/warranty routes for safe components and block damaged batteries into specialist review.",
    ),
    "organic/process residue": AdvancedMaterialPlaybook(
        material_family="organic/process residue",
        material_cycle="biological material cycle with contamination controls",
        core_circularity_question="Can clean biological residue be prevented or routed to authorised biological recovery while contaminated residues remain controlled?",
        best_fit_streams=["starch residue", "coffee grounds", "biomass fibre", "grease trap waste", "wastewater sludge"],
        high_value_intervention_patterns=["Prevent avoidable residues at source.", "Separate clean food-grade/biogenic residues from contaminated streams.", "Screen AD, composting or bio-material routes only with acceptance evidence.", "Treat grease/FOG and sludge as controlled review streams until classification is confirmed."],
        prevention_and_design_levers=["process yield improvement", "food waste separation", "maintenance schedule optimisation", "kitchen practice review"],
        value_retention_levers=["authorised AD", "composting/soil improver route", "bio-based material input", "FOG specialist recovery where lawful"],
        supplier_and_procurement_levers=["Ask contractor for acceptance criteria and treatment evidence.", "Request volume trend and contamination feedback.", "Clarify animal by-product or FOG constraints where relevant."],
        industrial_symbiosis_partner_types=["anaerobic digestion operator", "composter", "bio-based material processor", "FOG recovery contractor"],
        evidence_tests=["composition", "contamination", "classification", "contractor acceptance", "volume trend", "hygiene/ABP constraints"],
        red_flags=["grease trap waste", "unknown sludge status", "high contamination", "animal by-product constraints", "no contractor evidence"],
        routes_to_avoid=["calling all organics compostable/AD-ready", "biodiesel/FOG claims without authorised route evidence"],
        pilot_patterns=["source-prevention review", "segregated clean-organic collection", "contractor acceptance sample", "4-6 week classification review for controlled streams"],
        kpis=["kg residue prevented", "kg accepted by authorised recovery", "contamination rejection", "collection frequency trend"],
        claim_controls=["Do not claim biological recovery until classification, contamination and authorised acceptance are evidenced."],
        esrs_e5_mapping=["biological material outflows", "waste diverted from disposal", "resource recovery actions"],
        cti_style_metrics=["% clean biological residue recovered", "% source reduction", "route readiness"],
        circular_design_questions=["Can residue be prevented upstream?", "Can clean and contaminated organics be separated?"],
        fallback_controls=["authorised treatment/disposal until classification and acceptance are confirmed"],
        example_resolution_prompt="For clean residue, screen biological recovery; for grease/sludge, run classification and contractor evidence review first.",
    ),
    "process water": AdvancedMaterialPlaybook(
        material_family="process water",
        material_cycle="water resource loop",
        core_circularity_question="Can water demand be reduced or looped internally while meeting contaminant, quality and permit limits?",
        best_fit_streams=["rinse water", "process wastewater", "cleaning water"],
        high_value_intervention_patterns=["Optimise water use before treatment.", "Screen counter-flow rinse, filtration or reuse in lower-grade steps.", "Measure water quality before reuse or discharge changes."],
        prevention_and_design_levers=["flow control", "counter-current rinsing", "sensor-based shutoff", "process chemical reduction"],
        value_retention_levers=["internal reuse loop", "filtration and reuse", "closed-loop treatment", "water reduction"],
        supplier_and_procurement_levers=["Ask treatment supplier for reuse thresholds and monitoring requirements.", "Request treatment/reuse feasibility data."],
        industrial_symbiosis_partner_types=["internal lower-grade water use", "authorised treatment partner", "nearby industrial water user only if permitted"],
        evidence_tests=["flow rate", "contaminant profile", "quality requirement", "permit/discharge limits", "treatment performance"],
        red_flags=["unknown contaminants", "permit constraints", "hazard status unknown", "quality mismatch"],
        routes_to_avoid=["calling process water waste diversion", "external reuse without permit and quality evidence"],
        pilot_patterns=["metered baseline", "small-loop filtration trial", "quality monitoring before/after treatment"],
        kpis=["m3 water reused", "m3 intake reduced", "contaminant levels", "non-conformance count"],
        claim_controls=["Frame as water efficiency or reuse screening, not waste diversion, unless method and boundary are clear."],
        esrs_e5_mapping=["resource inflows", "water/resource use", "waste/resource outflow actions"],
        cti_style_metrics=["% water reused", "% water intake reduced", "measurement readiness"],
        circular_design_questions=["Can water be avoided?", "Can it be reused internally before treatment/discharge?"],
        fallback_controls=["documented treatment/discharge route while reuse feasibility is validated"],
        example_resolution_prompt="Treat process water as a resource-efficiency loop with water-quality and permit gates.",
    ),
    "energy/resource stream": AdvancedMaterialPlaybook(
        material_family="energy/resource stream",
        material_cycle="energy/resource efficiency loop",
        core_circularity_question="Can lost energy be measured and reused internally or matched to a nearby heat demand before being treated as unavailable?",
        best_fit_streams=["waste heat", "excess steam", "thermal curing losses"],
        high_value_intervention_patterns=["Measure temperature, hours and recoverable energy before claiming opportunity.", "Screen internal heat use first.", "Assess heat exchanger or pre-heating feasibility.", "Consider external heat users only after distance/timing compatibility is known."],
        prevention_and_design_levers=["insulation", "process scheduling", "heat exchanger design", "thermal load matching"],
        value_retention_levers=["internal heat recovery", "pre-heating", "thermal storage", "industrial heat symbiosis"],
        supplier_and_procurement_levers=["Ask equipment supplier for heat recovery specifications and monitoring requirements.", "Request feasibility input from energy services provider."],
        industrial_symbiosis_partner_types=["adjacent low-temperature heat user", "district heat network", "internal drying/pre-heating process"],
        evidence_tests=["temperature profile", "operating hours", "recoverable kWh", "heat-demand match", "distance and technical feasibility"],
        red_flags=["zero measured energy data", "intermittent low-grade heat", "no compatible demand", "carbon claim without boundary"],
        routes_to_avoid=["claiming diversion from zero-kg stream", "carbon savings without measured energy and emission factor method"],
        pilot_patterns=["temperature logger study", "heat mapping", "internal demand matching", "supplier feasibility note"],
        kpis=["kWh recoverable", "hours matched", "temperature profile", "estimated energy cost opportunity"],
        claim_controls=["Do not make carbon or savings claims until energy data, boundary and method are documented."],
        esrs_e5_mapping=["resource efficiency actions", "energy/resource outflow context", "anticipated financial effect screening"],
        cti_style_metrics=["% recoverable heat used", "measurement readiness", "internal demand match"],
        circular_design_questions=["Can heat be avoided, captured or reused before external symbiosis?"],
        fallback_controls=["energy-efficiency review without diversion or carbon claims"],
        example_resolution_prompt="Start with heat measurement and internal demand matching before proposing symbiosis.",
    ),
    "process mineral residue": AdvancedMaterialPlaybook(
        material_family="process mineral residue",
        material_cycle="technical mineral residue route with legal-status controls",
        core_circularity_question="Can mineral residue be reduced, characterised and matched to a lawful secondary use without creating contamination or waste-status risk?",
        best_fit_streams=["ceramic grinding sludge", "mineral fines", "abrasive sludge"],
        high_value_intervention_patterns=["Reduce residue generation at source.", "Characterise mineral composition and contaminants.", "Screen specialist recovery or construction-material use only after legal and acceptance evidence."],
        prevention_and_design_levers=["grinding fluid control", "solids separation", "process setting optimisation", "abrasive use reduction"],
        value_retention_levers=["specialist mineral recovery", "secondary aggregate/material route", "process reduction"],
        supplier_and_procurement_levers=["Ask processor for analysis requirements and acceptance specification.", "Request legal status and documentation requirements before any recovery route."],
        industrial_symbiosis_partner_types=["mineral processor", "construction-material producer", "ceramics processor"],
        evidence_tests=["composition", "contamination", "hazardous status", "moisture/handling", "acceptance/legal status"],
        red_flags=["unknown hazard status", "oily sludge", "unverified construction use", "no waste/by-product status"],
        routes_to_avoid=["using as fill or construction input without classification and legal evidence", "mixing mineral residue with hazardous streams"],
        pilot_patterns=["sample analysis", "source-reduction trial", "specialist acceptance test", "legal-status review"],
        kpis=["kg residue reduced", "analysis pass/fail", "accepted kg", "disposal cost trend"],
        claim_controls=["No beneficial-use claim until composition, contamination, legal status and acceptance evidence are available."],
        esrs_e5_mapping=["resource outflows", "waste streams", "recovery/disposal actions"],
        cti_style_metrics=["% residue characterised", "% accepted by specialist route", "claim-readiness"],
        circular_design_questions=["Can process settings reduce solids?", "Can clean separation happen before contamination increases?"],
        fallback_controls=["compliant disposal or specialist treatment until evidence supports recovery"],
        example_resolution_prompt="Characterise the mineral residue before any by-product or recovery proposal.",
    ),
}


def get_advanced_playbook(material: str | None) -> AdvancedMaterialPlaybook:
    return ADVANCED_PLAYBOOKS[normalise_material(material)]


def list_advanced_playbooks() -> list[dict[str, Any]]:
    return [playbook.to_dict() for playbook in ADVANCED_PLAYBOOKS.values()]


def get_advanced_playbook_dict(material: str | None) -> dict[str, Any]:
    return get_advanced_playbook(material).to_dict()


def build_playbook_summary() -> dict[str, Any]:
    playbooks = list_advanced_playbooks()
    return {
        "total_playbooks": len(playbooks),
        "material_families": [item["material_family"] for item in playbooks],
        "technical_cycle_count": sum("technical" in item["material_cycle"] for item in playbooks),
        "biological_or_water_energy_count": sum(
            any(token in item["material_cycle"] for token in ["biological", "water", "energy"])
            for item in playbooks
        ),
        "coverage_note": (
            "Playbooks cover the synthetic dataset material families and are designed for screening, intervention design, "
            "evidence planning and claim control. They are not legal, safety or carbon verification."
        ),
    }
