import unittest
import json
import os
import re
import tempfile
from decimal import Decimal
from uc3m_consulting import EnterpriseManager, EnterpriseManagementException

class TestEnterpriseManager(unittest.TestCase):

    # 1. EL SETUPCLASS VA AQUÍ (Se ejecuta una vez al principio)
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_json = os.path.join(base_dir, "../../main/python/uc3m_consulting/data/f1_test_data.json")
        ruta_json_limpia = os.path.normpath(ruta_json)
        cls.__temp_dir = tempfile.TemporaryDirectory()
        cls.__projects_store_path = os.path.join(cls.__temp_dir.name, "corporate_operations.json")

        try:
            with open(ruta_json_limpia, encoding="utf-8", mode="r") as json_file:
                cls.__f1_test_data = json.load(json_file, parse_float=Decimal)
        except FileNotFoundError:
                    raise Exception(f"No se encuentra el archivo JSON en: {ruta_json_limpia}")
        except json.JSONDecodeError:
            cls.__f1_test_data = []

    @classmethod
    def tearDownClass(cls):
        cls.__temp_dir.cleanup()

    def setUp(self):
        if os.path.exists(self.__projects_store_path):
            os.remove(self.__projects_store_path)

    # 2. UN ÚNICO MÉTODO PARA TODOS LOS CASOS VÁLIDOS (OK)
    def test_casos_validos_OK(self):
        # Filtramos solo los IDs que en tu Excel son "VALID"
        casos_validos = ["TC1", "TC2", "TC33"]

        for input_data in self.__f1_test_data:
            if input_data["idTest"] in casos_validos:
                # Usamos subtest para que nos avise qué ID exacto está evaluando
                with self.subTest(i=input_data["idTest"]):
                    if os.path.exists(self.__projects_store_path):
                        os.remove(self.__projects_store_path)

                    en_manager = EnterpriseManager(projects_store_path=self.__projects_store_path)
                    result = en_manager.register_project(input_data["companyCIF"], input_data["projectAcronym"], input_data["operationName"], input_data["department"], input_data["date"], input_data["budget"])
                    self.assertEqual(len(result), 32)
                    patron_md5 = r"^[a-f0-9]{32}$"
                    self.assertRegex(result.lower(), patron_md5)

                    with open(self.__projects_store_path, encoding="utf-8", mode="r") as json_file:
                        stored_projects = json.load(json_file)

                    self.assertEqual(len(stored_projects), 1)
                    self.assertEqual(stored_projects[0]["company_cif"], input_data["companyCIF"])

    # 3. UN ÚNICO MÉTODO PARA TODOS LOS CASOS INVÁLIDOS (KO)
    def test_casos_invalidos_KO(self):
        casos_validos = ["TC1", "TC2", "TC33"]

        for input_data in self.__f1_test_data:
            if input_data["idTest"] not in casos_validos:
                with self.subTest(i=input_data["idTest"]):
                    # Le decimos al test que ESPERAMOS que salte tu excepción
                    with self.assertRaises(EnterpriseManagementException):
                        en_manager = EnterpriseManager(projects_store_path=self.__projects_store_path)
                        en_manager.register_project(
                            input_data["companyCIF"],
                            input_data["projectAcronym"],
                            input_data["operationName"],
                            input_data["department"],
                            input_data["date"],
                            input_data["budget"]
                        )

    def test_proyecto_duplicado_KO(self):
        duplicate_case = next(item for item in self.__f1_test_data if item["idTest"] == "TC33")
        en_manager = EnterpriseManager(projects_store_path=self.__projects_store_path)

        en_manager.register_project(
            duplicate_case["companyCIF"],
            duplicate_case["projectAcronym"],
            duplicate_case["operationName"],
            duplicate_case["department"],
            duplicate_case["date"],
            duplicate_case["budget"]
        )

        with self.assertRaises(EnterpriseManagementException):
            en_manager.register_project(
                duplicate_case["companyCIF"],
                duplicate_case["projectAcronym"],
                duplicate_case["operationName"],
                duplicate_case["department"],
                duplicate_case["date"],
                duplicate_case["budget"]
            )

if __name__ == '__main__':
    unittest.main()
