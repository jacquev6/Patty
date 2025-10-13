import datetime

import fastapi
import fastapi.testclient

from .. import database_utils
from .. import extraction
from .. import file_storage
from ..api_utils import ApiModel


router = fastapi.APIRouter()


class CreatePdfFileRequest(ApiModel):
    creator: str
    file_name: str
    bytes_count: int
    pages_count: int
    sha256: str


class CreatePdfFileResponse(ApiModel):
    upload_url: str | None


@router.post("/pdf-files")
def create_pdf_file(req: CreatePdfFileRequest, session: database_utils.SessionDependable) -> CreatePdfFileResponse:
    now = datetime.datetime.now(datetime.timezone.utc)
    pdf_file = session.get(extraction.PdfFile, req.sha256)
    if pdf_file is None:
        pdf_file = extraction.PdfFile(
            sha256=req.sha256,
            created_by=req.creator,
            created_at=now,
            bytes_count=req.bytes_count,
            pages_count=req.pages_count,
            known_file_names=[],
        )
        session.add(pdf_file)

    if req.file_name not in pdf_file.known_file_names:
        pdf_file.known_file_names = pdf_file.known_file_names + [req.file_name]

    if file_storage.pdf_files.has(pdf_file.sha256):
        upload_url = None
    else:
        upload_url = file_storage.pdf_files.get_put_url(pdf_file.sha256)

    return CreatePdfFileResponse(upload_url=upload_url)


class ApiTestCase(database_utils.TestCaseWithDatabase):
    def setUp(self) -> None:
        from .. import authentication
        from ..file_storage import file_system_engine

        super().setUp()
        self.app = fastapi.FastAPI(database_engine=self.engine)
        self.app.include_router(router)
        self.app.include_router(file_system_engine.router)
        access_token = authentication.login(authentication.PostTokenRequest(password="password")).access_token
        self.client = fastapi.testclient.TestClient(self.app, headers={"Authorization": f"Bearer {access_token}"})

    def test_create_the_same_pdf_file_several_times(self) -> None:
        sha = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

        file_storage.pdf_files.delete(sha)

        r = self.client.post(
            "/pdf-files",
            json={"creator": "UnitTest", "fileName": "foo.pdf", "bytesCount": 0, "pagesCount": 0, "sha256": sha},
        )
        self.assertEqual(r.status_code, 200, r.text)
        self.assertIsNotNone(r.json()["uploadUrl"])
        self.assertEqual(self.get_model(extraction.PdfFile, sha).known_file_names, ["foo.pdf"])

        r = self.client.post(
            "/pdf-files",
            json={"creator": "UnitTest", "fileName": "bar.pdf", "bytesCount": 0, "pagesCount": 0, "sha256": sha},
        )
        self.assertEqual(r.status_code, 200, r.text)
        upload_url = r.json()["uploadUrl"]
        self.assertIsNotNone(upload_url)
        self.client.put(upload_url, content=b"")
        self.assertTrue(file_storage.pdf_files.has(sha))
        self.assertEqual(self.get_model(extraction.PdfFile, sha).known_file_names, ["foo.pdf", "bar.pdf"])

        r = self.client.post(
            "/pdf-files",
            json={"creator": "UnitTest", "fileName": "foo.pdf", "bytesCount": 0, "pagesCount": 0, "sha256": sha},
        )
        self.assertEqual(r.status_code, 200, r.text)
        self.assertIsNone(r.json()["uploadUrl"])
        self.assertEqual(self.get_model(extraction.PdfFile, sha).known_file_names, ["foo.pdf", "bar.pdf"])
