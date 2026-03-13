"""Enterprise manager module."""
import json
import os
import re
from datetime import datetime
from decimal import Decimal

from validarnif import validar_cif

from .enterprise_management_exception import EnterpriseManagementException
from .enterprise_project import EnterpriseProject


PROJECTS_STORE_FILE = "corporate_operations.json"

class EnterpriseManager:
    """Class for providing the methods for enterprise management."""
    def __init__(self, projects_store_path=None):
        data_directory = os.path.join(os.path.dirname(__file__), "data")
        default_path = os.path.join(data_directory, PROJECTS_STORE_FILE)
        self.__projects_store_path = projects_store_path or default_path

    @staticmethod
    def validate_cif(cif: str):
        """Validate the company CIF using the external helper."""
        return validar_cif(cif)

    @staticmethod
    def _validate_project_acronym(project_acronym: str):
        if not isinstance(project_acronym, str):
            raise EnterpriseManagementException("Invalid project acronym")
        if re.fullmatch(r"[A-Z0-9]{5,10}", project_acronym) is None:
            raise EnterpriseManagementException("Invalid project acronym")

    @staticmethod
    def _validate_operation_name(operation_name: str):
        if not isinstance(operation_name, str):
            raise EnterpriseManagementException("Invalid operation name")
        if not 10 <= len(operation_name) <= 30:
            raise EnterpriseManagementException("Invalid operation name")

    @staticmethod
    def _validate_department(department: str):
        allowed_departments = {"HR", "FINANCE", "LEGAL", "LOGISTICS"}
        if not isinstance(department, str):
            raise EnterpriseManagementException("Invalid department")
        if department not in allowed_departments:
            raise EnterpriseManagementException("Invalid department")

    @staticmethod
    def _validate_starting_date(starting_date: str):
        if not isinstance(starting_date, str):
            raise EnterpriseManagementException("Invalid starting date")

        try:
            parsed_date = datetime.strptime(starting_date, "%d/%m/%Y")
        except ValueError as exc:
            raise EnterpriseManagementException("Invalid starting date") from exc

        if parsed_date.year < 2025 or parsed_date.year >= 2028:
            raise EnterpriseManagementException("Invalid starting date")

        if parsed_date.date() < datetime.now().date():
            raise EnterpriseManagementException("Invalid starting date")

    @staticmethod
    def _validate_budget(budget):
        if isinstance(budget, bool) or not isinstance(budget, (Decimal, float)):
            raise EnterpriseManagementException("Invalid budget")

        decimal_budget = Decimal(str(budget))
        if decimal_budget < Decimal("50000.00") or decimal_budget > Decimal("1000000.00"):
            raise EnterpriseManagementException("Invalid budget")

        if isinstance(budget, Decimal) and budget.as_tuple().exponent != -2:
            raise EnterpriseManagementException("Invalid budget")

        if isinstance(budget, float):
            normalized_budget = decimal_budget.quantize(Decimal("0.01"))
            if normalized_budget != decimal_budget:
                raise EnterpriseManagementException("Invalid budget")

    def _load_projects(self):
        if not os.path.exists(self.__projects_store_path):
            return []

        try:
            with open(self.__projects_store_path, "r", encoding="utf-8") as input_file:
                data = json.load(input_file)
        except (OSError, json.JSONDecodeError) as exc:
            raise EnterpriseManagementException("Error processing project storage") from exc

        if not isinstance(data, list):
            raise EnterpriseManagementException("Error processing project storage")

        return data

    def _save_projects(self, projects):
        directory = os.path.dirname(self.__projects_store_path)
        os.makedirs(directory, exist_ok=True)
        try:
            with open(self.__projects_store_path, "w", encoding="utf-8") as output_file:
                json.dump(projects, output_file, indent=2)
        except OSError as exc:
            raise EnterpriseManagementException("Error processing project storage") from exc

    def register_project(self, company_cif: str, project_achronym: str, operation_name: str, department: str, date: str,
                         budget: float):
        if not isinstance(company_cif, str) or not self.validate_cif(company_cif):
            raise EnterpriseManagementException("Invalid company CIF")

        self._validate_project_acronym(project_achronym)
        self._validate_operation_name(operation_name)
        self._validate_department(department)
        self._validate_starting_date(date)
        self._validate_budget(budget)

        stored_projects = self._load_projects()
        for stored_project in stored_projects:
            if (
                stored_project.get("company_cif") == company_cif
                and stored_project.get("project_description") == operation_name
            ):
                raise EnterpriseManagementException("Project already registered")

        new_project = EnterpriseProject(
            company_cif=company_cif,
            project_acronym=project_achronym,
            project_description=operation_name,
            department=department,
            starting_date=date,
            project_budget=budget
        )

        stored_projects.append(new_project.to_json())
        self._save_projects(stored_projects)
        return new_project.project_id