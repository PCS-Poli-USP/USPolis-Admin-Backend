from typing import Annotated

from fastapi import Depends

from server.services.conflict_checker import ConflictChecker

ConflictCheckerDep = Annotated[ConflictChecker, Depends()]
