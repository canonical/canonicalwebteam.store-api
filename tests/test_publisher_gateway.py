from os import getenv

from vcr_unittest import VCRTestCase
from canonicalwebteam.store_api.publishergw import PublisherGW
from canonicalwebteam.exceptions import (
    StoreApiResponseError,
)

test_session = getenv(
    "PUBLISHER_MACAROON",
    "test_session",
)
test_dev_auth = getenv(
    "DEVELOPER_TOKEN",
    {"developer_token": "test_dev_auth"},
)


class PublisherGWTest(VCRTestCase):
    def _get_vcr_kwargs(self):
        """
        This removes the authorization header
        from VCR so we don't record auth parameters
        """
        return {"filter_headers": ["Authorization", "Macaroons"]}

    def setUp(self):
        self.client = PublisherGW("charm")
        return super().setUp()

    def test_get_macaroon(self):
        macaroon = self.client.get_macaroon()
        self.assertIsInstance(macaroon, str)

    def test_get_account_packages_all_charms(self):
        charms = self.client.get_account_packages(
            test_session, package_type="charm"
        )
        for charm in charms:
            self.assertEqual(charm["type"], "charm")

    def test_get_package_metadata(self):
        metadata = self.client.get_package_metadata(
            test_dev_auth, package_name="marketplace-test-charm"
        )
        self.assertEqual(metadata["type"], "charm")
        self.assertEqual(metadata["name"], "marketplace-test-charm")

    def test_get_package_metadata_error(self):
        with self.assertRaises(StoreApiResponseError):
            self.client.get_package_metadata(
                test_dev_auth, package_name="marketplace-test-charm3"
            )

    def test_get_package_metadata_key_error(self):
        response = self.client.get_package_metadata(
            test_dev_auth, package_name="marketplace-test-charm4"
        )
        self.assertEqual(response["error"], "Some error")

    def test_update_package_metadata(self):
        metadata = self.client.update_package_metadata(
            test_session,
            package_type="charm",
            name="marketplace-test-charm",
            data={"description": "Updated description"},
        )
        self.assertEqual(metadata["description"], "Updated description")

    def test_register_package_name(self):
        response = self.client.register_package_name(
            test_session,
            data={
                "name": "marketplace-test-charm2",
                "type": "charm",
                "private": True,
            },
        )
        self.assertIn("id", response)

    def test_unregister_package_name(self):
        response = self.client.unregister_package_name(
            test_session, package_name="marketplace-test-charm2"
        )
        self.assertEqual(response.status_code, 200)

    def test_get_charm_libraries(self):
        response = self.client.get_charm_libraries(
            package_name="marketplace-test-charm",
        )
        self.assertIn("libraries", response)

    def test_get_releases(self):
        response = self.client.get_releases(
            test_session,
            package_name="marketplace-test-charm",
        )
        self.assertIn("channel-map", response)

    def test_get_item_details(self):
        response = self.client.get_item_details(
            name="marketplace-test-charm",
        )
        self.assertIn("name", response)

    def test_get_collaborators(self):
        response = self.client.get_collaborators(
            test_session,
            package_name="marketplace-test-charm",
        )
        self.assertIn("collaborators", response)

    def test_get_pending_invites(self):
        response = self.client.get_pending_invites(
            test_session,
            package_name="marketplace-test-charm",
        )
        self.assertIn("invites", response)

    def test_invite_collaborators(self):
        response = self.client.invite_collaborators(
            test_session,
            package_name="marketplace-test-charm",
            emails=["alimot.akinbode@test.canonical.com"],
        )
        self.assertIn("tokens", response)
        self.assertIsInstance(response["tokens"], list)

    def test_revoke_invites(self):
        response = self.client.revoke_invites(
            test_session,
            package_name="marketplace-test-charm",
            emails=["alimot.akinbode@test.canonical.com"],
        )
        self.assertEqual(response.status_code, 204)

    def test_create_store_signing_key(self):
        response = self.client.create_store_signing_key(
            test_dev_auth,
            store_id="marketplace_test_store_id",
            name="test-key",
        )
        self.assertEqual("test-key", response["name"])

    def test_get_store_models(self):
        response = self.client.get_store_models(
            test_dev_auth,
            store_id="marketplace_test_store_id",
        )
        self.assertIsInstance(response, list)

    def test_get_remodel_allowlist(self):
        response = self.client.get_remodel_allowlist(
            test_dev_auth,
            store_id="marketplace_test_store_id",
        )
        self.assertIsInstance(response, dict)

    def test_create_store_model(self):
        response = self.client.create_store_model(
            test_dev_auth,
            store_id="marketplace_test_store_id",
            name="test-model",
        )
        self.assertEqual("test-model", response["name"])

    def test_create_remodel_allowlist(self):
        response = self.client.create_remodel_allowlist(
            test_dev_auth,
            store_id="marketplace_test_store_id",
            allowlist=[
                {
                    "from-model": "test-from-model",
                    "to-model": "test-to-model",
                    "from-serial": "test-to-serial",
                    "description": "Test description",
                }
            ],
        )
        self.assertEqual("test-to-model", response["allowlist"][0]["to-model"])

    def test_get_store_model_policies(self):
        response = self.client.get_store_model_policies(
            test_dev_auth,
            store_id="marketplace_test_store_id",
            model_name="test-model",
        )
        self.assertIsInstance(response, list)

    def test_create_store_model_policy(self):
        response = self.client.create_store_model_policy(
            test_dev_auth,
            store_id="marketplace_test_store_id",
            model_name="test-model",
            signing_key="test_signing_key",
        )
        self.assertEqual("test_signing_key", response["signing-key-sha3-384"])

    def test_delete_store_model_policy(self):
        response = self.client.delete_store_model_policy(
            test_dev_auth,
            store_id="marketplace_test_store_id",
            model_name="test-model",
            rev=0,
        )
        self.assertEqual(response.status_code, 204)

    def test_get_store_signing_keys(self):
        response = self.client.get_store_signing_keys(
            test_dev_auth,
            store_id="marketplace_test_store_id",
        )
        self.assertIsInstance(response, list)

    def test_delete_store_signing_key(self):
        response = self.client.delete_store_signing_key(
            test_dev_auth,
            store_id="marketplace_test_store_id",
            signing_key_sha3_384="h1_5lws3GBr_DXSOlLquzEN7cfq49xAGG",
        )
        self.assertEqual(response.status_code, 204)

    def test_get_brand(self):
        response = self.client.get_brand(
            test_dev_auth,
            store_id="marketplace_test_store_id",
        )
        self.assertEqual("marketplace_test_store_id", response["account-id"])
