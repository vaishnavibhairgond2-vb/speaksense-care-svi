from svi.pipeline import run

SAMPLES = [
    "They threatened to kill me and I am very scared",
    "I feel hopeless and I want to end my life",
    "I want to file a complaint about a delay in my compensation",
    "Nobody in the village talks to me anymore, they have boycotted my family",
    "Thank you, the officer helped me and I feel much better now",
    "मुझे बहुत डर लग रहा है, वे रोज़ धमकी देते हैं",
]

for s in SAMPLES:
    r = run(text=s)
    t = r["text_scores"]
    print("\nTEXT:", s)
    print("  SVI:", r["svi"], "| Category:", r["category"])
    print("  fear %.2f | dep %.2f | intim %.2f | isol %.2f | suic %.2f"
          % (t["fear"], t["depression"], t["intimidation"], t["isolation"], t["suicidal"]))
    print("  flags: suicide =", t["suicide_flag"], "| threat =", t["threat_flag"])