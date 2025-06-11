from infrastructure import Config


class EmployeeService:
    def __init__(self):
        self.config = Config()
        self.service_url = self.config.EMPLOYEE_SERVICE_URL

    async def get_employees(self) -> set:
        return {"list_of_usernames from service"}