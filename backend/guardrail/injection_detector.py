"""Prompt Injection 检测器 — 识别用户输入中的注入/越狱攻击"""

import re


# 常见越狱/注入模式
INJECTION_PATTERNS = [
    # 角色重定义
    r"(ignore|forget|disregard|override)\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?|rules?)",
    r"you\s+are\s+now\s+(a\s+)?(DAN|evil|unethical|jailbreak)",
    r"(pretend|act|pose)\s+as\s+(if\s+you\s+are|a\s+)?",
    r"new\s+system\s+prompt",
    r"you\s+(must|have\s+to|should)\s+(ignore|disregard|bypass)",
    # 安全机制绕过
    r"(bypass|disable|remove|delete|turn\s+off)\s+(the\s+)?(security|safety|filter|guardrail|护栏)",
    r"don'?t\s+(check|validate|filter|scan)",
    r"without\s+(any\s+)?(check|validation|approval|confirmation)",
    # 隐写/编码攻击
    r"base64\s*[:-].*decode",
    r"(fromcharcode|atob|eval\s*\(|exec\s*\()",
    # Prompt 泄露
    r"(tell|show|reveal|print|display|output)\s+(me\s+)?(your|the)\s+(system\s+)?(prompt|instructions?|rules?|guidelines?)",
    r"what\s+(is|are)\s+(your|the)\s+(system\s+)?(prompt|instructions?)",
    # 中文越狱
    r"(忽略|忘记|无视|跳过|绕过).*(指令|规则|限制|护栏|安全)",
    r"(假装|扮演|装作|作为).*(角色|身份)",
]

# 输出操纵模式
OUTPUT_MANIPULATION_PATTERNS = [
    r"(reply|respond|answer|output)\s+(only\s+)?(with\s+)?['\"]?(yes|no|ok|true|false)['\"]?\s*$",
    r"(do\s+not|don'?t)\s+(explain|describe|elaborate)",
    r"(just|only)\s+(say|output|return|write)\s+['\"]",
]

# System prompt 分隔符注入
DELIMITER_INJECTION = [
    r"-{3,}\s*(system|user|assistant)",
    r"<\|im_start\|>",
    r"<\|im_end\|>",
    r"\[INST\]",
    r"\[/INST\]",
    r"<system>",
    r"</system>",
]


def detect_injection(text: str) -> dict:
    """返回检测结果: {suspicious: bool, matches: [str], score: int}"""
    matches = []
    score = 0

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            matches.append(f"注入模式: {pattern}")
            score += 3

    for pattern in OUTPUT_MANIPULATION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            matches.append(f"输出操纵: {pattern}")
            score += 1

    for pattern in DELIMITER_INJECTION:
        if re.search(pattern, text):
            matches.append(f"分隔符注入: {pattern}")
            score += 5

    suspicious = score >= 3
    return {
        "suspicious": suspicious,
        "score": score,
        "matches": matches,
        "blocked": score >= 5,
    }
