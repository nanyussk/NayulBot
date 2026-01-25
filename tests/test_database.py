import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from src.database.user_db import UsersDB
from src.database.skin_db import SkinsDB
from src.database.models.user import UserData
from src.database.models.skin import ProfileSkin


class FakeCursor:
    def __init__(self, data):
        self._data = list(data)
        self._skip = 0
        self._limit = None

    def skip(self, value):
        self._skip = value
        return self

    def limit(self, value):
        self._limit = value
        return self

    async def to_list(self, length=None):
        data = self._data[self._skip :]
        if self._limit is not None:
            data = data[: self._limit]
        return data


class FakeCollection:
    def __init__(self, data):
        self._data = list(data)

    def find(self, query=None):
        data = self._data
        if query and query.get("banStatus") == {"$ne": None}:
            data = [item for item in data if item.get("banStatus") is not None]
        return FakeCursor(data)


class UsersDBTests(unittest.IsolatedAsyncioTestCase):
    async def test_get_all_users_paginates(self):
        data = [{"_id": 1}, {"_id": 2}, {"_id": 3}]
        db = UsersDB.__new__(UsersDB)
        db.collection = FakeCollection(data)

        results = []
        async for page in db.get_all_users(size=2):
            results.extend(page)

        self.assertEqual([user.id for user in results], [1, 2, 3])

    async def test_get_all_users_banned(self):
        data = [
            {"_id": 1, "banStatus": None},
            {"_id": 2, "banStatus": {"bannedBy": 1, "bannedAt": "2024-01-01T00:00:00", "reason": ""}},
        ]
        db = UsersDB.__new__(UsersDB)
        db.collection = FakeCollection(data)

        results = []
        async for page in db.get_all_users_banned(size=10):
            results.extend(page)

        self.assertEqual([user.id for user in results], [2])

    async def test_update_married_sets_fields(self):
        db = UsersDB.__new__(UsersDB)
        db.get_user = AsyncMock(side_effect=[UserData(id=1), UserData(id=2), UserData(id=1), UserData(id=2)])
        db.update_user = AsyncMock()

        user = SimpleNamespace(id=1)
        partner = SimpleNamespace(id=2)
        await db.update_married(user, partner, married=True, division_of_assets=True)

        self.assertGreaterEqual(db.update_user.call_count, 2)
        updates = [call.kwargs["query"]["$set"] for call in db.update_user.call_args_list]

        self.assertTrue(any(u["marriedStatus"]["marriedWith"] == 2 for u in updates))
        self.assertTrue(any(u["marriedStatus"]["marriedWith"] == 1 for u in updates))

    async def test_update_married_clears_fields(self):
        db = UsersDB.__new__(UsersDB)
        db.get_user = AsyncMock(side_effect=[UserData(id=1), UserData(id=2)])
        db.update_user = AsyncMock()

        user = SimpleNamespace(id=1)
        partner = SimpleNamespace(id=2)
        await db.update_married(user, partner, married=False)

        calls = db.update_user.call_args_list
        updates = [call.kwargs["query"]["$set"] for call in calls]
        self.assertTrue(all(u["marriedStatus"]["marriedWith"] is None for u in updates))
        self.assertTrue(all(u["marriedStatus"]["since"] is None for u in updates))


class SkinsDBTests(unittest.IsolatedAsyncioTestCase):
    async def test_get_all_skins(self):
        data = [
            {"_id": "basic", "name": "Basica", "price": 0, "rarity": 0, "url": "https://x.test/a.png"},
            {"_id": "rare", "name": "Rara", "price": 10, "rarity": 2, "url": "https://x.test/b.png"},
        ]
        db = SkinsDB.__new__(SkinsDB)
        db.collection = FakeCollection(data)

        skins = await db.get_all_skins()

        self.assertEqual([skin.id for skin in skins], ["basic", "rare"])
        self.assertTrue(all(isinstance(skin, ProfileSkin) for skin in skins))


if __name__ == "__main__":
    unittest.main()
