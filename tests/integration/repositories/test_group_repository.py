import pytest
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.group_db_model import Group
from server.models.database.user_db_model import User
from server.repositories.group_repository import (
    GroupNotFound,
    GroupRepository,
    GroupWithAllClassrooms,
    GroupWithMultipleBuildings,
    GroupWithoutClassroom,
    MainGroupDeleting,
)
from server.utils.must_be_int import must_be_int
from tests.factories.model.building_model_factory import BuildingModelFactory
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.model.group_model_factory import GroupModelFactory
from tests.factories.model.user_model_factory import UserModelFactory
from tests.factories.request.group_request_factory import GroupRequestFactory


class TestGetById:
    def test_returns_the_matching_group(
        self, building: Building, group: Group, session: Session
    ) -> None:
        found = GroupRepository.get_by_id(id=must_be_int(group.id), session=session)

        assert found.id == group.id

    def test_raises_when_group_does_not_exist(self, session: Session) -> None:
        with pytest.raises(GroupNotFound):
            GroupRepository.get_by_id(id=999999, session=session)


class TestGetByIds:
    def test_returns_only_the_matching_groups(
        self, building: Building, group: Group, session: Session
    ) -> None:
        other_group = GroupModelFactory(
            building=building, session=session
        ).create_and_refresh(classrooms=[])

        found = GroupRepository.get_by_ids(
            ids=[must_be_int(group.id), must_be_int(other_group.id)], session=session
        )

        assert {g.id for g in found} == {group.id, other_group.id}


class TestGetBuildingMainGroup:
    def test_returns_the_buildings_main_group(
        self, building: Building, group: Group, session: Session
    ) -> None:
        found = GroupRepository.get_building_main_group(
            building_id=must_be_int(building.id), session=session
        )

        assert found.id == group.id


class TestGetByUserId:
    def test_returns_groups_the_user_belongs_to(
        self, building: Building, group: Group, session: Session
    ) -> None:
        user = group.users[0]

        found = GroupRepository.get_by_user_id(
            user_id=must_be_int(user.id), session=session
        )

        assert [g.id for g in found] == [group.id]

    def test_returns_empty_for_a_user_with_no_groups(
        self, session: Session
    ) -> None:
        user = UserModelFactory(session=session).create_and_refresh()

        found = GroupRepository.get_by_user_id(
            user_id=must_be_int(user.id), session=session
        )

        assert found == []


class TestGetByClassroomId:
    def test_returns_groups_the_classroom_belongs_to(
        self, admin_user: User, building: Building, session: Session
    ) -> None:
        classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        other_group = GroupModelFactory(
            building=building, session=session
        ).create_and_refresh(classrooms=[classroom])

        found = GroupRepository.get_by_classroom_id(
            classroom_id=must_be_int(classroom.id), session=session
        )

        assert [g.id for g in found] == [other_group.id]


class TestGetAll:
    def test_returns_every_group_with_classrooms_sorted_by_name(
        self,
        admin_user: User,
        building: Building,
        group: Group,
        session: Session,
    ) -> None:
        classroom_z = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh(name="Sala Z")
        classroom_a = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh(name="Sala A")
        other_group = GroupModelFactory(
            building=building, session=session
        ).create_and_refresh(classrooms=[classroom_z, classroom_a])

        groups = GroupRepository.get_all(session=session)

        found = next(g for g in groups if g.id == other_group.id)
        assert [c.name for c in found.classrooms] == ["Sala A", "Sala Z"]
        assert group.id in [g.id for g in groups]


class TestCreate:
    def test_creates_a_group_with_a_subset_of_the_buildings_classrooms(
        self,
        admin_user: User,
        building: Building,
        group: Group,
        session: Session,
    ) -> None:
        classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        # `building` already has an "all classrooms" main group (`group`), so
        # a subset of one classroom is not "all of the building's classrooms".
        ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        input = GroupRequestFactory(building=building).create_input(
            classroom_ids=[must_be_int(classroom.id)]
        )

        new_group = GroupRepository.create(input=input, session=session)
        session.commit()
        session.refresh(new_group)

        assert new_group.name == input.name
        assert [c.id for c in new_group.classrooms] == [classroom.id]

    def test_raises_when_no_classrooms_are_given(
        self, building: Building, group: Group, session: Session
    ) -> None:
        input = GroupRequestFactory(building=building).create_input(classroom_ids=None)

        with pytest.raises(GroupWithoutClassroom):
            GroupRepository.create(input=input, session=session)

    def test_raises_when_classrooms_span_multiple_buildings(
        self,
        admin_user: User,
        building: Building,
        group: Group,
        session: Session,
    ) -> None:
        other_building = BuildingModelFactory(admin_user, session).create_and_refresh()
        classroom = ClassroomModelFactory(
            creator=admin_user, building=other_building, session=session
        ).create_and_refresh()
        input = GroupRequestFactory(building=building).create_input(
            classroom_ids=[must_be_int(classroom.id)]
        )

        with pytest.raises(GroupWithMultipleBuildings):
            GroupRepository.create(input=input, session=session)

    def test_raises_when_the_group_would_have_every_classroom(
        self,
        admin_user: User,
        building: Building,
        group: Group,
        classroom: Classroom,
        session: Session,
    ) -> None:
        # `classroom` fixture is the only classroom of `building` at this
        # point, so requesting it alone means "every classroom".
        input = GroupRequestFactory(building=building).create_input(
            classroom_ids=[must_be_int(classroom.id)]
        )

        with pytest.raises(GroupWithAllClassrooms):
            GroupRepository.create(input=input, session=session)

    def test_assigns_users_and_their_building(
        self,
        admin_user: User,
        building: Building,
        group: Group,
        session: Session,
    ) -> None:
        classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        user = UserModelFactory(session=session).create_and_refresh()
        input = GroupRequestFactory(building=building).create_input(
            classroom_ids=[must_be_int(classroom.id)],
            user_ids=[must_be_int(user.id)],
        )

        new_group = GroupRepository.create(input=input, session=session)
        session.commit()
        session.refresh(new_group)
        session.refresh(user)

        assert [u.id for u in new_group.users] == [user.id]
        assert building.id in [b.id for b in (user.buildings or [])]


class TestUpdate:
    def test_updates_the_name(
        self, admin_user: User, building: Building, session: Session
    ) -> None:
        classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        # A second classroom in the building keeps `classroom` a proper
        # subset - a group with every classroom in its building is rejected
        # unless it's the main group.
        ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        target_group = GroupModelFactory(
            building=building, session=session
        ).create_and_refresh(classrooms=[classroom])
        update_input = GroupRequestFactory(building=building).update_input(
            classroom_ids=[must_be_int(classroom.id)]
        )

        updated = GroupRepository.update(
            id=must_be_int(target_group.id), input=update_input, session=session
        )
        session.commit()
        session.refresh(updated)

        assert updated.name == update_input.name

    def test_raises_when_group_does_not_exist(
        self, building: Building, session: Session
    ) -> None:
        update_input = GroupRequestFactory(building=building).update_input()

        with pytest.raises(GroupNotFound):
            GroupRepository.update(id=999999, input=update_input, session=session)

    def test_removes_a_user_and_clears_their_building_when_it_was_their_last_group_there(
        self,
        admin_user: User,
        building: Building,
        session: Session,
    ) -> None:
        classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        user = UserModelFactory(session=session).create_and_refresh(
            buildings=[building]
        )
        target_group = GroupModelFactory(
            building=building, session=session
        ).create_and_refresh(classrooms=[classroom], users=[user])

        update_input = GroupRequestFactory(building=building).update_input(
            classroom_ids=[must_be_int(classroom.id)], user_ids=[]
        )

        updated = GroupRepository.update(
            id=must_be_int(target_group.id), input=update_input, session=session
        )
        session.commit()
        session.refresh(updated)
        session.refresh(user)

        assert updated.users == []
        assert building.id not in [b.id for b in (user.buildings or [])]

    def test_updating_the_main_group_skips_classroom_validation(
        self, building: Building, group: Group, session: Session
    ) -> None:
        # `group` is the building's main group - updating it with no
        # classroom_ids must not raise GroupWithoutClassroom, unlike a
        # regular group, because main-group classroom validation is skipped.
        update_input = GroupRequestFactory(building=building).update_input(
            classroom_ids=None
        )

        updated = GroupRepository.update(
            id=must_be_int(group.id), input=update_input, session=session
        )
        session.commit()
        session.refresh(updated)

        assert updated.name == update_input.name


class TestDelete:
    def test_deletes_a_regular_group(
        self, admin_user: User, building: Building, session: Session
    ) -> None:
        classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        target_group = GroupModelFactory(
            building=building, session=session
        ).create_and_refresh(classrooms=[classroom])
        group_id = must_be_int(target_group.id)

        GroupRepository.delete(id=group_id, session=session)
        session.commit()

        with pytest.raises(GroupNotFound):
            GroupRepository.get_by_id(id=group_id, session=session)

    def test_raises_when_deleting_the_main_group(
        self, building: Building, group: Group, session: Session
    ) -> None:
        with pytest.raises(MainGroupDeleting):
            GroupRepository.delete(id=must_be_int(group.id), session=session)

    def test_removing_a_group_clears_the_building_from_users_with_no_other_group_there(
        self,
        admin_user: User,
        building: Building,
        session: Session,
    ) -> None:
        classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        user = UserModelFactory(session=session).create_and_refresh(
            buildings=[building]
        )
        target_group = GroupModelFactory(
            building=building, session=session
        ).create_and_refresh(classrooms=[classroom], users=[user])

        GroupRepository.delete(id=must_be_int(target_group.id), session=session)
        session.commit()
        session.refresh(user)

        assert building.id not in [b.id for b in (user.buildings or [])]
