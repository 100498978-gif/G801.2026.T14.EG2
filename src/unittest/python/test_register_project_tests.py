"""Tests for register_project in EnterpriseManager."""

import json
import os
import shutil
import tempfile
import unittest
from decimal import Decimal

from uc3m_consulting import EnterpriseManager, EnterpriseManagementException


class TestEnterpriseManager(unittest.TestCase):
    """Functional tests for project registration."""

    # 1. EL SETUPCLASS VA AQUÍ (Se ejecuta una vez al principio)
    @classmethod
    def setUpClass(cls):
        """Load shared test data and prepare an isolated JSON store."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_json = os.path.join(
            base_dir,
            "../../main/python/uc3m_consulting/data/f1_test_data.json"
        )
        ruta_json_limpia = os.path.normpath(ruta_json)
        cls.__temp_dir = tempfile.mkdtemp()
        cls.__projects_store_path = os.path.join(
            cls.__temp_dir,
            "corporate_operations.json"
        )

        try:
            with open(ruta_json_limpia, encoding="utf-8", mode="r") as json_file:
                cls.__f1_test_data = json.load(json_file, parse_float=Decimal)
        except FileNotFoundError as exc:
            raise RuntimeError(
                f"No se encuentra el archivo JSON en: {ruta_json_limpia}"
            ) from exc
        except json.JSONDecodeError:
            cls.__f1_test_data = []

    @classmethod
    def tearDownClass(cls):
        """Delete temporary resources created for the test suite."""
        shutil.rmtree(cls.__temp_dir, ignore_errors=True)


    def setUp(self):
        """Start each test with an empty project store."""
        if os.path.exists(self.__projects_store_path):
            os.remove(self.__projects_store_path)

    # 2. UN ÚNICO MÉTODO PARA TODOS LOS CASOS VÁLIDOS (OK)
    def test_casos_validos_ok(self):
        """Verify that every valid input returns and stores one MD5 project id."""
        # 1. SOLO TC1 y TC2 son válidos. TC33 queda fuera.
        casos_validos = ["TC1", "TC2"]

        # 2. Limpiamos el JSON UNA SOLA VEZ antes de empezar el bucle
        if os.path.exists(self.__projects_store_path):
            os.remove(self.__projects_store_path)

        for input_data in self.__f1_test_data:
            if input_data["idTest"] in casos_validos:
                with self.subTest(i=input_data["idTest"]):
                    en_manager = EnterpriseManager(
                        projects_store_path=self.__projects_store_path
                    )
                    presupuesto = Decimal(str(input_data["budget"]))

                    # Guardamos el proyecto
                    result = en_manager.register_project(
                        input_data["companyCIF"],
                        input_data["projectAcronym"],
                        input_data["operationName"],
                        input_data["department"],
                        input_data["date"],
                        presupuesto
                    )

                    self.assertEqual(len(result), 32)
                    self.assertRegex(result.lower(), r"^[a-f0-9]{32}$")

        # 3. AL TERMINAR EL BUCLE, COMPROBAMOS QUE HAY EXACTAMENTE 2 GUARDADOS
        with open(self.__projects_store_path, encoding="utf-8", mode="r") as json_file:
            stored_projects = json.load(json_file)

        self.assertEqual(len(stored_projects), 2, "Deberían haberse guardado TC1 y TC2.")

    # 3. UN ÚNICO MÉTODO PARA TODOS LOS CASOS INVÁLIDOS (KO)
    def test_casos_invalidos_ko(self):
        """Verify that every invalid input raises EnterpriseManagementException and is NOT saved."""
        # Estos casos ya los hemos probado en los tests OK y en el de duplicados
        casos_excluidos = ["TC1", "TC2", "TC33"]

        for input_data in self.__f1_test_data:
            if input_data["idTest"] not in casos_excluidos:
                with self.subTest(i=input_data["idTest"]):

                    # 1. Empezamos con el JSON borrado para asegurarnos de que no hay basura
                    if os.path.exists(self.__projects_store_path):
                        os.remove(self.__projects_store_path)

                    en_manager = EnterpriseManager(
                        projects_store_path=self.__projects_store_path
                    )

                    # 2. Manejo de datos maliciosos
                    # Intentamos pasarlo a Decimal. Si falla (porque el test KO tiene letras
                    # u otro tipo de dato en el budget), lo dejamos como está para que el manager salte.
                    try:
                        presupuesto = Decimal(str(input_data["budget"]))
                    except Exception:
                        presupuesto = input_data["budget"]

                    # 3. Comprobamos que salta EXACTAMENTE tu excepción personalizada
                    with self.assertRaises(EnterpriseManagementException):
                        en_manager.register_project(
                            input_data["companyCIF"],
                            input_data["projectAcronym"],
                            input_data["operationName"],
                            input_data["department"],
                            input_data["date"],
                            presupuesto
                        )

                    # 4. COMPROBAMOS QUE NO SE HA GUARDADO NADA
                    # Si el archivo se creó de todos modos, nos aseguramos de que esté vacío
                    if os.path.exists(self.__projects_store_path):
                        with open(self.__projects_store_path, encoding="utf-8", mode="r") as json_file:
                            try:
                                stored_projects = json.load(json_file)
                                self.assertEqual(
                                    len(stored_projects),
                                    0,
                                    f"¡Error! El test {input_data['idTest']} era inválido pero se guardó en el JSON."
                                )
                            except json.JSONDecodeError:
                                # Si el archivo existe pero está totalmente vacío (no es un JSON válido),
                                # también significa que no se ha guardado el proyecto, así que está bien.
                                pass

    def test_proyecto_duplicado_ko(self):
        """Verify that TC33 is rejected because it is a duplicate of TC1."""
        # Limpiamos el entorno para este test
        if os.path.exists(self.__projects_store_path):
            os.remove(self.__projects_store_path)

        en_manager = EnterpriseManager(projects_store_path=self.__projects_store_path)

        # 1. Buscamos los datos exactos de TC1 y TC33 en el JSON
        tc1_data = next(item for item in self.__f1_test_data if item["idTest"] == "TC1")
        tc33_data = next(item for item in self.__f1_test_data if item["idTest"] == "TC33")

        # 2. Guardamos TC1 (Esto TIENE que funcionar porque el archivo está vacío)
        en_manager.register_project(
            tc1_data["companyCIF"],
            tc1_data["projectAcronym"],
            tc1_data["operationName"],
            tc1_data["department"],
            tc1_data["date"],
            Decimal(str(tc1_data["budget"]))
        )

        # 3. Intentamos guardar TC33. Aquí le decimos a Python:
        # "Espero que esto lance un EnterpriseManagementException"
        with self.assertRaises(EnterpriseManagementException) as context:
            en_manager.register_project(
                tc33_data["companyCIF"],
                tc33_data["projectAcronym"],
                tc33_data["operationName"],
                tc33_data["department"],
                tc33_data["date"],
                Decimal(str(tc33_data["budget"]))
            )

        # Opcional: Podemos comprobar que el mensaje de error es exactamente el de duplicado
        self.assertEqual(str(context.exception), "Proyecto duplicado")

        with open(self.__projects_store_path, encoding="utf-8", mode="r") as json_file:
            stored_projects = json.load(json_file)

        # COMPRUEBA QUE SOLO HAY 1 (EL TC1), EL TC33 FUE RECHAZADO:
        self.assertEqual(len(stored_projects), 1, "Solo debería estar guardado el TC1.")


if __name__ == '__main__':
    unittest.main()
