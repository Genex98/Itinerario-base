from locust import HttpUser, task, between


class UsuarioContrato(HttpUser):
    wait_time = between(1, 2)
    
    @task(3)
    def ver_contratos(self):
        self.client.get("/contratos/")

    @task(2)
    def consultar_contratos(self):
        with self.client.post(
            "/contratos/",
            data={"consultar": "1"},
            name="POST /contratos/ [consultar]",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 400):
                resp.success()
            else:
                resp.failure(f"Status inesperado: {resp.status_code}")


#locust -f tests/rendimiento/test_contrato_rend.py --host=http://127.0.0.1:5001
