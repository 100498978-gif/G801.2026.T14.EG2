"""Module """
from .enterprise_management_exception import EnterpriseManagementException
from .enterprise_project import EnterpriseProject
from validarnif import validar_cif

class EnterpriseManager:
    """Class for providing the methods for managing the orders"""
    def __init__(self):
        pass

    @staticmethod
    def validate_cif(cif: str):
        return validar_cif(cif)

    def register_project(self, company_cif: str, project_achronym: str, operation_name: str, department: str, date: str,
                         budget: float):

        #1. Comprobación de los tipos de dato
        if type(company_cif) is not str:
            raise EnterpriseManagementException("El CIF de la compañía debe ser una cadena de texto")

        if type(project_achronym) is not str:
            raise EnterpriseManagementException("El acrónimo del proyecto debe ser una cadena de texto")

        if type(operation_name) is not str:
            raise EnterpriseManagementException("El nombre de la operación debe ser una cadena de texto")

        if type(department) is not str:
            raise EnterpriseManagementException("El departamento debe ser una cadena de texto")

        if type(date) is not str:
            raise EnterpriseManagementException("La fecha debe ser una cadena de texto")

        if type(budget) not in (float, int):
            raise EnterpriseManagementException("El presupuesto debe ser un valor numérico decimal")

        #2.Validación del CIF(incluye todos los formatos inválidos ya que es na función auxiliar)

        if not self.validate_cif(company_cif):
            raise EnterpriseManagementException("El CIF proporcionado no es válido")



        nuevo_proyecto = EnterpriseProject(
            company_cif=company_cif,
            project_acronym=project_achronym,
            project_description=operation_name,
            department=department,
            starting_date=date,
            project_budget=budget
        )

        # 3. DEVOLVEMOS EL MD5
        return nuevo_proyecto.project_id