"""命令安全校验器 — 对即将执行的命令进行'二次过滤'"""

import re
import shlex
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    allowed: bool
    blocked_command: str = ""
    reason: str = ""
    suggestions: list[str] = field(default_factory=list)


# 绝对禁止的命令模式
BLOCKED_COMMANDS = [
    r"\brm\s+(-r|-rf|--recursive)\s+/",
    r"\bdd\s+if=",
    r"mkfs\.",
    r">\s*/dev/",
    r"\bchmod\s+777\s+/",
    r":\(\)\s*\{",
    r"\bwget\s+.*\|",
    r"\bcurl\s+.*\|",
]

# 需要参数校验的命令
RESTRICTED_COMMANDS = {
    "rm": {
        "allow_flags": ["-r", "-rf", "-f", "-i"],
        "forbid_flags": ["--no-preserve-root"],
        "path_must_exist": True,
    },
    "chmod": {
        "allow_modes": ["644", "640", "755", "750", "700", "600", "400"],
        "forbid_modes": ["777", "000"],
    },
    "iptables": {
        "require_confirmation": True,
    },
    "systemctl": {
        "allow_actions": ["status", "list-units", "is-enabled", "is-active", "show"],
        "forbid_actions": ["disable", "mask"],
    },
}

# 命令长度限制
MAX_COMMAND_LENGTH = 2000

# 危险字符/模式
FORBIDDEN_PATTERNS = [
    r"(&&|\|\||;)\s*(rm|dd|mkfs|shutdown|reboot)",
    r"\$\(.*\)",          # 命令替换
    r"`[^`]*`",           # 反引号命令替换
    r"\$\[\[.*\]\]",      # bash 算术扩展执行
    r"/dev/tcp/",         # bash TCP 重定向
    r"/dev/udp/",
]


def validate_command(command: str) -> ValidationResult:
    if len(command) > MAX_COMMAND_LENGTH:
        return ValidationResult(False, command, "命令长度超过限制")

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return ValidationResult(False, command, f"命令包含危险模式: {pattern}")

    for pattern in BLOCKED_COMMANDS:
        if re.search(pattern, command, re.IGNORECASE):
            return ValidationResult(False, command, f"匹配拦截规则: {pattern}")

    try:
        parts = shlex.split(command)
    except ValueError:
        return ValidationResult(False, command, "命令解析失败，可能存在语法错误")

    if not parts:
        return ValidationResult(False, "", "空命令")

    cmd_name = parts[0].split("/")[-1]

    if cmd_name in RESTRICTED_COMMANDS:
        rules = RESTRICTED_COMMANDS[cmd_name]
        if "allow_flags" in rules:
            for part in parts[1:]:
                if part.startswith("-") and not any(
                    part.startswith(f) for f in rules["allow_flags"]
                ):
                    return ValidationResult(
                        False, command,
                        f"不允许的参数: {part}",
                        [f"允许的参数: {', '.join(rules['allow_flags'])}"],
                    )

    return ValidationResult(True)
