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
