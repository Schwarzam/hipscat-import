"""Utility to hold all arguments required throughout association pipeline"""

from dataclasses import dataclass

from hipscat.catalog import CatalogParameters

from hipscat_import.runtime_arguments import RuntimeArguments


@dataclass
class AssociationArguments(RuntimeArguments):
    """Data class for holding association arguments"""

    ## Input - Primary
    primary_input_catalog_path: str = ""
    primary_id_column: str = ""
    primary_join_column: str = ""

    ## Input - Join
    join_input_catalog_path: str = ""
    join_id_column: str = ""
    join_foreign_key: str = ""

    def __post_init__(self):
        RuntimeArguments._check_arguments(self)
        self._check_arguments()

    def _check_arguments(self):
        if not self.primary_input_catalog_path:
            raise ValueError("primary_input_catalog_path is required")
        if not self.primary_id_column:
            raise ValueError("primary_id_column is required")
        if not self.primary_join_column:
            raise ValueError("primary_join_column is required")

        if not self.join_input_catalog_path:
            raise ValueError("join_input_catalog_path is required")
        if not self.join_id_column:
            raise ValueError("join_id_column is required")
        if not self.join_foreign_key:
            raise ValueError("join_foreign_key is required")

    def to_catalog_parameters(self) -> CatalogParameters:
        """Convert importing arguments into hipscat catalog parameters.

        Returns:
            CatalogParameters for catalog being created.
        """
        return CatalogParameters(
            catalog_name=self.output_catalog_name,
            catalog_type="association",
            output_path=self.output_path,
        )

    def additional_runtime_provenance_info(self):
        return {
            "primary_input_catalog_path": str(self.primary_input_catalog_path),
            "primary_id_column": self.primary_id_column,
            "primary_join_column": self.primary_join_column,
            "join_input_catalog_path": str(self.join_input_catalog_path),
            "join_id_column": self.join_id_column,
            "join_foreign_key": self.join_foreign_key,
        }
