import pulumi


class PulumiHelper:
    @staticmethod
    def read_user_data():
        with open(f"env/{pulumi.get_stack()}/user_data_template.sh", "r") as file:
            return file.read()

    @staticmethod
    def default_tags(name: str) -> dict:
        return {"Name": name, "Environment": pulumi.get_stack(), "ManagedBy": "Pulumi"}
