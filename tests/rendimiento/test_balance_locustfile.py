#  python -m locust -f test/rendimiento/test_balance_locustfile.py --headless -u 20 -r 5 --run-time 15s --host http://127.0.0.1:5001

from locust import HttpUser, task, between
import random

class UsuarioBalanceRendimiento(HttpUser):
    # Simula un tiempo de espera humano entre 1 y 2 segundos
    wait_time = between(1, 5)

    @task(3)
    def ver_modulo_balance(self):
        """Prueba de carga sobre la vista principal del Balance de Pagos (RF-01)."""
        self.client.get("/balance/")

    @task(1)
    def consultar_api_balance(self):
        """Prueba de carga sobre la API o subrutas del balance."""
        id_prueba = random.randint(1, 3)
        self.client.get(f"/balance/api/contrato/{id_prueba}", name="/balance/api/contrato/[id]")

        #locust -f tests/rendimiento/test_balance_locustfile.py --host=http://127.0.0.1:5001
