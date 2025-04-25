from enum import Enum


class AllocationEnum(Enum):
    UNALLOCATED = "Não alocada"
    UNALLOCATED_CLASSROOM_ID = "Sala não alocada"
    UNALLOCATED_BUILDING_ID = "Prédio não alocado"

    @staticmethod
    def values() -> list["AllocationEnum"]:
        return [
            AllocationEnum.UNALLOCATED,
            AllocationEnum.UNALLOCATED_CLASSROOM_ID,
            AllocationEnum.UNALLOCATED_BUILDING_ID,
        ]
