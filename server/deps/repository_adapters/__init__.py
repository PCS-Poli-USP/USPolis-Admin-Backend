"""
## Repository Adapters

The responsability of the adapters are:
- require the necessary dependencies to access the repository (typically: building, session, user)
- Authenticate the information the user is trying to access
(example: a classroom_id, for route to proceed we must
first assure the user has permission to the building the class is in)
- Call the repository method with the necessary parameters
- Ideally, is here that the session is committed, not on the common repository
"""
