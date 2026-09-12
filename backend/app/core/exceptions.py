from enum import Enum


class ErrorCode(str, Enum):
    SPILL_NOT_FOUND = "SPILL_NOT_FOUND"
    VESSEL_NOT_FOUND = "VESSEL_NOT_FOUND"
    MODEL_INFERENCE_FAILED = "MODEL_INFERENCE_FAILED"
    AI_SERVICE_UNAVAILABLE = "AI_SERVICE_UNAVAILABLE"
    AIS_SERVICE_UNAVAILABLE = "AIS_SERVICE_UNAVAILABLE"
    GIS_SERVICE_UNAVAILABLE = "GIS_SERVICE_UNAVAILABLE"
    ATTRIBUTION_SERVICE_UNAVAILABLE = "ATTRIBUTION_SERVICE_UNAVAILABLE"
    FORECAST_SERVICE_UNAVAILABLE = "FORECAST_SERVICE_UNAVAILABLE"
    IMPACT_SERVICE_UNAVAILABLE = "IMPACT_SERVICE_UNAVAILABLE"
    INVALID_GEOMETRY = "INVALID_GEOMETRY"
    INVALID_COORDINATES = "INVALID_COORDINATES"
    INVALID_TIMESTAMP = "INVALID_TIMESTAMP"
    ANALYSIS_FAILED = "ANALYSIS_FAILED"
    DATABASE_ERROR = "DATABASE_ERROR"
    REPORT_NOT_FOUND = "REPORT_NOT_FOUND"


class AppException(Exception):
    def __init__(self, error_code: ErrorCode, message: str, status_code: int = 400):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class SpillNotFoundError(AppException):
    def __init__(self, spill_id: str):
        super().__init__(
            ErrorCode.SPILL_NOT_FOUND,
            f"Spill with id '{spill_id}' not found",
            status_code=404,
        )


class VesselNotFoundError(AppException):
    def __init__(self, vessel_id: str):
        super().__init__(
            ErrorCode.VESSEL_NOT_FOUND,
            f"Vessel with id '{vessel_id}' not found",
            status_code=404,
        )


class ServiceUnavailableError(AppException):
    def __init__(self, service: str, error_code: ErrorCode):
        super().__init__(
            error_code,
            f"{service} service is currently unavailable",
            status_code=503,
        )


class InvalidGeometryError(AppException):
    def __init__(self, detail: str = "Invalid geometry provided"):
        super().__init__(ErrorCode.INVALID_GEOMETRY, detail, status_code=422)


class InvalidCoordinatesError(AppException):
    def __init__(self, detail: str = "Invalid coordinates provided"):
        super().__init__(ErrorCode.INVALID_COORDINATES, detail, status_code=422)


class InvalidTimestampError(AppException):
    def __init__(self, detail: str = "Invalid timestamp provided"):
        super().__init__(ErrorCode.INVALID_TIMESTAMP, detail, status_code=422)


class AnalysisFailedError(AppException):
    def __init__(self, detail: str = "Analysis pipeline failed"):
        super().__init__(ErrorCode.ANALYSIS_FAILED, detail, status_code=500)


class ReportNotFoundError(AppException):
    def __init__(self, spill_id: str):
        super().__init__(
            ErrorCode.REPORT_NOT_FOUND,
            f"Report for spill '{spill_id}' not found",
            status_code=404,
        )
