"""意图风险过滤器 — 对用户自然语言指令进行安全审核"""

import re
from enum import Enum


class RiskLevel(str, Enum):
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    DANGEROUS = "dangerous"


# 危险操作关键词（直接拒绝）
DANGEROUS_PATTERNS = [
    r"\brm\s+(-rf?|--recursive)\b",
    r"\bdd\s+if=",
    r">\s*/dev/sd[a-z]",
    r"mkfs\.",
    r":\(\)\s*\{\s*:\|:",
    r"\bchmod\s+(-R\s+)?777",
    r"\bchown\s+-R\s+root",
    r"\bwget\s+.*\|\s*(sh|bash)",
    r"\bcurl\s+.*\|\s*(sh|bash)",
    r"nc\s+-[lL].*-[eE]",
]

# 可疑操作关键词（需要二次确认）
SUSPICIOUS_PATTERNS = [
    r"\bkill\s+-9",
    r"\bshutdown\b",
    r"\breboot\b",
    r"\biptables\s+-F",
    r"\buserdel\b",
    r"\bpasswd\b",
    r"\bsu\s+-",
    r"\bsudo\s+su",
    r">\s*/etc/",
    r"\bsystemctl\s+disable\b",
]

# 安全操作关键词
SAFE_PATTERNS = [
    r"\b(free|top|df|du|ps|lsof)\b",
    r"\b(cat|head|tail|less|grep)\b",
    r"\b(systemctl\s+status|journalctl)\b",
    r"\b(ss|netstat|ip\s+addr|ifconfig)\b",
    r"\b(who|w|last|uptime)\b",
    r"\b(查看|检查|显示|查询|获取|列出)",
]


def classify_intent(text: str) -> tuple[RiskLevel, str]:
    """返回 (风险等级, 匹配到的规则说明)"""
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return RiskLevel.DANGEROUS, f"匹配危险模式: {pattern}"

    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return RiskLevel.SUSPICIOUS, f"匹配可疑模式: {pattern}"

    for pattern in SAFE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return RiskLevel.SAFE, ""

    return RiskLevel.SUSPICIOUS, "无法明确分类，建议人工确认"


def filter_intent(text: str) -> dict:
    level, reason = classify_intent(text)
    return {
        "allowed": level != RiskLevel.DANGEROUS,
        "require_confirmation": level == RiskLevel.SUSPICIOUS,
        "risk_level": level.value,
        "reason": reason,
    }
