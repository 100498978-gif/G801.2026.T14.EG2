"""Module """
# from .enterprise_management_exception import EnterpriseManagementException
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
        """
        # Cadena string
        if type(company_cif) != str:
            raise EnterpriseManagementException("CIF debe ser una cadena")

        # Validación del CIF
        if not self.validate_cif(company_cif):
            raise EnterpriseManagementException("CIF inválido")

        if type(project_achronym) != str:
            raise EnterpriseManagementException("Achronym must be a string")

            # Comprobamos la longitud (entre 5 y 10)
        if len(project_achronym) < 5 or len(project_achronym) > 10:
            raise EnterpriseManagementException("Invalid achronym length")

            # Comprobamos que solo tenga letras y números (Alfanumérico)
        if not project_achronym.isalnum():
            raise EnterpriseManagementException("Invalid achronym characters")
        """
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