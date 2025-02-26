from locust import HttpUser, task, between


class CryptoCacherUser(HttpUser):
    wait_time = between(1, 2)

    @task(3)
    def get_btc_price(self):
        self.client.get("/price/BTCUSDT")

    @task(2)
    def get_eth_price(self):
        self.client.get("/price/ETHUSDT")

    @task(1)
    def get_metrics(self):
        self.client.get("/metrics/stats")
