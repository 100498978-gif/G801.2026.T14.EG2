import unittest
from uc3m_consulting.enterprise_manager import EnterpriseManager, EnterpriseManagementException


class TestRegisterProject(unittest.TestCase):

    def test_tc_00_register_project_success(self):
        """Prueba de éxito: Todos los datos son válidos."""
        manager = EnterpriseManager()
        # Llamamos a la función con datos válidos
        result = manager.register_project("A12345678", "PROY1", "Nombre de operacion", "HR", "01/01/2026", 60000.00)

        # Como la función solo tiene un 'pass', devolverá None y este assert provocará el FALLO que pide el TDD
        self.assertIsNotNone(result)

    def test_tc_01_cif_not_a_string(self):
        """TC-01: company_cif no es una cadena (ej. entero) -> ECNV1"""
        manager = EnterpriseManager()

        # Verificamos que lance la excepción si le pasamos un número (123456789) en vez de un string
        with self.assertRaises(EnterpriseManagementException):
            manager.register_project(123456789, "PROY1", "Nombre de operacion", "HR", "01/01/2026", 60000.00)