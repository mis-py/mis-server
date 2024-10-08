from core.services.base.base_service import BaseService
from modules.dummy.repositories.dummy import DummyRepository


class DummyService(BaseService):
    def __init__(self, dummy_repo: DummyRepository):
        self.dummy_repo = dummy_repo
        super().__init__(repo=dummy_repo)
