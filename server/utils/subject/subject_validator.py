class SubjectValidator:
    @staticmethod
    def validate_subject_code(code: str) -> bool:
        if (len(code) != 7):
            return False
        return True
