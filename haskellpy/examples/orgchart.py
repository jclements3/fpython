"""orgchart.py -- resolve an employee's manager's manager's email, or NOTHING
if any hop is missing. None-as-Nothing means a missing hop and a real
missing-email must stay distinguishable."""
from haskell import NOTHING, maybe_get, doM

MANAGER_OF = {"ada": "grace", "bob": "grace", "grace": "linus"}
EMAIL_OF = {"grace": "grace@corp", "linus": None}   # linus has no email on file

# --- imperative ---
def skip_manager_email_imp(emp):
    mgr = MANAGER_OF.get(emp, NOTHING)
    if mgr is NOTHING:
        return NOTHING
    skip = MANAGER_OF.get(mgr, NOTHING)
    if skip is NOTHING:
        return NOTHING
    if skip not in EMAIL_OF:
        return NOTHING
    return EMAIL_OF[skip]

# --- functional ---
@doM
def skip_manager_email_fn(emp):
    mgr = yield maybe_get(MANAGER_OF, emp)
    skip = yield maybe_get(MANAGER_OF, mgr)
    return (yield maybe_get(EMAIL_OF, skip))

# --- demo ---
if __name__ == "__main__":
    for emp in ("ada", "grace", "nobody"):
        a, b = skip_manager_email_imp(emp), skip_manager_email_fn(emp)
        assert a == b, (emp, a, b)
    print("ada's skip-manager email:", skip_manager_email_fn("ada"))
    print("grace's skip-manager email is NOTHING:",
          skip_manager_email_fn("grace") is NOTHING)
    print("orgchart: both agree")
