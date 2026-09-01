from server.models.http.responses.group_response_models import GroupResponse
from tests.utils.academic_test_utils import make_building, make_classroom, make_group, make_user


class TestGroupResponse:
    def test_from_a_non_main_group_uses_its_own_classrooms(self) -> None:
        building = make_building(name="Bloco A")
        group = make_group(building=building, name="Grupo B")
        classroom = make_classroom(building=building, name="Sala 1")
        group.classrooms = [classroom]
        user = make_user(name="Ana")
        group.users = [user]

        data = GroupResponse.from_group(group)

        assert data.id == group.id
        assert data.building_id == building.id
        assert data.building == "Bloco A"
        assert data.name == "Grupo B"
        assert data.main is False
        assert data.classroom_ids == [classroom.id]
        assert data.user_ids == [user.id]

    def test_from_the_main_group_uses_every_building_classroom_sorted_by_name(
        self,
    ) -> None:
        building = make_building(name="Bloco A")
        group = make_group(building=building, name="Grupo Principal")
        building.main_group_id = group.id
        classroom_b = make_classroom(building=building, name="Sala B")
        classroom_a = make_classroom(building=building, name="Sala A")
        building.classrooms = [classroom_b, classroom_a]
        # This group's own `classrooms` link is deliberately left empty - the
        # main group is meant to represent every classroom in the building,
        # not just the ones explicitly linked to it.
        group.classrooms = []

        data = GroupResponse.from_group(group)

        assert data.main is True
        assert data.classroom_ids == [classroom_a.id, classroom_b.id]

    def test_from_group_list(self) -> None:
        building = make_building()
        group1 = make_group(building=building)
        group2 = make_group(building=building)

        data = GroupResponse.from_group_list([group1, group2])

        assert [d.id for d in data] == [group1.id, group2.id]
