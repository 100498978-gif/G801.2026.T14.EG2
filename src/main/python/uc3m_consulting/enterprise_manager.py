"""Enterprise manager module."""
import json
import os
import re
from datetime import datetime
from decimal import Decimal

from validarnif import validar_cif

from .enterprise_management_exception import EnterpriseManagementException
from .enterprise_project import EnterpriseProject

class EnterpriseManager:
    """Class for providing the methods for managing the orders"""
    def __init__(self, projects_store_path=None):
        """Create the manager and configure the projects persistence path."""
        default_store = os.path.join(
            os.path.dirname(__file__),
            "data",
            "corporate_operations.json"
        )
        self.__projects_store_path = projects_store_path or default_store

    @staticmethod
    def validate_cif(cif: str):
        """Validate a Spanish CIF."""
        return validar_cif(cif)

    def __load_projects(self):
        """Load stored projects from the JSON persistence file."""
        if not os.path.exists(self.__projects_store_path):
            return []

        try:
            with open(self.__projects_store_path, encoding="utf-8", mode="r") as json_file:
                stored_projects = json.load(json_file)
        except (OSError, json.JSONDecodeError) as exc:
            raise EnterpriseManagementException("Error al cargar proyectos") from exc

        if not isinstance(stored_projects, list):
            raise EnterpriseManagementException("Formato de almacenamiento invalido")
        return stored_projects

    def __save_projects(self, stored_projects):
        """Persist the projects list in JSON format."""
        parent_dir = os.path.dirname(self.__projects_store_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        try:
            with open(self.__projects_store_path, encoding="utf-8", mode="w") as json_file:
                json.dump(stored_projects, json_file, indent=2)
        except OSError as exc:
            raise EnterpriseManagementException("Error al guardar proyectos") from exc

    def register_project(
            self,
            company_cif: str,
            project_achronym: str,
            operation_name: str,
            department: str,
            date: str,
            budget: float):
        """Register a project, persist it and return its md5 project id."""

        if not isinstance(company_cif, str):
            raise EnterpriseManagementException("CIF debe ser una cadena")
        if not self.validate_cif(company_cif):
            raise EnterpriseManagementException("CIF inválido")

        if not isinstance(project_achronym, str):
            raise EnterpriseManagementException("Achronym debe ser una cadena")
        if not re.fullmatch(r"[A-Z0-9]{5,10}", project_achronym):
            raise EnterpriseManagementException("Invalid achronym length")

        if not isinstance(operation_name, str):
            raise EnterpriseManagementException("Operation debe ser una cadena")
        if len(operation_name) < 10 or len(operation_name) > 30:
            raise EnterpriseManagementException("Longuitud de operation inválida")

        allowed_depts = ["HR", "FINANCE", "LEGAL", "LOGISTICS"]
        if not isinstance(department, str):
            raise EnterpriseManagementException("Department debe ser una cadena")
        if department not in allowed_depts:
            raise EnterpriseManagementException("Department inválido")

        if not isinstance(date, str):
            raise EnterpriseManagementException("Date debe ser una cadena")

        try:
            fecha_dt = datetime.strptime(date, "%d/%m/%Y").date()
            if fecha_dt.year < 2025 or fecha_dt.year >= 2028:
                raise EnterpriseManagementException("año fuera del rango")
            if fecha_dt < datetime.now().date():
                raise EnterpriseManagementException("No puede ser un día en el pasado")
        except ValueError as exc:
            raise EnterpriseManagementException("Formato invalido") from exc

        if not isinstance(budget, Decimal):
            raise EnterpriseManagementException("Tiene que ser un numero")
        if budget.as_tuple().exponent != -2:
            raise EnterpriseManagementException("Budget necesita dos decimales")
        if budget < Decimal("50000.00") or budget > Decimal("1000000.00"):
            raise EnterpriseManagementException("Budget fuera de rango")

        stored_projects = self.__load_projects()
        for stored_project in stored_projects:
            if (
                    stored_project.get("company_cif") == company_cif
                    and stored_project.get("project_description") == operation_name):
                raise EnterpriseManagementException("Proyecto duplicado")

        nuevo_proyecto = EnterpriseProject(
            company_cif=company_cif,
            project_acronym=project_achronym,
            project_description=operation_name,
            department=department,
            starting_date=date,
            project_budget=budget
        )

        stored_projects.append(nuevo_proyecto.to_json())
        self.__save_projects(stored_projects)

        return nuevo_proyecto.project_id