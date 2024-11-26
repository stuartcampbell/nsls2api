import locust


class ApiTest(locust.FastHttpUser):
    host = "http://127.0.0.1:8080"

    # The time a user 'waits' between requests
    wait_time = locust.between(5, 30)

    @locust.task(weight=1)
    def home_page(self):
        self.client.get("/")

    @locust.task(weight=5)
    def stats(self):
        self.client.get("/stats")

    @locust.task(weight=15)
    def recent(self):
        self.client.get("/proposals/recent/5")
