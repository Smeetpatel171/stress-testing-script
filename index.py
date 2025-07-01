import json
from locust import HttpUser, task, between
from random import choice
import uuid

class QuickieUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        with open('user_ids.json') as f:
            self.user_ids = json.load(f)
        self.index = 0

    def get_user_id(self):
        user_id = self.user_ids[self.index]
        self.index = (self.index + 1) % len(self.user_ids)
        return user_id

    def send_request(self, payload, name):
        headers = {"Content-Type": "application/json"}
        with self.client.post(
            "/api/quickie/user/coin-queue/pre-purchase",
            json=payload,
            headers=headers,
            name=name,
            catch_response=True  # Allows you to manually mark success/failure
        ) as response:
            if response.status_code != 201:
                response.failure(f"Error: {response.status_code} - {response.text}")
                raise Exception(f"Test failed for '{name}' with status {response.status_code}: {response.text}")
            else:
                response.success()


    @task
    def happy_path(self):
        payload = {
            "set_number": 1,
            "package_number": 1,
            "requested_coins": 27000,
           "client_wallet_address": "0x89f04ad6e8002df05ade8c86625bd6b21c4ccf7b",
            "user_wallet_address": "0x69177201691d284cb6828a36b38f82fee5ce064e",
            "chain_type": "base",
            "crypto_currency": "USDT",
            "amount": 1,
            "user_id": self.get_user_id()
        }
        self.send_request(payload, "actual API call")

    @task
    def limit_exceeded(self):
        payload = {
            "set_number": 1,
            "package_number": 1,
            "requested_coins": 1000000,  # Unrealistically high
           "client_wallet_address": "0x89f04ad6e8002df05ade8c86625bd6b21c4ccf7b",
            "client_wallet_address": "0x69177201691d284cb6828a36b38f82fee5ce064e",
            "chain_type": "base",
            "crypto_currency": "USDT",
            "amount": 999999,
            "user_id": self.get_user_id()
        }
        self.send_request(payload, "LimitExceeded")

    @task
    def stage_not_found(self):
        payload = {
            "set_number": 999,
            "package_number": 999,
            "requested_coins": 1,
           "client_wallet_address": "0x89f04ad6e8002df05ade8c86625bd6b21c4ccf7b",
            "client_wallet_address": "0x69177201691d284cb6828a36b38f82fee5ce064e",
            "chain_type": "base",
            "crypto_currency": "USDT",
            "amount": 0.01,
            "user_id": self.get_user_id()
        }
        self.send_request(payload, "StageNotFound")

    @task
    def not_enough_tokens(self):
        payload = {
            "set_number": 1,
            "package_number": 1,
            "requested_coins": 999999,  # Simulating more than available
           "client_wallet_address": "0x89f04ad6e8002df05ade8c86625bd6b21c4ccf7b",
            "client_wallet_address": "0x69177201691d284cb6828a36b38f82fee5ce064e",
            "chain_type": "base",
            "crypto_currency": "USDT",
            "amount": 100000,
            "user_id": self.get_user_id()
        }
        self.send_request(payload, "NotEnoughTokens")

    @task
    def invalid_user_id(self):
        payload = {
            "set_number": 1,
            "package_number": 1,
            "requested_coins": 1,
           "client_wallet_address": "0x89f04ad6e8002df05ade8c86625bd6b21c4ccf7b",
            "client_wallet_address": "0x69177201691d284cb6828a36b38f82fee5ce064e",
            "chain_type": "base",
            "crypto_currency": "USDT",
            "amount": 0.01,
            "user_id": "invalid-id"
        }
        self.send_request(payload, "InvalidUserID")

    @task
    def missing_required_fields(self):
        payload = {
            "user_id": self.get_user_id()  # Missing several required fields
        }
        self.send_request(payload, "MissingRequiredFields")

    @task
    def invalid_chain_type(self):
        payload = {
            "set_number": 1,
            "package_number": 1,
            "requested_coins": 1,
           "client_wallet_address": "0x89f04ad6e8002df05ade8c86625bd6b21c4ccf7b",
            "client_wallet_address": "0x69177201691d284cb6828a36b38f82fee5ce064e",
            "chain_type": "invalid_chain",
            "crypto_currency": "USDT",
            "amount": 0.01,
            "user_id": self.get_user_id()
        }
        self.send_request(payload, "InvalidChainType")

    @task
    def invalid_crypto_currency(self):
        payload = {
            "set_number": 1,
            "package_number": 1,
            "requested_coins": 1,
           "client_wallet_address": "0x89f04ad6e8002df05ade8c86625bd6b21c4ccf7b",
            "client_wallet_address": "0x69177201691d284cb6828a36b38f82fee5ce064e",
            "chain_type": "base",
            "crypto_currency": "BTC",  # Not allowed
            "amount": 0.01,
            "user_id": self.get_user_id()
        }
        self.send_request(payload, "InvalidCryptoCurrency")

