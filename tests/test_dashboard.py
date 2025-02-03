from os import getenv
from vcr_unittest import VCRTestCase
from canonicalwebteam.store_api.dashboard import Dashboard

test_session = getenv("PUBLISHER_MACAROON", "test_session")


class DashboardTest(VCRTestCase):
    def _get_vcr_kwargs(self):
        """
        This removes the authorization header
        from VCR so we don't record auth parameters
        """
        return {"filter_headers": ["Authorization", "Macaroons"]}

    def setUp(self):
        self.client = Dashboard()
        return super().setUp()

    def test_get_macaroon(self):
        macaroon = self.client.get_macaroon(["package_access"])
        self.assertIsInstance(macaroon, str)

    def test_get_account(self):
        account = self.client.get_account(test_session)
        self.assertIsInstance(account, dict)
        self.assertEqual(account["username"], "codeempress")
        self.assertIn("snaps", account)

    def test_get_agreement(self):
        agreement = self.client.get_agreement(test_session)
        self.assertIsInstance(agreement, dict)

    def test_post_agreement(self):
        agreement = self.client.post_agreement(test_session, True)
        self.assertIsInstance(agreement, dict)

    def test_post_username(self):
        username = self.client.post_username(test_session, "the-user")
        self.assertIsInstance(username, dict)

    def test_post_register_name_dispute(self):
        response = self.client.post_register_name_dispute(
            test_session, "test-snap", "testing a dispute"
        )
        self.assertIsInstance(response, dict)
        self.assertEqual(response["snap_name"], "test-snap")

    def test_get_snap_info(self):
        snap_info = self.client.get_snap_info(test_session, "steve-test-snap")
        self.assertIsInstance(snap_info, dict)

    def test_get_package_upload_macaroon(self):
        macaroon = self.client.get_package_upload_macaroon(
            test_session, "test-snap", ["testing"]
        )
        self.assertIn("macaroon", macaroon)
        self.assertIsInstance(macaroon["macaroon"], str)

    def test_get_snap_id(self):
        snap_id = self.client.get_snap_id(test_session, "steve-test-snap")
        self.assertIsInstance(snap_id, str)

    def test_get_snap_revision(self):
        revision = self.client.get_snap_revision(
            test_session, "steve-test-snap", 22
        )
        self.assertIsInstance(revision, dict)
        self.assertIn("revision", revision)

    def test_snap_release_history(self):
        release_history = self.client.snap_release_history(
            test_session, "steve-test-snap"
        )
        self.assertIsInstance(release_history, dict)
        self.assertNotEqual(len(release_history), 0)
        self.assertIn("releases", release_history)

    def test_snap_channel_map(self):
        channel_map = self.client.snap_channel_map(
            test_session, "steve-test-snap"
        )
        self.assertIsInstance(channel_map, dict)
        self.assertNotEqual(len(channel_map), 0)
        self.assertIn("channel-map", channel_map)
        self.assertIsInstance(channel_map["channel-map"], list)

    def test_post_snap_release(self):
        release = self.client.post_snap_release(
            test_session,
            {"channels": ["edge"], "name": "steve-test-snap", "revision": 22},
        )
        self.assertIsInstance(release, dict)

    def test_post_close_channel(self):
        close_channel = self.client.post_close_channel(
            test_session,
            "bv9Q2i9CNAvTjt9wTx1cFC6SAT9YrEfG",
            {"channels": ["edge"]},
        )
        self.assertIsInstance(close_channel, dict)
        self.assertIn("channel_map_tree", close_channel)

    def test_get_validation_sets(self):
        validation_sets = self.client.get_validation_sets(test_session)
        self.assertIsInstance(validation_sets, dict)
        # self.assertIn("assertions", validation_sets)

    def test_get_stores(self):
        stores = self.client.get_stores(test_session)
        self.assertIsInstance(stores, list)
        self.assertNotEqual(len(stores), 0)

    def test_get_store(self):
        store = self.client.get_store(test_session, "testGahNg0wohVae8aY4")
        self.assertIsInstance(store, dict)
        self.assertIn("name", store)

    def test_get_store_snaps(self):
        snaps = self.client.get_store_snaps(
            test_session, "testGahNg0wohVae8aY4"
        )
        self.assertIsInstance(snaps, list)

    def test_get_store_members(self):
        members = self.client.get_store_members(
            test_session, "testGahNg0wohVae8aY4"
        )
        self.assertIsInstance(members, list)
        self.assertNotEqual(len(members), 0)

    def test_get_store_invites(self):
        invite = self.client.get_store_invites(
            test_session, "testGahNg0wohVae8aY4"
        )
        self.assertIsInstance(invite, list)
