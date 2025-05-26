from datetime import datetime


class Utilities:
    @staticmethod
    def adopt_datetime(
        ivsStringDate: str, ivlFormats=["%d.%m.%Y", "%Y-%m-%d", "%m/%d/%Y"]
    ):
        for format in ivlFormats:
            try:
                return datetime.strptime(ivsStringDate, format).date()
            except Exception:
                continue
        return None
