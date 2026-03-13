"""Enterprise project entity."""
import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal

class EnterpriseProject:
    """Class representing an enterprise project."""
    def __init__(self,
                 company_cif: str,
                 project_acronym: str,
                 project_description: str,
                 department: str,
                 starting_date: str,
                 project_budget: float):
        self.__company_cif = company_cif
        self.__project_description = project_description
        self.__project_achronym = project_acronym
        self.__department = department
        self.__starting_date = starting_date
        self.__project_budget = project_budget
        justnow = datetime.now(timezone.utc)
        self.__time_stamp = datetime.timestamp(justnow)

    def __str__(self):
        return json.dumps(self.to_json(), default=str, sort_keys=True)

    def __signature_payload(self):
        budget_value = self.__project_budget
        if isinstance(budget_value, Decimal):
            budget_value = format(budget_value, ".2f")

        return {
            "company_cif": self.__company_cif,
            "project_description": self.__project_description,
            "project_acronym": self.__project_achronym,
            "project_budget": budget_value,
            "department": self.__department,
            "starting_date": self.__starting_date
        }

    def to_json(self):
        """returns the object information in json format"""
        budget_value = self.__project_budget
        if isinstance(budget_value, Decimal):
            budget_value = format(budget_value, ".2f")

        return {
            "company_cif": self.__company_cif,
            "project_description": self.__project_description,
            "project_acronym": self.__project_achronym,
            "project_budget": budget_value,
            "department": self.__department,
            "starting_date": self.__starting_date,
            "time_stamp": self.__time_stamp,
            "project_id": self.project_id
        }
    @property
    def company_cif(self):
        """Sender's iban"""
        return self.__company_cif

    @company_cif.setter
    def company_cif(self, value):
        self.__company_cif = value

    @property
    def project_description(self):
        """receiver's iban"""
        return self.__project_description

    @project_description.setter
    def project_description(self, value):
        self.__project_description = value

    @property
    def project_acronym(self):
        """Property representing the type of transfer: REGULAR, INMEDIATE or URGENT """
        return self.__project_achronym
    @project_acronym.setter
    def project_acronym(self, value):
        self.__project_achronym = value

    @property
    def project_budget(self):
        """Property respresenting the transfer amount"""
        return self.__project_budget
    @project_budget.setter
    def project_budget(self, value):
        self.__project_budget = value

    @property
    def department(self):
        """Property representing the transfer concept"""
        return self.__department
    @department.setter
    def department(self, value):
        self.__department = value

    @property
    def starting_date( self ):
        """Property representing the transfer's date"""
        return self.__starting_date
    @starting_date.setter
    def starting_date( self, value ):
        self.__starting_date = value

    @property
    def time_stamp(self):
        """Read-only property that returns the timestamp of the request"""
        return self.__time_stamp

    @property
    def project_id(self):
        """Returns the md5 signature based only on the input fields."""
        payload = json.dumps(self.__signature_payload(), sort_keys=True)
        return hashlib.md5(payload.encode("utf-8")).hexdigest()
