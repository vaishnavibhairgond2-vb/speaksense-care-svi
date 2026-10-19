
from svi.pipeline import run

SAMPLES = [
    "They threatened to kill me and I am very scared",
    "I feel hopeless and I want to end my life",
    "I want to file a complaint about a delay in my compensation",
    "Nobody in the village talks to me anymore, they have boycotted my family",
    "Thank you, the officer helped me and I feel much better now",
    "मुझे बहुत डर लग रहा है, वे रोज़ धमकी देते हैं",

    # Additional test cases
    "I am safe now and my family is supporting me",
    "Someone threatened me yesterday, but I am safe today",
    "मुझे अब डर नहीं लग रहा है और मैं सुरक्षित हूँ",
    "माझ्या कुटुंबाचा मला पाठिंबा आहे आणि मी सुरक्षित आहे",
]

for text in SAMPLES:
    try:
        result = run(text=text)
        scores = result["text_scores"]

        print("\n" + "=" * 65)
        print("TEXT:", text)
        print("SVI:", result["svi"], "| Category:", result["category"])

        print(
            "Fear: %.2f | Depression: %.2f | Intimidation: %.2f | "
            "Isolation: %.2f | Suicidal: %.2f"
            % (
                scores["fear"],
                scores["depression"],
                scores["intimidation"],
                scores["isolation"],
                scores["suicidal"],
            )
        )

        print(
            "Flags: suicide =",
            scores["suicide_flag"],
            "| threat =",
            scores["threat_flag"],
        )

        print(
            "Review signals: suicide =",
            scores.get("suicide_review"),
            "| threat =",
            scores.get("threat_review"),
        )

    except Exception as error:
        print("\nERROR for:", text)
        print(type(error).__name__ + ":", error)
