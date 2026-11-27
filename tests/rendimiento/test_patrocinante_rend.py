from locust import HttpUser, task, between


class UsuarioPatrocinador(HttpUser):
    wait_time = between(1, 2)

    @task(3)
    def ver_patrocinadores(self):
        self.client.get("/patrocinador/")

    @task(2)
    def consultar_patrocinadores(self):
        with self.client.post(
            "/patrocinador/",
            data={"consultar": "1"},
            name="POST /patrocinador/ [consultar]",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 400):
                resp.success()
            else:
                resp.failure(f"Status inesperado: {resp.status_code}")


# locust -f tests/rendimiento/test_patrocinante_rend.py --host=http://127.0.0.1:5001