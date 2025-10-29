from server.models.dicts.base.exam_base_dict import ExamBaseDict
from tests.factories.base.base_factory import BaseFactory


class ExamBaseFactory(BaseFactory):
    def __init__(self, subject_id: int) -> None:
        super().__init__()
        self.subject_id = subject_id

    def get_base_defaults(self) -> ExamBaseDict:
        """
        Get a Random ExamBaseDict, only need to pass the subject_id (must be valid)\n
        """
        return {
            "subject_id": self.subject_id,
        }
