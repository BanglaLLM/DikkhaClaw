"""Rich lesson content — teaching plans for each lesson.

Each lesson has:
- learning_objectives: what student should understand after
- teaching_steps: ordered sequence the AI follows
- key_formulas: equations to teach
- common_mistakes: what students typically get wrong
- practice_prompts: questions to check understanding
- real_world_example: relatable analogy

The AI uses this to deliver structured, Socratic lessons instead
of random conversation.
"""

from __future__ import annotations

LESSON_CONTENT: dict[str, dict] = {
    # ══ PHYSICS — Chapter 1: Measurement ══
    "phy1-01-01": {
        "title": "Physical Quantities & SI Units",
        "learning_objectives": [
            "Distinguish between fundamental and derived quantities",
            "List the 7 SI base units with symbols",
            "Convert between unit systems",
            "Apply dimensional analysis to verify equations",
        ],
        "teaching_steps": [
            {
                "step": 1,
                "type": "intro",
                "prompt": "Start by asking: what do you think a 'physical quantity' means? Give an example.",
            },
            {
                "step": 2,
                "type": "concept",
                "prompt": "Explain fundamental vs derived quantities. Ask student to classify: length, speed, force, mass, acceleration.",
            },
            {
                "step": 3,
                "type": "teach",
                "prompt": "Introduce the 7 SI base units. Ask: which base unit is defined by a physical artifact? (kg was until 2019)",
            },
            {
                "step": 4,
                "type": "practice",
                "prompt": "Give a dimensional analysis problem: verify if v = u + at is dimensionally correct.",
            },
            {
                "step": 5,
                "type": "mastery",
                "prompt": "Ask: convert 72 km/h to m/s. Then ask a BUET-style MCQ from the question bank about units.",
            },
        ],
        "key_formulas": [
            "[M^a L^b T^c] — dimensional formula",
            "1 km/h = 5/18 m/s",
        ],
        "common_mistakes": [
            "Confusing fundamental and derived quantities",
            "Forgetting that radian is dimensionless",
            "Wrong conversion factors (km/h to m/s)",
        ],
        "practice_prompts": [
            "Is force a fundamental or derived quantity? Why?",
            "What is the dimensional formula of energy?",
            "Convert 100 km/h to m/s",
        ],
        "real_world_example": "Think of buying fabric — you measure length in meters (fundamental), but price per meter is derived from two quantities.",
    },

    "phy1-01-02": {
        "title": "Measurement & Errors",
        "learning_objectives": [
            "Use vernier caliper and screw gauge measurements",
            "Calculate absolute, relative, and percentage errors",
            "Apply rules of significant figures",
            "Propagate errors in calculations",
        ],
        "teaching_steps": [
            {"step": 1, "type": "intro", "prompt": "Ask: why can't any measurement be perfectly accurate? What causes errors?"},
            {"step": 2, "type": "concept", "prompt": "Explain systematic vs random errors with examples. Ask student for an example of each."},
            {"step": 3, "type": "teach", "prompt": "Teach vernier caliper reading: main scale + vernier scale × least count. Give a practice reading."},
            {"step": 4, "type": "practice", "prompt": "Problem: if length = 5.0 ± 0.1 cm and width = 3.0 ± 0.1 cm, what is the area with error?"},
            {"step": 5, "type": "mastery", "prompt": "Ask a BUET/DU MCQ about significant figures or error propagation."},
        ],
        "key_formulas": [
            "Least count of vernier = 1 MSD - 1 VSD",
            "Relative error = Δx/x",
            "% error = (Δx/x) × 100",
        ],
        "common_mistakes": [
            "Forgetting to add errors when multiplying measurements",
            "Confusing precision with accuracy",
            "Wrong significant figure rules for zeros",
        ],
        "practice_prompts": [
            "A vernier caliper reads 3.2 cm on main scale, 7th division matches. Least count = 0.01 cm. What is the reading?",
            "How many significant figures in 0.00340?",
        ],
        "real_world_example": "A tailor measures your waist as 32 inches — but is it exactly 32.000? The ± error matters when the shirt needs to fit perfectly.",
    },

    # ══ PHYSICS — Chapter 2: Vectors ══
    "phy1-02-01": {
        "title": "Vector Addition & Resolution",
        "learning_objectives": [
            "Distinguish scalar and vector quantities",
            "Add vectors using triangle and parallelogram law",
            "Resolve vectors into components",
            "Find resultant magnitude and direction",
        ],
        "teaching_steps": [
            {"step": 1, "type": "intro", "prompt": "Ask: what is the difference between 'speed' and 'velocity'? Why does direction matter?"},
            {"step": 2, "type": "concept", "prompt": "Explain scalar vs vector with examples. Ask student to classify: temperature, displacement, energy, momentum."},
            {"step": 3, "type": "teach", "prompt": "Teach parallelogram law of vector addition with the formula R = √(A² + B² + 2AB cos θ). Draw the diagram mentally."},
            {"step": 4, "type": "practice", "prompt": "Two forces 3N and 4N act at 90°. Find the resultant. Then ask: what if the angle was 60°?"},
            {"step": 5, "type": "mastery", "prompt": "Ask a BUET MCQ about vector resolution into components. Test if student can find Fx = F cos θ, Fy = F sin θ."},
        ],
        "key_formulas": [
            "R = √(A² + B² + 2AB cos θ)",
            "tan α = B sin θ / (A + B cos θ)",
            "Fx = F cos θ, Fy = F sin θ",
        ],
        "common_mistakes": [
            "Adding vector magnitudes directly without considering direction",
            "Confusing the angle in parallelogram law (angle between vectors vs angle with x-axis)",
            "Forgetting that vector subtraction = addition of negative vector",
        ],
        "practice_prompts": [
            "Two vectors of magnitude 5 and 12 are perpendicular. Find the resultant.",
            "Resolve a 10N force at 30° into horizontal and vertical components.",
        ],
        "real_world_example": "Imagine crossing a river — you swim forward but the current pushes you sideways. Your actual path is the vector sum of your swimming direction and the current.",
    },

    # ══ PHYSICS — Chapter 3: Dynamics ══
    "phy1-03-01": {
        "title": "Rectilinear Motion",
        "learning_objectives": [
            "Apply equations of motion (v=u+at, s=ut+½at², v²=u²+2as)",
            "Solve free fall problems with g=9.8 m/s²",
            "Interpret motion from v-t and s-t graphs",
            "Calculate stopping distance and time",
        ],
        "teaching_steps": [
            {"step": 1, "type": "intro", "prompt": "Ask: if you throw a ball up at 20 m/s, how long before it stops? What do you think happens to its speed each second?"},
            {"step": 2, "type": "concept", "prompt": "Teach the 3 equations of motion. Ask student which equation to use when: (a) no distance given, (b) no final velocity given, (c) no time given."},
            {"step": 3, "type": "teach", "prompt": "Solve a free fall problem together: a stone dropped from 80m height. Find time to reach ground and velocity on impact."},
            {"step": 4, "type": "practice", "prompt": "Problem: a car traveling at 72 km/h brakes with deceleration 5 m/s². Find stopping distance."},
            {"step": 5, "type": "mastery", "prompt": "Give a BUET admission MCQ about projectile or free fall. Test complete problem-solving ability."},
        ],
        "key_formulas": [
            "v = u + at",
            "s = ut + ½at²",
            "v² = u² + 2as",
            "For free fall: u=0, a=g=9.8 m/s²",
        ],
        "common_mistakes": [
            "Forgetting to convert km/h to m/s before calculating",
            "Wrong sign convention for deceleration (should be negative a)",
            "For upward throw: forgetting total time = 2 × time to reach max height",
        ],
        "practice_prompts": [
            "A ball is thrown up at 19.6 m/s. Find total time of flight.",
            "A car accelerates from rest at 2 m/s² for 10s. How far does it travel?",
        ],
        "real_world_example": "When you brake in a car at 60 km/h, you don't stop instantly — the stopping distance depends on your speed squared. That's why highway speed limits matter so much.",
    },

    "phy1-03-02": {
        "title": "Motion Graphs & Relative Motion",
        "learning_objectives": [
            "Read displacement, velocity, and acceleration from graphs",
            "Calculate displacement from area under v-t graph",
            "Solve relative velocity problems",
            "Understand reference frames",
        ],
        "teaching_steps": [
            {"step": 1, "type": "intro", "prompt": "Show a v-t graph description and ask: what does the slope mean? What does the area under the curve mean?"},
            {"step": 2, "type": "concept", "prompt": "Teach: slope of s-t = velocity, slope of v-t = acceleration, area under v-t = displacement."},
            {"step": 3, "type": "teach", "prompt": "Relative motion: if train A goes 60 km/h east and train B goes 40 km/h west, what is the velocity of A relative to B?"},
            {"step": 4, "type": "practice", "prompt": "A v-t graph shows: 0-4s velocity increases from 0 to 20 m/s, then constant for 6s. Find total displacement."},
            {"step": 5, "type": "mastery", "prompt": "Give a motion graph MCQ from the question bank."},
        ],
        "key_formulas": [
            "v_AB = v_A - v_B (relative velocity)",
            "Displacement = area under v-t graph",
            "Acceleration = slope of v-t graph",
        ],
        "common_mistakes": [
            "Confusing distance (always positive) with displacement (can be negative)",
            "Forgetting that area below the time axis in v-t graph is negative displacement",
            "Wrong sign in relative velocity when objects move in opposite directions",
        ],
        "practice_prompts": [
            "Two cars approach each other at 60 km/h and 40 km/h. What is their relative speed?",
            "From a v-t graph, how do you find the distance traveled vs displacement?",
        ],
        "real_world_example": "Sitting in a train, the trees seem to move backward — that's relative motion. Your velocity relative to the ground is different from your velocity relative to the train.",
    },

    # ══ CHEMISTRY — Chapter 1: পরিবেশ রসায়ন (Environmental Chemistry) ══
    "chem1-01-01": {
        "title": "Atmosphere, Pollutants & Air Quality",
        "learning_objectives": [
            "Describe the composition and layers of Earth's atmosphere",
            "Classify air pollutants as primary and secondary with examples",
            "Explain the formation of photochemical smog and acid rain with chemical equations",
            "Analyze the causes and effects of ozone layer depletion (CFCs, NOx)",
        ],
        "teaching_steps": [
            {
                "step": 1,
                "type": "intro",
                "prompt": "Ask: why do you think Dhaka's air quality is among the worst in the world during winter? What gases might be responsible?",
            },
            {
                "step": 2,
                "type": "concept",
                "prompt": "Explain the layers of the atmosphere (troposphere, stratosphere, etc.) and where ozone is concentrated. Ask: why is ozone beneficial in the stratosphere but harmful in the troposphere?",
            },
            {
                "step": 3,
                "type": "teach",
                "prompt": "Teach the chemistry of acid rain: SO2 + H2O -> H2SO3, 2SO2 + O2 -> 2SO3, SO3 + H2O -> H2SO4. Also NO2 + H2O -> HNO3 + HNO2. Ask: which industries in Bangladesh release SO2?",
            },
            {
                "step": 4,
                "type": "practice",
                "prompt": "Problem: Write the chain reaction mechanism for ozone depletion by CFCs. Cl + O3 -> ClO + O2, ClO + O -> Cl + O2. Why is Cl called a catalyst here?",
            },
            {
                "step": 5,
                "type": "mastery",
                "prompt": "Ask: the pH of normal rain is about 5.6 (not 7). Why? If a rain sample has pH 3.5, calculate the [H+] concentration and identify which acids are likely responsible.",
            },
        ],
        "key_formulas": [
            "SO2 + H2O -> H2SO3 (sulfurous acid)",
            "2SO2 + O2 -> 2SO3 ; SO3 + H2O -> H2SO4 (sulfuric acid)",
            "NO2 + H2O -> HNO3 + HNO2",
            "O3 + Cl -> ClO + O2 ; ClO + O -> Cl + O2 (net: O3 + O -> 2O2)",
            "CO2 + H2O <=> H2CO3 (why normal rain is pH ~5.6)",
        ],
        "common_mistakes": [
            "Confusing primary pollutants (directly emitted: CO, SO2, NO) with secondary pollutants (formed by reaction: O3, PAN, H2SO4)",
            "Writing the ozone depletion mechanism without showing the catalytic regeneration of Cl",
            "Forgetting that normal rainwater is already slightly acidic (pH 5.6) due to dissolved CO2, not pH 7",
        ],
        "practice_prompts": [
            "A factory emits SO2 at a rate of 500 kg/day. Write the complete pathway showing how this leads to acid rain. If all SO2 converts to H2SO4, what mass of H2SO4 is produced? (S=32, O=16, H=1)",
            "Explain with equations why the greenhouse effect of CH4 is ~25 times stronger per molecule than CO2, yet CO2 is the bigger concern overall.",
            "In Dhaka, photochemical smog is worst in winter afternoons. Explain the role of sunlight, NO2, and VOCs in smog formation.",
        ],
        "real_world_example": "In Dhaka, brick kilns around the city burn coal and release SO2 and particulates. During winter, the inversion layer traps these pollutants close to the ground, making breathing difficult — this is why your eyes water and throat hurts on foggy December mornings.",
    },

    "chem1-01-02": {
        "title": "Water & Soil Pollution and Green Chemistry",
        "learning_objectives": [
            "Explain BOD, COD, and DO as indicators of water quality",
            "Describe causes and effects of eutrophication in Bangladeshi water bodies",
            "Identify major soil pollutants (pesticides, heavy metals) and their bioaccumulation",
            "Apply the 12 principles of green chemistry to reduce pollution",
        ],
        "teaching_steps": [
            {
                "step": 1,
                "type": "intro",
                "prompt": "Ask: why do fish die in the Buriganga river near Old Dhaka? What do you think the tannery waste contains?",
            },
            {
                "step": 2,
                "type": "concept",
                "prompt": "Explain BOD (Biochemical Oxygen Demand) and DO (Dissolved Oxygen). Ask: if BOD is high, is the water clean or polluted? Why does high BOD cause fish kills?",
            },
            {
                "step": 3,
                "type": "teach",
                "prompt": "Teach eutrophication: excess N and P from fertilizers -> algal bloom -> algae die -> decomposition uses O2 -> aquatic life dies. Ask: which fertilizers used in Bangladesh cause this? (urea, TSP)",
            },
            {
                "step": 4,
                "type": "practice",
                "prompt": "Problem: A water sample has BOD of 300 mg/L. Safe drinking water BOD is <5 mg/L. Calculate by what factor the organic pollutant load must be reduced. What treatment methods can achieve this?",
            },
            {
                "step": 5,
                "type": "mastery",
                "prompt": "Green chemistry challenge: The Hazaribagh tanneries used Cr(VI) for leather tanning, contaminating soil. Suggest how green chemistry principles (atom economy, safer solvents) could redesign the process. What is the oxidation state change if Cr(VI) is reduced to Cr(III)?",
            },
        ],
        "key_formulas": [
            "BOD = initial DO - final DO (after 5 days at 20C)",
            "Eutrophication: excess PO4^3- / NO3^- -> algal bloom -> O2 depletion",
            "Atom economy = (MW of desired product / MW of all products) x 100%",
            "Cr2O7^2- + 14H+ + 6e- -> 2Cr^3+ + 7H2O (Cr(VI) to Cr(III) reduction)",
        ],
        "common_mistakes": [
            "Confusing BOD with COD — BOD is biological oxygen demand (5-day test), COD uses chemical oxidant (K2Cr2O7) and measures total oxidizable matter",
            "Thinking eutrophication is caused by toxic chemicals — it is actually caused by excess nutrients (N, P) leading to algal overgrowth",
            "Mixing up bioaccumulation (increase within an organism) with biomagnification (increase along the food chain)",
        ],
        "practice_prompts": [
            "The arsenic contamination in Bangladesh groundwater is a major crisis. If a tube well has As concentration of 0.15 mg/L and the WHO safe limit is 0.01 mg/L, by what percentage must arsenic be removed? Suggest a chemical method for arsenic removal (hint: co-precipitation with Fe(OH)3).",
            "Calculate the atom economy of the reaction: CH3CH2OH + CH3COOH -> CH3COOCH2CH3 + H2O. Is this reaction atom-efficient? (C=12, H=1, O=16)",
        ],
        "real_world_example": "The Buriganga river in Dhaka was once a lifeline but is now biologically dead in the dry season. Tannery waste from Hazaribagh dumped chromium compounds, dyes, and organic waste directly into the river, pushing BOD above 30 mg/L — fish cannot survive when DO drops below 4 mg/L.",
    },

    # ══ CHEMISTRY — Chapter 2: গুণগত রসায়ন (Qualitative Chemistry) ══
    "chem1-02-01": {
        "title": "Stoichiometry & Chemical Equations",
        "learning_objectives": [
            "Balance complex chemical equations including redox reactions",
            "Apply the mole concept to calculate masses, volumes, and number of particles",
            "Solve limiting reagent and percentage yield problems",
            "Use Avogadro's law and molar volume (22.4 L at STP) in gas calculations",
        ],
        "teaching_steps": [
            {
                "step": 1,
                "type": "intro",
                "prompt": "Ask: if you react 10g of Zn with excess HCl, can you predict exactly how much H2 gas you will get? How? This is the power of stoichiometry.",
            },
            {
                "step": 2,
                "type": "concept",
                "prompt": "Review the mole concept: 1 mol = 6.022 x 10^23 particles = molar mass in grams = 22.4 L gas at STP. Ask: how many molecules are in 1.8 g of water? (H=1, O=16)",
            },
            {
                "step": 3,
                "type": "teach",
                "prompt": "Teach limiting reagent: if 5 mol H2 reacts with 2 mol O2 (2H2 + O2 -> 2H2O), which is limiting? Calculate moles of H2O formed and excess reactant remaining.",
            },
            {
                "step": 4,
                "type": "practice",
                "prompt": "Problem: 50 mL of 0.1M AgNO3 reacts with 30 mL of 0.2M NaCl. Find: (a) limiting reagent, (b) mass of AgCl precipitate, (c) concentration of excess ions. (Ag=108, Cl=35.5, N=14, O=16, Na=23)",
            },
            {
                "step": 5,
                "type": "mastery",
                "prompt": "BUET-level: In the thermite reaction 2Al + Fe2O3 -> Al2O3 + 2Fe, 5.4g Al reacts with 24g Fe2O3. Find the theoretical yield of Fe and the percentage yield if only 8.4g Fe is actually obtained. (Al=27, Fe=56, O=16)",
            },
        ],
        "key_formulas": [
            "n = m / M (moles = mass / molar mass)",
            "n = N / NA (moles = number of particles / Avogadro's number)",
            "PV = nRT (ideal gas: P in atm, V in L, R = 0.0821 L.atm/mol.K)",
            "At STP (0C, 1 atm): 1 mol gas = 22.4 L",
            "Percentage yield = (actual yield / theoretical yield) x 100%",
            "Molarity (M) = moles of solute / volume of solution in L",
        ],
        "common_mistakes": [
            "Forgetting to convert grams to moles before doing stoichiometric calculations",
            "Assuming the reactant present in smaller mass is always the limiting reagent — it depends on mole ratio, not mass",
            "Using 22.4 L/mol at non-STP conditions — this value is only valid at 0C and 1 atm",
        ],
        "practice_prompts": [
            "How many grams of CO2 are produced when 50g of CaCO3 is completely decomposed? (CaCO3 -> CaO + CO2). If the actual yield is 19.8g, what is the percentage yield? (Ca=40, C=12, O=16)",
            "At STP, what volume of O2 is needed to completely combust 11.2 L of CH4? (CH4 + 2O2 -> CO2 + 2H2O)",
            "A 250 mL solution contains 5.85g NaCl. Calculate the molarity. If 50 mL of this is diluted to 500 mL, what is the new concentration? (Na=23, Cl=35.5)",
        ],
        "real_world_example": "When you take an antacid tablet (500mg CaCO3) for acidity, stoichiometry tells us exactly how much stomach acid (HCl) it can neutralize: CaCO3 + 2HCl -> CaCl2 + H2O + CO2. That is why the dose matters — too little does not help, too much wastes medicine.",
    },

    "chem1-02-02": {
        "title": "Oxidation-Reduction & Balancing Redox Reactions",
        "learning_objectives": [
            "Assign oxidation numbers to atoms in compounds and ions",
            "Identify oxidizing agents and reducing agents in a reaction",
            "Balance redox equations using the ion-electron (half-reaction) method",
            "Balance redox equations using the oxidation number change method",
        ],
        "teaching_steps": [
            {
                "step": 1,
                "type": "intro",
                "prompt": "Ask: when iron rusts (4Fe + 3O2 -> 2Fe2O3), is iron gaining or losing electrons? What happens to oxygen? This is the heart of redox chemistry.",
            },
            {
                "step": 2,
                "type": "concept",
                "prompt": "Teach oxidation number rules: free element = 0, monatomic ion = charge, O = -2 (except peroxides), H = +1 (except metal hydrides). Ask: what is the oxidation number of Mn in KMnO4? of Cr in K2Cr2O7?",
            },
            {
                "step": 3,
                "type": "teach",
                "prompt": "Demonstrate the ion-electron method for balancing: MnO4^- + Fe^2+ -> Mn^2+ + Fe^3+ in acidic medium. Write separate half-reactions, balance atoms and charge, then combine.",
            },
            {
                "step": 4,
                "type": "practice",
                "prompt": "Balance using the ion-electron method in acidic solution: Cr2O7^2- + SO3^2- -> Cr^3+ + SO4^2-. Identify the oxidizing and reducing agents.",
            },
            {
                "step": 5,
                "type": "mastery",
                "prompt": "BUET-level: Balance in basic medium: MnO4^- + I^- -> MnO2 + IO3^-. Verify your answer by checking that atoms and charges balance on both sides.",
            },
        ],
        "key_formulas": [
            "Oxidation = loss of electrons (OIL), Reduction = gain of electrons (RIG)",
            "Oxidizing agent is reduced, Reducing agent is oxidized",
            "In acidic medium: balance O with H2O, balance H with H+",
            "In basic medium: after balancing in acid, add OH^- to neutralize H+ on both sides",
            "KMnO4 in acidic medium: MnO4^- + 8H+ + 5e^- -> Mn^2+ + 4H2O",
            "K2Cr2O7 in acidic medium: Cr2O7^2- + 14H+ + 6e^- -> 2Cr^3+ + 7H2O",
        ],
        "common_mistakes": [
            "Forgetting to balance oxygen atoms with H2O and hydrogen atoms with H+ before balancing charge with electrons",
            "Not multiplying half-reactions to equalize electrons before adding them — electrons must cancel completely",
            "Confusing oxidizing agent with the species being oxidized — the oxidizing agent itself gets reduced",
        ],
        "practice_prompts": [
            "Assign oxidation numbers to every atom in: K2Cr2O7, Na2S2O3, H2SO4, KMnO4. What is the oxidation state of S in Na2S2O3?",
            "Balance in acidic medium: Cu + HNO3(dilute) -> Cu(NO3)2 + NO + H2O. How many moles of HNO3 react per mole of Cu?",
            "In the reaction Zn + CuSO4 -> ZnSO4 + Cu, identify which species is oxidized, which is reduced, the oxidizing agent, and the reducing agent.",
        ],
        "real_world_example": "The batteries in your phone work on redox chemistry. In a lithium-ion battery, Li is oxidized at the anode (loses electrons) and the electrons flow through the circuit to power your device before being accepted at the cathode — that current flow is what charges your phone.",
    },

    # ══ CHEMISTRY — Chapter 3: মৌলের পর্যায়বৃত্ত ধর্ম (Periodic Properties) ══
    "chem1-03-01": {
        "title": "Periodic Table & Electron Configuration",
        "learning_objectives": [
            "Write electron configurations using Aufbau principle, Hund's rule, and Pauli exclusion",
            "Relate electron configuration to position in the periodic table (block, group, period)",
            "Explain the anomalous configurations of Cr (3d5 4s1) and Cu (3d10 4s1)",
            "Predict properties of elements based on their position in the periodic table",
        ],
        "teaching_steps": [
            {
                "step": 1,
                "type": "intro",
                "prompt": "Ask: if I give you the atomic number of an element, can you predict which group and period it belongs to? How? The secret is electron configuration.",
            },
            {
                "step": 2,
                "type": "concept",
                "prompt": "Teach the Aufbau order: 1s, 2s, 2p, 3s, 3p, 4s, 3d, 4p... Use the (n+l) rule. Ask: why does 4s fill before 3d?",
            },
            {
                "step": 3,
                "type": "teach",
                "prompt": "Write configurations for Fe (Z=26), Cr (Z=24), Cu (Z=29). Explain why Cr is [Ar] 3d5 4s1 not [Ar] 3d4 4s2 — extra stability of half-filled d subshell.",
            },
            {
                "step": 4,
                "type": "practice",
                "prompt": "Problem: Write the electron configuration of Mn^2+ (Z=25) and Fe^3+ (Z=26). Which one is more stable and why? (Hint: look at the d subshell)",
            },
            {
                "step": 5,
                "type": "mastery",
                "prompt": "BUET-level: An element has the configuration [Ar] 3d10 4s2 4p3. Identify the element, its block, group, period, and predict whether it is a metal, nonmetal, or metalloid. What is its highest possible oxidation state?",
            },
        ],
        "key_formulas": [
            "Aufbau order (n+l rule): 1s < 2s < 2p < 3s < 3p < 4s < 3d < 4p < 5s < 4d < 5p ...",
            "Maximum electrons in a shell: 2n^2",
            "Maximum electrons in a subshell: 2(2l+1)",
            "For ions: remove electrons from outermost shell first (4s before 3d for transition metals)",
            "Half-filled (d5) and fully-filled (d10) configurations have extra stability",
        ],
        "common_mistakes": [
            "When writing ion configurations for transition metals, removing electrons from 3d instead of 4s first — Fe^2+ is [Ar] 3d6, NOT [Ar] 3d4 4s2",
            "Forgetting the anomalous configurations of Cr and Cu due to half-filled and fully-filled d orbital stability",
            "Confusing the order of filling (4s before 3d) with the order of removing electrons (4s removed first for ions)",
        ],
        "practice_prompts": [
            "Write the electron configuration of Ni (Z=28), Ni^2+, and Cu+ (Z=29). Which of these has a completely filled d subshell?",
            "An element has the configuration [Kr] 4d5 5s1. Identify the element and explain why it does not have the configuration [Kr] 4d4 5s2.",
        ],
        "real_world_example": "The vibrant colors in fireworks come from electron configurations. When heated, electrons jump to higher energy levels and emit specific colors when they fall back — Na gives yellow, Cu gives green-blue, Sr gives red. This is why the periodic table matters even in celebrations like Pohela Boishakh fireworks.",
    },

    "chem1-03-02": {
        "title": "Periodic Trends: Radius, IE, EA & Electronegativity",
        "learning_objectives": [
            "Explain trends in atomic radius, ionic radius across periods and down groups",
            "Compare ionization energies and identify anomalies (Be>B, N>O)",
            "Distinguish electron affinity and electronegativity",
            "Use periodic trends to predict chemical behavior and bond type",
        ],
        "teaching_steps": [
            {
                "step": 1,
                "type": "intro",
                "prompt": "Ask: which atom is bigger — Na or Cl? They are in the same period. What about Na or K? Why does size change across and down the table?",
            },
            {
                "step": 2,
                "type": "concept",
                "prompt": "Teach atomic radius trend: decreases across a period (more protons, same shell), increases down a group (more shells). Ask: why is Na+ much smaller than Na, but Cl^- is larger than Cl?",
            },
            {
                "step": 3,
                "type": "teach",
                "prompt": "Teach ionization energy trends and anomalies. IE increases across a period but B < Be (2p1 easier to remove than 2s2) and O < N (paired 2p4 electron easier than half-filled 2p3). Explain with orbital diagrams.",
            },
            {
                "step": 4,
                "type": "practice",
                "prompt": "Arrange in order of increasing first ionization energy: Na, Mg, Al, Si, P. Explain any anomalies. Then arrange O, S, Se in order of increasing electron affinity.",
            },
            {
                "step": 5,
                "type": "mastery",
                "prompt": "BUET-level: The first ionization energies (kJ/mol) of four consecutive elements are: 786, 1086, 1402, 1314. Identify the elements and explain why the 4th value is lower than the 3rd. Also predict which of these elements forms the most stable +2 ion.",
            },
        ],
        "key_formulas": [
            "Atomic radius: decreases L->R across period, increases top->bottom in group",
            "Ionic radius: cation < atom < anion (for same element)",
            "Isoelectronic species: more protons = smaller radius (O^2- > F^- > Na+ > Mg^2+)",
            "IE1 < IE2 < IE3 ... (successive IEs always increase)",
            "Electronegativity (Pauling): F(4.0) > O(3.5) > N(3.0) > Cl(3.0)",
            "Electron affinity: most negative (exothermic) for halogens; noble gases ~0",
        ],
        "common_mistakes": [
            "Thinking atomic radius always decreases across a period without exception — actually d-block elements show very small changes due to poor shielding by d electrons",
            "Confusing electron affinity with electronegativity — EA is energy released when an atom gains one electron (measurable), electronegativity is the tendency to attract shared electrons in a bond (relative scale)",
            "Not recognizing IE anomalies: Be > B and N > O due to subshell stability — this is a very common BUET/DU admission question",
        ],
        "practice_prompts": [
            "Arrange the following isoelectronic species in order of increasing ionic radius: Na+, F^-, O^2-, Mg^2+, N^3-. Explain your reasoning.",
            "The second ionization energy of Na is dramatically higher than its first IE, but for Mg the jump is less dramatic. Explain using electron configuration.",
            "Which has a more negative electron affinity: Cl or F? Explain why, despite F being more electronegative. (Hint: consider the small size of the 2p orbital)",
        ],
        "real_world_example": "The reason table salt (NaCl) forms so readily is explained by periodic trends. Na has very low ionization energy (easy to lose its electron) and Cl has very high electron affinity (eager to gain one). This huge difference in electronegativity across period 3 drives the formation of ionic bonds — the same chemistry that preserves fish (shutki) in Cox's Bazar.",
    },
}


def get_lesson_content(lesson_id: str) -> dict | None:
    return LESSON_CONTENT.get(lesson_id)


def get_teaching_prompt(lesson_id: str, step: int = 1) -> str | None:
    content = LESSON_CONTENT.get(lesson_id)
    if not content:
        return None
    steps = content.get("teaching_steps", [])
    for s in steps:
        if s["step"] == step:
            return s["prompt"]
    return None
