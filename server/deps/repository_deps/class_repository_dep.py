class ClassRepositoryAdapter:
    def __init__(self, building: BuildingDep, session: SessionDep, user: UserDep):
        self.building = building
        self.session = session
        self.user = user
