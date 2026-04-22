import re


class AIFixEngine:
    RULES = [
        (r"ModuleNotFoundError: No module named '(\w+)'",
         lambda m: f"📦 pip install {m.group(1)}"),
        (r"SyntaxError: invalid syntax",
         "🐍 সিনট্যাক্স ত্রুটি: কোলন, ব্র্যাকেট বা ইন্ডেন্টেশন চেক করুন।"),
        (r"PermissionError",
         "🔒 পারমিশন ত্রুটি: ফাইল অ্যাক্সেস সীমিত।"),
        (r"ConnectionRefusedError",
         "🌐 কানেকশন ব্যর্থ: পোর্ট / হোস্ট সঠিক কিনা দেখুন।"),
    ]

    def analyze(self, log_text: str) -> str:
        out = []
        for pat, fix in self.RULES:
            matches = re.findall(pat, log_text)
            if matches:
                out.append(fix(matches[0]) if callable(fix) else fix)
        if not out:
            return "🤖 সাধারণ ত্রুটি স্বয়ংক্রিয়ভাবে সনাক্ত হয়নি। লগ ম্যানুয়ালি পরীক্ষা করুন।"
        return "\n".join(out)