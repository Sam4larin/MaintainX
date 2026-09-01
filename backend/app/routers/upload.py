from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.schemas.upload import UploadParseResponse
from backend.app.services.upload_service import parse_uploaded_file

router = APIRouter()

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB is generous for a CSV/XLSX telemetry export


@router.post('/upload/parse', response_model=UploadParseResponse)
async def parse_upload(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail='No file was provided.')

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail='File is too large. Please upload a file under 10 MB.')
    if not content:
        raise HTTPException(status_code=400, detail='The uploaded file is empty.')

    try:
        result = parse_uploaded_file(file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=422, detail=f'Could not parse file: {exc}') from exc

    return result
