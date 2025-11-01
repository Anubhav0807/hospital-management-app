from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .hospital import *
from .user import *

"""
__all__ is a special variable in Python modules and packages that defines
the public interface of a module. It is a list of strings that specify
the names of the symbols (variables, functions, classes) that should be imported
when using the from module import * syntax.

When __all__ is defined in a module, only the names included in the list
will be imported when using a wildcard import. If __all__ is not defined,
all public names (those not starting with an underscore) are imported.
"""
__all__ = [
  "db", "User", "Doctor", "Patient", "RoleEnum", "GenderEnum",
  "Availability", "Appointment", "Treatment", "Department", "StatusEnum"
]
