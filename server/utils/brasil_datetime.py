from datetime import datetime
from zoneinfo import ZoneInfo


class BrasilDatetime(datetime):
    """
    A subclass of datetime that provides a method to format dates in the Brazilian format.
    """

    @staticmethod
    def brasil_tz() -> ZoneInfo:
        """
        Returns the timezone information for Brazil.
        """
        return ZoneInfo("America/Sao_Paulo")

    @staticmethod
    def now_utc() -> datetime:
        """
        Returns the current date and time in the Brazilian utc.
        """
        return datetime.now(tz=BrasilDatetime.brasil_tz())

    def format_brasil(self) -> str:
        """
        Formats the date in the Brazilian format (DD/MM/YYYY).
        """
        return self.strftime("%d/%m/%Y")
