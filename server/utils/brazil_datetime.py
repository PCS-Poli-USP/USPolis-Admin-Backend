from datetime import datetime
from zoneinfo import ZoneInfo


class BrazilDatetime(datetime):
    """
    A subclass of datetime that provides a method to format dates in the Brazilian format.
    """

    @staticmethod
    def brazil_tz() -> ZoneInfo:
        """
        Returns the timezone information for Brazil.
        """
        return ZoneInfo("America/Sao_Paulo")

    @staticmethod
    def now_utc() -> datetime:
        """
        Returns the current date and time in the Brazilian utc.
        """
        return datetime.now(tz=BrazilDatetime.brazil_tz())

    def format_brazil(self) -> str:
        """
        Formats the date in the Brazilian format (DD/MM/YYYY).
        """
        return self.strftime("%d/%m/%Y")

    @staticmethod
    def current_semester() -> tuple[datetime, datetime]:
        """
        Returns the start and end dates of the current semester in Brazil.
        """
        now = BrazilDatetime.now_utc()
        if now.month <= 6:
            return BrazilDatetime(now.year, 1, 1), BrazilDatetime(now.year, 6, 30)
        else:
            return BrazilDatetime(now.year, 7, 1), BrazilDatetime(now.year + 1, 1, 1)
