"""Module """
from .enterprise_management_exception import EnterpriseManagementException
from .enterprise_project import EnterpriseProject
from validarnif import validar_cif
from datetime import datetime
from decimal import Decimal

class EnterpriseManager:
    """Class for providing the methods for managing the orders"""
    def __init__(self):
        pass

    @staticmethod
    def validate_cif(cif: str):
        return validar_cif(cif)

    def register_project(self, company_cif: str, project_achronym: str, operation_name: str, department: str, date: str,
                         budget: float):

        # 1. Validación CIF (TC3, TC4, TC5, TC6, TC7)
        if type(company_cif) != str:
            raise EnterpriseManagementException("CIF debe ser una cadena")
        if not self.validate_cif(company_cif):
            raise EnterpriseManagementException("CIF inválido")

        # 2. Validación Acrónimo (TC8, TC9, TC10, TC11, TC12, TC13)
        if type(project_achronym) != str:
            raise EnterpriseManagementException("Achronym debe ser una cadena")
        if len(project_achronym) < 5 or len(project_achronym) > 10:
            raise EnterpriseManagementException("Invalid achronym length")
        if not project_achronym.isupper():
            raise EnterpriseManagementException("achronym inválido (debe ser mayúsculas)")
        if not project_achronym.isalnum() or " " in project_achronym:
            raise EnterpriseManagementException("achronym inválido")

        # 3. Validación Nombre Operación (TC14, TC15, TC16)
        if type(operation_name) != str:
            raise EnterpriseManagementException("Operation debe ser una cadena")
        if len(operation_name) < 10 or len(operation_name) > 30:
            raise EnterpriseManagementException("Longuitud de operation inválida")

        # 4. Validación Departamento (TC17, TC18)
        allowed_depts = ["HR", "LOGISTICS", "MARKETING", "SALES"]  # Basado en tus TCs
        if type(department) != str:
            raise EnterpriseManagementException("Department debe ser una cadena")
        if department not in allowed_depts:
            raise EnterpriseManagementException("Department inválido")

        # 5. Validación Fecha (TC19 a TC27)
        if type(date) != str:
            raise EnterpriseManagementException("Date debe ser una cadena")

        # Formato y rangos (TC20, TC21, TC22, TC23, TC24, TC25, TC26)
        try:
            fecha_dt = datetime.strptime(date, "%d/%m/%Y")
            if not (2025 <= fecha_dt.year <= 2028):
                raise EnterpriseManagementException("año fuera del rango")
            # TC27: Fecha anterior a hoy (Simulando 2026 como 'hoy' según enunciado)
            if fecha_dt < datetime.now():
                raise EnterpriseManagementException("No puede ser un día en el pasado")
        except ValueError:
            raise EnterpriseManagementException("Formato invalido")

        # 6. Validación Presupuesto (TC28 a TC32)
        if not isinstance(budget, (int, float, Decimal)):
            raise EnterpriseManagementException("Tiene que ser un numero")

        if isinstance(budget, Decimal):
            if budget.as_tuple().exponent != -2:
                raise EnterpriseManagementException("Budget necesita dos decimales")
        else:
            # Por si acaso llegara un entero o un float normal
            raise EnterpriseManagementException("Budget necesita dos decimales")

        # Rangos (TC29, TC30)
        if budget < 50000.00 or budget > 1000000.00:
            raise EnterpriseManagementException("Budget fuera de rango")

        # asi no lo vamos a hacer, lo vamos a hacer con jsons
        nuevo_proyecto = EnterpriseProject(
            company_cif=company_cif,
            project_acronym=project_achronym,
            project_description=operation_name,
            department=department,
            starting_date=date,
            project_budget=budget
        )

        if nuevo_proyecto.project_id in self.__projects_list:
            raise EnterpriseManagementException("Proyecto duplicado")

        self.__projects_list.append(nuevo_proyecto.project_id)

        # 3. DEVOLVEMOS EL MD5
        return nuevo_proyecto.project_id