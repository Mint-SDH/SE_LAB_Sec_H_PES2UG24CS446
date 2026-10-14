# Static Code Analysis - Identified Issues and Fixes

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Insecure Random Generator (`B311`) | Security | 11 | Standard pseudo-random generator `random.randint` is unsuitable for security purposes | Replaced `random` with `secrets` module (`secrets.randbelow(90000) + 10000`) |
| Try-Except-Pass Pattern (`B110`) | Security / Bug | 20-23 | Bare `try...except: pass` catches and silently swallows unexpected exceptions | Replaced with idiomatic and safe `permits.pop(vehicle_plate, None)` |
| Mutable Default Argument (`W0102`) | Bug | 9 | `zone_records=[]` mutable default persists state across subsequent function calls | Changed default argument to `None` and initialized `zone_records = []` inside function body |
| Bare `except` Clauses (`E722`, `W0702`) | Code Quality / Bug Risk | 16, 22, 29, 43 | Unspecified exception handling catches all errors indiscriminately | Replaced bare `except:` with explicit exception types (`ValueError`, `TypeError`, `KeyError`, `FileNotFoundError`) |
| Unmanaged File Resources (`R1732`, `W1514`) | Resource Leak / Quality | 42, 47-49 | `open()` used without context managers and without explicit UTF-8 encoding | Refactored file operations to `with open(..., encoding="utf-8") as f:` |
| Non-conforming Function Name (`C0103`) | Style / PEP 8 | 51 | Function `setExpiry` violates snake_case naming convention | Renamed `setExpiry` to `set_expiry` across the codebase |
| PEP 8 Spacing & Line Length (`E302`, `E305`, `E501`) | Formatting | 9, 13, 19, 25, 27, 32, 62, 68 | Lines exceed 79 chars and functions lacked 2 blank separating lines | Added 2 blank lines around functions and wrapped long lines |
| Missing Module & Function Docstrings (`C0114`, `C0116`) | Documentation | 1, 9, 19, 25, 32, 39, 46, 51, 54 | Lacked PEP 257 docstrings for module and function definitions | Added comprehensive descriptive docstrings to all functions and module header |
