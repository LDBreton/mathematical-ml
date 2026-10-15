"""Regenerate all eight lectures' synthetic datasets, with independent generators."""
from generate_data import generate as generate_original
from generate_tabular_extensions import generate as generate_tabular
from generate_text_data import generate as generate_text
from generate_sales_data import generate as generate_sales


if __name__ == "__main__":
    generate_original()
    generate_tabular()
    generate_text()
    generate_sales()
    print("Regenerated all course datasets; inspect changes before committing.")
