
from svi.pipeline import run

# Manually assigned evaluation labels.
# These are test targets, not clinical ground truth.

TEST_CASES = [
    # 1. Direct threat, no suicidal statement
    {
        "text": "They threatened to kill me and I am very scared",
        "expected_suicide_review": False,
        "expected_threat_review": True,
    },
    # 2. Explicit suicidal ideation
    {
        "text": "I feel hopeless and I want to end my life",
        "expected_suicide_review": True,
        "expected_threat_review": False,
    },
    # 3. Ordinary administrative complaint
    {
        "text": "I want to file a complaint about a delay in my compensation",
        "expected_suicide_review": False,
        "expected_threat_review": False,
    },
    # 4. Social isolation
    {
        "text": "Nobody in the village talks to me anymore, they have boycotted my family",
        "expected_suicide_review": False,
        "expected_threat_review": False,
    },
    # 5. Feeling better after support
    {
        "text": "Thank you, the officer helped me and I feel much better now",
        "expected_suicide_review": False,
        "expected_threat_review": False,
    },
    # 6. Hindi threat
    {
        "text": "मुझे बहुत डर लग रहा है, वे रोज़ धमकी देते हैं",
        "expected_suicide_review": False,
        "expected_threat_review": True,
    },
    # 7. Current safety and family support
    {
        "text": "I am safe now and my family is supporting me",
        "expected_suicide_review": False,
        "expected_threat_review": False,
    },
    # 8. Past threat, currently safe
    {
        "text": "Someone threatened me yesterday, but I am safe today",
        "expected_suicide_review": False,
        "expected_threat_review": True,
    },
    # 9. Hindi safety statement
    {
        "text": "मुझे अब डर नहीं लग रहा है और मैं सुरक्षित हूँ",
        "expected_suicide_review": False,
        "expected_threat_review": False,
    },
    # 10. Marathi safety and family support
    {
        "text": "माझ्या कुटुंबाचा मला पाठिंबा आहे आणि मी सुरक्षित आहे",
        "expected_suicide_review": False,
        "expected_threat_review": False,
    },
    # 11. Self-harm negation
    {
        "text": "I do not want to hurt myself. I want help staying safe.",
        "expected_suicide_review": False,
        "expected_threat_review": False,
    },
    # 12. Explicit suicide-related statement
    {
        "text": "I am thinking about suicide and need help",
        "expected_suicide_review": True,
        "expected_threat_review": False,
    },

    # Additional evaluation cases

    # 13. Direct wish to die
    {
        "text": "I want to die",
        "expected_suicide_review": True,
        "expected_threat_review": False,
    },
    # 14. Denial of suicidal thoughts
    {
        "text": "I am not suicidal and I do not want to die",
        "expected_suicide_review": False,
        "expected_threat_review": False,
    },
    # 15. No reason to live
    {
        "text": "I feel there is no reason to live anymore",
        "expected_suicide_review": True,
        "expected_threat_review": False,
    },
    # 16. Request for help without explicit suicide wording
    {
        "text": "I feel completely overwhelmed and I don't know how to continue",
        "expected_suicide_review": False,
        "expected_threat_review": False,
    },
    # 17. Threat of physical violence
    {
        "text": "He said he will beat me if I report him",
        "expected_suicide_review": False,
        "expected_threat_review": True,
    },
    # 18. Threat to burn the person
    {
        "text": "My relatives said they will burn me alive",
        "expected_suicide_review": False,
        "expected_threat_review": True,
    },
    # 19. General fear without explicit threat
    {
        "text": "I feel frightened when I have to go outside alone",
        "expected_suicide_review": False,
        "expected_threat_review": False,
    },
    # 20. Current support after a difficult experience
    {
        "text": "My friend is with me and I feel safe at the moment",
        "expected_suicide_review": False,
        "expected_threat_review": False,
    },
    # 21. Hindi explicit suicide-related phrase
    {
        "text": "मैं आत्महत्या के बारे में सोच रहा हूँ",
        "expected_suicide_review": True,
        "expected_threat_review": False,
    },
    # 22. Hindi denial of suicidal intent
    {
        "text": "मुझे आत्महत्या नहीं करनी है",
        "expected_suicide_review": False,
        "expected_threat_review": False,
    },
    # 23. Hindi threat
    {
        "text": "उसने मुझे जान से मारने की धमकी दी",
        "expected_suicide_review": False,
        "expected_threat_review": True,
    },
    # 24. Marathi threat
    {
        "text": "तो मला मारून टाकण्याची धमकी देतो",
        "expected_suicide_review": False,
        "expected_threat_review": True,
    },
    # 25. Marathi safety statement
    {
        "text": "मी आता सुरक्षित आहे आणि माझे मित्र माझ्यासोबत आहेत",
        "expected_suicide_review": False,
        "expected_threat_review": False,
    },
    # 26. Threat and suicidal ideation both present
    {
        "text": "He keeps threatening me, and I have been thinking about suicide",
        "expected_suicide_review": True,
        "expected_threat_review": True,
    },
    # 27. Threat in reported speech
    {
        "text": "My neighbour threatened me last week",
        "expected_suicide_review": False,
        "expected_threat_review": True,
    },
    # 28. Complaint with no explicit threat
    {
        "text": "I need help understanding the status of my case",
        "expected_suicide_review": False,
        "expected_threat_review": False,
    },
    # 29. Hindi distress without explicit suicide wording
    {
        "text": "मैं बहुत परेशान हूँ और मुझे किसी की मदद चाहिए",
        "expected_suicide_review": False,
        "expected_threat_review": False,
    },
    # 30. Marathi distress without explicit suicide wording
    {
        "text": "मी खूप घाबरले आहे आणि मला मदत हवी आहे",
        "expected_suicide_review": False,
        "expected_threat_review": False,
    },
]


def update_counts(counts, expected, actual):
    if expected and actual:
        counts["TP"] += 1
    elif not expected and not actual:
        counts["TN"] += 1
    elif not expected and actual:
        counts["FP"] += 1
    else:
        counts["FN"] += 1


def show_metrics(name, counts):
    tp = counts["TP"]
    tn = counts["TN"]
    fp = counts["FP"]
    fn = counts["FN"]

    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total else 0
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0

    print(f"\n{name} REVIEW EVALUATION")
    print(f"TP={tp} | TN={tn} | FP={fp} | FN={fn}")
    print(f"Accuracy:  {accuracy:.2%}")
    print(f"Precision: {precision:.2%}")
    print(f"Recall:    {recall:.2%}")


suicide_counts = {"TP": 0, "TN": 0, "FP": 0, "FN": 0}
threat_counts = {"TP": 0, "TN": 0, "FP": 0, "FN": 0}

print("=" * 72)
print("SPEAKSENSE CARE - EXPANDED TEXT REVIEW EVALUATION")
print(f"Total test cases: {len(TEST_CASES)}")
print("=" * 72)

for index, case in enumerate(TEST_CASES, start=1):
    text = case["text"]

    try:
        result = run(text=text)
        scores = result["text_scores"]

        actual_suicide = bool(scores.get("suicide_review", False))
        actual_threat = bool(scores.get("threat_review", False))

        expected_suicide = case["expected_suicide_review"]
        expected_threat = case["expected_threat_review"]

        update_counts(
            suicide_counts, expected_suicide, actual_suicide
        )
        update_counts(
            threat_counts, expected_threat, actual_threat
        )

        suicide_status = (
            "OK" if expected_suicide == actual_suicide
            else "MISMATCH"
        )
        threat_status = (
            "OK" if expected_threat == actual_threat
            else "MISMATCH"
        )

        print("\n" + "-" * 72)
        print(f"TEST {index}: {text}")
        print(f"SVI: {result['svi']} | Category: {result['category']}")
        print(
            f"Suicide review: expected={expected_suicide}, "
            f"actual={actual_suicide} [{suicide_status}]"
        )
        print(
            f"Threat review: expected={expected_threat}, "
            f"actual={actual_threat} [{threat_status}]"
        )
        print(
            "Scores: "
            f"fear={scores['fear']:.2f}, "
            f"depression={scores['depression']:.2f}, "
            f"intimidation={scores['intimidation']:.2f}, "
            f"isolation={scores['isolation']:.2f}, "
            f"suicidal={scores['suicidal']:.2f}"
        )

    except Exception as error:
        print(f"\nTEST {index} FAILED: {text}")
        print(f"{type(error).__name__}: {error}")


print("\n" + "=" * 72)
show_metrics("SUICIDE", suicide_counts)
show_metrics("THREAT", threat_counts)
print("\nEvaluation finished.")
print("Labels are manually assigned evaluation targets.")
print("These small tests do not establish clinical validity or safety.")
